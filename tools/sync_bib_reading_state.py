"""
Sincroniza `estado-lectura` desde fichas Obsidian hacia BIB (Notion).

Contrato:
- Escanea fichas de lectura bajo A1-INV/B13-PUB/{C137-ART,C138-COM,C139-REV}
- Lee frontmatter `citekey` + `estado-lectura`
- Actualiza `BIB.Estado` para el paper con ese citekey

Uso:
    python tools/sync_bib_reading_state.py
    python tools/sync_bib_reading_state.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, query_data_source, update_page_properties
from tools.obsidian_tools import ALPHA_PATH, get_frontmatter


B13_CONTEXTOS = ("C137-ART", "C138-COM", "C139-REV")
STATE_MAP = {
    "por leer": "Por leer",
    "en proceso": "En proceso",
    "leyendo": "En proceso",
    "leido": "Leído",
    "leído": "Leído",
    "revisado": "Revisado",
    "descartado": "Descartado",
}


def _normalize(value: str) -> str:
    norm = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(ch for ch in norm if not unicodedata.combining(ch))


def _canon_state(value: str) -> str | None:
    return STATE_MAP.get(_normalize(value))


def _scan_fichas() -> list[dict]:
    fichas: list[dict] = []
    for ctx in B13_CONTEXTOS:
        base = ALPHA_PATH / "A1-INV" / "B13-PUB" / ctx
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            fm = get_frontmatter(str(md))
            citekey = (fm.get("citekey") or "").strip()
            estado = (fm.get("estado-lectura") or "").strip()
            if citekey and estado:
                fichas.append(
                    {
                        "ruta": str(md.relative_to(ALPHA_PATH)),
                        "path": str(md),
                        "citekey": citekey,
                        "estado_frontmatter": estado,
                        "estado_canonico": _canon_state(estado),
                    }
                )
    return fichas


def _bib_map(db_bib: str) -> dict[str, dict]:
    mapping: dict[str, dict] = {}
    for row in query_data_source(db_bib):
        props = row.get("properties", {})
        citekey = (extract_property_value(props.get("Citekey", {})) or "").strip()
        if not citekey:
            continue
        mapping[citekey.lower()] = {
            "id": row["id"],
            "estado": extract_property_value(props.get("Estado", {})) or "",
        }
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Solo informa cambios, no escribe en Notion.")
    args = parser.parse_args()

    db_bib = os.getenv("NOTION_DB_BIB")
    if not db_bib:
        print("Falta NOTION_DB_BIB en .env")
        return 2

    fichas = _scan_fichas()
    bib = _bib_map(db_bib)

    invalid = [f for f in fichas if not f["estado_canonico"]]
    missing = [f for f in fichas if f["citekey"].lower() not in bib]
    changes = []
    for ficha in fichas:
        ck = ficha["citekey"].lower()
        if ck not in bib or not ficha["estado_canonico"]:
            continue
        bib_estado = bib[ck]["estado"]
        if bib_estado != ficha["estado_canonico"]:
            changes.append(
                {
                    "citekey": ficha["citekey"],
                    "ruta": ficha["ruta"],
                    "from": bib_estado,
                    "to": ficha["estado_canonico"],
                    "page_id": bib[ck]["id"],
                }
            )

    print("=== Sync estado-lectura Obsidian -> BIB ===\n")
    print(f"Fichas con citekey + estado-lectura: {len(fichas)}")
    print(f"Estados invalidos/no soportados: {len(invalid)}")
    print(f"Fichas sin paper en BIB: {len(missing)}")
    print(f"Cambios requeridos: {len(changes)}")

    if invalid:
        print("\n[!] Estados no reconocidos (hasta 5):")
        for item in invalid[:5]:
            print(f"  - {item['citekey']} | {item['ruta']} | {item['estado_frontmatter']}")

    if missing:
        print("\n[!] Fichas sin paper correspondiente en BIB (hasta 5):")
        for item in missing[:5]:
            print(f"  - {item['citekey']} | {item['ruta']}")

    if changes:
        print("\nCambios detectados (hasta 10):")
        for item in changes[:10]:
            print(f"  - {item['citekey']} | {item['from'] or '(vacio)'} -> {item['to']} | {item['ruta']}")

    if args.dry_run:
        print("\n[dry-run] no se escribe nada.")
        return 0 if not invalid else 1

    for item in changes:
        update_page_properties(item["page_id"], {"Estado": {"select": {"name": item["to"]}}})

    print(f"\nOK: cambios aplicados: {len(changes)}")
    return 0 if not invalid else 1


if __name__ == "__main__":
    raise SystemExit(main())
