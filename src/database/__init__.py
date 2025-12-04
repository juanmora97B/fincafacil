"""
Capa de base de datos de FincaFacil
"""

from src.database.connection import get_connection, db, DatabaseManager

__all__ = [
    "get_connection",
    "db",
    "DatabaseManager",
]
