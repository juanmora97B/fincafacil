import os
from pathlib import Path

class Config:
    # Rutas
    BASE_DIR = Path(__file__).parent
    DB_PATH = BASE_DIR / "database" / "fincafacil.db"
    BACKUP_DIR = BASE_DIR / "backup"
    LOG_DIR = BASE_DIR / "logs"
    
    # Configuración de la aplicación
    APP_NAME = "FincaFacil"
    VERSION = "1.0.0"
    
    # Configuración de base de datos
    DB_TIMEOUT = 30
    
    # Configuración de backup
    BACKUP_DAYS = 7
    
    # Configuración de logging - ¡ESTOS FALTABAN!
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"

# Configuración actual
config = DevelopmentConfig()