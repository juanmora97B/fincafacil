"""
Script simple para ver el contenido de la base de datos
Ejecuta: python ver_base_datos.py
"""
import sqlite3
import os

def ver_base_datos():
    db_path = "database/fincafacil.db"
    
    if not os.path.exists(db_path):
        print("❌ La base de datos no existe aún.")
        print("   Ejecuta la aplicación primero para crearla.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 70)
        print("📊 BASE DE DATOS FINCAFACIL")
        print("=" * 70)
        print()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas = cursor.fetchall()
        
        print(f"📋 Tablas encontradas: {len(tablas)}")
        print()
        
        for tabla in tablas:
            nombre_tabla = tabla[0]
            print("-" * 70)
            print(f"📄 Tabla: {nombre_tabla}")
            print("-" * 70)
            
            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({nombre_tabla})")
            columnas = cursor.fetchall()
            
            print("Columnas:")
            for col in columnas:
                print(f"  • {col[1]} ({col[2]})")
            print()
            
            # Obtener datos (limitado a 10 registros)
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            total = cursor.fetchone()[0]
            
            if total > 0:
                cursor.execute(f"SELECT * FROM {nombre_tabla} LIMIT 10")
                datos = cursor.fetchall()
                
                # Obtener nombres de columnas
                nombres_columnas = [col[1] for col in columnas]
                
                print(f"Registros (mostrando {min(10, total)} de {total}):")
                # Mostrar de forma simple
                print(" | ".join(nombres_columnas))
                print("-" * 70)
                for fila in datos:
                    valores = []
                    for val in fila:
                        if val is None:
                            valores.append("NULL")
                        elif isinstance(val, str) and len(val) > 30:
                            valores.append(val[:27] + "...")
                        else:
                            valores.append(str(val))
                    print(" | ".join(valores))
            else:
                print("Sin registros")
            
            print()
            print()
        
        conn.close()
        print("=" * 70)
        print("✅ Visualización completada")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ver_base_datos()
    input("\nPresiona Enter para salir...")
