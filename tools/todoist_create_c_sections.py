"""
Crea secciones C* en proyectos B* de Todoist según docs/abc-taxonomy.md.
"""

import os
import re
import sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.todoist_tools import get_projects, _headers, BASE_URL


def _parse_taxonomy(path: str) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    current_block = None

    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("- `B") and line.endswith("`"):
                current_block = line.strip("- ").strip("`")
                mapping.setdefault(current_block, [])
            elif line.startswith("- `C") and current_block:
                ctx = line.strip("- ").strip("`")
                mapping[current_block].append(ctx)

    return mapping


def _get_sections(project_id: str) -> set[str]:
    resp = requests.get(f"{BASE_URL}/sections", headers=_headers(), params={"project_id": project_id})
    resp.raise_for_status()
    data = resp.json()
    items = data["results"] if isinstance(data, dict) and "results" in data else data
    return {s.get("name") for s in items if isinstance(s, dict) and s.get("name")}


def main() -> int:
    taxonomy_path = os.path.join("docs", "abc-taxonomy.md")
    mapping = _parse_taxonomy(taxonomy_path)
    projects = {p["name"]: p["id"] for p in get_projects()}

    created = 0
    for block, contexts in mapping.items():
        if not block.startswith("B"):
            continue
        if block not in projects:
            continue
        project_id = projects[block]
        existing = _get_sections(project_id)
        for ctx in contexts:
            if ctx in existing:
                continue
            resp = requests.post(
                f"{BASE_URL}/sections",
                headers=_headers(),
                json={"project_id": project_id, "name": ctx},
            )
            resp.raise_for_status()
            created += 1

    print(f"Secciones creadas: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
