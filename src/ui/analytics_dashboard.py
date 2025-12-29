from __future__ import annotations
import threading
import customtkinter as ctk
from tkinter import messagebox
from src.core.error_handler import safe_ui_call
from src.core.audit_service import log_event
from src.analytics.analytics_service import (
    calcular_kpis_financieros,
    calcular_kpis_productivos,
    comparativo_periodos,
)
from src.analytics.insights_service import generar_insights

class AnalyticsDashboard(ctk.CTkFrame):
    def __init__(self, master, usuario: str | None = None):
        super().__init__(master)
        self.usuario = usuario
        self._build_ui()
        self.after(300, self.load_data_async)
        log_event(usuario=self.usuario, modulo="analytics", accion="VIEW_DASHBOARD", entidad="dashboard", resultado="OK")

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        header = ctk.CTkLabel(self, text="📊 BI: Analytics Dashboard (solo lectura)", font=("Segoe UI", 22, "bold"))
        header.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        self.kpi_frame = ctk.CTkFrame(self)
        self.kpi_frame.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.kpi_frame.columnconfigure((0,1,2), weight=1)

        self.alerts_frame = ctk.CTkFrame(self)
        self.alerts_frame.grid(row=2, column=0, padx=12, pady=12, sticky="nsew")

        self.status = ctk.CTkLabel(self, text="Cargando datos...")
        self.status.grid(row=3, column=0, padx=12, pady=(0,12), sticky="w")

    @safe_ui_call
    def load_data_async(self):
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            periodo = 'mes_actual'
            fkpis = calcular_kpis_financieros(periodo, usuario=self.usuario)
            pkpis = calcular_kpis_productivos(periodo, usuario=self.usuario)
            insights = generar_insights(periodo, usuario=self.usuario)

            self._render_kpis(fkpis, pkpis)
            self._render_insights(insights)
            self.status.configure(text="Listo")
        except Exception as e:
            messagebox.showerror("Analytics", f"Error cargando datos: {e}")

    def _render_kpis(self, f, p):
        for w in self.kpi_frame.winfo_children():
            w.destroy()
        items = [
            ("Ingresos", f"${f.ingresos_totales:,.0f}"),
            ("Costos", f"${f.costos_totales:,.0f}"),
            ("Margen", f"${f.margen_bruto:,.0f}"),
            ("Rentabilidad", f"{f.rentabilidad_mensual:.1f}%" if f.rentabilidad_mensual is not None else "-"),
            ("Prod. diaria", f"{p.produccion_diaria:.1f} L"),
            ("Prod. mensual", f"{p.produccion_mensual:.1f} L"),
        ]
        r, c = 0, 0
        for title, value in items:
            card = ctk.CTkFrame(self.kpi_frame)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=8, pady=(8,0))
            ctk.CTkLabel(card, text=value, font=("Segoe UI", 18)).pack(anchor="w", padx=8, pady=(0,8))
            c = (c + 1) % 3
            if c == 0:
                r += 1

    def _render_insights(self, insights):
        for w in self.alerts_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.alerts_frame, text="Alertas / Insights", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=8, pady=(8,4))
        if not insights:
            ctk.CTkLabel(self.alerts_frame, text="Sin alertas", font=("Segoe UI", 14)).pack(anchor="w", padx=8, pady=(0,8))
            return
        for ins in insights:
            box = ctk.CTkFrame(self.alerts_frame)
            box.pack(fill="x", padx=8, pady=6)
            ctk.CTkLabel(box, text=f"[{ins.nivel}] {ins.categoria}", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=8, pady=(6,2))
            ctk.CTkLabel(box, text=ins.mensaje, font=("Segoe UI", 13)).pack(anchor="w", padx=8)
            ctk.CTkLabel(box, text=f"Sugerencia: {ins.recomendacion}", font=("Segoe UI", 12, "italic")).pack(anchor="w", padx=8, pady=(0,8))
