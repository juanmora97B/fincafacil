"""
Tour interactivo global del sistema FincaFácil - Ventana Modal Única.
Implementa un tour dinámico en una sola ventana CTkToplevel con dos secciones:
- Sección Superior: Contenido del paso (título + descripción)
- Sección Inferior: Controles de navegación
"""
import customtkinter as ctk
from tkinter import StringVar, messagebox
from pathlib import Path
from PIL import Image
from config import config
from modules.utils.tour_state_manager import TourStateManager