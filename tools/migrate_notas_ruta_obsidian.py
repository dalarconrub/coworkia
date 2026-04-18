"""
Migracion one-shot: separa `Tarea` (ruta Obsidian) de NOTION_DS_NOTAS en una
propiedad dedicada `Ruta Obsidian` (rich_text).

Motivo: hoy `Tarea` en PTN-Notas almacena la ruta relativa de la nota en el
vault Obsidian (caso 03 y caso 07). Su nombre sugiere "tarea PTN relacionada"
(Gap 4 del caso 07). Separar la ruta en `Ruta Obsidian` libera `Tarea` para
su semantica natural y evita retocar validadores futuros.

Efecto:
  1. Si la propiedad `Ruta Obsidian` no existe en NOTION_DS_NOTAS, se crea
     (rich_text).
  2. Para cada fila, si `Tarea` contiene una ruta (termina en `.md`) y
     `Ruta Obsidian` esta vacia, se copia `Tarea` -> `Ruta Obsidian`.
  3. No se modifica `Tarea`; la limpieza queda al usuario cuando decida
     repurposar la propiedad.

Idempotente: se puede ejecutar varias veces. Las filas con `Ruta Obsidian`
ya poblada se saltan.

Uso:
    python tools/migrate_notas_ruta_obsidian.py --dry-run    # previsualiza
    python tools/migrate_notas_ruta_obsidian.py              # aplica

Requisitos:
  - `.env` con NOTION_TOKEN y NOTION_DS_NOTAS.

Exit codes:
  0  OK (incluye --dry-run sin errores).
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


NEW_PROP = "Ruta Obsidian"
OLD_PROP = "Tarea"


def _schema_has_prop(rows: list[dict], prop: str) -> bool:
    """Detecta si una propiedad existe en el schema a partir de filas existentes.

    Notion incluye todas las propiedades del schema en cada page.properties,
    aunque esten vacias. Basta con inspeccionar una fila.
    Si la DB esta vacia, devuelve False (asumimos que hay que crearla).
    """
    if not rows:
        return False
    return prop in rows[0].get("properties", {})


def _ensure_property(db_id: str, rows: list[dict], dry_run: bool) -> bool:
    """Garantiza que existe la propiedad NEW_PROP. Devuelve True si la creo."""
    if _schema_has_prop(rows, NEW_PROP):
        print(f"[schema] {NEW_PROP!r} ya existe en el schema.")
        return False
    action = "Se crearia" if dry_run else "Creando"
    print(f"[schema] {NEW_PROP!r} no existe. {action} como rich_text...")
    if not dry_run:
        update_database_properties(db_id, {NEW_PROP: {"rich_text": {}}})
        print(f"[schema] {NEW_PROP!r} creada.")
    return True


def _looks_like_path(value: str) -> bool:
    return bool(value) and value.strip().endswith(".md")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="No modifica nada; solo imprime el plan y ejemplos.",
    )
    args = parser.parse_args()

    load_dotenv()
    db_notas = os.environ.get("NOTION_DS_NOTAS")
    if not db_notas:
        print("[error] Falta NOTION_DS_NOTAS en .env", file=sys.stderr)
        return 2

    print(f"=== Migrando {OLD_PROP!r} -> {NEW_PROP!r} en NOTION_DS_NOTAS ===")
    print(f"    dry_run={args.dry_run}, db={db_notas}")

    rows = query_data_source(db_notas)
    _ensure_property(db_notas, rows, args.dry_run)

    # Si acabamos de crear la propiedad, re-consultar para que las filas
    # incluyan el campo vacio en sus properties.
    if not args.dry_run and rows and NEW_PROP not in rows[0].get("properties", {}):
        rows = query_data_source(db_notas)

    total = len(rows)
    to_migrate: list[tuple[str, str]] = []
    already = 0
    non_path = 0

    for row in rows:
        props = row.get("properties", {})
        old_val = extract_property_value(props.get(OLD_PROP, {}))
        new_val = extract_property_value(props.get(NEW_PROP, {}))
        if new_val:
            already += 1
            continue
        if not _looks_like_path(old_val):
            non_path += 1
            continue
        to_migrate.append((row["id"], old_val.strip()))

    print(f"[scan] total filas: {total}")
    print(f"[scan] ya migradas ({NEW_PROP!r} poblada): {already}")
    print(f"[scan] {OLD_PROP!r} vacia o no parece ruta (.md): {non_path}")
    print(f"[scan] a migrar: {len(to_migrate)}")

    for page_id, ruta in to_migrate[:5]:
        print(f"    {page_id[:8]}... -> {ruta}")
    if len(to_migrate) > 5:
        print(f"    (+{len(to_migrate) - 5} mas)")

    if args.dry_run:
        print("[dry-run] no se aplica nada. Ejecuta sin --dry-run para migrar.")
        return 0

    if not to_migrate:
        print("[migrate] nada que migrar. Salida 0.")
        return 0

    ok = 0
    errors = 0
    for page_id, ruta in to_migrate:
        try:
            update_page_properties(
                page_id,
                {NEW_PROP: {"rich_text": [{"text": {"content": ruta}}]}},
            )
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
        "  1. tools/promote_obsidian_to_ptn.py ya escribe 'Ruta Obsidian' "
        "(no mas 'Tarea=<ruta>' en nuevas filas).\n"
        "  2. Cuando @Codex/ABGD tenga listo tools/validate_case_07.py, "
        "usar esa propiedad.\n"
        "  3. Si quieres liberar 'Tarea' para su uso semantico original "
        "(relation a tarea PTN), limpia manualmente esa propiedad en las "
        "filas migradas o haz un script de follow-up."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
