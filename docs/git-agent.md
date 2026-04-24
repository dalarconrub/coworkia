# Agente GIT — Repositorios GitHub → Notion

Cataloga y documenta repositorios de GitHub en una base de datos de Notion.
Permite importar, sincronizar, catalogar y explorar repos desde CLI o GUI.

## Arquitectura

```
GitHub API ──→ tools/github_tools.py ──→ agents/github_agent.py ──→ Notion API
                                              │
                                    apps/github_gui.py (GUI)
                                    apps/catalogar_repos.py (masivo)
```

| Archivo | Propósito |
|---------|-----------|
| `tools/github_tools.py` | Wrappers API GitHub REST v3 |
| `agents/github_agent.py` | Agente GIT: importar, sincronizar, catalogar, listar |
| `apps/github_gui.py` | Interfaz gráfica (tkinter) |
| `apps/catalogar_repos.py` | Script de catalogación masiva inicial |

## Requisitos en `.env`

```
GITHUB_TOKEN=ghp_...              # Token clásico con scope 'repo'
NOTION_GIT_PARENT_PAGE=xxx      # ID de la página padre donde se creó la BD
NOTION_DB_GIT=xxx               # ID de la BD GIT-Repositorios
```

### Cómo obtener `GITHUB_TOKEN`

1. GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → scope `repo` → copiar

### Cómo obtener `NOTION_GIT_PARENT_PAGE`

1. Crea una página en Notion (o usa una existente)
2. Comparte la página con tu integración de Notion (... → Conexiones)
3. Copia el ID de la URL: últimos 32 caracteres, formateados con guiones

## Comandos CLI

### Setup inicial (una vez)

```bash
python agents/github_agent.py crear-db
# Devuelve el ID → copiarlo a NOTION_DB_GIT en .env
```

### Importar repos

```bash
python agents/github_agent.py importar
python agents/github_agent.py importar --sin-lenguajes   # más rápido
```

Trae todos los repos del usuario autenticado. Detecta duplicados por nombre.

### Sincronizar metadata

```bash
python agents/github_agent.py sincronizar
```

Actualiza: estrellas, forks, lenguajes, última actividad. Marca archivados.

### Catalogar un repo

```bash
python agents/github_agent.py catalogar nombre-repo \
  --tipo Proyecto \
  --estado Activo \
  --version-de "repo-original" \
  --proceso "pipeline-datos" \
  --etiquetas ml python \
  --notas "Este repo es la v2 del pipeline"
```

### Listar repos

```bash
python agents/github_agent.py listar
python agents/github_agent.py listar --estado Activo --tipo Proyecto
python agents/github_agent.py listar --proceso "pipeline-datos"
```

### Estado general

```bash
python agents/github_agent.py estado
```

## Interfaz gráfica (GUI)

```bash
python apps/github_gui.py
```

Tres pestañas:

### Explorar
- Tabla con todos los repos y sus propiedades
- Filtros por búsqueda de texto, tipo, estado y proceso
- Ordenación por cualquier columna (click en encabezado, incluye fechas)
- Doble click en un repo abre su URL en el navegador

### Catalogar
- Selecciona un repo en Explorar
- Edita tipo, estado, versión de, proceso, etiquetas y notas
- Guarda cambios directo a Notion

### Acciones
- **Importar repos nuevos**: trae repos de GitHub que no están en Notion
- **Sincronizar metadata**: actualiza estrellas, forks, lenguajes y fechas
- **Recargar tabla**: vuelve a leer desde Notion
- Log de salida en tiempo real

## Catalogación masiva

```bash
python apps/catalogar_repos.py
```

Script para asignar tipo, proceso y cadenas de versión a todos los repos de una vez.
Editar el script para definir las clasificaciones y ejecutar una sola vez tras la importación inicial.

Define tres diccionarios:
- `PROCESOS`: agrupa repos que forman parte del mismo flujo
- `VERSIONES`: indica qué repo es versión mejorada de cuál
- `TIPOS`: clasifica cada repo (Proyecto, Ejercicio, Librería, Config, Template, Script)

## Propiedades de la base de datos

| Propiedad | Tipo | Auto | Descripción |
|-----------|------|------|-------------|
| Nombre | title | ✓ | Nombre del repo en GitHub |
| Estado | select | ✓* | Activo / WIP / Archivado / Deprecado / Pausado |
| Tipo | select | ✓* | Proyecto / Librería / Fork / Ejercicio / Config / Template / Script |
| Lenguajes | multi_select | ✓ | Lenguajes detectados por GitHub API |
| Etiquetas | multi_select | ✓ | Topics de GitHub + etiquetas manuales |
| Descripción | rich_text | ✓ | Descripción del repo en GitHub |
| URL | url | ✓ | Link al repo |
| Versión de | select | — | Nombre del repo del que es versión mejorada |
| Proceso | select | — | Nombre del proceso/flujo al que pertenece |
| Visibilidad | select | ✓ | Público / Privado |
| Creado | date | ✓ | Fecha de creación del repo |
| Última actividad | date | ✓ | Fecha del último push |
| Estrellas | number | ✓ | Stars del repo |
| Forks | number | ✓ | Forks del repo |
| Es fork | checkbox | ✓ | Si es fork de otro repo |
| Notas | rich_text | — | Notas manuales de catalogación |

*Auto = se rellena automáticamente al importar. ✓* = se auto-detecta parcialmente (archivado, fork).

## Flujo recomendado

1. **Setup**: `crear-db` → copiar ID a `.env`
2. **Importar**: `importar` → trae todos los repos con metadata
3. **Catalogar**: editar `catalogar_repos.py` con tus clasificaciones → ejecutar
4. **Explorar**: `python apps/github_gui.py` → revisar y ajustar en la GUI
5. **Mantener**: `sincronizar` periódicamente para actualizar metadata
