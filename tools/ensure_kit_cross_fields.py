"""
Garantiza las propiedades necesarias para el cruce automatico Obsidian <-> KIT.

Compatibilidad mantenida:
  - OBSIDIAN_DB.KIT IDs
  - NOTION_DB_INX.KIT IDs

Relaciones reales añadidas:
  - OBSIDIAN_DB.KIT            -> relation a KIT
  - NOTION_DB_INX.KIT          -> relation a KIT
  - KIT.Usada en notas         -> relation a OBSIDIAN_DB
  - INX-ENLACES.Fuente incluye -> KIT

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

from tools.notion_tools import get_data_source_schema, get_database_info, resolve_data_source_id, update_database_properties


KIT_IDS_SCHEMA = {"KIT IDs": {"rich_text": {}}}


def _relation_target_ids(database_or_data_source_id: str) -> tuple[str, str]:
    info = get_database_info(database_or_data_source_id, object_type="data_source")
    raw = info.get("raw") or {}
    try:
        data_source_id = resolve_data_source_id(database_or_data_source_id)
    except Exception:
        data_source_id = raw.get("id") or database_or_data_source_id
    parent = raw.get("parent") or {}
    if parent.get("type") == "database_id" and parent.get("database_id"):
        return parent["database_id"], data_source_id
    return data_source_id, data_source_id


def _relation_schema(database_or_data_source_id: str) -> dict:
    database_id, data_source_id = _relation_target_ids(database_or_data_source_id)
    return {
        "relation": {
            "database_id": database_id,
            "data_source_id": data_source_id,
            "type": "single_property",
            "single_property": {},
        }
    }


def _ensure_property(db_id: str, label: str, prop_name: str, prop_schema: dict) -> bool:
    schema = get_data_source_schema(db_id)
    if prop_name in schema.get("properties", []):
        print(f"[ok] {label}: '{prop_name}' ya existe")
        return False
    update_database_properties(db_id, {prop_name: prop_schema})
    print(f"[add] {label}: creada propiedad '{prop_name}'")
    return True


def _ensure_inx_fuente_option(db_inx: str) -> bool:
    info = get_database_info(db_inx, object_type="data_source")
    fuente = ((info.get("raw") or {}).get("properties") or {}).get("Fuente") or {}
    options = (((fuente.get("select") or {}).get("options")) or [])
    names = {opt.get("name", "") for opt in options}
    if "KIT" in names:
        print("[ok] NOTION_DB_INX: opcion Fuente=KIT ya existe")
        return False
    update_database_properties(
        db_inx,
        {"Fuente": {"select": {"options": [{"name": "KIT", "color": "blue"}]}}},
    )
    print("[add] NOTION_DB_INX: opcion Fuente=KIT creada")
    return True


def main() -> int:
    db_obsidian = os.getenv("OBSIDIAN_DB")
    db_inx = os.getenv("NOTION_DB_INX")
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_obsidian or not db_inx or not db_kit:
        print("Faltan OBSIDIAN_DB, NOTION_DB_INX o NOTION_DB_KIT en .env")
        return 2

    changed = 0
    changed += int(_ensure_property(db_obsidian, "OBSIDIAN_DB", "KIT IDs", {"rich_text": {}}))
    changed += int(_ensure_property(db_obsidian, "OBSIDIAN_DB", "KIT", _relation_schema(db_kit)))
    changed += int(_ensure_property(db_inx, "NOTION_DB_INX", "KIT IDs", {"rich_text": {}}))
    changed += int(_ensure_property(db_inx, "NOTION_DB_INX", "KIT", _relation_schema(db_kit)))
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Usada en notas", _relation_schema(db_obsidian)))
    changed += int(_ensure_inx_fuente_option(db_inx))
    print(f"\nPropiedades aseguradas. Cambios aplicados: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
