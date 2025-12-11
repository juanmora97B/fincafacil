import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter, MonthLocator
from datetime import datetime, timedelta

# Importaciones corregidas
try:
    from database.database import get_db_connection
    from modules.utils.logger import get_logger
    from modules.utils.ui import add_tooltip
    from modules.utils.notificaciones import SistemaNotificaciones
    from modules.utils.colores import obtener_colores
except ImportError as e:
    import logging
    logging.error(f"Error importando dependencias en dashboard: {e}")

class DashboardModule(ctk.CTkFrame):
    """Dashboard profesional del sistema con KPIs, gráficos interactivos y alertas reales."""
    
    # Colores corporativos
    COLORS_CORP = {
        "primary": "#1E88E5",      # Azul profesional
        "success": "#43A047",       # Verde profesional
        "warning": "#FB8C00",       # Naranja profesional
        "danger": "#E53935",        # Rojo profesional
        "info": "#0097A7",          # Cyan profesional
        "secondary": "#5E35B1",     # Púrpura profesional
    }

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Configurar logger
        self.logger = get_logger("Dashboard")
        self.logger.info("Módulo Dashboard rediseñado iniciado")
        
        # Obtener colores del módulo
        self.color_bg, self.color_hover = obtener_colores('dashboard')
        
        # Inicializar sistema de notificaciones
        self.sistema_notificaciones = SistemaNotificaciones()
        
        # Estado del filtro de periodo
        self.periodo_actual = "Últimos 30 días"
        self.rango_dias_produccion = 30
        
        # Inicializar interfaz y datos
        self.crear_widgets()
        self.actualizar_estadisticas()

    # =========================================================
    #                      CREACIÓN DE UI - REDISEÑADA
    # =========================================================
    def crear_widgets(self):
        """Construcción completa de la interfaz del Dashboard rediseñada"""
        # Contenedor principal scrollable
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # ---------- TÍTULO Y CONTROLES ----------
        self._crear_titulo_y_controles(container)

        # ---------- FILA 1: MÉTRICAS KPI (8 tarjetas) ----------
        self._crear_metricas_kpi(container)

        # ---------- FILA 2: ESTADO DE ANIMALES + EVENTOS RECIENTES ----------
        fila2_frame = ctk.CTkFrame(container, fg_color="transparent")
        fila2_frame.pack(fill="both", expand=True, pady=(10, 10))
        fila2_frame.columnconfigure(0, weight=1)
        fila2_frame.columnconfigure(1, weight=1)
        
        self._crear_grafico_estados(fila2_frame)
        self._crear_panel_eventos(fila2_frame)

        # ---------- FILA 3: PRODUCCIÓN DE LECHE + ALERTAS ----------
        fila3_frame = ctk.CTkFrame(container, fg_color="transparent")
        fila3_frame.pack(fill="both", expand=True, pady=(0, 10))
        fila3_frame.columnconfigure(0, weight=1)
        fila3_frame.columnconfigure(1, weight=1)
        
        self._crear_grafico_produccion(fila3_frame)
        self._crear_panel_alertas(fila3_frame)

    def _crear_titulo_y_controles(self, parent):
        """Crea el título y los controles de filtro"""
        titulo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(0, 15))

        # Título
        titulo_container = ctk.CTkFrame(
            titulo_frame,
            fg_color=self.COLORS_CORP["primary"],
            corner_radius=16,
            height=65
        )
        titulo_container.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        ctk.CTkLabel(
            titulo_container,
            text="📊 Dashboard Profesional",
            font=("Segoe UI", 26, "bold"),
            text_color="white"
        ).pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(
            titulo_container,
            text="Sistema de Gestión Integral",
            font=("Segoe UI", 11),
            text_color="#B3E5FC"
        ).pack(side="left", padx=(0, 15))

        # Controles
        controles_frame = ctk.CTkFrame(titulo_frame, fg_color="transparent")
        controles_frame.pack(side="right")
        
        # Selector de rango para producción
        ctk.CTkLabel(controles_frame, text="Rango:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        self.combo_rango_produccion = ctk.CTkComboBox(
            controles_frame,
            values=["7 días", "15 días", "30 días", "90 días"],
            width=100,
            command=self._on_rango_produccion_change
        )
        self.combo_rango_produccion.set("30 días")
        self.combo_rango_produccion.pack(side="left", padx=5)
        
        # Botón actualizar
        ctk.CTkButton(
            controles_frame,
            text="🔄 Actualizar",
            command=self.actualizar_estadisticas,
            width=110,
            font=("Segoe UI", 11, "bold"),
            fg_color=self.COLORS_CORP["success"],
            hover_color="#5CB85C",
            corner_radius=12
        ).pack(side="left", padx=5)

    def _crear_metricas_kpi(self, parent):
        """Crea las 8 tarjetas de métricas KPI"""
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 15))

        # Configurar grid para 8 columnas
        for i in range(8):
            metrics_frame.columnconfigure(i, weight=1)

        # Definición de métricas con colores corporativos
        self.metricas = {
            "total_animales": self._crear_kpi_card(
                metrics_frame, 
                "🐄 Total", 
                "0", 
                self.COLORS_CORP["primary"], 
                0
            ),
            "activos": self._crear_kpi_card(
                metrics_frame, 
                "✅ Activos", 
                "0", 
                self.COLORS_CORP["success"], 
                1
            ),
            "muertos": self._crear_kpi_card(
                metrics_frame, 
                "⚰️ Muertos", 
                "0", 
                self.COLORS_CORP["danger"], 
                2
            ),
            "vendidos": self._crear_kpi_card(
                metrics_frame, 
                "🛒 Vendidos", 
                "0", 
                "#673AB7", 
                3
            ),
            "en_tratamiento": self._crear_kpi_card(
                metrics_frame, 
                "🏥 Tratamiento", 
                "0", 
                self.COLORS_CORP["warning"], 
                4
            ),
            "gestantes": self._crear_kpi_card(
                metrics_frame, 
                "🤰 Gestantes", 
                "0", 
                "#E91E63", 
                5
            ),
            "produccion_hoy": self._crear_kpi_card(
                metrics_frame, 
                "🥛 Prod. HOY", 
                "0L", 
                self.COLORS_CORP["info"], 
                6
            ),
            "nacimientos_mes": self._crear_kpi_card(
                metrics_frame, 
                "👶 Nacimientos", 
                "0", 
                "#FF6F00", 
                7
            ),
        }

    def _crear_kpi_card(self, parent, titulo, valor, color, columna):
        """Crea una tarjeta KPI profesional con tamaño uniforme"""
        card = ctk.CTkFrame(
            parent, 
            fg_color=color, 
            corner_radius=16,
            border_width=0,
            width=140,
            height=100
        )
        card.grid(row=0, column=columna, sticky="nsew", padx=4, pady=4)
        card.grid_propagate(False)  # Mantener tamaño fijo

        # Icono + Título
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(10, 5))

        # Título con tamaño fijo
        title_label = ctk.CTkLabel(
            header, 
            text=titulo, 
            font=("Segoe UI", 9, "bold"), 
            text_color="white",
            wraplength=120
        )
        title_label.pack()

        # Valor con tamaño consistente
        valor_label = ctk.CTkLabel(
            card, 
            text=valor, 
            font=("Segoe UI", 20, "bold"), 
            text_color="white"
        )
        valor_label.pack(pady=(5, 10))

        return valor_label

    def _crear_grafico_estados(self, parent):
        """Crea el gráfico de estado de animales en el lado izquierdo"""
        estados_frame = ctk.CTkFrame(
            parent,
            corner_radius=16,
            border_width=1,
            border_color="#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#424242",
            fg_color="#F5F5F5" if ctk.get_appearance_mode() == "Light" else "#1E1E1E"
        )
        estados_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Header
        header = ctk.CTkFrame(estados_frame, fg_color=self.COLORS_CORP["success"], corner_radius=14)
        header.pack(fill="x", padx=8, pady=8)
        
        ctk.CTkLabel(
            header,
            text="📊 Estado de Animales",
            font=("Segoe UI", 13, "bold"),
            text_color="white"
        ).pack(pady=8)

        # Gráfico
        self.fig_estados, self.ax_estados = plt.subplots(figsize=(6.5, 4))
        self._estilizar_matplotlib()
        
        self.canvas_estados = FigureCanvasTkAgg(self.fig_estados, estados_frame)
        self.canvas_estados.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _crear_grafico_produccion(self, parent):
        """Crea el gráfico de producción de leche en el lado izquierdo"""
        prod_frame = ctk.CTkFrame(
            parent,
            corner_radius=16,
            border_width=1,
            border_color="#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#424242",
            fg_color="#F5F5F5" if ctk.get_appearance_mode() == "Light" else "#1E1E1E"
        )
        prod_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Header con selector de rango
        header_frame = ctk.CTkFrame(prod_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=8, pady=8)
        
        header_bg = ctk.CTkFrame(header_frame, fg_color=self.COLORS_CORP["primary"], corner_radius=12)
        header_bg.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            header_bg,
            text="🥛 Producción de Leche",
            font=("Segoe UI", 13, "bold"),
            text_color="white"
        ).pack(pady=8)

        # Gráfico
        self.fig_produccion, self.ax_produccion = plt.subplots(figsize=(6.5, 4))
        self._estilizar_matplotlib()
        
        self.canvas_produccion = FigureCanvasTkAgg(self.fig_produccion, prod_frame)
        self.canvas_produccion.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _crear_panel_eventos(self, parent):
        """Crea el panel de eventos recientes en el lado derecho"""
        eventos_frame = ctk.CTkFrame(
            parent,
            corner_radius=16,
            border_width=1,
            border_color="#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#424242",
            fg_color="#F5F5F5" if ctk.get_appearance_mode() == "Light" else "#1E1E1E"
        )
        eventos_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Header
        header = ctk.CTkFrame(eventos_frame, fg_color=self.COLORS_CORP["warning"], corner_radius=14)
        header.pack(fill="x", padx=8, pady=8)
        
        ctk.CTkLabel(
            header,
            text="📅 Eventos Recientes",
            font=("Segoe UI", 13, "bold"),
            text_color="white"
        ).pack(pady=8)

        # Tabla de eventos
        tree_frame = ctk.CTkFrame(eventos_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.eventos_tree = ttk.Treeview(
            tree_frame, 
            columns=("fecha", "tipo", "evento"),
            show="headings", 
            height=14
        )
        self.eventos_tree.heading("fecha", text="Fecha")
        self.eventos_tree.heading("tipo", text="Tipo")
        self.eventos_tree.heading("evento", text="Descripción")
        self.eventos_tree.column("fecha", width=70, anchor="center")
        self.eventos_tree.column("tipo", width=60, anchor="center")
        self.eventos_tree.column("evento", width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.eventos_tree.yview)
        self.eventos_tree.configure(yscrollcommand=scrollbar.set)

        self.eventos_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _crear_panel_alertas(self, parent):
        """Crea el panel de alertas del sistema en el lado derecho"""
        alertas_frame = ctk.CTkFrame(
            parent,
            corner_radius=16,
            border_width=1,
            border_color="#E0E0E0" if ctk.get_appearance_mode() == "Light" else "#424242",
            fg_color="#F5F5F5" if ctk.get_appearance_mode() == "Light" else "#1E1E1E"
        )
        alertas_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Header
        header = ctk.CTkFrame(alertas_frame, fg_color=self.COLORS_CORP["danger"], corner_radius=14)
        header.pack(fill="x", padx=8, pady=8)
        
        titulo_btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_btn_frame.pack(fill="x", pady=8, padx=8)
        
        ctk.CTkLabel(
            titulo_btn_frame,
            text="⚠️ Alertas del Sistema",
            font=("Segoe UI", 13, "bold"),
            text_color="white"
        ).pack(side="left")
        
        # Botón "Ver todas"
        ctk.CTkButton(
            titulo_btn_frame,
            text="Ver todas",
            width=70,
            height=22,
            font=("Segoe UI", 9),
            fg_color="#FF6B6B",
            hover_color="#FF8080",
            corner_radius=8,
            command=self._mostrar_todas_alertas
        ).pack(side="right")

        # Área de alertas
        self.alertas_text = ctk.CTkTextbox(alertas_frame, wrap="word")
        self.alertas_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.alertas_text.configure(state="disabled")

    def _estilizar_matplotlib(self):
        """Aplica estilos profesionales a las figuras matplotlib"""
        plt.style.use('default')
        
        # Modo oscuro si es necesario
        if ctk.get_appearance_mode() == "Dark":
            plt.rcParams['figure.facecolor'] = '#2b2b2b'
            plt.rcParams['axes.facecolor'] = '#3a3a3a'
            plt.rcParams['text.color'] = '#ffffff'
            plt.rcParams['axes.labelcolor'] = '#ffffff'
            plt.rcParams['xtick.color'] = '#ffffff'
            plt.rcParams['ytick.color'] = '#ffffff'
        else:
            plt.rcParams['figure.facecolor'] = '#ffffff'
            plt.rcParams['axes.facecolor'] = '#f5f5f5'
            plt.rcParams['text.color'] = '#333333'
            plt.rcParams['axes.labelcolor'] = '#333333'
            plt.rcParams['xtick.color'] = '#333333'
            plt.rcParams['ytick.color'] = '#333333'

    def _on_rango_produccion_change(self, value):
        """Callback cuando cambia el rango de producción"""
        dias_map = {
            "7 días": 7,
            "15 días": 15,
            "30 días": 30,
            "90 días": 90
        }
        self.rango_dias_produccion = dias_map.get(value, 30)
        self.actualizar_estadisticas()

    # Nota: sección duplicada de producción eliminada para usar un único gráfico ampliado arriba.

    # =========================================================
    #            MÉTODO PARA CREAR TARJETA DE MÉTRICA
    # =========================================================
    def crear_metric_card(self, parent, titulo, valor, color, columna):
        # Colores vibrantes y modernos
        modo = ctk.get_appearance_mode()
        if modo == "Dark":
            bg_color = color
            fg_text = "white"
            border_color = ("#90CAF9", "#64B5F6")
        else:
            bg_color = color
            fg_text = "white"
            border_color = ("white", "#E3F2FD")

        # Card con borde sutil para efecto de elevación
        card = ctk.CTkFrame(
            parent, 
            fg_color=bg_color, 
            corner_radius=15,
            border_width=2,
            border_color=border_color[0] if modo == "Light" else border_color[1]
        )
        card.grid(row=0, column=columna, sticky="ew", padx=6, pady=6)

        # Icono más grande y destacado
        icon = ""
        if "Total Animales" in titulo:
            icon = "🐄"
        elif "Activos" in titulo:
            icon = "✅"
        elif "Valor Inventario" in titulo:
            icon = "💰"
        elif "Tratamiento" in titulo:
            icon = "🏥"

        icon_label = ctk.CTkLabel(card, text=icon, font=("Segoe UI", 35))
        icon_label.pack(pady=(12, 5))

        # Título con tooltip
        title_label = ctk.CTkLabel(
            card, 
            text=titulo, 
            font=("Segoe UI", 11, "bold"), 
            text_color=fg_text
        )
        title_label.pack(pady=(0, 5))
        add_tooltip(title_label, f"{titulo}: métrica clave del sistema")

        # Valor destacado más grande
        valor_label = ctk.CTkLabel(
            card, 
            text=valor, 
            font=("Segoe UI", 26, "bold"), 
            text_color=fg_text
        )
        valor_label.pack(pady=(0, 15))

        return valor_label

    # _add_tooltip eliminado: ahora se usa add_tooltip centralizado desde modules.utils.ui

    # =========================================================
    #                 ACTUALIZACIÓN DE ESTADÍSTICAS - MEJORADA
    # =========================================================
    def actualizar_estadisticas(self):
        """Actualiza todas las métricas, gráficos, eventos y alertas"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # -------- MÉTRICAS PRINCIPALES (8 KPIs) --------
                # Total animales
                cursor.execute("SELECT COUNT(*) FROM animal")
                total_animales = cursor.fetchone()[0]

                # Animales activos
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo' OR estado IS NULL")
                activos = cursor.fetchone()[0]

                # Animales muertos
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Muerto'")
                muertos = cursor.fetchone()[0]

                # Animales vendidos
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Vendido'")
                vendidos = cursor.fetchone()[0]

                # En tratamiento (últimos 30 días)
                cursor.execute("""
                    SELECT COUNT(DISTINCT id_animal) FROM tratamiento 
                    WHERE fecha_inicio >= date('now', '-30 days') 
                    AND (estado = 'En curso' OR estado = 'Activo' OR estado IS NULL)
                """)
                result_tratamiento = cursor.fetchone()
                en_tratamiento = result_tratamiento[0] if result_tratamiento else 0

                # Gestantes
                cursor.execute("""
                    SELECT COUNT(DISTINCT animal_id) FROM reproduccion 
                    WHERE estado = 'Gestante'
                """)
                result_gestantes = cursor.fetchone()
                gestantes = result_gestantes[0] if result_gestantes else 0

                # Producción de leche HOY
                cursor.execute("""
                    SELECT COALESCE(SUM(COALESCE(litros_manana, 0) + COALESCE(litros_tarde, 0) + COALESCE(litros_noche, 0)), 0)
                    FROM produccion_leche
                    WHERE fecha = date('now')
                """)
                produccion_hoy = cursor.fetchone()[0]

                # Nacimientos del mes
                cursor.execute("""
                    SELECT COUNT(*) FROM animal 
                    WHERE fecha_nacimiento >= date('now', 'start of month')
                """)
                result_nacimientos = cursor.fetchone()
                nacimientos_mes = result_nacimientos[0] if result_nacimientos else 0

                # Actualizar las métricas KPI
                self.metricas["total_animales"].configure(text=str(total_animales))
                self.metricas["activos"].configure(text=str(activos))
                self.metricas["muertos"].configure(text=str(muertos))
                self.metricas["vendidos"].configure(text=str(vendidos))
                self.metricas["en_tratamiento"].configure(text=str(en_tratamiento))
                self.metricas["gestantes"].configure(text=str(gestantes))
                self.metricas["produccion_hoy"].configure(text=f"{produccion_hoy:.0f}L")
                self.metricas["nacimientos_mes"].configure(text=str(nacimientos_mes))

                # -------- GRÁFICOS --------
                self._actualizar_grafico_estados(cursor)
                self._actualizar_grafico_produccion(cursor)

                # -------- INFORMACIÓN --------
                self._actualizar_eventos_recientes(cursor)
                self._actualizar_alertas(cursor)

                self.logger.info(f"Dashboard actualizado: {total_animales} animales, {activos} activos")

        except Exception as e:
            self.logger.error(f"Error actualizando dashboard: {e}")

    # =========================================================
    #                     FUNCIONES DE GRÁFICOS - MEJORADAS
    # =========================================================
    def _actualizar_grafico_estados(self, cursor):
        """Actualiza el gráfico de estado de animales mostrando SOLO: Activos, Muertos, Vendidos, Perdidos"""
        try:
            # Consultar solo estados relevantes
            cursor.execute("""
                SELECT COALESCE(estado, 'Activo') as estado, COUNT(*) as cantidad
                FROM animal
                WHERE estado IN ('Activo', 'Muerto', 'Vendido', 'Perdido') OR estado IS NULL
                GROUP BY estado
                ORDER BY cantidad DESC
            """)

            datos = cursor.fetchall()
            
            self.ax_estados.clear()

            if datos:
                estados = [d[0] if d[0] else "Activo" for d in datos]
                cantidades = [d[1] for d in datos]

                # Colores corporativos
                colores_map = {
                    "Activo": self.COLORS_CORP["success"],
                    "Muerto": self.COLORS_CORP["danger"],
                    "Vendido": "#673AB7",
                    "Perdido": "#FFA726"
                }
                colores = [colores_map.get(e, "#90CAF9") for e in estados]

                # Gráfico de barras profesional
                bars = self.ax_estados.barh(estados, cantidades, color=colores)
                
                # Configuración
                self.ax_estados.set_xlabel("Cantidad de Animales", fontsize=10, fontweight='bold')
                self.ax_estados.tick_params(axis='y', labelsize=10)
                self.ax_estados.tick_params(axis='x', labelsize=9)
                self.ax_estados.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.7)
                
                # Valores en las barras
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    self.ax_estados.text(
                        width,
                        bar.get_y() + bar.get_height() / 2,
                        f" {int(width)}",
                        ha="left", va="center", fontsize=10, fontweight='bold'
                    )
            else:
                self.ax_estados.text(0.5, 0.5, "No hay animales registrados", 
                                    ha="center", va="center", transform=self.ax_estados.transAxes,
                                    fontsize=11, style='italic', color='gray')

            self.fig_estados.tight_layout()
            self.canvas_estados.draw()

        except Exception as e:
            self.logger.error(f"Error en gráfico estados: {e}")

    def _actualizar_grafico_produccion(self, cursor):
        """Actualiza el gráfico de producción de leche con línea curva, promedio, máx y mín"""
        try:
            self.ax_produccion.clear()

            # Consultar producción según rango seleccionado
            cursor.execute(f"""
                SELECT fecha, 
                       SUM(COALESCE(litros_manana, 0) + COALESCE(litros_tarde, 0) + COALESCE(litros_noche, 0)) as total
                FROM produccion_leche
                WHERE fecha >= date('now', '-{self.rango_dias_produccion} days')
                GROUP BY fecha
                ORDER BY fecha
            """)
            datos = cursor.fetchall()

            if datos:
                fechas = [row[0] for row in datos]
                totales = [row[1] for row in datos]

                x = range(len(fechas))

                # Gráfico de línea suave con relleno
                self.ax_produccion.fill_between(x, totales, alpha=0.25, color=self.COLORS_CORP["primary"])
                self.ax_produccion.plot(x, totales, marker='o', markersize=4, 
                                       linewidth=2.5, color=self.COLORS_CORP["primary"], 
                                       label='Producción Diaria', zorder=3)
                
                # Línea de promedio
                promedio = sum(totales) / len(totales) if totales else 0
                self.ax_produccion.axhline(y=promedio, color=self.COLORS_CORP["warning"], 
                                          linestyle='--', linewidth=2, 
                                          label=f'Promedio: {promedio:.1f}L', alpha=0.8)
                
                # Línea de máximo
                maximo = max(totales) if totales else 0
                self.ax_produccion.axhline(y=maximo, color=self.COLORS_CORP["success"], 
                                          linestyle=':', linewidth=1.5, 
                                          label=f'Máximo: {maximo:.1f}L', alpha=0.6)
                
                # Línea de mínimo
                minimo = min(totales) if totales else 0
                self.ax_produccion.axhline(y=minimo, color=self.COLORS_CORP["danger"], 
                                          linestyle=':', linewidth=1.5, 
                                          label=f'Mínimo: {minimo:.1f}L', alpha=0.6)
                
                # Configuración del eje X
                step = max(1, len(fechas) // 6)  # Mostrar máximo 6 etiquetas
                self.ax_produccion.set_xticks(range(0, len(fechas), step))
                self.ax_produccion.set_xticklabels([fechas[i] for i in range(0, len(fechas), step)], 
                                                   rotation=45, ha='right', fontsize=9)
                
                # Configuración general
                self.ax_produccion.set_ylabel("Litros", fontsize=10, fontweight='bold')
                self.ax_produccion.set_xlabel("Fecha", fontsize=10, fontweight='bold')
                self.ax_produccion.tick_params(axis='both', labelsize=9)
                self.ax_produccion.legend(loc='upper left', fontsize=9, framealpha=0.95)
                self.ax_produccion.grid(True, alpha=0.3, linestyle=':', linewidth=0.7)
                
                # Estadísticas en el gráfico
                total_periodo = sum(totales)
                promedio_dias = self.rango_dias_produccion
                stats_text = f"Total: {total_periodo:.0f}L | Días: {len(fechas)} | Promedio: {promedio:.1f}L"
                self.ax_produccion.text(0.98, 0.05, stats_text, transform=self.ax_produccion.transAxes,
                                       fontsize=8, ha='right', va='bottom',
                                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'))
            else:
                self.ax_produccion.text(0.5, 0.5, "No hay datos de producción", 
                                       ha="center", va="center", transform=self.ax_produccion.transAxes,
                                       fontsize=11, style='italic', color='gray')

            self.fig_produccion.tight_layout()
            self.canvas_produccion.draw()

        except Exception as e:
            self.logger.error(f"Error en gráfico producción: {e}")

    # =========================================================
    #                     EVENTOS Y ALERTAS - MEJORADOS
    # =========================================================
    def _actualizar_eventos_recientes(self, cursor):
        """Actualiza el panel de eventos recientes (últimos 10 eventos reales)"""
        try:
            # Limpiar eventos existentes
            for item in self.eventos_tree.get_children():
                self.eventos_tree.delete(item)

            eventos_lista = []

            # Nuevos animales registrados
            cursor.execute("""
                SELECT date(fecha_creacion), 'Animal', 'Nuevo animal: ' || codigo || ' - ' || COALESCE(nombre, 'Sin nombre')
                FROM animal
                WHERE fecha_creacion IS NOT NULL
                ORDER BY fecha_creacion DESC
                LIMIT 3
            """)
            eventos_lista.extend(cursor.fetchall())

            # Tratamientos aplicados
            cursor.execute("""
                SELECT date(t.fecha_inicio), 'Tratamiento', 'Tratamiento: ' || t.producto || ' - ' || a.codigo
                FROM tratamiento t
                JOIN animal a ON t.id_animal = a.id
                WHERE t.fecha_inicio IS NOT NULL
                ORDER BY t.fecha_inicio DESC
                LIMIT 2
            """)
            eventos_lista.extend(cursor.fetchall())

            # Producción registrada (últimos 2 registros)
            cursor.execute("""
                SELECT date(fecha), 'Producción', 'Producción: ' || animal_id || ' L'
                FROM produccion_leche
                WHERE fecha IS NOT NULL
                ORDER BY fecha DESC
                LIMIT 2
            """)
            eventos_lista.extend(cursor.fetchall())

            # Ventas registradas
            cursor.execute("""
                SELECT date(v.fecha), 'Venta', 'Venta: ' || a.codigo || ' - $' || CAST(v.precio_total AS INT)
                FROM venta v
                JOIN animal a ON v.animal_id = a.id
                WHERE v.fecha IS NOT NULL
                ORDER BY v.fecha DESC
                LIMIT 2
            """)
            eventos_lista.extend(cursor.fetchall())

            # Nacimientos
            cursor.execute("""
                SELECT date(fecha_nacimiento), 'Nacimiento', 'Nacimiento: ' || codigo
                FROM animal
                WHERE fecha_nacimiento >= date('now', 'start of month')
                ORDER BY fecha_nacimiento DESC
                LIMIT 2
            """)
            eventos_lista.extend(cursor.fetchall())

            # Ordenar por fecha descendente y tomar máximo 10
            eventos_lista.sort(key=lambda x: x[0] if x[0] else "1900-01-01", reverse=True)
            eventos_lista = eventos_lista[:10]

            # Insertar en tabla
            for fecha, tipo, desc in eventos_lista:
                fecha_str = fecha if fecha else "--"
                self.eventos_tree.insert("", "end", values=(fecha_str, tipo, desc))

            # Si no hay eventos
            if not eventos_lista:
                self.eventos_tree.insert("", "end", values=("--", "--", "No hay eventos recientes"))

            self.logger.info(f"Cargados {len(eventos_lista)} eventos recientes")

        except Exception as e:
            self.logger.error(f"Error cargando eventos: {e}")
            for item in self.eventos_tree.get_children():
                self.eventos_tree.delete(item)
            self.eventos_tree.insert("", "end", values=("Error", "Error", "No se pudieron cargar eventos"))

    def _actualizar_alertas(self, cursor):
        """Actualiza alertas reales generadas automáticamente desde la base de datos"""
        try:
            self.alertas_text.configure(state="normal")
            self.alertas_text.delete("1.0", "end")

            alertas = []

            # 1. Animales sin raza
            cursor.execute("""
                SELECT COUNT(*), GROUP_CONCAT(codigo, ', ')
                FROM animal 
                WHERE raza_id IS NULL AND (estado = 'Activo' OR estado IS NULL)
            """)
            result = cursor.fetchone()
            sin_raza_count = result[0] if result else 0
            if sin_raza_count > 0:
                alertas.append(("alta", "🔴 CRIANZA", f"{sin_raza_count} animal(es) sin raza asignada"))

            # 2. Animales sin lote asignado
            cursor.execute("""
                SELECT COUNT(*), GROUP_CONCAT(codigo, ', ')
                FROM animal 
                WHERE lote_id IS NULL AND (estado = 'Activo' OR estado IS NULL)
            """)
            result = cursor.fetchone()
            sin_lote_count = result[0] if result else 0
            if sin_lote_count > 0:
                alertas.append(("media", "🟡 ORGANIZACIÓN", f"{sin_lote_count} animal(es) sin lote asignado"))

            # 3. Animales sin última vacunación registrada
            cursor.execute("""
                SELECT COUNT(*)
                FROM animal a
                WHERE (estado = 'Activo' OR estado IS NULL)
                AND NOT EXISTS (
                    SELECT 1 FROM tratamiento 
                    WHERE id_animal = a.id AND tipo_tratamiento = 'Vacunación'
                )
            """)
            sin_vacuna = cursor.fetchone()[0]
            if sin_vacuna > 0:
                alertas.append(("alta", "⚕️ SALUD", f"{sin_vacuna} animal(es) sin vacunación registrada"))

            # 4. Gestantes actuales
            cursor.execute("""
                SELECT COUNT(DISTINCT animal_id)
                FROM reproduccion
                WHERE estado = 'Gestante'
            """)
            result = cursor.fetchone()
            gestantes_count = result[0] if result else 0
            if gestantes_count > 0:
                alertas.append(("media", "🤰 REPRODUCCIÓN", f"{gestantes_count} animal(es) gestante(s) registrado(s)"))

            # 5. Tratamientos por vencer (últimos 3 días)
            cursor.execute("""
                SELECT COUNT(*)
                FROM tratamiento
                WHERE fecha_fin BETWEEN date('now') AND date('now', '+3 days')
                AND (estado = 'En curso' OR estado = 'Activo' OR estado IS NULL)
            """)
            tratamientos_vencer = cursor.fetchone()[0]
            if tratamientos_vencer > 0:
                alertas.append(("alta", "💊 MEDICINAS", f"{tratamientos_vencer} tratamiento(s) por vencer en 3 días"))

            # 6. Animales con problemas de salud
            cursor.execute("""
                SELECT COUNT(*)
                FROM animal
                WHERE (estado = 'Activo' OR estado IS NULL)
                AND (salud = 'Enfermo' OR salud = 'En cuarentena')
            """)
            enfermos = cursor.fetchone()[0]
            if enfermos > 0:
                alertas.append(("alta", "🏥 SALUD CRÍTICA", f"{enfermos} animal(es) con problemas de salud"))

            # Mostrar alertas ordenadas por prioridad
            if alertas:
                # Separar por prioridad
                alertas_alta = [a for a in alertas if a[0] == "alta"]
                alertas_media = [a for a in alertas if a[0] == "media"]

                # Mostrar alertas de alta prioridad
                if alertas_alta:
                    self.alertas_text.insert("end", "⚠️ ALERTAS URGENTES\n", "titulo_alta")
                    self.alertas_text.insert("end", "─" * 40 + "\n", "separador")
                    for _, titulo, desc in alertas_alta:
                        self.alertas_text.insert("end", f"{titulo}\n", "titulo_alerta")
                        self.alertas_text.insert("end", f"{desc}\n\n", "alerta_alta")

                # Mostrar alertas de prioridad media
                if alertas_media:
                    self.alertas_text.insert("end", "📌 RECORDATORIOS\n", "titulo_media")
                    self.alertas_text.insert("end", "─" * 40 + "\n", "separador")
                    for _, titulo, desc in alertas_media:
                        self.alertas_text.insert("end", f"{titulo}\n", "titulo_alerta")
                        self.alertas_text.insert("end", f"{desc}\n\n", "alerta_media")
            else:
                self.alertas_text.insert("end", "✅ TODO EN ORDEN\n\n", "exito")
                self.alertas_text.insert("end", "No hay alertas activas en el sistema.", "info")

            # Configurar tags de colores (sin font en CTkTextbox)
            self.alertas_text.tag_config("titulo_alta", foreground="#E53935")
            self.alertas_text.tag_config("alerta_alta", foreground="#D32F2F")
            self.alertas_text.tag_config("titulo_media", foreground="#FB8C00")
            self.alertas_text.tag_config("alerta_media", foreground="#F57C00")
            self.alertas_text.tag_config("titulo_alerta", foreground="#333333")
            self.alertas_text.tag_config("exito", foreground="#43A047")
            self.alertas_text.tag_config("info", foreground="#757575")
            self.alertas_text.tag_config("separador", foreground="#BDBDBD")

            self.alertas_text.configure(state="disabled")
            self.logger.info(f"Generadas {len(alertas)} alertas en dashboard")

        except Exception as e:
            self.logger.error(f"Error actualizando alertas: {e}")
            self.alertas_text.configure(state="normal")
            self.alertas_text.delete("1.0", "end")
            self.alertas_text.insert("end", "❌ Error cargando alertas\n")
            self.alertas_text.insert("end", f"Detalle: {str(e)}")
            self.alertas_text.configure(state="disabled")

    def _mostrar_todas_alertas(self):
        """Abre una ventana con todas las alertas del sistema (implementación futura)"""
        self.logger.info("Solicitada vista completa de alertas")
        # Placeholder para implementación futura

    # =========================================================
    #                   MÉTODOS ADICIONALES
    # =========================================================
    def actualizar_datos_tiempo_real(self):
        """Método para actualizaciones en tiempo real (puede ser llamado externamente)"""
        self.actualizar_estadisticas()

    def exportar_reporte(self):
        """Exporta un reporte del dashboard (para implementación futura)"""
        # Placeholder para funcionalidad de exportación
        self.logger.info("Solicitada exportación de reporte")
        # Implementar lógica de exportación aquí

    def limpiar_recursos(self):
        """Limpia recursos de matplotlib al cerrar"""
        try:
            plt.close(self.fig_estados)
            plt.close(self.fig_produccion)
            self.logger.info("Recursos de matplotlib liberados")
        except Exception as e:
            self.logger.error(f"Error liberando recursos: {e}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Dashboard Profesional Test")
    app.geometry("1400x900")
    
    dashboard = DashboardModule(app)
    dashboard.pack(fill="both", expand=True)
    
    app.mainloop()