# Notion KIT Agent — Guía de uso

Agente para el sistema **KIT (Knowledge-Information-Tools)** en Notion.

## Data Sources

| Nombre | ID | Contenido |
|--------|----|-----------|
| KIT-Knowledge | `2ad622cf-315b-80a2-a13e-000b063d2ca2` | Conocimiento interno, síntesis, conceptos propios |
| KIT-Information | `2ab622cf-315b-8011-b53d-000b43838fb3` | Información externa: artículos, papers, fuentes |
| KIT-Tools | `2ad622cf-315b-8029-bc67-000baecc1150` | Herramientas, apps, servicios, software |

---

## Comandos

### Consultas

```bash
# Estado general del KIT
python agents/kit_agent.py estado

# Listar por fuente
python agents/kit_agent.py knowledge
python agents/kit_agent.py information
python agents/kit_agent.py tools

# Filtrar por tipo o etiqueta
python agents/kit_agent.py knowledge --tipo "Metodología"
python agents/kit_agent.py information --etiqueta "Neuropsicología"
python agents/kit_agent.py tools --tipo "IA"

# Buscar en todo el KIT
python agents/kit_agent.py buscar "análisis estadístico"
python agents/kit_agent.py buscar "LLM"
```

### Crear

```bash
# Nueva entrada en Knowledge
python agents/kit_agent.py nueva-knowledge "Metodología de análisis GLM"
python agents/kit_agent.py nueva-knowledge "Protocolo entrevista semiestructurada" \
  --tipo "Metodología" \
  --estado "Activo" \
  --resumen "Pasos para diseñar y aplicar una entrevista semiestructurada" \
  --etiquetas "Metodología" "Investigación"

# Nueva entrada en Information
python agents/kit_agent.py nueva-information "Paper Cognición y Lenguaje 2025"
python agents/kit_agent.py nueva-information "Revisión meta-análisis memoria de trabajo" \
  --tipo "Paper" \
  --autor "Smith et al." \
  --enlace "https://doi.org/..." \
  --etiquetas "Memoria" "Meta-análisis"

# Nueva herramienta
python agents/kit_agent.py nueva-tool "Zotero"
python agents/kit_agent.py nueva-tool "Julius AI" \
  --tipo "IA" \
  --estado "Activo" \
  --resumen "Análisis estadístico con IA, genera código Python/R" \
  --enlace "https://julius.ai" \
  --etiquetas "Estadística" "IA"
```

---

## Propiedades (schema compartido)

Todas las fuentes comparten el mismo schema base:

`Título/Referencia/Aplicaciones` · `Tipo` · `Estado` · `Resumen` · `Etiquetas` · `Fuente / Autor` · `Enlace` · `Nivel de confianza` · `Fecha de publicación` · `Extractos` · `Proyectos` · `Tareas` · `Notas` · `Referencias relacionadas` · `Usada en` · `Archivos`

**KIT-Tools** añade: `Aplicaciones`

---

## API usada

- **Notion API v2025-09-03**
- Token en `.env` → `NOTION_TOKEN`
- IDs en `.env` → `NOTION_DS_KIT_KNOWLEDGE`, `NOTION_DS_KIT_INFORMATION`, `NOTION_DS_KIT_TOOLS`
