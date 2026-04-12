"""
Define las opciones válidas del campo Área en PTN-Proyectos.
"""

import os
import sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import _headers


def _patch_database(db_id: str, properties: dict) -> bool:
    for endpoint in (f"https://api.notion.com/v1/databases/{db_id}",
                     f"https://api.notion.com/v1/data_sources/{db_id}"):
        resp = requests.patch(endpoint, headers=_headers(), json={"properties": properties})
        if resp.status_code in (200, 202):
            return True
    return False


def main() -> int:
    db_id = os.getenv("NOTION_DS_PROYECTOS")
    if not db_id:
        print("Falta NOTION_DS_PROYECTOS en .env")
        return 2

    area_options = [
        {"name": "A1-INV", "color": "blue"},
        {"name": "A2-UNI", "color": "green"},
        {"name": "A3-VIT", "color": "yellow"},
        {"name": "A4-ARX", "color": "gray"},
    ]

    properties = {
        "Área": {
            "select": {
                "options": area_options
            }
        }
    }

    ok = _patch_database(db_id, properties)
    if not ok:
        print("No se pudo actualizar el schema de Área.")
        return 1

    print("Área actualizado con opciones A1-INV, A2-UNI, A3-VIT, A4-ARX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
