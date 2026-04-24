"""
Diagnostico rapido de configuracion para Coworkia.
"""

from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def load_local_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(ENV_PATH)
        return
    except Exception:
        pass

    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def missing(*keys: str) -> list[str]:
    return [key for key in keys if not os.getenv(key)]


def status_line(label: str, ok: bool, detail: str) -> str:
    state = "OK" if ok else "FALTA"
    return f"[{state}] {label}: {detail}"


def notion_token_detail() -> tuple[bool, str]:
    token = os.getenv("NOTION_TOKEN", "").strip()
    if not token:
        return False, "falta NOTION_TOKEN"
    if len(token) < 20:
        return False, "NOTION_TOKEN parece demasiado corto"
    return True, "NOTION_TOKEN presente"


def check_todoist() -> str:
    miss = missing("TODOIST_API_KEY")
    if miss:
        return status_line("MAR / Todoist", False, "falta TODOIST_API_KEY")
    return status_line("MAR / Todoist", True, "configuracion minima lista")


def check_ptn() -> str:
    ok, detail = notion_token_detail()
    return status_line("PTN / Notion", ok, detail if ok else detail)


def check_kit() -> str:
    ok, detail = notion_token_detail()
    return status_line("KIT / Notion", ok, detail if ok else detail)


def check_rep() -> str:
    token_ok, token_detail = notion_token_detail()
    miss = missing("NOTION_DB_GIT")
    if not token_ok:
        miss = ["NOTION_TOKEN", *miss]
    if miss:
        return status_line("GIT / GitHub", False, f"faltan {', '.join(miss)}")
    extra = ""
    if not os.getenv("GITHUB_TOKEN"):
        extra = " | aviso: falta GITHUB_TOKEN para llamadas a GitHub"
    return status_line("GIT / GitHub", True, f"{token_detail}; NOTION_DB_GIT presente{extra}")


def check_bib() -> str:
    token_ok, token_detail = notion_token_detail()
    miss = missing("NOTION_DB_BIB")
    if not token_ok:
        miss = ["NOTION_TOKEN", *miss]
    if miss:
        return status_line("BIB / Paperpile", False, f"faltan {', '.join(miss)}")
    extra = ""
    if not os.getenv("PAPERPILE_BIBTEX_URL"):
        extra = " | aviso: falta PAPERPILE_BIBTEX_URL para importar/sincronizar"
    return status_line("BIB / Paperpile", True, f"{token_detail}; NOTION_DB_BIB presente{extra}")


def check_obsidian() -> str:
    alpha = os.getenv("OBSIDIAN_ALPHA_PATH", "").strip()
    if not alpha:
        return status_line("ABGD / Obsidian", False, "falta OBSIDIAN_ALPHA_PATH")

    alpha_path = Path(alpha)
    try:
        alpha_exists = alpha_path.exists()
    except PermissionError:
        return status_line("ABGD / Obsidian", False, f"sin acceso a la ruta: {alpha}")

    if not alpha_exists:
        return status_line("ABGD / Obsidian", False, f"la ruta no existe: {alpha}")

    extra = ""
    root = os.getenv("OBSIDIAN_ABGD_ROOT", "").strip()
    if root:
        try:
            root_exists = Path(root).exists()
        except PermissionError:
            extra = f" | aviso: sin acceso a OBSIDIAN_ABGD_ROOT ({root})"
        else:
            if not root_exists:
                extra = f" | aviso: OBSIDIAN_ABGD_ROOT no existe ({root})"

    return status_line("ABGD / Obsidian", True, f"ruta valida: {alpha}{extra}")


def main() -> None:
    load_local_env()

    print("=== COWORKIA CONFIG DOCTOR ===\n")
    print(f"Repo : {ROOT}")
    print(f".env : {'encontrado' if ENV_PATH.exists() else 'no encontrado'}")
    print()
    print(check_todoist())
    print(check_ptn())
    print(check_kit())
    print(check_rep())
    print(check_bib())
    print(check_obsidian())
    print("\nVariables normalmente necesarias:")
    print("- TODOIST_API_KEY")
    print("- NOTION_TOKEN")
    print("- NOTION_DB_GIT")
    print("- NOTION_DB_BIB")
    print("- OBSIDIAN_ALPHA_PATH")


if __name__ == "__main__":
    main()
