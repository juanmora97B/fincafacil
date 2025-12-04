"""
Validadores centralizados para FincaFacil
Consolidación de módulos/utils/validaciones.py y módulos/utils/validators.py
"""

from typing import Optional, Any, Union
from datetime import datetime
import logging
from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class DataValidator:
    """Validador centralizado para datos del sistema"""

    # ==========================================
    # VALIDACIONES DE PESO
    # ==========================================
    
    @staticmethod
    def validate_peso(peso: Union[int, float], min_val: float = 0, max_val: float = 2000) -> bool:
        """
        Valida peso de animales
        
        Args:
            peso: Peso a validar
            min_val: Peso mínimo permitido
            max_val: Peso máximo permitido
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si el peso es inválido
        """
        if peso is None:
            raise ValidationError("El peso no puede estar vacío")
        
        try:
            peso_float = float(peso)
        except (ValueError, TypeError):
            raise ValidationError("El peso debe ser un número válido")
        
        if not (min_val <= peso_float <= max_val):
            raise ValidationError(f"Peso fuera de rango ({min_val}-{max_val} kg)")
        
        return True

    @staticmethod
    def validate_peso_nacimiento(peso: Union[int, float]) -> bool:
        """Valida peso de nacimiento (15-60 kg)"""
        return DataValidator.validate_peso(peso, 15, 60)

    @staticmethod
    def validate_peso_compra(peso: Union[int, float]) -> bool:
        """Valida peso de compra (50-1000 kg)"""
        return DataValidator.validate_peso(peso, 50, 1000)

    # ==========================================
    # VALIDACIONES DE FECHA
    # ==========================================
    
    @staticmethod
    def validate_fecha(fecha: str, format: str = "%Y-%m-%d") -> bool:
        """
        Valida formato de fecha
        
        Args:
            fecha: Fecha a validar
            format: Formato esperado (default: YYYY-MM-DD)
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValidationError: Si la fecha es inválida
        """
        if not fecha or not isinstance(fecha, str):
            raise ValidationError("La fecha debe ser texto")
        
        try:
            datetime.strptime(fecha, format)
            return True
        except ValueError:
            raise ValidationError(f"Formato de fecha inválido (use {format})")

    @staticmethod
    def validate_fecha_no_futura(fecha: str) -> bool:
        """Valida que la fecha no sea futura"""
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            if fecha_obj > datetime.now():
                raise ValidationError("La fecha no puede ser futura")
            return True
        except ValueError as e:
            raise ValidationError(f"Error validando fecha: {str(e)}")

    # ==========================================
    # VALIDACIONES DE CÓDIGO/ID
    # ==========================================
    
    @staticmethod
    def validate_codigo_unico(codigo: str, tabla: str, conn, column: str = "codigo") -> bool:
        """
        Valida que un código sea único en una tabla
        
        Args:
            codigo: Código a validar
            tabla: Tabla donde verificar
            conn: Conexión a BD
            column: Nombre de la columna (default: 'codigo')
            
        Returns:
            bool: True si es único
            
        Raises:
            ValidationError: Si el código ya existe
        """
        if not codigo or not isinstance(codigo, str):
            raise ValidationError("El código debe ser texto no vacío")
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {column} = ?", (codigo,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                raise ValidationError(f"El código '{codigo}' ya existe en {tabla}")
            return True
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Error verificando código: {str(e)}")

    # ==========================================
    # VALIDACIONES DE TEXTO
    # ==========================================
    
    @staticmethod
    def validate_nombre(nombre: str, min_len: int = 1, max_len: int = 255) -> bool:
        """Valida nombre/descripción"""
        if not nombre or not isinstance(nombre, str):
            raise ValidationError("El nombre debe ser texto no vacío")
        
        if len(nombre) < min_len or len(nombre) > max_len:
            raise ValidationError(f"Nombre debe tener entre {min_len} y {max_len} caracteres")
        
        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email or not isinstance(email, str):
            raise ValidationError("El email debe ser texto no vacío")
        
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError(f"Email inválido: {email}")
        
        return True

    # ==========================================
    # VALIDACIONES NUMÉRICAS
    # ==========================================
    
    @staticmethod
    def validate_numero(valor: Union[int, float], min_val: Optional[float] = None, 
                       max_val: Optional[float] = None) -> bool:
        """Valida número dentro de rango"""
        try:
            num = float(valor)
        except (ValueError, TypeError):
            raise ValidationError("Debe ser un número válido")
        
        if min_val is not None and num < min_val:
            raise ValidationError(f"Valor no puede ser menor a {min_val}")
        
        if max_val is not None and num > max_val:
            raise ValidationError(f"Valor no puede ser mayor a {max_val}")
        
        return True

    # ==========================================
    # VALIDACIONES DE RANGO
    # ==========================================
    
    @staticmethod
    def validate_rango(valor: Any, lista_valida: list, campo: str = "valor") -> bool:
        """Valida que el valor esté en una lista específica"""
        if valor not in lista_valida:
            raise ValidationError(f"{campo} inválido. Valores permitidos: {', '.join(map(str, lista_valida))}")
        return True

    # ==========================================
    # VALIDACIONES LÓGICAS
    # ==========================================
    
    @staticmethod
    def validate_required(*fields) -> bool:
        """Valida que los campos sean requeridos"""
        for field_name, field_value in fields:
            if not field_value:
                raise ValidationError(f"{field_name} es requerido")
        return True

    @staticmethod
    def validate_relacion(id_padre: int, tabla_padre: str, conn, column: str = "id") -> bool:
        """Valida que una relación exista"""
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {tabla_padre} WHERE {column} = ?", (id_padre,))
            if cursor.fetchone()[0] == 0:
                raise ValidationError(f"Registro {id_padre} no encontrado en {tabla_padre}")
            return True
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Error validando relación: {str(e)}")


# ============================================
# FUNCIONES LEGACY PARA COMPATIBILIDAD
# ============================================

def validar_peso_nacimiento(peso):
    """DEPRECADO: Usar DataValidator.validate_peso_nacimiento()"""
    return DataValidator.validate_peso_nacimiento(peso)

def validar_peso_compra(peso):
    """DEPRECADO: Usar DataValidator.validate_peso_compra()"""
    return DataValidator.validate_peso_compra(peso)

def validar_fecha_no_futura(fecha):
    """DEPRECADO: Usar DataValidator.validate_fecha_no_futura()"""
    return DataValidator.validate_fecha_no_futura(fecha)

def validar_codigo_unico(codigo, tabla, conn):
    """DEPRECADO: Usar DataValidator.validate_codigo_unico()"""
    return DataValidator.validate_codigo_unico(codigo, tabla, conn)
