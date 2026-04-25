# Caso de uso: Sync diario y verificación de coherencia (INX)

## Objetivo

Ejecutar una rutina diaria que mantenga **coherencia mínima** entre Todoist, Notion y Obsidian, y que deje `INX-ENLACES` actualizado para navegación cruzada.

## Actores

- **Usuario**: David
- **Sistema(s)**: Todoist, Notion, Obsidian

## Trigger

Inicio del día / cierre del día / antes de planificar.

## Precondiciones

- `.env` completo:
  - Todoist: `TODOIST_API_KEY`
  - Notion: `NOTION_TOKEN`, `TODOIST_DB_TAREAS`, `NOTION_DB`, `OBSIDIAN_DB`, `NOTION_DB_INX`
  - PTN: `NOTION_DS_PROYECTOS`, `NOTION_DS_TAREAS`, `NOTION_DS_NOTAS`

## Fuente de verdad (autoridad)

- Cambios de MAR: Todoist
- Cambios de PTN: Notion
- Cambios de documentos: Obsidian
- Trazabilidad: `INX-ENLACES`

## Flujo principal (happy path)

1. Sincronizar Todoist → Notion (`TODOIST-TAREAS`).
2. Log de cambios PTN → Notion (`NOTION_DB`).
3. Log de cambios Obsidian → Notion (`OBSIDIAN_DB`).
4. Upsert de `INX-ENLACES` desde las tres fuentes.
5. Revisar métricas de salud (duplicados, faltan relaciones, enlaces rotos).

### Variante MAR inmediata

Cuando solo han cambiado tareas en Todoist, basta con la cadena corta:

```bash
.\.venv\Scripts\python.exe tools\sync_todoist_to_notion.py --limit 200
.\.venv\Scripts\python.exe tools\sync_inx_links.py --source todoist --limit 200
```

La primera orden actualiza el espejo `TODOIST-TAREAS`; la segunda propaga o
actualiza filas `todoist:<id>` en `INX-ENLACES`. El sync Todoist excluye `Z-*`,
por lo que el origen operativo normal es el `Inbox` real y los proyectos A/B.

## Automatización actual

- Comando mínimo de sync:

```bash
.\.venv\Scripts\python.exe agents/orchestrator_agent.py inx-sync --limit 200
```

- Comando diario recomendado (sync + doctor + artefacto):

```bash
.\.venv\Scripts\python.exe apps/inx_daily.py --limit 200 --allow-missing-ptn
```

## Atajos Windows (recomendados)

Si quieres correr la cadena por partes (para entender qué se actualiza):

```bat
apps\sync_todoist_to_notion.bat 200 --no-pause
apps\log_ptn_changes.bat --no-pause
apps\inx_sync_notion.bat 200 --no-pause
apps\inx_sync_obsidian.bat 200 --no-pause
```

## Postcondiciones / Resultado verificable

- `TODOIST-TAREAS` actualizado.
- `INX-ENLACES` actualizado con `Estado=Activo` en nuevas filas.
- Los logs avanzan (si hubo cambios).

## Observabilidad

- Salida del comando (contadores).
- `INX-ENLACES`: filtrar por `Estado=Activo` y comprobar fuentes.
- `artifacts/*_state.json`: estado de los logs.

## Estado actual

- Existe `apps/inx_doctor.py` para auditar:
  - duplicados por `Clave`
  - campos mínimos ausentes según la `Fuente`
  - filas sin relación PTN
  - huérfanos de `GIT` y `BIB`
- Existe `apps/inx_daily.py` y `apps\inx_daily.bat` para ejecutar `inx-sync`, pasar el doctor y guardar un informe en `artifacts/inx/`.
- Sigue sin haber scheduling integrado en Windows; el wrapper ya deja el flujo preparado para programarlo.

Validación técnica realizada el `2026-04-17`:

- `apps/inx_daily.py --limit 200 --allow-missing-ptn` generó el artefacto:
  - `artifacts/inx/inx-daily-20260417-072710.md`
- Resultado del artefacto:
  - `sync=0`
  - `doctor=1`
- Sync observado:
  - `Tareas sincronizadas: 77`
  - `Entradas de log PTN creadas: 4`
  - `Entradas de log Obsidian creadas: 0`
  - `INX enlaces sincronizados: todoist=200 notion=15 obsidian=28 github=113 paperpile=0`
- Hallazgos del doctor:
  - `Claves duplicadas: 0`
  - `Campos mínimos ausentes: 232`
  - `Filas sin relación PTN: 574`
  - `GIT huérfanos: 0`
  - `BIB huérfanos: 0`

Lectura operativa:

- La rutina diaria completa funciona y deja artefacto reproducible.
- El fallo actual del doctor no viene del pipeline, sino de calidad de datos en `INX-ENLACES`, especialmente filas Todoist heredadas sin `Estado`.

## Mejoras propuestas (acciones)

- Añadir una tarea programada en Windows que ejecute:

```bat
apps\inx_daily.bat 200
```

- Ajustar reglas de severidad del doctor si algunas fuentes deben tolerar ausencia de relación PTN.
- Rellenar o normalizar `Estado` en filas antiguas de `INX-ENLACES` para que el doctor deje de fallar por `falta Estado`.
