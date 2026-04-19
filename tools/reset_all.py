"""
Reset general (Fase 4) — encadena las 3 fases en orden seguro.

Orden:
  1. MAR       → tools/reset_mar.py reset-all
  2. Notion    → tools/reset_notion.py reset-ptn-all --snapshot
  3. Obsidian  → tools/reset_obsidian.py rotate [--new-vault-path ...] --snapshot

Politica:
  - Subprocess chain (no imports): cada sub-CLI corre como proceso propio.
    Si el orquestador muere, las fases ya completadas NO se rebobinan automaticamente.
  - Si una fase falla, ABORT: no se intenta la siguiente. Se imprimen los
    comandos de restore necesarios para recuperar lo hecho.
  - Snapshot obligatorio en Notion y Obsidian (forzado siempre); MAR usa el
    marker reversible en description como su mecanismo equivalente.
  - `--dry-run` se propaga a las tres fases (nada se escribe).
  - Sin `--yes`, pregunta confirmacion interactiva antes de ejecutar en real.
  - Obsidian deriva por defecto la ruta destino bajo la misma raiz del vault
    actual con la convención `ABGD-yymmdd`. `--obsidian-new-vault-path` queda
    como override explicito.

Uso:
    python tools/reset_all.py --dry-run                             # plan completo con ruta Obsidian derivada
    python tools/reset_all.py --dry-run --obsidian-new-vault-path C:/tmp/new-vault
    python tools/reset_all.py --yes --obsidian-new-vault-path C:/GDrive/...
    python tools/reset_all.py --yes --skip-obsidian                 # solo MAR + Notion
    python tools/reset_all.py --yes --skip-mar --skip-obsidian      # solo Notion
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
TOOLS = _ROOT / "tools"


@dataclass
class PhaseResult:
    name: str
    status: str          # "OK" | "FAIL" | "SKIP"
    detail: str = ""
    exit_code: int | None = None
    command: str = ""


def _run(cmd: list[str]) -> tuple[int, str]:
    """Ejecuta un subcomando, devuelve (exit_code, combined_output)."""
    print(f">>> {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd, cwd=str(_ROOT), capture_output=False, text=True, encoding="utf-8",
        )
        return proc.returncode, ""
    except FileNotFoundError as exc:
        return 127, str(exc)
    except Exception as exc:
        return 1, str(exc)


def _mar_phase(args) -> PhaseResult:
    if args.skip_mar:
        return PhaseResult(name="MAR", status="SKIP", detail="--skip-mar")
    cmd = [sys.executable, str(TOOLS / "reset_mar.py"), "reset-all"]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.mar_limit:
        cmd += ["--limit", str(args.mar_limit)]
    shown = " ".join(cmd)
    rc, err = _run(cmd)
    if rc != 0:
        return PhaseResult("MAR", "FAIL", err or f"exit {rc}", rc, shown)
    return PhaseResult("MAR", "OK", "", rc, shown)


def _notion_phase(args) -> PhaseResult:
    if args.skip_notion:
        return PhaseResult(name="Notion", status="SKIP", detail="--skip-notion")
    cmd = [sys.executable, str(TOOLS / "reset_notion.py"), "reset-ptn-all", "--snapshot"]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.notion_limit:
        cmd += ["--limit", str(args.notion_limit)]
    shown = " ".join(cmd)
    rc, err = _run(cmd)
    if rc != 0:
        return PhaseResult("Notion", "FAIL", err or f"exit {rc}", rc, shown)
    return PhaseResult("Notion", "OK", "", rc, shown)


def _obsidian_phase(args) -> PhaseResult:
    if args.skip_obsidian:
        return PhaseResult(name="Obsidian", status="SKIP", detail="--skip-obsidian")
    cmd = [
        sys.executable, str(TOOLS / "reset_obsidian.py"), "rotate",
        "--snapshot",
    ]
    if args.obsidian_new_vault_path:
        cmd += ["--new-vault-path", args.obsidian_new_vault_path]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.obsidian_depth is not None:
        cmd += ["--depth", str(args.obsidian_depth)]
    if args.obsidian_force:
        cmd.append("--force")
    shown = " ".join(cmd)
    rc, err = _run(cmd)
    if rc != 0:
        return PhaseResult("Obsidian", "FAIL", err or f"exit {rc}", rc, shown)
    return PhaseResult("Obsidian", "OK", "", rc, shown)


def _print_plan(args) -> None:
    print("=" * 70)
    print(f"RESET GENERAL — plan ({'dry-run' if args.dry_run else 'REAL'})")
    print("=" * 70)
    print(f"MAR      : {'SKIP' if args.skip_mar else 'ejecutar reset-all' + (f' --limit {args.mar_limit}' if args.mar_limit else '')}")
    print(f"Notion   : {'SKIP' if args.skip_notion else 'ejecutar reset-ptn-all --snapshot' + (f' --limit {args.notion_limit}' if args.notion_limit else '')}")
    if args.skip_obsidian:
        obs_plan = "SKIP (--skip-obsidian)"
    else:
        obs_plan = "rotate --snapshot"
        if args.obsidian_new_vault_path:
            obs_plan += f" --new-vault-path {args.obsidian_new_vault_path}"
        else:
            obs_plan += " [ruta derivada ABGD-yymmdd]"
        if args.obsidian_depth is not None:
            obs_plan += f" --depth {args.obsidian_depth}"
        if args.obsidian_force:
            obs_plan += " --force"
    print(f"Obsidian : {obs_plan}")
    print("=" * 70)


def _prompt_confirm() -> bool:
    try:
        resp = input("Continuar con la ejecucion real? [y/N]: ").strip().lower()
    except EOFError:
        return False
    return resp in ("y", "yes", "s", "si", "sí")


def _print_restore_hints(results: list[PhaseResult]) -> None:
    executed = [r for r in results if r.status == "OK"]
    if not executed:
        return
    print()
    print("INSTRUCCIONES DE RESTORE (ejecuta manualmente para deshacer lo hecho):")
    for r in executed:
        if r.name == "MAR":
            print("  python tools/reset_mar.py restore-all")
        elif r.name == "Notion":
            print("  python tools/reset_notion.py restore-all --target all")
        elif r.name == "Obsidian":
            print("  python tools/reset_obsidian.py restore --from <ruta_vault_viejo>")
            print("    (luego edita .env para apuntar de vuelta al vault viejo)")


def _print_summary(results: list[PhaseResult], started_at: str) -> int:
    print()
    print("=" * 70)
    print(f"RESET GENERAL — resumen (inicio {started_at})")
    print("=" * 70)
    for r in results:
        status_mark = {"OK": "[OK]  ", "FAIL": "[FAIL]", "SKIP": "[skip]"}.get(r.status, r.status)
        extra = f" — {r.detail}" if r.detail else ""
        print(f"  {status_mark} {r.name}{extra}")
    any_fail = any(r.status == "FAIL" for r in results)
    if any_fail:
        _print_restore_hints(results)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true",
                        help="Propaga --dry-run a las 3 fases (nada se escribe)")
    parser.add_argument("--yes", action="store_true",
                        help="Sin confirmacion interactiva (requerido para ejecucion real scripteada)")
    # MAR
    parser.add_argument("--skip-mar", action="store_true")
    parser.add_argument("--mar-limit", type=int, default=0,
                        help="--limit para MAR (0 = sin limite)")
    # Notion
    parser.add_argument("--skip-notion", action="store_true")
    parser.add_argument("--notion-limit", type=int, default=0,
                        help="--limit para Notion (aplica a cada target proyectos/tareas/notas)")
    # Obsidian
    parser.add_argument("--skip-obsidian", action="store_true")
    parser.add_argument("--obsidian-new-vault-path",
                        help="Ruta destino para rotate (opcional; default = sibling ABGD-yymmdd)")
    parser.add_argument("--obsidian-depth", type=int, default=None,
                        help="Override --depth de reset_obsidian (default 3 en el CLI)")
    parser.add_argument("--obsidian-force", action="store_true")
    args = parser.parse_args()

    _print_plan(args)

    if not args.dry_run and not args.yes:
        if not _prompt_confirm():
            print("Cancelado.")
            return 2

    started_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print()
    results: list[PhaseResult] = []

    # Fase 1 — MAR
    r1 = _mar_phase(args)
    results.append(r1)
    if r1.status == "FAIL":
        print()
        print("FASE 1 (MAR) FALLO. Abortando antes de tocar Notion / Obsidian.")
        return _print_summary(results, started_at)

    # Fase 2 — Notion
    print()
    r2 = _notion_phase(args)
    results.append(r2)
    if r2.status == "FAIL":
        print()
        print("FASE 2 (Notion) FALLO. Abortando antes de rotar Obsidian.")
        return _print_summary(results, started_at)

    # Fase 3 — Obsidian
    print()
    r3 = _obsidian_phase(args)
    results.append(r3)
    # Aunque falle, imprime summary al final

    return _print_summary(results, started_at)


if __name__ == "__main__":
    sys.exit(main())
