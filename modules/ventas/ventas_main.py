import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class VentasModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_ventas()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="💰 Gestión de Ventas",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=15)

        # Frame principal con tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

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
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            form_frame,
            text="📝 Registrar Nueva Venta",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Campos del formulario
        campos_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        campos_frame.pack(fill="x", pady=10)

        # Animal
        row1 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Animal *:", width=150).pack(side="left", padx=5)
        self.combo_animal = ctk.CTkComboBox(row1, width=300)
        self.combo_animal.pack(side="left", padx=5, fill="x", expand=True)

        # Fecha
        row2 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Fecha Venta *:", width=150).pack(side="left", padx=5)
        self.entry_fecha = ctk.CTkEntry(row2, width=300)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side="left", padx=5, fill="x", expand=True)

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
        self.combo_motivo.pack(side="left", padx=5, fill="x", expand=True)

        # Destino
        row5 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Destino Venta:", width=150).pack(side="left", padx=5)
        self.combo_destino = ctk.CTkComboBox(row5, width=300)
        self.combo_destino.pack(side="left", padx=5, fill="x", expand=True)

        # Observaciones
        row6 = ctk.CTkFrame(campos_frame, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        ctk.CTkLabel(row6, text="Observaciones:", width=150).pack(side="left", padx=5, anchor="n")
        self.text_observaciones = ctk.CTkTextbox(row6, width=300, height=80)
        self.text_observaciones.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
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
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            table_frame,
            text="📋 Historial de Ventas",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        # Tabla
        self.tabla_ventas = ttk.Treeview(
            table_frame,
            columns=("fecha", "animal", "precio", "motivo", "destino"),
            show="headings",
            height=15
        )

        columnas = [
            ("fecha", "Fecha", 120),
            ("animal", "Animal", 150),
            ("precio", "Precio", 120),
            ("motivo", "Motivo", 150),
            ("destino", "Destino", 150)
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

    def cargar_combos(self):
        """Carga los datos en los combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Animales activos
                cursor.execute("""
                    SELECT codigo || ' - ' || COALESCE(nombre, 'Sin nombre')
                    FROM animal
                    WHERE estado = 'Activo'
                    ORDER BY codigo
                """)
                animales = [row[0] for row in cursor.fetchall()]
                self.combo_animal.configure(values=animales)

                # Motivos de venta
                cursor.execute("SELECT descripcion FROM motivo_venta WHERE estado = 'Activo'")
                motivos = [row[0] for row in cursor.fetchall()]
                self.combo_motivo.configure(values=motivos)

                # Destinos de venta (intentar ambos nombres de tabla)
                try:
                    cursor.execute("SELECT descripcion FROM destino_venta WHERE estado = 'Activo'")
                    destinos = [row[0] for row in cursor.fetchall()]
                except:
                    try:
                        cursor.execute("SELECT descripcion FROM destino_venta WHERE estado = 'Activo'")
                        destinos = [row[0] for row in cursor.fetchall()]
                    except:
                        destinos = []
                self.combo_destino.configure(values=destinos)

        except Exception as e:
            print(f"Error al cargar combos: {e}")

    def guardar_venta(self):
        """Guarda una nueva venta"""
        if not self.combo_animal.get() or not self.entry_fecha.get() or not self.entry_precio.get():
            messagebox.showwarning("Atención", "Complete los campos obligatorios (*)")
            return

        try:
            codigo_animal = self.combo_animal.get().split(" - ")[0]
            
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Obtener ID del animal
                cursor.execute("SELECT id FROM animal WHERE codigo = ?", (codigo_animal,))
                animal_row = cursor.fetchone()
                if not animal_row:
                    messagebox.showerror("Error", "Animal no encontrado")
                    return
                
                id_animal = animal_row[0]

                # Insertar venta
                try:
                    cursor.execute("""
                        INSERT INTO venta (
                            id_animal, fecha, precio_total, motivo_venta, 
                            destino_venta, observaciones, fecha_registro
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_animal,
                        self.entry_fecha.get(),
                        float(self.entry_precio.get()),
                        self.combo_motivo.get() or None,
                        self.combo_destino.get() or None,
                        self.text_observaciones.get("1.0", "end-1c").strip() or None,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                except sqlite3.OperationalError as e:
                    # Si la tabla no existe, crearla
                    if "no such table" in str(e).lower():
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS venta (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                id_animal INTEGER NOT NULL,
                                fecha TEXT NOT NULL,
                                precio_total REAL NOT NULL,
                                motivo_venta TEXT,
                                destino_venta TEXT,
                                observaciones TEXT,
                                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (id_animal) REFERENCES animales (id)
                            )
                        """)
                        # Reintentar insertar
                        cursor.execute("""
                            INSERT INTO venta (
                                id_animal, fecha, precio_total, motivo_venta, 
                                destino_venta, observaciones, fecha_registro
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            id_animal,
                            self.entry_fecha.get(),
                            float(self.entry_precio.get()),
                            self.combo_motivo.get() or None,
                            self.combo_destino.get() or None,
                            self.text_observaciones.get("1.0", "end-1c").strip() or None,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))
                    else:
                        raise

                # Actualizar estado del animal
                cursor.execute("""
                    UPDATE animal SET estado = 'Vendido' WHERE id = ?
                """, (id_animal,))

                conn.commit()

            messagebox.showinfo("Éxito", "Venta registrada correctamente")
            self.limpiar_formulario()
            self.cargar_ventas()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la venta:\n{e}")

    def cargar_ventas(self):
        """Carga las ventas en la tabla"""
        # Limpiar tabla
        for item in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(item)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        v.fecha,
                        a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                        v.precio_total,
                        v.motivo_venta,
                        v.destino_venta
                    FROM venta v
                    JOIN animal a ON v.id_animal = a.id
                    ORDER BY v.fecha DESC
                    LIMIT 100
                """)

                for row in cursor.fetchall():
                    precio = f"${row[2]:,.0f}" if row[2] else "$0"
                    self.tabla_ventas.insert("", "end", values=(
                        row[0], row[1], precio, row[3] or "-", row[4] or "-"
                    ))

        except Exception as e:
            # Si la tabla no existe, solo mostrar mensaje
            if "no such table" in str(e).lower():
                pass  # La tabla se creará en la base de datos
            else:
                print(f"Error al cargar ventas: {e}")

    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.combo_animal.set("")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_precio.delete(0, "end")
        self.combo_motivo.set("")
        self.combo_destino.set("")
        self.text_observaciones.delete("1.0", "end")

