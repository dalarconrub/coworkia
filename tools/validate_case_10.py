"""
Validacion del caso de uso 10: Tareas MAR nacidas dentro de notas Obsidian.

Contrato:
- Las notas Obsidian pueden contener lineas `- [ ] Descripcion <!-- todoist:<id> -->`
  que representan tareas ya capturadas en Todoist.
- Para cada marker encontrado: debe existir fila INX con Clave = `todoist:<id>`.
- Reporta tambien checkboxes sin marker (captura pendiente) como info.
- Para lineas `- [x] ... <!-- todoist:<id> -->`, el cierre round-trip debe verse
  reflejado en `TODOIST_DB_TAREAS.Estado=Completada` y en `INX.Estado=Completada`.

Uso:
  python tools/validate_case_10.py
  python tools/validate_case_10.py --scope close
  python tools/validate_case_10.py --scope all
Requiere .env: NOTION_DB_INX, OBSIDIAN_ALPHA_PATH

Exit codes:
  0  OK (markers presentes tienen todos fila INX).
  1  Markers sin fila INX, o no hay markers.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import ALPHA_PATH


MARKER_RE = re.compile(r"- \[[ xX]\] .+?<!-- todoist:([^ ]+) -->")
CLOSED_RE = re.compile(r"- \[[xX]\] .+?<!-- todoist:([^ ]+) -->")
PENDING_RE = re.compile(r"^\s*- \[ \] (.+?)(?:\s*<!-- todoist:[^ ]+ -->)?\s*$")


def _dedupe_rows(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        pid = (r.get("id") or "").strip()
        if pid and pid in seen:
            continue
        if pid:
            seen.add(pid)
        out.append(r)
    return out


def _scan_vault() -> tuple[list[dict], list[dict], int]:
    markers: list[dict] = []
    closed: list[dict] = []
    pending = 0
    for md in ALPHA_PATH.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(md.relative_to(ALPHA_PATH))
        for line_num, line in enumerate(content.splitlines(), 1):
            c = CLOSED_RE.search(line)
            if c:
                closed.append({"ruta": rel, "line": line_num, "task_id": c.group(1)})
            m = MARKER_RE.search(line)
            if m:
                markers.append({"ruta": rel, "line": line_num, "task_id": m.group(1)})
                continue
            if PENDING_RE.match(line) and "<!-- todoist:" not in line:
                pending += 1
    return markers, closed, pending


def _todoist_estado_map(db_id: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in _dedupe_rows(query_data_source(db_id)):
        props = row.get("properties", {})
        tid = extract_property_value(props.get("Todoist ID", {})) or ""
        if tid:
            mapping[tid] = extract_property_value(props.get("Estado", {})) or ""
    return mapping


def _inx_estado_map(db_id: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in _dedupe_rows(query_data_source(db_id)):
        props = row.get("properties", {})
        clave = extract_property_value(props.get("Clave", {})) or ""
        if clave.startswith("todoist:"):
            mapping[clave[len("todoist:"):]] = extract_property_value(props.get("Estado", {})) or ""
    return mapping


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["capture", "close", "all"], default="capture")
    args = parser.parse_args()

    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2
    db_todoist = os.getenv("TODOIST_DB_TAREAS")
    if args.scope in {"close", "all"} and not db_todoist:
        print("Falta TODOIST_DB_TAREAS en .env para validar cierre")
        return 2

    markers, closed, pending = _scan_vault()

    rows_inx = _dedupe_rows(query_data_source(db_inx))
    inx_todoist: set[str] = set()
    for r in rows_inx:
        clave = (extract_property_value(r.get("properties", {}).get("Clave", {})) or "")
        if clave.startswith("todoist:"):
            inx_todoist.add(clave[len("todoist:") :])

    matched = [m for m in markers if m["task_id"] in inx_todoist]
    missing = [m for m in markers if m["task_id"] not in inx_todoist]

    print("=== Validacion caso 10 (checkboxes Obsidian -> Todoist -> INX) ===\n")
    print(f"Vault: markers todoist encontrados: {len(markers)}")
    print(f"Vault: checkboxes pendientes sin marker (captura pendiente): {pending}")
    print(f"INX-ENLACES: {len(rows_inx)} filas unicas | {len(inx_todoist)} claves todoist:*")
    print(f"\nMarkers con fila INX: {len(matched)}/{len(markers)}")

    if matched:
        print("\nEjemplos (hasta 5):")
        for m in matched[:5]:
            print(f"  - todoist:{m['task_id']} | {m['ruta'][:70]} L{m['line']}")

    if missing:
        print("\n[!] Markers sin fila INX (hasta 5):")
        for m in missing[:5]:
            print(f"  - todoist:{m['task_id']} | {m['ruta'][:70]} L{m['line']}")
        print("    Ejecuta: python tools/sync_inx_links.py --source todoist --limit 200")

    if len(markers) == 0:
        print("\n[!] No hay markers `<!-- todoist:<id> -->` en el vault.")
        print("    Ejecuta: python tools/promote_notas_checkboxes_to_todoist.py <nota> --sync")
        return 1

    if missing:
        return 1

    print("\nOK: todos los markers tienen fila INX todoist:*.")
    if args.scope == "capture":
        return 0

    todoist_estado = _todoist_estado_map(db_todoist)
    inx_estado = _inx_estado_map(db_inx)
    closed_missing_todoist = [m for m in closed if todoist_estado.get(m["task_id"]) != "Completada"]
    closed_missing_inx = [m for m in closed if inx_estado.get(m["task_id"]) != "Completada"]

    print("\n=== Validacion cierre round-trip (Obsidian [x] -> Todoist/INX) ===\n")
    print(f"Checkboxes cerrados con marker: {len(closed)}")
    print(f"TODOIST_DB_TAREAS con Estado=Completada: {len(closed) - len(closed_missing_todoist)}/{len(closed)}")
    print(f"INX con Estado=Completada: {len(closed) - len(closed_missing_inx)}/{len(closed)}")

    if closed_missing_todoist:
        print("\n[!] Cerrados sin reflejo en TODOIST_DB_TAREAS (hasta 5):")
        for item in closed_missing_todoist[:5]:
            print(f"  - todoist:{item['task_id']} | {item['ruta']} L{item['line']}")
        print("    Ejecuta: python tools/close_obsidian_checkboxes_to_todoist.py <nota> --sync")

    if closed_missing_inx:
        print("\n[!] Cerrados sin reflejo en INX (hasta 5):")
        for item in closed_missing_inx[:5]:
            print(f"  - todoist:{item['task_id']} | {item['ruta']} L{item['line']}")
        print("    Ejecuta: python tools/close_obsidian_checkboxes_to_todoist.py <nota> --sync")

    if args.scope == "close" and len(closed) == 0:
        print("\n[!] No hay checkboxes cerrados con marker en el vault.")
        print("    Marca una linea como `- [x] ... <!-- todoist:<id> -->` y reintenta.")
        return 1

    if closed_missing_todoist or closed_missing_inx:
        return 1

    print("\nOK: todos los checkboxes cerrados con marker reflejan Estado=Completada en Todoist mirror e INX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
