#!/usr/bin/env python3
"""
Script de validación rápida de imports y dependencias de FASE 1 BI
"""
import sys
import traceback

print("=" * 80)
print("VALIDACIÓN DE MÓDULOS - FASE 1: DATA FOUNDATION")
print("=" * 80)
print()

tests = [
    ("Servicios BI: bi_snapshot_service", lambda: __import__('src.services.bi_snapshot_service', fromlist=['get_bi_snapshot_service'])),
    ("Servicios BI: analytics_cache_service", lambda: __import__('src.services.analytics_cache_service', fromlist=['get_analytics_cache'])),
    ("Servicios BI: cierre_mensual_service", lambda: __import__('src.services.cierre_mensual_service', fromlist=['CierreMensualService'])),
    ("Base de datos: migraciones", lambda: __import__('src.database.migraciones', fromlist=['ejecutar_migraciones'])),
]

passed = 0
failed = 0

for test_name, test_func in tests:
    try:
        test_func()
        print(f"✅ {test_name}")
        passed += 1
    except Exception as e:
        print(f"❌ {test_name}")
        print(f"   Error: {str(e)[:100]}")
        failed += 1

print()
print("=" * 80)
print(f"RESUMEN: {passed} pasado, {failed} fallido")
print("=" * 80)

sys.exit(0 if failed == 0 else 1)
