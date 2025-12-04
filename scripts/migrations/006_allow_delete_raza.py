"""
Migration 006: Permitir eliminar razas referenciadas por animales

Modifica la clave foránea raza_id en la tabla animal para que permita ON DELETE SET NULL.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database.database import get_db_connection

def run():
    with get_db_connection() as conn:
        cur = conn.cursor()
        # 1. Renombrar tabla actual
        cur.execute("ALTER TABLE animal RENAME TO animal_old;")
        # 2. Crear nueva tabla con FK ON DELETE SET NULL
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
            FOREIGN KEY (id_finca) REFERENCES finca (id),
            FOREIGN KEY (id_potrero) REFERENCES potrero (id),
            FOREIGN KEY (lote_id) REFERENCES lote (id),
            FOREIGN KEY (id_grupo) REFERENCES grupo (id),
            FOREIGN KEY (id_vendedor) REFERENCES vendedor (id),
            FOREIGN KEY (id_padre) REFERENCES animal (id),
            FOREIGN KEY (id_madre) REFERENCES animal (id)
        );
        """)
        # 3. Copiar datos
        cur.execute("INSERT INTO animal SELECT * FROM animal_old;")
        # 4. Eliminar tabla antigua
        cur.execute("DROP TABLE animal_old;")
        conn.commit()
        print("✔ Migración aplicada: ahora puedes eliminar razas referenciadas por animales.")

if __name__ == "__main__":
    run()
