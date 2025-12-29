"""
╔══════════════════════════════════════════════════════════════════════════╗
║                      REPORTE DE ANIMALES - FASE 3                        ║
╚══════════════════════════════════════════════════════════════════════════╝

Genera reportes de inventario y movimientos de animales.
"""

from datetime import date
from typing import Dict, Any
import logging
from src.database.database import get_db_connection


class ReporteAnimales:
    """Generador de reportes de animales e inventario"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generar(self, fecha_inicio: date, fecha_fin: date, 
               filtros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera reporte completo de animales.
        
        Returns:
            Dict con inventario, altas, bajas y estadísticas
        """
        self.logger.info(f"Generando reporte de animales ({fecha_inicio} → {fecha_fin})")
        
        inventario = self.obtener_inventario_actual()
        movimientos = self.obtener_movimientos_periodo(fecha_inicio, fecha_fin)
        estadisticas = self.obtener_estadisticas_generales()
        
        return {
            'datos': {
                'inventario_actual': inventario,
                'movimientos': movimientos,
                'estadisticas': estadisticas
            },
            'totales': {
                'total_activos': inventario['total_activos'],
                'altas_periodo': movimientos['total_altas'],
                'bajas_periodo': movimientos['total_bajas']
            },
            'metadatos': {
                'tipo': 'animales',
                'incluye_historico': True
            }
        }
    
    def obtener_inventario_actual(self) -> Dict[str, Any]:
        """Inventario actual de animales por estado y categoría"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total por estado
            cursor.execute("""
                SELECT 
                    estado,
                    COUNT(*) as cantidad,
                    COUNT(CASE WHEN sexo = 'Macho' THEN 1 END) as machos,
                    COUNT(CASE WHEN sexo = 'Hembra' THEN 1 END) as hembras
                FROM animal
                GROUP BY estado
            """)
            
            por_estado = {}
            total_activos = 0
            
            for row in cursor.fetchall():
                estado, cantidad, machos, hembras = row
                por_estado[estado] = {
                    'cantidad': cantidad,
                    'machos': machos,
                    'hembras': hembras
                }
                
                if estado == 'Activo':
                    total_activos = cantidad
            
            # Gestantes actuales
            cursor.execute("""
                SELECT COUNT(DISTINCT id_hembra)
                FROM servicio
                WHERE estado = 'Gestante'
            """)
            gestantes = cursor.fetchone()[0]
            
            # Distribución por raza (solo activos)
            cursor.execute("""
                SELECT r.nombre, COUNT(*) as cantidad
                FROM animal a
                JOIN raza r ON a.id_raza = r.id
                WHERE a.estado = 'Activo'
                GROUP BY r.nombre
                ORDER BY cantidad DESC
            """)
            
            por_raza = [
                {'raza': row[0], 'cantidad': row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                'total_activos': total_activos,
                'gestantes': gestantes,
                'por_estado': por_estado,
                'por_raza': por_raza
            }
    
    def obtener_movimientos_periodo(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, Any]:
        """Altas y bajas en el período"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Altas (compras/nacimientos)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    tipo_ingreso,
                    COUNT(*) as cantidad
                FROM animal
                WHERE DATE(fecha_nacimiento) BETWEEN ? AND ?
                GROUP BY tipo_ingreso
            """, (fecha_inicio, fecha_fin))
            
            altas_rows = cursor.fetchall()
            total_altas = sum(row[2] for row in altas_rows)
            altas_por_tipo = [
                {'tipo': row[1], 'cantidad': row[2]}
                for row in altas_rows
            ]
            
            # Bajas (ventas)
            cursor.execute("""
                SELECT COUNT(DISTINCT id_animal)
                FROM venta
                WHERE tipo = 'animal'
                  AND DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            total_ventas = cursor.fetchone()[0]
            
            # Muertes
            cursor.execute("""
                SELECT COUNT(*)
                FROM animal
                WHERE estado = 'Muerto'
                  AND DATE(fecha_muerte) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            total_muertes = cursor.fetchone()[0]
            
            return {
                'total_altas': total_altas,
                'altas_detalle': altas_por_tipo,
                'total_bajas': total_ventas + total_muertes,
                'ventas': total_ventas,
                'muertes': total_muertes
            }
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Estadísticas generales del hato"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Edad promedio
            cursor.execute("""
                SELECT AVG(JULIANDAY('now') - JULIANDAY(fecha_nacimiento)) / 365.25
                FROM animal
                WHERE estado = 'Activo'
            """)
            
            edad_promedio = cursor.fetchone()[0] or 0
            
            # Peso promedio
            cursor.execute("""
                SELECT AVG(peso_actual)
                FROM animal
                WHERE estado = 'Activo'
                  AND peso_actual IS NOT NULL
            """)
            
            peso_promedio = cursor.fetchone()[0] or 0
            
            return {
                'edad_promedio_años': round(edad_promedio, 1),
                'peso_promedio_kg': round(peso_promedio, 1)
            }


# Singleton
reporte_animales = ReporteAnimales()
