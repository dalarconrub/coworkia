# Estructura del Proyecto DMS

## Descripción General

Este documento describe la estructura completa del proyecto Sistema de Gestión de Documentación (DMS).

## Estructura de Directorios

```
DMS/
│
├── docs/                          # Documentación del sistema
│   ├── arquitectura.md           # Arquitectura y diseño
│   ├── guia-usuario.md           # Guía para usuarios
│   ├── guia-desarrollador.md     # Guía para desarrolladores
│   ├── api.md                    # Referencia de API
│   └── estructura-proyecto.md    # Este archivo
│
├── src/                          # Código fuente
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada CLI
│   │
│   ├── core/                     # Núcleo del sistema
│   │   ├── __init__.py
│   │   ├── document_manager.py   # Gestor principal de documentos
│   │   ├── version_controller.py # Control de versiones
│   │   ├── metadata_manager.py   # Gestión de metadatos
│   │   └── search_engine.py      # Motor de búsqueda
│   │
│   ├── models/                   # Modelos de datos
│   │   ├── __init__.py
│   │   ├── document.py           # Modelo Document
│   │   ├── category.py           # Modelo Category
│   │   └── version.py            # Modelo Version
│   │
│   ├── storage/                  # Sistema de almacenamiento
│   │   ├── __init__.py
│   │   └── file_storage.py       # Almacenamiento en archivos
│   │
│   └── utils/                    # Utilidades
│       ├── __init__.py
│       ├── validators.py         # Validadores
│       └── formatters.py         # Formateadores y exportadores
│
├── documents/                    # Almacenamiento de documentos (generado)
│   ├── categorias/               # Documentos organizados por categoría
│   │   ├── tecnico/
│   │   ├── administrativo/
│   │   └── legal/
│   ├── versiones/                # Control de versiones
│   │   └── {doc_id}/
│   │       ├── v1.0.md
│   │       ├── v1.1.md
│   │       └── latest.md -> v1.1.md
│   └── metadata/                 # Metadatos en JSON
│       └── {doc_id}.json
│
├── templates/                    # Plantillas de documentos
│   ├── informe.md
│   ├── manual.md
│   └── guia.md
│
├── config/                       # Archivos de configuración
│   └── config.json
│
├── tests/                        # Pruebas unitarias (futuro)
│
├── README.md                     # Documentación principal
├── requirements.txt              # Dependencias Python
└── .gitignore                   # Archivos ignorados por Git
```

## Descripción de Componentes

### Documentación (docs/)

Contiene toda la documentación del sistema en formato Markdown:

- **arquitectura.md**: Describe la arquitectura, componentes y flujo de datos
- **guia-usuario.md**: Guía completa para usuarios finales
- **guia-desarrollador.md**: Guía para desarrolladores que quieran extender el sistema
- **api.md**: Referencia completa de la API
- **estructura-proyecto.md**: Este archivo

### Código Fuente (src/)

#### Core (src/core/)

Contiene la lógica principal del sistema:

- **document_manager.py**: Gestor central que coordina todas las operaciones
- **version_controller.py**: Maneja el control de versiones
- **metadata_manager.py**: Gestiona metadatos de documentos
- **search_engine.py**: Motor de búsqueda de texto

#### Models (src/models/)

Define las estructuras de datos:

- **document.py**: Clase Document con todos sus atributos
- **category.py**: Clase Category para categorías
- **version.py**: Clase Version para versiones de documentos

#### Storage (src/storage/)

Sistema de persistencia:

- **file_storage.py**: Implementación de almacenamiento en sistema de archivos

#### Utils (src/utils/)

Utilidades y helpers:

- **validators.py**: Funciones de validación
- **formatters.py**: Formateo y exportación de documentos

### Almacenamiento (documents/)

Estructura generada automáticamente:

- **categorias/**: Organización por categorías
- **versiones/**: Historial de versiones por documento
- **metadata/**: Archivos JSON con metadatos

### Plantillas (templates/)

Plantillas reutilizables para crear documentos:

- **informe.md**: Plantilla para informes
- **manual.md**: Plantilla para manuales técnicos
- **guia.md**: Plantilla para guías

### Configuración (config/)

- **config.json**: Configuración del sistema

## Convenciones de Nomenclatura

### Archivos Python

- Nombres en minúsculas con guiones bajos: `document_manager.py`
- Clases en CamelCase: `DocumentManager`
- Funciones y variables en snake_case: `add_document`

### Documentos

- IDs de documentos: `doc-{hash}` (ej: `doc-a1b2c3d4`)
- Versiones: `v{numero}` (ej: `v1.0`, `v1.1`)
- Nombres de archivos: sanitizados del título

### Categorías

- Nombres en minúsculas
- Sin espacios (usar guiones si es necesario)

## Flujo de Datos

1. **Creación**: Usuario → DocumentManager → FileStorage + MetadataManager + VersionController
2. **Búsqueda**: Usuario → SearchEngine → MetadataManager → DocumentManager
3. **Actualización**: Usuario → DocumentManager → VersionController → FileStorage

## Extensiones Futuras

La estructura está diseñada para permitir:

- Nuevos backends de almacenamiento (base de datos, cloud)
- Nuevos formatos de exportación
- Plugins y extensiones
- Interfaz web
- API REST
