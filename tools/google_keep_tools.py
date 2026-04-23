"""
Utilidades para leer exports de Google Keep generados por Google Takeout.

El parser no depende de una API online: recorre un directorio local y detecta
ficheros JSON con shape compatible con notas exportadas por Keep.
"""

from __future__ import annotations

import json
from pathlib import Path


def _as_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _timestamp_usec_to_iso(value) -> str:
    raw = _as_text(value)
    if not raw:
        return ""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return ""
    try:
        usec = int(digits)
    except ValueError:
        return ""
    # Keep Takeout suele exportar microsegundos UNIX.
    seconds = usec / 1_000_000
    from datetime import datetime, timezone

    return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()


def _normalize_labels(labels) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    if not isinstance(labels, list):
        return out
    for label in labels:
        if isinstance(label, dict):
            name = _as_text(label.get("name"))
        else:
            name = _as_text(label)
        if not name:
            continue
        key = name.casefold()
        if key in seen:
            continue
        out.append(name[:100])
        seen.add(key)
    return out


def _extract_text_content(payload: dict) -> str:
    value = payload.get("textContent")
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return _as_text(value.get("text"))
    return ""


def _extract_list_content(payload: dict) -> tuple[str, list[str]]:
    raw_items = payload.get("listContent")
    if isinstance(raw_items, dict):
        raw_items = raw_items.get("listItems", [])

    lines: list[str] = []
    unchecked: list[str] = []
    checked: list[str] = []

    if not isinstance(raw_items, list):
        return "", []

    for item in raw_items:
        if not isinstance(item, dict):
            continue
        text = _as_text(item.get("text") or (item.get("text", {}) or {}).get("text"))
        if not text:
            continue
        is_checked = bool(item.get("isChecked") or item.get("checked"))
        marker = "[x]" if is_checked else "[ ]"
        lines.append(f"{marker} {text}")
        if is_checked:
            checked.append(text)
        else:
            unchecked.append(text)

    body = "\n".join(lines).strip()
    return body, unchecked + checked


def _extract_attachment_paths(payload: dict, note_path: Path) -> list[str]:
    attachments = payload.get("attachments", [])
    out: list[str] = []
    if not isinstance(attachments, list):
        return out
    for item in attachments:
        if not isinstance(item, dict):
            continue
        rel = _as_text(item.get("filePath"))
        if not rel:
            continue
        try:
            resolved = (note_path.parent / rel).resolve()
            out.append(str(resolved))
        except Exception:
            out.append(rel)
    return out


def _extract_title(payload: dict, body: str, stem: str) -> str:
    title = _as_text(payload.get("title"))
    if title:
        return title
    first_line = next((line.strip() for line in body.splitlines() if line.strip()), "")
    if first_line:
        return first_line[:120]
    return stem.replace("_", " ").strip() or "Nota Keep sin titulo"


def _is_keep_note_payload(payload: dict) -> bool:
    return any(
        key in payload
        for key in (
            "textContent",
            "listContent",
            "isArchived",
            "isPinned",
            "userEditedTimestampUsec",
            "createdTimestampUsec",
            "labels",
        )
    )


def _note_from_payload(path: Path, payload: dict) -> dict | None:
    text_body = _extract_text_content(payload)
    list_body, list_items = _extract_list_content(payload)
    body = text_body or list_body

    attachments = _extract_attachment_paths(payload, path)
    labels = _normalize_labels(payload.get("labels", []))
    color = _as_text(payload.get("color"))
    is_archived = bool(payload.get("isArchived") or payload.get("trashed"))
    is_pinned = bool(payload.get("isPinned"))

    meta_labels = list(labels)
    if color:
        meta_labels.append(f"KeepColor:{color[:80]}")
    if is_pinned:
        meta_labels.append("KeepPinned")
    if attachments:
        meta_labels.append("KeepAttachment")

    note_id = _as_text(payload.get("id")) or _as_text(payload.get("name")) or path.stem
    summary = body.strip()
    if len(summary) > 2000:
        summary = summary[:1997] + "..."

    extract_chunks: list[str] = []
    if list_items:
        extract_chunks.append("Checklist:\n" + "\n".join(f"- {item}" for item in list_items[:100]))
    if attachments:
        extract_chunks.append("Adjuntos:\n" + "\n".join(f"- {item}" for item in attachments[:25]))
    extracts = "\n\n".join(chunk for chunk in extract_chunks if chunk).strip()

    return {
        "keep_id": note_id[:500],
        "title": _extract_title(payload, body, path.stem)[:2000],
        "summary": summary,
        "extracts": extracts[:2000] if extracts else "",
        "labels": meta_labels[:25],
        "source_author": "Google Keep",
        "created_date": _timestamp_usec_to_iso(payload.get("createdTimestampUsec")),
        "updated_date": _timestamp_usec_to_iso(payload.get("userEditedTimestampUsec")),
        "archived": is_archived,
        "pinned": is_pinned,
        "body": body,
        "attachments": attachments,
        "path": str(path.resolve()),
    }


def load_keep_export(export_dir: str | Path) -> list[dict]:
    root = Path(export_dir).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"No existe la ruta de Google Keep: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"La ruta de Google Keep no es un directorio: {root}")

    notes: list[dict] = []
    for path in sorted(root.rglob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict) or not _is_keep_note_payload(payload):
            continue
        note = _note_from_payload(path, payload)
        if note:
            notes.append(note)
    return notes
