"""
Visor simple de la base de datos (sin dependencias externas)
"""
import sqlite3
import os

def ver_base_datos():
    db_path = "database/fincafacil.db"
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en: {db_path}")
        print("   La base de datos se creará automáticamente al ejecutar el programa.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("📊 VISOR DE BASE DE DATOS - FINCAFÁCIL")
        print("=" * 70)
        print()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        
        if not tablas:
            print("⚠️  No hay tablas en la base de datos.")
            return
        
        print(f"📋 Tablas encontradas: {len(tablas)}\n")
        
        for tabla in tablas:
            nombre_tabla = tabla[0]
            
            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas = cursor.fetchall()
            
            # Obtener datos
            cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 5")
            datos = cursor.fetchall()
            
            print("-" * 70)
            print(f"📄 TABLA: {nombre_tabla}")
            print("-" * 70)
            
            # Mostrar columnas
            nombres_columnas = [col[1] for col in columnas]
            print(f"Columnas ({len(nombres_columnas)}): {', '.join(nombres_columnas)}")
            print()
            
            # Mostrar datos
            if datos:
                print("Datos (primeros 5 registros):")
                # Encabezados
                print(" | ".join(f"{col:15}" for col in nombres_columnas))
                print("-" * 70)
                # Datos
                for fila in datos:
                    valores = [str(val)[:15] if val is not None else "NULL" for val in fila]
                    print(" | ".join(f"{val:15}" for val in valores))
                
                # Contar total de registros
                cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
                total = cursor.fetchone()[0]
                print(f"\n📊 Total de registros: {total}")
            else:
                print("⚠️  La tabla está vacía.")
            
            print()
        
        conn.close()
        print("=" * 70)
        print("✅ Visualización completada")
        print("=" * 70)
        print(f"\n📍 Ubicación de la BD: {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"❌ Error al acceder a la base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ver_base_datos()
    input("\nPresiona Enter para salir...")

