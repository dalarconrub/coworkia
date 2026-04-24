"""
GUI para el Agente GIT — Repositorios GitHub → Notion.
Interfaz gráfica con tkinter para importar, sincronizar, catalogar y explorar repos.
"""

import os
import sys
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import tkinter as tk
from tkinter import ttk, messagebox

from tools.notion_tools import query_database, extract_property_value, update_page_properties
from tools.github_tools import get_user_repos, get_repo_languages, extract_repo_info
from agents.github_agent import (
    DB_GIT, importar_repos, sincronizar, catalogar, estado_repos,
    _repos_existentes, _repo_a_propiedades,
)


# ─── CONSTANTES ──────────────────────────────────────────────────────────────

TIPOS = ["Proyecto", "Librería", "Fork", "Ejercicio", "Config", "Template", "Script"]
ESTADOS = ["Activo", "WIP", "Archivado", "Deprecado", "Pausado"]
BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
BG_CARD = "#313244"
BG_INPUT = "#45475a"
FG_DIM = "#6c7086"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"
RED = "#f38ba8"
PURPLE = "#cba6f7"


class GitHubGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GIT — Repositorios GitHub → Notion")
        self.root.geometry("960x700")
        self.root.configure(bg=BG)
        self.root.minsize(800, 600)

        self.repos_data = []  # cache de repos cargados de Notion

        self._build_styles()
        self._build_ui()
        self._cargar_repos()

    # ─── ESTILOS ─────────────────────────────────────────────────────────

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=FG, fieldbackground=BG_INPUT)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground=ACCENT)
        style.configure("Stat.TLabel", font=("Segoe UI", 11, "bold"), foreground=FG)
        style.configure("Dim.TLabel", foreground=FG_DIM, font=("Segoe UI", 9))

        style.configure("Accent.TButton", background=ACCENT, foreground=BG,
                         font=("Segoe UI", 10, "bold"), padding=(12, 6))
        style.map("Accent.TButton",
                   background=[("active", "#74c7ec"), ("disabled", FG_DIM)])

        style.configure("TButton", background=BG_CARD, foreground=FG,
                         font=("Segoe UI", 10), padding=(10, 5))
        style.map("TButton",
                   background=[("active", BG_INPUT)])

        style.configure("TCombobox", fieldbackground=BG_INPUT, foreground=FG,
                         background=BG_CARD, font=("Segoe UI", 10))
        style.map("TCombobox", fieldbackground=[("readonly", BG_INPUT)])

        style.configure("Treeview", background=BG_CARD, foreground=FG,
                         fieldbackground=BG_CARD, font=("Segoe UI", 10), rowheight=28)
        style.configure("Treeview.Heading", background=BG_INPUT, foreground=ACCENT,
                         font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)],
                   foreground=[("selected", BG)])

        style.configure("TEntry", fieldbackground=BG_INPUT, foreground=FG,
                         font=("Segoe UI", 10))

        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", background=BG_CARD, foreground=FG,
                         font=("Segoe UI", 10), padding=(14, 6))
        style.map("TNotebook.Tab",
                   background=[("selected", ACCENT)],
                   foreground=[("selected", BG)])

    # ─── UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=16, pady=(12, 0))
        ttk.Label(header, text="GIT — Repositorios", style="Title.TLabel").pack(side="left")

        self.lbl_status = ttk.Label(header, text="", style="Dim.TLabel")
        self.lbl_status.pack(side="right")

        # Stats bar
        self.stats_frame = ttk.Frame(self.root)
        self.stats_frame.pack(fill="x", padx=16, pady=(8, 4))
        self.lbl_stats = ttk.Label(self.stats_frame, text="", style="Stat.TLabel")
        self.lbl_stats.pack(side="left")

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=8)

        self._build_tab_explorar()
        self._build_tab_catalogar()
        self._build_tab_acciones()

    # ── Tab: Explorar ────────────────────────────────────────────────────

    def _build_tab_explorar(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Explorar  ")

        # Filtros
        filtros = ttk.Frame(tab)
        filtros.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(filtros, text="Buscar:").pack(side="left", padx=(0, 4))
        self.var_buscar = tk.StringVar()
        self.var_buscar.trace_add("write", lambda *_: self._filtrar_tabla())
        entry_buscar = ttk.Entry(filtros, textvariable=self.var_buscar, width=25)
        entry_buscar.pack(side="left", padx=(0, 12))

        ttk.Label(filtros, text="Tipo:").pack(side="left", padx=(0, 4))
        self.var_filtro_tipo = tk.StringVar(value="Todos")
        cb_tipo = ttk.Combobox(filtros, textvariable=self.var_filtro_tipo,
                                values=["Todos"] + TIPOS, state="readonly", width=12)
        cb_tipo.pack(side="left", padx=(0, 12))
        cb_tipo.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        ttk.Label(filtros, text="Estado:").pack(side="left", padx=(0, 4))
        self.var_filtro_estado = tk.StringVar(value="Todos")
        cb_estado = ttk.Combobox(filtros, textvariable=self.var_filtro_estado,
                                  values=["Todos"] + ESTADOS, state="readonly", width=12)
        cb_estado.pack(side="left", padx=(0, 12))
        cb_estado.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        ttk.Label(filtros, text="Proceso:").pack(side="left", padx=(0, 4))
        self.var_filtro_proceso = tk.StringVar(value="Todos")
        self.cb_proceso = ttk.Combobox(filtros, textvariable=self.var_filtro_proceso,
                                        values=["Todos"], state="readonly", width=16)
        self.cb_proceso.pack(side="left")
        self.cb_proceso.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        # Tabla
        cols = ("nombre", "tipo", "estado", "lenguajes", "proceso", "version_de", "visibilidad", "creado", "ultima_actividad")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", selectmode="browse")

        for col_id, texto, ancho, ancho_min in [
            ("nombre",            "Nombre",     180, 120),
            ("tipo",              "Tipo",        80,  60),
            ("estado",            "Estado",      80,  60),
            ("lenguajes",         "Lenguajes",  120,  80),
            ("proceso",           "Proceso",    120,  80),
            ("version_de",        "Versión de", 110,  80),
            ("visibilidad",       "Vis.",        60,  45),
            ("creado",            "Creado",      90,  75),
            ("ultima_actividad",  "Últ. actividad", 100, 75),
        ]:
            self.tree.heading(col_id, text=texto,
                              command=lambda c=col_id: self._sort_col(c))
            self.tree.column(col_id, width=ancho, minwidth=ancho_min)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)
        scrollbar.pack(side="right", fill="y", pady=4, padx=(0, 8))

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._abrir_url)

        self.sort_reverse = {}

    # ── Tab: Catalogar ───────────────────────────────────────────────────

    def _build_tab_catalogar(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Catalogar  ")

        # Info del repo seleccionado
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill="x", padx=12, pady=(12, 4))

        ttk.Label(info_frame, text="Repo seleccionado:").grid(row=0, column=0, sticky="w")
        self.lbl_repo_sel = ttk.Label(info_frame, text="(selecciona un repo en Explorar)",
                                       style="Stat.TLabel")
        self.lbl_repo_sel.grid(row=0, column=1, sticky="w", padx=(8, 0))

        # Campos editables
        form = ttk.Frame(tab)
        form.pack(fill="x", padx=12, pady=8)

        row = 0
        ttk.Label(form, text="Tipo:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_tipo = tk.StringVar()
        ttk.Combobox(form, textvariable=self.var_cat_tipo, values=[""] + TIPOS,
                      state="readonly", width=18).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(form, text="Estado:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_estado = tk.StringVar()
        ttk.Combobox(form, textvariable=self.var_cat_estado, values=[""] + ESTADOS,
                      state="readonly", width=18).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(form, text="Versión de:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_version = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_cat_version, width=30).grid(
            row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(form, text="Proceso:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_proceso = tk.StringVar()
        ttk.Entry(form, textvariable=self.var_cat_proceso, width=30).grid(
            row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(form, text="Etiquetas:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_etiquetas = tk.StringVar()
        e = ttk.Entry(form, textvariable=self.var_cat_etiquetas, width=40)
        e.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(form, text="(separadas por coma)", style="Dim.TLabel").grid(
            row=row, column=2, sticky="w")

        row += 1
        ttk.Label(form, text="Notas:").grid(row=row, column=0, sticky="nw", pady=4)
        self.txt_notas = tk.Text(form, width=50, height=4, bg=BG_INPUT, fg=FG,
                                  insertbackground=FG, font=("Segoe UI", 10),
                                  relief="flat", padx=6, pady=4)
        self.txt_notas.grid(row=row, column=1, columnspan=2, sticky="w", padx=8, pady=4)

        # Botón guardar
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", padx=12, pady=(4, 12))
        ttk.Button(btn_frame, text="Guardar catalogación", style="Accent.TButton",
                    command=self._guardar_catalogacion).pack(side="left")
        self.lbl_cat_status = ttk.Label(btn_frame, text="", style="Dim.TLabel")
        self.lbl_cat_status.pack(side="left", padx=12)

    # ── Tab: Acciones ────────────────────────────────────────────────────

    def _build_tab_acciones(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Acciones  ")

        content = ttk.Frame(tab)
        content.pack(padx=20, pady=20)

        actions = [
            ("Importar repos nuevos", "Trae repos de GitHub que aún no están en Notion",
             self._accion_importar),
            ("Sincronizar metadata", "Actualiza estrellas, forks, lenguajes y fechas",
             self._accion_sincronizar),
            ("Recargar tabla", "Vuelve a leer los repos desde Notion",
             lambda: self._cargar_repos()),
        ]

        for i, (titulo, desc, cmd) in enumerate(actions):
            frame = ttk.Frame(content)
            frame.pack(fill="x", pady=6)
            ttk.Button(frame, text=titulo, style="Accent.TButton",
                        command=cmd, width=25).pack(side="left")
            ttk.Label(frame, text=desc, style="Dim.TLabel").pack(side="left", padx=12)

        # Log de salida
        ttk.Label(content, text="Log:", style="Dim.TLabel").pack(anchor="w", pady=(16, 4))
        self.txt_log = tk.Text(content, width=80, height=18, bg=BG_CARD, fg=FG,
                                insertbackground=FG, font=("Consolas", 9),
                                relief="flat", padx=8, pady=6, state="disabled")
        self.txt_log.pack(fill="both", expand=True)

    # ─── DATOS ───────────────────────────────────────────────────────────

    def _cargar_repos(self):
        self._set_status("Cargando repos de Notion...")
        threading.Thread(target=self._cargar_repos_bg, daemon=True).start()

    def _cargar_repos_bg(self):
        try:
            paginas = query_database(DB_GIT)
            self.repos_data = []
            procesos = set()

            for p in paginas:
                props = p.get("properties", {})
                repo = {
                    "id": p["id"],
                    "nombre": extract_property_value(props.get("Nombre", {})),
                    "tipo": extract_property_value(props.get("Tipo", {})),
                    "estado": extract_property_value(props.get("Estado", {})),
                    "lenguajes": extract_property_value(props.get("Lenguajes", {})),
                    "proceso": extract_property_value(props.get("Proceso", {})),
                    "version_de": extract_property_value(props.get("Versión de", {})),
                    "visibilidad": extract_property_value(props.get("Visibilidad", {})),
                    "url": extract_property_value(props.get("URL", {})),
                    "etiquetas": extract_property_value(props.get("Etiquetas", {})),
                    "notas": extract_property_value(props.get("Notas", {})),
                    "estrellas": extract_property_value(props.get("Estrellas", {})),
                    "creado": extract_property_value(props.get("Creado", {})),
                    "ultima_actividad": extract_property_value(props.get("Última actividad", {})),
                }
                self.repos_data.append(repo)
                if repo["proceso"]:
                    procesos.add(repo["proceso"])

            self.root.after(0, self._actualizar_tabla, sorted(procesos))
        except Exception as e:
            self.root.after(0, self._set_status, f"Error: {e}")

    def _actualizar_tabla(self, procesos: list[str] = None):
        if procesos is not None:
            self.cb_proceso["values"] = ["Todos"] + procesos

        self.tree.delete(*self.tree.get_children())
        for repo in self.repos_data:
            self.tree.insert("", "end", iid=repo["id"], values=(
                repo["nombre"], repo["tipo"], repo["estado"],
                repo["lenguajes"], repo["proceso"], repo["version_de"],
                repo["visibilidad"], repo["creado"], repo["ultima_actividad"],
            ))

        self._actualizar_stats()
        self._set_status(f"{len(self.repos_data)} repos cargados")
        self._filtrar_tabla()

    def _actualizar_stats(self):
        total = len(self.repos_data)
        por_tipo = {}
        por_estado = {}
        for r in self.repos_data:
            t = r["tipo"] or "Sin tipo"
            e = r["estado"] or "Sin estado"
            por_tipo[t] = por_tipo.get(t, 0) + 1
            por_estado[e] = por_estado.get(e, 0) + 1

        partes = [f"{total} repos"]
        for estado in ["Activo", "WIP", "Archivado", "Deprecado"]:
            n = por_estado.get(estado, 0)
            if n:
                partes.append(f"{n} {estado.lower()}")
        self.lbl_stats.config(text="  ·  ".join(partes))

    # ─── FILTROS Y ORDENACIÓN ────────────────────────────────────────────

    def _filtrar_tabla(self):
        buscar = self.var_buscar.get().lower()
        tipo = self.var_filtro_tipo.get()
        estado = self.var_filtro_estado.get()
        proceso = self.var_filtro_proceso.get()

        self.tree.delete(*self.tree.get_children())
        for repo in self.repos_data:
            if buscar and buscar not in repo["nombre"].lower() and buscar not in repo.get("lenguajes", "").lower():
                continue
            if tipo != "Todos" and repo["tipo"] != tipo:
                continue
            if estado != "Todos" and repo["estado"] != estado:
                continue
            if proceso != "Todos" and repo["proceso"] != proceso:
                continue

            self.tree.insert("", "end", iid=repo["id"], values=(
                repo["nombre"], repo["tipo"], repo["estado"],
                repo["lenguajes"], repo["proceso"], repo["version_de"],
                repo["visibilidad"], repo["creado"], repo["ultima_actividad"],
            ))

    def _sort_col(self, col):
        reverse = self.sort_reverse.get(col, False)
        date_cols = ("creado", "ultima_actividad")

        if col in date_cols:
            # Ordenar fechas: vacías van al final siempre
            def date_key(r):
                val = r.get(col, "")
                if not val:
                    return ("1" if not reverse else "0", "")
                return ("0" if not reverse else "1", val)
            self.repos_data.sort(key=date_key, reverse=reverse)
        else:
            self.repos_data.sort(key=lambda r: r.get(col, "").lower(), reverse=reverse)
        self.sort_reverse[col] = not reverse
        self._filtrar_tabla()

    # ─── EVENTOS ─────────────────────────────────────────────────────────

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        repo_id = sel[0]
        repo = next((r for r in self.repos_data if r["id"] == repo_id), None)
        if not repo:
            return

        self.lbl_repo_sel.config(text=repo["nombre"])
        self.var_cat_tipo.set(repo["tipo"])
        self.var_cat_estado.set(repo["estado"])
        self.var_cat_version.set(repo["version_de"])
        self.var_cat_proceso.set(repo["proceso"])
        self.var_cat_etiquetas.set(repo["etiquetas"])
        self.txt_notas.delete("1.0", "end")
        self.txt_notas.insert("1.0", repo["notas"])

    def _abrir_url(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        repo = next((r for r in self.repos_data if r["id"] == sel[0]), None)
        if repo and repo["url"]:
            import webbrowser
            webbrowser.open(repo["url"])

    # ─── CATALOGAR ───────────────────────────────────────────────────────

    def _guardar_catalogacion(self):
        nombre = self.lbl_repo_sel.cget("text")
        if not nombre or nombre.startswith("("):
            messagebox.showwarning("Atención", "Selecciona un repo en la pestaña Explorar primero.")
            return

        etiquetas_raw = self.var_cat_etiquetas.get().strip()
        etiquetas = [e.strip() for e in etiquetas_raw.split(",") if e.strip()] if etiquetas_raw else None
        notas = self.txt_notas.get("1.0", "end").strip() or None

        self.lbl_cat_status.config(text="Guardando...")

        def _save():
            try:
                result = catalogar(
                    nombre,
                    tipo=self.var_cat_tipo.get() or None,
                    estado=self.var_cat_estado.get() or None,
                    version_de=self.var_cat_version.get().strip() or None,
                    proceso=self.var_cat_proceso.get().strip() or None,
                    etiquetas=etiquetas,
                    notas=notas,
                )
                self.root.after(0, self.lbl_cat_status.config, {"text": result})
                self.root.after(0, self._cargar_repos)
            except Exception as e:
                self.root.after(0, self.lbl_cat_status.config, {"text": f"Error: {e}"})

        threading.Thread(target=_save, daemon=True).start()

    # ─── ACCIONES ────────────────────────────────────────────────────────

    def _log(self, text: str):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def _log_clear(self):
        self.txt_log.config(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.config(state="disabled")

    def _accion_importar(self):
        self._log_clear()
        self._log("Importando repos de GitHub...")
        self._set_status("Importando...")

        def _run():
            try:
                # Redirect print to log
                result = importar_repos()
                self.root.after(0, self._log, result)
                self.root.after(0, self._set_status, "Importación completada")
                self.root.after(0, self._cargar_repos)
            except Exception as e:
                self.root.after(0, self._log, f"Error: {e}")
                self.root.after(0, self._set_status, "Error en importación")

        threading.Thread(target=_run, daemon=True).start()

    def _accion_sincronizar(self):
        self._log_clear()
        self._log("Sincronizando metadata desde GitHub...")
        self._set_status("Sincronizando...")

        def _run():
            try:
                result = sincronizar()
                self.root.after(0, self._log, result)
                self.root.after(0, self._set_status, "Sincronización completada")
                self.root.after(0, self._cargar_repos)
            except Exception as e:
                self.root.after(0, self._log, f"Error: {e}")
                self.root.after(0, self._set_status, "Error en sincronización")

        threading.Thread(target=_run, daemon=True).start()

    # ─── UTILIDADES ──────────────────────────────────────────────────────

    def _set_status(self, text: str):
        self.lbl_status.config(text=text)


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubGUI(root)
    root.mainloop()
