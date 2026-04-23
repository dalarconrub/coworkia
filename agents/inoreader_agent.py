"""
Agente Inoreader -> KIT (catalogo de Information en Notion).

Inoreader actua como FUENTE EXTERNA de KIT (no como catalogo separado).
Solo entra a KIT lo que se tagea EXPLICITAMENTE con INOREADER_FOLDER_KIT
(default 'kit-import'). El estado 'starred' NO importa: en Inoreader es el
buffer de "Read later" y no implica intencion de catalogar.

Cada articulo en KIT lleva:
  - Inoreader ID (rich_text, clave de unicidad)
  - Inoreader Tags (multi_select, tipicamente 'kit-import')
  - Tipo = Information, Subtipo segun heuristica (Articulo/Newsletter/Blog/Video/Podcast)

Dos rutas hacia KIT, ambas idempotentes y compatibles entre si:
  1. API OAuth2 con sync incremental (cursor en artifacts/inoreader_sync_state.json):
        python agents/inoreader_agent.py sync
        python agents/inoreader_agent.py sync --full
  2. JSON feed publico (sin auth, sin cuota), bulk one-shot:
        python agents/inoreader_agent.py import-feed --url "<feed_json_url>" --tag kit-import

INX-ENLACES: Inoreader NO crea filas inoreader:* propias. Las filas KIT que
materializa el sync aparecen en INX vía sync_inx_links --source kit (clave
kit:<page_id>). Para vincular un articulo a un proyecto PTN, usar:
        python agents/inoreader_agent.py link <inoreader_id> <proyecto_ref>
que actualiza la relacion PTN Proyecto sobre la fila kit:* existente.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

import requests

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.inoreader_tools import (
    API_BASE,
    _api_headers,
    list_folders,
    user_info,
)
from tools.notion_tools import extract_property_value, query_data_source


# ─── AUTH-CHECK ──────────────────────────────────────────────────────────────

def auth_check() -> str:
    """Valida tokens y reporta cuota disponible."""
    try:
        info = user_info()
    except Exception as exc:
        return (
            "[ERROR] No se pudo conectar con Inoreader.\n"
            f"  Detalle: {exc}\n"
            "  Soluciones:\n"
            "    1) Verifica INOREADER_APP_ID/KEY en .env\n"
            "    2) Re-autoriza con: python tools/inoreader_oauth.py"
        )

    # Headers de cuota: hacemos una request directa para leerlos
    resp = requests.get(f"{API_BASE}/user-info", headers=_api_headers(), timeout=30)
    z1_used = resp.headers.get("x-reader-zone1-usage", "?")
    z1_lim = resp.headers.get("x-reader-zone1-limit", "?")
    z2_used = resp.headers.get("x-reader-zone2-usage", "?")
    z2_lim = resp.headers.get("x-reader-zone2-limit", "?")
    reset_secs = resp.headers.get("x-reader-limits-reset-after", "?")

    return (
        f"[OK] Conectado como: {info.get('userName') or info.get('userEmail') or info.get('userId')}\n"
        f"  user_id: {info.get('userId')}\n"
        f"  Zone 1 (read): {z1_used}/{z1_lim}\n"
        f"  Zone 2 (write): {z2_used}/{z2_lim}\n"
        f"  Reset en: {reset_secs} seg"
    )


# ─── LIST-FOLDERS ────────────────────────────────────────────────────────────

def listar_folders() -> str:
    folders = list_folders()
    if not folders:
        return "Sin carpetas/tags definidas en tu cuenta Inoreader."
    return "Carpetas/tags Inoreader (ids=user/-/label/<nombre>):\n" + \
        "\n".join(f"  - {f}" for f in folders)


# ─── SYNC (delegado a tools/sync_inoreader_to_kit.py) ────────────────────────

def sync(full: bool = False, limit: int | None = None, dry_run: bool = False) -> str:
    from tools.sync_inoreader_to_kit import run_sync
    metrics = run_sync(full=full, limit=limit, dry_run=dry_run)
    folder_kit = os.getenv("INOREADER_FOLDER_KIT", "kit-import")
    return (
        f"\n=== SYNC COMPLETADO ===\n"
        f"  {folder_kit} (API): {metrics['tagged_fetched']}\n"
        f"  merged unique:     {metrics['merged']}\n"
        f"  created:           {metrics['created']}\n"
        f"  updated:           {metrics['updated']}\n"
        f"  errors:            {metrics['errors']}"
    )


# ─── LISTAR (artículos Inoreader en KIT) ─────────────────────────────────────

def _inoreader_rows(db_kit: str) -> list[dict]:
    rows = query_data_source(db_kit)
    out = []
    for r in rows:
        props = r.get("properties", {})
        if "Inoreader ID" not in props:
            continue
        if not extract_property_value(props["Inoreader ID"]):
            continue
        out.append(r)
    return out


def listar(subtipo: str | None = None, tag: str | None = None) -> str:
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_kit:
        return "[ERROR] Falta NOTION_DB_KIT en .env"
    rows = _inoreader_rows(db_kit)

    if subtipo:
        rows = [r for r in rows if extract_property_value(r["properties"].get("Subtipo", {})) == subtipo]
    if tag:
        rows = [r for r in rows if tag in (extract_property_value(r["properties"].get("Inoreader Tags", {})) or "")]

    if not rows:
        return "Sin articulos Inoreader en KIT que coincidan."
    lineas = [f"=== KIT - Inoreader ({len(rows)}) ===\n"]
    for r in rows:
        p = r["properties"]
        titulo = (extract_property_value(p.get("Titulo", {}))
                  or extract_property_value(p.get("Título", {})) or "(sin titulo)")
        sub = extract_property_value(p.get("Subtipo", {})) or "?"
        tags = extract_property_value(p.get("Inoreader Tags", {})) or ""
        autor = extract_property_value(p.get("Fuente / Autor", {})) or ""
        lineas.append(f"  • [{sub}] {titulo[:70]}")
        meta = []
        if tags: meta.append(f"tags={tags}")
        if autor: meta.append(f"de={autor[:40]}")
        if meta:
            lineas.append(f"    {', '.join(meta)}")
    return "\n".join(lineas)


# ─── ESTADO (resumen del catalogo Inoreader en KIT) ──────────────────────────

def estado() -> str:
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_kit:
        return "[ERROR] Falta NOTION_DB_KIT en .env"
    rows = _inoreader_rows(db_kit)
    if not rows:
        return "No hay articulos Inoreader catalogados en KIT todavia."

    por_subtipo: dict[str, int] = {}
    por_tag: dict[str, int] = {}
    for r in rows:
        p = r["properties"]
        sub = extract_property_value(p.get("Subtipo", {})) or "Sin subtipo"
        por_subtipo[sub] = por_subtipo.get(sub, 0) + 1
        tags_str = extract_property_value(p.get("Inoreader Tags", {})) or ""
        for t in [s.strip() for s in tags_str.split(",") if s.strip()]:
            por_tag[t] = por_tag.get(t, 0) + 1

    lineas = [f"=== ESTADO Inoreader en KIT ({len(rows)} articulos) ===\n", "Por subtipo:"]
    for k, v in sorted(por_subtipo.items(), key=lambda x: -x[1]):
        lineas.append(f"  {k}: {v}")
    lineas.append("\nPor tag de origen:")
    for k, v in sorted(por_tag.items(), key=lambda x: -x[1]):
        lineas.append(f"  {k}: {v}")
    return "\n".join(lineas)


# ─── LINK (vincula articulo a proyecto PTN) ──────────────────────────────────

def link(inoreader_id: str, proyecto_ref: str) -> str:
    from tools.sync_inx_links import link_article_to_ptn
    try:
        result = link_article_to_ptn(inoreader_id, proyecto_ref)
    except Exception as exc:
        return f"[ERROR] {exc}"
    return (
        f"[OK] Articulo vinculado a proyecto PTN\n"
        f"  KIT page: {result['kit_page_id']}\n"
        f"  Proyecto: {result['proyecto_id']}\n"
        f"  INX clave: {result['key']}"
    )


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agente Inoreader -> KIT")
    sub = parser.add_subparsers(dest="comando")

    sub.add_parser("auth-check", help="Verifica tokens y muestra cuota disponible")
    sub.add_parser("list-folders", help="Lista carpetas/tags de tu Inoreader")

    p_sync = sub.add_parser("sync", help="Sync incremental Inoreader -> KIT (vía API)")
    p_sync.add_argument("--full", action="store_true", help="Ignora cursor incremental")
    p_sync.add_argument("--limit", type=int, default=None, help="Tope N items para pruebas")
    p_sync.add_argument("--dry-run", action="store_true", help="No escribe en Notion")

    p_imp = sub.add_parser("import-feed", help="Importa desde JSON feed publico (sin OAuth)")
    p_imp.add_argument("--url", required=True, action="append", help="URL del JSON feed (repetible)")
    p_imp.add_argument("--tag", default=None, help="source_tag para los articulos")
    p_imp.add_argument("--newer-than", default=None, help="Solo articulos >= YYYY-MM-DD")
    p_imp.add_argument("--limit", type=int, default=None)
    p_imp.add_argument("--dry-run", action="store_true")

    p_list = sub.add_parser("listar", help="Lista articulos Inoreader catalogados en KIT")
    p_list.add_argument("--subtipo", default=None,
                        choices=["Artículo", "Newsletter", "Blog", "Vídeo", "Podcast"])
    p_list.add_argument("--tag", default=None, help="Filtra por tag (kit-import por defecto)")

    sub.add_parser("estado", help="Resumen del catalogo Inoreader en KIT")

    p_link = sub.add_parser("link", help="Vincula articulo Inoreader a proyecto PTN (via INX)")
    p_link.add_argument("inoreader_id", help="Inoreader ID del articulo (rich_text de la fila KIT)")
    p_link.add_argument("proyecto_ref", help="ID o nombre del proyecto PTN")

    args = parser.parse_args()

    if args.comando == "auth-check":
        print(auth_check())
    elif args.comando == "list-folders":
        print(listar_folders())
    elif args.comando == "sync":
        print(sync(full=args.full, limit=args.limit, dry_run=args.dry_run))
    elif args.comando == "import-feed":
        # Delegar al importer file (que ya soporta --url y --newer-than)
        cmd_args = []
        for u in args.url:
            cmd_args += ["--url", u]
        if args.tag:
            cmd_args += ["--tag", args.tag]
        if args.newer_than:
            cmd_args += ["--newer-than", args.newer_than]
        if args.limit:
            cmd_args += ["--limit", str(args.limit)]
        if args.dry_run:
            cmd_args += ["--dry-run"]
        sys.argv = [sys.argv[0]] + cmd_args
        from tools.import_inoreader_articles import main as importer_main
        sys.exit(importer_main())
    elif args.comando == "listar":
        print(listar(subtipo=args.subtipo, tag=args.tag))
    elif args.comando == "estado":
        print(estado())
    elif args.comando == "link":
        print(link(args.inoreader_id, args.proyecto_ref))
    else:
        parser.print_help()
