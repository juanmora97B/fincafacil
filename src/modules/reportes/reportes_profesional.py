"""
Módulo de Reportes y Estadísticas Profesional
Versión mejorada con gráficas, filtros avanzados, exportación y análisis
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sys
import os
import csv
import json
from io import StringIO

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from modules.utils.ui import add_tooltip, style_treeview
from modules.utils.logger import get_logger
from modules.utils.date_picker import attach_date_picker
from modules.utils.colores import obtener_colores
from database import db

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False


class ReportesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Colores adaptables
        self._modo = ctk.get_appearance_mode()
        self._fg_card = "#2B2B2B" if self._modo == "Dark" else "#F5F5F5"
        self._theme_variant = "base"
        self._sel = "#1976D2" if self._modo == "Light" else "#1F538D"
        self._hover = "#90caf9" if self._modo == "Light" else "#14375E"
        self.color_bg, self.color_hover = obtener_colores('reportes')
        self._text_secondary = "#B0BEC5" if self._modo == "Dark" else "#546E7A"
        self._text_muted = "#9FA8B1" if self._modo == "Dark" else "#607080"
        self._accent_a = "#00ACC1" if self._modo == "Light" else "#26C6DA"
        self._accent_b = "#8E24AA" if self._modo == "Light" else "#BA68C8"
        self._accent_c = "#FFB300" if self._modo == "Light" else "#FFCA28"
        self._border_soft = "#CFD8DC" if self._modo == "Light" else "#455A64"
        self.logger = get_logger("Reportes")
        
        # Estado de filtros
        self.filtros_activos = {}
        self.datos_cache = {}
        
        self.crear_widgets()

    def crear_widgets(self):
        """Crea la interfaz principal"""
        # Header mejorado
        header = ctk.CTkFrame(self, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        header.pack(fill="x", padx=15, pady=(10, 6))
        
        # Título con subtítulo
        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.pack(side="left", anchor="w", padx=15, pady=10, fill="x", expand=True)
        
        titulo = ctk.CTkLabel(
            titulo_frame,
            text="📊 Centro de Reportes y Analytics",
            font=("Segoe UI", 24, "bold"),
            text_color="white"
        )
        titulo.pack(anchor="w")
        
        subtitulo = ctk.CTkLabel(
            titulo_frame,
            text="Panel integral de análisis, inventario, nómina y producción",
            font=("Segoe UI", 10),
            text_color="#B0BEC5"
        )
        subtitulo.pack(anchor="w")

        # Contenedor principal
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        # Panel izquierdo - Selector de reportes
        self._crear_panel_reportes(main_container)
        
        # Panel derecho - Área de contenido
        self.content_area = ctk.CTkFrame(main_container)
        self.content_area.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Mostrar reporte inicial
        self.mostrar_reporte("dashboard")

    def _crear_panel_reportes(self, parent):
        """Crea el panel lateral de reportes"""
        left_panel = ctk.CTkFrame(parent, width=280, fg_color=self._fg_card)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        titulo_panel = ctk.CTkLabel(
            left_panel,
            text="📋 Reportes",
            font=("Segoe UI", 16, "bold"),
            text_color=self._sel
        )
        titulo_panel.pack(pady=10)

        # Lista de reportes
        self.reportes = {
            "dashboard": ("📊 Dashboard", "Visión general del negocio"),
            "inventario": ("🐄 Inventario", "Estado del inventario de animales"),
            "ventas": ("💰 Ventas", "Análisis de ventas y movimientos"),
            "salud": ("🏥 Salud Animal", "Tratamientos y diagnósticos"),
            "reproduccion": ("👶 Reproducción", "Servicios y partos"),
            "empleados": ("👥 Empleados", "Nómina y actividad laboral"),
            "potreros": ("🌿 Potreros", "Capacidad y ocupación"),
            "leche": ("🥛 Leche", "Producción diaria, litros/mes y análisis por vaca"),
            "actividad": ("📅 Actividad", "Movimientos recientes")
        }

        frame_reportes = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        frame_reportes.pack(fill="both", expand=True, padx=10, pady=5)

        for key, (icon, desc) in self.reportes.items():
            btn = ctk.CTkButton(
                frame_reportes,
                text=icon,
                width=240,
                height=45,
                command=lambda k=key: self.mostrar_reporte(k),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=self._hover,
                border_width=1,
                border_color=("gray70", "gray30")
            )
            btn.pack(pady=3)
            add_tooltip(btn, desc)

    def mostrar_reporte(self, tipo_reporte):
        """Muestra el reporte seleccionado"""
        # Limpiar contenido anterior
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Título y botones
        self._crear_header_reporte(main_frame, tipo_reporte)
        
        # Filtros específicos por tipo
        self._crear_filtros(main_frame, tipo_reporte)
        
        # Contenido del reporte
        if tipo_reporte == "dashboard":
            self._reporte_dashboard(main_frame)
        elif tipo_reporte == "inventario":
            self._reporte_inventario(main_frame)
        elif tipo_reporte == "ventas":
            self._reporte_ventas(main_frame)
        elif tipo_reporte == "salud":
            self._reporte_salud(main_frame)
        elif tipo_reporte == "reproduccion":
            self._reporte_reproduccion(main_frame)
        elif tipo_reporte == "empleados":
            self._reporte_empleados(main_frame)
        elif tipo_reporte == "potreros":
            self._reporte_potreros(main_frame)
        elif tipo_reporte == "leche":
            self._reporte_leche(main_frame)
        elif tipo_reporte == "actividad":
            self._reporte_actividad(main_frame)

    def _toggle_theme(self):
        """Alterna un set de acentos para darle variedad visual"""
        if self._theme_variant == "base":
            self._theme_variant = "alt"
            self._accent_a = "#00b894"
            self._accent_b = "#e17055"
            self._accent_c = "#0984e3"
        else:
            self._theme_variant = "base"
            self._accent_a = "#00ACC1" if self._modo == "Light" else "#26C6DA"
            self._accent_b = "#8E24AA" if self._modo == "Light" else "#BA68C8"
            self._accent_c = "#FFB300" if self._modo == "Light" else "#FFCA28"
        # Refrescar reporte actual
        self.mostrar_reporte(self._reporte_actual if hasattr(self, "_reporte_actual") else "dashboard")

    # Helpers de estilo para tarjetas y secciones
    def _kpi_card(self, parent, title, value, caption=None, color=None):
        """Crea una tarjeta KPI profesional con efecto visual mejorado"""
        # Frame externo con sombra
        card = ctk.CTkFrame(parent, fg_color=color or self._fg_card, corner_radius=12, border_width=1, border_color=self._border_soft if not color else color)
        card.pack(side="left", fill="both", expand=True, padx=6, pady=4)

        # Frame interno para padding
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Título con icono
        title_label = ctk.CTkLabel(
            inner, 
            text=title, 
            font=("Segoe UI", 10, "bold"), 
            text_color="white" if color else self._sel,
            wraplength=120
        )
        title_label.pack(anchor="w", pady=(0, 4))
        
        # Valor principal (grande y destacado)
        value_label = ctk.CTkLabel(
            inner, 
            text=value, 
            font=("Segoe UI", 24, "bold"), 
            text_color="white" if color else None
        )
        value_label.pack(anchor="w", pady=(4, 0))
        
        # Caption/descripción
        if caption:
            caption_label = ctk.CTkLabel(
                inner, 
                text=caption, 
                font=("Segoe UI", 9), 
                text_color=self._text_muted if not color else "#E3F2FD",
                wraplength=120
            )
            caption_label.pack(anchor="w", pady=(6, 0))
        return card

    def _section(self, parent, title, subtitle=None):
        """Crea una sección con estilo profesional y bordes mejorados"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(10, 4))
        
        # Header con línea divisoria
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            header, 
            text=title, 
            font=("Segoe UI", 14, "bold"), 
            text_color=self._sel
        ).pack(side="left", anchor="w")
        
        if subtitle:
            ctk.CTkLabel(
                header, 
                text=subtitle, 
                font=("Segoe UI", 9), 
                text_color=self._text_secondary
            ).pack(side="left", padx=12, anchor="w")
        
        # Línea separadora
        sep = ctk.CTkFrame(frame, fg_color=self._border_soft, corner_radius=0, height=1)
        sep.pack(fill="x", pady=(0, 8))
        
        # Body con fondo
        body = ctk.CTkFrame(frame, fg_color=self._fg_card, corner_radius=12, border_width=1, border_color=self._border_soft)
        body.pack(fill="both", expand=True, pady=(0, 2))
        return body

    def _chip_row(self, parent, items):
        """Render a row of small chips to highlight filtros activos"""
        if not items:
            return
        chip_row = ctk.CTkFrame(parent, fg_color="transparent")
        chip_row.pack(fill="x", padx=12, pady=(0, 6))
        colors = [self._accent_a, self._accent_b, self._accent_c, self._sel]
        for idx, txt in enumerate(items):
            chip = ctk.CTkFrame(chip_row, fg_color=colors[idx % len(colors)], corner_radius=10)
            chip.pack(side="left", padx=4, pady=2)
            ctk.CTkLabel(chip, text=txt, font=("Segoe UI", 10, "bold"), text_color="white").pack(padx=8, pady=4)

    def _crear_header_reporte(self, parent, tipo):
        """Crea encabezado con título y botones de acción"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=10, padx=10)

        icon, nombre = self.reportes.get(tipo, ("📊", "Reporte"))
        self._reporte_actual = tipo
        
        titulo = ctk.CTkLabel(
            header,
            text=f"{icon} {nombre}",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel
        )
        titulo.pack(side="left")

        # Frame de botones
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")

        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=lambda: self.mostrar_reporte(tipo),
            width=100,
            fg_color=self._sel,
            hover_color=self._hover
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📥 Exportar CSV",
            command=lambda: self._exportar_csv(tipo),
            width=120,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(side="left", padx=5)

        if HAS_MATPLOTLIB and tipo != "dashboard":
            ctk.CTkButton(
                btn_frame,
                text="📊 Gráficos",
                command=lambda: self._mostrar_graficos(tipo),
                width=100,
                fg_color="#FF6F00",
                hover_color="#E65100"
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🎨 Tema",
            command=self._toggle_theme,
            width=80,
            fg_color=self._accent_b,
            hover_color=self._hover
        ).pack(side="left", padx=5)

    def _crear_filtros(self, parent, tipo):
        """Crea filtros según el tipo de reporte"""
        if tipo == "dashboard":
            return

        filtro_frame = ctk.CTkFrame(parent, fg_color=self._fg_card)
        filtro_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            filtro_frame,
            text="🔍 Filtros",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        ctk.CTkLabel(
            filtro_frame,
            text="Usa estos filtros para ajustar la vista. 'Todas' muestra todo; combina varios para un enfoque preciso.",
            font=("Segoe UI", 10),
            text_color=self._text_secondary
        ).pack(anchor="w", padx=10, pady=(0, 6))

        # Filtros específicos por tipo de reporte
        if tipo == "inventario":
            self._crear_filtros_inventario(filtro_frame)
        else:
            # Filtros genéricos de fecha
            fila = ctk.CTkFrame(filtro_frame, fg_color="transparent")
            fila.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(fila, text="Desde:", width=50).pack(side="left", padx=5)
            entry_desde = ctk.CTkEntry(fila, width=120, placeholder_text="YYYY-MM-DD")
            entry_desde.pack(side="left", padx=5)
            attach_date_picker(fila, entry_desde)

            ctk.CTkLabel(fila, text="Hasta:", width=50).pack(side="left", padx=5)
            entry_hasta = ctk.CTkEntry(fila, width=120, placeholder_text="YYYY-MM-DD")
            hoy = datetime.now()
            entry_hasta.insert(0, hoy.strftime("%Y-%m-%d"))
            entry_hasta.pack(side="left", padx=5)
            attach_date_picker(fila, entry_hasta)

            # Botón Filtrar
            def aplicar_filtros():
                self.filtros_activos['desde'] = entry_desde.get().strip()
                self.filtros_activos['hasta'] = entry_hasta.get().strip()
                self.mostrar_reporte(tipo)

            def limpiar_filtros():
                entry_desde.delete(0, "end")
                entry_hasta.delete(0, "end")
                self.filtros_activos.pop('desde', None)
                self.filtros_activos.pop('hasta', None)
                self.mostrar_reporte(tipo)

            ctk.CTkButton(
                fila,
                text="Filtrar",
                command=aplicar_filtros,
                width=80,
                fg_color=self._sel,
                hover_color=self._hover
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                fila,
                text="Limpiar",
                command=limpiar_filtros,
                width=80,
                fg_color="#455A64",
                hover_color="#263238"
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                fila,
                text="Hoy",
                command=lambda: entry_hasta.delete(0, "end") or entry_hasta.insert(0, datetime.now().strftime("%Y-%m-%d")),
                width=60,
                fg_color=self._accent_a,
                hover_color=self._hover
            ).pack(side="left", padx=5)

    def _crear_filtros_inventario(self, parent):
        """Crea filtros específicos para inventario con descripciones claras"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=0, pady=4)

        # Header con instrucciones mejoradas
        header_frame = ctk.CTkFrame(container, fg_color="transparent", corner_radius=8)
        header_frame.pack(fill="x", pady=(8, 12))
        
        ctk.CTkLabel(
            header_frame,
            text="💡 CÓMO USAR LOS FILTROS",
            font=("Segoe UI", 11, "bold"),
            text_color=self._accent_a
        ).pack(anchor="w", padx=10, pady=(4, 2))
        
        ctk.CTkLabel(
            header_frame,
            text="Selecciona 'Todos' para ver todo el inventario, o elige valores específicos para análisis detallado. Combina varios filtros para búsquedas precisas.",
            font=("Segoe UI", 9),
            text_color=self._text_secondary,
            wraplength=700
        ).pack(anchor="w", padx=10, pady=(0, 4))

        # Fila 1: Sexo del Animal
        fila1 = ctk.CTkFrame(container, fg_color="transparent")
        fila1.pack(fill="x", pady=4)

        pill_sexo = ctk.CTkFrame(fila1, fg_color=self._fg_card, corner_radius=10, border_width=1, border_color=self._border_soft)
        pill_sexo.pack(side="left", padx=4, pady=2)
        
        sexo_label_frame = ctk.CTkFrame(pill_sexo, fg_color="transparent")
        sexo_label_frame.pack(side="left", padx=6, pady=4)
        ctk.CTkLabel(sexo_label_frame, text="♂️♀️ Sexo del Animal", font=("Segoe UI", 11, "bold"), text_color=self._accent_a).pack(anchor="w")
        ctk.CTkLabel(sexo_label_frame, text="Selecciona Macho, Hembra o Todos", font=("Segoe UI", 9), text_color=self._text_secondary).pack(anchor="w")
        
        combo_sexo = ctk.CTkComboBox(pill_sexo, values=["Todos", "Macho", "Hembra"], width=140, state="readonly")
        combo_sexo.set("Todos")
        combo_sexo.pack(side="left", padx=6, pady=6)
        add_tooltip(combo_sexo, "Todos: Incluye machos y hembras\nMacho: Solo animales machos\nHembra: Solo animales hembras")

        # Estado del Animal
        pill_estado = ctk.CTkFrame(fila1, fg_color=self._fg_card, corner_radius=10, border_width=1, border_color=self._border_soft)
        pill_estado.pack(side="left", padx=4, pady=2)
        
        estado_label_frame = ctk.CTkFrame(pill_estado, fg_color="transparent")
        estado_label_frame.pack(side="left", padx=6, pady=4)
        ctk.CTkLabel(estado_label_frame, text="📊 Estado del Animal", font=("Segoe UI", 11, "bold"), text_color=self._accent_b).pack(anchor="w")
        ctk.CTkLabel(estado_label_frame, text="Activo, Vendido, Muerto o Todos", font=("Segoe UI", 9), text_color=self._text_secondary).pack(anchor="w")
        
        combo_estado = ctk.CTkComboBox(pill_estado, values=["Todos", "Activo", "Vendido", "Muerto"], width=150, state="readonly")
        combo_estado.set("Todos")
        combo_estado.pack(side="left", padx=6, pady=6)
        add_tooltip(combo_estado, "Todos: Muestra todos los registros\nActivo: Animales en operación\nVendido: Animales ya vendidos\nMuerto: Animales fallecidos")

        # Fila 2: Finca y Raza
        fila2 = ctk.CTkFrame(container, fg_color="transparent")
        fila2.pack(fill="x", pady=4)

        pill_finca = ctk.CTkFrame(fila2, fg_color=self._fg_card, corner_radius=10, border_width=1, border_color=self._border_soft)
        pill_finca.pack(side="left", padx=4, pady=2)
        
        finca_label_frame = ctk.CTkFrame(pill_finca, fg_color="transparent")
        finca_label_frame.pack(side="left", padx=6, pady=4)
        ctk.CTkLabel(finca_label_frame, text="🌾 Finca/Ubicación", font=("Segoe UI", 11, "bold"), text_color=self._accent_c).pack(anchor="w")
        ctk.CTkLabel(finca_label_frame, text="Selecciona una finca o todas", font=("Segoe UI", 9), text_color=self._text_secondary).pack(anchor="w")
        
        combo_finca = ctk.CTkComboBox(pill_finca, width=180, state="readonly")
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT f.nombre FROM finca f ORDER BY f.nombre")
                fincas = [r[0] for r in cursor.fetchall()]
            combo_finca.configure(values=["Todas"] + fincas)
        except:
            combo_finca.configure(values=["Todas"])
        combo_finca.set("Todas")
        combo_finca.pack(side="left", padx=6, pady=6)
        add_tooltip(combo_finca, "Todas: Muestra animales de todas las fincas\nSelecciona una para ver solo de esa ubicación")

        pill_raza = ctk.CTkFrame(fila2, fg_color=self._fg_card, corner_radius=10, border_width=1, border_color=self._border_soft)
        pill_raza.pack(side="left", padx=4, pady=2)
        
        raza_label_frame = ctk.CTkFrame(pill_raza, fg_color="transparent")
        raza_label_frame.pack(side="left", padx=6, pady=4)
        ctk.CTkLabel(raza_label_frame, text="🐮 Raza/Genética", font=("Segoe UI", 11, "bold"), text_color=self._sel).pack(anchor="w")
        ctk.CTkLabel(raza_label_frame, text="Filtra por línea genética", font=("Segoe UI", 9), text_color=self._text_secondary).pack(anchor="w")
        
        combo_raza = ctk.CTkComboBox(pill_raza, width=180, state="readonly")
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM raza ORDER BY nombre")
                razas = [r[0] for r in cursor.fetchall()]
            combo_raza.configure(values=["Todas"] + razas)
        except:
            combo_raza.configure(values=["Todas"])
        combo_raza.set("Todas")
        combo_raza.pack(side="left", padx=6, pady=6)
        add_tooltip(combo_raza, "Todas: Muestra todas las razas\nSelecciona una para análisis específico de genética")

        # Fila 3: Acciones y presets
        fila3 = ctk.CTkFrame(container, fg_color="transparent")
        fila3.pack(fill="x", pady=(6, 2))

        def aplicar_filtros_inv():
            sexo = combo_sexo.get()
            estado = combo_estado.get()
            finca = combo_finca.get()
            raza = combo_raza.get()

            self.filtros_activos['sexo'] = None if sexo == "Todos" else sexo
            self.filtros_activos['estado'] = None if estado == "Todos" else estado
            self.filtros_activos['finca'] = None if finca == "Todas" else finca
            self.filtros_activos['raza'] = None if raza == "Todas" else raza

            self.mostrar_reporte("inventario")

        def limpiar_filtros_inv():
            combo_sexo.set("Todos")
            combo_estado.set("Todos")
            combo_finca.set("Todas")
            combo_raza.set("Todas")
            self.filtros_activos = {}
            self.mostrar_reporte("inventario")

        def preset_activos():
            combo_sexo.set("Todos"); combo_estado.set("Activo"); combo_finca.set("Todas"); combo_raza.set("Todas"); aplicar_filtros_inv()

        def preset_machos():
            combo_sexo.set("Macho"); combo_estado.set("Todos"); combo_finca.set("Todas"); combo_raza.set("Todas"); aplicar_filtros_inv()

        def preset_hembras():
            combo_sexo.set("Hembra"); combo_estado.set("Todos"); combo_finca.set("Todas"); combo_raza.set("Todas"); aplicar_filtros_inv()

        ctk.CTkButton(
            fila3,
            text="🔍 Filtrar",
            command=aplicar_filtros_inv,
            width=100,
            fg_color=self._sel,
            hover_color=self._hover
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            fila3,
            text="🗑️ Limpiar",
            command=limpiar_filtros_inv,
            width=100,
            fg_color="#455A64",
            hover_color="#263238"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            fila3,
            text="✓ Activos",
            command=preset_activos,
            width=100,
            fg_color=self._accent_a,
            hover_color=self._hover
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            fila3,
            text="♂️ Machos",
            command=preset_machos,
            width=100,
            fg_color=self._accent_b,
            hover_color=self._hover
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            fila3,
            text="♀️ Hembras",
            command=preset_hembras,
            width=100,
            fg_color=self._accent_c,
            hover_color=self._hover
        ).pack(side="left", padx=4)

    def _reporte_dashboard(self, parent):
        """Dashboard principal con KPIs y gráficas profesional"""
        # Sección principal de resumen
        kpi_shell = self._section(parent, "📊 Resumen Ejecutivo del Sistema", "Visión integral de tu operación agropecuaria en tiempo real")
        kpi_frame = ctk.CTkFrame(kpi_shell, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=8, pady=6)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Queries principales
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                total_animales = cursor.fetchone()[0]

                cursor.execute("SELECT SUM(precio_compra) FROM animal WHERE estado = 'Activo'")
                valor_inv = cursor.fetchone()[0] or 0

                fecha_mes = datetime.now().replace(day=1).strftime("%Y-%m-%d")
                cursor.execute("SELECT COUNT(*) FROM venta WHERE fecha >= ?", (fecha_mes,))
                ventas_mes = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM empleado WHERE estado = 'Activo'")
                empleados = cursor.fetchone()[0]

                cursor.execute("SELECT SUM(cantidad) FROM venta WHERE fecha >= ?", (fecha_mes,))
                unidades_vendidas = cursor.fetchone()[0] or 0

                # Datos adicionales
                cursor.execute("SELECT SUM(litros_manana + litros_tarde + litros_noche) FROM produccion_leche WHERE fecha >= ?", (fecha_mes,))
                litros_mes = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM potrero WHERE estado = 'Activo'")
                potreros_activos = cursor.fetchone()[0]

                # Primera fila de KPIs - Principales
                self._kpi_card(kpi_frame, "📦 Total de Animales", f"{total_animales:,}", "En inventario activo", "#2E7D32")
                self._kpi_card(kpi_frame, "💵 Valor Patrimonial", f"${valor_inv:,.0f}", "Inversión total en ganado", "#1976D2")
                self._kpi_card(kpi_frame, "🔄 Transacciones", f"{ventas_mes:,}", "Este mes", "#FF6F00")
                self._kpi_card(kpi_frame, "👨‍🌾 Equipo", f"{empleados:,}", "Activos", "#C2185B")

                # Segunda fila - Complementarios
                kpi_frame2 = ctk.CTkFrame(kpi_shell, fg_color="transparent")
                kpi_frame2.pack(fill="x", padx=8, pady=6)
                
                self._kpi_card(kpi_frame2, "📈 Unidades Vendidas", f"{unidades_vendidas:,}", "Movimientos este mes", "#00897B")
                self._kpi_card(kpi_frame2, "🥛 Producción Lechera", f"{litros_mes:,} L", "Litros mes actual", "#D32F2F")
                self._kpi_card(kpi_frame2, "🌾 Potreros Activos", f"{potreros_activos:,}", "Áreas de pastoreo", "#1565C0")

        except Exception as e:
            self.logger.error(f"Error en dashboard: {e}")


        # Gráficas si matplotlib disponible
        if HAS_MATPLOTLIB:
            self._crear_graficos_dashboard(parent)

    def _reporte_inventario(self, parent):
        """Reporte de inventario con estadísticas y filtros avanzados"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener estadísticas generales
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                total_activos = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Vendido'")
                total_vendidos = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Muerto'")
                total_muertos = cursor.fetchone()[0]
                
                # Construir query con filtros
                query = """
                    SELECT a.codigo, a.nombre, a.sexo, r.nombre, a.estado, f.nombre
                    FROM animal a
                    LEFT JOIN raza r ON a.raza_id = r.id
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN finca f ON p.id_finca = f.id
                    WHERE 1=1
                """
                params = []
                
                # Aplicar filtros
                if self.filtros_activos.get('sexo'):
                    query += " AND a.sexo = ?"
                    params.append(self.filtros_activos['sexo'])
                
                if self.filtros_activos.get('estado'):
                    query += " AND a.estado = ?"
                    params.append(self.filtros_activos['estado'])
                
                if self.filtros_activos.get('finca'):
                    query += " AND f.nombre = ?"
                    params.append(self.filtros_activos['finca'])
                
                if self.filtros_activos.get('raza'):
                    query += " AND r.nombre = ?"
                    params.append(self.filtros_activos['raza'])
                
                query += " ORDER BY a.estado, a.codigo"
                
                cursor.execute(query, params)

                # Mostrar estadísticas rápidas
                stats_frame = self._section(parent, "📊 Resumen del Inventario", "Visión general de tu ganado")
                stats_kpi = ctk.CTkFrame(stats_frame, fg_color="transparent")
                stats_kpi.pack(fill="x", padx=8, pady=6)
                
                self._kpi_card(stats_kpi, "✓ Activos", f"{total_activos:,}", "En operación", "#2E7D32")
                self._kpi_card(stats_kpi, "🔄 Vendidos", f"{total_vendidos:,}", "Movimientos", "#FF9800")
                self._kpi_card(stats_kpi, "✗ Fallecidos", f"{total_muertos:,}", "Pérdidas", "#D32F2F")
                self._kpi_card(stats_kpi, "📦 Total", f"{total_activos + total_vendidos + total_muertos:,}", "Historial completo", "#1976D2")

                # Mostrar filtros activos de forma compacta
                if self.filtros_activos:
                    activos = []
                    mapping = {"sexo": "Sexo", "estado": "Estado", "finca": "Finca", "raza": "Raza"}
                    for clave, etiqueta in mapping.items():
                        valor = self.filtros_activos.get(clave)
                        if valor:
                            activos.append(f"{etiqueta}: {valor}")
                    if activos:
                        self._chip_row(parent, activos)

                # Tabla en sección estilizada
                tabla_section = self._section(parent, "📋 Detalle del Inventario", "Registros filtrados con información completa")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("codigo", "nombre", "sexo", "raza", "estado", "finca"),
                    show="headings",
                    height=15
                )

                for col, heading, width in [
                    ("codigo", "Código", 80),
                    ("nombre", "Nombre", 120),
                    ("sexo", "Sexo", 60),
                    ("raza", "Raza", 100),
                    ("estado", "Estado", 80),
                    ("finca", "Finca", 120)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                filas = cursor.fetchall()
                if not filas:
                    ctk.CTkLabel(
                        tabla_section,
                        text="No hay datos para los filtros seleccionados",
                        font=("Segoe UI", 12),
                        text_color=self._text_secondary
                    ).pack(pady=8)
                else:
                    for row in filas:
                        tabla.insert("", "end", values=row)

                if filas:
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side="right", fill="y")

                # Mostrar cantidad de resultados
                ctk.CTkLabel(
                    tabla_section,
                    text=f"📊 Total de animales encontrados: {len(filas)}",
                    font=("Segoe UI", 10),
                    text_color=self._text_secondary
                ).pack(padx=10, pady=(0, 10))

                # Resumen visual
                self._mostrar_resumen_inventario(parent, cursor)

        except Exception as e:
            self.logger.error(f"Error en inventario: {e}")
            ctk.CTkLabel(parent, text=f"Error: {e}").pack()

    def _reporte_ventas(self, parent):
        """Reporte de ventas con análisis"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar tabla
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='venta'")
                if not cursor.fetchone():
                    ctk.CTkLabel(parent, text="No hay datos de ventas registrados").pack()
                    return

                query = """
                    SELECT v.fecha, a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre'),
                           v.precio_total, v.comprador, v.motivo_venta
                    FROM venta v
                    JOIN animal a ON v.id_animal = a.id
                    ORDER BY v.fecha DESC
                """
                cursor.execute(query)

                ventas = cursor.fetchall()

                # Sección y tabla
                tabla_section = self._section(parent, "Ventas", "Movimientos y montos")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("fecha", "animal", "precio", "comprador", "motivo"),
                    show="headings",
                    height=15
                )

                for col, heading, width in [
                    ("fecha", "Fecha", 100),
                    ("animal", "Animal", 170),
                    ("precio", "Precio", 110),
                    ("comprador", "Comprador", 140),
                    ("motivo", "Motivo", 140)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                if ventas:
                    total_ventas = 0
                    for row in ventas:
                        tabla.insert("", "end", values=row)
                        total_ventas += row[2] or 0
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(tabla_section, text="No hay ventas registradas", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=8)
                    total_ventas = 0

                # Resumen con cards
                resumen = ctk.CTkFrame(parent, fg_color="transparent")
                resumen.pack(fill="x", padx=10, pady=(0, 10))
                cards = ctk.CTkFrame(resumen, fg_color="transparent")
                cards.pack(fill="x")
                self._kpi_card(cards, "Ventas registradas", f"{len(ventas):,}", "Total de movimientos", "#1976D2")
                self._kpi_card(cards, "Monto total", f"${total_ventas:,.2f}", "Suma de precios", "#2E7D32")
                if ventas:
                    promedio = total_ventas / max(len(ventas), 1)
                    self._kpi_card(cards, "Ticket promedio", f"${promedio:,.2f}", "Promedio por venta", "#FF6F00")

                # Ventas por finca (últimos 60 días)
                try:
                    cursor.execute(
                        """
                        SELECT COALESCE(f.nombre, 'Sin finca') as finca,
                               COUNT(*) as cantidad,
                               SUM(v.precio_total) as total
                        FROM venta v
                        LEFT JOIN animal a ON v.id_animal = a.id
                        LEFT JOIN potrero p ON a.id_potrero = p.id
                        LEFT JOIN finca f ON p.id_finca = f.id
                        WHERE v.fecha >= DATE('now', '-60 days')
                        GROUP BY finca
                        ORDER BY total DESC
                        LIMIT 8
                        """
                    )
                    ventas_finca = cursor.fetchall()
                except Exception:
                    ventas_finca = []

                finca_section = self._section(parent, "Ventas por finca (60 días)", "Top fincas por monto y cantidad")
                if ventas_finca:
                    table_finca = ctk.CTkFrame(finca_section, fg_color="transparent")
                    table_finca.pack(fill="x", padx=8, pady=6)
                    style_treeview()
                    tv_finca = ttk.Treeview(
                        table_finca,
                        columns=("finca", "cantidad", "total"),
                        show="headings",
                        height=8
                    )
                    for col, heading, width in [
                        ("finca", "Finca", 200),
                        ("cantidad", "Ventas", 90),
                        ("total", "Monto", 110)
                    ]:
                        tv_finca.heading(col, text=heading)
                        tv_finca.column(col, width=width)
                    for row in ventas_finca:
                        tv_finca.insert("", "end", values=(row[0], row[1], f"${(row[2] or 0):,.2f}"))
                    tv_finca.pack(side="left", fill="x", expand=True)
                    sb = ttk.Scrollbar(table_finca, orient="vertical", command=tv_finca.yview)
                    tv_finca.configure(yscrollcommand=sb.set)
                    sb.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(finca_section, text="No hay ventas recientes por finca", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=8)

        except Exception as e:
            self.logger.error(f"Error en ventas: {e}")

    def _reporte_salud(self, parent):
        """Reporte de salud animal"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.id, a.codigo, a.nombre, t.tipo_tratamiento, t.estado,
                           t.fecha_inicio, COALESCE(t.fecha_fin, '-') as fecha_fin
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    ORDER BY t.fecha_inicio DESC
                    LIMIT 100
                """)

                tratamientos = cursor.fetchall()

                tabla_section = self._section(parent, "Salud animal", "Tratamientos activos y completados")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("id", "codigo", "animal", "tipo", "estado", "inicio", "fin"),
                    show="headings",
                    height=15
                )

                for col, heading, width in [
                    ("id", "ID", 40),
                    ("codigo", "Código", 90),
                    ("animal", "Animal", 140),
                    ("tipo", "Tratamiento", 140),
                    ("estado", "Estado", 90),
                    ("inicio", "Inicio", 100),
                    ("fin", "Fin", 100)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                if tratamientos:
                    for row in tratamientos:
                        tabla.insert("", "end", values=row)
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(tabla_section, text="No hay tratamientos registrados", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=8)

                # Resumen por tipo de tratamiento
                try:
                    cursor.execute(
                        """
                        SELECT t.tipo_tratamiento, COUNT(*) as cantidad,
                               SUM(CASE WHEN t.estado = 'Activo' THEN 1 ELSE 0 END) as activos
                        FROM tratamiento t
                        GROUP BY t.tipo_tratamiento
                        ORDER BY cantidad DESC
                        LIMIT 6
                        """
                    )
                    resumen_tipo = cursor.fetchall()
                except Exception:
                    resumen_tipo = []

                if resumen_tipo:
                    resumen = ctk.CTkFrame(parent, fg_color="transparent")
                    resumen.pack(fill="x", padx=10, pady=(0, 10))
                    cards = ctk.CTkFrame(resumen, fg_color="transparent")
                    cards.pack(fill="x")
                    for tipo, cantidad, activos in resumen_tipo:
                        self._kpi_card(cards, tipo or "Sin tipo", f"{cantidad:,}", f"Activos: {activos or 0}", self._accent_a)
                else:
                    ctk.CTkLabel(parent, text="Sin datos de tipos de tratamiento", font=("Segoe UI", 11), text_color=self._text_muted).pack(pady=(0, 8))

        except Exception as e:
            self.logger.error(f"Error en salud: {e}")

    def _reporte_reproduccion(self, parent):
        """Reporte de reproducción"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, a.codigo, a.nombre, s.tipo_servicio, s.fecha_servicio,
                           s.estado, CASE WHEN s.fecha_servicio IS NOT NULL 
                           THEN DATE(s.fecha_servicio, '+280 days') ELSE '-' END as parto_estimado
                    FROM servicio_reproduccion s
                    JOIN animal a ON s.id_animal = a.id
                    ORDER BY s.fecha_servicio DESC
                    LIMIT 100
                """)

                servicios = cursor.fetchall()

                tabla_section = self._section(parent, "Reproducción", "Servicios, estados y parto estimado")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("id", "codigo", "animal", "tipo", "fecha", "estado", "parto"),
                    show="headings",
                    height=15
                )

                for col, heading, width in [
                    ("id", "ID", 40),
                    ("codigo", "Código", 90),
                    ("animal", "Animal", 140),
                    ("tipo", "Tipo", 90),
                    ("fecha", "Fecha", 110),
                    ("estado", "Estado", 90),
                    ("parto", "Parto Est.", 110)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                if servicios:
                    for row in servicios:
                        tabla.insert("", "end", values=row)
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(tabla_section, text="No hay servicios registrados", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=8)

        except Exception as e:
            self.logger.error(f"Error en reproducción: {e}")

    def _reporte_empleados(self, parent):
        """Reporte de empleados con datos de nómina integrados"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener resumen de empleados y últimos pagos
                cursor.execute("""
                    SELECT e.codigo, e.nombres || ' ' || e.apellidos as nombre_completo, 
                           e.cargo, e.salario_diario, e.estado, 
                           COALESCE(f.nombre, 'Sin Asignar') as finca,
                           (SELECT p.total_pagado FROM pago_nomina p 
                            WHERE p.codigo_empleado = e.codigo 
                            AND p.estado = 'Pagado' 
                            ORDER BY p.fecha_pago DESC LIMIT 1) as ultimo_pago,
                           (SELECT p.fecha_pago FROM pago_nomina p 
                            WHERE p.codigo_empleado = e.codigo 
                            AND p.estado = 'Pagado' 
                            ORDER BY p.fecha_pago DESC LIMIT 1) as fecha_ultimo_pago
                    FROM empleado e
                    LEFT JOIN finca f ON e.id_finca = f.id
                    ORDER BY e.estado DESC, e.nombres
                """)

                empleados = cursor.fetchall()

                # Sección de información general
                info_section = self._section(parent, "👨‍💼 Gestión de Personal", "Empleados, salarios y control de nómina")
                
                # KPIs de empleados
                if empleados:
                    total_empleados = len(empleados)
                    empleados_activos = len([e for e in empleados if e[4] == 'Activo'])
                    
                    # Calcular costo diario y mensual
                    cursor.execute("""
                        SELECT SUM(e.salario_diario), SUM(e.salario_diario) * 30
                        FROM empleado e
                        WHERE e.estado = 'Activo'
                    """)
                    costo_diario, costo_mensual = cursor.fetchone()
                    costo_diario = costo_diario or 0
                    costo_mensual = costo_mensual or 0
                    
                    # Obtener datos de último ciclo de nómina
                    cursor.execute("""
                        SELECT COUNT(*), SUM(p.total_pagado)
                        FROM pago_nomina p
                        WHERE p.estado = 'Pagado'
                        AND p.fecha_pago >= DATE('now', '-30 days')
                    """)
                    pagos_30_dias, total_pagado_30 = cursor.fetchone()
                    pagos_30_dias = pagos_30_dias or 0
                    total_pagado_30 = total_pagado_30 or 0
                    
                    # KPI Cards
                    kpi_frame = ctk.CTkFrame(info_section, fg_color="transparent")
                    kpi_frame.pack(fill="x", padx=8, pady=6)
                    
                    self._kpi_card(kpi_frame, "👥 Total Personal", f"{total_empleados:,}", "Registrados en sistema", "#1976D2")
                    self._kpi_card(kpi_frame, "✓ Activos", f"{empleados_activos:,}", "Trabajando actualmente", "#2E7D32")
                    self._kpi_card(kpi_frame, "💰 Costo Diario", f"${costo_diario:,.2f}", "Suma de salarios/día", "#FF6F00")
                    
                    kpi_frame2 = ctk.CTkFrame(info_section, fg_color="transparent")
                    kpi_frame2.pack(fill="x", padx=8, pady=6)
                    
                    self._kpi_card(kpi_frame2, "📊 Costo Mensual", f"${costo_mensual:,.2f}", "Proyección 30 días", "#C2185B")
                    self._kpi_card(kpi_frame2, "📋 Pagos Mes", f"{pagos_30_dias:,}", "Últimos 30 días", "#00897B")
                    self._kpi_card(kpi_frame2, "🏦 Pagado 30d", f"${total_pagado_30:,.2f}", "Total desembolsado", "#5E35B1")

                # Tabla de empleados con información de nómina
                tabla_section = self._section(parent, "Registro de Empleados", "Datos actuales y últimas transacciones")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("codigo", "nombre", "cargo", "finca", "salario_diario", "ultimo_pago", "fecha_pago", "estado"),
                    show="headings",
                    height=12
                )

                for col, heading, width in [
                    ("codigo", "Código", 80),
                    ("nombre", "Nombre Completo", 160),
                    ("cargo", "Cargo", 120),
                    ("finca", "Finca", 140),
                    ("salario_diario", "Salario/Día", 100),
                    ("ultimo_pago", "Ult. Pago", 110),
                    ("fecha_pago", "Fecha Pago", 110),
                    ("estado", "Estado", 80)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                if empleados:
                    for row in empleados:
                        codigo, nombre, cargo, salario_diario, estado, finca, ultimo_pago, fecha_ultimo_pago = row
                        tabla.insert("", "end", values=(
                            codigo,
                            nombre,
                            cargo or "N/A",
                            finca,
                            f"${salario_diario:,.2f}" if salario_diario else "$0.00",
                            f"${ultimo_pago:,.2f}" if ultimo_pago else "Sin pago",
                            fecha_ultimo_pago or "N/A",
                            estado
                        ))
                    
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
                    scrollbar.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(tabla_section, text="No hay empleados registrados", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=20)

                # Sección de historial de nómina
                hist_section = self._section(parent, "📋 Historial de Nómina Reciente", "Últimos pagos realizados (últimos 30 días)")
                hist_frame = ctk.CTkFrame(hist_section, fg_color="transparent")
                hist_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla_hist = ttk.Treeview(
                    hist_frame,
                    columns=("fecha", "empleado", "periodo", "dias", "salario", "bonos", "deducciones", "total", "estado"),
                    show="headings",
                    height=10
                )

                for col, heading, width in [
                    ("fecha", "Fecha Pago", 100),
                    ("empleado", "Empleado", 140),
                    ("periodo", "Período", 140),
                    ("dias", "Días", 50),
                    ("salario", "Salario", 90),
                    ("bonos", "Bonos", 80),
                    ("deducciones", "Descuentos", 80),
                    ("total", "Total Pagado", 100),
                    ("estado", "Estado", 80)
                ]:
                    tabla_hist.heading(col, text=heading)
                    tabla_hist.column(col, width=width)

                cursor.execute("""
                    SELECT p.fecha_pago, e.nombres || ' ' || e.apellidos,
                           p.periodo_inicio || ' a ' || p.periodo_fin,
                           p.dias_trabajados, p.salario_base, p.bonos, p.deducciones,
                           p.total_pagado, p.estado
                    FROM pago_nomina p
                    JOIN empleado e ON p.codigo_empleado = e.codigo
                    WHERE p.estado = 'Pagado'
                    AND p.fecha_pago >= DATE('now', '-30 days')
                    ORDER BY p.fecha_pago DESC
                    LIMIT 30
                """)
                
                pagos = cursor.fetchall()
                if pagos:
                    for row in pagos:
                        fecha, empleado, periodo, dias, salario, bonos, descuentos, total, estado = row
                        tabla_hist.insert("", "end", values=(
                            fecha,
                            empleado,
                            periodo,
                            dias,
                            f"${salario:,.2f}",
                            f"${bonos:,.2f}",
                            f"${descuentos:,.2f}",
                            f"${total:,.2f}",
                            estado
                        ))
                    
                    tabla_hist.pack(side="left", fill="both", expand=True)
                    scrollbar_hist = ttk.Scrollbar(hist_frame, orient="vertical", command=tabla_hist.yview)
                    tabla_hist.configure(yscroll=scrollbar_hist.set)  # type: ignore[arg-type]
                    scrollbar_hist.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(hist_section, text="No hay registros de nómina en los últimos 30 días", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=20)

        except Exception as e:
            self.logger.error(f"Error en empleados: {e}")

    def _reporte_potreros(self, parent):
        """Reporte de potreros y capacidad mejorado"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener datos de potreros
                cursor.execute("""
                    SELECT p.id, p.nombre, f.nombre, p.area_hectareas, p.capacidad_maxima,
                           COUNT(a.id) as ocupacion, p.tipo_pasto, p.estado
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN animal a ON a.id_potrero = p.id AND a.estado = 'Activo'
                    GROUP BY p.id
                    ORDER BY f.nombre, p.nombre
                """)

                potreros = cursor.fetchall()

                # Sección de información
                info_section = self._section(parent, "🌾 Gestión de Potreros", "Ocupación, capacidad y salud del pastizal")
                
                # Estadísticas rápidas
                if potreros:
                    total_potreros = len(potreros)
                    total_animales = sum(int(p[5]) for p in potreros if p[5])
                    total_capacidad = sum(int(p[4]) for p in potreros if p[4])
                    
                    kpi_frame = ctk.CTkFrame(info_section, fg_color="transparent")
                    kpi_frame.pack(fill="x", padx=8, pady=6)
                    
                    self._kpi_card(kpi_frame, "🏘️ Total Potreros", f"{total_potreros:,}", "Áreas activas", "#00897B")
                    self._kpi_card(kpi_frame, "🐄 Animales", f"{total_animales:,}", "En potreros activos", "#1976D2")
                    self._kpi_card(kpi_frame, "📊 Capacidad Total", f"{total_capacidad:,}", "Máximo recomendado", "#FF6F00")
                    
                    # Porcentaje de ocupación
                    if total_capacidad > 0:
                        ocup_pct = (total_animales / total_capacidad) * 100
                        color_ocup = "#2E7D32" if ocup_pct <= 80 else ("#FF9800" if ocup_pct <= 100 else "#D32F2F")
                        self._kpi_card(kpi_frame, "📈 Ocupación Total", f"{ocup_pct:.1f}%", "Vs. Capacidad máxima", color_ocup)

                # Tabla de potreros detallada
                tabla_section = self._section(parent, "Detalle por Potrero", "Ocupación actual y disponibilidad")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("potrero", "finca", "area", "capacidad", "ocupacion", "disponible", "pasto", "estado"),
                    show="headings",
                    height=15
                )

                for col, heading, width in [
                    ("potrero", "Potrero", 120),
                    ("finca", "Finca", 120),
                    ("area", "Área (ha)", 80),
                    ("capacidad", "Capacidad", 80),
                    ("ocupacion", "Ocupados", 80),
                    ("disponible", "Disponibles", 90),
                    ("pasto", "Tipo Pasto", 100),
                    ("estado", "Estado", 80)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                if potreros:
                    for row in potreros:
                        potrero_id, nombre, finca, area, capacidad, ocupacion, pasto, estado = row
                        ocupacion = int(ocupacion) if ocupacion else 0
                        capacidad = int(capacidad) if capacidad else 0
                        disponible = capacidad - ocupacion
                        
                        tabla.insert("", "end", values=(
                            nombre,
                            finca or "N/A",
                            f"{area:.2f}" if area else "N/A",
                            capacidad,
                            ocupacion,
                            disponible,
                            pasto or "No especificado",
                            estado
                        ))
                    
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
                    scrollbar.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(tabla_section, text="No hay potreros registrados", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=20)

        except Exception as e:
            self.logger.error(f"Error en potreros: {e}")

    def _reporte_leche(self, parent):
        """Reporte profesional de producción de leche"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # KPIs de leche
                mes_actual = datetime.now().strftime("%Y-%m-01")
                cursor.execute(
                    "SELECT SUM(litros_manana + litros_tarde + litros_noche) FROM produccion_leche WHERE fecha >= ?",
                    (mes_actual,)
                )
                litros_mes = cursor.fetchone()[0] or 0

                cursor.execute(
                    "SELECT AVG(litros_manana + litros_tarde + litros_noche) FROM produccion_leche WHERE fecha >= ?",
                    (mes_actual,)
                )
                promedio_diario = cursor.fetchone()[0] or 0

                cursor.execute(
                    "SELECT COUNT(DISTINCT animal_id) FROM produccion_leche WHERE fecha >= ?",
                    (mes_actual,)
                )
                vacas_productivas = cursor.fetchone()[0] or 0

                # KPI Cards
                kpi_shell = self._section(parent, "Resumen de producción", "Métricas del mes actual")
                kpi_frame = ctk.CTkFrame(kpi_shell, fg_color="transparent")
                kpi_frame.pack(fill="x", padx=8, pady=8)

                self._kpi_card(kpi_frame, "Litros/mes", f"{litros_mes:,.0f}", "Producción total mes", "#1976D2")
                self._kpi_card(kpi_frame, "Promedio/día", f"{promedio_diario:,.1f}", "Litros diarios", "#2E7D32")
                self._kpi_card(kpi_frame, "Vacas activas", f"{vacas_productivas:,}", "Produciendo en el mes", "#FF6F00")

                if vacas_productivas > 0:
                    litros_por_vaca = litros_mes / vacas_productivas
                    self._kpi_card(kpi_frame, "Litros/vaca/mes", f"{litros_por_vaca:,.1f}", "Promedio por animal", "#C2185B")

                # Botón de gráficos
                if HAS_MATPLOTLIB:
                    btn_frame = ctk.CTkFrame(kpi_shell, fg_color="transparent")
                    btn_frame.pack(fill="x", padx=8, pady=8)
                    btn_graficos = ctk.CTkButton(
                        btn_frame,
                        text="📊 Gráficos",
                        command=lambda: self._crear_graficos_leche(parent),
                        fg_color=self._accent_b,
                        text_color="white",
                        height=32,
                        font=("Segoe UI", 11, "bold")
                    )
                    btn_graficos.pack(side="left", padx=4)

                # Tabla de últimas producciones
                cursor.execute("""
                    SELECT a.codigo, a.nombre, pl.fecha,
                           pl.litros_manana, pl.litros_tarde, pl.litros_noche,
                           (pl.litros_manana + pl.litros_tarde + pl.litros_noche) as total
                    FROM produccion_leche pl
                    JOIN animal a ON pl.animal_id = a.id
                    ORDER BY pl.fecha DESC
                    LIMIT 30
                """)
                registros = cursor.fetchall()

                tabla_section = self._section(parent, "Últimas producciones (30 días)", "Detalle diario por animal")
                table_frame = ctk.CTkFrame(tabla_section, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=8, pady=8)

                style_treeview()
                tabla = ttk.Treeview(
                    table_frame,
                    columns=("codigo", "animal", "fecha", "manana", "tarde", "noche", "total"),
                    show="headings",
                    height=15
                )

                for col, heading, width in [
                    ("codigo", "Código", 80),
                    ("animal", "Animal", 140),
                    ("fecha", "Fecha", 100),
                    ("manana", "Mañana (L)", 80),
                    ("tarde", "Tarde (L)", 80),
                    ("noche", "Noche (L)", 80),
                    ("total", "Total (L)", 90)
                ]:
                    tabla.heading(col, text=heading)
                    tabla.column(col, width=width)

                if registros:
                    for row in registros:
                        tabla.insert("", "end", values=row)
                    tabla.pack(side="left", fill="both", expand=True)
                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
                    tabla.configure(yscroll=scrollbar.set)  # type: ignore[arg-type]
                    scrollbar.pack(side="right", fill="y")
                else:
                    ctk.CTkLabel(tabla_section, text="No hay registros de producción de leche", font=("Segoe UI", 12), text_color=self._text_secondary).pack(pady=8)

                # Gráficos si matplotlib disponible
                if HAS_MATPLOTLIB:
                    self._crear_graficos_leche(parent)

        except Exception as e:
            self.logger.error(f"Error en leche: {e}")
            ctk.CTkLabel(parent, text=f"Error: {e}").pack()

    def _crear_graficos_leche(self, parent):
        """Crea gráficos para producción de leche"""
        if not HAS_MATPLOTLIB:
            return

        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.patch.set_facecolor('#1a1a1a' if self._modo == "Dark" else '#f0f0f0')

            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Gráfico 1: Litros por mes (últimos 6 meses)
                cursor.execute("""
                    SELECT DATE(fecha, 'start of month') as mes,
                           SUM(litros_manana + litros_tarde + litros_noche) as total
                    FROM produccion_leche
                    WHERE fecha >= DATE('now', '-6 months')
                    GROUP BY DATE(fecha, 'start of month')
                    ORDER BY mes
                """)
                datos_mes = cursor.fetchall()
                if datos_mes:
                    meses = [r[0] for r in datos_mes]
                    litros = [r[1] or 0 for r in datos_mes]
                    axes[0, 0].plot(meses, litros, marker='o', color=self._accent_a, linewidth=2)
                    axes[0, 0].fill_between(range(len(meses)), litros, alpha=0.3, color=self._accent_a)
                    axes[0, 0].set_title('Litros por Mes (últimos 6)', fontsize=12, fontweight='bold')
                    axes[0, 0].set_ylabel('Litros')
                    axes[0, 0].tick_params(axis='x', rotation=45)

                # Gráfico 2: Top vacas por producción (mes actual)
                mes_actual = datetime.now().strftime("%Y-%m-01")
                cursor.execute("""
                    SELECT a.codigo || ' - ' || a.nombre,
                           SUM(pl.litros_manana + pl.litros_tarde + pl.litros_noche) as total
                    FROM produccion_leche pl
                    JOIN animal a ON pl.animal_id = a.id
                    WHERE pl.fecha >= ?
                    GROUP BY pl.animal_id
                    ORDER BY total DESC
                    LIMIT 10
                """, (mes_actual,))
                datos_vacas = cursor.fetchall()
                if datos_vacas:
                    vacas = [r[0] for r in datos_vacas]
                    totales = [r[1] or 0 for r in datos_vacas]
                    axes[0, 1].barh(vacas, totales, color=self._accent_b)
                    axes[0, 1].set_title('Top 10 Vacas (mes actual)', fontsize=12, fontweight='bold')
                    axes[0, 1].set_xlabel('Litros')

                # Gráfico 3: Producción por turno (pie)
                cursor.execute("""
                    SELECT 'Mañana' as turno, SUM(litros_manana) as total FROM produccion_leche WHERE fecha >= ?
                    UNION ALL
                    SELECT 'Tarde', SUM(litros_tarde) FROM produccion_leche WHERE fecha >= ?
                    UNION ALL
                    SELECT 'Noche', SUM(litros_noche) FROM produccion_leche WHERE fecha >= ?
                """, (mes_actual, mes_actual, mes_actual))
                datos_turnos = cursor.fetchall()
                if datos_turnos:
                    turnos = [r[0] for r in datos_turnos]
                    cantidades = [r[1] or 0 for r in datos_turnos]
                    axes[1, 0].pie(cantidades, labels=turnos, autopct='%1.1f%%', colors=[self._accent_c, self._sel, self._accent_a])
                    axes[1, 0].set_title('Producción por Turno', fontsize=12, fontweight='bold')

                # Gráfico 4: Promedio por vaca (últimos 30 días)
                cursor.execute("""
                    SELECT a.codigo || ' - ' || a.nombre,
                           AVG(pl.litros_manana + pl.litros_tarde + pl.litros_noche) as promedio
                    FROM produccion_leche pl
                    JOIN animal a ON pl.animal_id = a.id
                    WHERE pl.fecha >= DATE('now', '-30 days')
                    GROUP BY pl.animal_id
                    ORDER BY promedio DESC
                    LIMIT 12
                """)
                datos_promedio = cursor.fetchall()
                if datos_promedio:
                    vacas_prom = [r[0] for r in datos_promedio]
                    promedios = [r[1] or 0 for r in datos_promedio]
                    axes[1, 1].bar(range(len(vacas_prom)), promedios, color=self._accent_a)
                    axes[1, 1].set_title('Promedio Litros/Día por Vaca (30 días)', fontsize=12, fontweight='bold')
                    axes[1, 1].set_ylabel('Litros')
                    axes[1, 1].set_xticks(range(len(vacas_prom)))
                    axes[1, 1].set_xticklabels([v.split(' - ')[0] for v in vacas_prom], rotation=45, ha='right')

            plt.tight_layout()

            # Insertar en Tkinter
            canvas_frame = ctk.CTkFrame(parent)
            canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            self.logger.error(f"Error en gráficos leche: {e}")

    def _reporte_actividad(self, parent):
        """Reporte de actividad reciente"""
        section = self._section(parent, "Actividad reciente", "Movimientos y eventos más recientes")
        ctk.CTkLabel(
            section,
            text="Este reporte muestra los movimientos más recientes del sistema",
            font=("Segoe UI", 12),
            text_color=self._text_secondary
        ).pack(pady=12)
        ctk.CTkLabel(
            section,
            text="Pronto se incluirán logs y eventos detallados.",
            font=("Segoe UI", 11),
            text_color=self._text_muted
        ).pack(pady=(0, 10))

    def _mostrar_resumen_inventario(self, parent, cursor):
        """Muestra resumen del inventario"""
        cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM animal WHERE sexo = 'Macho' AND estado = 'Activo'")
        machos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM animal WHERE sexo = 'Hembra' AND estado = 'Activo'")
        hembras = cursor.fetchone()[0]
        resumen = self._section(parent, "Resumen rápido", "Indicadores clave del inventario activo")
        cards = ctk.CTkFrame(resumen, fg_color="transparent")
        cards.pack(fill="x", padx=8, pady=8)
        self._kpi_card(cards, "Total activos", f"{total:,}", "Animales en el inventario", "#1976D2")
        self._kpi_card(cards, "Machos", f"{machos:,}", "Proporción actual", "#2E7D32")
        self._kpi_card(cards, "Hembras", f"{hembras:,}", "Proporción actual", "#C2185B")

    def _crear_graficos_dashboard(self, parent):
        """Crea gráficos para el dashboard"""
        if not HAS_MATPLOTLIB:
            return

        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.patch.set_facecolor('#1a1a1a' if self._modo == "Dark" else '#f0f0f0')

            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Gráfico 1: Animales por estado
                cursor.execute("SELECT estado, COUNT(*) FROM animal GROUP BY estado")
                datos_estados = cursor.fetchall()
                estados = [r[0] for r in datos_estados]
                cantidades = [r[1] for r in datos_estados]

                axes[0, 0].pie(cantidades or [1], labels=estados or ["Sin datos"], autopct='%1.1f%%')
                axes[0, 0].set_title('Animales por Estado')

                # Gráfico 2: Distribuión por sexo
                cursor.execute("SELECT sexo, COUNT(*) FROM animal WHERE estado = 'Activo' GROUP BY sexo")
                datos = cursor.fetchall()
                if datos:
                    sexos = [r[0] for r in datos]
                    cant_sexo = [r[1] for r in datos]
                    axes[0, 1].bar(sexos, cant_sexo, color=['#2E7D32', '#C2185B'])
                    axes[0, 1].set_title('Distribución por Sexo')
                    axes[0, 1].set_ylabel('Cantidad')

                # Gráfico 3: Ocupación de potreros
                cursor.execute("""
                    SELECT p.nombre,
                    CAST(COUNT(a.id) AS FLOAT) / NULLIF(p.capacidad_maxima, 0) * 100
                    FROM potrero p
                    LEFT JOIN animal a ON a.id_potrero = p.id
                    WHERE p.estado = 'Activo'
                    GROUP BY p.id
                    LIMIT 10
                """)
                datos_pot = cursor.fetchall()
                if datos_pot:
                    nombres = [r[0] for r in datos_pot]
                    ocupacion = [r[1] or 0 for r in datos_pot]
                    axes[1, 0].barh(nombres, ocupacion, color='#FF6F00')
                    axes[1, 0].set_title('Ocupación de Potreros (%)')
                    axes[1, 0].set_xlabel('Ocupación %')

                # Gráfico 4: Razas
                cursor.execute("""
                    SELECT r.nombre, COUNT(*) FROM animal a
                    LEFT JOIN raza r ON a.raza_id = r.id
                    WHERE a.estado = 'Activo'
                    GROUP BY a.raza_id
                    LIMIT 8
                """)
                datos_raza = cursor.fetchall()
                if datos_raza:
                    razas = [r[0] or 'Sin Raza' for r in datos_raza]
                    cant_raza = [r[1] for r in datos_raza]
                    axes[1, 1].bar(razas, cant_raza, color='#1976D2')
                    axes[1, 1].set_title('Animales por Raza')
                    axes[1, 1].tick_params(axis='x', rotation=45)

            plt.tight_layout()

            # Insertar en Tkinter
            canvas_frame = ctk.CTkFrame(parent)
            canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

            canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            self.logger.error(f"Error en gráficos: {e}")

    def _mostrar_graficos(self, tipo):
        """Muestra gráficos específicos por tipo de reporte"""
        if not HAS_MATPLOTLIB:
            messagebox.showwarning("Advertencia", "Matplotlib no está disponible")
            return

        # Ventana flotante con gráficos
        ventana = ctk.CTkToplevel(self)
        ventana.title(f"Gráficos - {self.reportes[tipo][0]}")
        ventana.geometry("1000x700")

        frame = ctk.CTkFrame(ventana)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            if tipo == "inventario":
                self._grafico_inventario(frame)
            elif tipo == "ventas":
                self._grafico_ventas(frame)
            elif tipo == "salud":
                self._grafico_salud(frame)
        except Exception as e:
            ctk.CTkLabel(frame, text=f"Error: {e}").pack()

    def _grafico_inventario(self, parent):
        """Gráfico de inventario"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Por sexo
                cursor.execute("SELECT sexo, COUNT(*) FROM animal WHERE estado = 'Activo' GROUP BY sexo")
                datos = cursor.fetchall()
                sexos = [r[0] or 'Desconocido' for r in datos]
                cant = [r[1] for r in datos]
                
                ax1.pie(cant, labels=sexos, autopct='%1.1f%%', colors=['#2E7D32', '#C2185B'])
                ax1.set_title('Distribución por Sexo')
                
                # Por finca
                cursor.execute("""
                    SELECT f.nombre, COUNT(*)
                    FROM animal a
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN finca f ON p.id_finca = f.id
                    WHERE a.estado = 'Activo'
                    GROUP BY f.id
                """)
                datos = cursor.fetchall()
                fincas = [r[0] or 'Sin Finca' for r in datos]
                cant = [r[1] for r in datos]
                
                ax2.bar(fincas, cant, color='#1976D2')
                ax2.set_title('Animales por Finca')
                ax2.set_ylabel('Cantidad')
                
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def _grafico_ventas(self, parent):
        """Gráfico de ventas"""
        try:
            fig, ax = plt.subplots(figsize=(12, 5))
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DATE(fecha), COUNT(*), SUM(precio_total)
                    FROM venta
                    WHERE fecha >= DATE('now', '-30 days')
                    GROUP BY DATE(fecha)
                    ORDER BY DATE(fecha)
                """)
                
                datos = cursor.fetchall()
                if datos:
                    fechas = [r[0] for r in datos]
                    cantidades = [r[1] for r in datos]
                    montos = [r[2] for r in datos]
                    
                    ax2 = ax.twinx()
                    ax.bar(fechas, cantidades, label='Ventas', color='#2E7D32', alpha=0.7)
                    ax2.plot(fechas, montos, label='Monto Total', color='#FF6F00', marker='o')
                    
                    ax.set_title('Ventas últimos 30 días')
                    ax.set_xlabel('Fecha')
                    ax.set_ylabel('Cantidad de Ventas', color='#2E7D32')
                    ax2.set_ylabel('Monto ($)', color='#FF6F00')
                    ax.tick_params(axis='x', rotation=45)
                    
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def _grafico_salud(self, parent):
        """Gráficos rápidos de salud"""
        try:
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Distribución por estado
                cursor.execute("SELECT estado, COUNT(*) FROM tratamiento GROUP BY estado")
                datos_estado = cursor.fetchall()
                etiquetas = [r[0] or 'Sin estado' for r in datos_estado]
                valores = [r[1] for r in datos_estado]
                axes[0].pie(valores or [1], labels=etiquetas or ['Sin datos'], autopct='%1.1f%%')
                axes[0].set_title('Tratamientos por estado')

                # Top tipos
                cursor.execute("SELECT tipo_tratamiento, COUNT(*) FROM tratamiento GROUP BY tipo_tratamiento ORDER BY COUNT(*) DESC LIMIT 8")
                datos_tipo = cursor.fetchall()
                if datos_tipo:
                    tipos = [r[0] or 'Sin tipo' for r in datos_tipo]
                    cant = [r[1] for r in datos_tipo]
                    axes[1].barh(tipos, cant, color=self._accent_b)
                    axes[1].set_title('Top tipos de tratamiento')

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def _exportar_csv(self, tipo_reporte):
        """Exporta reporte a CSV"""
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"reporte_{tipo_reporte}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        if not archivo:
            return

        try:
            with open(archivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([f"Reporte: {self.reportes[tipo_reporte][0]}"])
                writer.writerow([f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])
                # Los datos específicos se agregarían aquí

            messagebox.showinfo("Éxito", f"Reporte exportado a:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")
