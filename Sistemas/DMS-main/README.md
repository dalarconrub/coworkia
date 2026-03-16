# Sistema de Gestión de Documentación (DMS)

## Descripción

Sistema de gestión de documentación diseñado para organizar, versionar y gestionar documentos de manera estructurada y eficiente.

## Estructura del Proyecto

```
DMS/
├── docs/                    # Documentación del sistema
│   ├── arquitectura.md     # Arquitectura del sistema
│   ├── guia-usuario.md     # Guía de usuario
│   ├── guia-desarrollador.md # Guía para desarrolladores
│   └── api.md              # Documentación de API
├── src/                     # Código fuente
│   ├── core/               # Núcleo del sistema
│   ├── models/             # Modelos de datos
│   ├── storage/             # Gestión de almacenamiento
│   └── utils/               # Utilidades
├── documents/               # Almacenamiento de documentos
│   ├── categorias/          # Documentos por categoría
│   ├── versiones/           # Control de versiones
│   └── metadata/            # Metadatos de documentos
├── templates/               # Plantillas de documentos
├── config/                  # Archivos de configuración
└── tests/                   # Pruebas unitarias
```

## Características Principales

- ✅ Organización por categorías y etiquetas
- ✅ Control de versiones de documentos
- ✅ Metadatos y búsqueda avanzada
- ✅ Plantillas personalizables
- ✅ API para integración
- ✅ Documentación completa en Markdown

## Instalación

```bash
# Clonar o descargar el proyecto
cd DMS

# Instalar dependencias (si aplica)
pip install -r requirements.txt
```

## Uso Rápido

```bash
# Ver ayuda
python src/main.py --help

# Agregar un documento
python src/main.py add --categoria "Técnico" --titulo "Manual de Usuario"

# Buscar documentos
python src/main.py search --query "manual"
```

## Documentación

- **[Guía de Inicio Rápido](docs/quick-start.md)** - Comienza aquí si eres nuevo
- [Índice de Documentación](docs/README.md) - Índice completo
- [Arquitectura del Sistema](docs/arquitectura.md)
- [Guía de Usuario](docs/guia-usuario.md)
- [Guía de Desarrollador](docs/guia-desarrollador.md)
- [API Reference](docs/api.md)
- [Estructura del Proyecto](docs/estructura-proyecto.md)

## Licencia

Este proyecto está bajo licencia MIT.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, lee la [Guía de Contribución](docs/guia-desarrollador.md#contribuciones) antes de enviar cambios.
