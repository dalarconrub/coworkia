"""
Diagnostico y descubrimiento de recursos Notion para Coworkia.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.notion_tools import get_data_sources, get_databases, get_pages


ENV_PATH = ROOT / ".env"


def load_local_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_PATH)
        return
    except Exception:
        pass

    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def token_status() -> tuple[bool, str]:
    token = os.getenv("NOTION_TOKEN", "").strip()
    if not token:
        return False, "falta NOTION_TOKEN en .env"
    if len(token) < 20:
        return False, "NOTION_TOKEN parece demasiado corto"
    return True, "NOTION_TOKEN presente"


def short_id(value: str) -> str:
    return value.replace("-", "")


def find_candidates(resources: list[dict], query_terms: list[str]) -> list[dict]:
    out = []
    for item in resources:
        title = (item.get("title") or "").lower()
        if all(term.lower() in title for term in query_terms):
            out.append(item)
    return out


def print_resource_block(title: str, resources: list[dict], limit: int = 20) -> None:
    print(f"=== {title} ({len(resources)}) ===")
    for item in resources[:limit]:
        rid = item.get("id", "")
        rtitle = item.get("title", "(sin titulo)")
        robj = item.get("object", "")
        print(f"- {rtitle}")
        print(f"  id: {rid}")
        print(f"  id_sin_guiones: {short_id(rid)}")
        if robj:
            print(f"  tipo: {robj}")
    if len(resources) > limit:
        print(f"... {len(resources) - limit} mas")
    print()


def print_env_suggestions(data_sources: list[dict], databases: list[dict]) -> None:
    combined = data_sources + databases
    rep_candidates = find_candidates(combined, ["rep"])
    bib_candidates = find_candidates(combined, ["bib"])

    print("=== SUGERENCIAS PARA .env ===")
    if rep_candidates:
        print("NOTION_DB_REPOS candidatos:")
        for item in rep_candidates[:5]:
            print(f"- {item.get('title', '(sin titulo)')} -> {item['id']}")
    else:
        print("NOTION_DB_REPOS: sin candidato automatico por titulo")

    if bib_candidates:
        print("NOTION_DB_BIB candidatos:")
        for item in bib_candidates[:5]:
            print(f"- {item.get('title', '(sin titulo)')} -> {item['id']}")
    else:
        print("NOTION_DB_BIB: sin candidato automatico por titulo")
    print()


def main() -> int:
    load_local_env()

    ok, detail = token_status()
    print("=== COWORKIA NOTION DOCTOR ===\n")
    print(f"Repo : {ROOT}")
    print(f".env : {'encontrado' if ENV_PATH.exists() else 'no encontrado'}")
    print(f"Token: {detail}\n")

    if not ok:
        print("Pon el token en .env antes de ejecutar este doctor.")
        print("Linea esperada:")
        print("NOTION_TOKEN=tu_token_de_integracion")
        return 1

    try:
        data_sources = get_data_sources()
        databases = get_databases()
        pages = get_pages()
    except Exception as exc:
        print(f"Error al consultar Notion: {exc}")
        print("Revisa que el token sea valido y que la integracion tenga acceso compartido.")
        return 2

    print_resource_block("DATA SOURCES ACCESIBLES", data_sources)
    print_resource_block("DATABASES O DATA SOURCES", databases)
    print_resource_block("PAGINAS ACCESIBLES", pages)
    print_env_suggestions(data_sources, databases)

    print("Variables que suelen quedar pendientes:")
    print("- NOTION_DB_REPOS")
    print("- NOTION_DB_BIB")
    print("- NOTION_REPOS_PARENT_PAGE")
    print("- NOTION_BIB_PARENT_PAGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
