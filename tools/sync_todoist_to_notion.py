"""
Sincroniza tareas activas de Todoist a la BD NOTION `TODOIST-TAREAS` (B0A-INX).
"""

import os
import requests
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.todoist_tools import get_tasks, get_projects, classify_mar_type, _headers, BASE_URL
from tools.notion_tools import (
    query_data_source,
    create_page,
    update_page_properties,
    extract_property_value,
    get_database_info,
)


def _todoist_project_map() -> dict[str, str]:
    return {p["id"]: p.get("name", "") for p in get_projects()}


def _existing_map(db_id: str) -> dict[str, str]:
    rows = query_data_source(db_id)
    mapping = {}
    for r in rows:
        props = r.get("properties", {})
        tid = extract_property_value(props.get("Todoist ID", {}))
        if tid:
            mapping[tid] = r["id"]
    return mapping


def _date_from_task(task: dict) -> str | None:
    due = task.get("due") or {}
    if due.get("date"):
        return due["date"]
    deadline = task.get("deadline") or {}
    return deadline.get("date")

def _todoist_section_map() -> dict[str, str]:
    # Todoist API v1 sections
    try:
        resp = requests.get(f"{BASE_URL}/sections", headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        items = data["results"] if isinstance(data, dict) and "results" in data else data
        return {s.get("id"): s.get("name", "") for s in items if isinstance(s, dict)}
    except Exception:
        return {}

def _has_prop(schema: dict, name: str) -> bool:
    return name in schema


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Sync Todoist -> Notion")
    parser.add_argument("--limit", type=int, default=None, help="Limitar número de tareas procesadas")
    parser.add_argument("--skip-completed", action="store_true", help="No marcar completadas")
    parser.add_argument("--offset", type=int, default=0, help="Desplazamiento en la lista de tareas")
    parser.add_argument("--save-active", action="store_true", help="Guardar IDs activos en artifacts")
    parser.add_argument("--finalize-completed", action="store_true", help="Marcar completadas usando artifacts")
    parser.add_argument("--finalize-limit", type=int, default=None, help="Limitar completadas por ejecución")
    args = parser.parse_args()

    db_id = os.getenv("TODOIST_DB_TAREAS")
    if not db_id:
        print("Falta TODOIST_DB_TAREAS en .env")
        return 2

    schema = get_database_info(db_id, object_type="data_source").get("properties", [])
    schema_set = set(schema or [])
    projects = _todoist_project_map()
    sections = _todoist_section_map()
    tasks = get_tasks(include_excluded=False)
    if args.offset:
        tasks = tasks[args.offset:]
    if args.limit:
        tasks = tasks[:args.limit]
    existing = _existing_map(db_id)
    synced = 0
    active_ids = set()

    for task in tasks:
        todoist_id = str(task.get("id"))
        active_ids.add(todoist_id)
        nombre = task.get("content", "").strip() or "(sin titulo)"
        estado = "Activa"
        tipo = classify_mar_type(task)
        prioridad = str(task.get("priority", 1))
        fecha = _date_from_task(task)
        proj_name = projects.get(task.get("project_id", ""), "")
        labels = task.get("labels", []) or []
        section_name = sections.get(task.get("section_id", ""), "")

        props = {
            "Tarea": {"title": [{"text": {"content": nombre}}]},
            "Todoist ID": {"rich_text": [{"text": {"content": todoist_id}}]},
            "Estado": {"select": {"name": estado}},
            "Tipo MAR": {"select": {"name": tipo}},
            "Prioridad": {"select": {"name": prioridad}},
            "Proyecto Todoist": {"rich_text": [{"text": {"content": proj_name}}]},
        }
        if fecha:
            props["Fecha"] = {"date": {"start": fecha}}
        if labels:
            props["Labels"] = {"multi_select": [{"name": l} for l in labels]}
        if task.get("url"):
            props["URL"] = {"url": task["url"]}
        if section_name and _has_prop(schema_set, "Seccion Todoist"):
            props["Seccion Todoist"] = {"rich_text": [{"text": {"content": section_name}}]}

        page_id = existing.get(todoist_id)
        if page_id:
            update_page_properties(page_id, props)
        else:
            create_page(parent_id=db_id, title=nombre, properties=props, is_data_source=True)
        synced += 1

    # Guardar activos para batch
    if args.save_active:
        os.makedirs("artifacts", exist_ok=True)
        path = os.path.join("artifacts", "todoist_active_ids.txt")
        mode = "a" if args.offset else "w"
        with open(path, mode, encoding="utf-8") as fh:
            for tid in sorted(active_ids):
                fh.write(f"{tid}\n")

    # Marcar completadas usando artifacts (batch finalize)
    if args.finalize_completed and existing:
        path = os.path.join("artifacts", "todoist_active_ids.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                active_from_file = {line.strip() for line in fh if line.strip()}
        else:
            active_from_file = active_ids
        processed = 0
        for tid, page_id in existing.items():
            if tid not in active_from_file:
                update_page_properties(page_id, {"Estado": {"select": {"name": "Completada"}}})
                processed += 1
                if args.finalize_limit and processed >= args.finalize_limit:
                    break
        # limpiar archivo tras finalizar
        if os.path.exists(path) and not args.finalize_limit:
            os.remove(path)

    print(f"Tareas sincronizadas: {synced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
