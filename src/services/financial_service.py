"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SERVICIO FINANCIERO CENTRALIZADO                      ║
║                         FASE 2 - FincaFácil                              ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Centralizar todos los cálculos financieros, métricas y KPIs del sistema.
    Garantizar consistencia en reportes y trazabilidad de costos/ingresos.

Responsabilidades:
    - Cálculo de ingresos (ventas de animales y leche)
    - Cálculo de costos (insumos, tratamientos, nómina)
    - Márgenes y rentabilidad
    - KPIs financieros para dashboard
    - Reportes mensuales/anuales

Autor: Arquitecto Senior - Fase 2
Fecha: Diciembre 2025
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import logging
from src.database.database import get_db_connection


class FinancialService:
    """
    Servicio centralizado para cálculos financieros y reportes.
    
    Principios:
        - Todos los montos en COP (Pesos Colombianos)
        - Cálculos con precisión decimal
        - Cacheo opcional para dashboards
        - Logging de operaciones críticas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
    
    # ═══════════════════════════════════════════════════════════════════════
    #                         INGRESOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def calculate_total_revenue(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, float]:
        """
        Calcula ingresos totales en un período.
        
        Args:
            fecha_inicio: Fecha inicial del período
            fecha_fin: Fecha final del período
        
        Returns:
            {
                'total': Total general,
                'ventas_animales': Ingresos por venta de animales,
                'ventas_leche': Ingresos por venta de leche,
                'otros': Otros ingresos
            }
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Ingresos por ventas de animales
            cursor.execute("""
                SELECT COALESCE(SUM(precio), 0)
                FROM venta
                WHERE tipo = 'animal'
                AND DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            ventas_animales = float(cursor.fetchone()[0])
            
            # Ingresos por ventas de leche
            cursor.execute("""
                SELECT COALESCE(SUM(precio * cantidad), 0)
                FROM venta
                WHERE tipo = 'leche'
                AND DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            ventas_leche = float(cursor.fetchone()[0])
            
            total = ventas_animales + ventas_leche
            
            self.logger.info(
                f"Ingresos {fecha_inicio} → {fecha_fin}: "
                f"${total:,.0f} (Animales: ${ventas_animales:,.0f}, Leche: ${ventas_leche:,.0f})"
            )
            
            return {
                'total': total,
                'ventas_animales': ventas_animales,
                'ventas_leche': ventas_leche,
                'otros': 0  # Futuras expansiones
            }
    
    def calculate_average_animal_price(self, fecha_inicio: Optional[date] = None, 
                                      fecha_fin: Optional[date] = None) -> Optional[float]:
        """
        Calcula precio promedio de venta de animales.
        
        Args:
            fecha_inicio: Fecha inicial (opcional, últimos 6 meses por defecto)
            fecha_fin: Fecha final (opcional, hoy por defecto)
        
        Returns:
            Precio promedio o None si no hay ventas
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=180)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(precio), COUNT(*)
                FROM venta
                WHERE tipo = 'animal'
                AND DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            promedio, cantidad = row if row else (None, 0)
            
            if promedio and cantidad > 0:
                self.logger.debug(f"Precio promedio animales: ${promedio:,.0f} ({cantidad} ventas)")
                return float(promedio)
            
            return None
    
    def calculate_average_milk_price(self, fecha_inicio: Optional[date] = None, 
                                    fecha_fin: Optional[date] = None) -> Optional[float]:
        """
        Calcula precio promedio por litro de leche.
        
        Args:
            fecha_inicio: Fecha inicial (opcional, últimos 30 días por defecto)
            fecha_fin: Fecha final (opcional, hoy por defecto)
        
        Returns:
            Precio promedio por litro o None si no hay ventas
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(precio), COUNT(*)
                FROM venta
                WHERE tipo = 'leche'
                AND DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            promedio, cantidad = row if row else (None, 0)
            
            if promedio and cantidad > 0:
                self.logger.debug(f"Precio promedio leche: ${promedio:,.0f}/L ({cantidad} ventas)")
                return float(promedio)
            
            return None
    
    # ═══════════════════════════════════════════════════════════════════════
    #                         COSTOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def calculate_total_costs(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, float]:
        """
        Calcula costos totales en un período.
        
        Args:
            fecha_inicio: Fecha inicial del período
            fecha_fin: Fecha final del período
        
        Returns:
            {
                'total': Total general,
                'nomina': Costos de nómina,
                'tratamientos': Costos veterinarios,
                'insumos': Costos de insumos,
                'otros': Otros costos
            }
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Costos de nómina
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM pago_nomina
                WHERE DATE(fecha_pago) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            nomina = float(cursor.fetchone()[0])
            
            # Costos de tratamientos veterinarios
            cursor.execute("""
                SELECT COALESCE(SUM(costo), 0)
                FROM tratamiento
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            tratamientos = float(cursor.fetchone()[0])
            
            # Costos de insumos (salidas)
            cursor.execute("""
                SELECT COALESCE(SUM(i.precio_unitario * mi.cantidad), 0)
                FROM movimiento_insumo mi
                INNER JOIN insumo i ON mi.insumo_id = i.id
                WHERE mi.tipo = 'salida'
                AND DATE(mi.fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            insumos = float(cursor.fetchone()[0])
            
            total = nomina + tratamientos + insumos
            
            self.logger.info(
                f"Costos {fecha_inicio} → {fecha_fin}: "
                f"${total:,.0f} (Nómina: ${nomina:,.0f}, "
                f"Tratamientos: ${tratamientos:,.0f}, Insumos: ${insumos:,.0f})"
            )
            
            return {
                'total': total,
                'nomina': nomina,
                'tratamientos': tratamientos,
                'insumos': insumos,
                'otros': 0
            }
    
    def calculate_production_cost_per_liter(self, fecha_inicio: Optional[date] = None,
                                           fecha_fin: Optional[date] = None) -> Optional[float]:
        """
        Calcula costo de producción por litro de leche.
        
        Incluye:
            - Costos de alimentación (insumos)
            - Costos veterinarios
            - Proporción de nómina
        
        Args:
            fecha_inicio: Fecha inicial (opcional, último mes por defecto)
            fecha_fin: Fecha final (opcional, hoy por defecto)
        
        Returns:
            Costo por litro o None si no hay producción
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total de litros producidos
            cursor.execute("""
                SELECT COALESCE(SUM(litros_am + litros_pm), 0)
                FROM produccion_leche
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            litros_producidos = float(cursor.fetchone()[0])
            
            if litros_producidos == 0:
                return None
            
            # Calcular costos del período
            costos = self.calculate_total_costs(fecha_inicio, fecha_fin)
            
            # Estimación: 70% de los costos son atribuibles a producción de leche
            # (el resto son costos de cría, reproducción, etc.)
            costos_produccion = costos['total'] * 0.7
            
            costo_por_litro = costos_produccion / litros_producidos
            
            self.logger.debug(
                f"Costo por litro: ${costo_por_litro:,.2f} "
                f"({litros_producidos:.0f}L producidos, ${costos_produccion:,.0f} costos)"
            )
            
            return costo_por_litro
    
    def calculate_animal_maintenance_cost(self, animal_id: int, 
                                         fecha_inicio: Optional[date] = None,
                                         fecha_fin: Optional[date] = None) -> Dict[str, float]:
        """
        Calcula costo de mantenimiento de un animal específico.
        
        Incluye:
            - Tratamientos veterinarios
            - Estimación de alimentación
        
        Args:
            animal_id: ID del animal
            fecha_inicio: Fecha inicial (opcional, último año por defecto)
            fecha_fin: Fecha final (opcional, hoy por defecto)
        
        Returns:
            {
                'total': Costo total,
                'tratamientos': Costos veterinarios,
                'alimentacion_estimada': Estimación de costos de alimentación
            }
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=365)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Costos de tratamientos
            cursor.execute("""
                SELECT COALESCE(SUM(costo), 0)
                FROM tratamiento
                WHERE animal_id = ?
                AND DATE(fecha) BETWEEN ? AND ?
            """, (animal_id, fecha_inicio, fecha_fin))
            tratamientos = float(cursor.fetchone()[0])
            
            # Estimación de alimentación: $5,000 COP por día
            dias = (fecha_fin - fecha_inicio).days
            alimentacion = dias * 5000
            
            total = tratamientos + alimentacion
            
            return {
                'total': total,
                'tratamientos': tratamientos,
                'alimentacion_estimada': alimentacion
            }
    
    # ═══════════════════════════════════════════════════════════════════════
    #                    MÁRGENES Y RENTABILIDAD
    # ═══════════════════════════════════════════════════════════════════════
    
    def calculate_gross_margin(self, fecha_inicio: date, fecha_fin: date) -> Dict[str, float]:
        """
        Calcula margen bruto en un período.
        
        Margen Bruto = Ingresos - Costos
        Margen % = (Margen / Ingresos) * 100
        
        Args:
            fecha_inicio: Fecha inicial del período
            fecha_fin: Fecha final del período
        
        Returns:
            {
                'ingresos': Total de ingresos,
                'costos': Total de costos,
                'margen': Margen bruto (ingresos - costos),
                'margen_porcentaje': Margen como % de ingresos
            }
        """
        ingresos_data = self.calculate_total_revenue(fecha_inicio, fecha_fin)
        costos_data = self.calculate_total_costs(fecha_inicio, fecha_fin)
        
        ingresos = ingresos_data['total']
        costos = costos_data['total']
        margen = ingresos - costos
        margen_pct = (margen / ingresos * 100) if ingresos > 0 else 0
        
        self.logger.info(
            f"Margen bruto {fecha_inicio} → {fecha_fin}: "
            f"${margen:,.0f} ({margen_pct:.1f}%) | "
            f"Ingresos: ${ingresos:,.0f} - Costos: ${costos:,.0f}"
        )
        
        return {
            'ingresos': ingresos,
            'costos': costos,
            'margen': margen,
            'margen_porcentaje': margen_pct
        }
    
    def calculate_milk_profitability(self, fecha_inicio: Optional[date] = None,
                                    fecha_fin: Optional[date] = None) -> Optional[Dict[str, float]]:
        """
        Calcula rentabilidad específica de producción de leche.
        
        Args:
            fecha_inicio: Fecha inicial (opcional, último mes por defecto)
            fecha_fin: Fecha final (opcional, hoy por defecto)
        
        Returns:
            {
                'litros_producidos': Total de litros,
                'litros_vendidos': Litros vendidos,
                'ingresos': Ingresos por venta de leche,
                'costo_por_litro': Costo de producción por litro,
                'costo_total': Costo total de producción,
                'margen': Margen bruto,
                'margen_por_litro': Margen por litro vendido
            }
            o None si no hay datos suficientes
        """
        if fecha_fin is None:
            fecha_fin = date.today()
        if fecha_inicio is None:
            fecha_inicio = fecha_fin - timedelta(days=30)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Litros producidos
            cursor.execute("""
                SELECT COALESCE(SUM(litros_am + litros_pm), 0)
                FROM produccion_leche
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            litros_producidos = float(cursor.fetchone()[0])
            
            if litros_producidos == 0:
                return None
            
            # Litros vendidos e ingresos
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(cantidad), 0),
                    COALESCE(SUM(cantidad * precio), 0)
                FROM venta
                WHERE tipo = 'leche'
                AND DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            litros_vendidos, ingresos = float(row[0]), float(row[1])
            
            # Costo por litro
            costo_por_litro = self.calculate_production_cost_per_liter(fecha_inicio, fecha_fin)
            if not costo_por_litro:
                costo_por_litro = 0
            
            costo_total = litros_producidos * costo_por_litro
            margen = ingresos - (litros_vendidos * costo_por_litro)
            margen_por_litro = margen / litros_vendidos if litros_vendidos > 0 else 0
            
            return {
                'litros_producidos': litros_producidos,
                'litros_vendidos': litros_vendidos,
                'ingresos': ingresos,
                'costo_por_litro': costo_por_litro,
                'costo_total': costo_total,
                'margen': margen,
                'margen_por_litro': margen_por_litro
            }
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      KPIs PARA DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_dashboard_kpis(self, periodo: str = 'mes_actual') -> Dict[str, Any]:
        """
        Obtiene todos los KPIs financieros para el dashboard.
        
        Args:
            periodo: 'mes_actual', 'mes_anterior', 'anio_actual', 'ultimos_30_dias'
        
        Returns:
            Diccionario completo con todos los KPIs financieros
        """
        # Determinar fechas según período
        hoy = date.today()
        
        if periodo == 'mes_actual':
            fecha_inicio = date(hoy.year, hoy.month, 1)
            fecha_fin = hoy
        elif periodo == 'mes_anterior':
            primer_dia_mes = date(hoy.year, hoy.month, 1)
            fecha_fin = primer_dia_mes - timedelta(days=1)
            fecha_inicio = date(fecha_fin.year, fecha_fin.month, 1)
        elif periodo == 'anio_actual':
            fecha_inicio = date(hoy.year, 1, 1)
            fecha_fin = hoy
        else:  # ultimos_30_dias
            fecha_fin = hoy
            fecha_inicio = hoy - timedelta(days=30)
        
        # Calcular todos los KPIs
        ingresos = self.calculate_total_revenue(fecha_inicio, fecha_fin)
        costos = self.calculate_total_costs(fecha_inicio, fecha_fin)
        margen = self.calculate_gross_margin(fecha_inicio, fecha_fin)
        rentabilidad_leche = self.calculate_milk_profitability(fecha_inicio, fecha_fin)
        
        precio_promedio_animal = self.calculate_average_animal_price(fecha_inicio, fecha_fin)
        precio_promedio_leche = self.calculate_average_milk_price(fecha_inicio, fecha_fin)
        costo_por_litro = self.calculate_production_cost_per_liter(fecha_inicio, fecha_fin)
        
        kpis = {
            'periodo': periodo,
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            
            # Ingresos
            'ingresos_totales': ingresos['total'],
            'ingresos_animales': ingresos['ventas_animales'],
            'ingresos_leche': ingresos['ventas_leche'],
            
            # Costos
            'costos_totales': costos['total'],
            'costos_nomina': costos['nomina'],
            'costos_tratamientos': costos['tratamientos'],
            'costos_insumos': costos['insumos'],
            
            # Márgenes
            'margen_bruto': margen['margen'],
            'margen_porcentaje': margen['margen_porcentaje'],
            
            # Precios promedio
            'precio_promedio_animal': precio_promedio_animal,
            'precio_promedio_leche': precio_promedio_leche,
            'costo_por_litro': costo_por_litro,
            
            # Rentabilidad leche
            'rentabilidad_leche': rentabilidad_leche,
            
            # Alertas
            'alertas': self._generate_alerts(margen, costos, ingresos)
        }
        
        self.logger.info(f"KPIs generados para {periodo}: Margen {margen['margen_porcentaje']:.1f}%")
        
        return kpis
    
    def _generate_alerts(self, margen: Dict, costos: Dict, ingresos: Dict) -> List[Dict[str, str]]:
        """
        Genera alertas automáticas basadas en KPIs.
        
        Returns:
            Lista de alertas con severidad y mensaje
        """
        alertas = []
        
        # Alerta: Margen negativo
        if margen['margen'] < 0:
            alertas.append({
                'severity': 'CRITICAL',
                'category': 'rentabilidad',
                'message': f"Margen negativo: -${abs(margen['margen']):,.0f}. Costos superan ingresos."
            })
        
        # Alerta: Margen muy bajo
        elif margen['margen_porcentaje'] < 10:
            alertas.append({
                'severity': 'HIGH',
                'category': 'rentabilidad',
                'message': f"Margen muy bajo: {margen['margen_porcentaje']:.1f}%. Revisar estructura de costos."
            })
        
        # Alerta: Nómina desproporcionada
        if costos['total'] > 0:
            nomina_pct = (costos['nomina'] / costos['total']) * 100
            if nomina_pct > 60:
                alertas.append({
                    'severity': 'MEDIUM',
                    'category': 'costos',
                    'message': f"Nómina representa {nomina_pct:.1f}% de costos totales (>{60}% recomendado)."
                })
        
        # Alerta: Costos > Ingresos
        if costos['total'] > ingresos['total']:
            deficit = costos['total'] - ingresos['total']
            alertas.append({
                'severity': 'CRITICAL',
                'category': 'flujo_caja',
                'message': f"Déficit de ${deficit:,.0f}. Costos superan ingresos."
            })
        
        # Alerta: Sin ingresos por leche
        if ingresos['ventas_leche'] == 0:
            alertas.append({
                'severity': 'MEDIUM',
                'category': 'ingresos',
                'message': "No hay ventas de leche registradas en el período."
            })
        
        return alertas
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      REPORTES Y ANÁLISIS
    # ═══════════════════════════════════════════════════════════════════════
    
    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """
        Genera reporte financiero completo de un mes.
        
        Args:
            year: Año (ej: 2025)
            month: Mes (1-12)
        
        Returns:
            Diccionario con reporte detallado
        """
        # Calcular fechas
        fecha_inicio = date(year, month, 1)
        if month == 12:
            fecha_fin = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(year, month + 1, 1) - timedelta(days=1)
        
        # Generar KPIs para el mes
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Estadísticas de ventas
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE tipo = 'animal') as ventas_animales,
                    COUNT(*) FILTER (WHERE tipo = 'leche') as ventas_leche,
                    COALESCE(SUM(cantidad) FILTER (WHERE tipo = 'leche'), 0) as litros_vendidos
                FROM venta
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            ventas_animales_count, ventas_leche_count, litros_vendidos = row
            
            # Estadísticas de producción
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(litros_am + litros_pm), 0) as litros_producidos,
                    COUNT(DISTINCT animal_id) as vacas_produciendo
                FROM produccion_leche
                WHERE DATE(fecha) BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            litros_producidos, vacas_produciendo = row
        
        kpis = self.get_dashboard_kpis('mes_actual')  # Usaremos esta estructura
        
        reporte = {
            'periodo': f"{year}-{month:02d}",
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'resumen_financiero': {
                'ingresos_totales': kpis['ingresos_totales'],
                'costos_totales': kpis['costos_totales'],
                'margen_bruto': kpis['margen_bruto'],
                'margen_porcentaje': kpis['margen_porcentaje']
            },
            'desglose_ingresos': {
                'ventas_animales': {'cantidad': ventas_animales_count, 'monto': kpis['ingresos_animales']},
                'ventas_leche': {'cantidad': ventas_leche_count, 'litros': litros_vendidos, 'monto': kpis['ingresos_leche']}
            },
            'desglose_costos': {
                'nomina': kpis['costos_nomina'],
                'tratamientos': kpis['costos_tratamientos'],
                'insumos': kpis['costos_insumos']
            },
            'estadisticas_produccion': {
                'litros_producidos': litros_producidos,
                'litros_vendidos': litros_vendidos,
                'vacas_produciendo': vacas_produciendo,
                'promedio_por_vaca': litros_producidos / vacas_produciendo if vacas_produciendo > 0 else 0
            },
            'alertas': kpis['alertas']
        }
        
        self.logger.info(f"Reporte mensual generado: {year}-{month:02d}")
        
        return reporte
    
    def compare_periods(self, periodo1_inicio: date, periodo1_fin: date,
                       periodo2_inicio: date, periodo2_fin: date) -> Dict[str, Any]:
        """
        Compara métricas entre dos períodos.
        
        Returns:
            Diccionario con comparación y variaciones porcentuales
        """
        # Calcular KPIs de ambos períodos
        p1_ingresos = self.calculate_total_revenue(periodo1_inicio, periodo1_fin)
        p2_ingresos = self.calculate_total_revenue(periodo2_inicio, periodo2_fin)
        
        p1_costos = self.calculate_total_costs(periodo1_inicio, periodo1_fin)
        p2_costos = self.calculate_total_costs(periodo2_inicio, periodo2_fin)
        
        p1_margen = self.calculate_gross_margin(periodo1_inicio, periodo1_fin)
        p2_margen = self.calculate_gross_margin(periodo2_inicio, periodo2_fin)
        
        # Calcular variaciones
        def calc_variation(val1, val2):
            if val1 == 0:
                return 0
            return ((val2 - val1) / val1) * 100
        
        return {
            'periodo1': {
                'inicio': periodo1_inicio.isoformat(),
                'fin': periodo1_fin.isoformat(),
                'ingresos': p1_ingresos['total'],
                'costos': p1_costos['total'],
                'margen': p1_margen['margen']
            },
            'periodo2': {
                'inicio': periodo2_inicio.isoformat(),
                'fin': periodo2_fin.isoformat(),
                'ingresos': p2_ingresos['total'],
                'costos': p2_costos['total'],
                'margen': p2_margen['margen']
            },
            'variaciones': {
                'ingresos_pct': calc_variation(p1_ingresos['total'], p2_ingresos['total']),
                'costos_pct': calc_variation(p1_costos['total'], p2_costos['total']),
                'margen_pct': calc_variation(p1_margen['margen'], p2_margen['margen'])
            }
        }


# ═══════════════════════════════════════════════════════════════════════════
#                            INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════════════════

# Singleton para uso en toda la aplicación
financial_service = FinancialService()
