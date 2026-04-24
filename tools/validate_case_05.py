"""
Validacion del caso de uso 5: importar repo GitHub a REP y enlazar a PTN (INX).

Contrato base (alcance B):
- NOTION_DB_REPOS tiene N repos.
- INX-ENLACES tiene una fila por cada repo con Clave = 'github:<Nombre>'.
- La fila INX lleva Elemento (=Nombre), Fuente=GitHub, URL del repo si REP la tiene.

Chequeo adicional opcional (alcance C):
- Sin duplicados en REP por Nombre ni por URL.
- Sin filas github:* INX que no correspondan a un repo REP (huerfanas).
- Sin filas INX con Fuente!=GitHub para clave github:*.
- Reporta cuantos github:* tienen PTN Proyecto enlazado (informativo,
  no bloquea: el doc historico mencionaba >=1 enlace, pero el caso no lo
  exige).

Uso:
  python tools/validate_case_05.py
  python tools/validate_case_05.py --scope c
Requiere .env: NOTION_DB_REPOS, NOTION_DB_INX

Exit codes:
  0  OK.
  1  REP repos sin fila INX github:<nombre> O huerfanas o duplicados o fuente mismatch.
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


def _scope_c(rep_rows: list[dict], inx_github: dict[str, dict],
             rep_names: set[str]) -> int:
    """Validaciones extras: dedupe REP, huerfanas INX, fuente mismatch."""
    fails = 0

    # 1. Duplicados en REP por Nombre
    by_nombre: dict[str, list[dict]] = defaultdict(list)
    by_url: dict[str, list[dict]] = defaultdict(list)
    for r in rep_rows:
        props = r.get("properties", {})
        nombre = (extract_property_value(props.get("Nombre", {})) or "").strip()
        url = (extract_property_value(props.get("URL", {})) or "").strip()
        if nombre:
            by_nombre[nombre].append(r)
        if url:
            by_url[url].append(r)
    dups_nombre = {k: v for k, v in by_nombre.items() if len(v) > 1}
    dups_url = {k: v for k, v in by_url.items() if len(v) > 1}

    # 2. Huerfanas INX (en INX pero no en REP)
    huerfanas_inx = sorted(set(inx_github.keys()) - rep_names)

    # 3. Fuente mismatch
    fuente_mismatch = []
    for nombre, row in inx_github.items():
        fuente = extract_property_value(row.get("properties", {}).get("Fuente", {})) or ""
        if fuente and fuente != "GitHub":
            fuente_mismatch.append({"clave": f"github:{nombre}", "fuente": fuente})

    # 4. Linked to PTN (informativo, no bloquea)
    linked = []
    for nombre, row in inx_github.items():
        rel = row.get("properties", {}).get("PTN Proyecto", {}).get("relation", [])
        if rel:
            linked.append(nombre)

    print("\n=== Validacion alcance C (REP coherencia + INX huerfanas + Fuente) ===\n")
    print(f"REP duplicados por Nombre:           {len(dups_nombre)} grupos")
    print(f"REP duplicados por URL:              {len(dups_url)} grupos")
    print(f"INX github:* sin REP correspondiente: {len(huerfanas_inx)}")
    print(f"INX github:* con Fuente != GitHub:   {len(fuente_mismatch)}")
    print(f"INX github:* enlazados a PTN Proyecto: {len(linked)} (informativo)")

    if dups_nombre:
        print("\n[!] Duplicados REP por Nombre (hasta 5):")
        for nombre in list(dups_nombre.keys())[:5]:
            print(f"  - {nombre} ({len(dups_nombre[nombre])} filas)")
        print("    Ejecuta: python tools/dedupe_notion_db.py --db-env NOTION_DB_REPOS --by-title --apply")
        fails += 1
    if dups_url:
        print("\n[!] Duplicados REP por URL (hasta 5):")
        for url in list(dups_url.keys())[:5]:
            print(f"  - {url} ({len(dups_url[url])} filas)")
        print("    Ejecuta: python tools/dedupe_notion_db.py --db-env NOTION_DB_REPOS --key URL --apply")
        fails += 1
    if huerfanas_inx:
        print("\n[!] Huerfanas INX (github:* sin REP, hasta 5):")
        for n in huerfanas_inx[:5]:
            print(f"  - github:{n}")
        print("    Diagnosticar manualmente: repos archivados/renombrados en GitHub o REP")
        fails += 1
    if fuente_mismatch:
        print("\n[!] Filas github:* con Fuente != GitHub (hasta 5):")
        for row in fuente_mismatch[:5]:
            print(f"  - {row['clave']} | Fuente={row['fuente']}")
        print("    Ejecuta: python tools/sync_inx_links.py --source github --limit 200")
        fails += 1

    if linked:
        print(f"\nRepos enlazados a PTN Proyecto: {len(linked)} (hasta 5):")
        for n in linked[:5]:
            print(f"  - github:{n}")

    if fails:
        return 1
    print("\nOK: REP sin duplicados, INX sin huerfanas github:*, Fuente coherente.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["b", "c"], default="b")
    args = parser.parse_args()

    db_repos = os.getenv("NOTION_DB_REPOS")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_repos or not db_inx:
        print("Faltan NOTION_DB_REPOS o NOTION_DB_INX en .env")
        return 2

    rep_rows = _dedupe_rows(query_data_source(db_repos))
    rep_entries: list[dict] = []
    rep_names: set[str] = set()
    for r in rep_rows:
        props = r.get("properties", {})
        nombre = (extract_property_value(props.get("Nombre", {})) or "").strip()
        if not nombre:
            continue
        url = extract_property_value(props.get("URL", {})) or ""
        rep_entries.append({"page_id": r["id"], "nombre": nombre, "url": url})
        rep_names.add(nombre)

    inx_rows = _dedupe_rows(query_data_source(db_inx))
    inx_github: dict[str, dict] = {}
    for r in inx_rows:
        props = r.get("properties", {})
        clave = extract_property_value(props.get("Clave", {})) or ""
        if clave.startswith("github:"):
            nombre = clave[len("github:"):]
            inx_github[nombre] = r

    matched = [e for e in rep_entries if e["nombre"] in inx_github]
    missing = [e for e in rep_entries if e["nombre"] not in inx_github]

    print("=== Validacion caso 5 (REP -> INX-ENLACES) ===\n")
    print(f"REP: {len(rep_rows)} filas unicas")
    print(f"  - Con Nombre: {len(rep_entries)}")
    print(f"INX-ENLACES: {len(inx_rows)} filas unicas")
    print(f"  - Clave github:*: {len(inx_github)}")
    print(f"\nREP entries presentes en INX: {len(matched)}/{len(rep_entries)}")

    if matched:
        print("\nEjemplos (hasta 5):")
        for e in matched[:5]:
            print(f"  - github:{e['nombre']} | {e['url'][:70]}")

    if missing:
        print("\n[!] REP entries sin fila INX github:<nombre> (hasta 5):")
        for e in missing[:5]:
            print(f"  - github:{e['nombre']} | {e['url'][:70]}")
        print("\n    Ejecuta: python tools/sync_inx_links.py --source github --limit 200")
        return 1

    if len(rep_entries) == 0:
        print("\n[!] No hay entradas con Nombre en NOTION_DB_REPOS.")
        return 1

    print("\nOK: todos los repos REP estan reflejados en INX-ENLACES.")

    if args.scope == "c":
        return _scope_c(rep_rows, inx_github, rep_names)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
