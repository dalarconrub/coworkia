"""
Crea las bases ABC (Areas, Bloques, Contextos) bajo C0B1/C0B2/C0B3.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import create_database, get_page_content


def _schema_area() -> dict:
    return {
        "Nombre": {"title": {}},
        "Codigo": {"rich_text": {}},
        "Descripcion": {"rich_text": {}},
        "URL": {"url": {}},
    }


def _schema_bloque() -> dict:
    return {
        "Nombre": {"title": {}},
        "Codigo": {"rich_text": {}},
        "Area": {"rich_text": {}},
        "Descripcion": {"rich_text": {}},
        "URL": {"url": {}},
    }


def _schema_contexto() -> dict:
    return {
        "Nombre": {"title": {}},
        "Codigo": {"rich_text": {}},
        "Bloque": {"rich_text": {}},
        "Descripcion": {"rich_text": {}},
        "URL": {"url": {}},
    }


def _has_child_database(parent_id: str, title: str) -> bool:
    blocks = get_page_content(parent_id)
    for block in blocks:
        if block.get("type") == "child_database":
            if (block.get("child_database", {}) or {}).get("title") == title:
                return True
    return False


def _create_if_missing(parent_id: str, title: str, schema: dict) -> str:
    if _has_child_database(parent_id, title):
        return "(ya existe)"
    created = create_database(parent_id, title, schema)
    return created.get("id", "")


def main() -> int:
    if len(sys.argv) < 4:
        print("Uso: python tools/create_abc_taxonomy_dbs.py <C0B1_AREA_ID> <C0B2_BLOQUES_ID> <C0B3_CONTEXTOS_ID>")
        return 2

    c0b1, c0b2, c0b3 = sys.argv[1:4]

    area_id = _create_if_missing(c0b1, "ABC-Areas", _schema_area())
    bloque_id = _create_if_missing(c0b2, "ABC-Bloques", _schema_bloque())
    contexto_id = _create_if_missing(c0b3, "ABC-Contextos", _schema_contexto())

    print(f"ABC-Areas: {area_id}")
    print(f"ABC-Bloques: {bloque_id}")
    print(f"ABC-Contextos: {contexto_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
