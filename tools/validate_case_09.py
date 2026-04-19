"""
Validacion del caso de uso 9: Paper BIB -> ficha de lectura Obsidian -> INX.

Contrato:
- Cada ficha .md bajo A1-INV/B13-PUB/C137-ART (y C138-COM, C139-REV) con
  frontmatter 'citekey: X' se considera ficha-de-lectura.
- Para cada ficha detectada:
  * X existe como paper en BIB (propiedad Citekey).
  * La ruta de la ficha aparece en INX-ENLACES como obsidian:<ruta>.
  * El citekey aparece en INX-ENLACES como paperpile:<citekey>.
  * La fila INX obsidian:<ruta> expone `Paperpile Citekey = X`.
  * Cruce doble = ambas filas INX existen para la misma ficha/paper.

Uso:
  python tools/validate_case_09.py
  python tools/validate_case_09.py --scope state
  python tools/validate_case_09.py --scope all
Requiere .env: NOTION_DB_BIB, NOTION_DB_INX, OBSIDIAN_ALPHA_PATH

Exit codes:
  0  OK (todas las fichas detectadas tienen cruce doble).
  1  Gaps detectados o no hay fichas.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import os
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import ALPHA_PATH, get_frontmatter


B13_CONTEXTOS = ["C137-ART", "C138-COM", "C139-REV"]
STATE_MAP = {
    "por leer": "Por leer",
    "en proceso": "En proceso",
    "leyendo": "En proceso",
    "leido": "Leído",
    "leído": "Leído",
    "revisado": "Revisado",
    "descartado": "Descartado",
}


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


def _extract_citekey(md_path: Path) -> str | None:
    try:
        content = md_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end < 0:
        return None
    block = content[3:end]
    for line in block.splitlines():
        line = line.strip()
        if line.lower().startswith("citekey:"):
            return line.split(":", 1)[1].strip()
    return None


def _normalize(value: str) -> str:
    norm = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(ch for ch in norm if not unicodedata.combining(ch))


def _canon_state(value: str) -> str | None:
    return STATE_MAP.get(_normalize(value))


def _find_fichas() -> list[dict]:
    fichas: list[dict] = []
    for ctx in B13_CONTEXTOS:
        base = ALPHA_PATH / "A1-INV" / "B13-PUB" / ctx
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            citekey = _extract_citekey(md)
            if citekey:
                rel = str(md.relative_to(ALPHA_PATH))
                fm = get_frontmatter(str(md))
                estado = (fm.get("estado-lectura") or "").strip()
                fichas.append(
                    {
                        "path": str(md),
                        "ruta": rel,
                        "citekey": citekey,
                        "estado_frontmatter": estado,
                        "estado_canonico": _canon_state(estado) if estado else None,
                    }
                )
    return fichas


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["cross", "state", "all"], default="cross")
    args = parser.parse_args()

    db_bib = os.getenv("NOTION_DB_BIB")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_bib or not db_inx:
        print("Faltan NOTION_DB_BIB o NOTION_DB_INX en .env")
        return 2

    rows_bib = _dedupe_rows(query_data_source(db_bib))
    bib_citekeys: set[str] = set()
    bib_estado: dict[str, str] = {}
    for r in rows_bib:
        ck = (extract_property_value(r.get("properties", {}).get("Citekey", {})) or "").strip()
        if ck:
            norm_ck = ck.lower()
            bib_citekeys.add(norm_ck)
            bib_estado[norm_ck] = extract_property_value(r.get("properties", {}).get("Estado", {})) or ""

    rows_inx = _dedupe_rows(query_data_source(db_inx))
    inx_obsidian: set[str] = set()
    inx_obsidian_paperpile: dict[str, str] = {}
    inx_paperpile: set[str] = set()
    for r in rows_inx:
        props = r.get("properties", {})
        clave = (extract_property_value(props.get("Clave", {})) or "")
        if clave.startswith("obsidian:"):
            ruta = clave[len("obsidian:") :]
            inx_obsidian.add(ruta)
            inx_obsidian_paperpile[ruta] = extract_property_value(props.get("Paperpile Citekey", {})) or ""
        elif clave.startswith("paperpile:"):
            inx_paperpile.add(clave[len("paperpile:") :])

    fichas = _find_fichas()

    match_bib = [f for f in fichas if f["citekey"].lower() in bib_citekeys]
    match_inx_obs = [f for f in fichas if f["ruta"] in inx_obsidian]
    match_inx_paperpile = [f for f in fichas if f["citekey"] in inx_paperpile]
    match_explicit = [f for f in fichas if inx_obsidian_paperpile.get(f["ruta"], "") == f["citekey"]]
    match_doble = [
        f for f in fichas
        if f["ruta"] in inx_obsidian and f["citekey"] in inx_paperpile
    ]

    huerfanas_bib = [f for f in fichas if f["citekey"].lower() not in bib_citekeys]
    faltan_obs = [f for f in fichas if f["ruta"] not in inx_obsidian]
    faltan_pp = [f for f in fichas if f["citekey"] not in inx_paperpile]
    faltan_explicit = [f for f in fichas if inx_obsidian_paperpile.get(f["ruta"], "") != f["citekey"]]

    print("=== Validacion caso 9 (BIB -> ficha Obsidian -> INX) ===\n")
    print(f"BIB: {len(rows_bib)} filas unicas | {len(bib_citekeys)} con Citekey")
    print(f"INX-ENLACES: {len(rows_inx)} filas unicas")
    print(f"  - Clave obsidian:*: {len(inx_obsidian)}")
    print(f"  - Clave paperpile:*: {len(inx_paperpile)}")
    print(f"Fichas detectadas en A1-INV/B13-PUB/{'|'.join(B13_CONTEXTOS)}: {len(fichas)}")
    print()
    print(f"Fichas con citekey presente en BIB: {len(match_bib)}/{len(fichas)}")
    print(f"Fichas con ruta en INX obsidian:*: {len(match_inx_obs)}/{len(fichas)}")
    print(f"Fichas con citekey en INX paperpile:*: {len(match_inx_paperpile)}/{len(fichas)}")
    print(f"Fichas con Paperpile Citekey explicito en obsidian:*: {len(match_explicit)}/{len(fichas)}")
    print(f"Fichas con CRUCE DOBLE (obsidian:* AND paperpile:*): {len(match_doble)}/{len(fichas)}")

    if match_doble:
        print("\nEjemplos de cruce doble (hasta 5):")
        for f in match_doble[:5]:
            print(f"  - {f['citekey']} | {f['ruta'][:80]}")

    if huerfanas_bib:
        print("\n[!] Fichas huerfanas (citekey no existe en BIB) (hasta 5):")
        for f in huerfanas_bib[:5]:
            print(f"  - {f['citekey']} | {f['ruta'][:80]}")
        print("    Revisar el frontmatter o ejecutar: python agents/bib_agent.py sincronizar")

    if faltan_obs:
        print("\n[!] Fichas sin fila INX obsidian:<ruta> (hasta 5):")
        for f in faltan_obs[:5]:
            print(f"  - {f['ruta'][:80]}")
        print("    Ejecuta: python tools/log_obsidian_changes.py && python tools/sync_inx_links.py --source obsidian --limit 200")

    if faltan_pp:
        print("\n[!] Fichas sin fila INX paperpile:<citekey> (hasta 5):")
        for f in faltan_pp[:5]:
            print(f"  - {f['citekey']}")
        print("    Ejecuta: python tools/sync_inx_links.py --source paperpile --limit 200")

    if faltan_explicit:
        print("\n[!] Fichas sin `Paperpile Citekey` explicito en INX obsidian:* (hasta 5):")
        for f in faltan_explicit[:5]:
            got = inx_obsidian_paperpile.get(f["ruta"], "")
            print(f"  - {f['citekey']} | {f['ruta'][:80]} | INX='{got}'")
        print("    Ejecuta: python tools/ensure_inx_paperpile_citekey_field.py")
        print("             y despues: python tools/sync_inx_links.py --source obsidian --limit 200")

    if len(fichas) == 0:
        print("\n[!] No hay fichas de lectura detectadas en A1-INV/B13-PUB/*.")
        print("    Ejecuta: python tools/promote_bib_to_obsidian.py <citekey> --sync")
        return 1

    if huerfanas_bib or faltan_obs or faltan_pp or faltan_explicit:
        if args.scope == "cross":
            return 1

    if args.scope == "cross":
        print("\nOK: todas las fichas detectadas tienen cruce doble obsidian:* <-> paperpile:*.")
        return 0

    invalid_states = [f for f in fichas if f["estado_frontmatter"] and not f["estado_canonico"]]
    missing_state = [f for f in fichas if not f["estado_frontmatter"]]
    mismatch_state = [
        f for f in fichas
        if f["estado_canonico"]
        and f["citekey"].lower() in bib_estado
        and bib_estado[f["citekey"].lower()] != f["estado_canonico"]
    ]

    print("\n=== Validacion estado lectura (Obsidian frontmatter -> BIB) ===\n")
    print(f"Fichas con estado-lectura: {len(fichas) - len(missing_state)}/{len(fichas)}")
    print(f"Estados invalidos/no soportados: {len(invalid_states)}")
    print(f"Mismatch frontmatter vs BIB: {len(mismatch_state)}")

    if missing_state:
        print("\n[!] Fichas sin estado-lectura en frontmatter (hasta 5):")
        for f in missing_state[:5]:
            print(f"  - {f['citekey']} | {f['ruta'][:80]}")

    if invalid_states:
        print("\n[!] Estados no reconocidos en frontmatter (hasta 5):")
        for f in invalid_states[:5]:
            print(f"  - {f['citekey']} | {f['ruta'][:80]} | {f['estado_frontmatter']}")

    if mismatch_state:
        print("\n[!] Fichas con estado-lectura desalineado respecto a BIB (hasta 5):")
        for f in mismatch_state[:5]:
            print(
                f"  - {f['citekey']} | frontmatter={f['estado_canonico']} | "
                f"BIB={bib_estado.get(f['citekey'].lower(), '')} | {f['ruta'][:80]}"
            )
        print("    Ejecuta: python tools/sync_bib_reading_state.py")

    if huerfanas_bib or faltan_obs or faltan_pp or faltan_explicit or invalid_states or mismatch_state:
        return 1

    print("\nOK: todas las fichas detectadas tienen cruce doble obsidian:* <-> paperpile:*.")
    print("OK: el estado-lectura del frontmatter esta alineado con BIB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
