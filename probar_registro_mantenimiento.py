"""
Script de prueba para registrar un mantenimiento de ejemplo
"""
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from database.database import get_db_connection

print("=" * 70)
print("PRUEBA DE REGISTRO DE MANTENIMIENTO")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # 1. Obtener una herramienta para probar
    print("\n1. Obteniendo herramienta para prueba...")
    cur.execute("SELECT id, codigo, nombre FROM herramienta LIMIT 1")
    herramienta = cur.fetchone()
    
    if not herramienta:
        print("   ❌ No hay herramientas en la base de datos")
        print("   Registre una herramienta primero")
        exit(1)
    
    herr_id, herr_codigo, herr_nombre = herramienta
    print(f"   ✓ Herramienta seleccionada: {herr_codigo} - {herr_nombre}")
    
    # 2. Verificar si ya tiene mantenimientos
    cur.execute("SELECT COUNT(*) FROM mantenimiento_herramienta WHERE herramienta_id = ?", (herr_id,))
    cant_mant = cur.fetchone()[0]
    print(f"   ℹ️  Mantenimientos actuales: {cant_mant}")
    
    # 3. Intentar registrar un mantenimiento de prueba
    print("\n2. Registrando mantenimiento de prueba...")
    try:
        cur.execute("""
            INSERT INTO mantenimiento_herramienta (
                herramienta_id,
                tipo_mantenimiento,
                fecha_mantenimiento,
                descripcion,
                costo,
                realizado_por,
                estado_actual,
                estado_previo_herramienta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            herr_id,
            'Preventivo',
            datetime.now().strftime('%Y-%m-%d'),
            'Mantenimiento de prueba - verificación FK',
            0.0,
            'Sistema',
            'Activo',
            'Operativa'
        ))
        
        mant_id = cur.lastrowid
        print(f"   ✅ Mantenimiento registrado con ID: {mant_id}")
        
        # 4. Verificar que se guardó correctamente
        print("\n3. Verificando registro...")
        cur.execute("""
            SELECT m.*, h.nombre as herramienta_nombre
            FROM mantenimiento_herramienta m
            JOIN herramienta h ON m.herramienta_id = h.id
            WHERE m.id = ?
        """, (mant_id,))
        
        registro = cur.fetchone()
        if registro:
            print("   ✅ Registro verificado correctamente")
            print(f"   • ID: {registro[0]}")
            print(f"   • Herramienta: {registro[-1]}")
            print(f"   • Tipo: {registro[2]}")
            print(f"   • Fecha: {registro[3]}")
            print(f"   • Estado: {registro[11]}")
        
        # 5. Eliminar el registro de prueba
        print("\n4. Limpiando registro de prueba...")
        cur.execute("DELETE FROM mantenimiento_herramienta WHERE id = ?", (mant_id,))
        print("   ✓ Registro de prueba eliminado")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print("✅ PRUEBA EXITOSA")
        print("=" * 70)
        print("\nLa tabla mantenimiento_herramienta funciona correctamente.")
        print("El error 'no such table: main.herramienta_old' ha sido resuelto.")
        print("\nPuede registrar mantenimientos desde la aplicación sin problemas.")
        print("=" * 70)
        
    except Exception as e:
        print(f"   ❌ Error al registrar: {e}")
        conn.rollback()
        
        print("\n" + "=" * 70)
        print("❌ PRUEBA FALLIDA")
        print("=" * 70)
        print(f"\nError: {e}")
        print("=" * 70)
