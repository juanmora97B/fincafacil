"""
Script para actualizar las referencias a tablas en los módulos del sistema.
"""
import os
import re
from pathlib import Path

def update_sql_references(file_path):
    """Actualiza las referencias SQL en un archivo"""
    backup_path = str(file_path) + '.bak'
    
    try:
        # Leer archivo original
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
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
        
        # Hacer una copia del contenido original para detectar cambios
        updated_content = content
        
        # Reemplazar nombres de tablas en consultas SQL
        for old_name, new_name in table_mapping.items():
            # Patrones comunes en consultas SQL
            patterns = [
                (f'FROM {old_name}\\b', f'FROM {new_name}'),
                (f'INTO {old_name}\\b', f'INTO {new_name}'),
                (f'UPDATE {old_name}\\b', f'UPDATE {new_name}'),
                (f'JOIN {old_name}\\b', f'JOIN {new_name}'),
                (f'TABLE {old_name}\\b', f'TABLE {new_name}'),
                (f'CREATE TABLE IF NOT EXISTS {old_name}\\b', f'CREATE TABLE IF NOT EXISTS {new_name}')
            ]
            
            for pattern, replacement in patterns:
                updated_content = re.sub(pattern, replacement, updated_content, flags=re.IGNORECASE)
        
        # Guardar los cambios solo si hubo modificaciones
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print(f"✅ Archivo actualizado: {file_path}")
        else:
            print(f"ℹ️ No se requirieron cambios en: {file_path}")
            
        # Eliminar el backup si todo salió bien
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        # Intentar restaurar desde el backup si existe
        if os.path.exists(backup_path):
            try:
                os.replace(backup_path, file_path)
                print(f"🔄 Archivo restaurado desde backup: {file_path}")
            except Exception as restore_error:
                print(f"⚠️ Error al restaurar backup: {restore_error}")
        return False
    
    return True

def process_directory(directory):
    """Procesa todos los archivos Python en un directorio recursivamente"""
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"❌ Directorio no encontrado: {directory}")
        return False
        
    success = True
    for file_path in directory_path.rglob('*.py'):
        if file_path.name != 'update_references.py':
            print(f"\n📝 Procesando: {file_path}")
            try:
                if not update_sql_references(file_path):
                    success = False
            except Exception as e:
                print(f"❌ Error en archivo {file_path}: {e}")
                success = False
    
    return success

def main():
    # Directorios a procesar
    directories = [
        'modules',
        'database'
    ]
    
    print("\n🔄 Actualizando referencias a tablas en el código...")
    all_success = True
    
    for directory in directories:
        print(f"\n📁 Procesando directorio: {directory}")
        if not process_directory(directory):
            all_success = False
    
    if all_success:
        print("\n✅ Actualización completada exitosamente.")
    else:
        print("\n⚠️ Actualización completada con errores. Revise los mensajes anteriores.")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())