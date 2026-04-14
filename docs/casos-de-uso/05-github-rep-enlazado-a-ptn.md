## Caso de uso: Importar repo GitHub a REP y enlazar a PTN (INX)

### Objetivo

Importar/actualizar un repositorio desde GitHub al catálogo REP (Notion) y enlazarlo a un proyecto PTN, con trazabilidad en `INX-ENLACES`.

### Actores

- **Usuario**: David
- **Sistema(s)**: GitHub, Notion (REP + PTN + INX)

### Trigger

Se crea o se detecta un repo relevante para un proyecto activo (o se quiere catalogar backlog).

### Precondiciones

- `.env` con `GITHUB_TOKEN`.
- Notion REP operativo (`NOTION_DB_REPOS`, `NOTION_REPOS_PARENT_PAGE` si aplica).
- PTN operativo (para poder relacionar con proyecto).

### Fuente de verdad (autoridad)

- **Metadata técnica**: GitHub (lenguajes, topics, última actividad)
- **Catálogo/táctica**: Notion (REP)
- **Trazabilidad**: `INX-ENLACES`

### Flujo principal (happy path)

1. Importar/sincronizar repos (según flujo REP).
2. Catalogar el repo (tipo/estado/proceso/etiquetas).
3. Seleccionar el proyecto PTN al que pertenece.
4. Crear/actualizar la fila INX con:
   - `Clave=github:<owner>/<repo>`
   - relación a PTN Proyecto
   - URL del repo

### Automatización actual

- REP (según docs):
  - `python agents/github_agent.py importar`
  - `python agents/github_agent.py sincronizar`
  - `python agents/github_agent.py catalogar <repo> --tipo X --proceso Y`

### Postcondiciones / Resultado verificable

- En REP existe la fila del repo con propiedades correctas.
- En `INX-ENLACES` existe `Clave=github:<owner>/<repo>` con `URL` y relación a `PTN Proyecto`.

### Gaps (lo que falta hoy)

- No hay sync automático de “enlaces INX” para REP (no existe todavía un `sync_inx_links --source github`).
- No hay convención cerrada de `Clave` para repos (owner/repo vs URL completa).

### Mejoras propuestas (acciones)

- Extender `tools/sync_inx_links.py` con `--source github` que lea REP y upsertee INX.
- Añadir un comando “link-repo-to-ptn” que:
  - cree/actualice INX `github:<owner>/<repo>`
  - rellene relación PTN Proyecto y `Area/Bloque/Contexto` si procede.

