"""Migración 020: Agregar columnas adicionales a tabla animal (procedencia, vendedor, color, hierro, inventariado, comentarios, tipo_reproduccion)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from database.database import get_db_connection
except Exception:
    from database import get_db_connection  # type: ignore

NEW_COLUMNS = {
    'procedencia': 'TEXT',
    'vendedor': 'TEXT',
    'color': 'TEXT',
    'hierro': 'TEXT',
    'inventariado': 'TEXT',  # Puede cambiarse a INTEGER si se maneja como booleano
    'comentarios': 'TEXT',
    'tipo_reproduccion': 'TEXT'  # Valores esperados: Natural / Inseminación
}

print("=" * 65)
print("MIGRACIÓN 020 - Columnas adicionales para tabla animal")
print("=" * 65)

with get_db_connection() as conn:
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal'")
    if not cur.fetchone():
        print("✗ La tabla 'animal' no existe. Abortando migración.")
    else:
        cur.execute("PRAGMA table_info(animal)")
        existentes = {row[1] for row in cur.fetchall()}

        faltantes = [c for c in NEW_COLUMNS if c not in existentes]
        if not faltantes:
            print("✅ Todas las columnas ya existen. Nada que hacer.")
        else:
            print("⚠️ Faltan las siguientes columnas:")
            for c in faltantes:
                print(f"  • {c} -> {NEW_COLUMNS[c]}")
            print("\n🔧 Aplicando ALTER TABLE...")
            for c in faltantes:
                ddl = f"ALTER TABLE animal ADD COLUMN {c} {NEW_COLUMNS[c]}"
                try:
                    cur.execute(ddl)
                    print(f"✓ Agregada columna: {c}")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        print(f"✓ Columna ya existía: {c}")
                    else:
                        print(f"✗ Error agregando {c}: {e}")

            # Índice de ayuda para búsquedas por hierro y procedencia (opcionales)
            try:
                cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_hierro ON animal(hierro)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_procedencia ON animal(procedencia)")
                print("✓ Índices creados/asegurados: hierro, procedencia")
            except Exception as e:
                print(f"⚠️ Error creando índices opcionales: {e}")

            conn.commit()
            print("\n✅ Migración 020 completada exitosamente")

print("\n" + "=" * 65)
print("VERIFICACIÓN COMPLETADA")
print("=" * 65)
