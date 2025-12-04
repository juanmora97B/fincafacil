import sqlite3

conn = sqlite3.connect('fincafacil.db')
cursor = conn.cursor()

# Listar todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 80)
print("TABLAS EN LA BASE DE DATOS")
print("=" * 80)
for table in tables:
    table_name = table[0]
    print(f"\n>>> Tabla: {table_name}")
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    if columns:
        print(f"    Columnas ({len(columns)}):")
        for col in columns:
            col_id, col_name, col_type, notnull, default_val, pk = col
            pk_str = " [PK]" if pk else ""
            notnull_str = " NOT NULL" if notnull else ""
            print(f"      - {col_name} ({col_type}){pk_str}{notnull_str}")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"    Registros: {count}")

conn.close()
