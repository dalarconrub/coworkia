"""
Importa Areas, Bloques y Contextos desde los CSV refinados a Notion.
"""

import csv
import os
import re
import sys
from typing import Dict, Iterable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import create_page, query_data_source, extract_property_value


def _read_last_rows(path: str, key_field: str) -> Dict[str, dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    last: Dict[str, dict] = {}
    for r in rows:
        key = (r.get(key_field) or "").strip()
        if key:
            last[key] = r
    return last


def _extract_code(text: str) -> str:
    value = (text or "").strip()
    if not value:
        return ""
    if value.startswith("@"):
        value = value[1:]
    value = re.split(r"\s|\(", value, maxsplit=1)[0]
    return value.strip()


def _existing_codes(data_source_id: str) -> set[str]:
    rows = query_data_source(data_source_id)
    codes = set()
    for r in rows:
        props = r.get("properties", {})
        if "Codigo" in props:
            codes.add(extract_property_value(props["Codigo"]))
    return {c for c in codes if c}


def _create_rows(data_source_id: str, rows: Iterable[dict], kind: str) -> int:
    existing = _existing_codes(data_source_id)
    created = 0
    for r in rows:
        if kind == "area":
            codigo = (r.get("Area") or "").strip()
            if not re.match(r"^A[0-4]$", codigo):
                continue
            titulo = (r.get("A-Text") or "").strip() or codigo
            desc = (r.get("Nombre") or "").strip()
            url = (r.get("Area URL") or "").strip()
            if codigo in existing:
                continue
            props = {
                "Nombre": {"title": [{"text": {"content": titulo}}]},
                "Codigo": {"rich_text": [{"text": {"content": codigo}}]},
            }
            if desc:
                props["Descripcion"] = {"rich_text": [{"text": {"content": desc}}]}
            if url:
                props["URL"] = {"url": url}
        elif kind == "bloque":
            codigo = (r.get("Name") or "").strip()
            if not re.match(r"^B[0-9][0-9A-Z]$", codigo):
                continue
            titulo = (r.get("Fórmula") or "").strip() or codigo
            desc = (r.get("Nombre") or "").strip()
            area_raw = (r.get("AREA") or "").strip()
            area = _extract_code(area_raw)
            url = (r.get("URL") or "").strip()
            if codigo in existing:
                continue
            props = {
                "Nombre": {"title": [{"text": {"content": titulo}}]},
                "Codigo": {"rich_text": [{"text": {"content": codigo}}]},
            }
            if area:
                props["Area"] = {"rich_text": [{"text": {"content": area}}]}
            if desc:
                props["Descripcion"] = {"rich_text": [{"text": {"content": desc}}]}
            if url:
                props["URL"] = {"url": url}
        else:
            codigo = (r.get("Name") or "").strip()
            if not re.match(r"^C[0-9][0-9A-Za-z]{2}$", codigo):
                continue
            titulo = (r.get("C-TEXT") or "").strip() or codigo
            desc = (r.get("TITULO") or "").strip()
            bloque_raw = (r.get("BLOQUE") or "").strip()
            bloque = _extract_code(bloque_raw)
            url = (r.get("URL") or "").strip()
            if codigo in existing:
                continue
            props = {
                "Nombre": {"title": [{"text": {"content": titulo}}]},
                "Codigo": {"rich_text": [{"text": {"content": codigo}}]},
            }
            if bloque:
                props["Bloque"] = {"rich_text": [{"text": {"content": bloque}}]}
            if desc:
                props["Descripcion"] = {"rich_text": [{"text": {"content": desc}}]}
            if url:
                props["URL"] = {"url": url}

        create_page(parent_id=data_source_id, title="ABC", properties=props, is_data_source=True)
        created += 1
    return created


def main() -> int:
    if len(sys.argv) < 4:
        print("Uso: python tools/import_abc_taxonomy.py <DS_AREAS> <DS_BLOQUES> <DS_CONTEXTOS>")
        return 2

    ds_area, ds_bloque, ds_contexto = sys.argv[1:4]

    base_dir = os.path.join("Sistemas", "ABC")
    area_csv = os.path.join(base_dir, "ABC 2a5622cf315b8044a83feb2033f661d1_ABC-AREA 2a5622cf315b813faa22000be68a3416_all.csv")
    bloque_csv = os.path.join(base_dir, "ABC 2a5622cf315b8044a83feb2033f661d1_ABC-BLOQUE 2a5622cf315b803ca9f0000bd4fbd157_all.csv")
    contexto_csv = os.path.join(base_dir, "ABC 2a5622cf315b8044a83feb2033f661d1_ABC-CONTEXTO 2a5622cf315b8018919f000bbe9adc05_all.csv")

    areas = _read_last_rows(area_csv, "Area")
    bloques = _read_last_rows(bloque_csv, "Name")
    contextos = _read_last_rows(contexto_csv, "Name")

    a_count = _create_rows(ds_area, areas.values(), "area")
    b_count = _create_rows(ds_bloque, bloques.values(), "bloque")
    c_count = _create_rows(ds_contexto, contextos.values(), "contexto")

    print(f"Areas creadas: {a_count}")
    print(f"Bloques creados: {b_count}")
    print(f"Contextos creados: {c_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
