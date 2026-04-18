"""
Validacion del caso de uso 11: Journal diario Obsidian en timeline.

Contrato:
- El journal vive bajo `A0-GTD/B0C-PLA/C0C9-Notas/` en el vault.
- Cada nota del journal con nombre `N<YYMMDD>-*.md` corresponde a un dia.
- Para cada journal detectado, el timeline del dia
  (`artifacts/daily/YYYY-MM-DD.md`) debe contener la seccion
  "Journal Obsidian" con referencia al archivo.

Uso: python tools/validate_case_11.py
Requiere .env: OBSIDIAN_ALPHA_PATH (opcional, pero sin el caso no se valida).

Exit codes:
  0  OK.
  1  Gaps (journal sin timeline, o sin referencia en timeline).
  2  Falta configuracion.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


_ROOT = Path(__file__).resolve().parent.parent
DAILY_DIR = _ROOT / "artifacts" / "daily"
NAME_RE = re.compile(r"^N(\d{6})-")


def _day_from_stem(stem: str) -> str | None:
    m = NAME_RE.match(stem)
    if not m:
        return None
    yymmdd = m.group(1)
    return f"20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"


def main() -> int:
    alpha = os.getenv("OBSIDIAN_ALPHA_PATH")
    if not alpha:
        print("Falta OBSIDIAN_ALPHA_PATH en .env (requerido para leer el journal).")
        return 2

    base = Path(alpha) / "A0-GTD" / "B0C-PLA" / "C0C9-Notas"
    if not base.exists():
        print(f"Directorio journal no existe: {base}")
        print("Crea la primera entrada bajo A0-GTD/B0C-PLA/C0C9-Notas/ con formato N<YYMMDD>-<descripcion>.md")
        return 1

    journals: list[tuple[str, Path]] = []
    for p in base.rglob("N*.md"):
        day = _day_from_stem(p.stem)
        if day:
            journals.append((day, p))

    matched: list[tuple[str, Path]] = []
    missing_timeline: list[tuple[str, Path]] = []
    missing_ref: list[tuple[str, Path]] = []
    alpha_root = Path(alpha)

    for day, path in journals:
        timeline_path = DAILY_DIR / f"{day}.md"
        if not timeline_path.exists():
            missing_timeline.append((day, path))
            continue
        content = timeline_path.read_text(encoding="utf-8", errors="ignore")
        if "## Journal Obsidian" not in content:
            missing_ref.append((day, path))
            continue
        try:
            rel_str = str(path.relative_to(alpha_root))
        except ValueError:
            rel_str = path.name
        if rel_str in content or path.name in content:
            matched.append((day, path))
        else:
            missing_ref.append((day, path))

    print("=== Validacion caso 11 (Journal Obsidian en timeline) ===\n")
    print(f"Journals detectados en A0-GTD/B0C-PLA/C0C9-Notas/: {len(journals)}")
    print(f"Con timeline y referencia correcta: {len(matched)}")

    if matched:
        print("\nEjemplos (hasta 5):")
        for day, path in matched[:5]:
            print(f"  - {day} | {path.name}")

    if missing_timeline:
        print("\n[!] Journals sin artifacts/daily/<day>.md (hasta 5):")
        for day, path in missing_timeline[:5]:
            print(f"  - {day} | {path.name}")
        print(f"    Ejecuta: python tools/timeline.py --date <day>")

    if missing_ref:
        print("\n[!] Timelines sin referencia al journal del dia (hasta 5):")
        for day, path in missing_ref[:5]:
            print(f"  - {day} | {path.name}")
        print("    Regenera el timeline: python tools/timeline.py --date <day>")

    if len(journals) == 0:
        print("\n[!] No hay entradas de journal en C0C9-Notas.")
        print("    Crea una nota con formato N<YYMMDD>-<descripcion>.md bajo")
        print("    A0-GTD/B0C-PLA/C0C9-Notas/ (p.ej. via obsidian_agent.py nueva-nota).")
        return 1

    if missing_timeline or missing_ref:
        return 1

    print("\nOK: todos los journals detectados estan referenciados en su timeline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
