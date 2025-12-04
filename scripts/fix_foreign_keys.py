"""
Script para corregir errores de Foreign Keys en la base de datos
Identifica y soluciona problemas comunes con claves foráneas
"""

import sqlite3
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_connection

def verificar_foreign_keys():
    """Verifica el estado de las foreign keys en la base de datos"""
    print("=" * 70)
    print("VERIFICACIÓN DE FOREIGN KEYS")
    print("=" * 70)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Habilitar foreign keys (importante)
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Verificar si están habilitadas
            cursor.execute("PRAGMA foreign_keys")
            fk_status = cursor.fetchone()[0]
            print(f"\n✓ Foreign Keys habilitadas: {'SÍ' if fk_status else 'NO'}")
            
            if not fk_status:
                print("⚠️ ADVERTENCIA: Las foreign keys están deshabilitadas")
                print("   Ejecutando: PRAGMA foreign_keys = ON")
                cursor.execute("PRAGMA foreign_keys = ON")
            
            # Verificar integridad de foreign keys
            print("\n" + "-" * 70)
            print("VERIFICANDO INTEGRIDAD DE FOREIGN KEYS")
            print("-" * 70)
            
            tablas = [
                'animal', 'diagnostico_evento', 'tratamiento', 'reproduccion',
                'servicio', 'movimiento', 'peso', 'produccion_leche', 'muerte',
                'comentario', 'movimiento_insumo', 'potrero', 'insumo',
                'pago_nomina', 'sector'
            ]
            
            errores_encontrados = []
            
            for tabla in tablas:
                cursor.execute(f"PRAGMA foreign_key_check({tabla})")
                errores = cursor.fetchall()
                if errores:
                    errores_encontrados.append((tabla, errores))
                    print(f"\n❌ {tabla}: {len(errores)} error(es) encontrado(s)")
                    for error in errores[:5]:  # Mostrar solo los primeros 5
                        print(f"   {error}")
                else:
                    print(f"✓ {tabla}: Sin errores")
            
            return errores_encontrados
            
    except Exception as e:
        print(f"\n❌ Error durante verificación: {e}")
        return None

def limpiar_referencias_huerfanas():
    """Limpia referencias a registros que no existen (registros huérfanos)"""
    print("\n" + "=" * 70)
    print("LIMPIEZA DE REFERENCIAS HUÉRFANAS")
    print("=" * 70)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = OFF")  # Temporalmente off para limpieza
            
            registros_limpiados = 0
            
            # 1. Limpiar animales con referencias inválidas
            print("\n1. Limpiando referencias en tabla 'animal'...")
            
            # Fincas inválidas -> NULL
            cursor.execute("""
                UPDATE animal 
                SET id_finca = NULL 
                WHERE id_finca IS NOT NULL 
                AND id_finca NOT IN (SELECT id FROM finca)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con id_finca inválida -> NULL")
                registros_limpiados += count
            
            # Razas inválidas -> NULL
            cursor.execute("""
                UPDATE animal 
                SET raza_id = NULL 
                WHERE raza_id IS NOT NULL 
                AND raza_id NOT IN (SELECT id FROM raza)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con raza_id inválida -> NULL")
                registros_limpiados += count
            
            # Potreros inválidos -> NULL
            cursor.execute("""
                UPDATE animal 
                SET id_potrero = NULL 
                WHERE id_potrero IS NOT NULL 
                AND id_potrero NOT IN (SELECT id FROM potrero)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con id_potrero inválido -> NULL")
                registros_limpiados += count
            
            # Lotes inválidos -> NULL
            cursor.execute("""
                UPDATE animal 
                SET lote_id = NULL 
                WHERE lote_id IS NOT NULL 
                AND lote_id NOT IN (SELECT id FROM lote)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con lote_id inválido -> NULL")
                registros_limpiados += count
            
            # Limpieza de id_grupo legacy (si columna aún existe en instalaciones antiguas)
            try:
                cursor.execute("PRAGMA table_info(animal)")
                cols = {c[1] for c in cursor.fetchall()}
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grupo'")
                tiene_grupo = cursor.fetchone() is not None
                if 'id_grupo' in cols and tiene_grupo:
                    cursor.execute("""
                        UPDATE animal 
                        SET id_grupo = NULL 
                        WHERE id_grupo IS NOT NULL 
                        AND id_grupo NOT IN (SELECT id FROM grupo)
                    """)
                    count = cursor.rowcount
                    if count > 0:
                        print(f"   ✓ {count} animales con id_grupo inválido -> NULL")
                        registros_limpiados += count
            except Exception:
                pass
            
            # Vendedores inválidos -> NULL
            cursor.execute("""
                UPDATE animal 
                SET id_vendedor = NULL 
                WHERE id_vendedor IS NOT NULL 
                AND id_vendedor NOT IN (SELECT id FROM vendedor)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con id_vendedor inválido -> NULL")
                registros_limpiados += count
            
            # Padres inválidos -> NULL
            cursor.execute("""
                UPDATE animal 
                SET id_padre = NULL 
                WHERE id_padre IS NOT NULL 
                AND id_padre NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con id_padre inválido -> NULL")
                registros_limpiados += count
            
            # Madres inválidas -> NULL
            cursor.execute("""
                UPDATE animal 
                SET id_madre = NULL 
                WHERE id_madre IS NOT NULL 
                AND id_madre NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} animales con id_madre inválida -> NULL")
                registros_limpiados += count
            
            # 2. Limpiar eventos de diagnóstico con animales inválidos
            print("\n2. Limpiando tabla 'diagnostico_evento'...")
            cursor.execute("""
                DELETE FROM diagnostico_evento 
                WHERE animal_id NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} registros de diagnóstico huérfanos eliminados")
                registros_limpiados += count
            
            # 3. Limpiar tratamientos con animales inválidos
            print("\n3. Limpiando tabla 'tratamiento'...")
            cursor.execute("""
                DELETE FROM tratamiento 
                WHERE id_animal NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} tratamientos huérfanos eliminados")
                registros_limpiados += count
            
            # 4. Limpiar reproducción con animales inválidos
            print("\n4. Limpiando tabla 'reproduccion'...")
            cursor.execute("""
                DELETE FROM reproduccion 
                WHERE animal_id NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} registros de reproducción huérfanos eliminados")
                registros_limpiados += count
            
            # 5. Limpiar servicios con animales inválidos
            print("\n5. Limpiando tabla 'servicio'...")
            cursor.execute("""
                DELETE FROM servicio 
                WHERE id_hembra NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} servicios huérfanos eliminados")
                registros_limpiados += count
            
            # Machos inválidos en servicios -> NULL
            cursor.execute("""
                UPDATE servicio 
                SET id_macho = NULL 
                WHERE id_macho IS NOT NULL 
                AND id_macho NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} servicios con id_macho inválido -> NULL")
                registros_limpiados += count
            
            # 6. Limpiar movimientos con animales inválidos
            print("\n6. Limpiando tabla 'movimiento'...")
            cursor.execute("""
                DELETE FROM movimiento 
                WHERE animal_id NOT IN (SELECT id FROM animal)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} movimientos huérfanos eliminados")
                registros_limpiados += count
            
            # 7. Limpiar potreros con finca inválida
            print("\n7. Limpiando tabla 'potrero'...")
            cursor.execute("""
                UPDATE potrero 
                SET id_finca = NULL 
                WHERE id_finca IS NOT NULL 
                AND id_finca NOT IN (SELECT id FROM finca)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} potreros con id_finca inválida -> NULL")
                registros_limpiados += count
            
            # 8. Limpiar sectores con finca inválida
            print("\n8. Limpiando tabla 'sector'...")
            cursor.execute("""
                UPDATE sector 
                SET finca_id = NULL 
                WHERE finca_id IS NOT NULL 
                AND finca_id NOT IN (SELECT id FROM finca)
            """)
            count = cursor.rowcount
            if count > 0:
                print(f"   ✓ {count} sectores con finca_id inválida -> NULL")
                registros_limpiados += count
            
            # Commit de todos los cambios
            conn.commit()
            
            # Reactivar foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            print("\n" + "-" * 70)
            print(f"✓ LIMPIEZA COMPLETADA: {registros_limpiados} registros corregidos/eliminados")
            print("-" * 70)
            
            return registros_limpiados
            
    except Exception as e:
        print(f"\n❌ Error durante limpieza: {e}")
        return 0

def crear_registros_necesarios():
    """Crea registros básicos necesarios si no existen"""
    print("\n" + "=" * 70)
    print("CREANDO REGISTROS BÁSICOS NECESARIOS")
    print("=" * 70)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar y crear finca por defecto
            cursor.execute("SELECT COUNT(*) FROM finca")
            if cursor.fetchone()[0] == 0:
                print("\n✓ Creando finca por defecto...")
                cursor.execute("""
                    INSERT INTO finca (codigo, nombre, propietario, area_total, estado)
                    VALUES ('F001', 'Finca Principal', 'Propietario', 0, 'Activo')
                """)
                print("   Finca por defecto creada: F001 - Finca Principal")
            
            # Verificar y crear raza por defecto
            cursor.execute("SELECT COUNT(*) FROM raza")
            if cursor.fetchone()[0] == 0:
                print("\n✓ Creando raza por defecto...")
                cursor.execute("""
                    INSERT INTO raza (codigo, nombre, estado)
                    VALUES ('SIN-RAZA', 'Sin Raza Definida', 'Activo')
                """)
                print("   Raza por defecto creada: SIN-RAZA")
            
            # Verificar y crear lote por defecto
            cursor.execute("SELECT COUNT(*) FROM lote")
            if cursor.fetchone()[0] == 0:
                print("\n✓ Creando lote por defecto...")
                cursor.execute("""
                    INSERT INTO lote (codigo, nombre, descripcion, estado)
                    VALUES ('L001', 'Lote General', 'Lote general para animales sin clasificar', 'Activo')
                """)
                print("   Lote por defecto creado: L001 - Lote General")
            
            # Verificar y crear grupo por defecto
            cursor.execute("SELECT COUNT(*) FROM grupo")
            if cursor.fetchone()[0] == 0:
                print("\n✓ Creando grupo por defecto...")
                cursor.execute("""
                    INSERT INTO grupo (nombre, descripcion, estado)
                    VALUES ('General', 'Grupo general', 'Activo')
                """)
                print("   Grupo por defecto creado: General")
            
            conn.commit()
            print("\n✓ Registros básicos verificados/creados correctamente")
            
    except Exception as e:
        print(f"\n❌ Error creando registros: {e}")

def main():
    """Función principal"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 15 + "CORRECCIÓN DE FOREIGN KEYS" + " " * 27 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    # 1. Verificar estado actual
    errores = verificar_foreign_keys()
    
    if errores is None:
        print("\n❌ No se pudo verificar el estado de la base de datos")
        return
    
    # 2. Crear registros necesarios
    crear_registros_necesarios()
    
    # 3. Limpiar referencias huérfanas
    registros_limpiados = limpiar_referencias_huerfanas()
    
    # 4. Verificar nuevamente
    print("\n" + "=" * 70)
    print("VERIFICACIÓN FINAL")
    print("=" * 70)
    errores_finales = verificar_foreign_keys()
    
    # Resumen
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 25 + "RESUMEN FINAL" + " " * 30 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    if errores_finales is not None:
        if len(errores_finales) == 0:
            print("\n✓✓✓ TODAS LAS FOREIGN KEYS ESTÁN CORRECTAS ✓✓✓")
            print(f"✓ {registros_limpiados} registros fueron corregidos")
        else:
            print(f"\n⚠️ Aún quedan {len(errores_finales)} tabla(s) con errores")
            print("   Se recomienda revisión manual de los datos")
    
    print("\n" + "█" * 70 + "\n")

if __name__ == "__main__":
    main()
