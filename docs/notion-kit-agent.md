# Notion KIT Agent

Agente para el sistema **KIT** en Notion.

## Modelo

`KIT` usa una sola base maestra:

- `KIT`

Y un campo `Tipo` separa las tres vistas logicas:

- `Knowledge`
- `Information`
- `Tool`

La separacion visual se hace con vistas de Notion, no con tres bases distintas.

## Setup

```bash
python agents/kit_agent.py crear-db --parent <NOTION_PAGE_ID>
```

Crea la base maestra `KIT` bajo una pagina de Notion, recomendablemente `A4-ARX`.
El comando devuelve el ID para guardarlo en:

- `NOTION_DB_KIT`

## Comandos

### Consultas

```bash
python agents/kit_agent.py estado
python agents/kit_agent.py knowledge
python agents/kit_agent.py information
python agents/kit_agent.py tools
python agents/kit_agent.py buscar "llm"
```

Filtros:

```bash
python agents/kit_agent.py knowledge --subtipo Metodologia
python agents/kit_agent.py information --etiqueta Neuropsicologia
python agents/kit_agent.py tools --subtipo IA
```

### Crear

```bash
python agents/kit_agent.py nueva-knowledge "Metodologia GLM" --subtipo Metodologia --estado Activo
python agents/kit_agent.py nueva-information "Paper Cognicion 2025" --subtipo Paper --enlace https://doi.org/...
python agents/kit_agent.py nueva-tool "Julius AI" --subtipo IA --estado Activo --enlace https://julius.ai
```

### Importar desde Google Keep

```bash
python agents/kit_agent.py importar-keep --source "C:\ruta\Takeout\Keep"
python agents/kit_agent.py sincronizar-keep --source "C:\ruta\Takeout\Keep"
```

Reglas:

- `importar-keep` crea solo entradas nuevas.
- `sincronizar-keep` crea nuevas y actualiza existentes.
- La deduplicacion se hace por `Google Keep ID`.
- Por defecto entra como `Tipo=Information` y `Subtipo=Nota`.
- Las notas archivadas se omiten salvo `--incluir-archivadas`.

## Propiedades

`Titulo` · `Tipo` · `Subtipo` · `Estado` · `Resumen` · `Etiquetas` · `Fuente / Autor` · `Enlace` · `Nivel de confianza` · `Fecha de publicacion` · `Fecha de actualizacion` · `Extractos` · `Area` · `Usada en` · `Usada en notas` · `Google Keep ID` · `Inoreader ID` · `Inoreader Tags` · `Raindrop ID` · `Raindrop Tags` · `Raindrop Collection` · `Raindrop Type` · `Archivos`

Notas:

- `Usada en` sigue como campo libre/legacy.
- `Usada en notas` es la relation operativa con `OBSIDIAN_DB` para referencias `[[kit:<id>]]`.

## API usada

- `NOTION_TOKEN` en `.env`
- `NOTION_DB_KIT` en `.env`
- `NOTION_KIT_PARENT_PAGE` opcional para crear la base
