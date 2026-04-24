"""
Agente PTN para Notion.

Gestiona las tres fuentes de datos del sistema PTN:
  - PTN-Proyectos: Nombre del Proyecto, Estado, Prioridad, Fecha inicio/límite, Equipo, PLAN
  - PTN-Tareas:    Nombre de la tarea, Estado, Tipo, Prioridad, Plazo, Proyectos (relación)
  - PTN-Notas:     Título, Estado, Proyecto (relación), Próximos Pasos, Obstáculos, Fecha
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import sys
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    get_databases,
    get_data_sources,
    get_pages,
    query_data_source,
    get_database_info,
    create_database,
    create_page,
    update_page_properties,
    extract_property_value,
)

# IDs de los data sources PTN
DS_PROYECTOS = os.getenv("NOTION_DS_PROYECTOS", "27c622cf-315b-8021-87bd-000b9fbe99d3")
DS_TAREAS    = os.getenv("NOTION_DS_TAREAS",    "27c622cf-315b-80c8-9fdd-000bd097774d")
DS_NOTAS     = os.getenv("NOTION_DS_NOTAS",     "27c622cf-315b-80cb-a8b3-000beaa40e29")
PTN_PARENT_PAGE = os.getenv("NOTION_PTN_PARENT_PAGE", "116622cf-315b-8045-a581-f632b7c93f50")

ESTADOS_PTN = {
    "select": {
        "options": [
            {"name": "Sin empezar", "color": "gray"},
            {"name": "En progreso", "color": "yellow"},
            {"name": "En espera", "color": "orange"},
            {"name": "Completado", "color": "green"},
            {"name": "Archivado", "color": "blue"},
        ]
    }
}

PRIORIDADES_PTN = {
    "select": {
        "options": [
            {"name": "Alta", "color": "red"},
            {"name": "Media", "color": "yellow"},
            {"name": "Baja", "color": "gray"},
        ]
    }
}


def _schema_proyectos() -> dict:
    return {
        "Nombre del Proyecto": {"title": {}},
        "Estado": ESTADOS_PTN,
        "Prioridad": PRIORIDADES_PTN,
        "Progreso": {"number": {"format": "percent"}},
        "Fecha de inicio": {"date": {}},
        "Fecha límite": {"date": {}},
        "Equipo": {"multi_select": {"options": []}},
        "Área": {"select": {"options": []}},
        "Etiquetas": {"multi_select": {"options": []}},
        "URL": {"url": {}},
        "PLAN": {"rich_text": {}},
        "Descripción": {"rich_text": {}},
        "Responsable": {"rich_text": {}},
    }


def _schema_tareas() -> dict:
    return {
        "Nombre de la tarea": {"title": {}},
        "Estado": ESTADOS_PTN,
        "Tipo de tarea": {"select": {"options": []}},
        "Prioridad": PRIORIDADES_PTN,
        "Nivel de esfuerzo": {"select": {"options": []}},
        "Plazo": {"date": {}},
        "Proyecto": {"rich_text": {}},
        "Descripción": {"rich_text": {}},
        "Etiquetas": {"multi_select": {"options": []}},
        "Responsable": {"rich_text": {}},
        "Última actualización": {"date": {}},
    }


def _schema_notas() -> dict:
    return {
        "Título": {"title": {}},
        "Estado": ESTADOS_PTN,
        "Estado de Progreso": {"select": {"options": []}},
        "Prioridad": PRIORIDADES_PTN,
        "Fecha": {"date": {}},
        "Fecha de Vencimiento": {"date": {}},
        "Tarea": {"rich_text": {}},
        "Proyecto": {"rich_text": {}},
        "Próximos Pasos": {"rich_text": {}},
        "Obstáculos": {"rich_text": {}},
        "Tiempo Dedicado": {"number": {"format": "number"}},
        "Descripción": {"rich_text": {}},
        "Etiquetas": {"multi_select": {"options": []}},
    }


# ─── UTILIDAD INTERNA ─────────────────────────────────────────────────────────

def _titulo_registro(r: dict) -> str:
    """Extrae el título de un registro de base de datos."""
    props = r.get("properties", {})
    for prop in props.values():
        if isinstance(prop, dict) and prop.get("type") == "title":
            return extract_property_value(prop)
    return "(sin título)"


def _prop(r: dict, nombre: str) -> str:
    """Extrae el valor de una propiedad por nombre."""
    props = r.get("properties", {})
    if nombre in props:
        return extract_property_value(props[nombre])
    return ""


def crear_bases(parent_page_id: str = None) -> dict:
    """Crea las tres bases maestras del sistema PTN en Notion."""
    parent = parent_page_id or PTN_PARENT_PAGE
    if not parent:
        raise ValueError(
            "Falta NOTION_PTN_PARENT_PAGE o un --parent explícito. "
            "Usa la página A0-GTD como contenedor."
        )

    created = {
        "NOTION_DS_PROYECTOS": create_database(parent, "PTN-Proyectos", _schema_proyectos())["id"],
        "NOTION_DS_TAREAS": create_database(parent, "PTN-Tareas", _schema_tareas())["id"],
        "NOTION_DS_NOTAS": create_database(parent, "PTN-Notas", _schema_notas())["id"],
    }
    return created


# ─── PROYECTOS ────────────────────────────────────────────────────────────────

def listar_proyectos(estado: str = None) -> str:
    """
    Lista proyectos de PTN-Proyectos.
    estado: filtrar por valor de Estado (ej: 'Activo', 'En progreso', 'Completado')
    """
    filter_obj = None
    if estado:
        filter_obj = {
            "property": "Estado",
            "select": {"equals": estado}
        }

    registros = query_data_source(DS_PROYECTOS, filter_obj=filter_obj)

    if not registros:
        msg = f"No hay proyectos con estado '{estado}'." if estado else "No hay proyectos."
        return msg

    titulo_filtro = f" [{estado}]" if estado else ""
    lineas = [f"=== PTN-PROYECTOS{titulo_filtro} ({len(registros)}) ===\n"]

    for r in registros:
        nombre    = _titulo_registro(r)
        est       = _prop(r, "Estado")
        prioridad = _prop(r, "Prioridad")
        f_limite  = _prop(r, "Fecha límite")
        progreso  = _prop(r, "Progreso")

        linea = f"  • {nombre}"
        detalles = []
        if est:       detalles.append(f"Estado: {est}")
        if prioridad: detalles.append(f"P: {prioridad}")
        if progreso:  detalles.append(f"{progreso}%")
        if f_limite:  detalles.append(f"→ {f_limite}")
        if detalles:
            linea += f"  ({', '.join(detalles)})"
        linea += f"\n    ID: {r['id']}"
        lineas.append(linea)

    return "\n".join(lineas)


def crear_proyecto(nombre: str, estado: str = "Sin empezar", prioridad: str = None,
                   fecha_inicio: str = None, fecha_limite: str = None,
                   descripcion: str = None, equipo: list[str] = None) -> dict:
    """
    Crea un proyecto en PTN-Proyectos.
    fecha_inicio / fecha_limite: formato YYYY-MM-DD
    equipo: lista de nombres (multi-select)
    """
    props = {
        "Nombre del Proyecto": {"title": [{"text": {"content": nombre}}]},
        "Estado": {"select": {"name": estado}},
    }
    if prioridad:
        props["Prioridad"] = {"select": {"name": prioridad}}
    if fecha_inicio:
        props["Fecha de inicio"] = {"date": {"start": fecha_inicio}}
    if fecha_limite:
        props["Fecha límite"] = {"date": {"start": fecha_limite}}
    if descripcion:
        props["Descripción"] = {"rich_text": [{"text": {"content": descripcion}}]}
    if equipo:
        props["Equipo"] = {"multi_select": [{"name": e} for e in equipo]}

    return create_page(
        parent_id=DS_PROYECTOS,
        title=nombre,
        properties=props,
        is_data_source=True,
    )


# ─── TAREAS ───────────────────────────────────────────────────────────────────

def listar_tareas(estado: str = None, tipo: str = None) -> str:
    """
    Lista tareas de PTN-Tareas.
    estado: filtrar por Estado
    tipo: filtrar por Tipo de tarea
    """
    filters = []
    if estado:
        filters.append({"property": "Estado", "select": {"equals": estado}})
    if tipo:
        filters.append({"property": "Tipo de tarea", "select": {"equals": tipo}})

    filter_obj = None
    if len(filters) == 1:
        filter_obj = filters[0]
    elif len(filters) > 1:
        filter_obj = {"and": filters}

    registros = query_data_source(DS_TAREAS, filter_obj=filter_obj)

    if not registros:
        return "No hay tareas."

    lineas = [f"=== PTN-TAREAS ({len(registros)}) ===\n"]

    for r in registros:
        nombre    = _titulo_registro(r)
        est       = _prop(r, "Estado")
        tipo_t    = _prop(r, "Tipo de tarea")
        prioridad = _prop(r, "Prioridad")
        plazo     = _prop(r, "Plazo")

        linea = f"  • {nombre}"
        detalles = []
        if est:       detalles.append(est)
        if tipo_t:    detalles.append(tipo_t)
        if prioridad: detalles.append(f"P:{prioridad}")
        if plazo:     detalles.append(f"→{plazo}")
        if detalles:
            linea += f"  ({', '.join(detalles)})"
        linea += f"\n    ID: {r['id']}"
        lineas.append(linea)

    return "\n".join(lineas)


def crear_tarea(nombre: str, estado: str = "Sin empezar", tipo: str = None,
                prioridad: str = None, plazo: str = None,
                proyecto_id: str = None, descripcion: str = None) -> dict:
    """
    Crea una tarea en PTN-Tareas.
    plazo: formato YYYY-MM-DD
    proyecto_id: ID de página de PTN-Proyectos para relacionar
    """
    props = {
        "Nombre de la tarea": {"title": [{"text": {"content": nombre}}]},
        "Estado": {"select": {"name": estado}},
    }
    if tipo:
        props["Tipo de tarea"] = {"select": {"name": tipo}}
    if prioridad:
        props["Prioridad"] = {"select": {"name": prioridad}}
    if plazo:
        props["Plazo"] = {"date": {"start": plazo}}
    if descripcion:
        props["Descripción"] = {"rich_text": [{"text": {"content": descripcion}}]}
    if proyecto_id:
        props["Proyecto"] = {"rich_text": [{"text": {"content": proyecto_id}}]}

    return create_page(
        parent_id=DS_TAREAS,
        title=nombre,
        properties=props,
        is_data_source=True,
    )


# ─── NOTAS ────────────────────────────────────────────────────────────────────

def listar_notas(estado: str = None) -> str:
    """Lista notas de PTN-Notas."""
    filter_obj = None
    if estado:
        filter_obj = {"property": "Estado", "select": {"equals": estado}}

    registros = query_data_source(DS_NOTAS, filter_obj=filter_obj)

    if not registros:
        return "No hay notas."

    lineas = [f"=== PTN-NOTAS ({len(registros)}) ===\n"]

    for r in registros:
        titulo  = _titulo_registro(r)
        est     = _prop(r, "Estado")
        fecha   = _prop(r, "Fecha")
        tarea   = _prop(r, "Tarea")
        proyecto = _prop(r, "Proyecto")

        linea = f"  • {titulo}"
        detalles = []
        if est:      detalles.append(est)
        if tarea:    detalles.append(f"T:{tarea}")
        if proyecto: detalles.append(f"[{proyecto}]")
        if fecha:    detalles.append(fecha)
        if detalles:
            linea += f"  ({', '.join(detalles)})"
        linea += f"\n    ID: {r['id']}"
        lineas.append(linea)

    return "\n".join(lineas)


def crear_nota(titulo: str, tarea: str, fecha: str = None, estado: str = None,
               proyecto_id: str = None, descripcion: str = None,
               proximos_pasos: str = None) -> dict:
    """
    Crea una nota en PTN-Notas.
    fecha: formato YYYY-MM-DD
    tarea: referencia obligatoria a la tarea que justifica la nota
    """
    props = {
        "Título": {"title": [{"text": {"content": titulo}}]},
        "Tarea": {"rich_text": [{"text": {"content": tarea}}]},
    }
    if estado:
        props["Estado"] = {"select": {"name": estado}}
    if fecha:
        props["Fecha"] = {"date": {"start": fecha}}
    if descripcion:
        props["Descripción"] = {"rich_text": [{"text": {"content": descripcion}}]}
    if proximos_pasos:
        props["Próximos Pasos"] = {"rich_text": [{"text": {"content": proximos_pasos}}]}
    if proyecto_id:
        props["Proyecto"] = {"rich_text": [{"text": {"content": proyecto_id}}]}

    return create_page(
        parent_id=DS_NOTAS,
        title=titulo,
        properties=props,
        is_data_source=True,
    )


# ─── VISTA GENERAL ────────────────────────────────────────────────────────────

def listar_recursos() -> str:
    """Lista todos los recursos accesibles (sin duplicados)."""
    all_results = get_databases() + get_data_sources()

    # Deduplicar por ID
    seen = set()
    recursos = []
    for r in all_results:
        if r["id"] not in seen:
            seen.add(r["id"])
            recursos.append(r)

    pages = get_pages()
    lineas = ["=== NOTION — RECURSOS ACCESIBLES ===\n"]

    if recursos:
        lineas.append(f"BASES DE DATOS / DATA SOURCES ({len(recursos)})")
        for r in recursos:
            icono = "🗂️" if r.get("object") == "data_source" else "🗃️"
            lineas.append(f"  {icono}  {r['title'] or '(sin título)'}")
            lineas.append(f"      ID: {r['id']}")
    else:
        lineas.append("Sin bases de datos conectadas.")

    lineas.append("")
    lineas.append(f"PÁGINAS ({len(pages)}) — primeras 10")
    for p in pages[:10]:
        lineas.append(f"  📄 {p['title']}  [{p['id'][:8]}...]")
    if len(pages) > 10:
        lineas.append(f"  ... y {len(pages) - 10} más")

    return "\n".join(lineas)


def estado_ptn() -> str:
    """Resumen rápido del sistema PTN."""
    proyectos = query_data_source(DS_PROYECTOS)
    tareas    = query_data_source(DS_TAREAS)
    notas     = query_data_source(DS_NOTAS)

    lineas = ["=== ESTADO PTN ===\n"]
    lineas.append(f"  🗂️  Proyectos : {len(proyectos)}")
    lineas.append(f"  ✅  Tareas    : {len(tareas)}")
    lineas.append(f"  📝 Notas     : {len(notas)}")

    return "\n".join(lineas)


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente PTN para Notion")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("recursos",  help="Listar recursos accesibles")
    subparsers.add_parser("estado",    help="Resumen del sistema PTN")
    p_setup = subparsers.add_parser("crear-bases", help="Crear las bases maestras de PTN")
    p_setup.add_argument("--parent", default=None, help="ID de la página padre en Notion")

    p_db = subparsers.add_parser("db", help="Inspeccionar base de datos o data source")
    p_db.add_argument("database_id")

    p_pry = subparsers.add_parser("proyectos", help="Listar proyectos")
    p_pry.add_argument("--estado", default=None)

    p_tar = subparsers.add_parser("tareas", help="Listar tareas")
    p_tar.add_argument("--estado", default=None)
    p_tar.add_argument("--tipo",   default=None)

    p_not = subparsers.add_parser("notas", help="Listar notas")
    p_not.add_argument("--estado", default=None)

    p_np = subparsers.add_parser("nuevo-proyecto", help="Crear proyecto")
    p_np.add_argument("nombre")
    p_np.add_argument("--estado",    default="Sin empezar")
    p_np.add_argument("--prioridad", default=None)
    p_np.add_argument("--inicio",    default=None, help="YYYY-MM-DD")
    p_np.add_argument("--limite",    default=None, help="YYYY-MM-DD")

    p_nt = subparsers.add_parser("nueva-tarea", help="Crear tarea")
    p_nt.add_argument("nombre")
    p_nt.add_argument("--estado",    default="Sin empezar")
    p_nt.add_argument("--tipo",      default=None)
    p_nt.add_argument("--prioridad", default=None)
    p_nt.add_argument("--plazo",     default=None, help="YYYY-MM-DD")
    p_nt.add_argument("--proyecto",  default=None, help="ID del proyecto")

    p_nn = subparsers.add_parser("nueva-nota", help="Crear nota")
    p_nn.add_argument("titulo")
    p_nn.add_argument("--tarea", required=True, help="ID o referencia textual de la tarea")
    p_nn.add_argument("--fecha",    default=None, help="YYYY-MM-DD")
    p_nn.add_argument("--proyecto", default=None, help="ID del proyecto")

    p_lr = subparsers.add_parser("link-repo-to-ptn", help="Enlazar repo GitHub (GIT) a proyecto PTN via INX")
    p_lr.add_argument("repo", help="Nombre exacto del repo en GIT-Repositorios")
    p_lr.add_argument("proyecto", help="ID o nombre del proyecto PTN")

    p_lp = subparsers.add_parser("link-paper-to-ptn", help="Enlazar paper Paperpile (BIB) a proyecto PTN via INX")
    p_lp.add_argument("citekey", help="Citekey del paper en BIB-Bibliografía")
    p_lp.add_argument("proyecto", help="ID o nombre del proyecto PTN")

    args = parser.parse_args()

    if args.comando == "recursos":
        print(listar_recursos())
    elif args.comando == "estado":
        print(estado_ptn())
    elif args.comando == "crear-bases":
        created = crear_bases(args.parent)
        print("=== PTN CREADO ===")
        for key, value in created.items():
            print(f"{key}={value}")
    elif args.comando == "db":
        info = get_database_info(args.database_id)
        print(f"=== {info['title']} ===")
        print(f"ID: {info['id']}")
        props = ', '.join(info['properties']) or '(ninguna)'
        print(f"Propiedades: {props}")
        if info["data_sources"]:
            print(f"\nDATA SOURCES ({len(info['data_sources'])}):")
            for ds in info["data_sources"]:
                print(f"  🗂️  {ds['title']}  ID: {ds['id']}")
                print(f"      Propiedades: {', '.join(ds['properties'])}")
    elif args.comando == "proyectos":
        print(listar_proyectos(estado=args.estado))
    elif args.comando == "tareas":
        print(listar_tareas(estado=args.estado, tipo=args.tipo))
    elif args.comando == "notas":
        print(listar_notas(estado=args.estado))
    elif args.comando == "nuevo-proyecto":
        p = crear_proyecto(args.nombre, estado=args.estado, prioridad=args.prioridad,
                           fecha_inicio=args.inicio, fecha_limite=args.limite)
        print(f"Proyecto creado: {p['id']}")
    elif args.comando == "nueva-tarea":
        t = crear_tarea(args.nombre, estado=args.estado, tipo=args.tipo,
                        prioridad=args.prioridad, plazo=args.plazo,
                        proyecto_id=args.proyecto)
        print(f"Tarea creada: {t['id']}")
    elif args.comando == "nueva-nota":
        n = crear_nota(args.titulo, tarea=args.tarea, fecha=args.fecha, proyecto_id=args.proyecto)
        print(f"Nota creada: {n['id']}")
    elif args.comando == "link-repo-to-ptn":
        from tools.sync_inx_links import link_repo_to_ptn
        res = link_repo_to_ptn(args.repo, args.proyecto)
        print(f"Enlazado {res['key']} -> proyecto {res['proyecto_id']}")
    elif args.comando == "link-paper-to-ptn":
        from tools.sync_inx_links import link_paper_to_ptn
        res = link_paper_to_ptn(args.citekey, args.proyecto)
        print(f"Enlazado {res['key']} -> proyecto {res['proyecto_id']}")
    else:
        parser.print_help()
