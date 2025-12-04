"""
Migración 003: Agregar tablas de herramientas e insumos
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "fincafacil.db"

def aplicar_migracion():
    """Aplica la migración para agregar tablas de herramientas e insumos"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar si las tablas ya existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='insumo'")
        if cursor.fetchone():
            print("⏭️  Migración 003 omitida: Las tablas ya existen")
            return
        
        print("📦 Aplicando migración 003: Herramientas e Insumos...")
        
        # Crear tabla de insumos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insumo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                categoria TEXT CHECK(categoria IN ('Medicamento', 'Alimento', 'Fertilizante', 'Semilla', 'Herramienta', 'Otro')) NOT NULL,
                descripcion TEXT,
                unidad_medida TEXT NOT NULL,
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
                FOREIGN KEY (id_finca) REFERENCES finca(id)
            )
        """)
        
        # Crear tabla de movimientos de insumos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimiento_insumo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                insumo_id INTEGER NOT NULL,
                tipo_movimiento TEXT CHECK(tipo_movimiento IN ('Entrada', 'Salida', 'Ajuste')) NOT NULL,
                cantidad REAL NOT NULL,
                motivo TEXT,
                referencia TEXT,
                animal_id INTEGER,
                potrero_id INTEGER,
                usuario TEXT,
                costo_unitario REAL,
                costo_total REAL,
                observaciones TEXT,
                fecha_movimiento DATE NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (insumo_id) REFERENCES insumo(id) ON DELETE CASCADE,
                FOREIGN KEY (animal_id) REFERENCES animal(id),
                FOREIGN KEY (potrero_id) REFERENCES potrero(id)
            )
        """)
        
        # Crear tabla de herramientas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS herramienta (
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
                estado TEXT CHECK(estado IN ('Operativa', 'En Mantenimiento', 'Dañada', 'Fuera de Servicio')) DEFAULT 'Operativa',
                fecha_adquisicion DATE,
                valor_adquisicion REAL,
                vida_util_anos INTEGER,
                responsable TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_finca) REFERENCES finca(id)
            )
        """)
        
        # Crear tabla de mantenimientos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mantenimiento_herramienta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                herramienta_id INTEGER NOT NULL,
                tipo_mantenimiento TEXT CHECK(tipo_mantenimiento IN ('Preventivo', 'Correctivo', 'Calibración', 'Inspección')),
                fecha_mantenimiento DATE NOT NULL,
                descripcion TEXT,
                costo REAL,
                proveedor_servicio TEXT,
                proximo_mantenimiento DATE,
                realizado_por TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
            )
        """)
        
        # Crear índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_insumo_codigo ON insumo (codigo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_insumo_finca ON insumo (id_finca)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_insumo_categoria ON insumo (categoria)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mov_insumo_insumo ON movimiento_insumo (insumo_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mov_insumo_fecha ON movimiento_insumo (fecha_movimiento)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_codigo ON herramienta (codigo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_herramienta_finca ON herramienta (id_finca)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mant_herramienta ON mantenimiento_herramienta (herramienta_id)")
        
        conn.commit()
        print("✅ Migración 003 aplicada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en migración 003: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    aplicar_migracion()
