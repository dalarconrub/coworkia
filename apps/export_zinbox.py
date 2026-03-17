"""
Exporta todas las tareas de los proyectos Z-INBOX de Todoist
a una nueva base de datos "Backs-Todoist" en Notion.

Uso:
    python apps/export_zinbox.py --parent <PAGE_ID_NOTION>

Cómo obtener PAGE_ID_NOTION:
    1. Crea una página en Notion llamada "Backs" (o usa una existente)
    2. Compártela con tu integración: "..." > "Connections" > tu integración
    3. Copia el ID de la URL: notion.so/Tu-Pagina-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
       El ID son los últimos 32 caracteres (con o sin guiones)
"""

import sys
import os
import time
import argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

import requests
from tools.notion_tools import create_database, add_page_to_database

TODOIST_KEY = os.getenv("TODOIST_API_KEY")
TODOIST_BASE = "https://api.todoist.com/api/v1"

# Proyectos Z- a exportar
PROYECTOS_Z = {
    "6Mv5F76GQq3p699F": "Z-INBOX",
    "6JM9X2GhWRgR9M7v": "Z-TRASH",
    "6QR2xC8R9QjQgjqx": "Z-INBOXS",
    "6H3rFRr2HMhXxhXC": "Z-B01_TODOITS",
    "6MxJ3VRPhPP8FqW3": "Z-LIB",
}

SCHEMA_BACKS = {
    # ── Identificación ────────────────────────────────────────────────
    "Nombre":           {"title": {}},          # content limpio (sin Markdown)
    "Contenido_raw":    {"rich_text": {}},       # content original completo
    "Todoist_ID":       {"rich_text": {}},       # id de la tarea en Todoist
    # ── Fechas ────────────────────────────────────────────────────────
    "Fecha_due":        {"date": {}},            # due.date
    "Due_string":       {"rich_text": {}},       # due.string ("cada lun", etc.)
    "Deadline":         {"date": {}},            # deadline (campo separado de due)
    "Fecha_creacion":   {"date": {}},            # added_at
    "Exportado":        {"date": {}},            # fecha de esta exportación
    # ── Clasificación ─────────────────────────────────────────────────
    "Proyecto_origen":  {"select": {}},          # nombre del proyecto Z-
    "Prioridad":        {"select": {}},          # 1-4 → etiqueta legible
    "Etiquetas":        {"multi_select": {}},    # labels de Todoist
    "Es_recurrente":    {"checkbox": {}},        # due.is_recurring
    # ── Contenido ─────────────────────────────────────────────────────
    "URL":              {"url": {}},             # primera URL extraída
    "Descripcion":      {"rich_text": {}},       # description de la tarea
    # ── Estructura ────────────────────────────────────────────────────
    "Seccion_ID":       {"rich_text": {}},       # section_id
    "Padre_ID":         {"rich_text": {}},       # parent_id (subtareas)
}

PRIORIDAD_LABEL = {4: "❗ Urgente", 3: "⬆ Alta", 2: "⬇ Media", 1: "Normal"}


def _todoist_headers():
    return {"Authorization": f"Bearer {TODOIST_KEY}"}


def fetch_project_tasks(project_id: str) -> list[dict]:
    tareas, params = [], {"project_id": project_id, "limit": 200}
    while True:
        r = requests.get(f"{TODOIST_BASE}/tasks", headers=_todoist_headers(), params=params)
        r.raise_for_status()
        d = r.json()
        batch = d.get("results", d)
        tareas.extend(batch)
        cur = d.get("next_cursor")
        if not cur:
            break
        params["cursor"] = cur
    return tareas


def extract_url(content: str) -> str:
    """Extrae la primera URL de un contenido Markdown o texto plano."""
    import re
    # [texto](url)
    m = re.search(r'\]\((https?://[^\)]+)\)', content)
    if m:
        return m.group(1)
    # URL suelta
    m = re.search(r'https?://\S+', content)
    if m:
        return m.group(0)
    return ""


def clean_title(content: str) -> str:
    """Quita markdown de links del título, trunca a 100 chars."""
    import re
    # [texto](url) → texto
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    return content[:100].strip()


def task_to_notion_props(task: dict, project_name: str, fecha_hoy: str) -> dict:
    content  = task.get("content", "")
    due      = task.get("due") or {}
    deadline = task.get("deadline") or {}
    labels   = [{"name": l} for l in task.get("labels", [])]
    url      = extract_url(content)
    desc     = (task.get("description", "") or "")[:2000]

    # Fechas
    fecha_due      = due.get("date", "")[:10]      if due.get("date")      else None
    fecha_deadline = deadline.get("date", "")[:10] if deadline.get("date") else None
    added_at       = (task.get("added_at", "") or "")[:10] or None

    props = {
        # Identificación
        "Nombre":         {"title": [{"text": {"content": clean_title(content)}}]},
        "Contenido_raw":  {"rich_text": [{"text": {"content": content[:2000]}}]},
        "Todoist_ID":     {"rich_text": [{"text": {"content": task.get("id", "")}}]},
        # Clasificación
        "Proyecto_origen":{"select": {"name": project_name}},
        "Prioridad":      {"select": {"name": PRIORIDAD_LABEL.get(task.get("priority", 1), "Normal")}},
        "Es_recurrente":  {"checkbox": due.get("is_recurring", False)},
        # Fechas
        "Exportado":      {"date": {"start": fecha_hoy}},
    }

    if labels:
        props["Etiquetas"] = {"multi_select": labels}
    if url:
        props["URL"] = {"url": url}
    if desc:
        props["Descripcion"] = {"rich_text": [{"text": {"content": desc}}]}
    if fecha_due:
        props["Fecha_due"] = {"date": {"start": fecha_due}}
    if due.get("string"):
        props["Due_string"] = {"rich_text": [{"text": {"content": due["string"]}}]}
    if fecha_deadline:
        props["Deadline"] = {"date": {"start": fecha_deadline}}
    if added_at:
        props["Fecha_creacion"] = {"date": {"start": added_at}}
    if task.get("section_id"):
        props["Seccion_ID"] = {"rich_text": [{"text": {"content": task["section_id"]}}]}
    if task.get("parent_id"):
        props["Padre_ID"] = {"rich_text": [{"text": {"content": task["parent_id"]}}]}

    return props


def main(parent_page_id: str, proyectos: list[str], dry_run: bool):
    from datetime import date
    fecha_hoy = date.today().isoformat()

    # 1. Crear base de datos
    if not dry_run:
        print(f"Creando base de datos 'Backs-Todoist' en página {parent_page_id}...")
        db = create_database(parent_page_id, "Backs-Todoist", SCHEMA_BACKS)
        db_id = db["id"]
        print(f"  ✓ Base de datos creada: {db_id}\n")
    else:
        db_id = "DRY-RUN"
        print("(Dry run: no se crea nada en Notion)\n")

    # 2. Exportar tareas de cada proyecto
    total_ok = 0
    total_err = 0

    for proj_id in proyectos:
        proj_name = PROYECTOS_Z.get(proj_id, proj_id)
        print(f"Obteniendo tareas de {proj_name} ({proj_id})...")
        tareas = fetch_project_tasks(proj_id)
        print(f"  {len(tareas)} tareas encontradas")

        for i, t in enumerate(tareas, 1):
            try:
                props = task_to_notion_props(t, proj_name, fecha_hoy)
                if not dry_run:
                    add_page_to_database(db_id, props)
                    time.sleep(0.35)  # respetar rate limit Notion (3 req/s)
                total_ok += 1
                if i % 20 == 0:
                    print(f"    {i}/{len(tareas)} exportadas...")
            except Exception as e:
                total_err += 1
                print(f"  ✗ Error en tarea '{t.get('content','')[:40]}': {e}")

        print(f"  ✓ {len(tareas)} procesadas\n")

    print(f"{'─'*50}")
    print(f"  Exportadas: {total_ok}  |  Errores: {total_err}")
    if not dry_run:
        print(f"  Base de datos: https://notion.so/{db_id.replace('-','')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exporta Z-INBOX de Todoist a Notion")
    parser.add_argument("--parent", required=True,
                        help="ID de la página de Notion donde crear Backs-Todoist")
    parser.add_argument("--proyectos", nargs="*", default=list(PROYECTOS_Z.keys()),
                        help="IDs de proyectos Todoist a exportar (default: todos los Z-)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Muestra qué se haría sin escribir en Notion")
    args = parser.parse_args()

    # Normalizar ID (quitar guiones si viene de URL)
    parent_id = args.parent.replace("-", "")
    if len(parent_id) == 32:
        parent_id = f"{parent_id[:8]}-{parent_id[8:12]}-{parent_id[12:16]}-{parent_id[16:20]}-{parent_id[20:]}"

    main(parent_id, args.proyectos, args.dry_run)
