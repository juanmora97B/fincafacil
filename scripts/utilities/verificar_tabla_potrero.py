"""Verificar estructura de la tabla potrero."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database import db

with db.get_connection() as conn:
    cursor = conn.cursor()
    
    print("=== ESTRUCTURA DE LA TABLA POTRERO ===\n")
    cursor.execute("PRAGMA table_info(potrero)")
    columnas = cursor.fetchall()
    
    for col in columnas:
        print(f"{col[1]} ({col[2]})" + (" - NOT NULL" if col[3] else ""))
