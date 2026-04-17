"""
Resuelve o inicializa el chat del dia para el sistema multiagente.

Convencion:
  - Un fichero por dia: `chats/chat_YYYY-MM-DD.md`
  - Se crea desde `multiagents/chat_template.md` si no existe.
  - Si ya existe, se retoma (no se sobreescribe).

Uso:
    python tools/init_chat.py                 # imprime la ruta del chat activo
    python tools/init_chat.py --date 2026-04-18

Otros scripts pueden importar `ensure_today_chat()` y `get_chat_path()`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date as Date
from pathlib import Path


_ROOT = Path(__file__).resolve().parent.parent
CHATS_DIR = _ROOT / "chats"
TEMPLATE_PATH = _ROOT / "multiagents" / "chat_template.md"


def get_chat_path(for_date: Date | None = None) -> Path:
    day = for_date or Date.today()
    return CHATS_DIR / f"chat_{day.isoformat()}.md"


def ensure_today_chat(for_date: Date | None = None) -> tuple[Path, bool]:
    """Devuelve (ruta_chat_activo, creado_ahora)."""
    day = for_date or Date.today()
    path = get_chat_path(day)
    if path.exists():
        return path, False

    CHATS_DIR.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    rendered = template.replace("{{DATE}}", day.isoformat())
    path.write_text(rendered, encoding="utf-8", newline="")
    return path, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=None, help="Fecha YYYY-MM-DD (por defecto hoy)")
    parser.add_argument("--quiet", action="store_true", help="Imprime solo la ruta")
    args = parser.parse_args()

    for_date = Date.fromisoformat(args.date) if args.date else None
    path, created = ensure_today_chat(for_date)

    if args.quiet:
        print(path)
    else:
        state = "creado" if created else "existente"
        print(f"Chat activo ({state}): {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
