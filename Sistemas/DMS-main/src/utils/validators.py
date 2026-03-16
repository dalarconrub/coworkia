"""
Validadores de documentos
"""

from typing import Optional


def validate_document(contenido: str) -> bool:
    """Valida que el contenido de un documento sea válido"""
    if not contenido or not isinstance(contenido, str):
        return False
    
    if len(contenido.strip()) == 0:
        return False
    
    # Validaciones adicionales pueden agregarse aquí
    # Por ejemplo, verificar formato Markdown válido
    
    return True


def validate_category(nombre: str) -> bool:
    """Valida que un nombre de categoría sea válido"""
    if not nombre or not isinstance(nombre, str):
        return False
    
    if len(nombre.strip()) == 0:
        return False
    
    # No permitir caracteres especiales
    import re
    if re.search(r'[<>:"/\\|?*]', nombre):
        return False
    
    return True


def validate_tags(etiquetas: list) -> bool:
    """Valida una lista de etiquetas"""
    if not isinstance(etiquetas, list):
        return False
    
    for tag in etiquetas:
        if not isinstance(tag, str) or len(tag.strip()) == 0:
            return False
    
    return True
