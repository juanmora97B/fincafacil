"""
Sistema centralizado de validación para FincaFacil
Valida datos antes de insertar en la base de datos

NOTA: Este módulo (modules.utils.validators) es la FUENTE OFICIAL de validación.
Todas las validaciones de negocio deben definirse aquí.
Ver docs/CONTRATO_VALIDACIONES.md para contrato de APIs.
"""

import re
from datetime import datetime, date

# Importación segura de la base de datos - CORREGIDA
try:
    # Importación absoluta desde el directorio raíz
    from database.database import get_db_connection
    DB_DISPONIBLE = True
except ImportError as e:
    # Modo de prueba sin base de datos
    DB_DISPONIBLE = False
    print(f"⚠️ Modo de validación sin base de datos - no se verificará unicidad: {e}")

class ValidadorBase:
    """Clase base para validadores. No contiene lógica de validación."""


class FincaFacilValidator(ValidadorBase):
    """Validador principal para todos los datos del sistema.
    
    CONTRATO: Ver docs/CONTRATO_VALIDACIONES.md
    Esta es la implementación oficial de validaciones.
    Todas las firmas están congeladas.
    """
    
    # Patrones de validación
    PATRON_ARETE = re.compile(r'^[A-Za-z0-9\-_]{3,20}$')  # 3-20 chars alfanuméricos
    PATRON_CODIGO = re.compile(r'^[A-Za-z0-9]{2,10}$')    # 2-10 chars alfanuméricos
    PATRON_TELEFONO = re.compile(r'^[\d\s\+\-\(\)]{7,15}$')
    PATRON_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validar_arete(arete, animal_id=None):
        """
        Valida que un arete sea único y tenga formato correcto
        
        Args:
            arete (str): Número de arete a validar
            animal_id (int, optional): ID del animal (para exclusión en actualizaciones)
        
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        try:
            # Validar formato
            if not arete or not arete.strip():
                return False, "El arete no puede estar vacío"
            
            arete = arete.strip().upper()
            
            if not FincaFacilValidator.PATRON_ARETE.match(arete):
                return False, "Formato de arete inválido. Use 3-20 caracteres alfanuméricos"
            
            # Validar unicidad solo si la BD está disponible
            if not DB_DISPONIBLE:
                return True, "Arete válido (modo prueba - BD no disponible)"
            
            # Validar unicidad en la base de datos
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if animal_id:
                    # Para actualización: excluir el animal actual
                    cursor.execute(
                        "SELECT id FROM animal WHERE codigo = ? AND id != ?", 
                        (arete, animal_id)
                    )
                else:
                    # Para nuevo registro
                    cursor.execute(
                        "SELECT id FROM animal WHERE codigo = ?", 
                        (arete,)
                    )
                
                if cursor.fetchone():
                    return False, f"El arete '{arete}' ya existe en el sistema"
            
            return True, "Arete válido"
            
        except Exception as e:
            return False, f"Error validando arete: {e}"
    
    @staticmethod
    def validar_peso(peso, tipo="cualquiera"):
        """
        Valida que un peso sea razonable según el tipo
        
        Args:
            peso (float): Peso a validar
            tipo (str): 'ternero', 'adulto', 'cualquiera'
        
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        try:
            peso = float(peso)
            
            if peso <= 0:
                return False, "El peso debe ser mayor a 0"
            
            # Límites según tipo de animal
            limites = {
                'ternero': (10, 200),    # 10-200 kg para terneros
                'adulto': (200, 1500),   # 200-1500 kg para adultos
                'cualquiera': (1, 2000)  # 1-2000 kg límite general
            }
            
            min_peso, max_peso = limites.get(tipo, (1, 2000))
            
            if not (min_peso <= peso <= max_peso):
                return False, f"Peso fuera de rango. Debe estar entre {min_peso} y {max_peso} kg"
            
            return True, "Peso válido"
            
        except (ValueError, TypeError):
            return False, "El peso debe ser un número válido"
    
    @staticmethod
    def validar_fecha(fecha_str, fecha_min=None, fecha_max=None):
        """
        Valida una fecha y su rango
        
        Args:
            fecha_str (str): Fecha en formato YYYY-MM-DD
            fecha_min (str, optional): Fecha mínima permitida
            fecha_max (str, optional): Fecha máxima permitida
        
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        try:
            if not fecha_str:
                return True, "Fecha opcional"  # Fechas pueden ser opcionales
            
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hoy = date.today()
            
            # Validar que no sea fecha futura (para la mayoría de casos)
            if fecha > hoy:
                return False, "La fecha no puede ser futura"
            
            # Validar rangos personalizados
            if fecha_min:
                fecha_min_obj = datetime.strptime(fecha_min, '%Y-%m-%d').date()
                if fecha < fecha_min_obj:
                    return False, f"La fecha no puede ser anterior a {fecha_min}"
            
            if fecha_max:
                fecha_max_obj = datetime.strptime(fecha_max, '%Y-%m-%d').date()
                if fecha > fecha_max_obj:
                    return False, f"La fecha no puede ser posterior a {fecha_max}"
            
            return True, "Fecha válida"
            
        except ValueError:
            return False, "Formato de fecha inválido. Use YYYY-MM-DD"
    
    @staticmethod
    def validar_codigo_unico(codigo, tabla, campo='codigo', registro_id=None):
        """
        Valida que un código sea único en cualquier tabla
        
        Args:
            codigo (str): Código a validar
            tabla (str): Nombre de la tabla
            campo (str): Nombre del campo (default 'codigo')
            registro_id (int, optional): ID para excluir en actualizaciones
        
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        try:
            if not codigo or not codigo.strip():
                return False, "El código no puede estar vacío"
            
            codigo = codigo.strip().upper()
            
            if not FincaFacilValidator.PATRON_CODIGO.match(codigo):
                return False, "Formato de código inválido. Use 2-10 caracteres alfanuméricos"
            
            # Validar unicidad solo si la BD está disponible
            if not DB_DISPONIBLE:
                return True, f"Código válido (modo prueba - {tabla})"
            
            # Validar unicidad
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if registro_id:
                    cursor.execute(
                        f"SELECT id FROM {tabla} WHERE {campo} = ? AND id != ?", 
                        (codigo, registro_id)
                    )
                else:
                    cursor.execute(
                        f"SELECT id FROM {tabla} WHERE {campo} = ?", 
                        (codigo,)
                    )
                
                if cursor.fetchone():
                    return False, f"El código '{codigo}' ya existe en {tabla}"
            
            return True, "Código válido"
            
        except Exception as e:
            return False, f"Error validando código: {e}"
    
    @staticmethod
    def validar_telefono(telefono):
        """Valida formato de teléfono"""
        if not telefono:
            return True, "Teléfono opcional"
        
        telefono = telefono.strip()
        
        if not FincaFacilValidator.PATRON_TELEFONO.match(telefono):
            return False, "Formato de teléfono inválido"
        
        return True, "Teléfono válido"
    
    @staticmethod
    def validar_email(email):
        """Valida formato de email"""
        if not email:
            return True, "Email opcional"
        
        email = email.strip().lower()
        
        if not FincaFacilValidator.PATRON_EMAIL.match(email):
            return False, "Formato de email inválido"
        
        return True, "Email válido"
    
    @staticmethod
    def validar_valor_monetario(valor, minimo=0, maximo=100000000):
        """
        Valida un valor monetario
        
        Args:
            valor (float): Valor a validar
            minimo (float): Valor mínimo permitido
            maximo (float): Valor máximo permitido
        
        Returns:
            tuple: (bool, str) - (es_válido, mensaje_error)
        """
        try:
            valor = float(valor)
            
            if valor < minimo:
                return False, f"El valor no puede ser menor a {minimo:,.0f}"
            
            if valor > maximo:
                return False, f"El valor no puede ser mayor a {maximo:,.0f}"
            
            return True, "Valor monetario válido"
            
        except (ValueError, TypeError):
            return False, "El valor debe ser un número válido"

class AnimalValidator(FincaFacilValidator):
    """Validador especializado para datos de animales"""
    
    @staticmethod
    def validar_animal_completo(datos_animal):
        """
        Valida todos los datos de un animal antes de guardar
        
        Args:
            datos_animal (dict): Diccionario con datos del animal
        
        Returns:
            tuple: (bool, list) - (es_válido, lista_errores)
        """
        errores = []
        
        # Validar arete
        es_valido, mensaje = AnimalValidator.validar_arete(
            datos_animal.get('codigo'), 
            datos_animal.get('id')
        )
        if not es_valido:
            errores.append(f"Arete: {mensaje}")
        
        # Validar peso si existe
        if datos_animal.get('peso_nacimiento'):
            es_valido, mensaje = AnimalValidator.validar_peso(
                datos_animal.get('peso_nacimiento'), 'ternero'
            )
            if not es_valido:
                errores.append(f"Peso nacimiento: {mensaje}")
        
        if datos_animal.get('peso_compra'):
            es_valido, mensaje = AnimalValidator.validar_peso(
                datos_animal.get('peso_compra'), 'adulto'
            )
            if not es_valido:
                errores.append(f"Peso compra: {mensaje}")
        
        # Validar fechas
        if datos_animal.get('fecha_nacimiento'):
            es_valido, mensaje = AnimalValidator.validar_fecha(
                datos_animal.get('fecha_nacimiento')
            )
            if not es_valido:
                errores.append(f"Fecha nacimiento: {mensaje}")
        
        if datos_animal.get('fecha_compra'):
            es_valido, mensaje = AnimalValidator.validar_fecha(
                datos_animal.get('fecha_compra')
            )
            if not es_valido:
                errores.append(f"Fecha compra: {mensaje}")
        
        # Validar precio si existe
        if datos_animal.get('precio_compra'):
            es_valido, mensaje = AnimalValidator.validar_valor_monetario(
                datos_animal.get('precio_compra')
            )
            if not es_valido:
                errores.append(f"Precio compra: {mensaje}")
        
        return len(errores) == 0, errores

# Instancia global para uso fácil
validator = FincaFacilValidator()
animal_validator = AnimalValidator()