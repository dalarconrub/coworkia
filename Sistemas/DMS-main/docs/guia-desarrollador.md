# Guía de Desarrollador - Sistema DMS

## Configuración del Entorno

### Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd DMS

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Estructura del Código

### Organización de Módulos

```
src/
├── main.py                 # Punto de entrada
├── core/
│   ├── __init__.py
│   ├── document_manager.py
│   ├── version_controller.py
│   ├── metadata_manager.py
│   └── search_engine.py
├── models/
│   ├── __init__.py
│   ├── document.py
│   ├── category.py
│   └── version.py
├── storage/
│   ├── __init__.py
│   ├── file_storage.py
│   └── metadata_storage.py
└── utils/
    ├── __init__.py
    ├── validators.py
    └── formatters.py
```

## Modelos de Datos

### Document

```python
class Document:
    id: str
    titulo: str
    categoria: str
    autor: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    etiquetas: List[str]
    version_actual: str
    ruta: str
    activo: bool
```

### Version

```python
class Version:
    documento_id: str
    numero_version: str
    contenido: str
    fecha: datetime
    autor: str
    cambios: str
    ruta: str
```

### Category

```python
class Category:
    nombre: str
    descripcion: str
    fecha_creacion: datetime
    documento_count: int
```

## API Principal

### DocumentManager

```python
class DocumentManager:
    def add_document(self, titulo, categoria, contenido, autor, etiquetas)
    def get_document(self, doc_id)
    def update_document(self, doc_id, contenido)
    def delete_document(self, doc_id, permanente=False)
    def list_documents(self, filtros=None)
    def search_documents(self, query, filtros=None)
```

### VersionController

```python
class VersionController:
    def create_version(self, doc_id, contenido, autor, cambios)
    def get_version(self, doc_id, version)
    def list_versions(self, doc_id)
    def restore_version(self, doc_id, version)
    def compare_versions(self, doc_id, v1, v2)
```

### MetadataManager

```python
class MetadataManager:
    def save_metadata(self, doc_id, metadata)
    def get_metadata(self, doc_id)
    def update_metadata(self, doc_id, updates)
    def search_by_metadata(self, criterios)
```

## Extensión del Sistema

### Agregar Nuevo Formato de Documento

1. Crear parser en `src/utils/formatters.py`
2. Registrar en `DocumentManager`
3. Actualizar validadores

### Agregar Nuevo Backend de Almacenamiento

1. Implementar interfaz `StorageBackend`
2. Crear clase en `src/storage/`
3. Configurar en `config/storage.json`

### Agregar Nuevo Comando CLI

1. Agregar función en `src/main.py`
2. Registrar en parser de argumentos
3. Documentar en `docs/guia-usuario.md`

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Test específico
pytest tests/test_document_manager.py

# Con cobertura
pytest --cov=src tests/
```

### Escribir Tests

```python
# tests/test_document_manager.py
def test_add_document():
    manager = DocumentManager()
    doc = manager.add_document(
        titulo="Test",
        categoria="Test",
        contenido="# Test",
        autor="Test User"
    )
    assert doc.id is not None
    assert doc.titulo == "Test"
```

## Estándares de Código

### Formato

- Usar Black para formateo automático
- Línea máxima: 100 caracteres
- Usar type hints

### Documentación

- Docstrings en formato Google
- Comentarios para lógica compleja
- Mantener README actualizado

### Git

- Commits descriptivos
- Branch por feature
- Pull requests con descripción

## Contribuciones

### Proceso

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m "Agregar nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Checklist

- [ ] Código sigue estándares
- [ ] Tests pasan
- [ ] Documentación actualizada
- [ ] Sin errores de linting
- [ ] Compatible con versiones anteriores

## Debugging

### Logs

El sistema genera logs en `logs/dms.log`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Modo Debug

```bash
python src/main.py --debug --verbose
```

## Despliegue

### Configuración de Producción

1. Actualizar `config/production.json`
2. Configurar backups automáticos
3. Establecer permisos de archivos
4. Configurar monitoreo

### Docker (Futuro)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
```
