"""
Migración final: Corregir FK de lote.finca_id
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

def migrate_lote():
    """Actualiza FK de lote.finca_id a ON DELETE SET NULL"""
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            print("🔧 Migrando tabla lote...")
            
            # Deshabilitar FKs temporalmente
            cur.execute("PRAGMA foreign_keys = OFF;")
            
            # Obtener estructura
            cur.execute("PRAGMA table_info(lote)")
            columns = cur.fetchall()
            
            # Renombrar tabla
            cur.execute("ALTER TABLE lote RENAME TO lote_old;")
            
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
            CREATE TABLE lote (
                {', '.join(col_defs)},
                FOREIGN KEY (finca_id) REFERENCES finca (id) ON DELETE SET NULL
            )
            """
            cur.execute(create_sql)
            
            # Copiar datos
            col_names = [col[1] for col in columns]
            cur.execute(f"INSERT INTO lote ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM lote_old;")
            
            # Eliminar tabla antigua
            cur.execute("DROP TABLE lote_old;")
            
            # Rehabilitar FKs
            cur.execute("PRAGMA foreign_keys = ON;")
            
            conn.commit()
            print("✔ Lote migrado exitosamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            
            # Restaurar si existe temp
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lote_old'")
            if cur.fetchone():
                cur.execute("DROP TABLE IF EXISTS lote;")
                cur.execute("ALTER TABLE lote_old RENAME TO lote;")
                conn.commit()
            raise

if __name__ == "__main__":
    try:
        migrate_lote()
        print("\n✔ Migración completada. lote.finca_id ahora tiene ON DELETE SET NULL")
    except Exception as e:
        print(f"\nError en migración: {e}")
        sys.exit(1)
