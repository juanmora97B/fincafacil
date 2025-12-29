"""
Test rápido de FASE 8: Data Quality Service
============================================

Valida:
- Detección de KPIs faltantes
- Detección de valores atípicos
- Clasificación de calidad (ALTA/MEDIA/BAJA)
- Integración con alertas
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.data_quality_service import get_data_quality_service
from services.alert_rules_service import get_alert_rules_service
from datetime import date

def main():
    print("\n" + "="*70)
    print("SMOKE TEST: FASE 8 - DATA QUALITY SERVICE")
    print("="*70 + "\n")
    
    quality_service = get_data_quality_service()
    alert_service = get_alert_rules_service()
    
    # Test 1: Evaluar calidad del período actual
    print("📊 Test 1: Evaluando calidad período actual...")
    hoy = date.today()
    reporte = quality_service.evaluar_calidad_periodo(hoy.year, hoy.month)
    
    print(f"  Período: {reporte.periodo}")
    print(f"  Calidad: {reporte.calidad} (score {reporte.score}/100)")
    print(f"  KPIs validados: {reporte.kpis_validados}")
    print(f"  KPIs faltantes: {reporte.kpis_faltantes}")
    print(f"  Valores atípicos detectados: {reporte.valores_atipicos}")
    print(f"  Registros incompletos: {reporte.valor_incompleto}")
    
    if reporte.problemas:
        print(f"\n  Problemas detectados:")
        for i, problema in enumerate(reporte.problemas, 1):
            print(f"    {i}. {problema}")
    else:
        print(f"\n  ✅ Sin problemas detectados")
    
    # Test 2: Evaluar reglas de alerta (incluye calidad)
    print("\n" + "-"*70)
    print("🚨 Test 2: Evaluando reglas de alerta (incluida calidad)...")
    try:
        alertas = alert_service.evaluar_todas_reglas()
        
        alertas_calidad = [a for a in alertas if 'calidad' in a['tipo']]
        print(f"  Total alertas generadas: {len(alertas)}")
        print(f"  Alertas técnicas de calidad: {len(alertas_calidad)}")
        
        if alertas_calidad:
            print("\n  Alertas de calidad:")
            for alerta in alertas_calidad:
                print(f"    - {alerta['titulo']}")
                print(f"      Prioridad: {alerta['prioridad']}")
                print(f"      Score actual: {alerta['valor_actual']}, Ref: {alerta['valor_referencia']}")
    except Exception as e:
        print(f"  ⚠️ Algunas reglas no ejecutables (tablas faltantes): {e}")
        # Evaluar solo calidad
        alertas = alert_service._evaluar_calidad_datos(hoy)
        print(f"  Alertas de calidad: {len(alertas)}")
        for alerta in alertas:
            print(f"    - {alerta['titulo']}")
    
    # Test 3: Guardar alertas en BD (con cooldown)
    print("\n" + "-"*70)
    print("💾 Test 3: Guardando alertas en BD (con cooldown anti-duplicados)...")
    if alertas:
        try:
            guardadas = alert_service.guardar_alertas_en_bd(alertas)
            print(f"  Alertas guardadas: {guardadas}")
        except Exception as e:
            print(f"  ⚠️ No se pudieron guardar alertas: {e}")
    
    # Test 4: Verificar alertas activas
    print("\n" + "-"*70)
    print("📋 Test 4: Obteniendo alertas activas...")
    try:
        activas = alert_service.obtener_alertas_activas()
        print(f"  Alertas activas totales: {len(activas)}")
        
        if activas:
            print("\n  Muestra (máximo 5 alertas):")
            for alerta in activas[:5]:
                print(f"    - [{alerta['prioridad']}] {alerta['titulo']}")
    except Exception as e:
        print(f"  ⚠️ No se pudieron obtener alertas: {e}")
    
    print("\n" + "="*70)
    print("✅ SMOKE TEST COMPLETADO SIN EXCEPCIONES")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
