# Guía de Inicio Rápido - DMS

## Instalación Rápida

### Paso 1: Verificar Python

Asegúrate de tener Python 3.8 o superior instalado:

```bash
python --version
```

### Paso 2: Clonar/Descargar el Proyecto

Si tienes el proyecto en un repositorio:

```bash
git clone <url-del-repositorio>
cd DMS
```

O simplemente navega al directorio del proyecto.

### Paso 3: Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 4: Verificar Instalación

El sistema funciona sin dependencias adicionales. Para verificar:

```bash
python src/main.py --help
```

Deberías ver el menú de ayuda del sistema.

## Primeros Pasos

### Crear tu Primer Documento

```bash
python src/main.py add --categoria "Técnico" --titulo "Mi Primer Documento" --autor "Tu Nombre"
```

O en múltiples líneas (Windows CMD):
```bash
python src/main.py add ^
  --categoria "Técnico" ^
  --titulo "Mi Primer Documento" ^
  --autor "Tu Nombre"
```

El sistema te pedirá que ingreses el contenido. Escribe tu texto y presiona Ctrl+D (Linux/Mac) o Ctrl+Z (Windows) para terminar.

### Listar Documentos

```bash
python src/main.py list
```

### Ver un Documento

Primero obtén el ID del documento con `list`, luego:

```bash
python src/main.py view --id "doc-xxxxx"
```

### Buscar Documentos

```bash
python src/main.py search --query "palabra clave"
```

## Ejemplo Completo

```bash
# 1. Crear documento desde archivo
# En Windows CMD, crear el archivo primero:
echo # Mi Documento > mi-doc.md
echo. >> mi-doc.md
echo Contenido aquí >> mi-doc.md

# Luego agregar el documento:
python src/main.py add --categoria "Técnico" --titulo "Documento de Prueba" --archivo "mi-doc.md" --autor "Usuario" --etiquetas "prueba,ejemplo"

# 2. Listar todos los documentos
python src/main.py list

# 3. Buscar
python src/main.py search --query "prueba"

# 4. Ver historial de versiones (usa el ID del paso 2)
python src/main.py version history --id "doc-xxxxx"
```

## Estructura Creada

Después de crear documentos, verás esta estructura:

```
documents/
├── categorias/
│   └── tecnico/
│       └── mi-documento.md
├── versiones/
│   └── doc-xxxxx/
│       ├── v1.0.md
│       └── latest.md
└── metadata/
    └── doc-xxxxx.json
```

## Próximos Pasos

- Lee la [Guía de Usuario](guia-usuario.md) para funciones avanzadas
- Revisa la [Arquitectura](arquitectura.md) para entender el sistema
- Explora los [Ejemplos](../ejemplos/) para ver código de ejemplo

## Solución de Problemas

### Error: "No module named 'src'"

Asegúrate de estar en el directorio raíz del proyecto (donde está `src/`).

### Error de Permisos

Asegúrate de tener permisos de escritura en el directorio del proyecto.

### No se encuentran documentos

Verifica que el directorio `documents/` se haya creado correctamente.
