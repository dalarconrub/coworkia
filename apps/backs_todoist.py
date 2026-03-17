"""
BACK-Todoist — Crea la base de datos en Notion y exporta tareas de proyectos Z-.

Uso:
    python apps/backs_todoist.py --parent <PAGE_ID>
    python apps/backs_todoist.py --parent <PAGE_ID> --proyectos 6Mv5F76GQq3p699F
    python apps/backs_todoist.py --parent <PAGE_ID> --dry-run
"""

import sys, os, re, time, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date
from dotenv import load_dotenv
load_dotenv()

import requests
from tools.notion_tools import create_database, add_page_to_database

TODOIST_KEY  = os.getenv("TODOIST_API_KEY")
TODOIST_BASE = "https://api.todoist.com/api/v1"

PROYECTOS_Z = {
    "6Mv5F76GQq3p699F": "Z-INBOX",
    "6JM9X2GhWRgR9M7v": "Z-TRASH",
    "6QR2xC8R9QjQgjqx": "Z-INBOXS",
    "6H3rFRr2HMhXxhXC": "Z-B01_TODOITS",
    "6MxJ3VRPhPP8FqW3": "Z-LIB",
}

PRIORIDAD_LABEL = {4: "❗ Urgente", 3: "⬆ Alta", 2: "⬇ Media", 1: "Normal"}

SCHEMA = {
    # ── Identificación ────────────────────────────────────────────────
    "Nombre":           {"title": {}},
    "Contenido_raw":    {"rich_text": {}},
    "Todoist_ID":       {"rich_text": {}},
    # ── Contenido ─────────────────────────────────────────────────────
    "URL":              {"url": {}},
    "Descripcion":      {"rich_text": {}},
    # ── Clasificación ─────────────────────────────────────────────────
    "Proyecto_origen":  {"select": {}},
    "Prioridad":        {"select": {}},
    "Etiquetas":        {"multi_select": {}},
    "Es_recurrente":    {"checkbox": {}},
    # ── Fechas ────────────────────────────────────────────────────────
    "Fecha_due":        {"date": {}},
    "Due_string":       {"rich_text": {}},
    "Deadline":         {"date": {}},
    "Fecha_creacion":   {"date": {}},
    "Exportado":        {"date": {}},
    # ── Estructura interna ────────────────────────────────────────────
    "Seccion_ID":       {"rich_text": {}},
    "Padre_ID":         {"rich_text": {}},
}


def _headers():
    return {"Authorization": f"Bearer {TODOIST_KEY}"}


def fetch_project_tasks(project_id: str) -> list[dict]:
    tareas, params = [], {"project_id": project_id, "limit": 200}
    while True:
        r = requests.get(f"{TODOIST_BASE}/tasks", headers=_headers(), params=params)
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
    m = re.search(r'\]\((https?://[^\)]+)\)', content)
    url = m.group(1) if m else ""
    if not url:
        m = re.search(r'https?://\S+', content)
        url = m.group(0) if m else ""
    # Notion rechaza URLs con espacios o caracteres de control
    if url and any(c in url for c in (' ', '\n', '\t', '\r')):
        url = url.split()[0]  # truncar en el primer espacio
    return url


def clean_title(content: str) -> str:
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    return content[:100].strip()


def task_to_props(task: dict, project_name: str, fecha_hoy: str) -> dict:
    content  = task.get("content", "")
    due      = task.get("due") or {}
    deadline = task.get("deadline") or {}
    labels   = [{"name": l} for l in task.get("labels", [])]
    url      = extract_url(content)
    desc     = (task.get("description", "") or "")[:2000]

    fecha_due      = due.get("date", "")[:10]      if due.get("date")      else None
    fecha_deadline = deadline.get("date", "")[:10] if deadline.get("date") else None
    added_at       = (task.get("added_at", "") or "")[:10] or None

    props = {
        "Nombre":          {"title": [{"text": {"content": clean_title(content)}}]},
        "Contenido_raw":   {"rich_text": [{"text": {"content": content[:2000]}}]},
        "Todoist_ID":      {"rich_text": [{"text": {"content": task.get("id", "")}}]},
        "Proyecto_origen": {"select": {"name": project_name}},
        "Prioridad":       {"select": {"name": PRIORIDAD_LABEL.get(task.get("priority", 1), "Normal")}},
        "Es_recurrente":   {"checkbox": due.get("is_recurring", False)},
        "Exportado":       {"date": {"start": fecha_hoy}},
    }
    if url:
        props["URL"] = {"url": url}
    if desc:
        props["Descripcion"] = {"rich_text": [{"text": {"content": desc}}]}
    if labels:
        props["Etiquetas"] = {"multi_select": labels}
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


def main(parent_id: str, proyectos: list[str], dry_run: bool):
    fecha_hoy = date.today().isoformat()

    if not dry_run:
        print("Creando BACK-Todoist en Notion...")
        db = create_database(parent_id, "BACK-Todoist", SCHEMA)
        db_id = db["id"]
        props_creadas = list(db.get("properties", {}).keys())
        print(f"  ✓ {db_id}")
        print(f"  Props en DB: {props_creadas}\n")
    else:
        db_id = "DRY-RUN"
        print("(Dry run — no se escribe en Notion)\n")

    total_ok, total_err = 0, 0
    for proj_id in proyectos:
        proj_name = PROYECTOS_Z.get(proj_id, proj_id)
        print(f"→ {proj_name}...")
        tareas = fetch_project_tasks(proj_id)
        print(f"  {len(tareas)} tareas")
        for i, t in enumerate(tareas, 1):
            try:
                if not dry_run:
                    add_page_to_database(db_id, task_to_props(t, proj_name, fecha_hoy))
                    time.sleep(0.35)
                total_ok += 1
                if i % 25 == 0:
                    print(f"  {i}/{len(tareas)}...")
            except Exception as e:
                total_err += 1
                detail = ""
                if hasattr(e, "response") and e.response is not None:
                    try:
                        body = e.response.json()
                        detail = f" [{body.get('code','')}] {body.get('message','')[:150]}"
                    except Exception:
                        detail = f" {e.response.text[:150]}"
                print(f"  ✗ {t.get('content','')[:40]}: {e}{detail}")
        print(f"  ✓ {len(tareas)} procesadas")

    print(f"\n{'─'*50}")
    print(f"  OK: {total_ok}  |  Errores: {total_err}")
    if not dry_run:
        print(f"  → https://notion.so/{db_id.replace('-','')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exporta Z- de Todoist → BACK-Todoist en Notion")
    parser.add_argument("--parent",    required=True, help="ID de página Notion padre")
    parser.add_argument("--proyectos", nargs="*", default=list(PROYECTOS_Z.keys()))
    parser.add_argument("--dry-run",   action="store_true")
    args = parser.parse_args()

    pid = args.parent.replace("-", "")
    if len(pid) == 32:
        pid = f"{pid[:8]}-{pid[8:12]}-{pid[12:16]}-{pid[16:20]}-{pid[20:]}"
    main(pid, args.proyectos, args.dry_run)
