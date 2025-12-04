"""
Migración 018: Agregar estado 'En Revisión' a herramientas
SQLite no soporta ALTER TABLE para modificar CHECK constraints,
así que se debe recrear la tabla
"""

def migrate(conn):
    cursor = conn.cursor()
    
    # Verificar si ya existe el estado 'En Revisión'
    cursor.execute("SELECT estado FROM herramienta WHERE estado = 'En Revisión' LIMIT 1")
    if cursor.fetchone():
        print("✓ Estado 'En Revisión' ya existe en la tabla")
        return
    
    print("Actualizando tabla herramienta para incluir estado 'En Revisión'...")
    
    # Paso 1: Crear tabla temporal con el nuevo constraint
    cursor.execute("""
        CREATE TABLE herramienta_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT CHECK(categoria IN ('Maquinaria', 'Herramienta Manual', 'Equipo Medico', 'Vehiculo', 'Equipo Oficina', 'Otro')),
            descripcion TEXT,
            marca TEXT,
            modelo TEXT,
            numero_serie TEXT,
            id_finca INTEGER,
            ubicacion TEXT,
            estado TEXT CHECK(estado IN ('Operativa', 'En Mantenimiento', 'En Revisión', 'Dañada', 'Fuera de Servicio')) DEFAULT 'Operativa',
            fecha_adquisicion DATE,
            valor_adquisicion REAL,
            vida_util_anos INTEGER,
            responsable TEXT,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            foto_path TEXT,
            id_trabajador INTEGER,
            stock_total INTEGER DEFAULT 1,
            stock_bodega INTEGER DEFAULT 0,
            FOREIGN KEY (id_finca) REFERENCES finca(id),
            FOREIGN KEY (id_trabajador) REFERENCES empleado(rowid)
        )
    """)
    print("✓ Tabla temporal creada")
    
    # Paso 2: Copiar datos
    cursor.execute("""
        INSERT INTO herramienta_new 
        SELECT * FROM herramienta
    """)
    print("✓ Datos copiados a tabla temporal")
    
    # Paso 3: Eliminar tabla original
    cursor.execute("DROP TABLE herramienta")
    print("✓ Tabla original eliminada")
    
    # Paso 4: Renombrar tabla nueva
    cursor.execute("ALTER TABLE herramienta_new RENAME TO herramienta")
    print("✓ Tabla renombrada")
    
    # Paso 5: Recrear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_codigo ON herramienta (codigo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_estado ON herramienta (estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_finca ON herramienta (id_finca)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_trabajador ON herramienta (id_trabajador)")
    print("✓ Índices recreados")
    
    conn.commit()
    print("✅ Migración 018 completada exitosamente")

def rollback(conn):
    """Revertir migración"""
    print("⚠ Rollback no implementado (requiere backup de base de datos)")
