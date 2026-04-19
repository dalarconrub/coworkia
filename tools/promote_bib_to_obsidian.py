"""
Promueve un paper del catalogo BIB a una ficha de lectura en Obsidian.

Crea un .md bajo A1-INV/B13-PUB/<contexto>/ con frontmatter que cruza la
ficha con BIB (citekey, bib-id, doi) y el inicio de secciones de lectura
(Resumen, Puntos clave, Citas, Notas propias).

Opcional --sync: tras crear la ficha, encadena
log_obsidian_changes + log_ptn_changes + sync_inx_links --source obsidian
+ --source paperpile para que INX-ENLACES tenga tanto obsidian:<ruta>
+ como paperpile:<citekey>. En batch, el sync se ejecuta completo
+ para no dejar INX parcial por limites artificiales.

Uso:
    python tools/promote_bib_to_obsidian.py <citekey> [--contexto C137-ART] [--sync]
    python tools/promote_bib_to_obsidian.py --all-pending --dry-run --limit 10
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

from tools.env_utils import load_project_env

load_project_env(Path(__file__).resolve().parent.parent / ".env")

from tools.notion_tools import extract_property_value, query_data_source
from tools.obsidian_tools import ALPHA_PATH, crear_nota_en_contexto


def _paper_meta(row: dict) -> dict:
    props = row.get("properties", {})
    return {
        "citekey": (extract_property_value(props.get("Citekey", {})) or "").strip(),
        "estado": (extract_property_value(props.get("Estado", {})) or "").strip(),
        "titulo": (extract_property_value(props.get("Título", {})) or "").strip(),
        "autores": (extract_property_value(props.get("Autores", {})) or "").strip(),
        "journal": (extract_property_value(props.get("Journal", {})) or "").strip(),
        "anio": (extract_property_value(props.get("Año", {})) or "").strip(),
    }


def _matches_query(meta: dict, query: str | None) -> bool:
    if not query:
        return True
    haystack = " | ".join(
        [
            meta.get("citekey", ""),
            meta.get("titulo", ""),
            meta.get("autores", ""),
            meta.get("journal", ""),
            meta.get("anio", ""),
        ]
    ).lower()
    return query.lower() in haystack


def _matches_contains(value: str, needle: str | None) -> bool:
    if not needle:
        return True
    return needle.lower() in (value or "").lower()


def _matches_estado(meta: dict, estado: str | None) -> bool:
    if not estado:
        return meta["estado"] == "Por leer"
    return meta["estado"].lower() == estado.lower()


def _find_paper(db_bib: str, citekey: str) -> dict | None:
    ref = citekey.strip().lower()
    for r in query_data_source(db_bib):
        props = r.get("properties", {})
        ck = (extract_property_value(props.get("Citekey", {})) or "").strip()
        if ck and ck.lower() == ref:
            return r
    return None


def _pending_papers(
    db_bib: str,
    query: str | None = None,
    year: str | None = None,
    author: str | None = None,
    journal: str | None = None,
    estado: str | None = None,
) -> list[dict]:
    out: list[dict] = []
    for r in query_data_source(db_bib):
        meta = _paper_meta(r)
        if not meta["citekey"] or not _matches_estado(meta, estado):
            continue
        if year and meta["anio"] != str(year):
            continue
        if not _matches_contains(meta["autores"], author):
            continue
        if not _matches_contains(meta["journal"], journal):
            continue
        if not _matches_query(meta, query):
            continue
        out.append(r)
    out.sort(key=lambda row: _paper_meta(row)["citekey"].lower())
    return out


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
        ["tools/sync_inx_links.py", "--source", "obsidian"],
        ["tools/sync_inx_links.py", "--source", "paperpile"],
    ]
    for step in steps:
        print(f"[sync] {' '.join(step)}")
        result = subprocess.run([sys.executable, *step], cwd=repo_root)
        if result.returncode != 0:
            print(f"[sync] fallo en {step[0]} (exit={result.returncode})", file=sys.stderr)
            return False
    return True


def _promote_paper(paper: dict, citekey: str, contexto: str, force: bool) -> dict:
    if not paper:
        raise ValueError(f"Paper con citekey '{citekey}' no encontrado en BIB")

    existing = _existing_note_path(contexto, citekey)
    if existing and not force:
        print(f"[skip] ficha ya existe: {existing.relative_to(ALPHA_PATH)}")
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

    return {"action": "created", "path": path, "citekey": citekey}


def promote(citekey: str, contexto: str = "C137-ART", force: bool = False, sync: bool = False) -> dict:
    db_bib = os.getenv("NOTION_DB_BIB")
    if not db_bib:
        raise RuntimeError("Falta NOTION_DB_BIB en .env")

    paper = _find_paper(db_bib, citekey)
    result = _promote_paper(paper, citekey, contexto, force)
    if sync and not _run_sync_chain():
        raise RuntimeError("sync fallo")
    return result


def promote_all_pending(
    contexto: str = "C137-ART",
    force: bool = False,
    sync: bool = False,
    dry_run: bool = False,
    limit: int | None = None,
    query: str | None = None,
    year: str | None = None,
    author: str | None = None,
    journal: str | None = None,
    estado: str | None = None,
) -> dict:
    db_bib = os.getenv("NOTION_DB_BIB")
    if not db_bib:
        raise RuntimeError("Falta NOTION_DB_BIB en .env")

    papers = _pending_papers(
        db_bib,
        query=query,
        year=year,
        author=author,
        journal=journal,
        estado=estado,
    )
    if limit:
        papers = papers[:limit]

    planned = []
    created = []
    skipped = []
    for paper in papers:
        props = paper.get("properties", {})
        meta = _paper_meta(paper)
        citekey = meta["citekey"]
        if not citekey:
            continue
        existing = _existing_note_path(contexto, citekey)
        if dry_run:
            action = "create"
            if existing and not force:
                action = "skip"
            planned.append(
                {
                    "citekey": citekey,
                    "action": action,
                    "existing": str(existing) if existing else "",
                    "anio": meta["anio"],
                    "titulo": meta["titulo"],
                }
            )
            continue
        result = _promote_paper(paper, citekey, contexto, force)
        if result["action"] == "created":
            created.append(result["citekey"])
        else:
            skipped.append(result["citekey"])

    if dry_run:
        print("=== Promote BIB -> Obsidian --all-pending (dry-run) ===\n")
        print(f"Candidatos revisados: {len(planned)}")
        print(f"Crearia: {sum(1 for item in planned if item['action'] == 'create')}")
        print(f"Saltaria: {sum(1 for item in planned if item['action'] == 'skip')}")
        for item in planned[:20]:
            line = f"  - {item['citekey']} | {item['action']}"
            if item["anio"]:
                line += f" | {item['anio']}"
            if item["titulo"]:
                line += f" | {item['titulo'][:80]}"
            if item["existing"]:
                line += f" | {item['existing']}"
            print(line)
        if len(planned) > 20:
            print(f"  (+{len(planned) - 20} mas)")
        return {"dry_run": True, "planned": planned}

    print("\n=== Promote BIB -> Obsidian --all-pending ===")
    print(f"Creadas: {len(created)}")
    print(f"Saltadas: {len(skipped)}")

    if sync and (created or skipped) and not _run_sync_chain():
        raise RuntimeError("sync fallo")

    return {"dry_run": False, "created": created, "skipped": skipped}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promueve un paper BIB a ficha de lectura Obsidian",
    )
    parser.add_argument("citekey", nargs="?", help="Citekey del paper en BIB")
    parser.add_argument("--all-pending", action="store_true",
                        help="Promueve masivamente papers con Estado=Por leer que aun no tienen ficha.")
    parser.add_argument("--contexto", default="C137-ART",
                        help="Contexto ABGD donde crear la ficha (default: C137-ART)")
    parser.add_argument("--force", action="store_true",
                        help="Sobrescribe ficha si ya existe")
    parser.add_argument("--sync", action="store_true",
                        help="Tras crear, cierra cruce INX obsidian:<ruta> + paperpile:<citekey>")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo informa lo que haria con --all-pending, sin crear fichas.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limita cuantos papers revisar/promover en --all-pending.")
    parser.add_argument("--query",
                        help="Filtro textual para --all-pending: busca en citekey, titulo, autores, journal y año.")
    parser.add_argument("--year",
                        help="Filtro exacto por año para --all-pending.")
    parser.add_argument("--author",
                        help="Filtro por substring en Autores para --all-pending.")
    parser.add_argument("--journal",
                        help="Filtro por substring en Journal para --all-pending.")
    parser.add_argument("--estado",
                        help="Filtro exacto de Estado para --all-pending. Default operativo: Por leer.")
    args = parser.parse_args()

    try:
        if args.all_pending:
            if args.citekey:
                raise ValueError("No combines <citekey> con --all-pending")
            promote_all_pending(
                args.contexto,
                args.force,
                args.sync,
                args.dry_run,
                args.limit,
                args.query,
                args.year,
                args.author,
                args.journal,
                args.estado,
            )
        else:
            if not args.citekey:
                raise ValueError("Indica <citekey> o usa --all-pending")
            if args.dry_run:
                raise ValueError("--dry-run solo aplica a --all-pending")
            if args.limit is not None:
                raise ValueError("--limit solo aplica a --all-pending")
            if args.query or args.year or args.author or args.journal or args.estado:
                raise ValueError("--query/--year/--author/--journal/--estado solo aplican a --all-pending")
            promote(args.citekey, args.contexto, args.force, args.sync)
    except (ValueError, RuntimeError) as e:
        print(f"[error] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
