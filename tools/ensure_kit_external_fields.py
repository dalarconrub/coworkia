"""
Garantiza las propiedades de KIT necesarias para integrar fuentes externas
(Inoreader, Raindrop.io, Google Keep y futuras).

Anade en NOTION_DB_KIT (sin destruir lo existente):
  - Google Keep ID     (rich_text)  unique key de notas Google Keep
                                    SIN ESTA, import_keep_remaining duplica
                                    notas en cada run (incidente 2026-04-21)
  - Inoreader ID       (rich_text)  unique key del articulo en Inoreader
  - Inoreader Tags     (multi_select: 'starred', 'kit-import')
  - Raindrop ID        (rich_text)  unique key del bookmark en Raindrop.io
  - Raindrop Tags      (multi_select: 'kit-import')
  - Raindrop Collection / Type (rich_text)
  - Subtipo            (select)     anade Articulo / Newsletter / Blog / Vídeo / Podcast
                                    si faltan (preserva opciones existentes)
  - Fuente / Autor     (rich_text)  ya creado por el flujo Google Keep, idempotente

Anade en NOTION_DB_INX:
  - opciones 'Inoreader' y 'Raindrop' al select 'Fuente' (preserva opciones existentes)

Uso:
    python tools/ensure_kit_external_fields.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import (
    get_data_source_schema,
    get_database_info,
    update_database_properties,
)


NEW_SUBTIPO_OPTIONS = [
    {"name": "Artículo", "color": "blue"},
    {"name": "Newsletter", "color": "yellow"},
    {"name": "Blog", "color": "green"},
    {"name": "Vídeo", "color": "red"},
    {"name": "Podcast", "color": "purple"},
    {"name": "Paper", "color": "gray"},
]

INOREADER_TAG_OPTIONS = [
    {"name": "starred", "color": "yellow"},
    {"name": "kit-import", "color": "blue"},
]

RAINDROP_TAG_OPTIONS = [
    {"name": "kit-import", "color": "blue"},
]


def _ensure_property(db_id: str, label: str, prop_name: str, prop_schema: dict) -> bool:
    schema = get_data_source_schema(db_id)
    if prop_name in schema.get("properties", []):
        print(f"[ok] {label}: '{prop_name}' ya existe")
        return False
    update_database_properties(db_id, {prop_name: prop_schema})
    print(f"[add] {label}: creada propiedad '{prop_name}'")
    return True


def _ensure_select_options(db_id: str, label: str, prop_name: str,
                           desired: list[dict]) -> bool:
    """Fusiona nuevas opciones en un select, preservando las existentes."""
    info = get_database_info(db_id, object_type="data_source")
    raw_props = ((info.get("raw") or {}).get("properties") or {})
    if prop_name not in raw_props:
        print(f"[skip] {label}: '{prop_name}' no existe (no se crea aqui)")
        return False

    prop = raw_props[prop_name]
    select_or_multi = prop.get("select") or prop.get("multi_select") or {}
    existing = select_or_multi.get("options") or []
    existing_names = {opt.get("name", "") for opt in existing}

    to_add = [opt for opt in desired if opt["name"] not in existing_names]
    if not to_add:
        print(f"[ok] {label}: '{prop_name}' ya tiene todas las opciones requeridas")
        return False

    merged = list(existing) + to_add
    if "select" in prop:
        update_database_properties(db_id, {prop_name: {"select": {"options": merged}}})
    else:
        update_database_properties(db_id, {prop_name: {"multi_select": {"options": merged}}})

    added_names = ", ".join(opt["name"] for opt in to_add)
    print(f"[add] {label}: opciones '{prop_name}' anadidas -> {added_names}")
    return True


def main() -> int:
    db_kit = os.getenv("NOTION_DB_KIT")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_kit or not db_inx:
        print("Faltan NOTION_DB_KIT o NOTION_DB_INX en .env")
        return 2

    changed = 0

    # KIT: identificadores y tags por fuente externa
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Google Keep ID", {"rich_text": {}}))
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Inoreader ID", {"rich_text": {}}))
    changed += int(_ensure_property(
        db_kit, "NOTION_DB_KIT", "Inoreader Tags",
        {"multi_select": {"options": INOREADER_TAG_OPTIONS}},
    ))
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Raindrop ID", {"rich_text": {}}))
    changed += int(_ensure_property(
        db_kit, "NOTION_DB_KIT", "Raindrop Tags",
        {"multi_select": {"options": RAINDROP_TAG_OPTIONS}},
    ))
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Raindrop Collection", {"rich_text": {}}))
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Raindrop Type", {"rich_text": {}}))
    changed += int(_ensure_property(db_kit, "NOTION_DB_KIT", "Fuente / Autor", {"rich_text": {}}))

    # KIT: opciones nuevas en Subtipo (si la propiedad existe)
    changed += int(_ensure_select_options(db_kit, "NOTION_DB_KIT", "Subtipo", NEW_SUBTIPO_OPTIONS))

    # INX: nuevas opciones de fuentes externas
    changed += int(_ensure_select_options(
        db_inx, "NOTION_DB_INX", "Fuente",
        [
            {"name": "Inoreader", "color": "orange"},
            {"name": "Raindrop", "color": "blue"},
        ],
    ))

    print(f"\nPropiedades aseguradas. Cambios aplicados: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
