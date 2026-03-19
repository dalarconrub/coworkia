"""
GUI para el Agente BIB — Paperpile → Notion.
Interfaz gráfica con tkinter para importar, sincronizar, catalogar y explorar papers.
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
from agents.bib_agent import (
    DB_BIB, importar_papers, sincronizar, catalogar, estado_bib,
)


# ─── CONSTANTES ──────────────────────────────────────────────────────────────

TIPOS = ["Artículo", "Libro", "Capítulo de libro", "Conferencia",
         "Tesis doctoral", "Tesis de máster", "Informe técnico", "Otro"]
ESTADOS = ["Por leer", "En proceso", "Leído", "Revisado", "Descartado"]
RELEVANCIAS = ["Alta", "Media", "Baja"]

BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#cba6f7"
BG_CARD = "#313244"
BG_INPUT = "#45475a"
FG_DIM = "#6c7086"
GREEN = "#a6e3a1"
YELLOW = "#f9e2af"
RED = "#f38ba8"


class BibGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("BIB — Bibliografía Paperpile → Notion")
        self.root.geometry("1050x700")
        self.root.configure(bg=BG)
        self.root.minsize(900, 600)

        self.papers_data = []
        self.sort_reverse = {}

        self._build_styles()
        self._build_ui()
        self._cargar_papers()

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
                   background=[("active", "#b4befe"), ("disabled", FG_DIM)])

        style.configure("TButton", background=BG_CARD, foreground=FG,
                         font=("Segoe UI", 10), padding=(10, 5))
        style.map("TButton", background=[("active", BG_INPUT)])

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
        ttk.Label(header, text="BIB — Bibliografía", style="Title.TLabel").pack(side="left")
        self.lbl_status = ttk.Label(header, text="", style="Dim.TLabel")
        self.lbl_status.pack(side="right")

        # Stats
        self.stats_frame = ttk.Frame(self.root)
        self.stats_frame.pack(fill="x", padx=16, pady=(8, 4))
        self.lbl_stats = ttk.Label(self.stats_frame, text="", style="Stat.TLabel")
        self.lbl_stats.pack(side="left")

        # Tabs
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
        ttk.Entry(filtros, textvariable=self.var_buscar, width=22).pack(side="left", padx=(0, 10))

        ttk.Label(filtros, text="Tipo:").pack(side="left", padx=(0, 4))
        self.var_filtro_tipo = tk.StringVar(value="Todos")
        cb_tipo = ttk.Combobox(filtros, textvariable=self.var_filtro_tipo,
                                values=["Todos"] + TIPOS, state="readonly", width=14)
        cb_tipo.pack(side="left", padx=(0, 10))
        cb_tipo.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        ttk.Label(filtros, text="Estado:").pack(side="left", padx=(0, 4))
        self.var_filtro_estado = tk.StringVar(value="Todos")
        cb_estado = ttk.Combobox(filtros, textvariable=self.var_filtro_estado,
                                  values=["Todos"] + ESTADOS, state="readonly", width=10)
        cb_estado.pack(side="left", padx=(0, 10))
        cb_estado.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        ttk.Label(filtros, text="Carpeta:").pack(side="left", padx=(0, 4))
        self.var_filtro_carpeta = tk.StringVar(value="Todos")
        self.cb_carpeta = ttk.Combobox(filtros, textvariable=self.var_filtro_carpeta,
                                        values=["Todos"], state="readonly", width=14)
        self.cb_carpeta.pack(side="left")
        self.cb_carpeta.bind("<<ComboboxSelected>>", lambda _: self._filtrar_tabla())

        # Tabla
        cols = ("titulo", "autores", "year", "tipo", "journal", "estado", "relevancia", "carpeta")
        self.tree = ttk.Treeview(tab, columns=cols, show="headings", selectmode="browse")

        for col_id, texto, ancho, ancho_min in [
            ("titulo",      "Título",      250, 150),
            ("autores",     "Autores",     180, 120),
            ("year",        "Año",          55,  45),
            ("tipo",        "Tipo",         90,  70),
            ("journal",     "Journal",     150, 100),
            ("estado",      "Estado",       80,  60),
            ("relevancia",  "Relevancia",   80,  60),
            ("carpeta",     "Carpeta",     100,  70),
        ]:
            self.tree.heading(col_id, text=texto,
                              command=lambda c=col_id: self._sort_col(c))
            self.tree.column(col_id, width=ancho, minwidth=ancho_min)

        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=4)
        scrollbar.pack(side="right", fill="y", pady=4, padx=(0, 8))

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._abrir_doi)

    # ── Tab: Catalogar ───────────────────────────────────────────────────

    def _build_tab_catalogar(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  Catalogar  ")

        info_frame = ttk.Frame(tab)
        info_frame.pack(fill="x", padx=12, pady=(12, 4))
        ttk.Label(info_frame, text="Paper seleccionado:").grid(row=0, column=0, sticky="w")
        self.lbl_paper_sel = ttk.Label(info_frame, text="(selecciona un paper en Explorar)",
                                        style="Stat.TLabel")
        self.lbl_paper_sel.grid(row=0, column=1, sticky="w", padx=(8, 0))

        # Detalle del paper
        self.lbl_paper_detail = ttk.Label(info_frame, text="", style="Dim.TLabel")
        self.lbl_paper_detail.grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

        form = ttk.Frame(tab)
        form.pack(fill="x", padx=12, pady=8)

        row = 0
        ttk.Label(form, text="Estado:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_estado = tk.StringVar()
        ttk.Combobox(form, textvariable=self.var_cat_estado, values=[""] + ESTADOS,
                      state="readonly", width=18).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(form, text="Relevancia:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_relevancia = tk.StringVar()
        ttk.Combobox(form, textvariable=self.var_cat_relevancia, values=[""] + RELEVANCIAS,
                      state="readonly", width=18).grid(row=row, column=1, sticky="w", padx=8, pady=4)

        row += 1
        ttk.Label(form, text="Etiquetas:").grid(row=row, column=0, sticky="w", pady=4)
        self.var_cat_etiquetas = tk.StringVar()
        e = ttk.Entry(form, textvariable=self.var_cat_etiquetas, width=40)
        e.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        ttk.Label(form, text="(separadas por coma)", style="Dim.TLabel").grid(
            row=row, column=2, sticky="w")

        row += 1
        ttk.Label(form, text="Notas:").grid(row=row, column=0, sticky="nw", pady=4)
        self.txt_notas = tk.Text(form, width=55, height=5, bg=BG_INPUT, fg=FG,
                                  insertbackground=FG, font=("Segoe UI", 10),
                                  relief="flat", padx=6, pady=4)
        self.txt_notas.grid(row=row, column=1, columnspan=2, sticky="w", padx=8, pady=4)

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
            ("Importar papers nuevos", "Trae papers de Paperpile que no están en Notion",
             self._accion_importar),
            ("Sincronizar", "Importa nuevos + actualiza metadata de existentes",
             self._accion_sincronizar),
            ("Recargar tabla", "Vuelve a leer desde Notion",
             lambda: self._cargar_papers()),
        ]

        for titulo, desc, cmd in actions:
            frame = ttk.Frame(content)
            frame.pack(fill="x", pady=6)
            ttk.Button(frame, text=titulo, style="Accent.TButton",
                        command=cmd, width=25).pack(side="left")
            ttk.Label(frame, text=desc, style="Dim.TLabel").pack(side="left", padx=12)

        ttk.Label(content, text="Log:", style="Dim.TLabel").pack(anchor="w", pady=(16, 4))
        self.txt_log = tk.Text(content, width=85, height=18, bg=BG_CARD, fg=FG,
                                insertbackground=FG, font=("Consolas", 9),
                                relief="flat", padx=8, pady=6, state="disabled")
        self.txt_log.pack(fill="both", expand=True)

    # ─── DATOS ───────────────────────────────────────────────────────────

    def _cargar_papers(self):
        self._set_status("Cargando papers de Notion...")
        threading.Thread(target=self._cargar_papers_bg, daemon=True).start()

    def _cargar_papers_bg(self):
        try:
            paginas = query_database(DB_BIB)
            self.papers_data = []
            carpetas = set()

            for p in paginas:
                props = p.get("properties", {})
                paper = {
                    "id": p["id"],
                    "titulo": extract_property_value(props.get("Título", {})),
                    "autores": extract_property_value(props.get("Autores", {})),
                    "year": extract_property_value(props.get("Año", {})),
                    "tipo": extract_property_value(props.get("Tipo", {})),
                    "journal": extract_property_value(props.get("Journal", {})),
                    "estado": extract_property_value(props.get("Estado", {})),
                    "relevancia": extract_property_value(props.get("Relevancia", {})),
                    "carpeta": extract_property_value(props.get("Carpeta", {})),
                    "doi": extract_property_value(props.get("DOI", {})),
                    "keywords": extract_property_value(props.get("Keywords", {})),
                    "etiquetas": extract_property_value(props.get("Etiquetas", {})),
                    "citekey": extract_property_value(props.get("Citekey", {})),
                    "notas": extract_property_value(props.get("Notas", {})),
                    "abstract": extract_property_value(props.get("Abstract", {})),
                }
                self.papers_data.append(paper)
                if paper["carpeta"]:
                    carpetas.add(paper["carpeta"])

            self.root.after(0, self._actualizar_tabla, sorted(carpetas))
        except Exception as e:
            self.root.after(0, self._set_status, f"Error: {e}")

    def _actualizar_tabla(self, carpetas: list[str] = None):
        if carpetas is not None:
            self.cb_carpeta["values"] = ["Todos"] + carpetas

        self.tree.delete(*self.tree.get_children())
        for paper in self.papers_data:
            self.tree.insert("", "end", iid=paper["id"], values=(
                paper["titulo"], paper["autores"], paper["year"],
                paper["tipo"], paper["journal"], paper["estado"],
                paper["relevancia"], paper["carpeta"],
            ))

        self._actualizar_stats()
        self._set_status(f"{len(self.papers_data)} papers cargados")
        self._filtrar_tabla()

    def _actualizar_stats(self):
        total = len(self.papers_data)
        por_estado = {}
        for p in self.papers_data:
            e = p["estado"] or "Sin estado"
            por_estado[e] = por_estado.get(e, 0) + 1

        partes = [f"{total} papers"]
        for estado in ESTADOS:
            n = por_estado.get(estado, 0)
            if n:
                partes.append(f"{n} {estado.lower()}")
        self.lbl_stats.config(text="  ·  ".join(partes))

    # ─── FILTROS Y ORDENACIÓN ────────────────────────────────────────────

    def _filtrar_tabla(self):
        buscar = self.var_buscar.get().lower()
        tipo = self.var_filtro_tipo.get()
        estado = self.var_filtro_estado.get()
        carpeta = self.var_filtro_carpeta.get()

        self.tree.delete(*self.tree.get_children())
        for paper in self.papers_data:
            if buscar and not any(buscar in paper.get(f, "").lower()
                                  for f in ("titulo", "autores", "journal", "keywords", "citekey")):
                continue
            if tipo != "Todos" and paper["tipo"] != tipo:
                continue
            if estado != "Todos" and paper["estado"] != estado:
                continue
            if carpeta != "Todos" and paper["carpeta"] != carpeta:
                continue

            self.tree.insert("", "end", iid=paper["id"], values=(
                paper["titulo"], paper["autores"], paper["year"],
                paper["tipo"], paper["journal"], paper["estado"],
                paper["relevancia"], paper["carpeta"],
            ))

    def _sort_col(self, col):
        reverse = self.sort_reverse.get(col, False)

        if col == "year":
            def year_key(p):
                val = p.get("year", "")
                if not val:
                    return (1 if not reverse else 0, 0)
                try:
                    return (0 if not reverse else 1, int(val))
                except ValueError:
                    return (1 if not reverse else 0, 0)
            self.papers_data.sort(key=year_key, reverse=reverse)
        else:
            self.papers_data.sort(key=lambda p: p.get(col, "").lower(), reverse=reverse)

        self.sort_reverse[col] = not reverse
        self._filtrar_tabla()

    # ─── EVENTOS ─────────────────────────────────────────────────────────

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        paper = next((p for p in self.papers_data if p["id"] == sel[0]), None)
        if not paper:
            return

        # Primer autor corto
        autores = paper["autores"]
        primer_autor = autores.split(",")[0] if autores else "?"

        self.lbl_paper_sel.config(text=f"{primer_autor} ({paper['year'] or '?'})")
        self.lbl_paper_detail.config(text=paper["titulo"][:90])
        self.var_cat_estado.set(paper["estado"])
        self.var_cat_relevancia.set(paper["relevancia"])
        self.var_cat_etiquetas.set(paper["etiquetas"])
        self.txt_notas.delete("1.0", "end")
        self.txt_notas.insert("1.0", paper["notas"])

    def _abrir_doi(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        paper = next((p for p in self.papers_data if p["id"] == sel[0]), None)
        if paper and paper["doi"]:
            import webbrowser
            webbrowser.open(paper["doi"])

    # ─── CATALOGAR ───────────────────────────────────────────────────────

    def _guardar_catalogacion(self):
        titulo = self.lbl_paper_sel.cget("text")
        if not titulo or titulo.startswith("("):
            messagebox.showwarning("Atención", "Selecciona un paper en la pestaña Explorar primero.")
            return

        sel = self.tree.selection()
        if not sel:
            return
        paper = next((p for p in self.papers_data if p["id"] == sel[0]), None)
        if not paper:
            return

        citekey = paper["citekey"]
        etiquetas_raw = self.var_cat_etiquetas.get().strip()
        etiquetas = [e.strip() for e in etiquetas_raw.split(",") if e.strip()] if etiquetas_raw else None
        notas = self.txt_notas.get("1.0", "end").strip() or None

        self.lbl_cat_status.config(text="Guardando...")

        def _save():
            try:
                result = catalogar(
                    citekey or paper["titulo"],
                    estado=self.var_cat_estado.get() or None,
                    relevancia=self.var_cat_relevancia.get() or None,
                    etiquetas=etiquetas,
                    notas=notas,
                )
                self.root.after(0, self.lbl_cat_status.config, {"text": result})
                self.root.after(0, self._cargar_papers)
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
        self._log("Importando papers de Paperpile...")
        self._set_status("Importando...")

        def _run():
            try:
                result = importar_papers()
                self.root.after(0, self._log, result)
                self.root.after(0, self._set_status, "Importación completada")
                self.root.after(0, self._cargar_papers)
            except Exception as e:
                self.root.after(0, self._log, f"Error: {e}")
                self.root.after(0, self._set_status, "Error en importación")

        threading.Thread(target=_run, daemon=True).start()

    def _accion_sincronizar(self):
        self._log_clear()
        self._log("Sincronizando con Paperpile...")
        self._set_status("Sincronizando...")

        def _run():
            try:
                result = sincronizar()
                self.root.after(0, self._log, result)
                self.root.after(0, self._set_status, "Sincronización completada")
                self.root.after(0, self._cargar_papers)
            except Exception as e:
                self.root.after(0, self._log, f"Error: {e}")
                self.root.after(0, self._set_status, "Error en sincronización")

        threading.Thread(target=_run, daemon=True).start()

    def _set_status(self, text: str):
        self.lbl_status.config(text=text)


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = BibGUI(root)
    root.mainloop()
