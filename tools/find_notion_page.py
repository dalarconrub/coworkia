"""
Encuentra páginas accesibles por substring en el título.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import search_all, _extract_title


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python tools/find_notion_page.py <SUBSTRING>")
        return 2

    needle = sys.argv[1].lower()
    results = search_all(sys.argv[1])
    matches = []
    for r in results:
        if r.get("object") != "page":
            continue
        title = _extract_title(r) or ""
        if needle in title.lower():
            matches.append({
                "title": title,
                "id": r.get("id"),
            })

    matches = sorted(matches, key=lambda x: x.get("title", ""))
    for p in matches:
        print(f"- {p.get('title', '(sin titulo)')} | {p.get('id')}")
    print(f"TOTAL: {len(matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
