"""
Validacion del caso de uso 8: KIT como ciudadano de primera en INX-ENLACES.

Contrato base (alcance B):
- NOTION_DB_KIT tiene N entradas.
- INX-ENLACES tiene una fila por cada entrada KIT con Clave = 'kit:<page_id>'.
- La fila INX lleva titulo (Elemento), Fuente=Notion, Estado=Activo y, si la
  entrada KIT tiene Enlace, URL populated.

Chequeo adicional opcional (alcance C):
- Si OBSIDIAN_DB / INX-ENLACES ya tienen propiedad 'KIT IDs', verifica que
  las filas de origen Obsidian que referencian [[kit:<id>]] preservan ese
  dato al sincronizar a INX.

Uso:
  python tools/validate_case_08.py
  python tools/validate_case_08.py --scope c
Requiere .env: NOTION_DB_KIT, NOTION_DB_INX

Exit codes:
  0  OK.
  1  KIT entries sin fila INX kit:<id>.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, get_data_source_schema, query_data_source, normalize_notion_id


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


def _relation_ids(props: dict, name: str) -> list[str]:
    return sorted(
        _normalize(rel.get("id", ""))
        for rel in props.get(name, {}).get("relation", [])
        if rel.get("id")
    )


def _scope_c(db_kit: str, db_obsidian: str, db_inx: str) -> int:
    kit_schema = get_data_source_schema(db_kit)
    obs_schema = get_data_source_schema(db_obsidian)
    inx_schema = get_data_source_schema(db_inx)
    if "KIT IDs" not in obs_schema.get("properties", []) or "KIT IDs" not in inx_schema.get("properties", []):
        print("\n[scope-c] Propiedad 'KIT IDs' ausente en OBSIDIAN_DB o INX-ENLACES.")
        print("          Ejecuta: python tools/ensure_kit_cross_fields.py")
        return 1

    obs_has_rel = "KIT" in obs_schema.get("properties", [])
    inx_has_rel = "KIT" in inx_schema.get("properties", [])
    kit_has_backref = "Usada en notas" in kit_schema.get("properties", [])

    kit_rows = _dedupe_rows(query_data_source(db_kit))
    obsidian_rows = _dedupe_rows(query_data_source(db_obsidian))
    inx_rows = _dedupe_rows(query_data_source(db_inx))
    inx_by_path: dict[str, tuple[str, list[str]]] = {}
    for row in inx_rows:
        props = row.get("properties", {})
        path = extract_property_value(props.get("Obsidian Ruta", {})) or ""
        if not path:
            continue
        inx_by_path[path] = (
            extract_property_value(props.get("KIT IDs", {})) or "",
            _relation_ids(props, "KIT"),
        )

    kit_backrefs: dict[str, list[str]] = {}
    if kit_has_backref:
        for row in kit_rows:
            kit_backrefs[_normalize(row["id"])] = _relation_ids(row.get("properties", {}), "Usada en notas")

    scoped = []
    mismatched_text = []
    mismatched_rel = []
    missing_backrefs = []
    for row in obsidian_rows:
        props = row.get("properties", {})
        path = extract_property_value(props.get("Ruta", {})) or ""
        kit_ids = extract_property_value(props.get("KIT IDs", {})) or ""
        if not path or not kit_ids:
            continue
        scoped.append(path)
        inx_text, inx_rel_ids = inx_by_path.get(path, ("", []))
        if inx_text != kit_ids:
            mismatched_text.append((path, kit_ids, inx_text))

        expected_rel_ids = _relation_ids(props, "KIT")
        if not expected_rel_ids:
            expected_rel_ids = sorted(_normalize(normalize_notion_id(kit_id.strip())) for kit_id in kit_ids.split(",") if kit_id.strip())
        if obs_has_rel and inx_has_rel and inx_rel_ids != expected_rel_ids:
            mismatched_rel.append((path, expected_rel_ids, inx_rel_ids))

        if kit_has_backref:
            for kid in expected_rel_ids:
                if row["id"] not in kit_backrefs.get(kid, []):
                    missing_backrefs.append((path, kid, row["id"]))

    print("\n=== Validacion alcance C (Obsidian -> KIT relation/IDs -> INX -> KIT) ===\n")
    print(f"Filas OBSIDIAN_DB con KIT IDs: {len(scoped)}")
    print(f"Filas INX con mismatch textual: {len(mismatched_text)}")
    if obs_has_rel and inx_has_rel:
        print(f"Filas INX con mismatch relation: {len(mismatched_rel)}")
    if kit_has_backref:
        print(f"Backrefs KIT faltantes: {len(missing_backrefs)}")

    if mismatched_text:
        for path, expected, actual in mismatched_text[:5]:
            print(f"  - {path}")
            print(f"    OBSIDIAN_DB: {expected[:120]}")
            print(f"    INX:         {actual[:120]}")
    if mismatched_rel:
        for path, expected, actual in mismatched_rel[:5]:
            print(f"  - {path}")
            print(f"    OBSIDIAN_DB.KIT: {expected}")
            print(f"    INX.KIT:         {actual}")
    if missing_backrefs:
        for path, kid, row_id in missing_backrefs[:5]:
            print(f"  - {path} -> kit:{kid} no contiene obsidian-row {row_id} en 'Usada en notas'")

    if mismatched_text or mismatched_rel or missing_backrefs:
        print("\n    Ejecuta: python tools/ensure_kit_cross_fields.py")
        print("             python tools/sync_inx_links.py --source obsidian --limit 200")
        print("             python tools/sync_inx_links.py --source kit --limit 200")
        return 1

    print("\nOK: las referencias KIT detectadas en OBSIDIAN_DB se preservan en INX y write-backean a KIT.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["b", "c"], default="b")
    args = parser.parse_args()

    db_kit = os.getenv("NOTION_DB_KIT")
    db_inx = os.getenv("NOTION_DB_INX")
    db_obsidian = os.getenv("OBSIDIAN_DB")
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
    fuente_mismatch: list[dict] = []
    for r in rows_inx:
        props = r.get("properties", {})
        clave = extract_property_value(props.get("Clave", {})) or ""
        if clave.startswith("kit:"):
            inx_kit_ids.add(_normalize(clave[len("kit:") :]))
            fuente = extract_property_value(props.get("Fuente", {})) or ""
            if fuente and fuente != "KIT":
                fuente_mismatch.append({"clave": clave, "fuente": fuente})

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

    if fuente_mismatch:
        print("\n[!] Filas kit:* con Fuente distinta de KIT (hasta 5):")
        for row in fuente_mismatch[:5]:
            print(f"  - {row['clave']} | Fuente={row['fuente']}")
        print("\n    Ejecuta: python tools/ensure_kit_cross_fields.py")
        print("             python tools/sync_inx_links.py --source kit --limit 200")
        return 1

    if len(kit_entries) == 0:
        print("\n[!] No hay entradas con Titulo en NOTION_DB_KIT.")
        return 1

    print("\nOK: todas las entradas KIT estan reflejadas en INX-ENLACES.")
    if args.scope == "c":
        if not db_obsidian:
            print("\nFalta OBSIDIAN_DB en .env para --scope c")
            return 2
        return _scope_c(db_kit, db_obsidian, db_inx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
