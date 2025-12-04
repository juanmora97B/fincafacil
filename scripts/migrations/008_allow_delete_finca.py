"""
Migration 008: Permitir eliminar fincas referenciadas

Modifica las claves foráneas de tablas que referencian finca para usar ON DELETE SET NULL,
permitiendo eliminar fincas sin violar restricciones de integridad.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database.database import get_db_connection

def run():
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Limpiar cualquier tabla temporal residual
        for table in ['animal_old', 'potrero_old', 'insumo_old', 'herramienta_old', 'sector_old']:
            try:
                cur.execute(f"DROP TABLE IF EXISTS {table}")
            except:
                pass
        conn.commit()
        
        try:
            print("🔧 Migrando tabla animal para permitir eliminación de fincas...")
            # Recrear tabla animal con ON DELETE SET NULL para id_finca
            cur.execute("ALTER TABLE animal RENAME TO animal_old;")
            
            cur.execute("""
        CREATE TABLE animal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_finca INTEGER,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT,
            tipo_ingreso TEXT,
            sexo TEXT,
            raza_id INTEGER,
            id_potrero INTEGER,
            lote_id INTEGER,
            id_grupo INTEGER,
            id_vendedor INTEGER,
            fecha_nacimiento DATE,
            fecha_compra DATE,
            peso_nacimiento REAL,
            peso_compra REAL,
            precio_compra REAL,
            id_padre INTEGER,
            id_madre INTEGER,
            tipo_concepcion TEXT,
            salud TEXT,
            estado TEXT DEFAULT 'Activo',
            inventariado INTEGER DEFAULT 0,
            color TEXT,
            hierro TEXT,
            numero_hierros INTEGER,
            composicion_racial TEXT,
            comentarios TEXT,
            foto_path TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (raza_id) REFERENCES raza (id) ON DELETE SET NULL,
            FOREIGN KEY (id_finca) REFERENCES finca (id) ON DELETE SET NULL,
            FOREIGN KEY (id_potrero) REFERENCES potrero (id) ON DELETE SET NULL,
            FOREIGN KEY (lote_id) REFERENCES lote (id) ON DELETE SET NULL,
            FOREIGN KEY (id_grupo) REFERENCES grupo (id) ON DELETE SET NULL,
            FOREIGN KEY (id_vendedor) REFERENCES vendedor (id) ON DELETE SET NULL,
            FOREIGN KEY (id_padre) REFERENCES animal (id) ON DELETE SET NULL,
            FOREIGN KEY (id_madre) REFERENCES animal (id) ON DELETE SET NULL
            );
            """)
            
            cur.execute("INSERT INTO animal SELECT * FROM animal_old;")
            cur.execute("DROP TABLE IF EXISTS animal_old;")
            
            print("🔧 Migrando tabla potrero para permitir eliminación de fincas...")
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
            
            # Verificar si existen tablas insumo y herramienta
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='insumo'")
            if cur.fetchone():
                print("🔧 Migrando tabla insumo...")
                # Obtener columnas actuales
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
                # Copiar solo columnas existentes
                cols_new = ['id', 'codigo', 'nombre', 'categoria', 'descripcion', 'unidad_medida', 
                           'stock_actual', 'stock_minimo', 'stock_maximo', 'precio_unitario', 
                           'id_finca', 'ubicacion', 'proveedor_principal', 'fecha_vencimiento', 
                           'lote_proveedor', 'estado', 'fecha_creacion']
                cols_to_copy = [c for c in cols_new if c in cols_old]
                cols_str = ', '.join(cols_to_copy)
                cur.execute(f"INSERT INTO insumo ({cols_str}) SELECT {cols_str} FROM insumo_old;")
                cur.execute("DROP TABLE IF EXISTS insumo_old;")
            
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='herramienta'")
            if cur.fetchone():
                print("🔧 Migrando tabla herramienta...")
                # Obtener columnas actuales
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
                # Copiar solo columnas existentes
                cols_new = ['id', 'codigo', 'nombre', 'categoria', 'descripcion', 'marca', 'modelo',
                           'numero_serie', 'id_finca', 'ubicacion', 'estado', 'fecha_adquisicion',
                           'valor_adquisicion', 'vida_util_anos', 'responsable', 'observaciones',
                           'fecha_creacion']
                cols_to_copy = [c for c in cols_new if c in cols_old]
                cols_str = ', '.join(cols_to_copy)
                cur.execute(f"INSERT INTO herramienta ({cols_str}) SELECT {cols_str} FROM herramienta_old;")
                cur.execute("DROP TABLE IF EXISTS herramienta_old;")
        
            # Migrar tabla sector si existe finca_id
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sector'")
            if cur.fetchone():
                cur.execute("PRAGMA table_info(sector)")
                cols = [row[1] for row in cur.fetchall()]
                if 'finca_id' in cols:
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
            
            conn.commit()
            print("✔ Migración 008 aplicada: ahora puedes eliminar fincas sin errores de FK.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error en migración: {e}")
            # Limpiar tablas temporales en caso de error
            for table in ['animal_old', 'potrero_old', 'insumo_old', 'herramienta_old', 'sector_old']:
                try:
                    cur.execute(f"DROP TABLE IF EXISTS {table}")
                except:
                    pass
            raise

if __name__ == "__main__":
    run()
