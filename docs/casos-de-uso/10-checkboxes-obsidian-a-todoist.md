# Caso de uso: Checkboxes de nota Obsidian → tareas Todoist (con cruce INX)

## Objetivo

Convertir **checkboxes sueltos** (`- [ ] ...`) dentro de una nota Obsidian en **tareas Todoist** reales, dejando la línea original marcada con el `id` devuelto para que no se duplique en re-ejecuciones. Cada captura produce cruce INX `obsidian:<ruta>` + `todoist:<id>`.

Caso inverso a los habituales (MAR ya sincroniza hacia Notion). Aquí el pensamiento vivo de la nota — "hay que hacer X" — se ejecuta como tarea formal sin copiarla manualmente a Todoist.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (vault), Todoist (API), Notion (INX-ENLACES)

## Trigger

Mientras escribes una nota (reunión, análisis, diario), surgen pendientes concretos como:
```markdown
- [ ] Pedir dataset a Fran
- [ ] Revisar R-script del análisis GLM
```
Pasarlos a Todoist rompe el flujo. Este caso lo automatiza: guardas la nota → corres un comando → las líneas quedan marcadas con el `id` de cada tarea creada.

## Precondiciones

- `.env` con:
  - `TODOIST_API_TOKEN`
  - `OBSIDIAN_ALPHA_PATH`
  - `NOTION_DB_INX`, `TODOIST_DB_TAREAS` (para el `--sync`)
- Nota ya guardada en el vault (con `mtime` reciente).

## Fuente de verdad (autoridad)

- **Captura y redacción original**: Obsidian (la nota).
- **Ejecución y estado de la tarea**: Todoist.
- **Trazabilidad cruzada**: `INX-ENLACES`.

## Contrato

- **Marker inline**: cada checkbox capturado queda re-escrito como
  ```
  - [ ] Descripcion <!-- todoist:<task_id> -->
  ```
  Este comentario HTML es invisible en Obsidian render y sirve como ancla idempotente.
- **Clave INX Todoist**: `todoist:<id>` (ya la genera `sync_inx_links --source todoist`).
- **Clave INX Obsidian**: `obsidian:<ruta>` (ya la genera `sync_inx_links --source obsidian`).
- **Cruce**: por dos filas INX separadas que comparten contexto (sin columna dedicada hoy).

## Flujo principal (happy path)

1. Escribe tu nota normalmente; deja los pendientes como `- [ ] ...` sin marker.
2. Guarda la nota en el vault.
3. Promueve:
   ```bat
   python tools/promote_notas_checkboxes_to_todoist.py "<nombre-nota>" --sync
   ```
   (o `apps\promote_notas_checkboxes_to_todoist.bat "<nombre>" --sync` desde Windows).
4. El script:
   - Crea una tarea Todoist por línea `- [ ]` sin marker.
   - Re-escribe la nota añadiendo `<!-- todoist:<id> -->` al final de cada línea capturada.
   - Con `--sync`: dispara `log_obsidian_changes` + `sync_todoist_to_notion` + `sync_inx_links obsidian` + `sync_inx_links todoist`. El paso `sync_todoist_to_notion` es **imprescindible** porque `_sync_todoist` lee de `TODOIST_DB_TAREAS` (espejo Notion), no de la API Todoist directa; sin él, las tareas recién creadas no aparecen en INX.
5. Verifica con:
   ```bat
   apps\validate_case_10.bat --no-pause
   ```

## Variantes

- **A. Re-ejecución segura**: si corres el promote dos veces sobre la misma nota, el regex ignora las líneas que ya tienen marker. Solo procesa checkboxes nuevos.
- **B. Sin sync**: omite `--sync` si vas a sincronizar INX más tarde por separado.
- **C. Varias notas**: el script procesa una nota por invocación. Para batch: bucle externo o futuro flag `--all`.

## Checklist ejecutable

### Paso 1 — Promover checkboxes

```bat
.\.venv\Scripts\python.exe tools\promote_notas_checkboxes_to_todoist.py "<nombre-nota>" --sync
```

Output esperado:
```
[created] L<n> todoist:<id> | <descripcion>
...
Resumen: N tarea(s) creada(s) desde <ruta>
[sync] tools/log_obsidian_changes.py
[sync] tools/sync_inx_links.py --source obsidian --limit 200
[sync] tools/sync_inx_links.py --source todoist --limit 200
```

### Paso 2 — Validar

```bat
apps\validate_case_10.bat --no-pause
```

Lectura esperada:
- `Markers con fila INX: N/N`.
- Exit 0 + `OK: todos los markers tienen fila INX todoist:*.`.

## Postcondiciones / Resultado verificable

- Por cada línea `- [ ]` promovida: hay tarea en Todoist con `content = Descripcion` y `description = "Obsidian: <ruta_relativa>"`.
- La nota original ahora incluye `<!-- todoist:<id> -->` al final de cada línea capturada.
- `INX-ENLACES` contiene filas `obsidian:<ruta>` y `todoist:<id>` para la nota y cada tarea capturada.

## Criterios de aceptación (Definition of Done)

- [x] `tools/promote_notas_checkboxes_to_todoist.py` detecta checkboxes sin marker y los convierte en tareas Todoist reales.
- [x] La re-escritura añade el marker `<!-- todoist:<id> -->` inline.
- [x] Re-ejecución es idempotente (líneas con marker se ignoran).
- [x] Flag `--sync` encadena log + sync obsidian + sync todoist.
- [x] `tools/validate_case_10.py` + `apps/validate_case_10.bat` verifican markers vs INX `todoist:*`.
- [x] Validación end-to-end con captura real — ejecutado 2026-04-18 sobre `N251028-borrador` (10 checkboxes → 10 tareas Todoist → 10/10 cruce INX).

## Automatización actual

| Acción | Comando |
| --- | --- |
| Capturar checkboxes de una nota a Todoist | `python tools/promote_notas_checkboxes_to_todoist.py <nota> [--sync]` |
| Desde Windows | `apps\promote_notas_checkboxes_to_todoist.bat "<nota>" --sync` |
| Validación cruce INX | `apps\validate_case_10.bat --no-pause` |

## Observabilidad

- El vault (`OBSIDIAN_ALPHA_PATH`) es la fuente primaria; los markers son visibles en el `.md` original (HTML comment invisible en Obsidian render).
- `INX-ENLACES` — filas `todoist:<id>`.

## Gaps (pendientes)

- **Gap 1 — No refleja checkbox marcado**: si marcas `- [x]` en Obsidian después, la tarea Todoist no se cierra automáticamente. Dirección Obsidian → Todoist de "done" no implementada.
- **Gap 2 — Sin flag `--all`**: procesar todo el vault de una vez requiere bucle externo.
- **Gap 3 — Cruce INX explícito**: `obsidian:<ruta>` y `todoist:<id>` son dos filas separadas. No hay columna dedicada que las enlace.
- **Gap 4 — Sin `--project`**: todas las tareas se crean en el inbox Todoist (sin `project_id`). Para asignar a un proyecto Todoist específico hoy hay que moverlas manualmente.
- **Gap 5 — Descripcion plana**: `description` de la tarea es `Obsidian: <ruta>`. No incluye contexto del proyecto/tarea PTN que vive en la ruta del vault (se podría extraer de ABPC).

## Mejoras propuestas

- **Mejora 1 — Close sync**: script que lee `- [x]` con marker y cierra la tarea Todoist correspondiente via `close_task(task_id)`.
- **Mejora 2 — `--all` / batch**: escanea todo el vault y promueve todos los checkboxes nuevos en una pasada.
- **Mejora 3 — `--project <name>`**: resuelve proyecto Todoist por nombre y lo pasa a `create_task`.
- **Mejora 4 — Metadata ABPC en description**: parsear la ruta y añadir `Area/Bloque/Contexto/Proyecto` a la description de la tarea.

## Fallos típicos

- **`Nota no encontrada`**: nombre con `.md` sobrando, tildes mal codificadas o nota fuera de `OBSIDIAN_ALPHA_PATH`.
- **`Todoist no devolvio id`**: fallo transitorio de red; re-ejecuta. El regex ignora las líneas que ya tienen marker.
- **Re-ejecución doble** sin guardar cambios intermedios: el script detecta markers existentes y los ignora (idempotente).

## Validación práctica

```bat
apps\validate_case_10.bat --no-pause
```

El caso 10 queda **validado** cuando:
- Markers encontrados ≥ 1.
- `Markers con fila INX: N/N`.
- Exit 0 con `OK: todos los markers tienen fila INX todoist:*.`.
