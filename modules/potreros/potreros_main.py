import customtkinter as ctk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class PotrerosModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_potreros()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="🌿 Gestión de Potreros",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=15)

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tabla de potreros
        ctk.CTkLabel(
            main_frame,
            text="📋 Potreros Registrados",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Frame para la tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        # Tabla
        self.tabla = ttk.Treeview(
            table_frame,
            columns=("finca", "nombre", "area", "capacidad", "pasto", "estado"),
            show="headings",
            height=18
        )

        columnas = [
            ("finca", "Finca", 150),
            ("nombre", "Potrero", 150),
            ("area", "Área (Ha)", 100),
            ("capacidad", "Capacidad", 100),
            ("pasto", "Tipo Pasto", 150),
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
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(
            action_frame,
            text="🔄 Actualizar",
            command=self.cargar_potreros,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_frame,
            text="⚙️ Configurar Potreros",
            command=self.abrir_configuracion,
            width=200,
            fg_color="green",
            hover_color="#006400"
        ).pack(side="left", padx=5)

    def cargar_potreros(self):
        """Carga los potreros en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        f.nombre as finca,
                        p.nombre,
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.tipo_pasto,
                        p.estado
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    ORDER BY p.nombre
                """)

                for fila in cursor.fetchall():
                    area = f"{fila[2]:.2f}" if fila[2] else "-"
                    capacidad = str(fila[3]) if fila[3] else "-"
                    self.tabla.insert("", "end", values=(
                        fila[0] or "-",
                        fila[1],
                        area,
                        capacidad,
                        fila[4] or "-",
                        fila[5] or "Activo"
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los potreros:\n{e}")

    def abrir_configuracion(self):
        """Abre el módulo de configuración de potreros"""
        messagebox.showinfo(
            "Configuración",
            "Para configurar potreros, vaya al módulo de Configuración > Potreros"
        )

