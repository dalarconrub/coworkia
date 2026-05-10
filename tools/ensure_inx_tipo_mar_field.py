"""
Garantiza la propiedad `Tipo MAR` en INX-ENLACES.

La propiedad permite que las filas `todoist:*` propagadas desde TODOIST-TAREAS
queden identificadas directamente como idea/logro/habito/tarea/evento.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import get_data_source_schema, update_database_properties


TIPO_MAR_SCHEMA = {
    "select": {
        "options": [
            {"name": "idea", "color": "gray"},
            {"name": "logro", "color": "yellow"},
            {"name": "habito", "color": "green"},
            {"name": "tarea", "color": "blue"},
            {"name": "evento", "color": "red"},
        ]
    }
}


def main() -> int:
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    schema = get_data_source_schema(db_inx)
    if "Tipo MAR" in schema.get("properties", []):
        print("[ok] INX-ENLACES: 'Tipo MAR' ya existe")
        return 0

    update_database_properties(db_inx, {"Tipo MAR": TIPO_MAR_SCHEMA})
    print("[add] INX-ENLACES: creada propiedad 'Tipo MAR'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
