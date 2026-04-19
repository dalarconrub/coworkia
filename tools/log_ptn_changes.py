"""
Registra cambios en PTN (proyectos/tareas/notas) en la BD NOTION (B0A-INX).
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import query_data_source, create_page, extract_property_value


STATE_PATH = os.path.join("artifacts", "ptn_log_state.json")


def _load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def _to_dt(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _log_changes(ds_id: str, log_db: str, tipo: str, state: dict) -> int:
    last_ts = state.get(ds_id)
    last_dt = _to_dt(last_ts) if last_ts else datetime(1970, 1, 1, tzinfo=timezone.utc)

    rows = query_data_source(ds_id)
    created = 0
    max_dt = last_dt

    for r in rows:
        edited = _to_dt(r.get("last_edited_time", r.get("created_time")))
        if edited <= last_dt:
            continue
        if edited > max_dt:
            max_dt = edited

        props = r.get("properties", {})
        title = ""
        for p in props.values():
            if p.get("type") == "title":
                title = extract_property_value(p)
                break
        title = title or "(sin titulo)"

        log_props = {
            "Evento": {"title": [{"text": {"content": f"{tipo}: {title}"}}]},
            "Fecha": {"date": {"start": edited.date().isoformat()}},
            "Tipo": {"select": {"name": tipo}},
            "Fuente ID": {"rich_text": [{"text": {"content": r['id']}}]},
        }

        # Relaciones PTN
        if tipo == "Proyecto":
            log_props["PTN Proyecto"] = {"relation": [{"id": r["id"]}]}
        elif tipo == "Tarea":
            log_props["PTN Tarea"] = {"relation": [{"id": r["id"]}]}
        elif tipo == "Nota":
            log_props["PTN Nota"] = {"relation": [{"id": r["id"]}]}

        # Relaciones ABC (si existen en PTN)
        for name, target in [("Area Rel", "Area"), ("Bloque Rel", "Bloque"), ("Contexto Rel", "Contexto")]:
            rel = props.get(name, {}).get("relation", [])
            if rel:
                log_props[target] = {"relation": rel}

        create_page(parent_id=log_db, title="PTN LOG", properties=log_props, is_data_source=True)
        created += 1

    if max_dt > last_dt:
        state[ds_id] = max_dt.isoformat()
    return created


def main() -> int:
    log_db = os.getenv("NOTION_DB")
    if not log_db:
        print("Falta NOTION_DB en .env")
        return 2

    ds_proy = os.getenv("NOTION_DS_PROYECTOS")
    ds_tar = os.getenv("NOTION_DS_TAREAS")
    ds_not = os.getenv("NOTION_DS_NOTAS")
    if not all([ds_proy, ds_tar, ds_not]):
        print("Faltan IDs PTN en .env")
        return 2

    state = _load_state()
    total = 0
    total += _log_changes(ds_proy, log_db, "Proyecto", state)
    total += _log_changes(ds_tar, log_db, "Tarea", state)
    total += _log_changes(ds_not, log_db, "Nota", state)
    _save_state(state)

    print(f"Entradas de log creadas: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
