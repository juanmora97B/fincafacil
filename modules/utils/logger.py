import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Importación segura de config - CORREGIDA
try:
    # Intentar importar desde config.py en el directorio raíz
    from config import config
    HAS_CONFIG = True
except ImportError as e:
    # Configuración por defecto mejorada
    class DefaultConfig:
        def __init__(self):
            # Buscar el directorio base de forma más robusta
            current_file = Path(__file__).resolve()
            # Subir 3 niveles: utils -> modules -> project_root
            self.BASE_DIR = current_file.parent.parent.parent
            self.DB_PATH = self.BASE_DIR / "database" / "fincafacil.db"
            self.LOG_DIR = self.BASE_DIR / "logs"
            self.LOG_LEVEL = "INFO"
            self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            # Configuración de rotación de logs
            self.LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
            self.LOG_BACKUP_COUNT = 5  # Mantener 5 archivos de respaldo
    
    config = DefaultConfig()
    HAS_CONFIG = False
    print(f"⚠️ Usando configuración por defecto. BASE_DIR: {config.BASE_DIR}")

# Crear directorio de logs si no existe
try:
    config.LOG_DIR.mkdir(exist_ok=True, parents=True)
except Exception as e:
    print(f"⚠️ No se pudo crear directorio de logs: {e}")
    # Fallback al directorio actual
    config.LOG_DIR = Path.cwd() / "logs"
    config.LOG_DIR.mkdir(exist_ok=True, parents=True)

def limpiar_logs_antiguos():
    """Limpia archivos de log muy antiguos (más de 30 días)"""
    try:
        from datetime import datetime, timedelta
        
        log_dir = Path(config.LOG_DIR)
        if not log_dir.exists():
            return
        
        # Fecha límite (30 días atrás)
        fecha_limite = datetime.now() - timedelta(days=30)
        
        # Buscar archivos .log antiguos
        for log_file in log_dir.glob("*.log*"):
            try:
                tiempo_modificacion = datetime.fromtimestamp(log_file.stat().st_mtime)
                if tiempo_modificacion < fecha_limite:
                    log_file.unlink()
                    print(f"🗑️ Log antiguo eliminado: {log_file.name}")
            except Exception as e:
                print(f"⚠️ Error eliminando log antiguo {log_file.name}: {e}")
                
    except Exception as e:
        print(f"⚠️ Error en limpieza de logs: {e}")

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
    
    # Convertir nivel de string a constante de logging
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logger.setLevel(level)
    
    # Formato seguro
    log_format = getattr(config, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(log_format)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo con rotación
    try:
        log_file = config.LOG_DIR / "fincafacil.log"
        
        # Obtener configuración de rotación
        max_bytes = getattr(config, 'LOG_MAX_BYTES', 10 * 1024 * 1024)  # 10 MB por defecto
        backup_count = getattr(config, 'LOG_BACKUP_COUNT', 5)  # 5 backups por defecto
        
        # Usar RotatingFileHandler en lugar de FileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.debug(f"Archivo de log con rotación creado: {log_file}")
        logger.debug(f"Rotación configurada: {max_bytes/1024/1024:.1f}MB, {backup_count} backups")
        
        # Limpiar logs antiguos al iniciar
        limpiar_logs_antiguos()
        
    except Exception as e:
        print(f"⚠️ No se pudo crear archivo de log: {e}")
    
    return logger

# Logger global - con manejo de errores
try:
    log = setup_logger()
    log.info("Logger configurado correctamente")
except Exception as e:
    # Logger de emergencia si falla la configuración
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    log = logging.getLogger("FincaFacil_Emergency")
    log.warning(f"Usando logger de emergencia: {e}")

def get_logger(name=None):
    """Obtiene un logger por nombre"""
    try:
        if name:
            return setup_logger(name)
        else:
            return log
    except Exception as e:
        print(f"⚠️ Error obteniendo logger {name}: {e}")
        return logging.getLogger(name or "FincaFacil")