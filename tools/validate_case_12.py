"""
Validacion del caso de uso 12: cobertura completa vault Obsidian en INX.

Contrato:
- Cada .md del vault debe tener fila en OBSIDIAN_DB (propiedad Ruta).
- Cada fila OBSIDIAN_DB debe tener fila INX-ENLACES con Clave = obsidian:<ruta>.

Reporta dos deltas:
  vault -> OBSIDIAN_DB (gap que backfill cierra).
  OBSIDIAN_DB -> INX (gap que sync_inx_links --source obsidian cierra).

Uso: python tools/validate_case_12.py
Requiere .env: OBSIDIAN_DB, NOTION_DB_INX, OBSIDIAN_ALPHA_PATH

Exit codes:
  0  OK (cobertura 100% en ambas etapas).
  1  Gaps detectados.
  2  Falta configuracion.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import get_todas_notas


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
    alpha = os.getenv("OBSIDIAN_ALPHA_PATH")
    if not db_o or not db_i or not alpha:
        print("Faltan OBSIDIAN_DB, NOTION_DB_INX o OBSIDIAN_ALPHA_PATH en .env")
        return 2

    vault = [n.get("relativo", "") for n in get_todas_notas()]
    vault_rutas = {r for r in vault if r}

    rows_o = _dedupe_rows(query_data_source(db_o))
    obsidian_db_rutas: set[str] = set()
    for r in rows_o:
        ruta = extract_property_value(r.get("properties", {}).get("Ruta", {}))
        if ruta:
            obsidian_db_rutas.add(ruta)

    rows_i = _dedupe_rows(query_data_source(db_i))
    inx_obsidian: set[str] = set()
    for r in rows_i:
        clave = (extract_property_value(r.get("properties", {}).get("Clave", {})) or "")
        if clave.startswith("obsidian:"):
            inx_obsidian.add(clave[len("obsidian:") :])

    missing_in_db = sorted(vault_rutas - obsidian_db_rutas)
    missing_in_inx = sorted(obsidian_db_rutas - inx_obsidian)
    orphan_db_rows = sorted(obsidian_db_rutas - vault_rutas)

    print("=== Validacion caso 12 (cobertura vault -> OBSIDIAN_DB -> INX) ===\n")
    print(f"Vault (.md detectados): {len(vault_rutas)}")
    print(f"OBSIDIAN_DB filas con Ruta: {len(obsidian_db_rutas)}")
    print(f"INX-ENLACES filas obsidian:*: {len(inx_obsidian)}")
    print()
    print(f"Cobertura vault -> OBSIDIAN_DB: {len(vault_rutas) - len(missing_in_db)}/{len(vault_rutas)}")
    print(f"Cobertura OBSIDIAN_DB -> INX: {len(obsidian_db_rutas) - len(missing_in_inx)}/{len(obsidian_db_rutas)}")

    if missing_in_db:
        print(f"\n[!] Notas del vault sin fila OBSIDIAN_DB ({len(missing_in_db)}):")
        for r in missing_in_db[:5]:
            print(f"  - {r[:100]}")
        if len(missing_in_db) > 5:
            print(f"  (+{len(missing_in_db) - 5} mas)")
        print("    Ejecuta: python tools/backfill_obsidian_to_inx.py --sync")

    if missing_in_inx:
        print(f"\n[!] Filas OBSIDIAN_DB sin INX obsidian:<ruta> ({len(missing_in_inx)}):")
        for r in missing_in_inx[:5]:
            print(f"  - {r[:100]}")
        print("    Ejecuta: python tools/sync_inx_links.py --source obsidian --limit 200")

    if orphan_db_rows:
        print(f"\n[info] Filas OBSIDIAN_DB con Ruta que ya no existe en vault ({len(orphan_db_rows)}):")
        for r in orphan_db_rows[:5]:
            print(f"  - {r[:100]}")
        print("    Puede ser normal (notas renombradas/eliminadas). No bloquea el caso 12.")

    if missing_in_db or missing_in_inx:
        return 1

    print("\nOK: cobertura 100% vault -> OBSIDIAN_DB -> INX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
