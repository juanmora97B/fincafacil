"""
Configuración centralizada para FincaFacil
"""
import os
import sys
from pathlib import Path

class Config:
    # Detectar si está ejecutándose como ejecutable empaquetado
    if getattr(sys, 'frozen', False):
        # Ejecutándose como ejecutable empaquetado
        BASE_DIR = Path(sys.executable).parent
    else:
        # Ejecutándose como script Python
        BASE_DIR = Path(__file__).parent
    
    # Rutas
    DB_PATH = BASE_DIR / "database" / "fincafacil.db"
    BACKUP_DIR = BASE_DIR / "backup"
    LOG_DIR = BASE_DIR / "logs"
    ASSETS_DIR = BASE_DIR / "assets"

    # Configuración de la aplicación
    APP_NAME = "FincaFacil"
    VERSION = "2.0.0"

    # Configuración de base de datos
    DB_TIMEOUT = 30

    # Configuración de backup
    BACKUP_DAYS = 7

    # Configuración de logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Archivo de preferencias de usuario
    PREFERENCES_FILE = BASE_DIR / "config" / "user_preferences.json"

    def __init__(self):
        # Asegurar directorios al inicializar
        self._ensure_directories()

    def _ensure_directories(self):
        """Asegura que los directorios necesarios existan"""
        directories = [
            self.BASE_DIR / "database",
            self.BACKUP_DIR, 
            self.LOG_DIR, 
            self.ASSETS_DIR,
            self.BASE_DIR / "exports",
            self.BASE_DIR / "uploads",
            self.BASE_DIR / "config"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
            print(f"✅ Directorio verificado: {directory}")

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "WARNING"

# Configuración actual
config = DevelopmentConfig()

# Variables globales compatibles con el resto del proyecto
RUTA_BASE_DATOS = config.DB_PATH
RUTA_ASSETS = config.ASSETS_DIR

if __name__ == "__main__":
    print("🧪 Probando configuración...")
    print(f"BASE_DIR: {config.BASE_DIR}")
    print(f"DB_PATH: {config.DB_PATH}")
    print(f"LOG_DIR: {config.LOG_DIR}")
    print("✅ Configuración cargada correctamente")