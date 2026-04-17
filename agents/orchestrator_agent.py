"""
Orquestador Scrum del sistema multiagente de Coworkia.

Funciones principales:
  - Listar agentes especializados por dominio y por operación
  - Generar un squad Scrum para un objetivo
  - Crear un sprint plan con backlog, tareas, eventos y artefactos
  - Ejecutar runbooks mínimos asociados a tareas del sprint
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from multiagents.artifacts import (
    create_sprint_run,
    load_sprint_run,
    render_sprint_markdown,
    sprint_paths,
    utc_now_iso,
    write_sprint_artifact,
    write_sprint_run_artifacts,
)
from multiagents.chat_memory import build_chat_memory, render_chat_memory_markdown, write_chat_memory_artifacts
from multiagents.models import CommandExecution, SprintRun, TaskExecution, TaskStatus
from multiagents.planner import plan_sprint
from multiagents.registry import ALL_AGENTS, SCRUM_ROLES


def _root_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _run_step(script_rel_path: str, args: list[str] | None = None) -> int:
    root = _root_dir()
    script = os.path.join(root, script_rel_path)
    cmd = [sys.executable, script] + (args or [])
    proc = subprocess.run(cmd, cwd=root)
    return int(proc.returncode or 0)


def _run_command(script_rel_path: str, args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    root = _root_dir()
    script = os.path.join(root, script_rel_path)
    cmd = [sys.executable, script] + (args or [])
    return subprocess.run(
        cmd,
        cwd=root,
        text=True,
        capture_output=True,
    )


def listar_agentes() -> str:
    lines = ["=== SISTEMA MULTIAGENTE COWORKIA ===", ""]
    for kind in ("coordination", "operation", "domain"):
        lines.append(f"[{kind.upper()}]")
        for agent in [agent for agent in ALL_AGENTS if agent.kind == kind]:
            systems = ", ".join(agent.owned_systems) if agent.owned_systems else "Transversal"
            operations = ", ".join(agent.owned_operations)
            lines.append(f"  - {agent.name}")
            lines.append(f"    key: {agent.key}")
            lines.append(f"    scope: {agent.scope}")
            lines.append(f"    systems: {systems}")
            lines.append(f"    operations: {operations}")
        lines.append("")
    return "\n".join(lines)


def listar_roles() -> str:
    lines = ["=== ROLES SCRUM ===", ""]
    for role in SCRUM_ROLES:
        lines.append(f"- {role.name}: {role.mission}")
        lines.append(f"  Artefactos: {', '.join(role.owned_artifacts)}")
    return "\n".join(lines)


def generar_sprint(objetivo: str, nombre: str, inicio: str | None, dias: int, guardar: bool) -> str:
    start_date = date.fromisoformat(inicio) if inicio else None
    plan = plan_sprint(objetivo, sprint_name=nombre, start_date=start_date, duration_days=dias)

    if guardar:
        run = create_sprint_run(plan)
        markdown_path, json_path = write_sprint_run_artifacts(run)
        return (
            f"{render_sprint_markdown(plan)}\n\n"
            f"Artefactos guardados en:\n- {markdown_path}\n- {json_path}"
        )

    return render_sprint_markdown(plan)


def _get_task_state(run: SprintRun, task_key: str) -> TaskExecution:
    for task_state in run.task_states:
        if task_state.task_key == task_key:
            return task_state
    raise KeyError(f"Task state not found: {task_key}")


def _get_task(run: SprintRun, task_key: str):
    for task in run.plan.tasks:
        if task.key == task_key:
            return task
    raise KeyError(f"Task not found: {task_key}")


def _dependency_satisfied(status: TaskStatus) -> bool:
    return status in {"completed", "skipped"}


def _resolve_task_command(command, limit: int | None) -> list[str]:
    args = list(command.args)
    if limit is not None and command.accepts_limit and "--limit" not in args:
        args.extend(["--limit", str(limit)])
    return args


def _mark_task(
    task_state: TaskExecution,
    *,
    status: TaskStatus,
    note: str | None = None,
    exit_code: int | None = None,
) -> None:
    now = utc_now_iso()
    if task_state.started_at is None and status in {"running", "completed", "failed", "blocked", "skipped"}:
        task_state.started_at = now
    task_state.status = status
    task_state.finished_at = now if status != "running" else None
    task_state.exit_code = exit_code
    if note:
        task_state.notes.append(note)


def _refresh_plan_status(run: SprintRun) -> None:
    statuses = {state.status for state in run.task_states}
    if any(status == "running" for status in statuses):
        run.plan = run.plan.__class__(**{**run.plan.__dict__, "status": "active"})
    elif all(status in {"completed", "skipped"} for status in statuses):
        run.plan = run.plan.__class__(**{**run.plan.__dict__, "status": "completed"})
    else:
        run.plan = run.plan.__class__(**{**run.plan.__dict__, "status": "planned"})


def _write_run(run: SprintRun) -> None:
    run.updated_at = utc_now_iso()
    _refresh_plan_status(run)
    write_sprint_run_artifacts(run)


def run_task(sprint_name: str, task_key: str, limit: int | None = None) -> int:
    run = load_sprint_run(sprint_name)
    task = _get_task(run, task_key)
    task_state = _get_task_state(run, task_key)

    for dependency_key in task.depends_on:
        dependency_state = _get_task_state(run, dependency_key)
        if not _dependency_satisfied(dependency_state.status):
            _mark_task(
                task_state,
                status="blocked",
                note=f"Dependencia no satisfecha: {dependency_key} ({dependency_state.status})",
                exit_code=2,
            )
            _write_run(run)
            return 2

    if not task.commands:
        _mark_task(task_state, status="skipped", note="Tarea sin runbook ejecutable.", exit_code=0)
        _write_run(run)
        return 0

    _mark_task(task_state, status="running")
    _write_run(run)

    for task_command in task.commands:
        command_args = _resolve_task_command(task_command, limit)
        command_line = [sys.executable, os.path.join(_root_dir(), task_command.script_path), *command_args]
        command_state = CommandExecution(
            label=task_command.label,
            command=command_line,
            status="running",
            started_at=utc_now_iso(),
        )
        task_state.command_results.append(command_state)

        proc = _run_command(task_command.script_path, command_args)
        command_state.finished_at = utc_now_iso()
        command_state.exit_code = int(proc.returncode or 0)
        if proc.returncode == 0:
            command_state.status = "completed"
        else:
            command_state.status = "failed"
            command_state.note = (proc.stderr or proc.stdout or "").strip()[:500]
            _mark_task(
                task_state,
                status="failed",
                note=f"{task_command.label} falló con exit code {proc.returncode}.",
                exit_code=int(proc.returncode or 1),
            )
            _write_run(run)
            return int(proc.returncode or 1)

    _mark_task(task_state, status="completed", note="Runbook completado.", exit_code=0)
    _write_run(run)
    return 0


def run_sprint(sprint_name: str, limit: int | None = None) -> int:
    run = load_sprint_run(sprint_name)
    last_exit_code = 0
    for task in run.plan.tasks:
        task_state = _get_task_state(run, task.key)
        if task_state.status in {"completed", "skipped"}:
            continue
        exit_code = run_task(sprint_name, task.key, limit=limit)
        if exit_code != 0:
            last_exit_code = exit_code
            break
        run = load_sprint_run(sprint_name)
    return last_exit_code


def sprint_status(sprint_name: str) -> str:
    run = load_sprint_run(sprint_name)
    markdown_path, json_path = sprint_paths(sprint_name)
    lines = [
        f"=== {run.plan.sprint_name} ===",
        f"Estado sprint: {run.plan.status}",
        f"Creado: {run.created_at}",
        f"Actualizado: {run.updated_at}",
        f"Artefactos:",
        f"  - {markdown_path}",
        f"  - {json_path}",
        "",
        "Tareas:",
    ]
    task_map = {task.key: task for task in run.plan.tasks}
    for task_state in run.task_states:
        task = task_map[task_state.task_key]
        lines.append(f"- {task.key} [{task_state.status}] {task.title}")
        if task_state.notes:
            for note in task_state.notes[-2:]:
                lines.append(f"  note: {note}")
    return "\n".join(lines)


def sync_chat_memory(chat_path: str = "chat.md") -> str:
    snapshot = build_chat_memory(chat_path=chat_path)
    paths = write_chat_memory_artifacts(snapshot)
    return (
        f"{render_chat_memory_markdown(snapshot)}\n"
        f"Artifacts:\n"
        f"- {paths['markdown']}\n"
        f"- {paths['snapshot']}\n"
        f"- {paths['conversation']}\n"
        f"- {paths['decisions']}\n"
        f"- {paths['agent_state']}\n"
        f"- {paths['memory_records']}"
    )


def inx_sync(limit: int | None) -> int:
    """
    Cadena mínima para mantener B0A-INX coherente:
      1) Todoist -> NOTION TODOIST-TAREAS
      2) PTN -> log NOTION (B0A-INX)
      3) Obsidian -> log OBSIDIAN (B0A-INX)
      4) Upsert a INX-ENLACES
    """
    steps: list[tuple[str, list[str]]] = []

    todoist_args: list[str] = []
    if limit is not None:
        todoist_args += ["--limit", str(limit)]
    steps.append(("tools/sync_todoist_to_notion.py", todoist_args))
    steps.append(("tools/log_ptn_changes.py", []))
    steps.append(("tools/log_obsidian_changes.py", []))

    inx_args: list[str] = ["--source", "all"]
    if limit is not None:
        inx_args += ["--limit", str(limit)]
    steps.append(("tools/sync_inx_links.py", inx_args))

    for script, args in steps:
        code = _run_step(script, args)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestador Scrum multiagente para Coworkia")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("agentes", help="Listar catálogo de agentes")
    subparsers.add_parser("roles", help="Listar roles Scrum")

    p_sprint = subparsers.add_parser("plan-sprint", help="Generar sprint plan para un objetivo")
    p_sprint.add_argument("objetivo", help="Objetivo del sprint o iniciativa")
    p_sprint.add_argument("--nombre", default="Sprint 1", help="Nombre del sprint")
    p_sprint.add_argument("--inicio", default=None, help="Fecha YYYY-MM-DD")
    p_sprint.add_argument("--dias", type=int, default=14, help="Duración del sprint")
    p_sprint.add_argument("--guardar", action="store_true", help="Guardar artefactos markdown/json en artifacts/sprints")

    p_status = subparsers.add_parser("status", help="Mostrar estado de un sprint persistido")
    p_status.add_argument("nombre", help="Nombre del sprint persistido")

    p_run_task = subparsers.add_parser("run-task", help="Ejecutar una tarea del sprint")
    p_run_task.add_argument("nombre", help="Nombre del sprint persistido")
    p_run_task.add_argument("task_key", help="Clave de la tarea, por ejemplo ST-003")
    p_run_task.add_argument("--limit", type=int, default=None, help="Límite opcional para comandos que lo soporten")

    p_run_sprint = subparsers.add_parser("run-sprint", help="Ejecutar el sprint completo en orden")
    p_run_sprint.add_argument("nombre", help="Nombre del sprint persistido")
    p_run_sprint.add_argument("--limit", type=int, default=None, help="Límite opcional para comandos que lo soporten")

    p_chat_memory = subparsers.add_parser("sync-chat-memory", help="Parsear chat.md y generar memoria/logs multiagente")
    p_chat_memory.add_argument("--chat", default="chat.md", help="Ruta al chat compartido")

    p_inx = subparsers.add_parser("inx-sync", help="Ejecutar cadena de sincronización INX (Todoist/PTN/Obsidian -> INX-ENLACES)")
    p_inx.add_argument("--limit", type=int, default=None, help="Limitar elementos procesados (solo para fuentes enumerables)")

    args = parser.parse_args()

    if args.comando == "agentes":
        print(listar_agentes())
    elif args.comando == "roles":
        print(listar_roles())
    elif args.comando == "plan-sprint":
        print(generar_sprint(args.objetivo, args.nombre, args.inicio, args.dias, args.guardar))
    elif args.comando == "status":
        print(sprint_status(args.nombre))
    elif args.comando == "run-task":
        raise SystemExit(run_task(args.nombre, args.task_key, limit=args.limit))
    elif args.comando == "run-sprint":
        raise SystemExit(run_sprint(args.nombre, limit=args.limit))
    elif args.comando == "sync-chat-memory":
        print(sync_chat_memory(args.chat))
    elif args.comando == "inx-sync":
        raise SystemExit(inx_sync(args.limit))
    else:
        parser.print_help()
