"""
Migración final: Corregir FK de sector.finca_id
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

def migrate_sector():
    """Actualiza FK de sector.finca_id a ON DELETE SET NULL"""
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            print("🔧 Migrando tabla sector...")
            
            # Verificar si necesita migración
            cur.execute("PRAGMA foreign_key_list(sector)")
            fks = cur.fetchall()
            needs_fix = any(fk[2] == 'finca' and (len(fk) <= 6 or fk[6] != 'SET NULL') for fk in fks)
            
            if not needs_fix:
                print("✔ sector.finca_id ya tiene ON DELETE SET NULL")
                return
            
            # Deshabilitar FKs temporalmente
            cur.execute("PRAGMA foreign_keys = OFF;")
            
            # Obtener estructura
            cur.execute("PRAGMA table_info(sector)")
            columns = cur.fetchall()
            
            # Renombrar tabla
            cur.execute("ALTER TABLE sector RENAME TO sector_old;")
            
            # Crear nueva tabla
            col_defs = []
            for col in columns:
                name = col[1]
                tipo = col[2]
                notnull = " NOT NULL" if col[3] else ""
                default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                pk = " PRIMARY KEY AUTOINCREMENT" if col[5] and name == 'id' else ""
                col_defs.append(f"{name} {tipo}{pk}{notnull}{default}")
            
            create_sql = f"""
            CREATE TABLE sector (
                {', '.join(col_defs)},
                FOREIGN KEY (finca_id) REFERENCES finca (id) ON DELETE SET NULL
            )
            """
            cur.execute(create_sql)
            
            # Copiar datos
            col_names = [col[1] for col in columns]
            cur.execute(f"INSERT INTO sector ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM sector_old;")
            
            # Eliminar tabla antigua
            cur.execute("DROP TABLE sector_old;")
            
            # Rehabilitar FKs
            cur.execute("PRAGMA foreign_keys = ON;")
            
            conn.commit()
            print("✔ Sector migrado exitosamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            
            # Restaurar si existe temp
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sector_old'")
            if cur.fetchone():
                cur.execute("DROP TABLE IF EXISTS sector;")
                cur.execute("ALTER TABLE sector_old RENAME TO sector;")
                conn.commit()
            raise

if __name__ == "__main__":
    try:
        migrate_sector()
        print("\n✔ Migración completada. Todas las FKs de finca ahora tienen ON DELETE SET NULL")
    except Exception as e:
        print(f"\nError en migración: {e}")
        sys.exit(1)
