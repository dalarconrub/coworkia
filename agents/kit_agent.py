"""
Agente KIT para Notion.

Gestiona las tres fuentes de conocimiento del sistema KIT:
  - KIT-Knowledge:    Conocimiento interno (ideas, conceptos, síntesis propias)
  - KIT-Information:  Información externa (artículos, papers, fuentes)
  - KIT-Tools:        Herramientas (apps, software, servicios)

Schema compartido:
  Título/Referencia/Fuente, Tipo, Estado, Resumen, Etiquetas,
  Fuente/Autor, Enlace, Nivel de confianza, Fecha de publicación,
  Extractos, Proyectos (rel), Tareas (rel), Notas (rel),
  Referencias relacionadas (rel), Usada en, Archivos
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    query_data_source,
    get_database_info,
    create_page,
    extract_property_value,
)

DS_KNOWLEDGE   = os.getenv("NOTION_DS_KIT_KNOWLEDGE",   "2ad622cf-315b-80a2-a13e-000b063d2ca2")
DS_INFORMATION = os.getenv("NOTION_DS_KIT_INFORMATION", "2ab622cf-315b-8011-b53d-000b43838fb3")
DS_TOOLS       = os.getenv("NOTION_DS_KIT_TOOLS",       "2ad622cf-315b-8029-bc67-000baecc1150")

# Mapeo fuente → nombre de la propiedad título (cada fuente usa uno distinto)
TITLE_PROP = {
    DS_KNOWLEDGE:   "Fuente",
    DS_INFORMATION: "Referencia",
    DS_TOOLS:       "Aplicaciones",
}


# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def _titulo(r: dict, ds_id: str) -> str:
    """Extrae el título según el data source."""
    props = r.get("properties", {})
    # Buscar por nombre conocido
    nombre_prop = TITLE_PROP.get(ds_id, "")
    if nombre_prop and nombre_prop in props:
        return extract_property_value(props[nombre_prop])
    # Fallback: primera propiedad de tipo title
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return extract_property_value(prop)
    return "(sin título)"


def _prop(r: dict, nombre: str) -> str:
    props = r.get("properties", {})
    return extract_property_value(props[nombre]) if nombre in props else ""


def _fmt_registro(r: dict, ds_id: str) -> str:
    titulo   = _titulo(r, ds_id)
    tipo     = _prop(r, "Tipo")
    estado   = _prop(r, "Estado")
    etiquetas = _prop(r, "Etiquetas")
    confianza = _prop(r, "Nivel de confianza")

    linea = f"  • {titulo}"
    detalles = []
    if tipo:      detalles.append(tipo)
    if estado:    detalles.append(estado)
    if etiquetas: detalles.append(f"[{etiquetas}]")
    if confianza: detalles.append(f"★{confianza}")
    if detalles:
        linea += f"  ({', '.join(detalles)})"
    linea += f"\n    ID: {r['id']}"
    return linea


# ─── CONSULTAS ────────────────────────────────────────────────────────────────

def listar_knowledge(tipo: str = None, etiqueta: str = None) -> str:
    """Lista entradas de KIT-Knowledge (conocimiento interno)."""
    filter_obj = _build_filter(tipo, etiqueta)
    registros = query_data_source(DS_KNOWLEDGE, filter_obj=filter_obj)
    return _format_lista("KIT-KNOWLEDGE", registros, DS_KNOWLEDGE)


def listar_information(tipo: str = None, etiqueta: str = None) -> str:
    """Lista entradas de KIT-Information (información externa)."""
    filter_obj = _build_filter(tipo, etiqueta)
    registros = query_data_source(DS_INFORMATION, filter_obj=filter_obj)
    return _format_lista("KIT-INFORMATION", registros, DS_INFORMATION)


def listar_tools(tipo: str = None, etiqueta: str = None) -> str:
    """Lista entradas de KIT-Tools (herramientas)."""
    filter_obj = _build_filter(tipo, etiqueta)
    registros = query_data_source(DS_TOOLS, filter_obj=filter_obj)
    return _format_lista("KIT-TOOLS", registros, DS_TOOLS)


def buscar_kit(texto: str) -> str:
    """Busca en los tres data sources del KIT por título/resumen."""
    resultados = []
    for ds_id, nombre in [(DS_KNOWLEDGE, "Knowledge"), (DS_INFORMATION, "Information"), (DS_TOOLS, "Tools")]:
        registros = query_data_source(ds_id)
        for r in registros:
            titulo  = _titulo(r, ds_id)
            resumen = _prop(r, "Resumen")
            if texto.lower() in titulo.lower() or texto.lower() in resumen.lower():
                resultados.append((nombre, r, ds_id))

    if not resultados:
        return f"Sin resultados para '{texto}' en el KIT."

    lineas = [f"=== BÚSQUEDA KIT: '{texto}' ({len(resultados)} resultados) ===\n"]
    for fuente, r, ds_id in resultados:
        lineas.append(f"  [{fuente}] {_fmt_registro(r, ds_id)}")
    return "\n".join(lineas)


def estado_kit() -> str:
    """Resumen rápido del sistema KIT."""
    k = query_data_source(DS_KNOWLEDGE)
    i = query_data_source(DS_INFORMATION)
    t = query_data_source(DS_TOOLS)
    lineas = [
        "=== ESTADO KIT ===\n",
        f"  🧠 Knowledge   : {len(k)} entradas",
        f"  📰 Information : {len(i)} entradas",
        f"  🔧 Tools       : {len(t)} entradas",
        f"\n  TOTAL: {len(k)+len(i)+len(t)} entradas",
    ]
    return "\n".join(lineas)


# ─── CREACIÓN ─────────────────────────────────────────────────────────────────

def _nueva_entrada(ds_id: str, titulo: str, tipo: str = None, estado: str = None,
                   resumen: str = None, etiquetas: list[str] = None,
                   enlace: str = None, autor: str = None,
                   proyecto_id: str = None) -> dict:
    """Crea una entrada en cualquier data source del KIT."""
    title_prop = TITLE_PROP.get(ds_id, "Referencia")
    props = {
        title_prop: {"title": [{"text": {"content": titulo}}]},
    }
    if tipo:
        props["Tipo"] = {"select": {"name": tipo}}
    if estado:
        props["Estado"] = {"status": {"name": estado}}
    if resumen:
        props["Resumen"] = {"rich_text": [{"text": {"content": resumen}}]}
    if etiquetas:
        props["Etiquetas"] = {"multi_select": [{"name": e} for e in etiquetas]}
    if enlace:
        props["Enlace"] = {"url": enlace}
    if autor:
        props["Fuente / Autor"] = {"rich_text": [{"text": {"content": autor}}]}
    if proyecto_id:
        props["Proyectos"] = {"relation": [{"id": proyecto_id}]}

    return create_page(parent_id=ds_id, title=titulo, properties=props, is_data_source=True)


def nueva_knowledge(titulo: str, **kwargs) -> dict:
    """Crea una entrada en KIT-Knowledge."""
    return _nueva_entrada(DS_KNOWLEDGE, titulo, **kwargs)


def nueva_information(titulo: str, **kwargs) -> dict:
    """Crea una entrada en KIT-Information."""
    return _nueva_entrada(DS_INFORMATION, titulo, **kwargs)


def nueva_tool(titulo: str, **kwargs) -> dict:
    """Crea una entrada en KIT-Tools."""
    return _nueva_entrada(DS_TOOLS, titulo, **kwargs)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _build_filter(tipo: str, etiqueta: str) -> dict | None:
    filters = []
    if tipo:
        filters.append({"property": "Tipo", "select": {"equals": tipo}})
    if etiqueta:
        filters.append({"property": "Etiquetas", "multi_select": {"contains": etiqueta}})
    if len(filters) == 1:
        return filters[0]
    if len(filters) > 1:
        return {"and": filters}
    return None


def _format_lista(nombre: str, registros: list, ds_id: str) -> str:
    if not registros:
        return f"No hay entradas en {nombre}."
    lineas = [f"=== {nombre} ({len(registros)}) ===\n"]
    for r in registros:
        lineas.append(_fmt_registro(r, ds_id))
    return "\n".join(lineas)


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente KIT para Notion")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("estado", help="Resumen del KIT")

    p_k = subparsers.add_parser("knowledge",   help="Listar conocimiento")
    p_i = subparsers.add_parser("information", help="Listar información externa")
    p_t = subparsers.add_parser("tools",       help="Listar herramientas")
    for p in [p_k, p_i, p_t]:
        p.add_argument("--tipo",     default=None)
        p.add_argument("--etiqueta", default=None)

    p_b = subparsers.add_parser("buscar", help="Buscar en todo el KIT")
    p_b.add_argument("texto")

    for cmd, fn_name in [("nueva-knowledge", "knowledge"), ("nueva-information", "information"), ("nueva-tool", "tool")]:
        p = subparsers.add_parser(cmd, help=f"Crear entrada en KIT-{fn_name.capitalize()}")
        p.add_argument("titulo")
        p.add_argument("--tipo",     default=None)
        p.add_argument("--estado",   default=None)
        p.add_argument("--resumen",  default=None)
        p.add_argument("--enlace",   default=None)
        p.add_argument("--autor",    default=None)
        p.add_argument("--etiquetas", nargs="*", default=None)

    args = parser.parse_args()

    if args.comando == "estado":
        print(estado_kit())
    elif args.comando == "knowledge":
        print(listar_knowledge(tipo=args.tipo, etiqueta=args.etiqueta))
    elif args.comando == "information":
        print(listar_information(tipo=args.tipo, etiqueta=args.etiqueta))
    elif args.comando == "tools":
        print(listar_tools(tipo=args.tipo, etiqueta=args.etiqueta))
    elif args.comando == "buscar":
        print(buscar_kit(args.texto))
    elif args.comando == "nueva-knowledge":
        r = nueva_knowledge(args.titulo, tipo=args.tipo, estado=args.estado,
                            resumen=args.resumen, enlace=args.enlace,
                            autor=args.autor, etiquetas=args.etiquetas)
        print(f"Creado en Knowledge: {r['id']}")
    elif args.comando == "nueva-information":
        r = nueva_information(args.titulo, tipo=args.tipo, estado=args.estado,
                              resumen=args.resumen, enlace=args.enlace,
                              autor=args.autor, etiquetas=args.etiquetas)
        print(f"Creado en Information: {r['id']}")
    elif args.comando == "nueva-tool":
        r = nueva_tool(args.titulo, tipo=args.tipo, estado=args.estado,
                       resumen=args.resumen, enlace=args.enlace,
                       autor=args.autor, etiquetas=args.etiquetas)
        print(f"Creado en Tools: {r['id']}")
    else:
        parser.print_help()
