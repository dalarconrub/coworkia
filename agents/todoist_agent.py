"""
Agente MAR para Todoist.

Entiende el sistema MAR (Meta-Acción-Resultado) y opera sobre Todoist
respetando la clasificación temporal: Idea, Meta, Hábito, Tarea, Evento.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.todoist_tools import (
    get_tasks,
    create_task,
    close_task,
    get_tasks_by_mar_type,
    get_tasks_by_horizon,
    get_projects,
    classify_mar_type,
    MAR_FILTERS,
    HORIZON_FILTERS,
)


# ─── CONSULTAS ────────────────────────────────────────────────────────────────

def resumen_hoy() -> str:
    """Genera un resumen de tareas para hoy según sistema MAR."""
    tareas_hoy = get_tasks_by_horizon("hoy")

    if not tareas_hoy:
        return "No hay tareas para hoy."

    # Clasificar por tipo MAR
    por_tipo: dict[str, list] = {
        "evento": [], "meta": [], "tarea": [],
        "habito": [], "idea": []
    }

    for t in tareas_hoy:
        tipo = classify_mar_type(t)
        por_tipo[tipo].append(t)

    lineas = [f"=== RESUMEN HOY ({len(tareas_hoy)} acciones) ===\n"]

    iconos = {
        "evento": "🗓️  EVENTOS",
        "meta":   "🎯 METAS",
        "tarea":  "📋 TAREAS",
        "habito": "🔁 HÁBITOS",
        "idea":   "💡 IDEAS",
    }

    for tipo, items in por_tipo.items():
        if items:
            lineas.append(f"\n{iconos[tipo]} ({len(items)})")
            for t in items:
                due = t.get("due", {})
                hora = ""
                if due and due.get("datetime"):
                    hora = f" [{due['datetime'][11:16]}]"
                prioridad = "(!)" if t.get("priority", 1) >= 3 else ""
                lineas.append(f"  • {t['content']}{hora} {prioridad}".strip())

    return "\n".join(lineas)


def listar_por_tipo(tipo: str) -> str:
    """Lista tareas de un tipo MAR específico."""
    tareas = get_tasks_by_mar_type(tipo)
    if not tareas:
        return f"No hay {tipo}s activos."

    lineas = [f"=== {tipo.upper()}S ({len(tareas)}) ==="]
    for t in tareas:
        due = t.get("due")
        fecha = f" → {due['date']}" if due else ""
        lineas.append(f"  • {t['content']}{fecha}")

    return "\n".join(lineas)


def estado_sistema() -> str:
    """Muestra el estado completo del sistema MAR por tipos."""
    lineas = ["=== ESTADO SISTEMA MAR ===\n"]
    iconos = {
        "idea": "💡", "meta": "🎯", "habito": "🔁", "tarea": "📋", "evento": "🗓️"
    }
    total = 0
    for tipo in ["evento", "meta", "tarea", "habito", "idea"]:
        tareas = get_tasks_by_mar_type(tipo)
        n = len(tareas)
        total += n
        lineas.append(f"  {iconos[tipo]} {tipo.capitalize():8} {n:3} acciones")

    lineas.append(f"\n  TOTAL: {total} acciones activas")
    return "\n".join(lineas)


# ─── CREACIÓN ─────────────────────────────────────────────────────────────────

def nueva_idea(content: str, description: str = None, project_id: str = None) -> dict:
    """
    Crea una Idea: sin fecha ni deadline.
    Captura de pensamiento sin compromiso temporal.
    """
    return create_task(content=content, description=description, project_id=project_id)


def nueva_meta(content: str, fecha: str, description: str = None, project_id: str = None) -> dict:
    """
    Crea una Meta: compromiso puntual de un día.
    fecha: YYYY-MM-DD
    Sin hora, sin recurrencia.
    """
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_date=fecha,
    )


def nuevo_habito(content: str, recurrencia: str, description: str = None, project_id: str = None) -> dict:
    """
    Crea un Hábito: recurrente sin deadline.
    recurrencia: ej "every day", "every monday", "every week"
    """
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        is_recurring=True,
        recurring_string=recurrencia,
    )


def nueva_tarea(content: str, deadline: str, description: str = None, project_id: str = None, priority: int = 1) -> dict:
    """
    Crea una Tarea: trabajo flexible con deadline.
    deadline: YYYY-MM-DD (sin hora)
    """
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_date=deadline,
        priority=priority,
    )


def nuevo_evento(content: str, datetime_iso: str, description: str = None, project_id: str = None) -> dict:
    """
    Crea un Evento: hora fija.
    datetime_iso: formato ISO8601, ej "2026-03-16T10:00:00"
    """
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_datetime=datetime_iso,
    )


# ─── CLI BÁSICO ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente MAR para Todoist")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("hoy", help="Resumen de hoy")
    subparsers.add_parser("estado", help="Estado del sistema MAR")

    p_listar = subparsers.add_parser("listar", help="Listar por tipo MAR")
    p_listar.add_argument("tipo", choices=list(MAR_FILTERS.keys()))

    p_idea = subparsers.add_parser("idea", help="Crear idea")
    p_idea.add_argument("content")

    p_meta = subparsers.add_parser("meta", help="Crear meta")
    p_meta.add_argument("content")
    p_meta.add_argument("fecha", help="YYYY-MM-DD")

    p_habito = subparsers.add_parser("habito", help="Crear hábito")
    p_habito.add_argument("content")
    p_habito.add_argument("recurrencia", help='ej: "every day"')

    p_tarea = subparsers.add_parser("tarea", help="Crear tarea")
    p_tarea.add_argument("content")
    p_tarea.add_argument("deadline", help="YYYY-MM-DD")

    p_evento = subparsers.add_parser("evento", help="Crear evento")
    p_evento.add_argument("content")
    p_evento.add_argument("datetime_iso", help='ej: "2026-03-16T10:00:00"')

    args = parser.parse_args()

    if args.comando == "hoy":
        print(resumen_hoy())
    elif args.comando == "estado":
        print(estado_sistema())
    elif args.comando == "listar":
        print(listar_por_tipo(args.tipo))
    elif args.comando == "idea":
        t = nueva_idea(args.content)
        print(f"Idea creada: {t['id']} — {t['content']}")
    elif args.comando == "meta":
        t = nueva_meta(args.content, args.fecha)
        print(f"Meta creada: {t['id']} — {t['content']} → {args.fecha}")
    elif args.comando == "habito":
        t = nuevo_habito(args.content, args.recurrencia)
        print(f"Hábito creado: {t['id']} — {t['content']}")
    elif args.comando == "tarea":
        t = nueva_tarea(args.content, args.deadline)
        print(f"Tarea creada: {t['id']} — {t['content']} → {args.deadline}")
    elif args.comando == "evento":
        t = nuevo_evento(args.content, args.datetime_iso)
        print(f"Evento creado: {t['id']} — {t['content']} → {args.datetime_iso}")
    else:
        parser.print_help()
