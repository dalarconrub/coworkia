"""
Sincroniza la base puente INX-ENLACES a partir de TODOIST-TAREAS, NOTION, OBSIDIAN,
REP-Repositorios (GitHub) y BIB-Bibliografía (Paperpile).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import (
    query_data_source,
    create_page,
    update_page_properties,
    extract_property_value,
)
from tools.obsidian_tools import get_frontmatter_by_relative_path


def _rich_text(value: str) -> dict:
    return {"rich_text": [{"text": {"content": value[:2000]}}]}


def _existing_map(db_id: str) -> dict[str, str]:
    rows = query_data_source(db_id)
    mapping = {}
    for r in rows:
        key = extract_property_value(r.get("properties", {}).get("Clave", {}))
        if key:
            mapping[key] = r["id"]
    return mapping


def _upsert(db_id: str, key: str, title: str, props: dict, existing: dict) -> None:
    props["Clave"] = {"rich_text": [{"text": {"content": key}}]}
    props["Elemento"] = {"title": [{"text": {"content": title}}]}
    if key in existing:
        update_page_properties(existing[key], props)
    else:
        create_page(parent_id=db_id, title=title, properties=props, is_data_source=True)


def _sync_todoist(db_links: str, db_todoist: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_todoist)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        tid = extract_property_value(props.get("Todoist ID", {}))
        if not tid:
            continue
        title = extract_property_value(props.get("Tarea", {})) or f"Todoist {tid}"
        source_estado = extract_property_value(props.get("Estado", {})) or "Activa"
        inx_estado = "Completada" if source_estado == "Completada" else "Activo"
        data = {
            "Fuente": {"select": {"name": "Todoist"}},
            "Estado": {"select": {"name": inx_estado}},
            "Todoist ID": _rich_text(tid),
        }
        # Relaciones PTN si existen en TODOIST-TAREAS
        for rel, name in [("PTN Proyecto", "PTN Proyecto"), ("PTN Tarea", "PTN Tarea"), ("PTN Nota", "PTN Nota")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        for rel, name in [("Area", "Area"), ("Bloque", "Bloque"), ("Contexto", "Contexto")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        _upsert(db_links, f"todoist:{tid}", title, data, existing)
        n += 1
    return n


def _sync_ptn_log(db_links: str, db_notion: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_notion)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        source_id = extract_property_value(props.get("Fuente ID", {}))
        if not source_id:
            continue
        title = extract_property_value(props.get("Evento", {})) or source_id
        data = {
            "Fuente": {"select": {"name": "Notion"}},
            "Estado": {"select": {"name": "Activo"}},
        }
        for rel, name in [("PTN Proyecto", "PTN Proyecto"), ("PTN Tarea", "PTN Tarea"), ("PTN Nota", "PTN Nota")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        for rel, name in [("Area", "Area"), ("Bloque", "Bloque"), ("Contexto", "Contexto")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        _upsert(db_links, f"ptn:{source_id}", title, data, existing)
        n += 1
    return n


def _sync_obsidian(db_links: str, db_obsidian: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_obsidian)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        path = extract_property_value(props.get("Ruta", {}))
        if not path:
            continue
        title = extract_property_value(props.get("Evento", {})) or path
        data = {
            "Fuente": {"select": {"name": "Obsidian"}},
            "Estado": {"select": {"name": "Activo"}},
            "Obsidian Ruta": _rich_text(path),
        }
        fm = get_frontmatter_by_relative_path(path)
        citekey = (fm.get("citekey") or "").strip()
        if citekey:
            data["Paperpile Citekey"] = _rich_text(citekey)
        kit_ids = extract_property_value(props.get("KIT IDs", {}))
        if kit_ids:
            data["KIT IDs"] = _rich_text(kit_ids)
        for rel, name in [("Area", "Area"), ("Bloque", "Bloque"), ("Contexto", "Contexto")]:
            rel_val = props.get(rel, {}).get("relation", [])
            if rel_val:
                data[name] = {"relation": rel_val}
        _upsert(db_links, f"obsidian:{path}", title, data, existing)
        n += 1
    return n


def _resolve_project_id(db_proyectos: str, ref: str) -> str | None:
    """Devuelve el page_id de un proyecto PTN. Acepta ID directo o nombre."""
    if "-" in ref and len(ref.replace("-", "")) == 32:
        return ref
    rows = query_data_source(db_proyectos)
    ref_low = ref.lower()
    for r in rows:
        nombre = extract_property_value(r.get("properties", {}).get("Nombre del Proyecto", {})) \
            or extract_property_value(r.get("properties", {}).get("Nombre", {})) or ""
        if nombre.lower() == ref_low or ref_low in nombre.lower():
            return r["id"]
    return None


def _find_row_by_title(db_id: str, title_prop: str, value: str) -> dict | None:
    for r in query_data_source(db_id):
        v = extract_property_value(r.get("properties", {}).get(title_prop, {})) or ""
        if v == value:
            return r
    return None


def _find_row_by_text(db_id: str, prop: str, value: str) -> dict | None:
    for r in query_data_source(db_id):
        v = extract_property_value(r.get("properties", {}).get(prop, {})) or ""
        if v == value:
            return r
    return None


def link_repo_to_ptn(repo_nombre: str, proyecto_ref: str) -> dict:
    """Crea/actualiza fila INX github:<repo> con relación PTN Proyecto."""
    db_links = os.getenv("NOTION_DB_INX")
    db_repos = os.getenv("NOTION_DB_REPOS")
    db_proy = os.getenv("NOTION_DS_PROYECTOS")
    if not all([db_links, db_repos, db_proy]):
        raise RuntimeError("Faltan NOTION_DB_INX, NOTION_DB_REPOS o NOTION_DS_PROYECTOS en .env")
    repo = _find_row_by_title(db_repos, "Nombre", repo_nombre)
    if not repo:
        raise ValueError(f"Repo '{repo_nombre}' no encontrado en REP-Repositorios")
    proyecto_id = _resolve_project_id(db_proy, proyecto_ref)
    if not proyecto_id:
        raise ValueError(f"Proyecto PTN '{proyecto_ref}' no encontrado")
    rprops = repo.get("properties", {})
    url = extract_property_value(rprops.get("URL", {})) or extract_property_value(rprops.get("URL HTML", {}))
    tipo = extract_property_value(rprops.get("Tipo", {}))
    estado_repo = extract_property_value(rprops.get("Estado", {}))
    detalle_parts = [p for p in [tipo and f"Tipo: {tipo}", estado_repo and f"Estado: {estado_repo}"] if p]
    data = {
        "Fuente": {"select": {"name": "GitHub"}},
        "Estado": {"select": {"name": "Verificado"}},
        "PTN Proyecto": {"relation": [{"id": proyecto_id}]},
    }
    if url:
        data["URL"] = {"url": url}
    if detalle_parts:
        data["Detalle"] = {"rich_text": [{"text": {"content": " | ".join(detalle_parts)[:2000]}}]}
    existing = _existing_map(db_links)
    _upsert(db_links, f"github:{repo_nombre}", repo_nombre, data, existing)
    return {"key": f"github:{repo_nombre}", "proyecto_id": proyecto_id, "url": url}


def link_paper_to_ptn(citekey: str, proyecto_ref: str) -> dict:
    """Crea/actualiza fila INX paperpile:<citekey> con relación PTN Proyecto."""
    db_links = os.getenv("NOTION_DB_INX")
    db_bib = os.getenv("NOTION_DB_BIB")
    db_proy = os.getenv("NOTION_DS_PROYECTOS")
    if not all([db_links, db_bib, db_proy]):
        raise RuntimeError("Faltan NOTION_DB_INX, NOTION_DB_BIB o NOTION_DS_PROYECTOS en .env")
    paper = _find_row_by_text(db_bib, "Citekey", citekey)
    if not paper:
        raise ValueError(f"Paper citekey '{citekey}' no encontrado en BIB-Bibliografía")
    proyecto_id = _resolve_project_id(db_proy, proyecto_ref)
    if not proyecto_id:
        raise ValueError(f"Proyecto PTN '{proyecto_ref}' no encontrado")
    pprops = paper.get("properties", {})
    titulo = extract_property_value(pprops.get("Título", {})) or citekey
    doi = extract_property_value(pprops.get("DOI", {}))
    anio = extract_property_value(pprops.get("Año", {}))
    journal = extract_property_value(pprops.get("Journal", {}))
    detalle_parts = [p for p in [anio and f"Año: {anio}", journal and f"Journal: {journal}"] if p]
    data = {
        "Fuente": {"select": {"name": "Paperpile"}},
        "Estado": {"select": {"name": "Verificado"}},
        "PTN Proyecto": {"relation": [{"id": proyecto_id}]},
    }
    if doi:
        data["URL"] = {"url": doi}
    if detalle_parts:
        data["Detalle"] = {"rich_text": [{"text": {"content": " | ".join(detalle_parts)[:2000]}}]}
    existing = _existing_map(db_links)
    _upsert(db_links, f"paperpile:{citekey}", titulo[:2000], data, existing)
    return {"key": f"paperpile:{citekey}", "proyecto_id": proyecto_id, "url": doi}


def _sync_github(db_links: str, db_repos: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_repos)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        nombre = extract_property_value(props.get("Nombre", {}))
        if not nombre:
            continue
        url = extract_property_value(props.get("URL", {})) or extract_property_value(props.get("URL HTML", {}))
        tipo = extract_property_value(props.get("Tipo", {}))
        estado_repo = extract_property_value(props.get("Estado", {}))
        detalle_parts = [p for p in [tipo and f"Tipo: {tipo}", estado_repo and f"Estado: {estado_repo}"] if p]
        data = {
            "Fuente": {"select": {"name": "GitHub"}},
            "Estado": {"select": {"name": "Activo"}},
        }
        if url:
            data["URL"] = {"url": url}
        if detalle_parts:
            data["Detalle"] = {"rich_text": [{"text": {"content": " | ".join(detalle_parts)[:2000]}}]}
        _upsert(db_links, f"github:{nombre}", nombre, data, existing)
        n += 1
    return n


def _sync_kit(db_links: str, db_kit: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_kit)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        titulo = extract_property_value(props.get("Titulo", {})) \
            or extract_property_value(props.get("Título", {})) or ""
        if not titulo:
            continue
        tipo = extract_property_value(props.get("Tipo", {}))
        subtipo = extract_property_value(props.get("Subtipo", {}))
        enlace = extract_property_value(props.get("Enlace", {}))
        detalle_parts = [p for p in [tipo and f"Tipo: {tipo}", subtipo and f"Subtipo: {subtipo}"] if p]
        data = {
            "Fuente": {"select": {"name": "Notion"}},
            "Estado": {"select": {"name": "Activo"}},
        }
        if enlace:
            data["URL"] = {"url": enlace}
        if detalle_parts:
            data["Detalle"] = {"rich_text": [{"text": {"content": " | ".join(detalle_parts)[:2000]}}]}
        _upsert(db_links, f"kit:{r['id']}", titulo[:2000], data, existing)
        n += 1
    return n


def _sync_paperpile(db_links: str, db_bib: str, existing: dict, limit: int | None) -> int:
    rows = query_data_source(db_bib)
    if limit:
        rows = rows[:limit]
    n = 0
    for r in rows:
        props = r.get("properties", {})
        citekey = extract_property_value(props.get("Citekey", {}))
        titulo = extract_property_value(props.get("Título", {}))
        if not citekey:
            continue
        title = titulo or citekey
        doi = extract_property_value(props.get("DOI", {}))
        anio = extract_property_value(props.get("Año", {}))
        journal = extract_property_value(props.get("Journal", {}))
        detalle_parts = [p for p in [anio and f"Año: {anio}", journal and f"Journal: {journal}"] if p]
        data = {
            "Fuente": {"select": {"name": "Paperpile"}},
            "Estado": {"select": {"name": "Activo"}},
        }
        if doi:
            data["URL"] = {"url": doi}
        if detalle_parts:
            data["Detalle"] = {"rich_text": [{"text": {"content": " | ".join(detalle_parts)[:2000]}}]}
        _upsert(db_links, f"paperpile:{citekey}", title[:2000], data, existing)
        n += 1
    return n


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Sync INX links")
    parser.add_argument(
        "--source",
        choices=["todoist", "notion", "obsidian", "github", "paperpile", "kit", "all"],
        default="all",
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    db_links = os.getenv("NOTION_DB_INX")
    db_todoist = os.getenv("TODOIST_DB_TAREAS")
    db_notion = os.getenv("NOTION_DB")
    db_obsidian = os.getenv("OBSIDIAN_DB")
    db_repos = os.getenv("NOTION_DB_REPOS")
    db_bib = os.getenv("NOTION_DB_BIB")
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_links:
        print("Falta NOTION_DB_INX en .env")
        return 2

    required = {
        "todoist": ("TODOIST_DB_TAREAS", db_todoist),
        "notion": ("NOTION_DB", db_notion),
        "obsidian": ("OBSIDIAN_DB", db_obsidian),
        "github": ("NOTION_DB_REPOS", db_repos),
        "paperpile": ("NOTION_DB_BIB", db_bib),
        "kit": ("NOTION_DB_KIT", db_kit),
    }
    sources = list(required) if args.source == "all" else [args.source]
    missing = [required[s][0] for s in sources if not required[s][1]]
    if missing:
        print(f"Faltan IDs en .env para sources={sources}: {', '.join(missing)}")
        return 2

    counts = {s: 0 for s in required}
    if "todoist" in sources:
        counts["todoist"] = _sync_todoist(db_links, db_todoist, _existing_map(db_links), args.limit)
    if "notion" in sources:
        counts["notion"] = _sync_ptn_log(db_links, db_notion, _existing_map(db_links), args.limit)
    if "obsidian" in sources:
        counts["obsidian"] = _sync_obsidian(db_links, db_obsidian, _existing_map(db_links), args.limit)
    if "github" in sources:
        counts["github"] = _sync_github(db_links, db_repos, _existing_map(db_links), args.limit)
    if "paperpile" in sources:
        counts["paperpile"] = _sync_paperpile(db_links, db_bib, _existing_map(db_links), args.limit)
    if "kit" in sources:
        counts["kit"] = _sync_kit(db_links, db_kit, _existing_map(db_links), args.limit)
    print("INX enlaces sincronizados: " + " ".join(f"{k}={v}" for k, v in counts.items() if k in sources))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
