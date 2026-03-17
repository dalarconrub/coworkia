"""
BACK-Notion — Crea la base de datos en Notion y exporta páginas de Notion archivadas.

Exporta páginas accesibles por la integración (de cualquier base de datos o página suelta).

Uso:
    python apps/backs_notion.py --parent <PAGE_ID>
    python apps/backs_notion.py --parent <PAGE_ID> --fuente <DATABASE_ID>
    python apps/backs_notion.py --parent <PAGE_ID> --dry-run
"""

import sys, os, time, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date
from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    search_all, create_database, add_page_to_database,
    query_data_source, query_database, _extract_title,
)

SCHEMA = {
    # ── Identificación ────────────────────────────────────────────────
    "Título":           {"title": {}},
    "Notion_ID":        {"rich_text": {}},
    "URL":              {"url": {}},
    # ── Origen ────────────────────────────────────────────────────────
    "Base_origen":      {"rich_text": {}},
    "Tipo":             {"select": {}},        # Página / Base de datos
    # ── Fechas ────────────────────────────────────────────────────────
    "Creado":           {"date": {}},
    "Modificado":       {"date": {}},
    "Exportado":        {"date": {}},
}


def page_to_props(page: dict, base_nombre: str, fecha_hoy: str) -> dict:
    titulo = _extract_title(page)
    pid    = page.get("id", "")
    url    = page.get("url", "")
    tipo   = "Base de datos" if page.get("object") in ("database", "data_source") else "Página"

    creado     = (page.get("created_time", "") or "")[:10] or None
    modificado = (page.get("last_edited_time", "") or "")[:10] or None

    props = {
        "Título":      {"title": [{"text": {"content": titulo[:200]}}]},
        "Notion_ID":   {"rich_text": [{"text": {"content": pid}}]},
        "Base_origen": {"rich_text": [{"text": {"content": base_nombre}}]},
        "Tipo":        {"select": {"name": tipo}},
        "Exportado":   {"date": {"start": fecha_hoy}},
    }
    if url:
        props["URL"] = {"url": url}
    if creado:
        props["Creado"] = {"date": {"start": creado}}
    if modificado:
        props["Modificado"] = {"date": {"start": modificado}}
    return props


def fetch_pages_from_source(source_id: str) -> tuple[list[dict], str]:
    """Intenta obtener páginas de un data_source o database. Devuelve (pages, nombre)."""
    import requests as req
    from tools.notion_tools import _headers, BASE_URL

    # Intentar como data_source primero
    for endpoint in [f"{BASE_URL}/data_sources/{source_id}/query",
                     f"{BASE_URL}/databases/{source_id}/query"]:
        r = req.post(endpoint, headers=_headers(), json={})
        if r.status_code == 200:
            results = r.json().get("results", [])
            # Obtener nombre
            for get_ep in [f"{BASE_URL}/data_sources/{source_id}",
                           f"{BASE_URL}/databases/{source_id}"]:
                rg = req.get(get_ep, headers=_headers())
                if rg.status_code == 200:
                    nombre = _extract_title(rg.json())
                    return results, nombre
            return results, source_id
    return [], source_id


def main(parent_id: str, fuente_ids: list[str], dry_run: bool):
    fecha_hoy = date.today().isoformat()

    if not dry_run:
        print("Creando BACK-Notion en Notion...")
        db = create_database(parent_id, "BACK-Notion", SCHEMA)
        db_id = db["id"]
        print(f"  ✓ {db_id}\n")
    else:
        db_id = "DRY-RUN"
        print("(Dry run — no se escribe en Notion)\n")

    # Si no se especifican fuentes, usar todas las páginas accesibles
    if not fuente_ids:
        print("Obteniendo todas las páginas accesibles...")
        all_results = search_all()
        pages = [r for r in all_results if r.get("object") == "page"]
        print(f"  {len(pages)} páginas encontradas\n")
        sources = [("Búsqueda general", pages)]
    else:
        sources = []
        for sid in fuente_ids:
            pages, nombre = fetch_pages_from_source(sid)
            print(f"  {nombre}: {len(pages)} páginas")
            sources.append((nombre, pages))

    total_ok, total_err = 0, 0
    for nombre, pages in sources:
        print(f"→ {nombre} ({len(pages)} páginas)...")
        for i, page in enumerate(pages, 1):
            try:
                props = page_to_props(page, nombre, fecha_hoy)
                if not dry_run:
                    add_page_to_database(db_id, props)
                    time.sleep(0.35)
                total_ok += 1
                if i % 25 == 0:
                    print(f"  {i}/{len(pages)}...")
            except Exception as e:
                total_err += 1
                print(f"  ✗ {_extract_title(page)[:40]}: {e}")
        print(f"  ✓ {len(pages)} procesadas")

    print(f"\n{'─'*50}")
    print(f"  OK: {total_ok}  |  Errores: {total_err}")
    if not dry_run:
        print(f"  → https://notion.so/{db_id.replace('-','')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exporta páginas de Notion → BACK-Notion")
    parser.add_argument("--parent",  required=True, help="ID de página Notion padre")
    parser.add_argument("--fuente",  nargs="*", default=[], dest="fuentes",
                        help="IDs de data sources / databases a exportar (vacío = todas las páginas accesibles)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pid = args.parent.replace("-", "")
    if len(pid) == 32:
        pid = f"{pid[:8]}-{pid[8:12]}-{pid[12:16]}-{pid[16:20]}-{pid[20:]}"
    main(pid, args.fuentes, args.dry_run)
