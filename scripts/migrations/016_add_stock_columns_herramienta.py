"""
Migración 016: Agregar columnas de stock a herramienta
- stock_total INTEGER DEFAULT 1
- stock_bodega INTEGER DEFAULT 1 (cantidad actualmente en bodega)
Reglas:
  * Para herramientas asignadas a trabajador (id_trabajador NOT NULL) se puede mantener stock_bodega >= 0
  * Se recomienda que si la herramienta representa un único equipo físico individual asignado, stock_total = 1 y stock_bodega = 0
"""
import logging

def run_migration(conn):
    cursor = conn.cursor()
    logging.info("Iniciando migración 016: columnas stock_total, stock_bodega")
    try:
        cursor.execute("PRAGMA table_info(herramienta)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'stock_total' not in cols:
            cursor.execute("ALTER TABLE herramienta ADD COLUMN stock_total INTEGER DEFAULT 1")
            logging.info("✅ Columna stock_total agregada")
        else:
            logging.info("⚠️ Columna stock_total ya existe")
        if 'stock_bodega' not in cols:
            cursor.execute("ALTER TABLE herramienta ADD COLUMN stock_bodega INTEGER DEFAULT 1")
            logging.info("✅ Columna stock_bodega agregada")
        else:
            logging.info("⚠️ Columna stock_bodega ya existe")
        conn.commit()
        logging.info("✅ Migración 016 completada")
    except Exception as e:
        conn.rollback()
        logging.error(f"❌ Error migración 016: {e}")
        raise

if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
    from database import db
    logging.basicConfig(level=logging.INFO)
    with db.get_connection() as conn:
        run_migration(conn)
        try:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO migration_history (version, description, executed_at) VALUES (16, 'Agregar stock_total y stock_bodega a herramienta', datetime('now'))")
            conn.commit()
        except Exception:
            pass
    print("✅ Migración 016 ejecutada")
