"""
Validacion del caso de uso 7: Promocion Obsidian -> PTN-Notas -> INX-ENLACES.

Contrato:
- PTN-Notas (NOTION_DS_NOTAS) tiene filas con propiedad 'Ruta Obsidian' no
  vacia para cada nota promocionada.
- Para cada ruta promocionada: debe existir en OBSIDIAN_DB ('Ruta') y en
  INX-ENLACES con Clave 'obsidian:<ruta>'.
- Cruce doble deseable (Gap 3 del caso): INX-ENLACES tambien contiene
  'ptn:<id_nota_PTN>' para la pagina recien creada.

Uso: python tools/validate_case_07.py
Requiere .env: NOTION_DS_NOTAS, OBSIDIAN_DB, NOTION_DB_INX

Exit codes:
  0  OK (promociones reflejadas en OBSIDIAN_DB e INX obsidian:*).
  1  Faltantes detectadas (con hint del comando que las crea) o schema sin migrar.
  2  Falta configuracion (.env).
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from tools.notion_tools import extract_property_value, query_data_source


RUTA_PROP = "Ruta Obsidian"
TITLE_PROP = "Título"


def _dedupe_rows(rows: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        pid = (r.get("id") or "").strip()
        if pid and pid in seen:
            continue
        if pid:
            seen.add(pid)
        out.append(r)
    return out


def _id_variants(page_id: str) -> set[str]:
    pid = (page_id or "").strip()
    return {pid, pid.replace("-", "")}


def main() -> int:
    db_n = os.getenv("NOTION_DS_NOTAS")
    db_o = os.getenv("OBSIDIAN_DB")
    db_i = os.getenv("NOTION_DB_INX")
    if not db_n or not db_o or not db_i:
        print("Faltan NOTION_DS_NOTAS, OBSIDIAN_DB o NOTION_DB_INX en .env")
        return 2

    # Lado PTN-Notas.
    rows_n = _dedupe_rows(query_data_source(db_n))

    if rows_n and RUTA_PROP not in rows_n[0].get("properties", {}):
        print(f"[error] La propiedad '{RUTA_PROP}' no existe en NOTION_DS_NOTAS.")
        print("        Ejecuta primero: python tools/migrate_notas_ruta_obsidian.py")
        return 1

    promociones: list[dict] = []
    for r in rows_n:
        props = r.get("properties", {})
        ruta = (extract_property_value(props.get(RUTA_PROP, {})) or "").strip()
        if not ruta:
            continue
        titulo = extract_property_value(props.get(TITLE_PROP, {})) or "(sin titulo)"
        promociones.append({"page_id": r["id"], "titulo": titulo, "ruta": ruta})

    # Lado OBSIDIAN_DB.
    rows_o = _dedupe_rows(query_data_source(db_o))
    obsidian_rutas: set[str] = set()
    for r in rows_o:
        ruta = extract_property_value(r.get("properties", {}).get("Ruta", {}))
        if ruta:
            obsidian_rutas.add(ruta)

    # Lado INX.
    rows_i = _dedupe_rows(query_data_source(db_i))
    inx_obsidian: set[str] = set()
    inx_ptn: set[str] = set()
    for r in rows_i:
        clave = extract_property_value(r.get("properties", {}).get("Clave", {})) or ""
        if clave.startswith("obsidian:"):
            inx_obsidian.add(clave[len("obsidian:") :])
        elif clave.startswith("ptn:"):
            inx_ptn.add(clave[len("ptn:") :])

    def _ptn_match(page_id: str) -> bool:
        return bool(_id_variants(page_id) & inx_ptn)

    match_obs_db = [p for p in promociones if p["ruta"] in obsidian_rutas]
    match_inx_obs = [p for p in promociones if p["ruta"] in inx_obsidian]
    match_inx_ptn = [p for p in promociones if _ptn_match(p["page_id"])]
    match_doble = [
        p for p in promociones
        if p["ruta"] in inx_obsidian and _ptn_match(p["page_id"])
    ]

    missing_obs_db = [p for p in promociones if p["ruta"] not in obsidian_rutas]
    missing_inx_obs = [p for p in promociones if p["ruta"] not in inx_obsidian]

    print("=== Validacion caso 7 (Obsidian -> PTN-Notas -> INX) ===\n")
    print(f"PTN-Notas: {len(rows_n)} filas unicas")
    print(f"  - Con '{RUTA_PROP}' no vacia (promociones): {len(promociones)}")
    print(f"OBSIDIAN_DB: {len(rows_o)} filas unicas")
    print(f"  - Con Ruta: {len(obsidian_rutas)}")
    print(f"INX-ENLACES: {len(rows_i)} filas unicas")
    print(f"  - Clave obsidian:*: {len(inx_obsidian)}")
    print(f"  - Clave ptn:*: {len(inx_ptn)}")
    print()
    print(f"Promociones que matchean OBSIDIAN_DB.Ruta: {len(match_obs_db)}/{len(promociones)}")
    print(f"Promociones que matchean INX obsidian:<ruta>: {len(match_inx_obs)}/{len(promociones)}")
    print(f"Promociones que matchean INX ptn:<id>: {len(match_inx_ptn)}/{len(promociones)}")
    print(f"Promociones con CRUCE DOBLE (obsidian:* AND ptn:*): {len(match_doble)}/{len(promociones)}")

    if match_doble:
        print("\nEjemplos de cruce doble (hasta 5):")
        for p in match_doble[:5]:
            print(f"  - {p['titulo'][:60]} | {p['ruta'][:80]}")

    if missing_obs_db:
        print("\n[!] Promociones sin fila en OBSIDIAN_DB (hasta 5):")
        for p in missing_obs_db[:5]:
            print(f"  - {p['titulo'][:60]} | {p['ruta'][:80]}")
        print("    Ejecuta: python tools/log_obsidian_changes.py")

    if missing_inx_obs:
        print("\n[!] Promociones sin fila INX obsidian:<ruta> (hasta 5):")
        for p in missing_inx_obs[:5]:
            print(f"  - {p['titulo'][:60]} | {p['ruta'][:80]}")
        print("    Ejecuta: apps\\inx_sync_obsidian.bat 200 --no-pause")

    if len(promociones) == 0:
        print("\n[!] No hay promociones en PTN-Notas (ninguna fila con Ruta Obsidian).")
        print("    Ejecuta: python tools/promote_obsidian_to_ptn.py <nombre-nota> [--proyecto <ref>]")
        return 1

    if missing_obs_db or missing_inx_obs:
        return 1

    print("\nOK: la cadena caso 7 esta verificable (promociones reflejadas en OBSIDIAN_DB e INX obsidian:*).")
    if match_doble and len(match_doble) == len(promociones):
        print("OK: cruce doble (obsidian:* <-> ptn:*) completo para todas las promociones.")
    elif len(match_inx_ptn) < len(promociones):
        pendientes = len(promociones) - len(match_inx_ptn)
        print(
            f"[info] cruce ptn:* incompleto ({pendientes} faltantes). Gap 3 del caso 07."
        )
        print("       Para forzar sync completa: python agents/orchestrator_agent.py inx-sync --limit 200")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
