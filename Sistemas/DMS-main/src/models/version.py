"""
Modelo de Versión
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Version:
    """Representa una versión de un documento"""
    
    documento_id: str
    numero_version: str
    contenido: str
    fecha: datetime
    autor: str
    cambios: str = ""
    ruta: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte la versión a diccionario"""
        return {
            "documento_id": self.documento_id,
            "numero_version": self.numero_version,
            "contenido": self.contenido,
            "fecha": self.fecha.isoformat(),
            "autor": self.autor,
            "cambios": self.cambios,
            "ruta": self.ruta
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Version':
        """Crea una versión desde un diccionario"""
        return cls(
            documento_id=data["documento_id"],
            numero_version=data["numero_version"],
            contenido=data["contenido"],
            fecha=datetime.fromisoformat(data["fecha"]),
            autor=data["autor"],
            cambios=data.get("cambios", ""),
            ruta=data.get("ruta")
        )
