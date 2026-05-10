"""
Doctor de calidad MAR para el espejo `TODOIST-TAREAS` en Notion.

Objetivo: detectar inconsistencias frecuentes tras capturar/clasificar en Todoist:
- Duplicados por `Todoist ID`
- Reglas MAR (activables una a una) para detectar inconsistencias (Evento sin hora, Hábito sin recurrencia, etc.)
- Tareas sin descripción cuando el usuario espera usarla (opcional)

Nota: la autoridad sigue siendo Todoist; esto es un reporte para corregir en origen.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import query_data_source, extract_property_value


def _get(props: dict, name: str) -> str:
    return extract_property_value(props.get(name, {})) if props else ""

def _truthy(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in ("✓", "si", "sí", "true", "1", "yes")


def _has_time(iso: str) -> bool:
    # Todoist/Notion suelen usar ISO8601; para due con hora suele aparecer 'T'
    return "T" in (iso or "")

def _has_date(iso: str) -> bool:
    return bool((iso or "").strip())

def _expected_tipo(due: str, deadline: str, recurrencia: str) -> str:
    """
    Reglas MAR (David) inferidas desde el espejo en Notion:
    - Hábito: recurrencia true, tenga o no hora
    - Evento: due con hora, no recurrente
    - Logro: sin hora, no recurrente, con deadline (due opcional)
    - Tarea: sin hora, no recurrente, sin deadline, con due (fecha)
    - Idea: sin due, sin deadline, (y no recurrente)
    """
    is_recurring = _truthy(recurrencia)
    has_due = _has_date(due)
    has_deadline = _has_date(deadline)
    due_has_time = _has_time(due)

    if is_recurring:
        return "habito"
    if due_has_time:
        return "evento"
    if has_deadline:
        return "logro"
    if has_due:
        return "tarea"
    return "idea"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Doctor MAR sobre TODOIST-TAREAS (Notion)")
    parser.add_argument("--db", default=os.getenv("TODOIST_DB_TAREAS"), help="ID de TODOIST-TAREAS (data_source)")
    parser.add_argument("--max", type=int, default=50, help="Máximo de líneas por sección")
    parser.add_argument("--require-desc", action="store_true", help="Marcar como issue si falta Descripcion")

    # Checks activables (una a una). Por defecto el doctor es conservador.
    parser.add_argument("--check-duplicates", action="store_true", help="Detectar duplicados por Todoist ID")
    parser.add_argument("--check-missing-tipo", action="store_true", help="Detectar filas sin Tipo MAR")
    parser.add_argument("--check-evento-hora", action="store_true", help="Evento debe tener Due con hora")
    parser.add_argument("--check-habito-recurrencia", action="store_true", help="Hábito debe tener Recurrencia=✓")
    parser.add_argument("--check-meta-deadline", action="store_true", help="Legacy: Logro debe tener Deadline (no requiere Due)")
    parser.add_argument("--check-tarea-fecha", action="store_true", help="Tarea debe tener Due (fecha) y no tener Deadline")
    parser.add_argument("--check-idea-sin-fechas", action="store_true", help="Idea no debe tener Due/Deadline/Recurrencia")
    parser.add_argument("--check-tipo-consistency", action="store_true", help="Comparar Tipo MAR (Notion) vs tipo esperado por reglas MAR")
    args = parser.parse_args()

    if not args.db:
        print("Falta TODOIST_DB_TAREAS en .env (o pasa --db <id>)")
        return 2

    rows = query_data_source(args.db)

    # Dedupe por page_id para evitar falsos duplicados si Notion devuelve filas repetidas
    by_tid_ids: dict[str, set[str]] = defaultdict(set)
    by_tid_examples: dict[str, list[str]] = defaultdict(list)
    issues: dict[str, list[str]] = defaultdict(list)

    for r in rows:
        page_id = (r.get("id") or "").strip()
        props = r.get("properties", {}) or {}
        tid = _get(props, "Todoist ID").strip()
        title = _get(props, "Tarea").strip() or "(sin titulo)"
        tipo = _get(props, "Tipo MAR").strip().lower()
        due = _get(props, "Due").strip()
        deadline = _get(props, "Deadline").strip()
        recurrencia = _get(props, "Recurrencia").strip()
        desc = _get(props, "Descripcion").strip()
        url = _get(props, "URL").strip()

        if tid:
            if page_id and page_id in by_tid_ids[tid]:
                # Misma fila repetida en el query: ignórala
                continue
            if page_id:
                by_tid_ids[tid].add(page_id)
            if len(by_tid_examples[tid]) < 5:
                by_tid_examples[tid].append(title)

        if args.check_missing_tipo and not tipo:
            issues["Sin Tipo MAR"].append(f"- {title} | tid={tid} | url={url or '-'}")
            continue

        is_recurring = _truthy(recurrencia)
        has_due = _has_date(due)
        has_deadline = _has_date(deadline)
        due_has_time = _has_time(due)

        if args.check_tipo_consistency and tipo:
            expected = _expected_tipo(due=due, deadline=deadline, recurrencia=recurrencia)
            if tipo != expected:
                issues["Tipo MAR inconsistente"].append(
                    f"- {title} | tid={tid} | tipo={tipo} -> esperado={expected} | due={due or '-'} | deadline={deadline or '-'} | rec={recurrencia or '-'}"
                )

        # Checks (activables) — uno a uno
        if args.check_evento_hora and tipo == "evento":
            if not due_has_time:
                issues["Evento sin hora"].append(f"- {title} | tid={tid} | due={due or '-'}")

        if args.check_habito_recurrencia and tipo == "habito":
            if not is_recurring:
                issues["Hábito sin recurrencia"].append(f"- {title} | tid={tid} | recurrencia={recurrencia or '-'}")

        if args.check_meta_deadline and tipo in {"logro", "meta"}:
            # Regla David: Logro requiere Deadline; Due es opcional (pero si existe, no debe tener hora)
            if not has_deadline:
                issues["Logro sin deadline"].append(f"- {title} | tid={tid}")
            if has_due and due_has_time:
                issues["Logro con hora (debería ser sin hora)"].append(f"- {title} | tid={tid} | due={due}")

        if args.check_tarea_fecha and tipo == "tarea":
            # Regla David: Tarea requiere Due (sin hora) y NO debe tener Deadline
            if not has_due:
                issues["Tarea sin fecha"].append(f"- {title} | tid={tid}")
            if due_has_time:
                issues["Tarea con hora (debería ser Evento)"].append(f"- {title} | tid={tid} | due={due}")
            if has_deadline:
                issues["Tarea con deadline (debería ser Logro)"].append(f"- {title} | tid={tid} | deadline={deadline}")

        if args.check_idea_sin_fechas and tipo == "idea":
            if has_due:
                issues["Idea con fecha (revisar)"].append(f"- {title} | tid={tid} | due={due}")
            if has_deadline:
                issues["Idea con deadline (revisar)"].append(f"- {title} | tid={tid} | deadline={deadline}")
            if is_recurring:
                issues["Idea con recurrencia (revisar)"].append(f"- {title} | tid={tid}")

        if args.require_desc and not desc:
            issues["Sin descripción"].append(f"- {title} | tid={tid} | url={url or '-'}")

    # Duplicados por Todoist ID
    if args.check_duplicates:
        dups = {tid: ids for tid, ids in by_tid_ids.items() if tid and len(ids) > 1}
        if dups:
            for tid, ids in dups.items():
                ejemplos = "; ".join(by_tid_examples.get(tid, [])[:5])
                issues["Duplicados por Todoist ID"].append(
                    f"- tid={tid} | filas={len(ids)} | ejemplos={ejemplos or '(sin ejemplos)'}"
                )

    print("=== MAR DOCTOR (TODOIST-TAREAS) ===")
    print(f"Filas analizadas: {len(rows)}")
    enabled = []
    if args.check_duplicates:
        enabled.append("duplicates")
    if args.check_missing_tipo:
        enabled.append("missing-tipo")
    if args.check_evento_hora:
        enabled.append("evento-hora")
    if args.check_habito_recurrencia:
        enabled.append("habito-recurrencia")
    if args.check_meta_deadline:
        enabled.append("logro-deadline")
    if args.check_tarea_fecha:
        enabled.append("tarea-fecha")
    if args.check_idea_sin_fechas:
        enabled.append("idea-sin-fechas")
    if args.check_tipo_consistency:
        enabled.append("tipo-consistency")
    if args.require_desc:
        enabled.append("require-desc")
    print(f"Checks activos: {', '.join(enabled) if enabled else '(ninguno)'}")
    print()

    if not issues:
        print("OK: no se detectaron issues con las reglas actuales.")
        return 0

    for section in sorted(issues.keys()):
        lines = issues[section]
        print(f"[{section}] ({len(lines)})")
        for line in lines[: args.max]:
            print(line)
        if len(lines) > args.max:
            print(f"... {len(lines) - args.max} más")
        print()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

