"""
Limpieza opcional: vacia las propiedades legacy 'Proyecto' y 'Tarea'
(rich_text) de PTN-Notas para filas cuya relation 'Proyecto PTN' / 'Tarea PTN'
ya contiene el mismo UUID (confirmando que la migracion produjo la fuente
unica correcta).

Solo limpia las legacy; no toca 'Ruta Obsidian', 'Proyecto PTN' ni 'Tarea PTN'.
No toca filas cuyo valor legacy no sea un UUID valido o cuya relation no
coincida con el ID del legacy (caso en que la migracion aun no reflejo esa
fila o tenia contenido no migrable).

Idempotente. --dry-run previsualiza.

Uso:
    python tools/cleanup_notas_legacy_props.py --dry-run
    python tools/cleanup_notas_legacy_props.py

Exit codes:
  0  OK.
  1  Errores al actualizar filas.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

from tools.notion_tools import (
    extract_property_value,
    query_data_source,
    update_page_properties,
)


LEGACY_TO_RELATION = {
    "Proyecto": "Proyecto PTN",
    "Tarea": "Tarea PTN",
}


def _is_uuid(value: str) -> bool:
    v = (value or "").replace("-", "").strip()
    return len(v) == 32 and all(c in "0123456789abcdef" for c in v.lower())


def _normalize(uuid_str: str) -> str:
    return (uuid_str or "").replace("-", "").lower().strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    db_notas = os.environ.get("NOTION_DS_NOTAS")
    if not db_notas:
        print("[error] Falta NOTION_DS_NOTAS en .env")
        return 2

    print("=== Limpieza legacy Proyecto/Tarea (rich_text) en PTN-Notas ===")
    print(f"    dry_run={args.dry_run}, db={db_notas}")

    rows = query_data_source(db_notas)
    to_clean: list[tuple[str, dict]] = []
    skipped_no_uuid = 0
    skipped_no_match = 0
    skipped_empty = 0

    for row in rows:
        props = row.get("properties", {})
        updates: dict = {}

        for legacy, rel_prop in LEGACY_TO_RELATION.items():
            legacy_val = (extract_property_value(props.get(legacy, {})) or "").strip()
            if not legacy_val:
                skipped_empty += 1
                continue
            if not _is_uuid(legacy_val):
                skipped_no_uuid += 1
                continue
            rel = props.get(rel_prop, {}).get("relation", []) or []
            rel_ids_norm = {_normalize(r.get("id", "")) for r in rel if r.get("id")}
            if _normalize(legacy_val) not in rel_ids_norm:
                skipped_no_match += 1
                continue
            updates[legacy] = {"rich_text": []}

        if updates:
            to_clean.append((row["id"], updates))

    print(f"[scan] total filas: {len(rows)}")
    print(f"[scan] legacy vacia: {skipped_empty}")
    print(f"[scan] legacy no-UUID: {skipped_no_uuid}")
    print(f"[scan] legacy UUID pero no coincide con relation: {skipped_no_match}")
    print(f"[scan] a limpiar: {len(to_clean)}")

    for page_id, updates in to_clean[:5]:
        claves = ", ".join(updates.keys())
        print(f"    {page_id[:8]}... -> vacia {claves}")
    if len(to_clean) > 5:
        print(f"    (+{len(to_clean) - 5} mas)")

    if args.dry_run:
        print("[dry-run] no se aplica nada.")
        return 0

    if not to_clean:
        print("[cleanup] nada que limpiar.")
        return 0

    ok = 0
    errors = 0
    for page_id, updates in to_clean:
        try:
            update_page_properties(page_id, updates)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {page_id}: {exc}", file=sys.stderr)
            errors += 1

    print(f"[cleanup] limpiadas OK: {ok}")
    if errors:
        print(f"[cleanup] errores: {errors}")
        return 1
    print("[cleanup] completa. Las legacy 'Proyecto'/'Tarea' quedan vacias donde la relation ya cubria.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
