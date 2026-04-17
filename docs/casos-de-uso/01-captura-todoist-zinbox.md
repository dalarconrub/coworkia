# Caso de uso: Capturar en el inbox normal de Todoist y clasificar a MAR

## Objetivo

Capturar rápidamente una entrada (idea/acción) en el **inbox normal** de Todoist y dejarla **clasificada en MAR** con el mínimo contexto necesario para que pueda ejecutarse o derivarse a PTN/Obsidian.

## Actores

- **Usuario**: David
- **Sistema(s)**: Todoist (fuente MAR), Notion (espejo en `TODOIST-TAREAS`)

## Trigger

Surge una idea/acción en cualquier contexto (móvil/PC) y se captura en el inbox normal de Todoist.

## Precondiciones

- Todoist operativo y **Bandeja de entrada normal** accesible (Inbox), p. ej. `https://app.todoist.com/app/inbox`.
- `.env` configurado para sincronización a Notion:
  - `TODOIST_API_KEY`
  - `TODOIST_DB_TAREAS`

Nota:

- Este caso cubre el flujo que sí entra en `tools/sync_todoist_to_notion.py`.
- `Z-INBOX` es un flujo distinto de captura/triage y hoy queda excluido del sync operativo normal.

## Fuente de verdad (autoridad)

- **MAR**: Todoist
- **Espejo/consulta**: Notion `TODOIST-TAREAS` (no manda sobre MAR)

## Flujo principal (happy path)

1. Crear tarea en Todoist (texto mínimo).
2. Añadir lo mínimo de MAR (fecha/deadline/hora si aplica; recurrencia si hábito; prioridad si importa).
3. (Opcional) Añadir labels que indiquen contexto.
4. Sincronizar a Notion para trazabilidad y reporting.

## Reglas MAR canónicas (Coworkia)

El clasificador en código (`tools/todoist_tools.py`, `classify_mar_type`) y el espejo en Notion siguen este orden de prioridad:

| Tipo | Regla |
| --- | --- |
| **Evento** | Cualquier cosa con **hora** en `Due` (da igual lo demás). |
| **Hábito** | Cualquier cosa **recurrente** (da igual lo demás, salvo que si hay hora primero cuenta como Evento). |
| **Meta** | Sin hora, no recurrente, **con `Deadline`**. `Due` (fecha) opcional. |
| **Tarea** | Sin hora, no recurrente, **sin `Deadline`**, **con `Due`** solo como fecha (día). |
| **Idea** | Sin `Due` y sin `Deadline`. |

## Checklist ejecutable (v2)

### Checklist — Paso 0 (una vez): asegurar schema en Notion

- [x] Ejecutar (crea columnas necesarias en `TODOIST-TAREAS` para mapear propiedades Todoist):

```bat
apps\ensure_todoist_tasks_schema.bat
```

### Checklist — Captura (inbox normal)

- [ ] Abrir la Bandeja de entrada normal (Inbox) de Todoist: `https://app.todoist.com/app/inbox`
- [x] Crear la tarea con texto mínimo claro (verbo + objeto).
- [x] (Opcional) Añadir 1 línea de detalle si el texto no basta para ejecutarla en frío.

### Checklist — Clasificación MAR (en Todoist)

- [x] Ajustar campos nativos según la tabla de reglas (arriba). Referencia rápida:
  - [x] **Idea**: sin `Due` y sin `Deadline`.
  - [ ] **Tarea**: `Due` (solo día, sin hora), sin `Deadline`, no recurrente.
  - [ ] **Meta**: `Deadline` presente; sin hora en `Due`; no recurrente (`Due` opcional).
  - [ ] **Evento**: `Due` con hora.
  - [ ] **Hábito**: recurrente.
- [ ] Ajustar prioridad si importa (si no, dejar por defecto).
- [ ] (Opcional) Añadir labels de contexto (mínimo, sin sobre-etiquetar).

### Checklist — Sincronización a Notion (espejo)

- [x] Ejecutar el sync Todoist → Notion:

```bash
.\.venv\Scripts\python.exe tools/sync_todoist_to_notion.py --limit 200
```

- [ ] Alternativa (Windows, `.bat`):

```bat
apps\sync_todoist_to_notion.bat 200
```

- [ ] Nota: si lo ejecutas desde terminal y no quieres que se quede esperando, usa:

```bat
apps\sync_todoist_to_notion.bat 200 --no-pause
```

- [ ] Check completo (sync + doctor MAR):

```bat
apps\mar_check.bat 200 --no-pause
```

- [x] (Opcional) Doctor MAR regla a regla: `apps\mar_doctor.bat --check-duplicates`, `--check-evento-hora`, `--check-meta-deadline`, `--check-tarea-fecha`, etc. Ver `apps\mar_doctor.py --help`.

Verificación técnica realizada el `2026-04-17`:

- `tools/ensure_todoist_tasks_schema.py` → `Schema OK: no hay propiedades nuevas que añadir.`
- `tools/sync_todoist_to_notion.py --limit 200` → `Tareas sincronizadas: 76`
- `apps/mar_doctor.py` con checks completos → `OK: no se detectaron issues con las reglas actuales.`

- [x] Verificar que la tarea aparece/actualiza en `TODOIST-TAREAS` (Notion):
  - [x] `Todoist ID` relleno
  - [x] `Estado=Activa` (si corresponde)
  - [x] `Tipo MAR` razonable
  - [x] `Descripcion` presente si usas descripción en Todoist
  - [x] `Due`/`Deadline`/`Recurrencia` coherentes con el tipo MAR (si existen)
  - [ ] `Fecha` y/o `URL` presentes si aplica

Validación end-to-end realizada el `2026-04-17` con tarea real de prueba:

- Todoist (inbox normal): `6gPwFvJ22qhQ7GCc` → `[TEST CASE 01] Validar inbox normal`
- Descripción: `Prueba automatica Codex 2026-04-17 para validar el caso de uso 01 en inbox normal`
- Fila espejo en `TODOIST-TAREAS`: `345622cf-315b-81ca-b82b-d3ed41e4c790`
- Resultado observado en Notion:
  - `Estado=Activa`
  - `Tipo MAR=idea`
  - `Descripcion` presente
  - `Due` vacío
  - `Deadline` vacío
  - `Recurrencia=✗`
  - `URL` vacía

Nota de implementación:

- La captura en `Z-INBOX` no valida este caso porque `tools/sync_todoist_to_notion.py` excluye proyectos `Z-*` del flujo operativo normal.
- La API consultada de Todoist devolvió `url=None` para la tarea de prueba, así que el criterio sobre `URL` queda pendiente de confirmación o ajuste documental.

## Postcondiciones / Resultado verificable

- En Todoist existe una tarea con:
  - `content`, `id`, `url`
  - campos MAR coherentes (due/deadline/recurring según tipo)
- En Notion `TODOIST-TAREAS` existe/actualiza la fila con ese `Todoist ID`.

## Criterios de aceptación (Definition of Done)

- [ ] La tarea está en el inbox normal de Todoist (o ya movida si tu flujo lo hace) y es ejecutable/entendible.
- [ ] MAR está representado por campos nativos (due/deadline/hora/recurrence), no por “memoria”.
- [ ] Tras ejecutar el sync, existe exactamente **1** fila en `TODOIST-TAREAS` con ese `Todoist ID`.
- [ ] El `URL` de Todoist está presente en Notion (si Todoist lo expone para la tarea).

## Automatización actual

- **Sync Todoist → Notion**:

```bash
.\.venv\Scripts\python.exe tools/sync_todoist_to_notion.py --limit 200
```

## Observabilidad

- **Notion**: `TODOIST-TAREAS` (propiedades `Todoist ID`, `Estado`, `Tipo MAR`, `Fecha`, `Due`, `Deadline`, `Recurrencia`, `Descripcion`, `URL`, `Labels`)
- **Métrica**: una captura debería tardar < 30s; el sync debería tardar < 2–3 min para 200 tareas.

## Gaps (pendientes opcionales)

- Mapeo opcional desde labels/proyecto/sección a ABC/PTN (sin romper autoridad de Todoist).
- Reglas ad hoc por prioridad o por proyecto (si se quieren en el futuro).

## Estado del caso (v2)

- **Clasificador MAR** alineado con la tabla de reglas: `classify_mar_type` en `tools/todoist_tools.py`.
- **Doctor MAR**: `apps/mar_doctor.py` (checks activables con flags; incluye `--check-tipo-consistency`).
- **Check en un paso**: `apps\mar_check.bat` (sync + todos los checks; usar `--no-pause` en terminal).

## Mejoras ya implementadas

- Sync Todoist → Notion ampliado (descripción, Due/Deadline separados, IDs, etc.) y `.bat` de ayuda.
- Schema `TODOIST-TAREAS` asegurable con `apps\ensure_todoist_tasks_schema.bat`.
- Orquestación INX: `python agents/orchestrator_agent.py inx-sync` (cadena B0A-INX; fuera del flujo mínimo de este caso).

## Fallos típicos y diagnóstico rápido

- **La tarea no aparece en Notion**:
  - Revisa `.env`: `TODOIST_API_KEY`, `TODOIST_DB_TAREAS`.
  - Ejecuta `apps/config_doctor.py` si procede.
- **Aparece duplicada**:
  - Revisar si la BD `TODOIST-TAREAS` tiene filas antiguas con el mismo `Todoist ID`.
- **Tipo MAR “raro”**:
  - Revisar el mapeo en `tools/todoist_tools.py` (función `classify_mar_type`).
