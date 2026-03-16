"""
Motor de búsqueda de documentos
"""

from pathlib import Path
from typing import List, Dict, Optional


class SearchEngine:
    """Motor de búsqueda de texto en documentos"""
    
    def __init__(self, base_path: str = "documents"):
        self.base_path = Path(base_path)
    
    def search(self, query: str, filtros: Optional[Dict] = None) -> List[str]:
        """Busca documentos por texto"""
        query_lower = query.lower()
        resultados = []
        filtros = filtros or {}
        
        # Buscar en todas las categorías
        categorias_path = self.base_path / "categorias"
        if not categorias_path.exists():
            return resultados
        
        for categoria_dir in categorias_path.iterdir():
            if not categoria_dir.is_dir():
                continue
            
            # Aplicar filtro de categoría
            if filtros.get("categoria"):
                if categoria_dir.name != filtros["categoria"].lower():
                    continue
            
            # Buscar en archivos de la categoría
            for archivo in categoria_dir.glob("*.md"):
                try:
                    contenido = archivo.read_text(encoding='utf-8')
                    
                    # Búsqueda simple (case-insensitive)
                    if query_lower in contenido.lower():
                        # Obtener ID del documento desde metadatos
                        doc_id = self._find_doc_id_by_path(str(archivo))
                        if doc_id and doc_id not in resultados:
                            resultados.append(doc_id)
                except Exception:
                    continue
        
        return resultados
    
    def _find_doc_id_by_path(self, ruta: str) -> Optional[str]:
        """Encuentra el ID de un documento por su ruta"""
        from .metadata_manager import MetadataManager
        
        manager = MetadataManager(self.base_path)
        all_metadata = manager.get_all_metadata()
        
        for metadata in all_metadata:
            if metadata.get("ruta") == ruta:
                return metadata.get("id")
        
        return None
