"""
TESTS FASE 14: RISK MANAGEMENT SERVICE
Validación completa de gestión de riesgos humanos
"""

import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from services.risk_management_service import (
    RiskManagementService,
    AccionRiesgosa,
    TipoPatronPeligroso,
    NivelRiesgoUsuario,
    get_risk_management_service
)
from datetime import datetime, timedelta


def test_registro_accion_riesgosa():
    """Test 1: Registrar acciones riesgosas"""
    print("\n" + "="*70)
    print("TEST 1: Registro de acciones riesgosas")
    print("="*70)
    
    service = RiskManagementService()
    
    # Registrar acción riesgosa
    accion = AccionRiesgosa(
        usuario="operador_1",
        tipo_accion="override_alerta",
        modulo="dashboard",
        descripcion="Override de alerta de producción baja",
        gravedad=6
    )
    
    service.registrar_accion_riesgosa(accion)
    
    print(f"✓ Acción registrada:")
    print(f"  - Usuario: {accion.usuario}")
    print(f"  - Tipo: {accion.tipo_accion}")
    print(f"  - Gravedad: {accion.gravedad}/10")
    print(f"  - Timestamp: {accion.timestamp}")
    
    # Validar que se registró
    assert "operador_1" in service.acciones_riesgosas, "Usuario debe estar registrado"
    assert len(service.acciones_riesgosas["operador_1"]) == 1, "Debe tener 1 acción"
    
    print("\n✅ TEST 1 EXITOSO: Acción riesgosa registrada")
    return True


def test_deteccion_overrides_frecuentes():
    """Test 2: Detectar patrón de overrides frecuentes"""
    print("\n" + "="*70)
    print("TEST 2: Detección de overrides frecuentes")
    print("="*70)
    
    service = RiskManagementService()
    
    # Registrar 6 overrides en 5 días (umbral = 5 en 7 días)
    for i in range(6):
        accion = AccionRiesgosa(
            usuario="operador_2",
            tipo_accion="override_alerta",
            modulo="dashboard",
            descripcion=f"Override {i+1}",
            gravedad=6,
            timestamp=datetime.now() - timedelta(days=i)
        )
        service.registrar_accion_riesgosa(accion)
    
    print(f"✓ Registradas 6 acciones de override en 6 días")
    
    # Verificar detección de patrón
    patrones = service.patrones_detectados.get("operador_2", [])
    
    print(f"✓ Patrones detectados: {len(patrones)}")
    
    patron_overrides = next(
        (p for p in patrones if p.tipo_patron == TipoPatronPeligroso.OVERRIDES_FRECUENTES),
        None
    )
    
    if patron_overrides:
        print(f"✓ Patrón OVERRIDES_FRECUENTES detectado:")
        print(f"  - Descripción: {patron_overrides.descripcion}")
        print(f"  - Ocurrencias: {patron_overrides.ocurrencias}")
        print(f"  - Gravedad: {patron_overrides.gravedad}/10")
    
    # Validaciones
    assert patron_overrides is not None, "Debe detectar patrón de overrides"
    assert patron_overrides.ocurrencias >= 5, "Debe detectar al menos 5 overrides"
    
    print("\n✅ TEST 2 EXITOSO: Patrón de overrides detectado")
    return True


def test_calculo_score_riesgo():
    """Test 3: Calcular score de riesgo de usuario"""
    print("\n" + "="*70)
    print("TEST 3: Cálculo de score de riesgo")
    print("="*70)
    
    service = RiskManagementService()
    
    # Registrar múltiples acciones riesgosas
    acciones_test = [
        ("override_alerta", 6),
        ("override_alerta", 6),
        ("override_alerta", 6),
        ("override_alerta", 7),
        ("override_alerta", 7),
        ("eliminacion_masiva", 9),
        ("eliminacion_masiva", 9),
        ("eliminacion_masiva", 9)
    ]
    
    for tipo, gravedad in acciones_test:
        accion = AccionRiesgosa(
            usuario="operador_3",
            tipo_accion=tipo,
            modulo="test",
            descripcion=f"Acción {tipo}",
            gravedad=gravedad
        )
        service.registrar_accion_riesgosa(accion)
    
    print(f"✓ Registradas {len(acciones_test)} acciones riesgosas")
    
    # Obtener score
    score = service.obtener_score_usuario("operador_3")
    
    # Validación de existencia antes de acceder a atributos
    assert score is not None, "Debe calcular score"
    
    print(f"\n✓ Score de riesgo calculado:")
    print(f"  - Score: {score.score}/100")
    print(f"  - Nivel: {score.nivel.value.upper()}")
    print(f"  - Requiere acción: {score.requiere_accion}")
    print(f"  - Causas ({len(score.causas)}):")
    for causa in score.causas[:3]:  # Mostrar primeras 3
        print(f"    • {causa}")
    print(f"  - Recomendación: {score.recomendacion}")
    
    # Validaciones
    assert score.score >= 0 and score.score <= 100, "Score debe estar en 0-100"
    assert score.nivel in NivelRiesgoUsuario, "Debe tener nivel válido"
    assert len(score.causas) > 0, "Debe tener causas"
    
    print("\n✅ TEST 3 EXITOSO: Score de riesgo calculado")
    return True


def test_niveles_riesgo_progresivos():
    """Test 4: Validar niveles de riesgo progresivos"""
    print("\n" + "="*70)
    print("TEST 4: Niveles de riesgo progresivos")
    print("="*70)
    
    service = RiskManagementService()
    
    # Usuario con bajo riesgo (2 acciones)
    for i in range(2):
        service.registrar_accion_riesgosa(
            AccionRiesgosa("bajo_riesgo", "override_alerta", "test", "Test", 5)
        )
    
    # Usuario con riesgo medio (8 acciones moderadas)
    for i in range(8):
        service.registrar_accion_riesgosa(
            AccionRiesgosa("medio_riesgo", "override_alerta", "test", "Test", 6)
        )
    
    # Usuario con alto riesgo (patrones múltiples)
    for i in range(6):
        service.registrar_accion_riesgosa(
            AccionRiesgosa("alto_riesgo", "override_alerta", "test", "Test", 7)
        )
    for i in range(4):
        service.registrar_accion_riesgosa(
            AccionRiesgosa("alto_riesgo", "eliminacion_masiva", "test", "Test", 9)
        )
    
    # Obtener scores
    score_bajo = service.obtener_score_usuario("bajo_riesgo")
    score_medio = service.obtener_score_usuario("medio_riesgo")
    score_alto = service.obtener_score_usuario("alto_riesgo")
    
    # Asegurar que existen antes de acceder a atributos
    assert score_bajo is not None
    assert score_medio is not None
    assert score_alto is not None
    
    print(f"✓ Usuario BAJO riesgo: Score {score_bajo.score} ({score_bajo.nivel.value})")
    print(f"✓ Usuario MEDIO riesgo: Score {score_medio.score} ({score_medio.nivel.value})")
    print(f"✓ Usuario ALTO riesgo: Score {score_alto.score} ({score_alto.nivel.value})")
    
    # Validaciones
    assert score_bajo.score < score_medio.score, "Bajo < Medio"
    assert score_medio.score < score_alto.score, "Medio < Alto"
    assert score_alto.nivel in [NivelRiesgoUsuario.ALTO, NivelRiesgoUsuario.CRITICO], "Alto debe ser ALTO o CRITICO"
    
    print("\n✅ TEST 4 EXITOSO: Niveles progresivos validados")
    return True


def test_deteccion_eliminaciones_masivas():
    """Test 5: Detectar patrón de eliminaciones masivas"""
    print("\n" + "="*70)
    print("TEST 5: Detección de eliminaciones masivas")
    print("="*70)
    
    service = RiskManagementService()
    
    # Registrar 4 eliminaciones masivas en 10 días (umbral = 3 en 14 días)
    for i in range(4):
        accion = AccionRiesgosa(
            usuario="operador_4",
            tipo_accion="eliminacion_masiva",
            modulo="animales",
            descripcion=f"Eliminación masiva {i+1}: 100+ registros",
            gravedad=9,
            timestamp=datetime.now() - timedelta(days=i*2)
        )
        service.registrar_accion_riesgosa(accion)
    
    print(f"✓ Registradas 4 eliminaciones masivas en 8 días")
    
    # Verificar patrón
    patrones = service.patrones_detectados.get("operador_4", [])
    patron_eliminaciones = next(
        (p for p in patrones if p.tipo_patron == TipoPatronPeligroso.ELIMINACIONES_MASIVAS),
        None
    )
    
    if patron_eliminaciones:
        print(f"✓ Patrón ELIMINACIONES_MASIVAS detectado:")
        print(f"  - Descripción: {patron_eliminaciones.descripcion}")
        print(f"  - Ocurrencias: {patron_eliminaciones.ocurrencias}")
        print(f"  - Gravedad: {patron_eliminaciones.gravedad}/10")
    
    # Validaciones
    assert patron_eliminaciones is not None, "Debe detectar patrón de eliminaciones"
    assert patron_eliminaciones.gravedad >= 8, "Debe tener gravedad alta"
    
    print("\n✅ TEST 5 EXITOSO: Patrón de eliminaciones detectado")
    return True


def test_alertas_operativas():
    """Test 6: Generar alertas operativas para administradores"""
    print("\n" + "="*70)
    print("TEST 6: Generación de alertas operativas")
    print("="*70)
    
    service = RiskManagementService()
    
    # Crear usuario con alto riesgo (score > 60)
    for i in range(7):
        service.registrar_accion_riesgosa(
            AccionRiesgosa("riesgo_alto", "override_alerta", "test", "Test", 7)
        )
    for i in range(4):
        service.registrar_accion_riesgosa(
            AccionRiesgosa("riesgo_alto", "eliminacion_masiva", "test", "Test", 9)
        )
    
    # Obtener alertas
    alertas = service.obtener_alertas_operativas()
    
    print(f"✓ Alertas operativas generadas: {len(alertas)}")
    
    if alertas:
        for alerta in alertas[:2]:  # Mostrar primeras 2
            print(f"\n✓ Alerta {alerta.nivel_alerta}:")
            print(f"  - Usuario: {alerta.usuario}")
            print(f"  - Score: {alerta.score_riesgo}/100")
            print(f"  - Mensaje: {alerta.mensaje}")
            print(f"  - Patrones: {len(alerta.patrones)}")
            print(f"  - Acciones sugeridas: {len(alerta.acciones_sugeridas)}")
    
    # Validaciones
    assert len(alertas) > 0, "Debe generar al menos 1 alerta"
    alerta_test = next((a for a in alertas if a.usuario == "riesgo_alto"), None)
    assert alerta_test is not None, "Debe generar alerta para usuario riesgo_alto"
    assert alerta_test.nivel_alerta in ["ATENCION", "URGENTE", "CRITICO"], "Nivel de alerta válido"
    
    print("\n✅ TEST 6 EXITOSO: Alertas operativas generadas")
    return True


def test_usuarios_alto_riesgo():
    """Test 7: Obtener lista de usuarios de alto riesgo"""
    print("\n" + "="*70)
    print("TEST 7: Lista de usuarios de alto riesgo")
    print("="*70)
    
    service = RiskManagementService()
    
    # Crear 3 usuarios con diferentes niveles de riesgo
    usuarios = [
        ("bajo_1", 2, 5),
        ("medio_1", 6, 6),
        ("alto_1", 10, 8)
    ]
    
    for usuario, cantidad, gravedad in usuarios:
        for i in range(cantidad):
            service.registrar_accion_riesgosa(
                AccionRiesgosa(usuario, "override_alerta", "test", "Test", gravedad)
            )
    
    # Obtener usuarios alto riesgo (umbral = 60)
    usuarios_riesgo = service.obtener_usuarios_alto_riesgo(umbral=60)
    
    print(f"✓ Usuarios con riesgo >= 60: {len(usuarios_riesgo)}")
    
    for usuario in usuarios_riesgo:
        print(f"  - {usuario.usuario}: Score {usuario.score} ({usuario.nivel.value})")
    
    # Validaciones
    assert isinstance(usuarios_riesgo, list), "Debe retornar lista"
    
    # Validar que están ordenados por score descendente
    if len(usuarios_riesgo) > 1:
        for i in range(len(usuarios_riesgo) - 1):
            assert usuarios_riesgo[i].score >= usuarios_riesgo[i+1].score, "Debe estar ordenado desc"
    
    print("\n✅ TEST 7 EXITOSO: Lista de usuarios de alto riesgo obtenida")
    return True


def test_reporte_mensual():
    """Test 8: Generar reporte mensual de riesgos"""
    print("\n" + "="*70)
    print("TEST 8: Reporte mensual de riesgos")
    print("="*70)
    
    service = RiskManagementService()
    
    # Registrar acciones en el mes actual
    ahora = datetime.now()
    for i in range(5):
        service.registrar_accion_riesgosa(
            AccionRiesgosa(
                f"usuario_{i % 3}",
                "override_alerta",
                "test",
                "Test",
                6 + i % 3
            )
        )
    
    # Generar reporte
    reporte = service.generar_reporte_mensual()
    
    print(f"✓ Reporte generado para: {reporte['mes']}/{reporte['anio']}")
    print(f"✓ Total acciones riesgosas: {reporte['total_acciones_riesgosas']}")
    print(f"✓ Usuarios con acciones: {reporte['usuarios_con_acciones']}")
    print(f"✓ Distribución por gravedad: {reporte['distribucion_gravedad']}")
    print(f"✓ Top usuarios riesgo: {len(reporte['top_usuarios_riesgo'])}")
    print(f"✓ Patrones más comunes: {reporte['patrones_mas_comunes']}")
    
    # Validaciones
    assert reporte['mes'] == ahora.month, "Debe ser mes actual"
    assert reporte['anio'] == ahora.year, "Debe ser año actual"
    assert reporte['total_acciones_riesgosas'] >= 0, "Total >= 0"
    assert 'timestamp_generacion' in reporte, "Debe tener timestamp"
    
    print("\n✅ TEST 8 EXITOSO: Reporte mensual generado")
    return True


def test_exportacion_datos():
    """Test 9: Exportar datos de riesgos a JSON"""
    print("\n" + "="*70)
    print("TEST 9: Exportación de datos de riesgos")
    print("="*70)
    
    service = RiskManagementService()
    
    # Registrar algunos datos
    for i in range(3):
        service.registrar_accion_riesgosa(
            AccionRiesgosa(f"usuario_{i}", "override_alerta", "test", "Test", 6)
        )
    
    # Exportar
    filepath = "test_risk_data.json"
    service.exportar_datos(filepath)
    
    print(f"✓ Datos exportados a: {filepath}")
    
    # Validar archivo
    import os
    assert os.path.exists(filepath), "Archivo debe existir"
    
    # Leer y validar contenido
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    print(f"✓ Total usuarios en archivo: {datos['total_usuarios']}")
    print(f"✓ Scores registrados: {len(datos['scores_riesgo'])}")
    print(f"✓ Alertas operativas: {len(datos['alertas_operativas'])}")
    
    assert datos['total_usuarios'] >= 0, "Total usuarios válido"
    assert 'timestamp_exportacion' in datos, "Debe tener timestamp"
    
    # Limpiar archivo test
    os.remove(filepath)
    
    print("\n✅ TEST 9 EXITOSO: Datos exportados correctamente")
    return True


def test_singleton_service():
    """Test 10: Validar singleton del servicio"""
    print("\n" + "="*70)
    print("TEST 10: Singleton del servicio")
    print("="*70)
    
    service1 = get_risk_management_service()
    service2 = get_risk_management_service()
    
    print(f"✓ Servicio 1: {id(service1)}")
    print(f"✓ Servicio 2: {id(service2)}")
    print(f"✓ Son la misma instancia: {service1 is service2}")
    
    # Validaciones
    assert service1 is service2, "Deben ser la misma instancia"
    
    print("\n✅ TEST 10 EXITOSO: Singleton funciona correctamente")
    return True


def run_all_tests():
    """Ejecuta todos los tests de FASE 14"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  FASE 14: RISK MANAGEMENT SERVICE - TEST SUITE COMPLETO".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    tests = [
        ("Registro acción riesgosa", test_registro_accion_riesgosa),
        ("Detección overrides frecuentes", test_deteccion_overrides_frecuentes),
        ("Cálculo score riesgo", test_calculo_score_riesgo),
        ("Niveles riesgo progresivos", test_niveles_riesgo_progresivos),
        ("Detección eliminaciones masivas", test_deteccion_eliminaciones_masivas),
        ("Alertas operativas", test_alertas_operativas),
        ("Usuarios alto riesgo", test_usuarios_alto_riesgo),
        ("Reporte mensual", test_reporte_mensual),
        ("Exportación datos", test_exportacion_datos),
        ("Singleton service", test_singleton_service)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            exito = test_func()
            resultados.append((nombre, exito))
        except AssertionError as e:
            print(f"\n❌ FALLO: {nombre}")
            print(f"   Error: {str(e)}")
            resultados.append((nombre, False))
        except Exception as e:
            print(f"\n❌ ERROR INESPERADO: {nombre}")
            print(f"   Error: {str(e)}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  RESUMEN FINAL - FASE 14".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    exitosos = sum(1 for _, exito in resultados if exito)
    total = len(resultados)
    
    for nombre, exito in resultados:
        simbolo = "✓" if exito else "✗"
        print(f"{simbolo} {nombre}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {exitosos}/{total} tests exitosos ({exitosos/total*100:.1f}%)")
    print("="*70)
    
    if exitosos == total:
        print("\n🎉 ¡FASE 14 COMPLETADA EXITOSAMENTE! 🎉")
        print("\n✅ Risk Management Service operativo")
        print("✅ Score de riesgo por usuario (0-100)")
        print("✅ Detección de patrones peligrosos")
        print("✅ Alertas operativas automáticas")
        print("✅ Reportes mensuales funcionando")
        print("✅ Listo para FASE 15: Soporte & Continuidad")
        return True
    else:
        print(f"\n⚠️ {total - exitosos} test(s) fallaron")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
