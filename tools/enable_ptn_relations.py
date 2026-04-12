"""
Convierte la coherencia Área/Bloque/Contexto en relaciones usando las BD ABC.
"""

import os
import re
import sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    _headers,
    query_data_source,
    extract_property_value,
    update_page_properties,
)


ABC_AREAS = "340622cf-315b-8116-a1bd-f21b04bc0ac1"
ABC_BLOQUES = "340622cf-315b-8191-bda1-dbc73e342720"
ABC_CONTEXTOS = "340622cf-315b-8175-b6b0-db2e1c794552"


def _patch_database(db_id: str, properties: dict) -> bool:
    resp = requests.patch(
        f"https://api.notion.com/v1/databases/{db_id}",
        headers=_headers(),
        json={"properties": properties},
    )
    return resp.status_code in (200, 202)


def _map_by_code(ds_id: str) -> dict[str, str]:
    rows = query_data_source(ds_id)
    mapping = {}
    for r in rows:
        code = extract_property_value(r.get("properties", {}).get("Codigo", {}))
        if code:
            mapping[code] = r["id"]
    return mapping


def _normalize_area(value: str) -> str:
    m = re.match(r"^(A[0-4])", value or "")
    return m.group(1) if m else ""


def _normalize_block(value: str) -> str:
    m = re.match(r"^(B[0-9][0-9A-Z])", value or "")
    return m.group(1) if m else ""


def _normalize_context(value: str) -> str:
    m = re.match(r"^(C[0-9][0-9A-Za-z]{2})", value or "")
    return m.group(1) if m else ""


def main() -> int:
    ptn = os.getenv("NOTION_DS_PROYECTOS")
    if not ptn:
        print("Falta NOTION_DS_PROYECTOS")
        return 2

    # 1) Añadir relaciones en ABC-Bloques y ABC-Contextos
    _patch_database(ABC_BLOQUES, {
        "Area Rel": {
            "relation": {
                "database_id": ABC_AREAS,
                "type": "single_property",
                "single_property": {},
            }
        },
    })
    _patch_database(ABC_CONTEXTOS, {
        "Bloque Rel": {
            "relation": {
                "database_id": ABC_BLOQUES,
                "type": "single_property",
                "single_property": {},
            }
        },
    })

    # 2) Rellenar relaciones ABC (bloque->area, contexto->bloque)
    area_map = _map_by_code(ABC_AREAS)
    bloque_map = _map_by_code(ABC_BLOQUES)

    for r in query_data_source(ABC_BLOQUES):
        props = r.get("properties", {})
        area_code = _normalize_area(extract_property_value(props.get("Area", {})))
        if area_code and area_code in area_map:
            update_page_properties(r["id"], {"Area Rel": {"relation": [{"id": area_map[area_code]}]}})

    for r in query_data_source(ABC_CONTEXTOS):
        props = r.get("properties", {})
        bloque_code = _normalize_block(extract_property_value(props.get("Bloque", {})))
        if bloque_code and bloque_code in bloque_map:
            update_page_properties(r["id"], {"Bloque Rel": {"relation": [{"id": bloque_map[bloque_code]}]}})

    # 3) Añadir relaciones en PTN-Proyectos
    _patch_database(ptn, {
        "Area Rel": {
            "relation": {
                "database_id": ABC_AREAS,
                "type": "single_property",
                "single_property": {},
            }
        },
        "Bloque Rel": {
            "relation": {
                "database_id": ABC_BLOQUES,
                "type": "single_property",
                "single_property": {},
            }
        },
        "Contexto Rel": {
            "relation": {
                "database_id": ABC_CONTEXTOS,
                "type": "single_property",
                "single_property": {},
            }
        },
        "Area (via Bloque)": {
            "rollup": {
                "relation_property_name": "Bloque Rel",
                "rollup_property_name": "Area Rel",
                "function": "show_original"
            }
        },
        "Bloque (via Contexto)": {
            "rollup": {
                "relation_property_name": "Contexto Rel",
                "rollup_property_name": "Bloque Rel",
                "function": "show_original"
            }
        }
    })

    # 4) Migrar selects actuales a relaciones
    area_map = _map_by_code(ABC_AREAS)
    bloque_map = _map_by_code(ABC_BLOQUES)
    contexto_map = _map_by_code(ABC_CONTEXTOS)

    for r in query_data_source(ptn):
        props = r.get("properties", {})
        updates = {}

        area_val = extract_property_value(props.get("Área", {}))
        block_val = extract_property_value(props.get("Bloque", {}))
        ctx_val = extract_property_value(props.get("Contexto", {}))

        area_code = _normalize_area(area_val)
        block_code = _normalize_block(block_val)
        ctx_code = _normalize_context(ctx_val)

        if area_code in area_map:
            updates["Area Rel"] = {"relation": [{"id": area_map[area_code]}]}
        if block_code in bloque_map:
            updates["Bloque Rel"] = {"relation": [{"id": bloque_map[block_code]}]}
        if ctx_code in contexto_map:
            updates["Contexto Rel"] = {"relation": [{"id": contexto_map[ctx_code]}]}

        if updates:
            update_page_properties(r["id"], updates)

    print("Relaciones y rollups configurados en ABC y PTN-Proyectos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
