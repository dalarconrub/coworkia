# Agente BIB — Paperpile → Notion

Cataloga papers académicos de Paperpile en una base de datos de Notion.
Lee la biblioteca via Automatic BibTeX Export (no requiere API oficial).

## Arquitectura

```
Paperpile ──→ URL BibTeX ──→ tools/paperpile_tools.py ──→ agents/bib_agent.py ──→ Notion
                                                               │
                                                     apps/bib_gui.py (GUI)
```

| Archivo | Propósito |
|---------|-----------|
| `tools/paperpile_tools.py` | Descarga y parsea BibTeX, normaliza entradas |
| `agents/bib_agent.py` | Agente BIB: importar, sincronizar, catalogar, listar |
| `apps/bib_gui.py` | Interfaz gráfica (tkinter) |

## Requisitos

### Dependencia Python

```bash
pip install bibtexparser
```

### Variables en `.env`

```
PAPERPILE_BIBTEX_URL=https://paperpile.com/eb/...   # URL de exportación automática
NOTION_BIB_PARENT_PAGE=xxx                           # ID de la página padre en Notion
NOTION_DB_BIB=                                        # Se llena tras ejecutar crear-db
```

### Cómo obtener `PAPERPILE_BIBTEX_URL`

1. Abre Paperpile → **Settings** → **Workflows & Integrations**
2. En **Automatic BibTeX Export**, activa para **toda la biblioteca** (o carpetas específicas)
3. Copia la **URL de descarga** (empieza con `https://paperpile.com/eb/...`)
4. Pega la URL en `.env` como `PAPERPILE_BIBTEX_URL`

### Cómo obtener `NOTION_BIB_PARENT_PAGE`

1. Crea una página en Notion donde vivirá la tabla de papers
2. Comparte la página con tu integración de Notion (... → Conexiones)
3. Copia el ID de la URL (últimos 32 caracteres, con guiones)

## Comandos CLI

### Setup inicial (una vez)

```bash
python agents/bib_agent.py crear-db
# Copia el ID que devuelve a NOTION_DB_BIB en .env
```

### Importar papers

```bash
python agents/bib_agent.py importar
```

Descarga la biblioteca de Paperpile y crea entradas en Notion. Detecta duplicados por citekey.

### Sincronizar

```bash
python agents/bib_agent.py sincronizar
```

Importa papers nuevos + actualiza metadata de los existentes (título, autores, keywords, DOI).
No sobreescribe campos de catalogación manual (estado, relevancia, notas).

### Catalogar un paper

```bash
python agents/bib_agent.py catalogar einstein2005 \
  --estado "Leído" \
  --relevancia Alta \
  --etiquetas "meta-análisis" "cognitivo" \
  --notas "Revisar metodología del estudio 3"
```

Busca por citekey exacto o por texto parcial en el título.

### Listar papers

```bash
python agents/bib_agent.py listar
python agents/bib_agent.py listar --estado "Por leer" --tipo Artículo
python agents/bib_agent.py listar --carpeta "My Research"
python agents/bib_agent.py listar --relevancia Alta
```

### Estado general

```bash
python agents/bib_agent.py estado
```

## Interfaz gráfica (GUI)

```bash
python apps/bib_gui.py
```

Tres pestañas:

### Explorar
- Tabla con todos los papers: título, autores, año, tipo, journal, estado, relevancia, carpeta
- Filtros por búsqueda de texto (busca en título, autores, journal, keywords, citekey)
- Filtros por tipo, estado y carpeta de Paperpile
- Ordenación por cualquier columna (click en encabezado, año se ordena numéricamente)
- Doble click abre el DOI en el navegador

### Catalogar
- Selecciona un paper en Explorar
- Edita estado de lectura, relevancia, etiquetas y notas
- Guarda cambios directo a Notion

### Acciones
- **Importar papers nuevos**: trae papers de Paperpile que no están en Notion
- **Sincronizar**: importa nuevos + actualiza metadata de existentes
- **Recargar tabla**: vuelve a leer desde Notion
- Log de salida en tiempo real

## Propiedades de la base de datos

| Propiedad | Tipo | Auto | Descripción |
|-----------|------|------|-------------|
| Título | title | ✓ | Título del paper |
| Autores | rich_text | ✓ | Lista de autores (Nombre Apellido, ...) |
| Año | number | ✓ | Año de publicación |
| Tipo | select | ✓ | Artículo / Libro / Conferencia / Tesis / etc. |
| Journal | rich_text | ✓ | Nombre de la revista o conferencia |
| DOI | url | ✓ | Enlace DOI |
| Abstract | rich_text | ✓ | Resumen del paper |
| Keywords | multi_select | ✓ | Palabras clave del paper |
| Carpeta | select | ✓ | Carpeta de Paperpile |
| Etiquetas | multi_select | ✓ | Labels de Paperpile + manuales |
| Estado | select | — | Por leer / En proceso / Leído / Revisado / Descartado |
| Relevancia | select | — | Alta / Media / Baja |
| Citekey | rich_text | ✓ | Identificador BibTeX (ej: einstein2005) |
| URL | url | ✓ | URL del paper o DOI |
| Volumen | rich_text | ✓ | Volumen(número) |
| Páginas | rich_text | ✓ | Rango de páginas |
| PMID | rich_text | ✓ | PubMed ID |
| Notas | rich_text | ✓* | Notas de Paperpile al importar, editables manualmente |

*Auto = se rellena automáticamente al importar desde BibTeX.

## Datos que se importan de BibTeX

El parser normaliza estos campos de cada entrada BibTeX:

- `title`, `author`, `year`, `journal`/`booktitle`
- `doi`, `url`, `abstract`, `keywords`
- `volume`, `number`, `pages`, `publisher`
- `pmid`, `eprint` (arXiv), `isbn`, `issn`
- `paperpile-folder`, `paperpile-labels` (campos propios de Paperpile)
- `note`, `annote`
- `ENTRYTYPE` → tipo normalizado (article → Artículo, book → Libro, etc.)

## Flujo recomendado

1. **Setup**: activar BibTeX export en Paperpile → copiar URL a `.env`
2. **Setup**: `crear-db` → copiar ID a `.env`
3. **Importar**: `importar` → trae todos los papers
4. **Explorar**: `python apps/bib_gui.py` → revisar y catalogar
5. **Mantener**: `sincronizar` periódicamente (o tras añadir papers en Paperpile)
