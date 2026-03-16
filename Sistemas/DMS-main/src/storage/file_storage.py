"""
Almacenamiento en sistema de archivos
"""

from pathlib import Path
from typing import Optional


class FileStorage:
    """Gestiona el almacenamiento de archivos"""
    
    def __init__(self, base_path: str = "documents"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, ruta: Path, contenido: str) -> bool:
        """Guarda un archivo"""
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding='utf-8')
        return True
    
    def read_file(self, ruta: Path) -> Optional[str]:
        """Lee un archivo"""
        if not ruta.exists():
            return None
        
        try:
            return ruta.read_text(encoding='utf-8')
        except Exception:
            return None
    
    def delete_file(self, ruta: Path) -> bool:
        """Elimina un archivo"""
        if ruta.exists():
            ruta.unlink()
            return True
        return False
    
    def file_exists(self, ruta: Path) -> bool:
        """Verifica si un archivo existe"""
        return ruta.exists()
