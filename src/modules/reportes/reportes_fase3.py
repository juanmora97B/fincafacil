"""
╔══════════════════════════════════════════════════════════════════════════╗
║            MÓDULO UI DE REPORTES FASE 3 - VERSIÓN COMPACTA              ║
╚══════════════════════════════════════════════════════════════════════════╝

Interfaz gráfica simplificada para reportes de FASE 3.
Este archivo reemplaza/complementa reportes_main.py con funcionalidad de FASE 3.
"""

import customtkinter as ctk
from datetime import datetime, date, timedelta
from tkinter import messagebox, filedialog
from typing import Dict, Any
import logging
import os
import sys

# Agregar path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.services.reportes_service import reportes_service
from src.services.cierre_mensual_service import cierre_mensual_service
from src.services.ai_anomaly_detector import get_ai_anomaly_detector_service
from src.services.ai_pattern_detector import get_ai_pattern_detector_service
from src.utils.export.export_pdf import pdf_exporter
from src.utils.export.export_excel import excel_exporter
from src.utils.export.export_csv import csv_exporter
from src.core.error_handler import safe_ui_call, busy_ui
from src.core.permissions_manager import get_permissions_manager, RoleEnum


class ReportesFase3(ctk.CTkFrame):
    """Módulo de reportes FASE 3 (versión simplificada)"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.reporte_actual = None
        self._crear_ui()
    
    def _crear_ui(self):
        """Crea la interfaz"""
        # Título
        header = ctk.CTkFrame(self, fg_color="#1976D2")
        header.pack(fill="x", padx=10, pady=10)
        
        header_row = ctk.CTkFrame(header, fg_color="transparent")
        header_row.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_row,
            text="📊 REPORTES Y EXPORTACIÓN - FASE 3",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", pady=5)

        ctk.CTkButton(
            header_row,
            text="⬅ Dashboard",
            width=120,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#43A047",
            hover_color="#388E3C",
            corner_radius=10,
            command=self._volver_dashboard
        ).pack(side="right")
        
        # Frame principal con 2 columnas
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=3)
        
        # Columna izquierda: Controles
        left = self._crear_panel_controles(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Columna derecha: Vista previa
        right = self._crear_panel_vista(main)
        right.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Panel inferior: Exportación
        bottom = self._crear_panel_exportar()
        bottom.pack(fill="x", padx=10, pady=(0, 10))
    
    def _crear_panel_controles(self, parent) -> ctk.CTkFrame:
        """Panel de controles"""
        frame = ctk.CTkFrame(parent)
        
        # Tipo de reporte
        ctk.CTkLabel(frame, text="Tipo de Reporte:", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        
        self.combo_tipo = ctk.CTkComboBox(
            frame,
            values=["animales", "reproduccion", "produccion", "finanzas", "completo"],
            width=250
        )
        self.combo_tipo.set("animales")
        self.combo_tipo.pack(padx=10, pady=5)
        
        # Fechas
        ctk.CTkLabel(frame, text="Fecha Inicio:", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=(15, 5)
        )
        
        hoy = date.today()
        self.entry_inicio = ctk.CTkEntry(frame, width=250)
        self.entry_inicio.insert(0, date(hoy.year, hoy.month, 1).isoformat())
        self.entry_inicio.pack(padx=10, pady=5)
        
        ctk.CTkLabel(frame, text="Fecha Fin:", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=10, pady=(10, 5)
        )
        
        self.entry_fin = ctk.CTkEntry(frame, width=250)
        self.entry_fin.insert(0, hoy.isoformat())
        self.entry_fin.pack(padx=10, pady=5)
        
        # Botón generar
        ctk.CTkButton(
            frame,
            text="🔍 GENERAR REPORTE",
            command=self._generar,
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=10, pady=20, fill="x")
        
        # Botón cierre
        ctk.CTkButton(
            frame,
            text="📅 Cierre Mensual",
            command=self._cierre_mensual,
            height=35,
            fg_color="#4CAF50"
        ).pack(padx=10, pady=5, fill="x")

        # Botón AI: ejecutar detectores on-demand
        ctk.CTkButton(
            frame,
            text="🤖 Detectar Anomalías y Patrones",
            command=self._ejecutar_ai_detectors,
            height=35,
            fg_color="#673AB7",
            hover_color="#5E35B1",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(padx=10, pady=(5, 15), fill="x")
        
        return frame
    
    def _crear_panel_vista(self, parent) -> ctk.CTkFrame:
        """Panel de vista previa"""
        frame = ctk.CTkFrame(parent)
        
        ctk.CTkLabel(
            frame,
            text="Vista Previa",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.text_vista = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Courier New", size=10)
        )
        self.text_vista.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.text_vista.insert(
            "1.0",
            "Seleccione un tipo de reporte y genere para ver la vista previa.\n\n"
            "Luego podrá exportar en PDF, Excel o CSV."
        )
        self.text_vista.configure(state="disabled")
        
        return frame
    
    def _crear_panel_exportar(self) -> ctk.CTkFrame:
        """Panel de exportación"""
        frame = ctk.CTkFrame(self)
        
        ctk.CTkLabel(
            frame,
            text="Exportar:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=15)
        
        # Botones de exportación
        for texto, formato, color in [
            ("📄 PDF", "pdf", "#E53935"),
            ("📊 Excel", "excel", "#43A047"),
            ("📁 CSV", "csv", "#FB8C00")
        ]:
            ctk.CTkButton(
                frame,
                text=texto,
                command=lambda f=formato: self._exportar(f),
                width=130,
                height=35,
                fg_color=color
            ).pack(side="left", padx=5)
        
        return frame
    
    @safe_ui_call
    def _generar(self):
        """Genera el reporte"""
        busy_ui(self, True)
        tipo = self.combo_tipo.get()
        fecha_inicio = datetime.strptime(self.entry_inicio.get(), "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(self.entry_fin.get(), "%Y-%m-%d").date()
        self.reporte_actual = reportes_service.generar_reporte(
            tipo, fecha_inicio, fecha_fin
        )
        self._mostrar_vista()
        busy_ui(self, False)
        messagebox.showinfo("Éxito", "Reporte generado correctamente")
    
    def _mostrar_vista(self):
        """Muestra vista previa"""
        if not self.reporte_actual:
            return
        
        self.text_vista.configure(state="normal")
        self.text_vista.delete("1.0", "end")
        
        r = self.reporte_actual
        texto = f"""
{'=' * 70}
REPORTE: {r['tipo'].upper()}
{'=' * 70}
Período: {r['periodo']['inicio']} → {r['periodo']['fin']}
Generado: {r['generado_en']}
{'=' * 70}

TOTALES:
"""
        
        for k, v in r.get('totales', {}).items():
            texto += f"  {k}: {v}\n"
        
        texto += f"\n{'=' * 70}\nUse los botones de exportación para el reporte completo\n{'=' * 70}"
        
        self.text_vista.insert("1.0", texto)
        self.text_vista.configure(state="disabled")
    
    @safe_ui_call
    def _exportar(self, formato: str):
        """Exporta el reporte"""
        if not self.reporte_actual:
            messagebox.showwarning("Advertencia", "Genere un reporte primero")
            return
        busy_ui(self, True)
        ext = "xlsx" if formato == "excel" else formato
        ruta = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(formato.upper(), f"*.{ext}")]
        )
        if not ruta:
            busy_ui(self, False)
            return
        if formato == "pdf":
            pdf_exporter.exportar(self.reporte_actual, ruta)
        elif formato == "excel":
            excel_exporter.exportar(self.reporte_actual, ruta)
        else:
            csv_exporter.exportar(self.reporte_actual, ruta)
        busy_ui(self, False)
        if messagebox.askyesno("Éxito", f"Exportado.\n¿Abrir archivo?"):
            os.startfile(ruta)
    
    @safe_ui_call
    def _cierre_mensual(self):
        """Abre diálogo de cierre mensual"""
        d = CierreMensualDialog(self)
        d.grab_set()
        d.wait_window()

    def _volver_dashboard(self):
        """Regresa al Dashboard usando show_screen si está disponible."""
        try:
            root: Any = self.winfo_toplevel()
            show_screen = getattr(root, "show_screen", None)
            if callable(show_screen):
                show_screen("dashboard")
        except Exception:
            pass

    @safe_ui_call
    def _ejecutar_ai_detectors(self):
        """Ejecuta AI Lite (anomalías y patrones) bajo demanda y muestra resumen."""
        # RBAC: solo ADMINISTRADOR puede ejecutar detectores on-demand
        try:
            pm = get_permissions_manager()
            if pm.get_current_role() != RoleEnum.ADMINISTRADOR:
                messagebox.showwarning("Permiso denegado", "Tu rol no puede ejecutar detectores AI.")
                return
        except Exception:
            # Si el gestor no está disponible, permitir pero registrar
            pass
        busy_ui(self, True)
        try:
            anomaly_service = get_ai_anomaly_detector_service()
            pattern_service = get_ai_pattern_detector_service()
            anomalies = anomaly_service.evaluar_anomalias(usuario_id=None, incluir_alertas=True)
            patterns = pattern_service.detectar_patrones(usuario_id=None, incluir_alertas=True)

            # Mostrar resumen en vista
            self.text_vista.configure(state="normal")
            self.text_vista.delete("1.0", "end")
            resumen = (
                f"AI Lite ejecutado.\n\n"
                f"Anomalías detectadas: {len(anomalies)}\n"
                f"Patrones detectados: {len(patterns)}\n\n"
                f"Se han registrado alertas cuando corresponde."
            )
            self.text_vista.insert("1.0", resumen)
            self.text_vista.configure(state="disabled")

            messagebox.showinfo(
                "AI Lite",
                f"Anomalías: {len(anomalies)}\nPatrones: {len(patterns)}"
            )
        except Exception as e:
            messagebox.showwarning("AI Lite", f"No se pudo ejecutar: {e}")
        finally:
            busy_ui(self, False)


class CierreMensualDialog(ctk.CTkToplevel):
    """Diálogo de cierre mensual"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cierre Mensual")
        self.geometry("450x350")
        self._crear_ui()
    
    def _crear_ui(self):
        ctk.CTkLabel(
            self,
            text="📅 Cierre Mensual",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=10)
        
        # Año
        ctk.CTkLabel(frame, text="Año:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_año = ctk.CTkEntry(frame)
        self.entry_año.insert(0, str(date.today().year))
        self.entry_año.grid(row=0, column=1, padx=10, pady=5)
        
        # Mes
        ctk.CTkLabel(frame, text="Mes:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.combo_mes = ctk.CTkComboBox(frame, values=[str(i) for i in range(1, 13)])
        self.combo_mes.set(str(date.today().month))
        self.combo_mes.grid(row=1, column=1, padx=10, pady=5)
        
        # Observaciones
        ctk.CTkLabel(self, text="Observaciones:").pack(anchor="w", padx=20, pady=(10, 5))
        self.text_obs = ctk.CTkTextbox(self, height=80)
        self.text_obs.pack(fill="x", padx=20, pady=5)
        
        # Botones
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="✓ Realizar Cierre",
            command=self._realizar,
            fg_color="#4CAF50"
        ).grid(row=0, column=0, padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="gray"
        ).grid(row=0, column=1, padx=5)
    
    def _realizar(self):
        try:
            año = int(self.entry_año.get())
            mes = int(self.combo_mes.get())
            obs = self.text_obs.get("1.0", "end").strip() or None
            
            if not messagebox.askyesno("Confirmar", f"¿Realizar cierre de {año}-{mes:02d}?"):
                return
            
            resumen = cierre_mensual_service.realizar_cierre(año, mes, "Usuario", obs)
            
            messagebox.showinfo(
                "Completado",
                f"Cierre de {año}-{mes:02d} completado.\n\n"
                f"Margen: ${resumen['margen_bruto']:,.0f} ({resumen['margen_porcentaje']:.1f}%)"
            )
            
            self.destroy()
        
        except Exception as e:
            messagebox.showerror("Error", str(e))


# Para usar este módulo en lugar del antiguo:
# from src.modules.reportes.reportes_fase3 import ReportesFase3
