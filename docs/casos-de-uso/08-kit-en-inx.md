# Caso de uso: KIT como ciudadano de primera en INX (alcances B/C)

## Objetivo

Que cada entrada del catálogo **KIT** (`NOTION_DB_KIT`) aparezca en `INX-ENLACES` con clave canónica `kit:<page_id>`, homologándola al resto de sistemas (PTN, Obsidian, GitHub, Paperpile, Todoist).

Además, en alcance **C**, que las notas del vault Obsidian puedan declarar referencias a KIT con wikilinks `[[kit:<page_id>]]`, que esa relación quede persistida de forma estable en `OBSIDIAN_DB` e `INX-ENLACES`, y que haga write-back a KIT para navegar qué notas Obsidian usan cada entrada.

## Alcance

- **Alcance B**: KIT primera clase en INX.
- **Alcance C**: persistencia textual + relation real de referencias `[[kit:<page_id>]]` desde Obsidian a `OBSIDIAN_DB` / `INX-ENLACES`, con write-back a `KIT.Usada en notas`.
- **Fuera de alcance**: eliminar `KIT IDs` textual o refactorizar el campo legacy `Usada en` no relacionado con Obsidian.

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
  - `Fuente = KIT`
  - `Estado = Activo`
  - `URL = Enlace` si existe
  - `Detalle = Tipo | Subtipo` si existen

No hay relation a KIT en el schema de INX. Se mantiene el patrón de clave canónica textual, igual que `github:<repo>` y `paperpile:<citekey>`.

## Contrato Obsidian ↔ KIT alcance C

- Una nota puede citar entradas KIT con `[[kit:<page_id>]]`.
- `log_obsidian_changes.py` y `backfill_obsidian_to_inx.py` extraen esos IDs, los guardan en `OBSIDIAN_DB.KIT IDs` y, si el schema ya está preparado, también rellenan `OBSIDIAN_DB.KIT` como `relation`.
- `sync_inx_links.py --source obsidian` propaga ese dato a `INX-ENLACES.KIT IDs` y `INX-ENLACES.KIT` para la fila `obsidian:<ruta>`.
- `sync_inx_links.py --source kit|obsidian` hace write-back inverso a `KIT.Usada en notas` con relaciones a filas de `OBSIDIAN_DB`.
- El formato textual `KIT IDs` se mantiene por compatibilidad y auditoría; la navegación operativa pasa por relations.

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

- [ ] `OBSIDIAN_DB`: propiedades `KIT IDs` y `KIT` creadas o ya existentes
- [ ] `NOTION_DB_INX`: propiedades `KIT IDs` y `KIT` creadas o ya existentes
- [ ] `NOTION_DB_KIT`: propiedad `Usada en notas` creada o ya existente
- [ ] `INX-ENLACES.Fuente` acepta opcion `KIT`

### Paso 4 — Persistir metadata de notas Obsidian

```bat
python tools/backfill_obsidian_to_inx.py --sync
```

- [ ] Las filas nuevas de `OBSIDIAN_DB` pueden incluir `KIT IDs` y `KIT`
- [ ] El sync de Obsidian copia `KIT IDs` / `KIT` a `INX-ENLACES`
- [ ] El sync actualiza `KIT.Usada en notas`

### Paso 5 — Validación alcance C

```bat
python tools/validate_case_08.py --scope c
```

- [ ] Output: `OK: las referencias KIT detectadas en OBSIDIAN_DB se preservan en INX.`

## Postcondiciones

- Por cada fila con `Titulo` no vacío en `NOTION_DB_KIT`, existe una fila en `INX-ENLACES` con `Clave = kit:<page_id>` y `Fuente = KIT`.
- Si una nota Obsidian contiene `[[kit:<page_id>]]`, ese dato queda persistido en `OBSIDIAN_DB.KIT IDs` y, con schema preparado, en `OBSIDIAN_DB.KIT`.
- Tras `sync_inx_links --source obsidian`, la fila `obsidian:<ruta>` correspondiente refleja el mismo valor en `INX-ENLACES.KIT IDs` y `INX-ENLACES.KIT`.
- Tras `sync_inx_links --source obsidian` o `--source kit`, cada entrada KIT enlazada actualiza `Usada en notas` con las filas `OBSIDIAN_DB` que la citan.

## Criterios de aceptación

- [x] `sync_inx_links.py` soporta `--source kit`.
- [x] Cada entrada KIT con título produce una fila `kit:<page_id>` en INX.
- [x] `tools/validate_case_08.py` cubre el alcance B.
- [x] `tools/ensure_kit_cross_fields.py` asegura el schema de alcance C.
- [x] `log_obsidian_changes.py` y `backfill_obsidian_to_inx.py` persisten `KIT IDs`.
- [x] `sync_inx_links.py --source obsidian` propaga `KIT IDs` a INX.
- [x] Relation real Obsidian ↔ KIT materializada en `OBSIDIAN_DB` e `INX-ENLACES`.
- [x] Write-back inverso a `KIT.Usada en notas`.

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
- `OBSIDIAN_DB`: log del vault con columnas `KIT IDs` + `KIT`
- `INX-ENLACES`: filas `kit:*` y filas `obsidian:*` con `KIT IDs` + `KIT`
- `NOTION_DB_KIT`: columna `Usada en notas`

## Gaps pendientes

- **Gap 1 — [RESUELTO] relation real**: el alcance C mantiene `KIT IDs` textual para auditoría, pero ya materializa `relation` en `OBSIDIAN_DB.KIT` e `INX-ENLACES.KIT`.
- **Gap 2 — [RESUELTO] write-back a KIT**: las referencias desde Obsidian actualizan `KIT.Usada en notas` como relation dedicada, sin romper el campo legacy `Usada en`.
- **Gap 3 — [RESUELTO] `Fuente=KIT`**: INX ya distingue `kit:*` con `Fuente = KIT`.

## Mejoras propuestas

- **Mejora 1 — tabla puente real**: si el volumen crece, sustituir la relation N-N implícita por una tabla puente dedicada de menciones.
- **Mejora 2 — dedupe de write-back**: si en el futuro hay varias filas `OBSIDIAN_DB` por la misma ruta, consolidar primero el log antes del write-back a KIT.
- **Mejora 3 — navegación UI**: añadir vistas Notion prefiltradas para `KIT usados en notas` y `Notas con referencias KIT`.

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
