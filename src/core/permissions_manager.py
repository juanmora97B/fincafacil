"""
SISTEMA DE PERMISOS Y ROLES (RBAC) - FincaFácil
================================================

Arquitectura:
- Roles: Administrador, Operador, Consulta (extensible)
- Permisos: Granulares por módulo/acción
- Validación: Backend + UI (defensa en profundidad)
- Auditoría: Todos los cambios sensibles registrados

Diseño para escalabilidad:
- Estructura preparada para +10 roles
- Permisos definibles por parámetro
- Sin hardcoding de reglas
"""

from typing import List, Dict, Set, Tuple, Optional
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RoleEnum(Enum):
    """Roles del sistema"""
    ADMINISTRADOR = "Administrador"      # Control total
    OPERADOR = "Operador"                # Operaciones diarias
    CONSULTA = "Consulta"                # Solo lectura
    SUPERVISOR = "Supervisor"            # Supervisión de operadores (futuro)
    
    def __str__(self):
        return self.value


class PermissionEnum(Enum):
    """Permisos del sistema - Granulares por módulo"""
    
    # VENTAS
    VENTAS_CREAR = "ventas.crear"
    VENTAS_EDITAR = "ventas.editar"
    VENTAS_ELIMINAR = "ventas.eliminar"
    VENTAS_VER = "ventas.ver"
    
    # NÓMINA
    NOMINA_CREAR = "nomina.crear"
    NOMINA_EDITAR = "nomina.editar"
    NOMINA_ELIMINAR = "nomina.eliminar"
    NOMINA_VER = "nomina.ver"
    NOMINA_PAGAR = "nomina.pagar"
    
    # GASTOS
    GASTOS_CREAR = "gastos.crear"
    GASTOS_EDITAR = "gastos.editar"
    GASTOS_ELIMINAR = "gastos.eliminar"
    GASTOS_VER = "gastos.ver"
    
    # PRODUCCIÓN
    PRODUCCION_VER = "produccion.ver"
    PRODUCCION_REGISTRAR = "produccion.registrar"
    PRODUCCION_EDITAR = "produccion.editar"
    
    # CIERRES
    CIERRE_REALIZAR = "cierre.realizar"
    CIERRE_REVERTIR = "cierre.revertir"
    CIERRE_VER = "cierre.ver"
    
    # CONFIGURACIÓN
    CONFIG_VER = "config.ver"
    CONFIG_EDITAR = "config.editar"
    CONFIG_USUARIOS = "config.usuarios"
    
    # REPORTES
    REPORTES_VER = "reportes.ver"
    REPORTES_EXPORTAR = "reportes.exportar"
    
    # AUDITORÍA
    AUDITORIA_VER = "auditoria.ver"
    
    def __str__(self):
        return self.value


class PermissionsManager:
    """Gestor centralizado de permisos y roles"""
    
    def __init__(self):
        """Inicializa el gestor de permisos"""
        self.current_user = None
        self.current_role = None
        self._role_permissions: Dict[RoleEnum, Set[PermissionEnum]] = self._init_role_permissions()
        
    def _init_role_permissions(self) -> Dict[RoleEnum, Set[PermissionEnum]]:
        """
        Define los permisos por rol.
        Estructura escalable para agregar más roles/permisos.
        """
        perms = {}
        
        # ADMINISTRADOR - Control total
        perms[RoleEnum.ADMINISTRADOR] = {
            # Ventas
            PermissionEnum.VENTAS_CREAR,
            PermissionEnum.VENTAS_EDITAR,
            PermissionEnum.VENTAS_ELIMINAR,
            PermissionEnum.VENTAS_VER,
            # Nómina
            PermissionEnum.NOMINA_CREAR,
            PermissionEnum.NOMINA_EDITAR,
            PermissionEnum.NOMINA_ELIMINAR,
            PermissionEnum.NOMINA_VER,
            PermissionEnum.NOMINA_PAGAR,
            # Gastos
            PermissionEnum.GASTOS_CREAR,
            PermissionEnum.GASTOS_EDITAR,
            PermissionEnum.GASTOS_ELIMINAR,
            PermissionEnum.GASTOS_VER,
            # Producción
            PermissionEnum.PRODUCCION_VER,
            PermissionEnum.PRODUCCION_REGISTRAR,
            PermissionEnum.PRODUCCION_EDITAR,
            # Cierres
            PermissionEnum.CIERRE_REALIZAR,
            PermissionEnum.CIERRE_REVERTIR,
            PermissionEnum.CIERRE_VER,
            # Configuración
            PermissionEnum.CONFIG_VER,
            PermissionEnum.CONFIG_EDITAR,
            PermissionEnum.CONFIG_USUARIOS,
            # Reportes
            PermissionEnum.REPORTES_VER,
            PermissionEnum.REPORTES_EXPORTAR,
            # Auditoría
            PermissionEnum.AUDITORIA_VER,
        }
        
        # OPERADOR - Operaciones diarias
        perms[RoleEnum.OPERADOR] = {
            # Ventas - crear/editar (no eliminar)
            PermissionEnum.VENTAS_CREAR,
            PermissionEnum.VENTAS_EDITAR,
            PermissionEnum.VENTAS_VER,
            # Nómina - ver/registrar (no pagar ni eliminar)
            PermissionEnum.NOMINA_VER,
            PermissionEnum.NOMINA_CREAR,
            # Gastos
            PermissionEnum.GASTOS_CREAR,
            PermissionEnum.GASTOS_EDITAR,
            PermissionEnum.GASTOS_VER,
            # Producción
            PermissionEnum.PRODUCCION_VER,
            PermissionEnum.PRODUCCION_REGISTRAR,
            PermissionEnum.PRODUCCION_EDITAR,
            # Reportes - solo ver
            PermissionEnum.REPORTES_VER,
            PermissionEnum.CIERRE_VER,
        }
        
        # CONSULTA - Solo lectura
        perms[RoleEnum.CONSULTA] = {
            PermissionEnum.VENTAS_VER,
            PermissionEnum.NOMINA_VER,
            PermissionEnum.GASTOS_VER,
            PermissionEnum.PRODUCCION_VER,
            PermissionEnum.REPORTES_VER,
            PermissionEnum.CIERRE_VER,
        }
        
        # SUPERVISOR - Supervisión (futuro)
        perms[RoleEnum.SUPERVISOR] = perms[RoleEnum.OPERADOR].copy()
        # + permisos de auditoría
        perms[RoleEnum.SUPERVISOR].add(PermissionEnum.AUDITORIA_VER)
        
        return perms
    
    def set_current_user(self, user_id: str, role: RoleEnum):
        """Establece el usuario actual y su rol"""
        self.current_user = user_id
        self.current_role = role
        logger.info(f"Usuario activo: {user_id} (Rol: {role.value})")
    
    def get_current_user(self) -> Optional[str]:
        """Obtiene el usuario actual"""
        return self.current_user
    
    def get_current_role(self) -> Optional[RoleEnum]:
        """Obtiene el rol actual"""
        return self.current_role
    
    def has_permission(self, permission: PermissionEnum) -> bool:
        """
        Verifica si el usuario actual tiene un permiso
        
        Args:
            permission: El permiso a verificar
            
        Returns:
            True si tiene permiso, False caso contrario
        """
        if not self.current_role:
            logger.warning("No hay rol actual establecido")
            return False
        
        has_perm = permission in self._role_permissions.get(self.current_role, set())
        
        if not has_perm:
            logger.warning(
                f"Usuario {self.current_user} ({self.current_role.value}) "
                f"intentó acceder a permiso no autorizado: {permission.value}"
            )
        
        return has_perm
    
    def require_permission(self, permission: PermissionEnum) -> bool:
        """
        Valida un permiso y lanza excepción si no lo tiene
        
        Args:
            permission: El permiso requerido
            
        Raises:
            PermissionDeniedException: Si no tiene el permiso
        """
        if not self.has_permission(permission):
            raise PermissionDeniedException(
                f"Permiso denegado: {permission.value}",
                permission,
                self.current_role
            )
        return True
    
    def get_user_permissions(self, role: Optional[RoleEnum] = None) -> Set[PermissionEnum]:
        """Obtiene todos los permisos de un rol"""
        target_role = role or self.current_role
        if not target_role:
            return set()
        return self._role_permissions.get(target_role, set()).copy()
    
    def can_perform_action(self, module: str, action: str) -> bool:
        """
        Verificación conveniente: módulo.acción
        
        Args:
            module: Módulo (ej: "ventas")
            action: Acción (ej: "crear")
            
        Returns:
            True si puede realizar la acción
        """
        perm_str = f"{module}.{action}"
        try:
            perm = PermissionEnum(perm_str)
            return self.has_permission(perm)
        except ValueError:
            logger.error(f"Permiso inválido: {perm_str}")
            return False


class PermissionDeniedException(Exception):
    """Excepción para acceso denegado"""
    
    def __init__(self, message: str, permission: PermissionEnum, role: Optional[RoleEnum] = None):
        self.message = message
        self.permission = permission
        self.role = role
        super().__init__(self.message)
    
    def get_user_message(self) -> str:
        """Mensaje amigable para el usuario"""
        perm_name = self.permission.value.replace(".", " ").title()
        if self.role:
            return f"Tu rol ({self.role.value}) no tiene permiso para: {perm_name}"
        return f"No tienes permiso para esta acción"


# Instancia singleton global
_permissions_manager: Optional[PermissionsManager] = None


def get_permissions_manager() -> PermissionsManager:
    """Obtiene la instancia singleton del gestor de permisos"""
    global _permissions_manager
    if _permissions_manager is None:
        _permissions_manager = PermissionsManager()
    return _permissions_manager


def reset_permissions_manager():
    """Resetea el gestor de permisos (para tests)"""
    global _permissions_manager
    _permissions_manager = None
