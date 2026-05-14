"""
Sincroniza bookmarks de Raindrop.io -> KIT via REST API.

Politica Coworkia:
  - Raindrop es fuente externa de KIT, igual que Inoreader.
  - Solo entra lo marcado con RAINDROP_TAG_KIT (default kit-import), salvo que
    se defina RAINDROP_SEARCH_KIT para delegar el filtro al buscador de Raindrop.
  - No se crean filas raindrop:* en INX; sync_inx_links --source kit materializa
    las filas como kit:<page_id>.
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

from tools.notion_tools import (
    create_page,
    extract_property_value,
    query_data_source,
    update_page_properties,
)
from tools.raindrop_tools import (
    DEFAULT_COLLECTION_ID,
    DEFAULT_TAG,
    last_seen_for,
    list_raindrops,
    mark_seen_for,
    merge_raindrops,
    normalize_raindrop,
    utc_now_iso,
)
from tools.url_normalization import canonical_url


def existing_raindrops(db_kit: str) -> dict[str, dict[str, str]]:
    rows = query_data_source(db_kit)
    by_url: dict[str, str] = {}
    by_rid: dict[str, str] = {}
    for row in rows:
        props = row.get("properties", {})
        page_id = row["id"]
        url = canonical_url(extract_property_value(props.get("Enlace", {})))
        rid = extract_property_value(props.get("Raindrop ID", {})) if "Raindrop ID" in props else ""
        if url:
            by_url[url] = page_id
        if rid:
            by_rid[rid] = page_id
    return {"by_url": by_url, "by_raindrop_id": by_rid}


def raindrop_to_props(item: dict) -> dict:
    fuente = (item.get("domain") or item.get("collection_title") or "Raindrop.io")[:2000]
    props: dict = {
        "Titulo": {"title": [{"text": {"content": item["title"][:2000]}}]},
        "Tipo": {"select": {"name": "Information"}},
        "Subtipo": {"select": {"name": item["subtipo"]}},
        "Raindrop ID": {"rich_text": [{"text": {"content": item["raindrop_id"][:2000]}}]},
        "Raindrop Tags": {"multi_select": [{"name": tag[:100]} for tag in item.get("tags", [])]},
        "Estado": {"select": {"name": "Activo"}},
        "Fuente / Autor": {"rich_text": [{"text": {"content": fuente}}]},
    }
    if item.get("url"):
        props["Enlace"] = {"url": canonical_url(item["url"])}
    if item.get("summary_text"):
        props["Resumen"] = {"rich_text": [{"text": {"content": item["summary_text"][:2000]}}]}
    if item.get("created_date"):
        props["Fecha de publicacion"] = {"date": {"start": item["created_date"]}}
    if item.get("updated_date"):
        props["Fecha de actualizacion"] = {"date": {"start": item["updated_date"]}}
    if item.get("collection_title") or item.get("collection_id"):
        collection = item.get("collection_title") or item.get("collection_id")
        props["Raindrop Collection"] = {"rich_text": [{"text": {"content": collection[:2000]}}]}
    if item.get("raindrop_type"):
        props["Raindrop Type"] = {"rich_text": [{"text": {"content": item["raindrop_type"][:2000]}}]}
    return props


def upsert_raindrop_to_kit(db_kit: str, item: dict,
                           existing: dict[str, dict[str, str]]) -> tuple[str, str]:
    props = raindrop_to_props(item)
    url = canonical_url(item.get("url"))
    rid = item.get("raindrop_id", "")

    page_id: str | None = None
    if url and url in existing["by_url"]:
        page_id = existing["by_url"][url]
    elif rid and rid in existing["by_raindrop_id"]:
        page_id = existing["by_raindrop_id"][rid]

    if page_id:
        update_page_properties(page_id, props)
        if url:
            existing["by_url"][url] = page_id
        if rid:
            existing["by_raindrop_id"][rid] = page_id
        return ("updated", page_id)

    page = create_page(
        parent_id=db_kit,
        title=item["title"],
        properties=props,
        is_data_source=True,
    )
    new_id = page["id"]
    if url:
        existing["by_url"][url] = new_id
    if rid:
        existing["by_raindrop_id"][rid] = new_id
    return ("created", new_id)


def run_sync(full: bool = False, limit: int | None = None,
             dry_run: bool = False, max_pages: int | None = None) -> dict:
    db_kit = os.getenv("NOTION_DB_KIT")
    tag = os.getenv("RAINDROP_TAG_KIT", DEFAULT_TAG)
    collection_id = int(os.getenv("RAINDROP_COLLECTION_ID", str(DEFAULT_COLLECTION_ID)))
    search = (os.getenv("RAINDROP_SEARCH_KIT") or "").strip() or None
    if not db_kit and not dry_run:
        raise RuntimeError("Falta NOTION_DB_KIT en .env")

    cursor = None if full else last_seen_for(collection_id, tag, search)
    if cursor:
        print(f"[sync] Raindrop incremental desde {cursor}")
    else:
        print("[sync] Raindrop pull completo (sin cursor)")

    sync_started = utc_now_iso()
    raw_items = list_raindrops(
        collection_id=collection_id,
        tag=tag,
        search=search,
        limit=limit,
        newer_than=cursor,
        max_pages=max_pages,
    )
    normalized = [normalize_raindrop(item) for item in raw_items]
    merged = merge_raindrops(normalized)
    if limit:
        merged = merged[:limit]

    metrics = {
        "fetched": len(raw_items),
        "merged": len(merged),
        "created": 0,
        "updated": 0,
        "errors": 0,
        "tag": tag,
        "collection_id": collection_id,
        "search": search or "",
    }

    print(f"[sync] Raindrop items filtrados: {metrics['fetched']}")
    print(f"[merge] union deduplicada: {metrics['merged']}")

    if dry_run:
        print("[dry-run] no escribo en Notion. No actualizo cursor.")
        return metrics

    print("[notion] cargando indices existentes en KIT (por URL y por Raindrop ID)...")
    existing = existing_raindrops(db_kit)
    print(f"[notion] {len(existing['by_raindrop_id'])} bookmarks Raindrop, {len(existing['by_url'])} con URL")

    total = len(merged)
    for idx, item in enumerate(merged, 1):
        for attempt in range(5):
            try:
                action, _page_id = upsert_raindrop_to_kit(db_kit, item, existing)
                metrics[action] += 1
                break
            except Exception as exc:
                if attempt == 4:
                    metrics["errors"] += 1
                    print(f"[err {idx}/{total}] {item['title'][:80]}: {exc}")
                time.sleep(2 + attempt)
        time.sleep(0.35)
        if idx % 25 == 0:
            print(f"[progress] {idx}/{total} created={metrics['created']} updated={metrics['updated']} errors={metrics['errors']}")

    if metrics["errors"] == 0:
        mark_seen_for(collection_id, tag, sync_started, search)
        print(f"[cursor] Raindrop avanzado a {sync_started}")
    else:
        print("[cursor] cursor NO actualizado (hubo errores; reintenta para no perder items)")

    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Raindrop.io -> KIT via REST API")
    parser.add_argument("--full", action="store_true", help="Ignora cursor incremental")
    parser.add_argument("--limit", type=int, default=None, help="Procesa solo N items")
    parser.add_argument("--max-pages", type=int, default=None, help="Tope de paginas REST (50 items/pagina)")
    parser.add_argument("--dry-run", action="store_true", help="No escribe en Notion ni actualiza cursor")
    args = parser.parse_args()

    metrics = run_sync(full=args.full, limit=args.limit, dry_run=args.dry_run, max_pages=args.max_pages)
    print("\n=== SYNC RAINDROP COMPLETADO ===")
    print(f"  tag:          {metrics['tag']}")
    print(f"  collection:   {metrics['collection_id']}")
    print(f"  search:       {metrics['search'] or '(client-side tag filter)'}")
    print(f"  fetched:      {metrics['fetched']}")
    print(f"  merged:       {metrics['merged']}")
    print(f"  created:      {metrics['created']}")
    print(f"  updated:      {metrics['updated']}")
    print(f"  errors:       {metrics['errors']}")
    return 0 if metrics["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
