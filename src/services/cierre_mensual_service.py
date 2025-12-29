"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SERVICIO DE CIERRE MENSUAL - FASE 3                   ║
╚══════════════════════════════════════════════════════════════════════════╝

Gestiona el cierre operativo mensual y almacena snapshots históricos.
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
import logging
from src.core.audit_service import log_event
from src.core.backup_service import on_monthly_close
from src.database.database import get_db_connection
from src.services.reportes_service import reportes_service
from src.services.data_lock_service import get_data_lock_service
from src.services.bi_snapshot_service import get_bi_snapshot_service
from src.services.analytics_cache_service import get_analytics_cache
from src.services.ai_anomaly_detector import get_ai_anomaly_detector_service
from src.services.ai_pattern_detector import get_ai_pattern_detector_service
from src.services.system_metrics_service import get_system_metrics_service
from src.core.permission_decorators import require_permission, audit_action
from src.core.permissions_manager import PermissionEnum


class CierreMensualService:
    """
    Servicio de cierre mensual operativo.
    
    Funcionalidades:
        - Genera snapshot de métricas del mes
        - Almacena resumen en tabla resumen_mensual
        - Permite comparar con meses anteriores
        - NO bloquea el sistema (es informativo)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._verificar_tabla()
    
    def _verificar_tabla(self):
        """Crea la tabla resumen_mensual si no existe"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS resumen_mensual (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        año INTEGER NOT NULL,
                        mes INTEGER NOT NULL,
                        fecha_cierre TIMESTAMP NOT NULL,
                        
                        -- Animales
                        total_activos INTEGER DEFAULT 0,
                        gestantes INTEGER DEFAULT 0,
                        altas_mes INTEGER DEFAULT 0,
                        bajas_mes INTEGER DEFAULT 0,
                        
                        -- Producción
                        litros_totales REAL DEFAULT 0,
                        litros_promedio_dia REAL DEFAULT 0,
                        litros_promedio_vaca REAL DEFAULT 0,
                        vacas_productivas INTEGER DEFAULT 0,
                        
                        -- Reproducción
                        servicios_realizados INTEGER DEFAULT 0,
                        partos_mes INTEGER DEFAULT 0,
                        tasa_prenez REAL DEFAULT 0,
                        
                        -- Finanzas
                        ingresos_totales REAL DEFAULT 0,
                        ingresos_animales REAL DEFAULT 0,
                        ingresos_leche REAL DEFAULT 0,
                        costos_totales REAL DEFAULT 0,
                        costos_nomina REAL DEFAULT 0,
                        costos_tratamientos REAL DEFAULT 0,
                        costos_insumos REAL DEFAULT 0,
                        margen_bruto REAL DEFAULT 0,
                        margen_porcentaje REAL DEFAULT 0,
                        
                        -- Metadatos
                        observaciones TEXT,
                        usuario TEXT,
                        
                        UNIQUE(año, mes)
                    )
                """)
                
                conn.commit()
                self.logger.info("✓ Tabla resumen_mensual verificada/creada")
        
        except Exception as e:
            self.logger.error(f"Error verificando tabla resumen_mensual: {e}")
            raise
    
    @require_permission(PermissionEnum.CIERRE_REALIZAR)
    @audit_action("cierre_mensual", "REALIZAR")
    def realizar_cierre(self, año: int, mes: int, usuario: str = "Sistema",
                       observaciones: Optional[str] = None) -> Dict[str, Any]:
        """
        Realiza el cierre mensual de un período específico.
        
        Args:
            año: Año del cierre (ej: 2025)
            mes: Mes del cierre (1-12)
            usuario: Usuario que realiza el cierre
            observaciones: Observaciones opcionales
        
        Returns:
            Diccionario con el resumen guardado
        
        Raises:
            ValueError: Si el mes/año son inválidos
            Exception: Si ya existe un cierre para ese período
        """
        # Validaciones
        if not (1 <= mes <= 12):
            raise ValueError(f"Mes inválido: {mes}. Debe estar entre 1 y 12")
        
        if año < 2020 or año > datetime.now().year:
            raise ValueError(f"Año inválido: {año}")
        
        # Verificar si ya existe cierre
        if self.existe_cierre(año, mes):
            raise Exception(
                f"Ya existe un cierre para {año}-{mes:02d}. "
                "Use actualizar_cierre() para modificarlo."
            )
        
        self.logger.info(f"Iniciando cierre mensual: {año}-{mes:02d}")
        
        # Calcular fechas del mes
        fecha_inicio = date(año, mes, 1)
        if mes == 12:
            fecha_fin = date(año, 12, 31)
        else:
            from calendar import monthrange
            ultimo_dia = monthrange(año, mes)[1]
            fecha_fin = date(año, mes, ultimo_dia)
        
        # Generar reporte completo del mes
        reporte = reportes_service.generar_reporte(
            'completo',
            fecha_inicio,
            fecha_fin
        )
        
        # Extraer métricas de cada sección
        secciones = reporte.get('secciones', {})
        
        animales_data = secciones.get('animales', {}).get('totales', {})
        produccion_data = secciones.get('produccion', {}).get('datos', {})
        reproduccion_data = secciones.get('reproduccion', {}).get('totales', {})
        finanzas_data = secciones.get('finanzas', {}).get('datos', {})
        
        # Construir resumen
        resumen = {
            'año': año,
            'mes': mes,
            'fecha_cierre': datetime.now().isoformat(),
            
            # Animales
            'total_activos': animales_data.get('total_activos', 0),
            'gestantes': animales_data.get('gestantes', 0) if 'gestantes' in animales_data else 0,
            'altas_mes': animales_data.get('altas_periodo', 0),
            'bajas_mes': animales_data.get('bajas_periodo', 0),
            
            # Producción
            'litros_totales': produccion_data.get('produccion_periodo', {}).get('litros_totales', 0),
            'litros_promedio_dia': produccion_data.get('promedios', {}).get('promedio_litros_dia', 0),
            'litros_promedio_vaca': produccion_data.get('promedios', {}).get('promedio_litros_vaca', 0),
            'vacas_productivas': produccion_data.get('produccion_periodo', {}).get('vacas_productivas', 0),
            
            # Reproducción
            'servicios_realizados': reproduccion_data.get('servicios_realizados', 0),
            'partos_mes': reproduccion_data.get('partos_periodo', 0),
            'tasa_prenez': reproduccion_data.get('tasa_prenez_pct', 0),
            
            # Finanzas
            'ingresos_totales': finanzas_data.get('ingresos', {}).get('total', 0),
            'ingresos_animales': finanzas_data.get('ingresos', {}).get('ventas_animales', 0),
            'ingresos_leche': finanzas_data.get('ingresos', {}).get('ventas_leche', 0),
            'costos_totales': finanzas_data.get('costos', {}).get('total', 0),
            'costos_nomina': finanzas_data.get('costos', {}).get('nomina', 0),
            'costos_tratamientos': finanzas_data.get('costos', {}).get('tratamientos', 0),
            'costos_insumos': finanzas_data.get('costos', {}).get('insumos', 0),
            'margen_bruto': finanzas_data.get('margen', {}).get('valor', 0),
            'margen_porcentaje': finanzas_data.get('margen', {}).get('porcentaje', 0),
            
            # Metadatos
            'observaciones': observaciones,
            'usuario': usuario
        }
        
        # Guardar en BD
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO resumen_mensual (
                    año, mes, fecha_cierre,
                    total_activos, gestantes, altas_mes, bajas_mes,
                    litros_totales, litros_promedio_dia, litros_promedio_vaca, vacas_productivas,
                    servicios_realizados, partos_mes, tasa_prenez,
                    ingresos_totales, ingresos_animales, ingresos_leche,
                    costos_totales, costos_nomina, costos_tratamientos, costos_insumos,
                    margen_bruto, margen_porcentaje,
                    observaciones, usuario
                ) VALUES (
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    ?, ?
                )
            """, (
                resumen['año'], resumen['mes'], resumen['fecha_cierre'],
                resumen['total_activos'], resumen['gestantes'], resumen['altas_mes'], resumen['bajas_mes'],
                resumen['litros_totales'], resumen['litros_promedio_dia'], 
                resumen['litros_promedio_vaca'], resumen['vacas_productivas'],
                resumen['servicios_realizados'], resumen['partos_mes'], resumen['tasa_prenez'],
                resumen['ingresos_totales'], resumen['ingresos_animales'], resumen['ingresos_leche'],
                resumen['costos_totales'], resumen['costos_nomina'], 
                resumen['costos_tratamientos'], resumen['costos_insumos'],
                resumen['margen_bruto'], resumen['margen_porcentaje'],
                resumen['observaciones'], resumen['usuario']
            ))
            
            resumen['id'] = cursor.lastrowid
            conn.commit()
        
        # Bloquear ediciones del período cerrado
        lock_service = get_data_lock_service()
        lock_service.block_data(año, mes, "ventas")
        lock_service.block_data(año, mes, "gastos")
        lock_service.block_data(año, mes, "nomina")
        lock_service.block_data(año, mes, "produccion")
        
        self.logger.info(f"✓ Datos del período {año}-{mes:02d} bloqueados para edición")
        
        # Generar snapshot analítico para BI (NUEVA FASE 1)
        try:
            snapshot_service = get_bi_snapshot_service()
            snapshot = snapshot_service.generar_snapshot(año, mes, usuario)
            
            # Invalidar cache de análisis (nuevos KPIs disponibles)
            cache_service = get_analytics_cache()
            cache_service.invalidar_si_nuevos_kpis(año, mes)
            
            self.logger.info(f"✓ Snapshot analítico generado para {año}-{mes:02d}")
            self.logger.info(f"  - KPIs capturados: {len(snapshot.get('kpis', {}))}")
            self.logger.info(f"  - Alertas registradas: {snapshot.get('alertas', {}).get('total', 0)}")
        except Exception as e:
            self.logger.error(f"Error generando snapshot BI: {e}")
            # No romper el cierre por error en snapshots
        
        # Ejecutar detectores AI (FASE 3) tras generar snapshot e invalidar cache
        try:
            anomaly_service = get_ai_anomaly_detector_service()
            pattern_service = get_ai_pattern_detector_service()
            anomalies = anomaly_service.evaluar_anomalias(usuario_id=None, incluir_alertas=True)
            patterns = pattern_service.detectar_patrones(usuario_id=None, incluir_alertas=True)
            self.logger.info(
                f"✓ Detectores AI ejecutados: {len(anomalies)} anomalías, {len(patterns)} patrones"
            )
            try:
                log_event(
                    usuario=usuario,
                    modulo="AI",
                    accion="EJECUCION_POST_CIERRE",
                    entidad=f"{año}-{mes:02d}",
                    resultado="OK",
                    mensaje=f"{len(anomalies)} anomalías; {len(patterns)} patrones"
                )
            except Exception:
                pass
        except Exception as e:
            self.logger.warning(f"Detectores AI no ejecutados: {e}")
                # Registrar duración total del cierre
        try:
            metrics_service = get_system_metrics_service()
            # El tiempo total del cierre se aproxima por auditoría
            # Aquí registramos solo la métrica de BD resultante
            import os
            db_size = os.path.getsize(os.path.join(
                os.path.dirname(__file__), '..', '..', 'database', 'fincafacil.db'
            )) if os.path.exists(os.path.join(
                os.path.dirname(__file__), '..', '..', 'database', 'fincafacil.db'
            )) else 0
            if db_size > 0:
                metrics_service.registrar_tamaño_bd(db_size)
        except Exception:
            pass  # No bloquear cierre por error de métricas
                # Auditoría y backup
        try:
            log_event(usuario=usuario, modulo="cierre_mensual", accion="CIERRE", entidad=f"{año}-{mes:02d}", resultado="OK", mensaje="Cierre mensual registrado")
        except Exception:
            pass
        try:
            on_monthly_close(usuario)
        except Exception:
            pass
        
        self.logger.info(
            f"✓ Cierre mensual completado: {año}-{mes:02d} "
            f"(ID: {resumen['id']})"
        )
        
        return resumen
    
    def existe_cierre(self, año: int, mes: int) -> bool:
        """Verifica si existe un cierre para el período"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM resumen_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            return cursor.fetchone()[0] > 0
    
    def obtener_cierre(self, año: int, mes: int) -> Optional[Dict[str, Any]]:
        """Obtiene el cierre de un mes específico"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM resumen_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Convertir a diccionario
            columnas = [desc[0] for desc in cursor.description]
            return dict(zip(columnas, row))
    
    def comparar_meses(self, año1: int, mes1: int, 
                       año2: int, mes2: int) -> Dict[str, Any]:
        """
        Compara dos cierres mensuales.
        
        Returns:
            Diccionario con variaciones entre ambos períodos
        """
        cierre1 = self.obtener_cierre(año1, mes1)
        cierre2 = self.obtener_cierre(año2, mes2)
        
        if not cierre1 or not cierre2:
            raise ValueError("Uno o ambos cierres no existen")
        
        def calcular_variacion(valor1, valor2):
            """Calcula variación porcentual"""
            if valor1 == 0:
                return 0 if valor2 == 0 else 100
            return ((valor2 - valor1) / valor1) * 100
        
        return {
            'periodo1': f"{año1}-{mes1:02d}",
            'periodo2': f"{año2}-{mes2:02d}",
            'variaciones': {
                'ingresos': {
                    'valor_anterior': cierre1['ingresos_totales'],
                    'valor_actual': cierre2['ingresos_totales'],
                    'variacion_pct': calcular_variacion(
                        cierre1['ingresos_totales'],
                        cierre2['ingresos_totales']
                    )
                },
                'margen': {
                    'valor_anterior': cierre1['margen_bruto'],
                    'valor_actual': cierre2['margen_bruto'],
                    'variacion_pct': calcular_variacion(
                        cierre1['margen_bruto'],
                        cierre2['margen_bruto']
                    )
                },
                'produccion': {
                    'valor_anterior': cierre1['litros_totales'],
                    'valor_actual': cierre2['litros_totales'],
                    'variacion_pct': calcular_variacion(
                        cierre1['litros_totales'],
                        cierre2['litros_totales']
                    )
                }
            }
        }
    
    def listar_cierres(self, año: Optional[int] = None) -> list:
        """Lista todos los cierres (opcionalmente filtrados por año)"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if año:
                cursor.execute("""
                    SELECT año, mes, fecha_cierre, margen_bruto, margen_porcentaje
                    FROM resumen_mensual
                    WHERE año = ?
                    ORDER BY año DESC, mes DESC
                """, (año,))
            else:
                cursor.execute("""
                    SELECT año, mes, fecha_cierre, margen_bruto, margen_porcentaje
                    FROM resumen_mensual
                    ORDER BY año DESC, mes DESC
                """)
            
            return [
                {
                    'año': row[0],
                    'mes': row[1],
                    'fecha_cierre': row[2],
                    'margen_bruto': row[3],
                    'margen_porcentaje': row[4]
                }
                for row in cursor.fetchall()
            ]


# Singleton
cierre_mensual_service = CierreMensualService()
