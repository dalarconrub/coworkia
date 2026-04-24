"""
Importador OFFLINE de articulos Inoreader -> KIT (Notion).

Pensado como plan B mientras la app OAuth esta pendiente de aprobacion,
y como complemento permanente para evitar el limite de 100 calls/dia del
plan API (los JSON feeds publicos no consumen cuota API).

CONVENCION: solo se importan articulos tageados con INOREADER_FOLDER_KIT
(default 'kit-import'). El estado 'starred' en Inoreader es el buffer
"Read later" y NO implica intencion de catalogar; no se importa por
defecto. Si pasas explicitamente la URL JSON del stream starred via --url
se importara igualmente (este importer no impone politica, ejecuta lo que
le indiques).

Para Inoreader es equivalente folder o tag: ambos generan URLs
'/stream/user/<id>/tag/<nombre>/view/json'. La distincion es solo
operativa (folder = todos los feeds dentro; tag = articulos individuales
que tu etiquetas a mano).

Como obtener la URL publica (modo --url, recomendado):
  1. En Inoreader: click derecho sobre el folder/tag/Starred en el sidebar.
  2. 'Folder properties' (o equivalente segun idioma).
  3. Activa el toggle 'Export' / 'Make public'.
  4. Selecciona formato 'JSON feed'.
  5. Copia la URL publica que te muestra.
  6. Anade '?n=1000' para maximizar items por peticion.
  7. Ejecuta:
        python tools/import_inoreader_articles.py \\
            --url "https://www.inoreader.com/stream/user/.../tag/kit-import/view/json?n=1000" \\
            --tag kit-import
     Repetible con varias --url si quieres importar varias fuentes manuales.

Como usar archivos descargados (modo --source, equivalente offline):
  1. Mismos pasos 1-5; en vez de copiar URL, descarga el JSON al disco.
  2. Mueve los .json a artifacts/imports/inoreader/
  3. Ejecuta:
        python tools/import_inoreader_articles.py --source artifacts/imports/inoreader/

Convencion de source_tag (etiqueta en KIT.Inoreader Tags):
  - --url: se infiere INOREADER_FOLDER_KIT salvo que la URL manual contenga
           'starred', en cuyo caso se etiqueta asi solo para trazabilidad.
           Override con --tag.
  - --source: se infiere del nombre de archivo (stem).
              'starred' contiene esa palabra -> 'starred'.
              stem == INOREADER_FOLDER_KIT   -> ese nombre.
              cualquier otro                 -> stem.

Idempotente: clave = Inoreader ID. Re-ejecutar actualiza, no duplica.
Si el mismo articulo aparece en varias fuentes (e.g. starred + kit-import),
se fusionan source_tags antes del upsert.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

import requests

from tools.inoreader_tools import dispatch_normalize, merge_articles
from tools.sync_inoreader_to_kit import (
    existing_articles as _existing_articles,
    upsert_article_to_kit,
)


def _detect_source_tag(filename_stem: str) -> str:
    folder_kit = os.getenv("INOREADER_FOLDER_KIT", "kit-import")
    low = filename_stem.lower()
    if "starred" in low:
        return "starred"
    if low == folder_kit.lower():
        return folder_kit
    return filename_stem


def _extract_items(raw) -> list[dict]:
    if isinstance(raw, list):
        return raw  # algunos exports devuelven lista plana
    return raw.get("items") or raw.get("articles") or []


def _load_articles_from_file(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = _extract_items(raw)
    source_tag = _detect_source_tag(path.stem)
    return [dispatch_normalize(it, source_tag) for it in items]


def _load_articles_from_url(url: str, source_tag: str, timeout: int = 60) -> list[dict]:
    """Descarga y normaliza un JSON feed publico de Inoreader (sin auth).

    URLs validas suelen venir de:
      Inoreader -> click derecho en folder/tag/Starred -> Folder properties
      -> Export ON -> JSON feed -> copia URL publica.
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    items = _extract_items(resp.json())
    return [dispatch_normalize(it, source_tag) for it in items]


def _filter_newer_than(articles: list[dict], newer_than: str | None) -> list[dict]:
    """Filtra articulos client-side por published_date >= newer_than (YYYY-MM-DD).

    Articulos sin published_date se conservan (no podemos juzgar antiguedad).
    """
    if not newer_than:
        return articles
    return [
        a for a in articles
        if not a.get("published_date") or a["published_date"] >= newer_than
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Importa articulos Inoreader (JSON export) a KIT"
    )
    parser.add_argument(
        "--source", default=None,
        help="Carpeta con .json o un archivo JSON unico (descarga manual)",
    )
    parser.add_argument(
        "--url", default=None,
        help="URL publica de un JSON feed de Inoreader (no requiere OAuth). "
             "Repetible con --url multiple veces.",
        action="append",
    )
    parser.add_argument(
        "--tag", default=None,
        help="source_tag para articulos descargados con --url. "
             "Si se pasan varias --url, se aplica a todas. Default: INOREADER_FOLDER_KIT; "
             "si la URL manual contiene 'starred', se etiqueta 'starred' solo para trazabilidad.",
    )
    parser.add_argument("--limit", type=int, default=None,
                        help="Procesa solo los N primeros articulos (pruebas)")
    parser.add_argument("--newer-than", default=None,
                        help="Solo articulos con published_date >= YYYY-MM-DD "
                             "(filtro client-side, los sin fecha se conservan)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Lee y normaliza, no escribe en Notion")
    args = parser.parse_args()

    if not args.source and not args.url:
        print("Necesitas pasar --source <ruta> o --url <feed_url> (o ambos)")
        return 2

    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_kit and not args.dry_run:
        print("Falta NOTION_DB_KIT en .env (no critico si usas --dry-run)")
        return 2

    all_lists: list[list[dict]] = []

    # Fuente A: archivos locales
    if args.source:
        source = Path(args.source)
        if not source.exists():
            print(f"No existe la ruta: {source}")
            return 2
        files = [source] if source.is_file() else sorted(source.glob("*.json"))
        if not files:
            print(f"No hay archivos JSON en: {source}")
        for f in files:
            try:
                arts = _load_articles_from_file(f)
                tag = _detect_source_tag(f.stem)
                print(f"[read file] {f.name}: {len(arts)} articulos (source_tag={tag})")
                all_lists.append(arts)
            except Exception as exc:
                print(f"[err  file] {f.name}: {exc}")

    # Fuente B: URLs de JSON feeds publicos
    if args.url:
        folder_default = os.getenv("INOREADER_FOLDER_KIT", "kit-import")
        for url in args.url:
            tag = args.tag or ("starred" if "starred" in url.lower() else folder_default)
            try:
                arts = _load_articles_from_url(url, tag)
                print(f"[read url ] {url[:60]}... : {len(arts)} articulos (source_tag={tag})")
                all_lists.append(arts)
            except Exception as exc:
                print(f"[err  url ] {url[:60]}... : {exc}")

    merged = merge_articles(*all_lists)
    print(f"[merge] union deduplicada: {len(merged)} articulos")

    if args.newer_than:
        before = len(merged)
        merged = _filter_newer_than(merged, args.newer_than)
        print(f"[filter] newer-than={args.newer_than}: {before} -> {len(merged)} articulos")

    if args.limit:
        merged = merged[: args.limit]
        print(f"[limit] truncado a {len(merged)} articulos")

    if args.dry_run:
        print("[dry-run] no escribo en Notion. Termino.")
        return 0

    print("[notion] cargando indices existentes en KIT (por URL y por Inoreader ID)...")
    existing = _existing_articles(db_kit)
    print(f"[notion] {len(existing['by_inoreader_id'])} articulos Inoreader, {len(existing['by_url'])} con URL")

    created = updated = errors = 0
    total = len(merged)
    for idx, art in enumerate(merged, 1):
        for attempt in range(5):
            try:
                action, _page_id = upsert_article_to_kit(db_kit, art, existing)
                if action == "created":
                    created += 1
                else:
                    updated += 1
                break
            except Exception as exc:
                if attempt == 4:
                    errors += 1
                    print(f"[err {idx}/{total}] {art['title'][:80]}: {exc}")
                time.sleep(2 + attempt)
        time.sleep(0.35)
        if idx % 25 == 0:
            print(f"[progress] {idx}/{total} created={created} updated={updated} errors={errors}")

    print("\n=== IMPORT COMPLETADO ===")
    print(f"  Total procesados: {total}")
    print(f"  Creados:          {created}")
    print(f"  Actualizados:     {updated}")
    print(f"  Errores:          {errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
