## Caso de uso: <título>

### Objetivo

<Qué resultado operativo deja este flujo.>

### Actores

- **Usuario**: David
- **Sistema(s)**: Todoist / Notion / Obsidian / GitHub / Paperpile

### Trigger

<Qué dispara el flujo: captura de idea, cambio de estado, revisión diaria, etc.>

### Precondiciones

- **Acceso**: `.env` configurado (tokens/IDs).
- **Estructura**: PTN/KIT/REP/BIB disponibles en Notion; vault ABGD accesible.

### Datos y IDs (contrato)

- **Todoist**: `task_id`, `url`
- **Notion**: `page_id`/`database_id`/`data_source_id`, `url`
- **Obsidian**: `ruta_relativa` (y opcionalmente frontmatter si aplica)
- **INX**: `Clave` canónica (`todoist:<id>` / `ptn:<id>` / `obsidian:<ruta>` / `github:<Nombre>` / `paperpile:<citekey>`)

### Fuente de verdad (autoridad)

- **MAR (tiempo/ejecución)**: Todoist
- **PTN/KIT/REP/BIB (táctico/catálogos)**: Notion
- **Documentos**: Obsidian
- **Trazabilidad**: `INX-ENLACES` (Notion)

### Flujo principal (happy path)

1. <Paso>
2. <Paso>
3. <Paso>

### Variantes

- **Variante A**: <cuando ocurre>
- **Variante B**: <cuando ocurre>

### Postcondiciones / Resultado verificable

- **Qué queda creado** (filas/páginas/notas) y **qué enlaces** deben existir.
- **Qué estado** queda en cada sistema.

### Automatización actual

- **Comandos**:
  - `<comando>`

### Observabilidad

- **Dónde mirar**: `INX-ENLACES`, `TODOIST-TAREAS`, logs (`NOTION_DB`, `OBSIDIAN_DB`), `artifacts/*state.json`
- **Métricas de éxito**:
  - Tiempo total \(<X min\)
  - 0 duplicados
  - 0 enlaces rotos

### Gaps (lo que falta hoy)

- **Gap 1**: <qué falla / qué es manual / qué es frágil>

### Mejoras propuestas (acciones)

- **Mejora 1**: <script/cambio de schema/doctor/check>

