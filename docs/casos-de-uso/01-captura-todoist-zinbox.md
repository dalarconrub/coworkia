# Caso de uso: Capturar en la Bandeja de entrada de Todoist (Inbox) y clasificar a MAR

## Objetivo

Capturar rápidamente una entrada (idea/acción) en Todoist y dejarla **clasificada en MAR** con el mínimo contexto necesario para que pueda ejecutarse o derivarse a PTN/Obsidian.

## Actores

- **Usuario**: David
- **Sistema(s)**: Todoist (fuente MAR), Notion (espejo en `TODOIST-TAREAS`)

## Trigger

Surge una idea/acción en cualquier contexto (móvil/PC) y se captura en Todoist.

## Precondiciones

- Todoist operativo y **Bandeja de entrada** accesible (Inbox), p. ej. `https://app.todoist.com/app/inbox`.
- `.env` configurado para sincronización a Notion:
  - `TODOIST_API_KEY`
  - `TODOIST_DB_TAREAS`

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

- [ ] Ejecutar (crea columnas necesarias en `TODOIST-TAREAS` para mapear propiedades Todoist):

```bat
apps\ensure_todoist_tasks_schema.bat
```

### Checklist — Captura (Inbox)

- [ ] Abrir la Bandeja de entrada (Inbox) de Todoist: `https://app.todoist.com/app/inbox`
- [ ] Crear la tarea con texto mínimo claro (verbo + objeto).
- [ ] (Opcional) Añadir 1 línea de detalle si el texto no basta para ejecutarla en frío.

### Checklist — Clasificación MAR (en Todoist)

- [ ] Ajustar campos nativos según la tabla de reglas (arriba). Referencia rápida:
  - [ ] **Idea**: sin `Due` y sin `Deadline`.
  - [ ] **Tarea**: `Due` (solo día, sin hora), sin `Deadline`, no recurrente.
  - [ ] **Meta**: `Deadline` presente; sin hora en `Due`; no recurrente (`Due` opcional).
  - [ ] **Evento**: `Due` con hora.
  - [ ] **Hábito**: recurrente.
- [ ] Ajustar prioridad si importa (si no, dejar por defecto).
- [ ] (Opcional) Añadir labels de contexto (mínimo, sin sobre-etiquetar).

### Checklist — Sincronización a Notion (espejo)

- [ ] Ejecutar el sync Todoist → Notion:

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

- [ ] (Opcional) Doctor MAR regla a regla: `apps\mar_doctor.bat --check-duplicates`, `--check-evento-hora`, `--check-meta-deadline`, `--check-tarea-fecha`, etc. Ver `apps\mar_doctor.py --help`.

- [ ] Verificar que la tarea aparece/actualiza en `TODOIST-TAREAS` (Notion):
  - [ ] `Todoist ID` relleno
  - [ ] `Estado=Activa` (si corresponde)
  - [ ] `Tipo MAR` razonable
  - [ ] `Descripcion` presente si usas descripción en Todoist
  - [ ] `Due`/`Deadline`/`Recurrencia` coherentes con el tipo MAR (si existen)
  - [ ] `Fecha` y/o `URL` presentes si aplica

## Postcondiciones / Resultado verificable

- En Todoist existe una tarea con:
  - `content`, `id`, `url`
  - campos MAR coherentes (due/deadline/recurring según tipo)
- En Notion `TODOIST-TAREAS` existe/actualiza la fila con ese `Todoist ID`.

## Criterios de aceptación (Definition of Done)

- [ ] La tarea está en Todoist Inbox (o ya movida si tu flujo lo hace) y es ejecutable/entendible.
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
