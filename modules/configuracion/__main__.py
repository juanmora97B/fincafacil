import customtkinter as ctk
from tkinter import ttk
import sys
import os

# Ensure the parent directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.configuracion.proveedores import ProveedoresFrame
from modules.configuracion.calidad_animal import CalidadAnimalFrame
from modules.configuracion.motivos_venta import MotivosVentaFrame
from modules.configuracion.causa_muerte import CausaMuerteFrame
from modules.configuracion.destino_venta import DestinoVentaFrame
from modules.configuracion.procedencia import ProcedenciaFrame
from modules.configuracion.tipo_explotacion import TipoExplotacionFrame
from modules.configuracion.condiciones_corporales import CondicionesCorporalesFrame
from modules.configuracion.diagnosticos import DiagnosticosFrame
from modules.configuracion.empleados import EmpleadosFrame
from modules.configuracion.fincas import FincasFrame
from modules.configuracion.lotes import LotesFrame
from modules.configuracion.potreros import PotrerosFrame
from modules.configuracion.razas import RazasFrame
from modules.configuracion.sectores import SectoresFrame


class ConfiguracionModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Frame principal con dos columnas
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar grid
        self.main_container.grid_columnconfigure(0, weight=0)  # Menú lateral
        self.main_container.grid_columnconfigure(1, weight=1)  # Área de trabajo
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Crear menú lateral
        self.crear_menu_lateral()
        
        # Área de trabajo
        self.work_area = ctk.CTkFrame(self.main_container)
        self.work_area.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.work_area.grid_columnconfigure(0, weight=1)
        self.work_area.grid_rowconfigure(0, weight=1)
        
        # Mostrar pantalla de inicio
        self.mostrar_inicio()
    
    def crear_menu_lateral(self):
        """Crea el menú lateral con botones para cada módulo"""
        menu_frame = ctk.CTkFrame(self.main_container, width=250)
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.grid_propagate(False)  # Mantener ancho fijo
        
        # Título del menú
        titulo_menu = ctk.CTkLabel(menu_frame, text="📋 Configuraciones", 
                                  font=("Segoe UI", 16, "bold"))
        titulo_menu.pack(pady=15)
        
        # Separador
        separador = ctk.CTkFrame(menu_frame, height=2, fg_color="gray")
        separador.pack(fill="x", padx=10, pady=5)
        
        # Categorías y módulos
        categorias = {
            "🏠 FINCA Y UBICACIÓN": [
                ("🏠 Fincas", self.mostrar_fincas),
                ("📍 Sectores", self.mostrar_sectores),
                ("🌿 Potreros", self.mostrar_potreros),
                ("📦 Lotes", self.mostrar_lotes)
            ],
            "🐄 ANIMALES": [
                ("🐄 Razas", self.mostrar_razas),
                ("⭐ Calidad Animal", self.mostrar_calidad),
                ("⚖️ Cond. Corporales", self.mostrar_condiciones),
                ("🏭 Tipos Explotación", self.mostrar_tipos_explotacion)
            ],
            "💰 COMERCIAL": [
                ("📋 Motivos Venta", self.mostrar_motivos_venta),
                ("🏷️ Destinos Venta", self.mostrar_destinos_venta),
                ("📍 Procedencias", self.mostrar_procedencias)
            ],
            "🏥 SALUD": [
                ("💀 Causas Muerte", self.mostrar_causas_muerte),
                ("🏥 Diagnósticos", self.mostrar_diagnosticos)
            ],
            "👥 PERSONAL Y PROVEEDORES": [
                ("🛒 Proveedores", self.mostrar_proveedores),
                ("👥 Empleados", self.mostrar_empleados)
            ]
        }
        
        # Crear botones para cada categoría
        for categoria, modulos in categorias.items():
            # Título de categoría
            cat_label = ctk.CTkLabel(menu_frame, text=categoria, 
                                   font=("Segoe UI", 12, "bold"),
                                   text_color="gray")
            cat_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Botones de la categoría
            for texto, comando in modulos:
                btn = ctk.CTkButton(menu_frame, 
                                   text=texto,
                                   width=200,
                                   height=35,
                                   corner_radius=8,
                                   command=comando)
                btn.pack(pady=2, padx=10)
            
            # Separador entre categorías
            separador_cat = ctk.CTkFrame(menu_frame, height=1, fg_color="lightgray")
            separador_cat.pack(fill="x", padx=10, pady=8)
    
    def limpiar_area_trabajo(self):
        """Limpia el área de trabajo"""
        for widget in self.work_area.winfo_children():
            widget.destroy()
    
    def mostrar_inicio(self):
        """Muestra la pantalla de inicio en el área de trabajo"""
        self.limpiar_area_trabajo()
        
        # Frame de contenido
        content_frame = ctk.CTkFrame(self.work_area)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icono grande
        icono = ctk.CTkLabel(content_frame, text="⚙️", 
                            font=("Segoe UI", 80))
        icono.pack(pady=(50, 20))
        
        # Título
        titulo = ctk.CTkLabel(content_frame, 
                             text="Configuración del Sistema",
                             font=("Segoe UI", 28, "bold"))
        titulo.pack(pady=10)
        
        # Descripción
        descripcion = ctk.CTkLabel(content_frame,
                                  text="Seleccione una opción del menú lateral para gestionar\nlos diferentes parámetros y catálogos del sistema.",
                                  font=("Segoe UI", 16),
                                  justify="center")
        descripcion.pack(pady=10)
        
        # Información adicional
        info = ctk.CTkLabel(content_frame,
                           text="Aquí podrá configurar toda la información base\nnecesaria para el funcionamiento de FincaFácil.",
                           font=("Segoe UI", 14),
                           text_color="gray",
                           justify="center")
        info.pack(pady=20)
    
    # ==========================
    # FUNCIONES PARA MOSTRAR MÓDULOS
    # ==========================
    
    def mostrar_fincas(self):
        self.limpiar_area_trabajo()
        try:
            fincas_frame = FincasFrame(self.work_area)
            fincas_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Fincas: {e}")
    
    def mostrar_sectores(self):
        self.limpiar_area_trabajo()
        try:
            sectores_frame = SectoresFrame(self.work_area)
            sectores_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Sectores: {e}")
    
    def mostrar_potreros(self):
        self.limpiar_area_trabajo()
        try:
            potreros_frame = PotrerosFrame(self.work_area)
            potreros_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Potreros: {e}")
    
    def mostrar_lotes(self):
        self.limpiar_area_trabajo()
        try:
            lotes_frame = LotesFrame(self.work_area)
            lotes_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Lotes: {e}")
    
    def mostrar_razas(self):
        self.limpiar_area_trabajo()
        try:
            razas_frame = RazasFrame(self.work_area)
            razas_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Razas: {e}")
    
    def mostrar_calidad(self):
        self.limpiar_area_trabajo()
        try:
            calidad_frame = CalidadAnimalFrame(self.work_area)
            calidad_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Calidad Animal: {e}")
    
    def mostrar_condiciones(self):
        self.limpiar_area_trabajo()
        try:
            condiciones_frame = CondicionesCorporalesFrame(self.work_area)
            condiciones_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Condiciones Corporales: {e}")
    
    def mostrar_tipos_explotacion(self):
        self.limpiar_area_trabajo()
        try:
            tipos_frame = TipoExplotacionFrame(self.work_area)
            tipos_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Tipos de Explotación: {e}")
    
    def mostrar_motivos_venta(self):
        self.limpiar_area_trabajo()
        try:
            motivos_frame = MotivosVentaFrame(self.work_area)
            motivos_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Motivos de Venta: {e}")
    
    def mostrar_destinos_venta(self):
        self.limpiar_area_trabajo()
        try:
            destinos_frame = DestinoVentaFrame(self.work_area)
            destinos_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Destinos de Venta: {e}")
    
    def mostrar_procedencias(self):
        self.limpiar_area_trabajo()
        try:
            procedencias_frame = ProcedenciaFrame(self.work_area)
            procedencias_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Procedencias: {e}")
    
    def mostrar_causas_muerte(self):
        self.limpiar_area_trabajo()
        try:
            causas_frame = CausaMuerteFrame(self.work_area)
            causas_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Causas de Muerte: {e}")
    
    def mostrar_diagnosticos(self):
        self.limpiar_area_trabajo()
        try:
            diagnosticos_frame = DiagnosticosFrame(self.work_area)
            diagnosticos_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Diagnósticos: {e}")
    
    def mostrar_proveedores(self):
        self.limpiar_area_trabajo()
        try:
            proveedores_frame = ProveedoresFrame(self.work_area)
            proveedores_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Proveedores: {e}")
    
    def mostrar_empleados(self):
        self.limpiar_area_trabajo()
        try:
            empleados_frame = EmpleadosFrame(self.work_area)
            empleados_frame.pack(fill="both", expand=True)
        except Exception as e:
            self.mostrar_error(f"Error al cargar Empleados: {e}")
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en el área de trabajo"""
        error_frame = ctk.CTkFrame(self.work_area)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(error_frame, text="❌ Error", 
                    font=("Segoe UI", 20, "bold"), 
                    text_color="red").pack(pady=10)
        
        ctk.CTkLabel(error_frame, text=mensaje,
                    font=("Segoe UI", 14),
                    wraplength=600).pack(pady=5)
        
        ctk.CTkLabel(error_frame, text="El módulo podría no estar implementado aún",
                    font=("Segoe UI", 12),
                    text_color="gray").pack(pady=10)