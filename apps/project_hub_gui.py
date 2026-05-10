"""
UI unificada para gestión de proyecto, tareas y sprints en Coworkia.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from dotenv import load_dotenv

load_dotenv()

from agents.bib_agent import catalogar as bib_catalogar
from agents.bib_agent import estado_bib, importar_papers, listar_papers, sincronizar as bib_sync
from agents.github_agent import catalogar as rep_catalogar
from agents.github_agent import estado_repos, importar_repos, listar_repos, sincronizar as rep_sync
from agents.kit_agent import (
    buscar_kit,
    estado_kit,
    importar_keep,
    listar_information,
    listar_knowledge,
    listar_tools,
    nueva_information,
    nueva_knowledge,
    nueva_tool,
    sincronizar_keep,
)
from agents.notion_agent import crear_nota, crear_proyecto, crear_tarea, estado_ptn, listar_notas, listar_proyectos, listar_tareas
from agents.obsidian_agent import buscar as abgd_buscar
from agents.obsidian_agent import estado_vault, mapa as abgd_mapa, nueva_nota as abgd_nueva_nota, ultimas_notas, ver_nota
from agents.orchestrator_agent import generar_sprint, listar_agentes, listar_roles
from agents.todoist_agent import estado_sistema, listar_por_tipo, nueva_idea, nueva_meta, nueva_tarea, nuevo_evento, nuevo_habito, nuevo_logro, resumen_hoy

BG = "#0b1020"
BG_PANEL = "#111827"
BG_CARD = "#172033"
BG_INPUT = "#09101d"
FG = "#e5e7eb"
FG_DIM = "#93a3b8"
ACCENT = "#2dd4bf"
ACCENT_ALT = "#38bdf8"
WARN = "#f59e0b"
FONT = "Segoe UI"
ARTIFACTS_DIR = Path("artifacts") / "sprints"


class ProjectHubGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Coworkia Project Hub")
        self.root.geometry("1480x920")
        self.root.minsize(1240, 780)
        self.root.configure(bg=BG)
        self.tab_outputs: dict[str, ScrolledText] = {}
        self.overview_labels: dict[str, ttk.Label] = {}
        self.status_var = tk.StringVar(value="Listo")
        self.home_log: ScrolledText | None = None
        self.artifacts_listbox: tk.Listbox | None = None
        self.notebook: ttk.Notebook | None = None
        self._build_styles()
        self._build_layout()
        self.refresh_dashboard()

    def _missing_env(self, *keys: str) -> list[str]:
        return [key for key in keys if not os.getenv(key)]

    def _system_config_error(self, system: str) -> str | None:
        if system == "todoist":
            missing = self._missing_env("TODOIST_API_KEY")
            return f"No configurado: falta {', '.join(missing)}" if missing else None

        if system in {"ptn", "kit"}:
            missing = self._missing_env("NOTION_TOKEN")
            if system == "kit":
                missing += self._missing_env("NOTION_DB_KIT")
            return f"No configurado: falta {', '.join(missing)}" if missing else None

        if system == "rep":
            missing = self._missing_env("NOTION_TOKEN", "NOTION_DB_GIT")
            return f"No configurado: falta {', '.join(missing)}" if missing else None

        if system == "bib":
            missing = self._missing_env("NOTION_TOKEN", "NOTION_DB_BIB")
            return f"No configurado: falta {', '.join(missing)}" if missing else None

        if system == "abgd":
            alpha_path = os.getenv("OBSIDIAN_ALPHA_PATH")
            if not alpha_path:
                return "No configurado: falta OBSIDIAN_ALPHA_PATH"
            if not Path(alpha_path).exists():
                return f"No configurado: OBSIDIAN_ALPHA_PATH no existe ({alpha_path})"
            return None

        return None

    def _config_report(self) -> str:
        systems = [
            ("todoist", "MAR / Todoist"),
            ("ptn", "PTN / Notion"),
            ("kit", "KIT / Notion"),
            ("rep", "GIT / GitHub"),
            ("bib", "BIB / Paperpile"),
            ("abgd", "ABGD / Obsidian"),
        ]
        lines = ["Estado de configuracion:\n"]
        for key, label in systems:
            error = self._system_config_error(key)
            lines.append(f"- {label}: {'OK' if error is None else error}")
        return "\n".join(lines)

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG, foreground=FG, fieldbackground=BG_INPUT)
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=BG_PANEL)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("TLabel", background=BG, foreground=FG, font=(FONT, 10))
        style.configure("Title.TLabel", background=BG, foreground=ACCENT, font=(FONT, 19, "bold"))
        style.configure("Section.TLabel", background=BG_PANEL, foreground=FG, font=(FONT, 12, "bold"))
        style.configure("StatTitle.TLabel", background=BG_CARD, foreground=FG_DIM, font=(FONT, 10))
        style.configure("StatValue.TLabel", background=BG_CARD, foreground=FG, font=(FONT, 14, "bold"))
        style.configure("Dim.TLabel", background=BG, foreground=FG_DIM, font=(FONT, 9))
        style.configure("PanelDim.TLabel", background=BG_PANEL, foreground=FG_DIM, font=(FONT, 9))
        style.configure("Accent.TButton", background=ACCENT, foreground=BG, font=(FONT, 10, "bold"), padding=(10, 7))
        style.configure("Info.TButton", background=ACCENT_ALT, foreground=BG, font=(FONT, 10, "bold"), padding=(10, 7))
        style.configure("Warn.TButton", background=WARN, foreground=BG, font=(FONT, 10, "bold"), padding=(10, 7))
        style.configure("TButton", background=BG_CARD, foreground=FG, font=(FONT, 10), padding=(8, 6))
        style.configure("TEntry", fieldbackground=BG_INPUT, foreground=FG, insertcolor=FG)
        style.configure("TCombobox", fieldbackground=BG_INPUT, foreground=FG, background=BG_CARD)
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", background=BG_CARD, foreground=FG, padding=(12, 7), font=(FONT, 10))

    def _build_layout(self):
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=18, pady=(16, 8))
        ttk.Label(header, text="Coworkia Project Hub", style="Title.TLabel").pack(side="left")
        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Refrescar", command=self.refresh_dashboard, style="Info.TButton").pack(side="left", padx=(0, 8))
        ttk.Label(actions, textvariable=self.status_var, style="Dim.TLabel").pack(side="left")

        overview = ttk.Frame(self.root)
        overview.pack(fill="x", padx=18, pady=(0, 8))
        for key, title in [("todoist", "MAR / Todoist"), ("ptn", "PTN / Notion"), ("rep", "GIT / GitHub"), ("bib", "BIB / Paperpile"), ("abgd", "ABGD / Obsidian"), ("sprint", "Sprints")]:
            card = ttk.Frame(overview, style="Card.TFrame", padding=12)
            card.pack(side="left", fill="both", expand=True, padx=6)
            ttk.Label(card, text=title, style="StatTitle.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="Cargando...", style="StatValue.TLabel")
            value.pack(anchor="w", pady=(8, 2))
            self.overview_labels[key] = value

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        self._build_home_tab()
        self._build_todoist_tab()
        self._build_ptn_tab()
        self._build_kit_tab()
        self._build_rep_tab()
        self._build_bib_tab()
        self._build_abgd_tab()
        self._build_sprint_tab()

    def _build_home_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Home  ")
        left = ttk.Frame(tab, style="Panel.TFrame", padding=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        right = ttk.Frame(tab, style="Panel.TFrame", padding=12)
        right.pack(side="left", fill="y", pady=8)
        ttk.Label(left, text="Centro de control", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        buttons = ttk.Frame(left, style="Panel.TFrame")
        buttons.pack(fill="x")
        items = [("Abrir GUI GIT", lambda: self._launch_script("apps/github_gui.py"), "Info.TButton"), ("Abrir GUI BIB", lambda: self._launch_script("apps/bib_gui.py"), "Info.TButton"), ("Listar agentes", lambda: self._run_async("home", listar_agentes), "Accent.TButton"), ("Ir a Sprints", lambda: self.notebook.select(7), "TButton")]
        for idx, (label, cmd, style) in enumerate(items):
            ttk.Button(buttons, text=label, command=cmd, style=style).grid(row=idx // 2, column=idx % 2, padx=6, pady=6, sticky="ew")
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        ttk.Separator(left).pack(fill="x", pady=12)
        self.home_log = self._make_output(left, 20)
        self.tab_outputs["home"] = self.home_log
        self._write_output("home", f"Actividad del hub\n\n{self._config_report()}")

        ttk.Label(right, text="Artefactos de sprint", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.artifacts_listbox = tk.Listbox(right, bg=BG_INPUT, fg=FG, relief="flat", selectbackground=ACCENT_ALT, selectforeground=BG, width=40, height=18, font=(FONT, 10))
        self.artifacts_listbox.pack(fill="both", expand=True)
        ttk.Button(right, text="Refrescar artefactos", command=self._refresh_artifacts, style="TButton").pack(fill="x", pady=3)
        ttk.Button(right, text="Abrir artefacto", command=self._open_selected_artifact, style="Accent.TButton").pack(fill="x", pady=3)

    def _build_split_tab(self, title: str, key: str):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"  {title}  ")
        left = ttk.Frame(tab, style="Panel.TFrame", padding=12)
        left.pack(side="left", fill="y", padx=(0, 8), pady=8)
        right = ttk.Frame(tab, style="Panel.TFrame", padding=12)
        right.pack(side="left", fill="both", expand=True, pady=8)
        self.tab_outputs[key] = self._make_output(right)
        return left

    def _make_output(self, parent, height: int | None = None):
        out = ScrolledText(parent, bg=BG_PANEL, fg=FG, insertbackground=FG, relief="flat", font=("Consolas", 10), wrap="word", padx=10, pady=10, height=height)
        out.pack(fill="both", expand=True)
        return out

    def _btn(self, parent, text, cmd, style="TButton"):
        ttk.Button(parent, text=text, command=cmd, style=style).pack(fill="x", pady=4)

    def _build_todoist_tab(self):
        p = self._build_split_tab("Todoist", "todoist")
        ttk.Label(p, text="MAR / Todoist", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Resumen de hoy", lambda: self._run_async("todoist", resumen_hoy), "Accent.TButton")
        self._btn(p, "Estado del sistema", lambda: self._run_async("todoist", estado_sistema))
        self.todoist_type = tk.StringVar(value="logro")
        ttk.Combobox(p, textvariable=self.todoist_type, values=["idea", "logro", "habito", "tarea", "evento"], state="readonly").pack(fill="x", pady=8)
        self._btn(p, "Listar por tipo", lambda: self._run_async("todoist", lambda: listar_por_tipo(self.todoist_type.get())))
        ttk.Separator(p).pack(fill="x", pady=12)
        self.todoist_create_type = tk.StringVar(value="idea")
        self.todoist_content = tk.StringVar()
        self.todoist_param = tk.StringVar()
        ttk.Combobox(p, textvariable=self.todoist_create_type, values=["idea", "logro", "habito", "tarea", "evento"], state="readonly").pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.todoist_content).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.todoist_param).pack(fill="x", pady=2)
        self._btn(p, "Crear acción", self._create_todoist_item, "Accent.TButton")

    def _build_ptn_tab(self):
        p = self._build_split_tab("PTN", "ptn")
        ttk.Label(p, text="PTN / Notion", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Estado PTN", lambda: self._run_async("ptn", estado_ptn), "Accent.TButton")
        self.ptn_state_filter = tk.StringVar()
        self.ptn_task_type_filter = tk.StringVar()
        ttk.Entry(p, textvariable=self.ptn_state_filter).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.ptn_task_type_filter).pack(fill="x", pady=2)
        self._btn(p, "Listar proyectos", lambda: self._run_async("ptn", lambda: listar_proyectos(estado=self.ptn_state_filter.get().strip() or None)))
        self._btn(p, "Listar tareas", lambda: self._run_async("ptn", lambda: listar_tareas(estado=self.ptn_state_filter.get().strip() or None, tipo=self.ptn_task_type_filter.get().strip() or None)))
        self._btn(p, "Listar notas", lambda: self._run_async("ptn", lambda: listar_notas(estado=self.ptn_state_filter.get().strip() or None)))
        ttk.Separator(p).pack(fill="x", pady=12)
        self.ptn_kind = tk.StringVar(value="proyecto")
        self.ptn_title = tk.StringVar()
        self.ptn_date = tk.StringVar()
        ttk.Combobox(p, textvariable=self.ptn_kind, values=["proyecto", "tarea", "nota"], state="readonly").pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.ptn_title).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.ptn_date).pack(fill="x", pady=2)
        self._btn(p, "Crear recurso PTN", self._create_ptn_item, "Accent.TButton")

    def _build_kit_tab(self):
        p = self._build_split_tab("KIT", "kit")
        ttk.Label(p, text="KIT / Notion", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Estado KIT", lambda: self._run_async("kit", estado_kit), "Accent.TButton")
        self._btn(p, "Knowledge", lambda: self._run_async("kit", listar_knowledge))
        self._btn(p, "Information", lambda: self._run_async("kit", listar_information))
        self._btn(p, "Tools", lambda: self._run_async("kit", listar_tools))
        self.kit_query = tk.StringVar()
        self.kit_kind = tk.StringVar(value="knowledge")
        self.kit_title = tk.StringVar()
        self.kit_keep_dir = tk.StringVar()
        ttk.Entry(p, textvariable=self.kit_query).pack(fill="x", pady=8)
        self._btn(p, "Buscar en KIT", lambda: self._run_async("kit", lambda: buscar_kit(self.kit_query.get().strip())), "Accent.TButton")
        ttk.Combobox(p, textvariable=self.kit_kind, values=["knowledge", "information", "tool"], state="readonly").pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.kit_title).pack(fill="x", pady=2)
        self._btn(p, "Crear entrada", self._create_kit_item)
        ttk.Separator(p).pack(fill="x", pady=12)
        ttk.Entry(p, textvariable=self.kit_keep_dir).pack(fill="x", pady=2)
        self._btn(p, "Importar Google Keep", self._import_keep_to_kit, "Warn.TButton")
        self._btn(p, "Sincronizar Google Keep", self._sync_keep_to_kit, "Info.TButton")

    def _build_rep_tab(self):
        p = self._build_split_tab("GIT", "rep")
        ttk.Label(p, text="GIT / GitHub", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Estado GIT", lambda: self._run_async("rep", estado_repos), "Accent.TButton")
        self.rep_filter_state = tk.StringVar()
        self.rep_filter_type = tk.StringVar()
        self.rep_filter_process = tk.StringVar()
        ttk.Entry(p, textvariable=self.rep_filter_state).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.rep_filter_type).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.rep_filter_process).pack(fill="x", pady=2)
        self._btn(p, "Listar repos", lambda: self._run_async("rep", lambda: listar_repos(estado=self.rep_filter_state.get().strip() or None, tipo=self.rep_filter_type.get().strip() or None, proceso=self.rep_filter_process.get().strip() or None)))
        self._btn(p, "Importar repos", lambda: self._run_async("rep", importar_repos), "Warn.TButton")
        self._btn(p, "Sincronizar metadata", lambda: self._run_async("rep", rep_sync), "Warn.TButton")
        self._btn(p, "Abrir GUI GIT", lambda: self._launch_script("apps/github_gui.py"), "Info.TButton")
        ttk.Separator(p).pack(fill="x", pady=12)
        self.rep_name = tk.StringVar()
        self.rep_type = tk.StringVar()
        self.rep_status = tk.StringVar()
        ttk.Entry(p, textvariable=self.rep_name).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.rep_type).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.rep_status).pack(fill="x", pady=2)
        self._btn(p, "Guardar catalogación", self._catalog_rep, "Accent.TButton")

    def _build_bib_tab(self):
        p = self._build_split_tab("BIB", "bib")
        ttk.Label(p, text="BIB / Paperpile", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Estado BIB", lambda: self._run_async("bib", estado_bib), "Accent.TButton")
        self.bib_filter_state = tk.StringVar()
        self.bib_filter_type = tk.StringVar()
        self.bib_filter_rel = tk.StringVar()
        self.bib_filter_folder = tk.StringVar()
        for var in [self.bib_filter_state, self.bib_filter_type, self.bib_filter_rel, self.bib_filter_folder]:
            ttk.Entry(p, textvariable=var).pack(fill="x", pady=2)
        self._btn(p, "Listar papers", lambda: self._run_async("bib", lambda: listar_papers(estado=self.bib_filter_state.get().strip() or None, tipo=self.bib_filter_type.get().strip() or None, relevancia=self.bib_filter_rel.get().strip() or None, carpeta=self.bib_filter_folder.get().strip() or None)))
        self._btn(p, "Importar papers", lambda: self._run_async("bib", importar_papers), "Warn.TButton")
        self._btn(p, "Sincronizar papers", lambda: self._run_async("bib", bib_sync), "Warn.TButton")
        self._btn(p, "Abrir GUI BIB", lambda: self._launch_script("apps/bib_gui.py"), "Info.TButton")
        ttk.Separator(p).pack(fill="x", pady=12)
        self.bib_key = tk.StringVar()
        self.bib_state = tk.StringVar()
        self.bib_rel = tk.StringVar()
        ttk.Entry(p, textvariable=self.bib_key).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.bib_state).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.bib_rel).pack(fill="x", pady=2)
        self._btn(p, "Guardar catalogación", self._catalog_bib, "Accent.TButton")

    def _build_abgd_tab(self):
        p = self._build_split_tab("ABGD", "abgd")
        ttk.Label(p, text="ABGD / Obsidian", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Mapa del vault", lambda: self._run_async("abgd", abgd_mapa), "Accent.TButton")
        self._btn(p, "Estado del vault", lambda: self._run_async("abgd", estado_vault))
        self._btn(p, "Últimas notas", lambda: self._run_async("abgd", lambda: ultimas_notas(12)))
        self.abgd_query = tk.StringVar()
        ttk.Entry(p, textvariable=self.abgd_query).pack(fill="x", pady=8)
        self._btn(p, "Buscar texto", lambda: self._run_async("abgd", lambda: abgd_buscar(self.abgd_query.get().strip())), "Accent.TButton")
        self._btn(p, "Ver nota", lambda: self._run_async("abgd", lambda: ver_nota(self.abgd_query.get().strip())))
        ttk.Separator(p).pack(fill="x", pady=12)
        self.abgd_area = tk.StringVar(value="A1-INV")
        self.abgd_block = tk.StringVar()
        self.abgd_context = tk.StringVar()
        self.abgd_title = tk.StringVar()
        for var in [self.abgd_area, self.abgd_block, self.abgd_context, self.abgd_title]:
            ttk.Entry(p, textvariable=var).pack(fill="x", pady=2)
        self._btn(p, "Crear nota", self._create_abgd_note, "Accent.TButton")

    def _build_sprint_tab(self):
        p = self._build_split_tab("Sprints", "sprints")
        ttk.Label(p, text="Scrum / Orquestador", style="Section.TLabel").pack(anchor="w", pady=(0, 10))
        self._btn(p, "Listar agentes", lambda: self._run_async("sprints", listar_agentes), "Accent.TButton")
        self._btn(p, "Listar roles", lambda: self._run_async("sprints", listar_roles))
        self.sprint_goal = tk.StringVar(value="Implementar incremento multiagente")
        self.sprint_name = tk.StringVar(value="Sprint 1")
        self.sprint_days = tk.StringVar(value="14")
        ttk.Entry(p, textvariable=self.sprint_goal).pack(fill="x", pady=8)
        ttk.Entry(p, textvariable=self.sprint_name).pack(fill="x", pady=2)
        ttk.Entry(p, textvariable=self.sprint_days).pack(fill="x", pady=2)
        self._btn(p, "Generar sprint y guardar", self._plan_sprint, "Accent.TButton")
        self._btn(p, "Refrescar artefactos", self._refresh_artifacts, "Info.TButton")

    def refresh_dashboard(self):
        self.status_var.set("Actualizando resumen...")
        self._load_overview()
        self._refresh_artifacts()
        self.status_var.set("Resumen actualizado")

    def _run_async(self, key: str, func, success_message: str | None = None):
        config_error = self._system_config_error(key)
        if config_error:
            self.status_var.set("Configuracion incompleta")
            self._write_output(key, config_error)
            self._append_home_log(f"[{key}] {config_error}")
            return

        self.status_var.set("Ejecutando...")
        self._write_output(key, f"> Ejecutando {getattr(func, '__name__', 'acción')}...\n\n")
        self._append_home_log(f"[{key}] Ejecutando {getattr(func, '__name__', 'acción')}")
        def worker():
            try:
                result = func()
                text = "\n".join(f"{k}: {v}" for k, v in result.items()) if isinstance(result, dict) else str(result)
                self.root.after(0, self._write_output, key, text)
                self.root.after(0, self.status_var.set, success_message or "Operación completada")
                self.root.after(0, self._load_overview)
                self.root.after(0, self._append_home_log, f"[{key}] {success_message or 'Operación completada'}")
            except Exception as exc:
                tb = traceback.format_exc()
                self.root.after(0, self._write_output, key, f"ERROR: {exc}\n\n{tb}")
                self.root.after(0, self.status_var.set, "Error")
                self.root.after(0, self._append_home_log, f"[{key}] ERROR: {exc}")
        threading.Thread(target=worker, daemon=True).start()

    def _write_output(self, key: str, text: str):
        widget = self.tab_outputs[key]
        widget.delete("1.0", "end")
        widget.insert("1.0", text)

    def _append_home_log(self, text: str):
        if self.home_log is not None:
            self.home_log.insert("end", f"{text}\n")
            self.home_log.see("end")

    def _load_overview(self):
        def safe_text(system: str, fn, fallback: str):
            config_error = self._system_config_error(system)
            if config_error:
                return config_error
            try:
                return fn()
            except Exception:
                return fallback

        data = {
            "todoist": safe_text("todoist", estado_sistema, "Error de acceso"),
            "ptn": safe_text("ptn", estado_ptn, "Error de acceso"),
            "rep": safe_text("rep", estado_repos, "Error de acceso"),
            "bib": safe_text("bib", estado_bib, "Error de acceso"),
            "abgd": safe_text("abgd", estado_vault, "Error de acceso"),
        }
        for key, text in data.items():
            self.overview_labels[key].config(text=self._first_metric(text))
        self.overview_labels["sprint"].config(text=f"{date.today().isoformat()}\n{self._artifact_count()} artefactos")

    def _first_metric(self, text: str) -> str:
        for line in str(text).splitlines():
            line = line.strip()
            if line and not line.startswith("==="):
                return line
        return "Sin datos"

    def _artifact_count(self) -> int:
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        return len(list(ARTIFACTS_DIR.glob("*.md")))

    def _refresh_artifacts(self):
        if self.artifacts_listbox is None:
            return
        self.artifacts_listbox.delete(0, "end")
        ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        for path in sorted(ARTIFACTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
            self.artifacts_listbox.insert("end", path.name)

    def _open_selected_artifact(self):
        if self.artifacts_listbox is None or not self.artifacts_listbox.curselection():
            messagebox.showwarning("Artefactos", "Selecciona un artefacto primero.")
            return
        self._open_file(ARTIFACTS_DIR / self.artifacts_listbox.get(self.artifacts_listbox.curselection()[0]))

    def _open_file(self, path: Path):
        try:
            resolved = path.resolve()
            if os.name == "nt":
                os.startfile(str(resolved))
            else:
                subprocess.Popen(["xdg-open", str(resolved)])
        except Exception as exc:
            messagebox.showerror("Abrir archivo", str(exc))

    def _launch_script(self, relative_path: str):
        try:
            subprocess.Popen([sys.executable, relative_path], cwd=Path.cwd())
            self._append_home_log(f"[launcher] Abierta app {relative_path}")
            self.status_var.set(f"Lanzado {relative_path}")
        except Exception as exc:
            messagebox.showerror("Launch", str(exc))

    def _create_todoist_item(self):
        kind, content, param = self.todoist_create_type.get(), self.todoist_content.get().strip(), self.todoist_param.get().strip()
        if not content:
            messagebox.showwarning("Todoist", "El contenido es obligatorio.")
            return
        mapping = {"idea": lambda: nueva_idea(content), "logro": lambda: nuevo_logro(content, param), "meta": lambda: nueva_meta(content, param), "habito": lambda: nuevo_habito(content, param), "tarea": lambda: nueva_tarea(content, param), "evento": lambda: nuevo_evento(content, param)}
        self._run_async("todoist", mapping[kind], "Acción creada en Todoist")

    def _create_ptn_item(self):
        kind, title, raw_date = self.ptn_kind.get(), self.ptn_title.get().strip(), self.ptn_date.get().strip() or None
        if not title:
            messagebox.showwarning("PTN", "El título es obligatorio.")
            return
        fn = (lambda: crear_proyecto(title, fecha_inicio=raw_date)) if kind == "proyecto" else (lambda: crear_tarea(title, plazo=raw_date)) if kind == "tarea" else (lambda: crear_nota(title, fecha=raw_date))
        self._run_async("ptn", fn, "Recurso PTN creado")

    def _create_kit_item(self):
        kind, title = self.kit_kind.get(), self.kit_title.get().strip()
        if not title:
            messagebox.showwarning("KIT", "El título es obligatorio.")
            return
        fn = (lambda: nueva_knowledge(title)) if kind == "knowledge" else (lambda: nueva_information(title)) if kind == "information" else (lambda: nueva_tool(title))
        self._run_async("kit", fn, "Entrada KIT creada")

    def _import_keep_to_kit(self):
        source = self.kit_keep_dir.get().strip()
        if not source:
            messagebox.showwarning("KIT", "La ruta del export de Google Keep es obligatoria.")
            return
        self._run_async("kit", lambda: importar_keep(source), "Importacion Google Keep completada")

    def _sync_keep_to_kit(self):
        source = self.kit_keep_dir.get().strip()
        if not source:
            messagebox.showwarning("KIT", "La ruta del export de Google Keep es obligatoria.")
            return
        self._run_async("kit", lambda: sincronizar_keep(source), "Sincronizacion Google Keep completada")

    def _catalog_rep(self):
        name = self.rep_name.get().strip()
        if not name:
            messagebox.showwarning("GIT", "El nombre del repo es obligatorio.")
            return
        self._run_async("rep", lambda: rep_catalogar(name, tipo=self.rep_type.get().strip() or None, estado=self.rep_status.get().strip() or None), "Catalogación GIT actualizada")

    def _catalog_bib(self):
        text = self.bib_key.get().strip()
        if not text:
            messagebox.showwarning("BIB", "El citekey o texto de búsqueda es obligatorio.")
            return
        self._run_async("bib", lambda: bib_catalogar(text, estado=self.bib_state.get().strip() or None, relevancia=self.bib_rel.get().strip() or None), "Catalogación BIB actualizada")

    def _create_abgd_note(self):
        values = [self.abgd_area.get().strip(), self.abgd_block.get().strip(), self.abgd_context.get().strip(), self.abgd_title.get().strip()]
        if not all(values):
            messagebox.showwarning("ABGD", "Área, bloque, contexto y nombre son obligatorios.")
            return
        self._run_async("abgd", lambda: abgd_nueva_nota(values[0], values[1], values[2], values[3]), "Nota ABGD creada")

    def _plan_sprint(self):
        goal, name = self.sprint_goal.get().strip(), self.sprint_name.get().strip() or "Sprint 1"
        if not goal:
            messagebox.showwarning("Sprints", "El objetivo del sprint es obligatorio.")
            return
        try:
            days = int(self.sprint_days.get().strip() or "14")
        except ValueError:
            messagebox.showwarning("Sprints", "La duración del sprint debe ser numérica.")
            return
        self._run_async("sprints", lambda: generar_sprint(goal, name, None, days, True), "Sprint generado")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectHubGUI(root)
    root.mainloop()
