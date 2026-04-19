# Caso de uso: KIT como ciudadano de primera en INX (alcances B/C)

## Objetivo

Que cada entrada del catálogo **KIT** (`NOTION_DB_KIT`) aparezca en `INX-ENLACES` con clave canónica `kit:<page_id>`, homologándola al resto de sistemas (PTN, Obsidian, GitHub, Paperpile, Todoist).

Además, en alcance **C**, que las notas del vault Obsidian puedan declarar referencias a KIT con wikilinks `[[kit:<page_id>]]` y que esa relación quede persistida de forma estable en `OBSIDIAN_DB` e `INX-ENLACES`.

## Alcance

- **Alcance B**: KIT primera clase en INX.
- **Alcance C**: persistencia textual de referencias `[[kit:<page_id>]]` desde Obsidian a `OBSIDIAN_DB.KIT IDs` y `INX-ENLACES.KIT IDs`.
- **Fuera de alcance**: migrar `Usada en` de KIT a `relation` o crear una relation real Obsidian ↔ KIT en Notion.

## Actores

- **Usuario**: David
- **Sistema(s)**: Notion (KIT, OBSIDIAN_DB, INX-ENLACES), Obsidian

## Trigger

El catálogo KIT crece y se requiere poder:

1. Referenciar entradas desde otros sistemas usando la notación `kit:<id>`.
2. Registrar automáticamente cuándo una nota Obsidian cita una entrada KIT.

## Precondiciones

- `.env` con:
  - `NOTION_DB_KIT`
  - `NOTION_DB_INX`
  - `OBSIDIAN_DB`
  - `OBSIDIAN_ALPHA_PATH`

## Fuente de verdad

- **Contenido del catálogo**: `NOTION_DB_KIT`
- **Registro de notas del vault**: `OBSIDIAN_DB`
- **Trazabilidad cruzada**: `INX-ENLACES`

## Contrato INX alcance B

- Clave canónica: **`kit:<page_id>`**
- La fila INX lleva:
  - `Elemento = Titulo`
  - `Fuente = Notion`
  - `Estado = Activo`
  - `URL = Enlace` si existe
  - `Detalle = Tipo | Subtipo` si existen

No hay relation a KIT en el schema de INX. Se mantiene el patrón de clave canónica textual, igual que `github:<repo>` y `paperpile:<citekey>`.

## Contrato Obsidian ↔ KIT alcance C

- Una nota puede citar entradas KIT con `[[kit:<page_id>]]`.
- `log_obsidian_changes.py` y `backfill_obsidian_to_inx.py` extraen esos IDs y los guardan en `OBSIDIAN_DB.KIT IDs`.
- `sync_inx_links.py --source obsidian` propaga ese mismo valor a `INX-ENLACES.KIT IDs` para la fila `obsidian:<ruta>`.
- El formato actual es texto rico con IDs separados por comas. Es intencionalmente simple e idempotente.

## Flujo principal

1. El catálogo KIT se edita normalmente desde Notion o con `python agents/kit_agent.py ...`.
2. Ejecutar sync de KIT:

```bat
python tools/sync_inx_links.py --source kit --limit 200
```

3. Preparar schema para alcance C:

```bat
python tools/ensure_kit_cross_fields.py
```

4. Registrar o backfillear notas Obsidian:

```bat
python tools/backfill_obsidian_to_inx.py --sync
```

5. Validar alcance B o C:

```bat
python tools/validate_case_08.py
python tools/validate_case_08.py --scope c
```

## Checklist ejecutable

### Paso 1 — Sync KIT → INX

```bat
python tools/sync_inx_links.py --source kit --limit 200
```

- [ ] Output: `INX enlaces sincronizados: kit=N`

### Paso 2 — Validación alcance B

```bat
apps\validate_case_08.bat --no-pause
```

- [ ] Output: `OK: todas las entradas KIT estan reflejadas en INX-ENLACES.`

### Paso 3 — Preparar schema alcance C

```bat
python tools/ensure_kit_cross_fields.py
```

- [ ] `OBSIDIAN_DB`: propiedad `KIT IDs` creada o ya existente
- [ ] `NOTION_DB_INX`: propiedad `KIT IDs` creada o ya existente

### Paso 4 — Persistir metadata de notas Obsidian

```bat
python tools/backfill_obsidian_to_inx.py --sync
```

- [ ] Las filas nuevas de `OBSIDIAN_DB` pueden incluir `KIT IDs`
- [ ] El sync de Obsidian copia `KIT IDs` a `INX-ENLACES`

### Paso 5 — Validación alcance C

```bat
python tools/validate_case_08.py --scope c
```

- [ ] Output: `OK: las referencias KIT detectadas en OBSIDIAN_DB se preservan en INX.`

## Postcondiciones

- Por cada fila con `Titulo` no vacío en `NOTION_DB_KIT`, existe una fila en `INX-ENLACES` con `Clave = kit:<page_id>`.
- Si una nota Obsidian contiene `[[kit:<page_id>]]`, ese dato queda persistido en `OBSIDIAN_DB.KIT IDs`.
- Tras `sync_inx_links --source obsidian`, la fila `obsidian:<ruta>` correspondiente refleja el mismo valor en `INX-ENLACES.KIT IDs`.

## Criterios de aceptación

- [x] `sync_inx_links.py` soporta `--source kit`.
- [x] Cada entrada KIT con título produce una fila `kit:<page_id>` en INX.
- [x] `tools/validate_case_08.py` cubre el alcance B.
- [x] `tools/ensure_kit_cross_fields.py` asegura el schema de alcance C.
- [x] `log_obsidian_changes.py` y `backfill_obsidian_to_inx.py` persisten `KIT IDs`.
- [x] `sync_inx_links.py --source obsidian` propaga `KIT IDs` a INX.
- [ ] Relation real Obsidian ↔ KIT materializada en Notion.
- [ ] Migración de `Usada en` a `relation` en KIT.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Sync KIT → INX | `python tools/sync_inx_links.py --source kit --limit 200` |
| Cadena INX completa | `python agents/orchestrator_agent.py inx-sync` |
| Asegurar schema C | `python tools/ensure_kit_cross_fields.py` |
| Backfill Obsidian con sync | `python tools/backfill_obsidian_to_inx.py --sync` |
| Validar caso 08 alcance B | `python tools/validate_case_08.py` |
| Validar caso 08 alcance C | `python tools/validate_case_08.py --scope c` |

## Observabilidad

- `NOTION_DB_KIT`: catálogo fuente
- `OBSIDIAN_DB`: log del vault con columna `KIT IDs`
- `INX-ENLACES`: filas `kit:*` y filas `obsidian:*` con `KIT IDs`

## Gaps pendientes

- **Gap 1 — relation real**: el alcance C persiste IDs como texto, no como `relation`.
- **Gap 2 — `Usada en` en KIT sigue siendo rich_text**.
- **Gap 3 — `Fuente=KIT` sigue sin existir en el select de INX**; de momento KIT se registra como `Notion`.

## Mejoras propuestas

- **Mejora 1 — relation dedicada**: sustituir `KIT IDs` textual por una relation materializada o una tabla puente.
- **Mejora 2 — migrar `Usada en`**: conectar KIT contra `NOTION_DS_NOTAS`.
- **Mejora 3 — distinguir `Fuente=KIT`**: ampliar el select de INX si la separación semántica aporta valor operativo.

## Fallos típicos

- `kit=0` tras sync: `NOTION_DB_KIT` vacío o propiedad `Titulo` no accesible.
- `KIT IDs` ausente: falta ejecutar `python tools/ensure_kit_cross_fields.py`.
- Mismatch entre `OBSIDIAN_DB` e `INX`: falta ejecutar `python tools/sync_inx_links.py --source obsidian --limit 200`.

## Validación práctica

```bat
python tools/validate_case_08.py
python tools/validate_case_08.py --scope c
```

El caso 08 queda validado cuando:

- `KIT entries presentes en INX: N/N` con `N > 0`
- `OK: todas las entradas KIT estan reflejadas en INX-ENLACES.`
- `OK: las referencias KIT detectadas en OBSIDIAN_DB se preservan en INX.`
