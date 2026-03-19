# COWORKIA — Contexto para Claude Code

## Qué es este proyecto

Sistema multi-agente IA para gestión personal integrado con los sistemas MAR+ABGD+PTN+KIT+REP de David.

Los agentes deben conocer y respetar la filosofía del sistema: no se improvisa, se clasifica.

---

## Herramientas del usuario

| Herramienta | Propósito | Sistema | Agente |
|-------------|-----------|---------|--------|
| Todoist     | Tareas    | MAR (Meta-Acción-Resultado) | `todoist_agent.py` |
| Notion      | Proyectos | PTN (Proyectos-Tareas-Notas) | `notion_agent.py` |
| Notion      | Conocimiento | KIT (Knowledge-Information-Tools) | `kit_agent.py` |
| Notion      | Repositorios | REP (Repositorios GitHub) | `github_agent.py` |
| Notion      | Bibliografía | BIB (Bibliografía Paperpile) | `bib_agent.py` |
| Obsidian    | Documentos | ABGD (Alpha/Beta/Delta/Gamma) | `obsidian_agent.py` |
| GitHub      | Código    | Fuente de repos para REP | `github_agent.py` |
| Paperpile   | Papers    | Fuente de papers para BIB | `bib_agent.py` |

---

## Sistema MAR — Clasificación de tareas en Todoist

**Principio:** Las acciones se clasifican por cómo existen en el tiempo, no por lo que son.

### Tipos de acción (filtros Todoist)

| Tipo   | Filtro Todoist                              | Significado |
|--------|---------------------------------------------|-------------|
| Idea   | `no date & no deadline`                     | Sin fecha ni deadline |
| Meta   | `!recurring & !!no time & !no deadline`     | Compromiso puntual de un día |
| Hábito | `recurring & no time & no deadline`         | Rutina recurrente |
| Tarea  | `no time & !no deadline`                    | Trabajo flexible con deadline |
| Evento | `!no time`                                  | Hora fija |

### Horizonte temporal (mutuamente excluyentes)

| Horizonte    | Filtro |
|--------------|--------|
| +->Hoy       | `(!#Z-* & !search:*) & (overdue \| due before: +1 day)` |
| -+>1 Día     | `(!#Z-* & !search:*) & due after: yesterday & due before: +2day` |
| +->1 Semana  | `(!#Z-* & !search:*) & due after: today & due before: +7day` |
| +->1 Mes     | `(!#Z-* & !search:*) & (due after: +7 days & due before: +30 days)` |
| +->1 Año     | `(!#Z-* & !search:*) & (due after: +30 days & due before: +365 days)` |

**Regla de oro:** Los filtros de tipo dicen QUÉ es. Los horizontes dicen CUÁNDO vive. Nunca se mezclan.

---

## Sistema ABGD — Organización de documentos en Obsidian

### Estructura de primer nivel

| Carpeta | Propósito |
|---------|-----------|
| Alpha   | Vault activo (Johnny Decimal: Área → Bloque → Contexto) |
| Beta    | Backups cronológicos |
| Delta   | Archivo clasificado (DOC, LIB, MED, SOF) |
| Gamma   | Almacenamiento temporal |

### Áreas Alpha (nivel 1)

| Código  | Nombre | Descripción |
|---------|--------|-------------|
| A0-GTD  | Getting Things Done | Sistema operativo diario |
| A1-INV  | Investigación | Investigación académica |
| A2-UNI  | Universidad | Docencia y contenido universitario |
| A3-VIT  | Vital | Información personal |
| A4-ARC  | Archivo | Conocimiento consolidado |

---

## Sistema REP — Catálogo de repositorios GitHub en Notion

**Principio:** Cada repositorio se cataloga con su tipo, estado, proceso y cadena de versiones.

### Propiedades de la BD `REP-Repositorios`

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| Nombre | title | Nombre del repo |
| Estado | select | Activo / WIP / Archivado / Deprecado / Pausado |
| Tipo | select | Proyecto / Librería / Fork / Ejercicio / Config / Template / Script |
| Lenguajes | multi_select | Detectados por GitHub |
| Etiquetas | multi_select | Topics de GitHub + manuales |
| Versión de | select | Repo del que es versión mejorada |
| Proceso | select | Flujo/grupo al que pertenece |
| Visibilidad | select | Público / Privado |
| Creado | date | Fecha de creación |
| Última actividad | date | Último push |

### Flujo de trabajo

1. `python agents/github_agent.py importar` — trae repos nuevos de GitHub
2. `python agents/github_agent.py sincronizar` — actualiza metadata
3. `python agents/github_agent.py catalogar <repo> --tipo X --proceso Y` — clasifica
4. `python apps/github_gui.py` — interfaz gráfica para explorar y catalogar

---

## Sistema BIB — Catálogo bibliográfico de Paperpile en Notion

**Principio:** Cada paper se importa automáticamente desde Paperpile y se enriquece con estado de lectura, relevancia y notas.

**Fuente de datos:** URL de Automatic BibTeX Export de Paperpile (sin API oficial).

### Propiedades de la BD `BIB-Bibliografía`

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| Título | title | Título del paper |
| Autores | rich_text | Lista de autores |
| Año | number | Año de publicación |
| Tipo | select | Artículo / Libro / Conferencia / Tesis / etc. |
| Journal | rich_text | Revista o conferencia |
| DOI | url | Enlace DOI |
| Keywords | multi_select | Palabras clave del paper |
| Carpeta | select | Carpeta de Paperpile |
| Etiquetas | multi_select | Labels de Paperpile + manuales |
| Estado | select | Por leer / En proceso / Leído / Revisado / Descartado |
| Relevancia | select | Alta / Media / Baja |
| Notas | rich_text | Notas manuales |

### Flujo de trabajo

1. `python agents/bib_agent.py importar` — trae papers nuevos de Paperpile
2. `python agents/bib_agent.py sincronizar` — actualiza existentes + nuevos
3. `python agents/bib_agent.py catalogar <citekey> --estado Leído --relevancia Alta`
4. `python apps/bib_gui.py` — interfaz gráfica para explorar y catalogar

---

## Estructura del proyecto

```
coworkia/
├── .env                    ← API keys (NO al repo)
├── CLAUDE.md               ← este archivo
├── requirements.txt        ← dependencias Python
├── Sistemas/               ← documentación de referencia de los sistemas
├── agents/
│   ├── todoist_agent.py    ← agente MAR/Todoist
│   ├── notion_agent.py     ← agente PTN/Notion
│   ├── kit_agent.py        ← agente KIT/Notion
│   ├── github_agent.py     ← agente REP/GitHub→Notion
│   ├── bib_agent.py        ← agente BIB/Paperpile→Notion
│   └── obsidian_agent.py   ← agente ABGD/Obsidian
├── tools/
│   ├── todoist_tools.py    ← wrappers API Todoist REST v1
│   ├── notion_tools.py     ← wrappers API Notion v2022-06-28
│   ├── github_tools.py     ← wrappers API GitHub REST v3
│   ├── paperpile_tools.py  ← parser BibTeX de Paperpile
│   └── obsidian_tools.py   ← lectura/escritura vault local
├── apps/
│   ├── github_gui.py       ← GUI para el sistema REP
│   ├── bib_gui.py          ← GUI para el sistema BIB
│   ├── catalogar_repos.py  ← catalogación masiva de repos
│   ├── dashboard.py        ← dashboard MAR/Todoist
│   ├── export_zinbox.py    ← exportar Z-INBOX
│   ├── backs_todoist.py    ← backup Todoist
│   ├── backs_notion.py     ← backup Notion
│   └── backs_obsidian.py   ← backup Obsidian
└── docs/
    ├── todoist-agent.md    ← guía agente MAR
    ├── notion-ptn-agent.md ← guía agente PTN
    ├── notion-kit-agent.md ← guía agente KIT
    ├── github-rep-agent.md ← guía agente REP
    ├── bib-agent.md        ← guía agente BIB
    └── obsidian-agent.md   ← guía agente ABGD
```

---

## Variables de entorno (`.env`)

| Variable | Servicio | Descripción |
|----------|----------|-------------|
| `TODOIST_API_KEY` | Todoist | Token API v1 |
| `NOTION_TOKEN` | Notion | Token de integración |
| `NOTION_DS_PROYECTOS` | Notion | Data source PTN-Proyectos |
| `NOTION_DS_TAREAS` | Notion | Data source PTN-Tareas |
| `NOTION_DS_NOTAS` | Notion | Data source PTN-Notas |
| `NOTION_DS_KIT_KNOWLEDGE` | Notion | Data source KIT-Knowledge |
| `NOTION_DS_KIT_INFORMATION` | Notion | Data source KIT-Information |
| `NOTION_DS_KIT_TOOLS` | Notion | Data source KIT-Tools |
| `GITHUB_TOKEN` | GitHub | Token clásico (scope `repo`) |
| `NOTION_REPOS_PARENT_PAGE` | Notion | Página padre de REP-Repositorios |
| `NOTION_DB_REPOS` | Notion | ID de la BD REP-Repositorios |
| `PAPERPILE_BIBTEX_URL` | Paperpile | URL de Automatic BibTeX Export |
| `NOTION_BIB_PARENT_PAGE` | Notion | Página padre de BIB-Bibliografía |
| `NOTION_DB_BIB` | Notion | ID de la BD BIB-Bibliografía |
| `OBSIDIAN_ABGD_ROOT` | Obsidian | Ruta raíz del vault ABGD |
| `OBSIDIAN_ALPHA_PATH` | Obsidian | Ruta a la carpeta Alpha |

---

## Convenciones de código

- Python 3.10+
- Variables de entorno via `python-dotenv`
- Anthropic SDK para los agentes IA (pendiente de integración)
- APIs: Todoist REST v1, Notion v2022-06-28, GitHub REST v3, Paperpile (BibTeX export)
- Cada agente tiene CLI con argparse y puede usarse de forma independiente
- Sin frameworks innecesarios — código directo y legible
