# Raindrop.io -> KIT - Agente y herramientas

> **Raindrop.io actua como FUENTE EXTERNA de KIT**, no como catalogo
> independiente. Solo se importan bookmarks marcados explicitamente con
> `RAINDROP_TAG_KIT` (default `kit-import`) o con la busqueda configurada en
> `RAINDROP_SEARCH_KIT`. Se materializan en `NOTION_DB_KIT` con
> `Tipo=Information`, `Subtipo` granular y propiedades dedicadas
> (`Raindrop ID`, `Raindrop Tags`, `Raindrop Collection`, `Raindrop Type`).

## Arquitectura

```text
Raindrop.io
    └── tag 'kit-import' o RAINDROP_SEARCH_KIT
                    |
                    v
          tools/sync_raindrop_to_kit.py
          (REST API v1, Bearer token, cursor local)
                    |
                    v
          NOTION_DB_KIT (filas con Raindrop ID)
                    |
                    v
          sync_inx_links.py --source kit
          NOTION_DB_INX, clave = kit:<page_id>, Fuente = KIT
```

Raindrop ofrece tambien MCP beta para clientes IA Pro:

```text
https://api.raindrop.io/rest/v2/ai/mcp
```

Coworkia usa REST v1 para el sync local porque permite paginacion, dry-run,
tests y ejecucion reproducible desde CLI. El MCP queda como via interactiva para
clientes compatibles.

## Componentes

| Archivo | Funcion |
| --- | --- |
| [tools/raindrop_tools.py](../tools/raindrop_tools.py) | Wrapper REST, normalizador, tags, colecciones y cursor incremental |
| [tools/sync_raindrop_to_kit.py](../tools/sync_raindrop_to_kit.py) | Sync Raindrop -> KIT con upsert idempotente por URL y `Raindrop ID` |
| [tools/ensure_kit_external_fields.py](../tools/ensure_kit_external_fields.py) | Schema KIT: `Raindrop ID`, `Raindrop Tags`, collection/type y opciones de subtipo |
| [agents/raindrop_agent.py](../agents/raindrop_agent.py) | CLI: `auth-check`, `list-tags`, `list-collections`, `sync`, `listar`, `estado` |

## Configuracion

```dotenv
RAINDROP_ACCESS_TOKEN=
RAINDROP_CLIENT_ID=
RAINDROP_CLIENT_SECRET=
RAINDROP_REDIRECT_URI=http://localhost:8766/callback
RAINDROP_TAG_KIT=kit-import
RAINDROP_COLLECTION_ID=0
RAINDROP_SEARCH_KIT=
```

- `RAINDROP_ACCESS_TOKEN`: Bearer token REST manual. Para uso personal basta el
  Test token de la App Management Console. Si usas OAuth, puede quedar vacio.
- `RAINDROP_CLIENT_ID`, `RAINDROP_CLIENT_SECRET`, `RAINDROP_REDIRECT_URI`:
  credenciales OAuth REST para `python tools/raindrop_oauth.py`.
- `RAINDROP_TAG_KIT`: tag explicito que indica intencion de catalogar en KIT.
- `RAINDROP_COLLECTION_ID`: `0` trae todos los bookmarks excepto Trash; puedes
  restringir a una coleccion concreta.
- `RAINDROP_SEARCH_KIT`: opcional. Si lo defines, Coworkia lo pasa al parametro
  `search` de Raindrop. Si queda vacio, Coworkia filtra client-side por tag.

## Setup inicial

```bat
python tools/ensure_kit_external_fields.py
python tools/raindrop_oauth.py
python agents/raindrop_agent.py auth-check
python agents/raindrop_agent.py list-tags
```

## Uso diario

```bat
python agents/raindrop_agent.py sync
python agents/raindrop_agent.py sync --dry-run --limit 5
python agents/raindrop_agent.py sync --full
```

Tras importar a KIT:

```bat
python tools/sync_inx_links.py --source kit --limit 200
```

## Listar y resumir

```bat
python agents/raindrop_agent.py listar
python agents/raindrop_agent.py listar --tag kit-import
python agents/raindrop_agent.py listar --subtipo Paper
python agents/raindrop_agent.py estado
```

## Dedupe

El upsert busca primero por `Enlace` normalizado y despues por `Raindrop ID`.
La normalizacion elimina parametros de tracking (`utm_*`, `fbclid`, etc.),
fragmentos `#...`, ordena la query restante y normaliza host/scheme. Esto evita
duplicar entradas si el mismo recurso llega por Raindrop e Inoreader con
variantes triviales de URL.

Para limpiar duplicados historicos:

```bat
python tools/dedupe_notion_db.py --db-env NOTION_DB_KIT --key Enlace --normalize-url
python tools/dedupe_notion_db.py --db-env NOTION_DB_KIT --key Enlace --normalize-url --apply
```

## Limites

La API REST de Raindrop permite 120 requests/minuto por usuario autenticado.
El endpoint de listado usa `perpage=50`, asi que un full sync cuesta
aproximadamente `ceil(bookmarks_filtrados/50)` paginas mas las paginas omitidas
por el filtro client-side si no se usa `RAINDROP_SEARCH_KIT`.
