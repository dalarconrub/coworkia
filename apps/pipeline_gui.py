"""
Pipeline Atlas GUI — navegador Tkinter del pipeline completo de Coworkia.

Cada nodo del arbol lateral muestra:
  - Descripcion breve y flow en texto plano.
  - Scripts (CLI / apps / tools) con ruta clicable (copia al portapapeles).
  - Artifacts que genera.
  - Variables de entorno requeridas (verde si presentes, rojo si faltan).
  - Casos de uso aplicables con enlace a docs/casos-de-uso/.
  - Comandos de ejemplo copiables.

Barra superior: chat del dia, ultimas 5 entradas del devlog, sprints activos,
salud de memory/ (OK/KO), ultima decision cerrada.

Read-only: no ejecuta pipelines. Para ejecutar, copia el comando y pegalo en
la terminal, o usa los launchers .bat existentes.

La fuente de verdad es docs/pipeline-atlas.md; esta GUI ofrece la vista con
estado vivo.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from dataclasses import dataclass, field
from datetime import date as Date
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except Exception:
    pass

# --- Theme (consistente con project_hub_gui.py) ---
BG = "#0b1020"
BG_PANEL = "#111827"
BG_CARD = "#172033"
BG_INPUT = "#09101d"
FG = "#e5e7eb"
FG_DIM = "#93a3b8"
ACCENT = "#2dd4bf"
ACCENT_ALT = "#38bdf8"
WARN = "#f59e0b"
ERR = "#f87171"
OK = "#34d399"
FONT = "Segoe UI"

DEVLOG_PATH = _ROOT / "devlog" / "DEVLOG.md"
CHATS_DIR = _ROOT / "chats"
SPRINTS_DIR = _ROOT / "artifacts" / "sprints"
MEMORY_DIR = _ROOT / "memory"
ATLAS_PATH = _ROOT / "docs" / "pipeline-atlas.md"


# ==================== MODELO: nodos del atlas ====================


@dataclass
class AtlasNode:
    key: str
    title: str
    category: str                              # "datos" | "coordinacion"
    summary: str                               # 1-2 frases
    flow_text: str                             # ASCII o markdown plano
    scripts: list[tuple[str, str]] = field(default_factory=list)   # (etiqueta, ruta)
    artifacts: list[str] = field(default_factory=list)
    env_vars: list[str] = field(default_factory=list)
    casos: list[tuple[str, str]] = field(default_factory=list)     # (numero, doc path)
    doc_path: str = ""                         # doc principal del dominio
    sample_cli: str = ""


def _build_atlas() -> list[AtlasNode]:
    return [
        # --- CAPA DE DATOS ---
        AtlasNode(
            key="mar",
            title="MAR — Todoist",
            category="datos",
            summary="Ejecucion diaria. Clasifica acciones por Idea/Meta/Habito/Tarea/Evento. "
                    "Dashboard, captura rapida, sync opcional a Notion.",
            flow_text=(
                "Captura (cualquier cliente Todoist)\n"
                "    v\n"
                "Clasificacion MAR (Idea/Meta/Habito/Tarea/Evento)\n"
                "    v\n"
                "Dashboard diario  →  sync_todoist_to_notion.py\n"
                "                         v\n"
                "                   NOTION_DB_TODOIST_TAREAS\n"
                "                         v\n"
                "                     INX-ENLACES"
            ),
            scripts=[
                ("CLI",  "agents/todoist_agent.py"),
                ("App",  "apps/dashboard.py"),
                ("App",  "apps/backs_todoist.py"),
                ("App",  "apps/mar_doctor.py"),
                ("Tool", "tools/todoist_tools.py"),
                ("Tool", "tools/sync_todoist_to_notion.py"),
                ("Tool", "tools/promote_notas_checkboxes_to_todoist.py"),
            ],
            artifacts=[
                "NOTION_DB_TODOIST_TAREAS (espejo en Notion)",
                "Entradas nuevas en INX por cada tarea sincronizada",
            ],
            env_vars=["TODOIST_API_KEY"],
            casos=[
                ("01", "docs/casos-de-uso/01-captura-todoist.md"),
                ("04", "docs/casos-de-uso/04-sync-inx-diario.md"),
                ("10", "docs/casos-de-uso/10-checkboxes-obsidian-a-todoist.md"),
            ],
            doc_path="docs/todoist-agent.md",
            sample_cli="python agents/todoist_agent.py resumen",
        ),
        AtlasNode(
            key="ptn",
            title="PTN — Notion proyectos/tareas/notas",
            category="datos",
            summary="Director formal. Tres data sources relacionados (Proyectos/Tareas/Notas) "
                    "con taxonomia ABC. Log de cambios alimenta INX.",
            flow_text=(
                "Input (nuevo proyecto/tarea/nota)\n"
                "    v\n"
                "notion_agent.py  →  NOTION_DS_PROYECTOS / TAREAS / NOTAS\n"
                "                         v (relations)\n"
                "                    log_ptn_changes.py\n"
                "                         v\n"
                "                   NOTION_DB_INX (INX-ENLACES)"
            ),
            scripts=[
                ("CLI",  "agents/notion_agent.py"),
                ("App",  "apps/project_hub_gui.py"),
                ("App",  "apps/notion_doctor.py"),
                ("App",  "apps/backs_notion.py"),
                ("Tool", "tools/log_ptn_changes.py"),
                ("Tool", "tools/migrate_ptn.py"),
                ("Tool", "tools/migrate_notas_ptn_relations.py"),
                ("Tool", "tools/cleanup_notas_legacy_props.py"),
                ("Tool", "tools/promote_obsidian_to_ptn.py"),
            ],
            artifacts=[
                "NOTION_DS_PROYECTOS/TAREAS/NOTAS (en Notion)",
                "Entradas `ptn:<page_id>` en INX-ENLACES",
            ],
            env_vars=[
                "NOTION_TOKEN",
                "NOTION_DS_PROYECTOS",
                "NOTION_DS_TAREAS",
                "NOTION_DS_NOTAS",
                "NOTION_DB_INX",
            ],
            casos=[
                ("02", "docs/casos-de-uso/02-captura-a-ptn.md"),
                ("03", "docs/casos-de-uso/03-obsidian-a-ptn.md"),
                ("07", "docs/casos-de-uso/07-migracion-tarea-a-ruta.md"),
            ],
            doc_path="docs/notion-ptn-agent.md",
            sample_cli='python agents/notion_agent.py estado',
        ),
        AtlasNode(
            key="kit",
            title="KIT — Knowledge / Information / Tools",
            category="datos",
            summary="Catalogo unico de conocimiento en Notion. Tipos Knowledge, Information, Tool "
                    "con subtipos (Concepto, Paper, App, ...). INX lo referencia como `kit:<page_id>`.",
            flow_text=(
                "kit_agent.py  →  NOTION_DB_KIT\n"
                "                      v\n"
                "              sync_inx_links.py --source kit\n"
                "                      v\n"
                "               INX-ENLACES (kit:<id>)"
            ),
            scripts=[
                ("CLI",  "agents/kit_agent.py"),
                ("App",  "apps/project_hub_gui.py"),
                ("Tool", "tools/sync_inx_links.py"),
            ],
            artifacts=["NOTION_DB_KIT (entradas)"],
            env_vars=["NOTION_TOKEN", "NOTION_DB_KIT"],
            casos=[("08", "docs/casos-de-uso/08-kit-en-inx.md")],
            doc_path="docs/notion-kit-agent.md",
            sample_cli='python agents/kit_agent.py estado',
        ),
        AtlasNode(
            key="rep",
            title="REP — GitHub → Notion",
            category="datos",
            summary="Catalogo de repositorios propios/referencia. Importa desde GitHub, "
                    "sincroniza metadata, permite catalogar por tipo/estado/proceso.",
            flow_text=(
                "GitHub API  →  github_agent.py importar\n"
                "                      v\n"
                "                NOTION_DB_REPOS\n"
                "                      ^\n"
                "           sincronizar  |  catalogar\n"
                "                      |\n"
                "                 github_gui.py"
            ),
            scripts=[
                ("CLI",  "agents/github_agent.py"),
                ("App",  "apps/github_gui.py"),
                ("App",  "apps/catalogar_repos.py"),
                ("Tool", "tools/github_tools.py"),
            ],
            artifacts=["NOTION_DB_REPOS (en Notion)"],
            env_vars=["GITHUB_TOKEN", "NOTION_DB_REPOS", "NOTION_REPOS_PARENT_PAGE"],
            casos=[("05", "docs/casos-de-uso/05-catalogo-github.md")],
            doc_path="docs/github-rep-agent.md",
            sample_cli='python agents/github_agent.py estado',
        ),
        AtlasNode(
            key="bib",
            title="BIB — Paperpile → GitHub → Notion → Obsidian",
            category="datos",
            summary="Bibliografia. Paperpile sincroniza library.bib a un repo GitHub privado; "
                    "bib_agent importa. Fichas de lectura se promueven al vault Obsidian.",
            flow_text=(
                "Paperpile  →  repo privado paperpile-lib (library.bib)\n"
                "                      v  (fetch_bibtex con GITHUB_TOKEN)\n"
                "              bib_agent.py importar\n"
                "                      v\n"
                "                NOTION_DB_BIB\n"
                "                      |\n"
                "              sincronizar / catalogar\n"
                "                      v\n"
                "        promote_bib_to_obsidian.py\n"
                "                      v\n"
                "   Vault: A1-INV/B13-PUB/<ctx>/<citekey>.md"
            ),
            scripts=[
                ("CLI",  "agents/bib_agent.py"),
                ("App",  "apps/bib_gui.py"),
                ("App",  "apps/promote_bib_to_obsidian.bat"),
                ("Tool", "tools/paperpile_tools.py"),
                ("Tool", "tools/promote_bib_to_obsidian.py"),
            ],
            artifacts=[
                "NOTION_DB_BIB (Notion)",
                "Fichas .md en vault bajo A1-INV/B13-PUB/",
                "INX `paperpile:<citekey>` y `obsidian:<path>`",
            ],
            env_vars=[
                "PAPERPILE_BIBTEX_URL",
                "GITHUB_TOKEN",
                "NOTION_DB_BIB",
                "NOTION_BIB_PARENT_PAGE",
                "OBSIDIAN_ALPHA_PATH",
            ],
            casos=[
                ("06", "docs/casos-de-uso/06-catalogo-paperpile.md"),
                ("09", "docs/casos-de-uso/09-bib-a-obsidian.md"),
            ],
            doc_path="docs/bib-agent.md",
            sample_cli='python agents/bib_agent.py estado',
        ),
        AtlasNode(
            key="abgd",
            title="ABGD — Obsidian vault",
            category="datos",
            summary="Almacen de pensamiento vivo. Jerarquia A→B→C→P→T→N (Area/Bloque/Contexto/"
                    "Proyecto/Tarea/Nota). Cambios se loguean a Notion y alimentan INX.",
            flow_text=(
                "Obsidian vault (OBSIDIAN_ABGD_ROOT)\n"
                "    <->  obsidian_agent.py (mapa/nueva/buscar/...)\n"
                "     v\n"
                "log_obsidian_changes.py  →  NOTION_OBSIDIAN_DB\n"
                "     v                             v\n"
                "backfill_obsidian_to_inx.py  →  sync_inx_links.py\n"
                "                                  v\n"
                "                              INX (obsidian:<path>)\n"
                "     |\n"
                "     v\n"
                "obsidian_wikilinks.py audit → detecta [[prefix:id]] y cruza con INX"
            ),
            scripts=[
                ("CLI",  "agents/obsidian_agent.py"),
                ("App",  "apps/backs_obsidian.py"),
                ("App",  "apps/promote_obsidian_to_ptn.bat"),
                ("Tool", "tools/obsidian_tools.py"),
                ("Tool", "tools/log_obsidian_changes.py"),
                ("Tool", "tools/backfill_obsidian_to_inx.py"),
                ("Tool", "tools/obsidian_wikilinks.py"),
            ],
            artifacts=[
                "Vault en OBSIDIAN_ABGD_ROOT (.md)",
                "NOTION_OBSIDIAN_DB (espejo eventos vault)",
                "INX `obsidian:<path>`",
            ],
            env_vars=["OBSIDIAN_ABGD_ROOT", "OBSIDIAN_ALPHA_PATH"],
            casos=[
                ("03", "docs/casos-de-uso/03-obsidian-a-ptn.md"),
                ("07", "docs/casos-de-uso/07-migracion-tarea-a-ruta.md"),
                ("09", "docs/casos-de-uso/09-bib-a-obsidian.md"),
                ("10", "docs/casos-de-uso/10-checkboxes-obsidian-a-todoist.md"),
                ("11", "docs/casos-de-uso/11-journal-diario-en-timeline.md"),
                ("12", "docs/casos-de-uso/12-backfill-inx-historico.md"),
                ("13", "docs/casos-de-uso/13-wikilinks-cross-system.md"),
            ],
            doc_path="docs/obsidian-agent.md",
            sample_cli='python agents/obsidian_agent.py estado',
        ),
        AtlasNode(
            key="inx",
            title="INX — Trazabilidad cross-system",
            category="datos",
            summary="BD Notion que mantiene una fila por entidad con clave canonica "
                    "(`paperpile:`, `obsidian:`, `todoist:`, `kit:`, `ptn:`, `github:`). "
                    "Es el glue entre todos los dominios.",
            flow_text=(
                "Fuentes:\n"
                "  sync_todoist_to_notion.py → TODOIST_DB_TAREAS\n"
                "  log_ptn_changes.py\n"
                "  kit_agent (via KIT)\n"
                "  log_obsidian_changes.py\n"
                "  bib_agent (via BIB)\n"
                "         v\n"
                "sync_inx_links.py --source all|todoist|notion|obsidian|kit|paperpile\n"
                "         v\n"
                "NOTION_DB_INX (INX-ENLACES)\n"
                "         v\n"
                "  inx_daily.py   →   artifacts/inx/inx-daily-YYYYMMDD-HHMMSS.md\n"
                "  inx_doctor.py"
            ),
            scripts=[
                ("App",  "apps/inx_daily.py"),
                ("App",  "apps/inx_doctor.py"),
                ("App",  "apps/inx_sync_notion.bat"),
                ("App",  "apps/inx_sync_obsidian.bat"),
                ("App",  "apps/inx_sync_todoist.bat"),
                ("Tool", "tools/sync_inx_links.py"),
            ],
            artifacts=[
                "NOTION_DB_INX (INX-ENLACES en Notion)",
                "artifacts/inx/inx-daily-*.md",
            ],
            env_vars=["NOTION_TOKEN", "NOTION_DB_INX"],
            casos=[
                ("04", "docs/casos-de-uso/04-sync-inx-diario.md"),
                ("08", "docs/casos-de-uso/08-kit-en-inx.md"),
                ("12", "docs/casos-de-uso/12-backfill-inx-historico.md"),
                ("13", "docs/casos-de-uso/13-wikilinks-cross-system.md"),
            ],
            doc_path="",
            sample_cli='python tools/sync_inx_links.py --source all --limit 200',
        ),
        # --- CAPA DE COORDINACION ---
        AtlasNode(
            key="chat",
            title="Chat multiagente",
            category="coordinacion",
            summary="Un fichero por dia (chats/chat_YYYY-MM-DD.md). Append-only, UTF-8. "
                    "Formato `**Actor:** msg` con marcadores MEMORIA:/BLOQUEO:/SIGUIENTE: y "
                    "modos VOTO/EVAL/CERRADO.",
            flow_text=(
                "init_chat.py  →  chats/chat_<hoy>.md  (crea desde plantilla + briefing)\n"
                "         v\n"
                "Conversacion: David + Claude + Copilot + Codex + Root/Sub\n"
                "         v\n"
                "sync-chat-memory  →  artifacts/multiagent/*  +  memory/SNAPSHOT.md\n"
                "         |\n"
                "         v\n"
                "fix_chat_mojibake.py (si PowerShell rompio UTF-8)"
            ),
            scripts=[
                ("Tool", "tools/init_chat.py"),
                ("Tool", "tools/fix_chat_mojibake.py"),
                ("Tool", "tools/sync_chat_memory.py (wrap: orchestrator sync-chat-memory)"),
                ("Doc",  "multiagents/chat_template.md"),
            ],
            artifacts=[
                "chats/chat_YYYY-MM-DD.md",
                "artifacts/multiagent/ (derivado por sync-chat-memory)",
            ],
            env_vars=[],
            casos=[],
            doc_path=".claude/multiagent.md",
            sample_cli='python tools/init_chat.py',
        ),
        AtlasNode(
            key="devlog",
            title="Devlog — hitos feature-level",
            category="coordinacion",
            summary="Registro append-only de hitos (no por commit). Obligatorio tras CERRADO, "
                    "MEMORIA operativa, feature completa, BLOQUEO/UNBLOCKED, REVERT.",
            flow_text=(
                "Hito detectado por agente\n"
                "    v\n"
                "devlog.py append --agent <X> --area <AREA> --status <S>\n"
                "                 --title '...' --summary '...'\n"
                "                 [--commits ...] [--refs 'CERRADO #N']\n"
                "                 [--sprint '<slug>']\n"
                "    v\n"
                "devlog/DEVLOG.md (entry cronologica)\n"
                "    v (cruce)\n"
                "timeline.py (agrupa por fecha)\n"
                "memory_check.py (opcional, valida memory)"
            ),
            scripts=[
                ("Tool", "tools/devlog.py"),
                ("Tool", "tools/timeline.py"),
                ("Tool", "tools/memory_check.py"),
            ],
            artifacts=["devlog/DEVLOG.md"],
            env_vars=[],
            casos=[],
            doc_path=".claude/multiagent.md",
            sample_cli='python tools/devlog.py view --limit 10',
        ),
        AtlasNode(
            key="memory",
            title="Memoria curada del proyecto",
            category="coordinacion",
            summary="Carpeta memory/ con INDEX, PURPOSE, STRUCTURE (hibrido), ROSTER, SNAPSHOT. "
                    "PASO 1 de lectura para todo agente al arrancar.",
            flow_text=(
                "memory/INDEX.md      ← meta-indice (manual)\n"
                "memory/PURPOSE.md    ← vision (manual)\n"
                "memory/STRUCTURE.md  ← narrativa + TREE auto (snapshot_structure.py)\n"
                "memory/ROSTER.md     ← subagentes Root/Sub (manual)\n"
                "memory/SNAPSHOT.md   ← auto (sync-chat-memory agrega MEMORIA/BLOQUEO/SIGUIENTE)\n"
                "         v\n"
                "memory_check.py  ← valida ficheros + enlaces + TREE freshness"
            ),
            scripts=[
                ("Tool", "tools/snapshot_structure.py"),
                ("Tool", "tools/memory_check.py"),
                ("Tool", "tools/sync_chat_memory.py"),
            ],
            artifacts=["memory/*.md"],
            env_vars=[],
            casos=[],
            doc_path="memory/INDEX.md",
            sample_cli='python tools/memory_check.py',
        ),
        AtlasNode(
            key="timeline",
            title="Timeline agregado por fecha",
            category="coordinacion",
            summary="Vista temporal read-only que cruza chat + devlog + INX + sprints + "
                    "journal Obsidian. Regenerable.",
            flow_text=(
                "Para un dia D:\n"
                "   chats/chat_<D>.md\n"
                "   devlog/DEVLOG.md (entradas con ts startswith D)\n"
                "   artifacts/inx/inx-daily-<D>-*.md\n"
                "   artifacts/sprints/*.json (start <= D <= end)\n"
                "   Vault: A0-GTD/B0C-PLA/C0C9-Notas/N<yymmdd>-*.md\n"
                "        v\n"
                "   timeline.py build_daily + render_daily\n"
                "        v\n"
                "   artifacts/daily/<D>.md"
            ),
            scripts=[("Tool", "tools/timeline.py")],
            artifacts=["artifacts/daily/YYYY-MM-DD.md"],
            env_vars=["OBSIDIAN_ALPHA_PATH (opcional, para journal)"],
            casos=[("11", "docs/casos-de-uso/11-journal-diario-en-timeline.md")],
            doc_path="docs/multiagent-system.md",
            sample_cli='python tools/timeline.py',
        ),
        AtlasNode(
            key="sprints",
            title="Sprints — planificacion Scrum",
            category="coordinacion",
            summary="plan-sprint genera SprintPlan (roles Scrum + squad multiagente + backlog + "
                    "task board) desde objetivo en lenguaje natural. Persiste a artifacts/sprints/.",
            flow_text=(
                "orchestrator_agent.py plan-sprint 'Objetivo' --nombre 'Sprint X' --guardar\n"
                "                                    ^\n"
                "                         planner.py + registry.py\n"
                "                                    v\n"
                "                           artifacts/sprints/<slug>.md + .json\n"
                "                                    v\n"
                "              status / run-task / run-sprint\n"
                "                                    v\n"
                "                   timeline.py (muestra sprints activos por dia)\n"
                "                   devlog --sprint <slug> (cruce)"
            ),
            scripts=[
                ("CLI",  "agents/orchestrator_agent.py"),
                ("Lib",  "multiagents/planner.py"),
                ("Lib",  "multiagents/registry.py"),
                ("Lib",  "multiagents/artifacts.py"),
                ("Lib",  "multiagents/models.py"),
            ],
            artifacts=[
                "artifacts/sprints/<slug>.md",
                "artifacts/sprints/<slug>.json",
            ],
            env_vars=[],
            casos=[],
            doc_path="docs/multiagent-system.md",
            sample_cli='python agents/orchestrator_agent.py agentes',
        ),
        AtlasNode(
            key="reset_all",
            title="Reset General — MAR + Notion + Obsidian encadenados (Fase 4)",
            category="coordinacion",
            summary="Orquestador que ejecuta las 3 fases en orden (MAR -> Notion -> Obsidian). "
                    "Subprocess chain, abortable, con confirmacion interactiva y plan previo. "
                    "Obsidian skipea salvo que pases --obsidian-new-vault-path.",
            flow_text=(
                "Plan (print) → Confirmacion [y/N] → Ejecucion:\n"
                "  1. Fase 1 MAR: python tools/reset_mar.py reset-all [--dry-run] [--limit N]\n"
                "  2. Fase 2 Notion: python tools/reset_notion.py reset-ptn-all --snapshot\n"
                "  3. Fase 3 Obsidian: python tools/reset_obsidian.py rotate \\\n"
                "                      --new-vault-path <path> --snapshot\n"
                "         v\n"
                "Politica de fallo: si Fase N falla, ABORT (no avanza a N+1).\n"
                "Imprime comandos de restore para recuperar lo ejecutado.\n"
                "         v\n"
                "--dry-run: propaga a las 3 fases, nada se escribe.\n"
                "--yes    : sin confirmacion (scripteable).\n"
                "--skip-*: saltar una fase individual.\n"
                "Obsidian skipea automaticamente sin --obsidian-new-vault-path (seguridad)."
            ),
            scripts=[
                ("Tool", "tools/reset_all.py"),
                ("App",  "apps/reset_all.bat"),
            ],
            artifacts=[
                "Snapshots heredados: artifacts/resets/YYYY-MM-DD/ptn-*, obsidian-rotate-*",
                "MAR reversible via marker en description (sin snapshot adicional)",
            ],
            env_vars=[
                "TODOIST_API_KEY",
                "NOTION_TOKEN",
                "NOTION_DS_PROYECTOS",
                "NOTION_DS_TAREAS",
                "NOTION_DS_NOTAS",
                "NOTION_DB_INX",
                "OBSIDIAN_ABGD_ROOT",
            ],
            casos=[],
            doc_path="docs/pipeline-atlas.md",
            sample_cli='python tools/reset_all.py --dry-run',
        ),
        AtlasNode(
            key="reset_obsidian",
            title="Reset Obsidian — rotar vault (Fase 3)",
            category="coordinacion",
            summary="Crea un vault nuevo como sibling con la estructura canonica replicada "
                    "(depth default 3) y `.obsidian/` copiada. El vault viejo queda intacto. "
                    "Propaga Archivo=true a todas las filas INX obsidian:*. Requiere editar "
                    "OBSIDIAN_ABGD_ROOT manualmente al terminar.",
            flow_text=(
                "Prerrequisito: propiedad 'Archivo: Checkbox' en NOTION_DB_INX.\n"
                "               python tools/ensure_archivo_field.py\n"
                "         v\n"
                "Rotate --new-vault-path <path> [--depth N] [--dry-run] [--snapshot]:\n"
                "  1. Replica estructura de carpetas del viejo al nuevo hasta depth N\n"
                "     (default 3 = Area -> Bloque -> Contexto). Sin ficheros .md.\n"
                "  2. Copia .obsidian/ completa (plugins, hotkeys, themes, snippets).\n"
                "  3. Flip Archivo=true en toda fila INX con Clave 'obsidian:...'.\n"
                "  4. Imprime la linea que debes poner en .env: OBSIDIAN_ABGD_ROOT=<nuevo>.\n"
                "         v\n"
                "status            muestra vault actual + top-level + Archivo en INX\n"
                "list-archived     lista filas INX obsidian:* con Archivo=true\n"
                "restore --from <old>   flip Archivo=false + lista notas nuevas del vault activo\n"
                "                       para migracion manual antes de cambiar .env"
            ),
            scripts=[
                ("Tool", "tools/reset_obsidian.py"),
                ("App",  "apps/reset_obsidian.bat"),
            ],
            artifacts=[
                "Nuevo vault en --new-vault-path con estructura vacia + .obsidian/",
                "Filas INX obsidian:* marcadas Archivo=true (reversible)",
                "Snapshot opcional artifacts/resets/YYYY-MM-DD/obsidian-rotate-<ts>.json",
            ],
            env_vars=[
                "OBSIDIAN_ABGD_ROOT",
                "NOTION_TOKEN",
                "NOTION_DB_INX",
            ],
            casos=[],
            doc_path="docs/pipeline-atlas.md",
            sample_cli='python tools/reset_obsidian.py status',
        ),
        AtlasNode(
            key="reset_notion",
            title="Reset Notion — checkbox Archivo en PTN + INX (Fase 2)",
            category="coordinacion",
            summary="Activa un Checkbox 'Archivo' paralelo en PTN Proyectos/Tareas/Notas "
                    "(sin tocar el Estado existente) y propaga el flag a la BD INX. "
                    "Reversible con `restore` y `restore-all`. Requiere bootstrap previo.",
            flow_text=(
                "Bootstrap (una vez):\n"
                "  python tools/ensure_archivo_field.py\n"
                "  -> anade propiedad 'Archivo: Checkbox' a PTN Proyectos, PTN Tareas,\n"
                "     PTN Notas y NOTION_DB_INX (idempotente).\n"
                "         v\n"
                "Reset:\n"
                "  reset-ptn-{proyectos|tareas|notas|all} [--snapshot] [--dry-run] [--limit]\n"
                "  Para cada pagina PTN con Archivo!=true:\n"
                "    1. (opt) snapshot -> artifacts/resets/YYYY-MM-DD/ptn-<t>-<ts>.json\n"
                "    2. update_page_properties(page_id, Archivo=true)\n"
                "    3. buscar INX con Clave 'ptn:<page_id>' -> update_page_properties Archivo=true\n"
                "         v\n"
                "restore <page_id>       flip a false + propaga a INX\n"
                "restore-all --target <t>  idem masivo\n"
                "list-archived --target all"
            ),
            scripts=[
                ("Tool", "tools/ensure_archivo_field.py"),
                ("Tool", "tools/reset_notion.py"),
                ("App",  "apps/reset_notion.bat"),
            ],
            artifacts=[
                "Propiedad 'Archivo: Checkbox' anadida a PTN data sources y a NOTION_DB_INX",
                "Snapshots opcionales en artifacts/resets/YYYY-MM-DD/ptn-<target>-<ts>.json",
                "Paginas PTN marcadas Archivo=true (reversible con restore)",
            ],
            env_vars=[
                "NOTION_TOKEN",
                "NOTION_DS_PROYECTOS",
                "NOTION_DS_TAREAS",
                "NOTION_DS_NOTAS",
                "NOTION_DB_INX",
            ],
            casos=[],
            doc_path="docs/pipeline-atlas.md",
            sample_cli='python tools/reset_notion.py reset-ptn-proyectos --dry-run --snapshot',
        ),
        AtlasNode(
            key="reset_mar",
            title="Reset MAR — archivar Todoist a Z-INBOX (Fase 1)",
            category="coordinacion",
            summary="Archiva tareas Todoist al proyecto Z-INBOX sin cerrarlas, preservando el "
                    "proyecto origen para permitir restore. Filtros por tipo MAR, proyecto, "
                    "label, overdue. Idempotente, reversible, con --dry-run.",
            flow_text=(
                "Seleccion (reset-all / by-type / by-project / by-label / overdue)\n"
                "         v\n"
                "Filtro: excluye Z-* y tareas ya con marker [ARCHIVED: ...]\n"
                "         v\n"
                "Para cada tarea:\n"
                "  1. Append marker a description: [ARCHIVED: YYYY-MM-DD | orig-project: <id>]\n"
                "  2. update_task(task_id, description=new_desc)\n"
                "  3. move_task(task_id, project_id=Z-INBOX)\n"
                "         v\n"
                "list-archived  →  tareas en Z-INBOX con marker\n"
                "restore <id>   →  parsea marker, devuelve al proyecto origen, limpia marker\n"
                "restore-all [--from YYYY-MM-DD]  →  idem masivo"
            ),
            scripts=[
                ("Tool", "tools/reset_mar.py"),
                ("App",  "apps/reset_mar.bat"),
            ],
            artifacts=[
                "Tareas movidas al proyecto Todoist Z-INBOX (id 6Mv5F76GQq3p699F)",
                "Marker [ARCHIVED: ...] insertado en description (reversible)",
            ],
            env_vars=["TODOIST_API_KEY"],
            casos=[],
            doc_path="docs/pipeline-atlas.md",
            sample_cli='python tools/reset_mar.py reset-all --dry-run',
        ),
        AtlasNode(
            key="subagentes",
            title="Subagentes Root/Sub",
            category="coordinacion",
            summary="Identidad de primera clase para subagentes. Convencion `Root/Sub` donde "
                    "Root ∈ {Claude, Copilot, Codex}. Ej: Claude/KIT, Codex/ABGD.",
            flow_text=(
                "Declaracion manual: memory/ROSTER.md (foco + invocacion)\n"
                "         v\n"
                "Uso en chat: **Claude/KIT:** mensaje\n"
                "Mencion:     @Claude (coordinador) vs @Claude/KIT (subagente)\n"
                "         v\n"
                "chat_memory.py build_agent_states descubre subagentes automaticamente\n"
                "devlog.py append --agent Claude/KIT --area ... (validado por patron)\n"
                "         v\n"
                "Responsabilidad de escritura: coordinador escribe por el hijo\n"
                "(si el hijo no tiene interfaz propia, caso Agent tool de Claude Code)"
            ),
            scripts=[
                ("Doc",  "memory/ROSTER.md"),
                ("Lib",  "multiagents/chat_memory.py"),
                ("Tool", "tools/devlog.py"),
            ],
            artifacts=["Entradas en memory/ROSTER.md (manual)"],
            env_vars=[],
            casos=[],
            doc_path=".claude/multiagent.md",
            sample_cli='python tools/devlog.py view --agent Codex/ABGD',
        ),
    ]


# ==================== ESTADO VIVO (barra superior) ====================


def _last_devlog_entries(n: int = 5) -> list[str]:
    if not DEVLOG_PATH.exists():
        return []
    text = DEVLOG_PATH.read_text(encoding="utf-8")
    header_re = re.compile(
        r"^## (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z) \u2014 (?P<agent>\S+) \u2014 \[(?P<area>\w+)\] (?P<title>.+)$"
    )
    entries: list[dict] = []
    in_code = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = header_re.match(line)
        if m:
            entries.append({
                "ts": m.group("ts"),
                "agent": m.group("agent"),
                "area": m.group("area"),
                "title": m.group("title"),
            })
    return entries[-n:]


def _active_sprints() -> list[dict]:
    if not SPRINTS_DIR.exists():
        return []
    today = Date.today()
    active = []
    for p in sorted(SPRINTS_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        plan = data.get("plan") if isinstance(data, dict) else None
        if not plan:
            continue
        try:
            start = Date.fromisoformat(str(plan.get("start_date", ""))[:10])
            end = Date.fromisoformat(str(plan.get("end_date", ""))[:10])
        except Exception:
            continue
        if start <= today <= end:
            active.append({
                "name": plan.get("sprint_name", p.stem),
                "status": plan.get("status", ""),
                "start": start.isoformat(),
                "end": end.isoformat(),
            })
    return active


def _memory_health() -> tuple[bool, str]:
    script = _ROOT / "tools" / "memory_check.py"
    if not script.exists():
        return False, "memory_check.py no existe"
    try:
        r = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=_ROOT,
        )
        ok = r.returncode == 0
        msg = (r.stdout or r.stderr or "").strip().splitlines()
        return ok, msg[-1] if msg else ("OK" if ok else "KO")
    except Exception as exc:
        return False, f"error: {exc}"


def _today_chat() -> Path | None:
    p = CHATS_DIR / f"chat_{Date.today().isoformat()}.md"
    return p if p.exists() else None


# ==================== GUI ====================


class PipelineAtlasGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Coworkia Pipeline Atlas")
        self.root.geometry("1480x900")
        self.root.minsize(1200, 720)
        self.root.configure(bg=BG)
        self.atlas = _build_atlas()
        self.nodes_by_key = {n.key: n for n in self.atlas}
        self.current_key: str | None = None
        self._build_styles()
        self._build_layout()
        self.refresh_status()
        # Select first node by default
        if self.atlas:
            self._select_node(self.atlas[0].key)

    # -- styling --

    def _build_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", background=BG, foreground=FG, font=(FONT, 10))
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("TLabel", background=BG, foreground=FG, font=(FONT, 10))
        style.configure("Header.TLabel", background=BG, foreground=ACCENT, font=(FONT, 13, "bold"))
        style.configure("Dim.TLabel", background=BG, foreground=FG_DIM, font=(FONT, 9))
        style.configure("Section.TLabel", background=BG_PANEL, foreground=ACCENT_ALT, font=(FONT, 11, "bold"))
        style.configure("OK.TLabel", background=BG, foreground=OK, font=(FONT, 9, "bold"))
        style.configure("Warn.TLabel", background=BG, foreground=WARN, font=(FONT, 9, "bold"))
        style.configure("Err.TLabel", background=BG, foreground=ERR, font=(FONT, 9, "bold"))
        style.configure("Treeview",
                        background=BG_PANEL, foreground=FG,
                        fieldbackground=BG_PANEL, font=(FONT, 10),
                        rowheight=24, borderwidth=0)
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", BG)])
        style.configure("TButton", font=(FONT, 9), padding=(10, 4))
        style.configure("TSeparator", background=FG_DIM)

    # -- layout --

    def _build_layout(self):
        # Top status bar
        self.status_bar = ttk.Frame(self.root, style="Panel.TFrame")
        self.status_bar.pack(side=tk.TOP, fill=tk.X)
        self.status_bar.configure(padding=(12, 8))
        self._build_status_bar()

        ttk.Separator(self.root, orient="horizontal").pack(side=tk.TOP, fill=tk.X)

        # Main area: left tree + right detail
        main = ttk.Frame(self.root)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left — tree
        left = ttk.Frame(main, style="Panel.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0))
        left.configure(padding=(8, 8))

        ttk.Label(left, text="Pipeline Atlas", style="Header.TLabel").pack(anchor=tk.W, padx=4, pady=(0, 6))

        self.tree = ttk.Treeview(left, show="tree", selectmode="browse", height=30)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._populate_tree()

        refresh_btn = ttk.Button(left, text="Refrescar estado", command=self.refresh_status)
        refresh_btn.pack(fill=tk.X, pady=(8, 0))

        atlas_btn = ttk.Button(left, text="Abrir pipeline-atlas.md",
                               command=lambda: self._open_path(ATLAS_PATH))
        atlas_btn.pack(fill=tk.X, pady=(4, 0))

        # Right — detail
        right = ttk.Frame(main)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 10), pady=(6, 6))

        # Detail is a canvas with scrollbar for long content
        self.detail_canvas = tk.Canvas(right, bg=BG, highlightthickness=0, bd=0)
        self.detail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.detail_canvas.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_canvas.configure(yscrollcommand=sb.set)

        self.detail_frame = tk.Frame(self.detail_canvas, bg=BG)
        self._detail_window = self.detail_canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")
        self.detail_frame.bind("<Configure>", self._on_detail_configure)
        self.detail_canvas.bind("<Configure>", self._on_canvas_configure)
        self.detail_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _populate_tree(self):
        root_d = self.tree.insert("", "end", iid="cat:datos", text="Capa de datos", open=True)
        root_c = self.tree.insert("", "end", iid="cat:coordinacion", text="Capa de coordinacion", open=True)
        for node in self.atlas:
            parent = root_d if node.category == "datos" else root_c
            self.tree.insert(parent, "end", iid=f"node:{node.key}", text=node.title)

    # -- status bar --

    def _build_status_bar(self):
        # Fila 1: fecha, chat, memoria
        row1 = ttk.Frame(self.status_bar, style="Panel.TFrame")
        row1.pack(fill=tk.X)
        self.lbl_date = tk.Label(row1, text="", bg=BG_PANEL, fg=ACCENT, font=(FONT, 10, "bold"))
        self.lbl_date.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_chat = tk.Label(row1, text="", bg=BG_PANEL, fg=FG, font=(FONT, 9))
        self.lbl_chat.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_memory = tk.Label(row1, text="", bg=BG_PANEL, fg=FG_DIM, font=(FONT, 9, "bold"))
        self.lbl_memory.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_sprints = tk.Label(row1, text="", bg=BG_PANEL, fg=FG_DIM, font=(FONT, 9))
        self.lbl_sprints.pack(side=tk.LEFT, padx=(0, 14))

        # Fila 2: ultimas entradas devlog (una linea compacta)
        row2 = ttk.Frame(self.status_bar, style="Panel.TFrame")
        row2.pack(fill=tk.X, pady=(6, 0))
        tk.Label(row2, text="Devlog reciente:", bg=BG_PANEL, fg=FG_DIM, font=(FONT, 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.lbl_devlog = tk.Label(row2, text="", bg=BG_PANEL, fg=FG, font=(FONT, 9), anchor="w", justify=tk.LEFT)
        self.lbl_devlog.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def refresh_status(self):
        self.lbl_date.config(text=f"Hoy: {Date.today().isoformat()}")

        chat = _today_chat()
        if chat:
            self.lbl_chat.config(text=f"Chat: {chat.name}", fg=OK)
        else:
            self.lbl_chat.config(text="Chat: (no creado - corre init_chat.py)", fg=WARN)

        ok, msg = _memory_health()
        if ok:
            self.lbl_memory.config(text="Memoria: OK", fg=OK)
        else:
            self.lbl_memory.config(text=f"Memoria: KO — {msg[:80]}", fg=ERR)

        sprints = _active_sprints()
        if sprints:
            names = ", ".join(s["name"] for s in sprints[:3])
            self.lbl_sprints.config(text=f"Sprints activos: {len(sprints)} ({names})", fg=ACCENT_ALT)
        else:
            self.lbl_sprints.config(text="Sprints activos: 0", fg=FG_DIM)

        entries = _last_devlog_entries(5)
        if entries:
            parts = [f"[{e['area']}] {e['title'][:50]}" for e in entries]
            self.lbl_devlog.config(text="  |  ".join(parts))
        else:
            self.lbl_devlog.config(text="(sin entradas)")

        self.root.after(60_000, self.refresh_status)  # auto-refresh cada 60 s

    # -- scroll plumbing --

    def _on_detail_configure(self, _event):
        self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.detail_canvas.itemconfig(self._detail_window, width=event.width)

    def _on_mousewheel(self, event):
        delta = -1 * int(event.delta / 120) if event.delta else 0
        self.detail_canvas.yview_scroll(delta, "units")

    # -- tree selection --

    def _on_tree_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        if iid.startswith("node:"):
            key = iid.split(":", 1)[1]
            if key != self.current_key:
                self._render_node(key)

    def _select_node(self, key: str):
        """Selecciona programaticamente. Usa selection_set con guard para evitar
        re-disparar <<TreeviewSelect>> en loop."""
        if key == self.current_key:
            return
        target = f"node:{key}"
        current_sel = self.tree.selection()
        if not current_sel or current_sel[0] != target:
            # Esto dispara <<TreeviewSelect>> una unica vez, que llamara a
            # _render_node con el guard de current_key.
            self.tree.selection_set(target)
        else:
            self._render_node(key)

    def _render_node(self, key: str):
        """Aplica la seleccion y pinta el panel derecho. Llamado desde el handler
        del tree o desde _select_node cuando la seleccion no cambia."""
        node = self.nodes_by_key.get(key)
        if not node:
            return
        self.current_key = key
        self._render_detail(node)

    # -- detail rendering --

    def _render_detail(self, node: AtlasNode):
        for child in self.detail_frame.winfo_children():
            child.destroy()

        f = self.detail_frame

        # Header
        hdr = tk.Frame(f, bg=BG)
        hdr.pack(fill=tk.X, pady=(4, 0))
        tk.Label(hdr, text=node.title, bg=BG, fg=ACCENT, font=(FONT, 16, "bold")).pack(side=tk.LEFT, padx=(6, 0))
        tk.Label(hdr, text=f"  [{node.category}]", bg=BG, fg=FG_DIM, font=(FONT, 10)).pack(side=tk.LEFT)

        # Botones top
        actions = tk.Frame(f, bg=BG)
        actions.pack(fill=tk.X, pady=(6, 10), padx=6)
        if node.doc_path:
            ttk.Button(actions, text=f"Abrir {node.doc_path}",
                       command=lambda: self._open_path(_ROOT / node.doc_path)).pack(side=tk.LEFT, padx=(0, 6))
        if node.sample_cli:
            ttk.Button(actions, text="Copiar CLI de ejemplo",
                       command=lambda: self._copy_to_clipboard(node.sample_cli)).pack(side=tk.LEFT, padx=(0, 6))

        # Resumen
        self._section(f, "Resumen")
        self._paragraph(f, node.summary)

        # Flow
        self._section(f, "Flow")
        self._code_block(f, node.flow_text)

        # Scripts
        self._section(f, "Scripts / entry points")
        for label, path in node.scripts:
            self._script_row(f, label, path)

        # Artifacts
        if node.artifacts:
            self._section(f, "Artifacts que genera")
            for a in node.artifacts:
                self._bullet(f, a)

        # Env vars
        self._section(f, "Variables de entorno")
        if not node.env_vars:
            self._dim(f, "(ninguna requerida)")
        else:
            for var in node.env_vars:
                name = var.split(" ", 1)[0]
                present = bool(os.getenv(name))
                self._env_row(f, var, present)

        # Casos de uso
        if node.casos:
            self._section(f, "Casos de uso aplicables")
            for num, path in node.casos:
                self._caso_row(f, num, path)

        # Sample CLI
        if node.sample_cli:
            self._section(f, "Ejemplo de invocacion")
            self._code_block(f, node.sample_cli)

    # -- render helpers --

    def _section(self, parent, title: str):
        frame = tk.Frame(parent, bg=BG_PANEL)
        frame.pack(fill=tk.X, pady=(12, 2), padx=0)
        tk.Label(frame, text=title, bg=BG_PANEL, fg=ACCENT_ALT,
                 font=(FONT, 11, "bold"), padx=10, pady=4).pack(anchor=tk.W)

    def _paragraph(self, parent, text: str):
        tk.Label(parent, text=text, bg=BG, fg=FG, font=(FONT, 10),
                 wraplength=1000, justify=tk.LEFT, anchor="w").pack(fill=tk.X, padx=12, pady=(2, 0))

    def _dim(self, parent, text: str):
        tk.Label(parent, text=text, bg=BG, fg=FG_DIM, font=(FONT, 9, "italic")).pack(anchor=tk.W, padx=12, pady=2)

    def _bullet(self, parent, text: str):
        tk.Label(parent, text=f"•  {text}", bg=BG, fg=FG, font=(FONT, 10),
                 anchor="w", justify=tk.LEFT, wraplength=1000).pack(fill=tk.X, padx=24, pady=1)

    def _code_block(self, parent, text: str):
        w = tk.Text(parent, bg=BG_CARD, fg=FG, font=("Consolas", 9),
                    height=max(3, min(18, text.count("\n") + 2)),
                    relief=tk.FLAT, padx=10, pady=6, wrap="none")
        w.insert("1.0", text)
        w.configure(state=tk.DISABLED)
        w.pack(fill=tk.X, padx=12, pady=4)

    def _script_row(self, parent, label: str, path: str):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, padx=12, pady=1)
        tk.Label(row, text=f"[{label}]", bg=BG, fg=ACCENT_ALT, font=(FONT, 9, "bold"), width=8, anchor="w").pack(side=tk.LEFT)
        tk.Label(row, text=path, bg=BG, fg=FG, font=("Consolas", 9), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Copiar", width=9,
                   command=lambda p=path: self._copy_to_clipboard(p)).pack(side=tk.RIGHT, padx=(4, 0))
        real = _ROOT / path.split(" ", 1)[0]
        if real.exists():
            ttk.Button(row, text="Abrir", width=9,
                       command=lambda p=real: self._open_path(p)).pack(side=tk.RIGHT)
            if real.suffix.lower() in {".py", ".bat"}:
                ttk.Button(row, text="Ejecutar", width=9,
                           command=lambda p=real: self._execute_script(p)).pack(side=tk.RIGHT, padx=(0, 4))

    def _env_row(self, parent, var: str, present: bool):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, padx=12, pady=1)
        mark = "OK" if present else "MISSING"
        color = OK if present else ERR
        tk.Label(row, text=f"[{mark}]", bg=BG, fg=color, font=(FONT, 9, "bold"), width=10, anchor="w").pack(side=tk.LEFT)
        tk.Label(row, text=var, bg=BG, fg=FG, font=("Consolas", 9), anchor="w").pack(side=tk.LEFT)

    def _caso_row(self, parent, num: str, path: str):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, padx=12, pady=1)
        tk.Label(row, text=f"caso {num}", bg=BG, fg=ACCENT, font=(FONT, 9, "bold"), width=10, anchor="w").pack(side=tk.LEFT)
        tk.Label(row, text=path, bg=BG, fg=FG, font=("Consolas", 9), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        real = _ROOT / path
        if real.exists():
            ttk.Button(row, text="Abrir", width=9, command=lambda p=real: self._open_path(p)).pack(side=tk.RIGHT)

    # -- actions --

    def _copy_to_clipboard(self, text: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def _open_path(self, path: Path):
        try:
            p = Path(path)
            if not p.exists():
                messagebox.showwarning("No existe", f"Ruta no encontrada: {p}")
                return
            if os.name == "nt":
                os.startfile(str(p))  # type: ignore[attr-defined]
            else:
                webbrowser.open(str(p))
        except Exception as exc:
            messagebox.showerror("Error al abrir", str(exc))

    def _execute_script(self, path: Path):
        """Lanza el script en una terminal nueva sin bloquear la GUI.

        - Windows: cmd.exe con `/k` (ventana persiste tras terminar).
        - macOS:   genera un .command tempfile y lo abre con `open` → Terminal.
        - Linux:   intenta x-terminal-emulator / gnome-terminal / konsole / xterm.

        En todos los casos: `cd` al root del proyecto antes de ejecutar, y usa
        el mismo interprete que esta corriendo la GUI (`sys.executable`) para
        respetar el venv activo. Los `.bat` solo corren en Windows.
        """
        try:
            p = Path(path)
            if not p.exists():
                messagebox.showwarning("No existe", f"Ruta no encontrada: {p}")
                return

            system = platform.system()  # "Windows" | "Darwin" | "Linux"
            suffix = p.suffix.lower()
            py = sys.executable or ("python" if system == "Windows" else "python3")

            if system == "Windows":
                if suffix == ".bat":
                    cmd = f'start "" cmd /k "cd /d \"{_ROOT}\" && \"{p}\""'
                elif suffix == ".py":
                    cmd = f'start "" cmd /k "cd /d \"{_ROOT}\" && \"{py}\" \"{p}\""'
                else:
                    messagebox.showwarning("No ejecutable", f"Extension no soportada: {suffix}")
                    return
                subprocess.Popen(cmd, shell=True, cwd=str(_ROOT))

            elif system == "Darwin":
                if suffix == ".bat":
                    messagebox.showwarning(
                        "No ejecutable en macOS",
                        f"{p.name} es un .bat (Windows). Usa el equivalente .py o copia el comando."
                    )
                    return
                if suffix != ".py":
                    messagebox.showwarning("No ejecutable", f"Extension no soportada: {suffix}")
                    return
                # .command tempfile: Terminal.app lo abre en ventana nueva.
                # Paths con espacios manejados via shlex.quote.
                content = (
                    "#!/bin/bash\n"
                    f"cd {shlex.quote(str(_ROOT))}\n"
                    f"{shlex.quote(py)} {shlex.quote(str(p))}\n"
                    'echo ""\n'
                    'read -n 1 -s -r -p "[Pulsa una tecla para cerrar]"\n'
                    'echo ""\n'
                )
                tmp = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".command", delete=False, prefix="coworkia-", encoding="utf-8"
                )
                tmp.write(content)
                tmp.close()
                os.chmod(tmp.name, 0o755)
                subprocess.Popen(["open", tmp.name])

            else:  # Linux / otros Unix
                if suffix == ".bat":
                    messagebox.showwarning("No ejecutable", f"{p.name} es Windows-only.")
                    return
                if suffix != ".py":
                    messagebox.showwarning("No ejecutable", f"Extension no soportada: {suffix}")
                    return
                inner = (
                    f"cd {shlex.quote(str(_ROOT))} && "
                    f"{shlex.quote(py)} {shlex.quote(str(p))}; "
                    "echo; read -n 1 -s -r -p '[Pulsa una tecla para cerrar]'; echo"
                )
                launched = False
                for term in ("x-terminal-emulator", "gnome-terminal", "konsole",
                             "xfce4-terminal", "xterm"):
                    if not shutil.which(term):
                        continue
                    if term == "gnome-terminal":
                        subprocess.Popen([term, "--", "bash", "-c", inner])
                    else:
                        subprocess.Popen([term, "-e", f"bash -c {shlex.quote(inner)}"])
                    launched = True
                    break
                if not launched:
                    messagebox.showwarning(
                        "Sin terminal",
                        "No encontre un emulador de terminal (x-terminal-emulator, "
                        "gnome-terminal, konsole, xfce4-terminal, xterm). "
                        "Copia el comando y ejecutalo en tu terminal."
                    )
                    return

            self._flash_status(f"Ejecutando {p.name} en ventana nueva...")
        except Exception as exc:
            messagebox.showerror("Error al ejecutar", str(exc))

    def _flash_status(self, text: str):
        """Muestra un mensaje temporal en la barra de estado."""
        if hasattr(self, "lbl_date"):
            prev = self.lbl_date.cget("text")
            self.lbl_date.config(text=text, fg=ACCENT)
            self.root.after(3500, lambda: self.lbl_date.config(text=prev, fg=ACCENT))


def main() -> int:
    root = tk.Tk()
    PipelineAtlasGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
