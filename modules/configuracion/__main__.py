import customtkinter as ctk
import sys
import os
import logging
from modules.utils.ui import add_tooltip

# Ensure the parent directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configurar logging
logger = logging.getLogger(__name__)

class ConfiguracionModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Colores y modo adaptativos
        self._modo = ctk.get_appearance_mode()
        self._fg_card = "#2B2B2B" if self._modo == "Dark" else "#F5F5F5"
        self._sel = "#1976D2" if self._modo == "Light" else "#1F538D"
        self._hover = "#90caf9" if self._modo == "Light" else "#14375E"
        
        # Frame principal con dos columnas
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
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
                                   font=("Segoe UI", 16, "bold"),
                                   text_color=self._sel)
        titulo_menu.pack(pady=15)
        add_tooltip(titulo_menu, "Parámetros y catálogos del sistema")

        # Separador
        separador = ctk.CTkFrame(menu_frame, height=2, fg_color=("#D0D0D0" if self._modo == "Light" else "#404040"))
        separador.pack(fill="x", padx=10, pady=5)
        
        # Categorías y módulos - VERSIÓN MEJORADA CON MANEJO DINÁMICO
        categorias = {
            "🏠 FINCA Y UBICACIÓN": [
                ("🏠 Fincas", "fincas", self.mostrar_fincas),
                ("📍 Sectores", "sectores", self.mostrar_sectores),
                ("🌿 Potreros", "potreros", self.mostrar_potreros),
                ("📦 Lotes", "lotes", self.mostrar_lotes)
            ],
            "🐄 ANIMALES": [
                ("🐄 Razas", "razas", self.mostrar_razas),
                ("⭐ Calidad Animal", "calidad", self.mostrar_calidad),
                ("⚖️ Cond. Corporales", "condiciones", self.mostrar_condiciones),
                ("🏭 Tipos Explotación", "tipos_explotacion", self.mostrar_tipos_explotacion)
            ],
            "💰 COMERCIAL": [
                ("📋 Motivos Venta", "motivos_venta", self.mostrar_motivos_venta),
                ("🏷️ Destinos Venta", "destinos_venta", self.mostrar_destinos_venta),
                ("📍 Procedencias", "procedencias", self.mostrar_procedencias)
            ],
            "🏥 SALUD": [
                ("💀 Causas Muerte", "causas_muerte", self.mostrar_causas_muerte),
                ("🏥 Diagnósticos", "diagnosticos", self.mostrar_diagnosticos)
            ],
            "👥 PERSONAL Y PROVEEDORES": [
                ("🛒 Proveedores", "proveedores", self.mostrar_proveedores),
                ("👥 Empleados", "empleados", self.mostrar_empleados)
            ]
        }
        
        # Crear botones para cada categoría
        for categoria, modulos in categorias.items():
            # Título de categoría
            cat_label = ctk.CTkLabel(menu_frame, text=categoria, 
                                   font=("Segoe UI", 12, "bold"),
                                   text_color="gray")
            cat_label.pack(anchor="w", padx=15, pady=(15, 5))
            add_tooltip(cat_label, f"{categoria}")
            
            # Botones de la categoría
            for texto, modulo_id, comando in modulos:
                btn = ctk.CTkButton(menu_frame, 
                                   text=texto,
                                   width=200,
                                   height=35,
                                   corner_radius=8,
                                   command=comando,
                                   fg_color=self._sel,
                                   hover_color=self._hover)
                btn.pack(pady=2, padx=10)
                # Guardar referencia para posible uso futuro
                btn.modulo_id = modulo_id
                add_tooltip(btn, f"Abrir {texto}")
            
            # Separador entre categorías
            separador_cat = ctk.CTkFrame(menu_frame, height=1, fg_color=("#E0E0E0" if self._modo == "Light" else "#303030"))
            separador_cat.pack(fill="x", padx=10, pady=8)
    
    def limpiar_area_trabajo(self):
        """Limpia el área de trabajo de manera segura"""
        try:
            for widget in self.work_area.winfo_children():
                widget.destroy()
        except Exception as e:
            logger.error(f"Error al limpiar área de trabajo: {e}")
    
    def mostrar_inicio(self):
        """Muestra la pantalla de inicio en el área de trabajo"""
        self.limpiar_area_trabajo()
        
        try:
            # Frame de contenido
            content_frame = ctk.CTkFrame(self.work_area)
            # Compactar ancho (20→4)
            content_frame.pack(fill="both", expand=True, padx=4, pady=20)
            
            # Icono grande
            icono = ctk.CTkLabel(content_frame, text="⚙️", 
                                font=("Segoe UI", 80))
            icono.pack(pady=(50, 20))
            
            # Título
            titulo = ctk.CTkLabel(content_frame, 
                                 text="Configuración del Sistema",
                                 font=("Segoe UI", 28, "bold"),
                                 text_color=self._sel)
            titulo.pack(pady=10)
            add_tooltip(titulo, "Centro de configuración de FincaFácil")
            
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
            
        except Exception as e:
            logger.error(f"Error al mostrar pantalla de inicio: {e}")
            self.mostrar_error(f"Error al cargar la pantalla de inicio: {e}")

    # ==========================
    # FUNCIONES PARA MOSTRAR MÓDULOS - VERSIÓN MEJORADA
    # ==========================
    
    def cargar_modulo(self, nombre_modulo, clase_frame):
        """Carga un módulo de forma genérica con manejo de errores"""
        self.limpiar_area_trabajo()
        try:
            # Importación dinámica para evitar problemas de importación circular
            modulo = __import__(f'modules.configuracion.{nombre_modulo}', 
                              fromlist=[clase_frame])
            frame_class = getattr(modulo, clase_frame)
            frame_instance = frame_class(self.work_area)
            frame_instance.pack(fill="both", expand=True)
            logger.info(f"Módulo {nombre_modulo} cargado correctamente")
            
        except ImportError as e:
            logger.error(f"Error de importación en {nombre_modulo}: {e}")
            self.mostrar_error(f"El módulo {nombre_modulo} no está disponible.\nError: {e}")
        except Exception as e:
            logger.error(f"Error al cargar {nombre_modulo}: {e}")
            self.mostrar_error(f"Error al cargar {nombre_modulo}:\n{e}")
    
    def mostrar_fincas(self):
        self.cargar_modulo('fincas', 'FincasFrame')
    
    def mostrar_sectores(self):
        self.cargar_modulo('sectores', 'SectoresFrame')
    
    def mostrar_potreros(self):
        self.cargar_modulo('potreros', 'PotrerosFrame')
    
    def mostrar_lotes(self):
        self.cargar_modulo('lotes', 'LotesFrame')
    
    def mostrar_razas(self):
        self.cargar_modulo('razas', 'RazasFrame')
    
    def mostrar_calidad(self):
        self.cargar_modulo('calidad_animal', 'CalidadAnimalFrame')
    
    def mostrar_condiciones(self):
        self.cargar_modulo('condiciones_corporales', 'CondicionesCorporalesFrame')
    
    def mostrar_tipos_explotacion(self):
        self.cargar_modulo('tipo_explotacion', 'TipoExplotacionFrame')
    
    def mostrar_motivos_venta(self):
        self.cargar_modulo('motivos_venta', 'MotivosVentaFrame')
    
    def mostrar_destinos_venta(self):
        self.cargar_modulo('destino_venta', 'DestinoVentaFrame')
    
    def mostrar_procedencias(self):
        self.cargar_modulo('procedencia', 'ProcedenciaFrame')
    
    def mostrar_causas_muerte(self):
        self.cargar_modulo('causa_muerte', 'CausaMuerteFrame')
    
    def mostrar_diagnosticos(self):
        self.cargar_modulo('diagnosticos', 'DiagnosticosFrame')
    
    def mostrar_proveedores(self):
        self.cargar_modulo('proveedores', 'ProveedoresFrame')
    
    def mostrar_empleados(self):
        self.cargar_modulo('empleados', 'EmpleadosFrame')
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en el área de trabajo"""
        try:
            error_frame = ctk.CTkFrame(self.work_area)
            # Compactar ancho (20→4)
            error_frame.pack(fill="both", expand=True, padx=4, pady=20)
            
            ctk.CTkLabel(error_frame, text="❌ Error", 
                        font=("Segoe UI", 20, "bold"), 
                        text_color="red").pack(pady=10)
            
            ctk.CTkLabel(error_frame, text=mensaje,
                        font=("Segoe UI", 14),
                        wraplength=600).pack(pady=5)
            
            ctk.CTkLabel(error_frame, text="Verifique que el módulo esté correctamente implementado",
                        font=("Segoe UI", 12),
                        text_color="gray").pack(pady=10)
            
            # Botón para regresar al inicio
            btn_volver = ctk.CTkButton(error_frame, text="🏠 Volver al Inicio", 
                         command=self.mostrar_inicio, fg_color=self._sel, hover_color=self._hover)
            btn_volver.pack(pady=10)
            add_tooltip(btn_volver, "Regresar a la pantalla de inicio")
                        
        except Exception as e:
            logger.error(f"Error al mostrar mensaje de error: {e}")

    def mostrar(self):
        """Muestra el módulo (para compatibilidad)"""
        self.pack(fill="both", expand=True)

    def ocultar(self):
        """Oculta el módulo (para compatibilidad)"""
        self.pack_forget()

    # _add_tooltip eliminado: ahora se usa add_tooltip centralizado desde modules.utils.ui