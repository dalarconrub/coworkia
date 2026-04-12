"""
Clona una base de datos de Notion a una nueva base bajo una página destino.
"""

import os
import sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import _headers, get_database_info, query_database, create_database, create_page


SKIP_TYPES = {"formula", "rollup", "created_time", "last_edited_time", "created_by", "last_edited_by"}
ALLOWED_TYPES = {
    "title", "rich_text", "select", "multi_select", "date", "number",
    "url", "checkbox", "relation", "people", "files", "email", "phone_number"
}


def _clean_schema(schema: dict) -> dict:
    cleaned = {}
    for name, prop in schema.items():
        ptype = prop.get("type")
        if ptype in SKIP_TYPES:
            continue
        # Keep schema as-is for create_database (strip id)
        prop_copy = dict(prop)
        prop_copy.pop("id", None)
        cleaned[name] = {ptype: prop_copy.get(ptype, {})}
    return cleaned


def _value_from_prop(prop: dict) -> dict | None:
    ptype = prop.get("type")
    if ptype in SKIP_TYPES or ptype not in ALLOWED_TYPES:
        return None
    value = prop.get(ptype)
    if value is None:
        return None
    return {ptype: value}


def clone_database(src_db: str, dst_parent: str, dst_title: str) -> str:
    info = get_database_info(src_db, object_type="database")
    schema = info.get("raw", {}).get("properties", {})
    cleaned_schema = _clean_schema(schema)

    created = create_database(dst_parent, dst_title, cleaned_schema)
    return created["id"]


def migrate_rows(src_db: str, dst_db: str) -> int:
    rows = query_database(src_db)
    count = 0
    for row in rows:
        props = {}
        for name, prop in row.get("properties", {}).items():
            val = _value_from_prop(prop)
            if val is not None:
                props[name] = val
        try:
            create_page(parent_id=dst_db, title="MIGRACION", properties=props, is_database=True)
            count += 1
        except requests.HTTPError as exc:
            # Retry with only title
            title_props = {}
            for name, prop in row.get("properties", {}).items():
                if prop.get("type") == "title":
                    title_props[name] = {"title": prop.get("title", [])}
                    break
            if title_props:
                create_page(parent_id=dst_db, title="MIGRACION", properties=title_props, is_database=True)
                count += 1
            else:
                raise exc
    return count


def main() -> int:
    if len(sys.argv) < 4:
        print("Uso: python tools/migrate_database.py <SRC_DB_ID> <DEST_PARENT_PAGE_ID> <DEST_TITLE>")
        return 2

    src_db = sys.argv[1]
    dst_parent = sys.argv[2]
    dst_title = sys.argv[3]

    new_db = clone_database(src_db, dst_parent, dst_title)
    migrated = migrate_rows(src_db, new_db)
    print(f"Nueva DB: {new_db} | Filas migradas: {migrated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
