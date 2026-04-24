"""
Validacion del caso de uso 6: importar paper Paperpile a BIB y enlazar a PTN/Obsidian (INX).

Contrato base (alcance B):
- NOTION_DB_BIB tiene N papers (con Citekey).
- INX-ENLACES tiene una fila por cada paper con Clave = 'paperpile:<citekey>'.
- La fila INX lleva Elemento (=Titulo o citekey), Fuente=Paperpile,
  URL=DOI si BIB tiene DOI, Detalle con Año y Journal si existen.

Chequeo adicional opcional (alcance C):
- Sin duplicados en BIB por Citekey ni por DOI.
- Sin filas paperpile:* INX que no correspondan a un paper BIB (huerfanas).
- Sin filas INX con Fuente!=Paperpile para clave paperpile:*.
- Reporta cuantos paperpile:* tienen PTN Proyecto enlazado (informativo).

Uso:
  python tools/validate_case_06.py
  python tools/validate_case_06.py --scope c
Requiere .env: NOTION_DB_BIB, NOTION_DB_INX

Exit codes:
  0  OK.
  1  Papers BIB sin fila INX paperpile:<citekey> O huerfanas o duplicados o fuente mismatch.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

sys.stdout.reconfigure(encoding="utf-8")

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, query_data_source


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


def _scope_c(bib_rows: list[dict], inx_paperpile: dict[str, dict],
             bib_citekeys: set[str]) -> int:
    """Validaciones extras: dedupe BIB, huerfanas INX, fuente mismatch."""
    fails = 0

    # 1. Duplicados en BIB por Citekey y por DOI
    by_citekey: dict[str, list[dict]] = defaultdict(list)
    by_doi: dict[str, list[dict]] = defaultdict(list)
    for r in bib_rows:
        props = r.get("properties", {})
        citekey = (extract_property_value(props.get("Citekey", {})) or "").strip()
        doi = (extract_property_value(props.get("DOI", {})) or "").strip()
        if citekey:
            by_citekey[citekey].append(r)
        if doi:
            by_doi[doi].append(r)
    dups_citekey = {k: v for k, v in by_citekey.items() if len(v) > 1}
    dups_doi = {k: v for k, v in by_doi.items() if len(v) > 1}

    # 2. Huerfanas INX (paperpile:* en INX pero no en BIB)
    huerfanas_inx = sorted(set(inx_paperpile.keys()) - bib_citekeys)

    # 3. Fuente mismatch
    fuente_mismatch = []
    for citekey, row in inx_paperpile.items():
        fuente = extract_property_value(row.get("properties", {}).get("Fuente", {})) or ""
        if fuente and fuente != "Paperpile":
            fuente_mismatch.append({"clave": f"paperpile:{citekey}", "fuente": fuente})

    # 4. Linked to PTN (informativo)
    linked = []
    for citekey, row in inx_paperpile.items():
        rel = row.get("properties", {}).get("PTN Proyecto", {}).get("relation", [])
        if rel:
            linked.append(citekey)

    print("\n=== Validacion alcance C (BIB coherencia + INX huerfanas + Fuente) ===\n")
    print(f"BIB duplicados por Citekey:               {len(dups_citekey)} grupos")
    print(f"BIB duplicados por DOI:                   {len(dups_doi)} grupos")
    print(f"INX paperpile:* sin BIB correspondiente:  {len(huerfanas_inx)}")
    print(f"INX paperpile:* con Fuente != Paperpile:  {len(fuente_mismatch)}")
    print(f"INX paperpile:* enlazados a PTN Proyecto: {len(linked)} (informativo)")

    if dups_citekey:
        print("\n[!] Duplicados BIB por Citekey (hasta 5):")
        for citekey in list(dups_citekey.keys())[:5]:
            print(f"  - {citekey} ({len(dups_citekey[citekey])} filas)")
        print("    Ejecuta: python tools/dedupe_notion_db.py --db-env NOTION_DB_BIB --key Citekey --apply")
        fails += 1
    if dups_doi:
        print("\n[!] Duplicados BIB por DOI (hasta 5):")
        for doi in list(dups_doi.keys())[:5]:
            print(f"  - {doi} ({len(dups_doi[doi])} filas)")
        print("    Ejecuta: python tools/dedupe_notion_db.py --db-env NOTION_DB_BIB --key DOI --apply")
        fails += 1
    if huerfanas_inx:
        print("\n[!] Huerfanas INX (paperpile:* sin BIB, hasta 5):")
        for c in huerfanas_inx[:5]:
            print(f"  - paperpile:{c}")
        print("    Diagnosticar manualmente: papers eliminados/renombrados en Paperpile")
        fails += 1
    if fuente_mismatch:
        print("\n[!] Filas paperpile:* con Fuente != Paperpile (hasta 5):")
        for row in fuente_mismatch[:5]:
            print(f"  - {row['clave']} | Fuente={row['fuente']}")
        print("    Ejecuta: python tools/sync_inx_links.py --source paperpile --limit 200")
        fails += 1

    if linked:
        print(f"\nPapers enlazados a PTN Proyecto: {len(linked)} (hasta 5):")
        for c in linked[:5]:
            print(f"  - paperpile:{c}")

    if fails:
        return 1
    print("\nOK: BIB sin duplicados, INX sin huerfanas paperpile:*, Fuente coherente.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["b", "c"], default="b")
    args = parser.parse_args()

    db_bib = os.getenv("NOTION_DB_BIB")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_bib or not db_inx:
        print("Faltan NOTION_DB_BIB o NOTION_DB_INX en .env")
        return 2

    bib_rows = _dedupe_rows(query_data_source(db_bib))
    bib_entries: list[dict] = []
    bib_citekeys: set[str] = set()
    for r in bib_rows:
        props = r.get("properties", {})
        citekey = (extract_property_value(props.get("Citekey", {})) or "").strip()
        if not citekey:
            continue
        titulo = (extract_property_value(props.get("Título", {}))
                  or extract_property_value(props.get("Titulo", {})) or "")
        doi = extract_property_value(props.get("DOI", {})) or ""
        bib_entries.append({"page_id": r["id"], "citekey": citekey,
                             "titulo": titulo, "doi": doi})
        bib_citekeys.add(citekey)

    inx_rows = _dedupe_rows(query_data_source(db_inx))
    inx_paperpile: dict[str, dict] = {}
    for r in inx_rows:
        props = r.get("properties", {})
        clave = extract_property_value(props.get("Clave", {})) or ""
        if clave.startswith("paperpile:"):
            citekey = clave[len("paperpile:"):]
            inx_paperpile[citekey] = r

    matched = [e for e in bib_entries if e["citekey"] in inx_paperpile]
    missing = [e for e in bib_entries if e["citekey"] not in inx_paperpile]

    print("=== Validacion caso 6 (BIB -> INX-ENLACES) ===\n")
    print(f"BIB: {len(bib_rows)} filas unicas")
    print(f"  - Con Citekey: {len(bib_entries)}")
    print(f"INX-ENLACES: {len(inx_rows)} filas unicas")
    print(f"  - Clave paperpile:*: {len(inx_paperpile)}")
    print(f"\nBIB entries presentes en INX: {len(matched)}/{len(bib_entries)}")

    if matched:
        print("\nEjemplos (hasta 5):")
        for e in matched[:5]:
            print(f"  - paperpile:{e['citekey']} | {e['titulo'][:65]}")

    if missing:
        print("\n[!] BIB entries sin fila INX paperpile:<citekey> (hasta 5):")
        for e in missing[:5]:
            print(f"  - paperpile:{e['citekey']} | {e['titulo'][:65]}")
        print("\n    Ejecuta: python tools/sync_inx_links.py --source paperpile --limit 200")
        return 1

    if len(bib_entries) == 0:
        print("\n[!] No hay entradas con Citekey en NOTION_DB_BIB.")
        return 1

    print("\nOK: todos los papers BIB estan reflejados en INX-ENLACES.")

    if args.scope == "c":
        return _scope_c(bib_rows, inx_paperpile, bib_citekeys)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
