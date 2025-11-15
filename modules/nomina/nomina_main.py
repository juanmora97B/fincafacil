import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class NominaModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_empleados()
        self.cargar_historial()

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

        # Frame de información
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            info_frame,
            text="💡 Para agregar o editar empleados, use el módulo de Configuración > Empleados",
            font=("Segoe UI", 12),
            wraplength=600
        ).pack(pady=10)

        # Tabla de empleados
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.tabla_empleados = ttk.Treeview(
            table_frame,
            columns=("codigo", "nombre", "cargo", "salario", "bonos", "deducciones", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre Completo", 200),
            ("cargo", "Cargo", 150),
            ("salario", "Salario Diario", 120),
            ("bonos", "Bonos Mensual", 120),
            ("deducciones", "Deducciones", 120),
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
            text="📊 Ver Detalles",
            command=self.ver_detalles_empleado,
            width=150
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
        
        # Fechas predeterminadas (mes actual)
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        self.entry_fecha_inicio = ctk.CTkEntry(periodo_frame, placeholder_text="Fecha Inicio (YYYY-MM-DD)", width=200)
        self.entry_fecha_inicio.insert(0, primer_dia_mes.strftime("%Y-%m-%d"))
        self.entry_fecha_inicio.pack(side="left", padx=5)
        
        self.entry_fecha_fin = ctk.CTkEntry(periodo_frame, placeholder_text="Fecha Fin (YYYY-MM-DD)", width=200)
        self.entry_fecha_fin.insert(0, hoy.strftime("%Y-%m-%d"))
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

        # Opciones adicionales
        opciones_frame = ctk.CTkFrame(main_frame)
        opciones_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(opciones_frame, text="Opciones:", width=150).pack(side="left", padx=5)
        
        self.var_incluir_bonos = ctk.BooleanVar(value=True)
        self.check_bonos = ctk.CTkCheckBox(opciones_frame, text="Incluir Bonos", variable=self.var_incluir_bonos)
        self.check_bonos.pack(side="left", padx=5)
        
        self.var_incluir_deducciones = ctk.BooleanVar(value=True)
        self.check_deducciones = ctk.CTkCheckBox(opciones_frame, text="Incluir Deducciones", variable=self.var_incluir_deducciones)
        self.check_deducciones.pack(side="left", padx=5)

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
            text="💾 Registrar Pago",
            command=self.registrar_pago,
            fg_color="blue",
            hover_color="#0056b3",
            width=150
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

        # Filtros
        filtros_frame = ctk.CTkFrame(main_frame)
        filtros_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(filtros_frame, text="Filtrar por:", width=80).pack(side="left", padx=5)
        
        self.combo_filtro_empleado = ctk.CTkComboBox(filtros_frame, width=200, values=["Todos los empleados"])
        self.combo_filtro_empleado.pack(side="left", padx=5)
        
        ctk.CTkLabel(filtros_frame, text="Mes:", width=50).pack(side="left", padx=5)
        meses = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.combo_filtro_mes = ctk.CTkComboBox(filtros_frame, width=120, values=meses)
        self.combo_filtro_mes.set("Todos")
        self.combo_filtro_mes.pack(side="left", padx=5)

        ctk.CTkButton(
            filtros_frame,
            text="🔍 Aplicar Filtros",
            command=self.aplicar_filtros_historial,
            width=120
        ).pack(side="left", padx=5)

        # Tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

        self.tabla_historial = ttk.Treeview(
            table_frame,
            columns=("id", "fecha", "empleado", "periodo", "dias", "salario_base", "bonos", "deducciones", "total", "estado"),
            show="headings",
            height=15
        )

        columnas = [
            ("id", "ID", 60),
            ("fecha", "Fecha Pago", 100),
            ("empleado", "Empleado", 150),
            ("periodo", "Período", 100),
            ("dias", "Días", 60),
            ("salario_base", "Salario Base", 100),
            ("bonos", "Bonos", 100),
            ("deducciones", "Deducciones", 100),
            ("total", "Total", 100),
            ("estado", "Estado", 80)
        ]

        for col, heading, width in columnas:
            self.tabla_historial.heading(col, text=heading)
            self.tabla_historial.column(col, width=width, anchor="center")

        self.tabla_historial.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_historial.yview)
        self.tabla_historial.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar",
            command=self.cargar_historial,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📄 Ver Detalle",
            command=self.ver_detalle_pago,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Anular Pago",
            command=self.anular_pago,
            fg_color="red",
            hover_color="#8B0000",
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
                           cargo, salario_diario, 
                           COALESCE(bono_alimenticio, 0) + COALESCE(bono_productividad, 0) as total_bonos,
                           COALESCE(seguro_social, 0) + COALESCE(otras_deducciones, 0) as total_deducciones,
                           estado_actual
                    FROM empleado
                    WHERE estado = 'Activo'
                    ORDER BY nombres
                """)

                for row in cursor.fetchall():
                    salario = f"${row[3]:,.0f}" if row[3] else "$0"
                    bonos = f"${row[4]:,.0f}" if row[4] else "$0"
                    deducciones = f"${row[5]:,.0f}" if row[5] else "$0"
                    
                    self.tabla_empleados.insert("", "end", values=(
                        row[0], row[1], row[2] or "-", salario, bonos, deducciones, row[6] or "Activo"
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados:\n{e}")

    def cargar_empleados_combo(self):
        """Carga empleados en los combobox"""
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
                self.combo_filtro_empleado.configure(values=["Todos los empleados"] + empleados)
                self.combo_filtro_empleado.set("Todos los empleados")
        except Exception as e:
            print(f"Error al cargar empleados: {e}")

    def ver_detalles_empleado(self):
        """Muestra los detalles del empleado seleccionado"""
        seleccionado = self.tabla_empleados.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para ver sus detalles")
            return

        codigo = self.tabla_empleados.item(seleccionado[0])["values"][0]
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombres, apellidos, cargo, salario_diario,
                           bono_alimenticio, bono_productividad, seguro_social, otras_deducciones,
                           fecha_ingreso, estado_actual
                    FROM empleado
                    WHERE codigo = ?
                """, (codigo,))
                
                empleado = cursor.fetchone()
                if empleado:
                    detalles = f"""
📋 DETALLES DEL EMPLEADO

👤 Código: {empleado[0]}
📛 Nombre: {empleado[1]} {empleado[2]}
💼 Cargo: {empleado[3] or 'No especificado'}
📅 Fecha Ingreso: {empleado[9] or 'No especificada'}
📊 Estado: {empleado[10] or 'Activo'}

💰 INFORMACIÓN SALARIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 Salario Diario: ${empleado[4]:,.0f}
🍽️ Bono Alimenticio: ${empleado[5] or 0:,.0f}
📈 Bono Productividad: ${empleado[6] or 0:,.0f}
🏥 Seguro Social: ${empleado[7] or 0:,.0f}
📉 Otras Deducciones: ${empleado[8] or 0:,.0f}

📊 TOTALES MENSUALES (30 días)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Salario Base: ${(empleado[4] or 0) * 30:,.0f}
➕ Total Bonos: ${(empleado[5] or 0) + (empleado[6] or 0):,.0f}
➖ Total Deducciones: ${(empleado[7] or 0) + (empleado[8] or 0):,.0f}
💵 Neto a Pagar: ${((empleado[4] or 0) * 30) + (empleado[5] or 0) + (empleado[6] or 0) - (empleado[7] or 0) - (empleado[8] or 0):,.0f}
                    """
                    messagebox.showinfo(f"Detalles - {empleado[0]}", detalles)
                else:
                    messagebox.showerror("Error", "No se encontró el empleado")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")

    def calcular_nomina(self):
        """Calcula la nómina de un empleado"""
        if not self.combo_empleado.get() or not self.entry_dias.get():
            messagebox.showwarning("Atención", "Complete todos los campos")
            return

        try:
            codigo_empleado = self.combo_empleado.get().split(" - ")[0]
            dias = int(self.entry_dias.get())
            fecha_inicio = self.entry_fecha_inicio.get()
            fecha_fin = self.entry_fecha_fin.get()

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT salario_diario, bono_alimenticio, bono_productividad, 
                           seguro_social, otras_deducciones, nombres || ' ' || apellidos
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
                nombre_empleado = row[5]

                # Cálculos
                salario_base = salario_diario * dias
                
                # Aplicar opciones
                total_bonos = (bono_alimenticio + bono_productividad) if self.var_incluir_bonos.get() else 0
                total_deducciones = (seguro_social + otras_deducciones) if self.var_incluir_deducciones.get() else 0
                
                total_pagar = salario_base + total_bonos - total_deducciones

                # Mostrar resultado
                resultado = f"""
💰 CÁLCULO DE NÓMINA

👤 Empleado: {nombre_empleado}
📅 Período: {fecha_inicio} a {fecha_fin}
📊 Días Trabajados: {dias}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DESGLOSE:

💰 Salario Base ({dias} días × ${salario_diario:,.0f}): ${salario_base:,.0f}
"""

                if self.var_incluir_bonos.get():
                    resultado += f"""➕ Bonos: ${total_bonos:,.0f}
   • Alimenticio: ${bono_alimenticio:,.0f}
   • Productividad: ${bono_productividad:,.0f}
"""

                if self.var_incluir_deducciones.get():
                    resultado += f"""➖ Deducciones: ${total_deducciones:,.0f}
   • Seguro Social: ${seguro_social:,.0f}
   • Otras: ${otras_deducciones:,.0f}
"""

                resultado += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💵 TOTAL A PAGAR: ${total_pagar:,.0f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

                self.label_resultado.configure(text=resultado)
                self.calculo_actual = {
                    'codigo_empleado': codigo_empleado,
                    'nombre_empleado': nombre_empleado,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'dias': dias,
                    'salario_base': salario_base,
                    'total_bonos': total_bonos,
                    'total_deducciones': total_deducciones,
                    'total_pagar': total_pagar
                }

        except ValueError:
            messagebox.showerror("Error", "Los días trabajados deben ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular nómina:\n{e}")

    def registrar_pago(self):
        """Registra el pago de nómina en la base de datos"""
        if not hasattr(self, 'calculo_actual'):
            messagebox.showwarning("Atención", "Primero debe calcular una nómina")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla de pagos si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pago_nomina (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_empleado TEXT NOT NULL,
                        fecha_pago DATE DEFAULT CURRENT_DATE,
                        periodo_inicio DATE NOT NULL,
                        periodo_fin DATE NOT NULL,
                        dias_trabajados INTEGER NOT NULL,
                        salario_base REAL NOT NULL,
                        bonos REAL NOT NULL,
                        deducciones REAL NOT NULL,
                        total_pagado REAL NOT NULL,
                        estado TEXT DEFAULT 'Pagado',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (codigo_empleado) REFERENCES empleado(codigo)
                    )
                """)

                # Insertar pago
                cursor.execute("""
                    INSERT INTO pago_nomina 
                    (codigo_empleado, periodo_inicio, periodo_fin, dias_trabajados,
                     salario_base, bonos, deducciones, total_pagado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.calculo_actual['codigo_empleado'],
                    self.calculo_actual['fecha_inicio'],
                    self.calculo_actual['fecha_fin'],
                    self.calculo_actual['dias'],
                    self.calculo_actual['salario_base'],
                    self.calculo_actual['total_bonos'],
                    self.calculo_actual['total_deducciones'],
                    self.calculo_actual['total_pagar']
                ))

                conn.commit()

            messagebox.showinfo("Éxito", "Pago registrado correctamente en el historial")
            self.cargar_historial()
            self.limpiar_calculo()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el pago:\n{e}")

    def limpiar_calculo(self):
        """Limpia el formulario de cálculo"""
        self.combo_empleado.set("")
        self.entry_dias.delete(0, "end")
        self.entry_dias.insert(0, "30")
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        self.entry_fecha_inicio.delete(0, "end")
        self.entry_fecha_inicio.insert(0, primer_dia_mes.strftime("%Y-%m-%d"))
        self.entry_fecha_fin.delete(0, "end")
        self.entry_fecha_fin.insert(0, hoy.strftime("%Y-%m-%d"))
        self.label_resultado.configure(text="Complete los campos y haga clic en 'Calcular'")
        if hasattr(self, 'calculo_actual'):
            del self.calculo_actual

    def cargar_historial(self):
        """Carga el historial de pagos"""
        for item in self.tabla_historial.get_children():
            self.tabla_historial.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pago_nomina (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        codigo_empleado TEXT NOT NULL,
                        fecha_pago DATE DEFAULT CURRENT_DATE,
                        periodo_inicio DATE NOT NULL,
                        periodo_fin DATE NOT NULL,
                        dias_trabajados INTEGER NOT NULL,
                        salario_base REAL NOT NULL,
                        bonos REAL NOT NULL,
                        deducciones REAL NOT NULL,
                        total_pagado REAL NOT NULL,
                        estado TEXT DEFAULT 'Pagado',
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    SELECT p.id, p.fecha_pago, e.nombres || ' ' || e.apellidos,
                           p.periodo_inicio || ' a ' || p.periodo_fin, p.dias_trabajados,
                           p.salario_base, p.bonos, p.deducciones, p.total_pagado, p.estado
                    FROM pago_nomina p
                    JOIN empleado e ON p.codigo_empleado = e.codigo
                    ORDER BY p.fecha_pago DESC
                """)

                for row in cursor.fetchall():
                    self.tabla_historial.insert("", "end", values=(
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        f"${row[5]:,.0f}",
                        f"${row[6]:,.0f}",
                        f"${row[7]:,.0f}",
                        f"${row[8]:,.0f}",
                        row[9]
                    ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el historial:\n{e}")

    def aplicar_filtros_historial(self):
        """Aplica filtros al historial (implementación básica)"""
        self.cargar_historial()  # Por ahora recarga todo
        messagebox.showinfo("Info", "Los filtros se implementarán en una versión futura")

    def ver_detalle_pago(self):
        """Muestra el detalle de un pago seleccionado"""
        seleccionado = self.tabla_historial.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un pago para ver el detalle")
            return

        pago_id = self.tabla_historial.item(seleccionado[0])["values"][0]
        messagebox.showinfo("Detalle de Pago", f"Detalle del pago ID: {pago_id}\n\nEsta funcionalidad se implementará próximamente.")

    def anular_pago(self):
        """Anula un pago seleccionado"""
        seleccionado = self.tabla_historial.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un pago para anular")
            return

        pago_id = self.tabla_historial.item(seleccionado[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de anular el pago ID: {pago_id}?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE pago_nomina SET estado = 'Anulado' WHERE id = ?", (pago_id,))
                    conn.commit()
                
                messagebox.showinfo("Éxito", "Pago anulado correctamente")
                self.cargar_historial()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo anular el pago:\n{e}")