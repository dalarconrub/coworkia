"""
Modelo de Documento
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Document:
    """Representa un documento en el sistema"""
    
    id: str
    titulo: str
    categoria: str
    autor: str
    fecha_creacion: datetime
    fecha_modificacion: datetime
    etiquetas: List[str] = field(default_factory=list)
    version_actual: str = "1.0"
    ruta: Optional[str] = None
    activo: bool = True
    
    def to_dict(self) -> dict:
        """Convierte el documento a diccionario"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "autor": self.autor,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "fecha_modificacion": self.fecha_modificacion.isoformat(),
            "etiquetas": self.etiquetas,
            "version_actual": self.version_actual,
            "ruta": self.ruta,
            "activo": self.activo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """Crea un documento desde un diccionario"""
        return cls(
            id=data["id"],
            titulo=data["titulo"],
            categoria=data["categoria"],
            autor=data["autor"],
            fecha_creacion=datetime.fromisoformat(data["fecha_creacion"]),
            fecha_modificacion=datetime.fromisoformat(data["fecha_modificacion"]),
            etiquetas=data.get("etiquetas", []),
            version_actual=data.get("version_actual", "1.0"),
            ruta=data.get("ruta"),
            activo=data.get("activo", True)
        )
