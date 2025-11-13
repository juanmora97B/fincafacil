import logging
import os
import sys
from pathlib import Path

# Importación segura de config
try:
    from config import config
    HAS_CONFIG = True
except ImportError:
    # Configuración por defecto si config no existe
    class DefaultConfig:
        BASE_DIR = Path(__file__).parent.parent.parent
        DB_PATH = BASE_DIR / "database" / "fincafacil.db"
        LOG_DIR = BASE_DIR / "logs"
        LOG_LEVEL = "INFO"
        LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    config = DefaultConfig()
    HAS_CONFIG = False

# Crear directorio de logs si no existe
try:
    config.LOG_DIR.mkdir(exist_ok=True)
except Exception:
    # Fallback si no puede crear directorio
    config.LOG_DIR = Path("logs")
    config.LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name="FincaFacil", level=None):
    """Configura el sistema de logging"""
    if level is None:
        # Usar nivel por defecto seguro
        level = getattr(config, 'LOG_LEVEL', 'INFO')
    
    # Crear logger
    logger = logging.getLogger(name)
    
    # Evitar múltiples handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Formato seguro
    log_format = getattr(config, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(log_format)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (opcional)
    try:
        file_handler = logging.FileHandler(config.LOG_DIR / "fincafacil.log", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"⚠️ No se pudo crear archivo de log: {e}")
    
    return logger

# Logger global - con manejo de errores
try:
    log = setup_logger()
except Exception as e:
    # Logger de emergencia si falla la configuración
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("FincaFacil_Emergency")
    log.warning(f"Usando logger de emergencia: {e}")

def get_logger(name=None):
    """Obtiene un logger por nombre"""
    try:
        return setup_logger(name) if name else log
    except Exception:
        return logging.getLogger(name or "FincaFacil")