"""Script para verificar y aplicar migración 018 - agregar estado 'En Revisión'"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_connection

print("=" * 60)
print("VERIFICACIÓN DE TABLA herramienta - Estado 'En Revisión'")
print("=" * 60)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Obtener el CREATE TABLE actual
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='herramienta'")
    create_sql = cur.fetchone()[0]
    
    print("\nDefinición actual de la tabla:")
    print("-" * 60)
    print(create_sql)
    
    # Verificar si 'En Revisión' ya está en el CHECK constraint
    necesita_018 = 'En Revisión' not in create_sql
    
    print("\n" + "=" * 60)
    if necesita_018:
        print("⚠️  MIGRACIÓN 018 NECESARIA")
        print("=" * 60)
        print("\nEl estado 'En Revisión' no está en el CHECK constraint")
        
        print("\n🔧 Aplicando migración 018...")
        
        # Obtener todos los datos actuales
        cur.execute("SELECT * FROM herramienta")
        datos = cur.fetchall()
        
        # Obtener nombres de columnas
        cur.execute("PRAGMA table_info(herramienta)")
        columnas = [col[1] for col in cur.fetchall()]
        
        print(f"✓ {len(datos)} registros encontrados")
        print(f"✓ {len(columnas)} columnas: {', '.join(columnas)}")
        
        # Eliminar tabla temporal si existe
        cur.execute("DROP TABLE IF EXISTS herramienta_new")
        print("✓ Tabla temporal eliminada (si existía)")
        
        # Crear tabla nueva con CHECK actualizado (estructura real de la DB)
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
        print(f"✓ {len(datos)} registros copiados")
        
        # Eliminar tabla vieja
        cur.execute("DROP TABLE herramienta")
        print("✓ Tabla herramienta antigua eliminada")
        
        # Renombrar nueva tabla
        cur.execute("ALTER TABLE herramienta_new RENAME TO herramienta")
        print("✓ Tabla herramienta_new renombrada a herramienta")
        
        # Recrear índices según estructura real
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_categoria ON herramienta(categoria)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_estado ON herramienta(estado)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_id_finca ON herramienta(id_finca)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_id_trabajador ON herramienta(id_trabajador)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_codigo ON herramienta(codigo)")
        print("✓ Índices recreados")
        
        conn.commit()
        print("\n✅ Migración 018 completada exitosamente")
    else:
        print("✅ MIGRACIÓN 018 YA APLICADA")
        print("=" * 60)
        print("\nEl estado 'En Revisión' ya está disponible en el CHECK constraint")
    
    # Verificar estados actuales en uso
    cur.execute("SELECT estado, COUNT(*) as cant FROM herramienta GROUP BY estado")
    estados = cur.fetchall()
    
    print("\n" + "=" * 60)
    print("Estados en uso:")
    print("-" * 60)
    for estado, cant in estados:
        print(f"  {estado:30} {cant:>5} herramientas")
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)
