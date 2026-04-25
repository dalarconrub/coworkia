from pathlib import Path
import importlib.util
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def load_validator_module():
    module_path = ROOT / "bookdown" / "validate_static_html.py"
    spec = importlib.util.spec_from_file_location("bookdown_validate_static_html", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bookdown_static_html_generates_and_validates():
    generate = subprocess.run(
        [sys.executable, "bookdown/generate_static_html.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert generate.returncode == 0, generate.stdout + generate.stderr

    validate = subprocess.run(
        [sys.executable, "bookdown/validate_static_html.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert validate.returncode == 0, validate.stdout + validate.stderr

    html = (ROOT / "bookdown" / "_book" / "index.html").read_text(encoding="utf-8")
    assert "<table>" in html
    assert "<p>|" not in html
    assert "[memory/INDEX.md](" not in html


def test_bookdown_validator_rejects_missing_local_link():
    validator = load_validator_module()

    errors = validator.local_href_errors(["docs/no-existe-en-coworkia.md"])

    assert errors
    assert "Broken local link" in errors[0]


def test_bookdown_validator_rejects_missing_backticked_project_path(tmp_path):
    validator = load_validator_module()
    source = tmp_path / "chapter.Rmd"
    source.write_text("Path inexistente: `docs/no-existe-en-coworkia.md`\n", encoding="utf-8")

    errors = validator.source_path_errors(source)

    assert errors
    assert "missing referenced path" in errors[0]
