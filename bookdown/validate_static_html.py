from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
CONFIG = ROOT / "_bookdown.yml"
HTML_FILE = ROOT / "_book" / "index.html"
PROJECT_RELATIVE_PREFIXES = {
    ".claude/",
    ".github/",
    "AGENTS.md",
    "CLAUDE.md",
    "INICIAR_COWORKIA.bat",
    "README.md",
    "Sistemas/",
    "WINDOWS_START.md",
    "agents/",
    "apps/",
    "artifacts/",
    "bookdown/",
    "chats/",
    "devlog/",
    "docs/",
    "memory/",
    "multiagents/",
    "playbooks/",
    "tests/",
    "tools/",
}
OPTIONAL_LOCAL_PATHS = {".env"}
ROOT_FILES = {"AGENTS.md", "CLAUDE.md", "INICIAR_COWORKIA.bat", "README.md", "WINDOWS_START.md", ".env.example"}


def load_rmd_files() -> list[str]:
    files: list[str] = []
    in_list = False
    for raw in CONFIG.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("rmd_files:"):
            in_list = True
            continue
        if in_list and line.startswith("  - "):
            files.append(line.split("-", 1)[1].strip().strip('"'))
            continue
        if in_list and line and not line.startswith(" "):
            break
    return files


class AuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.paragraphs: list[str] = []
        self._in_p = False
        self._p_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if "id" in attr and attr["id"]:
            self.ids.append(attr["id"])
        if tag == "a" and attr.get("href"):
            self.hrefs.append(attr["href"] or "")
        if tag == "p":
            self._in_p = True
            self._p_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._in_p:
            self.paragraphs.append("".join(self._p_parts).strip())
            self._in_p = False

    def handle_data(self, data: str) -> None:
        if self._in_p:
            self._p_parts.append(data)


def table_errors(path: Path) -> list[str]:
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index + 1 < len(lines):
        current = lines[index].strip()
        separator = lines[index + 1].strip()
        if current.startswith("|") and re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$", separator):
            expected = len(current.strip("|").split("|"))
            row = index + 2
            while row < len(lines) and lines[row].strip().startswith("|"):
                actual = len(lines[row].strip().strip("|").split("|"))
                if actual != expected:
                    errors.append(f"{path.name}:{row + 1} table has {actual} cells, expected {expected}")
                row += 1
            index = row
            continue
        index += 1
    return errors


def is_external_href(href: str) -> bool:
    normalized = href.strip().lower()
    return normalized.startswith(("http://", "https://", "mailto:", "tel:", "#"))


def local_href_target(href: str) -> Path | None:
    if not href or is_external_href(href):
        return None
    split = urlsplit(href)
    if split.scheme or split.netloc:
        return None
    path_text = unquote(split.path).replace("\\", "/").strip()
    if not path_text:
        return None
    if path_text.startswith("/"):
        return Path(path_text)
    if path_text.startswith("../"):
        return (ROOT / path_text).resolve()
    if any(path_text == prefix.rstrip("/") or path_text.startswith(prefix) for prefix in PROJECT_RELATIVE_PREFIXES):
        return (PROJECT_ROOT / path_text).resolve()
    return (ROOT / path_text).resolve()


def local_href_errors(hrefs: list[str]) -> list[str]:
    errors: list[str] = []
    for href in hrefs:
        target = local_href_target(href)
        if target is not None and not target.exists():
            errors.append(f"Broken local link: {href} -> {target}")
    return errors


def looks_like_project_path(text: str) -> bool:
    normalized = text.replace("\\", "/").strip()
    if not normalized or normalized in OPTIONAL_LOCAL_PATHS:
        return False
    if any(token in normalized for token in ("*", "<", ">", "{", "}", "|", "...", "YYYY")):
        return False
    if re.search(r"\s", normalized):
        return False
    if ":" in normalized:
        return False
    return (
        normalized in ROOT_FILES
        or normalized.startswith("../")
        or normalized.startswith(".claude/")
        or normalized.startswith(".github/")
        or any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in PROJECT_RELATIVE_PREFIXES)
    )


def source_code_span_path_target(text: str) -> Path | None:
    normalized = text.strip().rstrip(".,;:").replace("\\", "/")
    if not looks_like_project_path(normalized):
        return None
    if normalized in ROOT_FILES:
        return (PROJECT_ROOT / normalized).resolve()
    if normalized.startswith("/"):
        return Path(normalized)
    if normalized.startswith("../"):
        return (ROOT / normalized).resolve()
    if any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in PROJECT_RELATIVE_PREFIXES):
        return (PROJECT_ROOT / normalized).resolve()
    return (ROOT / normalized).resolve()


def source_path_errors(path: Path) -> list[str]:
    errors: list[str] = []
    in_fence = False
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in re.finditer(r"(?<!`)`([^`\n]+)`(?!`)", raw_line):
            value = match.group(1)
            target = source_code_span_path_target(value)
            if target is not None and not target.exists():
                errors.append(f"{path.name}:{line_number} missing referenced path `{value}` -> {target}")
    return errors


def validate() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not CONFIG.exists():
        errors.append("Missing bookdown/_bookdown.yml")
        return report(errors, warnings)
    chapters = load_rmd_files()
    if not chapters:
        errors.append("No rmd_files declared in _bookdown.yml")
    for chapter in chapters:
        path = ROOT / chapter
        if not path.exists():
            errors.append(f"Missing chapter declared in _bookdown.yml: {chapter}")
        else:
            errors.extend(table_errors(path))
            errors.extend(source_path_errors(path))
    if not HTML_FILE.exists():
        errors.append("Missing generated HTML: bookdown/_book/index.html")
        return report(errors, warnings)
    html_text = HTML_FILE.read_text(encoding="utf-8")
    parser = AuditParser()
    parser.feed(html_text)
    for paragraph in parser.paragraphs:
        if paragraph.startswith("|"):
            errors.append("Raw Markdown table rendered as paragraph")
        if re.search(r"\[[^\]]+\]\([^)]+\)", paragraph):
            errors.append(f"Raw Markdown link rendered as text: {paragraph[:80]}")
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in parser.ids:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    if duplicates:
        errors.append("Duplicate HTML ids: " + ", ".join(sorted(duplicates)))
    for href in parser.hrefs:
        if href.startswith("#") and href[1:] not in seen:
            errors.append(f"Broken internal anchor: {href}")
    errors.extend(local_href_errors(parser.hrefs))
    if "cdn.jsdelivr.net/npm/mermaid" in html_text:
        warnings.append("Mermaid rendering uses CDN; diagrams are visible only with network access.")
    return report(errors, warnings)


def report(errors: list[str], warnings: list[str]) -> int:
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Bookdown validation OK")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
