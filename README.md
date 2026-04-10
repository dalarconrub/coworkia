# Coworkia

Sistema de automatización personal para clasificar, consultar y sincronizar información entre Todoist, Notion, GitHub, Paperpile y Obsidian.

La idea central del proyecto es simple: no improvisar, sino clasificar. El repositorio implementa varios agentes CLI especializados, más algunas aplicaciones auxiliares, para operar sobre los sistemas MAR, PTN, KIT, REP, BIB y ABGD.

## Qué Hace

- `MAR`: gestiona tareas en Todoist según su existencia temporal: idea, meta, hábito, tarea y evento.
- `PTN`: gestiona proyectos, tareas y notas en Notion.
- `KIT`: gestiona conocimiento, información y herramientas en Notion.
- `REP`: importa y cataloga repositorios de GitHub en Notion.
- `BIB`: importa y cataloga bibliografía de Paperpile en Notion.
- `ABGD`: navega y escribe notas en un vault local de Obsidian.

## Estructura

```text
coworkia/
├── agents/     # CLIs por sistema
├── tools/      # wrappers de APIs y filesystem
├── apps/       # GUIs, dashboards y scripts auxiliares
├── docs/       # documentación funcional
├── Sistemas/   # repos/documentación de referencia
├── CLAUDE.md   # contexto interno del proyecto
└── requirements.txt
```

## Requisitos

- Python 3.10+
- Acceso a las APIs o recursos configurados en `.env`

Instalación:

```bash
pip install -r requirements.txt
```

## Variables De Entorno

Crea un archivo `.env` en la raíz. Puedes partir de `.env.example` o del `.env` local ya creado. Las variables relevantes son:

```env
TODOIST_API_KEY=
NOTION_TOKEN=

NOTION_DS_PROYECTOS=
NOTION_DS_TAREAS=
NOTION_DS_NOTAS=

NOTION_DS_KIT_KNOWLEDGE=
NOTION_DS_KIT_INFORMATION=
NOTION_DS_KIT_TOOLS=

GITHUB_TOKEN=
NOTION_REPOS_PARENT_PAGE=
NOTION_DB_REPOS=

PAPERPILE_BIBTEX_URL=
NOTION_BIB_PARENT_PAGE=
NOTION_DB_BIB=

OBSIDIAN_ABGD_ROOT=
OBSIDIAN_ALPHA_PATH=
```

Notas:

- `NOTION_TOKEN` debe tener acceso a las páginas o bases compartidas con la integración.
- `PTN` y `KIT` ya traen `data source IDs` por defecto en el código, pero siguen necesitando `NOTION_TOKEN`.
- `REP` y `BIB` además necesitan `NOTION_DB_REPOS` y `NOTION_DB_BIB`.
- `GITHUB_TOKEN` necesita alcance suficiente para leer repos privados si se van a importar.
- `PAPERPILE_BIBTEX_URL` usa el export automático BibTeX de Paperpile.
- `OBSIDIAN_ALPHA_PATH` debe apuntar al directorio `Alpha` del vault ABGD.

Diagnóstico rápido:

```bash
python apps/config_doctor.py
python apps/notion_doctor.py
```

En Windows también puedes usar:

```bat
apps\config_doctor.bat
apps\notion_doctor.bat
```

## Uso Rápido

### MAR / Todoist

Dashboard:

```bash
python apps/dashboard.py
python apps/dashboard.py --limite 50
```

CLI:

```bash
python agents/todoist_agent.py hoy
python agents/todoist_agent.py estado
python agents/todoist_agent.py listar meta
python agents/todoist_agent.py proyectos
python agents/todoist_agent.py buscar "tesis"
python agents/todoist_agent.py ver <TASK_ID>
python agents/todoist_agent.py idea "Idea sin fecha"
python agents/todoist_agent.py meta "Entregar memoria" 2026-04-15
python agents/todoist_agent.py habito "Leer 20 minutos" "every day"
python agents/todoist_agent.py tarea "Preparar informe" 2026-04-20
python agents/todoist_agent.py evento "Reunión" 2026-04-15T10:00:00
python agents/todoist_agent.py completar <TASK_ID>
python agents/todoist_agent.py mover <TASK_ID> <PROJECT_ID>
python agents/todoist_agent.py editar <TASK_ID> --due-date 2026-04-15
python agents/todoist_agent.py reclasificar <TASK_ID> evento --valor 2026-04-15T10:00:00
```

### PTN / Notion

```bash
python agents/notion_agent.py recursos
python agents/notion_agent.py estado
python agents/notion_agent.py proyectos
python agents/notion_agent.py proyectos --estado "En progreso"
python agents/notion_agent.py tareas --estado "Sin empezar"
python agents/notion_agent.py notas
python agents/notion_agent.py nuevo-proyecto "Proyecto X" --prioridad Alta --inicio 2026-04-10
python agents/notion_agent.py nueva-tarea "Hacer X" --proyecto <ID_PROYECTO>
python agents/notion_agent.py nueva-nota "Seguimiento" --fecha 2026-04-10 --proyecto <ID_PROYECTO>
```

### KIT / Notion

```bash
python agents/kit_agent.py estado
python agents/kit_agent.py knowledge
python agents/kit_agent.py information
python agents/kit_agent.py tools
python agents/kit_agent.py buscar "machine learning"
python agents/kit_agent.py nueva-knowledge "Concepto X" --tipo Síntesis
python agents/kit_agent.py nueva-information "Paper Y" --enlace https://example.com
python agents/kit_agent.py nueva-tool "Herramienta Z" --tipo App
```

### REP / GitHub -> Notion

Configuración inicial de la base:

```bash
python agents/github_agent.py crear-db
python agents/github_agent.py crear-db --parent <NOTION_PAGE_ID>
```

Operación normal:

```bash
python agents/github_agent.py importar
python agents/github_agent.py importar --sin-lenguajes
python agents/github_agent.py sincronizar
python agents/github_agent.py listar
python agents/github_agent.py listar --tipo Proyecto --estado Activo
python agents/github_agent.py catalogar mi-repo --tipo Proyecto --estado Activo --proceso "pipeline-datos"
python agents/github_agent.py estado
```

GUI:

```bash
python apps/github_gui.py
```

### BIB / Paperpile -> Notion

Configuración inicial de la base:

```bash
python agents/bib_agent.py crear-db
python agents/bib_agent.py crear-db --parent <NOTION_PAGE_ID>
```

Operación normal:

```bash
python agents/bib_agent.py importar
python agents/bib_agent.py sincronizar
python agents/bib_agent.py listar
python agents/bib_agent.py listar --estado "Por leer" --tipo Artículo
python agents/bib_agent.py catalogar einstein2005 --estado "Leído" --relevancia Alta --notas "Metodología útil"
python agents/bib_agent.py estado
```

GUI:

```bash
python apps/bib_gui.py
```

### ABGD / Obsidian

```bash
python agents/obsidian_agent.py mapa
python agents/obsidian_agent.py estado
python agents/obsidian_agent.py listar A1-INV
python agents/obsidian_agent.py ultimas --n 15
python agents/obsidian_agent.py buscar "estadística"
python agents/obsidian_agent.py ver N260410-Mi-nota
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C125-DAT "Nueva nota" --fecha 2026-04-10
```

## Apps Auxiliares

```bash
python apps/catalogar_repos.py
python apps/backs_todoist.py --parent <NOTION_PAGE_ID>
python apps/backs_notion.py --parent <NOTION_PAGE_ID>
python apps/backs_obsidian.py --parent <NOTION_PAGE_ID>
python apps/export_zinbox.py --parent <NOTION_PAGE_ID>
python apps/project_hub_gui.py
python apps/config_doctor.py
python apps/notion_doctor.py
```

## Arranque En Windows

Accesos principales:

- `apps/setup_venv.bat`: crea `.venv` e instala dependencias.
- `apps/config_doctor.bat`: comprueba `.env` y rutas locales.
- `apps/notion_doctor.bat`: valida el acceso a Notion y lista recursos visibles para localizar IDs.
- `apps/project_hub_gui.bat`: arranca el hub con el `venv`.
- `INICIAR_COWORKIA.bat`: arranque desde la raíz del repo.

Guía corta:

- `WINDOWS_START.md`

## Sistema Multiagente

El repo incluye una primera infraestructura de orquestación multiagente organizada con roles Scrum y trabajo por sprints.

Comandos principales:

```bash
python agents/orchestrator_agent.py agentes
python agents/orchestrator_agent.py roles
python agents/orchestrator_agent.py plan-sprint "Implementar sistema multiagente para REP y BIB" --nombre "Sprint Multiagent 1" --guardar
```

Documentación:

- `docs/multiagent-system.md`
- `multiagents/registry.py`
- `multiagents/planner.py`

## Estado Actual Del Proyecto

El repositorio ya es útil como conjunto de CLIs y utilidades de integración, pero conviene tener en cuenta estas limitaciones:

- La documentación antigua en `docs/guia-rapida.md` no refleja todos los comandos reales.
- No hay tests automatizados en la raíz del proyecto.
- Parte de Notion usa `data_sources` y parte sigue usando `databases`.
- La separación conceptual entre `Meta` y `Tarea` en Todoist no está resuelta completamente a nivel de datos.
- La dependencia de `.env` es alta: sin configuración válida, la mayoría de agentes no funcionarán.
- La GUI `project_hub_gui.py` ahora distingue entre error real y configuración incompleta, pero no puede suplir credenciales o IDs ausentes.

## Archivos Clave

- `CLAUDE.md`: contexto funcional y filosofía del sistema.
- `agents/`: punto de entrada principal para uso por CLI.
- `tools/`: wrappers reutilizables de APIs.
- `apps/dashboard.py`: vista operativa diaria para MAR.
- `apps/github_gui.py` y `apps/bib_gui.py`: interfaces de catalogación.
