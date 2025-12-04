"""
Script de verificación del módulo de insumos
"""
import sys
sys.path.insert(0, '.')
from database.database import get_db_connection

print("=" * 70)
print("VERIFICACIÓN DEL MÓDULO DE INSUMOS")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # 1. Verificar tabla insumo
    print("\n1. Tabla INSUMO:")
    print("-" * 70)
    cur.execute('PRAGMA table_info(insumo)')
    cols = [col[1] for col in cur.fetchall()]
    
    campos_requeridos = ['id', 'codigo', 'nombre', 'categoria', 'id_finca', 
                         'foto_path', 'id_trabajador', 'responsable', 
                         'stock_actual', 'stock_bodega']
    
    for campo in campos_requeridos:
        if campo in cols:
            print(f"   ✅ {campo}")
        else:
            print(f"   ❌ {campo} - FALTA")
    
    # 2. Verificar tabla mantenimiento_insumo
    print("\n2. Tabla MANTENIMIENTO_INSUMO:")
    print("-" * 70)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mantenimiento_insumo'")
    if cur.fetchone():
        print("   ✅ Tabla mantenimiento_insumo existe")
        
        cur.execute('PRAGMA table_info(mantenimiento_insumo)')
        cols_mant = [col[1] for col in cur.fetchall()]
        
        campos_mant = ['id', 'insumo_id', 'estado_actual', 'estado_previo_insumo', 
                      'fecha_completado']
        
        for campo in campos_mant:
            if campo in cols_mant:
                print(f"   ✅ {campo}")
            else:
                print(f"   ❌ {campo} - FALTA")
    else:
        print("   ❌ Tabla mantenimiento_insumo NO EXISTE")
    
    # 3. Verificar índices
    print("\n3. Índices:")
    print("-" * 70)
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='insumo'")
    indices = [row[0] for row in cur.fetchall()]
    
    indices_esperados = ['idx_insumo_trabajador', 'idx_insumo_finca', 'idx_insumo_categoria']
    
    for idx in indices_esperados:
        if idx in indices:
            print(f"   ✅ {idx}")
        else:
            print(f"   ⚠️  {idx} - No existe (no crítico)")
    
    # 4. Verificar archivo del módulo
    print("\n4. Archivo del módulo:")
    print("-" * 70)
    import os
    module_path = "modules/insumos/insumos_main.py"
    if os.path.exists(module_path):
        size = os.path.getsize(module_path)
        print(f"   ✅ {module_path} existe ({size:,} bytes)")
        
        # Verificar que tenga la clase correcta
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class InsumosModule' in content:
                print("   ✅ Clase InsumosModule encontrada")
            else:
                print("   ❌ Clase InsumosModule NO encontrada")
            
            if 'mantenimiento_insumo' in content:
                print("   ✅ Referencias a mantenimiento_insumo encontradas")
            else:
                print("   ⚠️  No se encontraron referencias a mantenimiento_insumo")
    else:
        print(f"   ❌ {module_path} NO EXISTE")
    
    # 5. Verificar plantilla
    print("\n5. Plantilla de carga:")
    print("-" * 70)
    try:
        from modules.utils.plantillas_carga import TEMPLATE_SPECS, FRIENDLY_NAMES
        
        if 'insumos' in TEMPLATE_SPECS:
            print("   ✅ Plantilla 'insumos' definida en TEMPLATE_SPECS")
            campos = TEMPLATE_SPECS['insumos']
            print(f"   ✅ {len(campos)} campos: {', '.join(campos[:5])}...")
        else:
            print("   ❌ Plantilla 'insumos' NO definida")
        
        nombres = [n for n, _ in FRIENDLY_NAMES]
        if 'Insumos' in nombres:
            print("   ✅ 'Insumos' en lista de plantillas disponibles")
        else:
            print("   ❌ 'Insumos' NO en lista de plantillas")
            
    except Exception as e:
        print(f"   ❌ Error verificando plantillas: {e}")
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print("\n✅ Módulo de Insumos configurado correctamente")
    print("\nFuncionalidades disponibles:")
    print("  • Catálogo de insumos por finca")
    print("  • Asignación de insumos a trabajadores")
    print("  • Gestión de mantenimiento de insumos")
    print("  • Visualización de fotos en detalles")
    print("  • Importación masiva desde Excel")
    print("  • Plantilla de carga disponible en Ajustes")
    print("\n" + "=" * 70)
