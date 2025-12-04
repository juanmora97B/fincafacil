"""
Script para eliminar todos los animales de la base de datos
ADVERTENCIA: Esta operación no se puede deshacer
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from database import db


def eliminar_todos_animales():
    """
    Elimina todos los registros de la tabla animal
    """
    print("=" * 80)
    print("⚠️  ADVERTENCIA: ELIMINACIÓN DE TODOS LOS ANIMALES")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Contar animales actuales
            cursor.execute("SELECT COUNT(*) FROM animal")
            total_animales = cursor.fetchone()[0]
            
            if total_animales == 0:
                print("\n✓ No hay animales en la base de datos")
                return True
            
            print(f"\n📊 Total de animales en la base de datos: {total_animales}")
            
            # Mostrar resumen por estado
            cursor.execute("""
                SELECT estado, COUNT(*) 
                FROM animal 
                GROUP BY estado
            """)
            print("\nDistribución por estado:")
            for estado, count in cursor.fetchall():
                print(f"   - {estado}: {count}")
            
            # Mostrar resumen por finca
            cursor.execute("""
                SELECT f.nombre, COUNT(a.id)
                FROM animal a
                LEFT JOIN finca f ON a.id_finca = f.id
                GROUP BY a.id_finca
            """)
            print("\nDistribución por finca:")
            for nombre_finca, count in cursor.fetchall():
                finca_str = nombre_finca if nombre_finca else "Sin finca"
                print(f"   - {finca_str}: {count}")
            
            # Solicitar confirmación
            print("\n" + "=" * 80)
            print("⚠️  ESTA OPERACIÓN ELIMINARÁ TODOS LOS ANIMALES PERMANENTEMENTE")
            print("=" * 80)
            respuesta = input("\n¿Está seguro que desea continuar? Escriba 'ELIMINAR' para confirmar: ")
            
            if respuesta != "ELIMINAR":
                print("\n❌ Operación cancelada por el usuario")
                return False
            
            print("\n🔄 Eliminando animales...")
            
            # Primero, eliminar registros relacionados en otras tablas
            # (si existen foreign keys que lo requieran)
            
            # Eliminar comentarios de animales
            try:
                cursor.execute("DELETE FROM comentario_animal")
                comentarios_eliminados = cursor.rowcount
                print(f"   ✓ Eliminados {comentarios_eliminados} comentarios")
            except Exception as e:
                print(f"   ⚠ No se pudieron eliminar comentarios: {e}")
            
            # Eliminar pesos de animales
            try:
                cursor.execute("DELETE FROM peso_animal")
                pesos_eliminados = cursor.rowcount
                print(f"   ✓ Eliminados {pesos_eliminados} registros de peso")
            except Exception as e:
                print(f"   ⚠ No se pudieron eliminar pesos: {e}")
            
            # Eliminar tratamientos de animales
            try:
                cursor.execute("DELETE FROM tratamiento_animal")
                tratamientos_eliminados = cursor.rowcount
                print(f"   ✓ Eliminados {tratamientos_eliminados} tratamientos")
            except Exception as e:
                print(f"   ⚠ No se pudieron eliminar tratamientos: {e}")
            
            # Eliminar reubicaciones
            try:
                cursor.execute("DELETE FROM reubicacion")
                reubicaciones_eliminadas = cursor.rowcount
                print(f"   ✓ Eliminadas {reubicaciones_eliminadas} reubicaciones")
            except Exception as e:
                print(f"   ⚠ No se pudieron eliminar reubicaciones: {e}")
            
            # Finalmente, eliminar todos los animales
            cursor.execute("DELETE FROM animal")
            animales_eliminados = cursor.rowcount
            
            conn.commit()
            
            print(f"\n✅ Se eliminaron {animales_eliminados} animales correctamente")
            
            # Verificar que la tabla esté vacía
            cursor.execute("SELECT COUNT(*) FROM animal")
            animales_restantes = cursor.fetchone()[0]
            
            if animales_restantes == 0:
                print("✅ La tabla 'animal' está completamente vacía")
                
                # Resetear el autoincremento (opcional)
                try:
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='animal'")
                    conn.commit()
                    print("✅ Contador de ID reseteado")
                except Exception as e:
                    print(f"⚠ No se pudo resetear el contador de ID: {e}")
                
                return True
            else:
                print(f"⚠ Advertencia: Aún quedan {animales_restantes} animales")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def mostrar_estado_actual():
    """
    Muestra el estado actual de la tabla animal
    """
    print("\n" + "=" * 80)
    print("📊 ESTADO ACTUAL DE LA BASE DE DATOS")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total de animales
            cursor.execute("SELECT COUNT(*) FROM animal")
            total = cursor.fetchone()[0]
            
            print(f"\n✓ Total de animales: {total}")
            
            if total > 0:
                # Por estado
                cursor.execute("""
                    SELECT estado, COUNT(*) 
                    FROM animal 
                    GROUP BY estado
                """)
                print("\nPor estado:")
                for estado, count in cursor.fetchall():
                    print(f"   - {estado}: {count}")
                
                # Por finca
                cursor.execute("""
                    SELECT 
                        COALESCE(f.nombre, 'Sin finca') as finca,
                        COUNT(a.id) as total
                    FROM animal a
                    LEFT JOIN finca f ON a.id_finca = f.id
                    GROUP BY a.id_finca
                """)
                print("\nPor finca:")
                for finca, count in cursor.fetchall():
                    print(f"   - {finca}: {count}")
            else:
                print("\n✅ No hay animales en la base de datos")
                print("   La tabla está lista para una nueva importación")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    print("\n🗑️  SCRIPT DE LIMPIEZA DE ANIMALES\n")
    
    # Mostrar estado actual
    mostrar_estado_actual()
    
    # Eliminar animales
    print("\n")
    if eliminar_todos_animales():
        # Mostrar estado después de eliminar
        mostrar_estado_actual()
        
        print("\n" + "=" * 80)
        print("✅ BASE DE DATOS LIMPIA")
        print("=" * 80)
        print("\nAhora puedes:")
        print("1. Abrir FincaFácil")
        print("2. Ir al módulo de Animales")
        print("3. Importar el archivo Excel")
        print("4. Verificar que los animales se cargan con la finca correcta")
        print("\n💡 Recuerda: El sistema ahora es case-insensitive")
        print("   Puedes escribir 'FINCA EL PRADO', 'finca el prado' o 'Finca El Prado'")
        print("   ¡Y siempre encontrará la finca correcta! ✨")
        print("\n")
    else:
        print("\n❌ La limpieza no se completó correctamente")
        print("   Revisa los errores arriba")
