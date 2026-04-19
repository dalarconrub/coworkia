"""
Reset MAR — archivar tareas Todoist a Z-BACK-yymmdd sin cerrarlas (reversible).

Fase 1 del sistema de reseteo. Mueve tareas pendientes/programadas a un
proyecto diario derivado `Z-BACK-yymmdd`, preservando el proyecto de origen
en la descripcion para que el
comando `restore` pueda devolverlas a su sitio. No cierra ni borra tareas.

Reglas de seguridad:
  - Nunca archiva tareas que ya estan en algun proyecto Z-* (se saltan).
  - Solo toca tareas abiertas (Todoist no devuelve completadas en /tasks por
    defecto, pero igualmente no se escriben close/delete).
  - Idempotente: si una tarea ya lleva marker [ARCHIVED: ...], no se re-archiva.
    Si detecta un estado parcial (marker presente pero tarea aun fuera de Z-*),
    repara el movimiento pendiente hacia el backup diario.
  - Marker en descripcion: `[ARCHIVED: YYYY-MM-DD | orig-project: <id>]`
    anadido al final, separado por linea en blanco. `restore` lo elimina.

Subcomandos:
  reset-all                   Archiva todas las pendientes / programadas.
  reset-by-type TIPO          idea | meta | habito | tarea | evento
  reset-by-project NOMBRE     Por nombre de proyecto Todoist (case-insensitive).
  reset-by-label LABEL        Por label (sin @).
  reset-overdue [--days N]    Tareas con due.date anterior a hoy - N dias (N>=0).

  list-archived               Lista tareas actualmente en el backup diario con marker.
  restore TASK_ID             Devuelve la tarea a su proyecto original.
  restore-all [--from YYYY-MM-DD]
                              Restaura todas las archivadas (opcional desde fecha).

Flags transversales:
  --dry-run                   Imprime lo que haria sin llamar a la API.
  --limit N                   Corta en N tareas (0 = sin limite).
  --backup-project-id ID      Override del proyecto destino. Si no se pasa,
                              se deriva/crea `Z-BACK-yymmdd`.

Ejemplos:
  python tools/reset_mar.py reset-all --dry-run
  python tools/reset_mar.py reset-by-type idea --dry-run
  python tools/reset_mar.py reset-overdue --days 30
  python tools/reset_mar.py list-archived
  python tools/reset_mar.py restore 8123456789
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date as Date, datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from tools.env_utils import load_project_env

load_project_env(_ROOT / ".env")

from tools.todoist_tools import (  # noqa: E402
    Z_PROJECTS,
    classify_mar_type,
    create_project,
    get_projects,
    get_tasks,
    move_task,
    update_task,
)

DEFAULT_Z_INBOX_ID = "6Mv5F76GQq3p699F"

MARKER_RE = re.compile(
    r"\[ARCHIVED:\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*orig-project:\s*(?P<orig>\S+?)\]"
)


# ==================== helpers de marker en descripcion ====================


def _make_marker(orig_project_id: str, today: str) -> str:
    return f"[ARCHIVED: {today} | orig-project: {orig_project_id}]"


def _has_marker(desc: str | None) -> bool:
    return bool(desc) and MARKER_RE.search(desc) is not None


def _parse_marker(desc: str | None) -> tuple[str, str] | None:
    """Devuelve (date, orig_project_id) si el marker existe, None si no."""
    if not desc:
        return None
    m = MARKER_RE.search(desc)
    if not m:
        return None
    return m.group("date"), m.group("orig")


def _append_marker(desc: str | None, marker: str) -> str:
    base = (desc or "").rstrip()
    if not base:
        return marker
    return f"{base}\n\n{marker}"


def _strip_marker(desc: str | None) -> str:
    if not desc:
        return ""
    stripped = MARKER_RE.sub("", desc).rstrip()
    # Elimina posibles lineas en blanco huerfanas al final
    return re.sub(r"\n{3,}", "\n\n", stripped)


# ==================== helpers de seleccion ====================


def _is_in_z_project(task: dict) -> bool:
    return task.get("project_id") in Z_PROJECTS


def _backup_project_name(day: Date | None = None) -> str:
    day = day or Date.today()
    return f"Z-BACK-{day.strftime('%y%m%d')}"


def _project_map() -> dict[str, dict]:
    return {p["id"]: p for p in get_projects()}


def _resolve_backup_project_id(
    explicit_project_id: str | None,
    dry_run: bool,
    day: Date | None = None,
) -> tuple[str, str, bool]:
    if explicit_project_id:
        projects = _project_map()
        match = projects.get(explicit_project_id)
        if not match:
            raise SystemExit(f"Proyecto backup no encontrado: {explicit_project_id}")
        return explicit_project_id, match.get("name", explicit_project_id), False

    target_name = _backup_project_name(day)
    projects = get_projects()
    match = next((p for p in projects if str(p.get("name", "")).strip() == target_name), None)
    if match:
        return match["id"], target_name, False
    if dry_run:
        return f"<create:{target_name}>", target_name, True
    created = create_project(target_name)
    return created["id"], target_name, True


def _z_project_ids_by_name() -> set[str]:
    ids = set(Z_PROJECTS.keys())
    try:
        for p in get_projects():
            name = str(p.get("name", "")).strip()
            if name.startswith("Z-"):
                ids.add(p["id"])
    except Exception:
        pass
    return ids


def _task_candidates_from_all() -> list[dict]:
    """Tareas abiertas, excluyendo las ya archivadas consistentemente en Z-*.

    Incluye estados parciales (marker presente pero tarea fuera de Z-*), porque
    son reparables y no deben quedar invisibles al rerun.
    """
    tasks = get_tasks(include_excluded=True)
    z_ids = _z_project_ids_by_name()
    out: list[dict] = []
    for t in tasks:
        if t.get("project_id") in z_ids:
            # Todo lo que ya este en proyectos Z-* queda fuera del flujo normal.
            continue
        # Fuera de Z-* entran tanto tareas normales como parciales reparables.
        out.append(t)
    return out


def _task_candidates_by_type(mar_type: str) -> list[dict]:
    mar_type = mar_type.lower()
    base = _task_candidates_from_all()
    return [t for t in base if classify_mar_type(t) == mar_type]


def _task_candidates_by_project(name: str) -> list[dict]:
    target_name = name.strip().lower()
    projects = get_projects()
    matches = [p for p in projects if str(p.get("name", "")).strip().lower() == target_name]
    if not matches:
        # fallback: contains
        matches = [p for p in projects if target_name in str(p.get("name", "")).strip().lower()]
    if not matches:
        raise SystemExit(f"Proyecto no encontrado (match exacto o contains): {name!r}")
    target_ids = {p["id"] for p in matches}
    if target_ids & _z_project_ids_by_name():
        raise SystemExit(
            f"Rechazado: el proyecto indicado es Z-* (cuarentena). Eso no se archiva."
        )
    base = _task_candidates_from_all()
    return [t for t in base if t.get("project_id") in target_ids]


def _task_candidates_by_label(label: str) -> list[dict]:
    label_clean = label.lstrip("@").strip()
    base = _task_candidates_from_all()
    return [t for t in base if label_clean in (t.get("labels") or [])]


def _task_candidates_overdue(days: int = 0) -> list[dict]:
    today = Date.today()
    cutoff = today.fromordinal(today.toordinal() - max(days, 0))
    base = _task_candidates_from_all()
    out: list[dict] = []
    for t in base:
        due = t.get("due") or {}
        due_date = due.get("date")
        if not due_date:
            continue
        try:
            d = Date.fromisoformat(due_date[:10])
        except ValueError:
            continue
        if d < cutoff:
            out.append(t)
    return out


# ==================== archivado y restore ====================


@dataclass
class ResetReport:
    archived: list[dict]
    repaired: list[dict]
    skipped: list[tuple[dict, str]]
    errors: list[tuple[dict, str]]


def _apply_limit(tasks: list[dict], limit: int) -> list[dict]:
    if limit <= 0:
        return tasks
    return tasks[:limit]


def _archive_tasks(tasks: list[dict], backup_project_id: str, dry_run: bool, backup_project_name: str) -> ResetReport:
    report = ResetReport(archived=[], repaired=[], skipped=[], errors=[])
    today = Date.today().isoformat()
    z_ids = _z_project_ids_by_name()

    for task in tasks:
        tid = task.get("id")
        content = task.get("content") or "(sin titulo)"
        orig = task.get("project_id")
        desc = task.get("description")
        parsed = _parse_marker(desc)
        has_marker = parsed is not None

        if orig == backup_project_id:
            report.skipped.append((task, f"ya en {backup_project_name}"))
            continue
        if orig in z_ids:
            report.skipped.append((task, f"ya en proyecto Z-* ({Z_PROJECTS[orig]})"))
            continue
        if has_marker:
            # Estado parcial: ya se escribió el marker pero la tarea sigue fuera
            # de Z-*. Reparamos solo el movimiento pendiente.
            marker_orig = parsed[1] if parsed else (orig or "")
            print(f"{'[dry]' if dry_run else '[run]'} REPAIR  {tid[:10]}... {content[:60]!r:<62} -> {backup_project_name}")
            if dry_run:
                report.repaired.append(task)
                continue
            try:
                move_task(tid, project_id=backup_project_id)
                report.repaired.append(task)
            except Exception as exc:
                report.errors.append((task, str(exc)))
                print(f"      ERROR: {exc}")
            continue

        marker = _make_marker(orig or "", today)
        new_desc = _append_marker(desc, marker)

        print(f"{'[dry]' if dry_run else '[run]'} ARCHIVE {tid[:10]}... {content[:60]!r:<62} -> {backup_project_name}")
        if dry_run:
            report.archived.append(task)
            continue
        try:
            # Primero persistimos el marker para mantener el proyecto origen, y
            # los reruns ahora reparan automaticamente cualquier corte entre
            # update y move.
            update_task(tid, description=new_desc)
            move_task(tid, project_id=backup_project_id)
            report.archived.append(task)
        except Exception as exc:
            report.errors.append((task, str(exc)))
            print(f"      ERROR: {exc}")

    return report


def _restore_task(task: dict, dry_run: bool) -> str | None:
    """Devuelve msg de error si hubo problema, None si OK (o era dry-run OK)."""
    tid = task.get("id")
    content = task.get("content") or "(sin titulo)"
    parsed = _parse_marker(task.get("description"))
    if not parsed:
        return "sin marker [ARCHIVED: ...]"
    _, orig = parsed
    if not orig:
        return "marker sin orig-project"
    new_desc = _strip_marker(task.get("description"))
    print(f"{'[dry]' if dry_run else '[run]'} RESTORE {tid[:10]}... -> {orig[:12]}...  {content[:50]!r}")
    if dry_run:
        return None
    try:
        update_task(tid, description=new_desc)
        move_task(tid, project_id=orig)
        return None
    except Exception as exc:
        return str(exc)


# ==================== summary printer ====================


def _resolve_project_map() -> dict[str, str]:
    try:
        projects = get_projects()
        return {p["id"]: p.get("name", "?") for p in projects}
    except Exception:
        return {}


def _print_report(report: ResetReport, label: str, project_names: dict[str, str] | None = None):
    print()
    print(f"Resumen {label}:")
    print(f"  archivadas : {len(report.archived)}")
    print(f"  reparadas  : {len(report.repaired)}")
    print(f"  saltadas   : {len(report.skipped)}")
    print(f"  errores    : {len(report.errors)}")
    if report.skipped:
        print()
        print("  Saltadas (primeras 10):")
        for task, reason in report.skipped[:10]:
            pid = task.get("project_id")
            pname = (project_names or {}).get(pid, pid or "?")
            print(f"    - {task.get('content', '')[:50]!r:<52}  proyecto={pname}  motivo={reason}")
    if report.errors:
        print()
        print("  Errores:")
        for task, err in report.errors:
            print(f"    - {task.get('id')} {task.get('content', '')[:50]!r}  err={err[:80]}")


# ==================== comandos ====================


def cmd_reset_all(args):
    tasks = _apply_limit(_task_candidates_from_all(), args.limit)
    if not tasks:
        print("(sin tareas candidatas)")
        return 0
    project_names = _resolve_project_map()
    backup_id, backup_name, created = _resolve_backup_project_id(args.backup_project_id, args.dry_run)
    print(f"Proyecto backup: {backup_name} ({backup_id}){' [nuevo]' if created else ''}")
    report = _archive_tasks(tasks, backup_id, args.dry_run, backup_name)
    _print_report(report, "reset-all", project_names)
    return 0


def cmd_reset_by_type(args):
    tasks = _apply_limit(_task_candidates_by_type(args.tipo), args.limit)
    if not tasks:
        print(f"(sin tareas tipo MAR {args.tipo})")
        return 0
    project_names = _resolve_project_map()
    backup_id, backup_name, created = _resolve_backup_project_id(args.backup_project_id, args.dry_run)
    print(f"Proyecto backup: {backup_name} ({backup_id}){' [nuevo]' if created else ''}")
    report = _archive_tasks(tasks, backup_id, args.dry_run, backup_name)
    _print_report(report, f"reset-by-type {args.tipo}", project_names)
    return 0


def cmd_reset_by_project(args):
    tasks = _apply_limit(_task_candidates_by_project(args.proyecto), args.limit)
    if not tasks:
        print(f"(sin tareas en proyecto que coincida con {args.proyecto!r})")
        return 0
    project_names = _resolve_project_map()
    backup_id, backup_name, created = _resolve_backup_project_id(args.backup_project_id, args.dry_run)
    print(f"Proyecto backup: {backup_name} ({backup_id}){' [nuevo]' if created else ''}")
    report = _archive_tasks(tasks, backup_id, args.dry_run, backup_name)
    _print_report(report, f"reset-by-project {args.proyecto}", project_names)
    return 0


def cmd_reset_by_label(args):
    tasks = _apply_limit(_task_candidates_by_label(args.label), args.limit)
    if not tasks:
        print(f"(sin tareas con label {args.label!r})")
        return 0
    project_names = _resolve_project_map()
    backup_id, backup_name, created = _resolve_backup_project_id(args.backup_project_id, args.dry_run)
    print(f"Proyecto backup: {backup_name} ({backup_id}){' [nuevo]' if created else ''}")
    report = _archive_tasks(tasks, backup_id, args.dry_run, backup_name)
    _print_report(report, f"reset-by-label {args.label}", project_names)
    return 0


def cmd_reset_overdue(args):
    tasks = _apply_limit(_task_candidates_overdue(args.days), args.limit)
    if not tasks:
        print(f"(sin tareas vencidas hace >= {args.days} dias)")
        return 0
    project_names = _resolve_project_map()
    backup_id, backup_name, created = _resolve_backup_project_id(args.backup_project_id, args.dry_run)
    print(f"Proyecto backup: {backup_name} ({backup_id}){' [nuevo]' if created else ''}")
    report = _archive_tasks(tasks, backup_id, args.dry_run, backup_name)
    _print_report(report, f"reset-overdue --days {args.days}", project_names)
    return 0


def cmd_list_archived(args):
    day = Date.fromisoformat(args.from_date) if args.from_date else Date.today()
    backup_id, backup_name, created = _resolve_backup_project_id(args.backup_project_id, args.dry_run, day)
    tasks = [] if (args.dry_run and created) else get_tasks(project_id=backup_id, include_excluded=True)
    archived = [t for t in tasks if _has_marker(t.get("description"))]
    if not archived:
        print(f"(ninguna tarea archivada en {backup_name})")
        return 0
    project_names = _resolve_project_map()
    print(f"Archivadas en {backup_name} ({len(archived)}):")
    for t in archived:
        parsed = _parse_marker(t.get("description"))
        if not parsed:
            continue
        date_str, orig = parsed
        pname = project_names.get(orig, orig[:12] + "...")
        tid = t.get("id", "?")
        content = t.get("content", "")[:60]
        print(f"  {date_str}  {tid:<14}  {content!r:<62}  orig={pname}")
    return 0


def cmd_restore(args):
    day = Date.fromisoformat(args.from_date) if args.from_date else Date.today()
    backup_id, backup_name, _ = _resolve_backup_project_id(args.backup_project_id, args.dry_run, day)
    tasks = get_tasks(project_id=backup_id, include_excluded=True)
    task = next((t for t in tasks if str(t.get("id")) == str(args.task_id)), None)
    if task is None:
        raise SystemExit(f"Tarea {args.task_id} no encontrada en {backup_name}.")
    err = _restore_task(task, args.dry_run)
    if err:
        raise SystemExit(f"Fallo al restaurar: {err}")
    print("OK.")
    return 0


def cmd_restore_all(args):
    day = Date.fromisoformat(args.from_date) if args.from_date else Date.today()
    backup_id, backup_name, _ = _resolve_backup_project_id(args.backup_project_id, args.dry_run, day)
    tasks = get_tasks(project_id=backup_id, include_excluded=True)
    archived = [t for t in tasks if _has_marker(t.get("description"))]
    archived = _apply_limit(archived, args.limit)
    if not archived:
        print(f"(ninguna tarea a restaurar en {backup_name} con el filtro indicado)")
        return 0
    ok = 0
    errs = 0
    for t in archived:
        err = _restore_task(t, args.dry_run)
        if err:
            errs += 1
            print(f"    ERROR {t.get('id')}: {err}")
        else:
            ok += 1
    print()
    print(f"Resumen restore-all: ok={ok}  errores={errs}")
    return 0


# ==================== CLI ====================


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    def _add_common(p, include_limit=True):
        p.add_argument("--dry-run", action="store_true", help="Imprime acciones sin llamar a la API")
        if include_limit:
            p.add_argument("--limit", type=int, default=0, help="Corta en N tareas (0 = sin limite)")
        p.add_argument("--backup-project-id", default=None,
                       help="Override del proyecto destino backup (default = derivar/crear Z-BACK-yymmdd)")

    p_all = sub.add_parser("reset-all", help="Archivar todas las tareas abiertas (excluye Z-*)")
    _add_common(p_all)
    p_all.set_defaults(func=cmd_reset_all)

    p_type = sub.add_parser("reset-by-type", help="Archivar por tipo MAR")
    p_type.add_argument("tipo", choices=["idea", "meta", "habito", "tarea", "evento"])
    _add_common(p_type)
    p_type.set_defaults(func=cmd_reset_by_type)

    p_proj = sub.add_parser("reset-by-project", help="Archivar por nombre de proyecto")
    p_proj.add_argument("proyecto", help="Nombre del proyecto (exact o contains)")
    _add_common(p_proj)
    p_proj.set_defaults(func=cmd_reset_by_project)

    p_lab = sub.add_parser("reset-by-label", help="Archivar por label Todoist")
    p_lab.add_argument("label", help="Label (con o sin @)")
    _add_common(p_lab)
    p_lab.set_defaults(func=cmd_reset_by_label)

    p_over = sub.add_parser("reset-overdue", help="Archivar tareas vencidas hace N dias")
    p_over.add_argument("--days", type=int, default=0, help="Dias de antiguedad del vencimiento (default 0 = hoy y anteriores)")
    _add_common(p_over)
    p_over.set_defaults(func=cmd_reset_overdue)

    p_list = sub.add_parser("list-archived", help="Listar tareas archivadas en el backup diario")
    p_list.add_argument("--backup-project-id", default=None)
    p_list.add_argument("--from", dest="from_date", default=None, help="Fecha YYYY-MM-DD del backup a consultar (default = hoy)")
    p_list.add_argument("--dry-run", action="store_true", help="No crea el proyecto derivado si aun no existe")
    p_list.set_defaults(func=cmd_list_archived)

    p_rest = sub.add_parser("restore", help="Restaurar una tarea concreta a su proyecto origen")
    p_rest.add_argument("task_id")
    _add_common(p_rest, include_limit=False)
    p_rest.add_argument("--from", dest="from_date", default=None, help="Fecha YYYY-MM-DD del backup a restaurar (default = hoy)")
    p_rest.set_defaults(func=cmd_restore)

    p_ra = sub.add_parser("restore-all", help="Restaurar todas las archivadas (opcional desde fecha)")
    p_ra.add_argument("--from", dest="from_date", default=None, help="Fecha YYYY-MM-DD minima de archivado")
    _add_common(p_ra)
    p_ra.set_defaults(func=cmd_restore_all)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
