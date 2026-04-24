"""
Regenera el bloque TREE auto-generado dentro de `memory/STRUCTURE.md`.

El fichero STRUCTURE.md es hibrido:
  - Narrativa curada manualmente (que hace cada carpeta, logica, invariantes).
  - Bloque arbol auto-generado entre los marcadores:
        <!-- TREE:START -->
        ... (contenido sobrescrito por este script) ...
        <!-- TREE:END -->

Uso:
    python tools/snapshot_structure.py             # reescribe el bloque TREE
    python tools/snapshot_structure.py --check     # sale 1 si el bloque esta desactualizado

Profundidad: 2 niveles desde la raiz. Carpetas ruidosas excluidas.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
STRUCTURE_PATH = _ROOT / "memory" / "STRUCTURE.md"
START_MARK = "<!-- TREE:START -->"
END_MARK = "<!-- TREE:END -->"

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".idea", ".vscode", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "build", "dist", ".cache", ".next",
}
EXCLUDE_FILE_SUFFIXES = {".pyc", ".pyo", ".log"}
EXCLUDE_RELATIVE_FILES = {
    Path("artifacts") / "inoreader_state.json",
    Path("artifacts") / "inoreader_sync_state.json",
    Path(".claude") / "settings.json",
}

MAX_DEPTH = 2
MAX_CHILDREN_PER_DIR = 40


def _should_skip(p: Path) -> bool:
    try:
        rel = p.relative_to(_ROOT)
    except ValueError:
        rel = p
    if rel in EXCLUDE_RELATIVE_FILES:
        return True
    if p.name in EXCLUDE_DIRS:
        return True
    if p.is_file() and p.suffix in EXCLUDE_FILE_SUFFIXES:
        return True
    if p.name.startswith(".") and p.name not in {".claude", ".github", ".env.example"}:
        return True
    return False


def _sort_key(p: Path) -> tuple[int, str]:
    return (0 if p.is_dir() else 1, p.name.lower())


def _tree_lines(root: Path, depth: int = 0) -> list[str]:
    if depth > MAX_DEPTH:
        return []
    try:
        children = sorted((c for c in root.iterdir() if not _should_skip(c)), key=_sort_key)
    except PermissionError:
        return []

    lines: list[str] = []
    shown = children[:MAX_CHILDREN_PER_DIR]
    truncated = len(children) - len(shown)

    for child in shown:
        prefix = "  " * depth
        suffix = "/" if child.is_dir() else ""
        lines.append(f"{prefix}- {child.name}{suffix}")
        if child.is_dir() and depth < MAX_DEPTH:
            lines.extend(_tree_lines(child, depth + 1))

    if truncated > 0:
        prefix = "  " * depth
        lines.append(f"{prefix}- ... ({truncated} mas)")
    return lines


def build_tree_block() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    header = f"_Auto-generado por `tools/snapshot_structure.py` @ {now}. No editar a mano dentro de este bloque._"
    tree = "\n".join(_tree_lines(_ROOT))
    return f"{START_MARK}\n\n{header}\n\n```\n{tree}\n```\n\n{END_MARK}"


def _replace_block(text: str, new_block: str) -> str:
    start = text.find(START_MARK)
    end = text.find(END_MARK)
    if start == -1 or end == -1 or end < start:
        raise SystemExit(
            f"No se encontraron los marcadores {START_MARK} / {END_MARK} en {STRUCTURE_PATH}."
        )
    end_full = end + len(END_MARK)
    return text[:start] + new_block + text[end_full:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Salir 1 si el bloque esta desfasado")
    args = parser.parse_args()

    if not STRUCTURE_PATH.exists():
        raise SystemExit(f"No existe {STRUCTURE_PATH}. Crealo con los marcadores antes.")

    current = STRUCTURE_PATH.read_text(encoding="utf-8")
    new_block = build_tree_block()
    updated = _replace_block(current, new_block)

    if args.check:
        # Ignorar el timestamp del header para evitar falsos positivos.
        def _strip_ts(t: str) -> str:
            import re
            return re.sub(r"@ \d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z", "@ TS", t)

        if _strip_ts(current) == _strip_ts(updated):
            print("STRUCTURE.md al dia.")
            return 0
        print("STRUCTURE.md DESFASADO. Ejecuta `python tools/snapshot_structure.py`.")
        return 1

    if current == updated:
        print("Sin cambios en el arbol.")
        return 0
    STRUCTURE_PATH.write_text(updated, encoding="utf-8", newline="")
    print(f"STRUCTURE.md actualizado: {STRUCTURE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
