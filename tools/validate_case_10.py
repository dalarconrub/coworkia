"""
Validacion del caso de uso 10: Tareas MAR nacidas dentro de notas Obsidian.

Contrato:
- Las notas Obsidian pueden contener lineas `- [ ] Descripcion <!-- todoist:<id> -->`
  que representan tareas ya capturadas en Todoist.
- Para cada marker encontrado: debe existir fila INX con Clave = `todoist:<id>`.
- Reporta tambien checkboxes sin marker (captura pendiente) como info.

Uso: python tools/validate_case_10.py
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

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import ALPHA_PATH


MARKER_RE = re.compile(r"- \[[ xX]\] .+?<!-- todoist:([^ ]+) -->")
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


def _scan_vault() -> tuple[list[dict], int]:
    markers: list[dict] = []
    pending = 0
    for md in ALPHA_PATH.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(md.relative_to(ALPHA_PATH))
        for line_num, line in enumerate(content.splitlines(), 1):
            m = MARKER_RE.search(line)
            if m:
                markers.append({"ruta": rel, "line": line_num, "task_id": m.group(1)})
                continue
            if PENDING_RE.match(line) and "<!-- todoist:" not in line:
                pending += 1
    return markers, pending


def main() -> int:
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    markers, pending = _scan_vault()

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
