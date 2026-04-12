"""
Elimina duplicados por Codigo en una base ABC, conservando el más reciente.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import query_data_source, extract_property_value, archive_page


def _parse_time(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def dedupe(data_source_id: str) -> int:
    rows = query_data_source(data_source_id)
    by_code: dict[str, list[dict]] = {}
    for r in rows:
        props = r.get("properties", {})
        code = ""
        if "Codigo" in props:
            code = extract_property_value(props["Codigo"])
        if not code:
            continue
        by_code.setdefault(code, []).append(r)

    archived = 0
    for code, items in by_code.items():
        if len(items) <= 1:
            continue
        items_sorted = sorted(items, key=lambda r: _parse_time(r.get("created_time", "")), reverse=True)
        for dup in items_sorted[1:]:
            archive_page(dup["id"])
            archived += 1
    return archived


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python tools/dedupe_abc_taxonomy.py <DS_ID> [<DS_ID> ...]")
        return 2

    total = 0
    for ds_id in sys.argv[1:]:
        archived = dedupe(ds_id)
        print(f"{ds_id}: archivados {archived}")
        total += archived
    print(f"Total archivados: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
