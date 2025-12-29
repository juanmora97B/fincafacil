"""
Dominio Ajustes — Service
Responsabilidad: Validaciones mínimas y orquestación.
"""
from typing import List, Dict, Any, Optional
from infraestructura.ajustes.ajustes_repository import AjustesRepository


class AjustesService:
    def __init__(self, repository: Optional[AjustesRepository] = None) -> None:
        self.repository = repository or AjustesRepository()

    # Fincas (para combos)
    def listar_fincas_combo(self) -> List[str]:
        """Retorna valores formateados 'id - nombre' para el combo."""
        pares = self.repository.listar_fincas()
        return [f"{fid} - {nombre}" for fid, nombre in pares]

    # Settings
    def obtener_settings(self, defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Mezcla defaults con valores persistidos en app_settings."""
        out = dict(defaults)
        try:
            rows = self.repository.listar_app_settings()
            for k, v in rows:
                out[k] = v
        except Exception:
            # Best-effort: mantener defaults si falla lectura
            pass
        return out

    def guardar_setting(self, clave: str, valor: str) -> None:
        """Persiste una preferencia en app_settings (INSERT OR REPLACE)."""
        if not isinstance(clave, str):
            raise ValueError("Clave inválida")
        self.repository.upsert_app_setting(clave, valor or "")
