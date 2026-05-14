# Caso de uso: Importar bookmarks Raindrop.io a KIT

## Objetivo

Que cada bookmark curado en Raindrop.io con el tag explicito `kit-import`
quede catalogado en `NOTION_DB_KIT` como `Tipo=Information`, con metadata
limpia y trazabilidad posterior via INX como `kit:<page_id>`.

> Raindrop.io no es un catalogo Coworkia separado: alimenta KIT.

## Precondiciones

- `.env` contiene `RAINDROP_ACCESS_TOKEN`, `NOTION_TOKEN`, `NOTION_DB_KIT` y
  `NOTION_DB_INX`.
- Schema preparado:

```bat
python tools/ensure_kit_external_fields.py
```

- En Raindrop, David marca bookmarks a importar con `kit-import` o configura
  `RAINDROP_SEARCH_KIT` con una busqueda equivalente.

## Flujo principal

1. David guarda o actualiza un bookmark en Raindrop.
2. David anade tag `kit-import`.
3. Ejecuta:

```bat
python agents/raindrop_agent.py sync
```

4. Coworkia crea/actualiza la fila en KIT con:
   - `Raindrop ID`
   - `Raindrop Tags`
   - `Raindrop Collection`
   - `Raindrop Type`
   - `Enlace`
   - `Resumen`

5. Para materializar en INX:

```bat
python tools/sync_inx_links.py --source kit --limit 200
```

## Variantes

| Variante | Comando |
| --- | --- |
| Smoke sin escribir | `python agents/raindrop_agent.py sync --dry-run --limit 5` |
| Backfill completo | `python agents/raindrop_agent.py sync --full` |
| Restringir paginas REST | `python agents/raindrop_agent.py sync --max-pages 2` |
| Listar tags | `python agents/raindrop_agent.py list-tags` |
| Listar colecciones | `python agents/raindrop_agent.py list-collections` |

## Validacion

```bat
python agents/raindrop_agent.py estado
python agents/raindrop_agent.py listar --tag kit-import
python tools/sync_inx_links.py --source kit --limit 200
```

## Gaps

- No hay `link` especifico Raindrop -> PTN; de momento se enlaza desde la fila
  KIT/INX igual que cualquier otra entrada KIT.
- No hay modo `drain-tag` para retirar `kit-import` tras importar.
- El sync incremental usa cursor local por `lastUpdate`; si se cambia el tag de
  un bookmark antiguo y Raindrop no actualiza `lastUpdate`, usar `--full`.
- El dedupe preventivo cubre variantes triviales de URL; para duplicados
  historicos, usar `dedupe_notion_db.py --key Enlace --normalize-url` primero en
  dry-run.
