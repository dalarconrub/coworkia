# Caso de uso: KIT como ciudadano de primera en INX (alcance B)

## Objetivo

Que cada entrada del catálogo **KIT** (`NOTION_DB_KIT`) aparezca en `INX-ENLACES` con clave canónica `kit:<page_id>`, homologándola al resto de sistemas (PTN, Obsidian, GitHub, Paperpile, Todoist). Tras este caso, KIT deja de ser el único sistema operativo fuera del puente INX.

Alcance **B** (elegido explícitamente): KIT primera clase en INX. **No** implementa cruce automático Obsidian↔KIT ni migración del `Usada en` (rich_text) a `relation` — eso queda como alcance C en un caso futuro.

## Actores

- **Usuario**: David
- **Sistema(s)**: Notion (KIT, INX-ENLACES)

## Trigger

El catálogo KIT crece y se requiere poder referenciar entradas desde otros sistemas usando la misma notación (`kit:<id>`) que ya usan el resto.

## Precondiciones

- `.env` con:
  - `NOTION_DB_KIT`
  - `NOTION_DB_INX`

## Fuente de verdad (autoridad)

- **Contenido del catálogo**: Notion (`NOTION_DB_KIT`).
- **Trazabilidad**: `INX-ENLACES`.

## Contrato INX (clave canónica)

- **`kit:<page_id>`** (page_id con guiones, tal y como devuelve la API Notion).
- La fila INX lleva: `Elemento = Titulo`, `Fuente = Notion`, `Estado = Activo`, `URL = Enlace` (si existe), `Detalle = Tipo | Subtipo` (si existen).

No hay relation a KIT en el schema de INX-ENLACES. Mantenemos el patrón de "clave canónica como texto" igual que `github:<repo>` y `paperpile:<citekey>`.

## Flujo principal (happy path)

1. El catálogo KIT se edita normalmente desde Notion o con `python agents/kit_agent.py nueva-knowledge/information/tool ...`.
2. Ejecutar sync:
   ```bat
   python tools/sync_inx_links.py --source kit --limit 200
   ```
3. Verificar en `INX-ENLACES`: una fila con `Clave = kit:<page_id>` por cada entrada KIT con título.

## Checklist ejecutable

### Paso 1 — Sync KIT → INX

```bat
.\.venv\Scripts\python.exe tools\sync_inx_links.py --source kit --limit 200
```

- [ ] Output: `INX enlaces sincronizados: kit=N`.

### Paso 2 — Validación

```bat
apps\validate_case_08.bat --no-pause
```

- [ ] Output: `OK: todas las entradas KIT estan reflejadas en INX-ENLACES.`

## Postcondiciones / Resultado verificable

- Por cada fila con `Titulo` no vacío en `NOTION_DB_KIT`, existe exactamente una fila en `INX-ENLACES` con `Clave = kit:<page_id>`.
- La fila INX es idempotente: re-ejecutar `sync_inx_links --source kit` no crea duplicados (el `_upsert` detecta por `Clave`).

## Criterios de aceptación (Definition of Done)

- [x] `sync_inx_links.py` soporta `--source kit` y la opción aparece en `--help`.
- [x] Cada entrada KIT con título produce una fila `kit:<page_id>` en INX-ENLACES.
- [x] `tools/validate_case_08.py` + `apps/validate_case_08.bat` implementados.
- [x] `orchestrator_agent.py inx-sync` incluye `kit` automáticamente (via `--source all`).
- [ ] Cruce automático `obsidian:<ruta>` ↔ `kit:<id>` (fuera de alcance B, queda para alcance C).

## Automatización actual

| Acción | Comando |
| --- | --- |
| Sync KIT → INX | `python tools/sync_inx_links.py --source kit --limit 200` |
| Pipeline de validación | `apps\validate_case_08.bat --no-pause` |
| Cadena INX completa (incluye KIT vía `--source all`) | `python agents/orchestrator_agent.py inx-sync` |

## Observabilidad

- `NOTION_DB_KIT` — catálogo fuente.
- `INX-ENLACES` — filas con prefijo `kit:`.
- No hay log intermedio específico de KIT (a diferencia de PTN con `NOTION_DB` o Obsidian con `OBSIDIAN_DB`): `_sync_kit` lee directo de `NOTION_DB_KIT`.

## Gaps (pendientes)

- **Gap 1 — Cruce automático Obsidian↔KIT**: hoy no hay forma canónica de registrar que una nota `.md` del vault referencia una entrada KIT. Opciones futuras: (a) wikilinks `[[KIT:<titulo>]]` con parser; (b) columna `KIT` (relation) en `OBSIDIAN_DB`; (c) columna `Usada en Notas` (relation) en `NOTION_DB_KIT`. Ver alcance C.
- **Gap 2 — `Usada en` en KIT es rich_text**: mismo anti-patrón que tenía `Proyecto` en PTN-Notas antes del caso 07. Migrar a relation contra `NOTION_DS_NOTAS` cuando se implemente alcance C.
- **Gap 3 — Fuente `KIT` en el select**: `INX-ENLACES.Fuente` tiene opciones `Todoist | Notion | Obsidian | GitHub | Paperpile | Manual`. KIT se registra como `Notion` (porque vive en Notion), pero perdemos distinción. Opcional: añadir opción `KIT` al select.

## Mejoras propuestas

- **Mejora 1 — Alcance C**: caso 08b o nuevo caso que migre `Usada en` a relation en KIT, añada columna `KIT` (relation) a `OBSIDIAN_DB` (o a INX), y extienda `log_obsidian_changes` / `promote_obsidian_to_ptn` para popularla.
- **Mejora 2 — Opción `KIT` en `Fuente`**: script de migración de schema INX para añadir la opción sin perder filas existentes.

## Fallos típicos

- **`kit=0` tras sync**: `NOTION_DB_KIT` vacío o propiedad `Titulo` con nombre distinto. El sync acepta tanto `Titulo` como `Título`.
- **Duplicados kit:***: no deberían ocurrir — `_upsert` matchea por `Clave`. Si aparecen, limpieza manual en Notion.

## Validación práctica

```bat
apps\validate_case_08.bat --no-pause
```

El caso 08 queda **validado** cuando el informe muestra:
- `KIT entries presentes en INX: N/N` con N > 0.
- `OK: todas las entradas KIT estan reflejadas en INX-ENLACES.`
