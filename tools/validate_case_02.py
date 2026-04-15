"""
Validación del caso de uso 2: tarea Todoist -> PTN Proyecto en TODOIST-TAREAS -> INX-ENLACES.

Uso: python tools/validate_case_02.py
Requiere .env: TODOIST_DB_TAREAS, NOTION_DB_INX
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import query_data_source, extract_property_value


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


def main() -> int:
    db_t = os.getenv("TODOIST_DB_TAREAS")
    db_i = os.getenv("NOTION_DB_INX")
    if not db_t or not db_i:
        print("Faltan TODOIST_DB_TAREAS o NOTION_DB_INX en .env")
        return 2

    rows_t = _dedupe_rows(query_data_source(db_t))
    with_ptn: list[dict] = []
    for r in rows_t:
        props = r.get("properties", {})
        rel = props.get("PTN Proyecto", {}).get("relation", [])
        if rel:
            with_ptn.append(r)

    rows_i = _dedupe_rows(query_data_source(db_i))
    inx_ok: list[dict] = []
    for r in rows_i:
        props = r.get("properties", {})
        clave = extract_property_value(props.get("Clave", {}))
        rel = props.get("PTN Proyecto", {}).get("relation", [])
        if (clave or "").startswith("todoist:") and rel:
            inx_ok.append(r)

    print("=== Validación caso 2 (Todoist -> PTN -> INX) ===\n")
    print(f"TODOIST-TAREAS: {len(rows_t)} filas únicas (por page_id)")
    print(f"  - Con relación PTN Proyecto: {len(with_ptn)}")
    print(f"INX-ENLACES: {len(rows_i)} filas únicas")
    print(f"  - Clave todoist:* con PTN Proyecto: {len(inx_ok)}")

    if with_ptn:
        print("\nEjemplos (TODOIST-TAREAS con PTN Proyecto), hasta 5:")
        for r in with_ptn[:5]:
            p = r.get("properties", {})
            tid = extract_property_value(p.get("Todoist ID", {}))
            title = extract_property_value(p.get("Tarea", {})) or "(sin titulo)"
            print(f"  - tid={tid} | {title[:70]}")

    if inx_ok:
        print("\nEjemplos (INX todoist:* con PTN Proyecto), hasta 5:")
        for r in inx_ok[:5]:
            p = r.get("properties", {})
            clave = extract_property_value(p.get("Clave", {}))
            title = extract_property_value(p.get("Elemento", {})) or "(sin titulo)"
            print(f"  - {clave} | {title[:70]}")

    if len(with_ptn) == 0:
        print("\n[!] No hay ninguna fila en TODOIST-TAREAS con PTN Proyecto.")
        print("    Enlaza manualmente en Notion (caso 2) y vuelve a ejecutar sync INX.")
        return 1

    if len(inx_ok) == 0:
        print("\n[!] INX no tiene filas todoist:* con PTN Proyecto tras el estado actual.")
        print("    Ejecuta: apps\\inx_sync_todoist.bat 200 --no-pause")
        return 1

    if len(inx_ok) < len(with_ptn):
        print(
            f"\n[?] INX tiene {len(inx_ok)} filas con PTN pero TODOIST-TAREAS tiene {len(with_ptn)} con PTN."
            " Puede ser normal si aún no has corrido sync INX tras enlazar."
        )

    print("\nOK: la cadena caso 2 está verificable (hay PTN en INX para fuente Todoist).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
