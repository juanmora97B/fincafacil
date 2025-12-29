"""
╔══════════════════════════════════════════════════════════════════════════╗
║                 SERVICIO DE REGLAS DE ALERTAS - FASE CONSOLIDACIÓN       ║
╚══════════════════════════════════════════════════════════════════════════╝

Define y evalúa reglas heurísticas para generar alertas automáticas.

Reglas implementadas:
1. Gastos anormales (> 130% del promedio 6 meses)
2. Producción baja (< 80% del promedio 6 meses)
3. Inventario bajo de insumos (< umbral crítico)
4. Mortalidad elevada (> umbral permitido)
5. Tasa de preñez baja (< umbral esperado)
6. Animales sin revisión veterinaria (> 180 días)
7. Empleados sin pago reciente (> 45 días)
"""

from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List, Tuple
import logging
from src.database.database import get_db_connection
from src.services.data_quality_service import get_data_quality_service
from src.services.system_metrics_service import get_system_metrics_service

logger = logging.getLogger("alert_rules")


class AlertRulesService:
    """Servicio para evaluar reglas de alertas"""
    
    # Umbrales configurables
    UMBRAL_GASTO_ANORMAL_PCT = 130  # % sobre promedio
    UMBRAL_PRODUCCION_BAJA_PCT = 80  # % bajo promedio
    UMBRAL_MORTALIDAD_PCT = 5  # % máximo permitido mensual
    UMBRAL_PRENEZ_PCT = 60  # % mínimo esperado
    UMBRAL_DIAS_SIN_REVISION = 180  # días
    UMBRAL_DIAS_SIN_PAGO = 45  # días
    MESES_PROMEDIO = 6  # meses para calcular promedios
    
    def __init__(self):
        self.logger = logger
        self._asegurar_tabla_alertas()
    
    def _asegurar_tabla_alertas(self):
        """Asegura que la tabla alertas existe"""
        try:
            with get_db_connection() as conn:
                conn.execute("SELECT 1 FROM alertas LIMIT 1")
        except Exception as e:
            self.logger.warning(f"Tabla alertas no disponible: {e}")
    
    def evaluar_todas_reglas(
        self,
        fecha_referencia: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Evalúa todas las reglas de alerta configuradas.
        
        Args:
            fecha_referencia: Fecha de referencia (por defecto hoy)
        
        Returns:
            Lista de alertas generadas
        """
        if fecha_referencia is None:
            fecha_referencia = date.today()
        
        alertas = []
        
        # Evaluar cada regla
        alertas.extend(self._evaluar_gastos_anormales(fecha_referencia))
        alertas.extend(self._evaluar_produccion_baja(fecha_referencia))
        alertas.extend(self._evaluar_mortalidad_elevada(fecha_referencia))
        alertas.extend(self._evaluar_tasa_prenez_baja(fecha_referencia))
        alertas.extend(self._evaluar_animales_sin_revision(fecha_referencia))
        alertas.extend(self._evaluar_empleados_sin_pago(fecha_referencia))
        
        # Evaluar calidad de datos (alertas técnicas)
        alertas.extend(self._evaluar_calidad_datos(fecha_referencia))
        
        self.logger.info(f"Evaluación completada: {len(alertas)} alertas generadas")
        return alertas
    
    def _evaluar_gastos_anormales(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Detecta gastos anormalmente altos comparados con promedio histórico"""
        alertas = []
        
        # Período actual (mes actual)
        mes_actual = fecha_ref.replace(day=1)
        mes_anterior = (mes_actual - timedelta(days=1)).replace(day=1)
        
        # Calcular promedio de últimos 6 meses
        fecha_inicio_promedio = mes_actual - timedelta(days=180)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Promedio histórico por categoría
            cursor.execute("""
                SELECT 
                    categoria,
                    AVG(total_mes) as promedio
                FROM (
                    SELECT 
                        categoria,
                        strftime('%Y-%m', fecha) as mes,
                        SUM(monto) as total_mes
                    FROM gasto
                    WHERE fecha BETWEEN ? AND ?
                    AND categoria IS NOT NULL
                    GROUP BY categoria, mes
                )
                GROUP BY categoria
            """, (fecha_inicio_promedio, mes_anterior))
            
            promedios = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Gasto del mes actual por categoría
            cursor.execute("""
                SELECT 
                    categoria,
                    SUM(monto) as total_actual
                FROM gasto
                WHERE fecha >= ? AND fecha <= ?
                AND categoria IS NOT NULL
                GROUP BY categoria
            """, (mes_actual, fecha_ref))
            
            for row in cursor.fetchall():
                categoria = row[0]
                total_actual = row[1]
                
                promedio = promedios.get(categoria, 0)
                if promedio == 0:
                    continue
                
                porcentaje = (total_actual / promedio) * 100
                
                if porcentaje > self.UMBRAL_GASTO_ANORMAL_PCT:
                    alertas.append({
                        'tipo': 'gasto_anormal',
                        'prioridad': 'media' if porcentaje < 150 else 'alta',
                        'titulo': f"Gasto elevado en {categoria}",
                        'descripcion': (
                            f"Los gastos en {categoria} son {porcentaje:.0f}% del promedio histórico. "
                            f"Actual: ${total_actual:,.0f} vs Promedio: ${promedio:,.0f}"
                        ),
                        'entidad_tipo': 'categoria_gasto',
                        'entidad_id': categoria,
                        'valor_actual': total_actual,
                        'valor_referencia': promedio
                    })
        
        return alertas
    
    def _evaluar_produccion_baja(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Detecta producción lechera baja comparada con promedio"""
        alertas = []
        
        # Últimos 30 días
        fecha_inicio = fecha_ref - timedelta(days=30)
        
        # Últimos 180 días para promedio
        fecha_inicio_promedio = fecha_ref - timedelta(days=180)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Promedio diario histórico
            cursor.execute("""
                SELECT AVG(litros_dia) FROM (
                    SELECT fecha, SUM(cantidad_litros) as litros_dia
                    FROM produccion_leche
                    WHERE fecha BETWEEN ? AND ?
                    GROUP BY fecha
                )
            """, (fecha_inicio_promedio, fecha_inicio - timedelta(days=1)))
            
            promedio_historico = cursor.fetchone()[0] or 0
            
            if promedio_historico == 0:
                return alertas
            
            # Promedio últimos 30 días
            cursor.execute("""
                SELECT AVG(litros_dia) FROM (
                    SELECT fecha, SUM(cantidad_litros) as litros_dia
                    FROM produccion_leche
                    WHERE fecha BETWEEN ? AND ?
                    GROUP BY fecha
                )
            """, (fecha_inicio, fecha_ref))
            
            promedio_actual = cursor.fetchone()[0] or 0
            
            porcentaje = (promedio_actual / promedio_historico) * 100 if promedio_historico > 0 else 100
            
            if porcentaje < self.UMBRAL_PRODUCCION_BAJA_PCT:
                alertas.append({
                    'tipo': 'produccion_baja',
                    'prioridad': 'alta' if porcentaje < 70 else 'media',
                    'titulo': "Producción lechera por debajo del promedio",
                    'descripcion': (
                        f"La producción promedio diaria es {porcentaje:.0f}% del promedio histórico. "
                        f"Actual: {promedio_actual:.1f} L/día vs Promedio: {promedio_historico:.1f} L/día"
                    ),
                    'entidad_tipo': 'produccion',
                    'entidad_id': None,
                    'valor_actual': promedio_actual,
                    'valor_referencia': promedio_historico
                })
        
        return alertas
    
    def _evaluar_mortalidad_elevada(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Detecta mortalidad animal elevada"""
        alertas = []
        
        # Mes actual
        mes_inicio = fecha_ref.replace(day=1)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Animales activos al inicio del mes
            cursor.execute("""
                SELECT COUNT(*) FROM animal
                WHERE fecha_nacimiento < ?
                AND (fecha_muerte IS NULL OR fecha_muerte >= ?)
                AND (estado NOT IN ('Vendido', 'Muerto') OR estado IS NULL)
            """, (mes_inicio, mes_inicio))
            
            activos_inicio = cursor.fetchone()[0] or 0
            
            if activos_inicio == 0:
                return alertas
            
            # Muertes en el mes
            cursor.execute("""
                SELECT COUNT(*) FROM animal
                WHERE fecha_muerte BETWEEN ? AND ?
                OR (estado = 'Muerto' AND fecha_ultima_actualizacion BETWEEN ? AND ?)
            """, (mes_inicio, fecha_ref, mes_inicio, fecha_ref))
            
            muertes_mes = cursor.fetchone()[0] or 0
            
            tasa_mortalidad = (muertes_mes / activos_inicio) * 100
            
            if tasa_mortalidad > self.UMBRAL_MORTALIDAD_PCT:
                alertas.append({
                    'tipo': 'mortalidad_elevada',
                    'prioridad': 'alta' if tasa_mortalidad > 10 else 'media',
                    'titulo': "Tasa de mortalidad elevada",
                    'descripcion': (
                        f"La mortalidad en el mes actual es {tasa_mortalidad:.1f}% "
                        f"({muertes_mes} de {activos_inicio} animales). "
                        f"Umbral máximo: {self.UMBRAL_MORTALIDAD_PCT}%"
                    ),
                    'entidad_tipo': 'animales',
                    'entidad_id': None,
                    'valor_actual': tasa_mortalidad,
                    'valor_referencia': self.UMBRAL_MORTALIDAD_PCT
                })
        
        return alertas
    
    def _evaluar_tasa_prenez_baja(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Detecta tasa de preñez baja"""
        alertas = []
        
        # Últimos 90 días
        fecha_inicio = fecha_ref - timedelta(days=90)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as servicios_totales,
                    SUM(CASE WHEN confirmacion_prenez = 'Positivo' THEN 1 ELSE 0 END) as exitosos
                FROM servicio
                WHERE fecha BETWEEN ? AND ?
            """, (fecha_inicio, fecha_ref))
            
            row = cursor.fetchone()
            servicios_totales = row[0] if row else 0
            exitosos = row[1] if row else 0
            
            if servicios_totales < 5:  # Mínimo de servicios para alertar
                return alertas
            
            tasa_prenez = (exitosos / servicios_totales) * 100 if servicios_totales > 0 else 0
            
            if tasa_prenez < self.UMBRAL_PRENEZ_PCT:
                alertas.append({
                    'tipo': 'tasa_prenez_baja',
                    'prioridad': 'media' if tasa_prenez > 50 else 'alta',
                    'titulo': "Tasa de preñez por debajo del objetivo",
                    'descripcion': (
                        f"La tasa de preñez en los últimos 90 días es {tasa_prenez:.0f}% "
                        f"({exitosos} de {servicios_totales} servicios). "
                        f"Objetivo mínimo: {self.UMBRAL_PRENEZ_PCT}%"
                    ),
                    'entidad_tipo': 'reproduccion',
                    'entidad_id': None,
                    'valor_actual': tasa_prenez,
                    'valor_referencia': self.UMBRAL_PRENEZ_PCT
                })
        
        return alertas
    
    def _evaluar_animales_sin_revision(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Detecta animales sin revisión veterinaria reciente"""
        alertas = []
        
        fecha_limite = fecha_ref - timedelta(days=self.UMBRAL_DIAS_SIN_REVISION)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    a.id,
                    a.codigo,
                    a.nombre,
                    MAX(t.fecha) as ultima_revision
                FROM animal a
                LEFT JOIN tratamiento t ON a.id = t.animal_id
                WHERE a.estado = 'Activo'
                GROUP BY a.id, a.codigo, a.nombre
                HAVING ultima_revision IS NULL OR ultima_revision < ?
            """, (fecha_limite,))
            
            animales_sin_revision = cursor.fetchall()
            
            if len(animales_sin_revision) > 5:  # Alertar si son más de 5
                alertas.append({
                    'tipo': 'animales_sin_revision',
                    'prioridad': 'baja',
                    'titulo': f"{len(animales_sin_revision)} animales sin revisión veterinaria",
                    'descripcion': (
                        f"Hay {len(animales_sin_revision)} animales sin revisión en los últimos "
                        f"{self.UMBRAL_DIAS_SIN_REVISION} días. "
                        f"Se recomienda programar revisiones."
                    ),
                    'entidad_tipo': 'animales',
                    'entidad_id': None,
                    'valor_actual': len(animales_sin_revision),
                    'valor_referencia': 0
                })
        
        return alertas
    
    def _evaluar_calidad_datos(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Evalúa calidad de datos del período actual y genera alertas técnicas"""
        alertas = []
        
        try:
            # Obtener período actual
            año = fecha_ref.year
            mes = fecha_ref.month
            
            # Evaluar calidad
            quality_service = get_data_quality_service()
            reporte = quality_service.evaluar_calidad_periodo(año, mes)
            
            # Si calidad baja o media, generar alerta técnica
            if reporte.calidad in ("BAJA", "MEDIA"):
                prioridad = "alta" if reporte.calidad == "BAJA" else "media"
                alertas.append({
                    'tipo': f'calidad_{reporte.calidad.lower()}',
                    'prioridad': prioridad,
                    'titulo': f"Calidad de datos {reporte.calidad}",
                    'descripcion': (
                        f"Período {reporte.periodo}: score {reporte.score}/100. "
                        f"Problemas: {', '.join(reporte.problemas[:3])}{'...' if len(reporte.problemas) > 3 else ''}"
                    ),
                    'entidad_tipo': 'calidad_datos',
                    'entidad_id': reporte.periodo,
                    'valor_actual': reporte.score,
                    'valor_referencia': 85
                })
        except Exception as e:
            self.logger.warning(f"Error evaluando calidad de datos: {e}")
        
        return alertas
    
    def _evaluar_empleados_sin_pago(self, fecha_ref: date) -> List[Dict[str, Any]]:
        """Detecta empleados activos sin pagos recientes"""
        alertas = []
        
        fecha_limite = fecha_ref - timedelta(days=self.UMBRAL_DIAS_SIN_PAGO)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    e.codigo,
                    e.nombres || ' ' || e.apellidos as nombre,
                    MAX(p.fecha_pago) as ultimo_pago
                FROM empleado e
                LEFT JOIN pago_nomina p ON e.codigo = p.codigo_empleado
                WHERE e.estado_actual = 'Activo' OR e.estado_actual IS NULL
                GROUP BY e.codigo, nombre
                HAVING ultimo_pago IS NULL OR ultimo_pago < ?
            """, (fecha_limite,))
            
            empleados_sin_pago = cursor.fetchall()
            
            if len(empleados_sin_pago) > 0:
                alertas.append({
                    'tipo': 'empleados_sin_pago',
                    'prioridad': 'alta' if len(empleados_sin_pago) > 3 else 'media',
                    'titulo': f"{len(empleados_sin_pago)} empleados sin pago reciente",
                    'descripcion': (
                        f"Hay {len(empleados_sin_pago)} empleados activos sin registro de pago "
                        f"en los últimos {self.UMBRAL_DIAS_SIN_PAGO} días. "
                        f"Verificar nómina."
                    ),
                    'entidad_tipo': 'nomina',
                    'entidad_id': None,
                    'valor_actual': len(empleados_sin_pago),
                    'valor_referencia': 0
                })
        
        return alertas
    
    def guardar_alertas_en_bd(
        self,
        alertas: List[Dict[str, Any]],
        usuario: str = "Sistema"
    ) -> int:
        """
        Guarda las alertas generadas en la base de datos.
        
        Args:
            alertas: Lista de alertas a guardar
            usuario: Usuario que generó las alertas
        
        Returns:
            Número de alertas guardadas
        """
        guardadas = 0
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for alerta in alertas:
                try:
                    # Verificar si ya existe alerta similar reciente (últimos 7 días)
                    cursor.execute("""
                        SELECT id FROM alertas
                        WHERE tipo = ?
                        AND entidad_tipo = ?
                        AND fecha_deteccion > date('now', '-7 days')
                        AND estado = 'activa'
                    """, (alerta['tipo'], alerta['entidad_tipo']))
                    
                    if cursor.fetchone():
                        self.logger.debug(f"Alerta duplicada ignorada: {alerta['tipo']}")
                        continue
                    
                    # Insertar nueva alerta
                    cursor.execute("""
                        INSERT INTO alertas (
                            tipo, prioridad, titulo, descripcion,
                            entidad_tipo, entidad_id, valor_actual, valor_referencia
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        alerta['tipo'],
                        alerta['prioridad'],
                        alerta['titulo'],
                        alerta['descripcion'],
                        alerta.get('entidad_tipo'),
                        alerta.get('entidad_id'),
                        alerta.get('valor_actual'),
                        alerta.get('valor_referencia')
                    ))
                    
                    guardadas += 1
                    
                except Exception as e:
                    self.logger.error(f"Error guardando alerta {alerta['tipo']}: {e}")
            
            conn.commit()
        
        # Registrar métrica de alertas activas
        try:
            metrics_service = get_system_metrics_service()
            activas = self.obtener_alertas_activas()
            metrics_service.registrar_alertas_activas(len(activas) if activas else 0)
        except Exception:
            pass  # No bloquear alertas por error de métricas
        
        self.logger.info(f"{guardadas} alertas guardadas en BD")
        return guardadas
    
    def obtener_alertas_activas(
        self,
        prioridad: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las alertas activas de la base de datos.
        
        Args:
            prioridad: Filtrar por prioridad (alta, media, baja)
        
        Returns:
            Lista de alertas activas
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, tipo, prioridad, titulo, descripcion,
                    entidad_tipo, entidad_id, valor_actual, valor_referencia,
                    fecha_deteccion, estado
                FROM alertas
                WHERE estado = 'activa'
            """
            
            params = []
            if prioridad:
                query += " AND prioridad = ?"
                params.append(prioridad)
            
            query += " ORDER BY prioridad DESC, fecha_deteccion DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            alertas = []
            for row in rows:
                alertas.append({
                    'id': row[0],
                    'tipo': row[1],
                    'prioridad': row[2],
                    'titulo': row[3],
                    'descripcion': row[4],
                    'entidad_tipo': row[5],
                    'entidad_id': row[6],
                    'valor_actual': row[7],
                    'valor_referencia': row[8],
                    'fecha_deteccion': row[9],
                    'estado': row[10]
                })
            
            return alertas


# Singleton
_alert_rules_instance: Optional[AlertRulesService] = None


def get_alert_rules_service() -> AlertRulesService:
    """Obtiene la instancia singleton del servicio de reglas de alertas"""
    global _alert_rules_instance
    if _alert_rules_instance is None:
        _alert_rules_instance = AlertRulesService()
    return _alert_rules_instance
