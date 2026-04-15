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

## Automatización actual

- Un solo comando:

```bash
.\.venv\Scripts\python.exe agents/orchestrator_agent.py inx-sync --limit 200
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

## Gaps (lo que falta hoy)

- No existe un “doctor” que haga auditoría de coherencia (p.ej. filas INX sin `URL` o sin relaciones cuando deberían).
- No hay scheduling integrado (tarea programada en Windows) ni reporte resumido diario.

## Mejoras propuestas (acciones)

- `apps/inx_doctor.py`: chequeos de calidad y reporte:
  - duplicados por `Clave`
  - `Fuente` sin campos mínimos (`Todoist ID` vacío, `Obsidian Ruta` vacía, etc.)
  - relaciones vacías para claves que deberían tener PTN (según reglas)
- `apps/inx_daily.bat`: wrapper para correr `inx-sync` y luego `inx_doctor` y guardar un resumen en `artifacts/`.
