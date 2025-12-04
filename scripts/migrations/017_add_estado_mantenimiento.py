"""
Migración 017: Agregar campos de estado a mantenimiento_herramienta
- estado_actual: indica si el mantenimiento está Activo o Completado
- estado_previo_herramienta: guarda el estado de la herramienta antes del mantenimiento
- fecha_completado: registra cuándo se completó el mantenimiento
"""

def migrate(conn):
    cursor = conn.cursor()
    
    # Agregar campo estado_actual (Activo por defecto para registros existentes)
    try:
        cursor.execute("""
            ALTER TABLE mantenimiento_herramienta 
            ADD COLUMN estado_actual TEXT DEFAULT 'Activo' 
            CHECK(estado_actual IN ('Activo', 'Completado'))
        """)
        print("✓ Campo estado_actual agregado a mantenimiento_herramienta")
    except Exception as e:
        if "duplicate column name" not in str(e).lower():
            raise
        print("✓ Campo estado_actual ya existe")
    
    # Agregar campo estado_previo_herramienta para restaurar después
    try:
        cursor.execute("""
            ALTER TABLE mantenimiento_herramienta 
            ADD COLUMN estado_previo_herramienta TEXT
        """)
        print("✓ Campo estado_previo_herramienta agregado")
    except Exception as e:
        if "duplicate column name" not in str(e).lower():
            raise
        print("✓ Campo estado_previo_herramienta ya existe")
    
    # Agregar campo fecha_completado
    try:
        cursor.execute("""
            ALTER TABLE mantenimiento_herramienta 
            ADD COLUMN fecha_completado DATE
        """)
        print("✓ Campo fecha_completado agregado")
    except Exception as e:
        if "duplicate column name" not in str(e).lower():
            raise
        print("✓ Campo fecha_completado ya existe")
    
    # Crear índice para búsqueda rápida de mantenimientos activos
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mant_estado 
            ON mantenimiento_herramienta(estado_actual, herramienta_id)
        """)
        print("✓ Índice idx_mant_estado creado")
    except Exception as e:
        print(f"⚠ Error creando índice: {e}")
    
    conn.commit()
    print("✅ Migración 017 completada exitosamente")

def rollback(conn):
    """Revertir migración (SQLite no soporta DROP COLUMN, requiere recrear tabla)"""
    print("⚠ Rollback no implementado para SQLite (requiere recrear tabla completa)")
    print("  Si necesita revertir, use backup de base de datos")
