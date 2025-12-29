"""
DECORADOR DE PERMISOS - FincaFácil
===================================

Decoradores para validar permisos en servicios y métodos críticos.
Implementa defensa en profundidad: validación tanto en backend como en UI.
"""

import logging
from functools import wraps
from typing import Callable, Any

from src.core.permissions_manager import (
    get_permissions_manager,
    PermissionEnum,
    PermissionDeniedException
)

logger = logging.getLogger(__name__)


def require_permission(permission: PermissionEnum):
    """
    Decorador que requiere un permiso específico para ejecutar una función.
    
    Args:
        permission: El permiso requerido (ej: PermissionEnum.VENTAS_CREAR)
        
    Uso:
        @require_permission(PermissionEnum.VENTAS_CREAR)
        def crear_venta(self, datos):
            # código protegido
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            pm = get_permissions_manager()
            
            # Validar permiso
            if not pm.has_permission(permission):
                user = pm.get_current_user() or "desconocido"
                role = pm.get_current_role()
                
                logger.warning(
                    f"🚫 ACCESO DENEGADO: {user} ({role}) intentó ejecutar "
                    f"{func.__name__} sin permiso {permission.value}"
                )
                
                raise PermissionDeniedException(
                    f"No tienes permiso para realizar esta acción",
                    permission,
                    role
                )
            
            # Ejecutar función protegida
            logger.debug(f"✅ Permiso {permission.value} validado para {func.__name__}")
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(*permissions: PermissionEnum):
    """
    Decorador que requiere AL MENOS UNO de los permisos especificados.
    
    Args:
        *permissions: Lista de permisos (requiere al menos uno)
        
    Uso:
        @require_any_permission(PermissionEnum.VENTAS_VER, PermissionEnum.REPORTES_VER)
        def ver_reporte_ventas(self):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            pm = get_permissions_manager()
            
            # Verificar si tiene al menos uno de los permisos
            has_any = any(pm.has_permission(perm) for perm in permissions)
            
            if not has_any:
                user = pm.get_current_user() or "desconocido"
                role = pm.get_current_role()
                
                perms_str = " o ".join([p.value for p in permissions])
                logger.warning(
                    f"🚫 ACCESO DENEGADO: {user} ({role}) intentó ejecutar "
                    f"{func.__name__} sin permisos: {perms_str}"
                )
                
                raise PermissionDeniedException(
                    f"No tienes ninguno de los permisos requeridos para esta acción",
                    permissions[0],  # Primer permiso como referencia
                    role
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_all_permissions(*permissions: PermissionEnum):
    """
    Decorador que requiere TODOS los permisos especificados.
    
    Args:
        *permissions: Lista de permisos (requiere todos)
        
    Uso:
        @require_all_permissions(PermissionEnum.VENTAS_ELIMINAR, PermissionEnum.AUDITORIA_VER)
        def eliminar_venta_con_auditoria(self, venta_id):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            pm = get_permissions_manager()
            
            # Verificar que tiene todos los permisos
            missing_perms = [p for p in permissions if not pm.has_permission(p)]
            
            if missing_perms:
                user = pm.get_current_user() or "desconocido"
                role = pm.get_current_role()
                
                missing_str = ", ".join([p.value for p in missing_perms])
                logger.warning(
                    f"🚫 ACCESO DENEGADO: {user} ({role}) intentó ejecutar "
                    f"{func.__name__} sin permisos: {missing_str}"
                )
                
                raise PermissionDeniedException(
                    f"Te faltan permisos para esta acción: {missing_str}",
                    missing_perms[0],
                    role
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def audit_action(module: str, action: str):
    """
    Decorador que registra una acción en auditoría automáticamente.
    
    Args:
        module: Módulo (ej: "ventas")
        action: Acción (ej: "CREAR")
        
    Uso:
        @audit_action("ventas", "CREAR")
        @require_permission(PermissionEnum.VENTAS_CREAR)
        def crear_venta(self, datos):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            pm = get_permissions_manager()
            user = pm.get_current_user() or "Sistema"
            
            try:
                # Ejecutar función
                result = func(*args, **kwargs)
                
                # Registrar éxito en auditoría
                try:
                    from database.database import get_db_connection
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO auditoria 
                            (usuario_nombre, modulo, accion, resultado, timestamp)
                            VALUES (?, ?, ?, 'OK', datetime('now'))
                        """, (user, module, action))
                        conn.commit()
                except Exception as audit_err:
                    logger.warning(f"No se pudo registrar auditoría: {audit_err}")
                
                return result
                
            except Exception as e:
                # Registrar fallo en auditoría
                try:
                    from database.database import get_db_connection
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO auditoria 
                            (usuario_nombre, modulo, accion, resultado, detalles, timestamp)
                            VALUES (?, ?, ?, 'ERROR', ?, datetime('now'))
                        """, (user, module, action, str(e)))
                        conn.commit()
                except Exception:
                    pass
                
                raise
        
        return wrapper
    return decorator
