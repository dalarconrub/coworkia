"""
Wrappers para la API de Notion.
Soporta la versión 2025-09-03 con multi-source databases.
Documentación: https://developers.notion.com/reference
"""

import os
import requests
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
BASE_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"  # versión estable documentada


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


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
    endpoints = []
    if object_type == "data_source":
        endpoints = [f"{BASE_URL}/data_sources/{database_id}", f"{BASE_URL}/databases/{database_id}"]
    else:
        endpoints = [f"{BASE_URL}/databases/{database_id}", f"{BASE_URL}/data_sources/{database_id}"]

    db = None
    for endpoint in endpoints:
        try:
            resp = requests.get(endpoint, headers=_headers())
            if resp.status_code == 200:
                db = resp.json()
                break
        except Exception:
            continue

    if not db:
        return {"id": database_id, "title": "(no accesible)", "properties": [], "data_sources": []}

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
        "data_sources": data_sources,
        "raw": db,
    }


def get_data_source_schema(data_source_id: str) -> dict:
    """Obtiene el schema de un data source específico."""
    resp = requests.get(f"{BASE_URL}/data_sources/{data_source_id}", headers=_headers())
    resp.raise_for_status()
    ds = resp.json()
    return {
        "id": ds["id"],
        "title": _extract_title(ds),
        "properties": list(ds.get("properties", {}).keys()),
    }


def query_database(database_id: str, filter_obj: dict = None, sorts: list = None) -> list[dict]:
    """Consulta una base de datos (endpoint legacy, funciona con bases simples)."""
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

    last_error = None
    for url in (
        f"{BASE_URL}/data_sources/{data_source_id}/query",
        f"{BASE_URL}/databases/{data_source_id}/query",
    ):
        try:
            return _post_paginated(url, data)
        except requests.HTTPError as exc:
            last_error = exc
            status = exc.response.status_code if exc.response is not None else None
            if status not in (400, 404):
                raise

    if last_error:
        raise last_error
    return []


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


def add_page_to_database(database_id: str, properties: dict) -> dict:
    """Añade una fila a una base de datos existente."""
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
    if is_data_source:
        parents = [{"data_source_id": parent_id}, {"database_id": parent_id}]
    elif is_database:
        parents = [{"database_id": parent_id}]
    else:
        parents = [{"page_id": parent_id}]

    last_error = None
    for parent in parents:
        data = {"parent": parent, "properties": props}
        try:
            resp = requests.post(f"{BASE_URL}/pages", headers=_headers(), json=data)
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


def _post_paginated(url: str, data: dict | None = None) -> list[dict]:
    """Recorre endpoints paginados de Notion hasta agotar resultados."""
    payload = dict(data or {})
    payload.setdefault("page_size", 100)

    results = []
    next_cursor = None

    while True:
        body = dict(payload)
        if next_cursor:
            body["start_cursor"] = next_cursor

        resp = requests.post(url, headers=_headers(), json=body)
        resp.raise_for_status()
        page = resp.json()

        results.extend(page.get("results", []))
        if not page.get("has_more"):
            break

        next_cursor = page.get("next_cursor")
        if not next_cursor:
            break

    return results


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
