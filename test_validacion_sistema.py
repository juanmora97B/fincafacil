#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación completo del sistema FincaFácil
Ejecuta verificaciones sin problemas de encoding
"""

import sys
import os
import logging

# Configurar encoding UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ValidationTest')

def test_imports():
    """Test all critical imports"""
    logger.info("=" * 80)
    logger.info("VALIDACION 1: Imports Críticos")
    logger.info("=" * 80)
    
    tests = [
        ("database.database", "get_db_connection", "get_db_path_safe"),
        ("src.database.migraciones", "MIGRACIONES_SISTEMA"),
        ("src.services.bi_snapshot_service", "get_bi_snapshot_service"),
        ("src.services.analytics_cache_service", "get_analytics_cache"),
        ("src.core.permissions_manager", "PermissionEnum"),
        ("src.core.lifecycle_manager", "LifecycleManager"),
        ("src.services.kpi_calculator_service", "get_kpi_calculator"),
        ("src.services.alert_rules_service", "get_alert_rules_service"),
        ("src.services.cierre_mensual_service", "get_cierre_mensual_service"),
    ]
    
    passed = 0
    failed = 0
    
    for test_case in tests:
        module_name = test_case[0]
        items = test_case[1:]
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if not hasattr(module, item):
                    logger.error(f"FAIL: {module_name}.{item} no encontrado")
                    failed += 1
                else:
                    logger.info(f"OK: {module_name}.{item}")
                    passed += 1
        except Exception as e:
            logger.error(f"FAIL: {module_name} - {str(e)}")
            failed += 1
    
    logger.info(f"\nResultado Imports: {passed} OK, {failed} FAILED")
    return failed == 0

def test_database():
    """Test database connectivity and migrations"""
    logger.info("\n" + "=" * 80)
    logger.info("VALIDACION 2: Base de Datos y Migraciones")
    logger.info("=" * 80)
    
    try:
        from src.database.database import get_db_connection, get_db_path_safe
        from src.database.migraciones import MIGRACIONES_SISTEMA
        
        # Verificar path
        db_path = get_db_path_safe()
        logger.info(f"OK: Database path: {db_path}")
        
        # Verificar migraciones
        num_migrations = len(MIGRACIONES_SISTEMA)
        logger.info(f"OK: Total migraciones en sistema: {num_migrations}")
        for i in range(num_migrations):
            logger.info(f"  Migracion {i + 1}: SQL ejecutada")
        
        # Test connection
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                count = cursor.fetchone()[0]
                logger.info(f"OK: Database conectada - {count} usuarios registrados")
                return True
        except Exception as e:
            logger.error(f"FAIL: No se pudo conectar a BD: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"FAIL: {str(e)}")
        return False

def test_services():
    """Test key services initialization"""
    logger.info("\n" + "=" * 80)
    logger.info("VALIDACION 3: Servicios Críticos")
    logger.info("=" * 80)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test BI Snapshot Service
    try:
        from src.services.bi_snapshot_service import get_bi_snapshot_service
        service = get_bi_snapshot_service()
        logger.info("OK: BI Snapshot Service inicializado")
        tests_passed += 1
    except Exception as e:
        logger.error(f"FAIL: BI Snapshot Service - {str(e)}")
        tests_failed += 1
    
    # Test Analytics Cache Service
    try:
        from src.services.analytics_cache_service import get_analytics_cache
        service = get_analytics_cache()
        logger.info("OK: Analytics Cache Service inicializado")
        tests_passed += 1
    except Exception as e:
        logger.error(f"FAIL: Analytics Cache Service - {str(e)}")
        tests_failed += 1
    
    # Test KPI Calculator
    try:
        from src.services.kpi_calculator_service import get_kpi_calculator
        service = get_kpi_calculator()
        logger.info("OK: KPI Calculator Service inicializado")
        tests_passed += 1
    except Exception as e:
        logger.error(f"FAIL: KPI Calculator Service - {str(e)}")
        tests_failed += 1
    
    # Test Alert Rules Service
    try:
        from src.services.alert_rules_service import get_alert_rules_service
        service = get_alert_rules_service()
        logger.info("OK: Alert Rules Service inicializado")
        tests_passed += 1
    except Exception as e:
        logger.error(f"FAIL: Alert Rules Service - {str(e)}")
        tests_failed += 1
    
    # Test Permissions Manager
    try:
        from src.core.permissions_manager import get_permissions_manager, PermissionEnum
        manager = get_permissions_manager()
        logger.info(f"OK: Permissions Manager inicializado - {len(list(PermissionEnum))} permisos definidos")
        tests_passed += 1
    except Exception as e:
        logger.error(f"FAIL: Permissions Manager - {str(e)}")
        tests_failed += 1
    
    logger.info(f"\nResultado Servicios: {tests_passed} OK, {tests_failed} FAILED")
    return tests_failed == 0

def main():
    logger.info("\n" + "=" * 80)
    logger.info("VALIDACION INTEGRAL DEL SISTEMA FINCAFACIL")
    logger.info("=" * 80)
    
    results = []
    results.append(("Imports Críticos", test_imports()))
    results.append(("Base de Datos", test_database()))
    results.append(("Servicios Críticos", test_services()))
    
    logger.info("\n" + "=" * 80)
    logger.info("RESUMEN FINAL")
    logger.info("=" * 80)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\nESTADO: Todas las validaciones pasaron correctamente")
        return 0
    else:
        logger.error("\nESTADO: Algunas validaciones fallaron. Ver detalles arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
