"""
Detecta y archiva filas duplicadas en una base Notion segun una clave configurable.

Notion no permite borrado fisico via API: archiva las filas (soft-delete).
Reversible desde Notion: 'Show archived' -> Restore.

Casos tipicos:
  KIT articulos Inoreader (mismo articulo via 2 rutas o 2 feeds):
    python tools/dedupe_notion_db.py --db-env NOTION_DB_KIT --key Enlace
    python tools/dedupe_notion_db.py --db-env NOTION_DB_KIT --key Enlace --apply

  BIB papers (mismo citekey re-importado):
    python tools/dedupe_notion_db.py --db-env NOTION_DB_BIB --key Citekey
    python tools/dedupe_notion_db.py --db-env NOTION_DB_BIB --key Citekey --apply

  Por titulo (muy estricto, solo igualdad case-insensitive):
    python tools/dedupe_notion_db.py --db-env NOTION_DB_KIT --by-title

Modo deteccion (sin --apply): solo lista grupos de duplicados, no toca nada.
Modo accion (--apply): conserva 1 fila por grupo, archiva el resto.

Politica de conservacion (--keep):
  oldest  - primera fila creada (default, conservador)
  newest  - ultima fila creada
  lowest  - page_id alfabeticamente menor (estable e idempotente)

Filas con clave vacia se ignoran (no se consideran duplicadas entre si).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Forzar UTF-8 en stdout (consola Windows usa CP1252 por defecto y rompe con
# emojis/caracteres no-latinos en los titulos Notion).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import (
    archive_page,
    extract_property_value,
    get_data_source_schema,
    query_data_source,
)


def _find_title_field(db_id: str) -> str | None:
    """Detecta el campo title del schema (Notion permite uno solo)."""
    schema = get_data_source_schema(db_id)
    for name, ptype in (schema.get("property_types") or {}).items():
        if ptype == "title":
            return name
    # Fallback heuristico
    for cand in ("Titulo", "Título", "Title", "Nombre", "Name", "Elemento"):
        if cand in (schema.get("properties") or []):
            return cand
    return None


def _row_key(row: dict, key_field: str | None,
             by_title: bool, title_field: str | None) -> str:
    props = row.get("properties", {})
    if by_title and title_field:
        return (extract_property_value(props.get(title_field, {})) or "").strip().lower()
    if key_field:
        return (extract_property_value(props.get(key_field, {})) or "").strip()
    return ""


def _row_title(row: dict, title_field: str | None) -> str:
    if not title_field:
        return "(sin campo titulo)"
    return (extract_property_value(row.get("properties", {}).get(title_field, {}))
            or "(sin titulo)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dedupe filas duplicadas en una base Notion (archive soft-delete)",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--db", help="ID literal del data source / database")
    src.add_argument("--db-env", help="Nombre de la variable .env que contiene el ID")

    keysrc = parser.add_mutually_exclusive_group(required=True)
    keysrc.add_argument("--key",
                        help="Nombre del campo Notion para dedupe (rich_text, url, etc.)")
    keysrc.add_argument("--by-title", action="store_true",
                        help="Dedupe por titulo (case-insensitive trim)")

    parser.add_argument("--keep", default="oldest",
                        choices=["oldest", "newest", "lowest"],
                        help="Politica de conservacion: cual fila se queda (default oldest)")
    parser.add_argument("--apply", action="store_true",
                        help="Archiva las copias. Sin esta flag solo lista (dry-run)")
    parser.add_argument("--limit-groups", type=int, default=None,
                        help="Procesa solo los N primeros grupos (pruebas)")
    args = parser.parse_args()

    db_id = args.db or os.getenv(args.db_env or "", "")
    if not db_id:
        env_label = args.db_env or "(--db)"
        print(f"[ERROR] Falta ID. Pasa --db <id> o pon {env_label} en .env")
        return 2

    title_field = _find_title_field(db_id)
    if args.by_title and not title_field:
        print("[ERROR] No se detecto campo de tipo 'title' en el schema")
        return 2
    key_label = title_field if args.by_title else args.key

    print(f"[notion] consultando {db_id}...")
    rows = query_data_source(db_id)
    print(f"[notion] {len(rows)} filas totales | campo dedupe: '{key_label}'")

    groups: dict[str, list] = defaultdict(list)
    for row in rows:
        key = _row_key(row, args.key, args.by_title, title_field)
        if not key:
            continue
        groups[key].append(row)

    dups = {k: v for k, v in groups.items() if len(v) > 1}
    if not dups:
        print(f"[ok] Sin duplicados por '{key_label}'")
        return 0

    affected = sum(len(v) for v in dups.values())
    will_drop = affected - len(dups)
    print(f"[dups] {len(dups)} grupos con duplicados | {affected} filas afectadas | "
          f"{will_drop} se archivarian (--keep={args.keep})")
    print()

    archived = 0
    errors = 0
    grupos_procesados = 0
    for key, rows in sorted(dups.items()):
        if args.limit_groups and grupos_procesados >= args.limit_groups:
            break
        grupos_procesados += 1

        if args.keep == "oldest":
            rows.sort(key=lambda r: r.get("created_time", ""))
        elif args.keep == "newest":
            rows.sort(key=lambda r: r.get("created_time", ""), reverse=True)
        else:  # lowest
            rows.sort(key=lambda r: r["id"])
        keeper = rows[0]
        losers = rows[1:]

        print(f"[group] {key_label}={key[:80]}")
        print(f"  KEEP   {keeper['id']}  {keeper.get('created_time','?')}  "
              f"{_row_title(keeper, title_field)[:60]}")
        for loser in losers:
            print(f"  DROP   {loser['id']}  {loser.get('created_time','?')}  "
                  f"{_row_title(loser, title_field)[:60]}")
            if args.apply:
                for attempt in range(5):
                    try:
                        archive_page(loser["id"])
                        archived += 1
                        break
                    except Exception as exc:
                        if attempt == 4:
                            errors += 1
                            print(f"    [err] {exc}")
                        time.sleep(1 + attempt)
                time.sleep(0.25)
        print()

    if args.apply:
        print(f"[done] {archived} filas archivadas, {errors} errores")
    else:
        print("[dry] sin --apply no se archivo nada. Repite con --apply para confirmar.")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
