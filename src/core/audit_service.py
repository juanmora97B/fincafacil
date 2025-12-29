"""
Servicio de auditoría operativa (FASE 4)
- Tabla audit_log
- Registro automático de operaciones críticas
- Desde Service Layer, no UI
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
import logging

from src.database.database import get_db_connection

logger = logging.getLogger("audit_service")

# Asegurar esquema en arranque

def ensure_audit_schema() -> None:
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT,
                    fecha TEXT NOT NULL,
                    modulo TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    entidad TEXT,
                    resultado TEXT NOT NULL,
                    mensaje TEXT
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_audit_fecha ON audit_log(fecha)"
            )
            conn.commit()
    except Exception as e:
        logger.error(f"No se pudo asegurar esquema audit_log: {e}")


ensure_audit_schema()


def log_event(
    *,
    usuario: Optional[str],
    modulo: str,
    accion: str,
    entidad: Optional[str],
    resultado: str,
    mensaje: Optional[str] = None,
) -> None:
    """
    Registra un evento de auditoría.
    resultado: "OK" | "ERROR"
    accion: "CREAR" | "EDITAR" | "ELIMINAR" | "EXPORTAR" | "CIERRE"
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO audit_log (usuario, fecha, modulo, accion, entidad, resultado, mensaje)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    usuario,
                    datetime.now().isoformat(timespec="seconds"),
                    modulo,
                    accion,
                    entidad,
                    resultado,
                    mensaje,
                ),
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Error registrando auditoría: {e}")
