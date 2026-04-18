from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path


ROOT_AGENTS = ("Claude", "Copilot", "Codex")

MESSAGE_RE = re.compile(r"^\*\*(?P<actor>.+?):\*\*\s?(?P<body>.*)$")
DIRECTED_RE = re.compile(r"^(?P<name>[^\[]+)\[@(?P<target>[^\]]+)\]$")
# Acepta raiz (Claude/Copilot/Codex) y subagentes `Root/Sub` (Sub: letras, digitos, _, -).
MENTION_RE = re.compile(r"@(?P<agent>(?:Claude|Copilot|Codex)(?:/[A-Za-z0-9_\-]+)?)\b")
MODE_RE = re.compile(r"(PROPUESTA|VOTO|EVALUACIÓN|EVAL|SÍNTESIS|CREATIVIDAD|CERRADO)\s*#?(?P<num>\d+)?")
MEMORY_LINE_RE = re.compile(r"^(MEMORIA|BLOQUEO|SIGUIENTE):\s*(?P<value>.+)$", re.MULTILINE)


def _agent_root(name: str) -> str | None:
    """Devuelve la raiz si `name` es un agente (raiz o subagente), si no None."""
    if not name:
        return None
    head = name.split("/", 1)[0]
    return head if head in ROOT_AGENTS else None


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


def _read_text_strict(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(
            exc.encoding,
            exc.object,
            exc.start,
            exc.end,
            (
                f"{path} no es UTF-8 valido. "
                "Repara con `python tools/fix_chat_mojibake.py <ruta>` "
                "y asegura que toda escritura use encoding='utf-8'."
            ),
        ) from exc


def _sanitize_text(text: str) -> str:
    return "".join(ch for ch in text if ch in "\n\t" or ord(ch) >= 32)


CODE_FENCE_RE = re.compile(r"^\s*```")


def parse_chat_messages(chat_text: str) -> list[ChatMessage]:
    lines = _sanitize_text(chat_text).splitlines()
    messages: list[ChatMessage] = []
    current_actor: str | None = None
    current_body: list[str] = []
    in_code_block = False

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
        if CODE_FENCE_RE.match(line):
            in_code_block = not in_code_block
            if current_actor is not None:
                current_body.append(line)
            continue
        if in_code_block:
            if current_actor is not None:
                current_body.append(line)
            continue
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
    """Descubre agentes raiz y subagentes (`Root/Sub`) citados en el hilo.

    Un agente se registra si aparece como actor, como destino de `David [@X]`
    o como mencion `@X`, siempre que su raiz sea Claude/Copilot/Codex.
    Las raices se garantizan siempre presentes.
    """
    agents: dict[str, AgentState] = {name: AgentState(name=name) for name in ROOT_AGENTS}

    def ensure(name: str | None) -> AgentState | None:
        if not name or _agent_root(name) is None:
            return None
        if name not in agents:
            agents[name] = AgentState(name=name)
        return agents[name]

    for message in messages:
        ensure(message.actor)
        if message.actor_type == "director":
            ensure(message.target)
        for mention in message.mentions:
            ensure(mention)

    open_decisions = [decision.number for decision in decisions if decision.status != "closed"]

    for message in messages:
        actor_state = agents.get(message.actor)
        if actor_state is not None:
            actor_state.last_message_index = message.index
        if message.actor == "David":
            target_state = agents.get(message.target) if message.target else None
            if target_state is not None:
                target_state.last_direct_mention_index = message.index
                target_state.pending_mentions.append(message.index)
        for mention in message.mentions:
            mention_state = agents.get(mention)
            if mention_state is not None and mention != message.actor:
                mention_state.pending_mentions.append(message.index)

    for state in agents.values():
        responded_after = state.last_message_index or 0
        state.pending_mentions = [idx for idx in state.pending_mentions if idx > responded_after]
        state.pending_decisions = open_decisions[:]

    return sorted(agents.values(), key=lambda s: (s.name.count("/"), s.name))


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


def build_chat_memory(chat_path: str | Path | None = None) -> ChatMemorySnapshot:
    if chat_path is None:
        from tools.init_chat import ensure_today_chat

        source, _ = ensure_today_chat()
    else:
        source = Path(chat_path)
    messages = parse_chat_messages(_read_text_strict(source))
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


@dataclass
class ProjectMemoryEntry:
    kind: str
    actor: str
    value: str
    chat_date: str
    chat_path: str
    message_index: int


def build_project_memory_entries(chats_dir: str | Path = "chats") -> list[ProjectMemoryEntry]:
    """Agrega MEMORIA/BLOQUEO/SIGUIENTE de todos los chats en `chats/`.

    Dedup por (kind, value normalizado) conservando la aparicion mas reciente.
    """
    directory = Path(chats_dir)
    if not directory.exists():
        return []

    collected: list[ProjectMemoryEntry] = []
    for chat_path in sorted(directory.glob("chat_*.md")):
        stem = chat_path.stem
        chat_date = stem.replace("chat_", "")
        try:
            text = _read_text_strict(chat_path)
        except UnicodeDecodeError:
            continue
        messages = parse_chat_messages(text)
        records = build_memory_records(messages)
        for record in records:
            collected.append(
                ProjectMemoryEntry(
                    kind=record.kind,
                    actor=record.actor,
                    value=record.value,
                    chat_date=chat_date,
                    chat_path=str(chat_path.as_posix()),
                    message_index=record.message_index,
                )
            )

    seen: dict[tuple[str, str], ProjectMemoryEntry] = {}
    for entry in collected:
        key = (entry.kind, " ".join(entry.value.lower().split()))
        seen[key] = entry
    return sorted(seen.values(), key=lambda e: (e.kind, e.chat_date, e.message_index))


def render_project_memory_markdown(entries: list[ProjectMemoryEntry]) -> str:
    now = _utc_now_iso()
    lines = [
        "# Project Memory Snapshot",
        "",
        f"_Auto-generado por `python agents/orchestrator_agent.py sync-chat-memory` @ {now}. No editar a mano._",
        "",
        "Agregado de marcadores `MEMORIA:`, `BLOQUEO:` y `SIGUIENTE:` de todos los chats en `chats/`.",
        "Cada entrada enlaza al chat donde aparecio por ultima vez (dedup por contenido normalizado).",
        "",
    ]

    for kind, title in (("MEMORIA", "## MEMORIA (acuerdos duraderos)"),
                        ("BLOQUEO", "## BLOQUEO (impedimentos)"),
                        ("SIGUIENTE", "## SIGUIENTE (handoffs pendientes)")):
        subset = [e for e in entries if e.kind == kind]
        lines.append(title)
        lines.append("")
        if not subset:
            lines.append("- Ninguno.")
            lines.append("")
            continue
        for e in subset:
            lines.append(f"- **[{e.chat_date}]** `{e.actor}` \u2014 {e.value}")
            lines.append(f"  - origen: `{e.chat_path}` (msg #{e.message_index})")
        lines.append("")

    return "\n".join(lines)


def write_project_memory_snapshot(
    entries: list[ProjectMemoryEntry],
    output_path: str | Path = "memory/SNAPSHOT.md",
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_project_memory_markdown(entries), encoding="utf-8")
    return path


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
