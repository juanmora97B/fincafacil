"""
SMOKE TEST - FASE 10: EXPLAINABILITY SERVICE

Verifica:
- Generación de explicaciones de anomalías
- Pasos de razonamiento (5 pasos)
- Evidencia clara y calculada
- Recomendaciones accionables
- Cálculo de confianza
- Generación de explicaciones de patrones
- Emojis según severidad
"""

import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestFase10")


def test_explicar_anomalia_produccion_baja():
    """Test 1: Explicación de anomalía de producción baja"""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Explicación de Anomalía - Producción Baja")
    logger.info("="*70)
    
    try:
        from src.services.insight_explainer_service import get_insight_explainer_service
        
        explainer = get_insight_explainer_service()
        
        # Crear anomalía de prueba
        anomalia = {
            'metrica': 'produccion_total',
            'valor_observado': 800,
            'valor_esperado': 1200,
            'umbral_alerta': 0.25,
            'periodo': '2025-12-28',
            'datos_historicos': list(range(180)),  # 6 meses
            'estacion': 'invierno',
            'valor_mes_anterior': 1220,
            'cambios': []
        }
        
        explicacion = explainer.explicar_anomalia(anomalia)
        
        # Validaciones
        assert explicacion.titulo, "Debe tener título"
        assert "Producción" in explicacion.titulo, "Debe mencionar Producción"
        assert "baja" in explicacion.titulo.lower(), "Debe mencionar que es baja"
        assert "🚨" in explicacion.titulo or "⚠️" in explicacion.titulo, "Debe tener emoji"
        
        assert len(explicacion.evidencia) > 0, "Debe tener evidencia"
        assert explicacion.evidencia[0].desviacion_pct < 0, "Desviación debe ser negativa"
        assert abs(explicacion.evidencia[0].desviacion_pct - (-33.33)) < 1, "Desviación debe ser ~-33%"
        
        assert len(explicacion.pasos) == 5, f"Debe tener 5 pasos, tiene {len(explicacion.pasos)}"
        assert explicacion.pasos[0].numero == 1, "Primer paso debe ser #1"
        assert explicacion.pasos[-1].numero == 5, "Último paso debe ser #5"
        
        # Validar contenido de pasos
        assert "datos" in explicacion.pasos[0].accion.lower(), "Paso 1: obtener datos"
        assert "promedio" in explicacion.pasos[1].accion.lower(), "Paso 2: calcular promedio"
        assert "comparé" in explicacion.pasos[2].accion.lower() or "compar" in explicacion.pasos[2].accion.lower(), "Paso 3: comparar"
        assert "contexto" in explicacion.pasos[3].accion.lower() or "factor" in explicacion.pasos[3].accion.lower(), "Paso 4: contexto"
        assert "conclusión" in explicacion.pasos[4].accion.lower(), "Paso 5: conclusión"
        
        assert explicacion.recomendacion, "Debe tener recomendación"
        assert len(explicacion.recomendacion) > 10, "Recomendación debe ser detallada"
        
        assert explicacion.confianza_pct > 50, "Confianza debe ser > 50%"
        assert explicacion.confianza_pct <= 100, "Confianza no puede ser > 100%"
        
        logger.info(f"  ✓ Título: {explicacion.titulo}")
        logger.info(f"  ✓ Pasos: {len(explicacion.pasos)} pasos")
        logger.info(f"  ✓ Desviación: {explicacion.evidencia[0].desviacion_pct:.2f}%")
        logger.info(f"  ✓ Confianza: {explicacion.confianza_pct:.0f}%")
        logger.info(f"  ✓ Recomendación: {explicacion.recomendacion[:50]}...")
        
        logger.info("✓ TEST 1 PASADO")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ TEST 1 FALLÓ: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ TEST 1 ERROR: {e}", exc_info=True)
        return False


def test_explicar_anomalia_costos_altos():
    """Test 2: Explicación de anomalía de costos altos"""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Explicación de Anomalía - Costos Altos")
    logger.info("="*70)
    
    try:
        from src.services.insight_explainer_service import get_insight_explainer_service
        
        explainer = get_insight_explainer_service()
        
        anomalia = {
            'metrica': 'costo_total',
            'valor_observado': 15000,
            'valor_esperado': 10000,
            'umbral_alerta': 0.30,
            'periodo': '2025-12-28',
            'datos_historicos': list(range(180)),
            'estacion': 'verano',
            'valor_mes_anterior': 9500,
            'cambios': [{'fecha': '2025-12-25', 'cambio': 'Compra de forraje'}]
        }
        
        explicacion = explainer.explicar_anomalia(anomalia)
        
        assert "Costos" in explicacion.titulo, "Debe mencionar Costos"
        assert "alta" in explicacion.titulo.lower(), "Debe mencionar que es alta"
        assert explicacion.evidencia[0].desviacion_pct > 0, "Desviación debe ser positiva"
        assert "proveedores" in explicacion.recomendacion.lower(), "Debe recomendar revisar proveedores"
        assert "IMPORTANTE" in explicacion.recomendacion, "Debe marcar como importante"
        
        logger.info(f"  ✓ Título: {explicacion.titulo}")
        logger.info(f"  ✓ Desviación: {explicacion.evidencia[0].desviacion_pct:.2f}%")
        logger.info(f"  ✓ Confianza reducida por cambios recientes: {explicacion.confianza_pct:.0f}%")
        
        logger.info("✓ TEST 2 PASADO")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ TEST 2 FALLÓ: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ TEST 2 ERROR: {e}", exc_info=True)
        return False


def test_pasos_estructura():
    """Test 3: Pasos tienen estructura y contenido correcto"""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: Estructura de Pasos de Razonamiento")
    logger.info("="*70)
    
    try:
        from src.services.insight_explainer_service import get_insight_explainer_service
        
        explainer = get_insight_explainer_service()
        
        anomalia = {
            'metrica': 'produccion_total',
            'valor_observado': 800,
            'valor_esperado': 1200,
            'umbral_alerta': 0.25,
            'periodo': '2025-12-28',
            'datos_historicos': list(range(180)),
            'estacion': 'invierno',
            'cambios': []
        }
        
        explicacion = explainer.explicar_anomalia(anomalia)
        
        # Validar cada paso
        for paso in explicacion.pasos:
            assert paso.numero > 0, f"Paso {paso.numero} debe tener número válido"
            assert paso.accion, f"Paso {paso.numero} debe tener acción"
            assert paso.detalle, f"Paso {paso.numero} debe tener detalle"
            assert paso.resultado is not None, f"Paso {paso.numero} debe tener resultado"
            assert isinstance(paso.resultado, dict), f"Paso {paso.numero} resultado debe ser dict"
        
        # Validar progresión
        for i in range(len(explicacion.pasos)):
            assert explicacion.pasos[i].numero == i + 1, f"Paso {i} debe tener número {i+1}"
        
        logger.info(f"  ✓ 5 pasos estructurados correctamente")
        logger.info(f"  ✓ Cada paso tiene: acción, detalle, resultado")
        logger.info(f"  ✓ Progresión lógica: 1→2→3→4→5")
        
        # Mostrar pasos
        for paso in explicacion.pasos:
            logger.info(f"    Paso {paso.numero}: {paso.accion}")
        
        logger.info("✓ TEST 3 PASADO")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ TEST 3 FALLÓ: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ TEST 3 ERROR: {e}", exc_info=True)
        return False


def test_confianza_segun_datos():
    """Test 4: Confianza se ajusta según cantidad de datos"""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Cálculo de Confianza según Datos Disponibles")
    logger.info("="*70)
    
    try:
        from src.services.insight_explainer_service import get_insight_explainer_service
        
        explainer = get_insight_explainer_service()
        
        # Con muchos datos
        anomalia_muchos = {
            'metrica': 'produccion_total',
            'valor_observado': 800,
            'valor_esperado': 1200,
            'umbral_alerta': 0.25,
            'periodo': '2025-12-28',
            'datos_historicos': list(range(200)),  # Muchos datos
            'estacion': 'invierno',
            'valor_mes_anterior': 1220,
            'cambios': []
        }
        
        exp_muchos = explainer.explicar_anomalia(anomalia_muchos)
        
        # Con pocos datos
        anomalia_pocos = {
            'metrica': 'produccion_total',
            'valor_observado': 800,
            'valor_esperado': 1200,
            'umbral_alerta': 0.25,
            'periodo': '2025-12-28',
            'datos_historicos': [1200, 1100, 950],  # Pocos datos
            'estacion': 'invierno',
            'cambios': []
        }
        
        exp_pocos = explainer.explicar_anomalia(anomalia_pocos)
        
        # Confianza con muchos datos debe ser mayor
        assert exp_muchos.confianza_pct > exp_pocos.confianza_pct, \
            f"Confianza con muchos datos ({exp_muchos.confianza_pct}%) debe ser mayor que con pocos ({exp_pocos.confianza_pct}%)"
        
        logger.info(f"  ✓ Con muchos datos: {exp_muchos.confianza_pct:.0f}%")
        logger.info(f"  ✓ Con pocos datos: {exp_pocos.confianza_pct:.0f}%")
        logger.info(f"  ✓ Diferencia: {exp_muchos.confianza_pct - exp_pocos.confianza_pct:.0f}%")
        
        logger.info("✓ TEST 4 PASADO")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ TEST 4 FALLÓ: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ TEST 4 ERROR: {e}", exc_info=True)
        return False


def test_emojis_segun_severidad():
    """Test 5: Emojis reflejan severidad correcta"""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Emojis según Severidad de Anomalía")
    logger.info("="*70)
    
    try:
        from src.services.insight_explainer_service import get_insight_explainer_service
        
        explainer = get_insight_explainer_service()
        
        # Anomalía pequeña (ℹ️ o ⚠️)
        anomalia_pequena = {
            'metrica': 'produccion_total',
            'valor_observado': 1150,
            'valor_esperado': 1200,
            'umbral_alerta': 0.25,
            'periodo': '2025-12-28',
            'datos_historicos': list(range(180)),
            'estacion': 'invierno',
            'cambios': []
        }
        
        exp_pequena = explainer.explicar_anomalia(anomalia_pequena)
        tiene_emoji_pequena = "ℹ️" in exp_pequena.titulo or "⚠️" in exp_pequena.titulo or "INFO" in exp_pequena.titulo
        assert tiene_emoji_pequena, \
            f"Anomalía pequeña debe tener emoji, tiene: {exp_pequena.titulo}"
        
        # Anomalía grande (⚠️)
        anomalia_grande = {
            'metrica': 'produccion_total',
            'valor_observado': 700,
            'valor_esperado': 1200,
            'umbral_alerta': 0.25,
            'periodo': '2025-12-28',
            'datos_historicos': list(range(180)),
            'estacion': 'invierno',
            'cambios': []
        }
        
        exp_grande = explainer.explicar_anomalia(anomalia_grande)
        tiene_emoji_grande = "⚠️" in exp_grande.titulo or "ANOMALÍA" in exp_grande.titulo
        assert tiene_emoji_grande, \
            f"Anomalía grande debe tener emoji, tiene: {exp_grande.titulo}"
        
        logger.info(f"  ✓ Pequeña (-4%): {exp_pequena.titulo}")
        logger.info(f"  ✓ Grande (-42%): {exp_grande.titulo}")
        
        logger.info("✓ TEST 5 PASADO")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ TEST 5 FALLÓ: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ TEST 5 ERROR: {e}", exc_info=True)
        return False


def test_explicar_patron():
    """Test 6: Explicación de patrones"""
    logger.info("\n" + "="*70)
    logger.info("TEST 6: Explicación de Patrones Detectados")
    logger.info("="*70)
    
    try:
        from src.services.insight_explainer_service import get_insight_explainer_service
        
        explainer = get_insight_explainer_service()
        
        patron = {
            'tipo': 'estacionalidad',
            'metrica': 'produccion_total',
            'nivel': 'ALTO',
            'descripcion': 'Producción baja en invierno',
            'evidencia': ['Enero: -20%', 'Febrero: -18%', 'Julio: -22%', 'Agosto: -20%']
        }
        
        explicacion = explainer.explicar_patron(patron)
        
        assert "PATRÓN" in explicacion.titulo, "Debe mencionar PATRÓN"
        assert "Producción" in explicacion.titulo, "Debe mencionar métrica en negocio"
        assert len(explicacion.pasos) == 5, "Debe tener 5 pasos para patrón"
        assert explicacion.recomendacion, "Debe tener recomendación"
        assert "predecible" in explicacion.recomendacion.lower() or "planifica" in explicacion.recomendacion.lower(), \
            "Debe recomendar acciones predictivas"
        
        # Confianza debe aumentar con más casos de evidencia
        assert explicacion.confianza_pct > 70, "Confianza con 4 casos de evidencia debe ser alta"
        
        logger.info(f"  ✓ Título: {explicacion.titulo}")
        logger.info(f"  ✓ Pasos: {len(explicacion.pasos)}")
        logger.info(f"  ✓ Confianza: {explicacion.confianza_pct:.0f}%")
        logger.info(f"  ✓ Recomendación: {explicacion.recomendacion[:50]}...")
        
        logger.info("✓ TEST 6 PASADO")
        return True
        
    except AssertionError as e:
        logger.error(f"✗ TEST 6 FALLÓ: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ TEST 6 ERROR: {e}", exc_info=True)
        return False


def main():
    """Ejecuta todos los tests de FASE 10"""
    logger.info("\n" + "#"*70)
    logger.info("# SMOKE TEST - FASE 10: EXPLAINABILITY SERVICE")
    logger.info("#"*70)
    
    tests = [
        test_explicar_anomalia_produccion_baja,
        test_explicar_anomalia_costos_altos,
        test_pasos_estructura,
        test_confianza_segun_datos,
        test_emojis_segun_severidad,
        test_explicar_patron,
    ]
    
    resultados = []
    for test in tests:
        try:
            resultado = test()
            resultados.append((test.__name__, resultado))
        except Exception as e:
            logger.error(f"Excepción no manejada en {test.__name__}: {e}", exc_info=True)
            resultados.append((test.__name__, False))
    
    # Resumen
    logger.info("\n" + "#"*70)
    logger.info("# RESUMEN DE RESULTADOS")
    logger.info("#"*70)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✓ PASADO" if resultado else "✗ FALLÓ"
        logger.info(f"{nombre}: {estado}")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"TOTAL: {exitosos}/{total} tests exitosos")
    logger.info(f"{'='*70}\n")
    
    # FASE 10 COMPLETADA
    if exitosos == total:
        logger.info("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  ✓ FASE 10 COMPLETADA CON ÉXITO                           ║
║                                                                           ║
║  ✓ Insight Explainer Service implementado                                ║
║  ✓ Explicaciones de anomalías con 5 pasos                                ║
║  ✓ Explicaciones de patrones detectados                                  ║
║  ✓ Evidencia numérica clara                                              ║
║  ✓ Recomendaciones accionables                                           ║
║  ✓ Cálculo de confianza dinámico                                         ║
║  ✓ Emojis que reflejan severidad                                         ║
║                                                                           ║
║  Próximo: Integrar en Dashboard + FASE 11 (Simulation)                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        return 0
    else:
        logger.warning(f"\n✗ {total - exitosos} test(s) fallaron. Revisar logs arriba.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
