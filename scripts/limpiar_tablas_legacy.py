"""
Script de limpieza: eliminar tablas legacy residuales y asegurar esquema limpio
Ejecutar después de verificar que la tabla 'animal' principal tiene todos los datos
"""
import sqlite3
from pathlib import Path

def limpiar_tablas_legacy():
    """Elimina tablas legacy y asegura que no haya referencias rotas"""
    db_path = Path("database/fincafacil.db")
    if not db_path.exists():
        print("❌ No se encuentra la base de datos")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        print("🔧 Iniciando limpieza de tablas legacy...")
        
        # 1. Verificar que tabla animal principal existe y tiene datos
        cur.execute("SELECT COUNT(*) FROM animal")
        count = cur.fetchone()[0]
        print(f"✓ Tabla 'animal' principal tiene {count} registros")
        
        if count == 0:
            print("⚠️ ADVERTENCIA: La tabla animal está vacía. No se eliminará nada por seguridad.")
            return False
        
        # 2. Eliminar tablas legacy si existen
        legacy_tables = ['animal_legacy', 'animal_legacy_temp']
        
        for table in legacy_tables:
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cur.fetchone():
                print(f"\n🗑️ Eliminando tabla '{table}'...")
                cur.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"   ✓ Tabla '{table}' eliminada")
            else:
                print(f"   ℹ️ Tabla '{table}' no existe (ya limpia)")
        
        # 3. Verificar que no queden triggers que referencien legacy
        cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND sql LIKE '%legacy%'")
        triggers = cur.fetchall()
        if triggers:
            print("\n🗑️ Eliminando triggers con referencias legacy...")
            for (trigger_name,) in triggers:
                cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                print(f"   ✓ Trigger '{trigger_name}' eliminado")
        else:
            print("\n✓ No hay triggers con referencias legacy")
        
        # 4. Confirmar cambios
        conn.commit()
        print("\n✅ Limpieza completada exitosamente")
        print("\n📊 Estado final:")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%legacy%'")
        remaining = cur.fetchall()
        if remaining:
            print("⚠️ Tablas legacy restantes:")
            for (name,) in remaining:
                print(f"   - {name}")
        else:
            print("✓ No quedan tablas legacy")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("LIMPIEZA DE TABLAS LEGACY - FincaFácil")
    print("=" * 80)
    print("\nEste script eliminará las tablas animal_legacy y animal_legacy_temp")
    print("residuales que causan errores de FOREIGN KEY.\n")
    
    respuesta = input("¿Desea continuar? (s/n): ").lower()
    if respuesta == 's':
        if limpiar_tablas_legacy():
            print("\n✅ Limpieza exitosa. Puede cerrar esta ventana.")
        else:
            print("\n⚠️ Limpieza no completada. Revise los mensajes anteriores.")
    else:
        print("\n❌ Operación cancelada por el usuario.")
    
    input("\nPresione Enter para salir...")
