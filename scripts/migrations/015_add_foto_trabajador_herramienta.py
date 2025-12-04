"""
Migración 015: Agregar campos foto_path e id_trabajador a herramienta
- Agrega columna foto_path para almacenar ruta de imagen de la herramienta
- Agrega columna id_trabajador para vincular con trabajador (nómina)
- Mantiene compatibilidad con campo responsable TEXT existente
"""
import sqlite3
import logging

def run_migration(conn):
    """Ejecuta la migración 015"""
    cursor = conn.cursor()
    
    try:
        logging.info("Iniciando migración 015: Agregar foto_path e id_trabajador a herramienta")
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(herramienta)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Agregar foto_path si no existe
        if 'foto_path' not in columns:
            cursor.execute("ALTER TABLE herramienta ADD COLUMN foto_path TEXT")
            logging.info("✅ Columna foto_path agregada a herramienta")
        else:
            logging.info("⚠️ Columna foto_path ya existe")
        
        # Agregar id_trabajador si no existe
        if 'id_trabajador' not in columns:
            cursor.execute("ALTER TABLE herramienta ADD COLUMN id_trabajador INTEGER")
            logging.info("✅ Columna id_trabajador agregada a herramienta")
        else:
            logging.info("⚠️ Columna id_trabajador ya existe")
        
        # Agregar foreign key manualmente (SQLite no soporta ADD CONSTRAINT en ALTER)
        # La FK se validará en el código de la aplicación
        
        conn.commit()
        logging.info("✅ Migración 015 completada exitosamente")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error en migración 015: {e}")
        conn.rollback()
        raise

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
    from database import db
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        with db.get_connection() as conn:
            run_migration(conn)
            # Registrar migración
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO migration_history (version, description, executed_at)
                VALUES (15, 'Agregar foto_path e id_trabajador a herramienta', datetime('now'))
            """)
            conn.commit()
            print("✅ Migración 015 ejecutada exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
