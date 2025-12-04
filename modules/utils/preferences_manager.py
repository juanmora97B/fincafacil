"""
Sistema centralizado de gestión de preferencias de usuario
Permite guardar y restaurar configuraciones de manera persistente
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("PreferencesManager")


class PreferencesManager:
    """Gestor centralizado de preferencias de usuario"""
    
    def __init__(self, preferences_file: Path):
        """
        Inicializa el gestor de preferencias
        
        Args:
            preferences_file: Ruta al archivo JSON de preferencias
        """
        self.preferences_file = preferences_file
        self._preferences: Dict[str, Any] = {}
        self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Carga las preferencias desde el archivo"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    self._preferences = json.load(f)
                logger.info(f"Preferencias cargadas desde {self.preferences_file}")
            else:
                logger.info("Archivo de preferencias no existe, usando valores por defecto")
                self._preferences = self._get_default_preferences()
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar JSON de preferencias: {e}")
            self._preferences = self._get_default_preferences()
        except Exception as e:
            logger.error(f"Error al cargar preferencias: {e}")
            self._preferences = self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Retorna las preferencias por defecto"""
        return {
            "appearance": "Oscuro",
            "language": "es",
            "units_weight": "kg",
            "units_volume": "L",
            "default_finca_id": None,
            "backup_dir": "",
            "auto_backup": True,
            "show_tooltips": True,
            "notifications_enabled": True
        }
    
    def save_preferences(self) -> bool:
        """
        Guarda las preferencias actuales al archivo
        
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        try:
            # Asegurar que el directorio existe
            self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self._preferences, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Preferencias guardadas en {self.preferences_file}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar preferencias: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene el valor de una preferencia
        
        Args:
            key: Clave de la preferencia
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor de la preferencia o default
        """
        return self._preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Establece el valor de una preferencia
        
        Args:
            key: Clave de la preferencia
            value: Valor a establecer
        """
        self._preferences[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Retorna todas las preferencias"""
        return self._preferences.copy()
    
    def update(self, preferences: Dict[str, Any]) -> None:
        """
        Actualiza múltiples preferencias a la vez
        
        Args:
            preferences: Diccionario con las preferencias a actualizar
        """
        self._preferences.update(preferences)
    
    def reset_to_defaults(self) -> None:
        """Resetea todas las preferencias a los valores por defecto"""
        self._preferences = self._get_default_preferences()
        logger.info("Preferencias reseteadas a valores por defecto")
    
    def export_preferences(self, export_path: Path) -> bool:
        """
        Exporta las preferencias a un archivo externo
        
        Args:
            export_path: Ruta donde exportar las preferencias
            
        Returns:
            True si se exportó exitosamente
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._preferences, f, indent=4, ensure_ascii=False)
            logger.info(f"Preferencias exportadas a {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error al exportar preferencias: {e}")
            return False
    
    def import_preferences(self, import_path: Path) -> bool:
        """
        Importa preferencias desde un archivo externo
        
        Args:
            import_path: Ruta del archivo a importar
            
        Returns:
            True si se importó exitosamente
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            # Validar que sea un diccionario
            if not isinstance(imported, dict):
                logger.error("El archivo importado no contiene un diccionario válido")
                return False
            
            self._preferences.update(imported)
            logger.info(f"Preferencias importadas desde {import_path}")
            return True
        except Exception as e:
            logger.error(f"Error al importar preferencias: {e}")
            return False


# Instancia global del gestor de preferencias
_preferences_manager: Optional[PreferencesManager] = None


def get_preferences_manager() -> PreferencesManager:
    """
    Obtiene la instancia global del gestor de preferencias
    
    Returns:
        Instancia de PreferencesManager
    """
    global _preferences_manager
    if _preferences_manager is None:
        from config import config
        _preferences_manager = PreferencesManager(config.PREFERENCES_FILE)
    return _preferences_manager
