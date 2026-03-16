"""
Formateadores y exportadores de documentos
"""

from typing import Optional
from pathlib import Path


def format_document(contenido: str, formato: str = "markdown") -> str:
    """Formatea un documento según el formato especificado"""
    if formato == "markdown":
        return contenido
    elif formato == "html":
        return markdown_to_html(contenido)
    else:
        return contenido


def markdown_to_html(markdown: str) -> str:
    """Convierte Markdown a HTML básico"""
    # Conversión básica (puede mejorarse con una librería como markdown)
    html = markdown
    html = html.replace('\n\n', '</p><p>')
    html = html.replace('\n', '<br>')
    
    # Headers
    for i in range(6, 0, -1):
        html = html.replace('#' * i + ' ', f'<h{i}>')
        html = html.replace('\n', f'</h{i}>\n', 1)
    
    return f'<html><body><p>{html}</p></body></html>'


def export_to_pdf(contenido: str, ruta_salida: Path) -> bool:
    """Exporta un documento a PDF"""
    # Implementación básica - requiere librerías adicionales como reportlab o weasyprint
    try:
        html = markdown_to_html(contenido)
        # Aquí iría la conversión a PDF real
        # Por ahora, guardamos como HTML
        ruta_salida.with_suffix('.html').write_text(html, encoding='utf-8')
        return True
    except Exception:
        return False


def export_to_html(contenido: str, ruta_salida: Path) -> bool:
    """Exporta un documento a HTML"""
    try:
        html = markdown_to_html(contenido)
        ruta_salida.write_text(html, encoding='utf-8')
        return True
    except Exception:
        return False
