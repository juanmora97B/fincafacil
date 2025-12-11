"""Wrapper ligero para logging de operaciones de base de datos.
Permite instrumentar consultas críticas sin invadir demasiado el código existente.
Configurado con rotación automática de logs por tamaño (5MB, 3 backups).
"""
from __future__ import annotations
import logging, time, sqlite3, os
from contextlib import contextmanager
from typing import Iterable, Any, Optional
from logging.handlers import RotatingFileHandler

# Configuración del logger con rotación de archivos
logger = logging.getLogger("db")
if not logger.handlers:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "db.log")
    
    # RotatingFileHandler: rota cuando alcanza maxBytes, mantiene backupCount archivos antiguos
    handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,              # mantiene db.log.1, db.log.2, db.log.3
        encoding="utf-8"
    )
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@contextmanager
def logged_connection(get_conn_callable):
    """Context manager que envuelve la conexión retornada por get_conn_callable para logging básico.
    Solo loggea apertura/cierre; queries se loggean con log_query.
    """
    start = time.time()
    conn = get_conn_callable()
    logger.debug("CONN abierta")
    try:
        yield conn
        logger.debug("CONN uso OK")
    finally:
        conn.close()
        logger.debug("CONN cerrada %.3fs" % (time.time() - start))

def log_query(sql: str, params: Optional[Iterable[Any]] = None, rows: Optional[int] = None, level: str = "debug"):
    msg = f"SQL: {sql.strip()} | params={params}"
    if rows is not None:
        msg += f" | rows={rows}"
    getattr(logger, level, logger.info)(msg)

def safe_execute(cursor: sqlite3.Cursor, sql: str, params: Optional[Iterable[Any]] = None):
    """Ejecuta y loggea, retorna cursor para encadenar fetch.*"""
    cursor.execute(sql, params or [])
    try:
        size = cursor.rowcount
    except Exception:
        size = None
    log_query(sql, params, size)
    return cursor

__all__ = ["logged_connection", "log_query", "safe_execute", "logger"]
