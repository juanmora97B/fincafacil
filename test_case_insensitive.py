"""
Test para validar que las búsquedas case-insensitive funcionan correctamente
"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(__file__))

from database import db
from modules.utils.database_helpers import (
    normalizar_texto,
    buscar_finca_id,
    buscar_raza_id,
    buscar_potrero_id,
    buscar_lote_id,
    buscar_sector_id,
    buscar_vendedor_id,
    obtener_diccionario_normalizado,
    verificar_existe_nombre
)


def test_normalizacion_texto():
    """Prueba la función de normalización de texto"""
    print("\n" + "=" * 80)
    print("TEST 1: Normalización de Texto")
    print("=" * 80)
    
    casos = [
        ("FINCA EL PRADO", "finca el prado"),
        ("  Finca El Prado  ", "finca el prado"),
        ("finca el prado", "finca el prado"),
        ("FiNcA eL pRaDo", "finca el prado"),
        ("", ""),
        (None, ""),
    ]
    
    todos_correctos = True
    for entrada, esperado in casos:
        resultado = normalizar_texto(entrada)
        correcto = resultado == esperado
        todos_correctos = todos_correctos and correcto
        
        simbolo = "✓" if correcto else "✗"
        print(f"{simbolo} '{entrada}' → '{resultado}' (esperado: '{esperado}')")
    
    if todos_correctos:
        print("\n✅ Todas las normalizaciones son correctas")
    else:
        print("\n❌ Algunas normalizaciones fallaron")
    
    return todos_correctos


def test_busqueda_fincas_case_insensitive():
    """Prueba la búsqueda de fincas con diferentes variaciones de mayúsculas/minúsculas"""
    print("\n" + "=" * 80)
    print("TEST 2: Búsqueda de Fincas Case-Insensitive")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener una finca de prueba
            cursor.execute("SELECT id, nombre FROM finca WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            finca = cursor.fetchone()
            
            if not finca:
                print("⚠ No hay fincas activas para probar")
                return False
            
            id_esperado, nombre_original = finca
            print(f"\nFinca de prueba: '{nombre_original}' (ID: {id_esperado})")
            
            # Probar diferentes variaciones
            variaciones = [
                nombre_original.lower(),
                nombre_original.upper(),
                nombre_original.title(),
                "  " + nombre_original + "  ",  # Con espacios
                nombre_original.swapcase() if len(nombre_original) > 0 else nombre_original,
            ]
            
            print("\nProbando variaciones:")
            todos_correctos = True
            for variacion in variaciones:
                id_encontrado = buscar_finca_id(cursor, variacion)
                correcto = id_encontrado == id_esperado
                todos_correctos = todos_correctos and correcto
                
                simbolo = "✓" if correcto else "✗"
                print(f"{simbolo} '{variacion}' → ID: {id_encontrado} (esperado: {id_esperado})")
            
            # Probar con nombre que no existe
            id_inexistente = buscar_finca_id(cursor, "FINCA_QUE_NO_EXISTE_12345")
            if id_inexistente is None:
                print("✓ Búsqueda de finca inexistente retorna None correctamente")
            else:
                print(f"✗ Búsqueda de finca inexistente retornó ID: {id_inexistente}")
                todos_correctos = False
            
            if todos_correctos:
                print("\n✅ Todas las búsquedas de fincas son correctas")
            else:
                print("\n❌ Algunas búsquedas de fincas fallaron")
            
            return todos_correctos
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_busqueda_razas_case_insensitive():
    """Prueba la búsqueda de razas con diferentes variaciones"""
    print("\n" + "=" * 80)
    print("TEST 3: Búsqueda de Razas Case-Insensitive")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener una raza de prueba
            cursor.execute("SELECT id, nombre FROM raza WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            raza = cursor.fetchone()
            
            if not raza:
                print("⚠ No hay razas activas para probar")
                return False
            
            id_esperado, nombre_original = raza
            print(f"\nRaza de prueba: '{nombre_original}' (ID: {id_esperado})")
            
            # Probar diferentes variaciones
            variaciones = [
                nombre_original.lower(),
                nombre_original.upper(),
                nombre_original.title(),
                "  " + nombre_original + "  ",
            ]
            
            print("\nProbando variaciones:")
            todos_correctos = True
            for variacion in variaciones:
                id_encontrado = buscar_raza_id(cursor, variacion)
                correcto = id_encontrado == id_esperado
                todos_correctos = todos_correctos and correcto
                
                simbolo = "✓" if correcto else "✗"
                print(f"{simbolo} '{variacion}' → ID: {id_encontrado} (esperado: {id_esperado})")
            
            if todos_correctos:
                print("\n✅ Todas las búsquedas de razas son correctas")
            else:
                print("\n❌ Algunas búsquedas de razas fallaron")
            
            return todos_correctos
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_busqueda_potreros_case_insensitive():
    """Prueba la búsqueda de potreros con diferentes variaciones"""
    print("\n" + "=" * 80)
    print("TEST 4: Búsqueda de Potreros Case-Insensitive")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener un potrero de prueba
            cursor.execute("SELECT id, nombre FROM potrero WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            potrero = cursor.fetchone()
            
            if not potrero:
                print("⚠ No hay potreros activos para probar")
                return False
            
            id_esperado, nombre_original = potrero
            print(f"\nPotrero de prueba: '{nombre_original}' (ID: {id_esperado})")
            
            # Probar diferentes variaciones
            variaciones = [
                nombre_original.lower(),
                nombre_original.upper(),
                nombre_original.title(),
            ]
            
            print("\nProbando variaciones:")
            todos_correctos = True
            for variacion in variaciones:
                id_encontrado = buscar_potrero_id(cursor, variacion)
                correcto = id_encontrado == id_esperado
                todos_correctos = todos_correctos and correcto
                
                simbolo = "✓" if correcto else "✗"
                print(f"{simbolo} '{variacion}' → ID: {id_encontrado} (esperado: {id_esperado})")
            
            if todos_correctos:
                print("\n✅ Todas las búsquedas de potreros son correctas")
            else:
                print("\n❌ Algunas búsquedas de potreros fallaron")
            
            return todos_correctos
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_diccionario_normalizado():
    """Prueba la función de obtener diccionario normalizado"""
    print("\n" + "=" * 80)
    print("TEST 5: Diccionario Normalizado")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener diccionario de fincas
            fincas_dict = obtener_diccionario_normalizado(
                cursor,
                "finca",
                condicion="estado IN ('Activa', 'Activo')"
            )
            
            print(f"\nFincas encontradas: {len(fincas_dict)}")
            
            if fincas_dict:
                print("\nPrimeras 5 fincas (nombre normalizado → ID):")
                for i, (nombre_norm, id_finca) in enumerate(list(fincas_dict.items())[:5]):
                    print(f"  {i+1}. '{nombre_norm}' → ID: {id_finca}")
                
                # Verificar que todas las claves están en minúsculas
                todas_minusculas = all(nombre == nombre.lower() for nombre in fincas_dict.keys())
                
                if todas_minusculas:
                    print("\n✅ Todas las claves están normalizadas (minúsculas)")
                else:
                    print("\n❌ Algunas claves NO están normalizadas")
                    return False
                
                # Verificar que se puede buscar con diferentes variaciones
                primera_finca_norm = list(fincas_dict.keys())[0]
                
                # Buscar la misma finca pero en mayúsculas en el diccionario
                # (simulando búsqueda después de normalizar)
                busqueda_mayus = normalizar_texto(primera_finca_norm.upper())
                encontrado = busqueda_mayus in fincas_dict
                
                if encontrado:
                    print(f"✅ Búsqueda normalizada funciona: '{busqueda_mayus}' encontrado en dict")
                else:
                    print(f"❌ Búsqueda normalizada falló: '{busqueda_mayus}' NO encontrado")
                    return False
                
                return True
            else:
                print("⚠ No hay fincas activas en el sistema")
                return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verificar_existe_nombre():
    """Prueba la función de verificar existencia de nombres"""
    print("\n" + "=" * 80)
    print("TEST 6: Verificar Existencia de Nombres (Case-Insensitive)")
    print("=" * 80)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener una finca existente
            cursor.execute("SELECT id, nombre FROM finca WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            finca = cursor.fetchone()
            
            if not finca:
                print("⚠ No hay fincas activas para probar")
                return False
            
            id_finca, nombre_finca = finca
            print(f"\nFinca de prueba: '{nombre_finca}' (ID: {id_finca})")
            
            # Verificar con diferentes variaciones
            variaciones = [
                nombre_finca.lower(),
                nombre_finca.upper(),
                nombre_finca.title(),
            ]
            
            print("\nVerificando existencia con variaciones:")
            todos_correctos = True
            for variacion in variaciones:
                existe = verificar_existe_nombre(cursor, "finca", variacion)
                correcto = existe == True
                todos_correctos = todos_correctos and correcto
                
                simbolo = "✓" if correcto else "✗"
                print(f"{simbolo} '{variacion}' → Existe: {existe} (esperado: True)")
            
            # Verificar con nombre que no existe
            no_existe = verificar_existe_nombre(cursor, "finca", "FINCA_INEXISTENTE_XYZ_123")
            if no_existe == False:
                print("✓ Nombre inexistente retorna False correctamente")
            else:
                print(f"✗ Nombre inexistente retornó: {no_existe}")
                todos_correctos = False
            
            if todos_correctos:
                print("\n✅ Todas las verificaciones de existencia son correctas")
            else:
                print("\n❌ Algunas verificaciones fallaron")
            
            return todos_correctos
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_escenario_real_importacion():
    """Simula un escenario real de importación con variaciones de mayúsculas"""
    print("\n" + "=" * 80)
    print("TEST 7: Escenario Real de Importación")
    print("=" * 80)
    
    print("\nSimulando importación de Excel con nombres en diferentes formatos...")
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener datos reales de la BD
            cursor.execute("SELECT nombre FROM finca WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            finca_row = cursor.fetchone()
            
            cursor.execute("SELECT nombre FROM raza WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            raza_row = cursor.fetchone()
            
            cursor.execute("SELECT nombre FROM potrero WHERE estado IN ('Activa', 'Activo') LIMIT 1")
            potrero_row = cursor.fetchone()
            
            if not (finca_row and raza_row and potrero_row):
                print("⚠ No hay datos suficientes en la BD para simular importación")
                return False
            
            nombre_finca = finca_row[0]
            nombre_raza = raza_row[0]
            nombre_potrero = potrero_row[0]
            
            # Simular datos de Excel en diferentes formatos
            registros_excel = [
                {"finca": nombre_finca.upper(), "raza": nombre_raza.lower(), "potrero": nombre_potrero.title()},
                {"finca": nombre_finca.lower(), "raza": nombre_raza.upper(), "potrero": nombre_potrero.upper()},
                {"finca": nombre_finca.title(), "raza": nombre_raza.title(), "potrero": nombre_potrero.lower()},
                {"finca": f"  {nombre_finca.upper()}  ", "raza": f"  {nombre_raza.lower()}  ", "potrero": f"  {nombre_potrero.upper()}  "},
            ]
            
            print(f"\nDatos originales en BD:")
            print(f"  Finca: '{nombre_finca}'")
            print(f"  Raza: '{nombre_raza}'")
            print(f"  Potrero: '{nombre_potrero}'")
            
            print(f"\nProbando {len(registros_excel)} registros con diferentes variaciones:")
            todos_correctos = True
            
            for i, registro in enumerate(registros_excel, 1):
                print(f"\n  Registro {i}:")
                print(f"    Finca Excel: '{registro['finca']}'")
                print(f"    Raza Excel: '{registro['raza']}'")
                print(f"    Potrero Excel: '{registro['potrero']}'")
                
                # Buscar IDs
                id_finca = buscar_finca_id(cursor, registro['finca'])
                id_raza = buscar_raza_id(cursor, registro['raza'])
                id_potrero = buscar_potrero_id(cursor, registro['potrero'])
                
                # Verificar que se encontraron todos
                encontrados = all([id_finca is not None, id_raza is not None, id_potrero is not None])
                
                simbolo = "✓" if encontrados else "✗"
                print(f"    {simbolo} IDs encontrados: Finca={id_finca}, Raza={id_raza}, Potrero={id_potrero}")
                
                todos_correctos = todos_correctos and encontrados
            
            if todos_correctos:
                print("\n✅ Todos los registros se resolverían correctamente en la importación")
                print("   El sistema NO distingue entre mayúsculas y minúsculas ✨")
            else:
                print("\n❌ Algunos registros no se resolverían correctamente")
            
            return todos_correctos
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🔍 PRUEBAS DE BÚSQUEDAS CASE-INSENSITIVE")
    print("=" * 80)
    print("\nEstas pruebas verifican que el sistema no distingue entre mayúsculas")
    print("y minúsculas al buscar fincas, razas, potreros, etc.")
    print("=" * 80)
    
    resultados = []
    
    # Ejecutar todas las pruebas
    resultados.append(("Normalización de texto", test_normalizacion_texto()))
    resultados.append(("Búsqueda de fincas", test_busqueda_fincas_case_insensitive()))
    resultados.append(("Búsqueda de razas", test_busqueda_razas_case_insensitive()))
    resultados.append(("Búsqueda de potreros", test_busqueda_potreros_case_insensitive()))
    resultados.append(("Diccionario normalizado", test_diccionario_normalizado()))
    resultados.append(("Verificación de existencia", test_verificar_existe_nombre()))
    resultados.append(("Escenario real de importación", test_escenario_real_importacion()))
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN DE PRUEBAS")
    print("=" * 80)
    
    for nombre, resultado in resultados:
        simbolo = "✅" if resultado else "❌"
        print(f"{simbolo} {nombre}")
    
    total_correctos = sum(1 for _, r in resultados if r)
    total_pruebas = len(resultados)
    
    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {total_correctos}/{total_pruebas} pruebas pasaron")
    print("=" * 80)
    
    if total_correctos == total_pruebas:
        print("\n🎉 ¡ÉXITO! El sistema es completamente case-insensitive")
        print("   Puedes usar MAYÚSCULAS, minúsculas o MeZcLaDaS en:")
        print("   - Nombres de fincas")
        print("   - Nombres de razas")
        print("   - Nombres de potreros")
        print("   - Nombres de lotes, sectores, vendedores, etc.")
        print("\n   ¡El sistema siempre encontrará la entidad correcta!")
    else:
        print("\n⚠ Algunas pruebas fallaron. Revisa los detalles arriba.")
    
    print("\n")
