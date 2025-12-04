"""
Reconstrucción completa y correcta de tabla animal con FKs bien ordenadas
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.database import get_db_connection

def rebuild_animal_table():
    """Reconstruye la tabla animal con FKs correctamente definidas"""
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            print("🔧 Reconstruyendo tabla animal...")
            
            # Deshabilitar FKs temporalmente
            cur.execute("PRAGMA foreign_keys = OFF;")
            
            # Respaldar datos
            cur.execute("ALTER TABLE animal RENAME TO animal_backup;")
            print("✔ Datos respaldados en animal_backup")
            
            # Crear tabla nueva con definición limpia y correcta
            cur.execute("""
                CREATE TABLE animal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_finca INTEGER,
                    codigo TEXT NOT NULL,
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
                )
            """)
            print("✔ Tabla nueva creada con definición limpia")
            
            # Copiar datos
            cur.execute("""
                INSERT INTO animal SELECT * FROM animal_backup
            """)
            rows_copied = cur.rowcount
            print(f"✔ {rows_copied} registros copiados")
            
            # Eliminar backup
            cur.execute("DROP TABLE animal_backup;")
            print("✔ Backup eliminado")
            
            # Rehabilitar FKs
            cur.execute("PRAGMA foreign_keys = ON;")
            
            # Verificar integridad
            cur.execute("PRAGMA foreign_key_check(animal);")
            fk_errors = cur.fetchall()
            
            if fk_errors:
                print(f"\n⚠ Advertencia: {len(fk_errors)} errores de integridad FK:")
                for err in fk_errors[:5]:  # Mostrar solo primeros 5
                    print(f"  - {err}")
            else:
                print("\n✔ Verificación de integridad FK: OK")
            
            conn.commit()
            print("\n✔ TABLA ANIMAL RECONSTRUIDA EXITOSAMENTE")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            conn.rollback()
            
            # Restaurar backup si existe
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal_backup'")
            if cur.fetchone():
                print("🔄 Restaurando backup...")
                cur.execute("DROP TABLE IF EXISTS animal;")
                cur.execute("ALTER TABLE animal_backup RENAME TO animal;")
                cur.execute("PRAGMA foreign_keys = ON;")
                conn.commit()
                print("✔ Backup restaurado")
            raise

if __name__ == "__main__":
    try:
        rebuild_animal_table()
    except Exception as e:
        print(f"\nError fatal: {e}")
        sys.exit(1)
