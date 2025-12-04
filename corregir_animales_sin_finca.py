"""
Script para corregir animales sin finca asignada
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(__file__))
from database import db
from tkinter import messagebox

def corregir_animales_sin_finca():
    """
    Asigna una finca por defecto a todos los animales que no tienen finca asignada
    """
    print("=" * 80)
    print("CORRECCIÓN: Asignar finca a animales sin finca")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Verificar animales sin finca
            cursor.execute("""
                SELECT COUNT(*) FROM animal WHERE id_finca IS NULL AND estado = 'Activo'
            """)
            total_sin_finca = cursor.fetchone()[0]
            
            if total_sin_finca == 0:
                print("\n✓ No hay animales sin finca asignada")
                return True
            
            print(f"\n⚠ Se encontraron {total_sin_finca} animales sin finca asignada")
            
            # 2. Obtener la finca por defecto o la primera finca activa
            cursor.execute("""
                SELECT id, nombre FROM finca 
                WHERE estado IN ('Activa', 'Activo')
                ORDER BY id 
                LIMIT 1
            """)
            finca = cursor.fetchone()
            
            if not finca:
                print("\n❌ ERROR: No hay fincas activas en el sistema")
                print("   Por favor, cree al menos una finca activa antes de continuar")
                return False
            
            id_finca, nombre_finca = finca
            print(f"\n✓ Finca seleccionada: {nombre_finca} (ID: {id_finca})")
            
            # 3. Mostrar animales que se van a actualizar
            cursor.execute("""
                SELECT codigo, nombre, tipo_ingreso, sexo
                FROM animal 
                WHERE id_finca IS NULL AND estado = 'Activo'
                ORDER BY codigo
                LIMIT 20
            """)
            animales = cursor.fetchall()
            
            print(f"\nAnimales que se actualizarán (mostrando primeros 20 de {total_sin_finca}):")
            print("Código    | Nombre           | Tipo      | Sexo")
            print("-" * 60)
            for codigo, nombre, tipo_ing, sexo in animales:
                nombre = nombre or "Sin nombre"
                tipo_ing = tipo_ing or "N/A"
                sexo = sexo or "N/A"
                print(f"{codigo:10} | {nombre:16} | {tipo_ing:9} | {sexo}")
            
            # 4. Solicitar confirmación
            respuesta = input(f"\n¿Asignar la finca '{nombre_finca}' a estos {total_sin_finca} animales? (s/n): ")
            
            if respuesta.lower() != 's':
                print("\n⚠ Operación cancelada por el usuario")
                return False
            
            # 5. Actualizar animales
            cursor.execute("""
                UPDATE animal 
                SET id_finca = ?
                WHERE id_finca IS NULL AND estado = 'Activo'
            """, (id_finca,))
            
            conn.commit()
            
            print(f"\n✅ Se actualizaron {cursor.rowcount} animales")
            print(f"   Todos los animales ahora están asignados a la finca '{nombre_finca}'")
            
            # 6. Verificar resultado
            cursor.execute("""
                SELECT COUNT(*) FROM animal WHERE id_finca IS NULL AND estado = 'Activo'
            """)
            restantes = cursor.fetchone()[0]
            
            if restantes == 0:
                print("\n✓ ÉXITO: Todos los animales activos ahora tienen finca asignada")
                return True
            else:
                print(f"\n⚠ ADVERTENCIA: Aún quedan {restantes} animales sin finca")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def eliminar_duplicados_codigo():
    """
    Identifica y elimina (o marca como inactivos) los registros duplicados por código
    Mantiene solo el más reciente de cada código
    """
    print("\n" + "=" * 80)
    print("CORRECCIÓN: Eliminar códigos duplicados")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Buscar códigos duplicados
            cursor.execute("""
                SELECT codigo, COUNT(*) as total
                FROM animal
                WHERE estado = 'Activo'
                GROUP BY codigo
                HAVING COUNT(*) > 1
            """)
            duplicados = cursor.fetchall()
            
            if not duplicados:
                print("\n✓ No hay códigos duplicados")
                return True
            
            print(f"\n⚠ Se encontraron {len(duplicados)} códigos duplicados:")
            for codigo, total in duplicados[:10]:
                print(f"   - {codigo}: {total} registros")
            
            if len(duplicados) > 10:
                print(f"   ... y {len(duplicados) - 10} más")
            
            # 2. Solicitar confirmación
            respuesta = input(f"\n¿Marcar como 'Eliminado' los registros duplicados más antiguos? (s/n): ")
            
            if respuesta.lower() != 's':
                print("\n⚠ Operación cancelada por el usuario")
                return False
            
            # 3. Para cada código duplicado, mantener solo el más reciente
            total_eliminados = 0
            for codigo, _ in duplicados:
                # Marcar como eliminados todos excepto el más reciente
                cursor.execute("""
                    UPDATE animal
                    SET estado = 'Eliminado'
                    WHERE codigo = ?
                    AND id NOT IN (
                        SELECT id FROM animal
                        WHERE codigo = ?
                        ORDER BY fecha_registro DESC
                        LIMIT 1
                    )
                    AND estado = 'Activo'
                """, (codigo, codigo))
                
                total_eliminados += cursor.rowcount
            
            conn.commit()
            
            print(f"\n✅ Se marcaron como 'Eliminado' {total_eliminados} registros duplicados")
            print("   Se mantuvo el registro más reciente de cada código")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔧 INICIANDO CORRECCIÓN DE DATOS\n")
    
    # Primero eliminar duplicados
    if eliminar_duplicados_codigo():
        # Luego asignar fincas
        if corregir_animales_sin_finca():
            print("\n" + "=" * 80)
            print("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print("\nAhora puede:")
            print("1. Abrir el módulo de Animales")
            print("2. Ir a la pestaña 'Inventario General'")
            print("3. Seleccionar la finca en el combobox")
            print("4. Ver todos los animales listados correctamente")
            print("\n")
        else:
            print("\n⚠ La corrección de fincas no se completó correctamente")
    else:
        print("\n⚠ La eliminación de duplicados no se completó correctamente")
