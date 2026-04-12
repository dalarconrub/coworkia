"""
Registra cambios en notas Obsidian en la BD OBSIDIAN (B0A-INX).
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.obsidian_tools import get_todas_notas
from tools.notion_tools import create_page, query_data_source, extract_property_value


ABC_AREAS = "340622cf-315b-8116-a1bd-f21b04bc0ac1"
ABC_BLOQUES = "340622cf-315b-8191-bda1-dbc73e342720"
ABC_CONTEXTOS = "340622cf-315b-8175-b6b0-db2e1c794552"


STATE_PATH = os.path.join("artifacts", "obsidian_log_state.json")


def _load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def _file_mtime(path: str) -> float:
    return os.path.getmtime(path)


def main() -> int:
    db_id = os.getenv("OBSIDIAN_DB")
    if not db_id:
        print("Falta OBSIDIAN_DB en .env")
        return 2

    state = _load_state()
    last_ts = state.get("last_mtime", 0)
    notas = get_todas_notas()
    created = 0
    max_ts = last_ts

    # Mapas ABC por código
    area_map = {extract_property_value(r.get("properties", {}).get("Codigo", {})): r["id"]
                for r in query_data_source(ABC_AREAS)}
    bloque_map = {extract_property_value(r.get("properties", {}).get("Codigo", {})): r["id"]
                  for r in query_data_source(ABC_BLOQUES)}
    contexto_map = {extract_property_value(r.get("properties", {}).get("Codigo", {})): r["id"]
                    for r in query_data_source(ABC_CONTEXTOS)}

    for nota in notas:
        path = nota.get("path")
        if not path:
            continue
        mtime = _file_mtime(path)
        if mtime <= last_ts:
            continue
        max_ts = max(max_ts, mtime)
        rel = nota.get("relativo", "")
        parts = rel.split(os.sep)
        area = parts[0] if len(parts) > 0 else ""
        bloque = parts[1] if len(parts) > 1 else ""
        contexto = parts[2] if len(parts) > 2 else ""

        fecha = datetime.fromtimestamp(mtime).date().isoformat()
        props = {
            "Evento": {"title": [{"text": {"content": nota.get("nombre", "Nota")}}]},
            "Fecha": {"date": {"start": fecha}},
            "Archivo": {"rich_text": [{"text": {"content": nota.get("nombre", "")}}]},
            "Ruta": {"rich_text": [{"text": {"content": rel}}]},
            "Tipo": {"select": {"name": "Nota"}},
            "Detalle": {"rich_text": [{"text": {"content": path}}]},
        }

        # Relaciones ABC si existen
        if area in area_map:
            props["Area"] = {"relation": [{"id": area_map[area]}]}
        if bloque in bloque_map:
            props["Bloque"] = {"relation": [{"id": bloque_map[bloque]}]}
        if contexto in contexto_map:
            props["Contexto"] = {"relation": [{"id": contexto_map[contexto]}]}

        create_page(parent_id=db_id, title="OBSIDIAN", properties=props, is_data_source=True)
        created += 1

    state["last_mtime"] = max_ts
    _save_state(state)
    print(f"Entradas de log creadas: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
