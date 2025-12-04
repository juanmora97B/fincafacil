"""Análisis de estructura de datos del sistema FincaFacil.
Verifica qué tablas tienen relación con finca y cuáles son globales.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

def analyze_table_structure():
    print("=" * 80)
    print("ANÁLISIS DE ESTRUCTURA DE DATOS - FincaFacil")
    print("=" * 80)
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Obtener todas las tablas
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        
        # Clasificar tablas
        tables_with_finca = []
        tables_global = []
        tables_unclear = []
        
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            columns = [c[1] for c in cur.fetchall()]
            
            # Buscar columnas relacionadas con finca
            has_finca = any(col in columns for col in ['id_finca', 'finca_id'])
            
            if has_finca:
                # Verificar cuál columna tiene
                fk_col = 'id_finca' if 'id_finca' in columns else 'finca_id'
                # Contar registros con/sin finca
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {fk_col} IS NOT NULL")
                con_finca = cur.fetchone()[0]
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {fk_col} IS NULL")
                sin_finca = cur.fetchone()[0]
                tables_with_finca.append((table, fk_col, con_finca, sin_finca))
            else:
                # Tabla global
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                tables_global.append((table, count))
        
        # Mostrar resultados
        print("\n📌 TABLAS CON RELACIÓN A FINCA:")
        print("-" * 80)
        print(f"{'Tabla':<25} {'Columna FK':<15} {'Con Finca':<12} {'Sin Finca':<12}")
        print("-" * 80)
        for table, fk_col, con_finca, sin_finca in sorted(tables_with_finca):
            status = "✓ OK" if sin_finca == 0 else f"⚠️ {sin_finca} NULL"
            print(f"{table:<25} {fk_col:<15} {con_finca:<12} {status}")
        
        print("\n🌍 TABLAS GLOBALES (sin relación con finca):")
        print("-" * 80)
        print(f"{'Tabla':<30} {'Registros':<12}")
        print("-" * 80)
        for table, count in sorted(tables_global):
            print(f"{table:<30} {count:<12}")
        
        # Análisis de conformidad
        print("\n" + "=" * 80)
        print("ANÁLISIS DE CONFORMIDAD CON REQUISITOS")
        print("=" * 80)
        
        # Requisitos del usuario
        debe_tener_finca = ['potrero', 'lote', 'sector', 'animal', 'empleado', 'insumo', 'herramienta']
        debe_ser_global = ['raza', 'motivo_venta', 'destino_venta', 'condicion_corporal', 
                          'calidad_animal', 'tipo_explotacion']
        
        print("\n✅ DEBE TENER RELACIÓN CON FINCA:")
        for table in debe_tener_finca:
            tiene = any(t[0] == table for t in tables_with_finca)
            if tiene:
                info = next(t for t in tables_with_finca if t[0] == table)
                print(f"  ✓ {table:<20} - {info[1]} (FK encontrada)")
            else:
                print(f"  ❌ {table:<20} - FALTA FK hacia finca")
        
        print("\n🌍 DEBE SER GLOBAL (sin FK a finca):")
        for table in debe_ser_global:
            es_global = any(t[0] == table for t in tables_global)
            if es_global:
                info = next(t for t in tables_global if t[0] == table)
                print(f"  ✓ {table:<25} - Global ({info[1]} registros)")
            else:
                # Verificar si tiene FK
                tiene_fk = any(t[0] == table for t in tables_with_finca)
                if tiene_fk:
                    info = next(t for t in tables_with_finca if t[0] == table)
                    print(f"  ⚠️ {table:<25} - Tiene FK {info[1]} (debería ser global)")
                else:
                    print(f"  ❓ {table:<25} - Tabla no encontrada")
        
        # Casos especiales
        print("\n⚠️ CASOS ESPECIALES A REVISAR:")
        special_cases = {
            'origen': 'Tiene id_finca pero todos son NULL (¿debería ser global?)',
            'procedencia': 'Tiene id_finca - verificar si debe ser global',
            'vendedor': 'Tiene id_finca - verificar si debe ser global',
            'pago_nomina': 'Debe relacionarse con empleado (que tiene finca)'
        }
        
        for table, nota in special_cases.items():
            tiene_fk = any(t[0] == table for t in tables_with_finca)
            es_global = any(t[0] == table for t in tables_global)
            if tiene_fk:
                info = next(t for t in tables_with_finca if t[0] == table)
                print(f"  • {table:<20} - {nota}")
                print(f"    → Tiene {info[1]}: {info[2]} con finca, {info[3]} sin finca")
            elif es_global:
                print(f"  • {table:<20} - {nota}")
                print(f"    → Es global actualmente")

if __name__ == '__main__':
    analyze_table_structure()
