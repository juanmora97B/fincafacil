"""Generación de manual PDF usando la fuente Markdown oficial.

Usa `modules.utils.pdf_generator.generar_manual_pdf` como motor real
para convertir `docs/Manual_Usuario_FincaFacil.md` a PDF.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from modules.utils.logger import Logger
from modules.utils.pdf_generator import generar_manual_pdf

logger = Logger(__name__)


class GeneradorPDFManual:
    """Generador de manuales en formato PDF."""

    def __init__(self):
        self.nombre_app = "FincaFácil"
        self.version = "2.0.0"
        self.manual_md = Path(__file__).parent.parent.parent / "docs" / "Manual_Usuario_FincaFacil.md"
        self.manual_pdf = Path(__file__).parent.parent.parent / "docs" / "Manual_Usuario_FincaFacil.pdf"
        logger.info("Generador de PDF manual inicializado")

    def generar_manual(self, titulo: Optional[str] = None, contenido: Optional[List[Dict[str, Any]]] = None,
                      ruta_salida: Optional[str] = None) -> Tuple[bool, str]:
        """Genera el manual completo a PDF a partir del Markdown oficial.

        Args:
            titulo: No utilizado (el título viene del markdown).
            contenido: No utilizado (se toma del markdown).
            ruta_salida: Ruta alternativa para guardar el PDF.

        Returns:
            (exito, ruta_pdf|mensaje_error)
        """
        try:
            target_pdf = Path(ruta_salida) if ruta_salida else self.manual_pdf
            ok, msg = generar_manual_pdf(md_path=str(self.manual_md), pdf_path=str(target_pdf))
            if ok:
                logger.info(f"Manual generado en {target_pdf}")
                return True, str(target_pdf)
            logger.error(f"Error generando manual: {msg}")
            return False, msg
        except Exception as e:
            logger.error(f"Error generando manual: {e}")
            return False, str(e)

    def generar_guia_rapida(self) -> Tuple[bool, str]:
        """Alias: genera el manual completo (no hay guía reducida separada)."""
        return self.generar_manual()

    def generar_manual_tecnico(self) -> Tuple[bool, str]:
        """Alias: genera el manual completo."""
        return self.generar_manual()


def obtener_generador_pdf() -> GeneradorPDFManual:
    """Obtiene una instancia del generador de PDF."""
    return GeneradorPDFManual()
