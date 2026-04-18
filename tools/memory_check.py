"""
Valida la integridad de la capa de memoria curada del proyecto.

Comprueba:
  1. Existen memory/INDEX.md, memory/PURPOSE.md, memory/STRUCTURE.md.
  2. Todos los enlaces markdown [label](path) dentro de memory/INDEX.md apuntan
     a ficheros o directorios reales (relativos a la carpeta memory/).
  3. El bloque TREE dentro de memory/STRUCTURE.md esta al dia
     (llama a `tools/snapshot_structure.py --check`).

Uso:
    python tools/memory_check.py           # reporta todos los problemas y sale 0/1
    python tools/memory_check.py --fix-tree  # regenera el TREE si esta desfasado

Pensado para ejecutar a mano, en pre-commit o en CI.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = _ROOT / "memory"
INDEX_PATH = MEMORY_DIR / "INDEX.md"
PURPOSE_PATH = MEMORY_DIR / "PURPOSE.md"
STRUCTURE_PATH = MEMORY_DIR / "STRUCTURE.md"
SNAPSHOT_SCRIPT = _ROOT / "tools" / "snapshot_structure.py"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:")


def _check_required_files() -> list[str]:
    problems = []
    for p in (INDEX_PATH, PURPOSE_PATH, STRUCTURE_PATH):
        if not p.exists():
            problems.append(f"FALTA: {p}")
    return problems


def _check_index_links() -> list[str]:
    if not INDEX_PATH.exists():
        return []
    problems: list[str] = []
    text = INDEX_PATH.read_text(encoding="utf-8")
    for match in LINK_RE.finditer(text):
        label = match.group(1).strip()
        target = match.group(2).strip()
        if target.startswith(EXTERNAL_PREFIXES):
            continue
        if target.startswith("#"):
            continue
        target_path = target.split("#", 1)[0]
        resolved = (INDEX_PATH.parent / target_path).resolve()
        if not resolved.exists():
            problems.append(f"ENLACE ROTO en INDEX.md: [{label}]({target}) -> {resolved}")
    return problems


def _check_tree_up_to_date(fix: bool = False) -> list[str]:
    if not STRUCTURE_PATH.exists():
        return []
    cmd = [sys.executable, str(SNAPSHOT_SCRIPT), "--check"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        return []
    if fix:
        regen = subprocess.run(
            [sys.executable, str(SNAPSHOT_SCRIPT)], capture_output=True, text=True, encoding="utf-8"
        )
        if regen.returncode == 0:
            return []
        return [f"TREE regen fallo: {regen.stderr.strip() or regen.stdout.strip()}"]
    return [f"TREE desfasado en STRUCTURE.md. Ejecuta: python tools/snapshot_structure.py"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix-tree", action="store_true", help="Regenera el TREE si esta desfasado")
    args = parser.parse_args()

    problems: list[str] = []
    problems.extend(_check_required_files())
    problems.extend(_check_index_links())
    problems.extend(_check_tree_up_to_date(fix=args.fix_tree))

    if not problems:
        print("memory/ OK: ficheros presentes, enlaces validos, TREE al dia.")
        return 0

    print(f"memory/ KO: {len(problems)} problema(s)")
    for p in problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
