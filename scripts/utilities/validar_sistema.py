"""
Script para validar que todos los módulos del sistema funcionen correctamente
Ejecuta: python validar_sistema.py
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

def validar_modulos():
    """Valida que todos los módulos se puedan importar"""
    print("=" * 70)
    print("🔍 VALIDACIÓN DEL SISTEMA FINCAFACIL")
    print("=" * 70)
    print()
    
    modulos = [
        ("Dashboard", "modules.dashboard"),
        ("Animales", "modules.animales"),
        ("Ventas", "modules.ventas"),
        ("Tratamientos", "modules.tratamientos"),
        ("Reportes", "modules.reportes"),
        ("Potreros", "modules.potreros"),
        ("Configuración", "modules.configuracion"),
        ("Nómina", "modules.nomina"),
        ("Ajustes", "modules.ajustes"),
        ("Base de Datos", "database.conexion"),
    ]
    
    resultados = []
    
    for nombre, modulo in modulos:
        try:
            __import__(modulo)
            resultados.append((nombre, "✅ OK", None))
            print(f"✅ {nombre:20} - OK")
        except Exception as e:
            resultados.append((nombre, "❌ ERROR", str(e)))
            print(f"❌ {nombre:20} - ERROR: {e}")
    
    print()
    print("=" * 70)
    
    # Resumen
    ok = sum(1 for _, estado, _ in resultados if estado == "✅ OK")
    total = len(resultados)
    
    print(f"RESUMEN: {ok}/{total} módulos funcionando correctamente")
    print("=" * 70)
    
    if ok == total:
        print("🎉 ¡Todos los módulos están funcionando correctamente!")
    else:
        print("⚠️  Algunos módulos tienen problemas. Revisa los errores arriba.")
    
    print()
    
    # Validar base de datos
    print("Validando base de datos...")
    try:
        from database import db
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = cursor.fetchall()
            print(f"✅ Base de datos OK - {len(tablas)} tablas encontradas")
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
    
    print()
    print("=" * 70)
    return ok == total

if __name__ == "__main__":
    try:
        exito = validar_modulos()
        input("\nPresiona Enter para salir...")
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\nValidación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

