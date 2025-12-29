"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   SCRIPT DE AUDITORÍA OPERATIVA                          ║
║                         FASE 2 - FincaFácil                              ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Script CLI para ejecutar auditorías operativas completas del sistema.
    Detecta inconsistencias, violaciones de reglas de negocio y genera
    reportes ejecutivos.

Uso:
    python scripts/audit_operations.py [--scope all|ventas|nomina|produccion|inventario]
                                       [--output console|file|both]
                                       [--detailed]

Ejemplos:
    python scripts/audit_operations.py
    python scripts/audit_operations.py --scope ventas --output file
    python scripts/audit_operations.py --detailed

Autor: Arquitecto Senior - Fase 2
Fecha: Diciembre 2025
"""

import sys
import os
import argparse
from datetime import datetime, date
from pathlib import Path
import json

# Agregar src/ al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.business_rules import business_rules
from src.services.financial_service import financial_service
from src.services.validation_service import validation_service
from database.database import get_db_connection


class OperationalAuditor:
    """Ejecuta auditorías operativas completas del sistema"""
    
    def __init__(self, detailed: bool = False):
        self.detailed = detailed
        self.timestamp = datetime.now()
        self.results = {
            'timestamp': self.timestamp.isoformat(),
            'detailed': detailed,
            'sections': {}
        }
    
    def print_header(self, title: str, char: str = "═"):
        """Imprime encabezado formateado"""
        width = 80
        print(f"\n{char * width}")
        print(f"{title.center(width)}")
        print(f"{char * width}\n")
    
    def print_section(self, title: str):
        """Imprime título de sección"""
        print(f"\n{'─' * 80}")
        print(f"  {title}")
        print(f"{'─' * 80}")
    
    def audit_database_integrity(self):
        """Auditoría 1: Integridad de base de datos"""
        self.print_section("1. INTEGRIDAD DE BASE DE DATOS")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Contar registros por tabla
            tables = [
                'animal', 'finca', 'potrero', 'lote', 'raza',
                'produccion_leche', 'tratamiento', 'servicio',
                'parto', 'peso', 'venta', 'insumo', 'herramienta',
                'empleado', 'contrato', 'pago_nomina'
            ]
            
            counts = {}
            print("📊 Registros por tabla:\n")
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    counts[table] = count
                    status = "✓" if count > 0 else "⚠"
                    print(f"   {status} {table:20} {count:>6} registros")
                except Exception as e:
                    counts[table] = -1
                    print(f"   ✗ {table:20} ERROR: {e}")
            
            self.results['sections']['database_integrity'] = counts
            
            # Verificar FK principales
            print("\n🔗 Integridad referencial:\n")
            
            checks = [
                ("animal → finca", "SELECT COUNT(*) FROM animal a WHERE NOT EXISTS (SELECT 1 FROM finca f WHERE f.id = a.id_finca)"),
                ("animal → potrero", "SELECT COUNT(*) FROM animal a WHERE a.potrero_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM potrero p WHERE p.id = a.potrero_id)"),
                ("produccion_leche → animal", "SELECT COUNT(*) FROM produccion_leche pl WHERE NOT EXISTS (SELECT 1 FROM animal a WHERE a.id = pl.animal_id)"),
                ("venta → animal", "SELECT COUNT(*) FROM venta v WHERE v.tipo = 'animal' AND NOT EXISTS (SELECT 1 FROM animal a WHERE a.id = v.animal_id)"),
            ]
            
            for check_name, query in checks:
                try:
                    cursor.execute(query)
                    orphans = cursor.fetchone()[0]
                    if orphans == 0:
                        print(f"   ✓ {check_name:30} OK")
                    else:
                        print(f"   ✗ {check_name:30} {orphans} registros huérfanos")
                except Exception as e:
                    print(f"   ✗ {check_name:30} ERROR: {e}")
    
    def audit_business_rules(self, scope: str = 'all'):
        """Auditoría 2: Reglas de negocio"""
        self.print_section("2. VALIDACIÓN DE REGLAS DE NEGOCIO")
        
        # Ejecutar validaciones centralizadas
        report = validation_service.run_all_validations(scope)
        
        summary = report['summary']
        
        print(f"📋 Resumen de validación:\n")
        print(f"   Total de alertas: {report['total_alerts']}")
        print(f"   Alertas críticas: {summary['by_severity']['CRITICAL']} 🔴")
        print(f"   Alertas altas:    {summary['by_severity']['HIGH']} 🟠")
        print(f"   Alertas medias:   {summary['by_severity']['MEDIUM']} 🟡")
        print(f"   Alertas bajas:    {summary['by_severity']['LOW']} 🟢")
        
        print(f"\n📂 Por categoría:\n")
        for category, count in summary['by_category'].items():
            print(f"   {category:20} {count:>3} alertas")
        
        # Mostrar alertas críticas
        critical_alerts = [a for a in report['alerts'] if a['severity'] == 'CRITICAL']
        if critical_alerts:
            print(f"\n🚨 ALERTAS CRÍTICAS (primeras 10):\n")
            for i, alert in enumerate(critical_alerts[:10], 1):
                print(f"   {i}. [{alert['category']}] {alert['message']}")
                if self.detailed and alert.get('recommendation'):
                    print(f"      → {alert['recommendation']}")
        else:
            print(f"\n✅ No se encontraron alertas críticas")
        
        self.results['sections']['business_rules'] = {
            'summary': summary,
            'total_alerts': report['total_alerts'],
            'critical_alerts': critical_alerts[:10] if self.detailed else []
        }
    
    def audit_financial_health(self):
        """Auditoría 3: Salud financiera"""
        self.print_section("3. SALUD FINANCIERA")
        
        # Obtener KPIs del mes actual
        kpis = financial_service.get_dashboard_kpis('mes_actual')
        
        print(f"💰 KPIs Financieros (Mes actual):\n")
        print(f"   Ingresos totales:     ${kpis['ingresos_totales']:>12,.0f}")
        print(f"   ├─ Ventas animales:   ${kpis['ingresos_animales']:>12,.0f}")
        print(f"   └─ Ventas leche:      ${kpis['ingresos_leche']:>12,.0f}")
        
        print(f"\n   Costos totales:       ${kpis['costos_totales']:>12,.0f}")
        print(f"   ├─ Nómina:            ${kpis['costos_nomina']:>12,.0f}")
        print(f"   ├─ Tratamientos:      ${kpis['costos_tratamientos']:>12,.0f}")
        print(f"   └─ Insumos:           ${kpis['costos_insumos']:>12,.0f}")
        
        margen = kpis['margen_bruto']
        margen_pct = kpis['margen_porcentaje']
        
        print(f"\n   Margen bruto:         ${margen:>12,.0f} ({margen_pct:>6.1f}%)")
        
        # Indicador visual del margen
        if margen < 0:
            status = "🔴 DÉFICIT"
        elif margen_pct < 10:
            status = "🟠 BAJO"
        elif margen_pct < 30:
            status = "🟡 MODERADO"
        else:
            status = "🟢 SALUDABLE"
        
        print(f"   Estado:               {status}")
        
        # Precios promedio
        if kpis['precio_promedio_animal']:
            print(f"\n   Precio prom. animal:  ${kpis['precio_promedio_animal']:>12,.0f}")
        if kpis['precio_promedio_leche']:
            print(f"   Precio prom. leche:   ${kpis['precio_promedio_leche']:>12,.0f}/L")
        if kpis['costo_por_litro']:
            print(f"   Costo por litro:      ${kpis['costo_por_litro']:>12,.0f}/L")
        
        # Mostrar alertas financieras
        if kpis['alertas']:
            print(f"\n⚠️  ALERTAS FINANCIERAS:\n")
            for i, alert in enumerate(kpis['alertas'], 1):
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(alert['severity'], '⚪')
                print(f"   {i}. {severity_icon} {alert['message']}")
        else:
            print(f"\n✅ No hay alertas financieras")
        
        self.results['sections']['financial_health'] = {
            'kpis': {k: v for k, v in kpis.items() if k != 'alertas'},
            'alertas': kpis['alertas']
        }
    
    def audit_production_efficiency(self):
        """Auditoría 4: Eficiencia de producción"""
        self.print_section("4. EFICIENCIA DE PRODUCCIÓN")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Producción de leche
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT animal_id) as vacas_produciendo,
                    COUNT(*) as registros,
                    SUM(litros_am + litros_pm) as litros_totales,
                    AVG(litros_am + litros_pm) as promedio_dia,
                    MIN(fecha) as primer_registro,
                    MAX(fecha) as ultimo_registro
                FROM produccion_leche
                WHERE DATE(fecha) >= DATE('now', '-30 days')
            """)
            
            row = cursor.fetchone()
            if row and row[0]:
                vacas, registros, litros, promedio, primera, ultima = row
                
                print(f"🥛 Producción de Leche (últimos 30 días):\n")
                print(f"   Vacas produciendo:    {vacas:>6}")
                print(f"   Registros totales:    {registros:>6}")
                print(f"   Litros producidos:    {litros:>12,.1f}L")
                print(f"   Promedio por día:     {promedio:>12,.1f}L")
                print(f"   Prom. por vaca/día:   {litros/vacas/30:>12,.1f}L" if vacas > 0 else "   N/A")
                print(f"   Período:              {primera} → {ultima}")
                
                # Calcular rentabilidad
                rentabilidad = financial_service.calculate_milk_profitability()
                if rentabilidad:
                    print(f"\n   💰 Rentabilidad:")
                    print(f"   Ingresos:             ${rentabilidad['ingresos']:>12,.0f}")
                    print(f"   Margen por litro:     ${rentabilidad['margen_por_litro']:>12,.0f}/L")
                
                self.results['sections']['production_efficiency'] = {
                    'vacas_produciendo': vacas,
                    'litros_totales': litros,
                    'promedio_dia': promedio,
                    'rentabilidad': rentabilidad
                }
            else:
                print("⚠️  No hay datos de producción en los últimos 30 días")
                self.results['sections']['production_efficiency'] = None
    
    def audit_inventory_status(self):
        """Auditoría 5: Estado de inventarios"""
        self.print_section("5. ESTADO DE INVENTARIOS")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Inventario de animales
            cursor.execute("""
                SELECT 
                    estado,
                    COUNT(*) as cantidad
                FROM animal
                GROUP BY estado
            """)
            
            print(f"🐄 Inventario de Animales:\n")
            total_animales = 0
            for row in cursor.fetchall():
                estado, cantidad = row
                estado = estado or 'Sin estado'
                total_animales += cantidad
                print(f"   {estado:15} {cantidad:>6} animales")
            print(f"   {'TOTAL':15} {total_animales:>6} animales")
            
            # Animales sin potrero
            cursor.execute("""
                SELECT COUNT(*) FROM animal
                WHERE (estado = 'activo' OR estado IS NULL)
                AND potrero_id IS NULL
            """)
            sin_potrero = cursor.fetchone()[0]
            if sin_potrero > 0:
                print(f"\n   ⚠️  {sin_potrero} animales activos sin potrero asignado")
            
            # Capacidad de potreros
            cursor.execute("""
                SELECT 
                    SUM(p.capacidad) as capacidad_total,
                    COUNT(DISTINCT a.id) as ocupacion_total
                FROM potrero p
                LEFT JOIN animal a ON p.id = a.potrero_id AND a.estado != 'muerto'
            """)
            
            capacidad, ocupacion = cursor.fetchone()
            if capacidad:
                uso_pct = (ocupacion / capacidad * 100) if capacidad > 0 else 0
                print(f"\n🌳 Potreros:")
                print(f"   Capacidad total:      {capacidad:>6}")
                print(f"   Ocupación actual:     {ocupacion:>6} ({uso_pct:.1f}%)")
                print(f"   Disponibilidad:       {capacidad - ocupacion:>6} espacios")
            
            # Insumos
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN stock_actual <= 0 THEN 1 ELSE 0 END) as agotados,
                    SUM(CASE WHEN stock_actual < stock_minimo THEN 1 ELSE 0 END) as bajos
                FROM insumo
            """)
            
            total, agotados, bajos = cursor.fetchone()
            print(f"\n📦 Insumos:")
            print(f"   Total registrados:    {total:>6}")
            print(f"   Agotados:             {agotados:>6} {'⚠️' if agotados > 0 else '✓'}")
            print(f"   Stock bajo:           {bajos:>6} {'⚠️' if bajos > 0 else '✓'}")
            
            self.results['sections']['inventory_status'] = {
                'animales': {'total': total_animales, 'sin_potrero': sin_potrero},
                'potreros': {'capacidad': capacidad, 'ocupacion': ocupacion},
                'insumos': {'total': total, 'agotados': agotados, 'bajos': bajos}
            }
    
    def generate_recommendations(self):
        """Genera recomendaciones basadas en los hallazgos"""
        self.print_section("6. RECOMENDACIONES")
        
        recommendations = []
        
        # Basado en reglas de negocio
        br_results = self.results['sections'].get('business_rules', {})
        if br_results.get('critical_alerts', 0) > 0:
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Reglas de Negocio',
                'message': 'Resolver alertas críticas inmediatamente',
                'action': 'Revisar reporte de validaciones y corregir datos inconsistentes'
            })
        
        # Basado en finanzas
        fh_results = self.results['sections'].get('financial_health', {})
        kpis = fh_results.get('kpis', {})
        if kpis.get('margen_bruto', 0) < 0:
            recommendations.append({
                'priority': 'CRÍTICA',
                'category': 'Finanzas',
                'message': 'Déficit operativo detectado',
                'action': 'Analizar estructura de costos y estrategia de precios'
            })
        elif kpis.get('margen_porcentaje', 0) < 10:
            recommendations.append({
                'priority': 'ALTA',
                'category': 'Finanzas',
                'message': 'Margen bruto muy bajo (<10%)',
                'action': 'Optimizar costos operativos o incrementar precios'
            })
        
        # Basado en inventarios
        inv_results = self.results['sections'].get('inventory_status', {})
        insumos = inv_results.get('insumos', {})
        if insumos.get('agotados', 0) > 0:
            recommendations.append({
                'priority': 'MEDIA',
                'category': 'Inventario',
                'message': f"{insumos['agotados']} insumos agotados",
                'action': 'Realizar pedido de reabastecimiento urgente'
            })
        
        animales = inv_results.get('animales', {})
        if animales.get('sin_potrero', 0) > 0:
            recommendations.append({
                'priority': 'MEDIA',
                'category': 'Operaciones',
                'message': f"{animales['sin_potrero']} animales sin potrero",
                'action': 'Asignar potreros a animales activos'
            })
        
        # Mostrar recomendaciones
        if recommendations:
            print("\n💡 Recomendaciones de acción:\n")
            for i, rec in enumerate(recommendations, 1):
                priority_icon = {
                    'CRÍTICA': '🔴',
                    'ALTA': '🟠',
                    'MEDIA': '🟡',
                    'BAJA': '🟢'
                }.get(rec['priority'], '⚪')
                
                print(f"   {i}. {priority_icon} [{rec['priority']}] {rec['category']}")
                print(f"      {rec['message']}")
                print(f"      → {rec['action']}\n")
        else:
            print("\n✅ No se requieren acciones inmediatas")
        
        self.results['sections']['recommendations'] = recommendations
    
    def run_full_audit(self, scope: str = 'all'):
        """Ejecuta auditoría completa"""
        self.print_header("AUDITORÍA OPERATIVA - FINCAFÁCIL", "╔")
        print(f"Fecha: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Alcance: {scope.upper()}")
        print(f"Modo: {'DETALLADO' if self.detailed else 'RESUMEN'}")
        
        self.audit_database_integrity()
        self.audit_business_rules(scope)
        self.audit_financial_health()
        self.audit_production_efficiency()
        self.audit_inventory_status()
        self.generate_recommendations()
        
        self.print_header("FIN DE AUDITORÍA", "╚")
    
    def save_report(self, output_path: str):
        """Guarda reporte en archivo JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✓ Reporte guardado en: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Auditoría Operativa de FincaFácil (Fase 2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s
  %(prog)s --scope ventas --output file
  %(prog)s --detailed
  %(prog)s --scope all --output both --detailed
        """
    )
    
    parser.add_argument(
        '--scope',
        choices=['all', 'ventas', 'nomina', 'produccion', 'inventario'],
        default='all',
        help='Alcance de la auditoría (default: all)'
    )
    
    parser.add_argument(
        '--output',
        choices=['console', 'file', 'both'],
        default='console',
        help='Destino del reporte (default: console)'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Incluir información detallada en el reporte'
    )
    
    args = parser.parse_args()
    
    # Crear auditor
    auditor = OperationalAuditor(detailed=args.detailed)
    
    # Ejecutar auditoría
    try:
        auditor.run_full_audit(scope=args.scope)
        
        # Guardar en archivo si se solicita
        if args.output in ['file', 'both']:
            logs_dir = Path(__file__).parent.parent / 'logs'
            logs_dir.mkdir(exist_ok=True)
            
            timestamp = auditor.timestamp.strftime('%Y%m%d_%H%M%S')
            output_file = logs_dir / f'audit_{timestamp}.json'
            auditor.save_report(str(output_file))
        
        print("\n✓ Auditoría completada exitosamente")
        return 0
        
    except Exception as e:
        print(f"\n✗ Error durante la auditoría: {e}")
        import traceback
        if args.detailed:
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
