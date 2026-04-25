"""
Protocolo local de inicio/cierre de sesion para Coworkia.

Adapta `playbooks/PROTOCOLO_INICIO_CIERRE_SESION.md` a la infraestructura
existente del repo: memoria versionada, chat diario, devlog y estado Git.

Uso:
    python tools/session_protocol.py inicia
    python tools/session_protocol.py cierra
    python tools/session_protocol.py cierra --paths bookdown tests --commit-message "Document bookdown"
    python tools/session_protocol.py cierra --paths bookdown tests --commit-message "Document bookdown" --push
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = ROOT / "memory"
DEVLOG_PATH = ROOT / "devlog" / "DEVLOG.md"
PLAYBOOK_PATH = ROOT / "playbooks" / "PROTOCOLO_INICIO_CIERRE_SESION.md"
CHAT_TEMPLATE = "chats/chat_{day}.md"


@dataclass
class CmdResult:
    cmd: list[str]
    returncode: int
    stdout: str
    stderr: str


def run(cmd: list[str]) -> CmdResult:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
    return CmdResult(cmd=cmd, returncode=proc.returncode, stdout=proc.stdout.strip(), stderr=proc.stderr.strip())


def git_output(*args: str) -> str:
    result = run(["git", *args])
    output = result.stdout or result.stderr
    if result.returncode != 0:
        return f"(ERROR {' '.join(result.cmd)}: {output})"
    return output or "(sin salida)"


def ensure_chat() -> Path:
    result = run([sys.executable, "tools/init_chat.py", "--quiet"])
    if result.returncode != 0:
        raise SystemExit(result.stderr or result.stdout or "No se pudo resolver el chat activo")
    return Path(result.stdout.strip())


def append_chat(agent: str, message: str) -> None:
    chat_path = ensure_chat()
    line = f"\n**{agent}:** {message}\n"
    with chat_path.open("a", encoding="utf-8", newline="") as handle:
        handle.write(line)


def root_listing(limit: int = 80) -> list[str]:
    names = sorted(p.name + ("/" if p.is_dir() else "") for p in ROOT.iterdir())
    if len(names) > limit:
        return names[:limit] + [f"... ({len(names) - limit} mas)"]
    return names


def existing(paths: list[str]) -> list[str]:
    found: list[str] = []
    for item in paths:
        if (ROOT / item).exists():
            found.append(item)
    return found


def devlog_tail(limit: int = 5) -> str:
    result = run([sys.executable, "tools/devlog.py", "view", "--limit", str(limit)])
    return result.stdout if result.returncode == 0 else result.stderr


def render_start() -> str:
    chat_path = ensure_chat()
    status = git_output("status", "--short", "--branch")
    branch = git_output("branch", "--show-current")
    last_commit = git_output("log", "-1", "--oneline")
    remotes = git_output("remote", "-v")
    diff_stat = git_output("diff", "--stat")
    diff_names = git_output("diff", "--name-only")
    tracked_docs = existing(
        [
            "AGENTS.md",
            "CLAUDE.md",
            ".github/copilot-instructions.md",
            ".claude/multiagent.md",
            "README.md",
            "memory/INDEX.md",
            "memory/PURPOSE.md",
            "memory/STRUCTURE.md",
            "memory/SNAPSHOT.md",
            "devlog/DEVLOG.md",
            "docs/",
            "bookdown/",
            "playbooks/",
            "artifacts/sprints/",
            "artifacts/multiagent/",
        ]
    )
    manifests = existing(["requirements.txt", ".env.example", "pyproject.toml", "package.json", "Makefile"])

    lines = [
        "# Inicio De Sesion Coworkia",
        "",
        f"- Chat activo: `{chat_path}`",
        f"- Rama: `{branch}`",
        f"- Ultimo commit: `{last_commit}`",
        "",
        "## Estado Git",
        "",
        "```text",
        status,
        "```",
        "",
        "## Cambios Pendientes",
        "",
        "```text",
        diff_stat,
        "```",
        "",
        "## Archivos Modificados",
        "",
        "```text",
        diff_names,
        "```",
        "",
        "## Mapa Minimo",
        "",
        ", ".join(root_listing()),
        "",
        "## Recursos Consultados",
        "",
        "\n".join(f"- `{item}`" for item in tracked_docs),
        "",
        "## Manifiestos Detectados",
        "",
        "\n".join(f"- `{item}`" for item in manifests) or "- (ninguno)",
        "",
        "## Remotos",
        "",
        "```text",
        remotes,
        "```",
        "",
        "## Devlog Reciente",
        "",
        devlog_tail(5),
        "",
        "## Siguiente Paso Probable",
        "",
        "Continuar desde los cambios pendientes del arbol Git; no revertir nada sin permiso.",
    ]
    return "\n".join(lines)


def render_close(commit_message: str = "", paths: list[str] | None = None, push: bool = False) -> tuple[str, list[str]]:
    actions: list[str] = []
    paths = paths or []
    before = git_output("status", "--short", "--branch")
    diff_stat = git_output("diff", "--stat")

    if commit_message:
        if not paths:
            actions.append("Commit no ejecutado: `--commit-message` requiere `--paths` para evitar incluir cambios ajenos.")
        else:
            add = run(["git", "add", *paths])
            actions.append(f"git add {' '.join(paths)} -> rc={add.returncode}")
            if add.returncode == 0:
                commit = run(["git", "commit", "-m", commit_message])
                actions.append((commit.stdout or commit.stderr or "git commit sin salida").strip())
                if commit.returncode == 0 and push:
                    push_result = run(["git", "push"])
                    actions.append((push_result.stdout or push_result.stderr or "git push sin salida").strip())
            else:
                actions.append(add.stderr or add.stdout)
    elif push:
        actions.append("Push no ejecutado: `--push` solo se permite junto a `--commit-message`.")

    after = git_output("status", "--short", "--branch")
    last_commit = git_output("log", "-1", "--oneline")
    branch = git_output("branch", "--show-current")

    lines = [
        "# Cierre De Sesion Coworkia",
        "",
        f"- Rama: `{branch}`",
        f"- Ultimo commit: `{last_commit}`",
        "",
        "## Estado Inicial Del Cierre",
        "",
        "```text",
        before,
        "```",
        "",
        "## Diff Pendiente",
        "",
        "```text",
        diff_stat,
        "```",
        "",
        "## Acciones De Git",
        "",
        "\n".join(f"- {item}" for item in actions) if actions else "- Sin commit/push: no se pidio `--commit-message`.",
        "",
        "## Estado Final",
        "",
        "```text",
        after,
        "```",
        "",
        "## Pendiente Para Proxima Sesion",
        "",
        "Revisar cambios que sigan en `git status`; si pertenecen a la sesion, preparar commit selectivo.",
    ]
    return "\n".join(lines), actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    ap_start = sub.add_parser("inicia", aliases=["start"], help="Recupera contexto de sesion")
    ap_start.add_argument("--agent", default="Codex", help="Firma para append en chat; usa --no-chat para desactivar")
    ap_start.add_argument("--no-chat", action="store_true", help="No anadir resumen al chat diario")

    ap_close = sub.add_parser("cierra", aliases=["close"], help="Inventario de cierre de sesion")
    ap_close.add_argument("--agent", default="Codex", help="Firma para append en chat; usa --no-chat para desactivar")
    ap_close.add_argument("--no-chat", action="store_true", help="No anadir resumen al chat diario")
    ap_close.add_argument("--paths", nargs="*", default=[], help="Rutas concretas a preparar si hay commit")
    ap_close.add_argument("--commit-message", default="", help="Mensaje de commit; requiere --paths")
    ap_close.add_argument("--push", action="store_true", help="Ejecuta git push tras commit correcto")

    args = parser.parse_args()

    if not PLAYBOOK_PATH.exists():
        raise SystemExit(f"No existe {PLAYBOOK_PATH}")

    if args.cmd in {"inicia", "start"}:
        report = render_start()
        print(report)
        if not args.no_chat:
            append_chat(args.agent, "Inicio de sesion ejecutado con `python tools/session_protocol.py inicia`; contexto Git, memoria, chat y devlog revisados.")
        return 0

    if args.cmd in {"cierra", "close"}:
        report, _actions = render_close(commit_message=args.commit_message, paths=args.paths, push=args.push)
        print(report)
        if not args.no_chat:
            append_chat(args.agent, "Cierre de sesion ejecutado con `python tools/session_protocol.py cierra`; estado Git inventariado y pendientes visibles para la siguiente sesion.")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
