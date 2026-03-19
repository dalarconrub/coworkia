"""
Agente BIB (Bibliografía) para Paperpile + Notion.

Cataloga papers de Paperpile en una base de datos de Notion.
Funcionalidades:
  - Crear la base de datos BIB-Bibliografía en Notion
  - Importar papers desde Paperpile (vía BibTeX export)
  - Sincronizar (reimportar con detección de cambios)
  - Catalogar: asignar estado de lectura, relevancia, proyecto
  - Listar papers catalogados con filtros
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
from tools.paperpile_tools import get_library

DB_BIB = os.getenv("NOTION_DB_BIB", "")
BIB_PARENT_PAGE = os.getenv("NOTION_BIB_PARENT_PAGE", "")


# ─── SCHEMA DE LA BASE DE DATOS ──────────────────────────────────────────────

DB_SCHEMA = {
    "Título": {"title": {}},
    "Autores": {"rich_text": {}},
    "Año": {"number": {"format": "number"}},
    "Tipo": {
        "select": {
            "options": [
                {"name": "Artículo", "color": "blue"},
                {"name": "Libro", "color": "brown"},
                {"name": "Capítulo de libro", "color": "orange"},
                {"name": "Conferencia", "color": "purple"},
                {"name": "Tesis doctoral", "color": "red"},
                {"name": "Tesis de máster", "color": "pink"},
                {"name": "Informe técnico", "color": "gray"},
                {"name": "Otro", "color": "default"},
            ]
        }
    },
    "Journal": {"rich_text": {}},
    "DOI": {"url": {}},
    "Abstract": {"rich_text": {}},
    "Keywords": {"multi_select": {"options": []}},
    "Carpeta": {
        "select": {"options": []}
    },
    "Etiquetas": {"multi_select": {"options": []}},
    "Estado": {
        "select": {
            "options": [
                {"name": "Por leer", "color": "red"},
                {"name": "En proceso", "color": "yellow"},
                {"name": "Leído", "color": "green"},
                {"name": "Revisado", "color": "blue"},
                {"name": "Descartado", "color": "gray"},
            ]
        }
    },
    "Relevancia": {
        "select": {
            "options": [
                {"name": "Alta", "color": "red"},
                {"name": "Media", "color": "yellow"},
                {"name": "Baja", "color": "gray"},
            ]
        }
    },
    "Citekey": {"rich_text": {}},
    "URL": {"url": {}},
    "Volumen": {"rich_text": {}},
    "Páginas": {"rich_text": {}},
    "PMID": {"rich_text": {}},
    "Notas": {"rich_text": {}},
}


# ─── SETUP ───────────────────────────────────────────────────────────────────

def crear_base_datos(parent_page_id: str = None) -> dict:
    """Crea la base de datos BIB-Bibliografía en Notion."""
    parent = parent_page_id or BIB_PARENT_PAGE
    if not parent:
        raise ValueError(
            "Falta NOTION_BIB_PARENT_PAGE en .env. "
            "Crea una página en Notion y pon su ID como valor."
        )
    result = create_database(parent, "BIB-Bibliografía", DB_SCHEMA)
    db_id = result["id"]
    print(f"Base de datos creada: {db_id}")
    print(f"Añade a tu .env:\n  NOTION_DB_BIB={db_id}")
    return result


# ─── IMPORTAR ────────────────────────────────────────────────────────────────

def _paper_a_propiedades(paper: dict) -> dict:
    """Convierte un paper normalizado a propiedades Notion."""
    props = {
        "Título": {"title": [{"text": {"content": paper["titulo"][:2000]}}]},
        "Autores": {"rich_text": [{"text": {"content": paper["autores"][:2000]}}]},
        "Tipo": {"select": {"name": paper["tipo"]}},
    }

    if paper["year"]:
        props["Año"] = {"number": paper["year"]}
    if paper["journal"]:
        props["Journal"] = {"rich_text": [{"text": {"content": paper["journal"][:2000]}}]}
    if paper["doi_url"]:
        props["DOI"] = {"url": paper["doi_url"]}
    if paper["abstract"]:
        props["Abstract"] = {"rich_text": [{"text": {"content": paper["abstract"][:2000]}}]}
    if paper["keywords"]:
        props["Keywords"] = {"multi_select": [{"name": k[:100]} for k in paper["keywords"][:25]]}
    if paper["folders"]:
        props["Carpeta"] = {"select": {"name": paper["folders"][0][:100]}}
    if paper["labels"]:
        props["Etiquetas"] = {"multi_select": [{"name": l[:100]} for l in paper["labels"][:25]]}
    if paper["citekey"]:
        props["Citekey"] = {"rich_text": [{"text": {"content": paper["citekey"]}}]}
    if paper["url"]:
        props["URL"] = {"url": paper["url"]}
    if paper["volume"]:
        vol = paper["volume"]
        if paper["number"]:
            vol += f"({paper['number']})"
        props["Volumen"] = {"rich_text": [{"text": {"content": vol}}]}
    if paper["pages"]:
        props["Páginas"] = {"rich_text": [{"text": {"content": paper["pages"]}}]}
    if paper["pmid"]:
        props["PMID"] = {"rich_text": [{"text": {"content": paper["pmid"]}}]}
    if paper["note"]:
        props["Notas"] = {"rich_text": [{"text": {"content": paper["note"][:2000]}}]}

    # Estado por defecto
    props["Estado"] = {"select": {"name": "Por leer"}}

    return props


def importar_papers(db_id: str = None) -> str:
    """Importa papers de Paperpile a Notion."""
    database = db_id or DB_BIB
    if not database:
        return "Error: falta NOTION_DB_BIB en .env. Ejecuta 'crear-db' primero."

    existentes = _papers_existentes(database)

    print("Descargando biblioteca de Paperpile...")
    papers = get_library()
    print(f"Encontrados {len(papers)} papers.")

    creados = 0
    omitidos = 0
    errores = 0

    for paper in papers:
        # Usar citekey como identificador único
        if paper["citekey"] in existentes:
            omitidos += 1
            continue

        props = _paper_a_propiedades(paper)

        try:
            add_page_to_database(database, props)
            creados += 1
            autor_corto = paper["autores"].split(",")[0] if paper["autores"] else "?"
            print(f"  ✓ {autor_corto} ({paper['year'] or '?'}) — {paper['titulo'][:60]}")
        except Exception as e:
            errores += 1
            print(f"  ✗ {paper['citekey']}: {e}")

    return (
        f"\n=== IMPORTACIÓN COMPLETADA ===\n"
        f"  Creados:  {creados}\n"
        f"  Omitidos: {omitidos} (ya existían)\n"
        f"  Errores:  {errores}\n"
        f"  Total Paperpile: {len(papers)}"
    )


def sincronizar(db_id: str = None) -> str:
    """Sincroniza: importa nuevos y actualiza metadata de existentes."""
    database = db_id or DB_BIB
    if not database:
        return "Error: falta NOTION_DB_BIB en .env."

    # Mapear citekey → page_id de Notion
    paginas = query_database(database)
    existentes = {}
    for p in paginas:
        citekey = extract_property_value(p["properties"].get("Citekey", {}))
        if citekey:
            existentes[citekey] = p

    print("Descargando biblioteca de Paperpile...")
    papers = get_library()

    nuevos = 0
    actualizados = 0
    errores = 0

    for paper in papers:
        if paper["citekey"] in existentes:
            # Actualizar campos que pueden cambiar
            pagina = existentes[paper["citekey"]]
            props = {}

            # Actualizar título, autores, journal, abstract (pueden corregirse en Paperpile)
            props["Título"] = {"title": [{"text": {"content": paper["titulo"][:2000]}}]}
            if paper["autores"]:
                props["Autores"] = {"rich_text": [{"text": {"content": paper["autores"][:2000]}}]}
            if paper["keywords"]:
                props["Keywords"] = {"multi_select": [{"name": k[:100]} for k in paper["keywords"][:25]]}
            if paper["doi_url"]:
                props["DOI"] = {"url": paper["doi_url"]}

            try:
                update_page_properties(pagina["id"], props)
                actualizados += 1
            except Exception as e:
                errores += 1
                print(f"  ✗ actualizar {paper['citekey']}: {e}")
        else:
            # Nuevo paper
            props = _paper_a_propiedades(paper)
            try:
                add_page_to_database(database, props)
                nuevos += 1
                autor_corto = paper["autores"].split(",")[0] if paper["autores"] else "?"
                print(f"  + {autor_corto} ({paper['year'] or '?'}) — {paper['titulo'][:60]}")
            except Exception as e:
                errores += 1
                print(f"  ✗ nuevo {paper['citekey']}: {e}")

    return (
        f"\n=== SINCRONIZACIÓN ===\n"
        f"  Nuevos:       {nuevos}\n"
        f"  Actualizados: {actualizados}\n"
        f"  Errores:      {errores}\n"
        f"  Total Paperpile: {len(papers)}\n"
        f"  Total Notion:    {len(paginas)}"
    )


# ─── CATALOGAR ───────────────────────────────────────────────────────────────

def catalogar(titulo_o_citekey: str, estado: str = None, relevancia: str = None,
              etiquetas: list[str] = None, notas: str = None,
              db_id: str = None) -> str:
    """Actualiza campos de catalogación de un paper."""
    database = db_id or DB_BIB
    if not database:
        return "Error: falta NOTION_DB_BIB en .env."

    pagina = _buscar_paper(database, titulo_o_citekey)
    if not pagina:
        return f"No se encontró '{titulo_o_citekey}' en Notion."

    props = {}
    if estado:
        props["Estado"] = {"select": {"name": estado}}
    if relevancia:
        props["Relevancia"] = {"select": {"name": relevancia}}
    if etiquetas:
        props["Etiquetas"] = {"multi_select": [{"name": e} for e in etiquetas]}
    if notas:
        props["Notas"] = {"rich_text": [{"text": {"content": notas[:2000]}}]}

    if not props:
        return "Sin cambios — especifica al menos un campo."

    update_page_properties(pagina["id"], props)
    titulo = extract_property_value(pagina["properties"].get("Título", {}))
    return f"Actualizado: {titulo}"


# ─── LISTAR ──────────────────────────────────────────────────────────────────

def listar_papers(estado: str = None, tipo: str = None, relevancia: str = None,
                  carpeta: str = None, db_id: str = None) -> str:
    """Lista papers catalogados con filtros opcionales."""
    database = db_id or DB_BIB
    if not database:
        return "Error: falta NOTION_DB_BIB en .env."

    filter_obj = _build_filter(estado, tipo, relevancia, carpeta)
    registros = query_database(database, filter_obj=filter_obj)

    if not registros:
        return "No hay papers que coincidan."

    lineas = [f"=== BIB-BIBLIOGRAFÍA ({len(registros)}) ===\n"]
    for r in registros:
        lineas.append(_fmt_paper(r))
    return "\n".join(lineas)


def estado_bib(db_id: str = None) -> str:
    """Resumen del catálogo bibliográfico."""
    database = db_id or DB_BIB
    if not database:
        return "Error: falta NOTION_DB_BIB en .env."

    registros = query_database(database)
    if not registros:
        return "El catálogo está vacío."

    por_estado = {}
    por_tipo = {}
    por_carpeta = {}
    por_relevancia = {}

    for r in registros:
        estado = _prop(r, "Estado") or "Sin estado"
        tipo = _prop(r, "Tipo") or "Sin tipo"
        carpeta = _prop(r, "Carpeta") or ""
        relevancia = _prop(r, "Relevancia") or ""

        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        if carpeta:
            por_carpeta[carpeta] = por_carpeta.get(carpeta, 0) + 1
        if relevancia:
            por_relevancia[relevancia] = por_relevancia.get(relevancia, 0) + 1

    lineas = [
        f"=== ESTADO BIB ({len(registros)} papers) ===\n",
        "Por estado:",
    ]
    for k, v in sorted(por_estado.items(), key=lambda x: -x[1]):
        lineas.append(f"  {k}: {v}")

    lineas.append("\nPor tipo:")
    for k, v in sorted(por_tipo.items(), key=lambda x: -x[1]):
        lineas.append(f"  {k}: {v}")

    if por_carpeta:
        lineas.append("\nPor carpeta:")
        for k, v in sorted(por_carpeta.items(), key=lambda x: -x[1]):
            lineas.append(f"  {k}: {v}")

    if por_relevancia:
        lineas.append("\nPor relevancia:")
        for k, v in sorted(por_relevancia.items(), key=lambda x: -x[1]):
            lineas.append(f"  {k}: {v}")

    return "\n".join(lineas)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _papers_existentes(db_id: str) -> set[str]:
    """Obtiene los citekeys de papers ya catalogados."""
    paginas = query_database(db_id)
    citekeys = set()
    for p in paginas:
        ck = extract_property_value(p["properties"].get("Citekey", {}))
        if ck:
            citekeys.add(ck)
    return citekeys


def _buscar_paper(db_id: str, texto: str) -> dict | None:
    """Busca un paper por citekey o título (parcial)."""
    # Primero buscar por citekey exacto
    filter_obj = {"property": "Citekey", "rich_text": {"equals": texto}}
    resultados = query_database(db_id, filter_obj=filter_obj)
    if resultados:
        return resultados[0]

    # Fallback: buscar por título contiene
    filter_obj = {"property": "Título", "title": {"contains": texto}}
    resultados = query_database(db_id, filter_obj=filter_obj)
    return resultados[0] if resultados else None


def _prop(r: dict, nombre: str) -> str:
    props = r.get("properties", {})
    return extract_property_value(props[nombre]) if nombre in props else ""


def _fmt_paper(r: dict) -> str:
    titulo = _prop(r, "Título")
    autores = _prop(r, "Autores")
    year = _prop(r, "Año")
    tipo = _prop(r, "Tipo")
    estado = _prop(r, "Estado")
    journal = _prop(r, "Journal")
    relevancia = _prop(r, "Relevancia")
    carpeta = _prop(r, "Carpeta")

    # Primer autor abreviado
    primer_autor = autores.split(",")[0] if autores else "?"
    if len(autores.split(",")) > 1:
        primer_autor += " et al."

    linea = f"  • {primer_autor} ({year or '?'}) — {titulo[:70]}"
    detalles = []
    if tipo:        detalles.append(tipo)
    if estado:      detalles.append(estado)
    if relevancia:  detalles.append(f"★{relevancia}")
    if journal:     detalles.append(journal[:30])
    if carpeta:     detalles.append(f"📁{carpeta}")
    if detalles:
        linea += f"\n    {', '.join(detalles)}"
    return linea


def _build_filter(estado: str = None, tipo: str = None,
                  relevancia: str = None, carpeta: str = None) -> dict | None:
    filters = []
    if estado:
        filters.append({"property": "Estado", "select": {"equals": estado}})
    if tipo:
        filters.append({"property": "Tipo", "select": {"equals": tipo}})
    if relevancia:
        filters.append({"property": "Relevancia", "select": {"equals": relevancia}})
    if carpeta:
        filters.append({"property": "Carpeta", "select": {"equals": carpeta}})
    if len(filters) == 1:
        return filters[0]
    if len(filters) > 1:
        return {"and": filters}
    return None


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente BIB - Paperpile → Notion")
    subparsers = parser.add_subparsers(dest="comando")

    # crear-db
    p_db = subparsers.add_parser("crear-db", help="Crear la base de datos en Notion")
    p_db.add_argument("--parent", default=None, help="ID de la página padre en Notion")

    # importar
    subparsers.add_parser("importar", help="Importar papers de Paperpile a Notion")

    # sincronizar
    subparsers.add_parser("sincronizar", help="Sincronizar: nuevos + actualizar existentes")

    # catalogar
    p_cat = subparsers.add_parser("catalogar", help="Catalogar un paper")
    p_cat.add_argument("texto", help="Citekey o parte del título")
    p_cat.add_argument("--estado", default=None, choices=["Por leer", "En proceso", "Leído", "Revisado", "Descartado"])
    p_cat.add_argument("--relevancia", default=None, choices=["Alta", "Media", "Baja"])
    p_cat.add_argument("--etiquetas", nargs="*", default=None)
    p_cat.add_argument("--notas", default=None)

    # listar
    p_list = subparsers.add_parser("listar", help="Listar papers catalogados")
    p_list.add_argument("--estado", default=None)
    p_list.add_argument("--tipo", default=None)
    p_list.add_argument("--relevancia", default=None)
    p_list.add_argument("--carpeta", default=None)

    # estado
    subparsers.add_parser("estado", help="Resumen del catálogo")

    args = parser.parse_args()

    if args.comando == "crear-db":
        crear_base_datos(args.parent)
    elif args.comando == "importar":
        print(importar_papers())
    elif args.comando == "sincronizar":
        print(sincronizar())
    elif args.comando == "catalogar":
        print(catalogar(
            args.texto,
            estado=args.estado,
            relevancia=args.relevancia,
            etiquetas=args.etiquetas,
            notas=args.notas,
        ))
    elif args.comando == "listar":
        print(listar_papers(
            estado=args.estado, tipo=args.tipo,
            relevancia=args.relevancia, carpeta=args.carpeta,
        ))
    elif args.comando == "estado":
        print(estado_bib())
    else:
        parser.print_help()
