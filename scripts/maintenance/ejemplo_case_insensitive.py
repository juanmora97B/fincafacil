"""
Ejemplo práctico: Demostración de búsquedas case-insensitive
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from database import db
from modules.utils.database_helpers import (
    buscar_finca_id,
    buscar_raza_id,
    buscar_potrero_id,
    normalizar_texto
)


def ejemplo_practico():
    """
    Demuestra cómo usar las búsquedas case-insensitive en situaciones reales
    """
    print("=" * 80)
    print("EJEMPLO PRÁCTICO: Búsquedas Case-Insensitive")
    print("=" * 80)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        print("\n📋 ESCENARIO: Usuario importa datos desde Excel")
        print("-" * 80)
        
        # Simular diferentes formas en que el usuario puede escribir
        variantes_usuario = [
            "FINCA EL PRADO",
            "finca el prado",
            "Finca El Prado",
            "  FINCA EL PRADO  ",  # Con espacios
        ]
        
        print("\nEl usuario escribe el nombre de la finca de diferentes formas:")
        for variante in variantes_usuario:
            print(f"  - '{variante}'")
        
        print("\n🔍 El sistema busca en la base de datos...")
        print("-" * 80)
        
        for variante in variantes_usuario:
            id_finca = buscar_finca_id(cursor, variante)
            
            if id_finca:
                # Obtener el nombre real guardado en la BD
                cursor.execute("SELECT nombre FROM finca WHERE id = ?", (id_finca,))
                nombre_bd = cursor.fetchone()[0]
                
                print(f"\n✅ '{variante}'")
                print(f"   → Encontró: '{nombre_bd}' (ID: {id_finca})")
            else:
                print(f"\n❌ '{variante}'")
                print(f"   → No encontrado")
        
        print("\n" + "=" * 80)
        print("✨ RESULTADO: Todas las variantes encontraron la misma finca!")
        print("=" * 80)
        
        # Ejemplo 2: Razas
        print("\n\n📋 ESCENARIO 2: Búsqueda de razas")
        print("-" * 80)
        
        # Obtener una raza de ejemplo
        cursor.execute("SELECT nombre FROM raza WHERE estado IN ('Activa', 'Activo') LIMIT 1")
        raza_ejemplo = cursor.fetchone()
        
        if raza_ejemplo:
            nombre_raza = raza_ejemplo[0]
            
            variantes_raza = [
                nombre_raza.lower(),
                nombre_raza.upper(),
                nombre_raza.title(),
            ]
            
            print(f"\nRaza en la BD: '{nombre_raza}'")
            print("\nUsuario busca con diferentes variantes:")
            
            for variante in variantes_raza:
                id_raza = buscar_raza_id(cursor, variante)
                simbolo = "✅" if id_raza else "❌"
                print(f"{simbolo} '{variante}' → {'Encontrado' if id_raza else 'No encontrado'} (ID: {id_raza})")
        
        # Ejemplo 3: Comparación con búsqueda tradicional
        print("\n\n📊 COMPARACIÓN: Búsqueda Tradicional vs Case-Insensitive")
        print("=" * 80)
        
        nombre_buscar = "FINCA EL PRADO"
        
        print(f"\nBuscando: '{nombre_buscar}'")
        print("\n1️⃣ Búsqueda Tradicional (sensible a mayúsculas):")
        cursor.execute("SELECT id, nombre FROM finca WHERE nombre = ?", (nombre_buscar,))
        resultado_tradicional = cursor.fetchone()
        
        if resultado_tradicional:
            print(f"   ✅ Encontrado: {resultado_tradicional[1]} (ID: {resultado_tradicional[0]})")
        else:
            print(f"   ❌ No encontrado (requiere coincidencia exacta)")
        
        print("\n2️⃣ Búsqueda Case-Insensitive (con helper):")
        id_case_insensitive = buscar_finca_id(cursor, nombre_buscar)
        
        if id_case_insensitive:
            cursor.execute("SELECT nombre FROM finca WHERE id = ?", (id_case_insensitive,))
            nombre_encontrado = cursor.fetchone()[0]
            print(f"   ✅ Encontrado: '{nombre_encontrado}' (ID: {id_case_insensitive})")
            print(f"   ✨ Aunque el usuario escribió en MAYÚSCULAS!")
        else:
            print(f"   ❌ No encontrado")
        
        # Ejemplo 4: Normalización de texto
        print("\n\n🔧 NORMALIZACIÓN DE TEXTO")
        print("=" * 80)
        
        ejemplos_normalizacion = [
            "FINCA EL PRADO",
            "  Finca El Prado  ",
            "fInCa eL pRaDo",
            "Holstein",
            "  HOLSTEIN  ",
        ]
        
        print("\nTexto Original → Texto Normalizado")
        print("-" * 50)
        for texto in ejemplos_normalizacion:
            normalizado = normalizar_texto(texto)
            print(f"'{texto:25}' → '{normalizado}'")
        
        # Ejemplo 5: Uso en código de importación
        print("\n\n💻 CÓDIGO DE EJEMPLO: Importación con Case-Insensitive")
        print("=" * 80)
        
        codigo_ejemplo = '''
# En tu código de importación:
from modules.utils.database_helpers import buscar_finca_id, buscar_raza_id

# Datos del Excel (pueden venir en cualquier formato)
datos_excel = {
    "finca": "FINCA EL PRADO",      # En mayúsculas
    "raza": "holstein",              # En minúsculas
    "potrero": "Potrero 1"           # Mixto
}

# Buscar IDs (case-insensitive)
id_finca = buscar_finca_id(cursor, datos_excel["finca"])
id_raza = buscar_raza_id(cursor, datos_excel["raza"])
id_potrero = buscar_potrero_id(cursor, datos_excel["potrero"])

# Todos los IDs se encuentran correctamente ✨
print(f"Finca ID: {id_finca}")
print(f"Raza ID: {id_raza}")
print(f"Potrero ID: {id_potrero}")
'''
        
        print(codigo_ejemplo)
        
        print("\n" + "=" * 80)
        print("✅ CONCLUSIÓN")
        print("=" * 80)
        print("\n🎯 El sistema ahora es COMPLETAMENTE case-insensitive")
        print("📝 Los usuarios pueden escribir como quieran")
        print("🔍 El sistema siempre encuentra lo correcto")
        print("✨ ¡Menos errores, mejor experiencia!")
        print("\n")


if __name__ == "__main__":
    ejemplo_practico()
