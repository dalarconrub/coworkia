"""
Agente KIT para Notion.

Modelo canónico:
  - una sola base maestra `KIT`
  - un campo `Tipo` separa Knowledge / Information / Tool
  - las vistas se construyen en Notion, no con tres bases distintas
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

sys.stdout.reconfigure(encoding="utf-8")
from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import (
    query_data_source,
    create_page,
    create_database,
    get_data_source_schema,
    resolve_data_source_id,
    update_page_properties,
    update_database_properties,
    extract_property_value,
)
from tools.google_keep_tools import load_keep_export

DB_KIT = os.getenv("NOTION_DB_KIT", "")
KIT_PARENT_PAGE = os.getenv("NOTION_KIT_PARENT_PAGE", os.getenv("NOTION_GIT_PARENT_PAGE", ""))

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
    "Nota",
    "App",
    "Servicio",
    "IA",
]

ESTADOS_KIT = ["Activo", "En revision", "Archivado", "Descartado"]
KEEP_ID_PROP = "Google Keep ID"
UPDATED_AT_PROP = "Fecha de actualizacion"


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
        "Fecha de actualizacion": {"date": {}},
        "Extractos": {"rich_text": {}},
        "Area": {"select": {"options": []}},
        "Usada en": {"rich_text": {}},
        "Usada en notas": {"relation": {"database_id": os.getenv("OBSIDIAN_DB", ""), "type": "single_property", "single_property": {}}},
        "Google Keep ID": {"rich_text": {}},
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
    ds_id = resolve_data_source_id(db_id)
    print(f"Base de datos creada: {db_id}")
    print(f"Data source resuelto: {ds_id}")
    print(f"Anade a tu .env:\n  NOTION_DB_KIT={ds_id}")
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


def _ensure_kit_schema() -> None:
    if not DB_KIT:
        raise ValueError("Falta NOTION_DB_KIT en .env.")
    schema = get_data_source_schema(DB_KIT)
    missing = {}
    props = schema.get("properties", [])
    if KEEP_ID_PROP not in props:
        missing[KEEP_ID_PROP] = {"rich_text": {}}
    if UPDATED_AT_PROP not in props:
        missing[UPDATED_AT_PROP] = {"date": {}}
    if missing:
        update_database_properties(DB_KIT, missing)


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


def _keep_props(note: dict, tipo: str, subtipo: str, only_if_empty: dict | None = None) -> dict:
    props = {
        "Titulo": {"title": [{"text": {"content": note["title"][:2000]}}]},
        "Tipo": {"select": {"name": tipo}},
        "Subtipo": {"select": {"name": subtipo}},
        KEEP_ID_PROP: {"rich_text": [{"text": {"content": note["keep_id"][:500]}}]},
        "Fuente / Autor": {"rich_text": [{"text": {"content": "Google Keep"}}]},
    }

    estado = "Archivado" if note.get("archived") else "Activo"
    props["Estado"] = {"select": {"name": estado}}

    if note.get("summary"):
        props["Resumen"] = {"rich_text": [{"text": {"content": note["summary"][:2000]}}]}
    if note.get("labels"):
        props["Etiquetas"] = {"multi_select": [{"name": e[:100]} for e in note["labels"][:25]]}
    if note.get("created_date"):
        props["Fecha de publicacion"] = {"date": {"start": note["created_date"]}}
    if note.get("updated_date"):
        props[UPDATED_AT_PROP] = {"date": {"start": note["updated_date"]}}
    if note.get("extracts"):
        props["Extractos"] = {"rich_text": [{"text": {"content": note["extracts"][:2000]}}]}
    if note.get("attachments"):
        joined = "\n".join(note["attachments"])
        props["Usada en"] = {"rich_text": [{"text": {"content": joined[:2000]}}]}

    if only_if_empty:
        merged = dict(only_if_empty)
        merged.update(props)
        return merged
    return props


def _existing_keep_entries() -> dict[str, dict]:
    existing: dict[str, dict] = {}
    for row in _query_kit():
        keep_id = _prop(row, KEEP_ID_PROP)
        if keep_id:
            existing[keep_id] = row
    return existing


def _check_keep_existing_integrity(existentes: dict) -> str | None:
    """Heuristica defensiva: si KIT tiene >100 filas con Subtipo='Nota' pero
    NINGUNA con 'Google Keep ID' poblado, importar ahora duplicaria todas.

    Caso historico: 2026-04-21 el re-run de import_keep sin el campo Keep ID
    en schema produjo 821 x 3 = ~2463 filas duplicadas en KIT. _ensure_kit_schema
    cubre el caso de schema faltante en creaciones futuras, pero no repara
    filas creadas ANTES de que existiera la propiedad.

    Devuelve None si esta OK, o mensaje de error si debe abortar.
    """
    if existentes:
        return None
    rows = _query_kit()
    notas = sum(1 for r in rows if _prop(r, "Subtipo") == "Nota")
    if notas > 100:
        return (
            f"Error: KIT tiene {notas} filas con Subtipo='Nota' pero NINGUNA "
            f"tiene '{KEEP_ID_PROP}' poblado. Continuar duplicaria todas las notas "
            f"(caso historico 2026-04-21).\n"
            f"  Soluciones:\n"
            f"    1) Backfill manual de '{KEEP_ID_PROP}' en las filas Nota existentes\n"
            f"    2) Archivar primero las filas Nota sin Keep ID (filtro Notion: "
            f"Subtipo=Nota AND Google Keep ID is empty), luego re-importar"
        )
    return None


def importar_keep(
    export_dir: str,
    tipo: str = TIPOS_KIT["Information"],
    subtipo: str = "Nota",
    incluir_archivadas: bool = False,
) -> str:
    if not DB_KIT:
        return "Error: falta NOTION_DB_KIT en .env. Ejecuta 'crear-db' primero."

    _ensure_kit_schema()
    notas = load_keep_export(export_dir)
    existentes = _existing_keep_entries()
    err = _check_keep_existing_integrity(existentes)
    if err:
        return err

    creados = 0
    omitidos = 0
    archivados_omitidos = 0
    errores = 0

    for note in notas:
        if note.get("archived") and not incluir_archivadas:
            archivados_omitidos += 1
            continue
        if note["keep_id"] in existentes:
            omitidos += 1
            continue
        try:
            create_page(
                parent_id=DB_KIT,
                title=note["title"],
                properties=_keep_props(note, tipo=tipo, subtipo=subtipo),
                is_data_source=True,
            )
            creados += 1
        except Exception:
            errores += 1

    return (
        f"\n=== IMPORTACION GOOGLE KEEP -> KIT ===\n"
        f"  Directorio: {export_dir}\n"
        f"  Leidas:     {len(notas)}\n"
        f"  Creadas:    {creados}\n"
        f"  Omitidas:   {omitidos} (ya existian)\n"
        f"  Archivadas: {archivados_omitidos} (saltadas)\n"
        f"  Errores:    {errores}"
    )


def sincronizar_keep(
    export_dir: str,
    tipo: str = TIPOS_KIT["Information"],
    subtipo: str = "Nota",
    incluir_archivadas: bool = False,
) -> str:
    if not DB_KIT:
        return "Error: falta NOTION_DB_KIT en .env. Ejecuta 'crear-db' primero."

    _ensure_kit_schema()
    notas = load_keep_export(export_dir)
    existentes = _existing_keep_entries()
    err = _check_keep_existing_integrity(existentes)
    if err:
        return err

    nuevos = 0
    actualizados = 0
    archivados_omitidos = 0
    errores = 0

    for note in notas:
        if note.get("archived") and not incluir_archivadas:
            archivados_omitidos += 1
            continue
        props = _keep_props(note, tipo=tipo, subtipo=subtipo)
        try:
            if note["keep_id"] in existentes:
                update_page_properties(existentes[note["keep_id"]]["id"], props)
                actualizados += 1
            else:
                create_page(
                    parent_id=DB_KIT,
                    title=note["title"],
                    properties=props,
                    is_data_source=True,
                )
                nuevos += 1
        except Exception:
            errores += 1

    return (
        f"\n=== SINCRONIZACION GOOGLE KEEP -> KIT ===\n"
        f"  Directorio:   {export_dir}\n"
        f"  Leidas:       {len(notas)}\n"
        f"  Nuevas:       {nuevos}\n"
        f"  Actualizadas: {actualizados}\n"
        f"  Archivadas:   {archivados_omitidos} (saltadas)\n"
        f"  Errores:      {errores}"
    )


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

    for cmd in ["importar-keep", "sincronizar-keep"]:
        p = subparsers.add_parser(cmd, help=f"{cmd} desde export de Google Keep")
        p.add_argument("--source", required=True, help="Carpeta del export de Google Keep (Takeout)")
        p.add_argument("--tipo", default=TIPOS_KIT["Information"], choices=list(TIPOS_KIT.values()))
        p.add_argument("--subtipo", default="Nota")
        p.add_argument("--incluir-archivadas", action="store_true")

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
    elif args.comando == "importar-keep":
        print(importar_keep(
            args.source,
            tipo=args.tipo,
            subtipo=args.subtipo,
            incluir_archivadas=args.incluir_archivadas,
        ))
    elif args.comando == "sincronizar-keep":
        print(sincronizar_keep(
            args.source,
            tipo=args.tipo,
            subtipo=args.subtipo,
            incluir_archivadas=args.incluir_archivadas,
        ))
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
