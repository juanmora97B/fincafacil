"""
Tests para FASE 15: Incident Management Service
Valida gestión de incidentes y continuidad operativa
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import unittest
from datetime import datetime, timedelta
from src.services.incident_management_service import (
    IncidentManagementService,
    Incidente,
    TipoIncidente,
    SeveridadIncidente,
    EstadoIncidente,
    SolucionKnowledgeBase,
    ChecklistOperativo,
    get_incident_management_service
)
from typing import cast


class TestFase15IncidentManagement(unittest.TestCase):
    """Tests del servicio de gestión de incidentes"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración una vez para todos los tests"""
        # Usar singleton para mantener estado entre tests
        cls.service = get_incident_management_service()
    
    def setUp(self):
        """Configuración antes de cada test"""
        # Limpiar estado para tests independientes donde sea necesario
        # (pero mantener singleton para tests que validan acumulación)
        pass
    
    def test_01_registro_incidente(self):
        """Test: Registro de incidente con ID automático"""
        print("\n" + "="*80)
        print("TEST 1: Registro de Incidente")
        print("="*80)
        
        incidente = Incidente(
            titulo="Base de datos bloqueada",
            descripcion="Error al intentar guardar registro de producción",
            tipo=TipoIncidente.ERROR,
            severidad=SeveridadIncidente.ALTA,
            modulo_afectado="produccion",
            usuario_reporta="operador_1"
        )
        
        id_incidente = self.service.registrar_incidente(incidente)
        
        # Verificar ID generado
        self.assertIsNotNone(id_incidente)
        self.assertTrue(id_incidente.startswith("INC-"))
        
        # Verificar que está en el sistema
        self.assertIn(id_incidente, self.service.incidentes)
        
        # Verificar estado inicial
        inc_registrado = self.service.incidentes[id_incidente]
        self.assertEqual(inc_registrado.estado, EstadoIncidente.ABIERTO)
        
        print(f"✓ Incidente registrado: {id_incidente}")
        print(f"✓ Título: {inc_registrado.titulo}")
        print(f"✓ Severidad: {inc_registrado.severidad.value}")
        print(f"✓ Estado: {inc_registrado.estado.value}")
    
    def test_02_actualizacion_estados(self):
        """Test: Timeline de estados del incidente"""
        print("\n" + "="*80)
        print("TEST 2: Timeline de Estados")
        print("="*80)
        
        incidente = Incidente(
            titulo="Performance degradado",
            descripcion="Dashboard carga muy lento",
            tipo=TipoIncidente.PERFORMANCE,
            severidad=SeveridadIncidente.MEDIA,
            modulo_afectado="dashboard"
        )
        
        id_inc = self.service.registrar_incidente(incidente)
        
        # Transiciones de estado
        self.service.actualizar_estado(id_inc, EstadoIncidente.EN_INVESTIGACION, "Analizando logs")
        self.service.actualizar_estado(id_inc, EstadoIncidente.EN_RESOLUCION, "Optimizando consultas")
        self.service.actualizar_estado(id_inc, EstadoIncidente.RESUELTO, "Problema resuelto")
        
        inc = self.service.incidentes[id_inc]
        
        # Verificar historial
        self.assertIn("historial_estados", inc.datos_contexto)
        historial = inc.datos_contexto["historial_estados"]
        self.assertEqual(len(historial), 3)
        
        # Verificar tiempo de resolución
        self.assertIsNotNone(inc.tiempo_resolucion_min)
        self.assertGreaterEqual(cast(int, inc.tiempo_resolucion_min), 0)
        
        print(f"✓ Estados recorridos: {len(historial)}")
        print(f"✓ Estado final: {inc.estado.value}")
        print(f"✓ Tiempo resolución: {inc.tiempo_resolucion_min} min")
        
        for i, cambio in enumerate(historial, 1):
            print(f"  {i}. {cambio['estado_anterior']} → {cambio['estado_nuevo']}: {cambio['notas']}")
    
    def test_03_knowledge_base_busqueda(self):
        """Test: Búsqueda en knowledge base"""
        print("\n" + "="*80)
        print("TEST 3: Knowledge Base - Búsqueda")
        print("="*80)
        
        # Buscar solución para problema de base de datos
        # Usar término más genérico que aparece en síntomas
        soluciones = self.service.buscar_solucion("database")
        
        self.assertGreater(len(soluciones), 0)
        
        solucion = soluciones[0]
        self.assertIsNotNone(solucion.problema)
        self.assertGreater(len(solucion.pasos), 0)
        self.assertIsNotNone(solucion.solucion)
        
        print(f"✓ Soluciones encontradas: {len(soluciones)}")
        print(f"\nSolución #1:")
        print(f"  Problema: {solucion.problema}")
        print(f"  Causa: {solucion.causa}")
        print(f"  Solución: {solucion.solucion}")
        print(f"  Pasos:")
        for paso in solucion.pasos:
            print(f"    {paso}")
        
        if solucion.prevencion:
            print(f"  Prevención: {solucion.prevencion}")
    
    def test_04_resolucion_incidente_completa(self):
        """Test: Resolución completa con documentación"""
        print("\n" + "="*80)
        print("TEST 4: Resolución Completa con Documentación")
        print("="*80)
        
        incidente = Incidente(
            titulo="Error en cálculo de promedio",
            descripcion="Producción promedio muestra valor incorrecto",
            tipo=TipoIncidente.DATA,
            severidad=SeveridadIncidente.ALTA,
            modulo_afectado="produccion"
        )
        
        id_inc = self.service.registrar_incidente(incidente)
        
        # Resolver con documentación completa
        exito = self.service.resolver_incidente(
            id_inc,
            solucion="Corrección de fórmula de promedio ponderado",
            pasos_resolucion=[
                "1. Identificar animales con registros faltantes",
                "2. Corregir fórmula en código",
                "3. Recalcular promedios históricos",
                "4. Validar con casos conocidos"
            ],
            causa_raiz="División por cero cuando no hay registros",
            se_puede_prevenir=True
        )
        
        self.assertTrue(exito)
        
        inc = self.service.incidentes[id_inc]
        self.assertEqual(inc.estado, EstadoIncidente.RESUELTO)
        self.assertIsNotNone(inc.solucion_aplicada)
        self.assertEqual(len(inc.pasos_resolucion), 4)
        self.assertTrue(inc.se_puede_prevenir)
        self.assertIsNotNone(inc.causa_raiz)
        
        print(f"✓ Incidente resuelto: {id_inc}")
        print(f"✓ Causa raíz: {inc.causa_raiz}")
        print(f"✓ Solución: {inc.solucion_aplicada}")
        print(f"✓ Prevenible: {inc.se_puede_prevenir}")
        print(f"\nPasos de resolución:")
        for paso in inc.pasos_resolucion:
            print(f"  {paso}")
    
    def test_05_incidentes_activos_priorizados(self):
        """Test: Lista de incidentes activos ordenados por prioridad"""
        print("\n" + "="*80)
        print("TEST 5: Incidentes Activos Priorizados")
        print("="*80)
        
        # Contar incidentes existentes al inicio
        incidentes_iniciales = len(self.service.obtener_incidentes_activos())
        
        # Crear varios incidentes de diferente severidad
        incidentes = [
            Incidente("Bug menor test5", "Typo en label", TipoIncidente.UX, SeveridadIncidente.BAJA, "ui"),
            Incidente("Sistema caído test5", "Base de datos corrupta", TipoIncidente.ERROR, SeveridadIncidente.CRITICA, "core"),
            Incidente("Lentitud test5", "Dashboard lento", TipoIncidente.PERFORMANCE, SeveridadIncidente.MEDIA, "dashboard"),
            Incidente("Datos incorrectos test5", "Reporte con error", TipoIncidente.DATA, SeveridadIncidente.ALTA, "reportes")
        ]
        
        for inc in incidentes:
            self.service.registrar_incidente(inc)
        
        # Cerrar uno para que no aparezca en activos
        self.service.actualizar_estado(incidentes[0].id_incidente, EstadoIncidente.CERRADO)
        
        activos = self.service.obtener_incidentes_activos()
        
        # Verificar que hay al menos los 3 nuevos activos (más los que había)
        self.assertGreaterEqual(len(activos), 3)
        
        # Encontrar los 3 incidentes nuevos que no fueron cerrados
        nuevos_activos = [a for a in activos if a.id_incidente in [inc.id_incidente for inc in incidentes[1:]]]
        self.assertEqual(len(nuevos_activos), 3)
        
        # Verificar orden por severidad (crítica primero)
        self.assertEqual(nuevos_activos[0].severidad, SeveridadIncidente.CRITICA)
        self.assertEqual(nuevos_activos[1].severidad, SeveridadIncidente.ALTA)
        self.assertEqual(nuevos_activos[2].severidad, SeveridadIncidente.MEDIA)
        
        print(f"✓ Incidentes activos totales: {len(activos)}")
        print(f"✓ Incidentes nuevos: {len(nuevos_activos)}")
        print(f"\nOrden de prioridad (nuevos incidentes):")
        for i, inc in enumerate(nuevos_activos, 1):
            print(f"  {i}. [{inc.severidad.value.upper()}] {inc.titulo} ({inc.modulo_afectado})")
    
    def test_06_estadisticas_incidentes(self):
        """Test: Estadísticas de incidentes por período"""
        print("\n" + "="*80)
        print("TEST 6: Estadísticas de Incidentes")
        print("="*80)
        
        # Contar incidentes existentes
        stats_inicial = self.service.obtener_estadisticas_incidentes(dias=30)
        incidentes_iniciales = stats_inicial["total_incidentes"]
        
        # Crear múltiples incidentes
        tipos_incidentes = [
            (TipoIncidente.ERROR, SeveridadIncidente.ALTA),
            (TipoIncidente.PERFORMANCE, SeveridadIncidente.MEDIA),
            (TipoIncidente.DATA, SeveridadIncidente.CRITICA),
            (TipoIncidente.UX, SeveridadIncidente.BAJA),
            (TipoIncidente.ERROR, SeveridadIncidente.MEDIA)
        ]
        
        ids_nuevos = []
        for i, (tipo, severidad) in enumerate(tipos_incidentes):
            inc = Incidente(
                titulo=f"Incidente test6-{i+1}",
                descripcion=f"Descripción {i+1}",
                tipo=tipo,
                severidad=severidad,
                modulo_afectado="test"
            )
            id_inc = self.service.registrar_incidente(inc)
            ids_nuevos.append(id_inc)
            
            # Resolver algunos
            if i < 3:
                self.service.resolver_incidente(
                    id_inc,
                    solucion="Solución aplicada",
                    pasos_resolucion=["Paso 1", "Paso 2"],
                    se_puede_prevenir=(i % 2 == 0)
                )
        
        stats = self.service.obtener_estadisticas_incidentes(dias=30)
        
        # Verificar que hay al menos los 5 nuevos incidentes
        self.assertGreaterEqual(stats["total_incidentes"], 5)
        self.assertEqual(stats["total_incidentes"], incidentes_iniciales + 5)
        
        # Verificar que hay datos estadísticos
        self.assertIn("por_tipo", stats)
        self.assertIn("por_severidad", stats)
        self.assertIn("por_estado", stats)
        self.assertGreaterEqual(stats["tiempo_resolucion_promedio_min"], 0)
        self.assertGreaterEqual(stats["incidentes_prevenibles"], 2)  # i=0 e i=2
        
        print(f"✓ Total incidentes (30 días): {stats['total_incidentes']}")
        print(f"✓ Incidentes nuevos: 5")
        print(f"✓ Tiempo resolución promedio: {stats['tiempo_resolucion_promedio_min']} min")
        print(f"✓ Incidentes prevenibles: {stats['incidentes_prevenibles']} ({stats['porcentaje_prevenibles']}%)")
        
        print(f"\nDistribución por tipo:")
        for tipo, cant in stats["por_tipo"].items():
            print(f"  {tipo}: {cant}")
        
        print(f"\nDistribución por severidad:")
        for sev, cant in stats["por_severidad"].items():
            print(f"  {sev}: {cant}")
    
    def test_07_checklist_operativo(self):
        """Test: Checklist operativo semanal/mensual"""
        print("\n" + "="*80)
        print("TEST 7: Checklist Operativo")
        print("="*80)
        
        # Obtener checklist semanal
        checklist = self.service.obtener_checklist("semanal")
        
        self.assertIsNotNone(checklist)
        checklist = cast(ChecklistOperativo, checklist)
        self.assertEqual(checklist.frecuencia, "semanal")
        self.assertGreater(len(checklist.items), 0)
        
        print(f"✓ Checklist: {checklist.nombre}")
        print(f"✓ Frecuencia: {checklist.frecuencia}")
        print(f"✓ Items totales: {len(checklist.items)}")
        
        # Completar algunos items
        self.service.completar_item_checklist("semanal", 0, True)
        self.service.completar_item_checklist("semanal", 1, True)
        
        checklist_actualizado = self.service.obtener_checklist("semanal")
        checklist_actualizado = cast(ChecklistOperativo, checklist_actualizado)
        self.assertTrue(checklist_actualizado.items[0]["completado"])
        self.assertTrue(checklist_actualizado.items[1]["completado"])
        self.assertFalse(checklist_actualizado.items[2]["completado"])
        
        print(f"\nItems completados:")
        for i, item in enumerate(checklist_actualizado.items):
            status = "✓" if item["completado"] else "○"
            print(f"  {status} {item['tarea']}")
    
    def test_08_asociacion_snapshots_metricas(self):
        """Test: Asociación con snapshots y métricas de FASES anteriores"""
        print("\n" + "="*80)
        print("TEST 8: Asociación con Snapshots y Métricas")
        print("="*80)
        
        incidente = Incidente(
            titulo="Calidad de datos degradada",
            descripcion="Score de calidad bajó de 8.5 a 6.2",
            tipo=TipoIncidente.DATA,
            severidad=SeveridadIncidente.ALTA,
            modulo_afectado="produccion",
            snapshot_id="SNAP-20240115-083045",  # De FASE 8
            metrica_relacionada="data_quality_score"  # De FASE 9
        )
        
        # Agregar contexto técnico
        incidente.datos_contexto = {
            "score_anterior": 8.5,
            "score_actual": 6.2,
            "registros_afectados": 45,
            "periodo_analizado": "2024-01-01 a 2024-01-15",
            "fase_origen": "FASE 8 - Data Quality"
        }
        
        id_inc = self.service.registrar_incidente(incidente)
        
        inc = self.service.incidentes[id_inc]
        self.assertIsNotNone(inc.snapshot_id)
        self.assertIsNotNone(inc.metrica_relacionada)
        self.assertIn("score_anterior", inc.datos_contexto)
        
        print(f"✓ Incidente asociado: {id_inc}")
        print(f"✓ Snapshot ID: {inc.snapshot_id}")
        print(f"✓ Métrica: {inc.metrica_relacionada}")
        print(f"\nContexto técnico:")
        for clave, valor in inc.datos_contexto.items():
            print(f"  {clave}: {valor}")
    
    def test_09_agregar_solucion_kb(self):
        """Test: Agregar nueva solución a knowledge base"""
        print("\n" + "="*80)
        print("TEST 9: Agregar Solución a Knowledge Base")
        print("="*80)
        
        kb_inicial = len(self.service.knowledge_base)
        
        nueva_solucion = SolucionKnowledgeBase(
            problema="Reporte PDF no se genera",
            sintomas=["Error al exportar", "Archivo vacío", "Timeout"],
            causa="Falta librería reportlab o datos muy grandes",
            solucion="Instalar reportlab y paginar datos",
            pasos=[
                "1. Verificar que reportlab esté instalado: pip list | grep reportlab",
                "2. Si falta: pip install reportlab",
                "3. Si persiste: Reducir rango de fechas del reporte",
                "4. Considerar generación en background para reportes grandes"
            ],
            prevencion="Validar dependencias en instalación",
            tags=["reportes", "pdf", "exportacion"]
        )
        
        self.service.agregar_solucion_kb(nueva_solucion)
        
        kb_final = len(self.service.knowledge_base)
        self.assertEqual(kb_final, kb_inicial + 1)
        
        # Verificar que se puede buscar
        soluciones = self.service.buscar_solucion("pdf")
        encontrada = any(s.problema == nueva_solucion.problema for s in soluciones)
        self.assertTrue(encontrada)
        
        print(f"✓ Soluciones en KB: {kb_inicial} → {kb_final}")
        print(f"✓ Nueva solución: {nueva_solucion.problema}")
        print(f"✓ Búsqueda funcional: {'pdf' in [s.problema for s in soluciones]}")
    
    def test_10_exportacion_incidentes(self):
        """Test: Exportación de datos de incidentes"""
        print("\n" + "="*80)
        print("TEST 10: Exportación de Datos")
        print("="*80)
        
        # Crear algunos incidentes
        for i in range(3):
            inc = Incidente(
                titulo=f"Test incidente {i+1}",
                descripcion=f"Descripción {i+1}",
                tipo=TipoIncidente.ERROR,
                severidad=SeveridadIncidente.MEDIA,
                modulo_afectado="test"
            )
            self.service.registrar_incidente(inc)
        
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        # Exportar
        self.service.exportar_datos(filepath)
        
        # Verificar archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        self.assertIn("timestamp_exportacion", datos)
        self.assertIn("incidentes", datos)
        self.assertIn("knowledge_base", datos)
        self.assertIn("checklists", datos)
        self.assertGreater(datos["total_incidentes"], 0)
        
        print(f"✓ Archivo exportado: {filepath}")
        print(f"✓ Total incidentes: {datos['total_incidentes']}")
        print(f"✓ Soluciones en KB: {len(datos['knowledge_base'])}")
        print(f"✓ Checklists: {len(datos['checklists'])}")
        
        # Cleanup
        import os
        os.unlink(filepath)
    
    def test_11_singleton_service(self):
        """Test: Servicio es singleton global"""
        print("\n" + "="*80)
        print("TEST 11: Singleton Service")
        print("="*80)
        
        service1 = get_incident_management_service()
        service2 = get_incident_management_service()
        
        self.assertIs(service1, service2)
        
        # Agregar incidente en service1
        inc = Incidente(
            titulo="Test singleton",
            descripcion="Verificar instancia única",
            tipo=TipoIncidente.ERROR,
            severidad=SeveridadIncidente.BAJA,
            modulo_afectado="test"
        )
        id_inc = service1.registrar_incidente(inc)
        
        # Verificar que está disponible en service2
        self.assertIn(id_inc, service2.incidentes)
        
        print(f"✓ Singleton verificado: service1 is service2 = {service1 is service2}")
        print(f"✓ Instancia compartida funcional")


def run_tests():
    """Ejecuta todos los tests con formato visual"""
    print("\n" + "="*80)
    print(" FASE 15: INCIDENT MANAGEMENT SERVICE - SUITE DE TESTS".center(80))
    print("="*80)
    print("\nPropósito: Validar gestión de incidentes y continuidad operativa")
    print("Alcance: 11 tests cubriendo registro, resolución, KB y checklists")
    print("="*80)
    
    # Configurar test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFase15IncidentManagement)
    
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
        print("\nFASE 15 COMPLETADA:")
        print("✓ Gestión de incidentes operativa")
        print("✓ Knowledge base con soluciones comunes")
        print("✓ Checklists operativos implementados")
        print("✓ Timeline de resolución funcional")
        print("✓ Integración con FASES 8-14")
        print("="*80)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON ❌".center(80))
        print("="*80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
