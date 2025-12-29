#!/usr/bin/env python3
import sys, sqlite3
sys.path.insert(0, '.')
sys.path.insert(0, 'src')
from src.database.database import get_db_path_safe

p = get_db_path_safe()
conn = sqlite3.connect(str(p))
cur = conn.cursor()

# Check reproduccion columns
cur.execute("PRAGMA table_info(reproduccion)")
cols = cur.fetchall()
print('Columnas en reproduccion:')
for r in cols:
    print(f'  {r[1]} ({r[2]})')

conn.close()
