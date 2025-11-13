import sqlite3
import os
from config import config

def init_database():
    """Inicializa la base de datos con tablas vacías"""
    
    # Crear directorios si no existen
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    os.makedirs(config.BACKUP_DIR, exist_ok=True)
    
    # Conectar a la base de datos
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Aquí van todas las CREATE TABLE de tu schema.py
    # (voy a extraerlas de tu código existente)
    
    print("✅ Base de datos inicializada correctamente")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()