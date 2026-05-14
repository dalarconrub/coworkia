"""
Wrapper minimo para Raindrop.io -> KIT.

Raindrop actua como fuente externa de KIT, no como catalogo independiente.
El endpoint MCP oficial sirve para clientes IA interactivos, pero el sync local
usa REST v1 porque es estable, paginable y facil de validar.

Config:
  - RAINDROP_ACCESS_TOKEN: Bearer token REST manual (opcional)
  - RAINDROP_CLIENT_ID, RAINDROP_CLIENT_SECRET, RAINDROP_REDIRECT_URI: OAuth
  - RAINDROP_TAG_KIT: tag que marca items a importar (default kit-import)
  - RAINDROP_COLLECTION_ID: coleccion origen (default 0 = all except Trash)
  - RAINDROP_SEARCH_KIT: busqueda opcional server-side (ej. #kit-import)
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import requests

ROOT = Path(__file__).resolve().parent.parent
SYNC_STATE_PATH = ROOT / "artifacts" / "raindrop_sync_state.json"
STATE_PATH = ROOT / "artifacts" / "raindrop_state.json"
API_BASE = "https://api.raindrop.io/rest/v1"
MCP_ENDPOINT = "https://api.raindrop.io/rest/v2/ai/mcp"
AUTH_URL = "https://raindrop.io/oauth/authorize"
TOKEN_URL = "https://raindrop.io/oauth/access_token"
DEFAULT_REDIRECT = "http://localhost:8766/callback"
DEFAULT_TAG = "kit-import"
DEFAULT_COLLECTION_ID = 0
MAX_PER_PAGE = 50


def _load_sync_state() -> dict:
    if not SYNC_STATE_PATH.exists():
        return {}
    return json.loads(SYNC_STATE_PATH.read_text(encoding="utf-8"))


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def save_initial_tokens(access_token: str, refresh_token: str, expires_in: int) -> None:
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
            "No hay RAINDROP_ACCESS_TOKEN ni refresh_token en artifacts/raindrop_state.json. "
            "Ejecuta 'python tools/raindrop_oauth.py'."
        )
    client_id = os.getenv("RAINDROP_CLIENT_ID", "").strip()
    client_secret = os.getenv("RAINDROP_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise RuntimeError("Faltan RAINDROP_CLIENT_ID / RAINDROP_CLIENT_SECRET en .env")

    resp = requests.post(
        TOKEN_URL,
        json={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh,
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    new_state = {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token", refresh),
        "expires_at": int(time.time()) + int(payload.get("expires_in", 1209600)) - 60,
    }
    _save_state(new_state)
    return new_state["access_token"]


def get_access_token() -> str:
    manual = os.getenv("RAINDROP_ACCESS_TOKEN", "").strip()
    if manual:
        return manual
    state = _load_state()
    token = state.get("access_token")
    expires_at = state.get("expires_at", 0)
    if token and time.time() < expires_at:
        return token
    return _refresh_access_token()


def _save_sync_state(state: dict) -> None:
    SYNC_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _state_key(collection_id: int, tag: str, search: str | None) -> str:
    search_part = search or f"tag:{tag}"
    return f"collection:{collection_id}|{search_part}"


def last_seen_for(collection_id: int, tag: str, search: str | None = None) -> str | None:
    return _load_sync_state().get(_state_key(collection_id, tag, search))


def mark_seen_for(collection_id: int, tag: str, value: str, search: str | None = None) -> None:
    state = _load_sync_state()
    state[_state_key(collection_id, tag, search)] = value
    _save_sync_state(state)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _headers() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}"}


def _get(path: str, params: dict | None = None) -> dict:
    url = path if path.startswith("http") else f"{API_BASE}{path}"
    resp = requests.get(url, headers=_headers(), params=params or {}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def user_info() -> dict:
    return _get("/user").get("user", {})


def list_tags(collection_id: int | None = None) -> list[dict]:
    path = "/tags" if collection_id is None else f"/tags/{collection_id}"
    return _get(path).get("items", [])


def list_collections() -> list[dict]:
    root = _get("/collections").get("items", [])
    children = _get("/collections/childrens").get("items", [])
    by_id: dict[str, dict] = {}
    for collection in root + children:
        key = str(collection.get("_id") or "")
        if key:
            by_id[key] = collection
    return list(by_id.values())


def iter_raindrops(collection_id: int = DEFAULT_COLLECTION_ID,
                  search: str | None = None,
                  sort: str = "-created",
                  nested: bool = True,
                  max_pages: int | None = None) -> Iterator[dict]:
    page = 0
    while True:
        if max_pages is not None and page >= max_pages:
            break
        params = {
            "page": page,
            "perpage": MAX_PER_PAGE,
            "sort": sort,
            "nested": "true" if nested else "false",
        }
        if search:
            params["search"] = search
        payload = _get(f"/raindrops/{collection_id}", params=params)
        items = payload.get("items", [])
        for item in items:
            yield item
        if len(items) < MAX_PER_PAGE:
            break
        page += 1


def list_raindrops(collection_id: int = DEFAULT_COLLECTION_ID,
                   tag: str = DEFAULT_TAG,
                   search: str | None = None,
                   limit: int | None = None,
                   newer_than: str | None = None,
                   max_pages: int | None = None) -> list[dict]:
    out: list[dict] = []
    for item in iter_raindrops(collection_id=collection_id, search=search, max_pages=max_pages):
        if not search and tag:
            tags = [str(t).lower() for t in item.get("tags", [])]
            if tag.lower() not in tags:
                continue
        if newer_than and _item_updated(item) <= newer_than:
            continue
        out.append(item)
        if limit and len(out) >= limit:
            break
    return out


def normalize_raindrop(raw: dict) -> dict:
    link = raw.get("link") or ""
    tags = [str(t) for t in raw.get("tags", []) if str(t).strip()]
    collection = raw.get("collection") or {}
    collection_id = collection.get("$id")
    collection_title = collection.get("title") or ""
    domain = raw.get("domain") or ""
    excerpt = raw.get("excerpt") or ""
    note = raw.get("note") or ""
    summary = "\n\n".join(part for part in [excerpt, note] if part).strip()

    return {
        "raindrop_id": str(raw.get("_id") or ""),
        "title": (raw.get("title") or "").strip() or "(sin titulo)",
        "url": link,
        "domain": domain,
        "collection_id": str(collection_id or ""),
        "collection_title": collection_title,
        "tags": tags,
        "subtipo": _infer_subtipo(raw),
        "summary_text": summary[:2000],
        "created_date": _iso_to_date(raw.get("created")),
        "updated_date": _iso_to_date(raw.get("lastUpdate") or raw.get("created")),
        "raindrop_type": raw.get("type") or "",
    }


def merge_raindrops(items: list[dict]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for item in items:
        key = item.get("url") or item.get("raindrop_id") or ""
        if not key:
            continue
        if key in by_key:
            tags = set(by_key[key].get("tags", [])) | set(item.get("tags", []))
            by_key[key]["tags"] = sorted(tags)
        else:
            by_key[key] = dict(item)
    return list(by_key.values())


def _item_updated(item: dict) -> str:
    return item.get("lastUpdate") or item.get("created") or ""


def _iso_to_date(value: str | None) -> str | None:
    if not value or len(value) < 10:
        return None
    return value[:10]


def _infer_subtipo(raw: dict) -> str:
    rtype = (raw.get("type") or "").lower()
    haystack = " ".join([
        raw.get("link") or "",
        raw.get("domain") or "",
        " ".join(raw.get("tags") or []),
    ]).lower()
    if rtype == "video" or "youtube.com" in haystack or "vimeo.com" in haystack:
        return "Vídeo"
    if rtype == "audio" or "podcast" in haystack:
        return "Podcast"
    if rtype == "document" or ".pdf" in haystack:
        return "Paper"
    if "substack.com" in haystack or "newsletter" in haystack:
        return "Newsletter"
    if "blog" in haystack or "/blog" in haystack:
        return "Blog"
    return "Artículo"
