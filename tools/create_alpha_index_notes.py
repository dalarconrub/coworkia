"""
Crea estructura minima e indices dentro de las carpetas estructurales ABGD-E.

No sobrescribe notas existentes salvo que se use --refresh-existing. Cada
carpeta estructural recibe una nota con su mismo nombre, frontmatter Obsidian y
una explicacion breve de que es y como se usa.
"""

from __future__ import annotations

import os
import sys
import argparse
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.env_utils import load_project_env

ROOT = Path(__file__).resolve().parent.parent
load_project_env(ROOT / ".env")


AREAS = {
    "A0-GTD": ("Getting Things Done", "Sistema operativo personal: captura, planificacion, trazabilidad y control diario."),
    "A1-INV": ("Investigacion", "Investigacion academica y tecnica: lineas, laboratorios, datos, direccion, publicaciones y revision."),
    "A2-UNI": ("Universidad", "Actividad universitaria: docencia, formacion, gestion institucional y materiales asociados."),
    "A3-VIT": ("Vital", "Vida personal, organizacion, tecnologia personal, bienestar y desarrollo."),
    "A4-ARX": ("Archivo", "Archivo, biblioteca, medios, aplicaciones, codigo y recursos de referencia catalogables."),
}

BLOCKS = {
    "B0A-INX": ("Integracion y trazabilidad", "Agrupa notas sobre enlaces entre sistemas, sincronizacion y resolucion cross-system."),
    "B0B-ABC": ("Taxonomia ABC", "Define y mantiene la taxonomia Area-Bloque-Contexto."),
    "B0C-PLA": ("Planificacion", "Direccion operativa, proyectos, tareas y notas formales."),
    "B11-CVT": ("Convocatorias y trayectoria", "CV, convocatorias, solicitudes, evaluacion y carrera investigadora."),
    "B12-LAB": ("Laboratorio y datos", "Proyectos de investigacion, datos, analisis y direccion de trabajos."),
    "B13-PUB": ("Publicaciones", "Articulos, comunicaciones, manuscritos, revisiones y produccion cientifica."),
    "B24-DOC": ("Docencia", "Grado, master, posgrado, asignaturas y materiales docentes."),
    "B25-FOR": ("Formacion", "Formacion propia, estudiantes, PDI, cursos y mejora docente."),
    "B26-GES": ("Gestion universitaria", "Gestion UPO/UNED, ministerio, evaluacion y administracion universitaria."),
    "B37-ORG": ("Organizacion vital", "Administracion personal, vida domestica, relaciones y organizacion social."),
    "B38-TEC": ("Tecnologia personal", "Infraestructura, software, estadistica, IA aplicada y herramientas personales."),
    "B39-DES": ("Desarrollo personal", "Cuerpo, mente, musica, habitos y crecimiento personal."),
    "B4X-LIB": ("Biblioteca", "Libros, ficcion, ciencia, ensayo y materiales textuales estables."),
    "B4Y-MED": ("Medios", "Video, audio, web, multimedia y recursos mediaticos."),
    "B4Z-APP": ("Aplicaciones y codigo", "Apps, codigo, agentes, software y repositorios de referencia."),
}

CONTEXTS = {
    "C0A1-TODOIST": ("Todoist / MAR", "Notas sobre la capa ejecutiva, tareas, habitos, eventos, ideas y logros."),
    "C0A2-NOTION": ("Notion / PTN", "Notas sobre proyectos, tareas, notas formales y estructuras Notion."),
    "C0A3-OBSIDIAN": ("Obsidian / ABGD-E", "Notas sobre el vault, capas ALPHA-EPSILON, rutas, notas y organizacion documental."),
    "C0B0-ABC": ("ABC", "Notas de definicion, ajustes y criterios de la taxonomia ABC."),
    "C0C7-PROYECTOS": ("Proyectos", "Notas de direccion, mapas y decisiones sobre proyectos formales."),
    "C0C8-TAREAS": ("Tareas", "Notas de coordinacion de tareas, criterios de ejecucion y seguimiento."),
    "C0C9-NOTAS": ("Notas", "Notas operativas generales, diarios y memoria de planificacion."),
    "C111-REP": ("Reputacion y trayectoria", "Evidencias, CV, meritos y trayectoria academica."),
    "C112-SOL": ("Solicitudes", "Convocatorias, solicitudes, grants y procedimientos competitivos."),
    "C113-CAT": ("Catalogacion academica", "Acreditaciones, evaluacion, categorias y clasificacion academica."),
    "C124-PRO": ("Proyectos de investigacion", "Diseno y seguimiento conceptual de proyectos de investigacion."),
    "C125-DAT": ("Datos y analisis", "Decisiones metodologicas, datasets, analisis y resultados interpretados."),
    "C126-DIR": ("Direccion", "Direccion de tesis, TFM, TFG y supervision investigadora."),
    "C137-ART": ("Articulos", "Mapas, decisiones y fichas de articulos cientificos."),
    "C138-COM": ("Comunicaciones", "Congresos, charlas, comunicaciones y presentaciones academicas."),
    "C139-REV": ("Revision", "Revision bibliografica, peer review y sintesis critica."),
    "C241-GRA": ("Grado", "Docencia y materiales de grado."),
    "C242-MAS": ("Master", "Docencia y materiales de master."),
    "C243-POS": ("Posgrado", "Doctorado, posgrado y formacion avanzada."),
    "C254-EST": ("Estudiantes", "Seguimiento, recursos y decisiones relacionadas con estudiantes."),
    "C255-PDI": ("PDI", "Formacion y actividad relacionada con personal docente e investigador."),
    "C256-MOC": ("Cursos y MOOCs", "Cursos, itinerarios de formacion y recursos formativos."),
    "C267-UPO": ("UPO", "Gestion, docencia y actividad institucional UPO."),
    "C268-UNED": ("UNED", "Gestion, docencia y actividad institucional UNED."),
    "C269-MIN": ("Ministerio / evaluacion", "Normativa, ministerio, evaluacion y procesos institucionales."),
    "C371-ADM": ("Administracion personal", "Tramites, documentos personales y organizacion administrativa."),
    "C372-PER": ("Personal", "Vida personal, organizacion domestica y asuntos privados."),
    "C373-SOC": ("Social", "Relaciones, comunidad y coordinacion social."),
    "C384-INF": ("Infraestructura", "Equipos, sistemas, red, almacenamiento y configuracion tecnica."),
    "C385-STA": ("Estadistica", "Metodos estadisticos, modelos, analisis y notas tecnicas."),
    "C386-IAA": ("IA aplicada y agentes", "IA, agentes, automatizacion y workflows asistidos."),
    "C397-FIS": ("Fisico", "Salud, entrenamiento, cuerpo y habitos fisicos."),
    "C398-MEN": ("Mental", "Cognicion, bienestar mental, reflexion y habitos psicologicos."),
    "C399-MUS": ("Musica", "Practica musical, recursos, repertorio y aprendizaje."),
    "C4X0-LIB": ("Libros", "Libros y biblioteca textual general."),
    "C4X1-FIC": ("Ficcion", "Ficcion, narrativa y literatura no tecnica."),
    "C4X2-SCI": ("Ciencia", "Divulgacion, ciencia y recursos cientificos estables."),
    "C4X3-ENS": ("Ensayo", "Ensayo, pensamiento y textos largos de referencia."),
    "C4Y0-MED": ("Medios", "Recursos multimedia generales."),
    "C4Y4-VID": ("Video", "Videos, cursos audiovisuales, conferencias y tutoriales."),
    "C4Y5-AUD": ("Audio", "Audio, podcasts, grabaciones y recursos sonoros."),
    "C4Y6-WEB": ("Web", "Recursos web, paginas, documentacion online y capturas."),
    "C4Z0-APP": ("Aplicaciones", "Aplicaciones, herramientas y servicios."),
    "C4Z7-COD": ("Codigo", "Codigo, snippets, librerias y recursos de programacion."),
    "C4Z8-AGI": ("Agentes IA", "Agentes IA, prompts, sistemas multiagente y automatizaciones."),
    "C4Z9-SOF": ("Software", "Software, instalaciones, configuracion y documentacion tecnica."),
}

AREA_BLOCKS = {
    "A0-GTD": ["B0A-INX", "B0B-ABC", "B0C-PLA"],
    "A1-INV": ["B11-CVT", "B12-LAB", "B13-PUB"],
    "A2-UNI": ["B24-DOC", "B25-FOR", "B26-GES"],
    "A3-VIT": ["B37-ORG", "B38-TEC", "B39-DES"],
    "A4-ARX": ["B4X-LIB", "B4Y-MED", "B4Z-APP"],
}

EPSILON_TYPES = {
    "PDF": "Documentos PDF estables: articulos, libros digitalizados, informes y manuales.",
    "EPUB": "Libros y documentos en formato EPUB.",
    "VIDEO": "Videos, clases grabadas, conferencias, tutoriales y material audiovisual.",
    "AUDIO": "Audio general: podcasts, grabaciones, entrevistas y recursos sonoros.",
    "MUSICA": "Musica, repertorios, pistas, partituras digitalizadas y recursos musicales.",
    "IMAGENES": "Imagenes, figuras, capturas y recursos visuales estables.",
    "PRESENTACIONES": "Presentaciones, diapositivas y materiales de exposicion.",
    "DOCS": "Documentos editables o textuales que no son notas vivas de ALPHA.",
    "HOJAS-CALCULO": "Hojas de calculo, tablas exportadas y ficheros tabulares de biblioteca.",
    "ZIP": "Paquetes comprimidos conservados como objetos estables.",
    "OTROS": "Formatos no cubiertos por las categorias anteriores.",
}

LAYERS = {
    "ABGDE-2026-05-15": ("Vault ABGD-E", "Raiz operativa del vault local. Contiene la configuracion de Obsidian y las cinco capas ALPHA, BETA, GAMMA, DELTA y EPSILON."),
    "1.ALPHA": ("ALPHA", "Capa cognitiva de Obsidian: notas Markdown vivas con jerarquia ABC/ABPC."),
    "2.BETA": ("BETA", "Historico operativo de proyectos finalizados o en hibernacion, organizado por Area y Bloque."),
    "3.GAMMA": ("GAMMA", "Proyectos activos y sus carpetas materiales, organizados por Area."),
    "4.DELTA": ("DELTA", "Referencias y documentos no-proyecto organizados por fecha de incorporacion: AÑO/YYYY-MM-DD."),
    "5.EPSILON": ("EPSILON", "Biblioteca estable organizada primero por tipo de fichero: PDF, EPUB, VIDEO, AUDIO, MUSICA y otros."),
}


@dataclass
class IndexStats:
    dirs_created: list[Path] = field(default_factory=list)
    notes_written: list[Path] = field(default_factory=list)
    notes_skipped: list[Path] = field(default_factory=list)


def _ensure_minimal_structure(vault: Path, dry_run: bool = False) -> list[Path]:
    """Crea la estructura operativa minima de BETA, GAMMA, DELTA y EPSILON."""
    created: list[Path] = []

    beta = vault / "2.BETA"
    for area, blocks in AREA_BLOCKS.items():
        area_dir = beta / area
        if not area_dir.exists():
            if not dry_run:
                area_dir.mkdir(parents=True, exist_ok=True)
            created.append(area_dir)
        for block in blocks:
            block_dir = area_dir / block
            if not block_dir.exists():
                if not dry_run:
                    block_dir.mkdir(parents=True, exist_ok=True)
                created.append(block_dir)

    gamma = vault / "3.GAMMA"
    for area in AREA_BLOCKS:
        area_dir = gamma / area
        if not area_dir.exists():
            if not dry_run:
                area_dir.mkdir(parents=True, exist_ok=True)
            created.append(area_dir)

    today = date.today().isoformat()
    year_dir = vault / "4.DELTA" / today[:4]
    day_dir = year_dir / today
    for folder in [year_dir, day_dir]:
        if not folder.exists():
            if not dry_run:
                folder.mkdir(parents=True, exist_ok=True)
            created.append(folder)

    epsilon = vault / "5.EPSILON"
    for file_type in EPSILON_TYPES:
        type_dir = epsilon / file_type
        inbox_dir = type_dir / "SIN-CLASIFICAR"
        for folder in [type_dir, inbox_dir]:
            if not folder.exists():
                if not dry_run:
                    folder.mkdir(parents=True, exist_ok=True)
                created.append(folder)

    return created


def _layer(path: Path, vault: Path) -> str:
    if path == vault:
        return "vault"
    try:
        return path.relative_to(vault).parts[0]
    except ValueError:
        return ""


def _level(path: Path, alpha: Path) -> str:
    vault = alpha.parent
    if path == vault:
        return "vault"
    if path.parent == vault:
        return "capa"
    if path == alpha:
        return "alpha"

    layer = _layer(path, vault)
    parts = path.relative_to(vault).parts
    name = path.name
    if layer == "1.ALPHA" and name.startswith("A"):
        return "area"
    if layer == "1.ALPHA" and name.startswith("B"):
        return "bloque"
    if layer == "1.ALPHA" and name.startswith("C"):
        return "contexto"
    if layer == "2.BETA" and len(parts) == 2:
        return "beta-area"
    if layer == "2.BETA" and len(parts) == 3:
        return "beta-bloque"
    if layer == "3.GAMMA" and len(parts) == 2:
        return "gamma-area"
    if layer == "4.DELTA" and len(parts) == 2:
        return "delta-year"
    if layer == "4.DELTA" and len(parts) == 3:
        return "delta-date"
    if layer == "5.EPSILON" and len(parts) == 2:
        return "epsilon-tipo"
    if layer == "5.EPSILON" and len(parts) == 3 and name == "SIN-CLASIFICAR":
        return "epsilon-inbox"
    return "carpeta"


def _metadata(path: Path, alpha: Path) -> tuple[str, str, str]:
    level = _level(path, alpha)
    name = path.name
    if level in {"vault", "capa"}:
        title, desc = LAYERS.get(name, (name, "Capa estructural ABGD-E."))
        return (title, "Capa", desc)
    if level == "alpha":
        return ("ALPHA", "Capa de notas vivas de Obsidian", "Contiene la jerarquia ABC canonica. Aqui viven notas Markdown, mapas, decisiones, diarios, fichas y notas puente.")
    if level == "area":
        title, desc = AREAS.get(name, (name, "Area ABC canonica."))
        return (title, "Area", desc)
    if level == "bloque":
        title, desc = BLOCKS.get(name, (name, "Bloque dentro de un area ABC."))
        return (title, "Bloque", desc)
    if level == "contexto":
        title, desc = CONTEXTS.get(name, (name, "Contexto dentro de un bloque ABC."))
        return (title, "Contexto", desc)
    if level == "beta-area":
        title, desc = AREAS.get(name, (name, "Area de historico de proyectos."))
        return (title, "Area BETA", f"Historico de proyectos de {title}. {desc}")
    if level == "beta-bloque":
        title, desc = BLOCKS.get(name, (name, "Bloque de historico de proyectos."))
        return (title, "Bloque BETA", f"Proyectos cerrados o hibernados asociados a este bloque. {desc}")
    if level == "gamma-area":
        title, desc = AREAS.get(name, (name, "Area de proyectos activos."))
        return (title, "Area GAMMA", f"Proyectos activos de {title}. {desc}")
    if level == "delta-year":
        return (name, "Ano DELTA", "Contenedor anual de referencias no-proyecto incorporadas por fecha.")
    if level == "delta-date":
        return (name, "Fecha DELTA", "Bandeja diaria de referencias, documentos o carpetas utiles que aun no son proyecto.")
    if level == "epsilon-tipo":
        return (name, "Tipo EPSILON", EPSILON_TYPES.get(name, "Tipo de fichero dentro de la biblioteca estable."))
    if level == "epsilon-inbox":
        parent = path.parent.name
        return ("Sin clasificar", "Bandeja EPSILON", f"Bandeja provisional para ficheros {parent} pendientes de coleccion o categoria.")
    return (name, "Carpeta", "Carpeta auxiliar.")


def _organization(level: str) -> str:
    if level == "vault":
        return "La raiz del vault contiene `.obsidian/` y las capas `1.ALPHA`, `2.BETA`, `3.GAMMA`, `4.DELTA` y `5.EPSILON`."
    if level == "capa":
        return "Esta capa se organiza segun su funcion propia. `1.ALPHA` usa ABC/ABPC; `2.BETA` usa AB; `3.GAMMA` usa A; `4.DELTA` usa fecha; `5.EPSILON` usa tipo de fichero."
    if level == "alpha":
        return "ALPHA se organiza como Area -> Bloque -> Contexto -> Proyecto -> Tarea -> Nota. Coworkia indexa esta capa mediante `OBSIDIAN_ALPHA_PATH`."
    if level == "area":
        return "Esta area se organiza en bloques `B*` y estos en contextos `C*`. Usa esta nota como mapa de entrada al area."
    if level == "bloque":
        return "Este bloque se organiza en contextos `C*`. Las notas vivas deberian colocarse dentro del contexto mas especifico."
    if level == "contexto":
        return "Dentro de este contexto pueden vivir notas `NYYMMDD-*`, proyectos `P*`, tareas `T*` y notas puente relacionadas con su tema."
    if level == "beta-area":
        return "Esta area de BETA se organiza en bloques `B*`. Dentro de cada bloque viven proyectos cerrados o hibernados."
    if level == "beta-bloque":
        return "Este bloque de BETA contiene carpetas de proyecto historicas. La carpeta de cada proyecto conserva su material recuperable."
    if level == "gamma-area":
        return "Esta area de GAMMA contiene carpetas de proyecto activo. No necesita nivel B ni C salvo que un proyecto lo decida internamente."
    if level == "delta-year":
        return "Este ano de DELTA se organiza en carpetas diarias `YYYY-MM-DD/`, segun fecha de entrada del material."
    if level == "delta-date":
        return "Esta fecha de DELTA contiene referencias no-proyecto incorporadas ese dia. Si alguna madura a proyecto, se mueve o se enlaza desde GAMMA/BETA."
    if level == "epsilon-tipo":
        return "Este tipo de EPSILON se organiza progresivamente por colecciones. `SIN-CLASIFICAR/` recoge material pendiente de ordenar."
    if level == "epsilon-inbox":
        return "Bandeja minima de entrada para este tipo de fichero. Cuando haya patron estable, crea colecciones hermanas y mueve alli los ficheros."
    return "Se organiza segun la convencion local de la carpeta."


def _child_lines(path: Path) -> str:
    children = [p for p in sorted(path.iterdir()) if p.is_dir() and not p.name.startswith(".")]
    if not children:
        return "- No tiene subcarpetas canonicas por ahora."
    return "\n".join(f"- `{child.name}/`" for child in children)


def _note_text(path: Path, alpha: Path) -> str:
    title, role, desc = _metadata(path, alpha)
    level = _level(path, alpha)
    layer = _layer(path, alpha.parent)
    rel = path.relative_to(alpha.parent).as_posix()
    aliases = [path.name] if title == path.name else [path.name, title]
    alias_yaml = "\n".join(f'  - "{alias}"' for alias in aliases)
    layer_tag = {
        "1.ALPHA": "alpha",
        "2.BETA": "beta",
        "3.GAMMA": "gamma",
        "4.DELTA": "delta",
        "5.EPSILON": "epsilon",
    }.get(layer, "vault")
    tags = "\n".join(f"  - {tag}" for tag in ["abgde", layer_tag, level])
    if level in {"alpha", "area", "bloque", "contexto"}:
        rule = """- Guarda aqui solo notas Markdown e indices vivos de Obsidian.
- Si el material es pesado o ejecutable, enlazalo desde una nota y guardalo en `2.BETA`, `3.GAMMA`, `4.DELTA` o `5.EPSILON` segun corresponda.
- Manten los nombres de carpetas canonicos para que Coworkia pueda derivar Area, Bloque y Contexto desde la ruta."""
    elif path.name == "2.BETA" or level in {"beta-area", "beta-bloque"}:
        rule = """- Guarda aqui carpetas de proyectos cerrados, finalizados o en hibernacion.
- Organiza por Area y Bloque; no hace falta bajar a Contexto salvo que el proyecto lo requiera.
- Mantén una nota puente en `1.ALPHA` si el proyecto puede reactivarse."""
    elif path.name == "3.GAMMA" or level == "gamma-area":
        rule = """- Guarda aqui carpetas materiales de proyectos activos: codigo, datos, escritura, referencias locales y outputs.
- Organiza por Area y por carpeta de proyecto.
- Cada proyecto activo deberia tener como minimo `README.md`, `AGENTS.md` o una nota puente en `1.ALPHA`."""
    elif path.name == "4.DELTA" or level in {"delta-year", "delta-date"}:
        rule = """- Guarda aqui referencias no-proyecto por fecha de incorporacion.
- La estructura base es `AÑO/YYYY-MM-DD/`.
- La interpretacion o sintesis de estos materiales debe vivir en `1.ALPHA`."""
    elif path.name == "5.EPSILON" or level in {"epsilon-tipo", "epsilon-inbox"}:
        rule = """- Guarda aqui biblioteca estable por tipo de fichero.
- La raiz se organiza por formato (`PDF`, `EPUB`, `VIDEO`, `AUDIO`, `MUSICA`, etc.) y luego por colecciones.
- No uses EPSILON para proyectos activos ni hibernados: esos van a `3.GAMMA` o `2.BETA`."""
    else:
        rule = """- Esta carpeta organiza la estructura general del vault ABGD-E.
- La configuracion de Obsidian vive en `.obsidian/`.
- Las capas internas separan notas, proyectos, referencias y biblioteca material."""

    return f"""---
title: "{path.name}"
tipo: indice-carpeta
nivel: {level}
codigo: "{path.name}"
estado: activa
ruta: "{rel}"
tags:
{tags}
aliases:
{alias_yaml}
---

# {path.name} - {title}

## Que es

{desc}

## Como se organiza

{_organization(level)}

## Subcarpetas

{_child_lines(path)}

## Regla de uso

{rule}
"""


def _structural_folders(vault: Path) -> list[Path]:
    return [
        vault,
        *(
            path
            for path in sorted(vault.rglob("*"))
            if path.is_dir()
            and not any(part.startswith(".") for part in path.relative_to(vault).parts)
        ),
    ]


def ensure_abgde_structure(
    vault: Path,
    *,
    refresh_existing: bool = False,
    skip_structure: bool = False,
    dry_run: bool = False,
) -> IndexStats:
    """Asegura estructura minima ABGD-E y notas indice homonimas.

    Pensado para uso manual y para `reset_obsidian.py rotate`. En dry-run no
    escribe carpetas ni notas; solo informa de las carpetas minimas que faltan.
    """
    vault = vault.resolve()
    alpha = vault / "1.ALPHA"
    if not dry_run and not alpha.exists():
        raise FileNotFoundError(f"No existe capa ALPHA esperada: {alpha}")

    stats = IndexStats()
    if not skip_structure:
        stats.dirs_created = _ensure_minimal_structure(vault, dry_run=dry_run)

    folders = _structural_folders(vault) if vault.exists() else []
    for folder in folders:
        note = folder / f"{folder.name}.md"
        if note.exists() and not refresh_existing:
            stats.notes_skipped.append(note)
            continue
        if dry_run:
            stats.notes_written.append(note)
            continue
        note.write_text(_note_text(folder, alpha), encoding="utf-8")
        stats.notes_written.append(note)

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-structure", action="store_true",
                        help="No crea subcarpetas minimas de BETA, GAMMA, DELTA y EPSILON")
    parser.add_argument("--refresh-existing", action="store_true",
                        help="Sobrescribe notas indice existentes con la plantilla actual")
    args = parser.parse_args()

    alpha = Path(os.getenv("OBSIDIAN_ALPHA_PATH", "")).resolve()
    if not alpha.exists():
        print(f"No existe OBSIDIAN_ALPHA_PATH: {alpha}")
        return 2

    vault = alpha.parent
    stats = ensure_abgde_structure(
        vault,
        refresh_existing=args.refresh_existing,
        skip_structure=args.skip_structure,
    )

    print(f"Carpetas estructurales creadas: {len(stats.dirs_created)}")
    print(f"Notas indice creadas/actualizadas: {len(stats.notes_written)}")
    print(f"Notas ya existentes saltadas: {len(stats.notes_skipped)}")
    for folder in stats.dirs_created[:20]:
        print(f"  + dir {folder.relative_to(vault)}")
    if len(stats.dirs_created) > 20:
        print(f"  ... y {len(stats.dirs_created) - 20} carpetas mas")
    for note in stats.notes_written[:20]:
        print(f"  + {note.relative_to(vault)}")
    if len(stats.notes_written) > 20:
        print(f"  ... y {len(stats.notes_written) - 20} mas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
