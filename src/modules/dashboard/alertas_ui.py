"""
Función auxiliar para mostrar una alerta con botón "¿Por qué?" (FASE 10 integration)
Este archivo complementa el dashboard para agregar funcionalidad de explicabilidad.
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional, Dict, Any
from datetime import datetime


class AlertaConExplicacion:
    """Representa una alerta con su explicación asociada"""
    def __init__(self, 
                 alerta_id: str,
                 titulo: str,
                 descripcion: str,
                 severidad: str,
                 explicacion_dict: Optional[Dict] = None):
        self.alerta_id = alerta_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.severidad = severidad  # "alta", "media", "baja"
        self.explicacion_dict = explicacion_dict
        self.tiene_explicacion = explicacion_dict is not None
    
    def emoji_severidad(self) -> str:
        if self.severidad == "alta":
            return "🔴"
        elif self.severidad == "media":
            return "🟡"
        else:
            return "🟢"
    
    def color_severidad(self) -> str:
        if self.severidad == "alta":
            return "#E53935"
        elif self.severidad == "media":
            return "#FB8C00"
        else:
            return "#43A047"


def crear_fila_alerta_con_boton(parent_frame,
                               alerta: AlertaConExplicacion,
                               callback_explicacion: Optional[Callable] = None,
                               callback_cerrar: Optional[Callable] = None) -> ctk.CTkFrame:
    """
    Crea una fila visual para una alerta con botón "¿Por qué?" si tiene explicación.
    
    Args:
        parent_frame: Frame padre donde se agregará la alerta
        alerta: Instancia de AlertaConExplicacion
        callback_explicacion: Función a llamar cuando se hace clic en "¿Por qué?"
        callback_cerrar: Función a llamar cuando se cierra la alerta
    
    Returns:
        Frame de la alerta creado
    """
    # Frame contenedor
    alerta_frame = ctk.CTkFrame(parent_frame, corner_radius=10)
    alerta_frame.pack(fill="x", padx=5, pady=5)
    
    # Contenedor horizontal: contenido + botones
    contenido_frame = ctk.CTkFrame(alerta_frame, fg_color="transparent")
    contenido_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Parte izquierda: Título y descripción
    info_frame = ctk.CTkFrame(contenido_frame, fg_color="transparent")
    info_frame.pack(side="left", fill="both", expand=True)
    
    # Emoji + Título
    titulo_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
    titulo_frame.pack(fill="x", padx=(0, 10))
    
    ctk.CTkLabel(
        titulo_frame,
        text=f"{alerta.emoji_severidad()} {alerta.titulo}",
        font=("Segoe UI", 11, "bold"),
        text_color=alerta.color_severidad()
    ).pack(side="left", padx=(0, 8))
    
    # Descripción
    ctk.CTkLabel(
        info_frame,
        text=alerta.descripcion,
        font=("Segoe UI", 10),
        text_color="gray",
        wraplength=400,
        justify="left"
    ).pack(fill="x", padx=(28, 0), pady=(0, 5))
    
    # Parte derecha: Botones
    botones_frame = ctk.CTkFrame(contenido_frame, fg_color="transparent")
    botones_frame.pack(side="right", padx=(10, 0))
    
    # Botón "¿Por qué?" si hay explicación
    if alerta.tiene_explicacion and callback_explicacion:
        btn_explicacion = ctk.CTkButton(
            botones_frame,
            text="❓ ¿Por qué?",
            font=("Segoe UI", 9),
            width=100,
            height=28,
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=lambda: callback_explicacion(alerta)
        )
        btn_explicacion.pack(side="left", padx=2)
    
    # Botón cerrar alerta
    if callback_cerrar:
        btn_cerrar = ctk.CTkButton(
            botones_frame,
            text="✕",
            font=("Segoe UI", 9),
            width=32,
            height=28,
            fg_color="#666666",
            hover_color="#999999",
            command=lambda: callback_cerrar(alerta.alerta_id)
        )
        btn_cerrar.pack(side="left", padx=2)
    
    return alerta_frame


def crear_panel_alertas_mejorado(parent_frame,
                                alertas_list: list,
                                callback_explicacion: Optional[Callable] = None,
                                callback_cerrar: Optional[Callable] = None) -> ctk.CTkFrame:
    """
    Crea un panel de alertas mejorado con soporte para explicaciones.
    
    Args:
        parent_frame: Frame padre
        alertas_list: Lista de AlertaConExplicacion
        callback_explicacion: Función para mostrar explicación
        callback_cerrar: Función para cerrar una alerta
    
    Returns:
        Frame contenedor del panel
    """
    panel = ctk.CTkFrame(parent_frame, corner_radius=12)
    panel.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Encabezado
    header = ctk.CTkFrame(panel, fg_color="#E53935", corner_radius=10)
    header.pack(fill="x", padx=0, pady=(0, 10))
    
    ctk.CTkLabel(
        header,
        text=f"⚠️ ALERTAS ({len(alertas_list)})",
        font=("Segoe UI", 13, "bold"),
        text_color="white"
    ).pack(pady=10)
    
    # Área scrollable para alertas
    if alertas_list:
        # Crear frame scrollable si hay muchas alertas
        canvas_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Agregar cada alerta
        for alerta in alertas_list:
            crear_fila_alerta_con_boton(
                canvas_frame,
                alerta,
                callback_explicacion=callback_explicacion,
                callback_cerrar=callback_cerrar
            )
    else:
        # Mensaje cuando no hay alertas
        ctk.CTkLabel(
            panel,
            text="✅ No hay alertas activas",
            font=("Segoe UI", 11),
            text_color="green"
        ).pack(pady=40)
    
    return panel
