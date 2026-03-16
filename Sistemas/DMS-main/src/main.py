"""
Interfaz de línea de comandos del Sistema DMS
"""

import argparse
import sys
from pathlib import Path

from src.core.document_manager import DocumentManager, DocumentNotFoundError
from src.core.version_controller import VersionController


def main():
    """Función principal de la CLI"""
    parser = argparse.ArgumentParser(
        description="Sistema de Gestión de Documentación (DMS)"
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # Comando: add
    add_parser = subparsers.add_parser('add', help='Agregar un nuevo documento')
    add_parser.add_argument('--categoria', required=True, help='Categoría del documento')
    add_parser.add_argument('--titulo', required=True, help='Título del documento')
    add_parser.add_argument('--archivo', help='Archivo con el contenido (opcional)')
    add_parser.add_argument('--autor', default='Usuario', help='Autor del documento')
    add_parser.add_argument('--etiquetas', help='Etiquetas separadas por comas')
    
    # Comando: list
    list_parser = subparsers.add_parser('list', help='Listar documentos')
    list_parser.add_argument('--categoria', help='Filtrar por categoría')
    list_parser.add_argument('--autor', help='Filtrar por autor')
    list_parser.add_argument('--etiqueta', help='Filtrar por etiqueta')
    
    # Comando: view
    view_parser = subparsers.add_parser('view', help='Ver un documento')
    view_parser.add_argument('--id', required=True, help='ID del documento')
    view_parser.add_argument('--version', help='Versión específica (opcional)')
    
    # Comando: search
    search_parser = subparsers.add_parser('search', help='Buscar documentos')
    search_parser.add_argument('--query', required=True, help='Texto a buscar')
    search_parser.add_argument('--categoria', help='Filtrar por categoría')
    search_parser.add_argument('--etiqueta', help='Filtrar por etiqueta')
    
    # Comando: edit
    edit_parser = subparsers.add_parser('edit', help='Editar un documento')
    edit_parser.add_argument('--id', required=True, help='ID del documento')
    edit_parser.add_argument('--archivo', help='Archivo con nuevo contenido')
    edit_parser.add_argument('--autor', default='Usuario', help='Autor de la modificación')
    edit_parser.add_argument('--cambios', help='Descripción de los cambios')
    
    # Comando: delete
    delete_parser = subparsers.add_parser('delete', help='Eliminar un documento')
    delete_parser.add_argument('--id', required=True, help='ID del documento')
    delete_parser.add_argument('--permanente', action='store_true', help='Eliminar permanentemente')
    
    # Comando: version
    version_parser = subparsers.add_parser('version', help='Gestión de versiones')
    version_subparsers = version_parser.add_subparsers(dest='version_comando')
    
    history_parser = version_subparsers.add_parser('history', help='Ver historial de versiones')
    history_parser.add_argument('--id', required=True, help='ID del documento')
    
    restore_parser = version_subparsers.add_parser('restore', help='Restaurar una versión')
    restore_parser.add_argument('--id', required=True, help='ID del documento')
    restore_parser.add_argument('--version', required=True, help='Versión a restaurar')
    
    args = parser.parse_args()
    
    if not args.comando:
        parser.print_help()
        return
    
    manager = DocumentManager()
    version_ctrl = VersionController()
    
    try:
        if args.comando == 'add':
            # Leer contenido
            if args.archivo:
                contenido = Path(args.archivo).read_text(encoding='utf-8')
            else:
                print("Ingrese el contenido del documento (Ctrl+D o Ctrl+Z para terminar):")
                contenido = sys.stdin.read()
            
            etiquetas = args.etiquetas.split(',') if args.etiquetas else []
            etiquetas = [tag.strip() for tag in etiquetas]
            
            doc = manager.add_document(
                titulo=args.titulo,
                categoria=args.categoria,
                contenido=contenido,
                autor=args.autor,
                etiquetas=etiquetas
            )
            
            print(f"✓ Documento creado: {doc.id}")
            print(f"  Título: {doc.titulo}")
            print(f"  Categoría: {doc.categoria}")
            print(f"  Versión: {doc.version_actual}")
        
        elif args.comando == 'list':
            filtros = {}
            if args.categoria:
                filtros['categoria'] = args.categoria
            if args.autor:
                filtros['autor'] = args.autor
            if args.etiqueta:
                filtros['etiqueta'] = args.etiqueta
            
            documentos = manager.list_documents(filtros)
            
            if not documentos:
                print("No se encontraron documentos.")
            else:
                print(f"\nDocumentos encontrados: {len(documentos)}\n")
                for doc in documentos:
                    estado = "✓" if doc.activo else "✗"
                    print(f"{estado} [{doc.id}] {doc.titulo}")
                    print(f"    Categoría: {doc.categoria} | Autor: {doc.autor} | Versión: {doc.version_actual}")
                    if doc.etiquetas:
                        print(f"    Etiquetas: {', '.join(doc.etiquetas)}")
                    print()
        
        elif args.comando == 'view':
            doc = manager.get_document(args.id)
            
            if args.version:
                version = version_ctrl.get_version(args.id, args.version)
                contenido = version.contenido
                print(f"\n=== {doc.titulo} (Versión {args.version}) ===\n")
            else:
                if doc.ruta:
                    contenido = Path(doc.ruta).read_text(encoding='utf-8')
                else:
                    version = version_ctrl.get_version(args.id, doc.version_actual)
                    contenido = version.contenido
                print(f"\n=== {doc.titulo} (Versión {doc.version_actual}) ===\n")
            
            print(contenido)
            print(f"\n---")
            print(f"Autor: {doc.autor} | Categoría: {doc.categoria}")
        
        elif args.comando == 'search':
            filtros = {}
            if args.categoria:
                filtros['categoria'] = args.categoria
            if args.etiqueta:
                filtros['etiqueta'] = args.etiqueta
            
            resultados = manager.search_documents(args.query, filtros)
            
            if not resultados:
                print(f"No se encontraron documentos con la búsqueda: '{args.query}'")
            else:
                print(f"\nResultados de búsqueda: {len(resultados)}\n")
                for doc in resultados:
                    print(f"  [{doc.id}] {doc.titulo}")
                    print(f"    Categoría: {doc.categoria} | Versión: {doc.version_actual}\n")
        
        elif args.comando == 'edit':
            doc = manager.get_document(args.id)
            
            if args.archivo:
                nuevo_contenido = Path(args.archivo).read_text(encoding='utf-8')
            else:
                # Mostrar contenido actual
                if doc.ruta:
                    contenido_actual = Path(doc.ruta).read_text(encoding='utf-8')
                else:
                    version = version_ctrl.get_version(args.id, doc.version_actual)
                    contenido_actual = version.contenido
                
                print("Contenido actual:")
                print("---")
                print(contenido_actual)
                print("---\n")
                print("Ingrese el nuevo contenido (Ctrl+D o Ctrl+Z para terminar):")
                nuevo_contenido = sys.stdin.read()
            
            doc_actualizado = manager.update_document(
                doc_id=args.id,
                contenido=nuevo_contenido,
                autor=args.autor,
                cambios=args.cambios or "Actualización de documento"
            )
            
            print(f"✓ Documento actualizado: {doc_actualizado.id}")
            print(f"  Nueva versión: {doc_actualizado.version_actual}")
        
        elif args.comando == 'delete':
            manager.delete_document(args.id, permanente=args.permanente)
            tipo = "permanentemente" if args.permanente else "marcado como eliminado"
            print(f"✓ Documento {args.id} {tipo}")
        
        elif args.comando == 'version':
            if args.version_comando == 'history':
                versiones = version_ctrl.list_versions(args.id)
                
                if not versiones:
                    print("No se encontraron versiones para este documento.")
                else:
                    print(f"\nHistorial de versiones para documento {args.id}:\n")
                    for v in versiones:
                        print(f"  Versión {v.numero_version}")
                        print(f"    Fecha: {v.fecha}")
                        print(f"    Autor: {v.autor}")
                        if v.cambios:
                            print(f"    Cambios: {v.cambios}")
                        print()
            
            elif args.version_comando == 'restore':
                nueva_version = version_ctrl.restore_version(args.id, args.version)
                print(f"✓ Versión {args.version} restaurada como versión {nueva_version.numero_version}")
    
    except DocumentNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error inesperado: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
