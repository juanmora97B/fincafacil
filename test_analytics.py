#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'src')

from src.analytics.analytics_service import calcular_kpis_financieros, calcular_kpis_productivos
from src.analytics.insights_service import generar_insights

print('=== KPIs Financieros ===')
fk = calcular_kpis_financieros('mes_actual')
print(f'Ingresos totales: ${fk.ingresos_totales:,.2f}')
print(f'Costos totales: ${fk.costos_totales:,.2f}')
print(f'Margen bruto: ${fk.margen_bruto:,.2f}')
print(f'Rentabilidad: {fk.rentabilidad_mensual:.2f}%' if fk.rentabilidad_mensual else 'N/A')

print()
print('=== KPIs Productivos ===')
pk = calcular_kpis_productivos('mes_actual')
print(f'Producción diaria: {pk.produccion_diaria:.2f} L')
print(f'Producción mensual: {pk.produccion_mensual:.2f} L')
print(f'Promedio por animal: {pk.produccion_promedio_por_animal:.2f} L' if pk.produccion_promedio_por_animal else 'N/A')

print()
print('=== Insights ===')
insights = generar_insights('mes_actual')
if insights:
    for ins in insights:
        print(f'[{ins.nivel}] {ins.categoria}: {ins.mensaje}')
else:
    print('Sin alertas')
