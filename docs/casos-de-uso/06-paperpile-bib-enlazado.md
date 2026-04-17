## Caso de uso: Importar paper Paperpile a BIB y enlazar a PTN/Obsidian (INX)

### Objetivo

Importar un paper desde Paperpile al catálogo BIB (Notion), y enlazarlo a un proyecto PTN y/o una nota Obsidian, dejando trazabilidad en `INX-ENLACES`.

### Actores

- **Usuario**: David
- **Sistema(s)**: Paperpile, Notion (BIB + PTN + INX), Obsidian (opcional)

### Trigger

Se añade un paper a Paperpile o se decide incorporar un paper a un proyecto activo.

### Precondiciones

- `.env` con:
  - `PAPERPILE_BIBTEX_URL`
  - `NOTION_DB_BIB`, `NOTION_BIB_PARENT_PAGE` (si aplica)
- PTN operativo (si se enlaza a proyecto/tarea).

### Fuente de verdad (autoridad)

- **Metadata bibliográfica**: Paperpile (vía BibTeX export)
- **Catálogo y estado de lectura**: Notion (BIB)
- **Trazabilidad**: `INX-ENLACES`

### Flujo principal (happy path)

1. Importar/sincronizar papers a BIB (Notion).
2. Seleccionar paper objetivo (citekey/DOI).
3. Seleccionar proyecto PTN (y/o nota Obsidian).
4. Crear/actualizar INX:
   - `Clave=paperpile:<citekey>`
   - `URL` (DOI o Paperpile si procede)
   - relación a PTN y opcionalmente a `obsidian:<ruta>`

### Automatización actual

- BIB (según docs):
  - `python agents/bib_agent.py importar`
  - `python agents/bib_agent.py sincronizar`
  - `python agents/bib_agent.py catalogar <citekey> --estado Leído --relevancia Alta`
- INX:
  - `python tools/sync_inx_links.py --source paperpile --limit 200`
  - helper interno disponible: `link_paper_to_ptn(citekey, proyecto_ref)` en `tools/sync_inx_links.py`

### Postcondiciones / Resultado verificable

- BIB contiene el paper con propiedades mínimas (título, autores, año, DOI si existe).
- `INX-ENLACES` contiene `Clave=paperpile:<citekey>` con enlaces y relaciones.

### Estado actual

- `sync_inx_links.py --source paperpile` ya existe y upsertea INX desde BIB.
- La convención real actual de clave es `paperpile:<citekey>`.
- Existe helper `link_paper_to_ptn(...)` para crear/actualizar la relación `PTN Proyecto` desde código.

Validación técnica realizada el `2026-04-17`:

- Filas totales en `BIB`: `0`
- Filas `paperpile:*` en `INX-ENLACES`: `0`
- Filas `paperpile:*` con `PTN Proyecto`: `0`
- Huérfanos BIB→INX: `0`

Lectura operativa:

- El caso no es validable hoy con datos reales porque `BIB` está vacío.
- No hay evidencia de rotura en la cadena Paperpile→BIB→INX; simplemente no hay papers cargados todavía en el catálogo.

### Mejoras propuestas (acciones)

- Cargar al menos un paper real en `BIB` para poder validar end-to-end el caso con evidencia.
- Exponer `link_paper_to_ptn(...)` como CLI o `.bat` para no depender de invocación manual desde Python.
- Evaluar si conviene añadir dedupe por DOI/citekey una vez exista volumen real en `BIB`.

