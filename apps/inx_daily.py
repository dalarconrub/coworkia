"""
Rutina diaria INX: ejecuta sync completo, pasa el doctor y guarda un informe en artifacts/inx.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts" / "inx"


def _run_step(label: str, cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    lines = [f"## {label}", "", f"Command: `{' '.join(cmd)}`", ""]
    if proc.stdout.strip():
        lines.extend(["### stdout", "", "```text", proc.stdout.rstrip(), "```", ""])
    if proc.stderr.strip():
        lines.extend(["### stderr", "", "```text", proc.stderr.rstrip(), "```", ""])
    lines.append(f"Exit code: {proc.returncode}")
    lines.append("")
    return proc.returncode, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run daily INX sync and store a report artifact")
    parser.add_argument("--limit", type=int, default=200, help="Límite para la sincronización enumerada")
    parser.add_argument("--allow-missing-ptn", action="store_true", help="No fallar si el doctor detecta filas sin PTN")
    args = parser.parse_args(argv)

    python = sys.executable
    sync_cmd = [python, "agents/orchestrator_agent.py", "inx-sync", "--limit", str(args.limit)]
    doctor_cmd = [python, "apps/inx_doctor.py", "--max", "25"]
    if args.allow_missing_ptn:
        doctor_cmd.append("--allow-missing-ptn")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACTS_DIR / f"inx-daily-{timestamp}.md"

    sync_code, sync_report = _run_step("Sync", sync_cmd)
    doctor_code, doctor_report = _run_step("Doctor", doctor_cmd)

    report = [
        "# INX Daily Report",
        "",
        f"- Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"- Sync exit code: {sync_code}",
        f"- Doctor exit code: {doctor_code}",
        "",
        sync_report,
        doctor_report,
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")

    print(f"Informe guardado en: {report_path}")
    print(f"sync={sync_code} doctor={doctor_code}")

    if sync_code != 0:
        return sync_code
    return doctor_code


if __name__ == "__main__":
    raise SystemExit(main())
