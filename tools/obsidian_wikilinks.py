"""
Parser y utilidades para wikilinks cross-system en notas Obsidian.

Convencion: dentro del markdown del vault, una nota puede citar una entidad
de otro sistema con `[[<prefix>:<id>]]` donde prefix esta en el set:
  - ptn         (pagina Notion PTN: proyecto/tarea/nota)
  - kit         (entrada KIT)
  - paperpile   (paper BIB)
  - todoist     (tarea Todoist)
  - github      (repo REP)

Obsidian nativamente no resuelve estos wikilinks (apuntan fuera del vault).
Este modulo los detecta, lista y valida contra INX-ENLACES.

Subcomandos:
  audit              Escanea todo el vault, lista wikilinks y reporta rotos.
  find <prefix>:<id> Busca notas que mencionan un wikilink concreto.

Uso:
    python tools/obsidian_wikilinks.py audit
    python tools/obsidian_wikilinks.py find ptn:343622cf-315b-80d4-8b0f-e8a0c71808bd
    python tools/obsidian_wikilinks.py find kit:340622cf-315b-814b-bf50-e20378365646

Requisitos:
  - .env con NOTION_DB_INX, OBSIDIAN_ALPHA_PATH.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import ALPHA_PATH


PREFIXES = ("ptn", "kit", "paperpile", "todoist", "github")
WIKILINK_RE = re.compile(
    r"\[\[(" + "|".join(PREFIXES) + r"):([^\]\n]+?)\]\]"
)


def _dedupe_rows(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        pid = (r.get("id") or "").strip()
        if pid and pid in seen:
            continue
        if pid:
            seen.add(pid)
        out.append(r)
    return out


def _normalize(value: str) -> str:
    return value.replace("-", "").lower().strip()


def _load_inx_keys(db_inx: str) -> dict[str, set[str]]:
    keys: dict[str, set[str]] = {p: set() for p in PREFIXES}
    for r in _dedupe_rows(query_data_source(db_inx)):
        clave = (extract_property_value(r.get("properties", {}).get("Clave", {})) or "")
        for p in PREFIXES:
            prefix = f"{p}:"
            if clave.startswith(prefix):
                keys[p].add(clave[len(prefix) :])
                break
    return keys


def scan_vault() -> list[dict]:
    """Devuelve lista de dicts {ruta, line, prefix, id} por cada wikilink hallado."""
    hits: list[dict] = []
    for md in ALPHA_PATH.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(md.relative_to(ALPHA_PATH))
        for line_num, line in enumerate(content.splitlines(), 1):
            for m in WIKILINK_RE.finditer(line):
                hits.append({
                    "ruta": rel,
                    "line": line_num,
                    "prefix": m.group(1),
                    "id": m.group(2).strip(),
                })
    return hits


def _resolve(prefix: str, value: str, inx_keys: dict[str, set[str]]) -> bool:
    bag = inx_keys.get(prefix, set())
    if prefix in {"ptn", "kit"}:
        norm = _normalize(value)
        return any(_normalize(k) == norm for k in bag)
    return value in bag


def cmd_audit(args: argparse.Namespace) -> int:
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        print("Falta NOTION_DB_INX en .env")
        return 2

    hits = scan_vault()
    inx_keys = _load_inx_keys(db_inx)

    by_prefix: dict[str, list[dict]] = {p: [] for p in PREFIXES}
    broken: list[dict] = []
    for h in hits:
        by_prefix[h["prefix"]].append(h)
        if not _resolve(h["prefix"], h["id"], inx_keys):
            broken.append(h)

    print("=== Audit wikilinks cross-system en vault Obsidian ===\n")
    print(f"Wikilinks detectados: {len(hits)}")
    for p in PREFIXES:
        print(f"  - [[{p}:...]]: {len(by_prefix[p])}  (INX {p}:* = {len(inx_keys[p])})")

    if hits and by_prefix:
        print("\nEjemplos por prefijo (hasta 3 c/u):")
        for p in PREFIXES:
            if by_prefix[p]:
                print(f"  [{p}]")
                for h in by_prefix[p][:3]:
                    print(f"    - {h['ruta']} L{h['line']} -> {h['id'][:60]}")

    if broken:
        print(f"\n[!] Wikilinks rotos (el id no existe en INX, {len(broken)}):")
        for h in broken[:10]:
            print(f"  - [[{h['prefix']}:{h['id'][:40]}]] en {h['ruta']} L{h['line']}")
        if len(broken) > 10:
            print(f"  (+{len(broken) - 10} mas)")

    if len(hits) == 0:
        print("\n[info] No hay wikilinks cross-system en el vault todavia.")
        print("       Inserta p.ej. [[ptn:<uuid>]] o [[kit:<uuid>]] en tus notas para cruzarlas con INX.")
        return 0

    if broken:
        return 1

    print("\nOK: todos los wikilinks cross-system resuelven contra INX.")
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    query = args.query.strip()
    if ":" not in query:
        print("Formato: <prefix>:<id>  (ej. ptn:343622cf-...)", file=sys.stderr)
        return 2
    prefix, value = query.split(":", 1)
    if prefix not in PREFIXES:
        print(f"Prefix desconocido: '{prefix}'. Use uno de: {', '.join(PREFIXES)}", file=sys.stderr)
        return 2

    pattern = re.compile(r"\[\[" + re.escape(prefix) + r":" + re.escape(value) + r"\]\]")
    matches: list[tuple[str, int, str]] = []
    for md in ALPHA_PATH.rglob("*.md"):
        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(md.relative_to(ALPHA_PATH))
        for line_num, line in enumerate(content.splitlines(), 1):
            if pattern.search(line):
                matches.append((rel, line_num, line.strip()))

    if not matches:
        print(f"Sin resultados para [[{prefix}:{value}]]")
        return 1

    print(f"=== Notas que mencionan [[{prefix}:{value}]] ({len(matches)}) ===\n")
    for rel, line_num, line in matches:
        print(f"  {rel} L{line_num}")
        print(f"    {line[:140]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit", help="Audita todos los wikilinks cross-system contra INX")
    p_find = sub.add_parser("find", help="Busca notas que mencionan un wikilink concreto")
    p_find.add_argument("query", help="Prefix:id (ej. ptn:343622cf-315b-80d4-...)")

    args = parser.parse_args()
    if args.cmd == "audit":
        return cmd_audit(args)
    if args.cmd == "find":
        return cmd_find(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
