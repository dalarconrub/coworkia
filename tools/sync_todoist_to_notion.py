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

def _first_existing_prop(schema_set: set[str], names: list[str]) -> str | None:
    for n in names:
        if n in schema_set:
            return n
    return None

def _prop_type(prop_types: dict[str, str], name: str) -> str:
    return prop_types.get(name, "")

def _set_rich_text(props: dict, key: str, value: str) -> None:
    if value is None:
        return
    value = str(value).strip()
    if not value:
        return
    props[key] = {"rich_text": [{"text": {"content": value[:2000]}}]}

def _set_number(props: dict, key: str, value) -> None:
    if value is None:
        return
    try:
        n = float(value)
    except Exception:
        return
    props[key] = {"number": n}

def _set_checkbox(props: dict, key: str, value: bool) -> None:
    props[key] = {"checkbox": bool(value)}

def _set_date(props: dict, key: str, value: str) -> None:
    if not value:
        return
    props[key] = {"date": {"start": value}}


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

    db_info = get_database_info(db_id, object_type="data_source")
    schema = db_info.get("properties", [])
    schema_set = set(schema or [])
    prop_types = db_info.get("property_types", {}) or {}
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
        desc = (task.get("description", "") or "").strip()
        project_id = str(task.get("project_id") or "").strip()
        section_id = str(task.get("section_id") or "").strip()
        parent_id = str(task.get("parent_id") or "").strip()
        creator_id = str(task.get("creator_id") or "").strip()
        created_at = str(task.get("created_at") or "").strip()
        comment_count = task.get("comment_count", None)
        order = task.get("order", None)
        due = task.get("due") or {}
        deadline = task.get("deadline") or {}
        due_date = (due.get("date") or "").strip()
        due_timezone = (due.get("timezone") or "").strip()
        due_string = (due.get("string") or "").strip()
        is_recurring = bool(due.get("is_recurring", False))
        deadline_date = (deadline.get("date") or "").strip()
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
        if desc:
            desc_prop = _first_existing_prop(schema_set, ["Descripcion", "Descripción", "Description"])
            if desc_prop:
                props[desc_prop] = {"rich_text": [{"text": {"content": desc[:2000]}}]}

        # Mapeos adicionales (solo si existen propiedades en Notion)
        # IDs de estructura
        for candidates, val in [
            (["Todoist Project ID", "Todoist Proyecto ID", "Proyecto Todoist ID"], project_id),
            (["Todoist Section ID", "Todoist Seccion ID", "Seccion Todoist ID"], section_id),
            (["Todoist Parent ID", "Parent ID", "Todoist Padre ID"], parent_id),
            (["Todoist Creator ID", "Creator ID", "Todoist Creador ID"], creator_id),
        ]:
            key = _first_existing_prop(schema_set, candidates)
            if key and val:
                ptype = _prop_type(prop_types, key)
                if ptype == "number":
                    _set_number(props, key, val)
                else:
                    _set_rich_text(props, key, val)

        # Timestamps
        created_key = _first_existing_prop(schema_set, ["Creada", "Created at", "Todoist Created at", "Creada en"])
        if created_key and created_at:
            # Notion date acepta ISO8601; si la propiedad no es date, guardamos texto.
            if _prop_type(prop_types, created_key) == "date":
                _set_date(props, created_key, created_at)
            else:
                _set_rich_text(props, created_key, created_at)

        # Due / Deadline separados si existen
        due_key = _first_existing_prop(schema_set, ["Due", "Fecha due", "Fecha (due)", "Fecha Todoist", "Due date"])
        if due_key and due_date:
            if _prop_type(prop_types, due_key) == "date":
                _set_date(props, due_key, due_date)
            else:
                _set_rich_text(props, due_key, due_date)

        deadline_key = _first_existing_prop(schema_set, ["Deadline", "Vencimiento", "Fecha límite", "Fecha limite", "Deadline date"])
        if deadline_key and deadline_date:
            if _prop_type(prop_types, deadline_key) == "date":
                _set_date(props, deadline_key, deadline_date)
            else:
                _set_rich_text(props, deadline_key, deadline_date)

        # Campos de due extra
        tz_key = _first_existing_prop(schema_set, ["Timezone", "Zona horaria", "Todoist Timezone"])
        if tz_key and due_timezone:
            _set_rich_text(props, tz_key, due_timezone)
        due_string_key = _first_existing_prop(schema_set, ["Due string", "Texto due", "Todoist Due string"])
        if due_string_key and due_string:
            _set_rich_text(props, due_string_key, due_string)
        recurring_key = _first_existing_prop(schema_set, ["Recurrencia", "Recurring", "Es recurrente", "Todoist Recurring"])
        if recurring_key:
            if _prop_type(prop_types, recurring_key) == "checkbox":
                _set_checkbox(props, recurring_key, is_recurring)
            else:
                _set_rich_text(props, recurring_key, "Sí" if is_recurring else "No")

        # Conteos/orden (si existen)
        cc_key = _first_existing_prop(schema_set, ["Comentarios", "Comment count", "Todoist Comment count"])
        if cc_key and comment_count is not None:
            if _prop_type(prop_types, cc_key) == "number":
                _set_number(props, cc_key, comment_count)
            else:
                _set_rich_text(props, cc_key, str(comment_count))

        order_key = _first_existing_prop(schema_set, ["Orden", "Order", "Todoist Order"])
        if order_key and order is not None:
            if _prop_type(prop_types, order_key) == "number":
                _set_number(props, order_key, order)
            else:
                _set_rich_text(props, order_key, str(order))

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
