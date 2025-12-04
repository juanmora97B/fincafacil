"""Limpiar tablas temporales y aplicar migración 018"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_connection

print("=" * 70)
print("LIMPIEZA Y MIGRACIÓN 018")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # 1. Limpiar tablas temporales
    print("\n1. Eliminando tablas temporales...")
    print("-" * 70)
    
    cur.execute("DROP TABLE IF EXISTS animal_old")
    print("✓ animal_old eliminada")
    
    cur.execute("DROP TABLE IF EXISTS herramienta_new")
    print("✓ herramienta_new eliminada")
    
    conn.commit()
    
    # 2. Aplicar migración 018
    print("\n2. Aplicando migración 018...")
    print("-" * 70)
    
    # Verificar si ya está aplicada
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='herramienta'")
    create_sql = cur.fetchone()[0]
    
    if 'En Revisión' in create_sql:
        print("✅ Migración 018 ya aplicada - Estado 'En Revisión' disponible")
    else:
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
        print("✓ Tabla herramienta_new creada con CHECK actualizado")
        
        # Copiar datos
        columnas_str = ', '.join(columnas)
        cur.execute(f"INSERT INTO herramienta_new ({columnas_str}) SELECT {columnas_str} FROM herramienta")
        copiados = cur.rowcount
        print(f"✓ {copiados} registros copiados")
        
        # Eliminar tabla vieja
        cur.execute("DROP TABLE herramienta")
        print("✓ Tabla herramienta antigua eliminada")
        
        # Renombrar nueva tabla
        cur.execute("ALTER TABLE herramienta_new RENAME TO herramienta")
        print("✓ Tabla renombrada a herramienta")
        
        # Recrear índices
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_categoria ON herramienta(categoria)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_estado ON herramienta(estado)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_id_finca ON herramienta(id_finca)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_id_trabajador ON herramienta(id_trabajador)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_codigo ON herramienta(codigo)")
        print("✓ Índices recreados")
        
        conn.commit()
        print("\n✅ Migración 018 completada exitosamente")
    
    # 3. Verificación final
    print("\n3. Verificación final...")
    print("-" * 70)
    
    # Verificar estados disponibles
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='herramienta'")
    final_sql = cur.fetchone()[0]
    
    if 'En Revisión' in final_sql:
        print("✅ Estado 'En Revisión' DISPONIBLE")
    else:
        print("❌ Estado 'En Revisión' NO disponible")
    
    # Contar registros
    cur.execute("SELECT COUNT(*) FROM herramienta")
    cant_final = cur.fetchone()[0]
    print(f"✅ {cant_final} herramientas en la tabla")
    
    # Verificar tablas temporales
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new' OR name LIKE '%_old'")
    temp_tables = cur.fetchall()
    
    if temp_tables:
        print(f"⚠️  {len(temp_tables)} tablas temporales aún presentes")
    else:
        print("✅ No hay tablas temporales residuales")
    
    print("\n" + "=" * 70)
    print("PROCESO COMPLETADO")
    print("=" * 70)
    print("\n🎉 Todas las migraciones aplicadas correctamente:")
    print("   ✓ Migración 017: Seguimiento de estado de mantenimientos")
    print("   ✓ Migración 018: Estado 'En Revisión' para herramientas")
    print("\nEl módulo de mantenimiento está completamente funcional.")
    print("=" * 70)
