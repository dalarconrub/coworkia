"""
Agente REP (Repositorios) para GitHub + Notion.

Cataloga repositorios de GitHub en una base de datos de Notion.
Funcionalidades:
  - Crear la base de datos REP-Repositorios en Notion
  - Importar todos los repos del usuario
  - Sincronizar metadata (última actividad, estrellas, lenguajes)
  - Catalogar: asignar tipo, estado, versión, proceso
  - Listar repos catalogados con filtros
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    create_database,
    add_page_to_database,
    query_database,
    update_page_properties,
    extract_property_value,
)
from tools.github_tools import (
    get_user_repos,
    get_repo_languages,
    extract_repo_info,
)

DB_REPOS = os.getenv("NOTION_DB_REPOS", "")
REPOS_PARENT_PAGE = os.getenv("NOTION_REPOS_PARENT_PAGE", "")


# ─── SCHEMA DE LA BASE DE DATOS ──────────────────────────────────────────────

DB_SCHEMA = {
    "Nombre": {"title": {}},
    "Estado": {
        "select": {
            "options": [
                {"name": "Activo", "color": "green"},
                {"name": "WIP", "color": "yellow"},
                {"name": "Archivado", "color": "gray"},
                {"name": "Deprecado", "color": "red"},
                {"name": "Pausado", "color": "orange"},
            ]
        }
    },
    "Tipo": {
        "select": {
            "options": [
                {"name": "Proyecto", "color": "blue"},
                {"name": "Librería", "color": "purple"},
                {"name": "Fork", "color": "pink"},
                {"name": "Ejercicio", "color": "yellow"},
                {"name": "Config", "color": "gray"},
                {"name": "Template", "color": "green"},
                {"name": "Script", "color": "orange"},
            ]
        }
    },
    "Lenguajes": {"multi_select": {"options": []}},
    "Etiquetas": {"multi_select": {"options": []}},
    "Descripción": {"rich_text": {}},
    "URL": {"url": {}},
    "Versión de": {
        "select": {"options": []}
    },
    "Proceso": {
        "select": {"options": []}
    },
    "Visibilidad": {
        "select": {
            "options": [
                {"name": "Público", "color": "green"},
                {"name": "Privado", "color": "red"},
            ]
        }
    },
    "Última actividad": {"date": {}},
    "Creado": {"date": {}},
    "Estrellas": {"number": {"format": "number"}},
    "Forks": {"number": {"format": "number"}},
    "Es fork": {"checkbox": {}},
    "Notas": {"rich_text": {}},
}


# ─── SETUP ───────────────────────────────────────────────────────────────────

def crear_base_datos(parent_page_id: str = None) -> dict:
    """Crea la base de datos REP-Repositorios en Notion."""
    parent = parent_page_id or REPOS_PARENT_PAGE
    if not parent:
        raise ValueError(
            "Falta NOTION_REPOS_PARENT_PAGE en .env. "
            "Crea una página en Notion y pon su ID como valor."
        )
    result = create_database(parent, "REP-Repositorios", DB_SCHEMA)
    db_id = result["id"]
    print(f"Base de datos creada: {db_id}")
    print(f"Añade a tu .env:\n  NOTION_DB_REPOS={db_id}")
    return result


# ─── IMPORTAR ────────────────────────────────────────────────────────────────

def _repo_a_propiedades(info: dict, lenguajes: list[str] = None) -> dict:
    """Convierte info de un repo a propiedades Notion."""
    props = {
        "Nombre": {"title": [{"text": {"content": info["nombre"]}}]},
        "Descripción": {"rich_text": [{"text": {"content": info["descripcion"][:2000]}}]},
        "URL": {"url": info["url"]},
        "Visibilidad": {"select": {"name": info["visibilidad"]}},
        "Estrellas": {"number": info["estrellas"]},
        "Forks": {"number": info["forks"]},
        "Es fork": {"checkbox": info["fork"]},
    }

    if info["ultima_actividad"]:
        props["Última actividad"] = {"date": {"start": info["ultima_actividad"]}}
    if info["creado"]:
        props["Creado"] = {"date": {"start": info["creado"]}}

    # Lenguajes
    langs = lenguajes or ([info["lenguaje_principal"]] if info["lenguaje_principal"] else [])
    if langs:
        props["Lenguajes"] = {"multi_select": [{"name": l} for l in langs]}

    # Topics de GitHub como etiquetas
    if info.get("topics"):
        props["Etiquetas"] = {"multi_select": [{"name": t} for t in info["topics"]]}

    # Estado automático
    if info["archivado"]:
        props["Estado"] = {"select": {"name": "Archivado"}}
    else:
        props["Estado"] = {"select": {"name": "Activo"}}

    # Tipo automático
    if info["fork"]:
        props["Tipo"] = {"select": {"name": "Fork"}}

    return props


def importar_repos(db_id: str = None, con_lenguajes: bool = True) -> str:
    """
    Importa todos los repos del usuario a Notion.
    con_lenguajes=True hace una llamada extra por repo para obtener todos los lenguajes.
    """
    database = db_id or DB_REPOS
    if not database:
        return "Error: falta NOTION_DB_REPOS en .env. Ejecuta 'crear-db' primero."

    # Obtener repos existentes para evitar duplicados
    existentes = _repos_existentes(database)

    print("Obteniendo repositorios de GitHub...")
    repos = get_user_repos()
    print(f"Encontrados {len(repos)} repositorios.")

    creados = 0
    omitidos = 0
    errores = 0

    for repo in repos:
        info = extract_repo_info(repo)

        if info["nombre"] in existentes:
            omitidos += 1
            continue

        # Obtener lenguajes detallados
        lenguajes = []
        if con_lenguajes:
            try:
                lang_dict = get_repo_languages(info["full_name"].split("/")[0], info["nombre"])
                lenguajes = list(lang_dict.keys())
            except Exception:
                lenguajes = [info["lenguaje_principal"]] if info["lenguaje_principal"] else []

        props = _repo_a_propiedades(info, lenguajes)

        try:
            add_page_to_database(database, props)
            creados += 1
            print(f"  ✓ {info['nombre']}")
        except Exception as e:
            errores += 1
            print(f"  ✗ {info['nombre']}: {e}")

    return (
        f"\n=== IMPORTACIÓN COMPLETADA ===\n"
        f"  Creados:  {creados}\n"
        f"  Omitidos: {omitidos} (ya existían)\n"
        f"  Errores:  {errores}\n"
        f"  Total GitHub: {len(repos)}"
    )


def sincronizar(db_id: str = None) -> str:
    """Actualiza metadata de repos existentes desde GitHub."""
    database = db_id or DB_REPOS
    if not database:
        return "Error: falta NOTION_DB_REPOS en .env."

    # Obtener repos de Notion y GitHub
    paginas = query_database(database)
    repos_gh = {extract_repo_info(r)["nombre"]: r for r in get_user_repos()}

    actualizados = 0
    no_encontrados = 0

    for pagina in paginas:
        nombre = extract_property_value(pagina["properties"].get("Nombre", {}))
        if nombre not in repos_gh:
            no_encontrados += 1
            continue

        info = extract_repo_info(repos_gh[nombre])

        # Obtener lenguajes
        try:
            lang_dict = get_repo_languages(info["full_name"].split("/")[0], info["nombre"])
            lenguajes = list(lang_dict.keys())
        except Exception:
            lenguajes = []

        props = {}
        if info["ultima_actividad"]:
            props["Última actividad"] = {"date": {"start": info["ultima_actividad"]}}
        if info["creado"]:
            props["Creado"] = {"date": {"start": info["creado"]}}
        props["Estrellas"] = {"number": info["estrellas"]}
        props["Forks"] = {"number": info["forks"]}
        if info.get("url"):
            props["URL"] = {"url": info["url"]}
        if info.get("descripcion"):
            props["Descripción"] = {"rich_text": [{"text": {"content": info["descripcion"][:2000]}}]}
        if info.get("visibilidad"):
            props["Visibilidad"] = {"select": {"name": info["visibilidad"]}}
        if lenguajes:
            props["Lenguajes"] = {"multi_select": [{"name": l} for l in lenguajes]}
        if info["archivado"]:
            props["Estado"] = {"select": {"name": "Archivado"}}

        try:
            update_page_properties(pagina["id"], props)
            actualizados += 1
        except Exception as e:
            print(f"  ✗ {nombre}: {e}")

    return (
        f"\n=== SINCRONIZACIÓN ===\n"
        f"  Actualizados:    {actualizados}\n"
        f"  No en GitHub:    {no_encontrados}\n"
        f"  Total en Notion: {len(paginas)}"
    )


# ─── CATALOGAR ───────────────────────────────────────────────────────────────

def catalogar(nombre: str, tipo: str = None, estado: str = None,
              version_de: str = None, proceso: str = None,
              etiquetas: list[str] = None, notas: str = None,
              db_id: str = None) -> str:
    """Actualiza campos de catalogación de un repo."""
    database = db_id or DB_REPOS
    if not database:
        return "Error: falta NOTION_DB_REPOS en .env."

    pagina = _buscar_repo(database, nombre)
    if not pagina:
        return f"No se encontró el repo '{nombre}' en Notion."

    props = {}
    if tipo:
        props["Tipo"] = {"select": {"name": tipo}}
    if estado:
        props["Estado"] = {"select": {"name": estado}}
    if version_de:
        props["Versión de"] = {"select": {"name": version_de}}
    if proceso:
        props["Proceso"] = {"select": {"name": proceso}}
    if etiquetas:
        props["Etiquetas"] = {"multi_select": [{"name": e} for e in etiquetas]}
    if notas:
        props["Notas"] = {"rich_text": [{"text": {"content": notas}}]}

    if not props:
        return "Sin cambios — especifica al menos un campo."

    update_page_properties(pagina["id"], props)
    return f"Actualizado: {nombre}"


# ─── LISTAR ──────────────────────────────────────────────────────────────────

def listar_repos(estado: str = None, tipo: str = None, proceso: str = None,
                 db_id: str = None) -> str:
    """Lista repos catalogados con filtros opcionales."""
    database = db_id or DB_REPOS
    if not database:
        return "Error: falta NOTION_DB_REPOS en .env."

    filter_obj = _build_filter(estado, tipo, proceso)
    registros = query_database(database, filter_obj=filter_obj)

    if not registros:
        return "No hay repositorios que coincidan."

    lineas = [f"=== REP-REPOSITORIOS ({len(registros)}) ===\n"]
    for r in registros:
        lineas.append(_fmt_repo(r))
    return "\n".join(lineas)


def estado_repos(db_id: str = None) -> str:
    """Resumen del catálogo de repositorios."""
    database = db_id or DB_REPOS
    if not database:
        return "Error: falta NOTION_DB_REPOS en .env."

    registros = query_database(database)
    if not registros:
        return "El catálogo está vacío."

    # Contar por estado y tipo
    por_estado = {}
    por_tipo = {}
    por_proceso = {}

    for r in registros:
        estado = _prop(r, "Estado") or "Sin estado"
        tipo = _prop(r, "Tipo") or "Sin tipo"
        proceso = _prop(r, "Proceso") or ""

        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        if proceso:
            por_proceso[proceso] = por_proceso.get(proceso, 0) + 1

    lineas = [
        f"=== ESTADO REP ({len(registros)} repos) ===\n",
        "Por estado:",
    ]
    for k, v in sorted(por_estado.items(), key=lambda x: -x[1]):
        lineas.append(f"  {k}: {v}")

    lineas.append("\nPor tipo:")
    for k, v in sorted(por_tipo.items(), key=lambda x: -x[1]):
        lineas.append(f"  {k}: {v}")

    if por_proceso:
        lineas.append("\nPor proceso:")
        for k, v in sorted(por_proceso.items(), key=lambda x: -x[1]):
            lineas.append(f"  {k}: {v}")

    return "\n".join(lineas)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _repos_existentes(db_id: str) -> set[str]:
    """Obtiene los nombres de repos ya catalogados."""
    paginas = query_database(db_id)
    nombres = set()
    for p in paginas:
        nombre = extract_property_value(p["properties"].get("Nombre", {}))
        if nombre:
            nombres.add(nombre)
    return nombres


def _buscar_repo(db_id: str, nombre: str) -> dict | None:
    """Busca un repo por nombre exacto."""
    filter_obj = {"property": "Nombre", "title": {"equals": nombre}}
    resultados = query_database(db_id, filter_obj=filter_obj)
    return resultados[0] if resultados else None


def _prop(r: dict, nombre: str) -> str:
    props = r.get("properties", {})
    return extract_property_value(props[nombre]) if nombre in props else ""


def _fmt_repo(r: dict) -> str:
    nombre = _prop(r, "Nombre")
    estado = _prop(r, "Estado")
    tipo = _prop(r, "Tipo")
    lenguajes = _prop(r, "Lenguajes")
    visibilidad = _prop(r, "Visibilidad")
    version_de = _prop(r, "Versión de")
    proceso = _prop(r, "Proceso")
    url = _prop(r, "URL")

    linea = f"  • {nombre}"
    detalles = []
    if estado:      detalles.append(estado)
    if tipo:        detalles.append(tipo)
    if lenguajes:   detalles.append(lenguajes)
    if visibilidad: detalles.append(visibilidad)
    if detalles:
        linea += f"  ({', '.join(detalles)})"

    extras = []
    if version_de: extras.append(f"↑ {version_de}")
    if proceso:    extras.append(f"⟡ {proceso}")
    if extras:
        linea += f"\n    {' | '.join(extras)}"

    linea += f"\n    {url}" if url else ""
    return linea


def _build_filter(estado: str = None, tipo: str = None, proceso: str = None) -> dict | None:
    filters = []
    if estado:
        filters.append({"property": "Estado", "select": {"equals": estado}})
    if tipo:
        filters.append({"property": "Tipo", "select": {"equals": tipo}})
    if proceso:
        filters.append({"property": "Proceso", "select": {"equals": proceso}})
    if len(filters) == 1:
        return filters[0]
    if len(filters) > 1:
        return {"and": filters}
    return None


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente REP - Repositorios GitHub → Notion")
    subparsers = parser.add_subparsers(dest="comando")

    # crear-db
    p_db = subparsers.add_parser("crear-db", help="Crear la base de datos en Notion")
    p_db.add_argument("--parent", default=None, help="ID de la página padre en Notion")

    # importar
    p_imp = subparsers.add_parser("importar", help="Importar repos de GitHub a Notion")
    p_imp.add_argument("--sin-lenguajes", action="store_true", help="No consultar lenguajes (más rápido)")

    # sincronizar
    subparsers.add_parser("sincronizar", help="Actualizar metadata desde GitHub")

    # catalogar
    p_cat = subparsers.add_parser("catalogar", help="Catalogar un repo")
    p_cat.add_argument("nombre", help="Nombre del repo")
    p_cat.add_argument("--tipo", default=None)
    p_cat.add_argument("--estado", default=None)
    p_cat.add_argument("--version-de", default=None)
    p_cat.add_argument("--proceso", default=None)
    p_cat.add_argument("--etiquetas", nargs="*", default=None)
    p_cat.add_argument("--notas", default=None)

    # listar
    p_list = subparsers.add_parser("listar", help="Listar repos catalogados")
    p_list.add_argument("--estado", default=None)
    p_list.add_argument("--tipo", default=None)
    p_list.add_argument("--proceso", default=None)

    # estado
    subparsers.add_parser("estado", help="Resumen del catálogo")

    args = parser.parse_args()

    if args.comando == "crear-db":
        crear_base_datos(args.parent)
    elif args.comando == "importar":
        print(importar_repos(con_lenguajes=not args.sin_lenguajes))
    elif args.comando == "sincronizar":
        print(sincronizar())
    elif args.comando == "catalogar":
        print(catalogar(
            args.nombre,
            tipo=args.tipo,
            estado=args.estado,
            version_de=getattr(args, "version_de", None),
            proceso=args.proceso,
            etiquetas=args.etiquetas,
            notas=args.notas,
        ))
    elif args.comando == "listar":
        print(listar_repos(estado=args.estado, tipo=args.tipo, proceso=args.proceso))
    elif args.comando == "estado":
        print(estado_repos())
    else:
        parser.print_help()
