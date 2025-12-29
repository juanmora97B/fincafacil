"""
SERVICIO DE VALIDACIÓN CON PERMISOS - FincaFácil
=================================================

Valida operaciones considerando:
- Permisos del usuario
- Integridad de datos
- Restricciones de negocio
- Estado de cierres mensuales
"""

import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime, date
from enum import Enum

from core.permissions_manager import (
    get_permissions_manager, 
    PermissionEnum, 
    PermissionDeniedException
)

logger = logging.getLogger(__name__)


class ValidationResult:
    """Resultado de una validación"""
    
    def __init__(self, valid: bool, message: str = "", details: Dict[str, Any] | None = None):
        self.valid = valid
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def __bool__(self):
        return self.valid
    
    def to_dict(self):
        return {
            "valid": self.valid,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class ValidationService:
    """Servicio de validación con control de permisos"""
    
    def __init__(self):
        self.pm = get_permissions_manager()
    
    # ==================== VENTAS ====================
    
    def validar_creacion_venta(self, venta_data: Dict[str, Any]) -> ValidationResult:
        """Valida creación de venta"""
        # Validar permiso
        try:
            self.pm.require_permission(PermissionEnum.VENTAS_CREAR)
        except PermissionDeniedException as e:
            logger.warning(f"Venta rechazada por permisos: {e.message}")
            return ValidationResult(False, e.get_user_message())
        
        # Validar campos requeridos
        campos_requeridos = ["animal_id", "fecha", "precio", "comprador"]
        for campo in campos_requeridos:
            if campo not in venta_data or not venta_data[campo]:
                return ValidationResult(False, f"Campo requerido faltante: {campo}")
        
        # Validar que la venta no sea de un mes cerrado
        fecha_venta = datetime.fromisoformat(venta_data["fecha"])
        if self._es_mes_cerrado(fecha_venta.year, fecha_venta.month, "ventas"):
            return ValidationResult(
                False,
                f"No puedes crear ventas en meses cerrados ({fecha_venta.month}/{fecha_venta.year})"
            )
        
        # Validar que el animal existe y está disponible
        try:
            from database.database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, estado FROM animal WHERE id = ?", (venta_data["animal_id"],))
                animal = cursor.fetchone()
                
                if not animal:
                    return ValidationResult(False, f"Animal {venta_data['animal_id']} no existe")
                
                if animal[1] not in ["Activo", "Disponible"]:
                    return ValidationResult(False, f"Animal no disponible para venta (estado: {animal[1]})")
        
        except Exception as e:
            logger.error(f"Error validando animal: {e}")
            return ValidationResult(False, f"Error verificando disponibilidad del animal")
        
        logger.info(f"✅ Venta validada - Animal {venta_data['animal_id']}")
        return ValidationResult(True, "Venta válida")
    
    def validar_edicion_venta(self, venta_id: int, cambios: Dict[str, Any]) -> ValidationResult:
        """Valida edición de venta"""
        # Validar permiso
        try:
            self.pm.require_permission(PermissionEnum.VENTAS_EDITAR)
        except PermissionDeniedException as e:
            return ValidationResult(False, e.get_user_message())
        
        # Validar que no sea de un mes cerrado
        try:
            from database.database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT fecha FROM venta WHERE id = ?", (venta_id,))
                venta = cursor.fetchone()
                
                if not venta:
                    return ValidationResult(False, f"Venta {venta_id} no existe")
                
                fecha_venta = datetime.fromisoformat(venta[0])
                if self._es_mes_cerrado(fecha_venta.year, fecha_venta.month, "ventas"):
                    return ValidationResult(False, "No puedes editar ventas de meses cerrados")
        
        except Exception as e:
            logger.error(f"Error validando venta: {e}")
            return ValidationResult(False, "Error verificando venta")
        
        logger.info(f"✅ Edición de venta validada - Venta {venta_id}")
        return ValidationResult(True, "Edición válida")
    
    # ==================== NÓMINA ====================
    
    def validar_pago_nomina(self, nomina_data: Dict[str, Any]) -> ValidationResult:
        """Valida pago de nómina"""
        # Validar permiso especial
        try:
            self.pm.require_permission(PermissionEnum.NOMINA_PAGAR)
        except PermissionDeniedException as e:
            return ValidationResult(False, e.get_user_message())
        
        # Validar campos
        campos_requeridos = ["empleado_id", "periodo", "monto"]
        for campo in campos_requeridos:
            if campo not in nomina_data:
                return ValidationResult(False, f"Campo requerido: {campo}")
        
        # Validar que no sea de un mes cerrado
        periodo = nomina_data["periodo"]  # Formato: "2024-12"
        año, mes = map(int, periodo.split("-"))
        
        if self._es_mes_cerrado(año, mes, "nomina"):
            return ValidationResult(False, f"No puedes pagar nómina en meses cerrados ({mes}/{año})")
        
        logger.info(f"✅ Pago de nómina validado - Empleado {nomina_data.get('empleado_id')}")
        return ValidationResult(True, "Pago válido")
    
    # ==================== CIERRES ====================
    
    def validar_cierre_mensual(self, año: int, mes: int) -> ValidationResult:
        """Valida si se puede hacer cierre mensual"""
        # Validar permiso
        try:
            self.pm.require_permission(PermissionEnum.CIERRE_REALIZAR)
        except PermissionDeniedException as e:
            return ValidationResult(False, e.get_user_message())
        
        # Validar que ya no esté cerrado
        try:
            from database.database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM cierre_mensual 
                    WHERE año = ? AND mes = ?
                """, (año, mes))
                
                if cursor.fetchone():
                    return ValidationResult(False, f"Mes {mes}/{año} ya está cerrado")
        
        except Exception as e:
            logger.error(f"Error validando cierre: {e}")
            return ValidationResult(False, "Error verificando estado del cierre")
        
        logger.info(f"✅ Cierre mensual validado - {mes}/{año}")
        return ValidationResult(True, "Cierre válido")
    
    # ==================== UTILIDADES ====================
    
    def _es_mes_cerrado(self, año: int, mes: int, modulo: str) -> bool:
        """Verifica si un mes está cerrado para un módulo"""
        try:
            from database.database import get_db_connection
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM datos_cerrados
                    WHERE año = ? AND mes = ? AND modulo = ?
                """, (año, mes, modulo))
                
                return cursor.fetchone()[0] > 0
        
        except Exception as e:
            logger.warning(f"Error verificando cierre: {e}")
            return False
    
    def get_validations_summary(self) -> str:
        """Obtiene resumen de validaciones en el sistema"""
        user_perms = self.pm.get_user_permissions()
        current_role = self.pm.get_current_role()
        
        role_name = current_role.value if current_role else "Sin asignar"
        summary = f"Validaciones activas para {role_name}:\n"
        summary += f"  - Permisos: {len(user_perms)}\n"
        summary += f"  - Control de cierres: Sí\n"
        summary += f"  - Validación de integridad: Sí\n"
        
        return summary


# Instancia singleton
_validation_service: ValidationService | None = None


def get_validation_service() -> ValidationService:
    """Obtiene la instancia del servicio de validación"""
    global _validation_service
    if _validation_service is None:
        _validation_service = ValidationService()
    return _validation_service
