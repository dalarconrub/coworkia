"""
Archiva entradas con Codigo fuera del patrón esperado.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import query_data_source, extract_property_value, archive_page


PATTERNS = {
    "area": re.compile(r"^A[0-4]$"),
    "bloque": re.compile(r"^B[0-9][0-9A-Z]$"),
    "contexto": re.compile(r"^C[0-9][0-9A-Za-z]{2}$"),
}


def prune(data_source_id: str, kind: str) -> int:
    pattern = PATTERNS[kind]
    rows = query_data_source(data_source_id)
    archived = 0
    for r in rows:
        props = r.get("properties", {})
        code = extract_property_value(props.get("Codigo", {})) if props else ""
        if code and not pattern.match(code):
            archive_page(r["id"])
            archived += 1
    return archived


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: python tools/prune_abc_taxonomy.py <kind: area|bloque|contexto> <DS_ID> [<DS_ID> ...]")
        return 2

    kind = sys.argv[1].lower()
    if kind not in PATTERNS:
        print("kind inválido. Usa: area | bloque | contexto")
        return 2

    total = 0
    for ds_id in sys.argv[2:]:
        archived = prune(ds_id, kind)
        print(f"{ds_id}: archivados {archived}")
        total += archived
    print(f"Total archivados: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
