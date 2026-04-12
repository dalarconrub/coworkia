"""
Define las opciones válidas de Bloque y Contexto en PTN-Proyectos
usando las bases ABC-Bloques y ABC-Contextos.
"""

import os
import sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import _headers, query_data_source, extract_property_value


ABC_BLOQUES = "340622cf-315b-8191-bda1-dbc73e342720"
ABC_CONTEXTOS = "340622cf-315b-8175-b6b0-db2e1c794552"


def _options_from_ds(ds_id: str) -> list[dict]:
    rows = query_data_source(ds_id)
    values = []
    for r in rows:
        props = r.get("properties", {})
        name = extract_property_value(props.get("Nombre", {}))
        if name:
            values.append(name)
    values = sorted(set(values))
    return [{"name": v, "color": "gray"} for v in values]


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

    bloque_options = _options_from_ds(ABC_BLOQUES)
    contexto_options = _options_from_ds(ABC_CONTEXTOS)

    properties = {
        "Bloque": {"select": {"options": bloque_options}},
        "Contexto": {"select": {"options": contexto_options}},
    }

    ok = _patch_database(db_id, properties)
    if not ok:
        print("No se pudo actualizar Bloque/Contexto.")
        return 1

    print(f"Bloque actualizado con {len(bloque_options)} opciones.")
    print(f"Contexto actualizado con {len(contexto_options)} opciones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
