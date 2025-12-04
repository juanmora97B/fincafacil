import customtkinter as ctk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.ui import get_theme_colors, style_treeview, add_tooltip


class PotrerosModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._colors = get_theme_colors()
        self._modo = self._colors["mode"]
        self._fg_card = self._colors["fg"]
        self._sel_card = self._colors["sel"]
        self._hover_card = self._colors["hover"]
        self.main_frame = None  # Inicializar atributo
        self.crear_widgets()
        self.cargar_potreros()

    def crear_widgets(self):
        # Título compacto
        titulo = ctk.CTkLabel(
            self,
            text="🌿 Gestión de Potreros",
            font=("Segoe UI", 22, "bold"),
            text_color=self._sel_card
        )
        titulo.pack(pady=(5, 3))
        add_tooltip(titulo, "Gestión y visualización de potreros en la finca")

        # Frame principal expandido
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=(3, 10))

        # Información general
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.pack(fill="x", pady=5)

        info_label = ctk.CTkLabel(
            info_frame,
            text="💡 Para agregar o editar potreros, use el módulo de Configuración > Potreros",
            font=("Segoe UI", 12),
            wraplength=600,
            text_color="gray"
        )
        info_label.pack(pady=5)
        add_tooltip(info_label, "Acceso rápido a configuración de potreros")

        # Métricas rápidas
        self.crear_metricas_rapidas(self.main_frame)

        # Tabla de potreros
        tabla_label = ctk.CTkLabel(
            self.main_frame,
            text="📋 Potreros Registrados",
            font=("Segoe UI", 18, "bold"),
            text_color=self._sel_card
        )
        tabla_label.pack(pady=(10, 5))
        add_tooltip(tabla_label, "Listado de todos los potreros registrados")

        # Frame para la tabla
        table_frame = ctk.CTkFrame(self.main_frame)
        table_frame.pack(fill="both", expand=True)

        # Tabla
        style_treeview()
        self.tabla = ttk.Treeview(
            table_frame,
            columns=("finca", "nombre", "sector", "area", "capacidad", "animales", "pasto", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("finca", "Finca", 120),
            ("nombre", "Potrero", 120),
            ("sector", "Sector", 100),
            ("area", "Área (Ha)", 90),
            ("capacidad", "Capacidad", 90),
            ("animales", "Animales", 90),
            ("pasto", "Tipo Pasto", 120),
            ("estado", "Estado", 100)
        ]

        for col, heading, width in columnas:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.pack(pady=5)

        btn_actualizar = ctk.CTkButton(
            action_frame,
            text="🔄 Actualizar",
            command=self.cargar_potreros,
            width=150,
            fg_color=self._sel_card,
            hover_color=self._hover_card
        )
        btn_actualizar.pack(side="left", padx=5)
        add_tooltip(btn_actualizar, "Recargar la lista y métricas de potreros")

        btn_detalles = ctk.CTkButton(
            action_frame,
            text="📊 Ver Detalles",
            command=self.ver_detalles_potrero,
            width=150,
            fg_color=self._sel_card,
            hover_color=self._hover_card
        )
        btn_detalles.pack(side="left", padx=5)
        add_tooltip(btn_detalles, "Ver información detallada del potrero seleccionado")

        btn_animales = ctk.CTkButton(
            action_frame,
            text="🐄 Ver Animales",
            command=self.ver_animales_potrero,
            width=150,
            fg_color=self._sel_card,
            hover_color=self._hover_card
        )
        btn_animales.pack(side="left", padx=5)
        add_tooltip(btn_animales, "Ver animales asignados al potrero seleccionado")

        btn_config = ctk.CTkButton(
            action_frame,
            text="⚙️ Configurar Potreros",
            command=self.abrir_configuracion,
            width=200,
            fg_color="#388E3C" if self._modo == "Light" else "#006400",
            hover_color="#43A047" if self._modo == "Light" else "#228B22"
        )
        btn_config.pack(side="left", padx=5)
        add_tooltip(btn_config, "Ir a configuración avanzada de potreros")

    def crear_metricas_rapidas(self, parent):
        """Crea métricas rápidas de potreros"""
        metrics_frame = ctk.CTkFrame(parent)
        metrics_frame.pack(fill="x", pady=10)

        # Configurar grid para 4 columnas
        for i in range(4):
            metrics_frame.columnconfigure(i, weight=1)

        self.metricas = {
            "total_potreros": self.crear_metric_card(metrics_frame, "🌿 Total Potreros", "0", "#2E7D32", 0),
            "potreros_activos": self.crear_metric_card(metrics_frame, "✅ Activos", "0", "#1976D2", 1),
            "area_total": self.crear_metric_card(metrics_frame, "📐 Área Total", "0 Ha", "#F57C00", 2),
            "capacidad_total": self.crear_metric_card(metrics_frame, "🐄 Capacidad Total", "0", "#7B1FA2", 3),
        }

    def crear_metric_card(self, parent, titulo, valor, color, columna):
        """Crea una tarjeta de métrica"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=12)
        card.grid(row=0, column=columna, sticky="ew", padx=5)

        label = ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 12), text_color="white")
        label.pack(pady=(10, 5))
        add_tooltip(label, f"Métrica: {titulo}")

        valor_label = ctk.CTkLabel(card, text=valor, font=("Segoe UI", 16, "bold"), text_color="white")
        valor_label.pack(pady=(0, 10))
        add_tooltip(valor_label, f"Valor actual de {titulo}")

        return valor_label
    

    def cargar_potreros(self):
        """Carga los potreros en la tabla y actualiza métricas"""
        # Limpiar tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Cargar datos de potreros
                cursor.execute("""
                    SELECT 
                        f.nombre as finca,
                        p.nombre,
                        COALESCE(s.nombre, 'N/A') as sector,
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.tipo_pasto,
                        p.estado,
                        p.id
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN sector s ON p.id_sector = s.id
                    ORDER BY f.nombre, p.nombre
                """)

                potreros_data = []
                for fila in cursor.fetchall():
                    area = f"{fila[3]:.2f}" if fila[3] else "-"
                    capacidad = str(fila[4]) if fila[4] else "-"
                    
                    # Contar animales en este potrero
                    cursor.execute("""
                        SELECT COUNT(*) FROM animal 
                        WHERE id_potrero = ? AND estado = 'Activo'
                    """, (fila[7],))
                    cantidad_animales = cursor.fetchone()[0]

                    self.tabla.insert("", "end", values=(
                        fila[0] or "-",
                        fila[1],
                        fila[2] or "-",
                        area,
                        capacidad,
                        str(cantidad_animales),
                        fila[5] or "-",
                        fila[6] or "Activo"
                    ))
                    potreros_data.append(fila)

                # Actualizar métricas
                self.actualizar_metricas(cursor, potreros_data)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los potreros:\n{e}")

    def actualizar_metricas(self, cursor, potreros_data):
        """Actualiza las métricas rápidas"""
        try:
            # Total de potreros
            total_potreros = len(potreros_data)
            
            # Potreros activos
            potreros_activos = sum(1 for p in potreros_data if p[6] == 'Activo')
            
            # Área total
            area_total = sum(p[3] for p in potreros_data if p[3] is not None)
            
            # Capacidad total
            capacidad_total = sum(p[4] for p in potreros_data if p[4] is not None)

            # Actualizar labels
            self.metricas["total_potreros"].configure(text=str(total_potreros))
            self.metricas["potreros_activos"].configure(text=str(potreros_activos))
            self.metricas["area_total"].configure(text=f"{area_total:.2f} Ha")
            self.metricas["capacidad_total"].configure(text=str(capacidad_total))

        except Exception as e:
            print(f"Error actualizando métricas: {e}")

    def ver_detalles_potrero(self):
        """Muestra los detalles del potrero seleccionado"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un potrero para ver sus detalles")
            return

        finca = self.tabla.item(seleccionado[0])["values"][0]
        nombre_potrero = self.tabla.item(seleccionado[0])["values"][1]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        p.nombre, COALESCE(s.nombre, 'N/A') as sector, p.area_hectareas, p.capacidad_maxima,
                        p.tipo_pasto, p.descripcion, p.estado, f.nombre as finca_nombre
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN sector s ON p.id_sector = s.id
                    WHERE p.nombre = ? AND f.nombre = ?
                """, (nombre_potrero, finca))

                potrero = cursor.fetchone()
                if potrero:
                    # Contar animales en el potrero
                    cursor.execute("""
                        SELECT COUNT(*) FROM animal 
                        WHERE id_potrero = (
                            SELECT p.id FROM potrero p
                            LEFT JOIN finca f ON p.id_finca = f.id
                            WHERE p.nombre = ? AND f.nombre = ?
                        ) AND estado = 'Activo'
                    """, (nombre_potrero, finca))
                    cantidad_animales = cursor.fetchone()[0]

                    detalles = f"""
📋 DETALLES DEL POTRERO

🏠 Finca: {potrero[7] or 'No especificada'}
🌿 Potrero: {potrero[0]}
📍 Sector: {potrero[1] or 'No especificado'}
📐 Área: {potrero[2] or 0:.2f} hectáreas
🐄 Capacidad Máxima: {potrero[3] or 0} animales
🌱 Tipo de Pasto: {potrero[4] or 'No especificado'}
📊 Estado: {potrero[6] or 'Activo'}

📊 OCUPACIÓN ACTUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐄 Animales asignados: {cantidad_animales}
📈 Porcentaje ocupación: {(cantidad_animales / (potrero[3] or 1)) * 100:.1f}%

📝 DESCRIPCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{potrero[5] or 'No hay descripción disponible'}
                    """
                    messagebox.showinfo(f"Detalles - {potrero[0]}", detalles)
                else:
                    messagebox.showerror("Error", "No se encontró el potrero")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")

    def ver_animales_potrero(self):
        """Muestra los animales asignados al potrero seleccionado"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un potrero para ver sus animales")
            return

        finca = self.tabla.item(seleccionado[0])["values"][0]
        nombre_potrero = self.tabla.item(seleccionado[0])["values"][1]
        animales_actuales = self.tabla.item(seleccionado[0])["values"][5]

        if animales_actuales == "0":
            messagebox.showinfo("Animales", f"El potrero '{nombre_potrero}' no tiene animales asignados")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        a.codigo, a.nombre, r.nombre as raza, a.sexo, a.estado
                    FROM animal a
                    LEFT JOIN raza r ON a.raza_id = r.id
                    WHERE a.id_potrero = (
                        SELECT p.id FROM potrero p
                        LEFT JOIN finca f ON p.id_finca = f.id
                        WHERE p.nombre = ? AND f.nombre = ?
                    ) AND a.estado = 'Activo'
                    ORDER BY a.codigo
                """, (nombre_potrero, finca))

                animales = cursor.fetchall()
                if animales:
                    # Crear ventana con lista de animales
                    ventana_animales = ctk.CTkToplevel(self)
                    ventana_animales.title(f"Animales en {nombre_potrero}")
                    ventana_animales.geometry("600x400")
                    ventana_animales.transient(self)
                    ventana_animales.grab_set()

                    # Frame principal
                    main_frame = ctk.CTkFrame(ventana_animales)
                    # Compactar ancho (20→4)
                    main_frame.pack(fill="both", expand=True, padx=4, pady=5)

                    ctk.CTkLabel(
                        main_frame,
                        text=f"🐄 Animales en {nombre_potrero}",
                        font=("Segoe UI", 16, "bold")
                    ).pack(pady=(0, 10))

                    ctk.CTkLabel(
                        main_frame,
                        text=f"Total: {len(animales)} animales",
                        font=("Segoe UI", 12)
                    ).pack(pady=(0, 10))

                    # Tabla de animales
                    table_frame = ctk.CTkFrame(main_frame)
                    table_frame.pack(fill="both", expand=True)

                    tabla_animales = ttk.Treeview(
                        table_frame,
                        columns=("codigo", "nombre", "raza", "sexo", "estado"),
                        show="headings",
                        height=12
                    )

                    columnas = [
                        ("codigo", "Código", 100),
                        ("nombre", "Nombre", 150),
                        ("raza", "Raza", 120),
                        ("sexo", "Sexo", 80),
                        ("estado", "Estado", 100)
                    ]

                    for col, heading, width in columnas:
                        tabla_animales.heading(col, text=heading)
                        tabla_animales.column(col, width=width, anchor="center")

                    for animal in animales:
                        tabla_animales.insert("", "end", values=animal)

                    tabla_animales.pack(side="left", fill="both", expand=True)

                    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla_animales.yview)
                    tabla_animales.configure(yscroll=scrollbar.set)
                    scrollbar.pack(side="right", fill="y")

                    # Botón cerrar
                    ctk.CTkButton(
                        main_frame,
                        text="Cerrar",
                        command=ventana_animales.destroy,
                        width=100
                    ).pack(pady=10)

                else:
                    messagebox.showinfo("Animales", f"El potrero '{nombre_potrero}' no tiene animales asignados")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los animales:\n{e}")

    def abrir_configuracion(self):
        """Abre el módulo de configuración de potreros"""
        messagebox.showinfo(
            "Configuración",
            "Para configurar potreros, vaya al módulo de Configuración > Potreros\n\n"
            "Allí podrá:\n"
            "• Agregar nuevos potreros\n"
            "• Editar potreros existentes\n"
            "• Configurar áreas y capacidades\n"
            "• Gestionar tipos de pasto\n"
            "• Cambiar estados de potreros"
        )