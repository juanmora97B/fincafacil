"""Script temporal para verificar el esquema de la tabla animal"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_connection

print("🔍 Verificando estructura de la tabla 'animal'...\n")

with get_connection() as conn:
    cursor = conn.cursor()
    
    # Obtener información de columnas
    cursor.execute("PRAGMA table_info(animal)")
    cols = cursor.fetchall()
    
    print(f"Total de columnas: {len(cols)}\n")
    print("Columnas de la tabla 'animal':")
    print("-" * 60)
    for col in cols:
        print(f"  {col[1]:25} {col[2]:15} {'NOT NULL' if col[3] else ''}")
    
    print("\n" + "=" * 60)
    
    # Verificar columnas clave esperadas (post-normalización)
    columnas_esperadas = [
        'id', 'codigo', 'nombre', 'raza_id',
        'id_finca', 'id_potrero', 'lote_id', 'id_sector', 'id_vendedor',
        'id_padre', 'id_madre', 'tipo_concepcion',
        'sexo', 'estado', 'salud', 'inventariado', 'tipo_ingreso',
        'fecha_nacimiento', 'fecha_compra', 'peso_nacimiento', 'peso_compra', 'precio_compra',
        'color', 'hierro', 'numero_hierros', 'composicion_racial',
        'comentarios', 'foto_path', 'fecha_registro',
        'fecha_creacion', 'fecha_actualizacion'
    ]
    
    columnas_actuales = {col[1] for col in cols}
    
    print("\n✅ Columnas esperadas presentes:")
    for col in columnas_esperadas:
        if col in columnas_actuales:
            print(f"  ✓ {col}")
        else:
            print(f"  ✗ {col} (FALTA)")
    
    print("\n📋 Columnas adicionales no esperadas (posibles remanentes legacy):")
    adicionales = columnas_actuales - set(columnas_esperadas)
    if adicionales:
        for col in adicionales:
            print(f"  + {col}")
    else:
        print("  (ninguna)")
    
    print("\n✅ Verificación completada")
