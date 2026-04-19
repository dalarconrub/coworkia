# Caso de uso: Checkboxes de nota Obsidian ↔ tareas Todoist (con cruce INX)

## Objetivo

Convertir checkboxes sueltos dentro de una nota Obsidian en tareas Todoist reales y, después, reflejar también el camino inverso cuando esos checkboxes pasan a `- [x]`.

El caso queda así en dos direcciones:

- **Captura**: `- [ ]` en Obsidian → tarea activa en Todoist
- **Cierre**: `- [x]` con marker → tarea completada en Todoist

En ambos casos, la trazabilidad cruza por `INX-ENLACES`.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (vault), Todoist (API), Notion (`TODOIST-TAREAS`, `INX-ENLACES`)

## Trigger

Mientras escribes una nota aparecen pendientes ejecutables:

```md
- [ ] Pedir dataset a Fran
- [ ] Revisar R-script del análisis GLM
```

Más tarde, alguno se completa en la propia nota:

```md
- [x] Pedir dataset a Fran <!-- todoist:<id> -->
```

El caso 10 automatiza ambas transiciones sin copiar/pegar manual entre Obsidian y Todoist.

## Precondiciones

- `.env` con:
  - `TODOIST_API_KEY` o equivalente operativo del proyecto
  - `OBSIDIAN_ALPHA_PATH`
  - `TODOIST_DB_TAREAS`
  - `NOTION_DB_INX`
- La nota existe ya en el vault.

## Fuente de verdad

- **Redacción y contexto original**: Obsidian
- **Estado operativo de la tarea**: Todoist
- **Espejo / reporting**: `TODOIST-TAREAS`
- **Trazabilidad cross-system**: `INX-ENLACES`

## Contrato

- Cada checkbox promovido queda anclado con marker inline:

```md
- [ ] Descripcion <!-- todoist:<task_id> -->
```

- Si luego se marca como completado:

```md
- [x] Descripcion <!-- todoist:<task_id> -->
```

- La fila de espejo en Notion usa `Todoist ID = <task_id>`.
- La fila de INX usa `Clave = todoist:<task_id>`.

## Flujo principal

### Fase A — Captura

1. Escribes una nota con líneas `- [ ]` sin marker.
2. Ejecutas:

```bat
python tools/promote_notas_checkboxes_to_todoist.py "<nombre-nota>" --sync
```

3. El script:
   - crea una tarea Todoist por cada línea pendiente sin marker
   - reescribe la nota añadiendo `<!-- todoist:<id> -->`
   - con `--sync`, refresca `OBSIDIAN_DB`, `TODOIST-TAREAS` e `INX`

### Fase B — Cierre round-trip

1. En la nota, cambias una línea promovida a `- [x]`.
2. Ejecutas:

```bat
python tools/close_obsidian_checkboxes_to_todoist.py "<nombre-nota>" --sync
```

3. El script:
   - cierra la tarea en Todoist
   - marca `Estado=Completada` en `TODOIST-TAREAS`
   - marca `Estado=Completada` en `INX-ENLACES`
   - con `--sync`, reconcilia los espejos para que un sync posterior no reviva la fila como `Activo`

## Checklist ejecutable

### Paso 1 — Promover checkboxes pendientes

```bat
python tools/promote_notas_checkboxes_to_todoist.py "<nota>" --sync
```

Output esperado:

```text
[created] L<n> todoist:<id> | <descripcion>
Resumen: N tarea(s) creada(s) desde <ruta>
```

### Paso 2 — Cerrar checkboxes ya hechos

```bat
python tools/close_obsidian_checkboxes_to_todoist.py "<nota>" --sync
```

Output esperado:

```text
[closed] L<n> todoist:<id>
Resumen: N tarea(s) cerrada(s) desde <ruta>
```

### Paso 3 — Validar el caso completo

```bat
apps\validate_case_10.bat --no-pause
```

Lectura esperada:

- `Markers con fila INX: N/N`
- `TODOIST_DB_TAREAS con Estado=Completada: M/M`
- `INX con Estado=Completada: M/M`

## Postcondiciones

- Cada línea promovida tiene marker `todoist:<id>`.
- Cada marker tiene fila `todoist:<id>` en INX.
- Cada checkbox cerrado con marker refleja `Estado=Completada` en `TODOIST-TAREAS`.
- Cada checkbox cerrado con marker refleja `Estado=Completada` en INX.

## Criterios de aceptación

- [x] `tools/promote_notas_checkboxes_to_todoist.py` crea tareas Todoist desde `- [ ]`.
- [x] La reescritura añade marker inline `<!-- todoist:<id> -->`.
- [x] Reejecución de captura es idempotente.
- [x] `tools/close_obsidian_checkboxes_to_todoist.py` detecta `- [x] ... <!-- todoist:<id> -->` y cierra la tarea.
- [x] `TODOIST-TAREAS` refleja `Estado=Completada` tras el cierre.
- [x] `INX-ENLACES` refleja `Estado=Completada` para `todoist:<id>`.
- [x] `tools/validate_case_10.py --scope all` valida captura + cierre.
- [x] `apps/validate_case_10.bat` ejecuta la validación completa.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Capturar checkboxes a Todoist | `python tools/promote_notas_checkboxes_to_todoist.py <nota> [--sync]` |
| Cerrar tareas desde checkboxes marcados | `python tools/close_obsidian_checkboxes_to_todoist.py <nota> [--sync]` |
| Wrapper Windows de cierre | `apps\close_obsidian_checkboxes_to_todoist.bat "<nota>" --sync` |
| Validación completa | `python tools/validate_case_10.py --scope all` |
| Validación Windows | `apps\validate_case_10.bat --no-pause` |

## Observabilidad

- El vault es la fuente primaria; los markers viven en el `.md`.
- `TODOIST-TAREAS` permite ver el espejo de estado.
- `INX-ENLACES` permite ver la fila `todoist:<id>` con `Estado`.

## Gaps pendientes

- **Gap 1 — Sin batch `--all`**: captura y cierre siguen operando nota por nota.
- **Gap 2 — Cruce explícito en INX**: `obsidian:<ruta>` y `todoist:<id>` siguen siendo filas separadas.
- **Gap 3 — Sin `--project` en captura**: las tareas nuevas siguen naciendo en inbox.
- **Gap 4 — Cleanup de fixtures / borrados**: si se elimina una nota, la limpieza de filas derivadas sigue siendo manual.

## Mejoras propuestas

- **Mejora 1 — Batch del vault**: `--all` para captura y cierre.
- **Mejora 2 — Proyecto Todoist por ruta o flag**: `--project <name>`.
- **Mejora 3 — Relación explícita en INX**: vincular `obsidian:<ruta>` con `todoist:<id>` más allá del contexto compartido.
- **Mejora 4 — Limpieza de huérfanos Todoist/Obsidian**: script idempotente de cleanup.

## Fallos típicos

- **`Nota no encontrada`**: nombre mal escrito o nota fuera de `OBSIDIAN_ALPHA_PATH`.
- **Sync incompleto tras captura**: falta ejecutar `sync_todoist_to_notion.py`, requisito para que INX vea la tarea.
- **Timeout en sync Todoist → INX**: el refresh completo puede ser lento; reintentar `python tools/sync_inx_links.py --source todoist --limit 200`.
- **INX sin `Completada`**: resolver con `python tools/ensure_inx_completed_status.py`.

## Validación práctica

```bat
python tools/validate_case_10.py --scope all
```

El caso 10 queda validado cuando:

- `Markers con fila INX: N/N`
- `TODOIST_DB_TAREAS con Estado=Completada: M/M`
- `INX con Estado=Completada: M/M`
- Exit 0
