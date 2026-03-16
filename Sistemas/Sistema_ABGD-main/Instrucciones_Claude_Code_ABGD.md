# Instrucciones para Generar la Estructura ABGD con Claude Code

## Objetivo

Crear un script de Python que genere automáticamente toda la estructura de carpetas del sistema ABGD (Alpha, Beta, Delta, Gamma) con sus subcarpetas correspondientes, incluyendo un archivo Markdown en cada carpeta con el mismo nombre y título.

---

## Requisitos Previos

1. **Claude Code instalado** en VS Code
2. **Python 3.8+** instalado en el sistema
3. **Archivo Excel** `Sistema_ABC_Completo_Final.xlsx` como fuente de datos
4. Acceso al directorio donde se generará la estructura

---

## Estructura a Generar

### 1. Alpha (Vault de Obsidian)

Generar estructura Johnny Decimal completa basada en el Excel:

```
Alpha/
├── README.md
├── A0-GTD/
│   ├── A0-GTD.md
│   ├── B0A-RED/
│   │   ├── B0A-RED.md
│   │   ├── C0A0/
│   │   │   └── C0A0.md
│   │   ├── C0A1-REF/
│   │   │   └── C0A1-REF.md
│   │   ├── C0A2-ENL/
│   │   │   └── C0A2-ENL.md
│   │   └── C0A3-DIR/
│   │       └── C0A3-DIR.md
│   ├── B0B-ABC/
│   │   ├── B0B-ABC.md
│   │   ├── C0B0/
│   │   │   └── C0B0.md
│   │   ├── C0B4-ARE/
│   │   │   └── C0B4-ARE.md
│   │   ├── C0B5-BLQ/
│   │   │   └── C0B5-BLQ.md
│   │   └── C0B6-CTX/
│   │       └── C0B6-CTX.md
│   └── B0C-PLA/
│       ├── B0C-PLA.md
│       ├── C0C0/
│       │   └── C0C0.md
│       ├── C0C7-PRY/
│       │   └── C0C7-PRY.md
│       ├── C0C8-TAR/
│       │   └── C0C8-TAR.md
│       └── C0C9-NOT/
│           └── C0C9-NOT.md
├── A1-INV/
│   ├── A1-INV.md
│   └── [estructura similar con sus bloques y contextos]
├── A2-UNI/
│   ├── A2-UNI.md
│   └── [estructura similar]
├── A3-VIT/
│   ├── A3-VIT.md
│   └── [estructura similar]
└── A4-ARC/
    ├── A4-ARC.md
    └── [estructura similar]
```

### 2. Beta (Backups)

Generar estructura de año actual y subcarpetas de origen:

```
Beta/
├── README.md
├── BACKS-2026/
│   ├── BACKS-2026.md
│   ├── GDRIVE-2026/
│   │   ├── GDRIVE-2026.md
│   │   └── .gitkeep
│   ├── MSI-2026/
│   │   ├── MSI-2026.md
│   │   └── .gitkeep
│   ├── HP-2026/
│   │   ├── HP-2026.md
│   │   └── .gitkeep
│   └── ONEDRIVE-2026/
│       ├── ONEDRIVE-2026.md
│       └── .gitkeep
└── .gitkeep
```

### 3. Delta (Archivo Clasificado)

Generar estructura semántica por tipo de contenido:

```
Delta/
├── README.md
├── DOC/
│   ├── DOC.md
│   ├── Académico/
│   │   ├── Académico.md
│   │   └── .gitkeep
│   ├── Personal/
│   │   ├── Personal.md
│   │   └── .gitkeep
│   ├── Profesional/
│   │   ├── Profesional.md
│   │   └── .gitkeep
│   └── Referencia/
│       ├── Referencia.md
│       └── .gitkeep
├── LIB/
│   ├── LIB.md
│   ├── Ficción/
│   │   ├── Ficción.md
│   │   └── .gitkeep
│   ├── No-ficción/
│   │   ├── No-ficción.md
│   │   └── .gitkeep
│   ├── Técnico/
│   │   ├── Técnico.md
│   │   └── .gitkeep
│   └── Académico/
│       ├── Académico.md
│       └── .gitkeep
├── MED/
│   ├── MED.md
│   ├── Audio/
│   │   ├── Audio.md
│   │   └── .gitkeep
│   ├── Video/
│   │   ├── Video.md
│   │   └── .gitkeep
│   ├── Imágenes/
│   │   ├── Imágenes.md
│   │   └── .gitkeep
│   └── Presentaciones/
│       ├── Presentaciones.md
│       └── .gitkeep
└── SOF/
    ├── SOF.md
    ├── Instaladores/
    │   ├── Instaladores.md
    │   └── .gitkeep
    ├── Portable/
    │   ├── Portable.md
    │   └── .gitkeep
    ├── Scripts/
    │   ├── Scripts.md
    │   └── .gitkeep
    └── Configuraciones/
        ├── Configuraciones.md
        └── .gitkeep
```

### 4. Gamma (Temporal)

Generar estructura de año actual:

```
Gamma/
├── README.md
├── Gamma-2026/
│   ├── Gamma-2026.md
│   └── .gitkeep
└── .gitkeep
```

---

## Especificaciones del Script

### Funcionalidades Requeridas

1. **Leer archivo Excel** `Sistema_ABC_Completo_Final.xlsx`
   - Hoja "AREAS": Obtener todas las áreas
   - Hoja "BLOQUES": Obtener bloques por área
   - Hoja "CONTEXTOS": Obtener contextos por bloque

2. **Crear estructura Alpha** (dinámica desde Excel)
   - Para cada ÁREA:
     - Crear carpeta `A[N]-[CÓDIGO]/`
     - Crear archivo `A[N]-[CÓDIGO].md`
   - Para cada BLOQUE dentro del área:
     - Crear carpeta `B[XX]-[CÓDIGO]/`
     - Crear archivo `B[XX]-[CÓDIGO].md`
   - Para cada CONTEXTO dentro del bloque:
     - Crear carpeta `C[XXX]` o `C[XXX]-[CÓDIGO]/`
     - Crear archivo con mismo nombre `.md`

3. **Crear estructura Beta** (estática)
   - Carpeta año actual: `BACKS-YYYY/`
   - Subcarpetas de origen: `GDRIVE-YYYY/`, `MSI-YYYY/`, `HP-YYYY/`, `ONEDRIVE-YYYY/`
   - Archivos `.md` y `.gitkeep` en cada carpeta

4. **Crear estructura Delta** (estática)
   - Carpetas principales: `DOC/`, `LIB/`, `MED/`, `SOF/`
   - Subcarpetas según especificación
   - Archivos `.md` y `.gitkeep` en cada carpeta

5. **Crear estructura Gamma** (estática)
   - Carpeta año actual: `Gamma-YYYY/`
   - Archivos `.md` y `.gitkeep`

### Formato de Archivos Markdown

Cada archivo `.md` debe contener:

```markdown
# [Nombre de la carpeta]

**Tipo:** [ÁREA/BLOQUE/CONTEXTO]  
**Código:** [Código completo]  
**Descripción:** [Descripción desde Excel o descripción predefinida]

---

## Propósito

[Descripción extendida del propósito de esta carpeta]

## Contenido

[Descripción de qué tipo de archivos/notas deben ir aquí]

---

*Generado automáticamente por el script de estructura ABGD*
```

#### Ejemplos de contenido según tipo:

**Para ÁREA (ej: A1-INV.md):**
```markdown
# A1-INV - Investigación

**Tipo:** ÁREA  
**Código:** A1-INV  
**Descripción:** Investigación académica y proyectos

---

## Propósito

Esta área contiene toda la documentación relacionada con investigación académica, proyectos de investigación, publicaciones y trabajo de laboratorio.

## Bloques

- B11-CVT: Curriculum Vitae
- B12-LAB: Laboratorio
- B13-PUB: Publicaciones

---

*Generado automáticamente por el script de estructura ABGD*
```

**Para BLOQUE (ej: B12-LAB.md):**
```markdown
# B12-LAB - Laboratorio

**Tipo:** BLOQUE  
**Código:** B12-LAB  
**Área:** A1-INV - Investigación  
**Descripción:** Trabajo de laboratorio

---

## Propósito

Documentación y gestión de trabajo de laboratorio, experimentos, proyectos de laboratorio y dirección de tesis.

## Contextos

- C120: Base laboratorio
- C124-PRY: Proyectos
- C125-EXP: Experimentos
- C126-DIR: Direccion tesis tfg tfm

---

*Generado automáticamente por el script de estructura ABGD*
```

**Para CONTEXTO (ej: C124-PRY.md):**
```markdown
# C124-PRY - Proyectos

**Tipo:** CONTEXTO  
**Código:** C124-PRY  
**Bloque:** B12-LAB - Laboratorio  
**Área:** A1-INV - Investigación  
**Descripción:** Proyectos de laboratorio

---

## Propósito

Notas y documentación de proyectos específicos de laboratorio.

## Estructura sugerida

- Una nota por proyecto
- Usar plantillas de proyecto
- Enlaces a experimentos relacionados

---

*Generado automáticamente por el script de estructura ABGD*
```

**Para carpetas de Beta (ej: GDRIVE-2026.md):**
```markdown
# GDRIVE-2026

**Tipo:** ORIGEN DE BACKUP  
**Servicio:** Google Drive  
**Año:** 2026

---

## Propósito

Almacena los snapshots de backups de Google Drive del año 2026.

## Estructura de Snapshots

Cada backup se guarda en una carpeta con formato: `GDRIVE-2026-MM-DD/`

Dentro de cada snapshot se mantiene la estructura original:
- Descargas/
- Escritorio/
- Documentos/
- Imágenes/
- Vídeos/

## Frecuencia

Backups semanales (cada lunes)

---

*Generado automáticamente por el script de estructura ABGD*
```

---

## Instrucciones para Claude Code

### Prompt Inicial para Claude Code

```
Necesito crear un script de Python que genere automáticamente la estructura completa 
de carpetas del sistema ABGD. El script debe:

1. Leer el archivo Excel "Sistema_ABC_Completo_Final.xlsx" que contiene:
   - Hoja "AREAS": 5 áreas con columnas [Código, Nombre, Descripción, Estado]
   - Hoja "BLOQUES": 15 bloques con columnas [Código, Nombre, Área, Descripción]
   - Hoja "CONTEXTOS": 60 contextos con columnas [Código, Nombre, Bloque, Área, Descripción, Num_Notas]

2. Crear la estructura completa de 4 carpetas principales:
   - Alpha/: Estructura dinámica basada en el Excel (áreas → bloques → contextos)
   - Beta/: Estructura estática de backups por año
   - Delta/: Estructura estática clasificada por tipo (DOC, LIB, MED, SOF)
   - Gamma/: Estructura estática temporal por año

3. En cada carpeta creada (de cualquier nivel), generar un archivo .md con:
   - Nombre del archivo = nombre de la carpeta
   - Título del archivo = nombre de la carpeta
   - Contenido estructurado con tipo, código, descripción y propósito

4. Incluir archivos .gitkeep en carpetas vacías finales

El script debe ser modular, con funciones claras para cada sección, y debe 
permitir especificar el directorio raíz donde crear la estructura.

¿Puedes ayudarme a crear este script siguiendo las especificaciones detalladas 
que tengo en el documento de instrucciones?
```

### Flujo de Trabajo Recomendado

1. **Abrir VS Code** con Claude Code activado

2. **Preparar el directorio:**
   ```bash
   mkdir ~/ABGD_Sistema
   cd ~/ABGD_Sistema
   ```

3. **Copiar el archivo Excel** al directorio de trabajo:
   ```bash
   cp /ruta/al/Sistema_ABC_Completo_Final.xlsx .
   ```

4. **Iniciar Claude Code** con el prompt inicial

5. **Iteración con Claude Code:**
   
   **Primera iteración:**
   ```
   Comienza creando la función para leer el Excel y las funciones 
   para crear la estructura de Alpha basándose en los datos del Excel.
   ```

   **Segunda iteración:**
   ```
   Ahora añade las funciones para crear Beta, Delta y Gamma con sus 
   estructuras estáticas. Usa el año actual (2026) para Beta y Gamma.
   ```

   **Tercera iteración:**
   ```
   Añade la funcionalidad para crear los archivos .md en cada carpeta 
   con el formato especificado. Los archivos deben tener el mismo nombre 
   que la carpeta y usar la información del Excel cuando esté disponible.
   ```

   **Cuarta iteración:**
   ```
   Añade manejo de errores, logging, y una función main() que orqueste 
   todo el proceso. Debe poder ejecutarse con un parámetro para especificar 
   el directorio raíz.
   ```

   **Quinta iteración (opcional):**
   ```
   Añade una opción --dry-run que muestre qué se va a crear sin crear 
   realmente las carpetas y archivos.
   ```

6. **Ejecutar el script:**
   ```bash
   python generar_estructura_abgd.py --root-dir ./ABGD_Sistema
   ```

---

## Estructura del Script Sugerida

```python
#!/usr/bin/env python3
"""
Script para generar la estructura completa del sistema ABGD.

Autor: [Tu nombre]
Fecha: 2026-02-04
Versión: 1.0
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import argparse
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ABGDGenerator:
    """Generador de estructura de carpetas ABGD."""
    
    def __init__(self, root_dir: str, excel_path: str, dry_run: bool = False):
        """
        Inicializa el generador.
        
        Args:
            root_dir: Directorio raíz donde crear la estructura
            excel_path: Ruta al archivo Excel con los datos
            dry_run: Si es True, solo muestra qué se va a crear
        """
        self.root_dir = Path(root_dir)
        self.excel_path = Path(excel_path)
        self.dry_run = dry_run
        self.current_year = datetime.now().year
        
        # Leer datos del Excel
        self.areas_df = None
        self.bloques_df = None
        self.contextos_df = None
        self._load_excel_data()
    
    def _load_excel_data(self):
        """Carga los datos del archivo Excel."""
        logger.info(f"Cargando datos desde {self.excel_path}")
        # Implementar carga de Excel
        pass
    
    def create_directory(self, path: Path):
        """Crea un directorio si no existe."""
        # Implementar creación de directorio
        pass
    
    def create_markdown_file(self, path: Path, content: str):
        """Crea un archivo markdown con contenido."""
        # Implementar creación de archivo
        pass
    
    def generate_area_md_content(self, area_row) -> str:
        """Genera contenido markdown para un área."""
        # Implementar generación de contenido
        pass
    
    def generate_bloque_md_content(self, bloque_row) -> str:
        """Genera contenido markdown para un bloque."""
        # Implementar generación de contenido
        pass
    
    def generate_contexto_md_content(self, contexto_row) -> str:
        """Genera contenido markdown para un contexto."""
        # Implementar generación de contenido
        pass
    
    def generate_alpha(self):
        """Genera la estructura de Alpha desde el Excel."""
        logger.info("Generando estructura Alpha...")
        # Implementar generación de Alpha
        pass
    
    def generate_beta(self):
        """Genera la estructura de Beta (backups)."""
        logger.info("Generando estructura Beta...")
        # Implementar generación de Beta
        pass
    
    def generate_delta(self):
        """Genera la estructura de Delta (archivo clasificado)."""
        logger.info("Generando estructura Delta...")
        # Implementar generación de Delta
        pass
    
    def generate_gamma(self):
        """Genera la estructura de Gamma (temporal)."""
        logger.info("Generando estructura Gamma...")
        # Implementar generación de Gamma
        pass
    
    def generate_all(self):
        """Genera toda la estructura ABGD."""
        logger.info("=== Iniciando generación de estructura ABGD ===")
        logger.info(f"Directorio raíz: {self.root_dir}")
        logger.info(f"Modo dry-run: {self.dry_run}")
        
        # Crear directorio raíz
        self.create_directory(self.root_dir)
        
        # Generar cada componente
        self.generate_alpha()
        self.generate_beta()
        self.generate_delta()
        self.generate_gamma()
        
        logger.info("=== Generación completada ===")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Genera la estructura completa del sistema ABGD'
    )
    parser.add_argument(
        '--root-dir',
        type=str,
        default='./ABGD_Sistema',
        help='Directorio raíz donde crear la estructura (default: ./ABGD_Sistema)'
    )
    parser.add_argument(
        '--excel-path',
        type=str,
        default='./Sistema_ABC_Completo_Final.xlsx',
        help='Ruta al archivo Excel (default: ./Sistema_ABC_Completo_Final.xlsx)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Modo simulación: muestra qué se va a crear sin crear nada'
    )
    
    args = parser.parse_args()
    
    # Validar que existe el Excel
    if not Path(args.excel_path).exists():
        logger.error(f"No se encuentra el archivo Excel: {args.excel_path}")
        sys.exit(1)
    
    # Crear generador y ejecutar
    generator = ABGDGenerator(
        root_dir=args.root_dir,
        excel_path=args.excel_path,
        dry_run=args.dry_run
    )
    
    generator.generate_all()


if __name__ == '__main__':
    main()
```

---

## Detalles Técnicos Importantes

### 1. Manejo de Caracteres Especiales

Algunos nombres de carpetas pueden tener caracteres especiales. El script debe:
- Sanitizar nombres si es necesario (ej: reemplazar `/` por `-`)
- Mantener tildes y caracteres UTF-8 correctamente
- Ejemplo: "Ficción" debe mantenerse como "Ficción", no "Ficcion"

### 2. Archivos .gitkeep

Crear `.gitkeep` en:
- Todas las carpetas finales (hojas del árbol) de Delta
- Carpetas de origen en Beta (GDRIVE-YYYY, MSI-YYYY, etc.)
- Carpeta Gamma-YYYY

**No crear** `.gitkeep` en:
- Carpetas de Alpha que contienen subcarpetas
- Carpetas intermedias que tendrán contenido

### 3. Encoding

- Todos los archivos `.md` deben usar **UTF-8** encoding
- Usar `encoding='utf-8'` al crear archivos

### 4. Rutas

- Usar `pathlib.Path` para compatibilidad multiplataforma
- Manejar correctamente separadores de ruta (Windows vs Unix)

### 5. Permisos

- El script puede requerir permisos de escritura en el directorio destino
- Manejar excepciones de permisos adecuadamente

---

## Testing del Script

### Checklist de Verificación

Después de ejecutar el script, verificar:

**Alpha:**
- [ ] Existen las 5 carpetas de áreas (A0-GTD a A4-ARC)
- [ ] Cada área tiene su archivo `.md` correspondiente
- [ ] Existen los 15 bloques distribuidos en las áreas
- [ ] Cada bloque tiene su archivo `.md`
- [ ] Existen los 60 contextos distribuidos en los bloques
- [ ] Cada contexto tiene su archivo `.md`
- [ ] Los archivos `.md` tienen el formato correcto
- [ ] Los nombres de archivo coinciden con los nombres de carpeta

**Beta:**
- [ ] Existe la carpeta `BACKS-2026/`
- [ ] Existen las 4 carpetas de origen (GDRIVE, MSI, HP, ONEDRIVE)
- [ ] Cada carpeta tiene su archivo `.md` y `.gitkeep`

**Delta:**
- [ ] Existen las 4 carpetas principales (DOC, LIB, MED, SOF)
- [ ] Cada categoría tiene sus subcarpetas correspondientes
- [ ] Todos los archivos `.md` y `.gitkeep` están presentes

**Gamma:**
- [ ] Existe la carpeta `Gamma-2026/`
- [ ] Tiene su archivo `.md` y `.gitkeep`

### Comando de Verificación

```bash
# Contar carpetas creadas
find ./ABGD_Sistema -type d | wc -l

# Contar archivos .md creados
find ./ABGD_Sistema -name "*.md" | wc -l

# Verificar estructura de Alpha
tree -L 3 ./ABGD_Sistema/Alpha/

# Verificar que todos los .md tienen contenido
find ./ABGD_Sistema -name "*.md" -exec wc -l {} \; | sort -n
```

---

## Troubleshooting

### Problema: Error al leer Excel

**Solución:** Verificar que pandas y openpyxl estén instalados
```bash
pip install pandas openpyxl
```

### Problema: Permisos denegados

**Solución:** Ejecutar con permisos adecuados o cambiar directorio destino
```bash
chmod u+w ./ABGD_Sistema
```

### Problema: Caracteres especiales mal codificados

**Solución:** Asegurar UTF-8 en la lectura del Excel y escritura de archivos
```python
df = pd.read_excel(excel_path, encoding='utf-8')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

### Problema: Carpetas ya existen

**Solución:** Añadir opción `--force` para sobrescribir o usar `--dry-run` primero

---

## Próximos Pasos

Una vez generada la estructura:

1. **Revisar** que todas las carpetas y archivos se crearon correctamente
2. **Personalizar** los archivos `.md` según necesidades específicas
3. **Inicializar** el vault de Obsidian en `Alpha/`
4. **Configurar** scripts de backup para Beta
5. **Comenzar** a usar el sistema

---

## Mantenimiento del Script

El script debe actualizarse cuando:
- Se añadan nuevas áreas, bloques o contextos al Excel
- Cambie la estructura de Beta (nuevos orígenes de backup)
- Se modifique la estructura de Delta (nuevas categorías)
- Se requieran nuevos tipos de archivos markdown

**Versión del script:** 1.0  
**Fecha:** 2026-02-04  
**Mantenedor:** David

---

*Documento generado como parte del Sistema ABGD v1.0*
