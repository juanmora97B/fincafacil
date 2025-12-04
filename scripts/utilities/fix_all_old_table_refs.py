"""
Corrección masiva: Actualizar todas las FKs que apuntan a tablas *_old
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.database import get_db_connection

def fix_table_fks(table_name, fk_corrections):
    """
    Corrige FKs de una tabla
    fk_corrections: dict {column_name: (old_table, new_table)}
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        try:
            print(f"\n🔧 Corrigiendo {table_name}...")
            
            # Deshabilitar FKs temporalmente
            cur.execute("PRAGMA foreign_keys = OFF;")
            
            # Obtener estructura actual
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()
            
            # Obtener FKs actuales
            cur.execute(f"PRAGMA foreign_key_list({table_name})")
            current_fks = cur.fetchall()
            
            # Construir definiciones de columnas
            col_defs = []
            for col in columns:
                name = col[1]
                tipo = col[2]
                notnull = " NOT NULL" if col[3] else ""
                default = f" DEFAULT {col[4]}" if col[4] is not None else ""
                pk = " PRIMARY KEY AUTOINCREMENT" if col[5] and name == 'id' else ""
                col_defs.append(f"{name} {tipo}{pk}{notnull}{default}")
            
            # Construir FKs corregidas
            fk_defs = []
            for fk in current_fks:
                column = fk[3]
                ref_table = fk[2]
                ref_column = fk[4]
                on_delete = fk[6] if len(fk) > 6 else 'NO ACTION'
                
                # Corregir si es necesario
                if column in fk_corrections and ref_table == fk_corrections[column][0]:
                    ref_table = fk_corrections[column][1]
                
                fk_defs.append(f"FOREIGN KEY ({column}) REFERENCES {ref_table} ({ref_column}) ON DELETE {on_delete}")
            
            # Renombrar tabla
            cur.execute(f"ALTER TABLE {table_name} RENAME TO {table_name}_fix_temp;")
            
            # Crear nueva tabla
            all_defs = col_defs + fk_defs
            create_sql = f"CREATE TABLE {table_name} ({', '.join(all_defs)})"
            cur.execute(create_sql)
            
            # Copiar datos
            col_names = [col[1] for col in columns]
            cur.execute(f"INSERT INTO {table_name} ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM {table_name}_fix_temp;")
            
            # Eliminar tabla temporal
            cur.execute(f"DROP TABLE {table_name}_fix_temp;")
            
            # Rehabilitar FKs
            cur.execute("PRAGMA foreign_keys = ON;")
            
            conn.commit()
            print(f"✔ {table_name} corregido")
            
        except Exception as e:
            print(f"❌ Error en {table_name}: {e}")
            conn.rollback()
            
            # Restaurar si existe temp
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}_fix_temp'")
            if cur.fetchone():
                cur.execute(f"DROP TABLE IF EXISTS {table_name};")
                cur.execute(f"ALTER TABLE {table_name}_fix_temp RENAME TO {table_name};")
                conn.commit()
            raise

def run_all_fixes():
    """Ejecuta todas las correcciones necesarias"""
    
    fixes = [
        ('movimiento', {
            'lote_destino_id': ('lote_old', 'lote'),
            'lote_origen_id': ('lote_old', 'lote')
        }),
        ('evento', {
            'lote_id': ('lote_old', 'lote')
        }),
        ('comentario', {
            'id_animal': ('animal_old', 'animal')
        }),
        ('mantenimiento_herramienta', {
            'herramienta_id': ('herramienta_old', 'herramienta')
        }),
        ('servicio', {
            'id_macho': ('animal_old', 'animal'),
            'id_hembra': ('animal_old', 'animal')
        })
    ]
    
    print("=" * 60)
    print("CORRECCIÓN MASIVA DE FKs A TABLAS *_old")
    print("=" * 60)
    
    for table, corrections in fixes:
        fix_table_fks(table, corrections)
    
    print("\n" + "=" * 60)
    print("✔ CORRECCIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_all_fixes()
    except Exception as e:
        print(f"\nError en corrección masiva: {e}")
        sys.exit(1)
