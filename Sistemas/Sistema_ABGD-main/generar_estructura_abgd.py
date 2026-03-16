#!/usr/bin/env python3
"""
Script para generar la estructura completa del sistema ABGD.

Autor: David
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
            root_dir: Directorio contenedor donde crear la estructura con fecha
            excel_path: Ruta al archivo Excel con los datos
            dry_run: Si es True, solo muestra qué se va a crear
        """
        # Obtener fecha actual
        now = datetime.now()
        self.current_year = now.year
        self.current_date = now.strftime('%Y-%m-%d')

        # Crear ruta completa: root_dir/ABGD-YYYY-MM-DD/
        self.container_dir = Path(root_dir)
        self.dated_folder = f"ABGD-{self.current_date}"
        self.root_dir = self.container_dir / self.dated_folder

        self.excel_path = Path(excel_path)
        self.dry_run = dry_run

        # Contadores para estadísticas
        self.dirs_created = 0
        self.files_created = 0

        # Leer datos del Excel
        self.areas_df = None
        self.bloques_df = None
        self.contextos_df = None
        self._load_excel_data()

    def _load_excel_data(self):
        """Carga los datos del archivo Excel."""
        logger.info(f"Cargando datos desde {self.excel_path}")
        try:
            self.areas_df = pd.read_excel(self.excel_path, sheet_name='AREAS')
            self.bloques_df = pd.read_excel(self.excel_path, sheet_name='BLOQUES')
            self.contextos_df = pd.read_excel(self.excel_path, sheet_name='CONTEXTOS')

            logger.info(f"✓ Cargadas {len(self.areas_df)} áreas")
            logger.info(f"✓ Cargados {len(self.bloques_df)} bloques")
            logger.info(f"✓ Cargados {len(self.contextos_df)} contextos")
        except Exception as e:
            logger.error(f"Error al cargar el Excel: {e}")
            sys.exit(1)

    def create_directory(self, path: Path):
        """Crea un directorio si no existe."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Crearía directorio: {path}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Creado directorio: {path}")
        self.dirs_created += 1

    def create_markdown_file(self, path: Path, content: str):
        """Crea un archivo markdown con contenido."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Crearía archivo: {path}")
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Creado archivo: {path}")
        self.files_created += 1

    def create_gitkeep(self, path: Path):
        """Crea un archivo .gitkeep vacío."""
        gitkeep_path = path / '.gitkeep'
        if self.dry_run:
            logger.info(f"[DRY-RUN] Crearía .gitkeep: {gitkeep_path}")
        else:
            gitkeep_path.touch()
            logger.debug(f"Creado .gitkeep: {gitkeep_path}")
        self.files_created += 1

    def generate_area_md_content(self, area_row) -> str:
        """Genera contenido markdown para un área."""
        codigo = area_row['Código']
        nombre = area_row['Nombre']
        descripcion = area_row['Descripción']

        # Obtener bloques de esta área
        bloques = self.bloques_df[self.bloques_df['Área'] == codigo]
        bloques_list = '\n'.join([f"- {b['Código']}: {b['Nombre']}" for _, b in bloques.iterrows()])

        content = f"""# {codigo} - {nombre}

**Tipo:** ÁREA
**Código:** {codigo}
**Descripción:** {descripcion}

---

## Propósito

Esta área contiene toda la documentación relacionada con {nombre.lower()}.

## Bloques

{bloques_list}

---

*Generado automáticamente por el script de estructura ABGD*
"""
        return content

    def generate_bloque_md_content(self, bloque_row) -> str:
        """Genera contenido markdown para un bloque."""
        codigo = bloque_row['Código']
        nombre = bloque_row['Nombre']
        area = bloque_row['Área']
        descripcion = bloque_row['Descripción']

        # Obtener el nombre del área
        area_row = self.areas_df[self.areas_df['Código'] == area].iloc[0]
        area_nombre = area_row['Nombre']

        # Obtener contextos de este bloque
        contextos = self.contextos_df[self.contextos_df['Bloque'] == codigo]
        contextos_list = '\n'.join([f"- {c['Código']}: {c['Nombre']}" for _, c in contextos.iterrows()])

        content = f"""# {codigo} - {nombre}

**Tipo:** BLOQUE
**Código:** {codigo}
**Área:** {area} - {area_nombre}
**Descripción:** {descripcion}

---

## Propósito

Documentación y gestión de {nombre.lower()}.

## Contextos

{contextos_list}

---

*Generado automáticamente por el script de estructura ABGD*
"""
        return content

    def generate_contexto_md_content(self, contexto_row) -> str:
        """Genera contenido markdown para un contexto."""
        codigo = contexto_row['Código']
        nombre = contexto_row['Nombre']
        bloque = contexto_row['Bloque']
        area = contexto_row['Área']
        descripcion = contexto_row['Descripción']

        # Obtener nombres de área y bloque
        area_row = self.areas_df[self.areas_df['Código'] == area].iloc[0]
        area_nombre = area_row['Nombre']

        bloque_row = self.bloques_df[self.bloques_df['Código'] == bloque].iloc[0]
        bloque_nombre = bloque_row['Nombre']

        content = f"""# {codigo} - {nombre}

**Tipo:** CONTEXTO
**Código:** {codigo}
**Bloque:** {bloque} - {bloque_nombre}
**Área:** {area} - {area_nombre}
**Descripción:** {descripcion}

---

## Propósito

Notas y documentación de {nombre.lower()}.

## Estructura sugerida

- Una nota por tema o proyecto
- Usar plantillas cuando sea apropiado
- Enlaces a recursos relacionados

---

*Generado automáticamente por el script de estructura ABGD*
"""
        return content

    def generate_alpha(self):
        """Genera la estructura de Alpha desde el Excel."""
        logger.info("Generando estructura Alpha...")

        alpha_path = self.root_dir / 'Alpha'
        self.create_directory(alpha_path)

        # Crear README de Alpha
        readme_content = """# Alpha - Vault de Obsidian

**Tipo:** NÚCLEO DE TRABAJO ACTIVO
**Sistema:** Johnny Decimal (Áreas → Bloques → Contextos)

---

## Propósito

Alpha es el vault principal de Obsidian organizado con un sistema Johnny Decimal adaptado de tres niveles jerárquicos.

## Estructura

- **ÁREAS (A)**: Grandes divisiones de vida y trabajo
- **BLOQUES (B)**: Agrupaciones temáticas dentro de cada área
- **CONTEXTOS (C)**: Carpetas específicas donde residen las notas

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(alpha_path / 'README.md', readme_content)

        # Iterar por cada área
        for _, area in self.areas_df.iterrows():
            area_codigo = area['Código']
            area_path = alpha_path / area_codigo
            self.create_directory(area_path)

            # Crear markdown del área
            area_md = self.generate_area_md_content(area)
            self.create_markdown_file(area_path / f"{area_codigo}.md", area_md)

            # Obtener bloques de esta área
            bloques = self.bloques_df[self.bloques_df['Área'] == area_codigo]

            for _, bloque in bloques.iterrows():
                bloque_codigo = bloque['Código']
                bloque_path = area_path / bloque_codigo
                self.create_directory(bloque_path)

                # Crear markdown del bloque
                bloque_md = self.generate_bloque_md_content(bloque)
                self.create_markdown_file(bloque_path / f"{bloque_codigo}.md", bloque_md)

                # Obtener contextos de este bloque
                contextos = self.contextos_df[self.contextos_df['Bloque'] == bloque_codigo]

                for _, contexto in contextos.iterrows():
                    contexto_codigo = contexto['Código']
                    contexto_path = bloque_path / contexto_codigo
                    self.create_directory(contexto_path)

                    # Crear markdown del contexto
                    contexto_md = self.generate_contexto_md_content(contexto)
                    self.create_markdown_file(contexto_path / f"{contexto_codigo}.md", contexto_md)

        logger.info("✓ Estructura Alpha completada")

    def generate_beta(self):
        """Genera la estructura de Beta (backups)."""
        logger.info("Generando estructura Beta...")

        beta_path = self.root_dir / 'Beta'
        self.create_directory(beta_path)

        # Crear README de Beta
        readme_content = """# Beta - Backups Cronológicos

**Tipo:** BACKUPS ESTRUCTURADOS
**Organización:** Cronológica por año y fecha

---

## Propósito

Beta contiene copias de seguridad periódicas organizadas cronológicamente por año y fecha.

## Estructura

- **BACKS-YYYY/**: Backups del año
  - **DISK-YYYY/**: Carpeta molde para backups
    - **DISK-YYYY-MM-DD/**: Snapshots por fecha

## Uso

Cada vez que realices un backup, crea una carpeta con la fecha dentro de DISK-YYYY:

```bash
# Ejemplo
mkdir Beta/BACKS-2026/DISK-2026/DISK-2026-02-04
# Copia tus archivos dentro
```

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(beta_path / 'README.md', readme_content)

        # Crear carpeta del año actual
        backs_year = f"BACKS-{self.current_year}"
        backs_path = beta_path / backs_year
        self.create_directory(backs_path)

        backs_md = f"""# {backs_year}

**Tipo:** CARPETA DE AÑO
**Año:** {self.current_year}

---

## Propósito

Contiene todos los backups del año {self.current_year}.

## Estructura

- **DISK-{self.current_year}/**: Carpeta molde para snapshots de backup
  - **DISK-{self.current_year}-MM-DD/**: Snapshots individuales por fecha

## Uso

Para realizar un backup:
1. Navega a `DISK-{self.current_year}/`
2. Crea una carpeta con la fecha: `DISK-{self.current_year}-MM-DD`
3. Copia el contenido a respaldar dentro de esa carpeta

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(backs_path / f"{backs_year}.md", backs_md)

        # Crear carpeta DISK con snapshot de ejemplo de la fecha actual
        disk_folder = f"DISK-{self.current_year}"
        disk_path = backs_path / disk_folder
        self.create_directory(disk_path)

        disk_md = f"""# {disk_folder}

**Tipo:** CARPETA MOLDE DE BACKUPS
**Año:** {self.current_year}

---

## Propósito

Esta carpeta contiene los snapshots de backup del año {self.current_year}.

## Estructura de Snapshots

Cada backup se guarda en una carpeta con formato: `DISK-{self.current_year}-MM-DD/`

Ejemplo:
```
DISK-{self.current_year}/
├── DISK-{self.current_year}-01-15/
│   └── [Contenido del backup]
├── DISK-{self.current_year}-02-01/
│   └── [Contenido del backup]
└── DISK-{self.current_year}-02-04/
    └── [Contenido del backup]
```

## Crear Nuevo Backup

```bash
# Crear carpeta con fecha de hoy
mkdir DISK-{self.current_year}-MM-DD

# Copiar contenido a respaldar
cp -r /ruta/origen/* DISK-{self.current_year}-MM-DD/
```

## Frecuencia Recomendada

- Backups críticos: Semanal
- Backups generales: Quincenal
- Backups completos: Mensual

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(disk_path / f"{disk_folder}.md", disk_md)

        # Crear snapshot de ejemplo con la fecha actual
        disk_snapshot = f"DISK-{self.current_year}-{self.current_date[5:]}"  # Extrae MM-DD
        disk_snapshot_path = disk_path / disk_snapshot
        self.create_directory(disk_snapshot_path)

        snapshot_md = f"""# {disk_snapshot}

**Tipo:** SNAPSHOT DE BACKUP
**Fecha:** {self.current_date}

---

## Propósito

Este es un snapshot de backup realizado el {self.current_date}.

## Contenido

Dentro de esta carpeta debes colocar el contenido que deseas respaldar en esta fecha.

Estructura sugerida:
```
{disk_snapshot}/
├── Documentos/
├── Proyectos/
├── Configuraciones/
└── Otros/
```

## Metadata del Backup

- **Fecha de creación:** {self.current_date}
- **Tipo de backup:** [Completo/Incremental/Diferencial]
- **Origen:** [Describir origen de los datos]
- **Notas:** [Añadir notas relevantes sobre este backup]

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(disk_snapshot_path / f"{disk_snapshot}.md", snapshot_md)
        self.create_gitkeep(disk_snapshot_path)

        logger.info("✓ Estructura Beta completada")

    def generate_delta(self):
        """Genera la estructura de Delta (archivo clasificado por formato)."""
        logger.info("Generando estructura Delta...")

        delta_path = self.root_dir / 'Delta'
        self.create_directory(delta_path)

        # Crear README de Delta
        readme_content = """# Delta - Archivo Clasificado

**Tipo:** BIBLIOTECA PERMANENTE
**Organización:** Por formato de archivo

---

## Propósito

Delta es la biblioteca permanente de archivos organizados por formato/extensión.

## Categorías (4×4)

- **DOC/**: Documentos ofimáticos (WORD, PPT, DAT, TEX)
- **LIB/**: Libros y bibliotecas (EPUB, PDF, CAL, BIB)
- **MED/**: Contenido multimedia (MP3, POD, AVI, PNG)
- **SOF/**: Software y desarrollo (ZIP, EXE, GIT, DEV)

## Estructura

Cada categoría contiene exactamente 4 subcarpetas por formato de archivo, facilitando la localización rápida según la extensión o tipo del archivo.

**Total: 16 formatos (4×4)**

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(delta_path / 'README.md', readme_content)

        # Estructura de Delta organizada por formato de archivo (4×4)
        delta_structure = {
            'DOC': {
                'nombre': 'Documentos',
                'descripcion': 'Documentos ofimáticos y de texto',
                'formatos': {
                    'WORD': {
                        'nombre': 'Microsoft Word',
                        'extensiones': ['.doc', '.docx'],
                        'descripcion': 'Documentos de Microsoft Word'
                    },
                    'PPT': {
                        'nombre': 'PowerPoint',
                        'extensiones': ['.ppt', '.pptx'],
                        'descripcion': 'Presentaciones de PowerPoint'
                    },
                    'DAT': {
                        'nombre': 'Datos',
                        'extensiones': ['.csv', '.dat', '.json', '.xml'],
                        'descripcion': 'Archivos de datos estructurados'
                    },
                    'TEX': {
                        'nombre': 'LaTeX',
                        'extensiones': ['.tex'],
                        'descripcion': 'Documentos LaTeX'
                    }
                }
            },
            'LIB': {
                'nombre': 'Libros',
                'descripcion': 'Libros y bibliotecas de referencias',
                'formatos': {
                    'EPUB': {
                        'nombre': 'EPUB',
                        'extensiones': ['.epub'],
                        'descripcion': 'Libros en formato EPUB'
                    },
                    'PDF': {
                        'nombre': 'PDF',
                        'extensiones': ['.pdf'],
                        'descripcion': 'Documentos PDF y libros digitales'
                    },
                    'CAL': {
                        'nombre': 'Calibre',
                        'extensiones': ['(carpetas)'],
                        'descripcion': 'Bibliotecas de Calibre'
                    },
                    'BIB': {
                        'nombre': 'Referencias',
                        'extensiones': ['.bib', '.ris', '.enw'],
                        'descripcion': 'Bibliotecas de Zotero y gestores de referencias'
                    }
                }
            },
            'MED': {
                'nombre': 'Media',
                'descripcion': 'Archivos multimedia',
                'formatos': {
                    'MP3': {
                        'nombre': 'Audio/Música',
                        'extensiones': ['.mp3', '.wav', '.flac', '.m4a'],
                        'descripcion': 'Archivos de audio y música'
                    },
                    'POD': {
                        'nombre': 'Podcasts',
                        'extensiones': ['.mp3', '.m4a', '.opus'],
                        'descripcion': 'Podcasts y audio hablado'
                    },
                    'AVI': {
                        'nombre': 'Video',
                        'extensiones': ['.avi', '.mp4', '.mkv', '.mov'],
                        'descripcion': 'Archivos de video'
                    },
                    'PNG': {
                        'nombre': 'Imágenes',
                        'extensiones': ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
                        'descripcion': 'Archivos de imagen'
                    }
                }
            },
            'SOF': {
                'nombre': 'Software',
                'descripcion': 'Software y desarrollo',
                'formatos': {
                    'ZIP': {
                        'nombre': 'Comprimidos',
                        'extensiones': ['.zip', '.rar', '.7z', '.tar.gz'],
                        'descripcion': 'Archivos comprimidos'
                    },
                    'EXE': {
                        'nombre': 'Ejecutables',
                        'extensiones': ['.exe', '.msi', '.app', '.dmg'],
                        'descripcion': 'Archivos ejecutables e instaladores'
                    },
                    'GIT': {
                        'nombre': 'Repositorios',
                        'extensiones': ['(.git)'],
                        'descripcion': 'Repositorios Git completos'
                    },
                    'DEV': {
                        'nombre': 'Desarrollo',
                        'extensiones': ['.py', '.js', '.sh', '.bat', '.ps1'],
                        'descripcion': 'Scripts sueltos y archivos de desarrollo'
                    }
                }
            }
        }

        for categoria, info in delta_structure.items():
            cat_path = delta_path / categoria
            self.create_directory(cat_path)

            # Listar formatos para el .md de categoría
            formatos_list = '\n'.join([f"- **{fmt}**: {data['nombre']} ({', '.join(data['extensiones'])})"
                                       for fmt, data in info['formatos'].items()])

            cat_md = f"""# {categoria} - {info['nombre']}

**Tipo:** CATEGORÍA DE ARCHIVO
**Código:** {categoria}
**Organización:** Por formato de archivo

---

## Propósito

{info['descripcion']}.

## Formatos

{formatos_list}

## Uso

Guarda cada archivo en la carpeta correspondiente a su formato/extensión.

---

*Generado automáticamente por el script de estructura ABGD*
"""
            self.create_markdown_file(cat_path / f"{categoria}.md", cat_md)

            # Crear carpetas por formato
            for formato, formato_info in info['formatos'].items():
                formato_path = cat_path / formato
                self.create_directory(formato_path)

                extensiones_str = ', '.join(formato_info['extensiones'])
                formato_md = f"""# {formato} - {formato_info['nombre']}

**Tipo:** FORMATO DE ARCHIVO
**Categoría:** {categoria} - {info['nombre']}
**Extensiones:** {extensiones_str}

---

## Propósito

{formato_info['descripcion']}.

## Archivos Soportados

{chr(10).join(['- `' + ext + '`' for ext in formato_info['extensiones']])}

## Uso

Guarda aquí todos los archivos con estas extensiones:
```
{formato}/
├── archivo1{formato_info['extensiones'][0]}
├── archivo2{formato_info['extensiones'][0]}
└── subdirectorio/
    └── archivo3{formato_info['extensiones'][0]}
```

**Tip:** Puedes crear subdirectorios temáticos dentro de esta carpeta para mejor organización.

---

*Generado automáticamente por el script de estructura ABGD*
"""
                self.create_markdown_file(formato_path / f"{formato}.md", formato_md)
                self.create_gitkeep(formato_path)

        logger.info("✓ Estructura Delta completada")

    def generate_gamma(self):
        """Genera la estructura de Gamma (temporal)."""
        logger.info("Generando estructura Gamma...")

        gamma_path = self.root_dir / 'Gamma'
        self.create_directory(gamma_path)

        # Crear README de Gamma
        readme_content = """# Gamma - Almacenamiento Temporal

**Tipo:** TEMPORAL CRONOLÓGICO
**Organización:** Cronológica por fecha

---

## Propósito

Gamma es el espacio para archivos que requieren conservación pero cuya clasificación no está clara o es temporal.

## Estructura

- **Gamma-YYYY/**: Año
  - **Gamma-YYYY-MM-DD/**: Carpetas por fecha de llegada

## Principio de Uso

- Depositar archivos sin clasificar
- **Revisión trimestral obligatoria**
- Tres destinos: Delta (clasificado), Alpha (proyecto activo), o Eliminar

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(gamma_path / 'README.md', readme_content)

        # Crear carpeta del año actual
        gamma_year = f"Gamma-{self.current_year}"
        gamma_year_path = gamma_path / gamma_year
        self.create_directory(gamma_year_path)

        gamma_md = f"""# {gamma_year}

**Tipo:** CARPETA TEMPORAL ANUAL
**Año:** {self.current_year}

---

## Propósito

Almacenamiento temporal de archivos del año {self.current_year} sin clasificación definida.

## Uso

Crear carpetas con formato `Gamma-{self.current_year}-MM-DD` según sea necesario.

## Revisión

- Trimestral obligatoria
- Carpetas >3 meses: revisar y reclasificar
- Carpetas >1 año: eliminar

---

*Generado automáticamente por el script de estructura ABGD*
"""
        self.create_markdown_file(gamma_year_path / f"{gamma_year}.md", gamma_md)
        self.create_gitkeep(gamma_year_path)

        logger.info("✓ Estructura Gamma completada")

    def generate_all(self):
        """Genera toda la estructura ABGD."""
        logger.info("=== Iniciando generación de estructura ABGD ===")
        logger.info(f"Directorio contenedor: {self.container_dir}")
        logger.info(f"Carpeta con fecha: {self.dated_folder}")
        logger.info(f"Ruta completa: {self.root_dir}")
        logger.info(f"Modo dry-run: {self.dry_run}")
        logger.info("")

        # Crear directorio contenedor
        self.create_directory(self.container_dir)

        # Crear directorio con fecha
        self.create_directory(self.root_dir)

        # Generar cada componente
        self.generate_alpha()
        self.generate_beta()
        self.generate_delta()
        self.generate_gamma()

        # Mostrar estadísticas
        logger.info("")
        logger.info("=== Generación completada ===")
        logger.info(f"Directorios creados: {self.dirs_created}")
        logger.info(f"Archivos creados: {self.files_created}")

        if self.dry_run:
            logger.info("")
            logger.info("MODO DRY-RUN: No se creó ningún archivo real.")
            logger.info("Ejecuta sin --dry-run para crear la estructura.")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Genera la estructura completa del sistema ABGD',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s
    (Crea ./Sistema_ABGD/ABGD-2026-02-04/)

  %(prog)s --dry-run
    (Simula la creación sin crear archivos)

  %(prog)s --root-dir ./Mi_Sistema
    (Crea ./Mi_Sistema/ABGD-2026-02-04/)

  %(prog)s --excel-path ./datos.xlsx
    (Usa un archivo Excel diferente)

Nota: Cada ejecución crea una carpeta con la fecha actual (ABGD-YYYY-MM-DD)
      dentro del directorio contenedor, permitiendo mantener versiones históricas.
"""
    )
    parser.add_argument(
        '--root-dir',
        type=str,
        default='./Sistema_ABGD',
        help='Directorio contenedor donde crear la estructura con fecha (default: ./Sistema_ABGD, creará ./Sistema_ABGD/ABGD-YYYY-MM-DD/)'
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
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verboso: muestra información detallada'
    )

    args = parser.parse_args()

    # Ajustar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validar que existe el Excel
    if not Path(args.excel_path).exists():
        logger.error(f"No se encuentra el archivo Excel: {args.excel_path}")
        sys.exit(1)

    # Crear generador y ejecutar
    try:
        generator = ABGDGenerator(
            root_dir=args.root_dir,
            excel_path=args.excel_path,
            dry_run=args.dry_run
        )

        generator.generate_all()

    except KeyboardInterrupt:
        logger.info("\nProceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
