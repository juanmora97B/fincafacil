"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     REPORTE DE FINANZAS - FASE 3                         ║
╚══════════════════════════════════════════════════════════════════════════╝

Genera reportes financieros reutilizando FinancialService de FASE 2.
"""

from datetime import date, timedelta
from typing import Dict, Any
import logging
from src.services.financial_service import financial_service


class ReporteFinanzas:
    """Generador de reportes financieros"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.financial_service = financial_service
    
    def generar(self, fecha_inicio: date, fecha_fin: date,
               filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte completo financiero"""
        self.logger.info(f"Generando reporte financiero ({fecha_inicio} → {fecha_fin})")
        
        # Reutilizar servicios de FASE 2
        ingresos = self.financial_service.calculate_total_revenue(fecha_inicio, fecha_fin)
        costos = self.financial_service.calculate_total_costs(fecha_inicio, fecha_fin)
        margen = self.financial_service.calculate_gross_margin(fecha_inicio, fecha_fin)
        
        # Métricas adicionales
        costo_litro = self.financial_service.calculate_production_cost_per_liter(
            fecha_inicio, fecha_fin
        )
        precio_promedio_animal = self.financial_service.calculate_average_animal_price(
            fecha_inicio, fecha_fin
        )
        precio_promedio_leche = self.financial_service.calculate_average_milk_price(
            fecha_inicio, fecha_fin
        )
        
        return {
            'datos': {
                'ingresos': {
                    'total': ingresos['total'],
                    'ventas_animales': ingresos['ventas_animales'],
                    'ventas_leche': ingresos['ventas_leche']
                },
                'costos': {
                    'total': costos['total'],
                    'nomina': costos['nomina'],
                    'tratamientos': costos['tratamientos'],
                    'insumos': costos['insumos']
                },
                'margen': {
                    'valor': margen['margen'],
                    'porcentaje': margen['margen_porcentaje']
                },
                'precios': {
                    'precio_promedio_animal': precio_promedio_animal,
                    'precio_promedio_leche': precio_promedio_leche,
                    'costo_por_litro': costo_litro
                }
            },
            'totales': {
                'ingresos_totales': ingresos['total'],
                'costos_totales': costos['total'],
                'margen_bruto': margen['margen'],
                'margen_porcentaje': margen['margen_porcentaje']
            },
            'metadatos': {
                'tipo': 'finanzas',
                'fuente': 'FinancialService FASE 2'
            }
        }
    
    def obtener_kpis_rapidos(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """KPIs rápidos para resumen ejecutivo"""
        ingresos = self.financial_service.calculate_total_revenue(fecha_inicio, fecha_fin)
        margen = self.financial_service.calculate_gross_margin(fecha_inicio, fecha_fin)
        
        return {
            'ingresos_totales': ingresos['total'],
            'margen_porcentaje': margen['margen_porcentaje']
        }


# Singleton
reporte_finanzas = ReporteFinanzas()
