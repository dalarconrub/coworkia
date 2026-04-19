"""
Garantiza que INX-ENLACES acepte el estado 'Completada'.

Necesario para reflejar round-trip de tareas Todoist cerradas desde Obsidian.

Uso:
    python tools/ensure_inx_completed_status.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import get_database_info, update_database_properties


def main() -> int:
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    info = get_database_info(db_inx, object_type="data_source")
    estado = ((info.get("raw") or {}).get("properties") or {}).get("Estado") or {}
    options = (((estado.get("select") or {}).get("options")) or [])
    names = {opt.get("name", "") for opt in options}
    if "Completada" in names:
        print("[ok] INX-ENLACES: Estado=Completada ya existe")
        return 0

    update_database_properties(
        db_inx,
        {"Estado": {"select": {"options": [{"name": "Completada", "color": "pink"}]}}},
    )
    print("[add] INX-ENLACES: opcion Estado=Completada creada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
