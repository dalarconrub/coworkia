"""
Gestor de metadatos de documentos
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class MetadataManager:
    """Gestiona los metadatos de los documentos"""
    
    def __init__(self, base_path: str = "documents"):
        self.base_path = Path(base_path) / "metadata"
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_metadata_path(self, doc_id: str) -> Path:
        """Obtiene la ruta del archivo de metadatos"""
        return self.base_path / f"{doc_id}.json"
    
    def save_metadata(self, doc_id: str, metadata: Dict) -> bool:
        """Guarda metadatos de un documento"""
        metadata_file = self._get_metadata_path(doc_id)
        metadata_file.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        return True
    
    def get_metadata(self, doc_id: str) -> Optional[Dict]:
        """Obtiene metadatos de un documento"""
        metadata_file = self._get_metadata_path(doc_id)
        
        if not metadata_file.exists():
            return None
        
        try:
            return json.loads(metadata_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def update_metadata(self, doc_id: str, updates: Dict) -> Dict:
        """Actualiza metadatos existentes"""
        metadata = self.get_metadata(doc_id) or {}
        metadata.update(updates)
        self.save_metadata(doc_id, metadata)
        return metadata
    
    def delete_metadata(self, doc_id: str) -> bool:
        """Elimina metadatos de un documento"""
        metadata_file = self._get_metadata_path(doc_id)
        if metadata_file.exists():
            metadata_file.unlink()
            return True
        return False
    
    def get_all_metadata(self) -> List[Dict]:
        """Obtiene todos los metadatos"""
        metadatos = []
        
        for metadata_file in self.base_path.glob("*.json"):
            try:
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                metadatos.append(metadata)
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        return metadatos
    
    def search_by_metadata(self, criterios: Dict) -> List[str]:
        """Busca documentos por criterios de metadatos"""
        resultados = []
        all_metadata = self.get_all_metadata()
        
        for metadata in all_metadata:
            match = True
            
            if "autor" in criterios and metadata.get("autor") != criterios["autor"]:
                match = False
            
            if "fecha_desde" in criterios:
                fecha_creacion = metadata.get("fecha_creacion", "")
                if fecha_creacion < criterios["fecha_desde"]:
                    match = False
            
            if "fecha_hasta" in criterios:
                fecha_creacion = metadata.get("fecha_creacion", "")
                if fecha_creacion > criterios["fecha_hasta"]:
                    match = False
            
            if "etiquetas" in criterios:
                doc_etiquetas = set(metadata.get("etiquetas", []))
                criterio_etiquetas = set(criterios["etiquetas"])
                if not criterio_etiquetas.issubset(doc_etiquetas):
                    match = False
            
            if match:
                resultados.append(metadata["id"])
        
        return resultados
