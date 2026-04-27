"""
Protocolo local de inicio/cierre de sesion para Coworkia.

Adapta `playbooks/PROTOCOLO_INICIO_CIERRE_SESION.md` a la infraestructura
existente del repo: memoria versionada, chat diario, devlog y estado Git.

Uso:
    python tools/session_protocol.py inicia
    python tools/session_protocol.py cierra
    python tools/session_protocol.py cierra --no-commit
    python tools/session_protocol.py cierra --paths bookdown tests --commit-message "Document bookdown"
    python tools/session_protocol.py cierra --paths bookdown tests --commit-message "Document bookdown" --no-push
"""

from __future__ import annotations

import argparse
import os
import shutil
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
OP_ENV_FILE = ROOT / "config" / "env.1password"
OP_ENV_FILE_EXAMPLE = ROOT / "config" / "env.1password.example"


def _op_available() -> bool:
    return shutil.which("op") is not None


def _should_try_op_reexec(argv: list[str]) -> bool:
    # Evita bucles (este flag lo ponemos solo en la re-ejecución).
    if os.environ.get("COWORKIA_OP_REEXEC") == "1":
        return False
    # Solo tiene sentido si el usuario ha creado el env file local.
    if not OP_ENV_FILE.exists():
        return False
    # Si no existe el CLI, no intentamos nada.
    if not _op_available():
        return False
    # Re-ejecutamos para cualquier comando (inicia/cierra); es seguro e idempotente.
    return True


def _reexec_with_op(argv: list[str]) -> int:
    env = dict(os.environ)
    env["COWORKIA_OP_REEXEC"] = "1"
    # Importante: ejecutamos el mismo Python, mismo script y mismos args.
    cmd = ["op", "run", f"--env-file={str(OP_ENV_FILE)}", "--", sys.executable, *argv]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", env=env, capture_output=False, check=False)
    return proc.returncode


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


def git_lines(*args: str) -> list[str]:
    output = git_output(*args)
    if output.startswith("(ERROR") or output == "(sin salida)":
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


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

    env_hints: list[str] = []
    if (ROOT / ".env").exists():
        env_hints.append("- `.env` detectado (local, gitignored).")
    if OP_ENV_FILE.exists():
        env_hints.append("- `config/env.1password` detectado (referencias a 1Password).")
    elif OP_ENV_FILE_EXAMPLE.exists():
        env_hints.append("- `config/env.1password` no existe (usa `config/env.1password.example` como plantilla).")
    if _op_available():
        env_hints.append("- `op` (1Password CLI) disponible en PATH.")
    else:
        env_hints.append("- `op` (1Password CLI) NO detectado en PATH.")

    lines = [
        "# Inicio De Sesion Coworkia",
        "",
        f"- Chat activo: `{chat_path}`",
        f"- Rama: `{branch}`",
        f"- Ultimo commit: `{last_commit}`",
        "",
        "## Entorno (secrets)",
        "",
        "\n".join(env_hints) or "- (sin datos)",
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


def render_close(
    commit_message: str = "",
    paths: list[str] | None = None,
    push: bool = True,
    auto_commit: bool = True,
) -> tuple[str, list[str]]:
    actions: list[str] = []
    paths = paths or []
    before = git_output("status", "--short", "--branch")
    diff_stat = git_output("diff", "--stat")

    if auto_commit and not paths:
        tracked = git_lines("diff", "--name-only")
        untracked = git_lines("ls-files", "--others", "--exclude-standard")
        paths = sorted(set(tracked + untracked))

    if auto_commit and not commit_message:
        commit_message = f"Close session {date.today().isoformat()}"

    if auto_commit and paths:
        add = run(["git", "add", "--", *paths])
        actions.append(f"git add {' '.join(paths)} -> rc={add.returncode}")
        if add.returncode == 0:
            commit = run(["git", "commit", "-m", commit_message])
            actions.append((commit.stdout or commit.stderr or "git commit sin salida").strip())
            if commit.returncode == 0 and push:
                push_result = run(["git", "push"])
                actions.append((push_result.stdout or push_result.stderr or "git push sin salida").strip())
            elif commit.returncode == 0 and not push:
                actions.append("Push omitido por `--no-push`.")
        else:
            actions.append(add.stderr or add.stdout)
    elif auto_commit:
        actions.append("Commit no ejecutado: no hay cambios detectados para preparar.")
    elif commit_message:
        if not paths:
            actions.append("Commit no ejecutado: `--commit-message` requiere `--paths` para evitar incluir cambios ajenos.")
        else:
            add = run(["git", "add", "--", *paths])
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
        actions.append("Push no ejecutado: `--no-commit` impide crear commit.")

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
        "\n".join(f"- {item}" for item in actions) if actions else "- Sin commit/push.",
        "",
        "## Estado Final",
        "",
        "```text",
        after,
        "```",
        "",
        "## Pendiente Para Proxima Sesion",
        "",
        "Revisar cambios que sigan en `git status`; si quedan pendientes, decidir si pertenecen a una sesion futura.",
    ]
    return "\n".join(lines), actions


def main() -> int:
    # Si el usuario preparó 1Password (config/env.1password) re-ejecutamos bajo `op run`
    # para que este protocolo también herede automáticamente el entorno, incluso cuando
    # se ejecuta fuera de los .bat del repo.
    if _should_try_op_reexec(sys.argv[1:]):
        rc = _reexec_with_op(sys.argv[1:])
        if rc == 0:
            return 0
        # Si falla (p. ej. sin `op signin`), seguimos sin abortar: el protocolo de sesión
        # no necesita secretos para imprimir Git/memoria/devlog, pero dejamos el warning.
        print(
            "[WARN] No se pudo ejecutar bajo 1Password CLI (`op run`). "
            "Continuo sin inyeccion de secretos. "
            "Tip: ejecuta `op signin` o revisa `config/env.1password`.",
            file=sys.stderr,
        )

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    ap_start = sub.add_parser("inicia", aliases=["start"], help="Recupera contexto de sesion")
    ap_start.add_argument("--agent", default="Codex", help="Firma para append en chat; usa --no-chat para desactivar")
    ap_start.add_argument("--no-chat", action="store_true", help="No anadir resumen al chat diario")

    ap_close = sub.add_parser("cierra", aliases=["close"], help="Inventario de cierre de sesion")
    ap_close.add_argument("--agent", default="Codex", help="Firma para append en chat; usa --no-chat para desactivar")
    ap_close.add_argument("--no-chat", action="store_true", help="No anadir resumen al chat diario")
    ap_close.add_argument("--paths", nargs="*", default=[], help="Rutas concretas a preparar si hay commit")
    ap_close.add_argument("--commit-message", default="", help="Mensaje de commit; por defecto se genera uno de cierre")
    ap_close.add_argument("--no-commit", action="store_true", help="Solo inventaria cierre; no hace commit")
    ap_close.add_argument("--no-push", action="store_true", help="Hace commit pero no ejecuta git push")

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
        if not args.no_chat:
            append_chat(args.agent, "Cierre de sesion ejecutado con `python tools/session_protocol.py cierra`; estado Git inventariado, validaciones revisadas y commit/push de cierre aplicado segun politica local.")
        report, _actions = render_close(
            commit_message=args.commit_message,
            paths=args.paths,
            push=not args.no_push and not args.no_commit,
            auto_commit=not args.no_commit,
        )
        print(report)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
