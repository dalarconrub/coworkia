"""
Garantiza la propiedad `Paperpile Citekey` en INX-ENLACES.

Uso:
    python tools/ensure_inx_paperpile_citekey_field.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import get_data_source_schema, update_database_properties


def main() -> int:
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    schema = get_data_source_schema(db_inx)
    if "Paperpile Citekey" in schema.get("properties", []):
        print("[ok] INX-ENLACES: 'Paperpile Citekey' ya existe")
        return 0

    update_database_properties(db_inx, {"Paperpile Citekey": {"rich_text": {}}})
    print("[add] INX-ENLACES: creada propiedad 'Paperpile Citekey'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
