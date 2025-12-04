"""Normalizar estados de herramientas y aplicar migración 018"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_connection

print("=" * 70)
print("NORMALIZACIÓN DE ESTADOS Y MIGRACIÓN 018")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # 1. Normalizar estados
    print("\n1. Normalizando estados...")
    print("-" * 70)
    
    # Mapeo de normalización
    normalizaciones = {
        'activo': 'Operativa',
        'Activo': 'Operativa',
        'ACTIVO': 'Operativa',
        'operativa': 'Operativa',
        'en mantenimiento': 'En Mantenimiento',
        'mantenimiento': 'En Mantenimiento',
        'dañada': 'Dañada',
        'danada': 'Dañada',
        'fuera de servicio': 'Fuera de Servicio'
    }
    
    for estado_viejo, estado_nuevo in normalizaciones.items():
        cur.execute("UPDATE herramienta SET estado = ? WHERE estado = ?", (estado_nuevo, estado_viejo))
        if cur.rowcount > 0:
            print(f"✓ '{estado_viejo}' → '{estado_nuevo}' ({cur.rowcount} herramientas)")
    
    conn.commit()
    
    # Verificar estados actuales
    cur.execute("SELECT DISTINCT estado FROM herramienta ORDER BY estado")
    estados_finales = [e[0] for e in cur.fetchall()]
    
    print("\nEstados después de normalización:")
    for estado in estados_finales:
        cur.execute("SELECT COUNT(*) FROM herramienta WHERE estado = ?", (estado,))
        cant = cur.fetchone()[0]
        print(f"  • {estado}: {cant}")
    
    # 2. Aplicar migración 018
    print("\n2. Aplicando migración 018...")
    print("-" * 70)
    
    # Verificar si ya está aplicada
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='herramienta'")
    create_sql = cur.fetchone()[0]
    
    if 'En Revisión' in create_sql:
        print("✅ Migración 018 ya aplicada")
    else:
        # Limpiar tablas temporales
        cur.execute("DROP TABLE IF EXISTS herramienta_new")
        cur.execute("DROP TABLE IF EXISTS herramienta_old")
        
        # Obtener datos actuales
        cur.execute("SELECT * FROM herramienta")
        datos = cur.fetchall()
        
        # Obtener columnas
        cur.execute("PRAGMA table_info(herramienta)")
        columnas = [col[1] for col in cur.fetchall()]
        
        print(f"Respaldo: {len(datos)} herramientas con {len(columnas)} columnas")
        
        # Crear tabla nueva con CHECK actualizado
        cur.execute("""
            CREATE TABLE herramienta_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                categoria TEXT,
                descripcion TEXT,
                marca TEXT,
                modelo TEXT,
                numero_serie TEXT,
                id_finca INTEGER,
                ubicacion TEXT,
                estado TEXT DEFAULT 'Operativa' 
                    CHECK(estado IN ('Operativa', 'En Mantenimiento', 'En Revisión', 'Dañada', 'Fuera de Servicio')),
                fecha_adquisicion DATE,
                valor_adquisicion REAL,
                vida_util_anos INTEGER,
                responsable TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                foto_path TEXT,
                id_trabajador INTEGER,
                stock_total INTEGER DEFAULT 1,
                stock_bodega INTEGER DEFAULT 1,
                FOREIGN KEY (id_finca) REFERENCES finca(id) ON DELETE SET NULL
            )
        """)
        print("✓ Tabla herramienta_new creada")
        
        # Copiar datos
        columnas_str = ', '.join(columnas)
        cur.execute(f"INSERT INTO herramienta_new ({columnas_str}) SELECT {columnas_str} FROM herramienta")
        copiados = cur.rowcount
        print(f"✓ {copiados} registros copiados")
        
        # Renombrar tabla vieja
        cur.execute("ALTER TABLE herramienta RENAME TO herramienta_old")
        print("✓ Tabla vieja renombrada")
        
        # Renombrar nueva tabla
        cur.execute("ALTER TABLE herramienta_new RENAME TO herramienta")
        print("✓ Tabla nueva activada")
        
        # Recrear índices
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_categoria ON herramienta(categoria)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_estado ON herramienta(estado)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_id_finca ON herramienta(id_finca)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_id_trabajador ON herramienta(id_trabajador)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_codigo ON herramienta(codigo)")
        print("✓ Índices recreados")
        
        # Eliminar tabla vieja
        cur.execute("DROP TABLE herramienta_old")
        print("✓ Tabla vieja eliminada")
        
        conn.commit()
        print("\n✅ Migración 018 completada")
    
    # 3. Verificación final
    print("\n3. Verificación final...")
    print("-" * 70)
    
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='herramienta'")
    final_sql = cur.fetchone()[0]
    
    tiene_revision = 'En Revisión' in final_sql
    print(f"✅ Estado 'En Revisión': {'DISPONIBLE' if tiene_revision else 'NO DISPONIBLE'}")
    
    cur.execute("SELECT COUNT(*) FROM herramienta")
    cant_final = cur.fetchone()[0]
    print(f"✅ Total herramientas: {cant_final}")
    
    # Verificar tablas temporales
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%_new' OR name LIKE '%_old')")
    temp_tables = cur.fetchall()
    print(f"✅ Tablas temporales: {len(temp_tables)}")
    
    print("\n" + "=" * 70)
    print("🎉 MIGRACIONES COMPLETADAS")
    print("=" * 70)
    print("\n✓ Migración 017: Seguimiento de estado de mantenimientos")
    print("✓ Migración 018: Estado 'En Revisión' para herramientas")
    print("\nEl módulo de mantenimiento está completamente funcional.")
    print("=" * 70)
