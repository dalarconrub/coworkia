from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "_bookdown.yml"
OUT_DIR = ROOT / "_book"
OUT_FILE = OUT_DIR / "index.html"


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
    if not files:
        raise RuntimeError("No rmd_files entries found in _bookdown.yml")
    return files


def slugify(text: str, used: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    base = base or "section"
    candidate = base
    index = 2
    while candidate in used:
        candidate = f"{base}-{index}"
        index += 1
    used.add(candidate)
    return candidate


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def is_table_start(lines: list[str], pos: int) -> bool:
    return (
        pos + 1 < len(lines)
        and lines[pos].lstrip().startswith("|")
        and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[pos + 1])
        is not None
    )


def split_table_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def render_table(lines: list[str], pos: int) -> tuple[str, int]:
    header = split_table_row(lines[pos])
    body_pos = pos + 2
    rows: list[list[str]] = []
    while body_pos < len(lines) and lines[body_pos].lstrip().startswith("|"):
        rows.append(split_table_row(lines[body_pos]))
        body_pos += 1
    parts = ["<table>", "<thead><tr>"]
    parts.extend(f"<th>{inline_markup(cell)}</th>" for cell in header)
    parts.append("</tr></thead>")
    parts.append("<tbody>")
    for row in rows:
        parts.append("<tr>")
        parts.extend(f"<td>{inline_markup(cell)}</td>" for cell in row)
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "\n".join(parts), body_pos


def render_markdown(text: str) -> tuple[str, list[tuple[str, str]]]:
    lines = text.splitlines()
    used_ids: set[str] = set()
    toc: list[tuple[str, str]] = []
    out: list[str] = []
    pos = 0
    in_code = False
    code_lang = ""
    code_buffer: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while pos < len(lines):
        line = lines[pos]
        if line.startswith("```"):
            if in_code:
                css_class = "mermaid" if code_lang == "mermaid" else f"language-{html.escape(code_lang)}"
                tag = "div" if code_lang == "mermaid" else "code"
                if code_lang == "mermaid":
                    out.append(f'<div class="{css_class}">{html.escape(chr(10).join(code_buffer))}</div>')
                else:
                    out.append(f'<pre><{tag} class="{css_class}">{html.escape(chr(10).join(code_buffer))}</{tag}></pre>')
                in_code = False
                code_buffer = []
                code_lang = ""
            else:
                close_list()
                in_code = True
                code_lang = line.strip().strip("`").strip()
            pos += 1
            continue
        if in_code:
            code_buffer.append(line)
            pos += 1
            continue
        if not line.strip():
            close_list()
            pos += 1
            continue
        if is_table_start(lines, pos):
            close_list()
            table_html, pos = render_table(lines, pos)
            out.append(table_html)
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            close_list()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = slugify(re.sub(r"`([^`]+)`", r"\1", title), used_ids)
            out.append(f'<h{level} id="{anchor}">{inline_markup(title)}</h{level}>')
            if level <= 2:
                toc.append((title, anchor))
            pos += 1
            continue
        item = re.match(r"^-\s+(.+)$", line)
        if item:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline_markup(item.group(1))}</li>")
            pos += 1
            continue
        close_list()
        out.append(f"<p>{inline_markup(line.strip())}</p>")
        pos += 1

    close_list()
    return "\n".join(out), toc


def build() -> None:
    chapters = load_rmd_files()
    combined: list[str] = []
    for chapter in chapters:
        path = ROOT / chapter
        if not path.exists():
            raise FileNotFoundError(path)
        combined.append(path.read_text(encoding="utf-8"))
    body, toc = render_markdown("\n\n".join(combined))
    toc_html = "\n".join(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>' for title, anchor in toc)
    page = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coworkia Manual</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; line-height: 1.55; color: #202124; background: #f7f7f5; }}
    .layout {{ display: grid; grid-template-columns: minmax(220px, 280px) minmax(0, 1fr); min-height: 100vh; }}
    nav {{ position: sticky; top: 0; height: 100vh; overflow: auto; padding: 24px; background: #17202a; color: white; }}
    nav a {{ color: #d8e9ff; text-decoration: none; }}
    nav li {{ margin: 0 0 8px; }}
    main {{ max-width: 980px; padding: 32px 40px 80px; background: white; }}
    h1, h2, h3 {{ line-height: 1.2; }}
    h1 {{ margin-top: 32px; border-bottom: 1px solid #ddd; padding-bottom: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 24px; font-size: 0.95rem; }}
    th, td {{ border: 1px solid #d8d8d8; padding: 8px 10px; vertical-align: top; }}
    th {{ background: #eef2f4; text-align: left; }}
    code {{ background: #f1f3f4; padding: 1px 4px; border-radius: 3px; }}
    pre {{ background: #111827; color: #f9fafb; padding: 16px; overflow: auto; border-radius: 6px; }}
    pre code {{ background: transparent; color: inherit; padding: 0; }}
    .mermaid {{ margin: 16px 0; padding: 16px; background: #f8fafc; border: 1px solid #d8dee4; border-radius: 6px; overflow: auto; }}
    @media (max-width: 860px) {{ .layout {{ display: block; }} nav {{ position: static; height: auto; }} main {{ padding: 24px 18px 60px; }} }}
  </style>
  <script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs'; mermaid.initialize({{ startOnLoad: true }});</script>
</head>
<body>
  <div class="layout">
    <nav>
      <h2>Coworkia</h2>
      <ol>{toc_html}</ol>
    </nav>
    <main>{body}</main>
  </div>
</body>
</html>
"""
    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_text(page, encoding="utf-8")
    print(f"Generated {OUT_FILE}")


if __name__ == "__main__":
    build()
