"""Verificar estados actuales de herramientas"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_connection

print("=" * 70)
print("ANÁLISIS DE ESTADOS ACTUALES")
print("=" * 70)

with get_db_connection() as conn:
    cur = conn.cursor()
    
    # Ver todos los estados únicos
    cur.execute("SELECT DISTINCT estado FROM herramienta ORDER BY estado")
    estados = cur.fetchall()
    
    print("\nEstados encontrados en la tabla:")
    print("-" * 70)
    for (estado,) in estados:
        cur.execute("SELECT COUNT(*) FROM herramienta WHERE estado = ?", (estado,))
        cant = cur.fetchone()[0]
        print(f"  '{estado}': {cant} herramientas")
    
    # Estados permitidos
    estados_permitidos = ['Operativa', 'En Mantenimiento', 'En Revisión', 'Dañada', 'Fuera de Servicio']
    
    print("\n" + "=" * 70)
    print("Estados que NO cumplen el nuevo CHECK constraint:")
    print("-" * 70)
    
    estados_invalidos = []
    for (estado,) in estados:
        if estado not in estados_permitidos:
            cur.execute("SELECT id, nombre, codigo FROM herramienta WHERE estado = ?", (estado,))
            herramientas = cur.fetchall()
            estados_invalidos.append((estado, herramientas))
            print(f"\n'{estado}':")
            for id_h, nombre, codigo in herramientas:
                print(f"  - ID {id_h}: {nombre} ({codigo})")
    
    if not estados_invalidos:
        print("✅ Todos los estados son válidos")
    else:
        print("\n" + "=" * 70)
        print("SOLUCIÓN")
        print("=" * 70)
        print("\nSe deben corregir los estados inválidos antes de aplicar la migración.")
        print("Opciones:")
        print("  1. Convertir estados similares al nuevo sistema")
        print("  2. Marcar como 'Operativa' los estados no reconocidos")
        print("  3. Agregar los estados actuales al CHECK constraint (no recomendado)")
    
    print("\n" + "=" * 70)
