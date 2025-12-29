"""
Configuración centralizada para FincaFacil
"""
import os
import sys
from pathlib import Path

def _user_data_dir() -> Path:
    """Return a writable base dir for user data (AppData/Local)."""
    base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or str(Path.home())
    return Path(base) / "FincaFacil"


class Config:
    # Detectar si está ejecutándose como ejecutable empaquetado
    if getattr(sys, "frozen", False):
        INSTALL_DIR = Path(sys.executable).parent
        DATA_DIR = _user_data_dir()
    else:
        INSTALL_DIR = Path(__file__).parent
        DATA_DIR = INSTALL_DIR
    BASE_DIR = INSTALL_DIR
    
    # Rutas
    DB_PATH = DATA_DIR / "database" / "fincafacil.db"
    BACKUP_DIR = DATA_DIR / "backup"
    LOG_DIR = DATA_DIR / "logs"
    ASSETS_DIR = INSTALL_DIR / "assets"

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
    PREFERENCES_FILE = DATA_DIR / "config" / "user_preferences.json"

    def __init__(self):
        # Asegurar directorios al inicializar
        self._ensure_directories()

    def _ensure_directories(self):
        """Asegura que los directorios necesarios existan"""
        directories = [
            self.DB_PATH.parent,
            self.BACKUP_DIR,
            self.LOG_DIR,
            self.DATA_DIR / "exports",
            self.DATA_DIR / "uploads",
            self.DATA_DIR / "config",
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True, parents=True)
            print(f"[OK] Directorio verificado: {directory}")

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
    print("[TEST] Probando configuración...")
    print(f"BASE_DIR: {config.BASE_DIR}")
    print(f"DB_PATH: {config.DB_PATH}")
    print(f"LOG_DIR: {config.LOG_DIR}")
    print("[OK] Configuración cargada correctamente")