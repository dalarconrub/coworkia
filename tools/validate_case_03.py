"""
Validación del caso de uso 3: Obsidian log (OBSIDIAN_DB) -> INX-ENLACES (obsidian:<ruta>).

Uso: python tools/validate_case_03.py
Requiere .env: OBSIDIAN_DB, NOTION_DB_INX
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
    db_o = os.getenv("OBSIDIAN_DB")
    db_i = os.getenv("NOTION_DB_INX")
    if not db_o or not db_i:
        print("Faltan OBSIDIAN_DB o NOTION_DB_INX en .env")
        return 2

    rows_o = _dedupe_rows(query_data_source(db_o))
    rutas: list[str] = []
    rutas_set: set[str] = set()
    with_ptn = 0
    for r in rows_o:
        props = r.get("properties", {})
        ruta = extract_property_value(props.get("Ruta", {}))
        if ruta:
            rutas.append(ruta)
            rutas_set.add(ruta)
        if props.get("PTN Proyecto", {}).get("relation", []) or props.get("PTN Tarea", {}).get("relation", []) or props.get(
            "PTN Nota", {}
        ).get("relation", []):
            with_ptn += 1

    rows_i = _dedupe_rows(query_data_source(db_i))
    inx_obsidian: dict[str, dict] = {}
    inx_with_ptn = 0
    for r in rows_i:
        props = r.get("properties", {})
        clave = extract_property_value(props.get("Clave", {}))
        if not (clave or "").startswith("obsidian:"):
            continue
        ruta = (clave or "")[len("obsidian:") :]
        if ruta:
            inx_obsidian[ruta] = r
        if props.get("PTN Proyecto", {}).get("relation", []) or props.get("PTN Tarea", {}).get("relation", []) or props.get(
            "PTN Nota", {}
        ).get("relation", []):
            inx_with_ptn += 1

    matched = [r for r in rutas if r in inx_obsidian]
    missing = [r for r in rutas if r not in inx_obsidian]

    print("=== Validación caso 3 (Obsidian -> OBSIDIAN_DB -> INX) ===\n")
    print(f"OBSIDIAN_DB: {len(rows_o)} filas únicas (por page_id)")
    print(f"  - Con Ruta: {len(rutas_set)}")
    print(f"  - Con alguna relación PTN (Proyecto/Tarea/Nota): {with_ptn}")
    print(f"INX-ENLACES: {len(rows_i)} filas únicas")
    print(f"  - Clave obsidian:*: {len(inx_obsidian)}")
    print(f"  - Clave obsidian:* con alguna relación PTN: {inx_with_ptn}")
    print(f"\nRutas OBSIDIAN_DB presentes en INX: {len(matched)}/{len(rutas_set)}")

    if matched:
        print("\nEjemplos (INX obsidian:*), hasta 5:")
        for ruta in matched[:5]:
            p = inx_obsidian[ruta].get("properties", {})
            clave = extract_property_value(p.get("Clave", {}))
            title = extract_property_value(p.get("Elemento", {})) or "(sin titulo)"
            print(f"  - {clave} | {title[:70]}")

    if missing:
        print("\n[!] Rutas en OBSIDIAN_DB sin fila INX obsidian:<ruta>, hasta 5:")
        for ruta in missing[:5]:
            print(f"  - {ruta[:120]}")
        print("\n    Ejecuta: apps\\inx_sync_obsidian.bat 200 --no-pause")
        return 1

    if len(rutas_set) == 0:
        print("\n[!] OBSIDIAN_DB no tiene ninguna Ruta. Ejecuta primero el log:")
        print("    python tools\\log_obsidian_changes.py")
        return 1

    print("\nOK: la cadena caso 3 está verificable (rutas de Obsidian reflejadas en INX).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

