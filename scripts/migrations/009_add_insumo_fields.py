"""
Migración 009: Agregar campos faltantes a tabla insumo
- fecha_adquisicion: Fecha de compra del insumo
- stock_bodega: Cantidad disponible en bodega
- responsable: Persona a cargo del insumo
- observaciones: Notas adicionales
- foto_path: Ruta a la imagen del insumo
"""

import sqlite3
import sys
from pathlib import Path

# Agregar directorio raíz al path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

DB_PATH = BASE_DIR / "database" / "fincafacil.db"

def aplicar_migracion():
    """Aplica la migración 009"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("🔧 Aplicando migración 009: Campos adicionales para insumo")
        
        # Verificar qué campos ya existen
        cursor.execute("PRAGMA table_info(insumo)")
        columnas_existentes = [row[1] for row in cursor.fetchall()]
        
        campos_a_agregar = {
            'fecha_adquisicion': 'DATE',
            'stock_bodega': 'REAL DEFAULT 0',
            'responsable': 'TEXT',
            'observaciones': 'TEXT',
            'foto_path': 'TEXT'
        }
        
        campos_agregados = 0
        for campo, tipo in campos_a_agregar.items():
            if campo not in columnas_existentes:
                print(f"  ➕ Agregando campo: {campo}")
                cursor.execute(f"ALTER TABLE insumo ADD COLUMN {campo} {tipo}")
                campos_agregados += 1
            else:
                print(f"  ✓ Campo ya existe: {campo}")
        
        # Inicializar stock_bodega = stock_actual para registros existentes
        if 'stock_bodega' not in columnas_existentes:
            print("  🔄 Inicializando stock_bodega con valores de stock_actual...")
            cursor.execute("UPDATE insumo SET stock_bodega = stock_actual WHERE stock_bodega IS NULL")
        
        conn.commit()
        
        print(f"\n✅ Migración 009 completada:")
        print(f"   - {campos_agregados} campos agregados")
        print(f"   - Tabla insumo actualizada correctamente")
        
        # Verificar estructura final
        cursor.execute("PRAGMA table_info(insumo)")
        columnas = cursor.fetchall()
        print(f"\n📋 Estructura final de tabla insumo ({len(columnas)} campos):")
        for col in columnas:
            print(f"   • {col[1]}: {col[2]}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error en migración 009: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN 009: Campos adicionales para insumo")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print(f"❌ Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)
    
    exito = aplicar_migracion()
    sys.exit(0 if exito else 1)
