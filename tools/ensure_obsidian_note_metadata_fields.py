"""
Garantiza campos de metadata de notas Obsidian en OBSIDIAN_DB e INX-ENLACES.

OBSIDIAN_DB recibe nombres directos desde frontmatter:
Estado, Tags, Personas, Fuente, Proyecto, Tarea, Alias.

OBSIDIAN_DB recibe tambien campos derivados de ruta:
Ruta Area, Ruta Bloque, Ruta Contexto, Ruta Proyecto, Ruta Tarea,
Ruta Nota, Ruta Nivel.

INX-ENLACES recibe nombres prefijados para no chocar con Fuente/Estado del
propio puente:
Nota Estado, Nota Tags, Nota Personas, Nota Fuente, Nota Proyecto,
Nota Tarea, Nota Alias, Nota Tipo, Obsidian Area, Obsidian Bloque,
Obsidian Contexto, Obsidian Proyecto, Obsidian Tarea, Obsidian Nota,
Obsidian Nivel.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import get_data_source_schema, update_database_properties


OBSIDIAN_PROPS = {
    "Estado": {"select": {}},
    "Tags": {"multi_select": {}},
    "Personas": {"multi_select": {}},
    "Fuente": {"rich_text": {}},
    "Proyecto": {"rich_text": {}},
    "Tarea": {"rich_text": {}},
    "Alias": {"rich_text": {}},
    "Ruta Area": {"rich_text": {}},
    "Ruta Bloque": {"rich_text": {}},
    "Ruta Contexto": {"rich_text": {}},
    "Ruta Proyecto": {"rich_text": {}},
    "Ruta Tarea": {"rich_text": {}},
    "Ruta Nota": {"rich_text": {}},
    "Ruta Nivel": {"rich_text": {}},
}

INX_PROPS = {
    "Nota Estado": {"select": {}},
    "Nota Tags": {"multi_select": {}},
    "Nota Personas": {"multi_select": {}},
    "Nota Fuente": {"rich_text": {}},
    "Nota Proyecto": {"rich_text": {}},
    "Nota Tarea": {"rich_text": {}},
    "Nota Alias": {"rich_text": {}},
    "Nota Tipo": {"select": {}},
    "Obsidian Area": {"rich_text": {}},
    "Obsidian Bloque": {"rich_text": {}},
    "Obsidian Contexto": {"rich_text": {}},
    "Obsidian Proyecto": {"rich_text": {}},
    "Obsidian Tarea": {"rich_text": {}},
    "Obsidian Nota": {"rich_text": {}},
    "Obsidian Nivel": {"rich_text": {}},
}


def _ensure(db_id: str, label: str, desired: dict[str, dict], dry_run: bool) -> int:
    schema = get_data_source_schema(db_id)
    existing = set(schema.get("properties", []))
    to_add = {name: prop for name, prop in desired.items() if name not in existing}
    if not to_add:
        print(f"[ok] {label}: schema ya esta completo")
        return 0
    if dry_run:
        print(f"[dry-run] {label}: añadiria {', '.join(sorted(to_add))}")
        return 0
    update_database_properties(db_id, to_add)
    print(f"[add] {label}: {', '.join(sorted(to_add))}")
    return len(to_add)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Asegura campos frontmatter Obsidian en OBSIDIAN_DB/INX")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db_obsidian = os.getenv("OBSIDIAN_DB")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_obsidian or not db_inx:
        print("Faltan OBSIDIAN_DB o NOTION_DB_INX en .env")
        return 2

    _ensure(db_obsidian, "OBSIDIAN_DB", OBSIDIAN_PROPS, args.dry_run)
    _ensure(db_inx, "INX-ENLACES", INX_PROPS, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
