"""
Servicio de backups automáticos (FASE 4)
- Backups versionados y comprimidos (.zip)
- Nombre con timestamp y razón
- Retención configurable (últimos N)
- Hooks: cierre aplicación, cierre mensual, error crítico
"""

from __future__ import annotations
import os
import zipfile
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

from src.database.database import get_db_path_safe

logger = logging.getLogger("backup_service")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logs/backups.log", encoding="utf-8")
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

DEFAULT_RETENTION = 10
BACKUP_DIR = Path("backup")


def backup_now(reason: str, user: Optional[str] = None, retention: int = DEFAULT_RETENTION) -> Path:
    """
    Crea un backup comprimido de la base de datos con timestamp.
    Args:
        reason: Motivo del backup (cierre_mensual, cierre_app, error_critico)
        user: Usuario opcional
        retention: Cantidad de backups a retener (más antiguos se eliminan)
    Returns:
        Ruta al archivo .zip creado
    """
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        db_path = get_db_path_safe()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_part = f"_{user}" if user else ""
        zip_name = f"backup_{ts}_{reason}{user_part}.zip"
        zip_path = BACKUP_DIR / zip_name

        logger.info(f"Creando backup: {zip_path}")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(db_path, arcname=db_path.name)
        logger.info("Backup creado exitosamente")

        # Retención
        _apply_retention(retention)
        return zip_path
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        raise


def _apply_retention(retention: int) -> None:
    """Elimina backups antiguos, dejando los N más recientes."""
    try:
        backups = sorted(BACKUP_DIR.glob("backup_*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in backups[retention:]:
            try:
                old.unlink()
                logger.info(f"Backup antiguo eliminado: {old}")
            except Exception:
                pass
    except Exception:
        pass


# Hooks de conveniencia

def on_app_close(user: Optional[str] = None) -> None:
    backup_now("cierre_app", user)


def on_monthly_close(user: Optional[str] = None) -> None:
    backup_now("cierre_mensual", user)


def on_critical_error(user: Optional[str] = None) -> None:
    backup_now("error_critico", user)
