"""
Asegura que la base `TODOIST-TAREAS` (C0A1-TODOIST) tenga propiedades para mapear
la mayor parte de campos de Todoist sin romper compatibilidad.

No elimina ni renombra propiedades existentes: solo añade las que faltan.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import get_database_info, update_database_properties


DESIRED_PROPS: dict[str, dict] = {
    # Descripción / texto
    "Descripcion": {"rich_text": {}},

    # IDs Todoist (texto por seguridad; algunas veces no caben en number)
    "Todoist Project ID": {"rich_text": {}},
    "Todoist Section ID": {"rich_text": {}},
    "Todoist Parent ID": {"rich_text": {}},
    "Todoist Creator ID": {"rich_text": {}},

    # Fechas auxiliares
    "Creada": {"date": {}},
    "Due": {"date": {}},
    "Deadline": {"date": {}},

    # Due extra
    "Timezone": {"rich_text": {}},
    "Due string": {"rich_text": {}},
    "Recurrencia": {"checkbox": {}},

    # Meta/orden
    "Comentarios": {"number": {}},
    "Orden": {"number": {}},
}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Asegurar schema de TODOIST-TAREAS para mapeo completo")
    parser.add_argument("--db", default=os.getenv("TODOIST_DB_TAREAS"), help="ID de la BD/data_source TODOIST-TAREAS")
    args = parser.parse_args()

    if not args.db:
        print("Falta TODOIST_DB_TAREAS en .env (o pasa --db <id>)")
        return 2

    info = get_database_info(args.db, object_type="data_source")
    existing = set((info.get("properties") or []))

    to_add: dict[str, dict] = {}
    for name, schema in DESIRED_PROPS.items():
        if name not in existing:
            to_add[name] = schema

    if not to_add:
        print("Schema OK: no hay propiedades nuevas que añadir.")
        return 0

    update_database_properties(args.db, to_add)
    print(f"Propiedades añadidas: {', '.join(sorted(to_add.keys()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

