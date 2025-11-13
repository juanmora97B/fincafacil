"""
Script para migrar datos entre tablas duplicadas.
"""
import sqlite3
from pathlib import Path

def migrate_table_data(cursor, old_table, new_table, common_columns=None):
    """Migra datos de una tabla antigua a una nueva"""
    try:
        # Obtener info de columnas (incluye flag pk)
        cursor.execute(f"PRAGMA table_info({old_table})")
        old_info = cursor.fetchall()
        old_columns = [row[1] for row in old_info]

        cursor.execute(f"PRAGMA table_info({new_table})")
        new_info = cursor.fetchall()
        new_columns = [row[1] for row in new_info]

        # detectar PK en tabla antigua (si existe)
        old_pk = None
        for col in old_info:
            # PRAGMA tuple: (cid, name, type, notnull, dflt_value, pk)
            if col[5]:
                old_pk = col[1]
                break

        # Usar columnas comunes si no se especifican
        if common_columns is None:
            # construiremos la lista de columnas a insertar respetando el orden de la tabla nueva
            common_columns = []
            for col in new_columns:
                if col in old_columns:
                    common_columns.append(col)
                elif col == 'codigo' and 'codigo' not in old_columns:
                    # permitimos generar 'codigo' a partir de la PK antigua si hace falta
                    common_columns.append(col)

        if not common_columns:
            print(f"⚠️ No se encontraron columnas comunes entre {old_table} y {new_table}")
            return False

        # Verificar si hay datos para migrar
        cursor.execute(f"SELECT COUNT(*) FROM {old_table}")
        count = cursor.fetchone()[0]

        if count == 0:
            print(f"ℹ️ No hay datos para migrar en {old_table}")
            return True

        # Preparar columnas e expressions para el SELECT (generar codigo si hace falta)
        insert_cols = []
        select_exprs = []
        for col in common_columns:
            insert_cols.append(col)
            if col == 'codigo' and col not in old_columns:
                # generar codigo a partir de la PK antigua, o usar rowid como último recurso
                if old_pk:
                    select_exprs.append(f"('V' || CAST({old_pk} AS TEXT)) AS codigo")
                else:
                    select_exprs.append("('V' || CAST(rowid AS TEXT)) AS codigo")
            else:
                select_exprs.append(col)

        columns_str = ", ".join(insert_cols)
        select_str = ", ".join(select_exprs)

        # Construir condición de existencia para evitar duplicados
        not_exists_cond = None
        if 'codigo' in new_columns:
            if 'codigo' in old_columns:
                not_exists_cond = f"n.codigo = {old_table}.codigo"
            elif old_pk:
                not_exists_cond = f"n.codigo = ('V' || CAST({old_table}.{old_pk} AS TEXT))"

        not_exists_sql = ''
        if not_exists_cond:
            not_exists_sql = f"WHERE NOT EXISTS (SELECT 1 FROM {new_table} n WHERE {not_exists_cond})"

        sql = f"INSERT INTO {new_table} ({columns_str}) SELECT {select_str} FROM {old_table} {not_exists_sql}"

        cursor.execute(sql)

        migrated = cursor.rowcount
        print(f"✅ Migrados {migrated} registros de {old_table} a {new_table}")
        return True

    except Exception as e:
        print(f"❌ Error migrando {old_table} a {new_table}: {e}")
        return False

def complete_migration():
    """Completa la migración de datos entre tablas duplicadas"""
    db_path = Path("database/fincafacil.db")
    if not db_path.exists():
        print("❌ No se encontró la base de datos.")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Lista de tablas a migrar (antigua -> nueva)
            migrations = [
                ('animales', 'animal'),
                ('condiciones_corporales', 'condicion_corporal'),
                ('destinos_ventas', 'destino_venta'),
                ('destinos_venta', 'destino_venta'),
                ('diagnosticos_veterinarios', 'diagnostico_veterinario'),
                ('sectores', 'sector'),
                ('tipos_explotacion', 'tipo_explotacion'),
                ('motivos_venta', 'motivo_venta'),
                ('causas_muerte', 'causa_muerte'),
                ('proveedores', 'proveedor'),
                ('vendedores', 'vendedor'),
                ('reubicaciones', 'reubicacion')
            ]
            
            print("\n🔄 Iniciando migración final de datos...")
            all_success = True
            
            for old_table, new_table in migrations:
                print(f"\n📦 Migrando {old_table} → {new_table}")
                if not migrate_table_data(cursor, old_table, new_table):
                    all_success = False
            
            if all_success:
                # Eliminar tablas antiguas
                for old_table, _ in migrations:
                    try:
                        cursor.execute(f"DROP TABLE IF EXISTS {old_table}")
                        print(f"🗑️ Eliminada tabla antigua: {old_table}")
                    except Exception as e:
                        print(f"⚠️ Error eliminando {old_table}: {e}")
                        all_success = False
            
            conn.commit()
            
            if all_success:
                print("\n✅ Migración completada exitosamente")
            else:
                print("\n⚠️ Migración completada con errores")
                
            return all_success
            
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    complete_migration()