"""
Tests para FASE 16: Value Metrics Service
Valida cuantificación del valor económico del sistema
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import unittest
from datetime import datetime
from src.services.value_metrics_service import (
    ValueMetricsService,
    ItemValor,
    TipoValor,
    CategoriaImpacto,
    get_value_metrics_service
)


class TestFase16ValueMetrics(unittest.TestCase):
    """Tests del servicio de métricas de valor"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración una vez para todos los tests"""
        cls.service = get_value_metrics_service()
    
    def test_01_valor_data_quality(self):
        """Test: Cálculo de valor de FASE 8 (Data Quality)"""
        print("\n" + "="*80)
        print("TEST 1: Valor Data Quality")
        print("="*80)
        
        valor = self.service.calcular_valor_data_quality(
            registros_corregidos=250,
            tiempo_ahorrado_horas=15.5,
            decisiones_mejoradas=8
        )
        
        # Verificar que genera valor positivo
        self.assertGreater(valor, 0)
        
        # Verificar componentes
        # Tiempo: 15.5h * $15k/h = $232,500
        # Decisiones: 8 * $50k = $400,000
        # Prevención: 2 incidentes * $200k = $400,000
        # Total esperado: ~$1M
        self.assertGreater(valor, 900000)
        self.assertLess(valor, 1200000)
        
        # Verificar que se registró
        self.assertGreater(len(self.service.items_valor), 0)
        ultimo_item = self.service.items_valor[-1]
        self.assertEqual(ultimo_item.categoria, CategoriaImpacto.DATA_QUALITY)
        self.assertTrue(ultimo_item.recurrente)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 250 registros corregidos")
        print(f"  - 15.5 horas ahorradas")
        print(f"  - 8 decisiones mejoradas")
        print(f"✓ Item registrado como recurrente")
    
    def test_02_valor_observability(self):
        """Test: Cálculo de valor de FASE 9 (Observability)"""
        print("\n" + "="*80)
        print("TEST 2: Valor Observability")
        print("="*80)
        
        valor = self.service.calcular_valor_observability(
            incidentes_detectados_temprano=5,
            tiempo_resolucion_reducido_horas=12.0
        )
        
        self.assertGreater(valor, 0)
        
        # Detección temprana: 5 * ($500k - $50k) = $2.25M
        # Tiempo ahorrado: 12h * $15k/h = $180k
        # Total: ~$2.43M
        self.assertGreater(valor, 2000000)
        
        ultimo_item = self.service.items_valor[-1]
        self.assertEqual(ultimo_item.categoria, CategoriaImpacto.OBSERVABILITY)
        self.assertEqual(ultimo_item.tipo_valor, TipoValor.COSTO_EVITADO)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 5 incidentes detectados temprano")
        print(f"  - 12h de tiempo de diagnóstico reducido")
    
    def test_03_valor_explainability(self):
        """Test: Cálculo de valor de FASE 10 (Explainability)"""
        print("\n" + "="*80)
        print("TEST 3: Valor Explainability")
        print("="*80)
        
        valor = self.service.calcular_valor_explainability(
            decisiones_explicadas=45,
            confianza_mejorada=0.25  # 25% mejora
        )
        
        self.assertGreater(valor, 0)
        
        # Adopción: 0.25 * 0.5 * $1M = $125k
        # Overrides: 45 * 0.1 * $30k = $135k
        # Total: ~$260k
        self.assertGreater(valor, 200000)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 45 decisiones explicadas")
        print(f"  - +25% mejora en confianza")
    
    def test_04_valor_simulation(self):
        """Test: Cálculo de valor de FASE 11 (Simulation)"""
        print("\n" + "="*80)
        print("TEST 4: Valor Simulation")
        print("="*80)
        
        valor = self.service.calcular_valor_simulation(
            escenarios_simulados=12,
            decisiones_optimizadas=6,
            roi_promedio_mejora=0.18  # 18% mejora ROI
        )
        
        self.assertGreater(valor, 0)
        
        # Optimización: 6 * $100k = $600k
        # ROI mejorado: $5M * 0.18 = $900k
        # Total: $1.5M
        self.assertGreater(valor, 1400000)
        
        ultimo_item = self.service.items_valor[-1]
        self.assertEqual(ultimo_item.categoria, CategoriaImpacto.SIMULATION)
        self.assertFalse(ultimo_item.recurrente)  # Simulaciones son one-time
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 12 escenarios simulados")
        print(f"  - 6 decisiones optimizadas")
        print(f"  - +18% mejora ROI")
    
    def test_05_valor_ux_guardrails(self):
        """Test: Cálculo de valor de FASE 13 (UX Guardrails)"""
        print("\n" + "="*80)
        print("TEST 5: Valor UX Guardrails")
        print("="*80)
        
        valor = self.service.calcular_valor_ux_guardrails(
            errores_prevenidos=85,
            tiempo_capacitacion_reducido_horas=20.0
        )
        
        self.assertGreater(valor, 0)
        
        # Errores: 85 * 0.5h * $15k = $637.5k
        # Capacitación: 20h * $15k = $300k
        # Adopción: $200k
        # Total: ~$1.14M
        self.assertGreater(valor, 1000000)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 85 errores de usuario prevenidos")
        print(f"  - 20h de capacitación reducida")
    
    def test_06_valor_risk_management(self):
        """Test: Cálculo de valor de FASE 14 (Risk Management)"""
        print("\n" + "="*80)
        print("TEST 6: Valor Risk Management")
        print("="*80)
        
        valor = self.service.calcular_valor_risk_management(
            usuarios_alto_riesgo_identificados=4,
            incidentes_prevenidos=7,
            patrones_detectados=12
        )
        
        self.assertGreater(valor, 0)
        
        # Incidentes: 7 * $200k = $1.4M
        # Usuarios: 4 * $150k = $600k
        # Patrones: 12 * $50k = $600k
        # Total: $2.6M
        self.assertGreater(valor, 2500000)
        
        ultimo_item = self.service.items_valor[-1]
        self.assertEqual(ultimo_item.tipo_valor, TipoValor.REDUCCION_RIESGO)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 4 usuarios alto riesgo identificados")
        print(f"  - 7 incidentes prevenidos")
        print(f"  - 12 patrones detectados")
    
    def test_07_valor_incident_management(self):
        """Test: Cálculo de valor de FASE 15 (Incident Management)"""
        print("\n" + "="*80)
        print("TEST 7: Valor Incident Management")
        print("="*80)
        
        valor = self.service.calcular_valor_incident_management(
            incidentes_resueltos_sin_soporte=15,
            tiempo_resolucion_promedio_min=45.0,
            kb_consultas=32
        )
        
        self.assertGreater(valor, 0)
        
        # Soporte: 15 * $100k = $1.5M
        # Tiempo: 15 * 3.25h * $15k = $731k
        # KB: 32 * $5k = $160k
        # Total: ~$2.4M
        self.assertGreater(valor, 2000000)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 15 incidentes resueltos sin soporte externo")
        print(f"  - 45 min tiempo promedio de resolución")
        print(f"  - 32 consultas a Knowledge Base")
    
    def test_08_valor_bi_analytics(self):
        """Test: Cálculo de valor de FASE 37 (BI & Analytics)"""
        print("\n" + "="*80)
        print("TEST 8: Valor BI & Analytics")
        print("="*80)
        
        valor = self.service.calcular_valor_bi_analytics(
            insights_generados=18,
            decisiones_data_driven=22,
            mejora_eficiencia_operativa=0.12  # 12% mejora
        )
        
        self.assertGreater(valor, 0)
        
        # Insights: 18 * $80k = $1.44M
        # Decisiones: 22 * $120k = $2.64M
        # Eficiencia: $10M * 0.12 = $1.2M
        # Total: ~$5.28M
        self.assertGreater(valor, 5000000)
        
        print(f"✓ Valor calculado: ${valor:,.0f} COP")
        print(f"  - 18 insights generados")
        print(f"  - 22 decisiones data-driven")
        print(f"  - +12% mejora eficiencia operativa")
    
    def test_09_calculo_roi(self):
        """Test: Cálculo de ROI completo"""
        print("\n" + "="*80)
        print("TEST 9: Cálculo de ROI")
        print("="*80)
        
        inversion_inicial = 50000000  # $50M COP
        
        roi = self.service.calcular_roi(
            inversion_inicial=inversion_inicial,
            meses_proyectados=12
        )
        
        # Verificar componentes
        self.assertEqual(roi.inversion_inicial, inversion_inicial)
        self.assertGreater(roi.beneficio_total, 0)
        self.assertIsNotNone(roi.roi_porcentaje)
        self.assertGreater(roi.payback_meses, 0)
        self.assertIsNotNone(roi.vnp)
        
        # Con los valores calculados, ROI debe ser >100%
        self.assertGreater(roi.roi_porcentaje, 100)
        
        # Payback debe ser <12 meses
        self.assertLess(roi.payback_meses, 12)
        
        # VNP debe ser positivo
        self.assertGreater(roi.vnp, 0)
        
        print(f"✓ Inversión inicial: ${roi.inversion_inicial:,.0f}")
        print(f"✓ Beneficio total (12 meses): ${roi.beneficio_total:,.0f}")
        print(f"✓ Beneficio neto: ${roi.beneficio_total - roi.inversion_inicial:,.0f}")
        print(f"✓ ROI: {roi.roi_porcentaje:.1f}%")
        print(f"✓ Payback: {roi.payback_meses:.1f} meses")
        print(f"✓ VNP: ${roi.vnp:,.0f}")
    
    def test_10_top_impactos(self):
        """Test: Obtención de top 5 impactos"""
        print("\n" + "="*80)
        print("TEST 10: Top 5 Impactos")
        print("="*80)
        
        top_5 = self.service.obtener_top_impactos(5)
        
        self.assertEqual(len(top_5), 5)
        
        # Verificar orden descendente por monto
        for i in range(len(top_5) - 1):
            self.assertGreaterEqual(top_5[i].monto_cop, top_5[i+1].monto_cop)
        
        print(f"✓ Top 5 impactos por valor:")
        for i, item in enumerate(top_5, 1):
            print(f"  {i}. {item.categoria.value}: ${item.monto_cop:,.0f}")
            print(f"     {item.descripcion}")
    
    def test_11_distribucion_por_categoria(self):
        """Test: Distribución de valor por categoría"""
        print("\n" + "="*80)
        print("TEST 11: Distribución por Categoría")
        print("="*80)
        
        distribucion = self.service.obtener_distribucion_por_categoria()
        
        # Debe haber al menos 6 categorías (FASES 8-15)
        self.assertGreaterEqual(len(distribucion), 6)
        
        # Todas deben tener valor >0
        for categoria, valor in distribucion.items():
            self.assertGreater(valor, 0)
        
        # Suma de todas las categorías = suma de todos los items
        total_distribucion = sum(distribucion.values())
        total_items = sum(item.monto_cop for item in self.service.items_valor)
        self.assertAlmostEqual(total_distribucion, total_items, places=0)
        
        print(f"✓ Distribución de valor por categoría:")
        for categoria, valor in sorted(distribucion.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (valor / total_distribucion) * 100
            print(f"  {categoria}: ${valor:,.0f} ({porcentaje:.1f}%)")
    
    def test_12_reporte_ejecutivo(self):
        """Test: Generación de reporte ejecutivo completo"""
        print("\n" + "="*80)
        print("TEST 12: Reporte Ejecutivo")
        print("="*80)
        
        inversion_inicial = 50000000  # $50M
        
        reporte = self.service.generar_reporte_ejecutivo(
            inversion_inicial=inversion_inicial,
            periodo_meses=6
        )
        
        # Verificar componentes
        self.assertIsNotNone(reporte.periodo_inicio)
        self.assertIsNotNone(reporte.periodo_fin)
        self.assertGreater(reporte.valor_total_generado, 0)
        self.assertIsNotNone(reporte.roi)
        self.assertEqual(len(reporte.top_5_impactos), 5)
        self.assertGreater(len(reporte.distribucion_por_categoria), 0)
        self.assertGreater(len(reporte.recomendaciones), 0)
        
        # ROI debe ser positivo\r\n        self.assertGreater(reporte.roi.roi_porcentaje, 0)
        
        print(f"✓ Período: {reporte.periodo_inicio.date()} a {reporte.periodo_fin.date()}")
        print(f"✓ Valor total generado: ${reporte.valor_total_generado:,.0f}")
        print(f"\n✓ ROI:")
        print(f"  - Inversión: ${reporte.roi.inversion_inicial:,.0f}")
        print(f"  - Beneficio: ${reporte.roi.beneficio_total:,.0f}")
        print(f"  - ROI: {reporte.roi.roi_porcentaje:.1f}%")
        print(f"  - Payback: {reporte.roi.payback_meses:.1f} meses")
        
        print(f"\n✓ Recomendaciones ({len(reporte.recomendaciones)}):")
        for i, rec in enumerate(reporte.recomendaciones, 1):
            print(f"  {i}. {rec}")
    
    def test_13_exportacion_json(self):
        """Test: Exportación de reporte a JSON"""
        print("\n" + "="*80)
        print("TEST 13: Exportación JSON")
        print("="*80)
        
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        inversion_inicial = 50000000
        
        # Exportar
        self.service.exportar_reporte_json(filepath, inversion_inicial)
        
        # Verificar archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        self.assertIn("periodo", datos)
        self.assertIn("valor_total_generado", datos)
        self.assertIn("roi", datos)
        self.assertIn("top_5_impactos", datos)
        self.assertIn("distribucion_por_categoria", datos)
        self.assertIn("recomendaciones", datos)
        
        # Verificar ROI
        self.assertIn("roi_porcentaje", datos["roi"])
        self.assertIn("payback_meses", datos["roi"])
        self.assertIn("vnp", datos["roi"])
        
        print(f"✓ Archivo exportado: {filepath}")
        print(f"✓ Valor total: ${datos['valor_total_generado']:,.0f}")
        print(f"✓ ROI: {datos['roi']['roi_porcentaje']:.1f}%")
        print(f"✓ Top impactos: {len(datos['top_5_impactos'])}")
        print(f"✓ Categorías: {len(datos['distribucion_por_categoria'])}")
        
        # Cleanup
        import os
        os.unlink(filepath)
    
    def test_14_singleton_service(self):
        """Test: Servicio es singleton global"""
        print("\n" + "="*80)
        print("TEST 14: Singleton Service")
        print("="*80)
        
        service1 = get_value_metrics_service()
        service2 = get_value_metrics_service()
        
        self.assertIs(service1, service2)
        
        # Verificar que comparten items
        items_antes = len(service1.items_valor)
        
        service2.registrar_valor(ItemValor(
            descripcion="Test singleton",
            tipo_valor=TipoValor.AHORRO_DIRECTO,
            categoria=CategoriaImpacto.DATA_QUALITY,
            monto_cop=100000
        ))
        
        self.assertEqual(len(service1.items_valor), items_antes + 1)
        
        print(f"✓ Singleton verificado: service1 is service2 = {service1 is service2}")
        print(f"✓ Items compartidos: {len(service1.items_valor)}")


def run_tests():
    """Ejecuta todos los tests con formato visual"""
    print("\n" + "="*80)
    print(" FASE 16: VALUE METRICS SERVICE - SUITE DE TESTS".center(80))
    print("="*80)
    print("\nPropósito: Validar cuantificación del valor económico del sistema")
    print("Alcance: 14 tests cubriendo todas las FASES 8-15, ROI y reporting")
    print("="*80)
    
    # Configurar test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFase16ValueMetrics)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "="*80)
    print(" RESUMEN DE EJECUCIÓN".center(80))
    print("="*80)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Tests exitosos:   {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests fallidos:   {len(result.failures)}")
    print(f"Errores:          {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n" + "🎉 ¡TODOS LOS TESTS PASARON! 🎉".center(80))
        print("="*80)
        print("\nFASE 16 COMPLETADA:")
        print("✓ Valor económico cuantificado para FASES 8-15")
        print("✓ ROI calculado con VNP y payback")
        print("✓ Reporte ejecutivo generado")
        print("✓ Exportación JSON funcional")
        print("✓ Sistema demuestra valor comercial claro")
        print("="*80)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON ❌".center(80))
        print("="*80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

