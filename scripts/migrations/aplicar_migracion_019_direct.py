"""Script para aplicar migración 019 - columnas de inventario animal (tipo_ingreso, compra, nacimiento y productivos)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from database.database import get_db_connection
except Exception:
    # Fallback para estructuras antiguas
    from database import get_db_connection  # type: ignore

COLUMNS_TO_ADD = {
    'tipo_ingreso': 'TEXT',
    'fecha_compra': 'TEXT',
    'precio_compra': 'REAL',
    'peso_compra': 'REAL',
    'raza': 'TEXT',
    'peso_nacimiento': 'REAL',
    'condicion_corporal': 'TEXT',
    'estado': 'TEXT',
    'salud': 'TEXT',
    'calidad': 'TEXT',
    'grupo': 'TEXT',
    'madre_id': 'INTEGER',
    'padre_id': 'INTEGER',
    'inseminacion_artificial': 'INTEGER DEFAULT 0',
    'ultimo_peso': 'REAL'
}

print("=" * 60)
print("MIGRACIÓN 019 - Tabla animal: columnas de compra/nacimiento/productivos")
print("=" * 60)

with get_db_connection() as conn:
    cur = conn.cursor()

    # Verificar existencia de tabla animal
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal'")
    if not cur.fetchone():
        print("✗ La tabla 'animal' no existe. Abortando migración 019.")
    else:
        # Leer columnas actuales
        cur.execute("PRAGMA table_info(animal)")
        existentes = {row[1] for row in cur.fetchall()}

        faltantes = [c for c in COLUMNS_TO_ADD.keys() if c not in existentes]

        if not faltantes:
            print("✅ Migración 019 ya aplicada. No hay columnas faltantes.")
        else:
            print("⚠️  Columnas faltantes en 'animal':")
            for c in faltantes:
                print(f"  • {c} -> {COLUMNS_TO_ADD[c]}")

            print("\n🔧 Aplicando ALTER TABLE para columnas faltantes...")
            for col in faltantes:
                ddl = f"ALTER TABLE animal ADD COLUMN {col} {COLUMNS_TO_ADD[col]}"
                try:
                    cur.execute(ddl)
                    print(f"✓ Agregada columna: {col}")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        print(f"✓ Columna ya existía: {col}")
                    else:
                        print(f"✗ Error agregando {col}: {e}")

            # Índices útiles opcionales
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_tipo_ingreso ON animal(tipo_ingreso)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_madre_id ON animal(madre_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_padre_id ON animal(padre_id)")
                print("✓ Índices creados/asegurados: tipo_ingreso, madre_id, padre_id")
            except Exception as e:
                print(f"⚠️  Error creando índices: {e}")

            conn.commit()
            print("\n✅ Migración 019 completada exitosamente")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETADA")
print("=" * 60)
