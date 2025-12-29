"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SERVICIO DE CÁLCULO DE KPIs - FASE CONSOLIDACIÓN      ║
╚══════════════════════════════════════════════════════════════════════════╝

Calcula Key Performance Indicators (KPIs) para análisis de negocio.

KPIs implementados:
- Margen Neto (%) y valor absoluto
- Producción diaria promedio (litros/día)
- Costo por litro producido ($/ litro)
- Tasa de preñez (%)
- Eficiencia reproductiva
- Mortalidad animal (%)
- Rotación de empleados (%)
"""

from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import logging
from src.database.database import get_db_connection

logger = logging.getLogger("kpi_calculator")


class KPICalculatorService:
    """Servicio para calcular KPIs del negocio"""
    
    def __init__(self):
        self.logger = logger
        self._asegurar_tabla_kpi()
    
    def _asegurar_tabla_kpi(self):
        """Asegura que la tabla kpi_tracking existe"""
        try:
            with get_db_connection() as conn:
                conn.execute("SELECT 1 FROM kpi_tracking LIMIT 1")
        except Exception as e:
            self.logger.warning(f"Tabla kpi_tracking no disponible: {e}")
    
    def calcular_kpis_periodo(
        self,
        fecha_inicio: str | date,
        fecha_fin: str | date,
        categoria: str = "general"
    ) -> Dict[str, Any]:
        """
        Calcula todos los KPIs para un período específico.
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            categoria: Categoría del KPI (general, financiero, produccion, reproduccion)
        
        Returns:
            Diccionario con todos los KPIs calculados
        """
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        
        kpis = {}
        
        # KPIs financieros
        if categoria in ["general", "financiero"]:
            kpis.update(self._calcular_kpis_financieros(fecha_inicio, fecha_fin))
        
        # KPIs de producción
        if categoria in ["general", "produccion"]:
            kpis.update(self._calcular_kpis_produccion(fecha_inicio, fecha_fin))
        
        # KPIs de reproducción
        if categoria in ["general", "reproduccion"]:
            kpis.update(self._calcular_kpis_reproduccion(fecha_inicio, fecha_fin))
        
        # KPIs de gestión animal
        if categoria in ["general", "animales"]:
            kpis.update(self._calcular_kpis_animales(fecha_inicio, fecha_fin))
        
        return kpis
    
    def _calcular_kpis_financieros(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> Dict[str, float]:
        """Calcula KPIs financieros"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Ingresos totales
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN v.precio_total IS NOT NULL THEN v.precio_total ELSE 0 END), 0) as ventas_animales,
                    COALESCE(SUM(CASE WHEN vl.precio_total IS NOT NULL THEN vl.precio_total ELSE 0 END), 0) as ventas_leche
                FROM (SELECT 1) dummy
                LEFT JOIN venta v ON v.fecha BETWEEN ? AND ?
                LEFT JOIN venta_leche vl ON vl.fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            ventas_animales = row[0] if row else 0
            ventas_leche = row[1] if row else 0
            ingresos_totales = ventas_animales + ventas_leche
            
            # Costos totales
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN g.monto IS NOT NULL THEN g.monto ELSE 0 END), 0) as gastos,
                    COALESCE(SUM(CASE WHEN p.total_pagado IS NOT NULL THEN p.total_pagado ELSE 0 END), 0) as nomina,
                    COALESCE(SUM(CASE WHEN t.costo IS NOT NULL THEN t.costo ELSE 0 END), 0) as tratamientos
                FROM (SELECT 1) dummy
                LEFT JOIN gasto g ON g.fecha BETWEEN ? AND ?
                LEFT JOIN pago_nomina p ON p.fecha_pago BETWEEN ? AND ?
                LEFT JOIN tratamiento t ON t.fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            gastos = row[0] if row else 0
            nomina = row[1] if row else 0
            tratamientos = row[2] if row else 0
            costos_totales = gastos + nomina + tratamientos
            
            # Cálculos
            margen_bruto = ingresos_totales - costos_totales
            margen_porcentaje = (margen_bruto / ingresos_totales * 100) if ingresos_totales > 0 else 0
            
            return {
                'margen_neto_pct': round(margen_porcentaje, 2),
                'margen_neto_valor': round(margen_bruto, 2),
                'ingresos_totales': round(ingresos_totales, 2),
                'costos_totales': round(costos_totales, 2),
                'roi_porcentaje': round((margen_bruto / costos_totales * 100) if costos_totales > 0 else 0, 2)
            }
    
    def _calcular_kpis_produccion(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> Dict[str, float]:
        """Calcula KPIs de producción lechera"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Producción total
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(cantidad_litros), 0) as litros_totales,
                    COUNT(DISTINCT fecha) as dias_registrados,
                    COUNT(DISTINCT animal_id) as vacas_productivas
                FROM produccion_leche
                WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            litros_totales = row[0] if row else 0
            dias_registrados = row[1] if row else 1
            vacas_productivas = row[2] if row else 0
            
            # Costos de producción
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM gasto
                WHERE categoria IN ('Alimentación', 'Insumos', 'Veterinario')
                AND fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            costos_produccion = cursor.fetchone()[0] or 0
            
            # Cálculos
            produccion_diaria = litros_totales / dias_registrados if dias_registrados > 0 else 0
            produccion_por_vaca = litros_totales / vacas_productivas if vacas_productivas > 0 else 0
            costo_por_litro = costos_produccion / litros_totales if litros_totales > 0 else 0
            
            return {
                'produccion_diaria_promedio': round(produccion_diaria, 2),
                'produccion_por_vaca_promedio': round(produccion_por_vaca, 2),
                'costo_por_litro': round(costo_por_litro, 2),
                'litros_totales_periodo': round(litros_totales, 2),
                'vacas_productivas': vacas_productivas
            }
    
    def _calcular_kpis_reproduccion(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> Dict[str, float]:
        """Calcula KPIs de reproducción"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Servicios y preñeces
            cursor.execute("""
                SELECT 
                    COUNT(*) as servicios_totales,
                    SUM(CASE WHEN confirmacion_prenez = 'Positivo' THEN 1 ELSE 0 END) as servicios_exitosos
                FROM servicio
                WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            row = cursor.fetchone()
            servicios_totales = row[0] if row else 0
            servicios_exitosos = row[1] if row else 0
            
            tasa_prenez = (servicios_exitosos / servicios_totales * 100) if servicios_totales > 0 else 0
            
            # Partos
            cursor.execute("""
                SELECT COUNT(*) FROM parto
                WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            partos_periodo = cursor.fetchone()[0] or 0
            
            # Intervalo entre partos (promedio)
            cursor.execute("""
                SELECT AVG(julianday(p2.fecha) - julianday(p1.fecha)) as dias_promedio
                FROM parto p1
                JOIN parto p2 ON p1.animal_id = p2.animal_id AND p2.fecha > p1.fecha
                WHERE p1.fecha BETWEEN ? AND ?
                AND p2.fecha <= ?
            """, (fecha_inicio, fecha_fin, fecha_fin))
            
            intervalo_partos = cursor.fetchone()[0] or 0
            
            return {
                'tasa_prenez_pct': round(tasa_prenez, 2),
                'servicios_realizados': servicios_totales,
                'servicios_exitosos': servicios_exitosos,
                'partos_periodo': partos_periodo,
                'intervalo_partos_promedio_dias': round(intervalo_partos, 1) if intervalo_partos else 0
            }
    
    def _calcular_kpis_animales(
        self, 
        fecha_inicio: date, 
        fecha_fin: date
    ) -> Dict[str, float]:
        """Calcula KPIs de gestión animal"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Animales activos al inicio
            cursor.execute("""
                SELECT COUNT(*) FROM animal
                WHERE fecha_nacimiento <= ?
                AND (fecha_muerte IS NULL OR fecha_muerte > ?)
                AND (estado NOT IN ('Vendido', 'Muerto') OR estado IS NULL)
            """, (fecha_inicio, fecha_inicio))
            
            activos_inicio = cursor.fetchone()[0] or 0
            
            # Muertes en el período
            cursor.execute("""
                SELECT COUNT(*) FROM animal
                WHERE fecha_muerte BETWEEN ? AND ?
                OR (estado = 'Muerto' AND fecha_ultima_actualizacion BETWEEN ? AND ?)
            """, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
            
            muertes_periodo = cursor.fetchone()[0] or 0
            
            # Nacimientos en el período
            cursor.execute("""
                SELECT COUNT(*) FROM animal
                WHERE fecha_nacimiento BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            nacimientos_periodo = cursor.fetchone()[0] or 0
            
            # Ventas en el período
            cursor.execute("""
                SELECT COUNT(*) FROM venta
                WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_fin))
            
            ventas_periodo = cursor.fetchone()[0] or 0
            
            # Tasa de mortalidad
            tasa_mortalidad = (muertes_periodo / activos_inicio * 100) if activos_inicio > 0 else 0
            
            return {
                'tasa_mortalidad_pct': round(tasa_mortalidad, 2),
                'animales_activos_inicio': activos_inicio,
                'muertes_periodo': muertes_periodo,
                'nacimientos_periodo': nacimientos_periodo,
                'ventas_periodo': ventas_periodo,
                'crecimiento_rebano_neto': nacimientos_periodo - muertes_periodo - ventas_periodo
            }
    
    def guardar_kpis_en_bd(
        self,
        año: int,
        mes: int,
        kpis: Dict[str, Any],
        categoria: str = "general"
    ) -> None:
        """
        Guarda los KPIs calculados en la tabla kpi_tracking.
        
        Args:
            año: Año del período
            mes: Mes del período (1-12)
            kpis: Diccionario con los KPIs calculados
            categoria: Categoría del KPI
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for nombre_kpi, valor in kpis.items():
                try:
                    # Verificar si ya existe
                    cursor.execute("""
                        SELECT id FROM kpi_tracking
                        WHERE año = ? AND mes = ? AND nombre_kpi = ?
                    """, (año, mes, nombre_kpi))
                    
                    if cursor.fetchone():
                        # Actualizar
                        cursor.execute("""
                            UPDATE kpi_tracking
                            SET valor = ?, categoria = ?, fecha_calculo = CURRENT_TIMESTAMP
                            WHERE año = ? AND mes = ? AND nombre_kpi = ?
                        """, (valor, categoria, año, mes, nombre_kpi))
                    else:
                        # Insertar
                        cursor.execute("""
                            INSERT INTO kpi_tracking (año, mes, nombre_kpi, valor, categoria)
                            VALUES (?, ?, ?, ?, ?)
                        """, (año, mes, nombre_kpi, valor, categoria))
                    
                except Exception as e:
                    self.logger.error(f"Error guardando KPI {nombre_kpi}: {e}")
            
            conn.commit()
        
        self.logger.info(f"KPIs guardados para {año}-{mes:02d}: {len(kpis)} indicadores")
    
    def obtener_tendencia_kpi(
        self,
        nombre_kpi: str,
        meses_atras: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la tendencia histórica de un KPI.
        
        Args:
            nombre_kpi: Nombre del KPI a consultar
            meses_atras: Número de meses hacia atrás a consultar
        
        Returns:
            Lista de diccionarios con (año, mes, valor)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT año, mes, valor, fecha_calculo
                FROM kpi_tracking
                WHERE nombre_kpi = ?
                ORDER BY año DESC, mes DESC
                LIMIT ?
            """, (nombre_kpi, meses_atras))
            
            rows = cursor.fetchall()
            
            tendencia = []
            for row in rows:
                tendencia.append({
                    'año': row[0],
                    'mes': row[1],
                    'valor': row[2],
                    'fecha_calculo': row[3],
                    'periodo': f"{row[0]}-{row[1]:02d}"
                })
            
            return tendencia


# Singleton
_kpi_calculator_instance: Optional[KPICalculatorService] = None


def get_kpi_calculator() -> KPICalculatorService:
    """Obtiene la instancia singleton del calculador de KPIs"""
    global _kpi_calculator_instance
    if _kpi_calculator_instance is None:
        _kpi_calculator_instance = KPICalculatorService()
    return _kpi_calculator_instance
