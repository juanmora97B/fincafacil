import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import sys
import os

# Asegurar que el directorio padre esté en el path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class DashboardModule(ctk.CTkFrame):
    """Dashboard principal del sistema con métricas, gráficos y alertas."""

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.crear_widgets()
        self.actualizar_estadisticas()

    # =========================================================
    #                      CREACIÓN DE UI
    # =========================================================
    def crear_widgets(self):
        """Construcción completa de la interfaz del Dashboard"""

        # ---------- TÍTULO ----------
        titulo_frame = ctk.CTkFrame(self, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            titulo_frame,
            text="📊 Dashboard - Resumen Ganadero",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left")

        ctk.CTkButton(
            titulo_frame,
            text="🔄 Actualizar",
            command=self.actualizar_estadisticas,
            width=100
        ).pack(side="right")

        # ---------- MÉTRICAS ----------
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
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
        data_frame = ctk.CTkFrame(self, fg_color="transparent")
        data_frame.pack(fill="both", expand=True)

        data_frame.columnconfigure(0, weight=2)
        data_frame.columnconfigure(1, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # ---------- GRÁFICOS ----------
        charts_frame = ctk.CTkFrame(data_frame)
        charts_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)

        # Gráfico Razas
        self.chart1_frame = ctk.CTkFrame(charts_frame)
        self.chart1_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        ctk.CTkLabel(self.chart1_frame, text="📈 Distribución por Razas",
                     font=("Segoe UI", 14, "bold")).pack(pady=5)

        self.fig1, self.ax1 = plt.subplots(figsize=(8, 4))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.chart1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        # Gráfico Estados
        self.chart2_frame = ctk.CTkFrame(charts_frame)
        self.chart2_frame.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(self.chart2_frame, text="📊 Estado de Animales",
                     font=("Segoe UI", 14, "bold")).pack(pady=5)

        self.fig2, self.ax2 = plt.subplots(figsize=(8, 4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.chart2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        # ---------- PANEL DERECHO ----------
        info_frame = ctk.CTkFrame(data_frame)
        info_frame.grid(row=0, column=1, sticky="nsew")

        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        info_frame.rowconfigure(1, weight=1)

        # Eventos
        eventos_frame = ctk.CTkFrame(info_frame)
        eventos_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        eventos_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(eventos_frame, text="📅 Eventos Recientes",
                     font=("Segoe UI", 14, "bold")).pack(pady=5)

        # Frame para el treeview con scrollbar
        eventos_tree_frame = ctk.CTkFrame(eventos_frame)
        eventos_tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.eventos_tree = ttk.Treeview(eventos_tree_frame, columns=("fecha", "evento"),
                                         show="headings", height=8)
        self.eventos_tree.heading("fecha", text="Fecha")
        self.eventos_tree.heading("evento", text="Evento")
        self.eventos_tree.column("fecha", width=100)
        self.eventos_tree.column("evento", width=200)

        # Scrollbar para eventos
        eventos_scrollbar = ttk.Scrollbar(eventos_tree_frame, orient="vertical", command=self.eventos_tree.yview)
        self.eventos_tree.configure(yscrollcommand=eventos_scrollbar.set)

        self.eventos_tree.pack(side="left", fill="both", expand=True)
        eventos_scrollbar.pack(side="right", fill="y")

        # Alertas
        alertas_frame = ctk.CTkFrame(info_frame)
        alertas_frame.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(alertas_frame, text="⚠️ Alertas",
                     font=("Segoe UI", 14, "bold")).pack(pady=5)

        self.alertas_text = ctk.CTkTextbox(alertas_frame, height=100)
        self.alertas_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.alertas_text.configure(state="disabled")

    # =========================================================
    #            MÉTODO PARA CREAR TARJETA DE MÉTRICA
    # =========================================================
    def crear_metric_card(self, parent, titulo, valor, color, columna):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=12)
        card.grid(row=0, column=columna, sticky="ew", padx=5)

        ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 12),
                     text_color="white").pack(pady=(15, 5))

        valor_label = ctk.CTkLabel(card, text=valor, font=("Segoe UI", 24, "bold"),
                                   text_color="white")
        valor_label.pack(pady=(0, 15))

        return valor_label

    # =========================================================
    #                 ACTUALIZACIÓN DE ESTADÍSTICAS
    # =========================================================
    def actualizar_estadisticas(self):
        """Actualiza métricas, gráficos, eventos y alertas"""

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # -------- MÉTRICAS PRINCIPALES --------
                cursor.execute("SELECT COUNT(*) FROM animal")
                total_animales = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                animales_activos = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(precio_compra), 0) FROM animal WHERE estado = 'Activo'")
                valor_inventario = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(DISTINCT id_animal)
                    FROM tratamiento
                    WHERE fecha_fin >= date('now') OR fecha_fin IS NULL
                """)
                en_tratamiento = cursor.fetchone()[0]

                # Mostrar métricas
                self.metricas["total_animales"].configure(text=str(total_animales))
                self.metricas["animales_activos"].configure(text=str(animales_activos))
                self.metricas["valor_inventario"].configure(text=f"${valor_inventario:,.0f}")
                self.metricas["en_tratamiento"].configure(text=str(en_tratamiento))

                # -------- GRÁFICOS --------
                self.actualizar_grafico_razas(cursor)
                self.actualizar_grafico_estados(cursor)

                # -------- INFORMACIÓN --------
                self.actualizar_eventos_recientes(cursor)
                self.actualizar_alertas(cursor)

        except Exception as e:
            print(f"Error actualizando dashboard: {e}")

    # =========================================================
    #                     FUNCIONES DE GRÁFICOS
    # =========================================================
    def actualizar_grafico_razas(self, cursor):
        try:
            cursor.execute("""
                SELECT r.nombre, COUNT(a.id)
                FROM animal a
                LEFT JOIN raza r ON a.id_raza = r.id
                WHERE a.estado = 'Activo'
                GROUP BY r.nombre
                ORDER BY COUNT(a.id) DESC
                LIMIT 8
            """)

            datos = cursor.fetchall()
            razas = [d[0] or "Sin raza" for d in datos]
            cantidades = [d[1] for d in datos]

            self.ax1.clear()

            if datos and sum(cantidades) > 0:
                self.ax1.pie(cantidades, labels=razas, autopct="%1.1f%%", startangle=90)
                self.ax1.set_title("Distribución por Razas", fontsize=12, fontweight='bold')
            else:
                self.ax1.text(0.5, 0.5, "Sin datos disponibles", 
                             ha="center", va="center", transform=self.ax1.transAxes,
                             fontsize=12, style='italic')
                self.ax1.set_title("Distribución por Razas", fontsize=12, fontweight='bold')

            self.fig1.tight_layout()
            self.canvas1.draw()

        except Exception as e:
            print(f"Error gráfico razas: {e}")
            self.ax1.clear()
            self.ax1.text(0.5, 0.5, "Error cargando datos", 
                         ha="center", va="center", transform=self.ax1.transAxes)
            self.canvas1.draw()

    def actualizar_grafico_estados(self, cursor):
        try:
            cursor.execute("""
                SELECT estado, COUNT(*)
                FROM animal
                GROUP BY estado
                ORDER BY COUNT(*) DESC
            """)

            datos = cursor.fetchall()
            estados = [d[0] for d in datos]
            cantidades = [d[1] for d in datos]

            self.ax2.clear()

            if datos:
                bars = self.ax2.bar(estados, cantidades, color=['#2E7D32', '#C62828', '#F57C00', '#1976D2'])
                self.ax2.set_title("Estado de Animales", fontsize=12, fontweight='bold')
                self.ax2.set_ylabel("Cantidad")
                
                # Rotar etiquetas si son muy largas
                self.ax2.tick_params(axis='x', rotation=45)
                
                for bar in bars:
                    height = bar.get_height()
                    self.ax2.text(
                        bar.get_x() + bar.get_width() / 2,
                        height,
                        f"{height}",
                        ha="center", va="bottom"
                    )
            else:
                self.ax2.text(0.5, 0.5, "Sin datos disponibles", 
                             ha="center", va="center", transform=self.ax2.transAxes,
                             fontsize=12, style='italic')
                self.ax2.set_title("Estado de Animales", fontsize=12, fontweight='bold')

            self.fig2.tight_layout()
            self.canvas2.draw()

        except Exception as e:
            print(f"Error gráfico estados: {e}")
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
                SELECT date(fecha_registro), 'Nuevo Animal: ' || codigo
                FROM animal
                ORDER BY fecha_registro DESC
                LIMIT 5
            """)

            eventos_animales = cursor.fetchall()

            # Eventos de tratamientos recientes
            cursor.execute("""
                SELECT date(fecha_inicio), 'Tratamiento: ' || d.descripcion || ' - ' || a.codigo
                FROM tratamiento t
                JOIN animal a ON t.id_animal = a.id
                JOIN diagnostico_veterinario d ON t.id_diagnostico = d.id
                ORDER BY t.fecha_inicio DESC
                LIMIT 3
            """)

            eventos_tratamientos = cursor.fetchall()

            # Combinar eventos
            todos_eventos = eventos_animales + eventos_tratamientos
            todos_eventos.sort(key=lambda x: x[0], reverse=True)
            
            # Mostrar máximo 5 eventos
            for fecha, evento in todos_eventos[:5]:
                self.eventos_tree.insert("", "end", values=(fecha, evento))

            # Si no hay eventos
            if not todos_eventos:
                self.eventos_tree.insert("", "end", values=("--", "No hay eventos recientes"))

        except Exception as e:
            print("Error eventos recientes:", e)
            for item in self.eventos_tree.get_children():
                self.eventos_tree.delete(item)
            self.eventos_tree.insert("", "end", values=("Error", "No se pudieron cargar eventos"))

    def actualizar_alertas(self, cursor):
        try:
            self.alertas_text.configure(state="normal")
            self.alertas_text.delete("1.0", "end")

            alertas = []

            # Animales sin raza
            cursor.execute("SELECT COUNT(*) FROM animal WHERE id_raza IS NULL AND estado = 'Activo'")
            sin_raza = cursor.fetchone()[0]
            if sin_raza > 0:
                alertas.append(f"⚠️ {sin_raza} animal(es) sin raza asignada")

            # Animales sin potrero
            cursor.execute("SELECT COUNT(*) FROM animal WHERE id_potrero IS NULL AND estado = 'Activo'")
            sin_potrero = cursor.fetchone()[0]
            if sin_potrero > 0:
                alertas.append(f"📍 {sin_potrero} animal(es) sin potrero asignado")

            # Tratamientos próximos a vencer
            cursor.execute("""
                SELECT COUNT(*) FROM tratamiento 
                WHERE fecha_fin BETWEEN date('now') AND date('now', '+7 days')
            """)
            tratamientos_proximos = cursor.fetchone()[0]
            if tratamientos_proximos > 0:
                alertas.append(f"💉 {tratamientos_proximos} tratamiento(s) por finalizar esta semana")

            # Partos próximos
            cursor.execute("""
                SELECT COUNT(*) FROM animal 
                WHERE fecha_estimada_parto BETWEEN date('now') AND date('now', '+30 days')
                AND estado = 'Activo'
            """)
            partos_proximos = cursor.fetchone()[0]
            if partos_proximos > 0:
                alertas.append(f"🐣 {partos_proximos} parto(s) esperados en los próximos 30 días")

            # Mostrar alertas
            if alertas:
                for alerta in alertas:
                    self.alertas_text.insert("end", f"• {alerta}\n")
                self.alertas_text.insert("end", "\n📞 Contacte al veterinario si necesita asistencia")
            else:
                self.alertas_text.insert("end", "✅ Todo en orden\n\n")
                self.alertas_text.insert("end", "No se detectaron alertas críticas en el sistema")

            self.alertas_text.configure(state="disabled")

        except Exception as e:
            print("Error alertas:", e)
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
        print("Función de exportación de reporte - Por implementar")

    def limpiar_recursos(self):
        """Limpia recursos de matplotlib al cerrar"""
        try:
            plt.close(self.fig1)
            plt.close(self.fig2)
        except:
            pass