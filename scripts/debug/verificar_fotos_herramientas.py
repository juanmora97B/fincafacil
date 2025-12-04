"""
Script de prueba para verificar la visualización de fotos en detalles de herramientas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.database import get_db_connection

print("=" * 70)
print("VERIFICACIÓN DE FOTOS EN HERRAMIENTAS")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Verificar columna foto_path
    cur.execute("PRAGMA table_info(herramienta)")
    columnas = [col[1] for col in cur.fetchall()]
    
    print("\n✓ Columnas en tabla herramienta:")
    for col in columnas:
        if col in ['foto_path', 'codigo', 'nombre']:
            print(f"  • {col}")
    
    if 'foto_path' not in columnas:
        print("\n⚠️  ADVERTENCIA: La columna 'foto_path' no existe en la tabla")
    else:
        print("\n✅ Columna 'foto_path' presente")
    
    # Verificar herramientas con/sin fotos
    cur.execute("""
        SELECT codigo, nombre, foto_path 
        FROM herramienta 
        ORDER BY codigo
    """)
    herramientas = cur.fetchall()
    
    print(f"\n📊 Total de herramientas: {len(herramientas)}")
    print("-" * 70)
    
    con_foto = 0
    sin_foto = 0
    fotos_existentes = 0
    fotos_faltantes = 0
    
    for codigo, nombre, foto_path in herramientas:
        if foto_path:
            con_foto += 1
            existe = os.path.exists(foto_path) if foto_path else False
            if existe:
                fotos_existentes += 1
                print(f"✅ {codigo} - {nombre}")
                print(f"   📷 {foto_path}")
            else:
                fotos_faltantes += 1
                print(f"⚠️  {codigo} - {nombre}")
                print(f"   ❌ Foto registrada pero archivo no existe: {foto_path}")
        else:
            sin_foto += 1
            print(f"📷 {codigo} - {nombre}")
            print(f"   (Sin foto registrada)")
        print()
    
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Herramientas con foto registrada: {con_foto}")
    print(f"  • Archivos existentes: {fotos_existentes}")
    print(f"  • Archivos faltantes: {fotos_faltantes}")
    print(f"Herramientas sin foto: {sin_foto}")
    print()
    
    if con_foto > 0:
        print("✅ El módulo mostrará las fotos en 'Ver detalles'")
    else:
        print("ℹ️  Ninguna herramienta tiene foto registrada aún")
        print("   Para probar, registre una herramienta con foto desde el catálogo")
    
    print("=" * 70)
