"""
Corrección urgente: animal.lote_id apunta a lote_old en lugar de lote
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

def fix_animal_lote_fk():
    """Corrige FK de animal.lote_id para que apunte a lote en lugar de lote_old"""
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            print("🔧 Corrigiendo FK animal.lote_id...")
            
            # Verificar estado actual
            cur.execute("PRAGMA foreign_key_list(animal)")
            fks = cur.fetchall()
            lote_fk = next((fk for fk in fks if fk[3] == 'lote_id'), None)
            
            if lote_fk and lote_fk[2] == 'lote_old':
                print("❌ Confirmado: animal.lote_id apunta a lote_old")
                print("🔄 Recreando tabla animal con FK correcta...")
                
                # Deshabilitar FKs temporalmente para auto-referencia
                cur.execute("PRAGMA foreign_keys = OFF;")
                
                # Obtener estructura actual
                cur.execute("PRAGMA table_info(animal)")
                columns = cur.fetchall()
                col_defs = []
                
                for col in columns:
                    name = col[1]
                    tipo = col[2]
                    notnull = " NOT NULL" if col[3] else ""
                    default = f" DEFAULT {col[4]}" if col[4] else ""
                    col_defs.append(f"{name} {tipo}{notnull}{default}")
                
                # Renombrar tabla actual
                cur.execute("ALTER TABLE animal RENAME TO animal_fix_temp;")
                
                # Crear nueva tabla con FK correctas
                create_sql = f"""
                CREATE TABLE animal (
                    {', '.join(col_defs)},
                    FOREIGN KEY (id_madre) REFERENCES animal (id) ON DELETE SET NULL,
                    FOREIGN KEY (id_padre) REFERENCES animal (id) ON DELETE SET NULL,
                    FOREIGN KEY (id_vendedor) REFERENCES vendedor (id) ON DELETE SET NULL,
                    FOREIGN KEY (id_grupo) REFERENCES grupo (id) ON DELETE SET NULL,
                    FOREIGN KEY (lote_id) REFERENCES lote (id) ON DELETE SET NULL,
                    FOREIGN KEY (id_potrero) REFERENCES potrero (id) ON DELETE SET NULL,
                    FOREIGN KEY (id_finca) REFERENCES finca (id) ON DELETE SET NULL,
                    FOREIGN KEY (raza_id) REFERENCES raza (id) ON DELETE SET NULL
                )
                """
                cur.execute(create_sql)
                
                # Copiar datos
                col_names = [col[1] for col in columns]
                cur.execute(f"INSERT INTO animal ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM animal_fix_temp;")
                
                # Eliminar tabla temporal
                cur.execute("DROP TABLE animal_fix_temp;")
                
                # Rehabilitar FKs
                cur.execute("PRAGMA foreign_keys = ON;")
                
                conn.commit()
                print("✔ animal.lote_id ahora apunta correctamente a lote")
                
            else:
                print("✔ animal.lote_id ya apunta correctamente a lote")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            # Restaurar si existe temp
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal_fix_temp'")
            if cur.fetchone():
                cur.execute("DROP TABLE IF EXISTS animal;")
                cur.execute("ALTER TABLE animal_fix_temp RENAME TO animal;")
                conn.commit()
            raise

if __name__ == "__main__":
    try:
        fix_animal_lote_fk()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)
