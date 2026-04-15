# Caso de uso: Convertir una tarea en proyecto PTN con trazabilidad (INX)

## Objetivo

Tomar una tarea Todoist que “escala” a trabajo estructurado y convertirla en un **proyecto PTN** en Notion, dejando **trazabilidad** en `INX-ENLACES` para navegar Todoist ↔ PTN (y más adelante Obsidian/otros).

## Actores

- **Usuario**: David
- **Sistema(s)**: Todoist (MAR), Notion (PTN + `TODOIST-TAREAS` + `INX-ENLACES`)

## Trigger

En revisión (diaria/semanal) decides que una tarea deja de ser “un solo ítem MAR” y pasa a ser **proyecto** con planificación en PTN.

## Precondiciones

- `.env` con al menos:
  - `NOTION_TOKEN`
  - `NOTION_DS_PROYECTOS` (y si aplica `NOTION_DS_TAREAS`, `NOTION_DS_NOTAS`)
  - `TODOIST_DB_TAREAS`
  - `NOTION_DB_INX`
- La base `TODOIST-TAREAS` tiene relación **PTN Proyecto** (o equivalente) hacia proyectos PTN, para poder enlazar desde la fila de la tarea.

## Fuente de verdad (autoridad)

- **MAR / ejecución**: Todoist
- **Plan y estructura del proyecto**: Notion (PTN)
- **Trazabilidad cruzada**: `INX-ENLACES` (Notion), alimentada por sync desde `TODOIST-TAREAS` cuando existen relaciones

## Contrato INX (clave canónica)

- Para la tarea Todoist: **`Clave=todoist:<TodoistID>`** (sin espacios; el ID es el de la API de Todoist).
- Tras el sync, la fila INX correspondiente debe poder llevar **relación `PTN Proyecto`** si la fila en `TODOIST-TAREAS` la tiene.

## Flujo principal (happy path)

1. Identificar la tarea en Todoist y anotar su **Todoist ID** (o URL).
2. Crear el **proyecto** en PTN (Notion) con nombre y relaciones ABC si aplica.
3. En Notion, abrir la fila de esa tarea en **`TODOIST-TAREAS`** y establecer la relación **PTN Proyecto** → proyecto creado (tras un sync reciente desde Todoist si la fila no existía).
4. Ejecutar sync **INX** desde la fuente Todoist (ver checklist) para upsert en `INX-ENLACES`.
5. Verificar en `INX-ENLACES` la fila con `Clave=todoist:<id>` y `PTN Proyecto` relleno.

## Checklist ejecutable (v2)

### Paso 0 — Sync MAR → Notion (si hace falta fila actualizada)

```bat
apps\sync_todoist_to_notion.bat 200 --no-pause
```

### Paso 1 — Crear proyecto PTN

- [ ] En Notion, en el data source **PTN-Proyectos**, crear la página del proyecto (título, área/bloque/contexto si tu schema lo usa).

### Paso 2 — Enlazar tarea ↔ proyecto en `TODOIST-TAREAS`

- [ ] Localizar la fila cuya columna **Todoist ID** coincide con la tarea.
- [ ] Rellenar la propiedad de relación **PTN Proyecto** apuntando al proyecto creado.

### Paso 3 — Propagar a INX (solo fuente Todoist)

```bat
apps\inx_sync_todoist.bat 200 --no-pause
```

Alternativa (cadena completa B0A-INX: Todoist + logs PTN/Obsidian + INX):

```bat
.\.venv\Scripts\python.exe agents\orchestrator_agent.py inx-sync --limit 200
```

### Paso 4 — Verificación

- [ ] En **`INX-ENLACES`**: existe fila con **Clave** `todoist:<TodoistID>` (o búsqueda por **Todoist ID** / título).
- [ ] La propiedad **PTN Proyecto** en esa fila apunta al proyecto correcto.
- [ ] (Opcional) **Estado** = Activo en filas nuevas del sync.

## Postcondiciones / Resultado verificable

- Proyecto PTN creado y enlazable desde la fila de `TODOIST-TAREAS`.
- En `INX-ENLACES` hay fila coherente para `todoist:<id>` con relación PTN.

## Criterios de aceptación (Definition of Done)

- [ ] El **Todoist ID** es el correcto (misma tarea en Todoist y en Notion).
- [ ] La relación **PTN Proyecto** está en `TODOIST-TAREAS` y se refleja en INX tras el sync.
- [ ] No hay duplicados de `Clave` en INX para ese `todoist:<id>` (usar `apps\mar_doctor.bat --check-duplicates` sobre `TODOIST-TAREAS` si dudas; INX se dedupe por Clave en upsert).

## Automatización actual

| Acción | Comando |
| --- | --- |
| Sync Todoist → `TODOIST-TAREAS` | `apps\sync_todoist_to_notion.bat` |
| Sync solo INX desde Todoist | `apps\inx_sync_todoist.bat` |
| Cadena INX completa | `python agents/orchestrator_agent.py inx-sync --limit 200` |

## Observabilidad

- **Notion**: `TODOIST-TAREAS` (relación PTN), `INX-ENLACES` (Clave, PTN Proyecto, Fuente, Estado).
- **Métrica**: crear proyecto + enlazar + sync INX debería ser &lt; 5 min operativos.

## Gaps (pendientes)

- **Asistente “promote-to-project”**: un solo comando que cree PTN + relacione + dispare sync INX (sin clicks en Notion).
- **Convención explícita** si en el futuro se quiere también fila INX `ptn:<page_id>` además de `todoist:<id>` (hoy basta con la fila puente desde Todoist si la relación está en `TODOIST-TAREAS`).

## Nota operativa: “PTN existe” vs “PTN aparece en NOTION_DB”

- **PTN-Proyectos** (data source) es el **catálogo canónico**: si creas el proyecto desde una relación en `TODOIST-TAREAS`, el proyecto **sí existe** en PTN.
- `NOTION_DB` es un **log de cambios PTN** (B0A-INX): solo se llena al ejecutar `tools/log_ptn_changes.py` (o `apps\log_ptn_changes.bat`).
- Por tanto, es normal que el proyecto aparezca en `INX-ENLACES` como relación desde `todoist:<id>` pero **no** aparezca aún como entrada de log en `NOTION_DB` hasta correr el log.

## Mejoras ya implementadas / alineadas

- `tools/sync_inx_links.py` upsertea desde `TODOIST-TAREAS` copiando relaciones PTN cuando existen.
- Orquestador: `agents/orchestrator_agent.py inx-sync` para cadena completa.

## Fallos típicos

- **No aparece relación PTN en INX**: falta relación en `TODOIST-TAREAS` o no se ejecutó `sync_inx_links` tras enlazar.
- **IDs distintos**: copiar mal el Todoist ID; verificar columna **Todoist ID** en Notion.

## Validación práctica (opcional, una vez)

Para comprobar el flujo con una tarea real:

1. Ejecuta el validador (hace sync Todoist → Notion, sync INX desde Todoist y genera informe):

   ```bat
   apps\validate_case_02.bat --no-pause
   ```

2. Si el informe indica `Con relación PTN Proyecto: 0`, entonces falta el paso manual:
   - Crea un proyecto PTN mínimo.
   - En `TODOIST-TAREAS`, enlaza **PTN Proyecto** en la fila cuya columna **Todoist ID** corresponde a la tarea.
   - Vuelve a ejecutar `apps\validate_case_02.bat --no-pause`.

3. El caso 2 queda **validado** cuando el informe muestra al menos 1:
   - `TODOIST-TAREAS ... Con relación PTN Proyecto: N`
   - `INX-ENLACES ... Clave todoist:* con PTN Proyecto: N`
