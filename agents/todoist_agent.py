"""
Agente MAR para Todoist.

Entiende el sistema MAR (Meta-Accion-Resultado) y opera sobre Todoist
respetando la clasificacion temporal: Idea, Meta, Habito, Tarea, Evento.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from tools.todoist_tools import (
    MAR_FILTERS,
    classify_mar_type,
    close_task,
    create_task,
    delete_task,
    get_projects,
    get_task,
    get_tasks,
    get_tasks_by_horizon,
    get_tasks_by_mar_type,
    move_task,
    update_task,
)


ICONOS = {
    "idea": "💡",
    "meta": "🎯",
    "habito": "🔁",
    "tarea": "📋",
    "evento": "🗓️",
}


def _due_display(task: dict) -> str:
    due = task.get("due") or {}
    deadline = task.get("deadline") or {}
    parts = []
    if due.get("date"):
        parts.append(f"due={due['date']}")
    if deadline.get("date"):
        parts.append(f"deadline={deadline['date']}")
    return " | ".join(parts)


def _task_line(task: dict) -> str:
    tipo = classify_mar_type(task)
    extra = _due_display(task)
    suffix = f" | {extra}" if extra else ""
    return f"{ICONOS[tipo]} {task['id']} | {task['content']}{suffix}"


def _build_update_payload(args) -> dict:
    payload = {}

    if getattr(args, "content", None) is not None:
        payload["content"] = args.content
    if getattr(args, "description", None) is not None:
        payload["description"] = args.description
    if getattr(args, "priority", None) is not None:
        payload["priority"] = args.priority
    if getattr(args, "labels", None) is not None:
        payload["labels"] = args.labels

    if getattr(args, "clear_due", False):
        payload["due_string"] = "no date"
        payload["due_date"] = None
        payload["due_datetime"] = None
    elif getattr(args, "due_datetime", None):
        payload["due_datetime"] = args.due_datetime
    elif getattr(args, "due_date", None):
        payload["due_date"] = args.due_date
    elif getattr(args, "due_string", None):
        payload["due_string"] = args.due_string

    if getattr(args, "clear_deadline", False):
        payload["deadline_date"] = None
    elif getattr(args, "deadline_date", None):
        payload["deadline_date"] = args.deadline_date

    return payload


def _reclassify_payload(tipo: str, valor: str | None) -> dict:
    base = {"due_string": "no date", "due_date": None, "due_datetime": None, "deadline_date": None}

    if tipo == "idea":
        return base
    if tipo == "meta":
        if not valor:
            raise ValueError("Meta requiere una fecha YYYY-MM-DD")
        return {**base, "due_date": valor}
    if tipo == "habito":
        if not valor:
            raise ValueError('Habito requiere una recurrencia, por ejemplo "every day"')
        return {**base, "due_string": valor}
    if tipo == "tarea":
        if not valor:
            raise ValueError("Tarea requiere una fecha YYYY-MM-DD")
        return {**base, "due_date": valor, "deadline_date": valor}
    if tipo == "evento":
        if not valor:
            raise ValueError("Evento requiere una fecha-hora ISO 8601")
        return {**base, "due_datetime": valor}
    raise ValueError(f"Tipo MAR desconocido: {tipo}")


def resumen_hoy() -> str:
    """Genera un resumen de tareas para hoy segun sistema MAR."""
    tareas_hoy = get_tasks_by_horizon("hoy")

    if not tareas_hoy:
        return "No hay tareas para hoy."

    por_tipo: dict[str, list] = {
        "evento": [],
        "meta": [],
        "tarea": [],
        "habito": [],
        "idea": [],
    }

    for task in tareas_hoy:
        por_tipo[classify_mar_type(task)].append(task)

    lineas = [f"=== RESUMEN HOY ({len(tareas_hoy)} acciones) ===\n"]
    titulos = {
        "evento": "🗓️  EVENTOS",
        "meta": "🎯 METAS",
        "tarea": "📋 TAREAS",
        "habito": "🔁 HÁBITOS",
        "idea": "💡 IDEAS",
    }

    for tipo, items in por_tipo.items():
        if not items:
            continue
        lineas.append(f"\n{titulos[tipo]} ({len(items)})")
        for task in items:
            prioridad = "(!)" if task.get("priority", 1) >= 3 else ""
            lineas.append(f"• {task['content']} {prioridad}".rstrip())

    return "\n".join(lineas)


def listar_por_tipo(tipo: str) -> str:
    """Lista tareas de un tipo MAR especifico."""
    tareas = get_tasks_by_mar_type(tipo)
    if not tareas:
        return f"No hay {tipo}s activos."

    lineas = [f"=== {tipo.upper()}S ({len(tareas)}) ==="]
    for task in tareas:
        lineas.append(f"• {_task_line(task)}")
    return "\n".join(lineas)


def buscar_tareas(texto: str, limit: int = 20) -> str:
    """Busca tareas activas por texto en contenido o descripcion."""
    texto = texto.strip().lower()
    resultados = []
    for task in get_tasks():
        blob = f"{task.get('content', '')}\n{task.get('description', '')}".lower()
        if texto in blob:
            resultados.append(task)

    if not resultados:
        return f'No hay tareas activas que coincidan con "{texto}".'

    lineas = [f'=== BUSQUEDA "{texto}" ({len(resultados)}) ===']
    for task in resultados[:limit]:
        lineas.append(f"• {_task_line(task)}")
    if len(resultados) > limit:
        lineas.append(f"... y {len(resultados) - limit} mas")
    return "\n".join(lineas)


def ver_tarea(task_id: str) -> str:
    """Muestra el detalle de una tarea activa."""
    task = get_task(task_id)
    tipo = classify_mar_type(task)
    lineas = [f"=== TAREA {task_id} ==="]
    lineas.append(f"Tipo        : {tipo}")
    lineas.append(f"Contenido   : {task.get('content', '')}")
    lineas.append(f"Proyecto    : {task.get('project_id', '')}")
    lineas.append(f"Prioridad   : {task.get('priority', 1)}")
    lineas.append(f"Descripcion : {task.get('description', '') or '-'}")
    lineas.append(f"Due         : {(task.get('due') or {}).get('date', '-')}")
    lineas.append(f"Deadline    : {(task.get('deadline') or {}).get('date', '-')}")
    labels = ", ".join(task.get("labels", [])) or "-"
    lineas.append(f"Etiquetas   : {labels}")
    return "\n".join(lineas)


def listar_proyectos() -> str:
    """Lista proyectos activos disponibles en Todoist."""
    proyectos = [p for p in get_projects() if p.get("id") not in {"", None}]
    if not proyectos:
        return "No hay proyectos activos."

    lineas = [f"=== PROYECTOS ({len(proyectos)}) ==="]
    for proyecto in sorted(proyectos, key=lambda item: item.get("name", "").lower()):
        lineas.append(f"• {proyecto['id']} | {proyecto['name']}")
    return "\n".join(lineas)


def estado_sistema() -> str:
    """Muestra el estado completo del sistema MAR por tipos."""
    lineas = ["=== ESTADO SISTEMA MAR ===\n"]
    total = 0
    for tipo in ["evento", "meta", "tarea", "habito", "idea"]:
        tareas = get_tasks_by_mar_type(tipo)
        n = len(tareas)
        total += n
        lineas.append(f"  {ICONOS[tipo]} {tipo.capitalize():8} {n:3} acciones")

    lineas.append(f"\n  TOTAL: {total} acciones activas")
    return "\n".join(lineas)


def nueva_idea(content: str, description: str = None, project_id: str = None) -> dict:
    return create_task(content=content, description=description, project_id=project_id)


def nueva_meta(content: str, fecha: str, description: str = None, project_id: str = None) -> dict:
    return create_task(content=content, description=description, project_id=project_id, due_date=fecha)


def nuevo_habito(content: str, recurrencia: str, description: str = None, project_id: str = None) -> dict:
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        is_recurring=True,
        recurring_string=recurrencia,
    )


def nueva_tarea(
    content: str,
    deadline: str,
    description: str = None,
    project_id: str = None,
    priority: int = 1,
) -> dict:
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_date=deadline,
        priority=priority,
    )


def nuevo_evento(content: str, datetime_iso: str, description: str = None, project_id: str = None) -> dict:
    return create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_datetime=datetime_iso,
    )


def completar_tarea(task_id: str) -> str:
    close_task(task_id)
    return f"Tarea completada: {task_id}"


def borrar_tarea(task_id: str) -> str:
    delete_task(task_id)
    return f"Tarea eliminada: {task_id}"


def mover_tarea(task_id: str, project_id: str) -> str:
    move_task(task_id, project_id=project_id)
    proyecto = next((p for p in get_projects() if p.get("id") == project_id), None)
    nombre = proyecto.get("name") if proyecto else project_id
    return f"Tarea movida: {task_id} -> {nombre}"


def editar_tarea(task_id: str, payload: dict) -> str:
    if not payload:
        raise ValueError("No se indico ningun cambio")
    task = update_task(task_id, **payload)
    return f"Tarea actualizada: {_task_line(task)}"


def reclasificar_tarea(task_id: str, tipo: str, valor: str | None = None) -> str:
    payload = _reclassify_payload(tipo, valor)
    task = update_task(task_id, **payload)
    return f"Reclasificada como {tipo}: {_task_line(task)}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente MAR para Todoist")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("hoy", help="Resumen de hoy")
    subparsers.add_parser("estado", help="Estado del sistema MAR")
    subparsers.add_parser("proyectos", help="Listar proyectos activos")

    p_listar = subparsers.add_parser("listar", help="Listar por tipo MAR")
    p_listar.add_argument("tipo", choices=list(MAR_FILTERS.keys()))

    p_buscar = subparsers.add_parser("buscar", help="Buscar tareas activas por texto")
    p_buscar.add_argument("texto")
    p_buscar.add_argument("--limit", type=int, default=20)

    p_ver = subparsers.add_parser("ver", help="Ver detalle de una tarea")
    p_ver.add_argument("task_id")

    p_idea = subparsers.add_parser("idea", help="Crear idea")
    p_idea.add_argument("content")

    p_meta = subparsers.add_parser("meta", help="Crear meta")
    p_meta.add_argument("content")
    p_meta.add_argument("fecha", help="YYYY-MM-DD")

    p_habito = subparsers.add_parser("habito", help="Crear habito")
    p_habito.add_argument("content")
    p_habito.add_argument("recurrencia", help='ej: "every day"')

    p_tarea = subparsers.add_parser("tarea", help="Crear tarea")
    p_tarea.add_argument("content")
    p_tarea.add_argument("deadline", help="YYYY-MM-DD")

    p_evento = subparsers.add_parser("evento", help="Crear evento")
    p_evento.add_argument("content")
    p_evento.add_argument("datetime_iso", help='ej: "2026-03-16T10:00:00"')

    p_completar = subparsers.add_parser("completar", help="Completar una tarea")
    p_completar.add_argument("task_id")

    p_borrar = subparsers.add_parser("borrar", help="Eliminar una tarea")
    p_borrar.add_argument("task_id")

    p_mover = subparsers.add_parser("mover", help="Mover una tarea a otro proyecto")
    p_mover.add_argument("task_id")
    p_mover.add_argument("project_id")

    p_editar = subparsers.add_parser("editar", help="Editar una tarea existente")
    p_editar.add_argument("task_id")
    p_editar.add_argument("--content")
    p_editar.add_argument("--description")
    p_editar.add_argument("--priority", type=int, choices=[1, 2, 3, 4])
    p_editar.add_argument("--labels", nargs="*")
    p_editar.add_argument("--due-date")
    p_editar.add_argument("--due-datetime")
    p_editar.add_argument("--due-string")
    p_editar.add_argument("--deadline-date")
    p_editar.add_argument("--clear-due", action="store_true")
    p_editar.add_argument("--clear-deadline", action="store_true")

    p_reclass = subparsers.add_parser("reclasificar", help="Cambiar una tarea a otro tipo MAR")
    p_reclass.add_argument("task_id")
    p_reclass.add_argument("tipo", choices=list(MAR_FILTERS.keys()))
    p_reclass.add_argument(
        "--valor",
        help="Fecha, fecha-hora o recurrencia segun el tipo destino",
    )

    args = parser.parse_args()

    if args.comando == "hoy":
        print(resumen_hoy())
    elif args.comando == "estado":
        print(estado_sistema())
    elif args.comando == "proyectos":
        print(listar_proyectos())
    elif args.comando == "listar":
        print(listar_por_tipo(args.tipo))
    elif args.comando == "buscar":
        print(buscar_tareas(args.texto, limit=args.limit))
    elif args.comando == "ver":
        print(ver_tarea(args.task_id))
    elif args.comando == "idea":
        task = nueva_idea(args.content)
        print(f"Idea creada: {task['id']} | {task['content']}")
    elif args.comando == "meta":
        task = nueva_meta(args.content, args.fecha)
        print(f"Meta creada: {task['id']} | {task['content']} -> {args.fecha}")
    elif args.comando == "habito":
        task = nuevo_habito(args.content, args.recurrencia)
        print(f"Habito creado: {task['id']} | {task['content']}")
    elif args.comando == "tarea":
        task = nueva_tarea(args.content, args.deadline)
        print(f"Tarea creada: {task['id']} | {task['content']} -> {args.deadline}")
    elif args.comando == "evento":
        task = nuevo_evento(args.content, args.datetime_iso)
        print(f"Evento creado: {task['id']} | {task['content']} -> {args.datetime_iso}")
    elif args.comando == "completar":
        print(completar_tarea(args.task_id))
    elif args.comando == "borrar":
        print(borrar_tarea(args.task_id))
    elif args.comando == "mover":
        print(mover_tarea(args.task_id, args.project_id))
    elif args.comando == "editar":
        print(editar_tarea(args.task_id, _build_update_payload(args)))
    elif args.comando == "reclasificar":
        print(reclasificar_tarea(args.task_id, args.tipo, args.valor))
    else:
        parser.print_help()
