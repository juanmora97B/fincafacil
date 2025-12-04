"""
Tests para verificar configuración de rotación de logs en db_logging.
"""
import pytest
import os
import tempfile
import shutil
from logging.handlers import RotatingFileHandler


def test_log_rotation_handler_configurado():
    """Verifica que el logger db usa RotatingFileHandler."""
    from modules.utils.db_logging import logger
    
    handlers = logger.handlers
    assert len(handlers) > 0, "Logger debe tener al menos un handler"
    
    rotating_handlers = [h for h in handlers if isinstance(h, RotatingFileHandler)]
    assert len(rotating_handlers) > 0, "Logger debe usar RotatingFileHandler"


def test_log_rotation_parametros():
    """Verifica parámetros de rotación (5MB, 3 backups)."""
    from modules.utils.db_logging import logger
    
    rotating = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)][0]
    assert rotating.maxBytes == 5 * 1024 * 1024, "MaxBytes debe ser 5 MB"
    assert rotating.backupCount == 3, "BackupCount debe ser 3"


def test_log_rotation_crea_directorio():
    """Verifica que el directorio logs se crea automáticamente."""
    # El módulo ya habrá creado logs/ al importarse; verificamos que existe
    assert os.path.exists("logs"), "Directorio logs/ debe existir"


def test_log_escribible():
    """Verifica que se puede escribir en el log sin errores."""
    from modules.utils.db_logging import logger
    
    try:
        logger.info("Test log rotation: mensaje de prueba")
        assert True
    except Exception as e:
        pytest.fail(f"Escritura a log falló: {e}")


def test_simulacion_rotacion_basica():
    """Simula escritura grande para verificar lógica de rotación (sin forzar 5MB real)."""
    # Crear un RotatingFileHandler temporal
    with tempfile.TemporaryDirectory() as tmpdir:
        test_log = os.path.join(tmpdir, "test_rotate.log")
        handler = RotatingFileHandler(test_log, maxBytes=1024, backupCount=2)  # 1KB para test rápido
        
        import logging
        test_logger = logging.getLogger("test_rotation")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        
        # Escribir suficiente para provocar al menos una rotación
        for i in range(100):
            test_logger.info(f"Mensaje de prueba largo {i} " + "x" * 100)
        
        # Cerrar handler para flush
        handler.close()
        test_logger.removeHandler(handler)
        
        # Verificar que se crearon archivos rotados
        archivos = os.listdir(tmpdir)
        assert len(archivos) > 1, f"Debe haber archivos rotados. Encontrados: {archivos}"
        assert "test_rotate.log" in archivos, "Archivo principal debe existir"
