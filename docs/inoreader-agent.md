# Inoreader → KIT — Agente y herramientas

> **Inoreader actúa como FUENTE EXTERNA de KIT**, no como catálogo independiente.
> Solo se importan los artículos tageados explícitamente con
> `INOREADER_FOLDER_KIT` (default `kit-import`). El estado **`starred` NO
> entra**: en Inoreader es el buffer de "Read later" y no implica intención de
> catalogar. Los artículos importados se materializan en `NOTION_DB_KIT` con
> `Tipo=Information`, `Subtipo` granular, y propiedades dedicadas
> (`Inoreader ID`, `Inoreader Tags`).
>
> Inoreader no tiene código de entidad propio (no es catálogo). Se documenta
> aquí porque su tooling es no trivial y vive bajo `tools/` y `agents/`.

## Arquitectura

```
Inoreader (web)
    └── tag 'kit-import'  (Starred NO entra: es "Read later")
                                   │
        ┌──── ruta A ─── tools/sync_inoreader_to_kit.py
        │                (API OAuth2 incremental, cuota 100 calls/día)
        │
        └──── ruta B ─── tools/import_inoreader_articles.py
                         (JSON feed público, sin auth, sin cuota)
                                   │
                                   ▼
                         NOTION_DB_KIT (filas con Inoreader ID)
                                   │
                                   ▼ (sync_inx_links.py --source kit)
                            NOTION_DB_INX
                              clave = kit:<page_id>
                              Fuente = KIT
```

Ambas rutas son **idempotentes** (clave de unicidad: `Inoreader ID`) y producen
**filas KIT idénticas** porque comparten:
- normalización (`tools/inoreader_tools.normalize_article` + `normalize_jsonfeed_item` + `dispatch_normalize`)
- dedupe (`merge_articles`)
- upsert (`upsert_article_to_kit`, `article_to_props` en `tools/sync_inoreader_to_kit.py`)

## Componentes

| Archivo | Función |
| --- | --- |
| [tools/inoreader_tools.py](../tools/inoreader_tools.py) | Wrapper API OAuth2 con auto-refresh, normalizadores (API + JSON Feed), helpers de cursor incremental |
| [tools/inoreader_oauth.py](../tools/inoreader_oauth.py) | Flujo OAuth2 interactivo (una sola vez). Levanta servidor local, captura code, persiste tokens |
| [tools/ensure_kit_external_fields.py](../tools/ensure_kit_external_fields.py) | Schema KIT/INX: añade `Inoreader ID`, `Inoreader Tags`, opciones de `Subtipo` y `Fuente=Inoreader` (idempotente) |
| [tools/sync_inoreader_to_kit.py](../tools/sync_inoreader_to_kit.py) | Sync vía API con cursor incremental por stream. Helpers compartidos de upsert |
| [tools/import_inoreader_articles.py](../tools/import_inoreader_articles.py) | Importer offline desde JSON feeds públicos o archivos descargados. Sin OAuth ni cuota |
| [agents/inoreader_agent.py](../agents/inoreader_agent.py) | CLI por dominio: `auth-check`, `list-folders`, `sync`, `import-feed`, `listar`, `estado`, `link` |

## Configuración

### `.env`

```dotenv
# Credenciales OAuth (de https://www.inoreader.com/developers/)
INOREADER_APP_ID=...
INOREADER_APP_KEY=...
# Redirect URI debe coincidir LITERALMENTE con el registrado en la app
INOREADER_REDIRECT_URI=http://localhost:8765/callback
# Folder o tag (intercambiables, mismo URL /tag/<nombre>/)
INOREADER_FOLDER_KIT=kit-import
```

### Estado persistido (gitignored)

| Archivo | Contenido |
| --- | --- |
| `artifacts/inoreader_state.json` | `access_token`, `refresh_token`, `expires_at` (refrescados automáticamente) |
| `artifacts/inoreader_sync_state.json` | Cursores por stream (`starred`, `kit-import`): unix epoch del último sync OK |

## Setup inicial

### 1. Registrar la app OAuth en Inoreader (una sola vez)

1. Ir a https://www.inoreader.com/developers/.
2. **Register a new application**:
   - Name: `Coworkia`
   - Platform: `Desktop` (o `Other`)
   - Scope: `Read`
   - Redirect URI: `http://localhost:8765/callback` ← **debe coincidir con `.env`**
3. Esperar aprobación (manual de Inoreader, horas a días).
4. Copiar `App ID` y `App Key` a `.env`.

### 2. Asegurar schema KIT/INX

```bat
python tools/ensure_kit_external_fields.py
```

Añade (sin destruir lo existente):
- `KIT.Inoreader ID` (rich_text)
- `KIT.Inoreader Tags` (multi_select: `starred`, `kit-import`)
- `KIT.Fuente / Autor` (rich_text)
- `KIT.Subtipo`: opciones `Artículo`, `Newsletter`, `Blog`, `Vídeo`, `Podcast`
- `INX-ENLACES.Fuente`: opción `Inoreader`

### 3. Autorizar OAuth (una sola vez)

```bat
python tools/inoreader_oauth.py
```

- Abre navegador, das Allow, redirige a `localhost:8765/callback`.
- Tokens persistidos en `artifacts/inoreader_state.json`.
- Auto-refresh transparente cuando caducan (≈1h).

### 4. Verificar conexión y cuota

```bat
python agents/inoreader_agent.py auth-check
```

Debe imprimir `[OK] Conectado como: <usuario>` y los counters Zone 1/Zone 2.

## Uso diario

### Sync incremental vía API (recomendado)

```bat
python agents/inoreader_agent.py sync
```

- Lee solo el tag `kit-import` desde el último cursor (starred no entra).
- Solo procesa items nuevos.
- ~1 call API por ejecución (margen amplio sobre las 100/día).
- Tras éxito, avanza cursor en `artifacts/inoreader_sync_state.json`.

### Sync completo (reset de cursor)

```bat
python agents/inoreader_agent.py sync --full
```

Ignora cursor, pulla todo. Coste: `ceil(total_items / 1000)` calls por stream.
Usar al cargar histórico inicial o tras un reset.

### Importer offline (sin cuota, sin OAuth)

Útil cuando OAuth no está disponible o quieres evitar consumir cuota:

1. En Inoreader: click derecho sobre el tag `kit-import` → **Folder properties** → **Export ON** → **JSON feed** → copiar URL pública.
2. Añadir `?n=1000` al final para maximizar items por petición.
3. Ejecutar:

```bat
python agents/inoreader_agent.py import-feed --url "https://www.inoreader.com/stream/user/.../tag/kit-import/view/json?n=1000" --tag kit-import
```

`--url` es repetible si en algún flujo concreto necesitas combinar varios feeds (cualquier tag o folder); el importer no impone política, ejecuta lo que le indiques. La política de "solo `kit-import`" la aplica el sync por defecto, no el importer offline.

### Filtros útiles

```bat
:: Solo artículos publicados desde fecha
python agents/inoreader_agent.py import-feed --url "..." --tag kit-import --newer-than 2026-04-01

:: Tope para pruebas
python agents/inoreader_agent.py sync --limit 5

:: Pruebas sin escribir
python agents/inoreader_agent.py sync --dry-run
```

### Vincular un artículo a proyecto PTN

```bat
python agents/inoreader_agent.py link <inoreader_id> <proyecto_ref>
```

- `<inoreader_id>` es el `Inoreader ID` de la fila KIT (rich_text).
- `<proyecto_ref>` es el ID o nombre del proyecto PTN.
- Actualiza la fila INX `kit:<page_id>` existente añadiendo la relación `PTN Proyecto` y la URL del artículo.

### Listar y resumir

```bat
:: Listar todos los artículos Inoreader catalogados
python agents/inoreader_agent.py listar

:: Filtrar por subtipo
python agents/inoreader_agent.py listar --subtipo Newsletter

:: Filtrar por origen
python agents/inoreader_agent.py listar --tag starred

:: Resumen agregado por subtipo y por tag de origen
python agents/inoreader_agent.py estado
```

## Cuotas y límites

| Recurso | Límite |
| --- | --- |
| Inoreader API Zone 1 (read) | **100 calls/día** por app externa (independiente de plan Pro del usuario) |
| Inoreader API Zone 2 (write) | 100 calls/día |
| Reset | Diario, ver `x-reader-limits-reset-after` en headers |
| Page size por petición | Hasta `n=1000` items |

El plan Pro de Inoreader **no eleva** el límite API de apps externas. Para sync masivo histórico, usar la ruta JSON feed (sin cuota).

## INX-ENLACES y trazabilidad

Inoreader **no crea filas `inoreader:*` propias** en INX. Razón: los artículos
viven en KIT, así que `tools/sync_inx_links.py --source kit` ya los materializa
como `kit:<page_id>` con `Fuente=KIT`. Crear claves separadas duplicaría INX
para la misma entidad.

| Acción | Comando |
| --- | --- |
| Sync KIT (incluye Inoreader) → INX | `python tools/sync_inx_links.py --source kit --limit 200` |
| Vincular artículo a proyecto PTN | `python agents/inoreader_agent.py link <inoreader_id> <proyecto_ref>` |
| Helper Python directo | `link_article_to_ptn(inoreader_id, proyecto_ref)` en `tools/sync_inx_links.py` |

## Convención de duplicados

Si el mismo artículo (mismo título) llega dos veces con `Inoreader ID` distinto
(p. ej. publicado en 2 feeds distintos que sigues), se crean **dos filas KIT
distintas**. El sistema respeta `Inoreader ID` como única clave de dedupe.
Limpieza: manual desde Notion si procede.

## Heurística de Subtipo

Implementada en `tools/inoreader_tools._infer_subtipo`:

| Detección | Subtipo |
| --- | --- |
| URL contiene `youtube.com` o `vimeo.com` | `Vídeo` |
| URL contiene `substack.com`, `beehiiv.com`, `buttondown.email`, `convertkit.com` | `Newsletter` |
| Hay `enclosure` audio o palabra `podcast` en feed/categorías | `Podcast` |
| Categorías contienen `blog` o URL contiene `/blog` | `Blog` |
| Default | `Artículo` |

## Troubleshooting

| Síntoma | Causa | Acción |
| --- | --- | --- |
| `redirect_uri mismatch` al autorizar | Redirect URI en `.env` no coincide con la app Inoreader | Comparar carácter a carácter, ambos deben decir `http://localhost:8765/callback` |
| `localhost:8765` ERR_CONNECTION_REFUSED | Script `inoreader_oauth.py` no corriendo cuando pulsas Allow | Ejecutar primero el script, dejar que él abra el navegador |
| Puerto ocupado al ejecutar oauth | Otro servicio en ese puerto | Cambiar `INOREADER_REDIRECT_URI` y el redirect en Inoreader a un puerto libre |
| `KeyError: 'inoreader_id'` en sync | Items no normalizados | Verificar que `_fetch_stream` aplica `normalize_article` |
| `[notion] 0 articulos Inoreader ya en KIT` y crea muchos duplicados | Sync ejecutándose en KIT erróneo | Verificar `NOTION_DB_KIT` en `.env` |
| Cuota Zone1 agotada | Demasiados `--full` o `auth-check` | Esperar al reset o usar ruta JSON feed |
