"""Script para verificar que todas las tablas esenciales existan y sean accesibles"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_connection

print("🔍 Verificando tablas esenciales del sistema...\n")

tablas_a_verificar = {
    'animal': 'Gestión de animales',
    'raza': 'Catálogo de razas',
    'finca': 'Catálogo de fincas',
    'potrero': 'Gestión de potreros',
    'lote': 'Agrupación por lotes',
    'grupo': 'Agrupación por grupos',
    'vendedor': 'Catálogo de vendedores',
    'empleado': 'Gestión de empleados',
    'pago_nomina': 'Registro de pagos',
    'tratamiento': 'Historial de tratamientos',
    'venta': 'Registro de ventas',
    'motivo_venta': 'Catálogo motivos de venta',
    'destino_venta': 'Catálogo destinos de venta',
    # Nuevos catálogos añadidos
    'sector': 'Catálogo de sectores',
    'calidad_animal': 'Catálogo de calidad animal',
    'tipo_explotacion': 'Catálogo tipos de explotación',
    'condicion_corporal': 'Catálogo condiciones corporales',
    'procedencia': 'Catálogo de procedencias'
}

resultados = {'ok': [], 'error': []}

with get_connection() as conn:
    cursor = conn.cursor()
    
    for tabla, descripcion in tablas_a_verificar.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"✅ {tabla:20} - {descripcion:35} ({count} registros)")
            resultados['ok'].append(tabla)
        except Exception as e:
            print(f"❌ {tabla:20} - ERROR: {str(e)[:50]}")
            resultados['error'].append(tabla)

print("\n" + "=" * 80)
print(f"\n📊 RESUMEN:")
print(f"  ✅ Tablas funcionando correctamente: {len(resultados['ok'])}/{len(tablas_a_verificar)}")
if resultados['error']:
    print(f"  ❌ Tablas con errores: {len(resultados['error'])}")
    for tabla in resultados['error']:
        print(f"     - {tabla}")
else:
    print(f"  🎉 Todas las tablas esenciales están funcionando correctamente!")

print("\n🔍 Verificando columna 'especie' en tabla raza...")
try:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(raza)")
        cols = [c[1] for c in cur.fetchall()]
        if 'especie' in cols:
            print("  ✅ Columna 'especie' presente en raza")
        else:
            print("  ❌ Falta columna 'especie' en raza")
except Exception as e:
    print(f"  ⚠️ No se pudo verificar columna especie: {e}")

print("\n✅ Verificación completada")
