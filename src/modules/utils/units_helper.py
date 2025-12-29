"""
Sistema de conversión y formato de unidades para FincaFacil
Lee preferencias de app_settings y convierte/formatea valores
REFACTOR FASE 7.5: Usa inyección de DbConnectionService en lugar de acceso directo a BD.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.services import get_db_service


class UnitsHelper:
    """Helper para conversión y formato de unidades según preferencias del usuario"""
    
    # Factores de conversión
    KG_TO_LB = 2.20462
    L_TO_GAL = 0.264172
    
    def __init__(self):
        self.weight_unit = "kg"
        self.volume_unit = "L"
        self.db_service = get_db_service()
        self._load_preferences()
    
    def _load_preferences(self):
        """Carga las preferencias de unidades desde la base de datos"""
        try:
            with self.db_service.connection() as conn:
                cursor = conn.cursor()
                
                # Unidad de peso
                cursor.execute("SELECT valor FROM app_settings WHERE clave = 'units_weight'")
                row = cursor.fetchone()
                if row and row[0]:
                    self.weight_unit = row[0].strip()
                
                # Unidad de volumen
                cursor.execute("SELECT valor FROM app_settings WHERE clave = 'units_volume'")
                row = cursor.fetchone()
                if row and row[0]:
                    self.volume_unit = row[0].strip()
                    
        except Exception as e:
            print(f"Error al cargar preferencias de unidades: {e}")
    
    def format_weight(self, weight_kg, decimal_places=2, include_unit=True):
        """
        Formatea un peso según la unidad preferida del usuario
        
        Args:
            weight_kg: Peso en kilogramos (formato almacenado en BD)
            decimal_places: Decimales a mostrar
            include_unit: Si incluir la unidad en el string de salida
            
        Returns:
            str: Peso formateado
        """
        if weight_kg is None:
            return "N/A"
        
        try:
            weight_kg = float(weight_kg)
            
            if self.weight_unit == "lb":
                weight_display = weight_kg * self.KG_TO_LB
                unit = " lb" if include_unit else ""
            else:
                weight_display = weight_kg
                unit = " kg" if include_unit else ""
            
            return f"{weight_display:.{decimal_places}f}{unit}"
        except (ValueError, TypeError):
            return "N/A"
    
    def format_volume(self, volume_l, decimal_places=2, include_unit=True):
        """
        Formatea un volumen según la unidad preferida del usuario
        
        Args:
            volume_l: Volumen en litros (formato almacenado en BD)
            decimal_places: Decimales a mostrar
            include_unit: Si incluir la unidad en el string de salida
            
        Returns:
            str: Volumen formateado
        """
        if volume_l is None:
            return "N/A"
        
        try:
            volume_l = float(volume_l)
            
            if self.volume_unit == "gal":
                volume_display = volume_l * self.L_TO_GAL
                unit = " gal" if include_unit else ""
            else:
                volume_display = volume_l
                unit = " L" if include_unit else ""
            
            return f"{volume_display:.{decimal_places}f}{unit}"
        except (ValueError, TypeError):
            return "N/A"
    
    def convert_weight_to_kg(self, weight_value, from_unit=None):
        """
        Convierte un peso a kilogramos para almacenar en BD
        
        Args:
            weight_value: Valor numérico del peso
            from_unit: Unidad de origen (si None, usa la preferencia del usuario)
            
        Returns:
            float: Peso en kilogramos
        """
        if weight_value is None:
            return None
        
        try:
            weight_value = float(weight_value)
            source_unit = from_unit or self.weight_unit
            
            if source_unit == "lb":
                return weight_value / self.KG_TO_LB
            else:
                return weight_value
        except (ValueError, TypeError):
            return None
    
    def convert_volume_to_l(self, volume_value, from_unit=None):
        """
        Convierte un volumen a litros para almacenar en BD
        
        Args:
            volume_value: Valor numérico del volumen
            from_unit: Unidad de origen (si None, usa la preferencia del usuario)
            
        Returns:
            float: Volumen en litros
        """
        if volume_value is None:
            return None
        
        try:
            volume_value = float(volume_value)
            source_unit = from_unit or self.volume_unit
            
            if source_unit == "gal":
                return volume_value / self.L_TO_GAL
            else:
                return volume_value
        except (ValueError, TypeError):
            return None
    
    def get_weight_label(self):
        """Retorna la etiqueta de peso según unidad preferida"""
        return f"Peso ({self.weight_unit})"
    
    def get_volume_label(self):
        """Retorna la etiqueta de volumen según unidad preferida"""
        return f"Volumen ({self.volume_unit})"
    
    def refresh(self):
        """Recarga las preferencias desde la base de datos"""
        self._load_preferences()


# Instancia global para uso en toda la aplicación
units_helper = UnitsHelper()
