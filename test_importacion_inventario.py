"""
Test para validar la importación de animales desde Excel y su visualización en el inventario
"""
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from database import db

def validar_animales_importados():
    """
    Valida que los animales importados aparezcan correctamente en la base de datos
    y que tengan los campos necesarios para mostrarse en el inventario
    """
    print("=" * 80)
    print("TEST: Validación de Importación de Animales")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Verificar animales activos
            print("\n1. Verificando animales activos...")
            cursor.execute("""
                SELECT COUNT(*) FROM animal WHERE estado = 'Activo'
            """)
            total_activos = cursor.fetchone()[0]
            print(f"   ✓ Total animales activos: {total_activos}")
            
            # 2. Verificar animales sin finca asignada
            print("\n2. Verificando animales sin finca asignada...")
            cursor.execute("""
                SELECT COUNT(*) FROM animal WHERE estado = 'Activo' AND id_finca IS NULL
            """)
            sin_finca = cursor.fetchone()[0]
            if sin_finca > 0:
                print(f"   ⚠ ADVERTENCIA: {sin_finca} animales activos sin finca asignada")
                print("   Estos animales NO aparecerán en el inventario")
            else:
                print(f"   ✓ Todos los animales tienen finca asignada")
            
            # 3. Verificar últimos animales importados (últimas 24 horas)
            print("\n3. Verificando animales importados recientemente...")
            cursor.execute("""
                SELECT 
                    codigo, 
                    nombre, 
                    tipo_ingreso, 
                    sexo, 
                    estado, 
                    inventariado,
                    id_finca,
                    fecha_registro
                FROM animal 
                WHERE date(fecha_registro) = date('now')
                ORDER BY fecha_registro DESC
                LIMIT 10
            """)
            recientes = cursor.fetchall()
            
            if recientes:
                print(f"   ✓ Encontrados {len(recientes)} animales importados hoy:")
                print("\n   Código    | Nombre           | Tipo      | Sexo   | Estado | Inv | Finca | Fecha")
                print("   " + "-" * 90)
                for animal in recientes:
                    codigo, nombre, tipo_ing, sexo, estado, inv, finca, fecha = animal
                    nombre = nombre or "Sin nombre"
                    inv_txt = "Sí" if inv == 1 else "No"
                    finca_txt = str(finca) if finca else "Sin finca"
                    print(f"   {codigo:10} | {nombre:16} | {tipo_ing:9} | {sexo:6} | {estado:6} | {inv_txt:3} | {finca_txt:5} | {fecha}")
            else:
                print("   ⚠ No se encontraron animales importados hoy")
            
            # 4. Verificar códigos duplicados
            print("\n4. Verificando códigos duplicados...")
            cursor.execute("""
                SELECT codigo, COUNT(*) as total
                FROM animal
                GROUP BY codigo
                HAVING COUNT(*) > 1
            """)
            duplicados = cursor.fetchall()
            
            if duplicados:
                print(f"   ⚠ ADVERTENCIA: {len(duplicados)} códigos duplicados encontrados:")
                for codigo, total in duplicados[:5]:
                    print(f"      - {codigo}: {total} registros")
            else:
                print("   ✓ No hay códigos duplicados")
            
            # 5. Verificar animales por finca
            print("\n5. Verificando distribución por finca...")
            cursor.execute("""
                SELECT f.nombre, COUNT(a.id) as total
                FROM finca f
                LEFT JOIN animal a ON f.id = a.id_finca AND a.estado = 'Activo'
                WHERE f.estado IN ('Activa', 'Activo')
                GROUP BY f.id, f.nombre
                ORDER BY total DESC
            """)
            por_finca = cursor.fetchall()
            
            if por_finca:
                print("   Finca                          | Total Animales")
                print("   " + "-" * 50)
                for finca, total in por_finca:
                    print(f"   {finca:30} | {total:5}")
            else:
                print("   ⚠ No hay fincas activas")
            
            # 6. Verificar animales con problemas para mostrarse en inventario
            print("\n6. Verificando animales con posibles problemas de visualización...")
            cursor.execute("""
                SELECT 
                    codigo,
                    CASE 
                        WHEN id_finca IS NULL THEN 'Sin finca asignada'
                        WHEN estado != 'Activo' THEN 'Estado no activo: ' || estado
                        ELSE 'OK'
                    END as problema
                FROM animal
                WHERE id_finca IS NULL OR estado != 'Activo'
                LIMIT 10
            """)
            problemas = cursor.fetchall()
            
            if problemas:
                print(f"   ⚠ {len(problemas)} animales con problemas:")
                for codigo, problema in problemas:
                    print(f"      - {codigo}: {problema}")
            else:
                print("   ✓ No se detectaron problemas")
            
            # 7. Resumen final
            print("\n" + "=" * 80)
            print("RESUMEN:")
            print("=" * 80)
            print(f"✓ Total animales activos: {total_activos}")
            print(f"✓ Animales importados hoy: {len(recientes)}")
            print(f"{'✓' if sin_finca == 0 else '⚠'} Animales sin finca: {sin_finca}")
            print(f"{'✓' if len(duplicados) == 0 else '⚠'} Códigos duplicados: {len(duplicados)}")
            print(f"✓ Fincas activas: {len(por_finca)}")
            
            if sin_finca == 0 and len(duplicados) == 0 and len(recientes) > 0:
                print("\n✅ RESULTADO: Todo correcto - Los animales deberían aparecer en el inventario")
            else:
                print("\n⚠ RESULTADO: Se detectaron problemas - Revisar detalles arriba")
            
            print("=" * 80)
            
    except Exception as e:
        print(f"\n❌ ERROR en la validación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def verificar_esquema_tabla():
    """Verifica que la tabla animal tenga todas las columnas necesarias"""
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DE ESQUEMA DE LA TABLA ANIMAL")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(animal)")
            columnas = cursor.fetchall()
            
            print("\nColumnas en la tabla 'animal':")
            print("ID | Nombre              | Tipo       | No Nulo | Default | PK")
            print("-" * 80)
            for col in columnas:
                cid, nombre, tipo, no_nulo, default, pk = col
                print(f"{cid:2} | {nombre:20} | {tipo:10} | {no_nulo:7} | {str(default):7} | {pk}")
            
            # Verificar columnas clave
            nombres_columnas = [col[1] for col in columnas]
            columnas_clave = ['id_finca', 'codigo', 'estado', 'inventariado', 'tipo_ingreso', 'sexo', 'raza_id']
            
            print("\nVerificación de columnas clave:")
            for col in columnas_clave:
                if col in nombres_columnas:
                    print(f"   ✓ {col}")
                else:
                    print(f"   ❌ {col} - FALTANTE")
            
    except Exception as e:
        print(f"\n❌ ERROR verificando esquema: {e}")
        import traceback
        traceback.print_exc()


def test_consulta_inventario():
    """Simula la consulta que hace el inventario para mostrar animales"""
    print("\n" + "=" * 80)
    print("TEST: Simulación de consulta del inventario")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener primera finca activa
            cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo' LIMIT 1")
            finca = cursor.fetchone()
            
            if not finca:
                print("   ⚠ No hay fincas activas en la base de datos")
                return
            
            id_finca, nombre_finca = finca
            print(f"\nConsultando animales de la finca: {nombre_finca} (ID: {id_finca})")
            
            # Ejecutar la misma consulta que usa el inventario
            cursor.execute("""
                SELECT a.codigo, a.nombre, a.sexo, COALESCE(r.nombre, 'Sin raza') as raza, 
                       COALESCE(p.nombre, 'Sin potrero') as potrero, 
                       a.estado, COALESCE(a.inventariado, 0) as inventariado, 
                       COALESCE(a.salud, 'Sano') as salud, 
                       COALESCE(a.tipo_ingreso, 'N/A') as tipo_ingreso
                FROM animal a
                LEFT JOIN raza r ON a.raza_id = r.id
                LEFT JOIN potrero p ON a.id_potrero = p.id
                WHERE a.id_finca = ? AND a.estado = 'Activo'
                ORDER BY a.codigo
            """, (id_finca,))
            
            animales = cursor.fetchall()
            
            if animales:
                print(f"\n✅ Se encontraron {len(animales)} animales:")
                print("\nCódigo    | Nombre           | Sexo   | Raza         | Potrero      | Inventariado")
                print("-" * 90)
                for animal in animales[:10]:
                    codigo, nombre, sexo, raza, potrero, estado, inv, salud, tipo = animal
                    nombre = nombre or "Sin nombre"
                    inv_txt = "Sí" if inv == 1 else "No"
                    print(f"{codigo:10} | {nombre:16} | {sexo:6} | {raza:12} | {potrero:12} | {inv_txt}")
                
                if len(animales) > 10:
                    print(f"\n... y {len(animales) - 10} más")
            else:
                print(f"\n⚠ No se encontraron animales activos en la finca '{nombre_finca}'")
                print("\nPosibles causas:")
                print("   1. Los animales importados tienen un id_finca diferente")
                print("   2. Los animales no tienen estado='Activo'")
                print("   3. No se han importado animales aún")
                
    except Exception as e:
        print(f"\n❌ ERROR en consulta de inventario: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 INICIANDO VALIDACIÓN DE IMPORTACIÓN E INVENTARIO\n")
    
    # Ejecutar todas las validaciones
    verificar_esquema_tabla()
    validar_animales_importados()
    test_consulta_inventario()
    
    print("\n✅ VALIDACIÓN COMPLETADA\n")
    print("INSTRUCCIONES:")
    print("1. Si hay animales sin finca asignada, revise la plantilla Excel")
    print("2. Si hay códigos duplicados, elimine los duplicados antes de importar")
    print("3. Si no aparecen en el inventario, verifique que:")
    print("   - La finca seleccionada en el combobox sea la correcta")
    print("   - Los animales tengan estado='Activo'")
    print("   - El filtro de estado en el inventario esté en 'Activo' o 'Todos'")
    print("\n")
