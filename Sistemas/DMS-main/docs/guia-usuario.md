# Guía de Usuario - Sistema DMS

## Introducción

Esta guía te ayudará a utilizar el Sistema de Gestión de Documentación de manera efectiva.

## Conceptos Básicos

### Documento

Un documento es cualquier archivo de texto (principalmente Markdown) que deseas gestionar en el sistema.

### Categoría

Las categorías ayudan a organizar documentos por tema o tipo. Ejemplos: "Técnico", "Administrativo", "Legal".

### Versión

Cada vez que modificas un documento, se crea una nueva versión. El sistema mantiene un historial completo.

### Metadatos

Información adicional sobre el documento: autor, fecha, etiquetas, etc.

## Operaciones Básicas

### Agregar un Documento

```bash
python src/main.py add \
  --categoria "Técnico" \
  --titulo "Manual de Instalación" \
  --archivo "manual.md"
```

### Listar Documentos

```bash
# Listar todos
python src/main.py list

# Por categoría
python src/main.py list --categoria "Técnico"

# Con filtros
python src/main.py list --autor "Juan Pérez"
```

### Buscar Documentos

```bash
# Búsqueda simple
python src/main.py search --query "instalación"

# Búsqueda avanzada
python src/main.py search \
  --query "manual" \
  --categoria "Técnico" \
  --etiqueta "guia"
```

### Ver un Documento

```bash
# Versión actual
python src/main.py view --id "doc-001"

# Versión específica
python src/main.py view --id "doc-001" --version "1.0"
```

### Editar un Documento

```bash
# Editar versión actual
python src/main.py edit --id "doc-001"

# El sistema creará automáticamente una nueva versión
```

### Eliminar un Documento

```bash
# Eliminar (marca como eliminado, mantiene versiones)
python src/main.py delete --id "doc-001"

# Eliminar permanentemente
python src/main.py delete --id "doc-001" --permanente
```

## Gestión de Categorías

### Crear Categoría

```bash
python src/main.py categoria create --nombre "Marketing"
```

### Listar Categorías

```bash
python src/main.py categoria list
```

### Eliminar Categoría

```bash
python src/main.py categoria delete --nombre "Marketing"
```

## Gestión de Versiones

### Ver Historial

```bash
python src/main.py version history --id "doc-001"
```

### Restaurar Versión

```bash
python src/main.py version restore --id "doc-001" --version "1.0"
```

### Comparar Versiones

```bash
python src/main.py version compare \
  --id "doc-001" \
  --version1 "1.0" \
  --version2 "2.0"
```

## Etiquetas

### Agregar Etiquetas

```bash
python src/main.py tag add --id "doc-001" --tags "urgente,importante"
```

### Buscar por Etiqueta

```bash
python src/main.py search --etiqueta "urgente"
```

## Exportación e Importación

### Exportar Documento

```bash
python src/main.py export --id "doc-001" --formato "pdf"
```

### Exportar Categoría Completa

```bash
python src/main.py export --categoria "Técnico" --formato "zip"
```

### Importar Documentos

```bash
python src/main.py import --archivo "documentos.zip"
```

## Plantillas

### Usar Plantilla

```bash
python src/main.py create --template "informe" --titulo "Informe Mensual"
```

### Listar Plantillas Disponibles

```bash
python src/main.py template list
```

## Mejores Prácticas

1. **Organización**: Usa categorías consistentes
2. **Nombres**: Usa títulos descriptivos
3. **Etiquetas**: Aplica etiquetas relevantes para búsqueda
4. **Versiones**: Revisa el historial antes de hacer cambios grandes
5. **Backup**: Exporta regularmente documentos importantes

## Solución de Problemas

### Documento no encontrado

Verifica el ID del documento:
```bash
python src/main.py list --id "doc-001"
```

### Error de permisos

Asegúrate de tener permisos de escritura en el directorio `documents/`.

### Búsqueda no encuentra resultados

Prueba con términos más generales o verifica las etiquetas del documento.
