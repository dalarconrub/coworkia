# API Reference - Sistema DMS

## DocumentManager

### add_document

Agrega un nuevo documento al sistema.

**Parámetros:**
- `titulo` (str): Título del documento
- `categoria` (str): Categoría del documento
- `contenido` (str): Contenido del documento (Markdown)
- `autor` (str): Autor del documento
- `etiquetas` (List[str]): Lista de etiquetas

**Retorna:**
- `Document`: Objeto Document creado

**Ejemplo:**
```python
manager = DocumentManager()
doc = manager.add_document(
    titulo="Manual de Usuario",
    categoria="Técnico",
    contenido="# Manual\n\nContenido...",
    autor="Juan Pérez",
    etiquetas=["manual", "usuario"]
)
```

### get_document

Obtiene un documento por su ID.

**Parámetros:**
- `doc_id` (str): ID del documento

**Retorna:**
- `Document`: Objeto Document

**Lanza:**
- `DocumentNotFoundError`: Si el documento no existe

### update_document

Actualiza un documento existente.

**Parámetros:**
- `doc_id` (str): ID del documento
- `contenido` (str): Nuevo contenido
- `autor` (str): Autor de la modificación

**Retorna:**
- `Document`: Documento actualizado

**Nota:** Crea automáticamente una nueva versión.

### delete_document

Elimina un documento.

**Parámetros:**
- `doc_id` (str): ID del documento
- `permanente` (bool): Si True, elimina permanentemente

**Retorna:**
- `bool`: True si se eliminó correctamente

### list_documents

Lista documentos con filtros opcionales.

**Parámetros:**
- `filtros` (dict): Diccionario con filtros
  - `categoria` (str): Filtrar por categoría
  - `autor` (str): Filtrar por autor
  - `etiqueta` (str): Filtrar por etiqueta
  - `activo` (bool): Solo documentos activos

**Retorna:**
- `List[Document]`: Lista de documentos

### search_documents

Busca documentos por texto.

**Parámetros:**
- `query` (str): Texto a buscar
- `filtros` (dict): Filtros adicionales (mismo formato que list_documents)

**Retorna:**
- `List[Document]`: Lista de documentos encontrados

## VersionController

### create_version

Crea una nueva versión de un documento.

**Parámetros:**
- `doc_id` (str): ID del documento
- `contenido` (str): Contenido de la versión
- `autor` (str): Autor de la versión
- `cambios` (str): Descripción de los cambios

**Retorna:**
- `Version`: Objeto Version creado

### get_version

Obtiene una versión específica.

**Parámetros:**
- `doc_id` (str): ID del documento
- `version` (str): Número de versión

**Retorna:**
- `Version`: Objeto Version

### list_versions

Lista todas las versiones de un documento.

**Parámetros:**
- `doc_id` (str): ID del documento

**Retorna:**
- `List[Version]`: Lista de versiones ordenadas

### restore_version

Restaura una versión anterior como versión actual.

**Parámetros:**
- `doc_id` (str): ID del documento
- `version` (str): Número de versión a restaurar

**Retorna:**
- `Document`: Documento restaurado

### compare_versions

Compara dos versiones de un documento.

**Parámetros:**
- `doc_id` (str): ID del documento
- `v1` (str): Primera versión
- `v2` (str): Segunda versión

**Retorna:**
- `dict`: Diccionario con diferencias
  - `added`: Líneas agregadas
  - `removed`: Líneas eliminadas
  - `modified`: Líneas modificadas

## MetadataManager

### save_metadata

Guarda metadatos de un documento.

**Parámetros:**
- `doc_id` (str): ID del documento
- `metadata` (dict): Diccionario con metadatos

**Retorna:**
- `bool`: True si se guardó correctamente

### get_metadata

Obtiene metadatos de un documento.

**Parámetros:**
- `doc_id` (str): ID del documento

**Retorna:**
- `dict`: Diccionario con metadatos

### update_metadata

Actualiza metadatos existentes.

**Parámetros:**
- `doc_id` (str): ID del documento
- `updates` (dict): Diccionario con campos a actualizar

**Retorna:**
- `dict`: Metadatos actualizados

### search_by_metadata

Busca documentos por criterios de metadatos.

**Parámetros:**
- `criterios` (dict): Criterios de búsqueda
  - `autor` (str): Buscar por autor
  - `fecha_desde` (datetime): Fecha desde
  - `fecha_hasta` (datetime): Fecha hasta
  - `etiquetas` (List[str]): Lista de etiquetas

**Retorna:**
- `List[str]`: Lista de IDs de documentos

## Excepciones

### DocumentNotFoundError

Lanzada cuando un documento no se encuentra.

```python
class DocumentNotFoundError(Exception):
    pass
```

### VersionNotFoundError

Lanzada cuando una versión no se encuentra.

```python
class VersionNotFoundError(Exception):
    pass
```

### InvalidDocumentError

Lanzada cuando un documento no es válido.

```python
class InvalidDocumentError(Exception):
    pass
```

## Ejemplos de Uso

### Flujo Completo

```python
from src.core.document_manager import DocumentManager
from src.core.version_controller import VersionController

# Inicializar
manager = DocumentManager()
version_ctrl = VersionController()

# Crear documento
doc = manager.add_document(
    titulo="Guía de Instalación",
    categoria="Técnico",
    contenido="# Instalación\n\nPasos...",
    autor="Admin",
    etiquetas=["instalación", "guía"]
)

# Actualizar (crea nueva versión automáticamente)
manager.update_document(
    doc.id,
    contenido="# Instalación\n\nPasos actualizados...",
    autor="Admin"
)

# Ver historial
versiones = version_ctrl.list_versions(doc.id)
for v in versiones:
    print(f"Versión {v.numero_version}: {v.fecha}")

# Buscar
resultados = manager.search_documents("instalación")
```
