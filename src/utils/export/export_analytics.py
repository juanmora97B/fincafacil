from __future__ import annotations
from typing import Dict, List
from pathlib import Path
from src.core.audit_service import log_event
from src.utils.export.export_csv import CSVExporter
from src.utils.export.export_excel import ExcelExporter
from src.utils.export.export_pdf import PDFExporter

# Wrapper to export analytics data using existing exporters

class AnalyticsExporter:
    def __init__(self):
        self.csv = CSVExporter()
        self.xlsx = ExcelExporter()
        self.pdf = PDFExporter()

    def export(self, datos: Dict, formato: str, destino: Path, usuario: str | None = None) -> Path:
        # datos may include {'kpis_financieros': {...}, 'kpis_productivos': {...}, 'tendencias': [...], 'insights': [...]} 
        try:
            if formato.lower() == 'csv':
                path = self.csv.exportar_analitico(datos, destino)
            elif formato.lower() in ('xlsx', 'excel'):
                path = self.xlsx.exportar_analitico(datos, destino)
            elif formato.lower() == 'pdf':
                path = self.pdf.exportar_analitico(datos, destino)
            else:
                raise ValueError(f"Formato no soportado: {formato}")
            log_event(usuario=usuario, modulo="analytics", accion="EXPORT_ANALYTICS", entidad=str(path.name), resultado="OK")
            return path
        except Exception as e:
            log_event(usuario=usuario, modulo="analytics", accion="EXPORT_ANALYTICS", entidad="error", resultado="ERROR", mensaje=str(e))
            raise
