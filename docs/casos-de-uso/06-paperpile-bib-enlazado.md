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
   - `Clave=bib:<citekey>` (o `bib:<doi>` si se decide)
   - `URL` (DOI o Paperpile si procede)
   - relación a PTN y opcionalmente a `obsidian:<ruta>`

### Automatización actual

- BIB (según docs):
  - `python agents/bib_agent.py importar`
  - `python agents/bib_agent.py sincronizar`
  - `python agents/bib_agent.py catalogar <citekey> --estado Leído --relevancia Alta`

### Postcondiciones / Resultado verificable

- BIB contiene el paper con propiedades mínimas (título, autores, año, DOI si existe).
- `INX-ENLACES` contiene `Clave=bib:<citekey>` con enlaces y relaciones.

### Gaps (lo que falta hoy)

- No existe todavía `sync_inx_links --source bib` (BIB→INX).
- Falta estandarizar la `Clave` bibliográfica (citekey vs DOI) y resolver duplicados.

### Mejoras propuestas (acciones)

- Extender `tools/sync_inx_links.py` con `--source bib` que lea BIB y upsertee INX.
- Añadir un “dedupe” por DOI/citekey.
- Añadir un comando “link-paper-to-ptn” que conecte BIB↔PTN↔Obsidian vía INX.

