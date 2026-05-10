"""
Backfill: asegura que TODAS las notas del vault Obsidian tengan fila en
OBSIDIAN_DB (y por ende en INX cuando se ejecute sync).

A diferencia de `log_obsidian_changes.py` (que se basa en mtime > last_mtime
y ignora notas pre-existentes que nunca fueron procesadas), este script
recorre TODAS las notas y crea fila OBSIDIAN_DB para las que falten.

Idempotente por `Ruta`: si ya existe fila en OBSIDIAN_DB con la misma ruta
relativa, salta. No toca filas existentes.

Opcional --sync: tras el backfill, ejecuta `sync_inx_links --source obsidian`.

Uso:
    python tools/backfill_obsidian_to_inx.py --dry-run
    python tools/backfill_obsidian_to_inx.py
    python tools/backfill_obsidian_to_inx.py --sync

Requisitos:
  - .env con OBSIDIAN_DB, OBSIDIAN_ALPHA_PATH.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import create_page, extract_property_value, query_data_source, get_data_source_schema, normalize_notion_id
from tools.obsidian_tools import get_todas_notas, read_nota, get_frontmatter
from tools.obsidian_wikilinks import extract_kit_ids
from tools.obsidian_note_metadata import (
    note_metadata_from_frontmatter,
    obsidian_db_metadata_props,
    obsidian_db_route_props,
    route_metadata_from_relative_path,
)


ABC_AREAS = "340622cf-315b-8116-a1bd-f21b04bc0ac1"
ABC_BLOQUES = "340622cf-315b-8191-bda1-dbc73e342720"
ABC_CONTEXTOS = "340622cf-315b-8175-b6b0-db2e1c794552"


def _existing_rutas(db_id: str) -> set[str]:
    rutas: set[str] = set()
    for r in query_data_source(db_id):
        ruta = extract_property_value(r.get("properties", {}).get("Ruta", {}))
        if ruta:
            rutas.add(ruta)
    return rutas


def _run_sync_obsidian() -> bool:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cmd = [sys.executable, "tools/sync_inx_links.py", "--source", "obsidian", "--limit", "200"]
    print(f"[sync] {' '.join(cmd[1:])}")
    result = subprocess.run(cmd, cwd=repo_root)
    return result.returncode == 0


def _rich_text(value: str) -> dict:
    return {"rich_text": [{"text": {"content": value[:2000]}}]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Previsualiza sin escribir a Notion.")
    parser.add_argument("--sync", action="store_true", help="Tras el backfill, corre sync_inx_links --source obsidian.")
    args = parser.parse_args()

    db_id = os.getenv("OBSIDIAN_DB")
    if not db_id:
        print("[error] Falta OBSIDIAN_DB en .env")
        return 2

    notas = get_todas_notas()
    print(f"=== Backfill Obsidian -> OBSIDIAN_DB ===")
    print(f"    dry_run={args.dry_run}, vault_notas={len(notas)}, db={db_id}")

    existing = _existing_rutas(db_id)
    print(f"[scan] filas OBSIDIAN_DB con Ruta: {len(existing)}")
    obs_schema = get_data_source_schema(db_id)
    obs_props = set(obs_schema.get("properties", []))

    area_map = {extract_property_value(r.get("properties", {}).get("Codigo", {})): r["id"]
                for r in query_data_source(ABC_AREAS)}
    bloque_map = {extract_property_value(r.get("properties", {}).get("Codigo", {})): r["id"]
                  for r in query_data_source(ABC_BLOQUES)}
    contexto_map = {extract_property_value(r.get("properties", {}).get("Codigo", {})): r["id"]
                    for r in query_data_source(ABC_CONTEXTOS)}

    to_backfill: list[dict] = []
    for nota in notas:
        rel = nota.get("relativo", "")
        if not rel or rel in existing:
            continue
        to_backfill.append(nota)

    print(f"[scan] notas vault sin fila en OBSIDIAN_DB: {len(to_backfill)}")
    for nota in to_backfill[:5]:
        print(f"    - {nota.get('relativo', '')[:100]}")
    if len(to_backfill) > 5:
        print(f"    (+{len(to_backfill) - 5} mas)")

    if args.dry_run:
        print("[dry-run] no se escribe nada.")
        return 0

    if not to_backfill:
        print("[backfill] nada que backfillear.")
        if args.sync and not _run_sync_obsidian():
            return 1
        return 0

    ok = 0
    errors = 0
    for nota in to_backfill:
        path = nota.get("path")
        rel = nota.get("relativo", "")
        if not path:
            continue
        parts = rel.split(os.sep)
        area = parts[0] if len(parts) > 0 else ""
        bloque = parts[1] if len(parts) > 1 else ""
        contexto = parts[2] if len(parts) > 2 else ""

        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None
        fecha = (datetime.fromtimestamp(mtime).date().isoformat()
                 if mtime else datetime.now().date().isoformat())
        kit_ids = extract_kit_ids(read_nota(path))
        metadata = note_metadata_from_frontmatter(get_frontmatter(path))

        props = {
            "Evento": {"title": [{"text": {"content": nota.get("nombre", "Nota")}}]},
            "Fecha": {"date": {"start": fecha}},
            "Archivo": _rich_text(nota.get("nombre", "")),
            "Ruta": _rich_text(rel),
            "Tipo": {"select": {"name": "Nota"}},
            "Detalle": _rich_text(path),
        }
        if kit_ids:
            props["KIT IDs"] = _rich_text(", ".join(kit_ids))
            if "KIT" in obs_props:
                props["KIT"] = {"relation": [{"id": normalize_notion_id(kit_id)} for kit_id in kit_ids]}
        props.update(obsidian_db_metadata_props(metadata, obs_props))
        props.update(obsidian_db_route_props(route_metadata_from_relative_path(rel), obs_props))
        if area in area_map:
            props["Area"] = {"relation": [{"id": area_map[area]}]}
        if bloque in bloque_map:
            props["Bloque"] = {"relation": [{"id": bloque_map[bloque]}]}
        if contexto in contexto_map:
            props["Contexto"] = {"relation": [{"id": contexto_map[contexto]}]}

        try:
            create_page(parent_id=db_id, title="OBSIDIAN", properties=props, is_data_source=True)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"[error] {rel}: {exc}", file=sys.stderr)
            errors += 1

    print(f"[backfill] creadas OK: {ok}")
    if errors:
        print(f"[backfill] errores: {errors}")
        return 1

    if args.sync and not _run_sync_obsidian():
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
