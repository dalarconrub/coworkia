from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


MESSAGE_RE = re.compile(r"^\*\*(?P<actor>.+?):\*\*\s?(?P<body>.*)$")
DIRECTED_RE = re.compile(r"^(?P<name>[^\[]+)\[@(?P<target>[^\]]+)\]$")
MENTION_RE = re.compile(r"@(?P<agent>Copilot|Claude|Codex)\b")
MODE_RE = re.compile(r"(PROPUESTA|VOTO|EVALUACIÓN|EVAL|SÍNTESIS|CREATIVIDAD|CERRADO)\s*#?(?P<num>\d+)?")
MEMORY_LINE_RE = re.compile(r"^(MEMORIA|BLOQUEO|SIGUIENTE):\s*(?P<value>.+)$", re.MULTILINE)


@dataclass
class ChatMessage:
    index: int
    actor: str
    actor_type: str
    target: str | None
    body: str
    mentions: list[str] = field(default_factory=list)
    mode: str | None = None
    mode_number: int | None = None


@dataclass
class DecisionLog:
    number: int
    mode: str
    opened_by: str | None = None
    status: str = "open"
    closed_by: str | None = None
    last_message_index: int | None = None
    participants: list[str] = field(default_factory=list)
    summary: str | None = None


@dataclass
class AgentState:
    name: str
    last_message_index: int | None = None
    last_direct_mention_index: int | None = None
    pending_mentions: list[int] = field(default_factory=list)
    pending_decisions: list[int] = field(default_factory=list)


@dataclass
class MemoryRecord:
    kind: str
    actor: str
    message_index: int
    value: str


@dataclass
class ChatMemorySnapshot:
    generated_at: str
    source_path: str
    message_count: int
    last_actor: str | None
    decisions_open: list[DecisionLog]
    decisions_all: list[DecisionLog]
    agent_states: list[AgentState]
    memory_records: list[MemoryRecord]
    messages: list[ChatMessage]


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _read_text_fallback(path: Path) -> str:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="latin-1", errors="replace")


def _sanitize_text(text: str) -> str:
    return "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)


def parse_chat_messages(chat_text: str) -> list[ChatMessage]:
    lines = _sanitize_text(chat_text).splitlines()
    messages: list[ChatMessage] = []
    current_actor: str | None = None
    current_body: list[str] = []

    def flush() -> None:
        nonlocal current_actor, current_body
        if current_actor is None:
            return
        raw_actor = current_actor.strip()
        body = "\n".join(current_body).strip()
        actor_name = raw_actor
        actor_type = "agent"
        target = None

        directed_match = DIRECTED_RE.match(raw_actor.replace(" ", ""))
        if directed_match:
            actor_name = directed_match.group("name").strip()
            target = directed_match.group("target").strip()
            actor_type = "director"
        elif raw_actor == "David":
            actor_type = "director"

        mentions = sorted(set(MENTION_RE.findall(body)))
        mode = None
        mode_number = None
        mode_match = MODE_RE.search(body)
        if mode_match:
            mode = mode_match.group(1)
            if mode_match.group("num"):
                mode_number = int(mode_match.group("num"))

        messages.append(
            ChatMessage(
                index=len(messages) + 1,
                actor=actor_name,
                actor_type=actor_type,
                target=target,
                body=body,
                mentions=mentions,
                mode=mode,
                mode_number=mode_number,
            )
        )
        current_actor = None
        current_body = []

    for line in lines:
        match = MESSAGE_RE.match(line)
        if match:
            flush()
            current_actor = match.group("actor")
            current_body = [match.group("body")]
        elif current_actor is not None:
            current_body.append(line)
    flush()
    return messages


def build_decision_logs(messages: list[ChatMessage]) -> list[DecisionLog]:
    decisions: dict[int, DecisionLog] = {}
    for message in messages:
        if message.mode_number is None or message.mode is None:
            continue
        number = message.mode_number
        if number not in decisions:
            decisions[number] = DecisionLog(number=number, mode=message.mode)
        entry = decisions[number]
        if entry.opened_by is None:
            entry.opened_by = message.actor
        entry.mode = entry.mode if entry.mode not in {"EVAL", "SÍNTESIS"} else message.mode
        entry.last_message_index = message.index
        if message.actor not in entry.participants:
            entry.participants.append(message.actor)
        for mention in message.mentions:
            if mention not in entry.participants:
                entry.participants.append(mention)
        summary = " ".join(message.body.split())
        if message.mode == "CERRADO":
            entry.status = "closed"
            entry.closed_by = message.actor
            entry.summary = summary
        elif entry.summary is None:
            entry.summary = summary
    return [decisions[key] for key in sorted(decisions)]


def build_agent_states(messages: list[ChatMessage], decisions: list[DecisionLog]) -> list[AgentState]:
    agents = {name: AgentState(name=name) for name in ("Copilot", "Claude", "Codex")}
    open_decisions = [decision.number for decision in decisions if decision.status != "closed"]

    for message in messages:
        if message.actor in agents:
            agents[message.actor].last_message_index = message.index
        if message.actor == "David" and message.target in agents:
            agents[message.target].last_direct_mention_index = message.index
            agents[message.target].pending_mentions.append(message.index)
        for mention in message.mentions:
            if mention in agents and mention != message.actor:
                agents[mention].pending_mentions.append(message.index)

    for state in agents.values():
        responded_after = state.last_message_index or 0
        state.pending_mentions = [idx for idx in state.pending_mentions if idx > responded_after]
        state.pending_decisions = open_decisions[:]

    return list(agents.values())


def build_memory_records(messages: list[ChatMessage]) -> list[MemoryRecord]:
    records: list[MemoryRecord] = []
    for message in messages:
        for match in MEMORY_LINE_RE.finditer(message.body):
            records.append(
                MemoryRecord(
                    kind=match.group(1),
                    actor=message.actor,
                    message_index=message.index,
                    value=match.group("value").strip(),
                )
            )
    return records


def build_chat_memory(chat_path: str = "chat.md") -> ChatMemorySnapshot:
    source = Path(chat_path)
    messages = parse_chat_messages(_read_text_fallback(source))
    decisions = build_decision_logs(messages)
    states = build_agent_states(messages, decisions)
    memory_records = build_memory_records(messages)
    return ChatMemorySnapshot(
        generated_at=_utc_now_iso(),
        source_path=str(source),
        message_count=len(messages),
        last_actor=messages[-1].actor if messages else None,
        decisions_open=[decision for decision in decisions if decision.status != "closed"],
        decisions_all=decisions,
        agent_states=states,
        memory_records=memory_records,
        messages=messages,
    )


def render_chat_memory_markdown(snapshot: ChatMemorySnapshot) -> str:
    lines = [
        "# Chat Memory Snapshot",
        "",
        f"- Generated: `{snapshot.generated_at}`",
        f"- Source: `{snapshot.source_path}`",
        f"- Messages: `{snapshot.message_count}`",
        f"- Last actor: `{snapshot.last_actor or 'None'}`",
        "",
        "## Open Decisions",
        "",
    ]
    if not snapshot.decisions_open:
        lines.append("- None")
    else:
        for decision in snapshot.decisions_open:
            lines.append(
                f"- `#{decision.number}` `{decision.mode}` opened by `{decision.opened_by}` participants: {', '.join(decision.participants) or 'None'}"
            )

    lines.extend(["", "## Agent State", ""])
    for state in snapshot.agent_states:
        lines.append(f"- `{state.name}`")
        lines.append(f"  last_message_index: {state.last_message_index}")
        lines.append(f"  last_direct_mention_index: {state.last_direct_mention_index}")
        lines.append(f"  pending_mentions: {state.pending_mentions or '[]'}")
        lines.append(f"  pending_decisions: {state.pending_decisions or '[]'}")

    lines.extend(["", "## Structured Memory", ""])
    if not snapshot.memory_records:
        lines.append("- None")
    else:
        for record in snapshot.memory_records[-20:]:
            lines.append(f"- `{record.kind}` `{record.actor}` [{record.message_index}] {record.value}")

    lines.extend(["", "## Recent Messages", ""])
    for message in snapshot.messages[-10:]:
        body = " ".join(message.body.split())
        lines.append(f"- `{message.index}` `{message.actor}` -> {body[:160]}")
    lines.append("")
    return "\n".join(lines)


def write_chat_memory_artifacts(
    snapshot: ChatMemorySnapshot,
    output_dir: str = "artifacts/multiagent",
) -> dict[str, Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = target_dir / "chat_memory_snapshot.json"
    conversation_path = target_dir / "conversation_records.jsonl"
    decisions_path = target_dir / "decision_log.json"
    agent_state_path = target_dir / "agent_state.json"
    memory_records_path = target_dir / "memory_records.json"
    markdown_path = target_dir / "chat_memory.md"

    snapshot_path.write_text(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2), encoding="utf-8")
    decisions_path.write_text(
        json.dumps([asdict(item) for item in snapshot.decisions_all], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    agent_state_path.write_text(
        json.dumps([asdict(item) for item in snapshot.agent_states], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    memory_records_path.write_text(
        json.dumps([asdict(item) for item in snapshot.memory_records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with conversation_path.open("w", encoding="utf-8") as fh:
        for message in snapshot.messages:
            fh.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
    markdown_path.write_text(render_chat_memory_markdown(snapshot), encoding="utf-8")

    return {
        "snapshot": snapshot_path,
        "conversation": conversation_path,
        "decisions": decisions_path,
        "agent_state": agent_state_path,
        "memory_records": memory_records_path,
        "markdown": markdown_path,
    }
