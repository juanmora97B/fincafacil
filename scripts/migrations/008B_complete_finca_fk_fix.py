"""
Migration 008B: Completar fix de FK para finca en tablas restantes
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

def run():
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Verificar y arreglar potrero
            cur.execute("PRAGMA foreign_key_list(potrero)")
            fks = cur.fetchall()
            needs_fix = any(fk[2] == 'finca' and (len(fk) <= 6 or fk[6] != 'SET NULL') for fk in fks)
            
            if needs_fix:
                print("🔧 Migrando tabla potrero...")
                cur.execute("ALTER TABLE potrero RENAME TO potrero_old;")
                cur.execute("""
                CREATE TABLE potrero (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    id_finca INTEGER,
                    nombre TEXT NOT NULL,
                    id_sector INTEGER,
                    area_hectareas REAL,
                    capacidad_maxima INTEGER,
                    tipo_pasto TEXT,
                    descripcion TEXT,
                    estado TEXT DEFAULT 'Activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_finca) REFERENCES finca (id) ON DELETE SET NULL
                );
                """)
                cur.execute("INSERT INTO potrero SELECT * FROM potrero_old;")
                cur.execute("DROP TABLE IF EXISTS potrero_old;")
                print("✔ Potrero migrado")
            
            # Verificar insumo si existe
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='insumo'")
            if cur.fetchone():
                cur.execute("PRAGMA foreign_key_list(insumo)")
                fks = cur.fetchall()
                needs_fix = any(fk[2] == 'finca' and (len(fk) <= 6 or fk[6] != 'SET NULL') for fk in fks)
                
                if needs_fix:
                    print("🔧 Migrando tabla insumo...")
                    cur.execute("PRAGMA table_info(insumo)")
                    cols_old = [row[1] for row in cur.fetchall()]
                    
                    cur.execute("ALTER TABLE insumo RENAME TO insumo_old;")
                    cur.execute("""
                    CREATE TABLE insumo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo TEXT UNIQUE NOT NULL,
                        nombre TEXT NOT NULL,
                        categoria TEXT,
                        descripcion TEXT,
                        unidad_medida TEXT,
                        stock_actual REAL DEFAULT 0,
                        stock_minimo REAL DEFAULT 0,
                        stock_maximo REAL,
                        precio_unitario REAL,
                        id_finca INTEGER,
                        ubicacion TEXT,
                        proveedor_principal TEXT,
                        fecha_vencimiento DATE,
                        lote_proveedor TEXT,
                        estado TEXT DEFAULT 'Activo',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_finca) REFERENCES finca(id) ON DELETE SET NULL
                    );
                    """)
                    cols_new = ['id', 'codigo', 'nombre', 'categoria', 'descripcion', 'unidad_medida', 
                               'stock_actual', 'stock_minimo', 'stock_maximo', 'precio_unitario', 
                               'id_finca', 'ubicacion', 'proveedor_principal', 'fecha_vencimiento', 
                               'lote_proveedor', 'estado', 'fecha_creacion']
                    cols_to_copy = [c for c in cols_new if c in cols_old]
                    cols_str = ', '.join(cols_to_copy)
                    cur.execute(f"INSERT INTO insumo ({cols_str}) SELECT {cols_str} FROM insumo_old;")
                    cur.execute("DROP TABLE IF EXISTS insumo_old;")
                    print("✔ Insumo migrado")
            
            # Verificar herramienta si existe
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='herramienta'")
            if cur.fetchone():
                cur.execute("PRAGMA foreign_key_list(herramienta)")
                fks = cur.fetchall()
                needs_fix = any(fk[2] == 'finca' and (len(fk) <= 6 or fk[6] != 'SET NULL') for fk in fks)
                
                if needs_fix:
                    print("🔧 Migrando tabla herramienta...")
                    cur.execute("PRAGMA table_info(herramienta)")
                    cols_old = [row[1] for row in cur.fetchall()]
                    
                    cur.execute("ALTER TABLE herramienta RENAME TO herramienta_old;")
                    cur.execute("""
                    CREATE TABLE herramienta (
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
                        estado TEXT DEFAULT 'Operativa',
                        fecha_adquisicion DATE,
                        valor_adquisicion REAL,
                        vida_util_anos INTEGER,
                        responsable TEXT,
                        observaciones TEXT,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id_finca) REFERENCES finca(id) ON DELETE SET NULL
                    );
                    """)
                    cols_new = ['id', 'codigo', 'nombre', 'categoria', 'descripcion', 'marca', 'modelo',
                               'numero_serie', 'id_finca', 'ubicacion', 'estado', 'fecha_adquisicion',
                               'valor_adquisicion', 'vida_util_anos', 'responsable', 'observaciones',
                               'fecha_creacion']
                    cols_to_copy = [c for c in cols_new if c in cols_old]
                    cols_str = ', '.join(cols_to_copy)
                    cur.execute(f"INSERT INTO herramienta ({cols_str}) SELECT {cols_str} FROM herramienta_old;")
                    cur.execute("DROP TABLE IF EXISTS herramienta_old;")
                    print("✔ Herramienta migrado")
            
            # Verificar sector si existe
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sector'")
            if cur.fetchone():
                cur.execute("PRAGMA table_info(sector)")
                cols = [row[1] for row in cur.fetchall()]
                if 'finca_id' in cols:
                    cur.execute("PRAGMA foreign_key_list(sector)")
                    fks = cur.fetchall()
                    needs_fix = any(fk[2] == 'finca' and (len(fk) <= 6 or fk[6] != 'SET NULL') for fk in fks)
                    
                    if needs_fix:
                        print("🔧 Migrando tabla sector...")
                        cur.execute("ALTER TABLE sector RENAME TO sector_old;")
                        cur.execute("""
                        CREATE TABLE sector (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            codigo TEXT UNIQUE NOT NULL,
                            nombre TEXT NOT NULL,
                            descripcion TEXT,
                            comentario TEXT,
                            finca_id INTEGER,
                            estado TEXT DEFAULT 'Activo',
                            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (finca_id) REFERENCES finca(id) ON DELETE SET NULL
                        );
                        """)
                        cur.execute("INSERT INTO sector SELECT * FROM sector_old;")
                        cur.execute("DROP TABLE IF EXISTS sector_old;")
                        print("✔ Sector migrado")
            
            conn.commit()
            print("✔ Migración 008B completada: ahora puedes eliminar fincas sin errores de FK.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error en migración: {e}")
            # Limpiar tablas temporales
            for table in ['potrero_old', 'insumo_old', 'herramienta_old', 'sector_old']:
                try:
                    cur.execute(f"DROP TABLE IF EXISTS {table}")
                except:
                    pass
            raise

if __name__ == "__main__":
    run()
