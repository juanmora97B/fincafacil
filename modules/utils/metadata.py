"""
Módulo de metadatos para la aplicación FincaFácil.
Gestiona información y metadatos de animales, insumos y otros recursos.
"""

from modules.utils.logger import Logger
from typing import Dict, Any, Optional

logger = Logger(__name__)


class GestorMetadatos:
    """Gestor de metadatos para la aplicación."""
    
    def __init__(self):
        """Inicializa el gestor de metadatos."""
        self.metadatos = {}
        logger.info("Gestor de metadatos inicializado")
    
    def obtener_metadatos(self, clave: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene metadatos para una clave específica.
        
        Args:
            clave: La clave de los metadatos a obtener
            
        Returns:
            Los metadatos si existen, None en caso contrario
        """
        return self.metadatos.get(clave)
    
    def guardar_metadatos(self, clave: str, datos: Dict[str, Any]) -> bool:
        """
        Guarda metadatos para una clave específica.
        
        Args:
            clave: La clave para los metadatos
            datos: Los datos a guardar
            
        Returns:
            True si se guardó correctamente, False en caso contrario
        """
        try:
            self.metadatos[clave] = datos
            logger.info(f"Metadatos guardados para clave: {clave}")
            return True
        except Exception as e:
            logger.error(f"Error guardando metadatos para {clave}: {e}")
            return False
    
    def eliminar_metadatos(self, clave: str) -> bool:
        """
        Elimina metadatos para una clave específica.
        
        Args:
            clave: La clave de los metadatos a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            if clave in self.metadatos:
                del self.metadatos[clave]
                logger.info(f"Metadatos eliminados para clave: {clave}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando metadatos para {clave}: {e}")
            return False
    
    def limpiar_metadatos(self):
        """Limpia todos los metadatos."""
        self.metadatos.clear()
        logger.info("Todos los metadatos han sido limpiados")


# Instancia global del gestor de metadatos
_gestor_metadatos = None


def obtener_gestor_metadatos() -> GestorMetadatos:
    """Obtiene la instancia global del gestor de metadatos."""
    global _gestor_metadatos
    if _gestor_metadatos is None:
        _gestor_metadatos = GestorMetadatos()
    return _gestor_metadatos
