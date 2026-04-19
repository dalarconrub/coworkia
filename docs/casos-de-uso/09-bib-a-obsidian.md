# Caso de uso: Paper BIB ↔ ficha de lectura en Obsidian (con cruce INX)

## Objetivo

Dado un paper catalogado en BIB (`NOTION_DB_BIB`), crear una ficha de lectura `.md` bajo el vault ABGD y dejar el cruce `obsidian:<ruta>` ↔ `paperpile:<citekey>` reflejado en INX.

Además, cerrar el loop bidireccional mínimo:

- **BIB → Obsidian**: promoción del paper a ficha
- **Obsidian → BIB**: sincronización de `estado-lectura` desde frontmatter hacia `BIB.Estado`

## Actores

- **Usuario**: David
- **Sistema(s)**: Notion (BIB, INX), Obsidian

## Trigger

David decide leer un paper activamente y quiere:

1. una ficha editable en el vault
2. que el progreso de lectura quede reflejado en el catálogo BIB sin editarlo manualmente

## Precondiciones

- `.env` con:
  - `NOTION_DB_BIB`
  - `NOTION_DB_INX`
  - `OBSIDIAN_ALPHA_PATH`
  - `OBSIDIAN_ABGD_ROOT`
- El paper ya existe en BIB.
- La estructura del vault contiene `A1-INV/B13-PUB/{C137-ART,C138-COM,C139-REV}`.

## Fuente de verdad

- **Metadata bibliográfica**: BIB / Paperpile
- **Contenido vivo de lectura**: Obsidian
- **Estado de lectura canónico**: BIB, sincronizado desde el frontmatter de la ficha
- **Trazabilidad cruzada**: INX

## Contrato

### Claves canónicas en INX

| Entidad | Clave |
| --- | --- |
| Paper en BIB | `paperpile:<citekey>` |
| Ficha de lectura | `obsidian:<ruta_relativa>` |

### Campo explícito en filas `obsidian:*`

- `Paperpile Citekey`: rich_text con el `citekey` leído desde el frontmatter real de la nota.
- Se puebla durante `sync_inx_links.py --source obsidian`.
- Hace explícito el vínculo entre la fila `obsidian:<ruta>` y la entidad `paperpile:<citekey>` sin tener que inferirlo solo por contexto.

### Frontmatter mínimo de la ficha

```yaml
---
citekey: Candido2026y
bib-id: 346622cf-315b-81e7-a92d-d46389d53103
doi: ""
anio: ""
autores: Yasmin Santos Candido, Elton Bicalho de Souza
tipo: Artículo
journal: ""
estado-lectura: Por leer
---
```

### Estados soportados para `estado-lectura`

- `Por leer`
- `En proceso`
- `Leído`
- `Revisado`
- `Descartado`

Alias aceptados en el sync:

- `Leyendo` → `En proceso`
- `Leido` → `Leído`

## Flujo principal

### Fase A — Promoción BIB → Obsidian

```bat
python tools/promote_bib_to_obsidian.py <citekey> --sync
```

Efecto:

- crea la ficha `.md`
- deja frontmatter con `citekey`, `bib-id` y `estado-lectura`
- sincroniza cruce `obsidian:*` + `paperpile:*` en INX

### Fase A2 — Promoción masiva de pendientes

```bat
python tools/promote_bib_to_obsidian.py --all-pending --dry-run --limit 10
```

Efecto:

- revisa papers con `BIB.Estado = Por leer`
- detecta cuáles ya tienen ficha en el contexto elegido
- en `--dry-run` solo informa
- sin `--dry-run`, crea las fichas faltantes

Flags útiles:

- `--limit N`: acota el batch
- `--query TEXTO`: filtra por citekey, título, autores, journal o año
- `--year AAAA`: filtra por año exacto
- `--author AUTOR`: filtra por substring en autores
- `--journal REVISTA`: filtra por substring en journal
- `--estado ESTADO`: permite batch sobre un estado concreto; si no se indica, el default operativo sigue siendo `Por leer`
- `--contexto C137-ART|C138-COM|C139-REV`
- `--force`: regenera aunque ya exista ficha
- `--sync`: corre el pipeline INX al final del batch

Nota operativa:

- En batch, `--sync` lanza `sync_inx_links` completo para `obsidian` y `paperpile`, sin `--limit`, porque un recorte fijo puede dejar fuera citekeys recién promovidos y romper la validación del caso.

### Fase B — Sync estado-lectura Obsidian → BIB

```bat
python tools/sync_bib_reading_state.py
```

Efecto:

- escanea fichas bajo `A1-INV/B13-PUB/*`
- lee `citekey` + `estado-lectura`
- actualiza `BIB.Estado` cuando hay diferencia

### Fase C — Validación completa

```bat
apps\validate_case_09.bat --no-pause
```

Valida:

- cruce doble `obsidian:*` + `paperpile:*`
- alineación entre `estado-lectura` y `BIB.Estado`

## Variantes

- **Otro contexto**: `--contexto C138-COM` o `C139-REV`
- **Sobrescribir ficha existente**: `--force`
- **Sync en seco**: `python tools/sync_bib_reading_state.py --dry-run`

## Checklist ejecutable

### Paso 1 — Promover paper a ficha

```bat
python tools/promote_bib_to_obsidian.py <citekey> --sync
```

- [ ] Output: `created: N<YYMMDD>-<citekey>.md (<citekey>) bib-id=<id>`

### Paso 1b — Preview de promoción masiva

```bat
python tools/promote_bib_to_obsidian.py --all-pending --dry-run --limit 10
```

- [ ] Output: `Candidatos revisados: N`
- [ ] Output: `Crearia: X`
- [ ] Output: `Saltaria: Y`

Ejemplos más finos:

```bat
python tools/promote_bib_to_obsidian.py --all-pending --dry-run --query eating --limit 10
python tools/promote_bib_to_obsidian.py --all-pending --dry-run --year 2024 --limit 10
python tools/promote_bib_to_obsidian.py --all-pending --dry-run --author Candido --limit 10
python tools/promote_bib_to_obsidian.py --all-pending --dry-run --journal Body --limit 10
```

### Paso 2 — Editar progreso de lectura

Cambiar en la ficha:

```yaml
estado-lectura: En proceso
```

o cualquier estado soportado.

### Paso 3 — Sincronizar estado a BIB

```bat
python tools/sync_bib_reading_state.py
```

- [ ] Output con `Cambios requeridos: N`
- [ ] Output final `OK: cambios aplicados: N`

### Paso 4 — Validar caso completo

```bat
apps\validate_case_09.bat --no-pause
```

- [ ] `CRUCE DOBLE (obsidian:* AND paperpile:*): N/N`
- [ ] `Mismatch frontmatter vs BIB: 0`

## Postcondiciones

- La ficha existe bajo `A1-INV/B13-PUB/<contexto>/N<YYMMDD>-<citekey>.md`
- Existe fila `obsidian:<ruta>` en INX
- La fila `obsidian:<ruta>` expone `Paperpile Citekey=<citekey>`
- Existe fila `paperpile:<citekey>` en INX
- `BIB.Estado` coincide con `estado-lectura` de la ficha

## Criterios de aceptación

- [x] `tools/promote_bib_to_obsidian.py` crea ficha con frontmatter y secciones
- [x] `tools/promote_bib_to_obsidian.py --all-pending` soporta batch sobre `Estado=Por leer`
- [x] `--sync` encadena log + sync obsidian + sync paperpile
- [x] `tools/validate_case_09.py` valida cruce doble
- [x] `INX obsidian:*` expone `Paperpile Citekey` explícito
- [x] `tools/sync_bib_reading_state.py` sincroniza `estado-lectura` hacia BIB
- [x] `tools/validate_case_09.py --scope all` valida también alineación de estado
- [x] `apps/validate_case_09.bat` usa la validación completa

## Automatización actual

| Acción | Comando |
| --- | --- |
| Promover BIB a ficha | `python tools/promote_bib_to_obsidian.py <citekey> [--contexto <C>] [--force] [--sync]` |
| Preview batch de pendientes | `python tools/promote_bib_to_obsidian.py --all-pending --dry-run [--limit N] [--query TEXTO] [--year AAAA] [--author AUTOR] [--journal REVISTA] [--estado ESTADO] [--contexto <C>]` |
| Batch real de pendientes | `python tools/promote_bib_to_obsidian.py --all-pending [--limit N] [--query TEXTO] [--year AAAA] [--author AUTOR] [--journal REVISTA] [--estado ESTADO] [--contexto <C>] [--sync]` |
| Sync estado lectura → BIB | `python tools/sync_bib_reading_state.py [--dry-run]` |
| Wrapper Windows del sync | `apps\sync_bib_reading_state.bat` |
| Validación completa | `python tools/validate_case_09.py --scope all` |
| Validación Windows | `apps\validate_case_09.bat --no-pause` |

## Observabilidad

- `NOTION_DB_BIB`: catálogo y estado de lectura
- Vault `A1-INV/B13-PUB/*`: fichas
- `INX-ENLACES`: filas `obsidian:*` y `paperpile:*`
- `artifacts/obsidian_log_state.json`: mtime del log Obsidian

## Gaps pendientes

- **Gap 1 — Estado solo via frontmatter**: no hay write-back desde BIB a la ficha; el flujo actual asume que la edición viva ocurre en Obsidian

## Mejoras propuestas

- **Mejora 1 — Sync inverso BIB → frontmatter**: si el estado cambia en Notion, reflejarlo también en Obsidian

## Fallos típicos

- `Paper con citekey X no encontrado en BIB`: citekey mal escrito o BIB desactualizado
- `estado-lectura` inválido: usa una variante no soportada
- `Mismatch frontmatter vs BIB`: falta correr `python tools/sync_bib_reading_state.py`
- `0 fichas detectadas`: todavía no se ha promovido ninguna

## Validación práctica

```bat
python tools/validate_case_09.py --scope all
```

El caso 09 queda validado cuando:

- hay al menos una ficha
- cada ficha matchea BIB + INX `obsidian:*` + INX `paperpile:*`
- `Mismatch frontmatter vs BIB: 0`
- exit code `0`
