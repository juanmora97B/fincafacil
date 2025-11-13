import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db


class NominaModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_empleados()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="👥 Gestión de Nómina",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=15)

        # Frame principal con tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab: Empleados
        self.frame_empleados = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_empleados, text="👤 Empleados")

        # Tab: Cálculo de Nómina
        self.frame_calculo = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_calculo, text="💰 Cálculo de Nómina")

        # Tab: Historial
        self.frame_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_historial, text="📋 Historial")

        # Crear contenido de cada tab
        self.crear_tab_empleados()
        self.crear_tab_calculo()
        self.crear_tab_historial()

    def crear_tab_empleados(self):
        """Tab de gestión de empleados"""
        main_frame = ctk.CTkFrame(self.frame_empleados)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="📋 Lista de Empleados",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Tabla de empleados
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.tabla_empleados = ttk.Treeview(
            table_frame,
            columns=("codigo", "nombre", "cargo", "salario", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre Completo", 250),
            ("cargo", "Cargo", 150),
            ("salario", "Salario Diario", 120),
            ("estado", "Estado", 100)
        ]

        for col, heading, width in columnas:
            self.tabla_empleados.heading(col, text=heading)
            self.tabla_empleados.column(col, width=width, anchor="center")

        self.tabla_empleados.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_empleados.yview)
        self.tabla_empleados.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=self.cargar_empleados,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="⚙️ Configurar Empleados",
            command=self.abrir_configuracion,
            width=200,
            fg_color="green",
            hover_color="#006400"
        ).pack(side="left", padx=5)

    def crear_tab_calculo(self):
        """Tab de cálculo de nómina"""
        main_frame = ctk.CTkScrollableFrame(self.frame_calculo)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="💰 Cálculo de Nómina",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Período
        periodo_frame = ctk.CTkFrame(main_frame)
        periodo_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(periodo_frame, text="Período de Pago:", width=150).pack(side="left", padx=5)
        self.entry_fecha_inicio = ctk.CTkEntry(periodo_frame, placeholder_text="Fecha Inicio (YYYY-MM-DD)", width=200)
        self.entry_fecha_inicio.pack(side="left", padx=5)
        self.entry_fecha_fin = ctk.CTkEntry(periodo_frame, placeholder_text="Fecha Fin (YYYY-MM-DD)", width=200)
        self.entry_fecha_fin.pack(side="left", padx=5)

        # Empleado
        empleado_frame = ctk.CTkFrame(main_frame)
        empleado_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(empleado_frame, text="Empleado:", width=150).pack(side="left", padx=5)
        self.combo_empleado = ctk.CTkComboBox(empleado_frame, width=300)
        self.combo_empleado.pack(side="left", padx=5, fill="x", expand=True)

        # Días trabajados
        dias_frame = ctk.CTkFrame(main_frame)
        dias_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(dias_frame, text="Días Trabajados:", width=150).pack(side="left", padx=5)
        self.entry_dias = ctk.CTkEntry(dias_frame, width=200)
        self.entry_dias.insert(0, "30")
        self.entry_dias.pack(side="left", padx=5)

        # Resultado
        resultado_frame = ctk.CTkFrame(main_frame)
        resultado_frame.pack(fill="x", pady=20)

        self.label_resultado = ctk.CTkLabel(
            resultado_frame,
            text="Complete los campos y haga clic en 'Calcular'",
            font=("Segoe UI", 14),
            wraplength=600
        )
        self.label_resultado.pack(pady=20)

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="🧮 Calcular Nómina",
            command=self.calcular_nomina,
            fg_color="green",
            hover_color="#006400",
            width=200
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar",
            command=self.limpiar_calculo,
            width=150
        ).pack(side="left", padx=5)

        # Cargar empleados
        self.cargar_empleados_combo()

    def crear_tab_historial(self):
        """Tab de historial de pagos"""
        main_frame = ctk.CTkFrame(self.frame_historial)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="📋 Historial de Pagos",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.tabla_historial = ttk.Treeview(
            table_frame,
            columns=("fecha", "empleado", "dias", "salario_base", "bonos", "deducciones", "total"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 120),
            ("empleado", "Empleado", 200),
            ("dias", "Días", 80),
            ("salario_base", "Salario Base", 120),
            ("bonos", "Bonos", 120),
            ("deducciones", "Deducciones", 120),
            ("total", "Total", 120)
        ]

        for col, heading, width in columnas:
            self.tabla_historial.heading(col, text=heading)
            self.tabla_historial.column(col, width=width, anchor="center")

        self.tabla_historial.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botón
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=self.cargar_historial,
            width=150
        ).pack(side="left", padx=5)

    def cargar_empleados(self):
        """Carga los empleados en la tabla"""
        for item in self.tabla_empleados.get_children():
            self.tabla_empleados.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombres || ' ' || apellidos as nombre, 
                           cargo, salario_diario, estado_actual
                    FROM empleado
                    WHERE estado = 'Activo'
                    ORDER BY nombres
                """)

                for row in cursor.fetchall():
                    salario = f"${row[3]:,.0f}" if row[3] else "$0"
                    self.tabla_empleados.insert("", "end", values=(
                        row[0], row[1], row[2] or "-", salario, row[4] or "Activo"
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados:\n{e}")

    def cargar_empleados_combo(self):
        """Carga empleados en el combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombres || ' ' || apellidos as nombre
                    FROM empleado
                    WHERE estado = 'Activo'
                    ORDER BY nombres
                """)
                empleados = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
                self.combo_empleado.configure(values=empleados)
        except Exception as e:
            print(f"Error al cargar empleados: {e}")

    def calcular_nomina(self):
        """Calcula la nómina de un empleado"""
        if not self.combo_empleado.get() or not self.entry_dias.get():
            messagebox.showwarning("Atención", "Complete todos los campos")
            return

        try:
            codigo_empleado = self.combo_empleado.get().split(" - ")[0]
            dias = int(self.entry_dias.get())

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT salario_diario, bono_alimenticio, bono_productividad, 
                           seguro_social, otras_deducciones
                    FROM empleado
                    WHERE codigo = ? AND estado = 'Activo'
                """, (codigo_empleado,))

                row = cursor.fetchone()
                if not row:
                    messagebox.showerror("Error", "Empleado no encontrado")
                    return

                salario_diario = row[0] or 0
                bono_alimenticio = row[1] or 0
                bono_productividad = row[2] or 0
                seguro_social = row[3] or 0
                otras_deducciones = row[4] or 0

                # Cálculos
                salario_base = salario_diario * dias
                total_bonos = bono_alimenticio + bono_productividad
                total_deducciones = seguro_social + otras_deducciones
                total_pagar = salario_base + total_bonos - total_deducciones

                # Mostrar resultado
                resultado = f"""
💰 CÁLCULO DE NÓMINA

👤 Empleado: {self.combo_empleado.get()}
📅 Días Trabajados: {dias}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DESGLOSE:

💰 Salario Base ({dias} días × ${salario_diario:,.0f}): ${salario_base:,.0f}
➕ Bonos: ${total_bonos:,.0f}
   • Alimenticio: ${bono_alimenticio:,.0f}
   • Productividad: ${bono_productividad:,.0f}
➖ Deducciones: ${total_deducciones:,.0f}
   • Seguro Social: ${seguro_social:,.0f}
   • Otras: ${otras_deducciones:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 TOTAL A PAGAR: ${total_pagar:,.0f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """

                self.label_resultado.configure(text=resultado)

        except ValueError:
            messagebox.showerror("Error", "Los días trabajados deben ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular nómina:\n{e}")

    def limpiar_calculo(self):
        """Limpia el formulario de cálculo"""
        self.combo_empleado.set("")
        self.entry_dias.delete(0, "end")
        self.entry_dias.insert(0, "30")
        self.entry_fecha_inicio.delete(0, "end")
        self.entry_fecha_fin.delete(0, "end")
        self.label_resultado.configure(text="Complete los campos y haga clic en 'Calcular'")

    def cargar_historial(self):
        """Carga el historial de pagos"""
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        # Por ahora mostrar mensaje
        messagebox.showinfo("Info", "El historial de pagos se implementará próximamente.\nPor ahora use el módulo de Configuración > Empleados para gestionar empleados.")

    def abrir_configuracion(self):
        """Abre el módulo de configuración de empleados"""
        messagebox.showinfo(
            "Configuración",
            "Para configurar empleados, vaya al módulo de Configuración > Empleados"
        )

