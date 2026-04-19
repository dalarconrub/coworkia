"""
Validador del caso de uso 14: bateria auto-ejecutable del sistema de reseteo.

Comprueba que los CLIs de las fases 1-4 responden como especificados, son
idempotentes, protegen contra argumentos invalidos y no mutan datos en
--dry-run. No destruye nada: las unicas llamadas a la API que escriben son
las de `ensure_archivo_field.py`, que es idempotente (re-ejecutarlo con la
propiedad ya creada no toca el schema).

Exit codes:
  0  Todos los tests A han pasado.
  1  Hay fallos. Revisa el output [FAIL].

Uso:
    python tools/validate_case_14.py
    python tools/validate_case_14.py --verbose   # imprime stdout/stderr de cada test
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date as Date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except Exception:
    pass

PY = sys.executable
TOOLS = _ROOT / "tools"
APPS = _ROOT / "apps"


# ==================== infraestructura de test ====================


@dataclass
class TestResult:
    id: str
    label: str
    passed: bool
    detail: str = ""
    skipped: bool = False


class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []

    def run(self, cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
        proc = subprocess.run(
            cmd, cwd=str(_ROOT), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        if self.verbose:
            print(f"  $ {' '.join(cmd)}")
            if proc.stdout:
                print(f"    stdout: {proc.stdout[:400]}")
            if proc.stderr:
                print(f"    stderr: {proc.stderr[:400]}")
        return proc.returncode, proc.stdout or "", proc.stderr or ""

    def expect(self, tid: str, label: str, condition: bool, detail: str = "") -> None:
        self.results.append(TestResult(tid, label, condition, detail))

    def skip(self, tid: str, label: str, reason: str) -> None:
        self.results.append(TestResult(tid, label, True, reason, skipped=True))


# ==================== helpers ====================


def _tmp_dir() -> Path:
    """Directorio temporal seguro para tests que simulan paths."""
    return Path(tempfile.mkdtemp(prefix="coworkia-val14-"))


def _read_env(key: str) -> str | None:
    return os.getenv(key)


# ==================== Fase 1: MAR ====================


def fase_mar(tr: TestRunner) -> None:
    script = TOOLS / "reset_mar.py"

    # 1.1 help
    rc, out, _ = tr.run([PY, str(script), "--help"])
    tr.expect("1.1", "reset_mar.py --help exit 0 y muestra usage",
              rc == 0 and "usage:" in out, f"rc={rc}")

    # 1.2 reset-all --dry-run --limit 2
    rc, out, _ = tr.run([PY, str(script), "reset-all", "--dry-run", "--limit", "2"])
    tr.expect("1.2", "reset-all --dry-run --limit 2 exit 0",
              rc == 0 and "Resumen reset-all" in out)

    # 1.3 reset-by-type idea --dry-run --limit 2
    rc, out, _ = tr.run([PY, str(script), "reset-by-type", "idea", "--dry-run", "--limit", "2"])
    tr.expect("1.3", "reset-by-type idea --dry-run --limit 2 exit 0",
              rc == 0)

    # 1.4 reset-overdue --days 3650 --dry-run
    rc, out, _ = tr.run([PY, str(script), "reset-overdue", "--days", "3650", "--dry-run"])
    tr.expect("1.4", "reset-overdue --days 3650 --dry-run exit 0",
              rc == 0)

    # 1.5 reset-by-project "__NO_EXISTE__" --dry-run → debe fallar con mensaje claro
    rc, out, err = tr.run([PY, str(script), "reset-by-project", "__NO_EXISTE_14__", "--dry-run"])
    combined = (out + err).lower()
    tr.expect("1.5", "reset-by-project inexistente falla con mensaje claro",
              rc != 0 and "no encontrado" in combined)

    # 1.6 list-archived
    rc, out, _ = tr.run([PY, str(script), "list-archived"])
    tr.expect("1.6", "list-archived exit 0",
              rc == 0)

    # 1.7 restore NO_EXISTE
    rc, out, err = tr.run([PY, str(script), "restore", "999999999999"])
    combined = (out + err).lower()
    tr.expect("1.7", "restore id inexistente falla con mensaje claro",
              rc != 0 and "no encontrada" in combined)

    # 1.8 manual
    tr.skip("1.8", "idempotencia reset→reset (requiere ejecucion real)",
            "ejecuta manualmente tras un reset real")


# ==================== Fase 2: Notion ====================


def fase_notion(tr: TestRunner) -> None:
    bootstrapper = TOOLS / "ensure_archivo_field.py"
    script = TOOLS / "reset_notion.py"

    # 2.1 bootstrapper dry-run
    rc, out, _ = tr.run([PY, str(bootstrapper), "--dry-run"])
    tr.expect("2.1", "ensure_archivo_field.py --dry-run OK en 4 DS",
              rc == 0 and "Resumen:" in out)

    # 2.2 bootstrapper real (idempotente)
    rc, out, _ = tr.run([PY, str(bootstrapper)])
    m = re.search(r"ya_existian=(\d+)", out)
    all_already = m is not None and int(m.group(1)) == 4
    tr.expect("2.2", "ensure_archivo_field.py real reporta ya_existian=4 (idempotente)",
              rc == 0 and all_already, f"ya_existian={m.group(1) if m else '?'}")

    # 2.3 help
    rc, out, _ = tr.run([PY, str(script), "--help"])
    tr.expect("2.3", "reset_notion.py --help exit 0",
              rc == 0 and "usage:" in out)

    # 2.4-2.6 dry-run por target con limit
    for tid, tgt in [("2.4", "reset-ptn-proyectos"), ("2.5", "reset-ptn-tareas"), ("2.6", "reset-ptn-notas")]:
        rc, out, _ = tr.run([PY, str(script), tgt, "--dry-run", "--limit", "2"])
        ok = rc == 0 and "flipped" in out and "inx propagadas" in out
        # Extraer inx_missing del output
        missing_match = re.search(r"inx sin fila\s*:\s*(\d+)", out)
        missing = int(missing_match.group(1)) if missing_match else -1
        tr.expect(tid, f"{tgt} --dry-run --limit 2 + INX missing=0",
                  ok and missing == 0, f"rc={rc}, inx_missing={missing}")

    # 2.7 list-archived
    rc, out, _ = tr.run([PY, str(script), "list-archived", "--target", "all"])
    tr.expect("2.7", "list-archived --target all exit 0",
              rc == 0 and "Total:" in out)

    # 2.8 snapshot JSON válido
    rc, out, _ = tr.run([PY, str(script), "reset-ptn-proyectos", "--dry-run", "--snapshot", "--limit", "1"])
    snapshot_path = None
    for line in out.splitlines():
        if "Snapshot:" in line:
            snapshot_path = line.split("Snapshot:", 1)[1].strip()
            break
    snap_ok = False
    if snapshot_path:
        try:
            data = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
            snap_ok = isinstance(data, list) and all("id" in e and "title" in e for e in data)
        except Exception:
            snap_ok = False
    tr.expect("2.8", "snapshot JSON parseable con id/title",
              rc == 0 and snap_ok, f"snapshot={snapshot_path}")

    # 2.9 restore uuid inventado
    fake_uuid = "99999999-9999-9999-9999-999999999999"
    rc, out, err = tr.run([PY, str(script), "restore", fake_uuid])
    combined = (out + err).lower()
    tr.expect("2.9", "restore uuid inventado falla con mensaje claro",
              rc != 0 and "no encontrada" in combined)


# ==================== Fase 3: Obsidian ====================


def fase_obsidian(tr: TestRunner) -> None:
    script = TOOLS / "reset_obsidian.py"

    # 3.1 status
    rc, out, _ = tr.run([PY, str(script), "status"])
    vault = _read_env("OBSIDIAN_ABGD_ROOT")
    ok_status = rc == 0 and vault is not None and vault.replace("/", "\\") in out.replace("/", "\\")
    tr.expect("3.1", "status muestra OBSIDIAN_ABGD_ROOT + Archivo presente",
              ok_status and "Archivo" in out)

    # 3.2 rotate dry-run snapshot → path tmp
    tmp = _tmp_dir() / "new-vault-test"
    rc, out, _ = tr.run([PY, str(script), "rotate", "--new-vault-path", str(tmp),
                         "--dry-run", "--snapshot"])
    snap_ok = "Snapshot:" in out
    sigue_intacto = "SIGUIENTE PASO" in out
    tmp_empty = not tmp.exists() or (tmp.exists() and not any(tmp.iterdir()))
    tr.expect("3.2", "rotate --dry-run --snapshot no crea dirs + imprime snapshot",
              rc == 0 and snap_ok and sigue_intacto and tmp_empty,
              f"tmp_exists={tmp.exists()}, empty={tmp_empty}")

    # 3.3 rotate sin --new-vault-path
    rc, out, err = tr.run([PY, str(script), "rotate"])
    tr.expect("3.3", "rotate sin --new-vault-path falla (argparse)",
              rc != 0 and "required" in (out + err).lower())

    # 3.4 rotate --new-vault-path == OBSIDIAN_ABGD_ROOT
    if vault:
        rc, out, err = tr.run([PY, str(script), "rotate", "--new-vault-path", vault, "--dry-run"])
        tr.expect("3.4", "rotate con --new-vault-path == vault actual falla",
                  rc != 0 and "no puede coincidir" in (out + err).lower())
    else:
        tr.skip("3.4", "rotate colision con vault actual", "OBSIDIAN_ABGD_ROOT no definido")

    # 3.5 rotate sobre directorio no vacio sin --force
    non_empty = _tmp_dir()
    (non_empty / "existe.txt").write_text("x", encoding="utf-8")
    rc, out, err = tr.run([PY, str(script), "rotate", "--new-vault-path", str(non_empty), "--dry-run"])
    tr.expect("3.5", "rotate sobre dir no vacio sin --force falla",
              rc != 0 and "no esta vacia" in (out + err).lower())

    # 3.6 list-archived
    rc, out, _ = tr.run([PY, str(script), "list-archived"])
    tr.expect("3.6", "list-archived exit 0",
              rc == 0 and "INX obsidian:*" in out)

    # 3.7 restore --from ruta inexistente
    rc, out, err = tr.run([PY, str(script), "restore", "--from",
                           "C:/__no_existe__/_fake_vault_", "--dry-run"])
    tr.expect("3.7", "restore --from path inexistente falla",
              rc != 0 and "no existe" in (out + err).lower())

    # 3.8 --depth 1
    tmp2 = _tmp_dir() / "depth1"
    rc, out, _ = tr.run([PY, str(script), "rotate", "--new-vault-path", str(tmp2),
                         "--depth", "1", "--dry-run"])
    m = re.search(r"Estructura:\s*(\d+)\s*dirs replicadas", out)
    dirs_count = int(m.group(1)) if m else -1
    tr.expect("3.8", "--depth 1 replica solo top-level (<=10 dirs)",
              rc == 0 and 0 < dirs_count <= 10, f"dirs={dirs_count}")

    # 3.9 default depth (3) en rango razonable
    tmp3 = _tmp_dir() / "depth3"
    rc, out, _ = tr.run([PY, str(script), "rotate", "--new-vault-path", str(tmp3), "--dry-run"])
    m = re.search(r"Estructura:\s*(\d+)\s*dirs replicadas", out)
    dirs_count = int(m.group(1)) if m else -1
    tr.expect("3.9", "--depth 3 (default) replica 10-500 dirs",
              rc == 0 and 10 <= dirs_count <= 500, f"dirs={dirs_count}")


# ==================== Fase 4: reset_all ====================


def fase_all(tr: TestRunner) -> None:
    script = TOOLS / "reset_all.py"

    # 4.1 help
    rc, out, _ = tr.run([PY, str(script), "--help"])
    tr.expect("4.1", "reset_all.py --help exit 0",
              rc == 0 and "usage:" in out)

    # 4.2 dry-run + límites, sin Obsidian path (Obsidian debe skipear)
    rc, out, _ = tr.run([PY, str(script), "--dry-run", "--mar-limit", "1", "--notion-limit", "1"])
    has_mar_ok = "[OK]   MAR" in out
    has_notion_ok = "[OK]   Notion" in out
    has_obs_skip = "[skip] Obsidian" in out
    tr.expect("4.2", "dry-run sin Obsidian path: [OK] MAR, [OK] Notion, [skip] Obsidian",
              rc == 0 and has_mar_ok and has_notion_ok and has_obs_skip)

    # 4.3 dry-run con Obsidian path → las 3 fases [OK]
    tmp = _tmp_dir() / "all-phases"
    rc, out, _ = tr.run([PY, str(script), "--dry-run",
                         "--mar-limit", "1", "--notion-limit", "1",
                         "--obsidian-new-vault-path", str(tmp)], timeout=180)
    ok = all(f"[OK]   {p}" in out for p in ("MAR", "Notion", "Obsidian"))
    tr.expect("4.3", "dry-run con Obsidian path: 3 fases [OK]",
              rc == 0 and ok)

    # 4.4 skip mar y obsidian
    rc, out, _ = tr.run([PY, str(script), "--dry-run",
                         "--skip-mar", "--skip-obsidian", "--notion-limit", "1"])
    has_mar_skip = "[skip] MAR" in out
    has_obs_skip = "[skip] Obsidian" in out
    has_notion_ok = "[OK]   Notion" in out
    tr.expect("4.4", "--skip-mar --skip-obsidian solo corre Notion",
              rc == 0 and has_mar_skip and has_obs_skip and has_notion_ok)

    # 4.5 limits se propagan — verificacion indirecta via output
    rc, out, _ = tr.run([PY, str(script), "--dry-run", "--mar-limit", "3"])
    tr.expect("4.5", "--mar-limit 3 se propaga al subproceso MAR",
              rc == 0 and "--limit 3" in out and "reset_mar.py" in out)

    # 4.6 y 4.7 manuales
    tr.skip("4.6", "prompt interactivo sin --yes", "no automatizable sin stdin stubbing")
    tr.skip("4.7", "abort-on-fail simulando fallo de fase", "requiere mock de env invalida")


# ==================== Cross-phase ====================


def fase_cross(tr: TestRunner) -> None:
    # C.1 syntax de los 5 scripts
    errors: list[str] = []
    for rel in ["tools/reset_mar.py", "tools/ensure_archivo_field.py",
                "tools/reset_notion.py", "tools/reset_obsidian.py", "tools/reset_all.py"]:
        try:
            py_compile.compile(str(_ROOT / rel), doraise=True)
        except Exception as exc:
            errors.append(f"{rel}: {exc}")
    tr.expect("C.1", "py_compile sin errores en los 5 scripts reset",
              not errors, "; ".join(errors))

    # C.2 memory_check OK
    rc, out, _ = tr.run([PY, str(TOOLS / "memory_check.py")])
    tr.expect("C.2", "memory_check.py OK",
              rc == 0 and "memory/ OK" in out)

    # C.3 INX count invariante (antes/despues del resto de tests ya ejecutados)
    # Aproximacion: solo contamos una vez y verificamos que query responde.
    try:
        from tools.notion_tools import query_data_source
        db_id = _read_env("NOTION_DB_INX")
        if db_id:
            rows = query_data_source(db_id)
            tr.expect("C.3", f"query_data_source(NOTION_DB_INX) accesible (rows={len(rows)})",
                      len(rows) >= 0)
        else:
            tr.skip("C.3", "INX accesible", "NOTION_DB_INX no definido")
    except Exception as exc:
        tr.expect("C.3", "query_data_source(NOTION_DB_INX) accesible",
                  False, str(exc))

    # C.4 nodos reset en pipeline_gui
    gui_src = (_ROOT / "apps" / "pipeline_gui.py").read_text(encoding="utf-8")
    required_keys = {"reset_all", "reset_obsidian", "reset_notion", "reset_mar"}
    missing = {k for k in required_keys if f'key="{k}"' not in gui_src}
    tr.expect("C.4", "4 nodos reset_* presentes en apps/pipeline_gui.py _build_atlas()",
              not missing, f"missing={missing}" if missing else "")


# ==================== runner ====================


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--only", help="Filtrar por prefijo de test id (ej. '2.' o 'C.')")
    args = parser.parse_args()

    tr = TestRunner(verbose=args.verbose)

    phases = [
        ("Fase 1 — MAR",       fase_mar),
        ("Fase 2 — Notion",    fase_notion),
        ("Fase 3 — Obsidian",  fase_obsidian),
        ("Fase 4 — reset_all", fase_all),
        ("Cross-phase",        fase_cross),
    ]
    for title, fn in phases:
        print(f"\n== {title} ==")
        try:
            fn(tr)
        except Exception as exc:
            tr.expect(f"{title}!", f"{title} crashed: {exc}", False, str(exc))
        # Imprime resultados de esta fase inmediatamente
        for r in [x for x in tr.results if x.id.startswith(title.split(" ")[1][:1])] if False else []:
            pass

    # Output tabular
    print()
    print("=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    filtered = [r for r in tr.results if (not args.only or r.id.startswith(args.only))]
    passed = sum(1 for r in filtered if r.passed and not r.skipped)
    failed = sum(1 for r in filtered if not r.passed)
    skipped = sum(1 for r in filtered if r.skipped)
    for r in filtered:
        if r.skipped:
            mark = "[skip]"
        elif r.passed:
            mark = "[PASS]"
        else:
            mark = "[FAIL]"
        extra = f" — {r.detail}" if r.detail else ""
        print(f"  {mark} {r.id:<5} {r.label}{extra}")

    print()
    print(f"Total: {len(filtered)}   PASS: {passed}   FAIL: {failed}   SKIP: {skipped}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
