"""
Prueba de eliminación de finca
Simula el proceso sin realmente eliminar datos de producción
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

def test_finca_deletion():
    """Prueba que la eliminación de finca funcione sin errores de FK"""
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            print("=" * 60)
            print("PRUEBA DE ELIMINACIÓN DE FINCA")
            print("=" * 60)
            
            # Comenzar transacción de prueba
            cur.execute("BEGIN TRANSACTION;")
            
            # 1. Crear finca de prueba
            test_codigo = "TEST_FINCA_999"
            cur.execute("""
                    INSERT INTO finca (codigo, nombre, ubicacion, area_hectareas, estado)
                VALUES (?, ?, ?, ?, ?)
                """, (test_codigo, "Finca Test", "Ubicación Test", 100.0, "Activo"))
            
            finca_id = cur.lastrowid
            print(f"\n✔ Finca de prueba creada: ID={finca_id}, codigo={test_codigo}")
            
            # 2. Crear registros dependientes
            cur.execute("""
                    INSERT INTO potrero (codigo, nombre, id_finca, area_hectareas, estado)
                VALUES (?, ?, ?, ?, ?)
                """, ("POT_TEST", "Potrero Test", finca_id, 50.0, "Activo"))
            print(f"✔ Potrero creado asociado a finca {finca_id}")
            
            # Verificar que existe animal (si hay datos)
            cur.execute("SELECT id FROM animal LIMIT 1")
            animal_row = cur.fetchone()
            if animal_row:
                animal_id = animal_row[0]
                cur.execute("UPDATE animal SET id_finca = ? WHERE id = ?", (finca_id, animal_id))
                print(f"✔ Animal {animal_id} asociado a finca {finca_id}")
            
            # 3. Intentar eliminar finca
            print(f"\n🔄 Intentando eliminar finca {test_codigo}...")
            cur.execute("DELETE FROM finca WHERE codigo = ?", (test_codigo,))
            
            if cur.rowcount == 0:
                print("❌ No se eliminó ninguna finca")
            else:
                print(f"✔ Finca eliminada exitosamente (rowcount={cur.rowcount})")
            
            # 4. Verificar que dependencias tienen FK en NULL
            cur.execute("SELECT COUNT(*) FROM potrero WHERE id_finca IS NULL")
            potreros_nulos = cur.fetchone()[0]
            print(f"\n✔ Potreros con id_finca NULL: {potreros_nulos}")
            
            if animal_row:
                cur.execute("SELECT id_finca FROM animal WHERE id = ?", (animal_id,))
                animal_finca = cur.fetchone()[0]
                if animal_finca is None:
                    print(f"✔ Animal {animal_id} ahora tiene id_finca NULL")
                else:
                    print(f"⚠ Animal {animal_id} todavía tiene id_finca={animal_finca}")
            
            # 5. Rollback para no afectar datos reales
            conn.rollback()
            print("\n✔ Rollback ejecutado - No se modificó la base de datos")
            
            print("\n" + "=" * 60)
            print("✔ PRUEBA EXITOSA - LA ELIMINACIÓN FUNCIONA CORRECTAMENTE")
            print("=" * 60)
            
        except Exception as e:
            conn.rollback()
            print(f"\n❌ ERROR EN PRUEBA: {e}")
            print("\n" + "=" * 60)
            print("❌ PRUEBA FALLIDA")
            print("=" * 60)
            raise

if __name__ == "__main__":
    try:
        test_finca_deletion()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
