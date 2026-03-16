"""
Modelo de Categoría
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    """Representa una categoría de documentos"""
    
    nombre: str
    descripcion: str = ""
    fecha_creacion: datetime = None
    documento_count: int = 0
    
    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now()
    
    def to_dict(self) -> dict:
        """Convierte la categoría a diccionario"""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "documento_count": self.documento_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        """Crea una categoría desde un diccionario"""
        return cls(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
            fecha_creacion=datetime.fromisoformat(data.get("fecha_creacion", datetime.now().isoformat())),
            documento_count=data.get("documento_count", 0)
        )
