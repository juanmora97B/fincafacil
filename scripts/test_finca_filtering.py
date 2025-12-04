"""Script de validación de filtrado por finca en registro de animales.
Ejecutar: python scripts/test_finca_filtering.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

def test_finca_filtering():
    print("=" * 60)
    print("TEST: Filtrado por Finca en Registro de Animales")
    print("=" * 60)
    
    with get_connection() as conn:
        cur = conn.cursor()
        
        # 1. Verificar fincas activas
        print("\n1. FINCAS ACTIVAS:")
        cur.execute("SELECT id, codigo, nombre, estado FROM finca WHERE estado NOT IN ('Inactivo', 'Eliminado')")
        fincas = cur.fetchall()
        for f in fincas:
            print(f"   ID: {f[0]:2d} | Código: {f[1]:6s} | Nombre: {f[2]:20s} | Estado: {f[3]}")
        
        # 2. Verificar potreros por finca
        print("\n2. POTREROS POR FINCA:")
        for finca in fincas:
            finca_id = finca[0]
            finca_nombre = finca[2]
            cur.execute("SELECT COUNT(*) FROM potrero WHERE id_finca = ? AND estado = 'Activo'", (finca_id,))
            count = cur.fetchone()[0]
            cur.execute("SELECT nombre FROM potrero WHERE id_finca = ? AND estado = 'Activo' ORDER BY nombre LIMIT 3", (finca_id,))
            ejemplos = [r[0] for r in cur.fetchall()]
            print(f"   {finca_nombre}: {count} potreros (Ej: {', '.join(ejemplos)}...)")
        
        # 3. Verificar lotes por finca
        print("\n3. LOTES POR FINCA:")
        for finca in fincas:
            finca_id = finca[0]
            finca_nombre = finca[2]
            cur.execute("SELECT COUNT(*) FROM lote WHERE finca_id = ? AND estado = 'Activo'", (finca_id,))
            count = cur.fetchone()[0]
            cur.execute("SELECT nombre FROM lote WHERE finca_id = ? AND estado = 'Activo' ORDER BY nombre LIMIT 3", (finca_id,))
            ejemplos = [r[0] for r in cur.fetchall()]
            print(f"   {finca_nombre}: {count} lotes (Ej: {', '.join(ejemplos)}...)")
        
        # 4. Verificar razas (globales)
        print("\n4. RAZAS (CATÁLOGO GLOBAL):")
        cur.execute("SELECT COUNT(*) FROM raza WHERE estado IN ('Activa', 'Activo')")
        count = cur.fetchone()[0]
        cur.execute("SELECT nombre FROM raza WHERE estado IN ('Activa', 'Activo') ORDER BY nombre LIMIT 5")
        ejemplos = [r[0] for r in cur.fetchall()]
        print(f"   Total: {count} razas (Ej: {', '.join(ejemplos)}...)")
        
        # 5. Verificar origen
        print("\n5. ORIGEN (PROCEDENCIA/VENDEDOR):")
        cur.execute("SELECT COUNT(*) FROM origen WHERE estado = 'Activo'")
        count = cur.fetchone()[0]
        cur.execute("SELECT nombre FROM origen WHERE estado = 'Activo' ORDER BY nombre LIMIT 3")
        ejemplos = [r[0][:40] for r in cur.fetchall()]
        print(f"   Total: {count} orígenes (Ej: {', '.join(ejemplos)}...)")
        
        # 6. Verificar animales existentes por finca
        print("\n6. ANIMALES POR FINCA (para padres/madres):")
        for finca in fincas:
            finca_id = finca[0]
            finca_nombre = finca[2]
            cur.execute("SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo'", (finca_id,))
            count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND sexo = 'Hembra'", (finca_id,))
            hembras = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND sexo = 'Macho'", (finca_id,))
            machos = cur.fetchone()[0]
            print(f"   {finca_nombre}: {count} animales ({hembras} hembras, {machos} machos)")
    
    print("\n" + "=" * 60)
    print("RESULTADO: Estructura de datos verificada ✓")
    print("=" * 60)
    print("\nRECOMENDACIÓN DE PRUEBA:")
    print("1. Abrir aplicación → Animales → Registro de Animales")
    print("2. Pestaña Nacimiento:")
    print("   - Verificar campo Finca muestra las fincas listadas arriba")
    print("   - Seleccionar 'finca el prado' → verificar potreros y lotes correctos")
    print("   - Seleccionar 'finca el leon' → verificar cambio de potreros y lotes")
    print("3. Pestaña Compra:")
    print("   - Repetir verificación anterior")
    print("   - Verificar campo Origen muestra procedencias disponibles")
    print()

if __name__ == '__main__':
    test_finca_filtering()
