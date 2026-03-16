# Nueva Estructura de Delta - Organización por Formato de Archivo

**Fecha de Cambio:** 04 de febrero de 2026
**Modificación:** Organización por formato/extensión de archivo

---

## ¿Qué Cambió en Delta?

### Estructura Anterior ❌

```
Delta/
├── DOC/
│   ├── Académico/           ← Organización temática
│   ├── Personal/
│   ├── Profesional/
│   └── Referencia/
├── LIB/
│   ├── Ficción/
│   ├── No-ficción/
│   ├── Técnico/
│   └── Académico/
├── MED/
│   ├── Audio/
│   ├── Video/
│   ├── Imágenes/
│   └── Presentaciones/
└── SOF/
    ├── Instaladores/
    ├── Portable/
    ├── Scripts/
    └── Configuraciones/
```

**Problema:** Mezcla organización temática con tipos de contenido

### Estructura Nueva ✅

```
Delta/
├── DOC/                     ← Documentos ofimáticos
│   ├── WORD/    (.doc, .docx)
│   ├── PPT/     (.ppt, .pptx)
│   ├── EXC/     (.xls, .xlsx)
│   └── TEX/     (.tex)
│
├── LIB/                     ← Libros y lecturas
│   ├── EPUB/    (.epub)
│   └── PDF/     (.pdf)
│
├── MED/                     ← Multimedia
│   ├── MP3/     (.mp3, .wav, .flac, .m4a)
│   ├── AVI/     (.avi, .mp4, .mkv, .mov)
│   └── PNG/     (.png, .jpg, .jpeg, .gif, .svg)
│
└── SOF/                     ← Software
    ├── ZIP/     (.zip, .rar, .7z, .tar.gz)
    └── EXE/     (.exe, .msi, .app, .dmg)
```

**Ventaja:** Organización clara por formato/extensión

---

## Ventajas del Nuevo Sistema

### 1. Simplicidad
**Antes:** "¿Este paper es Académico o Referencia?"
**Ahora:** "Es un PDF → va en LIB/PDF/"

### 2. Velocidad
Sabes inmediatamente dónde está cada archivo según su extensión:
- `.docx` → DOC/WORD/
- `.pdf` → LIB/PDF/
- `.mp3` → MED/MP3/
- `.zip` → SOF/ZIP/

### 3. Sin Ambigüedades
No necesitas decidir categorías temáticas, el formato del archivo lo dice todo.

### 4. Escalable
Fácil añadir nuevos formatos:
```bash
mkdir Delta/DOC/ODT    # Para archivos OpenDocument
mkdir Delta/MED/FLAC   # Para audio sin pérdida
```

---

## Estructura Detallada

### DOC - Documentos Ofimáticos

**Propósito:** Documentos de oficina y texto

| Carpeta | Nombre | Extensiones | Uso |
|---------|--------|-------------|-----|
| WORD | Microsoft Word | `.doc`, `.docx` | Documentos de texto |
| PPT | PowerPoint | `.ppt`, `.pptx` | Presentaciones |
| EXC | Excel | `.xls`, `.xlsx` | Hojas de cálculo |
| TEX | LaTeX | `.tex` | Documentos LaTeX |

**Ejemplo:**
```
DOC/
├── WORD/
│   ├── Proyecto_Tesis.docx
│   ├── CV_2026.docx
│   └── Academico/
│       └── Paper_Revision.docx
├── PPT/
│   └── Presentacion_Congreso_2026.pptx
├── EXC/
│   └── Datos_Experimento.xlsx
└── TEX/
    └── Articulo_Journal.tex
```

---

### LIB - Libros y Lecturas

**Propósito:** Libros digitales y documentos de lectura

| Carpeta | Nombre | Extensiones | Uso |
|---------|--------|-------------|-----|
| EPUB | EPUB | `.epub` | Libros electrónicos |
| PDF | PDF | `.pdf` | Documentos PDF |

**Ejemplo:**
```
LIB/
├── EPUB/
│   ├── Ficcion/
│   │   └── 1984_Orwell.epub
│   └── Tecnico/
│       └── Python_Cookbook.epub
└── PDF/
    ├── Papers/
    │   ├── Machine_Learning_Review.pdf
    │   └── Statistical_Methods.pdf
    └── Manuales/
        └── Git_Manual.pdf
```

**Nota:** Aunque PDF está en LIB, si es un documento de trabajo (no lectura), podría ir en DOC/. Usa tu criterio.

---

### MED - Contenido Multimedia

**Propósito:** Archivos de audio, video e imagen

| Carpeta | Nombre | Extensiones | Uso |
|---------|--------|-------------|-----|
| MP3 | Audio | `.mp3`, `.wav`, `.flac`, `.m4a` | Archivos de audio |
| AVI | Video | `.avi`, `.mp4`, `.mkv`, `.mov` | Archivos de video |
| PNG | Imágenes | `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg` | Imágenes |

**Ejemplo:**
```
MED/
├── MP3/
│   ├── Musica/
│   │   └── album_favorito/
│   └── Podcasts/
│       └── episodio_01.mp3
├── AVI/
│   ├── Tutoriales/
│   │   └── Python_Tutorial.mp4
│   └── Conferencias/
│       └── Keynote_2026.mp4
└── PNG/
    ├── Fotos/
    │   └── evento_2026.jpg
    └── Diagramas/
        └── arquitectura_sistema.png
```

---

### SOF - Software y Ejecutables

**Propósito:** Software, instaladores y archivos comprimidos

| Carpeta | Nombre | Extensiones | Uso |
|---------|--------|-------------|-----|
| ZIP | Comprimidos | `.zip`, `.rar`, `.7z`, `.tar.gz` | Archivos comprimidos |
| EXE | Ejecutables | `.exe`, `.msi`, `.app`, `.dmg` | Instaladores y ejecutables |

**Ejemplo:**
```
SOF/
├── ZIP/
│   ├── Backups/
│   │   └── proyecto_2025.zip
│   └── Librerias/
│       └── python_libs.tar.gz
└── EXE/
    ├── Instaladores/
    │   ├── VSCode_Setup.exe
    │   └── Python_3.12.msi
    └── Portable/
        └── NotepadPlusPlus_Portable.exe
```

---

## Organización Interna Flexible

### Puedes Crear Subdirectorios Temáticos

Dentro de cada carpeta de formato, organiza como prefieras:

**Por Tema:**
```
WORD/
├── Academico/
├── Personal/
└── Trabajo/
```

**Por Proyecto:**
```
WORD/
├── Tesis_2026/
├── Paper_Congreso/
└── Documentacion_Sistema/
```

**Por Fecha:**
```
WORD/
├── 2026/
│   ├── 01_Enero/
│   └── 02_Febrero/
└── 2025/
```

**Sin Organización (plano):**
```
WORD/
├── documento1.docx
├── documento2.docx
└── documento3.docx
```

**¡Tú decides!** El sistema de formato solo define el primer nivel.

---

## Guía de Decisión Rápida

### ¿Dónde Va Este Archivo?

**Tengo un archivo `informe.docx`**
→ DOC/WORD/

**Tengo un PDF de un libro**
→ LIB/PDF/

**Tengo un PDF de un paper que estoy leyendo**
→ LIB/PDF/

**Tengo un PDF de un documento de trabajo**
→ DOC/ (puedes crear DOC/PDF/) o LIB/PDF/ (según prefieras)

**Tengo una foto `.jpg`**
→ MED/PNG/

**Tengo un video `.mp4`**
→ MED/AVI/

**Tengo una canción `.mp3`**
→ MED/MP3/

**Tengo un instalador `.exe`**
→ SOF/EXE/

**Tengo un archivo `.zip` con código**
→ SOF/ZIP/

**Tengo un documento LaTeX `.tex`**
→ DOC/TEX/

**Tengo una hoja de cálculo `.xlsx`**
→ DOC/EXC/

---

## Casos Especiales

### Archivos con Múltiples Versiones

```
DOC/WORD/
└── Tesis/
    ├── Tesis_v1.docx
    ├── Tesis_v2.docx
    └── Tesis_Final.docx
```

### Proyectos con Múltiples Formatos

**Opción 1: Separar por formato**
```
DOC/WORD/Proyecto_X/
DOC/PPT/Proyecto_X/
DOC/EXC/Proyecto_X/
```

**Opción 2: Referencias cruzadas en Alpha**
```
Alpha/A1-INV/B12-LAB/C124-PRY/Proyecto_X.md
```
En la nota de Alpha, referencias a los archivos en Delta:
```markdown
## Recursos
- [Documento principal](../../Delta/DOC/WORD/Proyecto_X/documento.docx)
- [Presentación](../../Delta/DOC/PPT/Proyecto_X/presentacion.pptx)
- [Datos](../../Delta/DOC/EXC/Proyecto_X/datos.xlsx)
```

### PDFs: ¿LIB o DOC?

**Regla general:**
- **Lectura** (libros, papers publicados) → LIB/PDF/
- **Trabajo** (documentos propios, borradores) → Podrías crear DOC/PDF/

**Recomendación:** Mantén todos los PDFs en LIB/PDF/ para simplicidad.

---

## Migración desde Estructura Anterior

Si tienes archivos en la estructura anterior:

### Script de Migración (Ejemplo)

```bash
#!/bin/bash

# Migrar de estructura temática a estructura por formato

# DOC/Académico/*.docx → DOC/WORD/Académico/
mv Delta/DOC/Académico/*.docx Delta_NEW/DOC/WORD/Académico/

# LIB/Ficción/*.epub → LIB/EPUB/Ficción/
mv Delta/LIB/Ficción/*.epub Delta_NEW/LIB/EPUB/Ficción/

# MED/Audio/*.mp3 → MED/MP3/
mv Delta/MED/Audio/*.mp3 Delta_NEW/MED/MP3/

# Continuar según necesidad...
```

**Recomendación:** No migres todo de golpe. Mueve archivos gradualmente a medida que los uses.

---

## Ventajas Técnicas

### 1. Búsqueda Eficiente

```bash
# Buscar todos los Word
find Delta/DOC/WORD -name "*.docx"

# Buscar todos los PDFs
find Delta/LIB/PDF -name "*.pdf"

# Buscar todas las imágenes
find Delta/MED/PNG -name "*.jpg" -o -name "*.png"
```

### 2. Automatización

```python
# Script para clasificar automáticamente
import shutil
from pathlib import Path

def clasificar_archivo(archivo):
    ext = archivo.suffix.lower()

    if ext in ['.doc', '.docx']:
        destino = Path('Delta/DOC/WORD')
    elif ext in ['.pdf']:
        destino = Path('Delta/LIB/PDF')
    elif ext in ['.mp3', '.wav']:
        destino = Path('Delta/MED/MP3')
    elif ext in ['.jpg', '.png']:
        destino = Path('Delta/MED/PNG')
    elif ext in ['.zip', '.rar']:
        destino = Path('Delta/SOF/ZIP')
    # ... más extensiones

    shutil.move(archivo, destino / archivo.name)
```

### 3. Estadísticas

```bash
# Contar archivos por formato
echo "Word: $(find Delta/DOC/WORD -name "*.docx" | wc -l)"
echo "PDF: $(find Delta/LIB/PDF -name "*.pdf" | wc -l)"
echo "Imágenes: $(find Delta/MED/PNG -type f | wc -l)"
```

---

## Extensiones del Sistema (Futuro)

### Añadir Nuevos Formatos

Si necesitas añadir más formatos:

```bash
# Archivos de audio sin pérdida
mkdir Delta/MED/FLAC

# Documentos de Google Docs exportados
mkdir Delta/DOC/GDOC

# Archivos de código fuente
mkdir Delta/SOF/SRC
```

### Modificar el Script

Edita `generar_estructura_abgd.py` en la sección `delta_structure` y añade:

```python
'FLAC': {
    'nombre': 'Audio Sin Pérdida',
    'extensiones': ['.flac', '.alac'],
    'descripcion': 'Archivos de audio sin compresión'
}
```

---

## Comparación con Beta

| Aspecto | Beta | Delta |
|---------|------|-------|
| Organización | Cronológica (por fecha) | Por formato (por extensión) |
| Propósito | Backups temporales | Archivo permanente |
| Flexibilidad | Estructura libre | Estructura por formato |
| Crecimiento | Añadir fechas | Añadir formatos |

**Complementarios:**
- **Beta:** "¿Qué respaldé el 15 de febrero?"
- **Delta:** "¿Dónde están mis archivos Word?"

---

## Archivos Modificados

### Script Principal
- **[generar_estructura_abgd.py](generar_estructura_abgd.py)** (función `generate_delta()`)
  - Líneas 456-650: Completamente reescrita
  - Ahora organiza por formato de archivo
  - Diccionario `delta_structure` con formatos y extensiones
  - Archivos .md con extensiones soportadas

### Estructura Generada
- **Directorios:** 105 (menos que antes)
- **Archivos:** 116 (más eficiente)
- **Subcarpetas:**
  - DOC: 4 formatos (WORD, PPT, EXC, TEX)
  - LIB: 2 formatos (EPUB, PDF)
  - MED: 3 formatos (MP3, AVI, PNG)
  - SOF: 2 formatos (ZIP, EXE)

---

## Preguntas Frecuentes

### ¿Por qué usar códigos cortos (WORD, PPT, etc.)?
→ Consistencia con el sistema ABGD. Son cortos, claros y fáciles de escribir.

### ¿Puedo mezclar PDFs de libros con PDFs de documentos?
→ Sí, todos en LIB/PDF/. Crea subdirectorios si quieres separarlos.

### ¿Qué pasa si tengo un formato no listado?
→ Colócalo en la categoría más cercana o crea una nueva carpeta de formato.

### ¿Debo reorganizar todo mi Delta actual?
→ No urgentemente. Hazlo gradualmente a medida que uses los archivos.

### ¿Puedo tener subcarpetas dentro de los formatos?
→ ¡Absolutamente! Es altamente recomendado para organización temática.

### ¿Esto reemplaza la organización temática?
→ No, la complementa. Formato en primer nivel, tema en segundo nivel.

---

## Próximos Pasos

1. **Explora la nueva estructura:**
   ```bash
   cd Sistema_ABGD/ABGD-2026-02-04/Delta/
   ls -R
   ```

2. **Lee los archivos .md descriptivos:**
   - [Delta/README.md](Sistema_ABGD/ABGD-2026-02-04/Delta/README.md)
   - [Delta/DOC/WORD/WORD.md](Sistema_ABGD/ABGD-2026-02-04/Delta/DOC/WORD/WORD.md)
   - [Delta/MED/PNG/PNG.md](Sistema_ABGD/ABGD-2026-02-04/Delta/MED/PNG/PNG.md)

3. **Empieza a usar el sistema:**
   - Guarda nuevos archivos según su formato
   - Crea subdirectorios temáticos según necesites
   - Migra archivos antiguos gradualmente

---

**Sistema actualizado por:** Claude Code
**Implementado por:** David
**Fecha:** 2026-02-04
**Versión:** ABGD v1.3 (Delta con organización por formato)
