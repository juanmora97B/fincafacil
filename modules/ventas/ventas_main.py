import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

# Importaciones corregidas
try:
    from database.database import get_db_connection
    from modules.utils.logger import get_logger
    from modules.utils.validators import validator
    from modules.utils.date_picker import attach_date_picker
except ImportError as e:
    import logging
    logging.error(f"Error importando módulos en ventas: {e}")
    raise

class VentasModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Configurar logger
        self.logger = get_logger("Ventas")
        self.logger.info("Módulo de ventas iniciado")
        
        self.crear_widgets()
        self.cargar_ventas()

    def crear_widgets(self):
        """Crea todos los widgets del módulo"""
        # Título compacto
        titulo = ctk.CTkLabel(
            self,
            text="💰 Gestión de Ventas",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=(5, 3))

        # Notebook expandido para ocupar toda la altura disponible
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=2, pady=2)

        # Tab: Nueva Venta
        self.frame_nueva_venta = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_nueva_venta, text="➕ Nueva Venta")

        # Tab: Historial
        self.frame_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_historial, text="📋 Historial de Ventas")

        # Crear formulario de nueva venta
        self.crear_formulario_venta()
        
        # Crear historial
        self.crear_historial()

    def crear_formulario_venta(self):
        """Crea el formulario para registrar una nueva venta"""
        form_frame = ctk.CTkFrame(self.frame_nueva_venta)
        # Compactar ancho y alto (padx 20→4, pady 10→5)
        form_frame.pack(fill="both", expand=True, padx=4, pady=5)

        ctk.CTkLabel(
            form_frame,
            text="📝 Registrar Nueva Venta",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 15))

        # Campos del formulario
        campos_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        campos_frame.pack(fill="both", expand=True, pady=5)

        # Animal
        row1 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Animal *:", width=150).pack(side="left", padx=5)
        self.combo_animal = ctk.CTkComboBox(row1, width=300)
        self.combo_animal.set("Seleccione el animal")
        self.combo_animal.pack(side="left", padx=5, fill="x", expand=True)

        # Fecha
        row2 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Fecha Venta *:", width=150).pack(side="left", padx=5)
        self.entry_fecha = ctk.CTkEntry(row2, width=260, placeholder_text="YYYY-MM-DD")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side="left", padx=5)
        attach_date_picker(row2, self.entry_fecha)

        # Precio
        row3 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Precio Total *:", width=150).pack(side="left", padx=5)
        self.entry_precio = ctk.CTkEntry(row3, width=300)
        self.entry_precio.pack(side="left", padx=5, fill="x", expand=True)

        # Motivo
        row4 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Motivo Venta:", width=150).pack(side="left", padx=5)
        self.combo_motivo = ctk.CTkComboBox(row4, width=300)
        self.combo_motivo.configure(values=[
            "Venta directa", "Subasta", "Consignación", 
            "Emergencia", "Renovación de stock", "Otro"
        ])
        self.combo_motivo.set("Seleccione el motivo")
        self.combo_motivo.pack(side="left", padx=5, fill="x", expand=True)

        # Destino
        row5 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Destino Venta:", width=150).pack(side="left", padx=5)
        self.combo_destino = ctk.CTkComboBox(row5, width=300)
        self.combo_destino.configure(values=[
            "Mercado local", "Frigorífico", "Exportación",
            "Consumidor final", "Otro productor", "Otro"
        ])
        self.combo_destino.set("Seleccione el destino")
        self.combo_destino.pack(side="left", padx=5, fill="x", expand=True)

        # Observaciones
        row6 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row6.pack(fill="both", expand=True, pady=5)
        ctk.CTkLabel(row6, text="Observaciones:", width=150).pack(side="left", padx=5, anchor="n")
        self.text_observaciones = ctk.CTkTextbox(row6, width=300, height=120)
        self.text_observaciones.pack(side="left", padx=5, fill="both", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Venta",
            command=self.guardar_venta,
            fg_color="green",
            hover_color="#006400",
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar",
            command=self.limpiar_formulario,
            width=150
        ).pack(side="left", padx=5)

        # Cargar datos en combos
        self.cargar_combos()

    def crear_historial(self):
        """Crea la tabla de historial de ventas"""
        # Frame para la tabla
        table_frame = ctk.CTkFrame(self.frame_historial)
        # Compactar ancho y alto (padx 20→4, pady 20→5)
        table_frame.pack(fill="both", expand=True, padx=4, pady=5)

        ctk.CTkLabel(
            table_frame,
            text="📋 Historial de Ventas",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Frame para controles
        controls_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=10)
        
        # Filtros
        ctk.CTkLabel(controls_frame, text="Filtrar por:").pack(side="left", padx=5)
        
        self.filtro_mes = ctk.CTkComboBox(controls_frame, width=120)
        self.filtro_mes.configure(values=["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        self.filtro_mes.set("Todos")
        self.filtro_mes.pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="🔍 Aplicar Filtro",
            command=self.aplicar_filtros,
            width=120
        ).pack(side="left", padx=5)

        # Tabla
        self.tabla_ventas = ttk.Treeview(
            table_frame,
            columns=("id", "fecha", "animal", "precio", "motivo", "destino", "observaciones"),
            show="headings",
            height=15
        )

        columnas = [
            ("id", "ID", 60),
            ("fecha", "Fecha", 100),
            ("animal", "Animal", 150),
            ("precio", "Precio", 100),
            ("motivo", "Motivo", 120),
            ("destino", "Destino", 120),
            ("observaciones", "Observaciones", 200)
        ]

        for col, heading, width in columnas:
            self.tabla_ventas.heading(col, text=heading)
            self.tabla_ventas.column(col, width=width, anchor="center")

        self.tabla_ventas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_ventas.yview)
        self.tabla_ventas.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self.frame_historial, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(
            action_frame,
            text="🔄 Actualizar",
            command=self.cargar_ventas,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="📊 Estadísticas",
            command=self.mostrar_estadisticas,
            width=150
        ).pack(side="left", padx=5)

    def cargar_combos(self):
        """Carga los datos en los combobox"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Animales activos (no vendidos)
                cursor.execute("""
                    SELECT id, codigo || ' - ' || COALESCE(nombre, 'Sin nombre') as animal
                    FROM animal 
                    WHERE estado = 'Activo' OR estado IS NULL
                    ORDER BY codigo
                """)
                animales = [f"{row[0]}|{row[1]}" for row in cursor.fetchall()]
                self.combo_animal.configure(values=animales)
                
                self.logger.info(f"Cargados {len(animales)} animales para venta")

        except Exception as e:
            self.logger.error(f"Error al cargar combos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")

    def validar_datos_venta(self):
        """Valida los datos del formulario antes de guardar"""
        errores = []
        
        # Validar animal seleccionado
        if not self.combo_animal.get():
            errores.append("Seleccione un animal")
        
        # Validar fecha
        fecha = self.entry_fecha.get()
        es_valido, mensaje = validator.validar_fecha(fecha)
        if not es_valido:
            errores.append(f"Fecha: {mensaje}")
        
        # Validar precio
        precio = self.entry_precio.get()
        if not precio:
            errores.append("Ingrese el precio de venta")
        else:
            es_valido, mensaje = validator.validar_valor_monetario(float(precio))
            if not es_valido:
                errores.append(f"Precio: {mensaje}")
        
        return errores

    def guardar_venta(self):
        """Guarda una nueva venta"""
        try:
            # Validar datos
            errores = self.validar_datos_venta()
            if errores:
                messagebox.showwarning("Validación", "\n".join(errores))
                return

            # Obtener ID del animal (formato: "id|codigo - nombre")
            animal_seleccionado = self.combo_animal.get()
            if "|" in animal_seleccionado:
                id_animal = animal_seleccionado.split("|")[0]
            else:
                messagebox.showerror("Error", "Formato de animal inválido")
                return
            
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Verificar que el animal existe y está activo
                cursor.execute("""
                    SELECT id, codigo, estado FROM animal WHERE id = ?
                """, (id_animal,))
                animal = cursor.fetchone()
                
                if not animal:
                    messagebox.showerror("Error", f"Animal con ID {id_animal} no encontrado en la base de datos")
                    return
                
                # Acceder al estado correctamente
                estado_animal = animal['estado'] if hasattr(animal, 'keys') else animal[2]
                if estado_animal == 'Vendido':
                    messagebox.showerror("Error", "Este animal ya fue vendido")
                    return

                # Crear tabla de ventas si no existe
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS venta (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL,
                        fecha TEXT NOT NULL,
                        precio_total REAL NOT NULL,
                        motivo_venta TEXT,
                        destino_venta TEXT,
                        observaciones TEXT,
                        fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (animal_id) REFERENCES animal (id)
                    )
                """)

                # Insertar venta
                cursor.execute("""
                    INSERT INTO venta (
                        animal_id, fecha, precio_total, motivo_venta, 
                        destino_venta, observaciones
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    id_animal,
                    self.entry_fecha.get(),
                    float(self.entry_precio.get()),
                    self.combo_motivo.get() or None,
                    self.combo_destino.get() or None,
                    self.text_observaciones.get("1.0", "end-1c").strip() or None
                ))

                # Actualizar estado del animal
                cursor.execute("""
                    UPDATE animal SET estado = 'Vendido' WHERE id = ?
                """, (id_animal,))

                conn.commit()

            self.logger.info(f"Venta registrada para animal ID: {id_animal}")
            messagebox.showinfo("Éxito", "Venta registrada correctamente")
            self.limpiar_formulario()
            self.cargar_ventas()

        except Exception as e:
            self.logger.error(f"Error al guardar venta: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la venta:\n{e}")

    def cargar_ventas(self):
        """Carga las ventas en la tabla"""
        try:
            # Limpiar tabla
            for item in self.tabla_ventas.get_children():
                self.tabla_ventas.delete(item)

            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si la tabla existe
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='venta'
                """)
                if not cursor.fetchone():
                    self.logger.info("Tabla de ventas no existe aún")
                    return
                
                cursor.execute("""
                    SELECT 
                        v.id,
                        v.fecha,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        v.precio_total,
                        v.motivo_venta,
                        v.destino_venta,
                        v.observaciones
                    FROM venta v
                    JOIN animal a ON v.animal_id = a.id
                    ORDER BY v.fecha DESC
                    LIMIT 100
                """)

                ventas = cursor.fetchall()
                for row in ventas:
                    precio = f"${row[3]:,.0f}" if row[3] else "$0"
                    observaciones = row[6] or "-"
                    if len(observaciones) > 30:
                        observaciones = observaciones[:27] + "..."
                        
                    self.tabla_ventas.insert("", "end", values=(
                        row[0], row[1], row[2], precio, 
                        row[4] or "-", row[5] or "-", observaciones
                    ))

                self.logger.info(f"Cargadas {len(ventas)} ventas en el historial")

        except Exception as e:
            self.logger.error(f"Error al cargar ventas: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar las ventas:\n{e}")

    def aplicar_filtros(self):
        """Aplica filtros al historial de ventas"""
        try:
            mes_seleccionado = self.filtro_mes.get()
            # Limpiar tabla
            for item in self.tabla_ventas.get_children():
                self.tabla_ventas.delete(item)

            with get_db_connection() as conn:
                cursor = conn.cursor()

                base_query = """
                    SELECT 
                        v.id,
                        v.fecha,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        v.precio_total,
                        v.motivo_venta,
                        v.destino_venta,
                        v.observaciones
                    FROM venta v
                    JOIN animal a ON v.animal_id = a.id
                """

                params = []
                if mes_seleccionado and mes_seleccionado != "Todos":
                    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
                    numero_mes = meses.index(mes_seleccionado) + 1
                    base_query += " WHERE strftime('%m', v.fecha) = ?"
                    params.append(f"{numero_mes:02d}")

                base_query += " ORDER BY v.fecha DESC LIMIT 200"

                cursor.execute(base_query, params)
                ventas = cursor.fetchall()

                for row in ventas:
                    precio = f"${row[3]:,.0f}" if row[3] else "$0"
                    observaciones = row[6] or "-"
                    if len(observaciones) > 30:
                        observaciones = observaciones[:27] + "..."
                    self.tabla_ventas.insert("", "end", values=(
                        row[0], row[1], row[2], precio,
                        row[4] or "-", row[5] or "-", observaciones
                    ))

                self.logger.info(f"Filtro aplicado. Ventas mostradas: {len(ventas)}")
        except Exception as e:
            self.logger.error(f"Error aplicando filtros: {e}")
            messagebox.showerror("Error", f"No se pudo aplicar el filtro:\n{e}")

    def limpiar_formulario(self):
        """Limpia los campos del formulario de venta"""
        try:
            self.combo_animal.set("")
            self.entry_fecha.delete(0, "end")
            self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.entry_precio.delete(0, "end")
            self.combo_motivo.set("")
            self.combo_destino.set("")
            self.text_observaciones.delete("1.0", "end")
            self.logger.info("Formulario de venta limpiado")
        except Exception as e:
            self.logger.warning(f"Error limpiando formulario: {e}")

    def mostrar_estadisticas(self):
        """Muestra estadísticas rápidas de ventas"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*), COALESCE(SUM(precio_total),0) FROM venta")
                total_ventas, suma_precios = cursor.fetchone()

                cursor.execute("""
                    SELECT motivo_venta, COUNT(*) as c
                    FROM venta
                    WHERE motivo_venta IS NOT NULL AND motivo_venta <> ''
                    GROUP BY motivo_venta
                    ORDER BY c DESC
                    LIMIT 3
                """)
                top_motivos = cursor.fetchall()

                resumen_motivos = "".join([f"\n• {m[0]}: {m[1]}" for m in top_motivos]) or "\n(No hay motivos registrados)"

                mensaje = (
                    f"Total de ventas: {total_ventas}\n"
                    f"Ingresos acumulados: ${suma_precios:,.0f}\n"
                    f"Motivos más frecuentes:{resumen_motivos}"
                )
                messagebox.showinfo("Estadísticas de Ventas", mensaje)
                self.logger.info("Estadísticas de ventas mostradas")
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            messagebox.showerror("Error", f"No se pudieron obtener estadísticas:\n{e}")
