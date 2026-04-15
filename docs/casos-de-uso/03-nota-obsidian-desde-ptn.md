# Caso de uso: Crear nota Obsidian desde PTN y dejarla enlazada (INX)

## Objetivo

Crear una nota (`.md`) en Obsidian asociada a un **proyecto o tarea PTN**, y dejar **trazabilidad** en Notion (`OBSIDIAN_DB` + `INX-ENLACES`) para poder navegar entre PTN, el documento y el resto del puente INX.

## Actores

- **Usuario**: David
- **Sistema(s)**: Obsidian (documento), Notion (PTN, `OBSIDIAN_DB`, `INX-ENLACES`)

## Trigger

Un proyecto o tarea PTN requiere **pensamiento extendido**, documentación, decisiones o borradores que no caben solo en Notion/Todoist.

## Precondiciones

- `.env` con:
  - `OBSIDIAN_ABGD_ROOT`, `OBSIDIAN_ALPHA_PATH` (vault ABGD accesible)
  - `OBSIDIAN_DB` (base log en Notion)
  - `NOTION_DB_INX`
  - Variables PTN si vas a relacionar desde INX: `NOTION_DS_PROYECTOS` / tareas / notas según tu flujo

## Fuente de verdad (autoridad)

- **Contenido y ruta del documento**: Obsidian
- **Metadatos y relaciones tácticas**: Notion (PTN + log Obsidian + INX)

## Contrato INX (clave canónica)

- Para una nota por ruta relativa al vault Alpha: **`Clave=obsidian:<ruta_relativa>`** (como en `sync_inx_links`).
- La fila puede llevar **Area / Bloque / Contexto** si el path sigue ABC y **relaciones PTN** si existen en la fila fuente del log `OBSIDIAN_DB`.

## Flujo principal (happy path)

1. En Notion PTN, tener claro el **proyecto o tarea** objetivo (IDs o enlaces).
2. Crear o editar un `.md` en Obsidian bajo la jerarquía ABC (Alpha).
3. Ejecutar el **log** Obsidian → Notion (`OBSIDIAN_DB`).
4. Ejecutar sync **INX** desde fuente Obsidian para upsert en `INX-ENLACES`.
5. En Notion, completar si hace falta la **relación PTN** en la fila de `OBSIDIAN_DB` o en `INX-ENLACES` (según tu schema), y verificar.

## Checklist ejecutable (v2)

### Paso 0 — Log de cambios Obsidian → Notion

```bat
.\.venv\Scripts\python.exe tools\log_obsidian_changes.py
```

(o desde la raíz con venv ya activo)

### Paso 1 — Crear / guardar la nota en Obsidian

- [ ] Ruta bajo Alpha coherente con ABC (carpetas = área/bloque/contexto cuando aplique).
- [ ] Guardar el archivo para que el log detecte `mtime`.

### Paso 2 — Propagar a INX (solo fuente Obsidian)

```bat
apps\inx_sync_obsidian.bat 200 --no-pause
```

### Paso 3 — (Opcional) Cadena INX completa

Si además quieres refrescar Todoist + logs PTN + Obsidian + INX:

```bat
.\.venv\Scripts\python.exe agents\orchestrator_agent.py inx-sync --limit 200
```

### Paso 4 — Verificación

- [ ] En **`OBSIDIAN_DB`**: entrada reciente con **Ruta** relativa y **Evento** / título coherente.
- [ ] En **`INX-ENLACES`**: fila con prefijo **`obsidian:`** en **Clave** (o búsqueda por **Obsidian Ruta**).
- [ ] Relaciones **ABC** o **PTN** presentes si las configuraste en el log o manualmente.

## Postcondiciones / Resultado verificable

- Archivo `.md` existente en el vault con ruta estable.
- Entrada en `OBSIDIAN_DB` tras `log_obsidian_changes`.
- Fila en `INX-ENLACES` para esa ruta (tras `sync_inx_links --source obsidian`).

## Criterios de aceptación (Definition of Done)

- [ ] La ruta en Notion coincide con la ruta real del archivo (relativa).
- [ ] `INX-ENLACES` refleja la fila sin duplicar `Clave` para la misma ruta.
- [ ] `artifacts\obsidian_log_state.json` avanza (no se queda “atascado” en el tiempo si editas de nuevo).

## Automatización actual

| Acción | Comando |
| --- | --- |
| Log Obsidian → Notion | `python tools/log_obsidian_changes.py` |
| INX solo desde Obsidian | `apps\inx_sync_obsidian.bat` |
| Cadena INX completa | `python agents/orchestrator_agent.py inx-sync` |

## Observabilidad

- `artifacts/obsidian_log_state.json` — estado del detector por `last_mtime`.
- `INX-ENLACES` — filas `Clave` con prefijo `obsidian:`.

## Gaps (pendientes)

- Enlace `obsidian://` en propiedad **URL** de INX (convención por definir).
- Comando único **link-obsidian-to-ptn** (crear/relacionar fila INX con PTN en un paso).

## Mejoras ya implementadas / alineadas

- `log_obsidian_changes.py` crea filas con ABC por ruta y tipo Nota.
- `sync_inx_links.py` upsertea desde `OBSIDIAN_DB` hacia `INX-ENLACES`.

## Fallos típicos

- **No aparece entrada en el log**: ruta fuera de Alpha, vault mal en `.env`, o archivo no guardado.
- **INX vacío para Obsidian**: no ejecutaste `sync_inx_links` o falta `NOTION_DB_INX` / permisos.

## Validación práctica (opcional, una vez)

Para comprobar el flujo con una nota real:

1. Ejecuta el validador (hace log Obsidian → Notion, sync INX desde Obsidian y genera informe):

   ```bat
   apps\validate_case_03.bat --no-pause
   ```

2. El caso 3 queda **validado** cuando el informe muestra:
   - `OBSIDIAN_DB ... Con Ruta: N` (N > 0)
   - `Rutas OBSIDIAN_DB presentes en INX: N/N`
