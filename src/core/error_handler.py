"""
Sistema global de manejo de errores (FASE 4)
- Clases de error de negocio
- Decorador @safe_ui_call para UI (CustomTkinter/Tkinter)
- Diálogo estándar para errores críticos
- Logging automático a archivo
- Stacktrace solo en log, no en UI
"""

from __future__ import annotations
import logging
import traceback
from functools import wraps
from typing import Callable, Any, Optional

try:
    import customtkinter as ctk
    from tkinter import messagebox
except Exception:
    ctk = None
    from tkinter import messagebox  # fallback

# Configuración de logging (archivo)
logger = logging.getLogger("error_handler")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logs/app_errors.log", encoding="utf-8")
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

# Clases de error
class BusinessError(Exception):
    """Errores de reglas de negocio (flujo esperado)."""

class ValidationError(Exception):
    """Errores de validación de datos de entrada."""

class DataIntegrityError(Exception):
    """Errores de integridad de datos (BD/consistencia)."""

class PermissionError(Exception):
    """Errores de permisos (acceso denegado)."""

# Diálogo estándar

def _show_error_dialog(title: str, message: str) -> None:
    try:
        # Usar messagebox simple; UI personalizada puede integrarse después
        messagebox.showerror(title, message)
    except Exception:
        # Evitar crash si GUI no disponible
        pass

# Decorador para envolver llamadas UI

def safe_ui_call(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Envuelve acciones de UI para capturar errores:
    - Muestra un diálogo de error
    - Registra stacktrace en logs
    - Nunca deja errores silenciosos
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (BusinessError, ValidationError, DataIntegrityError, PermissionError) as e:
            # Errores esperados: mensaje claro
            logger.error(f"{e.__class__.__name__}: {e}")
            _show_error_dialog("Error", str(e))
            return None
        except Exception as e:
            # Error inesperado: registrar stacktrace
            stack = traceback.format_exc()
            logger.error(f"UNEXPECTED ERROR: {e}\n{stack}")
            _show_error_dialog(
                "Error crítico",
                "Ocurrió un error inesperado. Se registró en los logs."
            )
            return None
    return wrapper

# Utilidad opcional para bloquear/desbloquear botones durante operaciones críticas

def busy_ui(master: Any, busy: bool) -> None:
    """Cambia el cursor y deshabilita controles, si es posible."""
    try:
        if hasattr(master, "configure"):
            master.configure(cursor="watch" if busy else "")
        # Deshabilitar botones comunes
        for child in getattr(master, "winfo_children", lambda: [])():
            try:
                if busy and hasattr(child, "configure"):
                    child.configure(state="disabled")
                elif hasattr(child, "configure"):
                    child.configure(state="normal")
            except Exception:
                continue
    except Exception:
        pass
