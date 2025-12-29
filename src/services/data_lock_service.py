"""
SERVICIO DE BLOQUEO DE DATOS CERRADOS - FincaFácil
===================================================

Previene edición/eliminación de datos de períodos cerrados.
Garantiza la integridad contable y auditable.
"""

import logging
from datetime import date
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)


class DataLockService:
    """Servicio para bloquear edición de datos cerrados"""
    
    def __init__(self):
        self.cache_cierres = {}  # Cache de períodos cerrados
        
    def is_period_closed(self, año: int, mes: int) -> bool:
        """
        Verifica si un período está cerrado.
        
        Args:
            año: Año del período
            mes: Mes del período (1-12)
            
        Returns:
            True si el período está cerrado
        """
        cache_key = f"{año}-{mes:02d}"
        
        # Verificar cache
        if cache_key in self.cache_cierres:
            return self.cache_cierres[cache_key]
        
        try:
            from database.database import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM cierre_mensual
                    WHERE año = ? AND mes = ? AND estado = 'Completado'
                """, (año, mes))
                
                is_closed = cursor.fetchone()[0] > 0
                
                # Actualizar cache
                self.cache_cierres[cache_key] = is_closed
                
                return is_closed
                
        except Exception as e:
            logger.error(f"Error verificando cierre: {e}")
            return False
    
    def is_date_in_closed_period(self, fecha: date) -> bool:
        """
        Verifica si una fecha pertenece a un período cerrado.
        
        Args:
            fecha: Fecha a verificar
            
        Returns:
            True si la fecha está en un período cerrado
        """
        return self.is_period_closed(fecha.year, fecha.month)
    
    def can_modify_data(self, fecha: date, modulo: str) -> Tuple[bool, str]:
        """
        Verifica si se puede modificar un dato de una fecha específica.
        
        Args:
            fecha: Fecha del dato
            modulo: Módulo (ventas, gastos, nomina, etc.)
            
        Returns:
            (puede_modificar, mensaje_error)
        """
        if self.is_date_in_closed_period(fecha):
            return False, (
                f"No se puede modificar. El período {fecha.month}/{fecha.year} está cerrado.\n"
                f"Contacta al administrador si necesitas hacer cambios."
            )
        
        return True, ""
    
    def block_data(self, año: int, mes: int, modulo: str, entidad_ids: List[int] | None = None):
        """
        Bloquea datos específicos de un período.
        
        Args:
            año: Año del período
            mes: Mes del período
            modulo: Módulo (ventas, gastos, nomina)
            entidad_ids: IDs de registros a bloquear (None = todos del período)
        """
        try:
            from database.database import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if entidad_ids:
                    # Bloquear registros específicos
                    for entidad_id in entidad_ids:
                        cursor.execute("""
                            INSERT OR IGNORE INTO datos_cerrados 
                            (año, mes, modulo, entidad_id, fecha_cierre)
                            VALUES (?, ?, ?, ?, datetime('now'))
                        """, (año, mes, modulo, entidad_id))
                else:
                    # Bloquear todos los datos del período
                    cursor.execute("""
                        INSERT OR IGNORE INTO datos_cerrados 
                        (año, mes, modulo, fecha_cierre)
                        VALUES (?, ?, ?, datetime('now'))
                    """, (año, mes, modulo))
                
                conn.commit()
                logger.info(f"Datos bloqueados: {modulo} {mes}/{año}")
                
                # Invalidar cache
                cache_key = f"{año}-{mes:02d}"
                if cache_key in self.cache_cierres:
                    del self.cache_cierres[cache_key]
                    
        except Exception as e:
            logger.error(f"Error bloqueando datos: {e}")
            raise
    
    def unblock_period(self, año: int, mes: int):
        """
        Desbloquea un período completo (requiere permiso de administrador).
        
        Args:
            año: Año del período
            mes: Mes del período
        """
        try:
            from database.database import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Eliminar cierre mensual
                cursor.execute("""
                    UPDATE cierre_mensual 
                    SET estado = 'Revertido'
                    WHERE año = ? AND mes = ?
                """, (año, mes))
                
                # Eliminar bloqueos de datos
                cursor.execute("""
                    DELETE FROM datos_cerrados
                    WHERE año = ? AND mes = ?
                """, (año, mes))
                
                conn.commit()
                logger.warning(f"⚠️ Período desbloqueado: {mes}/{año}")
                
                # Invalidar cache
                cache_key = f"{año}-{mes:02d}"
                if cache_key in self.cache_cierres:
                    del self.cache_cierres[cache_key]
                    
        except Exception as e:
            logger.error(f"Error desbloqueando período: {e}")
            raise
    
    def get_closed_periods(self) -> List[Tuple[int, int]]:
        """
        Obtiene lista de períodos cerrados.
        
        Returns:
            Lista de (año, mes) cerrados
        """
        try:
            from database.database import get_db_connection
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT año, mes FROM cierre_mensual
                    WHERE estado = 'Completado'
                    ORDER BY año DESC, mes DESC
                """)
                
                return [(row[0], row[1]) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error obteniendo períodos cerrados: {e}")
            return []
    
    def validate_before_save(self, fecha: date, modulo: str) -> None:
        """
        Valida antes de guardar un registro. Lanza excepción si está bloqueado.
        
        Args:
            fecha: Fecha del registro
            modulo: Módulo
            
        Raises:
            ValueError: Si el período está cerrado
        """
        can_modify, message = self.can_modify_data(fecha, modulo)
        
        if not can_modify:
            raise ValueError(message)


# Instancia singleton
_data_lock_service: Optional[DataLockService] = None


def get_data_lock_service() -> DataLockService:
    """Obtiene la instancia del servicio de bloqueo"""
    global _data_lock_service
    if _data_lock_service is None:
        _data_lock_service = DataLockService()
    return _data_lock_service


def reset_data_lock_service():
    """Resetea el servicio (para tests)"""
    global _data_lock_service
    _data_lock_service = None
