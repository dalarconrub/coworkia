"""
Reset Obsidian (Fase 3) — rotar vault construyendo uno nuevo como sibling.

Estrategia C del diseño:
  - El vault viejo queda INTACTO en su path actual (OBSIDIAN_ABGD_ROOT). Sus notas
    siguen siendo leibles; los `obsidian:<path>` del INX mantienen validez fisica.
  - El vault nuevo nace en `--new-vault-path` o, si no se pasa, en el sibling
    derivado automaticamente con la regla `ABGD-yymmdd` bajo la misma raiz del
    vault actual. Ejemplo: `C:/GDrive/.../ABGD/ABGD-260419`.
    Con:
      * Estructura de carpetas canonica replicada desde el viejo hasta `--depth N`
        (default 3: Area -> Bloque -> Contexto). Sin ficheros .md.
      * Carpeta `.obsidian/` completa (plugins, hotkeys, themes, snippets).
  - INX propaga el archivado marcando `Archivo=true` en toda fila cuya `Clave`
    empiece por `obsidian:`. Las vistas con filtro `Archivo != true` las ocultan.
  - El CLI NO edita `.env`. Al terminar imprime la linea que debes reemplazar.

Subcomandos:
  rotate [--new-vault-path PATH] [--depth N] [--dry-run] [--snapshot]
         [--no-inx] [--force]
  status
  list-archived
  restore --from OLD_VAULT_PATH [--dry-run] [--no-inx]

Flags:
  --dry-run      No crea carpetas ni llama a Notion; solo informa.
  --snapshot     Vuelca artifacts/resets/YYYY-MM-DD/obsidian-rotate-<ts>.json.
  --no-inx       Omite el flip INX (solo toca filesystem).
  --force        Permite escribir en la ruta destino aunque ya exista no-vacio.
  --depth N      Profundidad de replica estructural (default 3; -1 = todo).

Ejemplos:
  python tools/reset_obsidian.py status
  python tools/reset_obsidian.py rotate --dry-run --snapshot
  python tools/reset_obsidian.py rotate
  python tools/reset_obsidian.py rotate \
      --new-vault-path C:/GDrive/dalarconrub/ABGD/ABGD-260419
  python tools/reset_obsidian.py list-archived
  python tools/reset_obsidian.py restore --from C:/GDrive/dalarconrub/ABGD/ABGD-25.09.05
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date as Date, datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from tools.env_utils import load_project_env

load_project_env(_ROOT / ".env")

from tools.notion_tools import (  # noqa: E402
    extract_property_value,
    get_data_source_schema,
    query_data_source,
    update_page_properties,
)

ENV_VAULT = "OBSIDIAN_ABGD_ROOT"
ENV_INX = "NOTION_DB_INX"
ARCHIVE_DIR = _ROOT / "artifacts" / "resets"

DEFAULT_DEPTH = 3   # Area -> Bloque -> Contexto. -1 = todo.


# ==================== helpers ====================


def _current_vault() -> Path | None:
    raw = os.getenv(ENV_VAULT)
    return Path(raw) if raw else None


def _derived_new_vault_path(old: Path) -> Path:
    stamp = Date.today().strftime("%y%m%d")
    return (old.resolve().parent / f"ABGD-{stamp}").resolve()


def _inx_id() -> str:
    v = os.getenv(ENV_INX)
    if not v:
        raise SystemExit(f"Variable {ENV_INX} no definida en .env")
    return v


def _ensure_inx_archivo() -> None:
    schema = get_data_source_schema(_inx_id())
    if "Archivo" not in schema.get("properties", []):
        raise SystemExit(
            "La propiedad 'Archivo' no existe en NOTION_DB_INX. "
            "Ejecuta: python tools/ensure_archivo_field.py"
        )


def _is_path_empty(path: Path) -> bool:
    return not path.exists() or not any(path.iterdir())


# ==================== structure mirror ====================


@dataclass
class MirrorStats:
    dirs_created: list[str] = field(default_factory=list)
    dirs_skipped: list[str] = field(default_factory=list)
    obsidian_copied: bool = False
    obsidian_size_bytes: int = 0


def _mirror_structure(
    src: Path,
    dst: Path,
    depth_limit: int,
    dry_run: bool,
) -> MirrorStats:
    """Recrea la estructura de subdirectorios de src en dst.

    - depth_limit >= 0 limita a esa profundidad (1 = solo top-level).
    - depth_limit < 0 sin limite.
    - Excluye `.obsidian` (se copia aparte en _copy_obsidian_config).
    - No copia ficheros.
    """
    stats = MirrorStats()
    if not src.exists():
        raise SystemExit(f"Vault origen no existe: {src}")

    if not dry_run:
        dst.mkdir(parents=True, exist_ok=True)

    for root, dirs, _files in os.walk(src):
        rel = Path(root).relative_to(src)
        if rel == Path("."):
            # Filtrar subdirs al recorrer
            dirs[:] = [d for d in dirs if d != ".obsidian"]
            continue
        parts = rel.parts
        # skip anything under .obsidian
        if parts[0] == ".obsidian":
            dirs[:] = []
            continue
        depth = len(parts)
        if depth_limit >= 0 and depth > depth_limit:
            stats.dirs_skipped.append(str(rel).replace("\\", "/"))
            dirs[:] = []  # no descender
            continue
        target = dst / rel
        if dry_run:
            stats.dirs_created.append(str(rel).replace("\\", "/"))
        else:
            target.mkdir(parents=True, exist_ok=True)
            stats.dirs_created.append(str(rel).replace("\\", "/"))

    return stats


def _copy_obsidian_config(src: Path, dst: Path, dry_run: bool) -> tuple[bool, int]:
    """Copia src/.obsidian -> dst/.obsidian integra. Devuelve (copied, size_bytes)."""
    src_cfg = src / ".obsidian"
    if not src_cfg.exists() or not src_cfg.is_dir():
        return False, 0
    size_bytes = sum(
        f.stat().st_size for f in src_cfg.rglob("*") if f.is_file()
    )
    dst_cfg = dst / ".obsidian"
    if not dry_run:
        if dst_cfg.exists():
            shutil.rmtree(dst_cfg)
        shutil.copytree(src_cfg, dst_cfg)
    return True, size_bytes


# ==================== INX flip ====================


@dataclass
class InxFlipStats:
    target_value: bool
    checked: int = 0
    flipped: int = 0
    already: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)


def _flip_obsidian_inx(new_value: bool, dry_run: bool) -> InxFlipStats:
    _ensure_inx_archivo()
    db_id = _inx_id()
    stats = InxFlipStats(target_value=new_value)
    rows = query_data_source(db_id)
    for r in rows:
        props = r.get("properties", {}) or {}
        key = extract_property_value(props.get("Clave", {}))
        if not key or not key.startswith("obsidian:"):
            continue
        stats.checked += 1
        current = False
        a_prop = props.get("Archivo", {})
        if isinstance(a_prop, dict) and a_prop.get("type") == "checkbox":
            current = bool(a_prop.get("checkbox"))
        if current == new_value:
            stats.already += 1
            continue
        if dry_run:
            stats.flipped += 1
            continue
        try:
            update_page_properties(r["id"], {"Archivo": {"checkbox": new_value}})
            stats.flipped += 1
        except Exception as exc:
            stats.errors.append((r["id"], str(exc)))
    return stats


# ==================== snapshot ====================


def _write_snapshot(op: str, payload: dict) -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    day = ARCHIVE_DIR / Date.today().isoformat()
    day.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%H%M%SZ")
    out = day / f"obsidian-{op}-{ts}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


# ==================== subcomandos ====================


def cmd_status(_args) -> int:
    vault = _current_vault()
    print(f"{ENV_VAULT}: {vault}")
    if vault is None:
        print("  (sin definir)")
        return 0
    if not vault.exists():
        print("  (ruta no existe en disco)")
        return 1
    top = sorted([p.name for p in vault.iterdir()])
    print(f"  existe: True")
    print(f"  top-level ({len(top)}): {', '.join(top[:20])}")
    cfg = vault / ".obsidian"
    print(f"  .obsidian: {'si' if cfg.exists() else 'no'}")
    try:
        inx_schema = get_data_source_schema(_inx_id())
        has = "Archivo" in inx_schema.get("properties", [])
        print(f"NOTION_DB_INX.Archivo: {'presente' if has else 'AUSENTE — ejecuta ensure_archivo_field.py'}")
    except Exception as exc:
        print(f"NOTION_DB_INX: no accesible ({exc})")
    return 0


def cmd_rotate(args) -> int:
    old = _current_vault()
    if old is None:
        raise SystemExit(f"{ENV_VAULT} no definida en .env")
    if not old.exists():
        raise SystemExit(f"Vault actual no existe: {old}")
    new = Path(args.new_vault_path).resolve() if args.new_vault_path else _derived_new_vault_path(old)
    if new == old.resolve():
        raise SystemExit("La ruta destino derivada no puede coincidir con el vault actual; usa --new-vault-path para override")
    if new.exists() and not _is_path_empty(new) and not args.force:
        raise SystemExit(
            f"--new-vault-path ya existe y no esta vacia: {new}\n"
            "Pasa --force para escribir encima (riesgo: sobrescribe estructura existente)."
        )

    print(f"Vault actual   : {old}")
    print(f"Vault nuevo    : {new}")
    print(f"Ruta derivada  : {not bool(args.new_vault_path)}")
    print(f"Profundidad    : {'sin limite' if args.depth < 0 else args.depth}")
    print(f"Dry-run        : {args.dry_run}")
    print()

    mstats = _mirror_structure(old, new, args.depth, args.dry_run)
    print(f"Estructura: {len(mstats.dirs_created)} dirs replicadas"
          f" (skipped por profundidad: {len(mstats.dirs_skipped)})")

    obsidian_copied, obsidian_size = _copy_obsidian_config(old, new, args.dry_run)
    mstats.obsidian_copied = obsidian_copied
    mstats.obsidian_size_bytes = obsidian_size
    print(f".obsidian copiada: {obsidian_copied} ({obsidian_size / 1024:.1f} KB)")

    istats: InxFlipStats | None = None
    if not args.no_inx:
        print()
        istats = _flip_obsidian_inx(new_value=True, dry_run=args.dry_run)
        print(f"INX obsidian:* → Archivo=true: chequeadas={istats.checked}, "
              f"cambiadas={istats.flipped}, ya_estaban={istats.already}, "
              f"errores={len(istats.errors)}")

    if args.snapshot:
        snap_path = _write_snapshot("rotate", {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "dry_run": args.dry_run,
            "old_vault_path": str(old),
            "new_vault_path": str(new),
            "depth_limit": args.depth,
            "dirs_created": mstats.dirs_created,
            "dirs_skipped_by_depth": mstats.dirs_skipped,
            "obsidian_copied": obsidian_copied,
            "obsidian_size_bytes": obsidian_size,
            "inx_flip": None if istats is None else {
                "target_value": istats.target_value,
                "checked": istats.checked,
                "flipped": istats.flipped,
                "already": istats.already,
                "errors": istats.errors,
            },
        })
        print(f"Snapshot: {snap_path}")

    print()
    print("SIGUIENTE PASO (manual):")
    print(f"  Edita .env y deja:  {ENV_VAULT}={new}")
    print(f"  Abre el vault nuevo en Obsidian desktop (File -> Open Vault).")
    if args.dry_run:
        print()
        print("(dry-run: no se han creado directorios ni modificado Notion)")
    return 0


def cmd_list_archived(_args) -> int:
    _ensure_inx_archivo()
    rows = query_data_source(_inx_id())
    archived = []
    for r in rows:
        props = r.get("properties", {}) or {}
        key = extract_property_value(props.get("Clave", {}))
        if not key or not key.startswith("obsidian:"):
            continue
        a = props.get("Archivo", {})
        is_arch = isinstance(a, dict) and a.get("type") == "checkbox" and bool(a.get("checkbox"))
        if is_arch:
            title = extract_property_value(props.get("Elemento", {})) or "(sin titulo)"
            archived.append((key, title))
    print(f"INX obsidian:* con Archivo=true: {len(archived)}")
    for key, title in archived[:50]:
        print(f"  {key[:60]:<62}  {title[:60]!r}")
    if len(archived) > 50:
        print(f"  ... y {len(archived) - 50} mas")
    return 0


def cmd_restore(args) -> int:
    old = Path(args.from_path).resolve()
    if not old.exists():
        raise SystemExit(f"--from no existe: {old}")
    current = _current_vault()
    print(f"Vault archivado (target restore): {old}")
    print(f"Vault activo actual             : {current}")
    print()

    if not args.no_inx:
        istats = _flip_obsidian_inx(new_value=False, dry_run=args.dry_run)
        print(f"INX obsidian:* → Archivo=false: chequeadas={istats.checked}, "
              f"cambiadas={istats.flipped}, ya_estaban={istats.already}, "
              f"errores={len(istats.errors)}")

    # Listar notas creadas en el vault activo (si distinto al viejo) para aviso
    new_notes: list[str] = []
    if current is not None and current.exists() and current.resolve() != old.resolve():
        for p in current.rglob("*.md"):
            if ".obsidian" in p.parts:
                continue
            new_notes.append(str(p.relative_to(current)).replace("\\", "/"))

    if new_notes:
        print()
        print(f"AVISO: el vault activo contiene {len(new_notes)} notas nuevas desde la rotacion.")
        for n in new_notes[:20]:
            print(f"  {n}")
        if len(new_notes) > 20:
            print(f"  ... y {len(new_notes) - 20} mas")
        print("  Muevelas manualmente al vault archivado si corresponde, antes de cambiar .env.")

    print()
    print("SIGUIENTE PASO (manual):")
    print(f"  Edita .env y deja:  {ENV_VAULT}={old}")
    print(f"  Abre el vault restaurado en Obsidian desktop.")
    if args.dry_run:
        print()
        print("(dry-run: no se ha tocado Notion)")
    return 0


# ==================== CLI ====================


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_st = sub.add_parser("status", help="Estado vault actual + Archivo en INX")
    p_st.set_defaults(func=cmd_status)

    p_ro = sub.add_parser("rotate", help="Crear vault nuevo + marcar INX obsidian:* como Archivado")
    p_ro.add_argument("--new-vault-path",
                      help="Ruta donde nace el nuevo vault (opcional; default = sibling ABGD-yymmdd)")
    p_ro.add_argument("--depth", type=int, default=DEFAULT_DEPTH,
                      help=f"Profundidad de replica (default {DEFAULT_DEPTH}; -1 = todo el arbol)")
    p_ro.add_argument("--dry-run", action="store_true")
    p_ro.add_argument("--snapshot", action="store_true")
    p_ro.add_argument("--no-inx", action="store_true")
    p_ro.add_argument("--force", action="store_true",
                      help="Permite escribir en --new-vault-path aunque ya exista no-vacia")
    p_ro.set_defaults(func=cmd_rotate)

    p_la = sub.add_parser("list-archived", help="Listar filas INX obsidian:* marcadas Archivo=true")
    p_la.set_defaults(func=cmd_list_archived)

    p_re = sub.add_parser("restore", help="Revertir flag Archivo en INX + instrucciones para .env")
    p_re.add_argument("--from", dest="from_path", required=True, help="Ruta del vault archivado a restaurar")
    p_re.add_argument("--dry-run", action="store_true")
    p_re.add_argument("--no-inx", action="store_true")
    p_re.set_defaults(func=cmd_restore)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
