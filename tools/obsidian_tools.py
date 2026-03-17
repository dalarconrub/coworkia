"""
Herramientas para leer y escribir en el vault Obsidian ABGD.

Jerarquía real del vault:
  Área (A) → Bloque (B) → Contexto (C) → Proyecto (P) → Tarea (T) → Nota (N)

Nomenclatura:
  - Áreas:    A0-GTD, A1-INV, A2-UNI, A3-VIT, A4-REF
  - Bloques:  B0A-INX, B11-CVT, B12-LAB...
  - Contextos: C0C9-Notas, C111-REP, C125-DAT...
  - Proyectos: P125.01-NOMBRE, P126.01-NOMBRE...
  - Tareas:   T12601.03-NOMBRE...
  - Notas:    N[YYMMDD]-NOMBRE.md
"""

import os
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ALPHA_PATH = Path(os.getenv("OBSIDIAN_ALPHA_PATH", "G:/Mi unidad/ABGD/ABGD-25.09.05/1.ALPHA"))
ABGD_ROOT  = Path(os.getenv("OBSIDIAN_ABGD_ROOT",  "G:/Mi unidad/ABGD/ABGD-25.09.05"))

# Prefijos de nivel
NIVEL_PREFIJOS = {
    "area":     re.compile(r"^A\d"),
    "bloque":   re.compile(r"^B\w"),
    "contexto": re.compile(r"^C\w"),
    "proyecto": re.compile(r"^P\d"),
    "tarea":    re.compile(r"^T\d"),
    "nota":     re.compile(r"^N\d"),
}

MAPA_AREAS = {
    "A0-GTD": "Getting Things Done",
    "A1-INV": "Investigación",
    "A2-UNI": "Universidad",
    "A3-VIT": "Vital",
    "A4-REF": "Referencia",
}


# ─── NAVEGACIÓN ───────────────────────────────────────────────────────────────

def get_areas() -> list[dict]:
    """Lista las Áreas del vault Alpha."""
    areas = []
    for d in sorted(ALPHA_PATH.iterdir()):
        if d.is_dir() and NIVEL_PREFIJOS["area"].match(d.name):
            areas.append({
                "codigo": d.name,
                "nombre": MAPA_AREAS.get(d.name, d.name),
                "path": str(d),
            })
    return areas


def get_bloques(area_code: str) -> list[dict]:
    """Lista los Bloques de un Área."""
    area_path = ALPHA_PATH / area_code
    if not area_path.exists():
        return []
    bloques = []
    for d in sorted(area_path.iterdir()):
        if d.is_dir() and NIVEL_PREFIJOS["bloque"].match(d.name):
            bloques.append({"codigo": d.name, "path": str(d)})
    return bloques


def get_contextos(area_code: str, bloque_code: str) -> list[dict]:
    """Lista los Contextos de un Bloque."""
    bloque_path = ALPHA_PATH / area_code / bloque_code
    if not bloque_path.exists():
        return []
    contextos = []
    for d in sorted(bloque_path.iterdir()):
        if d.is_dir() and NIVEL_PREFIJOS["contexto"].match(d.name):
            contextos.append({"codigo": d.name, "path": str(d)})
    return contextos


def get_proyectos(contexto_path: str) -> list[dict]:
    """Lista los Proyectos dentro de un Contexto."""
    path = Path(contexto_path)
    if not path.exists():
        return []
    proyectos = []
    for d in sorted(path.iterdir()):
        if d.is_dir() and NIVEL_PREFIJOS["proyecto"].match(d.name):
            proyectos.append({"codigo": d.name, "path": str(d)})
    return proyectos


def get_tareas(proyecto_path: str) -> list[dict]:
    """Lista las Tareas dentro de un Proyecto."""
    path = Path(proyecto_path)
    if not path.exists():
        return []
    tareas = []
    for d in sorted(path.iterdir()):
        if d.is_dir() and NIVEL_PREFIJOS["tarea"].match(d.name):
            tareas.append({"codigo": d.name, "path": str(d)})
    return tareas


def get_notas(parent_path: str) -> list[dict]:
    """Lista las Notas (.md) en cualquier nivel del vault."""
    path = Path(parent_path)
    if not path.exists():
        return []
    notas = []
    for f in sorted(path.iterdir()):
        if f.is_file() and f.suffix == ".md" and NIVEL_PREFIJOS["nota"].match(f.stem):
            fecha = _parse_fecha_nota(f.stem)
            notas.append({
                "nombre": f.stem,
                "path": str(f),
                "fecha": fecha,
            })
    return notas


def get_todas_notas(parent_path: str = None) -> list[dict]:
    """Lista recursivamente todas las notas .md bajo un path."""
    root = Path(parent_path) if parent_path else ALPHA_PATH
    notas = []
    for f in sorted(root.rglob("*.md")):
        if NIVEL_PREFIJOS["nota"].match(f.stem):
            rel = f.relative_to(ALPHA_PATH)
            notas.append({
                "nombre": f.stem,
                "path": str(f),
                "relativo": str(rel),
                "fecha": _parse_fecha_nota(f.stem),
            })
    return notas


# ─── LECTURA ──────────────────────────────────────────────────────────────────

def read_nota(path: str) -> str:
    """Lee el contenido de una nota."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Nota no encontrada: {path}")
    return p.read_text(encoding="utf-8")


def read_nota_by_name(nombre: str, area_code: str = None) -> str:
    """Busca y lee una nota por nombre (sin extensión) en todo el vault o en un área."""
    root = ALPHA_PATH / area_code if area_code else ALPHA_PATH
    for f in root.rglob(f"{nombre}.md"):
        return f.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Nota '{nombre}' no encontrada")


def get_frontmatter(path: str) -> dict:
    """Extrae el frontmatter YAML de una nota."""
    content = read_nota(path)
    fm = {}
    if content.startswith("---"):
        end = content.find("---", 3)
        if end > 0:
            yaml_block = content[3:end].strip()
            for line in yaml_block.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    fm[key.strip()] = val.strip()
    return fm


# ─── BÚSQUEDA ─────────────────────────────────────────────────────────────────

def buscar_notas(texto: str, area_code: str = None) -> list[dict]:
    """Busca texto en el contenido de las notas del vault."""
    root = ALPHA_PATH / area_code if area_code else ALPHA_PATH
    resultados = []
    for f in root.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if texto.lower() in content.lower():
                rel = f.relative_to(ALPHA_PATH)
                resultados.append({
                    "nombre": f.stem,
                    "path": str(f),
                    "relativo": str(rel),
                })
        except Exception:
            continue
    return resultados


# ─── ESCRITURA ────────────────────────────────────────────────────────────────

def crear_nota(parent_path: str, nombre: str, contenido: str = "",
               fecha: str = None, frontmatter: dict = None) -> str:
    """
    Crea una nota nueva en el path especificado.
    nombre: descripción (sin prefijo de fecha, sin .md)
    fecha: YYYY-MM-DD (por defecto hoy)
    Retorna la ruta del archivo creado.
    """
    if not fecha:
        fecha = datetime.now().strftime("%Y-%m-%d")

    # Formato código fecha: YYMMDD
    fecha_code = fecha.replace("-", "")[2:]  # YYMMDD
    nombre_archivo = f"N{fecha_code}-{nombre}.md"

    path = Path(parent_path) / nombre_archivo
    path.parent.mkdir(parents=True, exist_ok=True)

    # Construir contenido
    partes = []
    if frontmatter:
        partes.append("---")
        for k, v in frontmatter.items():
            partes.append(f"{k}: {v}")
        partes.append("---")
        partes.append("")

    partes.append(f"# {nombre}")
    partes.append(f"**Fecha:** {fecha}")
    partes.append("")
    if contenido:
        partes.append(contenido)

    path.write_text("\n".join(partes), encoding="utf-8")
    return str(path)


def crear_nota_en_contexto(area: str, bloque: str, contexto: str,
                            nombre: str, contenido: str = "",
                            fecha: str = None, frontmatter: dict = None) -> str:
    """Crea una nota directamente en un Contexto (el nivel más común)."""
    parent = ALPHA_PATH / area / bloque / contexto
    return crear_nota(str(parent), nombre, contenido, fecha, frontmatter)


def append_a_nota(path: str, texto: str) -> None:
    """Añade texto al final de una nota existente."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Nota no encontrada: {path}")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"\n{texto}\n")


# ─── MAPA DEL VAULT ───────────────────────────────────────────────────────────

def get_mapa_vault() -> dict:
    """
    Genera un mapa completo del vault Alpha:
    { area: { bloque: { contexto: [proyectos...] } } }
    """
    mapa = {}
    for area in get_areas():
        mapa[area["codigo"]] = {}
        for bloque in get_bloques(area["codigo"]):
            mapa[area["codigo"]][bloque["codigo"]] = {}
            for ctx in get_contextos(area["codigo"], bloque["codigo"]):
                proyectos = get_proyectos(ctx["path"])
                mapa[area["codigo"]][bloque["codigo"]][ctx["codigo"]] = (
                    [p["codigo"] for p in proyectos]
                )
    return mapa


# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def _parse_fecha_nota(stem: str) -> str:
    """Extrae la fecha de un nombre de nota tipo N250922-Nombre."""
    m = re.match(r"^N(\d{6})", stem)
    if m:
        d = m.group(1)
        return f"20{d[:2]}-{d[2:4]}-{d[4:6]}"
    return ""


def resolver_path(codigo: str) -> str | None:
    """
    Resuelve el path de cualquier código ABGD.
    Ej: 'A1-INV' → path del área
        'B12-LAB' → busca el bloque en todas las áreas
        'C125-DAT' → busca el contexto
    """
    nivel = detectar_nivel(codigo)
    if nivel == "area":
        p = ALPHA_PATH / codigo
        return str(p) if p.exists() else None
    elif nivel == "bloque":
        for area in get_areas():
            p = ALPHA_PATH / area["codigo"] / codigo
            if p.exists():
                return str(p)
    elif nivel == "contexto":
        for f in ALPHA_PATH.rglob(codigo):
            if f.is_dir():
                return str(f)
    return None


def detectar_nivel(codigo: str) -> str:
    """Detecta el nivel ABGD de un código."""
    for nivel, patron in NIVEL_PREFIJOS.items():
        if patron.match(codigo):
            return nivel
    return "desconocido"
