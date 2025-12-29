"""
Core - Módulo de reglas de negocio y utilidades centrales
Evitar efectos secundarios al importar el paquete.
"""

__all__ = ['BusinessRules']

try:
	from .business_rules import BusinessRules
except Exception:
	# Evitar fallos en herramientas que importan core (p.ej. health_check)
	pass
