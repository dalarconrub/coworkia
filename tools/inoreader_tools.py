"""
Wrapper para la API REST de Inoreader (OAuth2).

Convencion de credenciales y estado:
  - .env:
      INOREADER_APP_ID, INOREADER_APP_KEY      (credenciales de la app, fijas)
      INOREADER_REDIRECT_URI                   (default http://localhost:8080/callback)
      INOREADER_FOLDER_KIT                     (carpeta/tag a sincronizar, default 'kit-import')
  - artifacts/inoreader_state.json (gitignored):
      access_token, refresh_token, expires_at  (estado vivo, refrescado automaticamente)

Endpoints relevantes:
  - Auth:    https://www.inoreader.com/oauth2/auth
  - Token:   https://www.inoreader.com/oauth2/token
  - API v0:  https://www.inoreader.com/reader/api/0/

Streams:
  - Starred: user/-/state/com.google/starred
  - Folder:  user/-/label/<folder_name>

Documentacion oficial: https://www.inoreader.com/developers/
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Iterator

import requests

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "artifacts" / "inoreader_state.json"
SYNC_STATE_PATH = ROOT / "artifacts" / "inoreader_sync_state.json"

# Inoreader admite hasta 1000 items por peticion. Subir el page size es la
# palanca mas barata para no agotar el limite diario de 100 calls.
DEFAULT_PAGE_SIZE = 1000

AUTH_URL = "https://www.inoreader.com/oauth2/auth"
TOKEN_URL = "https://www.inoreader.com/oauth2/token"
API_BASE = "https://www.inoreader.com/reader/api/0"

DEFAULT_REDIRECT = "http://localhost:8080/callback"
DEFAULT_FOLDER = "kit-import"

# Heuristicas de subtipo a partir de feed/categorias
SUBTIPO_RULES = [
    ("youtube.com", "Vídeo"),
    ("vimeo.com", "Vídeo"),
    ("substack.com", "Newsletter"),
    ("beehiiv.com", "Newsletter"),
    ("buttondown.email", "Newsletter"),
    ("convertkit.com", "Newsletter"),
]
SUBTIPO_AUDIO_HINTS = ("podcast", "audio/mpeg", ".mp3")


# ─── ESTADO Y TOKENS ─────────────────────────────────────────────────────────

def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def save_initial_tokens(access_token: str, refresh_token: str, expires_in: int) -> None:
    """Persiste los tokens iniciales emitidos por el flujo OAuth interactivo."""
    _save_state({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": int(time.time()) + int(expires_in) - 60,
    })


def _refresh_access_token() -> str:
    state = _load_state()
    refresh = state.get("refresh_token")
    if not refresh:
        raise RuntimeError(
            "No hay refresh_token en artifacts/inoreader_state.json. "
            "Ejecuta 'python tools/inoreader_oauth.py' para autorizar la app."
        )
    app_id = os.getenv("INOREADER_APP_ID")
    app_key = os.getenv("INOREADER_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError("Faltan INOREADER_APP_ID / INOREADER_APP_KEY en .env")

    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": app_id,
            "client_secret": app_key,
            "grant_type": "refresh_token",
            "refresh_token": refresh,
        },
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    new_state = {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token", refresh),
        "expires_at": int(time.time()) + int(payload.get("expires_in", 3600)) - 60,
    }
    _save_state(new_state)
    return new_state["access_token"]


def get_access_token() -> str:
    """Devuelve un access_token vigente, refrescando si esta expirado."""
    state = _load_state()
    token = state.get("access_token")
    expires_at = state.get("expires_at", 0)
    if token and time.time() < expires_at:
        return token
    return _refresh_access_token()


# ─── HTTP ────────────────────────────────────────────────────────────────────

def _api_headers() -> dict:
    app_id = os.getenv("INOREADER_APP_ID", "")
    app_key = os.getenv("INOREADER_APP_KEY", "")
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "AppId": app_id,
        "AppKey": app_key,
    }


def _get(path: str, params: dict | None = None) -> dict:
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    resp = requests.get(url, headers=_api_headers(), params=params or {}, timeout=60)
    if resp.status_code == 401:
        # Token expirado a media peticion: forzar refresh y reintentar una vez
        _refresh_access_token()
        resp = requests.get(url, headers=_api_headers(), params=params or {}, timeout=60)
    resp.raise_for_status()
    return resp.json()


# ─── ENDPOINTS DE ALTO NIVEL ─────────────────────────────────────────────────

def user_info() -> dict:
    """Devuelve info de la cuenta. Util para validar la autorizacion."""
    return _get("/user-info")


def list_folders() -> list[str]:
    """Lista los nombres de carpetas/tags del usuario."""
    payload = _get("/tag/list", params={"types": "1"})
    folders = []
    for tag in payload.get("tags", []):
        tag_id = tag.get("id", "")
        if "/label/" in tag_id:
            folders.append(tag_id.split("/label/", 1)[1])
    return folders


def _stream_contents(stream_id: str, count: int = DEFAULT_PAGE_SIZE,
                     newer_than: int | None = None) -> Iterator[dict]:
    """Itera todos los items de un stream paginando con continuation.

    Si se pasa newer_than (unix epoch), Inoreader devuelve solo items posteriores
    a ese timestamp -> base del sync incremental para no agotar el limite diario.
    """
    base_params: dict = {"n": count}
    if newer_than:
        base_params["ot"] = int(newer_than)
    params = dict(base_params)
    while True:
        payload = _get(f"/stream/contents/{stream_id}", params=params)
        for item in payload.get("items", []):
            yield item
        cont = payload.get("continuation")
        if not cont:
            break
        params = dict(base_params)
        params["c"] = cont


def list_starred(limit: int | None = None, newer_than: int | None = None) -> list[dict]:
    """Articulos marcados con estrella."""
    return _collect(_stream_contents(
        "user/-/state/com.google/starred", newer_than=newer_than,
    ), limit)


def list_folder(folder_name: str, limit: int | None = None,
                newer_than: int | None = None) -> list[dict]:
    """Articulos en una carpeta/tag concreto."""
    stream = f"user/-/label/{folder_name}"
    return _collect(_stream_contents(stream, newer_than=newer_than), limit)


def _collect(it: Iterator[dict], limit: int | None) -> list[dict]:
    out: list[dict] = []
    for item in it:
        out.append(item)
        if limit and len(out) >= limit:
            break
    return out


# ─── NORMALIZACION ──────────────────────────────────────────────────────────

def normalize_article(raw: dict, source_tag: str) -> dict:
    """
    Convierte un item del API de Inoreader a un dict consistente apto para KIT.

    source_tag identifica de donde vino: 'starred', 'kit-import', etc.
    """
    alternate = (raw.get("alternate") or [{}])[0]
    url = alternate.get("href", "")
    origin = raw.get("origin") or {}
    feed_title = origin.get("title", "")
    feed_url = origin.get("htmlUrl") or origin.get("streamId", "")

    summary_obj = raw.get("summary") or {}
    summary_html = summary_obj.get("content", "")

    categories = [c for c in raw.get("categories", []) if isinstance(c, str)]
    user_labels = [c.split("/label/", 1)[1] for c in categories if "/label/" in c]

    enclosures = raw.get("enclosure") or []
    has_audio = any(
        (enc.get("type", "").startswith("audio") or enc.get("href", "").endswith(".mp3"))
        for enc in enclosures
    )

    subtipo = _infer_subtipo(url, feed_url, feed_title, has_audio, categories)

    published = raw.get("published")
    updated = raw.get("updated") or published

    return {
        "inoreader_id": raw.get("id", ""),
        "title": (raw.get("title") or "").strip() or "(sin titulo)",
        "url": url,
        "feed_title": feed_title,
        "feed_url": feed_url,
        "summary_html": summary_html,
        "summary_text": _strip_html(summary_html)[:2000],
        "author": (raw.get("author") or "").strip(),
        "user_labels": user_labels,
        "subtipo": subtipo,
        "published_date": _epoch_to_iso(published),
        "updated_date": _epoch_to_iso(updated),
        "source_tags": [source_tag],
    }


# ─── CURSORES DE SYNC INCREMENTAL ────────────────────────────────────────────

def _load_sync_state() -> dict:
    if not SYNC_STATE_PATH.exists():
        return {}
    return json.loads(SYNC_STATE_PATH.read_text(encoding="utf-8"))


def _save_sync_state(state: dict) -> None:
    SYNC_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def last_seen_for(stream: str) -> int | None:
    """Ultimo unix epoch sincronizado para un stream ('starred' | folder name)."""
    return _load_sync_state().get(stream)


def mark_seen_for(stream: str, epoch: int) -> None:
    """Persiste el cursor del stream tras una sync exitosa."""
    state = _load_sync_state()
    state[stream] = int(epoch)
    _save_sync_state(state)


def merge_articles(*lists: list[dict]) -> list[dict]:
    """Une varias listas de articulos normalizados dedupando por URL del articulo
    (con fallback a inoreader_id si la URL esta vacia).

    Razon: Inoreader expone IDs distintos para el MISMO articulo segun el
    endpoint (API stream/contents vs JSON feed publico) y tambien si el
    articulo aparece en mas de un feed que sigues. La URL del articulo es
    la unica clave estable cross-route y cross-feed.

    Si un mismo articulo aparece en varias fuentes, fusiona source_tags.
    """
    by_key: dict[str, dict] = {}
    for lst in lists:
        for art in lst:
            key = art.get("url") or art.get("inoreader_id") or ""
            if not key:
                continue
            if key in by_key:
                tags = set(by_key[key]["source_tags"]) | set(art["source_tags"])
                by_key[key]["source_tags"] = sorted(tags)
            else:
                by_key[key] = dict(art)
    return list(by_key.values())


# ─── HEURISTICAS ─────────────────────────────────────────────────────────────

def _infer_subtipo(url: str, feed_url: str, feed_title: str,
                   has_audio: bool, categories: list[str]) -> str:
    haystack = " ".join([url, feed_url, feed_title]).lower()
    cats_low = " ".join(categories).lower()

    if has_audio or "podcast" in haystack or "podcast" in cats_low:
        return "Podcast"
    for needle, subtype in SUBTIPO_RULES:
        if needle in haystack:
            return subtype
    if "blog" in cats_low or "/blog" in haystack:
        return "Blog"
    return "Artículo"


def _epoch_to_iso(value) -> str | None:
    if not value:
        return None
    try:
        ts = int(value)
        return time.strftime("%Y-%m-%d", time.gmtime(ts))
    except (TypeError, ValueError):
        return None


def _strip_html(html: str) -> str:
    if not html:
        return ""
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _iso_to_date(value) -> str | None:
    """Convierte ISO 8601 (e.g. '2026-04-22T10:30:00Z') a 'YYYY-MM-DD'."""
    if not value or not isinstance(value, str) or len(value) < 10:
        return None
    return value[:10]


def normalize_jsonfeed_item(raw: dict, source_tag: str) -> dict:
    """Normaliza un item del export 'JSON Feed' (jsonfeed.org v1/v1.1).

    Devuelve el mismo dict que normalize_article -> el resto del pipeline
    (merge_articles, upsert_article_to_kit) lo trata identico, sin saber
    de que origen vino.
    """
    url = raw.get("url") or raw.get("external_url") or ""
    title = (raw.get("title") or "").strip() or "(sin titulo)"

    summary_html = raw.get("content_html") or raw.get("summary") or raw.get("content_text") or ""
    summary_text = _strip_html(summary_html)[:2000]

    # author (v1) | authors (v1.1)
    author = ""
    if isinstance(raw.get("author"), dict):
        author = raw["author"].get("name", "")
    elif isinstance(raw.get("authors"), list) and raw["authors"]:
        first = raw["authors"][0]
        if isinstance(first, dict):
            author = first.get("name", "")

    user_labels = [t for t in raw.get("tags", []) if isinstance(t, str)]

    attachments = raw.get("attachments") or []
    has_audio = any(
        (att.get("mime_type", "").startswith("audio") or att.get("url", "").endswith(".mp3"))
        for att in attachments if isinstance(att, dict)
    )

    # En JSON Feed estandar no hay feed_title/feed_url por item; pasan vacios
    subtipo = _infer_subtipo(url, "", "", has_audio, user_labels)

    return {
        "inoreader_id": raw.get("id", ""),
        "title": title,
        "url": url,
        "feed_title": "",
        "feed_url": "",
        "summary_html": summary_html,
        "summary_text": summary_text,
        "author": author,
        "user_labels": user_labels,
        "subtipo": subtipo,
        "published_date": _iso_to_date(raw.get("date_published")),
        "updated_date": _iso_to_date(raw.get("date_modified") or raw.get("date_published")),
        "source_tags": [source_tag],
    }


def dispatch_normalize(raw_item: dict, source_tag: str) -> dict:
    """Auto-detecta el formato del item y delega al normalizador correcto.

    - API stream/contents (Google Reader-like): tiene 'alternate' o 'origin'.
    - JSON Feed (jsonfeed.org):                  tiene 'url' o 'date_published'.
    """
    if "alternate" in raw_item or "origin" in raw_item:
        return normalize_article(raw_item, source_tag)
    return normalize_jsonfeed_item(raw_item, source_tag)
