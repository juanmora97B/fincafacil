"""Migration 001: Add extended domain tables (peso, produccion_leche, muerte, diagnostico_evento).

Safe to run multiple times; creates tables if they don't exist.
"""
from datetime import datetime
import sqlite3
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database.database import get_db_connection

# New tables DDL (kept minimal; can be evolved later)
DDL_STATEMENTS = [
    # Individual weight records (historical growth tracking)
    """
    CREATE TABLE IF NOT EXISTS peso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        peso REAL NOT NULL,
        metodo TEXT, -- 'Báscula', 'Estimado'
        observaciones TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(animal_id, fecha),
        FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
    );
    """,
    # Daily milk production (per animal) - aggregate queries can roll up per finca/lote
    """
    CREATE TABLE IF NOT EXISTS produccion_leche (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        litros_manana REAL DEFAULT 0,
        litros_tarde REAL DEFAULT 0,
        litros_noche REAL DEFAULT 0,
        observaciones TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(animal_id, fecha),
        FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
    );
    """,
    # Mortalidad registry (cause of death & basic necropsy info)
    """
    CREATE TABLE IF NOT EXISTS muerte (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        causa TEXT, -- free text or matches catalog futura 'causa_muerte'
        diagnostico_presuntivo TEXT,
        diagnostico_confirmado TEXT,
        observaciones TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(animal_id), -- a single definitive death record per animal
        FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
    );
    """,
    # Health / diagnostic events (unified lightweight log)
    """
    CREATE TABLE IF NOT EXISTS diagnostico_evento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        tipo TEXT, -- 'Diagnostico','Tratamiento','Vacunacion','Sintoma'
        detalle TEXT, -- description or catalog code
        severidad TEXT, -- 'Leve','Moderado','Grave'
        estado TEXT, -- 'Activo','Resuelto'
        observaciones TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
    );
    """,
]

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_peso_animal_fecha ON peso(animal_id, fecha);",
    "CREATE INDEX IF NOT EXISTS idx_leche_animal_fecha ON produccion_leche(animal_id, fecha);",
    "CREATE INDEX IF NOT EXISTS idx_muerte_animal ON muerte(animal_id);",
    "CREATE INDEX IF NOT EXISTS idx_diag_evento_animal_fecha ON diagnostico_evento(animal_id, fecha);",
]


def run():
    """Execute migration: create extended domain tables & indexes."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        for ddl in DDL_STATEMENTS:
            cur.execute(ddl)
        for idx in INDEX_STATEMENTS:
            cur.execute(idx)
        conn.commit()

if __name__ == "__main__":
    run()
    print("✅ Migration 001 applied (extended domain tables)")
