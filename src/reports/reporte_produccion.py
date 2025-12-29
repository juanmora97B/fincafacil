"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    REPORTE DE PRODUCCIÓN - FASE 3                        ║
╚══════════════════════════════════════════════════════════════════════════╝

Genera reportes de producción de leche.
"""

from datetime import date, timedelta
from typing import Dict, Any, List
import logging
from src.database.database import get_db_connection


class ReporteProduccion:
    """Generador de reportes de producción lechera"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generar(self, fecha_inicio: date, fecha_fin: date,
               filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte completo de producción"""
        self.logger.info(f"Generando reporte de producción ({fecha_inicio} → {fecha_fin})")
        
        produccion_total = self.obtener_produccion_periodo(fecha_inicio, fecha_fin)
        por_animal = self.obtener_produccion_por_animal(fecha_inicio, fecha_fin)
        promedios = self.calcular_promedios(fecha_inicio, fecha_fin)
        
        return {
            'datos': {
                'produccion_periodo': produccion_total,
                'por_animal': por_animal,
                'promedios': promedios
            },
            'totales': {
                'litros_totales': produccion_total['litros_totales'],
                'promedio_diario': promedios['promedio_litros_dia'],
                'vacas_productivas': len(por_animal)
            },
            'metadatos': {
                'tipo': 'produccion'
            }
        }
    
    def obtener_produccion_periodo(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Producción total del período"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(litros_am + litros_pm), 0) as litros_totales,
                    COUNT(DISTINCT DATE(fecha)) as dias_produccion,
                    COUNT(DISTINCT animal_id) as vacas_productivas
                FROM produccion_leche
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            litros_totales, dias_produccion, vacas = row
            
            # Producción por jornada
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(litros_am), 0) as am,
                    COALESCE(SUM(litros_pm), 0) as pm
                FROM produccion_leche
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            am, pm = cursor.fetchone()
            
            return {
                'litros_totales': round(litros_totales, 2),
                'dias_produccion': dias_produccion,
                'vacas_productivas': vacas,
                'por_jornada': {
                    'mañana': round(am, 2),
                    'tarde': round(pm, 2)
                }
            }
    
    def obtener_produccion_por_animal(self, fecha_inicio: date, fecha_fin: date) -> List[Dict[str, Any]]:
        """Producción por animal (top productores)"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    a.codigo,
                    a.nombre,
                    COALESCE(SUM(p.litros_am + p.litros_pm), 0) as litros_totales,
                    COUNT(DISTINCT DATE(p.fecha)) as dias_registrados,
                    COALESCE(AVG(p.litros_am + p.litros_pm), 0) as promedio_diario
                FROM animal a
                JOIN produccion_leche p ON a.id = p.animal_id
                WHERE DATE(p.fecha) BETWEEN ? AND ?
                GROUP BY a.id, a.codigo, a.nombre
                ORDER BY litros_totales DESC
                LIMIT 20
            """, (fecha_inicio, fecha_fin))
            
            return [
                {
                    'codigo': row[0],
                    'nombre': row[1],
                    'litros_totales': round(row[2], 2),
                    'dias_registrados': row[3],
                    'promedio_diario': round(row[4], 2)
                }
                for row in cursor.fetchall()
            ]
    
    def calcular_promedios(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Calcula promedios y métricas"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Promedio por día
            cursor.execute("""
                SELECT 
                    DATE(fecha) as dia,
                    SUM(litros_am + litros_pm) as litros
                FROM produccion_leche
                WHERE DATE(fecha) BETWEEN ? AND ?
                GROUP BY DATE(fecha)
            """, (fecha_inicio, fecha_fin))
            
            dias_data = cursor.fetchall()
            
            if dias_data:
                total_litros = sum(row[1] for row in dias_data)
                dias_count = len(dias_data)
                promedio_dia = total_litros / dias_count if dias_count > 0 else 0
            else:
                promedio_dia = 0
            
            # Promedio por vaca
            cursor.execute("""
                SELECT AVG(promedio_vaca)
                FROM (
                    SELECT 
                        animal_id,
                        AVG(litros_am + litros_pm) as promedio_vaca
                    FROM produccion_leche
                    WHERE DATE(fecha) BETWEEN ? AND ?
                    GROUP BY animal_id
                )
            """, (fecha_inicio, fecha_fin))
            
            promedio_vaca = cursor.fetchone()[0] or 0
            
            return {
                'promedio_litros_dia': round(promedio_dia, 2),
                'promedio_litros_vaca': round(promedio_vaca, 2)
            }
    
    def obtener_ultimos_dias(self, dias: int = 7) -> Dict[str, Any]:
        """Producción de los últimos N días (para resumen rápido)"""
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        produccion = self.obtener_produccion_periodo(fecha_inicio, fecha_fin)
        promedios = self.calcular_promedios(fecha_inicio, fecha_fin)
        
        return {
            'total_litros': produccion['litros_totales'],
            'promedio_diario': promedios['promedio_litros_dia']
        }


# Singleton
reporte_produccion = ReporteProduccion()
