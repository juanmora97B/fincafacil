"""
Migración 004: Agregar tabla servicio para gestión de reproducción
"""
import sqlite3
from pathlib import Path

def migrate(conn: sqlite3.Connection):
    """Ejecuta la migración"""
    cursor = conn.cursor()
    
    # Verificar si la tabla ya existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='servicio'
    """)
    
    if cursor.fetchone():
        print("✓ Tabla 'servicio' ya existe, saltando migración")
        return
    
    print("Creando tabla 'servicio'...")
    
    # Crear tabla de servicios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_hembra INTEGER NOT NULL,
            id_macho INTEGER,
            fecha_servicio DATE NOT NULL,
            tipo_servicio TEXT CHECK(tipo_servicio IN ('Monta Natural', 'Inseminación Artificial')),
            estado TEXT DEFAULT 'Servida' CHECK(estado IN ('Servida', 'Gestante', 'Vacía', 'Parida', 'Aborto')),
            fecha_parto_estimada DATE,
            fecha_parto_real DATE,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_hembra) REFERENCES animal (id),
            FOREIGN KEY (id_macho) REFERENCES animal (id)
        )
    """)
    
    conn.commit()
    print("✓ Tabla 'servicio' creada correctamente")

def rollback(conn: sqlite3.Connection):
    """Revierte la migración"""
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS servicio")
    conn.commit()
    print("✓ Tabla 'servicio' eliminada")

if __name__ == "__main__":
    # Para pruebas
    db_path = Path(__file__).parent.parent.parent / "database" / "fincafacil.db"
    
    if not db_path.exists():
        print(f"Base de datos no encontrada en: {db_path}")
        exit(1)
    
    conn = sqlite3.connect(db_path)
    
    try:
        migrate(conn)
        print("\n✅ Migración completada exitosamente")
    except Exception as e:
        print(f"\n❌ Error en migración: {e}")
        conn.rollback()
    finally:
        conn.close()
