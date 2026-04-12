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

## Convención Canónica

Coworkia separa tres funciones distintas:

- `Todoist` ejecuta.
- `Notion` dirige.
- `Obsidian` almacena.

Eso implica esta jerarquía:

- `Todoist` es el `Task Management System` y funciona como sistema atencional.
- `Notion` es el `Project Management System` y funciona como memoria de trabajo.
- `Obsidian` es el `Document Management System` y funciona como memoria a largo plazo.

Reglas de trabajo:

- Si algo requiere foco, fecha, recurrencia, plazo o evento, manda `Todoist`.
- Si algo requiere captura, contexto, relación entre objetos, seguimiento de proyecto o catálogo, manda `Notion`.
- Si algo requiere conservación documental, escritura larga o archivo estable, manda `Obsidian`.
- Las exportaciones de Todoist a Notion no sustituyen a `MAR`.
- `ABGD` debe entenderse como taxonomía estructural compartida, no como sinónimo de “todo vive en Obsidian”.

Ubicación operativa recomendada en Notion:

- `PTN`: sistema director en `A0-GTD / B0C-PLA`, dividido en:
  - `C0C7-PROYECTOS` → `PTN-Proyectos`
  - `C0C8-TAREAS` → `PTN-Tareas`
  - `C0C9-NOTAS` → `PTN-Notas`
- `KIT`: catálogo maestro en `A4-ARX / B40-REF / C400-REF`.
- `REP`: catálogo técnico en `A4-ARX / B4Z-APP`.
- `BIB`: catálogo bibliográfico en `A4-ARX / B4X-LIB`.
- `BACK-*`: siempre en `A5-BACK` o `Z9_BACK`.

## Mapa Maestro

La taxonomía `ABC` organiza Notion por `Área -> Bloque -> Contexto`. En el sistema actual queda así:

- `A0-GTD`: sistema operativo
  - `B00-GTD`: `MAR` y ejecución en Todoist
- `B0A-INX`: integración y trazabilidad entre sistemas
  - `C0A1-TODOIST` → `TODOIST-TAREAS` (relación PTN + ABC)
  - `C0A2-NOTION` → `NOTION` (histórico PTN + ABC)
  - `C0A3-OBSIDIAN` → `OBSIDIAN` (histórico Obsidian + PTN + ABC)
  - Relaciones cruzadas: `TODOIST-TAREAS` → `NOTION` → `OBSIDIAN` (+ retorno a `NOTION`)
  - Criterio de llenado:
    - `TODOIST-TAREAS`: alta/movimiento de tareas Todoist + relación PTN/ABC
    - `NOTION`: cambios en PTN (proyectos/tareas/notas)
    - `OBSIDIAN`: cambios en notas Obsidian
  - `B0B-ABC`: taxonomía estructural
  - `B0C-PLA`: dirección y planificación (`PTN`)
- `A1-INV`: investigación
  - `B11-CVT`: `C111-VIT`, `C112-CON`, `C113-EVA`
  - `B12-LAB`: `C124-PRY`, `C125-DAT`, `C126-DIR`
  - `B13-PUB`: `C137-ART`, `C138-CON`, `C139-MAN`
- `A2-UNI`: universidad
  - `B24-DOC`: `C241-GRA`, `C242-MAS`, `C243-POS`
  - `B25-FOR`: `C254-PDI`, `C255-EST`, `C256-CUR`
  - `B26-GES`: `C267-UPO`, `C268-MIN`, `C269-EVA`
- `A3-VIT`: vida personal
  - `B37-ORG`: `C371-ADM`, `C372-PER`, `C373-SOC`
  - `B38-TEC`: `C384-INF`, `C386-STA`, `C387-IAA`
  - `B39-DES`: `C397-FIS`, `C398-MEN`, `C399-MUS`
- `A4-ARX`: archivo y recursos documentales
  - `B40-REF`: `C400-REF`
  - `B4X-LIB`: `C4x0-LIB`, `C4x1-FIC`, `C4x2-SCI`, `C4x3-ENS`
  - `B4Y-MED`: `C4y0-MED`, `C4y4-VID`, `C4y5-AUD`, `C4y6-MP3`
  - `B4Z-APP`: `C4z0-APP`, `C4z7-MOC`, `C4z8-WEB`, `C4z9-SOF`

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
NOTION_PTN_PARENT_PAGE=

NOTION_DB_KIT=
NOTION_KIT_PARENT_PAGE=

GITHUB_TOKEN=
NOTION_REPOS_PARENT_PAGE=
NOTION_DB_REPOS=

PAPERPILE_BIBTEX_URL=
NOTION_BIB_PARENT_PAGE=
NOTION_DB_BIB=

TODOIST_DB_TAREAS=
NOTION_DB=
OBSIDIAN_DB=

OBSIDIAN_ABGD_ROOT=
OBSIDIAN_ALPHA_PATH=
```

Notas:

- `NOTION_TOKEN` debe tener acceso a las páginas o bases compartidas con la integración.
- `PTN` sigue necesitando `NOTION_TOKEN` y fuentes accesibles.
- `KIT` usa una sola base maestra `KIT` y un campo `Tipo` para separar `Knowledge`, `Information` y `Tool`.
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
python agents/todoist_agent.py zinbox --limit 20
python agents/todoist_agent.py buscar "tesis"
python agents/todoist_agent.py ver <TASK_ID>
python agents/todoist_agent.py idea "Idea sin fecha"
python agents/todoist_agent.py capturar "Nueva entrada"
python agents/todoist_agent.py meta "Entregar memoria" 2026-04-15
python agents/todoist_agent.py habito "Leer 20 minutos" "every day"
python agents/todoist_agent.py tarea "Preparar informe" 2026-04-20
python agents/todoist_agent.py evento "Reunión" 2026-04-15T10:00:00
python agents/todoist_agent.py completar <TASK_ID>
python agents/todoist_agent.py mover <TASK_ID> <PROJECT_ID>
python agents/todoist_agent.py editar <TASK_ID> --due-date 2026-04-15
python agents/todoist_agent.py reclasificar <TASK_ID> evento --valor 2026-04-15T10:00:00
python agents/todoist_agent.py procesar <TASK_ID> meta <PROJECT_ID> --valor 2026-04-15
```

Estructura alineada con Notion:

- Todoist mantiene proyectos `A*` y `B*` solo para agrupación liviana.
- La clasificación fina (Área/Bloque/Contexto) se hace en Notion.

### PTN / Notion

```bash
python agents/notion_agent.py recursos
python agents/notion_agent.py estado
python agents/notion_agent.py crear-bases --parent <NOTION_PAGE_ID>
python agents/notion_agent.py proyectos
python agents/notion_agent.py proyectos --estado "En progreso"
python agents/notion_agent.py tareas --estado "Sin empezar"
python agents/notion_agent.py notas
python agents/notion_agent.py nuevo-proyecto "Proyecto X" --prioridad Alta --inicio 2026-04-10
python agents/notion_agent.py nueva-tarea "Hacer X" --proyecto <ID_PROYECTO>
python agents/notion_agent.py nueva-nota "Seguimiento" --tarea <ID_TAREA> --fecha 2026-04-10 --proyecto <ID_PROYECTO>
```

### KIT / Notion

```bash
python agents/kit_agent.py estado
python agents/kit_agent.py crear-db --parent <NOTION_PAGE_ID>
python agents/kit_agent.py knowledge
python agents/kit_agent.py information
python agents/kit_agent.py tools
python agents/kit_agent.py buscar "machine learning"
python agents/kit_agent.py nueva-knowledge "Concepto X" --subtipo Sintesis
python agents/kit_agent.py nueva-information "Paper Y" --subtipo Paper --enlace https://example.com
python agents/kit_agent.py nueva-tool "Herramienta Z" --subtipo App
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

## B0A-INX (llenado manual)

```bash
python tools/sync_todoist_to_notion.py
python tools/log_ptn_changes.py
python tools/log_obsidian_changes.py
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
- Algunas páginas y bases heredadas de Notion no son accesibles por API aunque existan en la UI. En esos casos hay que crear o compartir las páginas con la integración para que los agentes puedan operar.

## Acceso Notion (Problema y Solución)

Problema detectado:

- Hay páginas visibles en Notion que no responden a la API (`400` o `no accesible`).
- Ocurre especialmente en bases heredadas (`ABC`, `AREA`, `BLOQUE`, `CONTEXTO`) o páginas no compartidas con la integración.

Solución práctica para que los agentes funcionen:

1. Asegurar que la integración está en el mismo workspace.
2. Compartir con la integración las páginas raíz operativas (`A0-GTD` y subpáginas).
3. Si una base heredada no es accesible, recrearla en un contenedor accesible y actualizar los IDs del `.env`.

Mapeo operativo confirmado bajo `A0-GTD`:

- `B0A-INX` (página accesible) → integración y trazabilidad:
  - `C0A1-TODOIST` → `TODOIST-TAREAS`
  - `C0A2-NOTION` → `NOTION`
  - `C0A3-OBSIDIAN` → `OBSIDIAN`
- `B0B-ABC` (página accesible) → taxonomía `ABC`
- `B0C-PLA` (página accesible) → `PTN`:
  - `C0C7-PROYECTOS` → `PTN-Proyectos`
  - `C0C8-TAREAS` → `PTN-Tareas`
  - `C0C9-NOTAS` → `PTN-Notas`

Mapeo operativo en `A4-ARX`:

- `C400-REF` → `KIT`
- `B4Z-APP` → `REP`
- `B4X-LIB` → `BIB`

Los agentes deben asumir lo siguiente:

- Si un ID en `.env` no responde, el agente debe recrear la base en el contenedor correcto y sobrescribir el ID.
- `PTN` vive en `B0C-PLA`
- `KIT/REP/BIB` viven en `B0A-KIT`

## Archivos Clave

- `CLAUDE.md`: contexto funcional y filosofía del sistema.
- `agents/`: punto de entrada principal para uso por CLI.
- `tools/`: wrappers reutilizables de APIs.
- `apps/dashboard.py`: vista operativa diaria para MAR.
- `apps/github_gui.py` y `apps/bib_gui.py`: interfaces de catalogación.
