"""
Ejemplo de uso del Sistema DMS
"""

from src.core.document_manager import DocumentManager
from src.core.version_controller import VersionController

# Inicializar el sistema
manager = DocumentManager()
version_ctrl = VersionController()

# Crear un documento
print("=== Creando documento ===")
doc = manager.add_document(
    titulo="Guía de Instalación",
    categoria="Técnico",
    contenido="""
# Guía de Instalación

## Requisitos

- Python 3.8+
- pip

## Instalación

1. Clonar el repositorio
2. Instalar dependencias
3. Ejecutar el sistema

## Verificación

Ejecutar: `python src/main.py --help`
""",
    autor="Sistema DMS",
    etiquetas=["instalación", "guía", "técnico"]
)

print(f"Documento creado: {doc.id}")
print(f"Título: {doc.titulo}")
print(f"Versión: {doc.version_actual}")

# Listar documentos
print("\n=== Listando documentos ===")
documentos = manager.list_documents()
print(f"Total de documentos: {len(documentos)}")
for d in documentos:
    print(f"  - {d.titulo} ({d.categoria})")

# Buscar documentos
print("\n=== Buscando documentos ===")
resultados = manager.search_documents("instalación")
print(f"Resultados encontrados: {len(resultados)}")
for r in resultados:
    print(f"  - {r.titulo}")

# Actualizar documento
print("\n=== Actualizando documento ===")
doc_actualizado = manager.update_document(
    doc_id=doc.id,
    contenido="""
# Guía de Instalación

## Requisitos

- Python 3.8+
- pip
- Git (opcional)

## Instalación

1. Clonar el repositorio
2. Crear entorno virtual
3. Instalar dependencias
4. Ejecutar el sistema

## Verificación

Ejecutar: `python src/main.py --help`
""",
    autor="Sistema DMS",
    cambios="Agregado Git como requisito opcional y paso de entorno virtual"
)

print(f"Nueva versión: {doc_actualizado.version_actual}")

# Ver historial de versiones
print("\n=== Historial de versiones ===")
versiones = version_ctrl.list_versions(doc.id)
for v in versiones:
    print(f"  Versión {v.numero_version}: {v.fecha} - {v.autor}")
    if v.cambios:
        print(f"    Cambios: {v.cambios}")

# Obtener documento
print("\n=== Obteniendo documento ===")
doc_obtenido = manager.get_document(doc.id)
print(f"Documento: {doc_obtenido.titulo}")
print(f"Última modificación: {doc_obtenido.fecha_modificacion}")

print("\n=== Ejemplo completado ===")
