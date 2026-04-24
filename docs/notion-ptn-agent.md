# Notion PTN Agent — Guía de uso

Agente para el sistema **PTN (Proyectos-Tareas-Notas)** en Notion.

## Jerarquía

```text
Proyecto -> Tarea -> Nota
```

Regla:

- un proyecto tiene tareas
- una tarea pertenece a un proyecto
- una nota siempre pertenece a una tarea
- una nota sin tarea no forma parte del modelo PTN

## Vistas operativas recomendadas (manual en Notion)

Notion no permite crear vistas por API. Estas vistas se configuran manualmente en la UI:

### En cada página de **Proyecto**

Insertar una **Linked Database** de `PTN-Tareas` y filtrar:

- Filtro: `Proyecto` contiene el ID o referencia del proyecto actual
- Nombre sugerido de vista: `Tareas del proyecto`

### En cada página de **Tarea**

Insertar una **Linked Database** de `PTN-Notas` y filtrar:

- Filtro: `Tarea` contiene el ID o referencia de la tarea actual
- Nombre sugerido de vista: `Notas de la tarea`

### En cada página de **Nota**

Insertar **Linked Databases** de:

- `KIT`
- `GIT`
- `BIB`

Aplicar filtros según los medios necesarios para la nota.

## Data Sources

Ubicación canónica en Notion: `A0-GTD / B0C-PLA` y dividido en:

- `C0C7-PROYECTOS` → `PTN-Proyectos`
- `C0C8-TAREAS` → `PTN-Tareas`
- `C0C9-NOTAS` → `PTN-Notas`

IDs en `.env`:

- `NOTION_DS_PROYECTOS`
- `NOTION_DS_TAREAS`
- `NOTION_DS_NOTAS`

---

## Comandos

### Consultas

```bash
# Estado general del sistema PTN
python agents/notion_agent.py estado

# Todos los recursos Notion accesibles
python agents/notion_agent.py recursos

# Listar proyectos (todos o filtrados por estado)
python agents/notion_agent.py proyectos
python agents/notion_agent.py proyectos --estado "En progreso"
python agents/notion_agent.py proyectos --estado "Sin empezar"

# Listar tareas
python agents/notion_agent.py tareas
python agents/notion_agent.py tareas --estado "En progreso"
python agents/notion_agent.py tareas --tipo "Investigación"

# Listar notas
python agents/notion_agent.py notas
python agents/notion_agent.py notas --estado "Activo"

# Inspeccionar schema de un data source
python agents/notion_agent.py db <NOTION_DS_PROYECTOS>
```

### Crear

```bash
python agents/notion_agent.py crear-bases --parent <NOTION_PAGE_ID>

# Nuevo proyecto
python agents/notion_agent.py nuevo-proyecto "Estudio neuropsicológico 2026"
python agents/notion_agent.py nuevo-proyecto "Paper revisión" \
  --estado "En progreso" \
  --prioridad "Alta" \
  --inicio 2026-03-01 \
  --limite 2026-06-30

# Nueva tarea
python agents/notion_agent.py nueva-tarea "Revisar bibliografía"
python agents/notion_agent.py nueva-tarea "Análisis estadístico" \
  --estado "Sin empezar" \
  --tipo "Investigación" \
  --prioridad "Alta" \
  --plazo 2026-04-15 \
  --proyecto <ID_del_proyecto>

# Nueva nota
python agents/notion_agent.py nueva-nota "Reunión con Enrique" --tarea <ID_o_referencia_tarea>
python agents/notion_agent.py nueva-nota "Sesión de trabajo" \
  --tarea <ID_o_referencia_tarea> \
  --fecha 2026-03-16 \
  --proyecto <ID_del_proyecto>
```

---

## Propiedades por data source

### PTN-Proyectos
`Nombre del Proyecto` · `Estado` · `Prioridad` · `Progreso` · `Fecha de inicio` · `Fecha límite` · `Equipo` · `Descripción` · `Etiquetas` · `URL` · `PLAN` · `Responsable`

### PTN-Tareas
`Nombre de la tarea` · `Estado` · `Tipo de tarea` · `Prioridad` · `Nivel de esfuerzo` · `Plazo` · `Proyectos` · `Descripción` · `Etiquetas` · `Responsable` · `Última actualización`

### PTN-Notas
`Título` · `Estado` · `Estado de Progreso` · `Prioridad` · `Fecha` · `Fecha de Vencimiento` · `Tarea` · `Proyecto` · `Próximos Pasos` · `Obstáculos` · `Tiempo Dedicado` · `Descripción` · `Etiquetas`

---

## API usada

- **Notion API v2025-09-03** (multi-source databases)
- Token en `.env` → `NOTION_TOKEN`
- IDs en `.env` → `NOTION_DS_PROYECTOS`, `NOTION_DS_TAREAS`, `NOTION_DS_NOTAS`
- Página padre opcional en `.env` → `NOTION_PTN_PARENT_PAGE`
