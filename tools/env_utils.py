"""
Carga ligera de `.env` con fallback cuando `python-dotenv` no esta instalado.

Reglas:
  - Si `python-dotenv` existe, delega en ese paquete.
  - Si no, parsea `.env` localmente sin sobrescribir variables ya definidas.
  - Soporta lineas `KEY=VALUE`, comillas simples/dobles y prefijo opcional
    `export `.
"""

from __future__ import annotations

import os
from pathlib import Path


def _strip_wrapping_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_env_file(env_path: Path, override: bool = False) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue

        value = _strip_wrapping_quotes(value.strip())
        if override or key not in os.environ:
            os.environ[key] = value


def load_project_env(env_path: str | Path | None = None, override: bool = False) -> None:
    target = Path(env_path) if env_path is not None else Path(".env")
    if not target.is_absolute():
        target = Path.cwd() / target

    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(target, override=override)
        return
    except Exception:
        pass

    _parse_env_file(target, override=override)
