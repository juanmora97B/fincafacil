"""
Corrección: Actualizar FKs que apuntan a potrero_old en animal_legacy y movimiento_insumo
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database import get_connection

def fix_potrero_old_references():
    """Corrige todas las FKs que apuntan a potrero_old"""
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        try:
            # Deshabilitar FKs temporalmente
            cur.execute("PRAGMA foreign_keys = OFF;")
            
            # FIX 1: animal_legacy
            print("🔧 Corrigiendo animal_legacy.id_potrero...")
            cur.execute("PRAGMA table_info(animal_legacy)")
            columns = cur.fetchall()
            
            if columns:
                col_defs = []
                for col in columns:
                    name = col[1]
                    tipo = col[2]
                    notnull = " NOT NULL" if col[3] else ""
                    default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                    col_defs.append(f"{name} {tipo}{notnull}{default}")
                
                cur.execute("ALTER TABLE animal_legacy RENAME TO animal_legacy_temp;")
                
                create_sql = f"""
                CREATE TABLE animal_legacy (
                    {', '.join(col_defs)},
                    FOREIGN KEY (id_potrero) REFERENCES potrero (id) ON DELETE SET NULL,
                    FOREIGN KEY (id_finca) REFERENCES finca (id) ON DELETE SET NULL
                )
                """
                cur.execute(create_sql)
                
                col_names = [col[1] for col in columns]
                cur.execute(f"INSERT INTO animal_legacy SELECT * FROM animal_legacy_temp;")
                cur.execute("DROP TABLE animal_legacy_temp;")
                print("✔ animal_legacy corregido")
            
            # FIX 2: movimiento_insumo
            print("🔧 Corrigiendo movimiento_insumo.potrero_id...")
            cur.execute("PRAGMA table_info(movimiento_insumo)")
            columns = cur.fetchall()
            
            if columns:
                col_defs = []
                for col in columns:
                    name = col[1]
                    tipo = col[2]
                    notnull = " NOT NULL" if col[3] else ""
                    default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                    col_defs.append(f"{name} {tipo}{notnull}{default}")
                
                cur.execute("ALTER TABLE movimiento_insumo RENAME TO movimiento_insumo_temp;")
                
                create_sql = f"""
                CREATE TABLE movimiento_insumo (
                    {', '.join(col_defs)},
                    FOREIGN KEY (insumo_id) REFERENCES insumo (id) ON DELETE CASCADE,
                    FOREIGN KEY (potrero_id) REFERENCES potrero (id) ON DELETE SET NULL
                )
                """
                cur.execute(create_sql)
                
                col_names = [col[1] for col in columns]
                cur.execute(f"INSERT INTO movimiento_insumo SELECT * FROM movimiento_insumo_temp;")
                cur.execute("DROP TABLE movimiento_insumo_temp;")
                print("✔ movimiento_insumo corregido")
            
            # Rehabilitar FKs
            cur.execute("PRAGMA foreign_keys = ON;")
            
            conn.commit()
            print("\n✔ Todas las referencias a potrero_old corregidas")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    try:
        fix_potrero_old_references()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)
