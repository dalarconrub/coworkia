"""
Promueve una nota de Obsidian a PTN-Notas.

- Dedup por `Título` (nombre de archivo sin .md).
- Si ya existe, actualiza Fecha y Proyecto.
- Opcionalmente enlaza a un proyecto PTN (por ID o nombre).
- Opcional `--sync`: cierra el cruce INX `obsidian:<ruta>` <-> `ptn:<id>`
  encadenando `log_obsidian_changes` + `log_ptn_changes` +
  `sync_inx_links --source {obsidian,notion}`.
"""

from __future__ import annotations

import os
import subprocess
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


def _resolve_task_id(db_tareas: str, ref: str) -> str | None:
    if "-" in ref and len(ref.replace("-", "")) == 32:
        return ref
    ref_low = ref.lower()
    for r in query_data_source(db_tareas):
        props = r.get("properties", {})
        nombre = ""
        for key in props:
            if key.lower() in {"nombre de la tarea", "nombre", "tarea", "título", "titulo"}:
                val = extract_property_value(props[key]) or ""
                if val:
                    nombre = val
                    break
        if nombre and (nombre.lower() == ref_low or ref_low in nombre.lower()):
            return r["id"]
    return None


def _find_nota(nombre: str) -> dict | None:
    nombre_low = nombre.lower().replace(".md", "")
    for n in get_todas_notas():
        if n.get("nombre", "").lower().replace(".md", "") == nombre_low:
            return n
    return None


def _find_ptn_nota(rows: list[dict], titulo: str) -> dict | None:
    for r in rows:
        if extract_property_value(r.get("properties", {}).get("Título", {})) == titulo:
            return r
    return None


def _require_schema_migrated(rows: list[dict]) -> None:
    if rows and "Ruta Obsidian" not in rows[0].get("properties", {}):
        raise RuntimeError(
            "La propiedad 'Ruta Obsidian' no existe en NOTION_DS_NOTAS. "
            "Ejecuta primero: python tools/migrate_notas_ruta_obsidian.py"
        )


def _schema_has(rows: list[dict], prop: str) -> bool:
    return bool(rows) and prop in rows[0].get("properties", {})


def _project_props(rows: list[dict], pid: str) -> dict:
    if _schema_has(rows, "Proyecto PTN"):
        return {"Proyecto PTN": {"relation": [{"id": pid}]}}
    return {"Proyecto": {"rich_text": [{"text": {"content": pid}}]}}


def _task_props(rows: list[dict], tid: str) -> dict:
    if _schema_has(rows, "Tarea PTN"):
        return {"Tarea PTN": {"relation": [{"id": tid}]}}
    return {"Tarea": {"rich_text": [{"text": {"content": tid}}]}}


def promote(
    nombre: str,
    proyecto_ref: str | None = None,
    tarea_ref: str | None = None,
) -> dict:
    db_notas = os.getenv("NOTION_DS_NOTAS")
    db_proy = os.getenv("NOTION_DS_PROYECTOS")
    db_tar = os.getenv("NOTION_DS_TAREAS")
    if not db_notas:
        raise RuntimeError("Falta NOTION_DS_NOTAS en .env")

    rows_notas = query_data_source(db_notas)
    _require_schema_migrated(rows_notas)

    nota = _find_nota(nombre)
    if not nota:
        raise ValueError(f"Nota '{nombre}' no encontrada en vault Obsidian")

    titulo = nota["nombre"].replace(".md", "")
    mtime = os.path.getmtime(nota["path"])
    fecha = datetime.fromtimestamp(mtime).date().isoformat()

    props = {
        "Título": {"title": [{"text": {"content": titulo}}]},
        "Fecha": {"date": {"start": fecha}},
        "Ruta Obsidian": {"rich_text": [{"text": {"content": nota.get("relativo", "")}}]},
    }
    if proyecto_ref:
        if not db_proy:
            raise RuntimeError("Falta NOTION_DS_PROYECTOS en .env (requerido con --proyecto)")
        pid = _resolve_project_id(db_proy, proyecto_ref)
        if not pid:
            raise ValueError(f"Proyecto PTN '{proyecto_ref}' no encontrado")
        props.update(_project_props(rows_notas, pid))
    if tarea_ref:
        if not db_tar:
            raise RuntimeError("Falta NOTION_DS_TAREAS en .env (requerido con --tarea)")
        tid = _resolve_task_id(db_tar, tarea_ref)
        if not tid:
            raise ValueError(f"Tarea PTN '{tarea_ref}' no encontrada")
        props.update(_task_props(rows_notas, tid))

    existente = _find_ptn_nota(rows_notas, titulo)
    if existente:
        update_page_properties(existente["id"], props)
        return {"action": "updated", "id": existente["id"], "titulo": titulo, "fecha": fecha}
    page = create_page(parent_id=db_notas, title=titulo, properties=props, is_data_source=True)
    return {"action": "created", "id": page["id"], "titulo": titulo, "fecha": fecha}


def _run_sync_chain() -> bool:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    steps = [
        ["tools/log_obsidian_changes.py"],
        ["tools/log_ptn_changes.py"],
        ["tools/sync_inx_links.py", "--source", "obsidian", "--limit", "200"],
        ["tools/sync_inx_links.py", "--source", "notion", "--limit", "200"],
    ]
    for step in steps:
        print(f"[sync] {' '.join(step)}")
        result = subprocess.run([sys.executable, *step], cwd=repo_root)
        if result.returncode != 0:
            print(f"[sync] fallo en {step[0]} (exit={result.returncode})", file=sys.stderr)
            return False
    return True


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Promover nota Obsidian a PTN-Notas")
    parser.add_argument("nombre", help="Nombre de la nota en vault (con o sin .md)")
    parser.add_argument("--proyecto", default=None, help="ID o nombre del proyecto PTN")
    parser.add_argument("--tarea", default=None, help="ID o nombre de la tarea PTN (NOTION_DS_TAREAS)")
    parser.add_argument(
        "--sync", action="store_true",
        help="Tras la promocion, cierra el cruce INX obsidian:<ruta> <-> ptn:<id>.",
    )
    args = parser.parse_args()
    res = promote(args.nombre, args.proyecto, args.tarea)
    print(f"{res['action']}: {res['titulo']} (fecha={res['fecha']}) id={res['id']}")
    if args.sync:
        if not _run_sync_chain():
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
