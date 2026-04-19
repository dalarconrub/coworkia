"""
Bootstrap idempotente: garantiza que cada data source Notion relevante tiene
la propiedad `Archivo: Checkbox`.

Es el paso previo obligatorio para `tools/reset_notion.py` (Fase 2 del sistema
de reseteo). No toca datos — solo schema.

Targets por defecto (Fase 2 MVP):
  - NOTION_DS_PROYECTOS
  - NOTION_DS_TAREAS
  - NOTION_DS_NOTAS
  - NOTION_DB_INX

Uso:
    python tools/ensure_archivo_field.py                 # todos los targets default
    python tools/ensure_archivo_field.py --dry-run       # solo informa, no PATCH
    python tools/ensure_archivo_field.py --targets proyectos,tareas
    python tools/ensure_archivo_field.py --property Archivado   # override nombre

Idempotente: si la propiedad ya existe, skip silencioso.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except Exception:
    pass

from tools.notion_tools import (  # noqa: E402
    get_data_source_schema,
    update_database_properties,
)

TARGETS = {
    "proyectos": "NOTION_DS_PROYECTOS",
    "tareas":    "NOTION_DS_TAREAS",
    "notas":     "NOTION_DS_NOTAS",
    "inx":       "NOTION_DB_INX",
}


def ensure_property(ds_id: str, property_name: str, dry_run: bool) -> tuple[str, str]:
    """Garantiza que la propiedad `property_name: Checkbox` existe en el data source.

    Devuelve (status, detalle). status ∈ {created, already, error}.
    """
    try:
        schema = get_data_source_schema(ds_id)
    except Exception as exc:
        return "error", f"get schema fallo: {exc}"

    props = schema.get("properties", []) or []
    if property_name in props:
        return "already", f"{schema.get('title', ds_id)} ya tiene '{property_name}'"

    if dry_run:
        return "created", f"{schema.get('title', ds_id)} [dry-run] PATCH con Checkbox '{property_name}'"

    try:
        update_database_properties(ds_id, {property_name: {"checkbox": {}}})
        return "created", f"{schema.get('title', ds_id)} PATCH OK: '{property_name}' anadida"
    except Exception as exc:
        return "error", f"{schema.get('title', ds_id)} PATCH fallo: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="No llama PATCH, solo informa")
    parser.add_argument(
        "--targets",
        default=",".join(TARGETS.keys()),
        help=f"Lista separada por comas: {', '.join(TARGETS.keys())} (default: todos)",
    )
    parser.add_argument("--property", default="Archivo", help="Nombre de la propiedad (default: Archivo)")
    args = parser.parse_args()

    requested = [t.strip() for t in args.targets.split(",") if t.strip()]
    unknown = [t for t in requested if t not in TARGETS]
    if unknown:
        raise SystemExit(f"Targets desconocidos: {unknown}. Validos: {list(TARGETS.keys())}")

    summary: dict[str, list[str]] = {"created": [], "already": [], "error": []}
    for target in requested:
        env_key = TARGETS[target]
        ds_id = os.getenv(env_key)
        if not ds_id:
            print(f"[skip] {target} ({env_key}): variable de entorno no definida")
            summary["error"].append(f"{target}: {env_key} vacio")
            continue
        status, detail = ensure_property(ds_id, args.property, args.dry_run)
        marker = {"created": "[OK]", "already": "[==]", "error": "[ERR]"}[status]
        print(f"{marker} {target}: {detail}")
        summary[status].append(f"{target}: {detail}")

    print()
    print(f"Resumen: creadas={len(summary['created'])} ya_existian={len(summary['already'])} errores={len(summary['error'])}")
    return 0 if not summary["error"] else 1


if __name__ == "__main__":
    sys.exit(main())
