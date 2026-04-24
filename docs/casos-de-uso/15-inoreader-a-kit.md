# Caso de uso: Importar artículos Inoreader a KIT y enlazar a PTN

## Objetivo

Que cada artículo curado en Inoreader con el tag explícito `kit-import`
quede catalogado en `NOTION_DB_KIT` con metadata limpia (subtipo, autor,
fecha, URL, resumen), expuesto en `INX-ENLACES` vía la fila `kit:<page_id>`,
y opcionalmente vinculado a un proyecto PTN.

## Actores

- **Usuario**: David
- **Sistema(s)**: Inoreader (lectura RSS), Notion (KIT, INX, PTN)

## Trigger

David quiere catalogar un artículo leído en Inoreader como Information del KIT:
- Lo tagea explícitamente con `kit-import` desde la web de Inoreader.

> **`Starred` NO dispara import.** En Inoreader, "Read later" estarrea
> automáticamente y eso no es señal de "catalogar en KIT". Solo el tag
> explícito `kit-import` cuenta. El sync por defecto ignora `Starred`.

## Precondiciones

- `.env` con:
  - `NOTION_DB_KIT`, `NOTION_DB_INX`, `NOTION_DS_PROYECTOS`
  - `INOREADER_APP_ID`, `INOREADER_APP_KEY`, `INOREADER_REDIRECT_URI`, `INOREADER_FOLDER_KIT`
- App OAuth registrada y aprobada en https://www.inoreader.com/developers/.
- Tokens persistidos en `artifacts/inoreader_state.json` (vía `tools/inoreader_oauth.py`).
- Schema KIT/INX preparado (`tools/ensure_kit_external_fields.py`).

## Fuente de verdad

- **Origen del artículo**: Inoreader (feed/tag; por defecto solo `kit-import`)
- **Catálogo y estado de lectura**: Notion (KIT, propiedad `Estado`)
- **Trazabilidad y enlace a PTN**: Notion (`INX-ENLACES`)

## Datos y IDs (contrato)

- **Inoreader**: `inoreader_id` (string que empieza por `http://www.inoreader.com/article/`)
- **KIT (Notion)**: `page_id`, propiedad `Inoreader ID` (rich_text, clave de unicidad)
- **INX**: clave canónica `kit:<kit_page_id>` con `Fuente = KIT`
  - **No se crea clave `inoreader:<id>`** propia (Inoreader alimenta KIT, no es catálogo separado)

## Flujo principal (happy path)

1. David tagea con `kit-import` en Inoreader (no basta starrear).
2. Sync vía API (consume cuota, incremental):

```bat
python agents/inoreader_agent.py sync
```

3. (Equivalente sin cuota, vía JSON feed público):

```bat
python agents/inoreader_agent.py import-feed --url "https://www.inoreader.com/stream/user/<id>/tag/kit-import/view/json?n=1000" --tag kit-import
```

4. Sync KIT → INX:

```bat
python tools/sync_inx_links.py --source kit --limit 200
```

5. (Opcional) Vincular el artículo a proyecto PTN:

```bat
python agents/inoreader_agent.py link <inoreader_id> "Nombre del proyecto"
```

## Variantes

- **Variante A — Setup inicial**: si es la primera vez, antes de sync correr `tools/inoreader_oauth.py` y `tools/ensure_kit_external_fields.py`.
- **Variante B — OAuth no disponible**: usar solo la ruta JSON feed público (sin auth, sin cuota). Funciona idéntico, mismas filas KIT.
- **Variante C — Backfill histórico**: `python agents/inoreader_agent.py sync --full` (consume hasta `ceil(total_items/1000)` calls por stream).
- **Variante D — Sync incremental con filtro de fecha**: `python agents/inoreader_agent.py import-feed --url "..." --newer-than 2026-04-01` (filtro client-side).

## Postcondiciones / Resultado verificable

- En **KIT**: existe fila con
  - `Tipo = Information`
  - `Subtipo` ∈ {`Artículo`, `Newsletter`, `Blog`, `Vídeo`, `Podcast`}
  - `Inoreader ID` poblado
  - `Inoreader Tags` contiene `kit-import` (otros tags solo si se importaron explícitamente vía `import-feed --url ... --tag <otro>`)
  - `Enlace`, `Fuente / Autor`, `Resumen`, `Fecha de publicacion` poblados
  - `Estado = Activo`
- En **INX-ENLACES**: existe fila con
  - `Clave = kit:<kit_page_id>`
  - `Fuente = KIT`
  - `URL = <enlace del artículo>` si aplica
- Tras `link`: la misma fila INX tiene `PTN Proyecto = <relation>` al proyecto resuelto.

## Automatización actual

| Acción | Comando |
| --- | --- |
| Sync API incremental | `python agents/inoreader_agent.py sync` |
| Sync API completo | `python agents/inoreader_agent.py sync --full` |
| Import offline (JSON feed) | `python agents/inoreader_agent.py import-feed --url "<url>" --tag kit-import` |
| Verificar conexión y cuota | `python agents/inoreader_agent.py auth-check` |
| Listar carpetas/tags | `python agents/inoreader_agent.py list-folders` |
| Listar artículos en KIT | `python agents/inoreader_agent.py listar [--subtipo X] [--tag Y]` |
| Resumen catálogo | `python agents/inoreader_agent.py estado` |
| Vincular a PTN | `python agents/inoreader_agent.py link <inoreader_id> <proyecto_ref>` |
| Sync KIT → INX | `python tools/sync_inx_links.py --source kit --limit 200` |
| Helper Python | `link_article_to_ptn(inoreader_id, proyecto_ref)` en `tools/sync_inx_links.py` |

## Cuotas y límites

- API Inoreader Zone 1: **100 calls/día** por app externa (Pro no eleva este límite).
- Sync incremental típico: ~2 calls. Sync completo: hasta `ceil(total/1000)` calls por stream.
- JSON feed público: sin cuota (recomendado para sync masivo).

## Observabilidad

- **NOTION_DB_KIT**: filas con `Inoreader ID` no vacío.
- **artifacts/inoreader_state.json**: tokens OAuth (refrescados automáticamente).
- **artifacts/inoreader_sync_state.json**: cursor incremental por stream (unix epoch).
- **INX-ENLACES**: filas `kit:*` con `Fuente=KIT` para los artículos importados.

## Gaps pendientes

- **Gap 1 — Detección de artículos archivados**: si un artículo se elimina de Inoreader (untag o destarrar), Coworkia no lo refleja. Política actual: una vez en KIT, vive en KIT (catalogación pura).
- **Gap 2 — Dedupe por título/URL**: dos `Inoreader ID` distintos para el mismo artículo (p. ej. publicado en 2 feeds) generan 2 filas KIT. Limpieza manual.
- **Gap 3 — Doctor**: no existe `apps/inoreader_doctor.py` aún para diagnóstico end-to-end.

## Mejoras propuestas

- **Mejora 1 — `link` por título parcial**: aceptar substring del título como fallback al `inoreader_id` literal.
- **Mejora 2 — Modo "drain"**: `sync --drain-tag` que tras importar a KIT quita el tag `kit-import` en Inoreader (consume cuota Zone 2). Cierra el ciclo.
- **Mejora 3 — `apps/inoreader_doctor.py`**: counters por subtipo, cuota disponible, último cursor, items huérfanos.
- **Mejora 4 — GUI**: `apps/inoreader_gui.py` para revisar artículos pendientes de catalogar y promocionar a Knowledge.

## Fallos típicos

| Síntoma | Solución |
| --- | --- |
| `Articulo Inoreader '<id>' no encontrado en KIT` al hacer link | Sincroniza primero (`sync` o `import-feed`) |
| `redirect_uri mismatch` al autorizar | Verificar coincidencia exacta `.env` ↔ app Inoreader |
| Cuota Zone 1 agotada | Esperar reset (`x-reader-limits-reset-after`) o usar `import-feed` |
| Subtipo siempre `Artículo` aunque sea YouTube | Heurística no detectó; ajustar `_infer_subtipo` |
