"""
Núcleo del sistema DMS
"""

from .document_manager import DocumentManager
from .version_controller import VersionController
from .metadata_manager import MetadataManager
from .search_engine import SearchEngine

__all__ = [
    'DocumentManager',
    'VersionController',
    'MetadataManager',
    'SearchEngine'
]
