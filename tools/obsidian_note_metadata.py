"""Helpers para mapear properties/frontmatter de notas Obsidian."""

from __future__ import annotations

from typing import Any


FIELD_ALIASES = {
    "tipo": ["tipo", "type"],
    "estado": ["estado", "status", "estado-nota"],
    "proyecto": ["proyecto", "project"],
    "tarea": ["tarea", "task"],
    "tags": ["tags", "tag"],
    "personas": ["personas", "people", "persons"],
    "fuente": ["fuente", "source"],
    "alias": ["aliases", "alias"],
}


def _first(frontmatter: dict, key: str) -> Any:
    lower_map = {str(k).lower(): v for k, v in frontmatter.items()}
    for alias in FIELD_ALIASES[key]:
        if alias in lower_map:
            return lower_map[alias]
    return None


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip().lstrip("#") for item in value if str(item).strip()]
    raw = str(value).strip()
    if not raw:
        return []
    if "," in raw:
        return [item.strip().lstrip("#") for item in raw.split(",") if item.strip()]
    return [raw.lstrip("#")]


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def note_metadata_from_frontmatter(frontmatter: dict) -> dict[str, str | list[str]]:
    return {
        "tipo": as_text(_first(frontmatter, "tipo")),
        "estado": as_text(_first(frontmatter, "estado")),
        "proyecto": as_text(_first(frontmatter, "proyecto")),
        "tarea": as_text(_first(frontmatter, "tarea")),
        "tags": as_list(_first(frontmatter, "tags")),
        "personas": as_list(_first(frontmatter, "personas")),
        "fuente": as_text(_first(frontmatter, "fuente")),
        "alias": as_text(_first(frontmatter, "alias")),
    }


def route_metadata_from_relative_path(rel_path: str) -> dict[str, str]:
    """Deriva metadata ABPC desde una ruta relativa al vault Alpha."""
    parts = [part for part in rel_path.replace("\\", "/").split("/") if part]
    note = parts[-1] if parts else ""
    note_stem = note[:-3] if note.lower().endswith(".md") else note
    metadata = {
        "area": "",
        "bloque": "",
        "contexto": "",
        "proyecto": "",
        "tarea": "",
        "nota": note_stem,
        "nivel": "nota" if note.lower().endswith(".md") else "",
    }
    for part in parts:
        if part.startswith("A") and not metadata["area"]:
            metadata["area"] = part
        elif part.startswith("B") and not metadata["bloque"]:
            metadata["bloque"] = part
        elif part.startswith("C") and not metadata["contexto"]:
            metadata["contexto"] = part
        elif part.startswith("P") and not metadata["proyecto"]:
            metadata["proyecto"] = part
        elif part.startswith("T") and not metadata["tarea"]:
            metadata["tarea"] = part
    if not metadata["nivel"]:
        for key in ["tarea", "proyecto", "contexto", "bloque", "area"]:
            if metadata[key]:
                metadata["nivel"] = key
                break
    return metadata


def rich_text(value: str) -> dict:
    return {"rich_text": [{"text": {"content": value[:2000]}}]}


def select_prop(value: str) -> dict:
    return {"select": {"name": value[:100]}}


def multi_select_prop(values: list[str]) -> dict:
    return {"multi_select": [{"name": value[:100]} for value in values[:25] if value]}


def obsidian_db_metadata_props(metadata: dict, existing_props: set[str]) -> dict:
    props = {}
    if metadata.get("tipo"):
        props["Tipo"] = select_prop(str(metadata["tipo"]))
    if metadata.get("estado") and "Estado" in existing_props:
        props["Estado"] = select_prop(str(metadata["estado"]))
    if metadata.get("tags") and "Tags" in existing_props:
        props["Tags"] = multi_select_prop(metadata["tags"])
    if metadata.get("personas") and "Personas" in existing_props:
        props["Personas"] = multi_select_prop(metadata["personas"])
    for meta_key, prop_name in [
        ("fuente", "Fuente"),
        ("proyecto", "Proyecto"),
        ("tarea", "Tarea"),
        ("alias", "Alias"),
    ]:
        value = str(metadata.get(meta_key) or "").strip()
        if value and prop_name in existing_props:
            props[prop_name] = rich_text(value)
    return props


def obsidian_db_route_props(route_metadata: dict[str, str], existing_props: set[str]) -> dict:
    props = {}
    mappings = [
        ("area", "Ruta Area"),
        ("bloque", "Ruta Bloque"),
        ("contexto", "Ruta Contexto"),
        ("proyecto", "Ruta Proyecto"),
        ("tarea", "Ruta Tarea"),
        ("nota", "Ruta Nota"),
        ("nivel", "Ruta Nivel"),
    ]
    for meta_key, prop_name in mappings:
        value = str(route_metadata.get(meta_key) or "").strip()
        if value and prop_name in existing_props:
            props[prop_name] = rich_text(value)
    return props


def inx_note_metadata_props(source_props: dict, extract_value, existing_props: set[str]) -> dict:
    props = {}
    mappings = [
        ("Estado", "Nota Estado", "select"),
        ("Tags", "Nota Tags", "multi_select"),
        ("Personas", "Nota Personas", "multi_select"),
        ("Fuente", "Nota Fuente", "rich_text"),
        ("Proyecto", "Nota Proyecto", "rich_text"),
        ("Tarea", "Nota Tarea", "rich_text"),
        ("Alias", "Nota Alias", "rich_text"),
        ("Tipo", "Nota Tipo", "select"),
    ]
    for source_name, target_name, target_type in mappings:
        if target_name not in existing_props:
            continue
        value = extract_value(source_props.get(source_name, {}))
        if not value:
            continue
        if target_type == "select":
            props[target_name] = select_prop(value)
        elif target_type == "multi_select":
            props[target_name] = multi_select_prop(as_list(value))
        else:
            props[target_name] = rich_text(value)
    return props


def inx_note_route_props(source_props: dict, extract_value, existing_props: set[str]) -> dict:
    props = {}
    mappings = [
        ("Ruta Area", "Obsidian Area"),
        ("Ruta Bloque", "Obsidian Bloque"),
        ("Ruta Contexto", "Obsidian Contexto"),
        ("Ruta Proyecto", "Obsidian Proyecto"),
        ("Ruta Tarea", "Obsidian Tarea"),
        ("Ruta Nota", "Obsidian Nota"),
        ("Ruta Nivel", "Obsidian Nivel"),
    ]
    for source_name, target_name in mappings:
        if target_name not in existing_props:
            continue
        value = extract_value(source_props.get(source_name, {}))
        if value:
            props[target_name] = rich_text(value)
    return props
