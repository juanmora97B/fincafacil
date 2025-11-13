"""
Script para migrar la base de datos al nuevo esquema.
"""
import sqlite3
import os
from database.schema import get_all_create_statements

def migrate_database():
    db_path = "database/fincafacil.db"
    backup_path = "database/fincafacil_backup.db"
    
    # Hacer backup de la base de datos actual
    if os.path.exists(db_path):
        print("Creando backup de la base de datos...")
        import shutil
        shutil.copy2(db_path, backup_path)
    
    # Conectar a la base de datos
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        print("Iniciando migración de la base de datos...")
        
        # Obtener todas las tablas actuales
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        # Crear tablas temporales y migrar datos
        schema_definitions = get_all_create_statements()
        
        for old_name in existing_tables:
            # Convertir nombre plural a singular si es necesario
            new_name = old_name.rstrip('s')
            if new_name in schema_definitions:
                # Crear tabla temporal con nuevo esquema
                temp_name = f"temp_{new_name}"
                cursor.execute(schema_definitions[new_name].replace(
                    f"CREATE TABLE IF NOT EXISTS {new_name}",
                    f"CREATE TABLE {temp_name}"
                ))
                
                # Obtener columnas de ambas tablas
                cursor.execute(f"PRAGMA table_info({old_name})")
                old_columns = [row[1] for row in cursor.fetchall()]
                
                cursor.execute(f"PRAGMA table_info({temp_name})")
                new_columns = [row[1] for row in cursor.fetchall()]
                
                # Encontrar columnas comunes
                common_columns = set(old_columns) & set(new_columns)
                columns_str = ", ".join(common_columns)
                
                # Migrar datos
                print(f"Migrando datos de {old_name} a {new_name}...")
                try:
                    cursor.execute(f"""
                        INSERT INTO {temp_name} ({columns_str})
                        SELECT {columns_str} FROM {old_name}
                    """)
                    
                    # Eliminar tabla antigua
                    cursor.execute(f"DROP TABLE {old_name}")
                    
                    # Renombrar tabla temporal
                    cursor.execute(f"ALTER TABLE {temp_name} RENAME TO {new_name}")
                    
                except sqlite3.Error as e:
                    print(f"Error migrando {old_name}: {e}")
        
        # Crear las tablas nuevas que no existían
        for new_name, create_stmt in schema_definitions.items():
            if new_name not in {t.rstrip('s') for t in existing_tables}:
                try:
                    cursor.execute(create_stmt)
                    print(f"Creada nueva tabla: {new_name}")
                except sqlite3.Error as e:
                    print(f"Error creando {new_name}: {e}")
        
        print("\nActualizando estados...")
        # Actualizar estados para usar consistentemente 'Activo'/'Inactivo'
        tables_with_estado = [
            name for name in schema_definitions.keys()
            if 'estado TEXT' in schema_definitions[name]
        ]
        
        for table in tables_with_estado:
            try:
                # Actualizar estados en femenino a masculino
                cursor.execute(f"""
                    UPDATE {table}
                    SET estado = 'Activo'
                    WHERE estado = 'Activa'
                """)
                cursor.execute(f"""
                    UPDATE {table}
                    SET estado = 'Inactivo'
                    WHERE estado = 'Inactiva'
                """)
            except sqlite3.Error as e:
                print(f"Error actualizando estados en {table}: {e}")
        
        conn.commit()
        print("\nMigración completada exitosamente.")
        print(f"Se ha creado un backup en: {backup_path}")

if __name__ == "__main__":
    migrate_database()