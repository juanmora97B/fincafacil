#!/usr/bin/env python3
"""
Database schema update script for FincaFácil v2.0
Adds missing columns and views to support latest module versions
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "fincafacil.db"

def update_database():
    """Apply all pending database updates"""
    print("FincaFácil Database Updater")
    print("=" * 50)
    
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # 1. Update comentario table
        print("\n[1] Updating 'comentario' table...")
        cursor.execute("PRAGMA table_info(comentario);")
        cols = [row[1] for row in cursor.fetchall()]
        
        updates = [
            ('tipo', "TEXT DEFAULT 'General'"),
            ('usuario', "TEXT DEFAULT 'Sistema'"),
            ('adjunto', "TEXT DEFAULT NULL")
        ]
        
        for col_name, col_def in updates:
            if col_name not in cols:
                try:
                    cursor.execute(f"ALTER TABLE comentario ADD COLUMN {col_name} {col_def}")
                    print(f"    + Added column '{col_name}'")
                except Exception as e:
                    print(f"    ! Column '{col_name}' already exists or error: {e}")
        
        # 2. Update venta table
        print("\n[2] Updating 'venta' table...")
        cursor.execute("PRAGMA table_info(venta);")
        cols = [row[1] for row in cursor.fetchall()]
        
        updates = [
            ('comprador', "TEXT DEFAULT NULL"),
            ('vendedor', "TEXT DEFAULT NULL")
        ]
        
        for col_name, col_def in updates:
            if col_name not in cols:
                try:
                    cursor.execute(f"ALTER TABLE venta ADD COLUMN {col_name} {col_def}")
                    print(f"    + Added column '{col_name}'")
                except Exception as e:
                    print(f"    ! Column '{col_name}' already exists or error: {e}")
        
        # 3. Create diagnostico_veterinario view
        print("\n[3] Creating 'diagnostico_veterinario' view...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name='diagnostico_veterinario'
        """)
        
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    CREATE VIEW diagnostico_veterinario AS 
                    SELECT * FROM diagnostico_evento
                """)
                print("    + Created view 'diagnostico_veterinario'")
            except Exception as e:
                print(f"    ! Error creating view: {e}")
        else:
            print("    ! View 'diagnostico_veterinario' already exists")
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("Database update completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == "__main__":
    success = update_database()
    sys.exit(0 if success else 1)
