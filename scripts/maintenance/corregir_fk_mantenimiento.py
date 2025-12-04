"""
Script para corregir el FOREIGN KEY de mantenimiento_herramienta
que apunta a herramienta_old en lugar de herramienta
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import get_db_connection

print("=" * 70)
print("CORRECCIÓN DE FOREIGN KEY EN mantenimiento_herramienta")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # 1. Verificar estado actual
    print("\n1. Verificando estado actual...")
    cur.execute("PRAGMA foreign_key_list(mantenimiento_herramienta)")
    fks = cur.fetchall()
    print(f"   Foreign key actual: {fks[0][3]} → {fks[0][2]}")
    
    # 2. Respaldar datos
    print("\n2. Respaldando datos...")
    cur.execute("SELECT * FROM mantenimiento_herramienta")
    datos = cur.fetchall()
    print(f"   ✓ {len(datos)} registros respaldados")
    
    # 3. Obtener estructura de columnas
    cur.execute("PRAGMA table_info(mantenimiento_herramienta)")
    columnas_info = cur.fetchall()
    columnas = [col[1] for col in columnas_info]
    print(f"   ✓ {len(columnas)} columnas: {', '.join(columnas[:5])}...")
    
    # 4. Eliminar tabla vieja
    print("\n3. Eliminando tabla con FK incorrecta...")
    cur.execute("DROP TABLE IF EXISTS mantenimiento_herramienta")
    print("   ✓ Tabla eliminada")
    
    # 5. Crear tabla nueva con FK correcta
    print("\n4. Creando tabla con FK correcta...")
    cur.execute("""
        CREATE TABLE mantenimiento_herramienta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            herramienta_id INTEGER NOT NULL,
            tipo_mantenimiento TEXT,
            fecha_mantenimiento DATE NOT NULL,
            descripcion TEXT,
            costo REAL,
            proveedor_servicio TEXT,
            proximo_mantenimiento DATE,
            realizado_por TEXT,
            observaciones TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado_actual TEXT DEFAULT 'Activo' 
                CHECK(estado_actual IN ('Activo', 'Completado')),
            estado_previo_herramienta TEXT,
            fecha_completado DATE,
            FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
        )
    """)
    print("   ✓ Tabla creada con FOREIGN KEY → herramienta")
    
    # 6. Crear índice
    print("\n5. Creando índice...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_mant_estado 
        ON mantenimiento_herramienta(estado_actual, herramienta_id)
    """)
    print("   ✓ Índice idx_mant_estado creado")
    
    # 7. Restaurar datos
    print("\n6. Restaurando datos...")
    if datos:
        placeholders = ','.join(['?'] * len(columnas))
        cur.executemany(
            f"INSERT INTO mantenimiento_herramienta ({','.join(columnas)}) VALUES ({placeholders})",
            datos
        )
        print(f"   ✓ {len(datos)} registros restaurados")
    else:
        print("   ℹ️  No había datos para restaurar")
    
    # 8. Verificar corrección
    print("\n7. Verificando corrección...")
    cur.execute("PRAGMA foreign_key_list(mantenimiento_herramienta)")
    fks_new = cur.fetchall()
    if fks_new:
        print(f"   ✓ Foreign key corregida: {fks_new[0][3]} → {fks_new[0][2]}")
        if fks_new[0][2] == 'herramienta':
            print("   ✅ FOREIGN KEY CORRECTA")
        else:
            print("   ❌ FOREIGN KEY AÚN INCORRECTA")
    
    # 9. Verificar que los datos se pueden consultar
    print("\n8. Verificando consultas...")
    cur.execute("""
        SELECT m.id, h.nombre 
        FROM mantenimiento_herramienta m
        JOIN herramienta h ON m.herramienta_id = h.id
    """)
    resultados = cur.fetchall()
    print(f"   ✓ Consulta exitosa: {len(resultados)} registros con JOIN")
    
    conn.commit()
    
    print("\n" + "=" * 70)
    print("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nLa tabla mantenimiento_herramienta ahora apunta correctamente a")
    print("la tabla 'herramienta' en lugar de 'herramienta_old'")
    print("\nPuede probar registrar un mantenimiento desde la aplicación.")
    print("=" * 70)
