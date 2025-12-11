"""
Gestor del estado del tour interactivo del sistema.
"""
import json
from pathlib import Path
from typing import Optional, List


class TourStateManager:
    """Gestiona el estado del tour interactivo"""
    
    CONFIG_FILE = Path("config/tour_state.json")
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Carga el estado del tour desde el archivo de configuración"""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando tour state: {e}")
                return self._get_default_state()
        return self._get_default_state()
    
    def _get_default_state(self) -> dict:
        """Retorna el estado por defecto"""
        return {
            "app_version": "2.0.0",
            "primer_uso_completado": False,
            "tour_completado": False,
            "last_tour_module": "dashboard",
            "modulos_tour_visitados": []
        }
    
    def _save_state(self):
        """Guarda el estado del tour en el archivo de configuración"""
        try:
            self.CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando tour state: {e}")
    
    def es_primer_uso(self) -> bool:
        """Retorna True si es la primera vez usando el sistema"""
        return not self.state.get("primer_uso_completado", False)
    
    def marcar_primer_uso_completado(self):
        """Marca que el usuario completó el primer uso/tour"""
        self.state["primer_uso_completado"] = True
        self._save_state()
    
    def marcar_tour_completado(self):
        """Marca el tour global como completado"""
        self.state["tour_completado"] = True
        self._save_state()
    
    def tour_completado(self) -> bool:
        """Retorna True si el tour fue completado"""
        return self.state.get("tour_completado", False)
    
    def registrar_modulo_visitado(self, modulo: str):
        """Registra que se visitó un módulo en el tour"""
        modulos = self.state.get("modulos_tour_visitados", [])
        if modulo not in modulos:
            modulos.append(modulo)
            self.state["modulos_tour_visitados"] = modulos
            self._save_state()
    
    def obtener_modulos_visitados(self) -> List[str]:
        """Retorna lista de módulos visitados en el tour"""
        return self.state.get("modulos_tour_visitados", [])
    
    def reset_tour(self):
        """Resetea el estado del tour (para testing)"""
        self.state = self._get_default_state()
        self._save_state()
