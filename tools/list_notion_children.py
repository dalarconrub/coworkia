"""
Lista paginas hijas directas de una pagina padre en Notion.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import get_page_content


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python tools/list_notion_children.py <PARENT_PAGE_ID>")
        return 2

    parent_id = sys.argv[1]
    blocks = get_page_content(parent_id)
    children = []
    for block in blocks:
        btype = block.get("type")
        if btype == "child_page":
            children.append({
                "title": block.get("child_page", {}).get("title", "(sin titulo)"),
                "id": block.get("id"),
                "type": "page",
            })
        elif btype == "child_database":
            children.append({
                "title": block.get("child_database", {}).get("title", "(sin titulo)"),
                "id": block.get("id"),
                "type": "database",
            })

    children = sorted(children, key=lambda x: (x.get("type", ""), x.get("title", "")))
    for c in children:
        print(f"- {c['title']} | {c['id']} | {c['type']}")
    print(f"TOTAL: {len(children)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
