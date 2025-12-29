"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   REPORTE DE REPRODUCCIÓN - FASE 3                       ║
╚══════════════════════════════════════════════════════════════════════════╝

Genera reportes de servicios, gestaciones y partos.
"""

from datetime import date, timedelta
from typing import Dict, Any
import logging
from src.database.database import get_db_connection


class ReporteReproduccion:
    """Generador de reportes de reproducción"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generar(self, fecha_inicio: date, fecha_fin: date,
               filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Genera reporte completo de reproducción"""
        self.logger.info(f"Generando reporte de reproducción ({fecha_inicio} → {fecha_fin})")
        
        servicios = self.obtener_servicios_periodo(fecha_inicio, fecha_fin)
        gestantes = self.obtener_gestantes_actuales()
        partos = self.obtener_partos_periodo(fecha_inicio, fecha_fin)
        tasas = self.calcular_tasas_reproduccion()
        
        return {
            'datos': {
                'servicios': servicios,
                'gestantes_actuales': gestantes,
                'partos': partos,
                'indicadores': tasas
            },
            'totales': {
                'servicios_realizados': servicios['total'],
                'gestantes_actuales': len(gestantes['listado']),
                'partos_periodo': partos['total'],
                'tasa_prenez_pct': tasas['tasa_prenez_pct']
            },
            'metadatos': {
                'tipo': 'reproduccion'
            }
        }
    
    def obtener_servicios_periodo(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Servicios realizados en el período"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    tipo_servicio,
                    COUNT(*) as cantidad
                FROM servicio
                WHERE DATE(fecha_servicio) BETWEEN ? AND ?
                GROUP BY tipo_servicio
            """, (fecha_inicio, fecha_fin))
            
            rows = cursor.fetchall()
            total = sum(row[2] for row in rows)
            por_tipo = [
                {'tipo': row[1], 'cantidad': row[2]}
                for row in rows
            ]
            
            return {
                'total': total,
                'por_tipo': por_tipo
            }
    
    def obtener_gestantes_actuales(self) -> Dict[str, Any]:
        """Hembras gestantes actuales"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    s.id,
                    a.nombre as hembra,
                    a.codigo as codigo_hembra,
                    s.fecha_servicio,
                    s.fecha_parto_estimada,
                    CAST((JULIANDAY(s.fecha_parto_estimada) - JULIANDAY('now')) AS INTEGER) as dias_para_parto
                FROM servicio s
                JOIN animal a ON s.id_hembra = a.id
                WHERE s.estado = 'Gestante'
                ORDER BY s.fecha_parto_estimada
            """)
            
            listado = []
            for row in cursor.fetchall():
                listado.append({
                    'id_servicio': row[0],
                    'hembra': row[1],
                    'codigo': row[2],
                    'fecha_servicio': row[3],
                    'fecha_estimada_parto': row[4],
                    'dias_restantes': row[5]
                })
            
            return {
                'total': len(listado),
                'listado': listado
            }
    
    def obtener_partos_periodo(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Partos registrados en el período"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Contamos nacimientos por fecha
            cursor.execute("""
                SELECT COUNT(*)
                FROM animal
                WHERE DATE(fecha_nacimiento) BETWEEN ? AND ?
                  AND tipo_ingreso = 'Nacimiento'
            """, (fecha_inicio, fecha_fin))
            
            total_partos = cursor.fetchone()[0]
            
            return {
                'total': total_partos
            }
    
    def calcular_tasas_reproduccion(self) -> Dict[str, Any]:
        """Calcula indicadores reproductivos"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total hembras en edad reproductiva (>2 años, activas)
            cursor.execute("""
                SELECT COUNT(*)
                FROM animal
                WHERE sexo = 'Hembra'
                  AND estado = 'Activo'
                  AND (JULIANDAY('now') - JULIANDAY(fecha_nacimiento)) / 365.25 >= 2
            """)
            
            hembras_aptas = cursor.fetchone()[0]
            
            # Gestantes actuales
            cursor.execute("""
                SELECT COUNT(DISTINCT id_hembra)
                FROM servicio
                WHERE estado = 'Gestante'
            """)
            
            gestantes = cursor.fetchone()[0]
            
            # Calcular tasa de preñez
            tasa_prenez = (gestantes / hembras_aptas * 100) if hembras_aptas > 0 else 0
            
            return {
                'hembras_aptas': hembras_aptas,
                'gestantes': gestantes,
                'tasa_prenez_pct': round(tasa_prenez, 1)
            }


# Singleton
reporte_reproduccion = ReporteReproduccion()
