"""
Wrappers para la API de Notion.
Soporta la versión 2025-09-03 con multi-source databases.
Documentación: https://developers.notion.com/reference
"""

import os
import requests
import re
from pathlib import Path

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"  # versión estable documentada
NOTION_VERSION_DATA_SOURCES = "2026-03-11"
NOTION_ID_RE = re.compile(r"^[0-9a-fA-F]{32}$")


def _headers(version: str | None = None) -> dict:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": version or NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _latest_headers() -> dict:
    return _headers(NOTION_VERSION_DATA_SOURCES)


def _http_timeout_seconds() -> float:
    """
    Timeout de red para requests a Notion.

    Sin timeout, algunos comandos pueden quedar aparentemente colgados si hay
    problemas de red/proxy o un request no responde (por ejemplo sync INX).
    """
    raw = (os.getenv("NOTION_HTTP_TIMEOUT") or "").strip()
    if not raw:
        return 60.0
    try:
        val = float(raw)
        return val if val > 0 else 60.0
    except Exception:
        return 60.0


def normalize_notion_id(raw_id: str) -> str:
    """Normaliza IDs de Notion a formato UUID con guiones cuando aplica."""
    if not raw_id:
        return raw_id
    raw_id = raw_id.strip()
    compact = raw_id.replace("-", "")
    if NOTION_ID_RE.fullmatch(compact):
        return f"{compact[:8]}-{compact[8:12]}-{compact[12:16]}-{compact[16:20]}-{compact[20:]}"
    return raw_id


# ─── BÚSQUEDA ─────────────────────────────────────────────────────────────────

def search_all(query: str = "") -> list[dict]:
    """Busca todos los objetos accesibles (páginas, databases, data_sources)."""
    data = {"query": query}
    return _post_paginated(f"{BASE_URL}/search", data)


def get_databases() -> list[dict]:
    """Obtiene bases de datos y data_sources accesibles."""
    results = search_all()
    out = []
    for r in results:
        obj_type = r.get("object", "")
        if obj_type in ("database", "data_source"):
            out.append({
                "id": r["id"],
                "title": _extract_title(r),
                "url": r.get("url", ""),
                "object": obj_type,
            })
    return out


def get_data_sources() -> list[dict]:
    """Obtiene solo data_sources accesibles."""
    results = search_all()
    return [
        {
            "id": r["id"],
            "title": _extract_title(r),
            "url": r.get("url", ""),
            "object": "data_source",
        }
        for r in results if r.get("object") == "data_source"
    ]


def get_pages() -> list[dict]:
    """Obtiene todas las páginas accesibles."""
    results = search_all()
    return [
        {
            "id": r["id"],
            "title": _extract_title(r),
            "url": r.get("url", ""),
            "parent": r.get("parent", {}),
        }
        for r in results if r.get("object") == "page"
    ]


# ─── BASE DE DATOS Y DATA SOURCES ─────────────────────────────────────────────

def get_database_info(database_id: str, object_type: str = "database") -> dict:
    """
    Obtiene info de una base de datos o data source.
    object_type: 'database' | 'data_source'
    Prueba ambos endpoints si el primero falla.
    """
    # Intentar con el endpoint correspondiente al tipo
    database_id = normalize_notion_id(database_id)
    endpoints = []
    if object_type == "data_source":
        endpoints = [f"{BASE_URL}/data_sources/{database_id}", f"{BASE_URL}/databases/{database_id}"]
    else:
        endpoints = [f"{BASE_URL}/databases/{database_id}", f"{BASE_URL}/data_sources/{database_id}"]

    db = None
    for endpoint in endpoints:
        try:
            resp = requests.get(
                endpoint,
                headers=_latest_headers() if "/data_sources/" in endpoint else _headers(),
            )
            if resp.status_code == 200:
                db = resp.json()
                break
        except Exception:
            continue

    if not db:
        return {"id": database_id, "title": "(no accesible)", "properties": [], "data_sources": []}

    property_types: dict[str, str] = {}
    raw_props = db.get("properties", {}) if isinstance(db.get("properties", {}), dict) else {}
    for name, meta in raw_props.items():
        if isinstance(meta, dict) and isinstance(meta.get("type"), str):
            property_types[name] = meta["type"]

    # Extraer data sources si existen (multi-source)
    data_sources = []
    for ds in db.get("data_sources", []):
        data_sources.append({
            "id": ds.get("id", ""),
            "title": _extract_title(ds) or ds.get("id", ""),
            "properties": list(ds.get("properties", {}).keys()),
        })

    return {
        "id": db["id"],
        "title": _extract_title(db),
        "properties": list(db.get("properties", {}).keys()),
        "property_types": property_types,
        "data_sources": data_sources,
        "raw": db,
    }


def get_data_source_schema(data_source_id: str) -> dict:
    """Obtiene el schema de un data source o database legacy.

    Prueba primero el endpoint `/data_sources/{id}` y, si Notion responde 400/404
    (ID de database legacy), cae a `/databases/{id}`. Devuelve el mismo shape
    en ambos casos: {id, title, properties: list[str], property_types: dict[str,str]}.
    """
    normalized_id = normalize_notion_id(data_source_id)
    payload = None

    try:
        resolved = resolve_data_source_id(normalized_id)
        resp = requests.get(f"{BASE_URL}/data_sources/{resolved}", headers=_latest_headers())
        resp.raise_for_status()
        payload = resp.json()
    except RuntimeError:
        resp = requests.get(f"{BASE_URL}/databases/{normalized_id}", headers=_headers())
        resp.raise_for_status()
        payload = resp.json()

    raw_props = payload.get("properties", {}) if isinstance(payload.get("properties", {}), dict) else {}
    property_types = {
        name: meta["type"]
        for name, meta in raw_props.items()
        if isinstance(meta, dict) and isinstance(meta.get("type"), str)
    }
    return {
        "id": payload.get("id", normalized_id),
        "title": _extract_title(payload),
        "properties": list(raw_props.keys()),
        "property_types": property_types,
    }


def query_database(database_id: str, filter_obj: dict = None, sorts: list = None) -> list[dict]:
    """Consulta una base de datos (endpoint legacy, funciona con bases simples)."""
    database_id = normalize_notion_id(database_id)
    data = {}
    if filter_obj:
        data["filter"] = filter_obj
    if sorts:
        data["sorts"] = sorts
    return _post_paginated(f"{BASE_URL}/databases/{database_id}/query", data)


def query_data_source(data_source_id: str, filter_obj: dict = None, sorts: list = None) -> list[dict]:
    """
    Consulta un data source específico (API 2025-09-03).
    Si el ID no corresponde a un data source accesible, prueba como database legacy.
    """
    data = {}
    if filter_obj:
        data["filter"] = filter_obj
    if sorts:
        data["sorts"] = sorts

    normalized_id = normalize_notion_id(data_source_id)
    try:
        resolved_data_source_id = resolve_data_source_id(normalized_id)
        try:
            return _post_paginated(
                f"{BASE_URL}/data_sources/{resolved_data_source_id}/query",
                data,
                headers=_latest_headers(),
            )
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status not in (400, 404):
                raise
            return query_database(normalized_id, filter_obj=filter_obj, sorts=sorts)
    except RuntimeError:
        return query_database(normalized_id, filter_obj=filter_obj, sorts=sorts)


# ─── BASES DE DATOS ───────────────────────────────────────────────────────────

def create_database(parent_page_id: str, title: str, properties: dict) -> dict:
    """
    Crea una base de datos en Notion como hija de una página.
    properties: dict con el schema de la base, ej:
        {"Nombre": {"title": {}}, "URL": {"url": {}}, ...}
    """
    data = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties,
    }
    resp = requests.post(f"{BASE_URL}/databases", headers=_headers(), json=data)
    resp.raise_for_status()
    return resp.json()


def update_database_properties(database_id: str, properties: dict) -> dict:
    """
    Añade/actualiza propiedades del schema de una base de datos o data source.
    Intenta primero como data_source y luego como database legacy.
    """
    normalized_id = normalize_notion_id(database_id)
    try:
        resolved_data_source_id = resolve_data_source_id(normalized_id)
        resp = requests.patch(
            f"{BASE_URL}/data_sources/{resolved_data_source_id}",
            headers=_latest_headers(),
            json={"properties": properties},
        )
        resp.raise_for_status()
        return resp.json()
    except RuntimeError:
        resp = requests.patch(
            f"{BASE_URL}/databases/{normalized_id}",
            headers=_headers(),
            json={"properties": properties},
        )
        resp.raise_for_status()
        return resp.json()

def add_page_to_database(database_id: str, properties: dict) -> dict:
    """Añade una fila a una base de datos existente."""
    database_id = normalize_notion_id(database_id)
    data = {
        "parent": {"database_id": database_id},
        "properties": properties,
    }
    resp = requests.post(f"{BASE_URL}/pages", headers=_headers(), json=data)
    resp.raise_for_status()
    return resp.json()


# ─── PÁGINAS ──────────────────────────────────────────────────────────────────

def get_page(page_id: str) -> dict:
    """Obtiene una página por ID."""
    resp = requests.get(f"{BASE_URL}/pages/{page_id}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def create_page(parent_id: str, title: str, properties: dict = None,
                is_database: bool = False, is_data_source: bool = False) -> dict:
    """
    Crea una página en Notion.
    - is_data_source=True: parent es un data_source_id (multi-source)
    - is_database=True: parent es un database_id (base simple)
    - ambos False: parent es una página
    """
    props = properties or {}
    # Buscar si ya existe alguna propiedad de tipo title.
    has_title_prop = any(
        isinstance(prop, dict) and "title" in prop
        for prop in props.values()
    )
    if not has_title_prop:
        props["Name"] = {"title": [{"text": {"content": title}}]}

    parents = []
    preferred_headers = _headers()
    if is_data_source:
        normalized_id = normalize_notion_id(parent_id)
        try:
            resolved_data_source_id = resolve_data_source_id(normalized_id)
            parents = [{"data_source_id": resolved_data_source_id}]
            preferred_headers = _latest_headers()
        except RuntimeError:
            parents = [{"database_id": normalized_id}]
    elif is_database:
        parents = [{"database_id": normalize_notion_id(parent_id)}]
    else:
        parents = [{"page_id": normalize_notion_id(parent_id)}]

    last_error = None
    for parent in parents:
        data = {"parent": parent, "properties": props}
        try:
            resp = requests.post(f"{BASE_URL}/pages", headers=preferred_headers, json=data)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as exc:
            last_error = exc
            status = exc.response.status_code if exc.response is not None else None
            if status not in (400, 404):
                raise

    if last_error:
        raise last_error
    raise RuntimeError("No se pudo crear la página en Notion.")


def update_page_properties(page_id: str, properties: dict) -> dict:
    """Actualiza propiedades de una página."""
    resp = requests.patch(
        f"{BASE_URL}/pages/{page_id}",
        headers=_headers(),
        json={"properties": properties}
    )
    resp.raise_for_status()
    return resp.json()


def archive_page(page_id: str) -> dict:
    """Archiva una página."""
    resp = requests.patch(
        f"{BASE_URL}/pages/{page_id}",
        headers=_headers(),
        json={"archived": True}
    )
    resp.raise_for_status()
    return resp.json()


# ─── BLOQUES ──────────────────────────────────────────────────────────────────

def get_page_content(page_id: str) -> list[dict]:
    """Obtiene los bloques de una página."""
    resp = requests.get(f"{BASE_URL}/blocks/{page_id}/children", headers=_headers())
    resp.raise_for_status()
    return resp.json().get("results", [])


def append_text_to_page(page_id: str, text: str) -> dict:
    """Añade un párrafo de texto al final de una página."""
    data = {
        "children": [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }]
    }
    resp = requests.patch(
        f"{BASE_URL}/blocks/{page_id}/children",
        headers=_headers(),
        json=data
    )
    resp.raise_for_status()
    return resp.json()


# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def _extract_title(obj: dict) -> str:
    """Extrae el título de un objeto Notion."""
    # Bases de datos / data sources: "title" en la raíz
    title_list = obj.get("title", [])
    if title_list and isinstance(title_list, list):
        texto = "".join(t.get("plain_text", "") for t in title_list)
        if texto.strip():
            return texto

    # Páginas: buscar propiedad de tipo "title"
    props = obj.get("properties", {})
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            rich = prop.get("title", [])
            texto = "".join(t.get("plain_text", "") for t in rich)
            if texto.strip():
                return texto

    return "(sin título)"


def _post_paginated(url: str, data: dict | None = None, headers: dict | None = None) -> list[dict]:
    """Recorre endpoints paginados de Notion hasta agotar resultados."""
    payload = dict(data or {})
    payload.setdefault("page_size", 100)

    results = []
    next_cursor = None

    while True:
        body = dict(payload)
        if next_cursor:
            body["start_cursor"] = next_cursor

        resp = requests.post(url, headers=headers or _headers(), json=body, timeout=_http_timeout_seconds())
        resp.raise_for_status()
        page = resp.json()

        results.extend(page.get("results", []))
        if not page.get("has_more"):
            break

        next_cursor = page.get("next_cursor")
        if not next_cursor:
            break

    return results


def _resolve_data_source_id(database_or_data_source_id: str) -> tuple[str | None, list[str]]:
    """Resuelve el data_source_id real y devuelve tambien candidatos detectados."""
    database_or_data_source_id = normalize_notion_id(database_or_data_source_id)
    candidates: list[str] = []
    try:
        resp = requests.get(
            f"{BASE_URL}/data_sources/{database_or_data_source_id}",
            headers=_latest_headers(),
            timeout=_http_timeout_seconds(),
        )
        if resp.status_code == 200:
            data_source_id = normalize_notion_id(resp.json().get("id", database_or_data_source_id))
            return data_source_id, [data_source_id]
    except Exception:
        pass

    try:
        resp = requests.get(
            f"{BASE_URL}/databases/{database_or_data_source_id}",
            headers=_latest_headers(),
            timeout=_http_timeout_seconds(),
        )
        if resp.status_code == 200:
            data = resp.json()
            data_sources = data.get("data_sources", [])
            if data_sources:
                candidates = [
                    normalize_notion_id(ds.get("id", ""))
                    for ds in data_sources
                    if ds.get("id")
                ]
                if len(candidates) == 1:
                    return candidates[0], candidates
                return None, candidates
    except Exception:
        pass

    return None, candidates


def resolve_data_source_id(database_or_data_source_id: str) -> str:
    """
    Resuelve de forma estricta el data_source_id moderno a partir de un data_source_id
    o de un database_id legacy.
    """
    normalized_id = normalize_notion_id(database_or_data_source_id)
    resolved_id, candidates = _resolve_data_source_id(normalized_id)
    if resolved_id:
        return resolved_id
    if candidates:
        joined = ", ".join(candidates)
        raise RuntimeError(
            f"{normalized_id} expone multiples data_sources y hace falta elegir uno explicitamente: {joined}"
        )
    raise RuntimeError(
        f"No se pudo resolver un data_source_id moderno a partir de {normalized_id}. "
        "Evito caer en /databases/{id}/query porque puede truncar resultados en bases legacy."
    )


def extract_property_value(prop: dict) -> str:
    """Extrae el valor legible de una propiedad."""
    ptype = prop.get("type", "")

    if ptype == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title", []))
    elif ptype == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", []))
    elif ptype == "select":
        sel = prop.get("select")
        return sel["name"] if sel else ""
    elif ptype == "multi_select":
        return ", ".join(s["name"] for s in prop.get("multi_select", []))
    elif ptype == "date":
        d = prop.get("date")
        return d["start"] if d else ""
    elif ptype == "checkbox":
        return "✓" if prop.get("checkbox") else "✗"
    elif ptype == "number":
        n = prop.get("number")
        return str(n) if n is not None else ""
    elif ptype == "url":
        return prop.get("url", "") or ""
    elif ptype == "status":
        s = prop.get("status")
        return s["name"] if s else ""
    else:
        return str(prop.get(ptype, ""))
