"""
Crea la base puente INX-ENLACES en B0A-INX.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import create_database


ABC_AREAS = "340622cf-315b-8116-a1bd-f21b04bc0ac1"
ABC_BLOQUES = "340622cf-315b-8191-bda1-dbc73e342720"
ABC_CONTEXTOS = "340622cf-315b-8175-b6b0-db2e1c794552"
PTN_PROY = "33f622cf-315b-816d-b95f-c5ce397d7397"
PTN_TAR = "33f622cf-315b-815a-95f3-d0d96c5b8dd8"
PTN_NOT = "33f622cf-315b-8173-8604-ee623959d4ce"


def _schema() -> dict:
    return {
        "Elemento": {"title": {}},
        "Clave": {"rich_text": {}},
        "Fuente": {"select": {"options": [
            {"name": "Todoist", "color": "red"},
            {"name": "Notion", "color": "blue"},
            {"name": "KIT", "color": "blue"},
            {"name": "Obsidian", "color": "green"},
            {"name": "GitHub", "color": "purple"},
            {"name": "Paperpile", "color": "orange"},
            {"name": "Manual", "color": "gray"},
        ]}},
        "Estado": {"select": {"options": [
            {"name": "Activo", "color": "yellow"},
            {"name": "Completada", "color": "pink"},
            {"name": "Verificado", "color": "green"},
            {"name": "Roto", "color": "red"},
            {"name": "Archivado", "color": "gray"},
        ]}},
        "Tipo MAR": {"select": {"options": [
            {"name": "idea", "color": "gray"},
            {"name": "logro", "color": "yellow"},
            {"name": "habito", "color": "green"},
            {"name": "tarea", "color": "blue"},
            {"name": "evento", "color": "red"},
        ]}},
        "Todoist ID": {"rich_text": {}},
        "PTN Proyecto": {"relation": {"database_id": PTN_PROY, "type": "single_property", "single_property": {}}},
        "PTN Tarea": {"relation": {"database_id": PTN_TAR, "type": "single_property", "single_property": {}}},
        "PTN Nota": {"relation": {"database_id": PTN_NOT, "type": "single_property", "single_property": {}}},
        "Obsidian Ruta": {"rich_text": {}},
        "KIT IDs": {"rich_text": {}},
        "KIT": {"relation": {"database_id": os.getenv("NOTION_DB_KIT", ""), "type": "single_property", "single_property": {}}},
        "Paperpile Citekey": {"rich_text": {}},
        "Area": {"relation": {"database_id": ABC_AREAS, "type": "single_property", "single_property": {}}},
        "Bloque": {"relation": {"database_id": ABC_BLOQUES, "type": "single_property", "single_property": {}}},
        "Contexto": {"relation": {"database_id": ABC_CONTEXTOS, "type": "single_property", "single_property": {}}},
        "URL": {"url": {}},
        "Detalle": {"rich_text": {}},
    }


def main() -> int:
    parent = os.getenv("NOTION_INX_PARENT", "117622cf-315b-80ee-bd25-e6c58cb4d4e6")
    db = create_database(parent, "INX-ENLACES", _schema())
    print(db["id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
