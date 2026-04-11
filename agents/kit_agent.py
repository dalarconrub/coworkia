"""
Agente KIT para Notion.

Modelo canónico:
  - una sola base maestra `KIT`
  - un campo `Tipo` separa Knowledge / Information / Tool
  - las vistas se construyen en Notion, no con tres bases distintas
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    query_data_source,
    create_page,
    create_database,
    extract_property_value,
)

DB_KIT = os.getenv("NOTION_DB_KIT", "")
KIT_PARENT_PAGE = os.getenv("NOTION_KIT_PARENT_PAGE", os.getenv("NOTION_REPOS_PARENT_PAGE", ""))

TIPOS_KIT = {
    "Knowledge": "Knowledge",
    "Information": "Information",
    "Tool": "Tool",
}

SUBTIPOS_KIT = [
    "Concepto",
    "Sintesis",
    "Metodologia",
    "Paper",
    "Articulo",
    "Fuente",
    "App",
    "Servicio",
    "IA",
]

ESTADOS_KIT = ["Activo", "En revision", "Archivado", "Descartado"]


def _schema_kit() -> dict:
    return {
        "Titulo": {"title": {}},
        "Tipo": {
            "select": {
                "options": [
                    {"name": "Knowledge", "color": "blue"},
                    {"name": "Information", "color": "yellow"},
                    {"name": "Tool", "color": "green"},
                ]
            }
        },
        "Subtipo": {"select": {"options": [{"name": s} for s in SUBTIPOS_KIT]}},
        "Estado": {"select": {"options": [{"name": s} for s in ESTADOS_KIT]}},
        "Resumen": {"rich_text": {}},
        "Etiquetas": {"multi_select": {"options": []}},
        "Fuente / Autor": {"rich_text": {}},
        "Enlace": {"url": {}},
        "Nivel de confianza": {"select": {"options": []}},
        "Fecha de publicacion": {"date": {}},
        "Extractos": {"rich_text": {}},
        "Area": {"select": {"options": []}},
        "Usada en": {"rich_text": {}},
        "Archivos": {"files": {}},
    }


def crear_base(parent_page_id: str = None) -> dict:
    """Crea la base maestra KIT en Notion."""
    parent = parent_page_id or KIT_PARENT_PAGE
    if not parent:
        raise ValueError(
            "Falta NOTION_KIT_PARENT_PAGE o un --parent explicito. "
            "Usa la pagina A4-ARX como contenedor."
        )
    result = create_database(parent, "KIT", _schema_kit())
    db_id = result["id"]
    print(f"Base de datos creada: {db_id}")
    print(f"Anade a tu .env:\n  NOTION_DB_KIT={db_id}")
    return result


def _prop(r: dict, nombre: str) -> str:
    props = r.get("properties", {})
    return extract_property_value(props[nombre]) if nombre in props else ""


def _titulo(r: dict) -> str:
    return _prop(r, "Titulo") or "(sin titulo)"


def _build_filter(tipo: str = None, subtipo: str = None, etiqueta: str = None) -> dict | None:
    filters = []
    if tipo:
        filters.append({"property": "Tipo", "select": {"equals": tipo}})
    if subtipo:
        filters.append({"property": "Subtipo", "select": {"equals": subtipo}})
    if etiqueta:
        filters.append({"property": "Etiquetas", "multi_select": {"contains": etiqueta}})
    if len(filters) == 1:
        return filters[0]
    if len(filters) > 1:
        return {"and": filters}
    return None


def _query_kit(filter_obj: dict = None) -> list[dict]:
    if not DB_KIT:
        raise ValueError("Falta NOTION_DB_KIT en .env.")
    return query_data_source(DB_KIT, filter_obj=filter_obj)


def _format_lista(nombre: str, registros: list[dict]) -> str:
    if not registros:
        return f"No hay entradas en {nombre}."
    lineas = [f"=== {nombre} ({len(registros)}) ===\n"]
    for r in registros:
        titulo = _titulo(r)
        tipo = _prop(r, "Tipo")
        subtipo = _prop(r, "Subtipo")
        estado = _prop(r, "Estado")
        etiquetas = _prop(r, "Etiquetas")
        detalles = [d for d in [tipo, subtipo, estado] if d]
        if etiquetas:
            detalles.append(f"[{etiquetas}]")
        linea = f"  • {titulo}"
        if detalles:
            linea += f"  ({', '.join(detalles)})"
        linea += f"\n    ID: {r['id']}"
        lineas.append(linea)
    return "\n".join(lineas)


def listar_knowledge(subtipo: str = None, etiqueta: str = None) -> str:
    registros = _query_kit(_build_filter(tipo=TIPOS_KIT["Knowledge"], subtipo=subtipo, etiqueta=etiqueta))
    return _format_lista("KIT-KNOWLEDGE", registros)


def listar_information(subtipo: str = None, etiqueta: str = None) -> str:
    registros = _query_kit(_build_filter(tipo=TIPOS_KIT["Information"], subtipo=subtipo, etiqueta=etiqueta))
    return _format_lista("KIT-INFORMATION", registros)


def listar_tools(subtipo: str = None, etiqueta: str = None) -> str:
    registros = _query_kit(_build_filter(tipo=TIPOS_KIT["Tool"], subtipo=subtipo, etiqueta=etiqueta))
    return _format_lista("KIT-TOOLS", registros)


def buscar_kit(texto: str) -> str:
    registros = _query_kit()
    resultados = []
    for r in registros:
        titulo = _titulo(r)
        resumen = _prop(r, "Resumen")
        if texto.lower() in titulo.lower() or texto.lower() in resumen.lower():
            resultados.append(r)
    return _format_lista(f"BUSQUEDA KIT: '{texto}'", resultados) if resultados else f"Sin resultados para '{texto}' en KIT."


def estado_kit() -> str:
    registros = _query_kit()
    conteos = {"Knowledge": 0, "Information": 0, "Tool": 0}
    for r in registros:
        tipo = _prop(r, "Tipo")
        if tipo in conteos:
            conteos[tipo] += 1
    return "\n".join([
        "=== ESTADO KIT ===\n",
        f"  Knowledge   : {conteos['Knowledge']} entradas",
        f"  Information : {conteos['Information']} entradas",
        f"  Tools       : {conteos['Tool']} entradas",
        f"\n  TOTAL: {len(registros)} entradas",
    ])


def _nueva_entrada(
    titulo: str,
    tipo: str,
    subtipo: str = None,
    estado: str = None,
    resumen: str = None,
    etiquetas: list[str] = None,
    enlace: str = None,
    autor: str = None,
) -> dict:
    if not DB_KIT:
        raise ValueError("Falta NOTION_DB_KIT en .env.")

    props = {
        "Titulo": {"title": [{"text": {"content": titulo}}]},
        "Tipo": {"select": {"name": tipo}},
    }
    if subtipo:
        props["Subtipo"] = {"select": {"name": subtipo}}
    if estado:
        props["Estado"] = {"select": {"name": estado}}
    if resumen:
        props["Resumen"] = {"rich_text": [{"text": {"content": resumen}}]}
    if etiquetas:
        props["Etiquetas"] = {"multi_select": [{"name": e} for e in etiquetas]}
    if enlace:
        props["Enlace"] = {"url": enlace}
    if autor:
        props["Fuente / Autor"] = {"rich_text": [{"text": {"content": autor}}]}

    return create_page(parent_id=DB_KIT, title=titulo, properties=props, is_data_source=True)


def nueva_knowledge(titulo: str, **kwargs) -> dict:
    return _nueva_entrada(titulo, TIPOS_KIT["Knowledge"], **kwargs)


def nueva_information(titulo: str, **kwargs) -> dict:
    return _nueva_entrada(titulo, TIPOS_KIT["Information"], **kwargs)


def nueva_tool(titulo: str, **kwargs) -> dict:
    return _nueva_entrada(titulo, TIPOS_KIT["Tool"], **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente KIT para Notion")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("estado", help="Resumen del KIT")
    p_setup = subparsers.add_parser("crear-db", help="Crear la base maestra KIT")
    p_setup.add_argument("--parent", default=None, help="ID de la pagina padre en Notion")

    p_k = subparsers.add_parser("knowledge", help="Listar conocimiento")
    p_i = subparsers.add_parser("information", help="Listar informacion externa")
    p_t = subparsers.add_parser("tools", help="Listar herramientas")
    for p in [p_k, p_i, p_t]:
        p.add_argument("--subtipo", default=None)
        p.add_argument("--etiqueta", default=None)

    p_b = subparsers.add_parser("buscar", help="Buscar en todo KIT")
    p_b.add_argument("texto")

    for cmd in ["nueva-knowledge", "nueva-information", "nueva-tool"]:
        p = subparsers.add_parser(cmd, help=f"Crear entrada en {cmd}")
        p.add_argument("titulo")
        p.add_argument("--subtipo", default=None)
        p.add_argument("--estado", default=None)
        p.add_argument("--resumen", default=None)
        p.add_argument("--enlace", default=None)
        p.add_argument("--autor", default=None)
        p.add_argument("--etiquetas", nargs="*", default=None)

    args = parser.parse_args()

    if args.comando == "estado":
        print(estado_kit())
    elif args.comando == "crear-db":
        crear_base(args.parent)
    elif args.comando == "knowledge":
        print(listar_knowledge(subtipo=args.subtipo, etiqueta=args.etiqueta))
    elif args.comando == "information":
        print(listar_information(subtipo=args.subtipo, etiqueta=args.etiqueta))
    elif args.comando == "tools":
        print(listar_tools(subtipo=args.subtipo, etiqueta=args.etiqueta))
    elif args.comando == "buscar":
        print(buscar_kit(args.texto))
    elif args.comando == "nueva-knowledge":
        r = nueva_knowledge(
            args.titulo,
            subtipo=args.subtipo,
            estado=args.estado,
            resumen=args.resumen,
            enlace=args.enlace,
            autor=args.autor,
            etiquetas=args.etiquetas,
        )
        print(f"Creado en KIT: {r['id']}")
    elif args.comando == "nueva-information":
        r = nueva_information(
            args.titulo,
            subtipo=args.subtipo,
            estado=args.estado,
            resumen=args.resumen,
            enlace=args.enlace,
            autor=args.autor,
            etiquetas=args.etiquetas,
        )
        print(f"Creado en KIT: {r['id']}")
    elif args.comando == "nueva-tool":
        r = nueva_tool(
            args.titulo,
            subtipo=args.subtipo,
            estado=args.estado,
            resumen=args.resumen,
            enlace=args.enlace,
            autor=args.autor,
            etiquetas=args.etiquetas,
        )
        print(f"Creado en KIT: {r['id']}")
    else:
        parser.print_help()
