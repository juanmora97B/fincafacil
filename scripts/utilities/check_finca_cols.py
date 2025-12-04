import sys, os
sys.path.insert(0, os.path.abspath('.'))
from database.database import get_db_connection

with get_db_connection() as conn:
    cur = conn.cursor()
    print("Columnas de tabla finca:")
    for col in cur.execute('PRAGMA table_info(finca)').fetchall():
        print(f"  {col[1]} {col[2]}")
    
    print("\nColumnas de tabla potrero:")
    for col in cur.execute('PRAGMA table_info(potrero)').fetchall():
        print(f"  {col[1]} {col[2]}")
