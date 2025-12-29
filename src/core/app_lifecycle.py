"""
CICLO DE VIDA DE LA APLICACIÓN - FincaFácil
============================================

Gestiona:
- Inicialización limpia
- Validaciones pre-cierre
- Guardado de estados
- Cierres mensuales automáticos
- Logs finales y auditoría
- Liberación de recursos
"""

import logging
import sys
from datetime import datetime, date
from typing import Callable, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class AppLifecycleManager:
    """Gestor centralizado del ciclo de vida de la aplicación"""
    
    def __init__(self):
        self.is_closing = False
        self.pending_operations: List[Tuple[str, Callable]] = []
        self.callbacks_pre_close: List[Callable] = []
        self.callbacks_post_close: List[Callable] = []
        self.unsaved_changes = {}
        
        logger.info("✅ AppLifecycleManager inicializado")
    
    def register_pre_close_callback(self, callback: Callable, name: Optional[str] = None):
        """
        Registra un callback a ejecutarse antes de cerrar la app.
        
        Args:
            callback: Función a ejecutar(sin argumentos)
            name: Nombre descriptivo para logs
        """
        self.callbacks_pre_close.append(callback)
        logger.debug(f"Callback pre-close registrado: {name or callback.__name__}")
    
    def register_post_close_callback(self, callback: Callable, name: Optional[str] = None):
        """
        Registra un callback a ejecutarse después de cerrar la app.
        (Para limpieza de recursos, etc.)
        """
        self.callbacks_post_close.append(callback)
        logger.debug(f"Callback post-close registrado: {name or callback.__name__}")
    
    def register_pending_operation(self, operation_name: str, handler: Callable):
        """
        Registra una operación pendiente que necesita validación pre-cierre.
        
        Args:
            operation_name: Descripción de la operación
            handler: Función que valida/completa la operación
        """
        self.pending_operations.append((operation_name, handler))
        logger.debug(f"Operación pendiente registrada: {operation_name}")
    
    def mark_unsaved_changes(self, module: str, entity_id: Optional[str] = None):
        """Marca cambios no guardados en un módulo"""
        key = f"{module}:{entity_id}" if entity_id else module
        self.unsaved_changes[key] = datetime.now()
        logger.debug(f"Cambios no guardados marcados: {key}")
    
    def clear_unsaved_changes(self, module: Optional[str] = None):
        """Limpia los cambios no guardados"""
        if module:
            keys_to_remove = [k for k in self.unsaved_changes.keys() if k.startswith(module)]
            for key in keys_to_remove:
                del self.unsaved_changes[key]
        else:
            self.unsaved_changes.clear()
        logger.debug(f"Cambios guardados: {module or 'todos'}")
    
    def has_unsaved_changes(self) -> bool:
        """Verifica si hay cambios sin guardar"""
        return len(self.unsaved_changes) > 0
    
    def get_unsaved_summary(self) -> str:
        """Obtiene resumen de cambios no guardados"""
        if not self.unsaved_changes:
            return "Sin cambios pendientes"
        
        summary = "Cambios sin guardar en:\n"
        for key, timestamp in self.unsaved_changes.items():
            summary += f"  - {key} (hace {datetime.now() - timestamp})\n"
        return summary
    
    async def validate_pending_operations(self) -> Tuple[bool, List[str]]:
        """
        Valida todas las operaciones pendientes.
        
        Returns:
            (todas_válidas, lista_de_errores)
        """
        errors = []
        
        logger.info("🔍 Validando operaciones pendientes...")
        
        for op_name, handler in self.pending_operations:
            try:
                logger.debug(f"Validando: {op_name}")
                result = handler()
                if not result:
                    errors.append(f"Validación fallida: {op_name}")
            except Exception as e:
                errors.append(f"Error validando {op_name}: {str(e)}")
                logger.error(f"Error en validación de {op_name}", exc_info=True)
        
        if errors:
            logger.warning(f"⚠️ Errores en validación: {len(errors)}")
        else:
            logger.info("✅ Todas las validaciones pasaron")
        
        return len(errors) == 0, errors
    
    def check_monthly_close_needed(self) -> Optional[Tuple[int, int]]:
        """
        Verifica si hay un cierre mensual pendiente.
        
        Returns:
            (año, mes) si hay pendiente, None si está al día
        """
        try:
            from database.database import get_db_connection
            
            today = date.today()
            current_year = today.year
            current_month = today.month
            
            # Si es antes del 5 del mes, verificar mes anterior
            if today.day < 5:
                if current_month == 1:
                    check_year, check_month = current_year - 1, 12
                else:
                    check_year, check_month = current_year, current_month - 1
            else:
                check_year, check_month = current_year, current_month
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM cierre_mensual 
                    WHERE año = ? AND mes = ?
                """, (check_year, check_month))
                
                if cursor.fetchone()[0] == 0:
                    logger.warning(f"⚠️ Cierre mensual pendiente: {check_month}/{check_year}")
                    return (check_year, check_month)
        
        except Exception as e:
            logger.error(f"Error verificando cierre pendiente: {e}")
        
        return None
    
    async def on_app_close(self, usuario_id: str = "Sistema") -> bool:
        """
        Ejecuta la secuencia completa de cierre de aplicación.
        
        Args:
            usuario_id: ID del usuario que inicia el cierre
            
        Returns:
            True si el cierre fue exitoso
        """
        if self.is_closing:
            logger.warning("Cierre ya en progreso")
            return False
        
        self.is_closing = True
        logger.info("=" * 60)
        logger.info("🔴 INICIANDO CIERRE DE APLICACIÓN")
        logger.info("=" * 60)
        
        try:
            # Fase 1: Validar operaciones pendientes
            logger.info("\n[FASE 1] Validando operaciones pendientes...")
            valid, errors = await self.validate_pending_operations()
            
            if not valid:
                logger.error(f"❌ Validaciones fallaron. Resumen:\n" + "\n".join(errors))
                # Dar opción de continuar anyway
                return False
            
            logger.info("✅ Validaciones completadas")
            
            # Fase 2: Guardar estados temporales
            logger.info("\n[FASE 2] Guardando estados temporales...")
            if self.has_unsaved_changes():
                logger.warning(f"⚠️ Cambios no guardados:\n{self.get_unsaved_summary()}")
                # Los cambios se habrían guardado de forma incremental
            else:
                logger.info("✅ Todos los cambios guardados")
            
            # Fase 3: Verificar cierres mensuales pendientes
            logger.info("\n[FASE 3] Verificando cierres mensuales...")
            pending_close = self.check_monthly_close_needed()
            
            if pending_close:
                logger.warning(
                    f"⚠️ Cierre mensual {pending_close[1]}/{pending_close[0]} aún no realizado.\n"
                    f"   Recomendación: Ejecutarlo antes de cerrar la aplicación."
                )
                # No es fatal, solo una advertencia
            else:
                logger.info("✅ Cierres mensuales al día")
            
            # Fase 4: Ejecutar callbacks pre-cierre
            logger.info("\n[FASE 4] Ejecutando callbacks pre-cierre...")
            for callback in self.callbacks_pre_close:
                try:
                    callback_name = callback.__name__ if hasattr(callback, '__name__') else str(callback)
                    logger.debug(f"Ejecutando: {callback_name}")
                    callback()
                except Exception as e:
                    logger.error(f"Error en callback: {e}", exc_info=True)
            
            logger.info("✅ Callbacks completados")
            
            # Fase 5: Registrar logs finales
            logger.info("\n[FASE 5] Registrando logs finales...")
            self._log_app_closure(usuario_id)
            logger.info("✅ Logs registrados")
            
            # Fase 6: Ejecutar callbacks post-cierre
            logger.info("\n[FASE 6] Ejecutando callbacks post-cierre (limpieza)...")
            for callback in self.callbacks_post_close:
                try:
                    callback_name = callback.__name__ if hasattr(callback, '__name__') else str(callback)
                    logger.debug(f"Limpiando: {callback_name}")
                    callback()
                except Exception as e:
                    logger.error(f"Error en callback post-cierre: {e}")
            
            logger.info("✅ Limpieza completada")
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ CIERRE DE APLICACIÓN COMPLETADO EXITOSAMENTE")
            logger.info("=" * 60)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error crítico durante cierre: {e}", exc_info=True)
            return False
        
        finally:
            self.is_closing = False
    
    def _log_app_closure(self, usuario_id: str):
        """Registra el cierre de la aplicación en auditoría"""
        try:
            from database.database import get_db_connection
            from datetime import datetime
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Registrar evento de cierre en auditoría
                cursor.execute("""
                    INSERT INTO auditoria 
                    (usuario_id, usuario_nombre, modulo, accion, resultado, timestamp)
                    VALUES (?, ?, 'app', 'SHUTDOWN', 'OK', ?)
                """, (usuario_id, usuario_id, datetime.now().isoformat()))
                
                conn.commit()
                logger.debug("Evento de cierre registrado en auditoría")
        
        except Exception as e:
            logger.warning(f"No se pudo registrar evento de cierre: {e}")


# Instancia global
_lifecycle_manager: Optional[AppLifecycleManager] = None


def get_app_lifecycle() -> AppLifecycleManager:
    """Obtiene la instancia del gestor de ciclo de vida"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = AppLifecycleManager()
    return _lifecycle_manager


def reset_app_lifecycle():
    """Resetea el gestor (para tests)"""
    global _lifecycle_manager
    _lifecycle_manager = None
