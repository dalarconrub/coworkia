"""
Wrappers para la API REST v2 de Todoist.
Documentación: https://developer.todoist.com/rest/v2/
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
BASE_URL = "https://api.todoist.com/api/v1"
SYNC_URL = "https://api.todoist.com/api/v1/sync"

Z_PROJECTS: dict[str, str] = {
    "6Mv5F76GQq3p699F": "Z-INBOX",
    "6JM9X2GhWRgR9M7v": "Z-TRASH",
    "6QR2xC8R9QjQgjqx": "Z-INBOXS",
    "6H3rFRr2HMhXxhXC": "Z-B01_TODOITS",
    "6MxJ3VRPhPP8FqW3": "Z-LIB",
}

# Proyectos excluidos de todas las consultas operativas por defecto.
PROYECTOS_EXCLUIDOS: set[str] = set(Z_PROJECTS.keys())


def _headers() -> dict:
    return {"Authorization": f"Bearer {TODOIST_API_KEY}"}


def _is_z_project_name(name: str | None) -> bool:
    """Detecta proyectos de cuarentena/staging por prefijo operativo Z."""
    return (name or "").strip().upper().startswith("Z")


def get_excluded_project_ids() -> set[str]:
    """Devuelve proyectos excluidos por defecto: lista histórica + nombres Z*."""
    excluded = set(PROYECTOS_EXCLUIDOS)
    for project in get_projects():
        if _is_z_project_name(project.get("name")):
            excluded.add(project["id"])
    return excluded


def is_excluded_project_id(project_id: str | None) -> bool:
    """Indica si un proyecto queda fuera del flujo operativo normal."""
    return bool(project_id) and project_id in get_excluded_project_ids()


# ─── TAREAS ───────────────────────────────────────────────────────────────────

def get_tasks(filter_str: str = None, project_id: str = None, include_excluded: bool = False) -> list[dict]:
    """Obtiene tareas con paginación completa. Puede usar filtros en sintaxis Todoist."""
    params = {"limit": 200}
    endpoint = f"{BASE_URL}/tasks"
    if filter_str:
        endpoint = f"{BASE_URL}/tasks/filter"
        params["query"] = filter_str
    elif project_id:
        params["project_id"] = project_id

    tareas = []
    while True:
        resp = requests.get(endpoint, headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        batch = data["results"] if isinstance(data, dict) and "results" in data else data
        tareas.extend(batch)
        cursor = data.get("next_cursor") if isinstance(data, dict) else None
        if not cursor:
            break
        params["cursor"] = cursor

    if include_excluded:
        return tareas

    excluded_project_ids = get_excluded_project_ids()
    return [t for t in tareas if t.get("project_id") not in excluded_project_ids]


def get_z_tasks(project_id: str = None) -> list[dict]:
    """Obtiene tareas de los proyectos Z-* excluidos del flujo operativo normal."""
    if project_id:
        if not is_excluded_project_id(project_id):
            return []
        return [t for t in get_tasks(project_id=project_id, include_excluded=True) if t.get("project_id") == project_id]

    excluded_project_ids = get_excluded_project_ids()
    return [t for t in get_tasks(include_excluded=True) if t.get("project_id") in excluded_project_ids]


def create_task(
    content: str,
    description: str = None,
    project_id: str = None,
    due_string: str = None,
    due_date: str = None,       # formato YYYY-MM-DD
    due_datetime: str = None,   # formato ISO8601 (para Eventos con hora)
    deadline_date: str = None,  # formato YYYY-MM-DD (para Logros)
    priority: int = 1,          # 1=normal, 2=medium, 3=high, 4=urgent
    labels: list[str] = None,
    is_recurring: bool = False,
    recurring_string: str = None,  # ej: "every day", "every monday"
) -> dict:
    """
    Crea una tarea en Todoist.

    Para crear correctamente según sistema MAR:
    - Idea:   sin due_date, sin due_datetime
    - Hábito: recurring_string (ej: "every day"), aunque tenga hora
    - Evento: due_datetime (con hora exacta), no recurring
    - Logro:  deadline_date (sin hora), no recurring
    - Tarea:  due_date (sin hora), no recurring, sin deadline
    """
    data = {"content": content, "priority": priority}

    if description:
        data["description"] = description
    if project_id:
        data["project_id"] = project_id
    if labels:
        data["labels"] = labels

    # Gestión de fecha/hora según tipo MAR
    if due_datetime:
        data["due_datetime"] = due_datetime  # Evento
    elif due_date:
        data["due_date"] = due_date          # Tarea, salvo que tambien haya deadline
    elif due_string:
        data["due_string"] = due_string

    if is_recurring and recurring_string:
        data["due_string"] = recurring_string  # Hábito
    if deadline_date:
        data["deadline_date"] = deadline_date

    resp = requests.post(f"{BASE_URL}/tasks", headers=_headers(), json=data)
    resp.raise_for_status()
    return resp.json()


def update_task(task_id: str, **kwargs) -> dict:
    """Actualiza campos de una tarea existente."""
    resp = requests.post(
        f"{BASE_URL}/tasks/{task_id}",
        headers=_headers(),
        json=kwargs
    )
    resp.raise_for_status()
    return resp.json()


def get_task(task_id: str) -> dict:
    """Obtiene una tarea activa por ID."""
    resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def close_task(task_id: str) -> bool:
    """Marca una tarea como completada."""
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/close", headers=_headers())
    resp.raise_for_status()
    return resp.status_code == 204


def move_task(
    task_id: str,
    project_id: str = None,
    section_id: str = None,
    parent_id: str = None,
) -> dict:
    """Mueve una tarea a otro proyecto, sección o tarea padre.

    Todoist documenta el movimiento de items en la Sync API (`item_move`), no
    como mutación REST sobre `/tasks/{id}/move`. Usamos Sync API para evitar los
    403 observados con el endpoint antiguo.
    """
    targets = {
        "project_id": project_id,
        "section_id": section_id,
        "parent_id": parent_id,
    }
    data = {key: value for key, value in targets.items() if value}
    if len(data) != 1:
        raise ValueError("Debe indicar exactamente uno de: project_id, section_id o parent_id")
    cmd_uuid = str(uuid4())
    command = {
        "type": "item_move",
        "uuid": cmd_uuid,
        "args": {
            "id": task_id,
            **data,
        },
    }
    resp = requests.post(
        SYNC_URL,
        headers=_headers(),
        data={"commands": json.dumps([command])},
    )
    resp.raise_for_status()
    payload = resp.json()
    sync_status = payload.get("sync_status", {}) if isinstance(payload, dict) else {}
    status = sync_status.get(cmd_uuid)
    if status != "ok":
        raise requests.HTTPError(f"Todoist item_move fallo: {status!r}", response=resp)
    return payload


def delete_task(task_id: str) -> bool:
    """Elimina una tarea."""
    resp = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=_headers())
    resp.raise_for_status()
    return resp.status_code == 204


# ─── PROYECTOS ────────────────────────────────────────────────────────────────

def get_projects() -> list[dict]:
    """Obtiene todos los proyectos."""
    resp = requests.get(f"{BASE_URL}/projects", headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


def get_project(project_id: str) -> dict:
    """Obtiene un proyecto por ID."""
    resp = requests.get(f"{BASE_URL}/projects/{project_id}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def create_project(name: str, parent_id: str = None) -> dict:
    """Crea un proyecto Todoist en raíz o bajo un padre dado."""
    payload = {"name": name}
    if parent_id:
        payload["parent_id"] = parent_id
    resp = requests.post(f"{BASE_URL}/projects", headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


# ─── FILTROS MAR ──────────────────────────────────────────────────────────────

MAR_FILTERS = {
    "idea":   "no date & no deadline",
    "logro":  "!recurring & no time & !no deadline",
    "meta":   "!recurring & no time & !no deadline",  # alias legacy de logro
    "habito": "recurring",
    "tarea":  "!recurring & no time & no deadline",
    "evento": "!recurring & !no time",
}

HORIZON_FILTERS = {
    "hoy":    "overdue | due before: +1 day",
    "1dia":   "due after: yesterday & due before: +2day",
    "1semana":"due after: today & due before: +7day",
    "1mes":   "due after: +7 days & due before: +30 days",
    "1año":   "due after: +30 days & due before: +365 days",
}


def get_tasks_by_mar_type(mar_type: str) -> list[dict]:
    """
    Obtiene tareas filtradas por tipo MAR.
    mar_type: 'idea' | 'logro' | 'habito' | 'tarea' | 'evento'

    La clasificación MAR final se hace localmente porque Todoist no distingue
    el modelo conceptual Logro/Tarea de forma nativa en todos los casos.
    """
    mar_type = normalize_mar_type(mar_type)
    if mar_type not in MAR_FILTERS:
        raise ValueError(f"Tipo MAR desconocido: {mar_type}. Use: {list(MAR_FILTERS.keys())}")
    return [task for task in get_tasks() if classify_mar_type(task) == mar_type]


def get_tasks_by_horizon(horizon: str) -> list[dict]:
    """
    Obtiene tareas por horizonte temporal MAR.
    horizon: 'hoy' | '1dia' | '1semana' | '1mes' | '1año'
    """
    filter_str = HORIZON_FILTERS.get(horizon.lower())
    if not filter_str:
        raise ValueError(f"Horizonte desconocido: {horizon}. Use: {list(HORIZON_FILTERS.keys())}")
    return get_tasks(filter_str=filter_str)


# ─── CLASIFICADOR MAR ─────────────────────────────────────────────────────────

def normalize_mar_type(mar_type: str) -> str:
    """Normaliza aliases historicos de tipos MAR."""
    value = (mar_type or "").strip().lower()
    if value == "meta":
        return "logro"
    return value


def classify_mar_type(task: dict) -> str:
    """
    Determina el tipo MAR de una tarea existente en Todoist
    basándose en sus propiedades.
    """
    due = task.get("due")
    deadline = task.get("deadline")

    due_date = (due or {}).get("date", "") or ""
    is_recurring = bool((due or {}).get("is_recurring", False))
    has_time = "T" in due_date
    has_deadline = bool(deadline and deadline.get("date"))

    # Reglas MAR (David, 2026-05-10):
    # - Hábito: recurrente, tenga o no hora.
    # - Evento: no recurrente con hora.
    # - Logro: no recurrente, sin hora, con deadline.
    # - Tarea: no recurrente, sin hora, sin deadline, con due date.
    # - Idea: nada de lo anterior.
    if is_recurring:
        return "habito"
    if has_time:
        return "evento"
    if has_deadline:
        return "logro"
    if due and not has_time:
        return "tarea"
    return "idea"
