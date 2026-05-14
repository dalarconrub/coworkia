"""
Sincroniza articulos de Inoreader -> KIT vía API autenticada.

Camino paralelo y complementario al importer offline (import_inoreader_articles.py
que usa JSON feed publico). Diferencias:

  - sync_inoreader_to_kit (este): vía API OAuth2, soporta sync INCREMENTAL
    con cursor (newer_than) persistido en artifacts/inoreader_sync_state.json.
    Consume cuota: ~1 call por sync incremental, ~ceil(total/1000) en --full.
  - import_inoreader_articles: vía JSON feed publico, sin auth, sin cuota,
    pero siempre full pull (no soporta cursor server-side).

Ambos comparten los mismos helpers de upsert (_article_to_props,
upsert_article_to_kit, _existing_articles), normalizacion (dispatch_normalize)
y dedupe (merge_articles), por lo que producen filas KIT identicas.

Stream sincronizado (uno solo):
  - INOREADER_FOLDER_KIT (tag)   -> user/-/label/<tag>     (default 'kit-import')

NOTA DE DISENO: Inoreader marca como 'starred' los articulos enviados a
'Read later'. Eso NO es senal de "quiero catalogar en KIT" -> el sync NO
trae starred. Solo entra al KIT lo que se tagea explicitamente con
INOREADER_FOLDER_KIT (typically 'kit-import'). list_starred() sigue
disponible en inoreader_tools por si se usa para otros flujos futuros, pero
este sync no lo invoca.

Cursor incremental: el stream recuerda su 'last seen' epoch en
artifacts/inoreader_sync_state.json. Tras cada sync exitoso se marca el
timestamp actual; el siguiente run solo trae items posteriores.

CLI:
    python tools/sync_inoreader_to_kit.py            # incremental
    python tools/sync_inoreader_to_kit.py --full     # ignora cursor
    python tools/sync_inoreader_to_kit.py --limit 5  # tope para pruebas
    python tools/sync_inoreader_to_kit.py --dry-run  # no escribe en Notion
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.inoreader_tools import (
    last_seen_for,
    list_folder,
    mark_seen_for,
    merge_articles,
    normalize_article,
)
from tools.notion_tools import (
    create_page,
    extract_property_value,
    query_data_source,
    update_page_properties,
)
from tools.url_normalization import canonical_url


# ─── HELPERS DE UPSERT (compartidos con import_inoreader_articles.py) ────────

def existing_articles(db_kit: str) -> dict[str, dict[str, str]]:
    """Indices de filas KIT-Inoreader para dedupe en upsert.

    Devuelve {'by_url': {url: page_id}, 'by_inoreader_id': {iid: page_id}}.
    La URL del articulo (campo Enlace) es la clave canonica para evitar
    duplicados entre rutas (API vs JSON feed) y entre feeds que duplican el
    mismo articulo. Inoreader ID es fallback cuando la URL esta vacia.
    """
    rows = query_data_source(db_kit)
    by_url: dict[str, str] = {}
    by_iid: dict[str, str] = {}
    for row in rows:
        props = row.get("properties", {})
        page_id = row["id"]
        url = canonical_url(extract_property_value(props.get("Enlace", {})))
        iid = extract_property_value(props.get("Inoreader ID", {})) if "Inoreader ID" in props else ""
        if url:
            by_url[url] = page_id
        if iid:
            by_iid[iid] = page_id
    return {"by_url": by_url, "by_inoreader_id": by_iid}


def article_to_props(article: dict) -> dict:
    """Convierte articulo normalizado en props Notion para KIT."""
    fuente = (article.get("author") or article.get("feed_title") or "Inoreader")[:2000]

    props: dict = {
        "Titulo": {"title": [{"text": {"content": article["title"][:2000]}}]},
        "Tipo": {"select": {"name": "Information"}},
        "Subtipo": {"select": {"name": article["subtipo"]}},
        "Inoreader ID": {"rich_text": [{"text": {"content": article["inoreader_id"][:2000]}}]},
        "Inoreader Tags": {"multi_select": [{"name": tag} for tag in article["source_tags"]]},
        "Estado": {"select": {"name": "Activo"}},
        "Fuente / Autor": {"rich_text": [{"text": {"content": fuente}}]},
    }
    if article.get("url"):
        props["Enlace"] = {"url": canonical_url(article["url"])}
    if article.get("summary_text"):
        props["Resumen"] = {"rich_text": [{"text": {"content": article["summary_text"][:2000]}}]}
    if article.get("published_date"):
        props["Fecha de publicacion"] = {"date": {"start": article["published_date"]}}
    if article.get("updated_date"):
        props["Fecha de actualizacion"] = {"date": {"start": article["updated_date"]}}
    return props


def upsert_article_to_kit(db_kit: str, article: dict,
                          existing: dict[str, dict[str, str]]) -> tuple[str, str]:
    """Crea o actualiza la pagina KIT del articulo.

    Lookup: URL del articulo primero (clave canonica), Inoreader ID como
    fallback. Devuelve ('created'|'updated', page_id). Mutar `existing` con
    el nuevo page_id evita duplicar dentro del mismo run si dos llamadas
    comparten el mismo articulo.
    """
    props = article_to_props(article)
    url = canonical_url(article.get("url"))
    iid = article.get("inoreader_id", "")

    page_id: str | None = None
    if url and url in existing["by_url"]:
        page_id = existing["by_url"][url]
    elif iid and iid in existing["by_inoreader_id"]:
        page_id = existing["by_inoreader_id"][iid]

    if page_id:
        update_page_properties(page_id, props)
        # Refresca ambos indices (puede ser primer encuentro por URL o por iid)
        if url:
            existing["by_url"][url] = page_id
        if iid:
            existing["by_inoreader_id"][iid] = page_id
        return ("updated", page_id)

    page = create_page(
        parent_id=db_kit,
        title=article["title"],
        properties=props,
        is_data_source=True,
    )
    new_id = page["id"]
    if url:
        existing["by_url"][url] = new_id
    if iid:
        existing["by_inoreader_id"][iid] = new_id
    return ("created", new_id)


# ─── SYNC VIA API ────────────────────────────────────────────────────────────

def _fetch_stream(stream_name: str, lister, source_tag: str,
                  full: bool, limit: int | None) -> list[dict]:
    """Llama al API para un stream y normaliza los items al formato compartido."""
    cursor = None if full else last_seen_for(stream_name)
    if cursor:
        print(f"[sync] {stream_name}: incremental desde {time.strftime('%Y-%m-%d %H:%M', time.gmtime(cursor))} UTC")
    else:
        print(f"[sync] {stream_name}: pull completo (sin cursor)")
    raw = lister(limit=limit, newer_than=cursor)
    return [normalize_article(it, source_tag) for it in raw]


def run_sync(full: bool = False, limit: int | None = None,
             dry_run: bool = False) -> dict:
    """Ejecuta el sync API. Devuelve dict con metricas."""
    db_kit = os.getenv("NOTION_DB_KIT")
    folder_kit = os.getenv("INOREADER_FOLDER_KIT", "kit-import")
    if not db_kit and not dry_run:
        raise RuntimeError("Falta NOTION_DB_KIT en .env")

    sync_started = int(time.time())

    tagged = _fetch_stream(
        folder_kit,
        lambda limit, newer_than: list_folder(folder_kit, limit=limit, newer_than=newer_than),
        source_tag=folder_kit,
        full=full, limit=limit,
    )
    print(f"[sync] {folder_kit}: {len(tagged)} articulos")

    # merge_articles dedupe por inoreader_id (defensivo aunque solo haya un stream)
    merged = merge_articles(tagged)
    print(f"[merge] union deduplicada: {len(merged)} articulos")

    if limit:
        merged = merged[:limit]
        print(f"[limit] truncado a {len(merged)} articulos")

    metrics = {
        "tagged_fetched": len(tagged),
        "merged": len(merged),
        "created": 0,
        "updated": 0,
        "errors": 0,
    }

    if dry_run:
        print("[dry-run] no escribo en Notion. No actualizo cursores.")
        return metrics

    print("[notion] cargando indices existentes en KIT (por URL y por Inoreader ID)...")
    existing = existing_articles(db_kit)
    print(f"[notion] {len(existing['by_inoreader_id'])} articulos Inoreader, {len(existing['by_url'])} con URL")

    total = len(merged)
    for idx, art in enumerate(merged, 1):
        for attempt in range(5):
            try:
                action, _pid = upsert_article_to_kit(db_kit, art, existing)
                if action == "created":
                    metrics["created"] += 1
                else:
                    metrics["updated"] += 1
                break
            except Exception as exc:
                if attempt == 4:
                    metrics["errors"] += 1
                    print(f"[err {idx}/{total}] {art['title'][:80]}: {exc}")
                time.sleep(2 + attempt)
        time.sleep(0.35)
        if idx % 25 == 0:
            print(f"[progress] {idx}/{total} created={metrics['created']} updated={metrics['updated']} errors={metrics['errors']}")

    # Cursor: solo si no hubo errores -> evitar saltar items en futuros runs
    if metrics["errors"] == 0:
        mark_seen_for(folder_kit, sync_started)
        print(f"[cursor] {folder_kit} avanzado a {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(sync_started))}")
    else:
        print("[cursor] cursor NO actualizado (hubo errores; reintenta para no perder items)")

    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Inoreader -> KIT via API")
    parser.add_argument("--full", action="store_true",
                        help="Ignora cursor incremental, full pull (consume mas cuota)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Procesa solo los N primeros items (pruebas)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Lee y normaliza, no escribe en Notion ni actualiza cursores")
    args = parser.parse_args()

    metrics = run_sync(full=args.full, limit=args.limit, dry_run=args.dry_run)
    folder_kit = os.getenv("INOREADER_FOLDER_KIT", "kit-import")
    print("\n=== SYNC COMPLETADO ===")
    print(f"  {folder_kit} (API): {metrics['tagged_fetched']}")
    print(f"  merged unique:     {metrics['merged']}")
    print(f"  created:           {metrics['created']}")
    print(f"  updated:           {metrics['updated']}")
    print(f"  errors:            {metrics['errors']}")
    return 0 if metrics["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
