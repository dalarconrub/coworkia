# Obsidian Agent — Guía de uso

Agente para el vault **ABGD** en Obsidian.

**Vault activo:** definido por `.env` en `OBSIDIAN_ABGD_ROOT`.

Política vigente desde 2026-05-09: el vault primario debe estar en disco local del PC. Google Drive, otros servicios de nube y discos externos se usan como réplicas/backups sincronizados, no como ruta operativa principal.

Ruta operativa actual en `.env`:

```text
OBSIDIAN_ABGD_ROOT=C:/Users/David/Documents/ABGDE/ABGDE-2026-05-15
OBSIDIAN_ALPHA_PATH=C:/Users/David/Documents/ABGDE/ABGDE-2026-05-15/1.ALPHA
```

Convención canónica vigente desde 2026-05-15:

```text
OBSIDIAN_ABGD_ROOT=C:/Users/David/Documents/ABGDE/ABGDE-YYYY-MM-DD
OBSIDIAN_ALPHA_PATH=C:/Users/David/Documents/ABGDE/ABGDE-YYYY-MM-DD/1.ALPHA
```

Convención vigente: Obsidian Desktop abre `OBSIDIAN_ABGD_ROOT` (el vault real). Las herramientas de Coworkia que operan sobre conocimiento vivo usan `OBSIDIAN_ALPHA_PATH`, que apunta a la subcarpeta `1.ALPHA`.

Si se rota el vault con `tools/reset_obsidian.py rotate`, estas rutas deben actualizarse en `.env`; la guía no debe apuntar a rutas históricas como fuente de verdad.
La rotación crea automáticamente la estructura mínima de `2.BETA`, `3.GAMMA`,
`4.DELTA` y `5.EPSILON`, además de las notas índice de carpetas.

Ruta local propuesta para la siguiente rotación/migración:

```text
C:/Users/David/Documents/ABGDE/ABGDE-YYYY-MM-DD
```

---

## Capas internas del vault

```text
ABGDE-YYYY-MM-DD/
├── .obsidian/
├── 1.ALPHA/
├── 2.BETA/
├── 3.GAMMA/
├── 4.DELTA/
└── 5.EPSILON/
```

| Carpeta | Rol | Jerarquía | Regla operativa |
| --- | --- | --- | --- |
| `1.ALPHA` | Notas Obsidian vivas | ABC canónica (`A/B/C/...`) | Solo Markdown y adjuntos ligeros imprescindibles: notas, MOCs, decisiones, journals, fichas, notas puente y enlaces. Coworkia la indexa por defecto. |
| `2.BETA` | Histórico de proyectos | AB (`A/B/Proyecto`) | Proyectos finalizados o en hibernación. Conserva material operativo recuperable sin exigir el nivel C. |
| `3.GAMMA` | Proyectos activos | A (`A/Proyecto`) | Carpetas materiales de proyectos vivos: código, datos, escritura, outputs y documentación de trabajo. |
| `4.DELTA` | Referencias no-proyecto por fecha | Temporal (`AÑO/YYYY-MM-DD/`) | Documentos, capturas, datasets o carpetas de referencia incorporadas al sistema por fecha, antes o al margen de un proyecto. |
| `5.EPSILON` | Biblioteca por tipo de fichero | Tipo de archivo | Biblioteca estable con raíz por formato (`PDF`, `EPUB`, `VIDEO`, `AUDIO`, `MUSICA`, etc.) y subcolecciones progresivas. |

Regla: las integraciones automáticas de Coworkia operan sobre `1.ALPHA` salvo que un flujo especifique explícitamente otra capa. `ALPHA` no es "todo lo importante": es solo la capa cognitiva en Markdown; los archivos pesados, datasets, repos, backups y productos materiales no deben vivir ahí.

### Reglas de clasificación por capa

| Si es... | Va a... |
| --- | --- |
| Nota, mapa, decisión, diario, ficha de lectura o nota puente | `1.ALPHA` |
| Proyecto cerrado, finalizado o hibernado con posible reactivación | `2.BETA` |
| Proyecto activo con código, datos, escritura, outputs o documentación operativa | `3.GAMMA` |
| Documento/carpeta de referencia no asignada como proyecto, conservada por fecha de entrada | `4.DELTA/AÑO/YYYY-MM-DD/` |
| PDF, EPUB, vídeo, audio, música u otro archivo estable organizado por formato | `5.EPSILON/<TIPO>/` |

`DELTA` conserva cuándo entró una referencia; `EPSILON` conserva qué tipo de objeto es. La interpretación de ambos vive en notas de `ALPHA`.

## Jerarquía ABGD

```
Área (A) → Bloque (B) → Contexto (C) → Proyecto (P) → Tarea (T) → Nota (N)
```

Esta jerarquía completa se exige solo en `1.ALPHA`. Las demás capas reducen la profundidad según su función: `BETA` usa AB, `GAMMA` usa A, `DELTA` usa tiempo y `EPSILON` usa tipo de fichero.

### Áreas

| Código | Nombre |
|--------|--------|
| A0-GTD | Getting Things Done |
| A1-INV | Investigación |
| A2-UNI | Universidad |
| A3-VIT | Vital |
| A4-ARX | Archivo |

### Nomenclatura de archivos

| Nivel | Formato | Ejemplo |
|-------|---------|---------|
| Nota | `N[YYMMDD]-Descripción.md` | `N260316-Reunión con Enrique.md` |
| Tarea | `T[BXXX.NN]-Nombre/` | `T12601.03-Datos Estudio 3/` |
| Proyecto | `P[BXXX.NN]-Nombre/` | `P126.01-Tesis Fran/` |

---

## Comandos

### Explorar estructura

```bash
# Mapa completo del vault (Área → Bloque → Contexto)
python agents/obsidian_agent.py mapa

# Estadísticas del vault
python agents/obsidian_agent.py estado

# Listar contenido de cualquier nivel por código
python agents/obsidian_agent.py listar A1-INV        # bloques de Investigación
python agents/obsidian_agent.py listar B12-LAB        # contextos de Laboratorio
python agents/obsidian_agent.py listar C125-DAT       # proyectos de Datos
python agents/obsidian_agent.py listar C126-DIR       # proyectos de Dirección tesis
```

### Notas

```bash
# Últimas N notas del vault
python agents/obsidian_agent.py ultimas
python agents/obsidian_agent.py ultimas --n 20
python agents/obsidian_agent.py ultimas --n 5 --area A1-INV

# Ver contenido de una nota (por nombre o path)
python agents/obsidian_agent.py ver "N260316-Reunión con Enrique"
python agents/obsidian_agent.py ver "C:/Users/David/Documents/ABGDE/ABGDE-YYYY-MM-DD/1.ALPHA/.../nota.md"

# Buscar texto en las notas
python agents/obsidian_agent.py buscar "análisis GLM"
python agents/obsidian_agent.py buscar "Tesis Fran" --area A1-INV
```

### Crear notas

```bash
# Nota en un contexto (nivel más común)
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C125-DAT "Resultados preliminares"

# Con contenido y fecha
python agents/obsidian_agent.py nueva-nota A1-INV B13-PUB C137-ART "Revisión Paper Human Communication" \
  --contenido "## Puntos clave\n- ..." \
  --fecha 2026-03-16

# En un proyecto específico
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C126-DIR "Sesión de trabajo" \
  --proyecto "P126.01-Tesis Fran" \
  --fecha 2026-03-16

# En una tarea específica
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C126-DIR "Análisis datos" \
  --proyecto "P126.01-Tesis Fran" \
  --tarea "T12601.03-Datos Estudio 3"
```

### Crear estructura mínima y notas índice de carpetas

Cada carpeta estructural ABGD-E puede tener una nota con su mismo nombre. Estas
notas explican qué es la carpeta, cómo se organiza y qué regla de uso aplica.

```bash
# Crea estructura mínima de BETA/GAMMA/DELTA/EPSILON y notas faltantes
python tools/create_alpha_index_notes.py

# Regenera las notas índice con la plantilla vigente
python tools/create_alpha_index_notes.py --refresh-existing

# Solo refresca notas, sin tocar subcarpetas
python tools/create_alpha_index_notes.py --refresh-existing --skip-structure
```

Este comando también se ejecuta automáticamente dentro de:

```bash
python tools/reset_obsidian.py rotate
```

Solo se omite si se pasa explícitamente `--no-abgde-index`.

Alcance actual del comando:

- raíz del vault (`ABGDE-YYYY-MM-DD.md`);
- capas `1.ALPHA` a `5.EPSILON`;
- áreas, bloques y contextos de `1.ALPHA`.
- áreas y bloques de `2.BETA`;
- áreas de `3.GAMMA`;
- año y fecha actual de `4.DELTA`;
- tipos de fichero y bandejas `SIN-CLASIFICAR` de `5.EPSILON`.

Nota: `obsidian_agent.py estado` cuenta solo notas operativas con prefijo
`NYYMMDD-*`; las notas índice de carpeta se crean con el mismo nombre de la
carpeta y por eso no incrementan ese contador.

---

## Properties sincronizadas

Las notas pueden declarar metadata en frontmatter YAML. Coworkia sincroniza estas
properties hacia `OBSIDIAN_DB` y, con nombres prefijados, hacia `INX-ENLACES`:

```yaml
---
tipo: nota
estado: activa
proyecto: JA-Linea-1-2026
tarea: revisar-literatura
tags:
  - lectura
  - paper
personas:
  - David
fuente: Paperpile
aliases:
  - Nombre alternativo
---
```

Mapeo:

| Frontmatter | `OBSIDIAN_DB` | `INX-ENLACES` |
| --- | --- | --- |
| `tipo` / `type` | `Tipo` | `Nota Tipo` |
| `estado` / `status` | `Estado` | `Nota Estado` |
| `tags` | `Tags` | `Nota Tags` |
| `personas` / `people` | `Personas` | `Nota Personas` |
| `fuente` / `source` | `Fuente` | `Nota Fuente` |
| `proyecto` / `project` | `Proyecto` | `Nota Proyecto` |
| `tarea` / `task` | `Tarea` | `Nota Tarea` |
| `aliases` / `alias` | `Alias` | `Nota Alias` |

Además, Coworkia deriva estructura ABPC desde la ruta relativa de la nota:

```text
A1-INV/B13-PUB/C137-ART/P137.01-LMS/T13701.03-Revision/N260510-nota.md
```

| Ruta | `OBSIDIAN_DB` | `INX-ENLACES` |
| --- | --- | --- |
| `A...` | `Ruta Area` | `Obsidian Area` |
| `B...` | `Ruta Bloque` | `Obsidian Bloque` |
| `C...` | `Ruta Contexto` | `Obsidian Contexto` |
| `P...` | `Ruta Proyecto` | `Obsidian Proyecto` |
| `T...` | `Ruta Tarea` | `Obsidian Tarea` |
| `N...md` | `Ruta Nota` | `Obsidian Nota` |
| nivel inferido | `Ruta Nivel` | `Obsidian Nivel` |

Bootstrap de schema:

```bash
python tools/ensure_obsidian_note_metadata_fields.py
```

Después, el pipeline normal `log_obsidian_changes.py` +
`sync_inx_links.py --source obsidian` propaga esas properties.

---

## Estructura real del vault

```
1.ALPHA/
├── A0-GTD/
│   ├── B0A-INX/
│   │   ├── C0A1-TODOIST/
│   │   ├── C0A2-NOTION/
│   │   └── C0A3-OBSIDIAN/
│   ├── B0B-ABC/
│   │   └── C0B0-ABC/
│   └── B0C-PLA/
│       ├── C0C7-PROYECTOS/
│       ├── C0C8-TAREAS/
│       └── C0C9-NOTAS/
├── A1-INV/
│   ├── B11-CVT/  (C111-REP, C112-SOL, C113-CAT)
│   ├── B12-LAB/  (C124-PRO, C125-DAT, C126-DIR)
│   └── B13-PUB/  (C137-ART, C138-COM, C139-REV)
├── A2-UNI/
│   ├── B24-DOC/  (C241-GRA, C242-MAS, C243-POS)
│   ├── B25-FOR/  (C254-EST, C255-PDI, C256-MOC)
│   └── B26-GES/  (C267-UPO, C268-UNED, C269-MIN)
├── A3-VIT/
│   ├── B37-ORG/  (C371-ADM, C372-PER, C373-SOC)
│   ├── B38-TEC/  (C384-INF, C385-STA, C386-IAA)
│   └── B39-DES/  (C397-FIS, C398-MEN, C399-MUS)
└── A4-ARX/
    ├── B4X-LIB/  (C4X0-LIB, C4X1-FIC, C4X2-SCI, C4X3-ENS)
    ├── B4Y-MED/  (C4Y0-MED, C4Y4-VID, C4Y5-AUD, C4Y6-WEB)
    └── B4Z-APP/  (C4Z0-APP, C4Z7-COD, C4Z8-AGI, C4Z9-SOF)
```

---

## Estructura operativa esperada de las capas no-ALPHA

```text
2.BETA/
├── A0-GTD/  (B0A-INX, B0B-ABC, B0C-PLA)
├── A1-INV/  (B11-CVT, B12-LAB, B13-PUB)
├── A2-UNI/  (B24-DOC, B25-FOR, B26-GES)
├── A3-VIT/  (B37-ORG, B38-TEC, B39-DES)
└── A4-ARX/  (B4X-LIB, B4Y-MED, B4Z-APP)

3.GAMMA/
├── A0-GTD/
├── A1-INV/
├── A2-UNI/
├── A3-VIT/
└── A4-ARX/

4.DELTA/
└── 2026/
    └── 2026-05-15/
        ├── papers-lms/
        └── docs-openai-api/

5.EPSILON/
├── PDF/
├── EPUB/
├── VIDEO/
├── AUDIO/
├── MUSICA/
├── IMAGENES/
├── PRESENTACIONES/
├── DOCS/
├── HOJAS-CALCULO/
├── ZIP/
└── OTROS/
```

En EPSILON cada tipo incluye una bandeja `SIN-CLASIFICAR/` para incorporar
material sin diseñar todavía una colección estable. En BETA y GAMMA no se crean
proyectos vacíos: se crean solo los contenedores necesarios para evitar ruido.

Las notas de `ALPHA` pueden referenciar cualquier carpeta material con rutas relativas al vault:

```yaml
---
tipo: mapa-proyecto
estado: activo
gamma_path: 3.GAMMA/A1-INV/P260515-LMS
delta_path: 4.DELTA/2026/2026-05-15/papers-lms
epsilon_path: 5.EPSILON/PDF/papers/lms
---
```

Y en el cuerpo:

```md
- Carpeta activa: `3.GAMMA/A1-INV/P260515-LMS/`
- Referencias incorporadas: `4.DELTA/2026/2026-05-15/papers-lms/`
- Biblioteca estable: `5.EPSILON/PDF/papers/lms/`
- PTN: [[ptn:...]]
- BIB: [[paperpile:...]]
- KIT: [[kit:...]]
- Repo: [[github:...]]
```

---

## Configuración

- Vault Obsidian real en `.env` → `OBSIDIAN_ABGD_ROOT`
- Carpeta viva de notas ABPC en `.env` → `OBSIDIAN_ALPHA_PATH` (`1.ALPHA`, solo notas Markdown)
- Ruta primaria recomendada: local (`C:/Users/David/Documents/ABGD/...` o equivalente).
