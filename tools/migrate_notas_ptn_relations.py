"""
Migracion: convierte los IDs rich_text de 'Proyecto' y 'Tarea' en PTN-Notas
a relations reales contra NOTION_DS_PROYECTOS y NOTION_DS_TAREAS.

Pasos:
  1. Crea las propiedades relation 'Proyecto PTN' y 'Tarea PTN' en
     NOTION_DS_NOTAS si no existen (tipo single_property apuntando a las
     bases correspondientes).
  2. Para cada fila: si la propiedad legacy contiene un UUID valido y la
     relation nueva esta vacia, agrega la relation.
  3. No toca las propiedades legacy ('Proyecto' / 'Tarea' rich_text); el
     usuario decide cuando limpiarlas.

Idempotente. --dry-run previsualiza.

Uso:
    python tools/migrate_notas_ptn_relations.py --dry-run
    python tools/migrate_notas_ptn_relations.py

Exit codes:
  0  OK.
  1  Errores durante la migracion de filas.
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
    update_database_properties,
    update_page_properties,
)


NEW_PROYECTO = "Proyecto PTN"
NEW_TAREA = "Tarea PTN"
OLD_PROYECTO = "Proyecto"
OLD_TAREA = "Tarea"


def _is_uuid(value: str) -> bool:
    v = (value or "").replace("-", "").strip()
    return len(v) == 32 and all(c in "0123456789abcdef" for c in v.lower())


def _schema_has(rows: list[dict], prop: str) -> bool:
    if not rows:
        return False
    return prop in rows[0].get("properties", {})


def _ensure_relation(db_id: str, rows: list[dict], prop: str, target_db: str, dry_run: bool) -> bool:
    if _schema_has(rows, prop):
        print(f"[schema] {prop!r} ya existe.")
        return False
    action = "Se crearia" if dry_run else "Creando"
    print(f"[schema] {prop!r} no existe. {action} como relation -> {target_db}")
    if not dry_run:
        update_database_properties(
            db_id,
            {prop: {"relation": {"database_id": target_db, "type": "single_property", "single_property": {}}}},
        )
        print(f"[schema] {prop!r} creada.")
    return True


def _current_relation_ids(props: dict, prop: str) -> set[str]:
    rel = props.get(prop, {}).get("relation", []) or []
    return {r.get("id") for r in rel if r.get("id")}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    db_notas = os.environ.get("NOTION_DS_NOTAS")
    db_proy = os.environ.get("NOTION_DS_PROYECTOS")
    db_tar = os.environ.get("NOTION_DS_TAREAS")
    if not (db_notas and db_proy and db_tar):
        print("[error] Faltan NOTION_DS_NOTAS, NOTION_DS_PROYECTOS o NOTION_DS_TAREAS en .env")
        return 2

    print("=== Migrando Proyecto/Tarea (rich_text) -> Proyecto PTN/Tarea PTN (relation) ===")
    print(f"    dry_run={args.dry_run}, db_notas={db_notas}")

    rows = query_data_source(db_notas)
    schema_changed = False
    schema_changed |= _ensure_relation(db_notas, rows, NEW_PROYECTO, db_proy, args.dry_run)
    schema_changed |= _ensure_relation(db_notas, rows, NEW_TAREA, db_tar, args.dry_run)

    if schema_changed and not args.dry_run:
        rows = query_data_source(db_notas)

    total = len(rows)
    to_migrate: list[tuple[str, dict]] = []
    skipped_no_uuid = 0
    skipped_already = 0

    for row in rows:
        props = row.get("properties", {})
        updates: dict = {}

        for old_name, new_name in [(OLD_PROYECTO, NEW_PROYECTO), (OLD_TAREA, NEW_TAREA)]:
            old_val = (extract_property_value(props.get(old_name, {})) or "").strip()
            if not old_val:
                continue
            if not _is_uuid(old_val):
                skipped_no_uuid += 1
                continue
            current = _current_relation_ids(props, new_name)
            if old_val in current or old_val.replace("-", "") in {c.replace("-", "") for c in current}:
                skipped_already += 1
                continue
            updates[new_name] = {"relation": [{"id": old_val}]}

        if updates:
            to_migrate.append((row["id"], updates))

    print(f"[scan] total filas: {total}")
    print(f"[scan] saltadas por valor no-UUID: {skipped_no_uuid}")
    print(f"[scan] saltadas por ya-migrada: {skipped_already}")
    print(f"[scan] a migrar: {len(to_migrate)}")

    for page_id, updates in to_migrate[:5]:
        claves = ", ".join(updates.keys())
        print(f"    {page_id[:8]}... -> {claves}")
    if len(to_migrate) > 5:
        print(f"    (+{len(to_migrate) - 5} mas)")

    if args.dry_run:
        print("[dry-run] no se aplica nada.")
        return 0

    if not to_migrate:
        print("[migrate] nada que migrar.")
        return 0

    ok = 0
    errors = 0
    for page_id, updates in to_migrate:
        try:
            update_page_properties(page_id, updates)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {page_id}: {exc}", file=sys.stderr)
            errors += 1

    print(f"[migrate] migradas OK: {ok}")
    if errors:
        print(f"[migrate] errores: {errors}")
        return 1
    print(
        "[migrate] completa. Proximos pasos:\n"
        "  1. tools/promote_obsidian_to_ptn.py detecta automaticamente las nuevas\n"
        "     props relation y las rellena al promocionar.\n"
        "  2. Si quieres limpiar las props legacy 'Proyecto' / 'Tarea' (rich_text),\n"
        "     hazlo manualmente desde Notion o con un script follow-up."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
