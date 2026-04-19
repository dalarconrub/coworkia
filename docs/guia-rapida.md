# Coworkia — Guía rápida de uso

Sistema multi-agente para gestión personal. Integra Todoist, Notion, Obsidian, GitHub y Paperpile bajo una filosofía común: **no se improvisa, se clasifica**.

---

## Instalación

```bash
cd coworkia
pip install -r requirements.txt
```

Configura `.env` con tus tokens y IDs (ver sección de cada sistema).

---

## Sistemas y comandos

### MAR — Tareas (Todoist)

Clasifica acciones por cómo existen en el tiempo: Idea, Meta, Hábito, Tarea, Evento.

```bash
# Dashboard diario: pendientes + hoy + inbox
python apps/dashboard.py

# Resumen del día
python agents/todoist_agent.py resumen

# Estado del sistema MAR
python agents/todoist_agent.py estado

# Listar por tipo
python agents/todoist_agent.py listar --tipo meta
python agents/todoist_agent.py listar --tipo evento
```

---

### PTN — Proyectos, Tareas, Notas (Notion)

Gestiona el ciclo de trabajo: Proyectos → Tareas → Notas de seguimiento.

```bash
# Estado general
python agents/notion_agent.py estado

# Proyectos
python agents/notion_agent.py proyectos
python agents/notion_agent.py proyectos --estado "En progreso"
python agents/notion_agent.py nuevo-proyecto "Mi proyecto" --prioridad Alta

# Tareas
python agents/notion_agent.py tareas
python agents/notion_agent.py nueva-tarea "Hacer X" --proyecto-id xxx

# Notas
python agents/notion_agent.py notas
python agents/notion_agent.py nueva-nota "Reunión Y" --proyecto-id xxx
```

---

### KIT — Knowledge, Information, Tools (Notion)

Almacena conocimiento interno, información externa y herramientas.

```bash
# Estado del KIT
python agents/kit_agent.py estado

# Listar por fuente
python agents/kit_agent.py knowledge
python agents/kit_agent.py information
python agents/kit_agent.py tools

# Buscar en todo el KIT
python agents/kit_agent.py buscar "machine learning"

# Crear entradas
python agents/kit_agent.py nueva-knowledge "Concepto X" --tipo Síntesis
python agents/kit_agent.py nueva-information "Paper Y" --enlace https://...
python agents/kit_agent.py nueva-tool "Herramienta Z" --tipo App
```

---

### REP — Repositorios GitHub (Notion)

Cataloga repos con tipo, estado, proceso y cadenas de versión.

```bash
# Importar repos nuevos de GitHub
python agents/github_agent.py importar

# Sincronizar metadata (estrellas, forks, lenguajes, fechas)
python agents/github_agent.py sincronizar

# Catalogar un repo
python agents/github_agent.py catalogar mi-repo \
  --tipo Proyecto --estado Activo \
  --proceso "pipeline-datos" --version-de "repo-viejo"

# Listar con filtros
python agents/github_agent.py listar
python agents/github_agent.py listar --tipo Proyecto --estado Activo
python agents/github_agent.py listar --proceso "pipeline-datos"

# Estado general
python agents/github_agent.py estado

# Interfaz gráfica
python apps/github_gui.py
```

**GUI REP** — 3 pestañas: Explorar (tabla con filtros y ordenación), Catalogar (editar propiedades), Acciones (importar/sincronizar).

---

### BIB — Bibliografía Paperpile (Notion)

Cataloga papers académicos con estado de lectura y relevancia.

```bash
# Setup inicial (una vez)
python agents/bib_agent.py crear-db

# Importar papers de Paperpile
python agents/bib_agent.py importar

# Sincronizar (nuevos + actualizar existentes)
python agents/bib_agent.py sincronizar

# Catalogar un paper
python agents/bib_agent.py catalogar einstein2005 \
  --estado "Leído" --relevancia Alta \
  --notas "Metodología interesante"

# Listar con filtros
python agents/bib_agent.py listar
python agents/bib_agent.py listar --estado "Por leer" --tipo Artículo
python agents/bib_agent.py listar --carpeta "My Research"

# Estado general
python agents/bib_agent.py estado

# Interfaz gráfica
python apps/bib_gui.py
```

**GUI BIB** — 3 pestañas: Explorar (tabla con filtros, doble click abre DOI), Catalogar (estado/relevancia/notas), Acciones (importar/sincronizar).

---

### ABGD — Documentos Obsidian

Organiza documentos en un vault local con jerarquía Johnny Decimal.

```bash
# Mapa del vault
python agents/obsidian_agent.py mapa

# Listar por nivel
python agents/obsidian_agent.py listar --area A1-INV

# Últimas notas
python agents/obsidian_agent.py ultimas

# Buscar
python agents/obsidian_agent.py buscar "estadística"

# Crear nota
python agents/obsidian_agent.py nueva-nota "Mi nota" --ruta "A1-INV/B10/C10.01"

# Estado del vault
python agents/obsidian_agent.py estado
```

---

## Aplicaciones (apps/)

| Comando | Qué hace |
|---------|----------|
| `python apps/pipeline_gui.py` | **Pipeline Atlas** — navega el proyecto completo por dominios con estado vivo |
| `python apps/dashboard.py` | Dashboard diario MAR (pendientes + hoy + inbox) |
| `python apps/github_gui.py` | GUI del catálogo de repositorios |
| `python apps/bib_gui.py` | GUI del catálogo bibliográfico |
| `python apps/catalogar_repos.py` | Catalogación masiva de repos (editar y ejecutar una vez) |
| `python apps/backs_todoist.py` | Backup de Todoist |
| `python apps/backs_notion.py` | Backup de Notion |
| `python apps/backs_obsidian.py` | Backup de Obsidian |
| `python apps/export_zinbox.py` | Exportar Z-INBOX |

---

## Coordinación multiagente

Capas de conocimiento y herramientas que usan Claude, Copilot y Codex cuando trabajan sobre el proyecto (y que tú puedes consultar directamente).

### Memoria curada — `memory/`

Primer lugar donde mirar si quieres entender el proyecto hoy.

| Archivo | Qué contiene |
|---------|--------------|
| `memory/INDEX.md` | Meta-índice de todos los recursos con orden de lectura |
| `memory/PURPOSE.md` | Qué es Coworkia, visión, principios no negociables |
| `memory/STRUCTURE.md` | Mapa de carpetas + árbol auto-generado |
| `memory/SNAPSHOT.md` | Agregado de `MEMORIA:` / `BLOQUEO:` / `SIGUIENTE:` de todos los chats (auto-generado) |

Regeneración y salud:

```bash
python tools/snapshot_structure.py         # regenera el árbol de STRUCTURE.md
python tools/memory_check.py               # valida memory/ (ficheros, enlaces, TREE)
python tools/memory_check.py --fix-tree    # idem pero regenera el árbol si está desfasado
```

### Chat del día — `chats/`

Hilo compartido append-only, un fichero por día.

```bash
python tools/init_chat.py                  # resolver chat activo + briefing (memory + devlog)
python tools/init_chat.py --quiet          # solo la ruta (uso desde scripts)
```

`init_chat.py` sin flags imprime el estado de `memory/` y las últimas 3 entradas del devlog — útil para arrancar sesión.

### DevLog — `devlog/DEVLOG.md`

Registro append-only de hitos del proyecto (features, cierres, bloqueos, reverts). No es por commit, es por hito.

```bash
python tools/devlog.py view                                    # últimas 20
python tools/devlog.py view --area PTN --limit 5
python tools/devlog.py view --status BLOCKED

python tools/devlog.py append \
  --agent Claude --area PTN --status DONE \
  --title "..." --summary "..." \
  [--commits sha1,sha2] [--refs "CERRADO #N"] [--sprint "<nombre>"]
```

Áreas: `MAR`, `PTN`, `KIT`, `REP`, `BIB`, `ABGD`, `INX`, `MULTIAGENT`, `TOOLING`, `DOCS`, `INFRA`.
Estados: `START`, `PROGRESS`, `BLOCKED`, `UNBLOCKED`, `DONE`, `REVERT`.

### Vista temporal — `artifacts/daily/`

Agrega chat + devlog + INX + sprints por fecha:

```bash
python tools/timeline.py                             # hoy
python tools/timeline.py --date 2026-04-18
python tools/timeline.py --from 2026-04-15 --to 2026-04-18
python tools/timeline.py --days 7                    # últimos 7 días
python tools/timeline.py --date 2026-04-18 --stdout  # no escribe, imprime
```

### Memoria multiagente derivada — `artifacts/multiagent/`

Se regenera desde el chat del día más `memory/SNAPSHOT.md` (proyecto):

```bash
python agents/orchestrator_agent.py sync-chat-memory
```

Genera `conversation_records.jsonl`, `decision_log.json`, `agent_state.json`, `memory_records.json`, `chat_memory.md`, y actualiza `memory/SNAPSHOT.md` agregando `MEMORIA/BLOQUEO/SIGUIENTE` de todos los chats.

---

## Setup de tokens y APIs

### Todoist
1. Todoist → Settings → Integrations → Developer → API token
2. `.env`: `TODOIST_API_KEY=tu_token`

### Notion
1. notion.so/my-integrations → New integration → copiar token
2. Compartir cada página/BD con la integración (... → Conexiones)
3. `.env`: `NOTION_TOKEN=ntn_...`
4. IDs de data sources: abrir en Notion → copiar de la URL

### GitHub
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Scope: `repo`
3. `.env`: `GITHUB_TOKEN=ghp_...`

### Paperpile
1. Paperpile → Settings → Workflows & Integrations → Automatic BibTeX Export
2. Activar para toda la biblioteca → copiar URL de descarga
3. `.env`: `PAPERPILE_BIBTEX_URL=https://paperpile.com/eb/...`

### Obsidian
1. Apuntar a la raíz de tu vault ABGD
2. `.env`: `OBSIDIAN_ABGD_ROOT=G:/Mi unidad/ABGD/ABGD-25.09.05`

---

## Rutinas recomendadas

### Al empezar sesión
```bash
python tools/init_chat.py                   # chat del día + briefing (memory + devlog)
python tools/memory_check.py                # valida memory/ en orden
```

### Diaria
```bash
python apps/dashboard.py                    # Ver pendientes + hoy
python agents/todoist_agent.py resumen      # Resumen MAR
python tools/timeline.py                    # Timeline del día (opcional)
```

### Al cerrar un hito o sesión
```bash
python tools/devlog.py append ...                    # registrar hito feature-level
python agents/orchestrator_agent.py sync-chat-memory # propagar MEMORIA del chat a memory/SNAPSHOT.md
```

En Windows, el cierre operativo recomendado ya encadena todo:

```bash
apps\cerrar_sesion.bat
```

Incluye `sync-chat-memory`, regeneración de `artifacts/daily/YYYY-MM-DD.md` y `memory_check`.

### Semanal
```bash
python agents/github_agent.py sincronizar   # Actualizar repos
python agents/bib_agent.py sincronizar      # Actualizar papers
python agents/notion_agent.py estado        # Revisar proyectos
python agents/kit_agent.py estado           # Revisar conocimiento
```

### Al añadir contenido nuevo
```bash
python agents/github_agent.py importar      # Tras crear repos nuevos
python agents/bib_agent.py importar         # Tras añadir papers en Paperpile
```

### Backups (mensual)
```bash
python apps/backs_todoist.py
python apps/backs_notion.py
python apps/backs_obsidian.py
```
