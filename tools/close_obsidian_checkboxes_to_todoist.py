"""
Cierra en Todoist checkboxes ya marcados en notas Obsidian.

Detecta lineas:
  - [x] Descripcion <!-- todoist:<id> -->

Y para cada task_id:
  - intenta cerrar la tarea en Todoist
  - marca Estado=Completada en TODOIST_DB_TAREAS
  - marca Estado=Completada en INX-ENLACES para la fila todoist:<id>

Uso:
    python tools/close_obsidian_checkboxes_to_todoist.py <nombre-nota>
    python tools/close_obsidian_checkboxes_to_todoist.py <nombre-nota> --sync
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import (
    extract_property_value,
    get_database_info,
    query_data_source,
    update_database_properties,
    update_page_properties,
)
from tools.obsidian_tools import ALPHA_PATH, get_todas_notas
from tools.todoist_tools import close_task


CLOSED_MARKERS = (
    "- [x] ",
    "- [X] ",
)


def _find_nota_path(nombre: str) -> Path | None:
    ref = nombre.lower().replace(".md", "")
    for n in get_todas_notas():
        if n.get("nombre", "").lower().replace(".md", "") == ref:
            return Path(n["path"])
    return None


def _extract_closed_ids(path: Path) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    seen: set[str] = set()
    content = path.read_text(encoding="utf-8")
    for line_num, line in enumerate(content.splitlines(), 1):
        if not line.lstrip().startswith(CLOSED_MARKERS):
            continue
        marker = "<!-- todoist:"
        if marker not in line:
            continue
        task_id = line.split(marker, 1)[1].split("-->", 1)[0].strip()
        if not task_id or task_id in seen:
            continue
        seen.add(task_id)
        hits.append((line_num, task_id))
    return hits


def _page_by_prop(db_id: str, prop_name: str, expected: str) -> str | None:
    for row in query_data_source(db_id):
        props = row.get("properties", {})
        value = extract_property_value(props.get(prop_name, {})) or ""
        if value == expected:
            return row["id"]
    return None


def _ensure_inx_completed_status() -> None:
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_inx:
        raise RuntimeError("Falta NOTION_DB_INX en .env")
    info = get_database_info(db_inx, object_type="data_source")
    estado = ((info.get("raw") or {}).get("properties") or {}).get("Estado") or {}
    options = (((estado.get("select") or {}).get("options")) or [])
    names = {opt.get("name", "") for opt in options}
    if "Completada" in names:
        return
    update_database_properties(
        db_inx,
        {"Estado": {"select": {"options": [{"name": "Completada", "color": "pink"}]}}},
    )


def _mark_notion_completed(task_id: str) -> None:
    db_todoist = os.getenv("TODOIST_DB_TAREAS")
    db_inx = os.getenv("NOTION_DB_INX")
    if not db_todoist or not db_inx:
        raise RuntimeError("Faltan TODOIST_DB_TAREAS o NOTION_DB_INX en .env")
    _ensure_inx_completed_status()

    todoist_page = _page_by_prop(db_todoist, "Todoist ID", task_id)
    if todoist_page:
        update_page_properties(todoist_page, {"Estado": {"select": {"name": "Completada"}}})

    inx_page = _page_by_prop(db_inx, "Clave", f"todoist:{task_id}")
    if inx_page:
        update_page_properties(inx_page, {"Estado": {"select": {"name": "Completada"}}})


def _run_sync_chain() -> bool:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    steps = [
        ["tools/sync_todoist_to_notion.py", "--save-active"],
        ["tools/sync_todoist_to_notion.py", "--finalize-completed"],
        ["tools/sync_inx_links.py", "--source", "todoist", "--limit", "200"],
    ]
    for step in steps:
        print(f"[sync] {' '.join(step)}")
        result = subprocess.run([sys.executable, *step], cwd=repo_root)
        if result.returncode != 0:
            print(f"[sync] fallo en {step[0]} (exit={result.returncode})", file=sys.stderr)
            return False
    return True


def close_from_note(nombre: str, sync: bool = False) -> dict:
    path = _find_nota_path(nombre)
    if not path:
        raise ValueError(f"Nota '{nombre}' no encontrada en vault Obsidian")

    hits = _extract_closed_ids(path)
    if not hits:
        print(f"Sin checkboxes cerrados con marker en {path.name}")
        return {"nota": path.name, "closed": 0, "ids": []}

    closed_ids: list[str] = []
    for line_num, task_id in hits:
        try:
            close_task(task_id)
            print(f"[closed] L{line_num} todoist:{task_id}")
        except Exception as exc:  # noqa: BLE001
            # Si ya estaba cerrada o inaccesible, aun intentamos reflejar el estado local.
            print(f"[warn] L{line_num} todoist:{task_id} no se pudo cerrar via API: {exc}", file=sys.stderr)
        _mark_notion_completed(task_id)
        closed_ids.append(task_id)

    print(f"\nResumen: {len(closed_ids)} tarea(s) cerrada(s) desde {path.relative_to(ALPHA_PATH)}")

    if sync and not _run_sync_chain():
        raise RuntimeError("sync fallo")

    return {"nota": path.name, "closed": len(closed_ids), "ids": closed_ids}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nombre", help="Nombre de la nota en vault (con o sin .md)")
    parser.add_argument("--sync", action="store_true", help="Reconciliar TODOIST_DB_TAREAS e INX tras el cierre.")
    args = parser.parse_args()
    try:
        close_from_note(args.nombre, args.sync)
    except (ValueError, RuntimeError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
