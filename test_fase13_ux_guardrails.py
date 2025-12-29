"""
TESTS FASE 13: UX GUARDRAILS SERVICE
Validación completa de protección contra errores humanos
"""

import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from services.ux_guardrails_service import (
    UXGuardrailsService,
    ContextoAccion,
    ErrorUX,
    TipoAccion,
    NivelRiesgo,
    ModoUsuario,
    get_ux_guardrails_service
)
from datetime import datetime


def test_analisis_riesgo_eliminacion():
    """Test 1: Analizar riesgo de eliminación de datos"""
    print("\n" + "="*70)
    print("TEST 1: Análisis de riesgo - Eliminación de datos")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Contexto: Eliminar 50 animales
    contexto = ContextoAccion(
        tipo_accion=TipoAccion.ELIMINAR_DATOS,
        usuario="operador_1",
        modulo="animales",
        datos_afectados={
            "cantidad_registros": 50,
            "tipo_dato": "animales"
        }
    )
    
    analisis = service.analizar_riesgo(contexto)
    
    print(f"✓ Nivel de riesgo: {analisis.nivel_riesgo.value.upper()}")
    print(f"✓ Requiere confirmación: {analisis.requiere_confirmacion}")
    print(f"✓ Puede revertirse: {analisis.puede_revertirse}")
    print(f"✓ Mensaje: {analisis.mensaje_advertencia}")
    print(f"✓ Consecuencias ({len(analisis.consecuencias)}):")
    for cons in analisis.consecuencias:
        print(f"  - {cons}")
    print(f"✓ Alternativas seguras ({len(analisis.alternativas_seguras)}):")
    for alt in analisis.alternativas_seguras:
        print(f"  - {alt}")
    
    # Validaciones
    assert analisis.nivel_riesgo == NivelRiesgo.ALTO, "Eliminación debe ser ALTO riesgo"
    assert analisis.requiere_confirmacion == True, "Debe requerir confirmación"
    assert analisis.puede_revertirse == False, "Eliminación NO es reversible"
    assert len(analisis.consecuencias) >= 3, "Debe listar consecuencias"
    assert len(analisis.alternativas_seguras) >= 2, "Debe ofrecer alternativas"
    
    print("\n✅ TEST 1 EXITOSO: Eliminación analizada correctamente")
    return True


def test_analisis_riesgo_cierre_periodo():
    """Test 2: Analizar riesgo de cierre de período"""
    print("\n" + "="*70)
    print("TEST 2: Análisis de riesgo - Cierre de período")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Contexto: Cierre mensual que bloquea 3 módulos
    contexto = ContextoAccion(
        tipo_accion=TipoAccion.CIERRE_PERIODO,
        usuario="admin",
        modulo="contabilidad",
        datos_afectados={
            "periodo": "Diciembre 2025",
            "modulos_bloqueados": ["produccion", "ventas", "costos"],
            "alertas_esperadas": 12
        }
    )
    
    analisis = service.analizar_riesgo(contexto)
    
    print(f"✓ Nivel de riesgo: {analisis.nivel_riesgo.value.upper()}")
    print(f"✓ Requiere confirmación: {analisis.requiere_confirmacion}")
    print(f"✓ Tiempo de impacto: {analisis.tiempo_estimado_impacto}")
    print(f"✓ Mensaje: {analisis.mensaje_advertencia}")
    print(f"✓ Acciones recomendadas:")
    for rec in analisis.acciones_recomendadas:
        print(f"  - {rec}")
    
    # Validaciones
    assert analisis.nivel_riesgo == NivelRiesgo.CRITICO, "Cierre período es CRITICO"
    assert analisis.requiere_confirmacion == True, "Debe requerir confirmación"
    assert "12 alertas" in analisis.mensaje_advertencia, "Debe mencionar alertas"
    assert "3 módulos" in analisis.mensaje_advertencia, "Debe mencionar módulos"
    assert len(analisis.acciones_recomendadas) >= 3, "Debe dar recomendaciones"
    
    print("\n✅ TEST 2 EXITOSO: Cierre de período analizado correctamente")
    return True


def test_modo_novato_bloqueos():
    """Test 3: Validar que modo novato bloquea acciones peligrosas"""
    print("\n" + "="*70)
    print("TEST 3: Modo Novato - Bloqueos de acciones peligrosas")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Acciones que un novato NO debe poder hacer
    acciones_bloqueadas = [
        TipoAccion.CIERRE_PERIODO,
        TipoAccion.DESACTIVAR_VALIDACION,
        TipoAccion.MODIFICAR_MASIVO
    ]
    
    bloqueados = 0
    for accion in acciones_bloqueadas:
        resultado = service.validar_modo_usuario("novato_1", accion, ModoUsuario.NOVATO)
        
        print(f"\n✓ Acción: {accion.value}")
        print(f"  - Permitido: {resultado['permitido']}")
        print(f"  - Razón: {resultado['razon']}")
        
        if not resultado['permitido']:
            bloqueados += 1
            assert "Novato" in resultado['razon'], "Debe mencionar modo Novato"
    
    print(f"\n✓ Total acciones bloqueadas para novato: {bloqueados}/{len(acciones_bloqueadas)}")
    
    # Validaciones
    assert bloqueados == len(acciones_bloqueadas), "Todas deben estar bloqueadas"
    
    # Ahora validar que un avanzado SÍ puede
    resultado_avanzado = service.validar_modo_usuario(
        "admin", 
        TipoAccion.CIERRE_PERIODO, 
        ModoUsuario.AVANZADO
    )
    
    print(f"\n✓ Usuario AVANZADO intentando CIERRE_PERIODO:")
    print(f"  - Permitido: {resultado_avanzado['permitido']}")
    
    assert resultado_avanzado['permitido'] == True, "Avanzado debe poder hacer cierre"
    
    print("\n✅ TEST 3 EXITOSO: Modo novato protege correctamente")
    return True


def test_tooltips_progresivos():
    """Test 4: Obtener tooltips según modo de usuario"""
    print("\n" + "="*70)
    print("TEST 4: Tooltips progresivos por modo usuario")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Novato: debe recibir TODOS los tooltips
    tooltips_novato = service.obtener_tooltips_para_usuario(
        ModoUsuario.NOVATO, 
        "dashboard"
    )
    
    print(f"✓ Tooltips para NOVATO en dashboard: {len(tooltips_novato)}")
    for tip in tooltips_novato[:3]:  # Mostrar primeros 3
        print(f"  - {tip.elemento}: {tip.mensaje[:50]}...")
    
    # Intermedio: solo tooltips prioritarios
    tooltips_intermedio = service.obtener_tooltips_para_usuario(
        ModoUsuario.INTERMEDIO,
        "dashboard"
    )
    
    print(f"\n✓ Tooltips para INTERMEDIO en dashboard: {len(tooltips_intermedio)}")
    
    # Avanzado: NO debe recibir tooltips
    tooltips_avanzado = service.obtener_tooltips_para_usuario(
        ModoUsuario.AVANZADO,
        "dashboard"
    )
    
    print(f"✓ Tooltips para AVANZADO en dashboard: {len(tooltips_avanzado)}")
    
    # Validaciones
    assert len(tooltips_novato) >= 2, "Novato debe recibir tooltips"
    assert len(tooltips_intermedio) < len(tooltips_novato), "Intermedio recibe menos que novato"
    assert len(tooltips_avanzado) == 0, "Avanzado no recibe tooltips"
    
    print("\n✅ TEST 4 EXITOSO: Tooltips progresivos funcionan")
    return True


def test_registro_errores_ux():
    """Test 5: Registrar y analizar errores UX"""
    print("\n" + "="*70)
    print("TEST 5: Registro y análisis de errores UX")
    print("="*70)
    
    service = UXGuardrailsService()  # Nueva instancia para test aislado
    
    # Registrar varios errores UX
    errores_test = [
        ErrorUX(
            usuario="operador_2",
            accion_intentada="buscar_animal",
            modulo="animales",
            mensaje_error="Animal no encontrado: CH-9999",
            modo_usuario=ModoUsuario.NOVATO
        ),
        ErrorUX(
            usuario="operador_2",
            accion_intentada="eliminar_produccion",
            modulo="produccion",
            mensaje_error="Permiso denegado",
            modo_usuario=ModoUsuario.NOVATO
        ),
        ErrorUX(
            usuario="operador_3",
            accion_intentada="cerrar_mes",
            modulo="contabilidad",
            mensaje_error="Período ya cerrado",
            modo_usuario=ModoUsuario.INTERMEDIO
        )
    ]
    
    for error in errores_test:
        service.registrar_error_ux(error)
        print(f"✓ Error registrado: {error.accion_intentada} → {error.mensaje_error}")
        print(f"  Sugerencia: {error.sugerencia_mejora}")
    
    # Obtener estadísticas
    stats = service.obtener_estadisticas_errores_ux(dias=7)
    
    print(f"\n✓ Estadísticas de errores UX:")
    print(f"  - Total errores: {stats['total_errores']}")
    print(f"  - Errores por módulo: {stats['errores_por_modulo']}")
    print(f"  - Errores por usuario: {stats['errores_por_usuario']}")
    print(f"  - Acciones problemáticas: {stats['acciones_mas_problematicas']}")
    
    # Validaciones
    assert stats['total_errores'] == 3, "Debe contar 3 errores"
    assert 'animales' in stats['errores_por_modulo'], "Debe agrupar por módulo"
    assert 'operador_2' in stats['errores_por_usuario'], "Debe agrupar por usuario"
    assert len(stats['acciones_mas_problematicas']) > 0, "Debe identificar acciones problemáticas"
    
    # Validar que se generaron sugerencias automáticas
    for error in errores_test:
        assert error.sugerencia_mejora is not None, "Debe generar sugerencia"
        assert len(error.sugerencia_mejora) > 0, "Sugerencia no vacía"
    
    print("\n✅ TEST 5 EXITOSO: Errores UX registrados y analizados")
    return True


def test_modificacion_masiva_validacion():
    """Test 6: Validar análisis de modificación masiva"""
    print("\n" + "="*70)
    print("TEST 6: Análisis de modificación masiva")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Contexto 1: Modificación pequeña (30 registros)
    contexto_pequeno = ContextoAccion(
        tipo_accion=TipoAccion.MODIFICAR_MASIVO,
        usuario="operador_1",
        modulo="animales",
        datos_afectados={
            "cantidad_registros": 30,
            "campos_modificados": ["peso", "estado"]
        }
    )
    
    analisis_pequeno = service.analizar_riesgo(contexto_pequeno)
    
    print(f"✓ Modificación PEQUEÑA (30 registros):")
    print(f"  - Nivel riesgo: {analisis_pequeno.nivel_riesgo.value}")
    print(f"  - Puede revertirse: {analisis_pequeno.puede_revertirse}")
    
    # Contexto 2: Modificación masiva (200 registros)
    contexto_grande = ContextoAccion(
        tipo_accion=TipoAccion.MODIFICAR_MASIVO,
        usuario="operador_1",
        modulo="animales",
        datos_afectados={
            "cantidad_registros": 200,
            "campos_modificados": ["estado", "lote", "sector"]
        }
    )
    
    analisis_grande = service.analizar_riesgo(contexto_grande)
    
    print(f"\n✓ Modificación MASIVA (200 registros):")
    print(f"  - Nivel riesgo: {analisis_grande.nivel_riesgo.value}")
    print(f"  - Puede revertirse: {analisis_grande.puede_revertirse}")
    print(f"  - Mensaje: {analisis_grande.mensaje_advertencia}")
    
    # Validaciones
    assert analisis_pequeno.nivel_riesgo == NivelRiesgo.MEDIO, "30 registros = MEDIO"
    assert analisis_grande.nivel_riesgo == NivelRiesgo.ALTO, "200 registros = ALTO"
    assert analisis_pequeno.puede_revertirse == True, "Modificaciones son reversibles"
    assert analisis_grande.puede_revertirse == True, "Modificaciones son reversibles"
    
    print("\n✅ TEST 6 EXITOSO: Modificación masiva validada")
    return True


def test_override_alerta_tracking():
    """Test 7: Rastrear overrides de alertas"""
    print("\n" + "="*70)
    print("TEST 7: Tracking de overrides de alertas")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Override de alerta MEDIA
    contexto_media = ContextoAccion(
        tipo_accion=TipoAccion.OVERRIDE_ALERTA,
        usuario="operador_1",
        modulo="dashboard",
        datos_afectados={
            "tipo_alerta": "Producción baja",
            "gravedad": "MEDIA"
        }
    )
    
    analisis_media = service.analizar_riesgo(contexto_media)
    
    print(f"✓ Override alerta MEDIA:")
    print(f"  - Nivel riesgo: {analisis_media.nivel_riesgo.value}")
    print(f"  - Requiere confirmación: {analisis_media.requiere_confirmacion}")
    
    # Override de alerta ALTA
    contexto_alta = ContextoAccion(
        tipo_accion=TipoAccion.OVERRIDE_ALERTA,
        usuario="operador_1",
        modulo="dashboard",
        datos_afectados={
            "tipo_alerta": "Mortalidad crítica",
            "gravedad": "ALTA"
        }
    )
    
    analisis_alta = service.analizar_riesgo(contexto_alta)
    
    print(f"\n✓ Override alerta ALTA:")
    print(f"  - Nivel riesgo: {analisis_alta.nivel_riesgo.value}")
    print(f"  - Requiere confirmación: {analisis_alta.requiere_confirmacion}")
    print(f"  - Mensaje: {analisis_alta.mensaje_advertencia}")
    
    # Validaciones
    assert analisis_media.nivel_riesgo == NivelRiesgo.MEDIO, "Alerta MEDIA = riesgo MEDIO"
    assert analisis_alta.nivel_riesgo == NivelRiesgo.ALTO, "Alerta ALTA = riesgo ALTO"
    assert analisis_media.puede_revertirse == False, "Override no es reversible"
    
    print("\n✅ TEST 7 EXITOSO: Override de alertas rastreado")
    return True


def test_eliminacion_masiva_critica():
    """Test 8: Detectar eliminación masiva como CRITICA"""
    print("\n" + "="*70)
    print("TEST 8: Detección de eliminación masiva crítica")
    print("="*70)
    
    service = get_ux_guardrails_service()
    
    # Eliminar >100 registros debe ser CRITICO
    contexto_masivo = ContextoAccion(
        tipo_accion=TipoAccion.ELIMINAR_DATOS,
        usuario="admin",
        modulo="produccion",
        datos_afectados={
            "cantidad_registros": 250,
            "tipo_dato": "registros de producción"
        }
    )
    
    analisis = service.analizar_riesgo(contexto_masivo)
    
    print(f"✓ Eliminación de {contexto_masivo.datos_afectados['cantidad_registros']} registros:")
    print(f"  - Nivel riesgo: {analisis.nivel_riesgo.value.upper()}")
    print(f"  - Mensaje: {analisis.mensaje_advertencia}")
    print(f"  - Consecuencias:")
    for cons in analisis.consecuencias:
        print(f"    • {cons}")
    
    # Validaciones
    assert analisis.nivel_riesgo == NivelRiesgo.CRITICO, ">100 registros = CRITICO"
    assert "250" in analisis.mensaje_advertencia, "Debe mencionar cantidad"
    assert "IRREVERSIBLE" in analisis.mensaje_advertencia.upper(), "Debe advertir irreversibilidad"
    
    print("\n✅ TEST 8 EXITOSO: Eliminación masiva detectada como CRITICA")
    return True


def test_exportacion_logs_ux():
    """Test 9: Exportar logs UX a archivo"""
    print("\n" + "="*70)
    print("TEST 9: Exportación de logs UX")
    print("="*70)
    
    service = UXGuardrailsService()
    
    # Registrar algunos errores
    for i in range(3):
        service.registrar_error_ux(
            ErrorUX(
                usuario=f"operador_{i}",
                accion_intentada="test_action",
                modulo="test",
                mensaje_error=f"Error test {i}"
            )
        )
    
    # Exportar
    filepath = "test_ux_logs.json"
    service.exportar_logs_ux(filepath)
    
    print(f"✓ Logs exportados a: {filepath}")
    
    # Validar que el archivo existe
    import os
    assert os.path.exists(filepath), "Archivo debe existir"
    
    # Leer y validar contenido
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    print(f"✓ Total errores en archivo: {datos['total_errores']}")
    print(f"✓ Timestamp exportación: {datos['timestamp_exportacion']}")
    
    assert datos['total_errores'] == 3, "Debe exportar 3 errores"
    assert len(datos['errores']) == 3, "Debe contener 3 errores"
    
    # Limpiar archivo test
    os.remove(filepath)
    
    print("\n✅ TEST 9 EXITOSO: Logs UX exportados correctamente")
    return True


def run_all_tests():
    """Ejecuta todos los tests de FASE 13"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  FASE 13: UX GUARDRAILS SERVICE - TEST SUITE COMPLETO".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    tests = [
        ("Análisis riesgo eliminación", test_analisis_riesgo_eliminacion),
        ("Análisis riesgo cierre período", test_analisis_riesgo_cierre_periodo),
        ("Modo novato - bloqueos", test_modo_novato_bloqueos),
        ("Tooltips progresivos", test_tooltips_progresivos),
        ("Registro errores UX", test_registro_errores_ux),
        ("Modificación masiva", test_modificacion_masiva_validacion),
        ("Override alertas", test_override_alerta_tracking),
        ("Eliminación masiva crítica", test_eliminacion_masiva_critica),
        ("Exportación logs UX", test_exportacion_logs_ux)
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
    print("█" + "  RESUMEN FINAL - FASE 13".center(68) + "█")
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
        print("\n🎉 ¡FASE 13 COMPLETADA EXITOSAMENTE! 🎉")
        print("\n✅ UX Guardrails Service operativo")
        print("✅ Modo novato protege correctamente")
        print("✅ Tooltips progresivos funcionan")
        print("✅ Errores UX se rastrean y analizan")
        print("✅ Listo para FASE 14: Gestión de Riesgos")
        return True
    else:
        print(f"\n⚠️ {total - exitosos} test(s) fallaron")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
