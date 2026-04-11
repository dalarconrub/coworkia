"""
BACK-Obsidian — Crea la base de datos en Notion y exporta archivos .md del vault.

Lee cada .md, extrae frontmatter (YAML), detecta nivel ABGD por la ruta
y crea una fila en BACK-Obsidian por cada archivo.

Uso:
    python apps/backs_obsidian.py --parent <PAGE_ID>
    python apps/backs_obsidian.py --parent <PAGE_ID> --carpeta /ruta/subcarpeta
    python apps/backs_obsidian.py --parent <PAGE_ID> --dry-run
"""

import sys, os, re, time, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import create_database, add_page_to_database

ALPHA_PATH = os.getenv("OBSIDIAN_ALPHA_PATH", "G:/Mi unidad/ABGD/ABGD-25.09.05/1.ALPHA")

# Niveles ABGD por prefijo de nombre de archivo/carpeta
NIVEL_PREFIJOS = {
    "A": "Área",
    "B": "Bloque",
    "C": "Contexto",
    "P": "Proyecto",
    "T": "Tarea",
    "N": "Nota",
}

AREAS = {
    "A0": "A0-GTD",
    "A1": "A1-INV",
    "A2": "A2-UNI",
    "A3": "A3-VIT",
    "A4": "A4-ARX",
}

SCHEMA = {
    # ── Identificación ────────────────────────────────────────────────
    "Título":           {"title": {}},
    "Ruta":             {"rich_text": {}},      # ruta relativa desde ALPHA
    # ── Clasificación ABGD ────────────────────────────────────────────
    "Area":             {"select": {}},         # A0-GTD, A1-INV, etc.
    "Nivel":            {"select": {}},         # Área/Bloque/Contexto/Proyecto/Tarea/Nota
    # ── Contenido ─────────────────────────────────────────────────────
    "Preview":          {"rich_text": {}},      # primeros 500 chars del contenido
    "Tags":             {"multi_select": {}},   # tags del frontmatter
    "Alias":            {"rich_text": {}},      # alias del frontmatter
    # ── Fechas ────────────────────────────────────────────────────────
    "Fecha_nota":       {"date": {}},           # del nombre N[YYMMDD] o frontmatter
    "Modificado":       {"date": {}},           # fecha modificación del archivo
    "Exportado":        {"date": {}},
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extrae YAML frontmatter. Devuelve (fm_dict, contenido_sin_fm)."""
    fm = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            yaml_block = text[3:end].strip()
            body = text[end + 4:].strip()
            for line in yaml_block.splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    k, v = k.strip(), v.strip()
                    # Tags: puede ser lista YAML inline [a, b] o valor simple
                    if v.startswith("[") and v.endswith("]"):
                        fm[k] = [x.strip().strip('"\'') for x in v[1:-1].split(",") if x.strip()]
                    else:
                        fm[k] = v.strip('"\'')
            return fm, body
    return fm, text


def detect_area(ruta: str) -> str:
    parts = Path(ruta).parts
    for part in parts:
        for code, name in AREAS.items():
            if part.startswith(code) or part.startswith(name):
                return name
    return ""


def detect_nivel(nombre: str) -> str:
    for prefix, nivel in NIVEL_PREFIJOS.items():
        if re.match(rf'^{prefix}\[', nombre) or re.match(rf'^{prefix}\d', nombre):
            return nivel
    return "Nota"


def extract_fecha_nota(nombre: str, fm: dict) -> str | None:
    # Nombre tipo N[260317]-Descripcion.md
    m = re.match(r'^N\[(\d{6})\]', nombre)
    if m:
        yy, mm, dd = m.group(1)[:2], m.group(1)[2:4], m.group(1)[4:6]
        return f"20{yy}-{mm}-{dd}"
    # Frontmatter: date, fecha, created
    for key in ("date", "fecha", "created", "Date"):
        if key in fm and fm[key]:
            val = str(fm[key])[:10]
            if re.match(r'\d{4}-\d{2}-\d{2}', val):
                return val
    return None


def md_to_props(md_path: Path, alpha_root: Path, fecha_hoy: str) -> dict:
    ruta_rel = str(md_path.relative_to(alpha_root))

    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        text = ""

    fm, body = parse_frontmatter(text)
    preview  = body[:500].strip()

    nombre   = md_path.stem
    titulo   = fm.get("title", fm.get("titulo", fm.get("alias", nombre)))
    if isinstance(titulo, list):
        titulo = titulo[0] if titulo else nombre

    tags = fm.get("tags", fm.get("Tags", []))
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    alias = fm.get("aliases", fm.get("alias", ""))
    if isinstance(alias, list):
        alias = ", ".join(alias)

    area        = detect_area(ruta_rel)
    nivel       = detect_nivel(nombre)
    fecha_nota  = extract_fecha_nota(nombre, fm)
    modificado  = datetime.fromtimestamp(md_path.stat().st_mtime).strftime("%Y-%m-%d")

    props = {
        "Título":    {"title": [{"text": {"content": str(titulo)[:200]}}]},
        "Ruta":      {"rich_text": [{"text": {"content": ruta_rel[:2000]}}]},
        "Nivel":     {"select": {"name": nivel}},
        "Exportado": {"date": {"start": fecha_hoy}},
        "Modificado":{"date": {"start": modificado}},
    }
    if area:
        props["Area"] = {"select": {"name": area}}
    if preview:
        props["Preview"] = {"rich_text": [{"text": {"content": preview}}]}
    if tags:
        props["Tags"] = {"multi_select": [{"name": t[:100]} for t in tags[:10]]}
    if alias:
        props["Alias"] = {"rich_text": [{"text": {"content": str(alias)[:500]}}]}
    if fecha_nota:
        props["Fecha_nota"] = {"date": {"start": fecha_nota}}
    return props


def main(parent_id: str, carpeta: str, dry_run: bool):
    fecha_hoy  = date.today().isoformat()
    alpha_root = Path(ALPHA_PATH)
    base_dir   = Path(carpeta) if carpeta else alpha_root

    if not base_dir.exists():
        print(f"ERROR: carpeta no encontrada: {base_dir}")
        sys.exit(1)

    archivos = sorted(base_dir.rglob("*.md"))
    print(f"Archivos .md encontrados: {len(archivos)} en {base_dir}")

    if not dry_run:
        print("Creando BACK-Obsidian en Notion...")
        db = create_database(parent_id, "BACK-Obsidian", SCHEMA)
        db_id = db["id"]
        print(f"  ✓ {db_id}\n")
    else:
        db_id = "DRY-RUN"
        print("(Dry run — no se escribe en Notion)\n")

    total_ok, total_err = 0, 0
    for i, md in enumerate(archivos, 1):
        try:
            props = md_to_props(md, alpha_root, fecha_hoy)
            if not dry_run:
                add_page_to_database(db_id, props)
                time.sleep(0.35)
            total_ok += 1
            if i % 25 == 0:
                print(f"  {i}/{len(archivos)}...")
        except Exception as e:
            total_err += 1
            print(f"  ✗ {md.name}: {e}")

    print(f"\n{'─'*50}")
    print(f"  OK: {total_ok}  |  Errores: {total_err}")
    if not dry_run:
        print(f"  → https://notion.so/{db_id.replace('-','')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exporta vault Obsidian → BACK-Obsidian en Notion")
    parser.add_argument("--parent",   required=True, help="ID de página Notion padre")
    parser.add_argument("--carpeta",  default="",    help="Subcarpeta del vault (vacío = ALPHA completo)")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    pid = args.parent.replace("-", "")
    if len(pid) == 32:
        pid = f"{pid[:8]}-{pid[8:12]}-{pid[12:16]}-{pid[16:20]}-{pid[20:]}"
    main(pid, args.carpeta, args.dry_run)
