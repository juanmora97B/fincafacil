"""
Popup para mostrar explicaciones de anomalías detectadas (FASE 10)
Permite al usuario entender POR QUÉ se generó cada alerta de forma clara y legible.
"""

import customtkinter as ctk
from tkinter import scrolledtext
from dataclasses import dataclass
from datetime import datetime


class PopupExplicacion(ctk.CTkToplevel):
    """
    Ventana popup para mostrar explicaciones de anomalías en lenguaje natural.
    Implementa la interfaz de usuario para FASE 10 (Explainability).
    """
    
    def __init__(self, parent, titulo: str, explicacion_dict: dict):
        """
        Args:
            parent: Widget padre
            titulo: Título de la alerta
            explicacion_dict: Diccionario con estructura ExplanationReport
                - titulo: str con emoji y descripción
                - resumen: str con resumen ejecutivo
                - evidencia: list de {"metrica_nombre", "valor_observado", "valor_esperado", "desviacion_pct"}
                - pasos: list de {"numero", "accion", "detalle", "resultado"}
                - contexto: dict con "estacion", "mes_anterior", "patrones", "cambios"
                - recomendacion: str con recomendación accionable
                - confianza_pct: int (50-95)
                - fecha_generacion: str (ISO format)
        """
        super().__init__(parent)
        
        self.title(titulo)
        self.geometry("900x750")
        self.resizable(True, True)
        
        # Evitar que la ventana sea modal
        self.transient(parent)
        
        # Colores corporativos
        self.COLORS = {
            "primary": "#1E88E5",
            "success": "#43A047",
            "warning": "#FB8C00",
            "danger": "#E53935",
            "info": "#0097A7",
        }
        
        self.explicacion = explicacion_dict
        
        # Construir UI
        self._crear_header()
        self._crear_resumen()
        self._crear_evidencia()
        self._crear_pasos()
        self._crear_contexto()
        self._crear_recomendacion()
        self._crear_footer()
    
    def _crear_header(self):
        """Encabezado con información general"""
        header = ctk.CTkFrame(self, fg_color=self.COLORS["danger"], corner_radius=12)
        header.pack(fill="x", padx=10, pady=10)
        
        # Título principal
        ctk.CTkLabel(
            header,
            text=self.explicacion.get('titulo', '⚠️ Anomalía Detectada'),
            font=("Segoe UI", 16, "bold"),
            text_color="white"
        ).pack(pady=(10, 5), padx=10)
        
        # Confianza
        confianza = self.explicacion.get('confianza_pct', 80)
        info_confianza = f"🎯 Confianza: {confianza}%"
        
        ctk.CTkLabel(
            header,
            text=info_confianza,
            font=("Segoe UI", 11),
            text_color="#FFD54F"
        ).pack(pady=(0, 10), padx=10)
    
    def _crear_resumen(self):
        """Resumen ejecutivo de la anomalía"""
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text="📋 RESUMEN EJECUTIVO",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        resumen_text = self.explicacion.get('resumen', 'Sin información')
        
        text_widget = ctk.CTkTextbox(frame, height=60, wrap="word")
        text_widget.pack(fill="x", padx=10, pady=(0, 10))
        text_widget.insert("1.0", resumen_text)
        text_widget.configure(state="disabled")
    
    def _crear_evidencia(self):
        """Evidencia numérica de la anomalía"""
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text="📊 EVIDENCIA NUMÉRICA",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        evidencia = self.explicacion.get('evidencia', [])
        
        if isinstance(evidencia, list) and len(evidencia) > 0:
            # Si es una lista de dicts
            for item in evidencia:
                self._mostrar_evidencia_item(frame, item)
        elif isinstance(evidencia, dict):
            # Si es un dict único
            self._mostrar_evidencia_item(frame, evidencia)
    
    def _mostrar_evidencia_item(self, parent, item):
        """Mostrar un item de evidencia"""
        if isinstance(item, dict):
            metrica = item.get('metrica_nombre', 'Métrica')
            observado = item.get('valor_observado', '--')
            esperado = item.get('valor_esperado', '--')
            desviacion = item.get('desviacion_pct', 0)
            
            texto = f"• {metrica}: {observado:.1f} vs {esperado:.1f} ({desviacion:+.1f}%)"
        else:
            texto = f"• {item}"
        
        ctk.CTkLabel(
            parent,
            text=texto,
            font=("Segoe UI", 10),
            justify="left"
        ).pack(pady=2, padx=20, anchor="w")
    
    def _crear_pasos(self):
        """Pasos de razonamiento (el corazón de FASE 10)"""
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text="🔍 PASOS DE RAZONAMIENTO",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        # Crear área scrollable para pasos
        pasos_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pasos_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        pasos = self.explicacion.get('pasos', [])
        
        if isinstance(pasos, list):
            for i, paso in enumerate(pasos, 1):
                self._mostrar_paso(pasos_frame, paso, i)
        else:
            ctk.CTkLabel(
                pasos_frame,
                text="No hay información de pasos disponible",
                font=("Segoe UI", 10),
                text_color="gray"
            ).pack(pady=5)
    
    def _mostrar_paso(self, parent, paso, numero):
        """Mostrar un paso individual de razonamiento"""
        if isinstance(paso, dict):
            accion = paso.get('accion', f'Paso {numero}')
            detalle = paso.get('detalle', '')
            
            paso_frame = ctk.CTkFrame(parent, fg_color="#F0F0F0", corner_radius=8)
            paso_frame.pack(fill="x", pady=5)
            
            # Número y acción
            ctk.CTkLabel(
                paso_frame,
                text=f"Paso {numero}: {accion}",
                font=("Segoe UI", 10, "bold")
            ).pack(pady=(8, 3), padx=10, anchor="w")
            
            # Detalle
            if detalle:
                ctk.CTkLabel(
                    paso_frame,
                    text=f"   → {detalle}",
                    font=("Segoe UI", 9),
                    text_color="gray"
                ).pack(pady=(0, 8), padx=10, anchor="w")
    
    def _crear_contexto(self):
        """Contexto y factores externos que influyen"""
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text="🌍 CONTEXTO",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        contexto = self.explicacion.get('contexto', {})
        
        if isinstance(contexto, dict) and contexto:
            for clave, valor in contexto.items():
                # Formatear clave
                clave_formateada = clave.replace('_', ' ').title()
                texto = f"• {clave_formateada}: {valor}"
                
                ctk.CTkLabel(
                    frame,
                    text=texto,
                    font=("Segoe UI", 9),
                    text_color="gray",
                    justify="left"
                ).pack(pady=2, padx=20, anchor="w")
        
        ctk.CTkLabel(
            frame,
            text="",
            font=("Segoe UI", 1)
        ).pack(pady=5)
    
    def _crear_recomendacion(self):
        """Recomendación accionable para el usuario"""
        frame = ctk.CTkFrame(self, fg_color=self.COLORS["success"], corner_radius=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text="✅ RECOMENDACIÓN",
            font=("Segoe UI", 12, "bold"),
            text_color="white"
        ).pack(pady=(10, 5), padx=10, anchor="w")
        
        recomendacion = self.explicacion.get('recomendacion', 'Sin recomendación disponible')
        
        text_widget = ctk.CTkTextbox(frame, height=60, wrap="word")
        text_widget.pack(fill="x", padx=10, pady=(0, 10))
        text_widget.insert("1.0", recomendacion)
        text_widget.configure(state="disabled")
        
        # Cambiar color de fondo para mejor legibilidad
        text_widget.configure(fg_color="#E8F5E9")
    
    def _crear_footer(self):
        """Pie de página con metadata e información de cierre"""
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=10)
        
        fecha = self.explicacion.get('fecha_generacion', 'N/A')
        texto_fecha = f"📅 Generado: {fecha}"
        
        ctk.CTkLabel(
            footer,
            text=texto_fecha,
            font=("Segoe UI", 8),
            text_color="gray"
        ).pack(pady=5)
        
        # Botón cerrar
        ctk.CTkButton(
            footer,
            text="Cerrar",
            width=100,
            fg_color=self.COLORS["info"],
            hover_color="#0077B6",
            command=self.destroy
        ).pack(pady=5)


def mostrar_explicacion_alerta(parent, alerta_id: str, titulo: str, explicacion_dict: dict):
    """
    Función auxiliar para mostrar una ventana de explicación.
    
    Args:
        parent: Widget padre
        alerta_id: ID único de la alerta
        titulo: Título de la alerta
        explicacion_dict: Diccionario con ExplanationReport
    """
    PopupExplicacion(parent, titulo, explicacion_dict)
