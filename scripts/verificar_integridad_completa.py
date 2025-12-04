"""
Script Maestro de Verificación de Integridad del Sistema FincaFacil
Ejecuta todas las verificaciones necesarias para validar la base de datos
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_connection
from datetime import datetime

print("=" * 80)
print("🔍 VERIFICACIÓN COMPLETA DE INTEGRIDAD - FINCAFACIL")
print("=" * 80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# 1. VERIFICACIÓN DE TABLAS ESENCIALES
# ============================================================================
print("📋 PASO 1: Verificando tablas esenciales del sistema...")
print("-" * 80)

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
    'sector': 'Catálogo de sectores',
    'calidad_animal': 'Catálogo de calidad animal',
    'tipo_explotacion': 'Catálogo tipos de explotación',
    'condicion_corporal': 'Catálogo condiciones corporales',
    'procedencia': 'Catálogo de procedencias'
}

resultados_tablas = {'ok': [], 'error': []}

with get_connection() as conn:
    cursor = conn.cursor()
    
    for tabla, descripcion in tablas_a_verificar.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"✅ {tabla:22} - {descripcion:35} ({count} registros)")
            resultados_tablas['ok'].append(tabla)
        except Exception as e:
            print(f"❌ {tabla:22} - ERROR: {str(e)[:50]}")
            resultados_tablas['error'].append((tabla, str(e)))

print(f"\n📊 Subtotal Tablas: {len(resultados_tablas['ok'])}/{len(tablas_a_verificar)} OK")

# ============================================================================
# 2. VERIFICACIÓN DE COLUMNAS CRÍTICAS
# ============================================================================
print("\n📋 PASO 2: Verificando columnas críticas...")
print("-" * 80)

verificaciones_columnas = []

# Verificar columna especie en raza
try:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(raza)")
        cols_raza = [c[1] for c in cur.fetchall()]
        if 'especie' in cols_raza:
            print("✅ Columna 'especie' presente en tabla 'raza'")
            verificaciones_columnas.append(('raza.especie', True, None))
        else:
            print("❌ Falta columna 'especie' en tabla 'raza'")
            verificaciones_columnas.append(('raza.especie', False, 'Columna no encontrada'))
except Exception as e:
    print(f"⚠️ Error verificando raza.especie: {e}")
    verificaciones_columnas.append(('raza.especie', False, str(e)))

# Verificar columnas clave en tabla animal
try:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(animal)")
        cols_animal = {c[1] for c in cur.fetchall()}
        
        # Columnas críticas tras normalización (se eliminan id_raza, id_lote y la columna textual raza)
        columnas_criticas_animal = [
            'id', 'codigo', 'raza_id', 'id_finca', 'id_potrero',
            'lote_id', 'id_grupo', 'id_vendedor', 'estado', 'inventariado'
        ]
        
        for col in columnas_criticas_animal:
            if col in cols_animal:
                verificaciones_columnas.append((f'animal.{col}', True, None))
            else:
                print(f"⚠️ Falta columna '{col}' en tabla 'animal'")
                verificaciones_columnas.append((f'animal.{col}', False, 'Columna no encontrada'))
        
        print(f"✅ Columnas críticas de 'animal': {len([c for c in columnas_criticas_animal if c in cols_animal])}/{len(columnas_criticas_animal)}")
        
except Exception as e:
    print(f"❌ Error verificando tabla animal: {e}")

# ============================================================================
# 3. VERIFICACIÓN DE ÍNDICES
# ============================================================================
print("\n📋 PASO 3: Verificando índices de rendimiento...")
print("-" * 80)

indices_esperados = [
    'idx_animal_codigo',
    'idx_animal_estado',
    'idx_venta_fecha',
    'idx_venta_animal',
    'idx_tratamiento_animal_fecha',
    'idx_empleado_estado',
    'idx_potrero_finca',
    'idx_sector_codigo',
    'idx_calidad_animal_codigo',
    'idx_tipo_explotacion_codigo',
    'idx_condicion_corporal_codigo',
    'idx_procedencia_codigo'
]

resultados_indices = {'ok': [], 'error': []}

try:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indices_actuales = {row[0] for row in cur.fetchall()}
        
        for idx in indices_esperados:
            if idx in indices_actuales:
                print(f"✅ Índice '{idx}' presente")
                resultados_indices['ok'].append(idx)
            else:
                print(f"⚠️ Índice '{idx}' no encontrado")
                resultados_indices['error'].append(idx)
        
        print(f"\n📊 Subtotal Índices: {len(resultados_indices['ok'])}/{len(indices_esperados)} presentes")
        
except Exception as e:
    print(f"❌ Error verificando índices: {e}")

# ============================================================================
# 4. VERIFICACIÓN DE INTEGRIDAD REFERENCIAL
# ============================================================================
print("\n📋 PASO 4: Verificando integridad referencial...")
print("-" * 80)

problemas_integridad = []

try:
    with get_connection() as conn:
        cur = conn.cursor()
        
        # Verificar animales sin raza válida (post-normalización solo usa raza_id)
        cur.execute(
            """
            SELECT COUNT(*) FROM animal 
            WHERE raza_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM raza 
                  WHERE raza.id = animal.raza_id
              )
            """
        )
        animales_sin_raza = cur.fetchone()[0]
        if animales_sin_raza > 0:
            print(f"⚠️ {animales_sin_raza} animales con referencia de raza inválida")
            problemas_integridad.append(f"Animales sin raza válida: {animales_sin_raza}")
        else:
            print("✅ Referencias raza → animal: OK")
        
        # Verificar ventas sin animal válido
        cur.execute("""
            SELECT COUNT(*) FROM venta 
            WHERE NOT EXISTS (SELECT 1 FROM animal WHERE animal.id = venta.animal_id)
        """)
        ventas_sin_animal = cur.fetchone()[0]
        if ventas_sin_animal > 0:
            print(f"⚠️ {ventas_sin_animal} ventas con referencia de animal inválida")
            problemas_integridad.append(f"Ventas sin animal válido: {ventas_sin_animal}")
        else:
            print("✅ Referencias animal → venta: OK")
        
        # Verificar tratamientos sin animal válido
        cur.execute("""
            SELECT COUNT(*) FROM tratamiento 
            WHERE NOT EXISTS (SELECT 1 FROM animal WHERE animal.id = tratamiento.id_animal)
        """)
        tratamientos_sin_animal = cur.fetchone()[0]
        if tratamientos_sin_animal > 0:
            print(f"⚠️ {tratamientos_sin_animal} tratamientos con referencia de animal inválida")
            problemas_integridad.append(f"Tratamientos sin animal válido: {tratamientos_sin_animal}")
        else:
            print("✅ Referencias animal → tratamiento: OK")
        
        print(f"\n📊 Problemas de integridad detectados: {len(problemas_integridad)}")
        
except Exception as e:
    print(f"❌ Error verificando integridad referencial: {e}")

# ============================================================================
# 5. RESUMEN FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📊 RESUMEN GENERAL DE INTEGRIDAD")
print("=" * 80)

total_problemas = len(resultados_tablas['error']) + len(problemas_integridad)
total_ok = len(resultados_tablas['ok'])

print(f"\n✅ TABLAS FUNCIONANDO: {total_ok}/{len(tablas_a_verificar)}")
if resultados_tablas['error']:
    print(f"❌ TABLAS CON ERRORES: {len(resultados_tablas['error'])}")
    for tabla, error in resultados_tablas['error']:
        print(f"   - {tabla}: {error[:60]}")

print(f"\n✅ ÍNDICES PRESENTES: {len(resultados_indices['ok'])}/{len(indices_esperados)}")
if resultados_indices['error']:
    print(f"⚠️ ÍNDICES FALTANTES: {len(resultados_indices['error'])}")
    for idx in resultados_indices['error'][:5]:  # Mostrar máximo 5
        print(f"   - {idx}")

print(f"\n✅ COLUMNAS CRÍTICAS: {len([c for c in verificaciones_columnas if c[1]])}/{len(verificaciones_columnas)}")
columnas_error = [c for c in verificaciones_columnas if not c[1]]
if columnas_error:
    print(f"⚠️ COLUMNAS CON PROBLEMAS: {len(columnas_error)}")
    for col, _, error in columnas_error[:5]:
        print(f"   - {col}: {error}")

if problemas_integridad:
    print(f"\n⚠️ PROBLEMAS DE INTEGRIDAD REFERENCIAL:")
    for problema in problemas_integridad:
        print(f"   - {problema}")
else:
    print(f"\n✅ INTEGRIDAD REFERENCIAL: OK (sin problemas detectados)")

print("\n" + "=" * 80)
if total_problemas == 0 and not resultados_indices['error'] and not columnas_error:
    print("🎉 RESULTADO: SISTEMA EN PERFECTO ESTADO")
    print("   Todas las tablas, índices y referencias están correctamente configurados.")
elif total_problemas == 0:
    print("✅ RESULTADO: SISTEMA FUNCIONAL")
    print("   Base de datos operativa. Considere crear los índices faltantes para mejor rendimiento.")
else:
    print("⚠️ RESULTADO: SE ENCONTRARON PROBLEMAS")
    print(f"   {total_problemas} problemas críticos requieren atención.")
    print("   Revise los detalles anteriores y corrija las tablas/referencias con errores.")

print("=" * 80)
print(f"\n✅ Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
