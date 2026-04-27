"""
Genera un `.env` a partir de un JSON descargado desde 1Password (u otro medio).

Objetivo: automatizar el setup sin pegar tokens manualmente y sin versionarlos en Git.

Formatos soportados:
  1) JSON plano: {"VAR": "valor", ...}
  2) Formato "tipo 1Password item": {"fields": [{"label": "VAR", "value": "valor"}, ...]}

Uso:
  python tools/generate_env_from_json.py --input config/secrets.1p.json --output .env
  python tools/generate_env_from_json.py --input config/secrets.1p.json --output .env --force
  python tools/generate_env_from_json.py --input config/secrets.1p.json --output .env --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_EXAMPLE = ROOT / ".env.example"


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("El JSON debe ser un objeto (dict).")
    return data


def _extract_vars(payload: dict) -> dict[str, str]:
    # 1) JSON plano {"KEY":"VALUE"}
    flat: dict[str, str] = {}
    for k, v in payload.items():
        if k == "_comment":
            continue
        if isinstance(k, str) and isinstance(v, (str, int, float, bool)) and k.isidentifier() is False:
            # isidentifier() no aplica bien a env vars (tienen underscores/números),
            # así que validamos más suave debajo.
            pass
        if isinstance(k, str) and isinstance(v, (str, int, float, bool)):
            flat[k] = str(v)

    if flat:
        return flat

    # 2) Formato fields: [{"label":"X","value":"Y"}]
    fields = payload.get("fields")
    if isinstance(fields, list):
        out: dict[str, str] = {}
        for f in fields:
            if not isinstance(f, dict):
                continue
            label = f.get("label")
            value = f.get("value")
            if isinstance(label, str) and isinstance(value, (str, int, float, bool)):
                out[label] = str(value)
        if out:
            return out

    return {}


def _parse_env_example_keys(example_path: Path) -> list[str]:
    keys: list[str] = []
    if not example_path.exists():
        return keys
    for raw_line in example_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.append(key)
    return keys


def _render_env(keys_in_order: list[str], values: dict[str, str]) -> str:
    lines: list[str] = []
    lines.append("# Coworkia - .env generado automaticamente")
    lines.append(f"# Fecha: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("# Fuente: tools/generate_env_from_json.py")
    lines.append("")

    seen: set[str] = set()
    for key in keys_in_order:
        seen.add(key)
        val = values.get(key, "")
        lines.append(f"{key}={val}")
    # Extras no presentes en .env.example
    extras = sorted(k for k in values.keys() if k not in seen and k != "_comment")
    if extras:
        lines.append("")
        lines.append("# Extras (no estaban en .env.example)")
        for key in extras:
            lines.append(f"{key}={values.get(key,'')}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Ruta al JSON con secretos (NO versionar).")
    ap.add_argument("--output", default=".env", help="Ruta de salida del .env (por defecto .env).")
    ap.add_argument("--force", action="store_true", help="Sobrescribe si ya existe el output.")
    ap.add_argument("--dry-run", action="store_true", help="No escribe; solo imprime un resumen.")
    ap.add_argument("--no-backup", action="store_true", help="No crea backup del .env existente.")
    args = ap.parse_args()

    input_path = (ROOT / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    output_path = (ROOT / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)

    if not input_path.exists():
        print(f"[ERROR] No existe el input: {input_path}", file=sys.stderr)
        return 2

    payload = _load_json(input_path)
    values = _extract_vars(payload)
    if not values:
        print("[ERROR] No se detectaron variables en el JSON (ni plano ni fields[]).", file=sys.stderr)
        return 2

    ordered_keys = _parse_env_example_keys(ENV_EXAMPLE)
    if not ordered_keys:
        # Fallback: orden alfabético
        ordered_keys = sorted(values.keys())

    content = _render_env(ordered_keys, values)

    if args.dry_run:
        print(f"[OK] Input: {input_path}")
        print(f"[OK] Output: {output_path}")
        print(f"[OK] Variables detectadas: {len(values)}")
        print("[OK] No se escribio ningun archivo (--dry-run).")
        return 0

    if output_path.exists() and not args.force:
        print(f"[ERROR] Ya existe {output_path}. Usa --force para sobrescribir.", file=sys.stderr)
        return 3

    if output_path.exists() and not args.no_backup:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = output_path.with_suffix(output_path.suffix + f".bak-{ts}")
        backup.write_text(output_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")

    output_path.write_text(content, encoding="utf-8")
    print(f"[OK] Escrito {output_path} con {len(values)} variables (segun JSON).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

