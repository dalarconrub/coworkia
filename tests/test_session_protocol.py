from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_session_protocol_start_no_chat_reports_context():
    result = subprocess.run(
        [sys.executable, "tools/session_protocol.py", "inicia", "--no-chat"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "# Inicio De Sesion Coworkia" in result.stdout
    assert "## Estado Git" in result.stdout
    assert "## Devlog Reciente" in result.stdout


def test_session_protocol_close_no_chat_no_commit_reports_inventory():
    result = subprocess.run(
        [sys.executable, "tools/session_protocol.py", "cierra", "--no-chat", "--no-commit"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "# Cierre De Sesion Coworkia" in result.stdout
    assert "Sin commit/push" in result.stdout
