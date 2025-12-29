"""
Servicio de permisos básicos (FASE 4)
- Roles: ADMIN, OPERADOR, CONSULTA
- Reglas:
  CONSULTA → solo lectura
  OPERADOR → CRUD operativo
  ADMIN → acceso total
- Checks de permiso para acciones comunes
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Role = Literal["ADMIN", "OPERADOR", "CONSULTA"]
Action = Literal["READ", "CREATE", "UPDATE", "DELETE", "EXPORT", "CLOSE"]

@dataclass
class UserContext:
    username: str
    role: Role


def can(user: UserContext, action: Action) -> bool:
    if user.role == "ADMIN":
        return True
    if user.role == "CONSULTA":
        return action == "READ" or action == "EXPORT"
    if user.role == "OPERADOR":
        return action in {"READ", "CREATE", "UPDATE", "DELETE", "EXPORT", "CLOSE"}
    return False


def require(user: UserContext, action: Action) -> None:
    from src.core.error_handler import PermissionError
    if not can(user, action):
        raise PermissionError(f"Acceso denegado: {user.role} no puede {action}")
