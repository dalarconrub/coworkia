"""
Agente Obsidian para el vault ABGD.

Opera sobre el vault Alpha siguiendo la jerarquía:
  Área (A) → Bloque (B) → Contexto (C) → Proyecto (P) → Tarea (T) → Nota (N)

Vault: G:/Mi unidad/ABGD/ABGD-25.09.05/1.ALPHA
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from tools.obsidian_tools import (
    get_areas,
    get_bloques,
    get_contextos,
    get_proyectos,
    get_tareas,
    get_notas,
    get_todas_notas,
    get_mapa_vault,
    read_nota,
    buscar_notas,
    crear_nota,
    crear_nota_en_contexto,
    append_a_nota,
    resolver_path,
    detectar_nivel,
    ALPHA_PATH,
    MAPA_AREAS,
)


# ─── ESTRUCTURA ───────────────────────────────────────────────────────────────

def mapa() -> str:
    """Muestra la estructura completa del vault Alpha."""
    lineas = ["=== VAULT ALPHA — MAPA ABGD ===\n"]
    vault = get_mapa_vault()

    for area_code, bloques in vault.items():
        nombre_area = MAPA_AREAS.get(area_code, area_code)
        lineas.append(f"📁 {area_code}  {nombre_area}")
        for bloque_code, contextos in bloques.items():
            lineas.append(f"  📂 {bloque_code}")
            for ctx_code, proyectos in contextos.items():
                linea_ctx = f"    📄 {ctx_code}"
                if proyectos:
                    linea_ctx += f"  ({len(proyectos)} proyectos)"
                lineas.append(linea_ctx)

    return "\n".join(lineas)


def listar(codigo: str) -> str:
    """
    Lista el contenido de cualquier nivel ABGD por código.
    Ej: listar('A1-INV') → bloques de INV
        listar('B12-LAB') → contextos de LAB
        listar('C125-DAT') → proyectos de DAT
    """
    nivel = detectar_nivel(codigo)
    path = resolver_path(codigo)

    if not path:
        return f"No se encontró '{codigo}' en el vault."

    lineas = [f"=== {codigo} [{nivel.upper()}] ===\n"]

    if nivel == "area":
        items = get_bloques(codigo)
        for it in items:
            lineas.append(f"  📂 {it['codigo']}")

    elif nivel == "bloque":
        # Necesitamos el área padre
        for area in get_areas():
            ctx_list = get_contextos(area["codigo"], codigo)
            if ctx_list:
                for ctx in ctx_list:
                    proyectos = get_proyectos(ctx["path"])
                    linea = f"  📄 {ctx['codigo']}"
                    if proyectos:
                        linea += f"  ({len(proyectos)} proyectos)"
                    lineas.append(linea)
                break

    elif nivel == "contexto":
        proyectos = get_proyectos(path)
        notas = get_notas(path)
        if proyectos:
            lineas.append(f"Proyectos ({len(proyectos)}):")
            for p in proyectos:
                lineas.append(f"  🗂️  {p['codigo']}")
        if notas:
            lineas.append(f"\nNotas directas ({len(notas)}):")
            for n in notas:
                lineas.append(f"  📝 {n['nombre']}  ({n['fecha']})")

    elif nivel == "proyecto":
        tareas = get_tareas(path)
        notas = get_notas(path)
        if tareas:
            lineas.append(f"Tareas ({len(tareas)}):")
            for t in tareas:
                lineas.append(f"  ✅ {t['codigo']}")
        if notas:
            lineas.append(f"\nNotas ({len(notas)}):")
            for n in notas:
                lineas.append(f"  📝 {n['nombre']}  ({n['fecha']})")

    elif nivel == "tarea":
        notas = get_notas(path)
        if notas:
            lineas.append(f"Notas ({len(notas)}):")
            for n in notas:
                lineas.append(f"  📝 {n['nombre']}  ({n['fecha']})")
        else:
            lineas.append("Sin notas.")

    if len(lineas) == 2:
        lineas.append("(vacío)")

    return "\n".join(lineas)


# ─── NOTAS ────────────────────────────────────────────────────────────────────

def ultimas_notas(n: int = 10, area_code: str = None) -> str:
    """Lista las N notas más recientes del vault (o de un área)."""
    parent = str(ALPHA_PATH / area_code) if area_code else None
    notas = get_todas_notas(parent)

    # Ordenar por fecha descendente
    notas.sort(key=lambda x: x["fecha"], reverse=True)

    lineas = [f"=== ÚLTIMAS {n} NOTAS ===\n"]
    for nota in notas[:n]:
        lineas.append(f"  📝 {nota['nombre']}")
        lineas.append(f"      {nota['relativo']}")
        if nota["fecha"]:
            lineas.append(f"      Fecha: {nota['fecha']}")

    if not notas:
        lineas.append("No hay notas.")

    return "\n".join(lineas)


def ver_nota(path_o_nombre: str) -> str:
    """Lee una nota por su path completo o por nombre."""
    from pathlib import Path as P
    if P(path_o_nombre).exists():
        return read_nota(path_o_nombre)
    # Buscar por nombre
    resultados = list((ALPHA_PATH).rglob(f"{path_o_nombre}.md"))
    if resultados:
        return read_nota(str(resultados[0]))
    return f"Nota '{path_o_nombre}' no encontrada."


def buscar(texto: str, area_code: str = None) -> str:
    """Busca texto en el contenido de las notas."""
    resultados = buscar_notas(texto, area_code)
    if not resultados:
        return f"Sin resultados para '{texto}'."

    lineas = [f"=== BÚSQUEDA: '{texto}' ({len(resultados)} resultados) ===\n"]
    for r in resultados:
        lineas.append(f"  📝 {r['nombre']}")
        lineas.append(f"      {r['relativo']}")

    return "\n".join(lineas)


# ─── CREACIÓN ─────────────────────────────────────────────────────────────────

def nueva_nota(area: str, bloque: str, contexto: str, nombre: str,
               contenido: str = "", fecha: str = None,
               proyecto: str = None, tarea: str = None) -> str:
    """
    Crea una nota nueva en el vault.
    Si se especifica proyecto y/o tarea, crea la nota en ese subnivel.
    """
    from pathlib import Path as P
    parent = ALPHA_PATH / area / bloque / contexto
    if proyecto:
        parent = parent / proyecto
    if tarea:
        parent = parent / tarea

    ruta = crear_nota(str(parent), nombre, contenido, fecha)
    return f"Nota creada: {ruta}"


# ─── ESTADO ───────────────────────────────────────────────────────────────────

def estado_vault() -> str:
    """Resumen estadístico del vault Alpha."""
    areas = get_areas()
    todas = get_todas_notas()

    lineas = ["=== ESTADO VAULT ALPHA ===\n"]
    lineas.append(f"  Áreas    : {len(areas)}")

    total_bloques = sum(len(get_bloques(a["codigo"])) for a in areas)
    lineas.append(f"  Bloques  : {total_bloques}")
    lineas.append(f"  Notas    : {len(todas)}")

    # Notas por área
    lineas.append("\nNotas por área:")
    for area in areas:
        notas_area = get_todas_notas(str(ALPHA_PATH / area["codigo"]))
        nombre = MAPA_AREAS.get(area["codigo"], area["codigo"])
        lineas.append(f"  {area['codigo']}  {nombre:20}  {len(notas_area):3} notas")

    # Nota más reciente
    if todas:
        mas_reciente = max(todas, key=lambda x: x["fecha"] or "")
        lineas.append(f"\nÚltima nota: {mas_reciente['nombre']}  ({mas_reciente['fecha']})")

    return "\n".join(lineas)


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agente Obsidian ABGD")
    subparsers = parser.add_subparsers(dest="comando")

    subparsers.add_parser("mapa",   help="Estructura completa del vault")
    subparsers.add_parser("estado", help="Resumen estadístico del vault")

    p_list = subparsers.add_parser("listar", help="Listar contenido de un nivel")
    p_list.add_argument("codigo", help="Código ABGD (ej: A1-INV, B12-LAB, C125-DAT)")

    p_ult = subparsers.add_parser("ultimas", help="Últimas notas")
    p_ult.add_argument("--n", type=int, default=10)
    p_ult.add_argument("--area", default=None)

    p_ver = subparsers.add_parser("ver", help="Ver una nota")
    p_ver.add_argument("nombre")

    p_bus = subparsers.add_parser("buscar", help="Buscar en notas")
    p_bus.add_argument("texto")
    p_bus.add_argument("--area", default=None)

    p_nueva = subparsers.add_parser("nueva-nota", help="Crear nota")
    p_nueva.add_argument("area",     help="ej: A1-INV")
    p_nueva.add_argument("bloque",   help="ej: B12-LAB")
    p_nueva.add_argument("contexto", help="ej: C125-DAT")
    p_nueva.add_argument("nombre",   help="Descripción de la nota")
    p_nueva.add_argument("--contenido", default="")
    p_nueva.add_argument("--fecha",     default=None, help="YYYY-MM-DD")
    p_nueva.add_argument("--proyecto",  default=None)
    p_nueva.add_argument("--tarea",     default=None)

    p_prom = subparsers.add_parser("promote-ptn", help="Promover nota Obsidian a PTN-Notas")
    p_prom.add_argument("nombre", help="Nombre de la nota en vault (con o sin .md)")
    p_prom.add_argument("--proyecto", default=None, help="ID o nombre del proyecto PTN")

    args = parser.parse_args()

    if args.comando == "mapa":
        print(mapa())
    elif args.comando == "estado":
        print(estado_vault())
    elif args.comando == "listar":
        print(listar(args.codigo))
    elif args.comando == "ultimas":
        print(ultimas_notas(n=args.n, area_code=args.area))
    elif args.comando == "ver":
        print(ver_nota(args.nombre))
    elif args.comando == "buscar":
        print(buscar(args.texto, area_code=args.area))
    elif args.comando == "nueva-nota":
        print(nueva_nota(args.area, args.bloque, args.contexto, args.nombre,
                         contenido=args.contenido, fecha=args.fecha,
                         proyecto=args.proyecto, tarea=args.tarea))
    elif args.comando == "promote-ptn":
        from tools.promote_obsidian_to_ptn import promote
        res = promote(args.nombre, args.proyecto)
        print(f"{res['action']}: {res['titulo']} (fecha={res['fecha']}) id={res['id']}")
    else:
        parser.print_help()
