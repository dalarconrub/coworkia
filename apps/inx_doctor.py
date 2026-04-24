"""
Doctor de calidad de INX-ENLACES.

Reporta:
- Conteo de filas por Fuente y Estado.
- Claves duplicadas.
- Filas con campos mínimos ausentes según la fuente.
- Filas sin relación PTN.
- Repos en GIT-Repositorios sin entrada INX.
- Papers en BIB-Bibliografía sin entrada INX.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source


def _get(props: dict, name: str) -> str:
    return extract_property_value(props.get(name, {})) if props else ""


def _has_relation(props: dict, name: str) -> bool:
    return bool(props.get(name, {}).get("relation"))


def _has_any_ptn(props: dict) -> bool:
    return any(_has_relation(props, key) for key in ("PTN Proyecto", "PTN Tarea", "PTN Nota"))


def _report_section(lines: list[str], title: str, max_lines: int) -> None:
    print(f"\n[{title}] {len(lines)}")
    for line in lines[:max_lines]:
        print(f"  {line}")
    if len(lines) > max_lines:
        print(f"  ... ({len(lines) - max_lines} más)")


def _required_field_issues(clave: str, elemento: str, fuente: str, props: dict) -> list[str]:
    prefix = f"[{fuente}] {clave or '(sin clave)'} - {elemento or '(sin elemento)'}"
    issues: list[str] = []

    if not clave:
        issues.append(f"{prefix} | falta Clave")
    if not elemento:
        issues.append(f"{prefix} | falta Elemento")
    if not _get(props, "Estado"):
        issues.append(f"{prefix} | falta Estado")

    if fuente == "Todoist" and not _get(props, "Todoist ID"):
        issues.append(f"{prefix} | falta Todoist ID")
    if fuente == "Obsidian" and not _get(props, "Obsidian Ruta"):
        issues.append(f"{prefix} | falta Obsidian Ruta")
    if fuente in {"GitHub", "Paperpile"} and not _get(props, "URL"):
        issues.append(f"{prefix} | falta URL")

    return issues


def _repo_orphans(db_repos: str | None, inx_keys: set[str]) -> list[str]:
    if not db_repos:
        return []
    repos = query_data_source(db_repos)
    return [
        _get(r["properties"], "Nombre")
        for r in repos
        if _get(r["properties"], "Nombre")
        and f"github:{_get(r['properties'], 'Nombre')}" not in inx_keys
    ]


def _paper_orphans(db_bib: str | None, inx_keys: set[str]) -> list[str]:
    if not db_bib:
        return []
    papers = query_data_source(db_bib)
    return [
        _get(r["properties"], "Citekey")
        for r in papers
        if _get(r["properties"], "Citekey")
        and f"paperpile:{_get(r['properties'], 'Citekey')}" not in inx_keys
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Doctor de coherencia para INX-ENLACES")
    parser.add_argument("--db", default=os.getenv("NOTION_DB_INX"), help="ID de INX-ENLACES")
    parser.add_argument("--max", type=int, default=15, help="Máximo de filas impresas por sección")
    parser.add_argument("--allow-missing-ptn", action="store_true", help="No fallar por filas sin relación PTN")
    args = parser.parse_args(argv)

    db_inx = args.db
    db_repos = os.getenv("NOTION_DB_GIT")
    db_bib = os.getenv("NOTION_DB_BIB")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    inx_rows = query_data_source(db_inx)
    print(f"=== INX-ENLACES: {len(inx_rows)} filas ===")

    by_source = Counter()
    by_state = Counter()
    duplicates = defaultdict(list)
    inx_keys: set[str] = set()
    missing_ptn: list[str] = []
    missing_required: list[str] = []

    for row in inx_rows:
        props = row.get("properties", {})
        clave = _get(props, "Clave").strip()
        elemento = _get(props, "Elemento").strip()
        fuente = (_get(props, "Fuente") or "(sin fuente)").strip()
        estado = (_get(props, "Estado") or "(sin estado)").strip()

        by_source[fuente] += 1
        by_state[estado] += 1

        if clave:
            duplicates[clave].append(elemento or row["id"])
            inx_keys.add(clave)

        missing_required.extend(_required_field_issues(clave, elemento, fuente, props))

        if not _has_any_ptn(props):
            missing_ptn.append(f"[{fuente}] {clave or '(sin clave)'} - {elemento or '(sin elemento)'}")

    print("\nPor Fuente:")
    for key, value in sorted(by_source.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {key:12s} {value}")

    print("\nPor Estado:")
    for key, value in sorted(by_state.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {key:12s} {value}")

    duplicate_lines = [f"{key}: {values}" for key, values in duplicates.items() if len(values) > 1]
    if duplicate_lines:
        _report_section(duplicate_lines, "Claves duplicadas", args.max)
    else:
        print("\n[Claves duplicadas] 0")
        print("  OK")

    if missing_required:
        _report_section(missing_required, "Campos mínimos ausentes", args.max)
    else:
        print("\n[Campos mínimos ausentes] 0")
        print("  OK")

    _report_section(missing_ptn, "Filas sin relación PTN", args.max)

    repo_orphans = _repo_orphans(db_repos, inx_keys)
    if repo_orphans:
        _report_section(repo_orphans, "GIT huérfanos (sin INX)", args.max)
        print("  Sugerencia: python tools/sync_inx_links.py --source github")
    elif db_repos:
        print("\n[GIT huérfanos (sin INX)] 0")
        print("  OK")

    paper_orphans = _paper_orphans(db_bib, inx_keys)
    if paper_orphans:
        _report_section(paper_orphans, "BIB huérfanos (sin INX)", args.max)
        print("  Sugerencia: python tools/sync_inx_links.py --source paperpile")
    elif db_bib:
        print("\n[BIB huérfanos (sin INX)] 0")
        print("  OK")

    has_failures = bool(duplicate_lines or missing_required or repo_orphans or paper_orphans)
    if missing_ptn and not args.allow_missing_ptn:
        has_failures = True

    return 1 if has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
