#!/usr/bin/env python3
"""Test critical imports and services"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

print("[VALIDACION SISTEMA]")
print("=" * 60)

# Test 1: Imports
print("\n1. Probando imports...")
try:
    from src.database.database import get_db_connection
    print("  OK: src.database.database.get_db_connection")
except Exception as e:
    print(f"  FAIL: {e}")

try:
    from src.services.bi_snapshot_service import get_bi_snapshot_service
    print("  OK: bi_snapshot_service")
except Exception as e:
    print(f"  FAIL: {e}")

try:
    from src.services.analytics_cache_service import get_analytics_cache
    print("  OK: analytics_cache_service")
except Exception as e:
    print(f"  FAIL: {e}")

try:
    from src.services.kpi_calculator_service import get_kpi_calculator
    print("  OK: kpi_calculator_service")
except Exception as e:
    print(f"  FAIL: {e}")

try:
    from src.services.alert_rules_service import get_alert_rules_service
    print("  OK: alert_rules_service")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 2: Database
print("\n2. Probando database...")
try:
    from src.database.database import get_db_path_safe
    db_path = get_db_path_safe()
    print(f"  OK: Database path = {db_path}")
except Exception as e:
    print(f"  FAIL: {e}")

# Test 3: Migraciones
print("\n3. Probando migraciones...")
try:
    from src.database.migraciones import MIGRACIONES_SISTEMA
    total_migs = len(MIGRACIONES_SISTEMA)
    print(f"  OK: {total_migs} migraciones en sistema")
    for i in range(total_migs):
        print(f"     {i + 1}. SQL Migration")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n" + "=" * 60)
print("[FIN VALIDACION]")
