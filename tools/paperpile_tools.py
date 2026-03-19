"""
Wrappers para obtener y parsear datos de Paperpile.
Usa la URL de Automatic BibTeX Export para leer la biblioteca.
Documentación: https://paperpile.com/h/automatic-bibtex-export/
"""

import os
import requests
import bibtexparser
from dotenv import load_dotenv

load_dotenv()

PAPERPILE_BIBTEX_URL = os.getenv("PAPERPILE_BIBTEX_URL", "")


# ─── OBTENER DATOS ───────────────────────────────────────────────────────────

def fetch_bibtex(url: str = None) -> str:
    """Descarga el archivo BibTeX desde la URL de Paperpile."""
    bibtex_url = url or PAPERPILE_BIBTEX_URL
    if not bibtex_url:
        raise ValueError(
            "Falta PAPERPILE_BIBTEX_URL en .env. "
            "Activa Automatic BibTeX Export en Paperpile y copia la URL."
        )
    resp = requests.get(bibtex_url, timeout=60)
    resp.raise_for_status()
    return resp.text


def parse_bibtex(bibtex_str: str) -> list[dict]:
    """Parsea un string BibTeX y devuelve lista de entradas normalizadas."""
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    db = bibtexparser.loads(bibtex_str, parser=parser)
    return [_normalize_entry(e) for e in db.entries]


def get_library(url: str = None) -> list[dict]:
    """Descarga y parsea toda la biblioteca de Paperpile."""
    raw = fetch_bibtex(url)
    return parse_bibtex(raw)


# ─── NORMALIZACIÓN ───────────────────────────────────────────────────────────

# Mapeo de tipos BibTeX a nombres legibles
TIPO_MAP = {
    "article": "Artículo",
    "book": "Libro",
    "inbook": "Capítulo de libro",
    "incollection": "En colección",
    "inproceedings": "Conferencia",
    "conference": "Conferencia",
    "phdthesis": "Tesis doctoral",
    "mastersthesis": "Tesis de máster",
    "techreport": "Informe técnico",
    "manual": "Manual",
    "misc": "Otro",
    "unpublished": "No publicado",
    "proceedings": "Actas",
    "booklet": "Folleto",
    "online": "Online",
}


def _normalize_entry(entry: dict) -> dict:
    """Normaliza una entrada BibTeX a un dict limpio."""
    entry_type = entry.get("ENTRYTYPE", "misc").lower()

    # Extraer autores como string limpio
    authors_raw = entry.get("author", "")
    authors = _clean_authors(authors_raw)

    # Keywords pueden venir separadas por coma o punto y coma
    keywords_raw = entry.get("keywords", "") or entry.get("keyword", "")
    keywords = _parse_keywords(keywords_raw)

    # Paperpile añade campos propios con prefijo paperpile-
    folders = entry.get("paperpile-folder", "") or entry.get("folder", "")
    labels = entry.get("paperpile-labels", "") or entry.get("labels", "")

    # DOI como URL
    doi = entry.get("doi", "")
    doi_url = f"https://doi.org/{doi}" if doi and not doi.startswith("http") else doi

    # Año como entero
    year_str = entry.get("year", "")
    year = int(year_str) if year_str.isdigit() else None

    return {
        "citekey": entry.get("ID", ""),
        "titulo": _clean_latex(entry.get("title", "")),
        "autores": authors,
        "year": year,
        "tipo": TIPO_MAP.get(entry_type, entry_type.capitalize()),
        "tipo_raw": entry_type,
        "journal": _clean_latex(entry.get("journal", "") or entry.get("booktitle", "")),
        "doi": doi,
        "doi_url": doi_url,
        "abstract": _clean_latex(entry.get("abstract", "")),
        "keywords": keywords,
        "volume": entry.get("volume", ""),
        "number": entry.get("number", "") or entry.get("issue", ""),
        "pages": entry.get("pages", ""),
        "publisher": entry.get("publisher", ""),
        "url": entry.get("url", "") or doi_url,
        "issn": entry.get("issn", ""),
        "isbn": entry.get("isbn", ""),
        "pmid": entry.get("pmid", ""),
        "arxivid": entry.get("eprint", "") or entry.get("arxivid", ""),
        "folders": [f.strip() for f in folders.split(",") if f.strip()] if folders else [],
        "labels": [l.strip() for l in labels.split(",") if l.strip()] if labels else [],
        "note": entry.get("note", "") or entry.get("annote", ""),
    }


def _clean_authors(raw: str) -> str:
    """Limpia string de autores BibTeX: 'Apellido, Nombre and ...' → 'Nombre Apellido, ...'"""
    if not raw:
        return ""
    authors = []
    for author in raw.split(" and "):
        author = author.strip()
        if not author:
            continue
        if "," in author:
            parts = [p.strip() for p in author.split(",", 1)]
            authors.append(f"{parts[1]} {parts[0]}")
        else:
            authors.append(author)
    return ", ".join(authors)


def _clean_latex(text: str) -> str:
    """Limpia comandos LaTeX comunes de un string."""
    if not text:
        return ""
    replacements = {
        "{": "", "}": "",
        "\\&": "&", "\\%": "%",
        "\\textit": "", "\\textbf": "",
        "\\emph": "", "\\url": "",
        "~": " ", "--": "–",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


def _parse_keywords(raw: str) -> list[str]:
    """Parsea keywords separadas por coma, punto y coma, o newline."""
    if not raw:
        return []
    # Normalizar separadores
    for sep in [";", "\n"]:
        raw = raw.replace(sep, ",")
    return [k.strip() for k in raw.split(",") if k.strip()]
