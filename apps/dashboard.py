"""
Dashboard MAR — Vista operativa de Todoist en tres bloques:

  🔴 PENDIENTE  — Tareas vencidas (due < hoy): hay que reasignar o liquidar
  🟡 HOY        — Compromisos del día: ejecutar ahora
  ⚪ INBOX      — Sin fecha ni deadline: clasificar en el sistema MAR
"""

import sys
import os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime, timezone
from tools.todoist_tools import get_tasks, classify_mar_type, PROYECTOS_EXCLUIDOS

# Límite de tareas a mostrar por bloque (evita saturar la vista)
LIMITE_BLOQUE = 30

# ─── ICONOS MAR ───────────────────────────────────────────────────────────────

ICONO_TIPO = {
    "evento": "🗓️",
    "meta":   "🎯",
    "tarea":  "📋",
    "habito": "🔁",
    "idea":   "💡",
}

ICONO_PRIORIDAD = {4: "❗", 3: "⬆", 2: "⬇", 1: ""}


# ─── CLASIFICADOR DE FECHA ────────────────────────────────────────────────────

def _due_date(t: dict):
    """Devuelve la fecha de vencimiento como date, o None si no tiene."""
    due = t.get("due")
    if not due:
        return None
    raw = due.get("date", "")
    if not raw:
        return None
    try:
        # Puede ser "2026-03-16" o "2026-03-16T16:00:00Z"
        if "T" in raw:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            # Convertir a fecha local
            return dt.astimezone().date()
        return date.fromisoformat(raw[:10])
    except ValueError:
        return None


def _clasificar(tareas: list[dict], hoy: date):
    """Separa tareas en tres bloques por fecha de vencimiento."""
    pendientes, hoy_list, inbox = [], [], []
    for t in tareas:
        d = _due_date(t)
        if d is None:
            inbox.append(t)
        elif d < hoy:
            pendientes.append(t)
        elif d == hoy:
            hoy_list.append(t)
        # Tareas futuras no aparecen en el dashboard
    return pendientes, hoy_list, inbox


# ─── RENDER ───────────────────────────────────────────────────────────────────

def _render_tarea(t: dict, mostrar_fecha: bool = True) -> str:
    tipo      = classify_mar_type(t)
    icono     = ICONO_TIPO.get(tipo, "•")
    prioridad = ICONO_PRIORIDAD.get(t.get("priority", 1), "")
    due       = t.get("due") or {}
    fecha     = ""

    if mostrar_fecha and due:
        raw = due.get("date", "")
        if "T" in raw:
            # Mostrar hora en local
            try:
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone()
                fecha = f" [{dt.strftime('%H:%M')}]"
            except ValueError:
                fecha = f" [{raw[11:16]}]"
        elif raw:
            fecha = f" [{raw}]"

    return f"  {icono} {prioridad}{t['content']}{fecha}"


def _bloque(titulo: str, icono: str, tareas: list[dict], mostrar_fecha: bool = True) -> list[str]:
    lineas = []
    sep = "─" * 50
    lineas.append(f"\n{sep}")
    lineas.append(f" {icono}  {titulo}  ({len(tareas)})")
    lineas.append(sep)

    if not tareas:
        lineas.append("  (vacío)")
    else:
        tareas_ord = sorted(tareas, key=lambda x: x.get("priority", 1), reverse=True)
        for t in tareas_ord:
            lineas.append(_render_tarea(t, mostrar_fecha))

    return lineas


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def dashboard() -> str:
    ahora = datetime.now().strftime("%Y-%m-%d  %H:%M")
    hoy   = date.today()

    # Una sola llamada paginada → clasificación client-side por fecha
    todas = get_tasks()
    pendientes, hoy_list, inbox = _clasificar(todas, hoy)

    total_real = len(pendientes) + len(hoy_list) + len(inbox)

    pendientes_vis = pendientes[:LIMITE_BLOQUE]
    hoy_vis        = hoy_list[:LIMITE_BLOQUE]
    inbox_vis      = inbox[:LIMITE_BLOQUE]
    total = len(pendientes_vis) + len(hoy_vis) + len(inbox_vis)

    lineas = []
    lineas.append(f"\n{'═' * 50}")
    lineas.append(f"  📊 DASHBOARD MAR  —  {ahora}")
    lineas.append(f"  {total_real} acciones totales  |  mostrando {total}")
    lineas.append(f"{'═' * 50}")

    lineas += _bloque("PENDIENTE", "🔴", pendientes_vis, mostrar_fecha=True)
    if len(pendientes) > LIMITE_BLOQUE:
        lineas.append(f"  ... y {len(pendientes) - LIMITE_BLOQUE} más")

    lineas += _bloque("HOY",   "🟡", hoy_vis,   mostrar_fecha=True)
    if len(hoy_list) > LIMITE_BLOQUE:
        lineas.append(f"  ... y {len(hoy_list) - LIMITE_BLOQUE} más")

    lineas += _bloque("INBOX", "⚪", inbox_vis, mostrar_fecha=False)
    if len(inbox) > LIMITE_BLOQUE:
        lineas.append(f"  ... y {len(inbox) - LIMITE_BLOQUE} más")

    lineas.append(f"\n{'─' * 50}")
    lineas.append(
        f"  🔴 {len(pendientes)} pendientes  "
        f"🟡 {len(hoy_list)} hoy  "
        f"⚪ {len(inbox)} inbox"
    )
    lineas.append(f"{'─' * 50}")
    lineas.append(f"  Límite por bloque: {LIMITE_BLOQUE}  |  python dashboard.py --limite N para ampliar\n")

    return "\n".join(lineas)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Dashboard MAR — Todoist")
    parser.add_argument("--limite", type=int, default=LIMITE_BLOQUE,
                        help=f"Tareas a mostrar por bloque (default: {LIMITE_BLOQUE})")
    args = parser.parse_args()
    LIMITE_BLOQUE = args.limite
    print(dashboard())
