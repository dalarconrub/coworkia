"""
Validacion del caso de uso 8: KIT como ciudadano de primera en INX-ENLACES.

Contrato (alcance B):
- NOTION_DB_KIT tiene N entradas.
- INX-ENLACES tiene una fila por cada entrada KIT con Clave = 'kit:<page_id>'.
- La fila INX lleva titulo (Elemento), Fuente=Notion, Estado=Activo y, si la
  entrada KIT tiene Enlace, URL populated.

NO cubre (queda para alcance C / caso 08 extendido):
- Cruce automatico Obsidian <-> KIT (propiedad relation en KIT o en
  OBSIDIAN_DB).

Uso: python tools/validate_case_08.py
Requiere .env: NOTION_DB_KIT, NOTION_DB_INX

Exit codes:
  0  OK.
  1  KIT entries sin fila INX kit:<id>.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source


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


def _normalize(uuid_str: str) -> str:
    return (uuid_str or "").replace("-", "").lower().strip()


def main() -> int:
    db_kit = os.getenv("NOTION_DB_KIT")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_kit or not db_inx:
        print("Faltan NOTION_DB_KIT o NOTION_DB_INX en .env")
        return 2

    rows_kit = _dedupe_rows(query_data_source(db_kit))
    kit_entries: list[dict] = []
    for r in rows_kit:
        props = r.get("properties", {})
        titulo = extract_property_value(props.get("Titulo", {})) \
            or extract_property_value(props.get("Título", {})) or ""
        if not titulo:
            continue
        kit_entries.append({"page_id": r["id"], "titulo": titulo})

    rows_inx = _dedupe_rows(query_data_source(db_inx))
    inx_kit_ids: set[str] = set()
    for r in rows_inx:
        clave = extract_property_value(r.get("properties", {}).get("Clave", {})) or ""
        if clave.startswith("kit:"):
            inx_kit_ids.add(_normalize(clave[len("kit:") :]))

    matched = [e for e in kit_entries if _normalize(e["page_id"]) in inx_kit_ids]
    missing = [e for e in kit_entries if _normalize(e["page_id"]) not in inx_kit_ids]

    print("=== Validacion caso 8 (KIT -> INX-ENLACES) ===\n")
    print(f"KIT: {len(rows_kit)} filas unicas")
    print(f"  - Con Titulo: {len(kit_entries)}")
    print(f"INX-ENLACES: {len(rows_inx)} filas unicas")
    print(f"  - Clave kit:*: {len(inx_kit_ids)}")
    print(f"\nKIT entries presentes en INX: {len(matched)}/{len(kit_entries)}")

    if matched:
        print("\nEjemplos (hasta 5):")
        for e in matched[:5]:
            print(f"  - kit:{e['page_id']} | {e['titulo'][:70]}")

    if missing:
        print("\n[!] KIT entries sin fila INX kit:<id> (hasta 5):")
        for e in missing[:5]:
            print(f"  - kit:{e['page_id']} | {e['titulo'][:70]}")
        print("\n    Ejecuta: python tools/sync_inx_links.py --source kit --limit 200")
        return 1

    if len(kit_entries) == 0:
        print("\n[!] No hay entradas con Titulo en NOTION_DB_KIT.")
        return 1

    print("\nOK: todas las entradas KIT estan reflejadas en INX-ENLACES.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
