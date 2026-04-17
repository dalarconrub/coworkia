"""
Repara mojibake UTF-8 -> Latin-1 -> UTF-8 en un fichero de texto.

Estrategia:
  1. Localiza runs consecutivos de caracteres Latin-1 (U+0080..U+00FF).
  2. Para cada run, intenta revertirlo con `.encode('latin-1').decode('utf-8')`.
     Si el resultado es UTF-8 valido, lo sustituye; si no, lo deja intacto.
  3. Aplica un post-pase de sustituciones para simbolos canonicos que se
     rompieron al cruzar saltos de linea (U+0085 NEL -> '\\n').

Uso:
    python tools/fix_chat_mojibake.py [ruta] [--dry-run] [--no-backup] [--output OUT]
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


LATIN1_RUN = re.compile(r"[\u0080-\u00ff]+")


RESIDUAL_REPAIRS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"â\u009c\s*\n\s*/â\u009d\u008c"), "✅/❌"),
    (re.compile(r"â\u009c\s*\n\s+CERRADO"), "✅ CERRADO"),
    (re.compile(r"â\u009c\s*\n\s+Opción"), "✅ Opción"),
    (re.compile(r"â\u009c\s*\n\s+Alineado"), "✅ Alineado"),
    (re.compile(r"(?<=\s)â\u009c(?=\s|$)", re.MULTILINE), "✅"),
    (re.compile(r"â\u009d\u008c"), "❌"),
]


def _fix_run(match: re.Match[str]) -> str:
    run = match.group(0)
    try:
        candidate = run.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return run
    return candidate


def repair_text(text: str) -> tuple[str, dict[str, int]]:
    stats = {"runs_fixed": 0, "residual_repairs": 0}

    def replace_with_stats(match: re.Match[str]) -> str:
        fixed = _fix_run(match)
        if fixed != match.group(0):
            stats["runs_fixed"] += 1
        return fixed

    result = LATIN1_RUN.sub(replace_with_stats, text)

    for pattern, replacement in RESIDUAL_REPAIRS:
        result, count = pattern.subn(replacement, result)
        stats["residual_repairs"] += count

    return result, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="chat.md", help="Fichero a reparar")
    parser.add_argument("--dry-run", action="store_true", help="No escribe, solo informa")
    parser.add_argument("--no-backup", action="store_true", help="No crea backup")
    parser.add_argument("--output", default=None, help="Escribe la salida en otra ruta en lugar de sobreescribir")
    args = parser.parse_args()

    src = Path(args.path)
    if not src.exists():
        print(f"ERROR: no existe {src}", file=sys.stderr)
        return 2

    original = src.read_text(encoding="utf-8")
    repaired, stats = repair_text(original)
    changed = repaired != original

    print(f"Fichero: {src}")
    print(f"Runs reparados: {stats['runs_fixed']}")
    print(f"Sustituciones residuales: {stats['residual_repairs']}")
    print(f"Cambios: {'si' if changed else 'no'}")

    if not changed or args.dry_run:
        return 0

    dest = Path(args.output) if args.output else src

    if dest == src and not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = src.with_name(f"{src.name}.bak-{stamp}")
        shutil.copy2(src, backup)
        print(f"Backup: {backup}")

    dest.write_text(repaired, encoding="utf-8", newline="")
    print(f"Escrito en: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
