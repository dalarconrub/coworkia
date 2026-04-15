"""
Promueve una nota de Obsidian a PTN-Notas.

- Dedup por `Título` (nombre de archivo sin .md).
- Si ya existe, actualiza Fecha y Proyecto.
- Opcionalmente enlaza a un proyecto PTN (por ID o nombre).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    query_data_source,
    create_page,
    update_page_properties,
    extract_property_value,
)
from tools.obsidian_tools import get_todas_notas


def _resolve_project_id(db_proyectos: str, ref: str) -> str | None:
    if "-" in ref and len(ref.replace("-", "")) == 32:
        return ref
    ref_low = ref.lower()
    for r in query_data_source(db_proyectos):
        p = r.get("properties", {})
        nombre = extract_property_value(p.get("Nombre del Proyecto", {})) \
            or extract_property_value(p.get("Nombre", {})) or ""
        if nombre.lower() == ref_low or ref_low in nombre.lower():
            return r["id"]
    return None


def _find_nota(nombre: str) -> dict | None:
    nombre_low = nombre.lower().replace(".md", "")
    for n in get_todas_notas():
        if n.get("nombre", "").lower().replace(".md", "") == nombre_low:
            return n
    return None


def _find_ptn_nota(db_notas: str, titulo: str) -> dict | None:
    for r in query_data_source(db_notas):
        if extract_property_value(r.get("properties", {}).get("Título", {})) == titulo:
            return r
    return None


def promote(nombre: str, proyecto_ref: str | None = None) -> dict:
    db_notas = os.getenv("NOTION_DS_NOTAS")
    db_proy = os.getenv("NOTION_DS_PROYECTOS")
    if not db_notas:
        raise RuntimeError("Falta NOTION_DS_NOTAS en .env")

    nota = _find_nota(nombre)
    if not nota:
        raise ValueError(f"Nota '{nombre}' no encontrada en vault Obsidian")

    titulo = nota["nombre"].replace(".md", "")
    mtime = os.path.getmtime(nota["path"])
    fecha = datetime.fromtimestamp(mtime).date().isoformat()

    props = {
        "Título": {"title": [{"text": {"content": titulo}}]},
        "Fecha": {"date": {"start": fecha}},
        "Tarea": {"rich_text": [{"text": {"content": nota.get("relativo", "")}}]},
    }
    if proyecto_ref:
        if not db_proy:
            raise RuntimeError("Falta NOTION_DS_PROYECTOS en .env (requerido con --proyecto)")
        pid = _resolve_project_id(db_proy, proyecto_ref)
        if not pid:
            raise ValueError(f"Proyecto PTN '{proyecto_ref}' no encontrado")
        props["Proyecto"] = {"rich_text": [{"text": {"content": pid}}]}

    existente = _find_ptn_nota(db_notas, titulo)
    if existente:
        update_page_properties(existente["id"], props)
        return {"action": "updated", "id": existente["id"], "titulo": titulo, "fecha": fecha}
    page = create_page(parent_id=db_notas, title=titulo, properties=props, is_data_source=True)
    return {"action": "created", "id": page["id"], "titulo": titulo, "fecha": fecha}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Promover nota Obsidian a PTN-Notas")
    parser.add_argument("nombre", help="Nombre de la nota en vault (con o sin .md)")
    parser.add_argument("--proyecto", default=None, help="ID o nombre del proyecto PTN")
    args = parser.parse_args()
    res = promote(args.nombre, args.proyecto)
    print(f"{res['action']}: {res['titulo']} (fecha={res['fecha']}) id={res['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
