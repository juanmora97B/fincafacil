import customtkinter as ctk
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta
from database import get_db_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('Agg')  # Para evitar problemas de hilos

class DashboardModule(ctk.CTkFrame):  # ⚠️ MANTENER EL MISMO NOMBRE para compatibilidad
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.crear_widgets()
        self.actualizar_estadisticas()

    def crear_widgets(self):
        """Crea la interfaz del dashboard mejorado"""
        # Título y botón actualizar
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

        # ==================== MÉTRICAS PRINCIPALES ====================
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        # Configurar grid 2x2 para métricas
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)

        # Métricas clave
        self.metricas = {
            'total_animales': self.crear_metric_card(metrics_frame, "🐄 Total Animales", "0", "#2E7D32", 0),
            'animales_activos': self.crear_metric_card(metrics_frame, "✅ Activos", "0", "#1976D2", 1),
            'valor_inventario': self.crear_metric_card(metrics_frame, "💰 Valor Inventario", "$0", "#F57C00", 2),
            'en_tratamiento': self.crear_metric_card(metrics_frame, "🏥 En Tratamiento", "0", "#C62828", 3)
        }

        # ==================== GRÁFICOS Y DATOS ====================
        data_frame = ctk.CTkFrame(self, fg_color="transparent")
        data_frame.pack(fill="both", expand=True)
        data_frame.grid_columnconfigure(0, weight=2)
        data_frame.grid_columnconfigure(1, weight=1)
        data_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo - Gráficos
        charts_frame = ctk.CTkFrame(data_frame)
        charts_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_rowconfigure(1, weight=1)

        # Gráfico 1: Distribución por Razas
        self.chart1_frame = ctk.CTkFrame(charts_frame)
        self.chart1_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        ctk.CTkLabel(self.chart1_frame, text="📈 Distribución por Razas", 
                    font=("Segoe UI", 14, "bold")).pack(pady=5)
        self.fig1, self.ax1 = plt.subplots(figsize=(8, 4))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.chart1_frame)
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        # Gráfico 2: Animales por Estado
        self.chart2_frame = ctk.CTkFrame(charts_frame)
        self.chart2_frame.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(self.chart2_frame, text="📊 Estado de Animales", 
                    font=("Segoe UI", 14, "bold")).pack(pady=5)
        self.fig2, self.ax2 = plt.subplots(figsize=(8, 4))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.chart2_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)

        # Panel derecho - Información detallada
        info_frame = ctk.CTkFrame(data_frame)
        info_frame.grid(row=0, column=1, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_rowconfigure(0, weight=1)
        info_frame.grid_rowconfigure(1, weight=1)

        # Eventos Recientes
        eventos_frame = ctk.CTkFrame(info_frame)
        eventos_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        eventos_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(eventos_frame, text="📅 Eventos Recientes", 
                    font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.eventos_tree = ttk.Treeview(eventos_frame, columns=("fecha", "evento"), 
                                       show="headings", height=8)
        self.eventos_tree.heading("fecha", text="Fecha")
        self.eventos_tree.heading("evento", text="Evento")
        self.eventos_tree.column("fecha", width=80)
        self.eventos_tree.column("evento", width=200)
        self.eventos_tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Alertas y Recordatorios
        alertas_frame = ctk.CTkFrame(info_frame)
        alertas_frame.grid(row=1, column=0, sticky="nsew")
        alertas_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(alertas_frame, text="⚠️ Alertas", 
                    font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.alertas_text = ctk.CTkTextbox(alertas_frame, height=100)
        self.alertas_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.alertas_text.configure(state="disabled")

    def crear_metric_card(self, parent, titulo, valor, color, columna):
        """Crea una card de métrica"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=12)
        card.grid(row=0, column=columna, sticky="ew", padx=5)
        
        ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 12), 
                    text_color="white").pack(pady=(15, 5))
        
        valor_label = ctk.CTkLabel(card, text=valor, font=("Segoe UI", 24, "bold"), 
                                 text_color="white")
        valor_label.pack(pady=(0, 15))
        
        return valor_label

    def actualizar_estadisticas(self):
        """Actualiza todas las estadísticas del dashboard"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # ==================== MÉTRICAS PRINCIPALES ====================
                # Total de animales
                cursor.execute("SELECT COUNT(*) FROM animal")
                total_animales = cursor.fetchone()[0]
                
                # Animales activos
                cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
                animales_activos = cursor.fetchone()[0]
                
                # Valor estimado del inventario (precio_compra de animales activos)
                cursor.execute("SELECT COALESCE(SUM(precio_compra), 0) FROM animal WHERE estado = 'Activo'")
                valor_inventario = cursor.fetchone()[0]
                
                # Animales en tratamiento (últimos 7 días)
                cursor.execute("""
                    SELECT COUNT(DISTINCT id_animal) 
                    FROM tratamiento 
                    WHERE fecha >= date('now', '-7 days')
                """)
                en_tratamiento = cursor.fetchone()[0]
                
                # Actualizar métricas
                self.metricas['total_animales'].configure(text=str(total_animales))
                self.metricas['animales_activos'].configure(text=str(animales_activos))
                self.metricas['valor_inventario'].configure(text=f"${valor_inventario:,.0f}")
                self.metricas['en_tratamiento'].configure(text=str(en_tratamiento))
                
                # ==================== GRÁFICOS ====================
                self.actualizar_grafico_razas(cursor)
                self.actualizar_grafico_estados(cursor)
                
                # ==================== INFORMACIÓN DETALLADA ====================
                self.actualizar_eventos_recientes(cursor)
                self.actualizar_alertas(cursor)
                
        except Exception as e:
            print(f"Error actualizando dashboard: {e}")

    def actualizar_grafico_razas(self, cursor):
        """Actualiza el gráfico de distribución por razas"""
        try:
            cursor.execute("""
                SELECT r.nombre, COUNT(a.id) as cantidad
                FROM animal a
                LEFT JOIN raza r ON a.id_raza = r.id
                WHERE a.estado = 'Activo'
                GROUP BY r.nombre
                ORDER BY cantidad DESC
                LIMIT 8
            """)
            
            datos = cursor.fetchall()
            razas = [f"{r[0] or 'Sin Raza'}" for r in datos]
            cantidades = [r[1] for r in datos]
            
            self.ax1.clear()
            if datos:
                self.ax1.pie(cantidades, labels=razas, autopct='%1.1f%%', startangle=90)
                self.ax1.set_title('Distribución por Razas', fontweight='bold')
            else:
                self.ax1.text(0.5, 0.5, 'No hay datos', ha='center', va='center', 
                             transform=self.ax1.transAxes, fontsize=12)
            
            self.fig1.tight_layout()
            self.canvas1.draw()
            
        except Exception as e:
            print(f"Error en gráfico razas: {e}")

    def actualizar_grafico_estados(self, cursor):
        """Actualiza el gráfico de animales por estado"""
        try:
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM animal
                GROUP BY estado
            """)
            
            datos = cursor.fetchall()
            estados = [e[0] for e in datos]
            cantidades = [e[1] for e in datos]
            
            self.ax2.clear()
            if datos:
                bars = self.ax2.bar(estados, cantidades, color=['#2E7D32', '#F57C00', '#C62828'])
                self.ax2.set_title('Animales por Estado', fontweight='bold')
                self.ax2.set_ylabel('Cantidad')
                
                # Agregar valores en las barras
                for bar in bars:
                    height = bar.get_height()
                    self.ax2.text(bar.get_x() + bar.get_width()/2., height,
                                 f'{int(height)}', ha='center', va='bottom')
            else:
                self.ax2.text(0.5, 0.5, 'No hay datos', ha='center', va='center', 
                             transform=self.ax2.transAxes, fontsize=12)
            
            self.fig2.tight_layout()
            self.canvas2.draw()
            
        except Exception as e:
            print(f"Error en gráfico estados: {e}")

    def actualizar_eventos_recientes(self, cursor):
        """Actualiza la lista de eventos recientes"""
        try:
            # Limpiar tabla
            for item in self.eventos_tree.get_children():
                self.eventos_tree.delete(item)
            
            # Animales registrados recientemente
            cursor.execute("""
                SELECT date(fecha_registro), 'Nuevo Animal: ' || codigo
                FROM animal 
                WHERE fecha_registro IS NOT NULL
                ORDER BY fecha_registro DESC 
                LIMIT 5
            """)
            
            for fecha, evento in cursor.fetchall():
                self.eventos_tree.insert("", "end", values=(fecha, evento))
                
        except Exception as e:
            print(f"Error actualizando eventos: {e}")

    def actualizar_alertas(self, cursor):
        """Actualiza las alertas del sistema"""
        try:
            self.alertas_text.configure(state="normal")
            self.alertas_text.delete("1.0", "end")
            
            alertas = []
            
            # Verificar animales sin raza
            cursor.execute("SELECT COUNT(*) FROM animal WHERE id_raza IS NULL AND estado = 'Activo'")
            sin_raza = cursor.fetchone()[0]
            if sin_raza > 0:
                alertas.append(f"⚠️ {sin_raza} animales sin raza asignada")
            
            # Verificar animales sin potrero
            cursor.execute("SELECT COUNT(*) FROM animal WHERE id_potrero IS NULL AND estado = 'Activo'")
            sin_potrero = cursor.fetchone()[0]
            if sin_potrero > 0:
                alertas.append(f"📍 {sin_potrero} animales sin potrero asignado")
            
            # Verificar tratamientos próximos
            cursor.execute("""
                SELECT COUNT(*) FROM tratamiento 
                WHERE fecha_proxima BETWEEN date('now') AND date('now', '+3 days')
            """)
            tratamientos_proximos = cursor.fetchone()[0]
            if tratamientos_proximos > 0:
                alertas.append(f"💉 {tratamientos_proximos} tratamientos próximos")
            
            if alertas:
                for alerta in alertas:
                    self.alertas_text.insert("end", f"• {alerta}\n")
            else:
                self.alertas_text.insert("end", "✅ Todo en orden\n")
            
            self.alertas_text.configure(state="disabled")
            
        except Exception as e:
            print(f"Error actualizando alertas: {e}")