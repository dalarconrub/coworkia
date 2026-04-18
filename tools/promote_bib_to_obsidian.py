"""
Promueve un paper del catalogo BIB a una ficha de lectura en Obsidian.

Crea un .md bajo A1-INV/B13-PUB/<contexto>/ con frontmatter que cruza la
ficha con BIB (citekey, bib-id, doi) y el inicio de secciones de lectura
(Resumen, Puntos clave, Citas, Notas propias).

Opcional --sync: tras crear la ficha, encadena
log_obsidian_changes + log_ptn_changes + sync_inx_links --source obsidian
+ --source paperpile para que INX-ENLACES tenga tanto obsidian:<ruta>
como paperpile:<citekey>.

Uso:
    python tools/promote_bib_to_obsidian.py <citekey> [--contexto C137-ART] [--sync]
    python tools/promote_bib_to_obsidian.py einstein2005 --sync
    python tools/promote_bib_to_obsidian.py smith2024 --contexto C138-COM
    python tools/promote_bib_to_obsidian.py garcia2023 --force  # sobrescribe

Requisitos:
  - .env con NOTION_DB_BIB, OBSIDIAN_ALPHA_PATH.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import ALPHA_PATH, crear_nota_en_contexto


def _find_paper(db_bib: str, citekey: str) -> dict | None:
    ref = citekey.strip().lower()
    for r in query_data_source(db_bib):
        props = r.get("properties", {})
        ck = (extract_property_value(props.get("Citekey", {})) or "").strip()
        if ck and ck.lower() == ref:
            return r
    return None


def _existing_note_path(contexto: str, citekey: str) -> Path | None:
    parent = ALPHA_PATH / "A1-INV" / "B13-PUB" / contexto
    if not parent.exists():
        return None
    for p in parent.rglob(f"*{citekey}*.md"):
        return p
    return None


def _run_sync_chain() -> bool:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    steps = [
        ["tools/log_obsidian_changes.py"],
        ["tools/log_ptn_changes.py"],
        ["tools/sync_inx_links.py", "--source", "obsidian", "--limit", "200"],
        ["tools/sync_inx_links.py", "--source", "paperpile", "--limit", "200"],
    ]
    for step in steps:
        print(f"[sync] {' '.join(step)}")
        result = subprocess.run([sys.executable, *step], cwd=repo_root)
        if result.returncode != 0:
            print(f"[sync] fallo en {step[0]} (exit={result.returncode})", file=sys.stderr)
            return False
    return True


def promote(citekey: str, contexto: str = "C137-ART", force: bool = False, sync: bool = False) -> dict:
    db_bib = os.getenv("NOTION_DB_BIB")
    if not db_bib:
        raise RuntimeError("Falta NOTION_DB_BIB en .env")

    paper = _find_paper(db_bib, citekey)
    if not paper:
        raise ValueError(f"Paper con citekey '{citekey}' no encontrado en BIB")

    existing = _existing_note_path(contexto, citekey)
    if existing and not force:
        print(f"[skip] ficha ya existe: {existing.relative_to(ALPHA_PATH)}")
        if sync and not _run_sync_chain():
            raise RuntimeError("sync fallo")
        return {"action": "skipped", "path": str(existing), "citekey": citekey}

    props = paper.get("properties", {})
    titulo = extract_property_value(props.get("Título", {})) or citekey
    autores = extract_property_value(props.get("Autores", {})) or ""
    anio = extract_property_value(props.get("Año", {})) or ""
    tipo = extract_property_value(props.get("Tipo", {})) or ""
    journal = extract_property_value(props.get("Journal", {})) or ""
    doi = extract_property_value(props.get("DOI", {})) or ""
    abstract = extract_property_value(props.get("Abstract", {})) or ""

    frontmatter = {
        "citekey": citekey,
        "bib-id": paper["id"],
        "doi": doi,
        "anio": anio,
        "autores": autores,
        "tipo": tipo,
        "journal": journal,
        "estado-lectura": "Por leer",
    }

    contenido = (
        f"> {titulo}\n\n"
        f"## Resumen\n{abstract}\n\n"
        "## Puntos clave\n- \n\n"
        "## Citas relevantes\n- \n\n"
        "## Notas propias\n- \n"
    )

    path = crear_nota_en_contexto(
        area="A1-INV",
        bloque="B13-PUB",
        contexto=contexto,
        nombre=citekey,
        contenido=contenido,
        frontmatter=frontmatter,
    )

    print(f"created: {Path(path).name} ({citekey}) bib-id={paper['id']}")

    if sync and not _run_sync_chain():
        raise RuntimeError("sync fallo")

    return {"action": "created", "path": path, "citekey": citekey}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promueve un paper BIB a ficha de lectura Obsidian",
    )
    parser.add_argument("citekey", help="Citekey del paper en BIB")
    parser.add_argument("--contexto", default="C137-ART",
                        help="Contexto ABGD donde crear la ficha (default: C137-ART)")
    parser.add_argument("--force", action="store_true",
                        help="Sobrescribe ficha si ya existe")
    parser.add_argument("--sync", action="store_true",
                        help="Tras crear, cierra cruce INX obsidian:<ruta> + paperpile:<citekey>")
    args = parser.parse_args()

    try:
        promote(args.citekey, args.contexto, args.force, args.sync)
    except (ValueError, RuntimeError) as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
