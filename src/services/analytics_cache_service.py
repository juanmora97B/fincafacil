"""
╔══════════════════════════════════════════════════════════════════════════╗
║       SERVICIO DE CACHE ANALÍTICO - FASE 1 BI/ANALYTICS                 ║
╚══════════════════════════════════════════════════════════════════════════╝

Cache distribuido en BD para análisis costosos.

Responsabilidades:
- Almacenar resultados de cálculos costosos (tendencias, comparativos)
- Invalidación inteligente (expira automáticamente o si hay nuevos KPIs)
- Fallback a cálculo si cache expirado
- Tracking de hits para optimización

Cache keys pattern:
  trend_{kpi}_{periodo}       - Ej: trend_produccion_6m
  comp_{kpi1}_{kpi2}_{scope}  - Ej: comp_margen_produccion_1y
  insights_{scope}            - Ej: insights_general_1m
"""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import logging
import hashlib
from src.database.database import get_db_connection
from src.services.system_metrics_service import get_system_metrics_service

logger = logging.getLogger("analytics_cache")


class AnalyticsCacheService:
    """Servicio de cache inteligente para análisis"""
    
    # Tiempos de expiración por tipo de cache (segundos)
    TTL_DEFAULT = 3600  # 1 hora
    TTL_TRENDS = 7200  # 2 horas (cálculos más pesados)
    TTL_INSIGHTS = 3600  # 1 hora
    TTL_COMPARATIVES = 5400  # 1.5 horas
    
    def __init__(self):
        self.logger = logger
        self._asegurar_tabla()
    
    def _asegurar_tabla(self):
        """Verifica que la tabla existe"""
        try:
            with get_db_connection() as conn:
                conn.execute("SELECT 1 FROM analytics_cache LIMIT 1")
        except Exception as e:
            self.logger.warning(f"Tabla analytics_cache no disponible: {e}")
    
    def get_or_calculate(
        self,
        cache_key: str,
        calculator_func,
        *args,
        ttl: Optional[int] = None,
        tags: Optional[list[str]] = None,
        **kwargs
    ) -> Any:
        """
        Obtiene valor de cache o calcula si no existe/expiró.
        
        Args:
            cache_key: Clave única del cache
            calculator_func: Función que calcula el valor
            ttl: Tiempo de vida en segundos (default según tipo)
            tags: Tags para invalidación grupal
            args, kwargs: Argumentos para calculator_func
        
        Returns:
            Valor cacheado o calculado
        """
        # Intentar obtener del cache
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Calcular
        self.logger.debug(f"Cache miss: {cache_key}, calculando...")
        valor = calculator_func(*args, **kwargs)
        
        # Guardar en cache
        if ttl is None:
            ttl = self.TTL_DEFAULT
        
        self._save_to_cache(cache_key, valor, ttl, tags)
        
        return valor
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """
        Obtiene valor del cache si existe y no expiró.
        
        Args:
            cache_key: Clave del cache
        
        Returns:
            Valor deserializado o None si no existe/expiró
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT valor_json, fecha_calculo, expira_en
                    FROM analytics_cache
                    WHERE cache_key = ?
                """, (cache_key,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                valor_json, fecha_calculo, expira_en = row
                
                # Verificar expiración
                fecha_calc = datetime.fromisoformat(fecha_calculo)
                ahora = datetime.now()
                
                if (ahora - fecha_calc).total_seconds() > expira_en:
                    self.logger.debug(f"Cache expirado: {cache_key}")
                    return None
                
                # Registrar cache hit
                try:
                    metrics = get_system_metrics_service()
                    metrics.registrar_cache_hit("analytics_cache", cache_key)
                except Exception:
                    pass  # No bloquear cache por error de métricas
                
                # Incrementar hits
                cursor.execute("""
                    UPDATE analytics_cache
                    SET hits = hits + 1
                    WHERE cache_key = ?
                """, (cache_key,))
                conn.commit()
                
                # Deserializar
                valor = json.loads(valor_json)
                self.logger.debug(f"Cache hit: {cache_key}")
                return valor
                
        except Exception as e:
            self.logger.error(f"Error leyendo cache {cache_key}: {e}")
            return None
    
    def _save_to_cache(
        self,
        cache_key: str,
        valor: Any,
        ttl: int,
        tags: Optional[list[str]] = None
    ) -> None:
        """
        Guarda valor en cache.
        
        Args:
            cache_key: Clave única
            valor: Valor a cachear
            ttl: Tiempo de vida en segundos
            tags: Tags para invalidación
        """
        try:
            valor_json = json.dumps(valor, ensure_ascii=False)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existe
                cursor.execute("""
                    SELECT id FROM analytics_cache
                    WHERE cache_key = ?
                """, (cache_key,))
                
                if cursor.fetchone():
                    # Actualizar
                    cursor.execute("""
                        UPDATE analytics_cache
                        SET valor_json = ?,
                            fecha_calculo = CURRENT_TIMESTAMP,
                            expira_en = ?,
                            hits = 0
                        WHERE cache_key = ?
                    """, (valor_json, ttl, cache_key))
                else:
                    # Insertar
                    cursor.execute("""
                        INSERT INTO analytics_cache
                        (cache_key, valor_json, expira_en)
                        VALUES (?, ?, ?)
                    """, (cache_key, valor_json, ttl))
                
                conn.commit()
                self.logger.debug(f"Valor cacheado: {cache_key} (TTL: {ttl}s)")
                
        except Exception as e:
            self.logger.error(f"Error guardando cache {cache_key}: {e}")
    
    def invalidar(self, cache_key: str) -> bool:
        """
        Invalida una entrada de cache específica.
        
        Args:
            cache_key: Clave a invalidar
        
        Returns:
            True si se eliminó, False si no existía
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM analytics_cache
                    WHERE cache_key = ?
                """, (cache_key,))
                
                eliminado = cursor.rowcount > 0
                conn.commit()
                
                if eliminado:
                    self.logger.info(f"Cache invalidado: {cache_key}")
                
                return eliminado
                
        except Exception as e:
            self.logger.error(f"Error invalidando cache {cache_key}: {e}")
            return False
    
    def invalidar_patron(self, patron: str) -> int:
        """
        Invalida todas las entradas que coincidan con patrón.
        
        Args:
            patron: Patrón LIKE (ej: "trend_%")
        
        Returns:
            Número de entradas eliminadas
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM analytics_cache
                    WHERE cache_key LIKE ?
                """, (patron,))
                
                eliminadas = cursor.rowcount
                conn.commit()
                
                if eliminadas > 0:
                    self.logger.info(f"Cache invalidado (patrón '{patron}'): {eliminadas} entradas")
                
                return eliminadas
                
        except Exception as e:
            self.logger.error(f"Error invalidando patrón {patron}: {e}")
            return 0
    
    def invalidar_si_nuevos_kpis(self, año: int, mes: int) -> int:
        """
        Invalida cache que depende de KPIs si hay nuevos del período.
        
        Llamado cuando se generan nuevos KPIs en cierre mensual.
        
        Args:
            año, mes: Período con KPIs nuevos
        
        Returns:
            Número de entradas invalidadas
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Invalidar caches que dependen de KPIs
                cursor.execute("""
                    DELETE FROM analytics_cache
                    WHERE invalidar_si_nuevos_kpis = 1
                    AND cache_key LIKE 'trend_%'
                    OR cache_key LIKE 'comp_%'
                    OR cache_key LIKE 'insights_%'
                """)
                
                eliminadas = cursor.rowcount
                conn.commit()
                
                if eliminadas > 0:
                    self.logger.info(
                        f"Cache invalidado (nuevos KPIs {año}-{mes:02d}): {eliminadas} entradas"
                    )
                
                return eliminadas
                
        except Exception as e:
            self.logger.error(f"Error invalidando cache por KPIs: {e}")
            return 0
    
    def limpiar_expirados(self) -> int:
        """
        Limpia todas las entradas de cache expiradas.
        
        Returns:
            Número de entradas eliminadas
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM analytics_cache
                    WHERE (julianday('now') - julianday(fecha_calculo)) * 86400 > expira_en
                """)
                
                eliminadas = cursor.rowcount
                conn.commit()
                
                if eliminadas > 0:
                    self.logger.info(f"Entradas expiradas eliminadas: {eliminadas}")
                
                return eliminadas
                
        except Exception as e:
            self.logger.error(f"Error limpiando cache expirado: {e}")
            return 0
    
    def limpiar_todo(self) -> int:
        """
        Limpia todo el cache.
        
        Returns:
            Número de entradas eliminadas
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM analytics_cache")
                eliminadas = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"Cache completo eliminado: {eliminadas} entradas")
                return eliminadas
                
        except Exception as e:
            self.logger.error(f"Error limpiando cache: {e}")
            return 0
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache.
        
        Returns:
            Diccionario con stats
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_entradas,
                        SUM(hits) as total_hits,
                        AVG(hits) as hits_promedio,
                        MAX(hits) as hits_maximo
                    FROM analytics_cache
                """)
                
                row = cursor.fetchone()
                return {
                    'total_entradas': row[0] or 0,
                    'total_hits': row[1] or 0,
                    'hits_promedio': round(row[2], 2) if row[2] else 0,
                    'hits_maximo': row[3] or 0
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}


# Singleton
_analytics_cache_instance: Optional[AnalyticsCacheService] = None


def get_analytics_cache() -> AnalyticsCacheService:
    """Obtiene la instancia singleton del servicio de cache"""
    global _analytics_cache_instance
    if _analytics_cache_instance is None:
        _analytics_cache_instance = AnalyticsCacheService()
    return _analytics_cache_instance
