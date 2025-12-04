"""
Script de Migración Ligera para Inventario V2
Asegura columnas y datos necesarios
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def get_db_path():
    """Obtener ruta de BD"""
    # Probar ambas rutas posibles
    paths = [
        Path("database/fincafacil.db"),
        Path("data/fincafacil.db")
    ]
    
    for db_path in paths:
        if db_path.exists():
            return db_path
    
    # Si no existe, crear en database/
    db_path = Path("database/fincafacil.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"⚠️  Creando nueva BD en: {db_path}")
    return db_path

def ejecutar_migracion():
    """Ejecutar migración completa"""
    print("=" * 70)
    print("🔧 MIGRACIÓN INVENTARIO V2 - INICIO")
    print("=" * 70)
    
    db_path = get_db_path()
    if not db_path:
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # 1. Verificar y agregar columnas
        print("\n📋 Verificando columnas en tabla 'animal'...")
        cur.execute("PRAGMA table_info(animal)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        columnas_requeridas = {
            'ultimo_peso': 'REAL',
            'fecha_ultimo_peso': 'DATE',
            'inventariado': 'INTEGER DEFAULT 0',
            'categoria': 'TEXT',
            'procedencia_id': 'INTEGER',
            'fecha_muerte': 'DATE'
        }
        
        for col, tipo in columnas_requeridas.items():
            if col not in columns:
                print(f"   ➕ Agregando columna: {col} ({tipo})")
                cur.execute(f"ALTER TABLE animal ADD COLUMN {col} {tipo}")
                conn.commit()
            else:
                print(f"   ✓ Columna '{col}' ya existe")
        
        # 2. Insertar categorías por defecto si no hay datos
        print("\n📊 Verificando categorías...")
        cur.execute("SELECT COUNT(*) FROM animal WHERE categoria IS NOT NULL")
        count_con_cat = cur.fetchone()[0]
        
        if count_con_cat == 0:
            print("   ⚠️  No hay animales con categoría")
            print("   📝 Categorías disponibles: Vaca, Toro, Novillo, Ternero, Ternera")
            
            # Actualizar animales existentes con categorías aleatorias
            cur.execute("SELECT id, sexo FROM animal WHERE categoria IS NULL LIMIT 10")
            animales = cur.fetchall()
            
            if animales:
                print(f"   ➕ Asignando categorías a {len(animales)} animales...")
                for animal_id, sexo in animales:
                    if sexo == 'Hembra':
                        cat = 'Vaca' if animal_id % 2 == 0 else 'Ternera'
                    else:
                        cat = 'Toro' if animal_id % 3 == 0 else 'Novillo'
                    
                    cur.execute("UPDATE animal SET categoria = ? WHERE id = ?", (cat, animal_id))
                
                conn.commit()
                print(f"   ✓ Categorías asignadas correctamente")
        else:
            print(f"   ✓ Hay {count_con_cat} animales con categoría")
        
        # 3. Insertar animal de prueba si no hay ninguno
        cur.execute("SELECT COUNT(*) FROM animal")
        count_animales = cur.fetchone()[0]
        
        if count_animales == 0:
            print("\n🐄 No hay animales. Insertando animal de prueba...")
            
            # Obtener primera finca
            cur.execute("SELECT id FROM finca LIMIT 1")
            finca = cur.fetchone()
            
            if finca:
                finca_id = finca[0]
                cur.execute("""
                    INSERT INTO animal (
                        codigo, nombre, sexo, fecha_nacimiento, 
                        id_finca, categoria, inventariado, ultimo_peso
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    'TEST001',
                    'Animal de Prueba',
                    'Hembra',
                    '2023-01-15',
                    finca_id,
                    'Vaca',
                    0,
                    450.0
                ))
                conn.commit()
                print("   ✓ Animal de prueba insertado correctamente")
            else:
                print("   ⚠️  No hay fincas disponibles para insertar animal de prueba")
        else:
            print(f"\n✓ Base de datos contiene {count_animales} animales")
        
        # 4. Verificar tabla registro_peso
        print("\n📈 Verificando tabla 'registro_peso'...")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='registro_peso'")
        if not cur.fetchone():
            print("   ➕ Creando tabla 'registro_peso'...")
            cur.execute("""
                CREATE TABLE registro_peso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    peso_anterior REAL,
                    peso_nuevo REAL NOT NULL,
                    diferencia REAL,
                    observaciones TEXT,
                    FOREIGN KEY (animal_id) REFERENCES animal(id)
                )
            """)
            conn.commit()
            print("   ✓ Tabla 'registro_peso' creada")
        else:
            print("   ✓ Tabla 'registro_peso' ya existe")
        
        # 5. Estadísticas finales
        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS FINALES")
        print("=" * 70)
        
        cur.execute("SELECT COUNT(*) FROM animal")
        total_animales = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM animal WHERE inventariado = 1")
        inventariados = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(DISTINCT categoria) FROM animal WHERE categoria IS NOT NULL")
        categorias = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM finca")
        fincas = cur.fetchone()[0]
        
        print(f"   🐄 Total animales: {total_animales}")
        print(f"   ✓ Inventariados: {inventariados}")
        print(f"   📋 Categorías únicas: {categorias}")
        print(f"   🏡 Fincas: {fincas}")
        
        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar: python main.py")
        print("   2. Navegar a: Animales → Inventario General")
        print("   3. Probar filtros, búsqueda y gráficas")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ejecutar_migracion()
