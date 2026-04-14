"""
Orquestador Scrum del sistema multiagente de Coworkia.

Funciones principales:
  - Listar agentes especializados por dominio y por operación
  - Generar un squad Scrum para un objetivo
  - Crear un sprint plan con backlog, tareas, eventos y artefactos
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from multiagents.artifacts import render_sprint_markdown, write_sprint_artifact
from multiagents.planner import plan_sprint
from multiagents.registry import ALL_AGENTS, SCRUM_ROLES


def _run_step(script_rel_path: str, args: list[str] | None = None) -> int:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    script = os.path.join(root, script_rel_path)
    cmd = [sys.executable, script] + (args or [])
    proc = subprocess.run(cmd, cwd=root)
    return int(proc.returncode or 0)


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
        path = write_sprint_artifact(plan)
        return f"{render_sprint_markdown(plan)}\n\nArtefacto guardado en: {path}"

    return render_sprint_markdown(plan)


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
    p_sprint.add_argument("--guardar", action="store_true", help="Guardar artefacto markdown en artifacts/sprints")

    p_inx = subparsers.add_parser("inx-sync", help="Ejecutar cadena de sincronización INX (Todoist/PTN/Obsidian -> INX-ENLACES)")
    p_inx.add_argument("--limit", type=int, default=None, help="Limitar elementos procesados (solo para fuentes enumerables)")

    args = parser.parse_args()

    if args.comando == "agentes":
        print(listar_agentes())
    elif args.comando == "roles":
        print(listar_roles())
    elif args.comando == "plan-sprint":
        print(generar_sprint(args.objetivo, args.nombre, args.inicio, args.dias, args.guardar))
    elif args.comando == "inx-sync":
        raise SystemExit(inx_sync(args.limit))
    else:
        parser.print_help()

