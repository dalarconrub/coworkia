## Caso de uso: Convertir una tarea en proyecto PTN con trazabilidad (INX)

### Objetivo

Tomar una tarea “grande” (o un conjunto) y convertirla en un **proyecto PTN** en Notion, asegurando trazabilidad en `INX-ENLACES` para navegar entre Todoist ↔ PTN ↔ Obsidian.

### Actores

- **Usuario**: David
- **Sistema(s)**: Todoist, Notion (PTN + INX)

### Trigger

Durante revisión diaria/semanal se detecta que una tarea requiere planificación y pasa a ser “proyecto”.

### Precondiciones

- PTN operativo en Notion (`NOTION_DS_PROYECTOS`, `NOTION_DS_TAREAS`, `NOTION_DS_NOTAS`).
- INX operativo en Notion (`NOTION_DB_INX`).
- (Opcional) `TODOIST-TAREAS` sincronizada recientemente.

### Fuente de verdad (autoridad)

- **Plan/estructura del proyecto**: Notion (PTN)
- **Ejecución temporal (MAR)**: Todoist
- **Trazabilidad**: `INX-ENLACES` (Notion)

### Flujo principal (happy path)

1. Identificar la tarea Todoist que “escala” a proyecto (guardar su `Todoist ID`).
2. Crear proyecto en PTN (Notion) con nombre y contexto ABC (Area/Bloque/Contexto).
3. Crear/seleccionar tareas PTN hijas (si aplica) y vincularlas al proyecto.
4. Crear entrada INX para:
   - `todoist:<TodoistID>` (si no existe)
   - `ptn:<page_id_del_proyecto>` (si no existe)
5. En `INX-ENLACES`, relacionar `PTN Proyecto` y guardar `Todoist ID` en la fila correspondiente.

### Postcondiciones / Resultado verificable

- Proyecto PTN creado con relaciones ABC.
- En `INX-ENLACES` existe al menos una fila con:
  - `Fuente=Todoist`, `Todoist ID=<id>`, y relación a `PTN Proyecto`
  - `Fuente=Notion` (si se decide llevar también el lado PTN como fila independiente)

### Automatización actual

- Upsert INX desde `TODOIST-TAREAS` (relaciones si existen):

```bash
.\.venv\Scripts\python.exe tools/sync_inx_links.py --source todoist --limit 200
```

- Cadena INX completa:

```bash
.\.venv\Scripts\python.exe agents/orchestrator_agent.py inx-sync --limit 200
```

### Observabilidad

- `INX-ENLACES`: comprobar `Clave=todoist:<id>` y que `PTN Proyecto` no está vacío.

### Gaps (lo que falta hoy)

- La relación `Todoist task -> PTN proyecto` es parcialmente manual (no hay asistente que cree el proyecto y complete INX).
- Falta una convención “1 fila vs 2 filas” (una fila puente con todo vs filas por fuente + relaciones cruzadas). Hoy conviven ambos enfoques.

### Mejoras propuestas (acciones)

- Crear un comando “promote-to-project”:
  - input: `Todoist ID` + datos mínimos
  - output: crea PTN Proyecto + rellena relaciones ABC + actualiza fila INX `todoist:<id>` con `PTN Proyecto`.
- Definir y documentar la convención canónica de `INX-ENLACES` (modelo de filas).

