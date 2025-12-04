"""
Migration 007: Agregar campos NIT, dirección, teléfono y email a destino_venta

Agrega columnas faltantes para alinear con la plantilla Excel.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_connection

def run():
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Verificar si las columnas ya existen
        cur.execute("PRAGMA table_info(destino_venta)")
        columns = [row[1] for row in cur.fetchall()]
        
        columns_to_add = {
            'nit': 'TEXT',
            'direccion': 'TEXT',
            'telefono': 'TEXT',
            'email': 'TEXT'
        }
        
        added = []
        for col_name, col_type in columns_to_add.items():
            if col_name not in columns:
                cur.execute(f"ALTER TABLE destino_venta ADD COLUMN {col_name} {col_type}")
                added.append(col_name)
        
        conn.commit()
        
        if added:
            print(f"✔ Migración 007 aplicada: columnas agregadas a destino_venta: {', '.join(added)}")
        else:
            print("➖ Migración 007 omitida: columnas ya existen en destino_venta")

if __name__ == "__main__":
    run()
