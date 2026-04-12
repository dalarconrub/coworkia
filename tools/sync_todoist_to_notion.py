"""
Sincroniza tareas activas de Todoist a la BD NOTION `TODOIST-TAREAS` (B0A-INX).
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.todoist_tools import get_tasks, get_projects, classify_mar_type
from tools.notion_tools import query_data_source, create_page, update_page_properties


def _todoist_project_map() -> dict[str, str]:
    return {p["id"]: p.get("name", "") for p in get_projects()}


def _find_existing(todoist_id: str, db_id: str) -> dict | None:
    filter_obj = {
        "property": "Todoist ID",
        "rich_text": {"equals": todoist_id},
    }
    rows = query_data_source(db_id, filter_obj=filter_obj)
    return rows[0] if rows else None


def _date_from_task(task: dict) -> str | None:
    due = task.get("due") or {}
    if due.get("date"):
        return due["date"]
    deadline = task.get("deadline") or {}
    return deadline.get("date")


def main() -> int:
    db_id = os.getenv("TODOIST_DB_TAREAS")
    if not db_id:
        print("Falta TODOIST_DB_TAREAS en .env")
        return 2

    projects = _todoist_project_map()
    tasks = get_tasks(include_excluded=True)
    synced = 0

    for task in tasks:
        todoist_id = str(task.get("id"))
        nombre = task.get("content", "").strip() or "(sin titulo)"
        estado = "Activa"
        tipo = classify_mar_type(task)
        prioridad = str(task.get("priority", 1))
        fecha = _date_from_task(task)
        proj_name = projects.get(task.get("project_id", ""), "")
        labels = task.get("labels", []) or []

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

        existing = _find_existing(todoist_id, db_id)
        if existing:
            update_page_properties(existing["id"], props)
        else:
            create_page(parent_id=db_id, title=nombre, properties=props, is_data_source=True)
        synced += 1

    print(f"Tareas sincronizadas: {synced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
