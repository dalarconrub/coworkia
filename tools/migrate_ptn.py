"""
Migra las bases PTN (Proyectos, Tareas, Notas) entre data sources de Notion.
Preserva el contenido y re-mapea IDs de proyectos/tareas en campos de texto.
"""

import os
import sys
from typing import Any, Dict, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    query_data_source,
    get_database_info,
    create_page,
    extract_property_value,
)


def _schema_props(data_source_id: str) -> Dict[str, Dict[str, Any]]:
    info = get_database_info(data_source_id, object_type="data_source")
    raw = info.get("raw", {}) if isinstance(info, dict) else {}
    return raw.get("properties", {}) or {}


def _title_prop_name(schema: Dict[str, Dict[str, Any]]) -> str:
    for name, definition in schema.items():
        if isinstance(definition, dict) and "title" in definition:
            return name
    return "Name"


def _prop_type(definition: Dict[str, Any]) -> str:
    for key in definition.keys():
        return key
    return ""


def _as_multi_select(value: str) -> list[dict]:
    items = [v.strip() for v in (value or "").split(",") if v.strip()]
    return [{"name": item} for item in items]


def _number_from_value(prop: dict) -> float | None:
    if prop.get("type") == "number":
        return prop.get("number")
    try:
        return float(extract_property_value(prop))
    except Exception:
        return None


def _date_from_value(prop: dict) -> str | None:
    if prop.get("type") == "date":
        date_obj = prop.get("date") or {}
        return date_obj.get("start")
    value = extract_property_value(prop)
    return value or None


def _build_properties(
    src_page: dict,
    dst_schema: Dict[str, Dict[str, Any]],
    remap: Dict[str, str] | None = None,
    warn: list[str] | None = None,
) -> Dict[str, Any]:
    src_props = src_page.get("properties", {})
    props: Dict[str, Any] = {}
    remap = remap or {}
    warn = warn if warn is not None else []

    title_name = _title_prop_name(dst_schema)
    title_value = ""
    if title_name in src_props:
        title_value = extract_property_value(src_props[title_name])
    if not title_value:
        # Buscar cualquier title del source
        for prop in src_props.values():
            if prop.get("type") == "title":
                title_value = extract_property_value(prop)
                break
    if not title_value:
        title_value = "(sin titulo)"

    props[title_name] = {"title": [{"text": {"content": title_value}}]}

    for name, definition in dst_schema.items():
        if name == title_name:
            continue
        if name not in src_props:
            continue

        src_prop = src_props[name]
        ptype = _prop_type(definition)
        raw_value = extract_property_value(src_prop)

        if name in ("Proyecto", "Tarea") and raw_value in remap:
            raw_value = remap[raw_value]

        if ptype == "rich_text":
            if raw_value:
                props[name] = {"rich_text": [{"text": {"content": raw_value}}]}
            elif name == "Tarea":
                warn.append(f"Nota sin tarea en source: {src_page.get('id')}")
                props[name] = {"rich_text": [{"text": {"content": "MIGRACION: REVISAR (sin tarea)"}}]}
        elif ptype == "select":
            if raw_value:
                props[name] = {"select": {"name": raw_value}}
        elif ptype == "multi_select":
            items = []
            if src_prop.get("type") == "multi_select":
                items = [{"name": i["name"]} for i in src_prop.get("multi_select", []) if i.get("name")]
            else:
                items = _as_multi_select(raw_value)
            if items:
                props[name] = {"multi_select": items}
        elif ptype == "date":
            date_value = _date_from_value(src_prop)
            if date_value:
                props[name] = {"date": {"start": date_value}}
        elif ptype == "number":
            number_value = _number_from_value(src_prop)
            if number_value is not None:
                props[name] = {"number": number_value}
        elif ptype == "url":
            if raw_value:
                props[name] = {"url": raw_value}

    return props


def _migrate(
    src_id: str,
    dst_id: str,
    remap: Dict[str, str] | None = None,
) -> Tuple[int, Dict[str, str], list[str]]:
    dst_schema = _schema_props(dst_id)
    rows = query_data_source(src_id)
    new_map: Dict[str, str] = {}
    warnings: list[str] = []

    for row in rows:
        props = _build_properties(row, dst_schema, remap=remap, warn=warnings)
        created = create_page(parent_id=dst_id, title="MIGRACION", properties=props, is_data_source=True)
        new_map[row["id"]] = created["id"]

    return len(rows), new_map, warnings


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Migrar PTN entre data sources")
    parser.add_argument("--src-proyectos", default=os.getenv("NOTION_DS_PROYECTOS"))
    parser.add_argument("--src-tareas", default=os.getenv("NOTION_DS_TAREAS"))
    parser.add_argument("--src-notas", default=os.getenv("NOTION_DS_NOTAS"))
    parser.add_argument("--dst-proyectos", required=True)
    parser.add_argument("--dst-tareas", required=True)
    parser.add_argument("--dst-notas", required=True)
    args = parser.parse_args()

    src_proy = args.src_proyectos
    src_tar = args.src_tareas
    src_not = args.src_notas
    dst_proy = args.dst_proyectos
    dst_tar = args.dst_tareas
    dst_not = args.dst_notas

    if not all([src_proy, src_tar, src_not]):
        print("Faltan variables de entorno de origen:")
        print("  NOTION_DS_PROYECTOS, NOTION_DS_TAREAS, NOTION_DS_NOTAS")
        return 2

    print("Migrando PTN-Proyectos...")
    p_count, proj_map, p_warn = _migrate(src_proy, dst_proy)
    print(f"  Copiados: {p_count}")

    print("Migrando PTN-Tareas...")
    t_count, task_map, t_warn = _migrate(src_tar, dst_tar, remap=proj_map)
    print(f"  Copiados: {t_count}")

    print("Migrando PTN-Notas...")
    n_count, _, n_warn = _migrate(src_not, dst_not, remap={**proj_map, **task_map})
    print(f"  Copiados: {n_count}")

    warnings = p_warn + t_warn + n_warn
    if warnings:
        print("\nAdvertencias:")
        for w in warnings:
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
