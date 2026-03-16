"""
Controlador de versiones de documentos
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json

from ..models.version import Version


class VersionNotFoundError(Exception):
    """Excepción cuando una versión no se encuentra"""
    pass


class VersionController:
    """Controla las versiones de los documentos"""
    
    def __init__(self, base_path: str = "documents"):
        self.base_path = Path(base_path) / "versiones"
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_version_path(self, doc_id: str) -> Path:
        """Obtiene la ruta del directorio de versiones de un documento"""
        return self.base_path / doc_id
    
    def _get_next_version(self, doc_id: str) -> str:
        """Obtiene el número de la próxima versión"""
        versiones = self.list_versions(doc_id)
        if not versiones:
            return "1.0"
        
        # Obtener última versión
        ultima = versiones[-1]
        numero = float(ultima.numero_version)
        return f"{numero + 0.1:.1f}"
    
    def create_version(
        self,
        doc_id: str,
        contenido: str,
        autor: str,
        cambios: str = ""
    ) -> Version:
        """Crea una nueva versión de un documento"""
        
        # Obtener número de versión
        numero_version = self._get_next_version(doc_id)
        
        # Crear directorio si no existe
        version_dir = self._get_version_path(doc_id)
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo de versión
        archivo_version = version_dir / f"v{numero_version}.md"
        archivo_version.write_text(contenido, encoding='utf-8')
        
        # Crear enlace simbólico a latest (si es posible)
        latest_link = version_dir / "latest.md"
        if latest_link.exists():
            latest_link.unlink()
        try:
            latest_link.symlink_to(archivo_version.name)
        except OSError:
            # En Windows puede fallar, crear copia
            import shutil
            shutil.copy(archivo_version, latest_link)
        
        # Crear objeto versión
        version = Version(
            documento_id=doc_id,
            numero_version=numero_version,
            contenido=contenido,
            fecha=datetime.now(),
            autor=autor,
            cambios=cambios,
            ruta=str(archivo_version)
        )
        
        # Guardar metadatos de versión
        self._save_version_metadata(version)
        
        return version
    
    def get_version(self, doc_id: str, version: str) -> Version:
        """Obtiene una versión específica"""
        version_dir = self._get_version_path(doc_id)
        archivo = version_dir / f"v{version}.md"
        
        if not archivo.exists():
            raise VersionNotFoundError(f"Versión {version} no encontrada para documento {doc_id}")
        
        contenido = archivo.read_text(encoding='utf-8')
        
        # Cargar metadatos
        metadata_file = version_dir / f"v{version}.json"
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text())
            return Version.from_dict(metadata)
        
        # Crear versión básica si no hay metadatos
        return Version(
            documento_id=doc_id,
            numero_version=version,
            contenido=contenido,
            fecha=datetime.fromtimestamp(archivo.stat().st_mtime),
            autor="Desconocido",
            cambios="",
            ruta=str(archivo)
        )
    
    def list_versions(self, doc_id: str) -> List[Version]:
        """Lista todas las versiones de un documento"""
        version_dir = self._get_version_path(doc_id)
        
        if not version_dir.exists():
            return []
        
        versiones = []
        
        # Buscar archivos de versión
        for archivo in version_dir.glob("v*.md"):
            if archivo.name == "latest.md":
                continue
            
            version_num = archivo.stem[1:]  # Quitar 'v' del inicio
            
            # Cargar metadatos si existen
            metadata_file = version_dir / f"v{version_num}.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                versiones.append(Version.from_dict(metadata))
            else:
                contenido = archivo.read_text(encoding='utf-8')
                versiones.append(Version(
                    documento_id=doc_id,
                    numero_version=version_num,
                    contenido=contenido,
                    fecha=datetime.fromtimestamp(archivo.stat().st_mtime),
                    autor="Desconocido",
                    cambios="",
                    ruta=str(archivo)
                ))
        
        # Ordenar por número de versión
        versiones.sort(key=lambda v: float(v.numero_version))
        
        return versiones
    
    def restore_version(self, doc_id: str, version: str) -> Version:
        """Restaura una versión anterior como versión actual"""
        version_obj = self.get_version(doc_id, version)
        
        # Crear nueva versión con el contenido restaurado
        nueva_version = self.create_version(
            doc_id=doc_id,
            contenido=version_obj.contenido,
            autor=version_obj.autor,
            cambios=f"Restaurado desde versión {version}"
        )
        
        return nueva_version
    
    def compare_versions(self, doc_id: str, v1: str, v2: str) -> dict:
        """Compara dos versiones de un documento"""
        version1 = self.get_version(doc_id, v1)
        version2 = self.get_version(doc_id, v2)
        
        lines1 = version1.contenido.split('\n')
        lines2 = version2.contenido.split('\n')
        
        # Comparación simple línea por línea
        added = []
        removed = []
        modified = []
        
        max_len = max(len(lines1), len(lines2))
        for i in range(max_len):
            if i >= len(lines1):
                added.append((i+1, lines2[i]))
            elif i >= len(lines2):
                removed.append((i+1, lines1[i]))
            elif lines1[i] != lines2[i]:
                modified.append((i+1, lines1[i], lines2[i]))
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def delete_all_versions(self, doc_id: str):
        """Elimina todas las versiones de un documento"""
        version_dir = self._get_version_path(doc_id)
        if version_dir.exists():
            import shutil
            shutil.rmtree(version_dir)
    
    def _save_version_metadata(self, version: Version):
        """Guarda metadatos de una versión"""
        version_dir = self._get_version_path(version.documento_id)
        metadata_file = version_dir / f"v{version.numero_version}.json"
        metadata_file.write_text(json.dumps(version.to_dict(), indent=2), encoding='utf-8')
