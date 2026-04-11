# Notion KIT Agent

Agente para el sistema **KIT** en Notion.

## Modelo

`KIT` usa una sola base maestra:

- `KIT`

Y un campo `Tipo` separa las tres vistas lógicas:

- `Knowledge`
- `Information`
- `Tool`

La separación visual se hace con vistas de Notion, no con tres bases distintas.

## Setup

```bash
python agents/kit_agent.py crear-db --parent <NOTION_PAGE_ID>
```

Crea la base maestra `KIT` bajo una página de Notion, recomendablemente `A4-ARX`.
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

## Propiedades

`Titulo` · `Tipo` · `Subtipo` · `Estado` · `Resumen` · `Etiquetas` · `Fuente / Autor` · `Enlace` · `Nivel de confianza` · `Fecha de publicacion` · `Extractos` · `Area` · `Usada en` · `Archivos`

## API usada

- `NOTION_TOKEN` en `.env`
- `NOTION_DB_KIT` en `.env`
- `NOTION_KIT_PARENT_PAGE` opcional para crear la base
