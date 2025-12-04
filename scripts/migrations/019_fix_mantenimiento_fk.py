"""
Migración correctiva: Reparar FOREIGN KEY en mantenimiento_herramienta

PROBLEMA:
Las migraciones 008 y 018 recrearon la tabla herramienta pero dejaron
mantenimiento_herramienta con FK apuntando a "herramienta_old" inexistente.

SOLUCIÓN:
Recrear mantenimiento_herramienta con FK correcta apuntando a "herramienta"
"""

def run(conn):
    print("➡️ Ejecutando migración correctiva FK mantenimiento_herramienta...")
    
    try:
        cur = conn.cursor()
        
        # 1. Verificar si la tabla necesita corrección
        cur.execute("PRAGMA foreign_key_list(mantenimiento_herramienta)")
        fks = cur.fetchall()
        
        if not fks:
            print("⚠️  No hay foreign keys en mantenimiento_herramienta")
            return
        
        fk_tabla = fks[0][2]  # Tabla referenciada
        
        if fk_tabla == 'herramienta':
            print("✅ Foreign key ya está correcta, no se requiere migración")
            return
        
        if fk_tabla != 'herramienta_old':
            print(f"⚠️  Foreign key apunta a '{fk_tabla}', verificar manualmente")
            return
        
        print(f"🔧 Corrigiendo FK: {fk_tabla} → herramienta")
        
        # 2. Respaldar datos
        cur.execute("SELECT * FROM mantenimiento_herramienta")
        datos = cur.fetchall()
        print(f"   📦 Respaldando {len(datos)} registros...")
        
        # 3. Obtener columnas
        cur.execute("PRAGMA table_info(mantenimiento_herramienta)")
        columnas = [col[1] for col in cur.fetchall()]
        
        # 4. Eliminar tabla con FK incorrecta
        cur.execute("DROP TABLE IF EXISTS mantenimiento_herramienta")
        print("   🗑️  Tabla antigua eliminada")
        
        # 5. Recrear tabla con FK correcta
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
        print("   ✅ Tabla recreada con FK → herramienta")
        
        # 6. Crear índice
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mant_estado 
            ON mantenimiento_herramienta(estado_actual, herramienta_id)
        """)
        
        # 7. Restaurar datos (solo los válidos)
        if datos:
            # Verificar qué herramientas existen
            cur.execute("SELECT id FROM herramienta")
            ids_validas = set(row[0] for row in cur.fetchall())
            
            datos_validos = [d for d in datos if d[1] in ids_validas]
            datos_invalidos = len(datos) - len(datos_validos)
            
            if datos_validos:
                placeholders = ','.join(['?'] * len(columnas))
                cur.executemany(
                    f"INSERT INTO mantenimiento_herramienta ({','.join(columnas)}) VALUES ({placeholders})",
                    datos_validos
                )
                print(f"   ✅ {len(datos_validos)} registros restaurados")
            
            if datos_invalidos > 0:
                print(f"   ⚠️  {datos_invalidos} registros descartados (herramienta inexistente)")
        else:
            print("   ℹ️  No había datos para restaurar")
        
        conn.commit()
        print("✅ Migración correctiva completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en migración correctiva: {e}")
        raise

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from database import get_connection
    
    with get_connection() as conn:
        run(conn)
