"""
Garantiza las propiedades minimas para el cruce automatico Obsidian <-> KIT.

Hoy el alcance C persiste los IDs de entradas KIT detectados en notas Obsidian
como texto canonico en dos bases:
  - OBSIDIAN_DB.KIT IDs
  - NOTION_DB_INX.KIT IDs

Uso:
    python tools/ensure_kit_cross_fields.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import get_data_source_schema, update_database_properties


KIT_IDS_SCHEMA = {"KIT IDs": {"rich_text": {}}}


def _ensure_property(db_id: str, label: str) -> bool:
    schema = get_data_source_schema(db_id)
    if "KIT IDs" in schema.get("properties", []):
        print(f"[ok] {label}: 'KIT IDs' ya existe")
        return False
    update_database_properties(db_id, KIT_IDS_SCHEMA)
    print(f"[add] {label}: creada propiedad 'KIT IDs'")
    return True


def main() -> int:
    db_obsidian = os.getenv("OBSIDIAN_DB")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_obsidian or not db_inx:
        print("Faltan OBSIDIAN_DB o NOTION_DB_INX en .env")
        return 2

    changed = 0
    changed += int(_ensure_property(db_obsidian, "OBSIDIAN_DB"))
    changed += int(_ensure_property(db_inx, "NOTION_DB_INX"))
    print(f"\nPropiedades aseguradas. Cambios aplicados: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
