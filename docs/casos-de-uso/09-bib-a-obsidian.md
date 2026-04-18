# Caso de uso: Paper BIB → ficha de lectura en Obsidian (con cruce INX)

## Objetivo

Dado un paper catalogado en BIB (`NOTION_DB_BIB`), crear una **ficha de lectura** `.md` bajo el vault ABGD en `A1-INV/B13-PUB/<contexto>/` con frontmatter que cruza con BIB (`citekey`, `bib-id`, `doi`) y secciones iniciales para resumen, puntos clave, citas y notas propias. Dejar el cruce `obsidian:<ruta>` ↔ `paperpile:<citekey>` reflejado en INX-ENLACES.

Es la **contraparte Obsidian del caso 06**: allí el paper se registra en BIB y opcionalmente se enlaza a PTN; aquí se materializa como documento vivo para lectura activa.

## Actores

- **Usuario**: David
- **Sistema(s)**: Notion (BIB, INX-ENLACES), Obsidian (vault ABGD)

## Trigger

David decide leer un paper activamente. Quiere una ficha editable en el vault, no solo una entrada en el catálogo Notion.

## Precondiciones

- `.env` con:
  - `NOTION_DB_BIB` (catálogo BIB)
  - `NOTION_DB_INX`
  - `OBSIDIAN_ALPHA_PATH`, `OBSIDIAN_ABGD_ROOT`
- Paper ya existe en BIB (importado vía `python agents/bib_agent.py importar`).
- Estructura del vault contiene `A1-INV/B13-PUB/<contexto>/` (uno de `C137-ART`, `C138-COM`, `C139-REV`).

## Fuente de verdad (autoridad)

- **Metadata bibliográfica**: Paperpile → BIB (Notion).
- **Ficha de lectura (contenido vivo)**: Obsidian.
- **Trazabilidad cruzada**: INX-ENLACES.

## Contrato INX (claves canónicas)

| Entidad | Clave |
| --- | --- |
| Paper en BIB | `paperpile:<citekey>` |
| Ficha en vault | `obsidian:<ruta_relativa>` |

El cruce emerge como dos filas INX separadas que comparten contexto. No hay columna dedicada que las enlace explícitamente (gap conocido, análogo al caso 07 inicial).

## Flujo principal (happy path)

1. Asegurar que el paper está en BIB:
   ```bat
   python agents/bib_agent.py importar
   ```
2. Promover a ficha Obsidian con sync INX completo:
   ```bat
   python tools/promote_bib_to_obsidian.py <citekey> --sync
   ```
   o desde Windows:
   ```bat
   apps\promote_bib_to_obsidian.bat "<citekey>" --sync
   ```
3. Verificar con el validador:
   ```bat
   apps\validate_case_09.bat --no-pause
   ```

## Variantes

- **A. Otro contexto**: `--contexto C138-COM` (comunicaciones) o `--contexto C139-REV` (reviews). Default: `C137-ART`.
- **B. Sobrescribir ficha existente**: `--force`. Sin flag, el script detecta la ficha (match por citekey en el nombre) y salta sin tocarla.
- **C. Sin sync**: omitir `--sync` si solo quieres crear la ficha y sincronizar INX más tarde por separado.

## Checklist ejecutable

### Paso 1 — Promover

```bat
.\.venv\Scripts\python.exe tools\promote_bib_to_obsidian.py <citekey> --sync
```

- [ ] Output: `created: N<YYMMDD>-<citekey>.md (<citekey>) bib-id=<id>`.
- [ ] Si `ValueError: Paper con citekey 'X' no encontrado en BIB`: revisar que el paper está en BIB o corre `bib_agent.py sincronizar`.
- [ ] Si `[skip] ficha ya existe`: la ficha estaba ya; usar `--force` si quieres sobrescribir.

### Paso 2 — Validar

```bat
apps\validate_case_09.bat --no-pause
```

Lectura esperada:
- Fichas detectadas ≥ 1.
- `CRUCE DOBLE (obsidian:* AND paperpile:*)`: `N/N`.

### Paso 3 — Edición manual posterior

Abre la ficha en Obsidian y rellena las secciones:
- `## Resumen` (puedes conservar el abstract importado de BIB).
- `## Puntos clave`
- `## Citas relevantes`
- `## Notas propias`

## Frontmatter generado

```yaml
---
citekey: einstein2005
bib-id: 34xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
doi: https://doi.org/10.xxxx/...
anio: 1905
autores: Albert Einstein
tipo: Artículo
journal: Annalen der Physik
estado-lectura: Por leer
---
```

## Postcondiciones / Resultado verificable

- Fichero `.md` existe bajo `A1-INV/B13-PUB/<contexto>/N<YYMMDD>-<citekey>.md` con frontmatter correcto.
- Fila `obsidian:<ruta>` en INX-ENLACES.
- Fila `paperpile:<citekey>` en INX-ENLACES (ya existía si el paper estaba sincronizado; sino se genera en paso 2 del `--sync`).

## Criterios de aceptación (Definition of Done)

- [x] `tools/promote_bib_to_obsidian.py` crea ficha con frontmatter y secciones, dedupla por presencia de archivo existente.
- [x] Flag `--sync` encadena el pipeline INX completo (log_obsidian + log_ptn + sync obsidian + sync paperpile).
- [x] `tools/validate_case_09.py` cuenta fichas por frontmatter `citekey:`, cruza con BIB + INX, reporta gaps.
- [x] `apps/validate_case_09.bat` y `apps/promote_bib_to_obsidian.bat` disponibles.
- [x] Validación end-to-end con papers reales — **ejecutada 2026-04-18**: 472 papers importados desde Paperpile vía GitHub (repo privado `dalarconrub/paperpile-lib`), promoción `Candido2026y → N260418-Candido2026y.md` con `--sync`, validator reporta 1/1 cruce doble `obsidian:* <-> paperpile:*`.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Promover paper BIB a ficha Obsidian | `python tools/promote_bib_to_obsidian.py <citekey> [--contexto <C>] [--force] [--sync]` |
| Desde Windows | `apps\promote_bib_to_obsidian.bat "<citekey>" --sync` |
| Validación end-to-end | `apps\validate_case_09.bat --no-pause` |
| Importar/sincronizar BIB desde Paperpile | `python agents/bib_agent.py importar` / `sincronizar` |

## Observabilidad

- `NOTION_DB_BIB` — fuente de metadata.
- Vault bajo `A1-INV/B13-PUB/{C137-ART,C138-COM,C139-REV}/` — fichas.
- `artifacts/obsidian_log_state.json` — mtime del último log Obsidian.
- `INX-ENLACES` — filas `obsidian:<ruta>` y `paperpile:<citekey>`.

## Gaps (pendientes)

- **Gap 1 — Cruce explícito obsidian:↔ paperpile: en INX**: hoy son dos filas separadas. Análogo al gap original del caso 07 antes de añadir relation. Para navegación nativa habría que extender schema de INX con propiedad `Paperpile Citekey` (rich_text) en filas obsidian:*, o crear fila-puente dedicada.
- **Gap 2 — BIB vacío en el workspace actual (2026-04-18)**: el caso no se puede smoke-testear end-to-end hasta que haya papers reales. Solo validado estructuralmente (syntax + flujo 0 fichas).
- **Gap 3 — No actualiza estado lectura en BIB**: si editas `estado-lectura` en el frontmatter de la ficha, BIB no se entera. Dirección inversa Obsidian→BIB no implementada.

## Mejoras propuestas

- **Mejora 1 — `sync_reading_state`**: script futuro que lea frontmatter `estado-lectura` de las fichas y actualice la propiedad `Estado` del paper en BIB. Cierra el loop bidireccional.
- **Mejora 2 — Cruce INX explícito**: extender schema de INX con columna `Paperpile Citekey` en filas obsidian y popularlo desde frontmatter durante `_sync_obsidian`.
- **Mejora 3 — `--all-pending`**: flag que promueva masivamente todos los papers con `Estado = Por leer` que aún no tienen ficha.

## Fallos típicos

- **`Paper con citekey X no encontrado en BIB`**: citekey mal escrito, o BIB desactualizado. Corre `bib_agent.py sincronizar`.
- **`[skip] ficha ya existe`**: match por filename que contiene el citekey. Usar `--force` si quieres regenerar.
- **Validación 0/0**: no hay fichas todavía. Promociona al menos una.

## Validación práctica

```bat
apps\validate_case_09.bat --no-pause
```

El caso 09 queda **validado** cuando:
- Fichas detectadas ≥ 1.
- Cada ficha matchea BIB, INX obsidian:*, INX paperpile:*.
- `CRUCE DOBLE`: `N/N`.
