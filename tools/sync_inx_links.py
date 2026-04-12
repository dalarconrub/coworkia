"""
Sincroniza la base puente INX-ENLACES a partir de TODOIST-TAREAS, NOTION y OBSIDIAN.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    query_data_source,
    create_page,
    update_page_properties,
    extract_property_value,
)


def _existing_map(db_id: str) -> dict[str, str]:
    rows = query_data_source(db_id)
    mapping = {}
    for r in rows:
        key = extract_property_value(r.get("properties", {}).get("Clave", {}))
        if key:
            mapping[key] = r["id"]
    return mapping


def _upsert(db_id: str, key: str, title: str, props: dict, existing: dict) -> None:
    props["Clave"] = {"rich_text": [{"text": {"content": key}}]}
    props["Elemento"] = {"title": [{"text": {"content": title}}]}
    if key in existing:
        update_page_properties(existing[key], props)
    else:
        create_page(parent_id=db_id, title=title, properties=props, is_data_source=True)


def _sync_todoist(db_links: str, db_todoist: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_todoist)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        tid = extract_property_value(props.get("Todoist ID", {}))
        if not tid:
            continue
        title = extract_property_value(props.get("Tarea", {})) or f"Todoist {tid}"
        data = {
            "Fuente": {"select": {"name": "Todoist"}},
            "Todoist ID": {"rich_text": [{"text": {"content": tid}}]},
        }
        for rel, name in [("Area", "Area"), ("Bloque", "Bloque"), ("Contexto", "Contexto")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        _upsert(db_links, f"todoist:{tid}", title, data, existing)
        n += 1
    return n


def _sync_ptn_log(db_links: str, db_notion: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_notion)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        source_id = extract_property_value(props.get("Fuente ID", {}))
        if not source_id:
            continue
        title = extract_property_value(props.get("Evento", {})) or source_id
        data = {
            "Fuente": {"select": {"name": "Notion"}},
        }
        for rel, name in [("PTN Proyecto", "PTN Proyecto"), ("PTN Tarea", "PTN Tarea"), ("PTN Nota", "PTN Nota")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        for rel, name in [("Area", "Area"), ("Bloque", "Bloque"), ("Contexto", "Contexto")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        _upsert(db_links, f"ptn:{source_id}", title, data, existing)
        n += 1
    return n


def _sync_obsidian(db_links: str, db_obsidian: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_obsidian)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        path = extract_property_value(props.get("Ruta", {}))
        if not path:
            continue
        title = extract_property_value(props.get("Evento", {})) or path
        data = {
            "Fuente": {"select": {"name": "Obsidian"}},
            "Obsidian Ruta": {"rich_text": [{"text": {"content": path}}]},
        }
        for rel, name in [("Area", "Area"), ("Bloque", "Bloque"), ("Contexto", "Contexto")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        _upsert(db_links, f"obsidian:{path}", title, data, existing)
        n += 1
    return n


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Sync INX links")
    parser.add_argument("--source", choices=["todoist", "notion", "obsidian", "all"], default="all")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    db_links = os.getenv("NOTION_DB_INX")
    db_todoist = os.getenv("TODOIST_DB_TAREAS")
    db_notion = os.getenv("NOTION_DB")
    db_obsidian = os.getenv("OBSIDIAN_DB")
    if not all([db_links, db_todoist, db_notion, db_obsidian]):
        print("Faltan IDs en .env: NOTION_DB_INX, TODOIST_DB_TAREAS, NOTION_DB, OBSIDIAN_DB")
        return 2

    n1 = n2 = n3 = 0
    if args.source in ("todoist", "all"):
        existing = _existing_map(db_links)
        n1 = _sync_todoist(db_links, db_todoist, existing, args.limit)
    if args.source in ("notion", "all"):
        existing = _existing_map(db_links)
        n2 = _sync_ptn_log(db_links, db_notion, existing, args.limit)
    if args.source in ("obsidian", "all"):
        existing = _existing_map(db_links)
        n3 = _sync_obsidian(db_links, db_obsidian, existing, args.limit)
    print(f"INX enlaces sincronizados: todoist={n1} notion={n2} obsidian={n3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
