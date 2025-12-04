"""
Migración 020: Agregar campos necesarios a la tabla insumo para funcionalidad completa
Similar a herramientas: foto_path, id_trabajador, responsable, stock_total, stock_bodega
"""

def run(conn):
    print("➡️ Ejecutando migración 020: Campos adicionales en tabla insumo...")
    
    try:
        cur = conn.cursor()
        
        # Verificar columnas existentes
        cur.execute("PRAGMA table_info(insumo)")
        columnas_existentes = [col[1] for col in cur.fetchall()]
        
        campos_necesarios = {
            'foto_path': 'TEXT',
            'id_trabajador': 'INTEGER',
            'responsable': 'TEXT',
            'stock_bodega': 'REAL DEFAULT 0',
            'observaciones': 'TEXT'
        }
        
        campos_agregados = []
        
        for campo, tipo in campos_necesarios.items():
            if campo not in columnas_existentes:
                try:
                    cur.execute(f"ALTER TABLE insumo ADD COLUMN {campo} {tipo}")
                    campos_agregados.append(campo)
                    print(f"   ✓ Campo '{campo}' agregado")
                except Exception as e:
                    if "duplicate column" not in str(e).lower():
                        print(f"   ⚠️  Error agregando '{campo}': {e}")
            else:
                print(f"   • Campo '{campo}' ya existe")
        
        # Crear índices si no existen
        indices = [
            ("idx_insumo_trabajador", "insumo", "id_trabajador"),
            ("idx_insumo_finca", "insumo", "id_finca"),
            ("idx_insumo_categoria", "insumo", "categoria")
        ]
        
        for idx_name, tabla, columna in indices:
            try:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tabla}({columna})")
                print(f"   ✓ Índice {idx_name} creado")
            except Exception as e:
                print(f"   ⚠️  Error creando índice {idx_name}: {e}")
        
        # Actualizar stock_bodega inicial (igual a stock_actual si no está asignado)
        if 'stock_bodega' in campos_agregados:
            cur.execute("""
                UPDATE insumo 
                SET stock_bodega = stock_actual 
                WHERE stock_bodega IS NULL OR stock_bodega = 0
            """)
            print("   ✓ stock_bodega inicializado")
        
        conn.commit()
        
        if campos_agregados:
            print(f"✅ Migración 020 completada: {len(campos_agregados)} campos agregados")
        else:
            print("✅ Migración 020: Todos los campos ya existían")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en migración 020: {e}")
        raise

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
    from database import get_connection
    
    with get_connection() as conn:
        run(conn)
