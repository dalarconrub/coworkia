"""
Resuelve o inicializa el chat del dia para el sistema multiagente.

Convencion:
  - Un fichero por dia: `chats/chat_YYYY-MM-DD.md`
  - Se crea desde `multiagents/chat_template.md` si no existe.
  - Si ya existe, se retoma (no se sobreescribe).

Uso:
    python tools/init_chat.py                 # imprime la ruta del chat activo + briefing
    python tools/init_chat.py --date 2026-04-18
    python tools/init_chat.py --quiet         # solo ruta, sin briefing (para otros scripts)
    python tools/init_chat.py --no-briefing   # ruta humana pero sin briefing

Otros scripts pueden importar `ensure_today_chat()` y `get_chat_path()`.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date as Date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


_ROOT = Path(__file__).resolve().parent.parent
CHATS_DIR = _ROOT / "chats"
TEMPLATE_PATH = _ROOT / "multiagents" / "chat_template.md"
MEMORY_DIR = _ROOT / "memory"
DEVLOG_PATH = _ROOT / "devlog" / "DEVLOG.md"


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


def _last_devlog_entries(n: int = 3) -> list[str]:
    """Devuelve las ultimas n entradas reales del DEVLOG, saltando bloques de codigo."""
    if not DEVLOG_PATH.exists():
        return []
    text = DEVLOG_PATH.read_text(encoding="utf-8")
    entries: list[list[str]] = []
    current: list[str] | None = None
    in_code_block = False
    import re
    header_re = re.compile(r"^## \d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z \u2014 \w+ \u2014 \[\w+\] .+$")
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            if current is not None:
                current.append(line)
            continue
        if in_code_block:
            if current is not None:
                current.append(line)
            continue
        if header_re.match(line):
            if current:
                entries.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
    if current:
        entries.append(current)
    return ["\n".join(e).rstrip() for e in entries[-n:]]


def _render_briefing(chat_path: Path, created: bool) -> str:
    state = "creado" if created else "existente"
    lines = [f"Chat activo ({state}): {chat_path}", ""]

    lines.append("--- Memoria del proyecto (leer antes de responder) ---")
    for fname in ("INDEX.md", "PURPOSE.md", "STRUCTURE.md"):
        p = MEMORY_DIR / fname
        mark = "OK" if p.exists() else "MISSING"
        lines.append(f"  [{mark}] {p}")

    snapshot = MEMORY_DIR / "SNAPSHOT.md"
    if snapshot.exists():
        lines.append(f"  [OK] {snapshot}  (MEMORIA/BLOQUEO/SIGUIENTE agregados)")

    lines.append("")
    lines.append("--- Ultimas 3 entradas del devlog ---")
    entries = _last_devlog_entries(3)
    if not entries:
        lines.append("  (sin entradas)")
    else:
        for e in entries:
            lines.append("")
            lines.append(e)
    lines.append("")
    lines.append("--- Recordatorio ---")
    lines.append("  Append-only en chats/ y devlog/. UTF-8 estricto.")
    lines.append("  Tras cerrar decision / MEMORIA operativa / feature / BLOQUEO / REVERT:")
    lines.append("  python tools/devlog.py append --agent <X> --area <AREA> --status <S> ...")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=None, help="Fecha YYYY-MM-DD (por defecto hoy)")
    parser.add_argument("--quiet", action="store_true", help="Imprime solo la ruta (sin briefing)")
    parser.add_argument("--no-briefing", action="store_true", help="Imprime ruta humana sin briefing")
    args = parser.parse_args()

    for_date = Date.fromisoformat(args.date) if args.date else None
    path, created = ensure_today_chat(for_date)

    if args.quiet:
        print(path)
        return 0
    if args.no_briefing:
        state = "creado" if created else "existente"
        print(f"Chat activo ({state}): {path}")
        return 0

    print(_render_briefing(path, created))
    return 0


if __name__ == "__main__":
    sys.exit(main())
