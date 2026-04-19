"""
Reset Notion (PTN) — marcar proyectos/tareas/notas como Archivo=true, reversible.

Fase 2 del sistema de reseteo. No destruye datos: activa un Checkbox `Archivo`
paralelo al `Estado` existente (que queda intacto), y propaga el mismo flag a
la BD INX-ENLACES para que las vistas que filtran por `Archivo != true` oculten
todo lo archivado de un plumazo.

Prerrequisito:
  python tools/ensure_archivo_field.py
  (garantiza que cada data source tiene la propiedad Archivo: Checkbox)

Subcomandos:
  reset-ptn-proyectos      Marca todas las paginas de Proyectos con Archivo=true
  reset-ptn-tareas         ... de Tareas
  reset-ptn-notas          ... de Notas
  reset-ptn-all            Los tres en orden (Proyectos, Tareas, Notas)

  list-archived [--target proyectos|tareas|notas|all]
  restore PAGE_ID
  restore-all [--target <t>] [--from YYYY-MM-DD]

Flags transversales:
  --dry-run                No llama a PATCH, solo informa.
  --limit N                Corta en N paginas (0 = sin limite).
  --snapshot               Antes de archivar, vuelca el estado actual a
                           artifacts/resets/YYYY-MM-DD/ptn-<target>-<ts>.json.
  --no-inx                 No propaga a INX (solo PTN).

Ejemplos:
  python tools/reset_notion.py reset-ptn-proyectos --dry-run
  python tools/reset_notion.py reset-ptn-all --snapshot
  python tools/reset_notion.py list-archived --target all
  python tools/reset_notion.py restore 33f622cf-315b-8173-8604-ee623959d4ce
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
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

from tools.notion_tools import (  # noqa: E402
    extract_property_value,
    get_data_source_schema,
    query_data_source,
    update_page_properties,
)

# --- Config ---

TARGET_ENVS = {
    "proyectos": "NOTION_DS_PROYECTOS",
    "tareas":    "NOTION_DS_TAREAS",
    "notas":     "NOTION_DS_NOTAS",
}

# Candidatos de propiedad titulo por target (primero encontrado gana)
TITLE_PROPS = {
    "proyectos": ["Nombre", "Título", "Titulo"],
    "tareas":    ["Nombre", "Título", "Titulo"],
    "notas":     ["Título", "Titulo", "Nombre"],
}

# Propiedades cuyo valor queremos en los snapshots (si existen)
SNAPSHOT_PROPS = [
    "Nombre", "Título", "Titulo", "Estado", "Estado Progreso",
    "Prioridad", "Fecha", "Fecha inicio", "Fecha límite",
    "Tipo", "Responsable", "Proyecto", "Proyectos", "Tarea",
]

INX_ENV = "NOTION_DB_INX"
ARCHIVE_DIR = _ROOT / "artifacts" / "resets"


# ==================== helpers ====================


def _get_ds_id(target: str) -> str:
    env_key = TARGET_ENVS[target]
    ds_id = os.getenv(env_key)
    if not ds_id:
        raise SystemExit(f"Variable {env_key} no definida en .env")
    return ds_id


def _get_inx_db_id() -> str:
    ds_id = os.getenv(INX_ENV)
    if not ds_id:
        raise SystemExit(f"Variable {INX_ENV} no definida en .env")
    return ds_id


def _ensure_archivo_present(ds_id: str, label: str) -> None:
    schema = get_data_source_schema(ds_id)
    if "Archivo" not in schema.get("properties", []):
        raise SystemExit(
            f"La propiedad 'Archivo' no existe en {label} ({ds_id}). "
            "Ejecuta primero: python tools/ensure_archivo_field.py"
        )


def _page_title(page: dict, target: str) -> str:
    props = page.get("properties", {}) or {}
    for candidate in TITLE_PROPS.get(target, ["Nombre", "Título", "Titulo"]):
        val = extract_property_value(props.get(candidate, {}))
        if val:
            return val
    # Fallback: primera propiedad tipo title
    for name, meta in props.items():
        if isinstance(meta, dict) and meta.get("type") == "title":
            val = extract_property_value(meta)
            if val:
                return val
    return "(sin titulo)"


def _is_archivo_true(page: dict) -> bool:
    archivo = page.get("properties", {}).get("Archivo", {})
    if isinstance(archivo, dict) and archivo.get("type") == "checkbox":
        return bool(archivo.get("checkbox"))
    return False


def _build_inx_map() -> dict[str, str]:
    """Devuelve {clave -> inx_page_id} para propagar cambios a INX."""
    inx_id = _get_inx_db_id()
    rows = query_data_source(inx_id)
    mapping: dict[str, str] = {}
    for r in rows:
        key = extract_property_value(r.get("properties", {}).get("Clave", {}))
        if key:
            mapping[key] = r["id"]
    return mapping


def _inx_candidates(page_id: str) -> list[str]:
    """Posibles claves en INX para una page de PTN (con y sin guiones)."""
    page_id = str(page_id)
    clean = page_id.replace("-", "")
    return [f"ptn:{page_id}", f"ptn:{clean}"]


# ==================== snapshot ====================


def _snapshot_pages(pages: list[dict], target: str) -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    day_dir = ARCHIVE_DIR / Date.today().isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%H%M%SZ")
    out = day_dir / f"ptn-{target}-{ts}.json"
    payload = []
    for p in pages:
        entry = {
            "id": p.get("id"),
            "title": _page_title(p, target),
            "url": p.get("url"),
            "archivo_before": _is_archivo_true(p),
            "properties_snapshot": {},
        }
        props = p.get("properties", {}) or {}
        for pname in SNAPSHOT_PROPS:
            if pname in props:
                val = extract_property_value(props[pname])
                if val:
                    entry["properties_snapshot"][pname] = val
        payload.append(entry)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


# ==================== core archive / restore ====================


@dataclass
class ResetReport:
    target: str
    flipped: int = 0
    skipped: int = 0
    inx_propagated: int = 0
    inx_missing: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)


def _flip_archivo(
    pages: list[dict],
    target: str,
    *,
    new_value: bool,
    dry_run: bool,
    propagate_inx: bool,
    inx_map: dict[str, str] | None,
) -> ResetReport:
    rep = ResetReport(target=target)
    prefix = "ARCHIVE" if new_value else "RESTORE"
    for p in pages:
        pid = p.get("id")
        title = _page_title(p, target)
        current = _is_archivo_true(p)
        if current == new_value:
            rep.skipped += 1
            continue

        print(f"{'[dry]' if dry_run else '[run]'} {prefix} {pid[:10]}...  {title[:60]!r}")

        if not dry_run:
            try:
                update_page_properties(pid, {"Archivo": {"checkbox": new_value}})
                rep.flipped += 1
            except Exception as exc:
                rep.errors.append((pid, str(exc)))
                print(f"      ERROR PTN: {exc}")
                continue
        else:
            rep.flipped += 1

        if propagate_inx and inx_map is not None:
            match = None
            for key_variant in _inx_candidates(pid):
                if key_variant in inx_map:
                    match = inx_map[key_variant]
                    break
            if match is None:
                rep.inx_missing += 1
                continue
            if dry_run:
                print(f"      {'[dry]' if dry_run else '[run]'} INX {match[:10]}... Archivo={new_value}")
                rep.inx_propagated += 1
                continue
            try:
                update_page_properties(match, {"Archivo": {"checkbox": new_value}})
                rep.inx_propagated += 1
            except Exception as exc:
                rep.errors.append((match, f"INX: {exc}"))
                print(f"      ERROR INX: {exc}")

    return rep


def _print_report(rep: ResetReport) -> None:
    print()
    print(f"Resumen target={rep.target}")
    print(f"  flipped         : {rep.flipped}")
    print(f"  saltadas        : {rep.skipped}")
    print(f"  inx propagadas  : {rep.inx_propagated}")
    print(f"  inx sin fila    : {rep.inx_missing}")
    print(f"  errores         : {len(rep.errors)}")
    for pid, err in rep.errors[:5]:
        print(f"    - {pid}: {err[:120]}")


# ==================== comandos archive ====================


def _reset_target(target: str, args: argparse.Namespace) -> ResetReport:
    ds_id = _get_ds_id(target)
    _ensure_archivo_present(ds_id, target)
    pages = query_data_source(ds_id)
    pages = [p for p in pages if not _is_archivo_true(p)]
    if args.limit > 0:
        pages = pages[:args.limit]

    if not pages:
        print(f"(target={target} sin paginas candidatas)")
        return ResetReport(target=target)

    if args.snapshot:
        snap = _snapshot_pages(pages, target)
        print(f"Snapshot: {snap}")

    inx_map = None if args.no_inx else _build_inx_map()
    rep = _flip_archivo(
        pages, target,
        new_value=True, dry_run=args.dry_run,
        propagate_inx=not args.no_inx, inx_map=inx_map,
    )
    _print_report(rep)
    return rep


def cmd_reset_proyectos(args): _reset_target("proyectos", args); return 0


def cmd_reset_tareas(args):    _reset_target("tareas",    args); return 0


def cmd_reset_notas(args):     _reset_target("notas",     args); return 0


def cmd_reset_all(args):
    for t in ("proyectos", "tareas", "notas"):
        _reset_target(t, args)
    return 0


# ==================== list-archived ====================


def _query_archived(target: str) -> list[dict]:
    ds_id = _get_ds_id(target)
    _ensure_archivo_present(ds_id, target)
    rows = query_data_source(ds_id)
    return [r for r in rows if _is_archivo_true(r)]


def cmd_list_archived(args) -> int:
    targets = ["proyectos", "tareas", "notas"] if args.target == "all" else [args.target]
    total = 0
    for t in targets:
        rows = _query_archived(t)
        print(f"[{t}] archivadas: {len(rows)}")
        for r in rows[:args.limit] if args.limit > 0 else rows:
            print(f"  {r.get('id')}  {_page_title(r, t)[:60]!r}")
        total += len(rows)
    print()
    print(f"Total: {total}")
    return 0


# ==================== restore ====================


def _find_page_in_targets(page_id: str) -> tuple[str, dict] | None:
    """Busca page_id en proyectos/tareas/notas. Devuelve (target, page) o None."""
    for target in ("proyectos", "tareas", "notas"):
        ds_id = _get_ds_id(target)
        rows = query_data_source(ds_id)
        for r in rows:
            if str(r.get("id")) == str(page_id):
                return target, r
    return None


def cmd_restore(args) -> int:
    found = _find_page_in_targets(args.page_id)
    if not found:
        raise SystemExit(f"Page {args.page_id} no encontrada en proyectos/tareas/notas")
    target, page = found
    if not _is_archivo_true(page):
        print(f"(page {args.page_id[:10]}... ya esta con Archivo=false en {target})")
        return 0
    inx_map = None if args.no_inx else _build_inx_map()
    rep = _flip_archivo(
        [page], target,
        new_value=False, dry_run=args.dry_run,
        propagate_inx=not args.no_inx, inx_map=inx_map,
    )
    _print_report(rep)
    return 0


def cmd_restore_all(args) -> int:
    targets = ["proyectos", "tareas", "notas"] if args.target == "all" else [args.target]
    inx_map = None if args.no_inx else _build_inx_map()
    for t in targets:
        rows = _query_archived(t)
        if args.from_date:
            # No tenemos fecha de archivado en la propiedad Archivo (solo booleano).
            # Si necesitas filtrar por fecha, usa los snapshots en artifacts/resets/.
            print(f"(aviso: --from ignorado para {t}, el checkbox no guarda fecha; "
                  "usa los snapshots en artifacts/resets/ para referencia temporal)")
        if args.limit > 0:
            rows = rows[:args.limit]
        if not rows:
            print(f"(target={t} sin paginas archivadas)")
            continue
        rep = _flip_archivo(
            rows, t,
            new_value=False, dry_run=args.dry_run,
            propagate_inx=not args.no_inx, inx_map=inx_map,
        )
        _print_report(rep)
    return 0


# ==================== CLI ====================


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def _add_common(p, *, include_limit=True, include_snapshot=True):
        p.add_argument("--dry-run", action="store_true")
        if include_limit:
            p.add_argument("--limit", type=int, default=0)
        if include_snapshot:
            p.add_argument("--snapshot", action="store_true")
        p.add_argument("--no-inx", action="store_true", help="No propaga a INX")

    p1 = sub.add_parser("reset-ptn-proyectos"); _add_common(p1); p1.set_defaults(func=cmd_reset_proyectos)
    p2 = sub.add_parser("reset-ptn-tareas");    _add_common(p2); p2.set_defaults(func=cmd_reset_tareas)
    p3 = sub.add_parser("reset-ptn-notas");     _add_common(p3); p3.set_defaults(func=cmd_reset_notas)
    p4 = sub.add_parser("reset-ptn-all");       _add_common(p4); p4.set_defaults(func=cmd_reset_all)

    pl = sub.add_parser("list-archived")
    pl.add_argument("--target", choices=["proyectos", "tareas", "notas", "all"], default="all")
    pl.add_argument("--limit", type=int, default=0)
    pl.set_defaults(func=cmd_list_archived)

    pr = sub.add_parser("restore"); pr.add_argument("page_id"); _add_common(pr, include_limit=False, include_snapshot=False)
    pr.set_defaults(func=cmd_restore)

    pra = sub.add_parser("restore-all")
    pra.add_argument("--target", choices=["proyectos", "tareas", "notas", "all"], default="all")
    pra.add_argument("--from", dest="from_date", default=None)
    _add_common(pra, include_snapshot=False)
    pra.set_defaults(func=cmd_restore_all)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
