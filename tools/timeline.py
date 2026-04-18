"""
Vista temporal agregada: une chat, devlog, INX y sprints en un fichero por dia.

Lee (no modifica) las fuentes canonicas y emite, para cada fecha pedida,
`artifacts/daily/YYYY-MM-DD.md` con:
  - Chat del dia + recuento de mensajes y decisiones cerradas.
  - Entradas del devlog cuyo timestamp cae en esa fecha.
  - INX runs de esa fecha (`artifacts/inx/inx-daily-YYYYMMDD-*.md`).
  - Sprints activos ese dia (segun `artifacts/sprints/*.json`, start <= D <= end).

Uso:
    python tools/timeline.py                      # hoy, escribe artifacts/daily/<hoy>.md
    python tools/timeline.py --date 2026-04-18
    python tools/timeline.py --from 2026-04-15 --to 2026-04-18
    python tools/timeline.py --days 7             # ultimos 7 dias incluyendo hoy
    python tools/timeline.py --date 2026-04-18 --stdout   # no escribe, imprime
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date as Date, datetime, timedelta, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

CHATS_DIR = _ROOT / "chats"
DEVLOG_PATH = _ROOT / "devlog" / "DEVLOG.md"
INX_DIR = _ROOT / "artifacts" / "inx"
SPRINTS_DIR = _ROOT / "artifacts" / "sprints"
DAILY_DIR = _ROOT / "artifacts" / "daily"

DEVLOG_HEADER_RE = re.compile(
    r"^## (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z) \u2014 (?P<agent>\w+) \u2014 \[(?P<area>\w+)\] (?P<title>.+)$"
)
INX_NAME_RE = re.compile(r"^inx-daily-(\d{8})-(\d{6})\.md$")


@dataclass
class DevlogEntryLite:
    timestamp: str
    agent: str
    area: str
    title: str
    status: str = ""
    sprint: str = ""
    refs: str = ""


@dataclass
class SprintLite:
    name: str
    start: str
    end: str
    status: str
    objective: str


@dataclass
class DailyBundle:
    day: str
    chat_path: Path | None
    chat_message_count: int
    chat_closed_decisions: list[tuple[int, str, str]] = field(default_factory=list)  # (number, actor, summary)
    devlog_entries: list[DevlogEntryLite] = field(default_factory=list)
    inx_runs: list[Path] = field(default_factory=list)
    active_sprints: list[SprintLite] = field(default_factory=list)


def _parse_devlog() -> list[DevlogEntryLite]:
    if not DEVLOG_PATH.exists():
        return []
    text = DEVLOG_PATH.read_text(encoding="utf-8")
    entries: list[DevlogEntryLite] = []
    current: DevlogEntryLite | None = None
    in_code_block = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        m = DEVLOG_HEADER_RE.match(line)
        if m:
            current = DevlogEntryLite(
                timestamp=m.group("ts"),
                agent=m.group("agent"),
                area=m.group("area"),
                title=m.group("title"),
            )
            entries.append(current)
            continue
        if current is None:
            continue
        if line.startswith("Estado:"):
            current.status = line.split(":", 1)[1].strip()
        elif line.startswith("Sprint:"):
            current.sprint = line.split(":", 1)[1].strip()
        elif line.startswith("Refs:"):
            current.refs = line.split(":", 1)[1].strip()
    return entries


def _load_sprints() -> list[SprintLite]:
    if not SPRINTS_DIR.exists():
        return []
    sprints: list[SprintLite] = []
    for path in sorted(SPRINTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        plan = data.get("plan") if isinstance(data, dict) else None
        if not plan:
            continue
        try:
            sprints.append(
                SprintLite(
                    name=plan.get("sprint_name", path.stem),
                    start=str(plan.get("start_date", "")),
                    end=str(plan.get("end_date", "")),
                    status=plan.get("status", ""),
                    objective=plan.get("objective", ""),
                )
            )
        except Exception:
            continue
    return sprints


def _chat_stats(day: str) -> tuple[Path | None, int, list[tuple[int, str, str]]]:
    chat_path = CHATS_DIR / f"chat_{day}.md"
    if not chat_path.exists():
        return None, 0, []
    try:
        from multiagents.chat_memory import build_decision_logs, parse_chat_messages
    except Exception:
        text = chat_path.read_text(encoding="utf-8")
        msgs = len(re.findall(r"^\*\*[^*]+:\*\*", text, re.MULTILINE))
        return chat_path, msgs, []
    text = chat_path.read_text(encoding="utf-8")
    messages = parse_chat_messages(text)
    decisions = build_decision_logs(messages)
    closed = [
        (d.number, d.closed_by or "", (d.summary or "")[:160])
        for d in decisions
        if d.status == "closed"
    ]
    return chat_path, len(messages), closed


def _inx_runs_for(day: str) -> list[Path]:
    if not INX_DIR.exists():
        return []
    compact = day.replace("-", "")
    runs: list[Path] = []
    for p in sorted(INX_DIR.iterdir()):
        m = INX_NAME_RE.match(p.name)
        if m and m.group(1) == compact:
            runs.append(p)
    return runs


def _active_sprints_on(day: str, sprints: list[SprintLite]) -> list[SprintLite]:
    try:
        d = Date.fromisoformat(day)
    except ValueError:
        return []
    active: list[SprintLite] = []
    for sp in sprints:
        try:
            start = Date.fromisoformat(sp.start[:10])
            end = Date.fromisoformat(sp.end[:10])
        except Exception:
            continue
        if start <= d <= end:
            active.append(sp)
    return active


def build_daily(day: str, devlog: list[DevlogEntryLite], sprints: list[SprintLite]) -> DailyBundle:
    chat_path, msg_count, closed = _chat_stats(day)
    day_prefix = day
    devlog_hits = [e for e in devlog if e.timestamp.startswith(day_prefix)]
    return DailyBundle(
        day=day,
        chat_path=chat_path,
        chat_message_count=msg_count,
        chat_closed_decisions=closed,
        devlog_entries=devlog_hits,
        inx_runs=_inx_runs_for(day),
        active_sprints=_active_sprints_on(day, sprints),
    )


def render_daily(bundle: DailyBundle) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    lines = [
        f"# Timeline \u2014 {bundle.day}",
        "",
        f"_Auto-generado por `python tools/timeline.py` @ {now}. Read-only: agrega chat + devlog + INX + sprints. No editar a mano._",
        "",
    ]

    lines.append("## Chat del dia")
    lines.append("")
    if bundle.chat_path is None:
        lines.append("- Sin chat para esta fecha.")
    else:
        rel = Path("..") / bundle.chat_path.relative_to(_ROOT)
        lines.append(
            f"- [{bundle.chat_path.name}]({rel.as_posix()}) \u2014 {bundle.chat_message_count} mensajes, "
            f"{len(bundle.chat_closed_decisions)} decisiones cerradas"
        )
    lines.append("")

    lines.append("## Decisiones cerradas")
    lines.append("")
    if not bundle.chat_closed_decisions:
        lines.append("- Ninguna.")
    else:
        for number, actor, summary in bundle.chat_closed_decisions:
            lines.append(f"- `#{number}` cerrada por `{actor}`: {summary}")
    lines.append("")

    lines.append("## Devlog (entradas de esta fecha)")
    lines.append("")
    if not bundle.devlog_entries:
        lines.append("- Ninguna.")
    else:
        for e in bundle.devlog_entries:
            time_part = e.timestamp[11:]
            sprint_part = f" · sprint=`{e.sprint}`" if e.sprint else ""
            refs_part = f" · refs=`{e.refs}`" if e.refs else ""
            lines.append(
                f"- `{time_part}` `{e.status}` `{e.agent}` [{e.area}] {e.title}{sprint_part}{refs_part}"
            )
    lines.append("")

    lines.append("## INX runs")
    lines.append("")
    if not bundle.inx_runs:
        lines.append("- Ninguno.")
    else:
        for p in bundle.inx_runs:
            rel = Path("..") / p.relative_to(_ROOT)
            lines.append(f"- [{p.name}]({rel.as_posix()})")
    lines.append("")

    lines.append("## Sprints activos")
    lines.append("")
    if not bundle.active_sprints:
        lines.append("- Ninguno.")
    else:
        for sp in bundle.active_sprints:
            lines.append(
                f"- `{sp.name}` ({sp.start} \u2192 {sp.end}) status=`{sp.status}` \u2014 {sp.objective}"
            )
    lines.append("")

    return "\n".join(lines)


def _resolve_days(args: argparse.Namespace) -> list[str]:
    today = Date.today()
    if args.days:
        return [(today - timedelta(days=i)).isoformat() for i in range(args.days - 1, -1, -1)]
    if args.date:
        Date.fromisoformat(args.date)
        return [args.date]
    if args.from_date or args.to_date:
        start = Date.fromisoformat(args.from_date) if args.from_date else today
        end = Date.fromisoformat(args.to_date) if args.to_date else today
        if end < start:
            raise SystemExit("--to debe ser posterior o igual a --from")
        days = []
        d = start
        while d <= end:
            days.append(d.isoformat())
            d += timedelta(days=1)
        return days
    return [today.isoformat()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=None, help="Fecha unica YYYY-MM-DD (por defecto hoy)")
    parser.add_argument("--from", dest="from_date", default=None)
    parser.add_argument("--to", dest="to_date", default=None)
    parser.add_argument("--days", type=int, default=0, help="Ultimos N dias incluyendo hoy")
    parser.add_argument("--stdout", action="store_true", help="No escribe, imprime al stdout")
    args = parser.parse_args()

    days = _resolve_days(args)
    devlog = _parse_devlog()
    sprints = _load_sprints()

    if not args.stdout:
        DAILY_DIR.mkdir(parents=True, exist_ok=True)

    for day in days:
        bundle = build_daily(day, devlog, sprints)
        rendered = render_daily(bundle)
        if args.stdout:
            print(rendered)
            print()
        else:
            out = DAILY_DIR / f"{day}.md"
            out.write_text(rendered, encoding="utf-8", newline="")
            print(f"escrito {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
