"""
Script para actualizar las referencias a tablas en los módulos del sistema.
"""
import os
import re
from pathlib import Path

def update_sql_references(file_path):
    """Actualiza las referencias SQL en un archivo"""
    backup_path = str(file_path) + '.bak'
    content = None
    updated_content = None
    
    try:
        # Leer archivo original
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            updated_content = content
        
        # Crear backup del archivo
        with open(backup_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        # Mapeo de nombres antiguos a nuevos
        table_mapping = {
            'fincas': 'finca',
            'sectores': 'sector',
            'potreros': 'potrero',
            'lotes': 'lote',
            'grupos': 'grupo',
            'razas': 'raza',
            'animales': 'animal',
            'vendedores': 'vendedor',
            'pesos': 'peso',
            'tratamientos': 'tratamiento',
            'reubicaciones': 'reubicacion',
            'comentarios': 'comentario',
            'diagnosticos_veterinarios': 'diagnostico_veterinario',
            'condiciones_corporales': 'condicion_corporal',
            'tipos_explotacion': 'tipo_explotacion',
            'procedencias': 'procedencia',
            'destinos_ventas': 'destino_venta',
            'destinos_venta': 'destino_venta',
            'motivos_venta': 'motivo_venta',
            'causas_muerte': 'causa_muerte',
            'proveedores': 'proveedor',
            'empleados': 'empleado',
            'ventas': 'venta'
        }
        
        # Reemplazar nombres de tablas en consultas SQL
        for old_name, new_name in table_mapping.items():
            # Patrones comunes en consultas SQL
            patterns = [
                (f'FROM {old_name}\\b', f'FROM {new_name}'),
                (f'INTO {old_name}\\b', f'INTO {new_name}'),
                (f'UPDATE {old_name}\\b', f'UPDATE {new_name}'),
                (f'JOIN {old_name}\\b', f'JOIN {new_name}'),
                (f'TABLE {old_name}\\b', f'TABLE {new_name}')
            ]
            
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Guardar los cambios solo si hubo modificaciones
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Archivo actualizado: {file_path}")
        else:
            print(f"No se requirieron cambios en: {file_path}")
            
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        # Intentar restaurar desde el backup si existe
        if os.path.exists(backup_path):
            try:
                os.replace(backup_path, file_path)
                print(f"Archivo restaurado desde backup: {file_path}")
            except Exception as restore_error:
                print(f"Error al restaurar backup: {restore_error}")
    finally:
        # Limpiar archivo de backup si existe
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except Exception as cleanup_error:
                print(f"Error al eliminar backup: {cleanup_error}")
            except Exception as restore_error:
                print(f"Error al restaurar backup: {restore_error}")
        raise  # Re-lanzar la excepción original

def process_directory(directory):
    """Procesa todos los archivos Python en un directorio recursivamente"""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Procesando: {file_path}")
                try:
                    update_sql_references(file_path)
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")

def main():
    # Directorios a procesar
    directories = [
        'modules',
        'database'
    ]
    
    print("Actualizando referencias a tablas en el código...")
    for directory in directories:
        process_directory(directory)
    print("Actualización completada.")

if __name__ == "__main__":
    main()