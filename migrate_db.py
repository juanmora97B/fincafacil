"""
Script principal para ejecutar la migración completa de la base de datos.
"""
import os
import sys
import time
import shutil
from pathlib import Path
from database.migrate_db import migrate_database
from database.update_references_new import main as update_references

def create_backup():
    """Crea un backup de la base de datos y archivos importantes"""
    db_path = Path("database/fincafacil.db")
    if not db_path.exists():
        print("❌ No se encontró la base de datos.")
        return False
    
    backup_dir = Path("backup")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_db = backup_dir / f"fincafacil_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_db)
        print(f"✅ Backup creado en: {backup_db}")
        return True
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False

def main():
    print("=" * 50)
    print("🔄 MIGRACIÓN DE BASE DE DATOS FINCAFACIL")
    print("=" * 50)
    print("\n📋 Este proceso realizará las siguientes acciones:")
    print("1. Crear un backup de la base de datos actual")
    print("2. Migrar las tablas al nuevo esquema")
    print("3. Actualizar las referencias en el código")
    print("\n⚠️ IMPORTANTE: Este proceso modificará la estructura de la base de datos.")
    print("   Se creará un backup automáticamente, pero se recomienda hacer")
    print("   una copia manual adicional si los datos son críticos.")
    
    response = input("\n❓ ¿Desea continuar? (s/n): ")
    if response.lower() != 's':
        print("\n❌ Migración cancelada por el usuario.")
        return 1
        
    if not create_backup():
        print("\n❌ No se pudo crear el backup. Migración cancelada.")
        return 1
    
    print("\n🚀 Iniciando proceso de migración...\n")
    
    try:
        # Paso 1: Migrar la base de datos
        print("📦 [Paso 1/2] Migrando base de datos...")
        migrate_database()
        print("✅ Base de datos migrada exitosamente\n")
        
        # Paso 2: Actualizar referencias en el código
        print("📝 [Paso 2/2] Actualizando referencias en el código...")
        if update_references() != 0:
            raise Exception("Error al actualizar las referencias en el código")
        print("✅ Referencias actualizadas exitosamente\n")
        
        print("🎉 ¡Migración completada exitosamente!")
        print("\n📋 Recomendaciones:")
        print("1. Revise la aplicación para verificar su funcionamiento")
        print("2. Si encuentra algún problema, puede restaurar el backup desde")
        print(f"   la carpeta: {os.path.abspath('backup')}")
        print("\n💡 Próximos pasos sugeridos:")
        print("1. Ejecute la aplicación y verifique que todo funcione correctamente")
        print("2. Realice pruebas en los módulos principales")
        print("3. Verifique que los datos existentes sean accesibles")
        
        return 0
        
    except Exception as e:
        print("\n❌ ¡ERROR DURANTE LA MIGRACIÓN!")
        print(f"⚠️  Error: {e}")
        print("\n🔄 Para restaurar desde el backup:")
        print(f"1. Localice el backup más reciente en: {os.path.abspath('backup')}")
        print("2. Copie el archivo .db a la carpeta database/")
        print("3. Renómbrelo a 'fincafacil.db'")
        return 1

if __name__ == "__main__":
    sys.exit(main())