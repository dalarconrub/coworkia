"""
DevLog: append-only feature-level development log for Coworkia.

Fuente de verdad narrativa del desarrollo, complementaria a:
  - `git log` (commits)
  - `chats/chat_YYYY-MM-DD.md` (conversacion del dia)

Reglas:
  - Append-only. Nunca editar ni borrar entradas previas.
  - UTF-8 estricto.
  - Un hito = una entrada (no una por commit).
  - Tag [AREA] obligatorio en el titulo.

Uso:
    # Anadir entrada
    python tools/devlog.py append --agent Claude --area MULTIAGENT \
        --status DONE --title "DevLog obligatorio para agentes" \
        --summary "Se crea devlog/DEVLOG.md y tools/devlog.py; se actualiza protocolo." \
        [--commits d5c6b5c,d2dbeb9] [--refs "CERRADO #1"]

    # Consultar
    python tools/devlog.py view                   # ultimas 20
    python tools/devlog.py view --area PTN
    python tools/devlog.py view --agent Claude --limit 5
    python tools/devlog.py view --status BLOCKED
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


_ROOT = Path(__file__).resolve().parent.parent
DEVLOG_PATH = _ROOT / "devlog" / "DEVLOG.md"
CHATS_DIR = _ROOT / "chats"

ROOT_AGENTS = {"Claude", "Copilot", "Codex"}
# `Cursor` es una identidad operativa adicional (no tiene subagentes Root/Sub).
VALID_AGENTS = {"David", "Cursor"} | ROOT_AGENTS  # raices + director + cursor; subagentes admitidos como Root/Sub
_SUBAGENT_RE = re.compile(r"^(?P<root>Claude|Copilot|Codex)/(?P<sub>[A-Za-z0-9_\-]+)$")
VALID_STATUSES = {"START", "PROGRESS", "BLOCKED", "UNBLOCKED", "DONE", "REVERT"}
VALID_AREAS = {
    "MAR", "PTN", "KIT", "GIT", "BIB", "ABGD", "INX",
    "REP",  # alias historico de GIT, conservado para que entradas pre-2026-04-24 sigan validas
    "MULTIAGENT", "TOOLING", "DOCS", "INFRA",
}

ENTRY_HEADER_RE = re.compile(
    r"^## (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z) "
    r"\u2014 (?P<agent>[\w/\-]+) \u2014 \[(?P<area>\w+)\] (?P<title>.+)$"
)


def _is_valid_agent(name: str) -> bool:
    """Acepta raices (David/Claude/Copilot/Codex) y subagentes `Root/Sub`."""
    if name in VALID_AGENTS:
        return True
    return bool(_SUBAGENT_RE.match(name))


@dataclass
class Entry:
    timestamp: str
    agent: str
    area: str
    title: str
    status: str = ""
    chat: str = ""
    commits: str = ""
    refs: str = ""
    sprint: str = ""
    summary: str = ""
    raw: str = ""


def _now_utc_iso_minutes() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _today_chat_path() -> str:
    day = datetime.now(timezone.utc).date().isoformat()
    return f"chats/chat_{day}.md"


def append_entry(
    agent: str,
    area: str,
    status: str,
    title: str,
    summary: str,
    commits: str = "",
    refs: str = "",
    chat: str = "",
    sprint: str = "",
) -> str:
    if not _is_valid_agent(agent):
        raise SystemExit(
            f"Agente invalido: {agent}. Validos: {sorted(VALID_AGENTS)} o subagente `Root/Sub` "
            f"(Root in {sorted(ROOT_AGENTS)}, Sub: letras/digitos/_/-)."
        )
    if status not in VALID_STATUSES:
        raise SystemExit(f"Estado invalido: {status}. Validos: {sorted(VALID_STATUSES)}")
    if area not in VALID_AREAS:
        raise SystemExit(f"Area invalida: {area}. Validas: {sorted(VALID_AREAS)}")
    title = title.strip()
    summary = summary.strip()
    if not title:
        raise SystemExit("Titulo vacio.")
    if not summary:
        raise SystemExit("Resumen vacio.")

    chat = chat or _today_chat_path()
    ts = _now_utc_iso_minutes()

    lines = [
        f"## {ts} \u2014 {agent} \u2014 [{area}] {title}",
        f"Estado: {status}",
        f"Chat: {chat}",
    ]
    if sprint:
        lines.append(f"Sprint: {sprint}")
    if commits:
        lines.append(f"Commits: {commits}")
    if refs:
        lines.append(f"Refs: {refs}")
    lines.append(f"Resumen: {summary}")
    entry = "\n".join(lines) + "\n"

    DEVLOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DEVLOG_PATH.exists():
        raise SystemExit(f"No existe {DEVLOG_PATH}. Crea el fichero base antes de append.")

    existing = DEVLOG_PATH.read_text(encoding="utf-8")
    separator = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    with DEVLOG_PATH.open("a", encoding="utf-8", newline="") as f:
        f.write(f"{separator}{entry}")
    return ts


def _parse_entries(text: str) -> list[Entry]:
    entries: list[Entry] = []
    current: Entry | None = None
    buf: list[str] = []

    for line in text.splitlines():
        m = ENTRY_HEADER_RE.match(line)
        if m:
            if current is not None:
                current.raw = "\n".join(buf)
                entries.append(current)
            current = Entry(
                timestamp=m.group("ts"),
                agent=m.group("agent"),
                area=m.group("area"),
                title=m.group("title"),
            )
            buf = [line]
            continue
        if current is None:
            continue
        buf.append(line)
        if line.startswith("Estado:"):
            current.status = line.split(":", 1)[1].strip()
        elif line.startswith("Chat:"):
            current.chat = line.split(":", 1)[1].strip()
        elif line.startswith("Commits:"):
            current.commits = line.split(":", 1)[1].strip()
        elif line.startswith("Refs:"):
            current.refs = line.split(":", 1)[1].strip()
        elif line.startswith("Sprint:"):
            current.sprint = line.split(":", 1)[1].strip()
        elif line.startswith("Resumen:"):
            current.summary = line.split(":", 1)[1].strip()

    if current is not None:
        current.raw = "\n".join(buf)
        entries.append(current)
    return entries


def view_entries(
    area: str | None = None,
    agent: str | None = None,
    status: str | None = None,
    limit: int = 20,
) -> str:
    if not DEVLOG_PATH.exists():
        return f"(no existe {DEVLOG_PATH})"
    text = DEVLOG_PATH.read_text(encoding="utf-8")
    entries = _parse_entries(text)

    if area:
        entries = [e for e in entries if e.area == area]
    if agent:
        entries = [e for e in entries if e.agent == agent]
    if status:
        entries = [e for e in entries if e.status == status]

    if limit > 0:
        entries = entries[-limit:]

    if not entries:
        return "(sin entradas que coincidan)"
    return "\n\n".join(e.raw for e in entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def _agent_arg(value: str) -> str:
        if not _is_valid_agent(value):
            raise argparse.ArgumentTypeError(
                f"Agente invalido: {value}. Usa {sorted(VALID_AGENTS)} o `Root/Sub` "
                f"(Root in {sorted(ROOT_AGENTS)})."
            )
        return value

    ap_append = sub.add_parser("append", help="Anadir entrada al devlog")
    ap_append.add_argument(
        "--agent", required=True, type=_agent_arg,
        help="David/Claude/Copilot/Codex o subagente `Root/Sub` (p.ej. Claude/KIT)",
    )
    ap_append.add_argument("--area", required=True, choices=sorted(VALID_AREAS))
    ap_append.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    ap_append.add_argument("--title", required=True)
    ap_append.add_argument("--summary", required=True)
    ap_append.add_argument("--commits", default="")
    ap_append.add_argument("--refs", default="")
    ap_append.add_argument("--sprint", default="", help="Nombre del sprint activo (cruce con artifacts/sprints/)")
    ap_append.add_argument("--chat", default="", help="Ruta al chat; por defecto chats/chat_HOY.md")

    ap_view = sub.add_parser("view", help="Consultar devlog")
    ap_view.add_argument("--area", choices=sorted(VALID_AREAS))
    ap_view.add_argument(
        "--agent", type=_agent_arg,
        help="Filtra por agente. Acepta raiz o `Root/Sub`.",
    )
    ap_view.add_argument("--status", choices=sorted(VALID_STATUSES))
    ap_view.add_argument("--limit", type=int, default=20, help="0 = sin limite")

    args = parser.parse_args()

    if args.cmd == "append":
        ts = append_entry(
            agent=args.agent,
            area=args.area,
            status=args.status,
            title=args.title,
            summary=args.summary,
            commits=args.commits,
            refs=args.refs,
            sprint=args.sprint,
            chat=args.chat,
        )
        print(f"DevLog entry added @ {ts} [{args.area}] {args.title}")
        return 0

    if args.cmd == "view":
        out = view_entries(area=args.area, agent=args.agent, status=args.status, limit=args.limit)
        print(out)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
