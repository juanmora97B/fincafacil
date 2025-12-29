"""
╔══════════════════════════════════════════════════════════════════════════╗
║         SERVICIO DE SNAPSHOTS ANALÍTICOS - FASE 1 BI/ANALYTICS          ║
╚══════════════════════════════════════════════════════════════════════════╝

Captura estado completo del negocio al final de cada mes.

Responsabilidades:
- Generar snapshot mensual con todos los KPIs y estado
- Persistir en tabla bi_snapshots_mensual para historial
- NO recalcular: usar datos ya persistidos
- Base para análisis histórico y tendencias

Flow:
1. on_monthly_close() llama a generar_snapshot()
2. Snapshot contiene: resumen, KPIs, alertas, tendencias
3. Se persiste en JSON comprimido para consultas ágiles
4. Analytics services leen snapshots sin cálculos costosos
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path
from src.database.database import get_db_connection
from src.services.system_metrics_service import get_system_metrics_service

logger = logging.getLogger("bi_snapshot")


class BISnapshotService:
    """Servicio para generar y gestionar snapshots analíticos mensuales"""
    
    def __init__(self):
        self.logger = logger
    
    def generar_snapshot(
        self,
        año: int,
        mes: int,
        usuario: str = "Sistema"
    ) -> Dict[str, Any]:
        """
        Genera snapshot completo del estado del negocio al final del mes.
        
        Args:
            año: Año del mes (2025, etc)
            mes: Número de mes (1-12)
            usuario: Usuario que genera el snapshot
        
        Returns:
            Diccionario con todo el snapshot
        """
        inicio = datetime.now()
        self.logger.info(f"Generando snapshot para {año}-{mes:02d}")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Obtener resumen mensual (ya calculado)
            cursor.execute("""
                SELECT * FROM resumen_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            resumen_row = cursor.fetchone()
            if not resumen_row:
                raise ValueError(f"No existe resumen mensual para {año}-{mes:02d}")
            
            resumen_cols = [desc[0] for desc in cursor.description]
            resumen = dict(zip(resumen_cols, resumen_row))
            
            # 2. Obtener KPIs persistidos del mes
            cursor.execute("""
                SELECT nombre_kpi, valor, categoria
                FROM kpi_tracking
                WHERE año = ? AND mes = ?
                ORDER BY categoria, nombre_kpi
            """, (año, mes))
            
            kpis = {}
            for row in cursor.fetchall():
                kpis[row[0]] = {
                    'valor': row[1],
                    'categoria': row[2]
                }
            
            # 3. Obtener alertas del período
            cursor.execute("""
                SELECT 
                    tipo, prioridad, titulo, descripcion,
                    entidad_tipo, valor_actual, valor_referencia
                FROM alertas
                WHERE fecha_deteccion >= date(?, '-1 month')
                AND fecha_deteccion < date(?)
                ORDER BY prioridad DESC, fecha_deteccion DESC
            """, (f"{año}-{mes:02d}-01", f"{año}-{mes:02d}-01"))
            
            alertas = []
            for row in cursor.fetchall():
                alertas.append({
                    'tipo': row[0],
                    'prioridad': row[1],
                    'titulo': row[2],
                    'descripcion': row[3],
                    'entidad_tipo': row[4],
                    'valor_actual': row[5],
                    'valor_referencia': row[6]
                })
            
            # 4. Calcular tendencias básicas (mes vs mes anterior)
            cursor.execute("""
                SELECT 
                    rm1.año, rm1.mes,
                    rm1.margen_porcentaje,
                    rm2.margen_porcentaje as margen_mes_anterior
                FROM resumen_mensual rm1
                LEFT JOIN resumen_mensual rm2
                    ON rm1.año = rm2.año
                    AND ((rm1.mes = 1 AND rm2.mes = 12 AND rm1.año - 1 = rm2.año)
                         OR (rm1.mes > 1 AND rm2.mes = rm1.mes - 1 AND rm1.año = rm2.año))
                WHERE rm1.año = ? AND rm1.mes = ?
            """, (año, mes))
            
            tendencias = {}
            row = cursor.fetchone()
            if row:
                margen_actual = row[2] or 0
                margen_anterior = row[3] or 0
                
                if margen_anterior != 0:
                    variacion = ((margen_actual - margen_anterior) / abs(margen_anterior)) * 100
                else:
                    variacion = 0
                
                tendencias['margen_variacion_mes_anterior_pct'] = round(variacion, 2)
            
            # 5. Contar alertas por prioridad
            alertas_por_prioridad = {}
            for alerta in alertas:
                prioridad = alerta['prioridad']
                alertas_por_prioridad[prioridad] = alertas_por_prioridad.get(prioridad, 0) + 1
            
            # 6. Armar snapshot completo
            snapshot = {
                'metadatos': {
                    'año': año,
                    'mes': mes,
                    'periodo': f"{año}-{mes:02d}",
                    'fecha_snapshot': datetime.now().isoformat(),
                    'generado_por': usuario,
                    'version': 1
                },
                'resumen_mensual': resumen,
                'kpis': kpis,
                'alertas': {
                    'total': len(alertas),
                    'por_prioridad': alertas_por_prioridad,
                    'lista': alertas[:20]  # Top 20 alertas
                },
                'tendencias': tendencias,
                'estadisticas': {
                    'total_kpis': len(kpis),
                    'total_alertas': len(alertas),
                    'alertas_criticas': alertas_por_prioridad.get('alta', 0)
                }
            }
        
        # Persistir en BD
        self._guardar_snapshot_en_bd(año, mes, snapshot, usuario)
        
        # Registrar métrica de tiempo
        duracion_ms = (datetime.now() - inicio).total_seconds() * 1000
        try:
            metrics = get_system_metrics_service()
            metrics.registrar_tiempo_ejecucion(
                "snapshot_generation",
                duracion_ms,
                {"kpis": len(kpis), "alertas": len(alertas)}
            )
        except Exception:
            pass  # No bloquear snapshot por error de métricas
        
        self.logger.info(f"✓ Snapshot generado: {año}-{mes:02d}")
        return snapshot
    
    def _guardar_snapshot_en_bd(
        self,
        año: int,
        mes: int,
        snapshot: Dict[str, Any],
        usuario: str
    ) -> None:
        """Guarda snapshot serializado en BD"""
        import hashlib
        
        snapshot_json = json.dumps(snapshot, ensure_ascii=False)
        md5_hash = hashlib.md5(snapshot_json.encode()).hexdigest()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si existe
            cursor.execute("""
                SELECT id FROM bi_snapshots_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            if cursor.fetchone():
                # Actualizar
                cursor.execute("""
                    UPDATE bi_snapshots_mensual
                    SET data_json = ?,
                        fecha_snapshot = CURRENT_TIMESTAMP,
                        md5_hash = ?,
                        generado_por = ?,
                        version = version + 1
                    WHERE año = ? AND mes = ?
                """, (snapshot_json, md5_hash, usuario, año, mes))
                self.logger.debug(f"Snapshot {año}-{mes:02d} actualizado")
            else:
                # Insertar
                cursor.execute("""
                    INSERT INTO bi_snapshots_mensual
                    (año, mes, data_json, md5_hash, generado_por)
                    VALUES (?, ?, ?, ?, ?)
                """, (año, mes, snapshot_json, md5_hash, usuario))
                self.logger.debug(f"Snapshot {año}-{mes:02d} insertado")
            
            conn.commit()
    
    def obtener_snapshot(self, año: int, mes: int) -> Dict[str, Any]:
        """
        Obtiene snapshot existente de la BD.
        
        Args:
            año: Año
            mes: Mes (1-12)
        
        Returns:
            Diccionario con snapshot
        
        Raises:
            ValueError: Si no existe snapshot
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data_json FROM bi_snapshots_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Snapshot no encontrado para {año}-{mes:02d}")
            
            return json.loads(row[0])
    
    def obtener_snapshots_rango(
        self,
        año_inicio: int,
        mes_inicio: int,
        año_fin: int,
        mes_fin: int
    ) -> list[Dict[str, Any]]:
        """
        Obtiene múltiples snapshots en un rango de fechas.
        
        Args:
            año_inicio, mes_inicio: Período inicio
            año_fin, mes_fin: Período fin
        
        Returns:
            Lista de snapshots ordenados cronológicamente
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT data_json
                FROM bi_snapshots_mensual
                WHERE (año > ? OR (año = ? AND mes >= ?))
                AND (año < ? OR (año = ? AND mes <= ?))
                ORDER BY año ASC, mes ASC
            """, (año_inicio, año_inicio, mes_inicio, año_fin, año_fin, mes_fin))
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append(json.loads(row[0]))
            
            return snapshots
    
    def limpiar_snapshots_antiguos(self, meses_retener: int = 24) -> int:
        """
        Limpia snapshots más antiguos que el período especificado.
        
        Args:
            meses_retener: Número de meses a mantener (default 24 = 2 años)
        
        Returns:
            Número de snapshots eliminados
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM bi_snapshots_mensual
                WHERE fecha_snapshot < date('now', '-' || ? || ' months')
            """, (meses_retener,))
            
            eliminados = cursor.rowcount
            conn.commit()
            
            if eliminados > 0:
                self.logger.info(f"Snapshots antiguos eliminados: {eliminados}")
            
            return eliminados


# Singleton
_bi_snapshot_instance: Optional[BISnapshotService] = None


def get_bi_snapshot_service() -> BISnapshotService:
    """Obtiene la instancia singleton del servicio de snapshots"""
    global _bi_snapshot_instance
    if _bi_snapshot_instance is None:
        _bi_snapshot_instance = BISnapshotService()
    return _bi_snapshot_instance
