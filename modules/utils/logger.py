import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Importación segura de config
try:
    from config import config
    HAS_CONFIG = True
except ImportError:
    class DefaultConfig:
        def __init__(self):
            current_file = Path(__file__).resolve()
            self.BASE_DIR = current_file.parent.parent.parent
            self.DB_PATH = self.BASE_DIR / "database" / "fincafacil.db"
            self.LOG_DIR = self.BASE_DIR / "logs"
            self.LOG_LEVEL = "INFO"
            self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            self.LOG_MAX_BYTES = 10 * 1024 * 1024
            self.LOG_BACKUP_COUNT = 5
    
    config = DefaultConfig()
    HAS_CONFIG = False

# Crear directorio de logs si no existe
try:
    config.LOG_DIR.mkdir(exist_ok=True, parents=True)
except Exception as e:
    config.LOG_DIR = Path.cwd() / "logs"
    config.LOG_DIR.mkdir(exist_ok=True, parents=True)


class Logger:
    """Clase wrapper para el logger de la aplicación."""
    
    def __init__(self, name="FincaFacil"):
        """Inicializa el logger."""
        self.logger = self._setup_logger(name)
    
    def _setup_logger(self, name):
        """Configura el logger."""
        logger = logging.getLogger(name)
        
        if logger.handlers:
            return logger
        
        logger.setLevel(logging.INFO)
        
        log_format = getattr(config, 'LOG_FORMAT', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler con rotación
        try:
            log_file = config.LOG_DIR / "fincafacil.log"
            max_bytes = getattr(config, 'LOG_MAX_BYTES', 10 * 1024 * 1024)
            backup_count = getattr(config, 'LOG_BACKUP_COUNT', 5)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"⚠️ Error creando file handler: {e}")
        
        return logger
    
    def debug(self, message):
        """Log debug."""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log critical."""
        self.logger.critical(message)


# Logger global para compatibilidad
_default_logger = Logger()

def get_logger(name=None):
    """Obtiene un logger por nombre."""
    if name:
        return Logger(name)
    return _default_logger


# Para compatibilidad con imports anteriores
log = _default_logger.logger


def setup_logger(name="FincaFacil", level=None):
    """Función de compatibilidad que retorna un logger configurado."""
    return Logger(name)