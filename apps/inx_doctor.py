"""
Doctor de calidad de INX-ENLACES.

Reporta:
- Conteo de filas por Fuente y Estado.
- Filas INX sin relación PTN (Proyecto/Tarea/Nota).
- Repos en REP-Repositorios sin entrada INX (huérfanos GitHub).
- Papers en BIB-Bibliografía sin entrada INX (huérfanos Paperpile).
- Claves duplicadas (mismo `Clave` en más de una fila).
"""

from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import query_data_source, extract_property_value


def _get(props: dict, name: str) -> str:
    return extract_property_value(props.get(name, {})) if props else ""


def _has_relation(props: dict, name: str) -> bool:
    return bool(props.get(name, {}).get("relation"))


def main() -> int:
    db_inx = os.getenv("NOTION_DB_INX")
    db_repos = os.getenv("NOTION_DB_REPOS")
    db_bib = os.getenv("NOTION_DB_BIB")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    inx_rows = query_data_source(db_inx)
    print(f"\n=== INX-ENLACES: {len(inx_rows)} filas ===")

    by_source = Counter()
    by_state = Counter()
    sin_ptn = []
    claves = defaultdict(list)
    inx_keys = set()

    for r in inx_rows:
        p = r["properties"]
        clave = _get(p, "Clave")
        elemento = _get(p, "Elemento")
        fuente = _get(p, "Fuente") or "(sin fuente)"
        estado = _get(p, "Estado") or "(sin estado)"
        by_source[fuente] += 1
        by_state[estado] += 1
        if clave:
            claves[clave].append(elemento)
            inx_keys.add(clave)
        tiene_ptn = any(_has_relation(p, k) for k in ("PTN Proyecto", "PTN Tarea", "PTN Nota"))
        if not tiene_ptn:
            sin_ptn.append((clave or "(sin clave)", elemento, fuente))

    print("\nPor Fuente:")
    for k, v in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {k:12s} {v}")
    print("\nPor Estado:")
    for k, v in sorted(by_state.items(), key=lambda x: -x[1]):
        print(f"  {k:12s} {v}")

    duplicados = {k: v for k, v in claves.items() if len(v) > 1}
    if duplicados:
        print(f"\n[WARN] {len(duplicados)} claves duplicadas:")
        for k, v in list(duplicados.items())[:10]:
            print(f"  {k}: {v}")
    else:
        print("\n[OK] Sin claves duplicadas")

    print(f"\nINX sin relación PTN: {len(sin_ptn)}")
    for clave, elem, fuente in sin_ptn[:15]:
        print(f"  [{fuente}] {clave} — {elem}")
    if len(sin_ptn) > 15:
        print(f"  ... ({len(sin_ptn) - 15} más)")

    if db_repos:
        repos = query_data_source(db_repos)
        huerfanos = [
            _get(r["properties"], "Nombre")
            for r in repos
            if _get(r["properties"], "Nombre")
            and f"github:{_get(r['properties'], 'Nombre')}" not in inx_keys
        ]
        print(f"\nREP huérfanos (sin INX): {len(huerfanos)} / {len(repos)}")
        for n in huerfanos[:10]:
            print(f"  - {n}")
        if len(huerfanos) > 10:
            print(f"  ... ({len(huerfanos) - 10} más)")
        print("  Solución: python tools/sync_inx_links.py --source github")

    if db_bib:
        papers = query_data_source(db_bib)
        huerfanos = [
            _get(r["properties"], "Citekey")
            for r in papers
            if _get(r["properties"], "Citekey")
            and f"paperpile:{_get(r['properties'], 'Citekey')}" not in inx_keys
        ]
        print(f"\nBIB huérfanos (sin INX): {len(huerfanos)} / {len(papers)}")
        for c in huerfanos[:10]:
            print(f"  - {c}")
        if len(huerfanos) > 10:
            print(f"  ... ({len(huerfanos) - 10} más)")
        print("  Solución: python tools/sync_inx_links.py --source paperpile")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
