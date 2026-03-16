"""
Wrappers para la API REST v2 de Todoist.
Documentación: https://developer.todoist.com/rest/v2/
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
BASE_URL = "https://api.todoist.com/rest/v2"


def _headers() -> dict:
    return {"Authorization": f"Bearer {TODOIST_API_KEY}"}


# ─── TAREAS ───────────────────────────────────────────────────────────────────

def get_tasks(filter_str: str = None, project_id: str = None) -> list[dict]:
    """Obtiene tareas. Puede usar filtros en sintaxis Todoist."""
    params = {}
    if filter_str:
        params["filter"] = filter_str
    if project_id:
        params["project_id"] = project_id

    resp = requests.get(f"{BASE_URL}/tasks", headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def create_task(
    content: str,
    description: str = None,
    project_id: str = None,
    due_string: str = None,
    due_date: str = None,       # formato YYYY-MM-DD
    due_datetime: str = None,   # formato ISO8601 (para Eventos con hora)
    priority: int = 1,          # 1=normal, 2=medium, 3=high, 4=urgent
    labels: list[str] = None,
    is_recurring: bool = False,
    recurring_string: str = None,  # ej: "every day", "every monday"
) -> dict:
    """
    Crea una tarea en Todoist.

    Para crear correctamente según sistema MAR:
    - Idea:   sin due_date, sin due_datetime
    - Meta:   due_date (sin hora), no recurring
    - Hábito: recurring_string (ej: "every day"), sin due_datetime
    - Tarea:  due_date (sin hora, con deadline)
    - Evento: due_datetime (con hora exacta)
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
        data["due_date"] = due_date          # Meta o Tarea
    elif due_string:
        data["due_string"] = due_string

    if is_recurring and recurring_string:
        data["due_string"] = recurring_string  # Hábito

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


def close_task(task_id: str) -> bool:
    """Marca una tarea como completada."""
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/close", headers=_headers())
    resp.raise_for_status()
    return resp.status_code == 204


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
    return resp.json()


def get_project(project_id: str) -> dict:
    """Obtiene un proyecto por ID."""
    resp = requests.get(f"{BASE_URL}/projects/{project_id}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


# ─── FILTROS MAR ──────────────────────────────────────────────────────────────

MAR_FILTERS = {
    "idea":   "no date & no deadline",
    "meta":   "!recurring & !!no time & !no deadline",
    "habito": "recurring & no time & no deadline",
    "tarea":  "no time & !no deadline",
    "evento": "!no time",
}

HORIZON_FILTERS = {
    "hoy":    "(!#Z-* & !search:*) & (overdue | due before: +1 day)",
    "1dia":   "(!#Z-* & !search:*) & due after: yesterday & due before: +2day",
    "1semana":"(!#Z-* & !search:*) & due after: today & due before: +7day",
    "1mes":   "(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)",
    "1año":   "(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)",
}


def get_tasks_by_mar_type(mar_type: str) -> list[dict]:
    """
    Obtiene tareas filtradas por tipo MAR.
    mar_type: 'idea' | 'meta' | 'habito' | 'tarea' | 'evento'
    """
    filter_str = MAR_FILTERS.get(mar_type.lower())
    if not filter_str:
        raise ValueError(f"Tipo MAR desconocido: {mar_type}. Use: {list(MAR_FILTERS.keys())}")
    return get_tasks(filter_str=filter_str)


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

def classify_mar_type(task: dict) -> str:
    """
    Determina el tipo MAR de una tarea existente en Todoist
    basándose en sus propiedades.
    """
    due = task.get("due")

    if not due:
        return "idea"

    is_recurring = due.get("is_recurring", False)
    has_time = "T" in due.get("datetime", "") if due.get("datetime") else False
    has_deadline = bool(due.get("date") or due.get("datetime"))

    if has_time:
        return "evento"
    if is_recurring and not has_time:
        return "habito"
    if not is_recurring and not has_time and has_deadline:
        # Meta: deadline pero sin hora, sin recurrencia
        # Tarea: también, pero en la práctica la distinción es conceptual
        # Meta = compromiso de un día específico
        return "meta"  # o "tarea" según contexto

    return "idea"
