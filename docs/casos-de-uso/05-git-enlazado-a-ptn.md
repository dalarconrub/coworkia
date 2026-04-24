## Caso de uso: Importar repo GitHub a GIT y enlazar a PTN (INX)

### Objetivo

Importar/actualizar un repositorio desde GitHub al catálogo GIT (Notion) y enlazarlo a un proyecto PTN, con trazabilidad en `INX-ENLACES`.

### Actores

- **Usuario**: David
- **Sistema(s)**: GitHub, Notion (GIT + PTN + INX)

### Trigger

Se crea o se detecta un repo relevante para un proyecto activo (o se quiere catalogar backlog).

### Precondiciones

- `.env` con `GITHUB_TOKEN`.
- Notion GIT operativo (`NOTION_DB_GIT`, `NOTION_GIT_PARENT_PAGE` si aplica).
- PTN operativo (para poder relacionar con proyecto).

### Fuente de verdad (autoridad)

- **Metadata técnica**: GitHub (lenguajes, topics, última actividad)
- **Catálogo/táctica**: Notion (GIT)
- **Trazabilidad**: `INX-ENLACES`

### Flujo principal (happy path)

1. Importar/sincronizar repos (según flujo GIT).
2. Catalogar el repo (tipo/estado/proceso/etiquetas).
3. Seleccionar el proyecto PTN al que pertenece.
4. Crear/actualizar la fila INX con:
   - `Clave=github:<Nombre>`
   - relación a PTN Proyecto
   - URL del repo

### Automatización actual

- GIT (según docs):
  - `python agents/github_agent.py importar`
  - `python agents/github_agent.py sincronizar`
  - `python agents/github_agent.py catalogar <repo> --tipo X --proceso Y`
- INX:
  - `python tools/sync_inx_links.py --source github --limit 200`
  - helper interno disponible: `link_repo_to_ptn(repo_nombre, proyecto_ref)` en `tools/sync_inx_links.py`

### Postcondiciones / Resultado verificable

- En GIT existe la fila del repo con propiedades correctas.
- En `INX-ENLACES` existe `Clave=github:<Nombre>` con `URL` y, si se ha enlazado, relación a `PTN Proyecto`.

### Estado actual

- `sync_inx_links.py --source github` ya existe y upsertea INX desde GIT.
- La convención real actual de clave es `github:<Nombre>`; no `github:<owner>/<repo>`.
- Existe helper `link_repo_to_ptn(...)` para crear/actualizar la relación `PTN Proyecto` desde código.

Validación técnica realizada el `2026-04-17`:

- GIT total: `113` repos
- Filas `github:*` en `INX-ENLACES`: `113`
- Repos huérfanos GIT→INX: `0`
- Filas `github:*` con `PTN Proyecto`: `1`
- Ejemplo real enlazado:
  - `github:coworkia`

Ejemplos reales detectados en INX:

- `github:starter-hugo-academic`
- `github:resumenet`
- `github:resumennet`
- `github:analitica-foros-master`
- `github:seel`

### Mejoras propuestas (acciones)

- Exponer `link_repo_to_ptn(...)` como CLI o `.bat` para no depender de invocación manual desde Python.
- Evaluar si conviene migrar la convención de `Clave` a `github:<owner>/<repo>` para reducir ambigüedad entre forks/nombres repetidos.
- Si se mantiene `github:<Nombre>`, documentarlo también en `00-template.md` para no seguir propagando la clave obsoleta.

