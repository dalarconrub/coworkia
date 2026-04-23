from pathlib import Path
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env
from tools.google_keep_tools import load_keep_export
from tools.notion_tools import (
    create_page,
    extract_property_value,
    get_data_source_schema,
    query_data_source,
)


KEEP_ID_PROP = "Google Keep ID"


def main() -> int:
    parser = argparse.ArgumentParser(description="Completa importacion restante de Google Keep a KIT")
    parser.add_argument("--source", required=True, help="Carpeta del export Google Keep")
    args = parser.parse_args()

    load_project_env(Path(".env"))
    db_kit = os.getenv("NOTION_DB_KIT")
    if not db_kit:
        print("Falta NOTION_DB_KIT")
        return 2

    # Pre-flight critico: sin la columna Google Keep ID en el schema, Notion
    # descarta silenciosamente el campo al crear filas -> dedupe queda roto y
    # el script duplica las 821 notas en cada run (incidente 2026-04-21,
    # cleanup masivo el 2026-04-23 con tools/dedupe_notion_db.py).
    schema = get_data_source_schema(db_kit)
    if KEEP_ID_PROP not in schema.get("properties", []):
        print(
            f"ERROR: la propiedad '{KEEP_ID_PROP}' NO existe en NOTION_DB_KIT.\n"
            f"  Sin ella el dedupe falla y se duplican notas en cada run.\n"
            f"  Soluciones (cualquiera vale):\n"
            f"    1) python tools/ensure_kit_external_fields.py  (idempotente, recomendado)\n"
            f"    2) En Notion KIT -> '+' columna -> Text -> nombre '{KEEP_ID_PROP}'"
        )
        return 2

    notes = load_keep_export(args.source)
    rows = query_data_source(db_kit)

    existing = set()
    for row in rows:
        props = row.get("properties", {})
        keep_id = extract_property_value(props.get(KEEP_ID_PROP, {})) if KEEP_ID_PROP in props else ""
        if keep_id:
            existing.add(keep_id)

    # Heuristica defensiva: si hay >100 filas en KIT con Subtipo='Nota'
    # (convencion de notas Keep) pero ninguna tiene Google Keep ID, casi seguro
    # estamos repitiendo el incidente 2026-04-21 (existing vacio = todo se ve
    # como nuevo = duplicado). Abortamos en vez de duplicar 821 notas.
    notas_existentes = sum(
        1 for r in rows
        if extract_property_value(r.get("properties", {}).get("Subtipo", {})) == "Nota"
    )
    if notas_existentes > 100 and not existing:
        print(
            f"ERROR: KIT tiene {notas_existentes} filas con Subtipo='Nota' pero NINGUNA tiene\n"
            f"  '{KEEP_ID_PROP}' poblado. Importar ahora duplicaria todas las notas.\n"
            f"  Causa probable: las filas se crearon antes de que existiera la columna.\n"
            f"  Soluciones:\n"
            f"    1) Backfill manual de Google Keep ID en las filas existentes desde Notion\n"
            f"    2) Si quieres re-importar TODO desde cero, archiva primero las filas Nota\n"
            f"       sin Keep ID (verlas en Notion con filtro Subtipo=Nota AND Google Keep ID is empty)"
        )
        return 2

    pending = [note for note in notes if note["keep_id"] not in existing]
    print(f"source={args.source}")
    print(f"existing={len(existing)} pending={len(pending)} total={len(notes)}")

    created = 0
    errors = 0

    for idx, note in enumerate(pending, 1):
        props = {
            "Titulo": {"title": [{"text": {"content": note["title"][:2000]}}]},
            "Tipo": {"select": {"name": "Information"}},
            "Subtipo": {"select": {"name": "Nota"}},
            "Google Keep ID": {"rich_text": [{"text": {"content": note["keep_id"][:500]}}]},
            "Fuente / Autor": {"rich_text": [{"text": {"content": "Google Keep"}}]},
            "Estado": {"select": {"name": "Archivado" if note.get("archived") else "Activo"}},
        }
        if note.get("summary"):
            props["Resumen"] = {"rich_text": [{"text": {"content": note["summary"][:2000]}}]}
        if note.get("labels"):
            props["Etiquetas"] = {"multi_select": [{"name": item[:100]} for item in note["labels"][:25]]}
        if note.get("created_date"):
            props["Fecha de publicacion"] = {"date": {"start": note["created_date"]}}
        if note.get("updated_date"):
            props["Fecha de actualizacion"] = {"date": {"start": note["updated_date"]}}
        if note.get("extracts"):
            props["Extractos"] = {"rich_text": [{"text": {"content": note["extracts"][:2000]}}]}
        if note.get("attachments"):
            joined = "\n".join(note["attachments"])
            props["Usada en"] = {"rich_text": [{"text": {"content": joined[:2000]}}]}

        for attempt in range(5):
            try:
                create_page(parent_id=db_kit, title=note["title"], properties=props, is_data_source=True)
                created += 1
                break
            except Exception as exc:
                if attempt == 4:
                    errors += 1
                    print(f"error {idx}/{len(pending)}: {note['title'][:80]} :: {exc}")
                time.sleep(2 + attempt)

        time.sleep(0.45)
        if idx % 25 == 0:
            print(f"progress {idx}/{len(pending)} created={created} errors={errors}")

    print(f"done created={created} errors={errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
