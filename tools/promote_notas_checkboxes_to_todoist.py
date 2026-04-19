"""
Promueve checkboxes pendientes (- [ ] ...) de una nota Obsidian a tareas Todoist.

Detecta en la nota lineas tipo `- [ ] Descripcion`. Para cada una que NO tenga
marcador `<!-- todoist:<id> -->`, crea una tarea en Todoist con:
  - content = Descripcion
  - description = ruta relativa de la nota
Luego re-escribe la nota in-place marcando la linea con el id devuelto para
evitar duplicar en re-ejecuciones (idempotente).

Opcional --sync: tras crear, encadena log_obsidian_changes + sync_inx_links
--source obsidian + --source todoist para que INX-ENLACES refleje la captura.

Uso:
    python tools/promote_notas_checkboxes_to_todoist.py <nombre-nota> [--sync]
    python tools/promote_notas_checkboxes_to_todoist.py "N251104-Analisis Estudio 2" --sync

Requisitos:
  - .env con TODOIST_API_TOKEN.
  - Nota existente en el vault (OBSIDIAN_ALPHA_PATH).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.obsidian_tools import ALPHA_PATH, get_todas_notas
from tools.todoist_tools import create_task


CHECKBOX_RE = re.compile(
    r"^(?P<indent>\s*)- \[ \] (?P<content>.+?)(?P<marker>\s*<!-- todoist:[^ ]+ -->)?\s*$"
)


def _find_nota_path(nombre: str) -> Path | None:
    ref = nombre.lower().replace(".md", "")
    for n in get_todas_notas():
        if n.get("nombre", "").lower().replace(".md", "") == ref:
            return Path(n["path"])
    return None


def _run_sync_chain() -> bool:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    steps = [
        ["tools/log_obsidian_changes.py"],
        ["tools/sync_todoist_to_notion.py"],
        ["tools/sync_inx_links.py", "--source", "obsidian", "--limit", "200"],
        ["tools/sync_inx_links.py", "--source", "todoist", "--limit", "200"],
    ]
    for step in steps:
        print(f"[sync] {' '.join(step)}")
        result = subprocess.run([sys.executable, *step], cwd=repo_root)
        if result.returncode != 0:
            print(f"[sync] fallo en {step[0]} (exit={result.returncode})", file=sys.stderr)
            return False
    return True


def promote(nombre: str, sync: bool = False) -> dict:
    path = _find_nota_path(nombre)
    if not path:
        raise ValueError(f"Nota '{nombre}' no encontrada en vault Obsidian")

    rel = path.relative_to(ALPHA_PATH)
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=False)

    created: list[tuple[int, str, str]] = []
    new_lines: list[str] = []
    for i, line in enumerate(lines):
        m = CHECKBOX_RE.match(line)
        if not m:
            new_lines.append(line)
            continue
        if m.group("marker"):
            new_lines.append(line)
            continue
        desc = m.group("content").strip()
        if not desc:
            new_lines.append(line)
            continue
        task = create_task(content=desc, description=f"Obsidian: {rel}")
        task_id = str(task.get("id") or "")
        if not task_id:
            print(f"[warn] linea {i + 1}: Todoist no devolvio id, salto", file=sys.stderr)
            new_lines.append(line)
            continue
        new_line = f"{m.group('indent')}- [ ] {desc} <!-- todoist:{task_id} -->"
        new_lines.append(new_line)
        created.append((i + 1, task_id, desc))
        print(f"[created] L{i + 1} todoist:{task_id} | {desc[:70]}")

    if created:
        path.write_text("\n".join(new_lines) + ("\n" if content.endswith("\n") else ""), encoding="utf-8")

    print(f"\nResumen: {len(created)} tarea(s) creada(s) desde {rel}")

    if sync:
        if not _run_sync_chain():
            raise RuntimeError("sync fallo")

    return {"nota": str(rel), "created": len(created), "ids": [c[1] for c in created]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nombre", help="Nombre de la nota en vault (con o sin .md)")
    parser.add_argument("--sync", action="store_true",
                        help="Tras crear, cierra cruce INX obsidian:<ruta> + todoist:<id>.")
    args = parser.parse_args()
    try:
        promote(args.nombre, args.sync)
    except (ValueError, RuntimeError) as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
