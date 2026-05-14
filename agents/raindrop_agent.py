"""
Agente Raindrop.io -> KIT.

Raindrop alimenta NOTION_DB_KIT como Information. No crea catalogo propio ni
filas raindrop:* en INX; las filas se materializan como kit:<page_id> via
sync_inx_links.py --source kit.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, query_data_source
from tools.raindrop_tools import MCP_ENDPOINT, list_collections, list_tags, user_info


def auth_check() -> str:
    try:
        user = user_info()
    except Exception as exc:
        return (
            "[ERROR] No se pudo conectar con Raindrop.io.\n"
            f"  Detalle: {exc}\n"
            "  Soluciones:\n"
            "    1) Verifica RAINDROP_ACCESS_TOKEN en .env\n"
            "    2) Usa el Test token de la App Management Console o un token OAuth REST\n"
            f"    3) Para clientes IA interactivos, endpoint MCP: {MCP_ENDPOINT}"
        )
    name = user.get("fullName") or user.get("email") or user.get("_id")
    return (
        f"[OK] Conectado a Raindrop.io como: {name}\n"
        f"  user_id: {user.get('_id')}\n"
        f"  pro: {user.get('pro')}\n"
        f"  mcp: {MCP_ENDPOINT}"
    )


def listar_tags(collection_id: int | None = None) -> str:
    tags = list_tags(collection_id)
    if not tags:
        return "Sin tags Raindrop detectados."
    lines = ["Tags Raindrop:"]
    for tag in sorted(tags, key=lambda t: str(t.get("_id", "")).lower()):
        lines.append(f"  - {tag.get('_id')} ({tag.get('count', 0)})")
    return "\n".join(lines)


def listar_collections() -> str:
    collections = list_collections()
    if not collections:
        return "Sin colecciones Raindrop detectadas."
    lines = ["Colecciones Raindrop:"]
    for col in sorted(collections, key=lambda c: str(c.get("title", "")).lower()):
        parent = (col.get("parent") or {}).get("$id")
        suffix = f" parent={parent}" if parent else ""
        lines.append(f"  - {col.get('_id')}: {col.get('title')} ({col.get('count', 0)}){suffix}")
    return "\n".join(lines)


def sync(full: bool = False, limit: int | None = None,
         dry_run: bool = False, max_pages: int | None = None) -> str:
    from tools.sync_raindrop_to_kit import run_sync
    metrics = run_sync(full=full, limit=limit, dry_run=dry_run, max_pages=max_pages)
    return (
        "\n=== SYNC RAINDROP COMPLETADO ===\n"
        f"  tag:          {metrics['tag']}\n"
        f"  collection:   {metrics['collection_id']}\n"
        f"  search:       {metrics['search'] or '(client-side tag filter)'}\n"
        f"  fetched:      {metrics['fetched']}\n"
        f"  merged:       {metrics['merged']}\n"
        f"  created:      {metrics['created']}\n"
        f"  updated:      {metrics['updated']}\n"
        f"  errors:       {metrics['errors']}"
    )


def _raindrop_rows(db_kit: str) -> list[dict]:
    rows = query_data_source(db_kit)
    out = []
    for row in rows:
        props = row.get("properties", {})
        if "Raindrop ID" not in props:
            continue
        if not extract_property_value(props["Raindrop ID"]):
            continue
        out.append(row)
    return out


def listar(subtipo: str | None = None, tag: str | None = None) -> str:
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_kit:
        return "[ERROR] Falta NOTION_DB_KIT en .env"
    rows = _raindrop_rows(db_kit)
    if subtipo:
        rows = [r for r in rows if extract_property_value(r["properties"].get("Subtipo", {})) == subtipo]
    if tag:
        rows = [r for r in rows if tag in (extract_property_value(r["properties"].get("Raindrop Tags", {})) or "")]
    if not rows:
        return "Sin bookmarks Raindrop en KIT que coincidan."
    lines = [f"=== KIT - Raindrop ({len(rows)}) ===\n"]
    for row in rows:
        props = row["properties"]
        title = extract_property_value(props.get("Titulo", {})) or extract_property_value(props.get("Título", {})) or "(sin titulo)"
        sub = extract_property_value(props.get("Subtipo", {})) or "?"
        tags = extract_property_value(props.get("Raindrop Tags", {})) or ""
        source = extract_property_value(props.get("Fuente / Autor", {})) or ""
        lines.append(f"  - [{sub}] {title[:70]}")
        meta = []
        if tags:
            meta.append(f"tags={tags}")
        if source:
            meta.append(f"de={source[:40]}")
        if meta:
            lines.append(f"    {', '.join(meta)}")
    return "\n".join(lines)


def estado() -> str:
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_kit:
        return "[ERROR] Falta NOTION_DB_KIT en .env"
    rows = _raindrop_rows(db_kit)
    if not rows:
        return "No hay bookmarks Raindrop catalogados en KIT todavia."

    by_sub: dict[str, int] = {}
    by_tag: dict[str, int] = {}
    for row in rows:
        props = row["properties"]
        sub = extract_property_value(props.get("Subtipo", {})) or "Sin subtipo"
        by_sub[sub] = by_sub.get(sub, 0) + 1
        tags_str = extract_property_value(props.get("Raindrop Tags", {})) or ""
        for tag in [s.strip() for s in tags_str.split(",") if s.strip()]:
            by_tag[tag] = by_tag.get(tag, 0) + 1

    lines = [f"=== ESTADO Raindrop en KIT ({len(rows)} bookmarks) ===\n", "Por subtipo:"]
    for key, value in sorted(by_sub.items(), key=lambda item: -item[1]):
        lines.append(f"  {key}: {value}")
    lines.append("\nPor tag de origen:")
    for key, value in sorted(by_tag.items(), key=lambda item: -item[1]):
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente Raindrop.io -> KIT")
    sub = parser.add_subparsers(dest="comando")

    sub.add_parser("auth-check", help="Verifica RAINDROP_ACCESS_TOKEN")
    sub.add_parser("list-tags", help="Lista tags de Raindrop")
    sub.add_parser("list-collections", help="Lista colecciones de Raindrop")

    p_sync = sub.add_parser("sync", help="Sync Raindrop -> KIT")
    p_sync.add_argument("--full", action="store_true", help="Ignora cursor incremental")
    p_sync.add_argument("--limit", type=int, default=None)
    p_sync.add_argument("--max-pages", type=int, default=None)
    p_sync.add_argument("--dry-run", action="store_true")

    p_list = sub.add_parser("listar", help="Lista bookmarks Raindrop catalogados en KIT")
    p_list.add_argument("--subtipo", default=None,
                        choices=["Artículo", "Newsletter", "Blog", "Vídeo", "Podcast", "Paper"])
    p_list.add_argument("--tag", default=None)

    sub.add_parser("estado", help="Resumen del catalogo Raindrop en KIT")

    args = parser.parse_args()
    if args.comando == "auth-check":
        print(auth_check())
    elif args.comando == "list-tags":
        print(listar_tags())
    elif args.comando == "list-collections":
        print(listar_collections())
    elif args.comando == "sync":
        print(sync(full=args.full, limit=args.limit, dry_run=args.dry_run, max_pages=args.max_pages))
    elif args.comando == "listar":
        print(listar(subtipo=args.subtipo, tag=args.tag))
    elif args.comando == "estado":
        print(estado())
    else:
        parser.print_help()
