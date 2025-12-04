"""
Script para corregir las FK que apuntan a animal_legacy_temp
Las cambia para que apunten a la tabla 'animal' correcta
"""
import sqlite3
import sys

def corregir_foreign_keys():
    conn = sqlite3.connect('database/fincafacil.db')
    cursor = conn.cursor()
    
    try:
        print("\n🔧 Corrigiendo claves foráneas...\n")
        
        # Deshabilitar FKs temporalmente
        cursor.execute("PRAGMA foreign_keys=OFF")
        
        # 1. REPRODUCCION
        print("1️⃣ Corrigiendo tabla 'reproduccion'...")
        cursor.execute("DROP TABLE IF EXISTS reproduccion_backup")
        cursor.execute("ALTER TABLE reproduccion RENAME TO reproduccion_backup")
        cursor.execute("""
            CREATE TABLE reproduccion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha_cubricion DATE,
                fecha_parto DATE,
                tipo_cubricion TEXT CHECK(tipo_cubricion IN ('Natural', 'Inseminacion')),
                estado TEXT CHECK(estado IN ('Gestante', 'Parida', 'Vacía', 'Aborto')),
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO reproduccion SELECT * FROM reproduccion_backup")
        cursor.execute("DROP TABLE reproduccion_backup")
        print("   ✅ reproduccion OK")
        
        # 2. TRATAMIENTO
        print("2️⃣ Corrigiendo tabla 'tratamiento'...")
        cursor.execute("DROP TABLE IF EXISTS tratamiento_backup")
        cursor.execute("ALTER TABLE tratamiento RENAME TO tratamiento_backup")
        cursor.execute("""
            CREATE TABLE tratamiento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_animal INTEGER NOT NULL,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE,
                tipo_tratamiento TEXT NOT NULL,
                producto TEXT NOT NULL,
                dosis TEXT,
                veterinario TEXT,
                comentario TEXT,
                fecha_proxima DATE,
                estado TEXT DEFAULT 'Activo',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_animal) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO tratamiento SELECT * FROM tratamiento_backup")
        cursor.execute("DROP TABLE tratamiento_backup")
        print("   ✅ tratamiento OK")
        
        # 3. VENTA
        print("3️⃣ Corrigiendo tabla 'venta'...")
        cursor.execute("DROP TABLE IF EXISTS venta_backup")
        cursor.execute("ALTER TABLE venta RENAME TO venta_backup")
        cursor.execute("""
            CREATE TABLE venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                precio_total REAL NOT NULL,
                motivo_venta TEXT,
                destino_venta TEXT,
                observaciones TEXT,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO venta SELECT * FROM venta_backup")
        cursor.execute("DROP TABLE venta_backup")
        print("   ✅ venta OK")
        
        # 4. PESO (¡LA CRÍTICA!)
        print("4️⃣ Corrigiendo tabla 'peso'...")
        cursor.execute("DROP TABLE IF EXISTS peso_backup")
        cursor.execute("ALTER TABLE peso RENAME TO peso_backup")
        cursor.execute("""
            CREATE TABLE peso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                peso REAL NOT NULL,
                metodo TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(animal_id, fecha),
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO peso SELECT * FROM peso_backup")
        cursor.execute("DROP TABLE peso_backup")
        print("   ✅ peso OK")
        
        # 5. PRODUCCION_LECHE
        print("5️⃣ Corrigiendo tabla 'produccion_leche'...")
        cursor.execute("DROP TABLE IF EXISTS produccion_leche_backup")
        cursor.execute("ALTER TABLE produccion_leche RENAME TO produccion_leche_backup")
        cursor.execute("""
            CREATE TABLE produccion_leche (
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
            )
        """)
        cursor.execute("INSERT INTO produccion_leche SELECT * FROM produccion_leche_backup")
        cursor.execute("DROP TABLE produccion_leche_backup")
        print("   ✅ produccion_leche OK")
        
        # 6. MUERTE
        print("6️⃣ Corrigiendo tabla 'muerte'...")
        cursor.execute("DROP TABLE IF EXISTS muerte_backup")
        cursor.execute("ALTER TABLE muerte RENAME TO muerte_backup")
        cursor.execute("""
            CREATE TABLE muerte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                causa TEXT,
                diagnostico_presuntivo TEXT,
                diagnostico_confirmado TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(animal_id),
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO muerte SELECT * FROM muerte_backup")
        cursor.execute("DROP TABLE muerte_backup")
        print("   ✅ muerte OK")
        
        # 7. DIAGNOSTICO_EVENTO
        print("7️⃣ Corrigiendo tabla 'diagnostico_evento'...")
        cursor.execute("DROP TABLE IF EXISTS diagnostico_evento_backup")
        cursor.execute("ALTER TABLE diagnostico_evento RENAME TO diagnostico_evento_backup")
        cursor.execute("""
            CREATE TABLE diagnostico_evento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                tipo TEXT,
                detalle TEXT,
                severidad TEXT,
                estado TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO diagnostico_evento SELECT * FROM diagnostico_evento_backup")
        cursor.execute("DROP TABLE diagnostico_evento_backup")
        print("   ✅ diagnostico_evento OK")
        
        # 8. MOVIMIENTO
        print("8️⃣ Corrigiendo tabla 'movimiento'...")
        cursor.execute("DROP TABLE IF EXISTS movimiento_backup")
        cursor.execute("ALTER TABLE movimiento RENAME TO movimiento_backup")
        cursor.execute("""
            CREATE TABLE movimiento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                lote_origen_id INTEGER,
                lote_destino_id INTEGER NOT NULL,
                fecha_movimiento DATE NOT NULL,
                tipo_movimiento TEXT,
                motivo TEXT,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lote_destino_id) REFERENCES lote(id) ON DELETE NO ACTION,
                FOREIGN KEY (lote_origen_id) REFERENCES lote(id) ON DELETE NO ACTION,
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO movimiento SELECT * FROM movimiento_backup")
        cursor.execute("DROP TABLE movimiento_backup")
        print("   ✅ movimiento OK")
        
        # 9. EVENTO
        print("9️⃣ Corrigiendo tabla 'evento'...")
        cursor.execute("DROP TABLE IF EXISTS evento_backup")
        cursor.execute("ALTER TABLE evento RENAME TO evento_backup")
        cursor.execute("""
            CREATE TABLE evento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                fecha_evento DATE NOT NULL,
                tipo_evento TEXT,
                animal_id INTEGER,
                lote_id INTEGER,
                completado BOOLEAN DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lote_id) REFERENCES lote(id) ON DELETE NO ACTION,
                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("INSERT INTO evento SELECT * FROM evento_backup")
        cursor.execute("DROP TABLE evento_backup")
        print("   ✅ evento OK")
        
        # Habilitar FKs de nuevo
        cursor.execute("PRAGMA foreign_keys=ON")
        
        conn.commit()
        print("\n✅ Todas las claves foráneas corregidas exitosamente")
        print("🎯 Ahora todas apuntan a la tabla 'animal' correcta\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    corregir_foreign_keys()
