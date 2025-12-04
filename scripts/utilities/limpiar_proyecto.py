"""
Script de Limpieza Automatizada para FincaFacil
Elimina archivos temporales, caches y optimiza el proyecto
"""
import os
import shutil
from pathlib import Path

def limpiar_pycache(base_dir):
    """Elimina recursivamente todos los directorios __pycache__"""
    count = 0
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                count += 1
                print(f"✓ Eliminado: {pycache_path}")
            except Exception as e:
                print(f"✗ Error eliminando {pycache_path}: {e}")
    return count

def limpiar_pytest_cache(base_dir):
    """Elimina recursivamente todos los directorios .pytest_cache"""
    count = 0
    for root, dirs, files in os.walk(base_dir):
        if '.pytest_cache' in dirs:
            pytest_path = os.path.join(root, '.pytest_cache')
            try:
                shutil.rmtree(pytest_path)
                count += 1
                print(f"✓ Eliminado: {pytest_path}")
            except Exception as e:
                print(f"✗ Error eliminando {pytest_path}: {e}")
    return count

def limpiar_logs_antiguos(logs_dir, dias=30):
    """Elimina logs más antiguos de X días"""
    import time
    from datetime import datetime, timedelta
    
    if not os.path.exists(logs_dir):
        return 0
    
    count = 0
    limite = time.time() - (dias * 86400)  # días a segundos
    
    for archivo in os.listdir(logs_dir):
        filepath = os.path.join(logs_dir, archivo)
        if os.path.isfile(filepath) and archivo.endswith('.log'):
            if os.path.getmtime(filepath) < limite:
                try:
                    os.remove(filepath)
                    count += 1
                    print(f"✓ Log antiguo eliminado: {archivo}")
                except Exception as e:
                    print(f"✗ Error eliminando {archivo}: {e}")
    return count

def limpiar_builds_antiguos(base_dir):
    """Limpia directorios build y dist antiguos"""
    dirs_to_clean = ['build', 'dist']
    count = 0
    
    for dirname in dirs_to_clean:
        dirpath = os.path.join(base_dir, dirname)
        if os.path.exists(dirpath):
            try:
                # Solo mostrar contenido, no eliminar automáticamente
                size = sum(
                    os.path.getsize(os.path.join(dirpath, f))
                    for f in os.listdir(dirpath)
                    if os.path.isfile(os.path.join(dirpath, f))
                )
                size_mb = size / (1024 * 1024)
                print(f"ℹ {dirname}/ ocupa {size_mb:.2f} MB")
                
                respuesta = input(f"  ¿Desea limpiar {dirname}/? (s/n): ")
                if respuesta.lower() == 's':
                    shutil.rmtree(dirpath)
                    os.makedirs(dirpath)
                    count += 1
                    print(f"✓ {dirname}/ limpiado")
            except Exception as e:
                print(f"✗ Error con {dirname}/: {e}")
    return count

def main():
    """Ejecuta limpieza completa del proyecto"""
    print("=" * 60)
    print("🧹 LIMPIEZA AUTOMATIZADA - FINCAFACIL")
    print("=" * 60)
    
    # Obtener directorio base
    base_dir = Path(__file__).parent.parent.parent
    print(f"\n📁 Directorio base: {base_dir}\n")
    
    # Limpieza de caches Python
    print("🗑️  Limpiando caches Python...")
    pycache_count = limpiar_pycache(base_dir)
    print(f"   Total: {pycache_count} directorios __pycache__ eliminados\n")
    
    # Limpieza de cache pytest
    print("🗑️  Limpiando caches pytest...")
    pytest_count = limpiar_pytest_cache(base_dir)
    print(f"   Total: {pytest_count} directorios .pytest_cache eliminados\n")
    
    # Limpieza de logs antiguos
    print("📋 Limpiando logs antiguos (>30 días)...")
    logs_dir = os.path.join(base_dir, 'logs')
    logs_count = limpiar_logs_antiguos(logs_dir, dias=30)
    print(f"   Total: {logs_count} logs antiguos eliminados\n")
    
    # Revisión de builds (no automático)
    print("📦 Revisando directorios de build...")
    build_count = limpiar_builds_antiguos(base_dir)
    print(f"   Total: {build_count} directorios limpiados\n")
    
    # Resumen
    print("=" * 60)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 60)
    print(f"Total de elementos limpiados: {pycache_count + pytest_count + logs_count + build_count}")
    print("\n💡 Recomendación: Ejecutar este script mensualmente")
    print("=" * 60)

if __name__ == "__main__":
    main()
