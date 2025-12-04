import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importaciones corregidas
try:
    from database.database import get_db_connection
    from modules.utils.logger import get_logger
    from modules.utils.ui import add_tooltip
    from modules.utils.notificaciones import SistemaNotificaciones
except ImportError as e:
    import logging
    logging.error(f"Error importando dependencias en dashboard: {e}")

class DashboardModule(ctk.CTkFrame):
    """Dashboard principal del sistema con métricas, gráficos y alertas."""

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Configurar logger
        self.logger = get_logger("Dashboard")
        self.logger.info("Módulo Dashboard iniciado")
        
        # Inicializar sistema de notificaciones
        self.sistema_notificaciones = SistemaNotificaciones()
        
        # Inicializar interfaz y datos
        self.crear_widgets()
        self.actualizar_estadisticas()

    # =========================================================
    #                      CREACIÓN DE UI
    # =========================================================
    def crear_widgets(self):
        """Construcción completa de la interfaz del Dashboard"""
        # Contenedor principal ahora scrollable para permitir gráficos más grandes
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=2, pady=6)

        # ---------- TÍTULO ----------
        titulo_frame = ctk.CTkFrame(container, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(0, 20))

        # Título con gradiente visual
        titulo_container = ctk.CTkFrame(
            titulo_frame,
            fg_color=("#1976D2", "#1565C0"),
            corner_radius=15,
            height=70
        )
        titulo_container.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            titulo_container,
            text="📊 Dashboard",
            font=("Segoe UI", 28, "bold"),
            text_color="white"
        ).pack(side="left", padx=10, pady=5)  # Reducir padding horizontal (20→10)
        
        ctk.CTkLabel(
            titulo_container,
            text="Resumen en Tiempo Real",
            font=("Segoe UI", 12),
            text_color=("#E3F2FD", "#90CAF9")
        ).pack(side="left", padx=(0, 20))

        # Frame de controles (filtros y actualizar)
        controles_frame = ctk.CTkFrame(titulo_frame, fg_color="transparent")
        controles_frame.pack(side="right")
        
        # Filtro de fechas
        filter_frame = ctk.CTkFrame(controles_frame, fg_color=("#E3F2FD", "#1E1E1E"), corner_radius=10)
        filter_frame.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(filter_frame, text="Filtrar por:", font=("Segoe UI", 11)).pack(side="left", padx=(10, 5), pady=10)
        
        self.filtro_periodo = ctk.CTkComboBox(
            filter_frame,
            values=["Hoy", "Últimos 7 días", "Últimos 30 días", "Este mes", "Todo"],
            width=140,
            command=self.aplicar_filtro_periodo
        )
        self.filtro_periodo.set("Últimos 30 días")
        self.filtro_periodo.pack(side="left", padx=5, pady=10)
        
        # Botón de actualizar estilizado
        ctk.CTkButton(
            controles_frame,
            text="🔄 Actualizar",
            command=self.actualizar_estadisticas,
            width=120,
            height=70,
            font=("Segoe UI", 13, "bold"),
            fg_color=("#2E7D32", "#388E3C"),
            hover_color=("#388E3C", "#4CAF50"),
            corner_radius=15
        ).pack(side="left")

        # ---------- MÉTRICAS ----------
        metrics_frame = ctk.CTkFrame(container, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))

        # Configurar grid para 4 columnas
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)

        self.metricas = {
            "total_animales": self.crear_metric_card(metrics_frame, "🐄 Total Animales", "0", "#2E7D32", 0),
            "animales_activos": self.crear_metric_card(metrics_frame, "✅ Activos", "0", "#1976D2", 1),
            "valor_inventario": self.crear_metric_card(metrics_frame, "💰 Valor Inventario", "$0", "#F57C00", 2),
            "en_tratamiento": self.crear_metric_card(metrics_frame, "🏥 En Tratamiento", "0", "#C62828", 3),
        }

        # ---------- PANEL PRINCIPAL ----------
        data_frame = ctk.CTkFrame(container, fg_color="transparent")
        data_frame.pack(fill="both", expand=True)

        # Configurar grid: 2 columnas, 2 filas
        data_frame.columnconfigure(0, weight=2)
        data_frame.columnconfigure(1, weight=1)
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)

        # ---------- GRÁFICO ESTADOS (Izquierda arriba) ----------
        estados_frame = ctk.CTkFrame(
            data_frame,
            corner_radius=12,
            border_width=2,
            border_color=("#E0E0E0", "#424242")
        )
        estados_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))

        # Header del gráfico
        estado_header = ctk.CTkFrame(estados_frame, fg_color=("#2E7D32", "#388E3C"), corner_radius=10)
        estado_header.pack(fill="x", pady=(5, 10), padx=5)
        
        estado_label = ctk.CTkLabel(
            estado_header,
            text="📊 Estado de Animales",
            font=("Segoe UI", 15, "bold"),
            text_color="white"
        )
        estado_label.pack(pady=8)
        add_tooltip(estado_label, "Distribución de animales por estado")
        # Gráfico de estados más grande
        self.fig2, self.ax2 = plt.subplots(figsize=(8, 4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, estados_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # ---------- PRODUCCIÓN DE LECHE (Izquierda abajo) ----------
        produccion_frame = ctk.CTkFrame(
            data_frame,
            corner_radius=12,
            border_width=2,
            border_color=("#E0E0E0", "#424242")
        )
        produccion_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5, 0))

        # Header del gráfico de producción
        prod_header = ctk.CTkFrame(produccion_frame, fg_color=("#1976D2", "#2196F3"), corner_radius=10)
        prod_header.pack(fill="x", pady=(5, 10), padx=5)
        
        prod_label = ctk.CTkLabel(
            prod_header,
            text="🥛 Producción de Leche - 30 días",
            font=("Segoe UI", 15, "bold"),
            text_color="white"
        )
        prod_label.pack(pady=8)
        add_tooltip(prod_label, "Tendencia de producción diaria")
        # Gráfico de producción más grande
        self.fig3, self.ax3 = plt.subplots(figsize=(8, 4))
        self.canvas3 = FigureCanvasTkAgg(self.fig3, produccion_frame)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # ---------- PANEL DERECHO (Eventos y Alertas) ----------
        info_frame = ctk.CTkFrame(
            data_frame,
            corner_radius=12,
            border_width=2,
            border_color=("#E0E0E0", "#424242")
        )
        info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(5, 0))

        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)

        # Eventos modernos con tooltip
        eventos_frame = ctk.CTkFrame(
            info_frame, 
            fg_color="transparent",
            corner_radius=10
        )
        eventos_frame.grid(row=0, column=0, sticky="nsew", pady=(5, 10), padx=5)
        eventos_frame.columnconfigure(0, weight=1)

        # Header de eventos
        eventos_header = ctk.CTkFrame(eventos_frame, fg_color=("#F57C00", "#FF9800"), corner_radius=10)
        eventos_header.pack(fill="x", pady=(0, 10))
        
        eventos_label = ctk.CTkLabel(
            eventos_header,
            text="📅 Eventos Recientes",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        eventos_label.pack(pady=8)
        add_tooltip(eventos_label, "Últimos eventos registrados en la finca")

        eventos_tree_frame = ctk.CTkFrame(eventos_frame, fg_color="transparent")
        eventos_tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.eventos_tree = ttk.Treeview(eventos_tree_frame, columns=("fecha", "evento"),
                         show="headings", height=12)
        self.eventos_tree.heading("fecha", text="Fecha")
        self.eventos_tree.heading("evento", text="Evento")
        self.eventos_tree.column("fecha", width=90)
        self.eventos_tree.column("evento", width=220)

        eventos_scrollbar = ttk.Scrollbar(eventos_tree_frame, orient="vertical", command=self.eventos_tree.yview)
        self.eventos_tree.configure(yscrollcommand=eventos_scrollbar.set)

        self.eventos_tree.pack(side="left", fill="both", expand=True)
        eventos_scrollbar.pack(side="right", fill="y")

        # Panel de alertas moderno con tooltip
        alertas_frame = ctk.CTkFrame(
            info_frame,
            fg_color="transparent",
            corner_radius=10
        )
        alertas_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Header de alertas
        alertas_header = ctk.CTkFrame(alertas_frame, fg_color=("#C62828", "#EF5350"), corner_radius=10)
        alertas_header.pack(fill="x", pady=(0, 10))
        
        alertas_label = ctk.CTkLabel(
            alertas_header,
            text="⚠️ Alertas del Sistema",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        )
        alertas_label.pack(pady=8)
        add_tooltip(alertas_label, "Alertas y recomendaciones del sistema")

        self.alertas_text = ctk.CTkTextbox(alertas_frame, wrap="word")
        self.alertas_text.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.alertas_text.configure(state="disabled")

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
    #                 ACTUALIZACIÓN DE ESTADÍSTICAS
    # =========================================================
    def actualizar_estadisticas(self):
        """Actualiza métricas, gráficos, eventos y alertas"""

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # -------- MÉTRICAS PRINCIPALES --------
                cursor.execute("SELECT COUNT(*) FROM animal")
                total_animales = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo' OR estado IS NULL")
                animales_activos = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(precio_compra), 0) FROM animal WHERE estado = 'Activo' OR estado IS NULL")
                valor_inventario = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM tratamiento WHERE fecha_inicio >= date('now', '-30 days') AND estado = 'Activo'")
                en_tratamiento = cursor.fetchone()[0]

                # Mostrar métricas
                self.metricas["total_animales"].configure(text=str(total_animales))
                self.metricas["animales_activos"].configure(text=str(animales_activos))
                self.metricas["valor_inventario"].configure(text=f"${valor_inventario:,.0f}")
                self.metricas["en_tratamiento"].configure(text=str(en_tratamiento))

                # -------- GRÁFICOS --------
                self.actualizar_grafico_estados(cursor)
                self.actualizar_grafico_produccion(cursor)

                # -------- INFORMACIÓN --------
                self.actualizar_eventos_recientes(cursor)
                self.actualizar_alertas(cursor)

                self.logger.info(f"Dashboard actualizado: {total_animales} animales, ${valor_inventario:,.0f} inventario")

        except Exception as e:
            self.logger.error(f"Error actualizando dashboard: {e}")
    
    def aplicar_filtro_periodo(self, periodo: str):
        """
        Aplica filtro de periodo para actualizar las estadísticas del dashboard
        
        Args:
            periodo: Periodo seleccionado (Hoy, Últimos 7 días, etc.)
        """
        from datetime import datetime, timedelta
        
        # Calcular rango de fechas según el periodo
        fecha_fin = datetime.now()
        
        if periodo == "Hoy":
            fecha_inicio = fecha_fin.replace(hour=0, minute=0, second=0, microsecond=0)
        elif periodo == "Últimos 7 días":
            fecha_inicio = fecha_fin - timedelta(days=7)
        elif periodo == "Últimos 30 días":
            fecha_inicio = fecha_fin - timedelta(days=30)
        elif periodo == "Este mes":
            fecha_inicio = fecha_fin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # Todo
            fecha_inicio = None
        
        # Guardar filtro para usar en consultas
        self.fecha_filtro_inicio = fecha_inicio
        self.fecha_filtro_fin = fecha_fin
        
        # Actualizar estadísticas con el nuevo filtro
        self.actualizar_estadisticas()
        self.logger.info(f"Filtro aplicado: {periodo}")

    # =========================================================
    #                     FUNCIONES DE GRÁFICOS
    # =========================================================
    def actualizar_grafico_estados(self, cursor):
        try:
            cursor.execute("""
                SELECT COALESCE(estado, 'Activo'), COUNT(*)
                FROM animal
                GROUP BY estado
                ORDER BY COUNT(*) DESC
            """)

            datos = cursor.fetchall()
            estados = [d[0] for d in datos]
            cantidades = [d[1] for d in datos]

            self.ax2.clear()

            if datos:
                # Colores adaptativos
                modo = ctk.get_appearance_mode()
                if modo == "Dark":
                    colors = ['#90caf9', '#a5d6a7', '#ffcc80', '#ef9a9a', '#ce93d8']
                else:
                    colors = ['#2E7D32', '#1976D2', '#F57C00', '#C62828', '#7B1FA2']
                bars = self.ax2.bar(estados, cantidades, color=colors[:len(estados)])
                self.ax2.set_ylabel("Cantidad de Animales", fontsize=10)
                self.ax2.set_xlabel("Estado", fontsize=10)
                self.ax2.tick_params(axis='x', rotation=45, labelsize=9)
                self.ax2.tick_params(axis='y', labelsize=9)
                self.ax2.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
                for bar in bars:
                    height = bar.get_height()
                    self.ax2.text(
                        bar.get_x() + bar.get_width() / 2,
                        height,
                        f"{int(height)}",
                        ha="center", va="bottom", fontsize=10, fontweight='bold'
                    )
            else:
                self.ax2.text(0.5, 0.5, "No hay animales registrados\n\n🐄 Comience agregando animales desde el módulo 'Animales'", 
                             ha="center", va="center", transform=self.ax2.transAxes,
                             fontsize=11, style='italic', color='gray')

            self.fig2.tight_layout()
            self.canvas2.draw()

        except Exception as e:
            self.logger.error(f"Error gráfico estados: {e}")

    def actualizar_grafico_produccion(self, cursor):
        """Actualiza el gráfico de producción de leche de los últimos 30 días"""
        try:
            self.ax3.clear()

            # Consultar producción diaria de los últimos 30 días
            cursor.execute("""
                SELECT fecha, 
                       SUM(COALESCE(litros_manana, 0) + COALESCE(litros_tarde, 0) + COALESCE(litros_noche, 0)) as total
                FROM produccion_leche
                WHERE fecha >= date('now', '-30 days')
                GROUP BY fecha
                ORDER BY fecha
            """)
            datos = cursor.fetchall()

            if datos:
                fechas = [row[0] for row in datos]
                totales = [row[1] for row in datos]

                # Crear gráfico de línea con área
                self.ax3.fill_between(range(len(fechas)), totales, alpha=0.3, color='#2196F3')
                self.ax3.plot(range(len(fechas)), totales, marker='o', markersize=3, 
                             linewidth=1.5, color='#1565C0', label='Producción')
                
                # Añadir línea de promedio
                promedio = sum(totales) / len(totales)
                self.ax3.axhline(y=promedio, color='red', linestyle='--', linewidth=1, 
                                label=f'Prom: {promedio:.1f}L')
                
                # Configurar eje X con fechas
                step = max(1, len(fechas) // 7)  # Mostrar máximo 7 etiquetas
                self.ax3.set_xticks(range(0, len(fechas), step))
                self.ax3.set_xticklabels([fechas[i] for i in range(0, len(fechas), step)], 
                                        rotation=45, ha='right', fontsize=8)
                
                self.ax3.set_xlabel("Fecha", fontsize=9)
                self.ax3.set_ylabel("Litros", fontsize=9)
                self.ax3.tick_params(axis='both', labelsize=8)
                self.ax3.legend(loc='upper left', fontsize=8)
                self.ax3.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
                
                # Calcular estadísticas adicionales
                total_mes = sum(totales)
                max_prod = max(totales)
                min_prod = min(totales)
                
                # Agregar texto con estadísticas
                stats_text = f"Total: {total_mes:.0f}L | Máx: {max_prod:.0f}L | Mín: {min_prod:.0f}L"
                self.ax3.text(0.98, 0.95, stats_text, transform=self.ax3.transAxes,
                            fontsize=8, verticalalignment='top', horizontalalignment='right',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            else:
                self.ax3.text(0.5, 0.5, "No hay datos de producción\n\n💡 Registre producción desde el módulo 'Animales'", 
                             ha="center", va="center", transform=self.ax3.transAxes,
                             fontsize=10, style='italic', color='gray')

            self.fig3.tight_layout()
            self.canvas3.draw()

        except Exception as e:
            self.logger.error(f"Error gráfico producción: {e}")
            self.ax2.clear()
            self.ax2.text(0.5, 0.5, "Error cargando datos", 
                         ha="center", va="center", transform=self.ax2.transAxes)
            self.canvas2.draw()

    # =========================================================
    #                     EVENTOS Y ALERTAS
    # =========================================================
    def actualizar_eventos_recientes(self, cursor):
        try:
            # Limpiar eventos existentes
            for item in self.eventos_tree.get_children():
                self.eventos_tree.delete(item)

            # Eventos de nuevos animales
            cursor.execute("""
                SELECT date(fecha_creacion), 'Nuevo Animal: ' || codigo
                FROM animal
                ORDER BY fecha_creacion DESC
                LIMIT 5
            """)

            eventos_animales = cursor.fetchall()

            # Eventos de tratamientos recientes
            cursor.execute("""
                SELECT date(t.fecha_inicio), 'Tratamiento: ' || t.producto || ' - ' || a.codigo
                FROM tratamiento t
                JOIN animal a ON t.id_animal = a.id
                ORDER BY t.fecha_inicio DESC
                LIMIT 3
            """)

            eventos_tratamientos = cursor.fetchall()

            # Combinar eventos
            # Normalizar fechas para evitar comparaciones con None
            todos_eventos = [(fech or "", ev) for (fech, ev) in (eventos_animales + eventos_tratamientos)]
            # Ordenar por fecha como cadena ISO (YYYY-MM-DD) descendente
            todos_eventos.sort(key=lambda x: str(x[0]), reverse=True)
            
            # Mostrar máximo 5 eventos
            for fecha, evento in todos_eventos[:5]:
                self.eventos_tree.insert("", "end", values=(fecha, evento))

            # Si no hay eventos
            if not todos_eventos:
                self.eventos_tree.insert("", "end", values=("--", "No hay eventos recientes"))

            self.logger.info(f"Cargados {len(todos_eventos[:5])} eventos recientes")

        except Exception as e:
            self.logger.error(f"Error eventos recientes: {e}")
            for item in self.eventos_tree.get_children():
                self.eventos_tree.delete(item)
            self.eventos_tree.insert("", "end", values=("Error", "No se pudieron cargar eventos"))

    def actualizar_alertas(self, cursor):
        """Actualiza alertas usando el sistema de notificaciones"""
        try:
            self.alertas_text.configure(state="normal")
            self.alertas_text.delete("1.0", "end")

            # Obtener notificaciones del sistema
            notificaciones = self.sistema_notificaciones.obtener_todas_notificaciones()
            
            if notificaciones:
                # Agrupar por prioridad
                notif_alta = [n for n in notificaciones if n['prioridad'] == 'alta']
                notif_media = [n for n in notificaciones if n['prioridad'] == 'media']
                notif_baja = [n for n in notificaciones if n['prioridad'] == 'baja']
                
                # Mostrar resumen
                resumen = self.sistema_notificaciones.obtener_resumen()
                self.alertas_text.insert("end", f"{resumen}\n", "resumen")
                self.alertas_text.insert("end", "─" * 50 + "\n\n", "separador")
                
                # Notificaciones de alta prioridad
                if notif_alta:
                    self.alertas_text.insert("end", "🔴 URGENTE\n", "titulo_alta")
                    for notif in notif_alta[:5]:  # Máximo 5
                        self.alertas_text.insert("end", f"{notif['icono']} {notif['titulo']}\n", "alta")
                        self.alertas_text.insert("end", f"   {notif['mensaje']}\n\n", "detalle_alta")
                
                # Notificaciones de prioridad media
                if notif_media:
                    self.alertas_text.insert("end", "🟡 IMPORTANTE\n", "titulo_media")
                    for notif in notif_media[:3]:  # Máximo 3
                        self.alertas_text.insert("end", f"{notif['icono']} {notif['titulo']}\n", "media")
                        self.alertas_text.insert("end", f"   {notif['mensaje']}\n\n", "detalle_media")
                
                # Notificaciones de baja prioridad
                if notif_baja and len(notif_alta) < 3 and len(notif_media) < 2:
                    self.alertas_text.insert("end", "🟢 INFORMACIÓN\n", "titulo_baja")
                    for notif in notif_baja[:2]:  # Máximo 2
                        self.alertas_text.insert("end", f"{notif['icono']} {notif['titulo']}\n", "baja")
                        self.alertas_text.insert("end", f"   {notif['mensaje']}\n\n", "detalle_baja")
                
                # Mensaje final
                if len(notificaciones) > 10:
                    self.alertas_text.insert("end", f"\n... y {len(notificaciones) - 10} notificaciones más\n", "info")
                
            else:
                # Sin notificaciones
                self.alertas_text.insert("end", "✅ Todo en orden\n\n", "exito")
                self.alertas_text.insert("end", "No hay notificaciones pendientes en el sistema", "info")
                
                # Alertas adicionales (mantener funcionalidad original)
                alertas_adicionales = []
                
                # Animales sin raza
                cursor.execute("SELECT COUNT(*) FROM animal WHERE raza_id IS NULL AND (estado = 'Activo' OR estado IS NULL)")
                sin_raza = cursor.fetchone()[0]
                if sin_raza > 0:
                    alertas_adicionales.append(f"⚠️ {sin_raza} animal(es) sin raza asignada")
                
                # Animales sin lote
                cursor.execute("SELECT COUNT(*) FROM animal WHERE lote_id IS NULL AND (estado = 'Activo' OR estado IS NULL)")
                sin_lote = cursor.fetchone()[0]
                if sin_lote > 0:
                    alertas_adicionales.append(f"� {sin_lote} animal(es) sin lote asignado")
                
                if alertas_adicionales:
                    self.alertas_text.insert("end", "\n\n📋 Recordatorios:\n", "titulo_info")
                    for alerta in alertas_adicionales:
                        self.alertas_text.insert("end", f"  • {alerta}\n", "info")
            
            # Configurar tags de colores (sin font para CTkTextbox)
            self.alertas_text.tag_config("titulo_alta", foreground="#EF5350")
            self.alertas_text.tag_config("alta", foreground="#EF5350")
            self.alertas_text.tag_config("detalle_alta", foreground="#D32F2F")
            self.alertas_text.tag_config("titulo_media", foreground="#FFA726")
            self.alertas_text.tag_config("media", foreground="#FFA726")
            self.alertas_text.tag_config("detalle_media", foreground="#F57C00")
            self.alertas_text.tag_config("titulo_baja", foreground="#66BB6A")
            self.alertas_text.tag_config("baja", foreground="#66BB6A")
            self.alertas_text.tag_config("detalle_baja", foreground="#388E3C")
            self.alertas_text.tag_config("exito", foreground="#4CAF50")
            self.alertas_text.tag_config("info", foreground="#757575")
            self.alertas_text.tag_config("titulo_info", foreground="#2196F3")

            self.alertas_text.configure(state="disabled")
            self.logger.info(f"Generadas {len(notificaciones)} notificaciones en dashboard")

        except Exception as e:
            self.logger.error(f"Error actualizando alertas: {e}")
            self.alertas_text.configure(state="normal")
            self.alertas_text.delete("1.0", "end")
            self.alertas_text.insert("end", "❌ Error cargando alertas\n")
            self.alertas_text.insert("end", f"Detalle: {str(e)}")
            self.alertas_text.configure(state="disabled")

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
            plt.close(self.fig1)
            plt.close(self.fig2)
            self.logger.info("Recursos de matplotlib liberados")
        except Exception as e:
            self.logger.error(f"Error liberando recursos: {e}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Dashboard Test")
    app.geometry("1000x700")
    
    dashboard = DashboardModule(app)
    dashboard.pack(fill="both", expand=True)
    
    app.mainloop()