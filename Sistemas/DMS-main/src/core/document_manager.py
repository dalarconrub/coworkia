"""
Gestor principal de documentos
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from ..models.document import Document
from ..models.category import Category
from .version_controller import VersionController
from .metadata_manager import MetadataManager
from ..storage.file_storage import FileStorage
from ..utils.validators import validate_document


class DocumentNotFoundError(Exception):
    """Excepción cuando un documento no se encuentra"""
    pass


class InvalidDocumentError(Exception):
    """Excepción cuando un documento no es válido"""
    pass


class DocumentManager:
    """Gestor central de documentos"""
    
    def __init__(self, base_path: str = "documents"):
        self.base_path = Path(base_path)
        self.storage = FileStorage(base_path)
        self.version_controller = VersionController(base_path)
        self.metadata_manager = MetadataManager(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Asegura que los directorios necesarios existan"""
        (self.base_path / "categorias").mkdir(parents=True, exist_ok=True)
        (self.base_path / "versiones").mkdir(parents=True, exist_ok=True)
        (self.base_path / "metadata").mkdir(parents=True, exist_ok=True)
    
    def _generate_id(self) -> str:
        """Genera un ID único para un documento"""
        return f"doc-{uuid.uuid4().hex[:8]}"
    
    def add_document(
        self,
        titulo: str,
        categoria: str,
        contenido: str,
        autor: str,
        etiquetas: List[str] = None
    ) -> Document:
        """Agrega un nuevo documento al sistema"""
        
        # Validar
        if not validate_document(contenido):
            raise InvalidDocumentError("El contenido del documento no es válido")
        
        # Crear documento
        doc_id = self._generate_id()
        ahora = datetime.now()
        
        # Crear ruta del archivo
        categoria_path = self.base_path / "categorias" / categoria.lower()
        categoria_path.mkdir(parents=True, exist_ok=True)
        
        nombre_archivo = self._sanitize_filename(titulo) + ".md"
        ruta = categoria_path / nombre_archivo
        
        # Guardar contenido
        self.storage.save_file(ruta, contenido)
        
        # Crear versión inicial
        version = self.version_controller.create_version(
            doc_id=doc_id,
            contenido=contenido,
            autor=autor,
            cambios="Versión inicial"
        )
        
        # Crear objeto documento
        documento = Document(
            id=doc_id,
            titulo=titulo,
            categoria=categoria.lower(),
            autor=autor,
            fecha_creacion=ahora,
            fecha_modificacion=ahora,
            etiquetas=etiquetas or [],
            version_actual=version.numero_version,
            ruta=str(ruta)
        )
        
        # Guardar metadatos
        self.metadata_manager.save_metadata(doc_id, documento.to_dict())
        
        return documento
    
    def get_document(self, doc_id: str) -> Document:
        """Obtiene un documento por su ID"""
        metadata = self.metadata_manager.get_metadata(doc_id)
        if not metadata:
            raise DocumentNotFoundError(f"Documento {doc_id} no encontrado")
        
        return Document.from_dict(metadata)
    
    def update_document(
        self,
        doc_id: str,
        contenido: str,
        autor: str,
        cambios: str = ""
    ) -> Document:
        """Actualiza un documento existente"""
        
        documento = self.get_document(doc_id)
        
        if not documento.activo:
            raise InvalidDocumentError("No se puede actualizar un documento eliminado")
        
        # Validar contenido
        if not validate_document(contenido):
            raise InvalidDocumentError("El contenido del documento no es válido")
        
        # Crear nueva versión
        version = self.version_controller.create_version(
            doc_id=doc_id,
            contenido=contenido,
            autor=autor,
            cambios=cambios or "Actualización de documento"
        )
        
        # Actualizar archivo
        if documento.ruta:
            self.storage.save_file(Path(documento.ruta), contenido)
        
        # Actualizar documento
        documento.fecha_modificacion = datetime.now()
        documento.version_actual = version.numero_version
        
        # Guardar metadatos actualizados
        self.metadata_manager.save_metadata(doc_id, documento.to_dict())
        
        return documento
    
    def delete_document(self, doc_id: str, permanente: bool = False) -> bool:
        """Elimina un documento"""
        documento = self.get_document(doc_id)
        
        if permanente:
            # Eliminar archivo
            if documento.ruta and Path(documento.ruta).exists():
                Path(documento.ruta).unlink()
            # Eliminar versiones
            self.version_controller.delete_all_versions(doc_id)
            # Eliminar metadatos
            self.metadata_manager.delete_metadata(doc_id)
        else:
            # Marcar como inactivo
            documento.activo = False
            self.metadata_manager.save_metadata(doc_id, documento.to_dict())
        
        return True
    
    def list_documents(self, filtros: Optional[Dict] = None) -> List[Document]:
        """Lista documentos con filtros opcionales"""
        filtros = filtros or {}
        documentos = []
        
        # Obtener todos los metadatos
        all_metadata = self.metadata_manager.get_all_metadata()
        
        for metadata in all_metadata:
            doc = Document.from_dict(metadata)
            
            # Aplicar filtros
            if filtros.get("activo") is not None and doc.activo != filtros["activo"]:
                continue
            if filtros.get("categoria") and doc.categoria != filtros["categoria"].lower():
                continue
            if filtros.get("autor") and doc.autor != filtros["autor"]:
                continue
            if filtros.get("etiqueta") and filtros["etiqueta"] not in doc.etiquetas:
                continue
            
            documentos.append(doc)
        
        return documentos
    
    def search_documents(self, query: str, filtros: Optional[Dict] = None) -> List[Document]:
        """Busca documentos por texto"""
        from .search_engine import SearchEngine
        
        search_engine = SearchEngine(self.base_path)
        doc_ids = search_engine.search(query, filtros)
        
        documentos = []
        for doc_id in doc_ids:
            try:
                documentos.append(self.get_document(doc_id))
            except DocumentNotFoundError:
                continue
        
        return documentos
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza un nombre de archivo"""
        import re
        # Reemplazar caracteres no válidos
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        # Limitar longitud
        filename = filename[:100]
        return filename.strip()
