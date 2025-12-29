"""
╔══════════════════════════════════════════════════════════════════════════╗
║        SERVICIO DE MÉTRICAS DEL SISTEMA - FASE 9                         ║
╚══════════════════════════════════════════════════════════════════════════╝

Recolecta y persiste métricas internas del sistema para observabilidad.

Métricas registradas:
1. Tiempos de ejecución (detectores AI, cálculos KPI, snapshots)
2. Uso de cache (hits, misses, tasa de acierto)
3. Tamaño de base de datos
4. Cantidad de alertas activas
5. Ejecución de cierre mensual

Persistencia:
- Tabla system_metrics con timestamps
- Histórico completo para análisis de tendencias
- Queries optimizadas para dashboards

Uso:
    metrics_service = get_system_metrics_service()
    metrics_service.registrar_tiempo_ejecucion("detector_ai", 234.5)
    metrics_service.registrar_cache_hit("analytics_cache")
    metrics_service.obtener_metricas_ultimas(horas=24)
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import os

from src.database.database import get_db_connection

logger = logging.getLogger("SystemMetrics")


@dataclass
class MetricaRegistro:
    tipo: str  # detector_ai, kpi_calc, snapshot, cache_hit, cache_miss, db_size, alertas_activas
    valor: float
    unidad: str  # ms, bytes, count, pct
    componente: str  # qué componente generó la métrica
    timestamp: str
    detalles: Optional[Dict[str, Any]] = None


class SystemMetricsService:
    """Servicio centralizado de métricas de sistema."""

    def __init__(self) -> None:
        self.logger = logger
        self._asegurar_tabla_metricas()

    def _asegurar_tabla_metricas(self) -> None:
        """Crea tabla system_metrics si no existe."""
        try:
            with get_db_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT NOT NULL,  -- detector_ai, kpi_calc, snapshot, cache_hit, etc.
                        valor REAL NOT NULL,
                        unidad TEXT,  -- ms, bytes, count, pct
                        componente TEXT,  -- qué componente/módulo
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        detalles TEXT  -- JSON opcional con contexto extra
                    )
                    """
                )
                # Índice para búsquedas rápidas
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_metricas_tipo_ts ON system_metrics(tipo, timestamp)"
                )
                conn.commit()
                self.logger.info("✓ Tabla system_metrics verificada/creada")
        except Exception as e:
            self.logger.warning(f"No se pudo crear tabla system_metrics: {e}")

    def registrar_tiempo_ejecucion(
        self,
        componente: str,
        tiempo_ms: float,
        detalles: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra tiempo de ejecución de un componente.

        Args:
            componente: Nombre del componente (ej: "detector_ai", "kpi_produccion")
            tiempo_ms: Tiempo en milisegundos
            detalles: Dict opcional con contexto (ej: {"periodo": "2025-01"})

        Returns:
            True si se registró, False si falló
        """
        return self._registrar_metrica(
            tipo="tiempo_ejecucion",
            valor=tiempo_ms,
            unidad="ms",
            componente=componente,
            detalles=detalles,
        )

    def registrar_cache_hit(
        self,
        cache_name: str,
        clave: Optional[str] = None,
        tiempo_recuperacion_ms: Optional[float] = None
    ) -> bool:
        """
        Registra un hit de cache.

        Args:
            cache_name: Nombre del cache (ej: "analytics_cache")
            clave: Clave accedida (opcional)
            tiempo_recuperacion_ms: Tiempo tomado (opcional)

        Returns:
            True si se registró
        """
        return self._registrar_metrica(
            tipo="cache_hit",
            valor=1.0,
            unidad="count",
            componente=cache_name,
            detalles={"clave": clave, "tiempo_ms": tiempo_recuperacion_ms},
        )

    def registrar_cache_miss(
        self,
        cache_name: str,
        clave: Optional[str] = None
    ) -> bool:
        """
        Registra un miss de cache.

        Args:
            cache_name: Nombre del cache
            clave: Clave accedida (opcional)

        Returns:
            True si se registró
        """
        return self._registrar_metrica(
            tipo="cache_miss",
            valor=1.0,
            unidad="count",
            componente=cache_name,
            detalles={"clave": clave},
        )

    def registrar_tamaño_bd(self, tamaño_bytes: int) -> bool:
        """
        Registra tamaño actual de la base de datos.

        Args:
            tamaño_bytes: Tamaño en bytes

        Returns:
            True si se registró
        """
        return self._registrar_metrica(
            tipo="db_size",
            valor=float(tamaño_bytes),
            unidad="bytes",
            componente="database",
        )

    def registrar_alertas_activas(self, cantidad: int) -> bool:
        """
        Registra cantidad de alertas activas.

        Args:
            cantidad: Número de alertas activas

        Returns:
            True si se registró
        """
        return self._registrar_metrica(
            tipo="alertas_activas",
            valor=float(cantidad),
            unidad="count",
            componente="alertas",
        )

    def obtener_metricas_ultimas(
        self,
        horas: int = 24,
        tipo: Optional[str] = None,
        componente: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene métricas de las últimas N horas.

        Args:
            horas: Horas hacia atrás
            tipo: Filtrar por tipo (opcional)
            componente: Filtrar por componente (opcional)

        Returns:
            Lista de métricas
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT id, tipo, valor, unidad, componente, timestamp, detalles
                    FROM system_metrics
                    WHERE timestamp >= datetime('now', ?)
                """
                params = [f"-{horas} hours"]

                if tipo:
                    query += " AND tipo = ?"
                    params.append(tipo)

                if componente:
                    query += " AND componente = ?"
                    params.append(componente)

                query += " ORDER BY timestamp DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [
                    {
                        "id": row[0],
                        "tipo": row[1],
                        "valor": row[2],
                        "unidad": row[3],
                        "componente": row[4],
                        "timestamp": row[5],
                        "detalles": row[6],
                    }
                    for row in rows
                ]
        except Exception as e:
            self.logger.warning(f"Error obteniendo métricas: {e}")
            return []

    def obtener_estadisticas_componente(
        self,
        componente: str,
        horas: int = 24
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas agregadas de un componente.

        Args:
            componente: Nombre del componente
            horas: Horas hacia atrás

        Returns:
            Diccionario con media, min, max, count
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as count,
                        AVG(valor) as promedio,
                        MIN(valor) as minimo,
                        MAX(valor) as maximo,
                        STDDEV(valor) as desv_std
                    FROM system_metrics
                    WHERE componente = ? AND timestamp >= datetime('now', ?)
                    """,
                    (componente, f"-{horas} hours"),
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "componente": componente,
                        "count": row[0] or 0,
                        "promedio": row[1] or 0,
                        "minimo": row[2] or 0,
                        "maximo": row[3] or 0,
                        "desv_std": row[4] or 0,
                    }
                return {"componente": componente, "count": 0}
        except Exception as e:
            self.logger.warning(f"Error calculando estadísticas: {e}")
            return {"componente": componente, "count": 0}

    def obtener_tasa_cache(
        self,
        cache_name: str,
        horas: int = 24
    ) -> Dict[str, Any]:
        """
        Calcula tasa de acierto de un cache.

        Args:
            cache_name: Nombre del cache
            horas: Horas hacia atrás

        Returns:
            {hits, misses, tasa_acierto_pct}
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT 
                        SUM(CASE WHEN tipo = 'cache_hit' THEN 1 ELSE 0 END) as hits,
                        SUM(CASE WHEN tipo = 'cache_miss' THEN 1 ELSE 0 END) as misses
                    FROM system_metrics
                    WHERE componente = ? AND timestamp >= datetime('now', ?)
                    """,
                    (cache_name, f"-{horas} hours"),
                )

                row = cursor.fetchone()
                hits = row[0] or 0
                misses = row[1] or 0
                total = hits + misses

                tasa = (hits / total * 100) if total > 0 else 0

                return {
                    "cache": cache_name,
                    "hits": hits,
                    "misses": misses,
                    "total": total,
                    "tasa_acierto_pct": round(tasa, 2),
                }
        except Exception as e:
            self.logger.warning(f"Error calculando tasa cache: {e}")
            return {"cache": cache_name, "hits": 0, "misses": 0, "tasa_acierto_pct": 0}

    def obtener_tamaño_bd_actual(self) -> int:
        """
        Obtiene tamaño actual de la base de datos en bytes.

        Returns:
            Tamaño en bytes
        """
        try:
            db_path = os.path.expanduser("~/AppData/Local/FincaFacil/fincafacil.db")
            if not os.path.exists(db_path):
                # Intentar ruta alternativa
                db_path = "database/fincafacil.db"

            if os.path.exists(db_path):
                return os.path.getsize(db_path)
            return 0
        except Exception as e:
            self.logger.warning(f"Error obteniendo tamaño BD: {e}")
            return 0

    def limpiar_metricas_antiguas(self, dias: int = 30) -> int:
        """
        Elimina métricas más antiguas que N días.

        Args:
            dias: Días hacia atrás a mantener

        Returns:
            Cantidad de registros eliminados
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f"DELETE FROM system_metrics WHERE timestamp < datetime('now', '-{dias} days')"
                )
                eliminadas = cursor.rowcount
                conn.commit()

                self.logger.info(f"Métricas antiguas eliminadas: {eliminadas}")
                return eliminadas
        except Exception as e:
            self.logger.warning(f"Error limpiando métricas antiguas: {e}")
            return 0

    # ==================== PRIVADOS ====================

    def _registrar_metrica(
        self,
        tipo: str,
        valor: float,
        unidad: str,
        componente: str,
        detalles: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Registra una métrica en la BD."""
        try:
            import json

            detalles_json = json.dumps(detalles) if detalles else None

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO system_metrics (tipo, valor, unidad, componente, detalles)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (tipo, valor, unidad, componente, detalles_json),
                )
                conn.commit()
                return True
        except Exception as e:
            self.logger.debug(f"Error registrando métrica {tipo}/{componente}: {e}")
            return False


# Singleton
_system_metrics_service: Optional[SystemMetricsService] = None


def get_system_metrics_service() -> SystemMetricsService:
    """Obtiene la instancia singleton del servicio de métricas del sistema."""
    global _system_metrics_service
    if _system_metrics_service is None:
        _system_metrics_service = SystemMetricsService()
    return _system_metrics_service
