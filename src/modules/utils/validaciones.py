"""
Sistema de Validaciones Centralizado para FincaFacil
Proporciona validaciones uniformes para todos los módulos
"""
import re
from datetime import datetime
from typing import Tuple, Optional, Any
import customtkinter as ctk
from tkinter import messagebox

class Validador:
    """Clase para validaciones centralizadas"""
    
    @staticmethod
    def validar_numerico(valor: str, nombre_campo: str = "Campo", 
                        minimo: Optional[float] = None, 
                        maximo: Optional[float] = None,
                        permitir_vacio: bool = False) -> Tuple[bool, Optional[float], str]:
        """
        Valida que un valor sea numérico
        
        Args:
            valor: Valor a validar
            nombre_campo: Nombre del campo para mensajes de error
            minimo: Valor mínimo permitido (opcional)
            maximo: Valor máximo permitido (opcional)
            permitir_vacio: Si se permite valor vacío
            
        Returns:
            Tupla (es_valido, valor_convertido, mensaje_error)
        """
        # Verificar si está vacío
        if not valor or valor.strip() == "":
            if permitir_vacio:
                return True, None, ""
            return False, None, f"{nombre_campo} no puede estar vacío"
        
        # Intentar convertir a float
        try:
            numero = float(valor.strip())
        except ValueError:
            return False, None, f"{nombre_campo} debe ser un número válido"
        
        # Validar rango mínimo
        if minimo is not None and numero < minimo:
            return False, None, f"{nombre_campo} debe ser mayor o igual a {minimo}"
        
        # Validar rango máximo
        if maximo is not None and numero > maximo:
            return False, None, f"{nombre_campo} debe ser menor o igual a {maximo}"
        
        return True, numero, ""
    
    @staticmethod
    def validar_entero(valor: str, nombre_campo: str = "Campo",
                      minimo: Optional[int] = None,
                      maximo: Optional[int] = None,
                      permitir_vacio: bool = False) -> Tuple[bool, Optional[int], str]:
        """
        Valida que un valor sea un entero
        
        Returns:
            Tupla (es_valido, valor_convertido, mensaje_error)
        """
        if not valor or valor.strip() == "":
            if permitir_vacio:
                return True, None, ""
            return False, None, f"{nombre_campo} no puede estar vacío"
        
        try:
            numero = int(valor.strip())
        except ValueError:
            return False, None, f"{nombre_campo} debe ser un número entero"
        
        if minimo is not None and numero < minimo:
            return False, None, f"{nombre_campo} debe ser mayor o igual a {minimo}"
        
        if maximo is not None and numero > maximo:
            return False, None, f"{nombre_campo} debe ser menor o igual a {maximo}"
        
        return True, numero, ""
    
    @staticmethod
    def validar_fecha(valor: str, nombre_campo: str = "Fecha",
                     formato: str = "%Y-%m-%d",
                     permitir_vacio: bool = False,
                     fecha_minima: Optional[datetime] = None,
                     fecha_maxima: Optional[datetime] = None) -> Tuple[bool, Optional[datetime], str]:
        """
        Valida que un valor sea una fecha válida
        
        Returns:
            Tupla (es_valido, fecha_convertida, mensaje_error)
        """
        if not valor or valor.strip() == "":
            if permitir_vacio:
                return True, None, ""
            return False, None, f"{nombre_campo} no puede estar vacía"
        
        try:
            fecha = datetime.strptime(valor.strip(), formato)
        except ValueError:
            return False, None, f"{nombre_campo} debe tener formato válido ({formato})"
        
        if fecha_minima and fecha < fecha_minima:
            return False, None, f"{nombre_campo} no puede ser anterior a {fecha_minima.strftime(formato)}"
        
        if fecha_maxima and fecha > fecha_maxima:
            return False, None, f"{nombre_campo} no puede ser posterior a {fecha_maxima.strftime(formato)}"
        
        return True, fecha, ""
    
    @staticmethod
    def validar_texto(valor: str, nombre_campo: str = "Campo",
                     min_longitud: Optional[int] = None,
                     max_longitud: Optional[int] = None,
                     permitir_vacio: bool = False,
                     solo_letras: bool = False,
                     solo_alfanumerico: bool = False) -> Tuple[bool, str, str]:
        """
        Valida un campo de texto
        
        Returns:
            Tupla (es_valido, valor_limpio, mensaje_error)
        """
        if not valor or valor.strip() == "":
            if permitir_vacio:
                return True, "", ""
            return False, "", f"{nombre_campo} no puede estar vacío"
        
        texto_limpio = valor.strip()
        
        if min_longitud and len(texto_limpio) < min_longitud:
            return False, "", f"{nombre_campo} debe tener al menos {min_longitud} caracteres"
        
        if max_longitud and len(texto_limpio) > max_longitud:
            return False, "", f"{nombre_campo} no puede tener más de {max_longitud} caracteres"
        
        if solo_letras and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', texto_limpio):
            return False, "", f"{nombre_campo} solo puede contener letras"
        
        if solo_alfanumerico and not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+$', texto_limpio):
            return False, "", f"{nombre_campo} solo puede contener letras y números"
        
        return True, texto_limpio, ""
    
    @staticmethod
    def validar_email(valor: str, nombre_campo: str = "Email",
                     permitir_vacio: bool = False) -> Tuple[bool, str, str]:
        """
        Valida que un valor sea un email válido
        
        Returns:
            Tupla (es_valido, email_limpio, mensaje_error)
        """
        if not valor or valor.strip() == "":
            if permitir_vacio:
                return True, "", ""
            return False, "", f"{nombre_campo} no puede estar vacío"
        
        email = valor.strip().lower()
        
        # Patrón básico de email
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, email):
            return False, "", f"{nombre_campo} no tiene un formato válido"
        
        return True, email, ""
    
    @staticmethod
    def validar_telefono(valor: str, nombre_campo: str = "Teléfono",
                        permitir_vacio: bool = False) -> Tuple[bool, str, str]:
        """
        Valida un número de teléfono
        
        Returns:
            Tupla (es_valido, telefono_limpio, mensaje_error)
        """
        if not valor or valor.strip() == "":
            if permitir_vacio:
                return True, "", ""
            return False, "", f"{nombre_campo} no puede estar vacío"
        
        # Limpiar caracteres no numéricos excepto + - ( ) espacios
        telefono_limpio = re.sub(r'[^\d+\-() ]', '', valor.strip())
        
        # Contar solo dígitos
        digitos = re.sub(r'\D', '', telefono_limpio)
        
        if len(digitos) < 7:
            return False, "", f"{nombre_campo} debe tener al menos 7 dígitos"
        
        if len(digitos) > 15:
            return False, "", f"{nombre_campo} no puede tener más de 15 dígitos"
        
        return True, telefono_limpio, ""
    
    @staticmethod
    def validar_codigo_unico(valor: str, nombre_campo: str = "Código",
                            longitud_exacta: Optional[int] = None) -> Tuple[bool, str, str]:
        """
        Valida un código único (solo letras, números, guiones)
        
        Returns:
            Tupla (es_valido, codigo_limpio, mensaje_error)
        """
        if not valor or valor.strip() == "":
            return False, "", f"{nombre_campo} no puede estar vacío"
        
        codigo = valor.strip().upper()
        
        # Solo alfanumérico y guiones
        if not re.match(r'^[A-Z0-9-]+$', codigo):
            return False, "", f"{nombre_campo} solo puede contener letras, números y guiones"
        
        if longitud_exacta and len(codigo) != longitud_exacta:
            return False, "", f"{nombre_campo} debe tener exactamente {longitud_exacta} caracteres"
        
        return True, codigo, ""


class ValidadorFormulario:
    """Clase auxiliar para validar formularios completos"""
    
    def __init__(self):
        self.errores = []
    
    def agregar_validacion(self, es_valido: bool, mensaje_error: str):
        """Agrega el resultado de una validación"""
        if not es_valido:
            self.errores.append(mensaje_error)
    
    def es_valido(self) -> bool:
        """Retorna True si no hay errores"""
        return len(self.errores) == 0
    
    def mostrar_errores(self, titulo: str = "Errores de Validación"):
        """Muestra los errores acumulados en un messagebox"""
        if self.errores:
            mensaje = "\n\n".join([f"• {error}" for error in self.errores])
            messagebox.showerror(titulo, mensaje)
    
    def limpiar(self):
        """Limpia la lista de errores"""
        self.errores = []


class EntryValidado(ctk.CTkEntry):
    """Entry con validación en tiempo real"""
    
    def __init__(self, master, tipo_validacion: str = "texto", **kwargs):
        """
        Args:
            master: Widget padre
            tipo_validacion: 'numerico', 'entero', 'texto', 'email', 'telefono'
            **kwargs: Argumentos adicionales para CTkEntry
        """
        super().__init__(master, **kwargs)
        self.tipo_validacion = tipo_validacion
        self.validador = Validador()
        
        # Configurar validación en tiempo real
        self.bind("<FocusOut>", self._validar_en_salida)
    
    def _validar_en_salida(self, event):
        """Valida cuando el usuario sale del campo"""
        valor = self.get()
        
        if self.tipo_validacion == "numerico":
            es_valido, _, mensaje = self.validador.validar_numerico(
                valor, permitir_vacio=True
            )
        elif self.tipo_validacion == "entero":
            es_valido, _, mensaje = self.validador.validar_entero(
                valor, permitir_vacio=True
            )
        elif self.tipo_validacion == "email":
            es_valido, _, mensaje = self.validador.validar_email(
                valor, permitir_vacio=True
            )
        elif self.tipo_validacion == "telefono":
            es_valido, _, mensaje = self.validador.validar_telefono(
                valor, permitir_vacio=True
            )
        else:
            es_valido = True
            mensaje = ""
        
        # Cambiar color de borde si hay error
        if not es_valido and valor:
            self.configure(border_color="red")
        else:
            self.configure(border_color=("gray70", "gray30"))
    
    def validar(self, nombre_campo: str = "Campo", 
                permitir_vacio: bool = False) -> Tuple[bool, Any, str]:
        """
        Valida el contenido actual del Entry
        
        Returns:
            Tupla (es_valido, valor_convertido, mensaje_error)
        """
        valor = self.get()
        
        if self.tipo_validacion == "numerico":
            return self.validador.validar_numerico(
                valor, nombre_campo, permitir_vacio=permitir_vacio
            )
        elif self.tipo_validacion == "entero":
            return self.validador.validar_entero(
                valor, nombre_campo, permitir_vacio=permitir_vacio
            )
        elif self.tipo_validacion == "email":
            return self.validador.validar_email(
                valor, nombre_campo, permitir_vacio=permitir_vacio
            )
        elif self.tipo_validacion == "telefono":
            return self.validador.validar_telefono(
                valor, nombre_campo, permitir_vacio=permitir_vacio
            )
        else:
            return self.validador.validar_texto(
                valor, nombre_campo, permitir_vacio=permitir_vacio
            )


# Funciones de conveniencia para uso rápido
def validar_peso(valor: str) -> Tuple[bool, Optional[float], str]:
    """Valida un peso (kg)"""
    return Validador.validar_numerico(valor, "Peso", minimo=0, maximo=2000)

def validar_precio(valor: str) -> Tuple[bool, Optional[float], str]:
    """Valida un precio"""
    return Validador.validar_numerico(valor, "Precio", minimo=0)

def validar_cantidad(valor: str) -> Tuple[bool, Optional[int], str]:
    """Valida una cantidad entera"""
    return Validador.validar_entero(valor, "Cantidad", minimo=0)

def validar_produccion_leche(valor: str) -> Tuple[bool, Optional[float], str]:
    """Valida producción de leche en litros"""
    return Validador.validar_numerico(valor, "Producción", minimo=0, maximo=100)


# Funciones de validación adicionales para compatibilidad
def validar_texto(valor: str, nombre_campo: str = "Campo", minimo: Optional[int] = None,
                 maximo: Optional[int] = None, permitir_vacio: bool = False) -> Tuple[bool, Optional[str], str]:
    """Valida texto genérico."""
    return Validador.validar_texto(valor, nombre_campo, minimo, maximo, permitir_vacio)


def validar_numero(valor: str, nombre_campo: str = "Campo", minimo: Optional[float] = None,
                  maximo: Optional[float] = None) -> Tuple[bool, Optional[float], str]:
    """Valida números."""
    return Validador.validar_numerico(valor, nombre_campo, minimo, maximo)


def validar_email(email: str) -> Tuple[bool, Optional[str], str]:
    """Valida formato de correo electrónico."""
    return Validador.validar_email(email)


def validar_telefono(telefono: str) -> Tuple[bool, Optional[str], str]:
    """Valida formato de teléfono."""
    return Validador.validar_telefono(telefono)
