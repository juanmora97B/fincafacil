import sqlite3
import json

conn = sqlite3.connect('database/fincafacil.db')
cur = conn.cursor()

for table in ('animales','potreros'):
    cur.execute(f"PRAGMA table_info('{table}')")
    rows = cur.fetchall()
    print(f"TABLE {table} schema:")
    print(json.dumps(rows, indent=2, ensure_ascii=False))

conn.close()
