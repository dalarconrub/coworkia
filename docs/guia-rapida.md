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
| `python apps/dashboard.py` | Dashboard diario MAR (pendientes + hoy + inbox) |
| `python apps/github_gui.py` | GUI del catálogo de repositorios |
| `python apps/bib_gui.py` | GUI del catálogo bibliográfico |
| `python apps/catalogar_repos.py` | Catalogación masiva de repos (editar y ejecutar una vez) |
| `python apps/backs_todoist.py` | Backup de Todoist |
| `python apps/backs_notion.py` | Backup de Notion |
| `python apps/backs_obsidian.py` | Backup de Obsidian |
| `python apps/export_zinbox.py` | Exportar Z-INBOX |

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

### Diaria
```bash
python apps/dashboard.py                    # Ver pendientes + hoy
python agents/todoist_agent.py resumen      # Resumen MAR
```

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
