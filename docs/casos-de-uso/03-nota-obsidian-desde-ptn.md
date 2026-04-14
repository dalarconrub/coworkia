## Caso de uso: Crear nota Obsidian desde PTN y dejarla enlazada (INX)

### Objetivo

Crear una nota (documento) en Obsidian asociada a un proyecto/tarea PTN y dejar la trazabilidad lista para navegar desde Notion y desde Obsidian.

### Actores

- **Usuario**: David
- **Sistema(s)**: Notion (PTN + INX), Obsidian (documento), Notion (OBSIDIAN_DB + sync)

### Trigger

Un proyecto/tarea requiere pensamiento extendido, documentación o registro (decisiones, investigación, borradores).

### Precondiciones

- Vault ABGD accesible (`OBSIDIAN_ABGD_ROOT`, `OBSIDIAN_ALPHA_PATH`).
- DB `OBSIDIAN_DB` en Notion configurada.

### Fuente de verdad (autoridad)

- **Documento**: Obsidian (ruta y contenido)
- **Relación documento↔proyecto**: Notion (PTN) + `INX-ENLACES`

### Flujo principal (happy path)

1. En PTN (Notion), seleccionar el proyecto/tarea objetivo.
2. Crear nota en Obsidian bajo la ruta ABC correspondiente.
3. Registrar el cambio en `OBSIDIAN_DB` (log).
4. Sincronizar `INX-ENLACES` desde Obsidian para que exista `Clave=obsidian:<ruta_relativa>`.
5. Relacionar esa fila INX con el proyecto/tarea PTN.

### Postcondiciones / Resultado verificable

- Existe un archivo `.md` en Obsidian con ruta relativa estable.
- En Notion `OBSIDIAN_DB` aparece una entrada (si el log corrió).
- En `INX-ENLACES` existe:
  - `Clave=obsidian:<ruta>`
  - `Obsidian Ruta=<ruta>`
  - relaciones ABC (si se detectan) y relación PTN (si se completó).

### Automatización actual

- Registrar cambios Obsidian → Notion:

```bash
.\.venv\Scripts\python.exe tools/log_obsidian_changes.py
```

- Upsert INX desde Obsidian:

```bash
.\.venv\Scripts\python.exe tools/sync_inx_links.py --source obsidian --limit 200
```

- Cadena INX completa:

```bash
.\.venv\Scripts\python.exe agents/orchestrator_agent.py inx-sync --limit 200
```

### Observabilidad

- Revisar `artifacts/obsidian_log_state.json` para confirmar que el detector “avanza”.
- Revisar `INX-ENLACES` por `Clave` prefijo `obsidian:`.

### Gaps (lo que falta hoy)

- No hay un enlace “clickable” de vuelta a Obsidian (depende de si se quiere usar `obsidian://` o enlaces de sistema).
- Falta automatizar la creación de la relación PTN↔Obsidian (hoy es manual).

### Mejoras propuestas (acciones)

- Añadir propiedad `URL` en INX para `obsidian://open?...` (si se decide estándar).
- Comando “link-obsidian-to-ptn” que:
  - detecte/cree la fila `obsidian:<ruta>` en INX
  - la relacione con `PTN Proyecto`/`PTN Tarea`

