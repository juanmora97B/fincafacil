import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class PotrerosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas_combobox()
        self.cargar_potreros()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="📍 Configuración de Potreros", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Potrero", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        self.widgets = {}
        
        # Finca
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Finca *:", width=120).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row1, width=300)
        self.combo_finca.pack(side="left", padx=5, fill="x", expand=True)

        # Nombre y Sector
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Nombre Potrero *:", width=120).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row2, width=140)
        self.entry_nombre.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Sector:", width=80).pack(side="left", padx=5)
        self.entry_sector = ctk.CTkEntry(row2, width=140)
        self.entry_sector.pack(side="left", padx=5)

        # Área y Capacidad
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Área (Hectáreas):", width=120).pack(side="left", padx=5)
        self.entry_area = ctk.CTkEntry(row3, width=140)
        self.entry_area.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Capacidad Máx:", width=100).pack(side="left", padx=5)
        self.entry_capacidad = ctk.CTkEntry(row3, width=140)
        self.entry_capacidad.pack(side="left", padx=5)

        # Pasto y Estado
        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Tipo de Pasto:", width=120).pack(side="left", padx=5)
        self.combo_pasto = ctk.CTkComboBox(row4, values=["Brachiaria", "Pangola", "Estrella", "Guinea", "Mixto", "Otro"], width=140)
        self.combo_pasto.set("Brachiaria")
        self.combo_pasto.pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="Estado:", width=80).pack(side="left", padx=5)
        self.combo_estado = ctk.CTkComboBox(row4, values=["Activo", "En Mantenimiento", "Inactivo"], width=140)
        self.combo_estado.set("Activo")
        self.combo_estado.pack(side="left", padx=5)

        # Descripción
        row5 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Descripción:", width=120).pack(side="left", padx=5, anchor="n")
        self.text_descripcion = ctk.CTkTextbox(row5, width=300, height=60)
        self.text_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Potrero", command=self.guardar_potrero, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(self, text="📋 Potreros Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("finca", "nombre", "sector", "area", "capacidad", "pasto", "estado"), show="headings", height=12)
        
        column_config = [
            ("finca", "Finca", 150),
            ("nombre", "Potrero", 120),
            ("sector", "Sector", 100),
            ("area", "Área (Ha)", 100),
            ("capacidad", "Capacidad", 100),
            ("pasto", "Pasto", 120),
            ("estado", "Estado", 100)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_potrero).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_potrero, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_potreros).pack(side="left", padx=5)

    def cargar_fincas_combobox(self):
        """Carga las fincas en el combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                self.combo_finca.configure(values=fincas)
                if fincas:
                    self.combo_finca.set(fincas[0])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def actualizar_potrero(self, id_finca, nombre_original):
        """Actualiza un potrero existente"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE potrero SET 
                        id_finca = ?,
                        nombre = ?,
                        sector = ?,
                        area_hectareas = ?,
                        capacidad_maxima = ?,
                        tipo_pasto = ?,
                        descripcion = ?,
                        estado = ?,
                        codigo = ?
                    WHERE id_finca = ? AND nombre = ?
                """, (
                    id_finca,
                    self.entry_nombre.get().strip(),
                    self.entry_sector.get().strip(),
                    float(self.entry_area.get() or 0),
                    int(self.entry_capacidad.get() or 0),
                    self.combo_pasto.get(),
                    self.text_descripcion.get("1.0", "end-1c").strip(),
                    self.combo_estado.get(),
                    f"{id_finca}-{self.entry_nombre.get().strip()}",
                    id_finca,
                    nombre_original
                ))
                conn.commit()
                return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el potrero:\n{e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el potrero:\n{e}")
            return False

    def guardar_potrero(self):
        """Guarda o actualiza un potrero"""
        if not self.combo_finca.get() or not self.entry_nombre.get().strip():
            messagebox.showwarning("Atención", "Finca y Nombre son campos obligatorios.")
            return

        try:
            id_finca = int(self.combo_finca.get().split("-")[0])
            nombre = self.entry_nombre.get().strip()
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existe el potrero
                cursor.execute("SELECT nombre FROM potrero WHERE id_finca = ? AND nombre = ?", 
                             (id_finca, nombre))
                existe = cursor.fetchone()
                
                if existe:
                    if messagebox.askyesno("Confirmar", "El potrero ya existe. ¿Desea actualizarlo?"):
                        if self.actualizar_potrero(id_finca, nombre):
                            messagebox.showinfo("Éxito", "Potrero actualizado correctamente.")
                            self.limpiar_formulario()
                            self.cargar_potreros()
                else:
                    # Generar código único para el potrero
                    codigo = f"{id_finca}-{nombre}"
                    cursor.execute("""
                        INSERT INTO potrero (codigo, id_finca, nombre, sector, area_hectareas, capacidad_maxima, 
                                            tipo_pasto, descripcion, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        codigo,
                        id_finca,
                        nombre,
                        self.entry_sector.get().strip(),
                        float(self.entry_area.get() or 0),
                        int(self.entry_capacidad.get() or 0),
                        self.combo_pasto.get(),
                        self.text_descripcion.get("1.0", "end-1c").strip(),
                        self.combo_estado.get()
                    ))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Potrero guardado correctamente.")
                    self.limpiar_formulario()
                    self.cargar_potreros()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el potrero:\n{e}")

    def cargar_potreros(self):
        """Carga los potreros en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT f.nombre as finca, p.nombre, p.sector, p.area_hectareas, 
                           p.capacidad_maxima, p.tipo_pasto, p.estado
                    FROM potrero p
                    JOIN finca f ON p.id_finca = f.id
                    WHERE p.estado = 'Activo'
                """)

                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los potreros:\n{e}")

    def editar_potrero(self):
        """Edita el potrero seleccionado"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un potrero para editar.")
            return
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                finca_nombre = self.tabla.item(seleccionado[0])["values"][0]  # nombre de la finca
                potrero_nombre = self.tabla.item(seleccionado[0])["values"][1]  # nombre del potrero
                
                # Obtener datos completos del potrero
                cursor.execute("""
                    SELECT p.*, f.nombre as finca_nombre 
                    FROM potrero p
                    JOIN finca f ON p.id_finca = f.id
                    WHERE p.nombre = ? AND f.nombre = ?
                """, (potrero_nombre, finca_nombre))
                potrero = cursor.fetchone()
                
                if not potrero:
                    messagebox.showerror("Error", "No se encontró el potrero")
                    return
                
                # Cargar datos en formulario
                cursor.execute("SELECT id, nombre FROM finca")
                fincas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                self.combo_finca.configure(values=fincas)
                finca_item = next((f for f in fincas if str(potrero["id_finca"]) in f), None)
                if finca_item:
                    self.combo_finca.set(finca_item)
                
                self.entry_nombre.delete(0, "end")
                self.entry_nombre.insert(0, potrero["nombre"])
                
                self.entry_sector.delete(0, "end")
                self.entry_sector.insert(0, potrero["sector"] or "")
                
                self.entry_area.delete(0, "end")
                self.entry_area.insert(0, str(potrero["area_hectareas"] or ""))
                
                self.entry_capacidad.delete(0, "end")
                self.entry_capacidad.insert(0, str(potrero["capacidad_maxima"] or ""))
                
                self.combo_pasto.set(potrero["tipo_pasto"] or "Brachiaria")
                self.combo_estado.set(potrero["estado"] or "Activo")
                
                self.text_descripcion.delete("1.0", "end")
                self.text_descripcion.insert("1.0", potrero["descripcion"] or "")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el potrero para editar:\n{e}")

    def eliminar_potrero(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un potrero para eliminar.")
            return
        
        nombre = self.tabla.item(seleccionado[0])["values"][1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el potrero '{nombre}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE potrero SET estado = 'Inactivo' WHERE nombre = ?", (nombre,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Potrero eliminado.")
                self.cargar_potreros()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, "end")
        self.entry_sector.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.entry_capacidad.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")
        self.combo_pasto.set("Brachiaria")
        self.combo_estado.set("Activo")
        
    def importar_excel(self):
        """Importar potreros desde un archivo Excel.
        Se esperan encabezados: finca,nombre,sector,area,capacidad,pasto,estado,descripcion
        """
        ruta = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls"), ("Todos los archivos", "*.*")])
        if not ruta:
            return

        filas, errores_parse = parse_excel_to_dicts(ruta)
        if errores_parse:
            messagebox.showerror("Error", "\n".join(errores_parse))
            return

        if not filas:
            messagebox.showinfo("Importar", "No se encontraron filas para importar.")
            return

        # Validar que existan columnas clave
        primera = filas[0]
        if 'finca' not in primera or 'nombre' not in primera:
            messagebox.showerror("Error", "El archivo debe tener columnas 'finca' y 'nombre'.")
            return

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener diccionario de fincas {nombre: id}
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas_dict = {row[1]: row[0] for row in cursor.fetchall()}

                for idx, fila in enumerate(filas, start=2):
                    nombre_finca = str(fila.get('finca') or "").strip()
                    nombre = str(fila.get('nombre') or "").strip()

                    if not nombre_finca or not nombre:
                        errores.append(f"Fila {idx}: falta finca o nombre")
                        continue

                    if nombre_finca not in fincas_dict:
                        errores.append(f"Fila {idx}: finca '{nombre_finca}' no encontrada o inactiva")
                        continue

                    try:
                        codigo = f"{fincas_dict[nombre_finca]}-{nombre}"
                        cursor.execute("""
                            INSERT INTO potrero (codigo, id_finca, nombre, sector, area_hectareas, capacidad_animales, capacidad_maxima, 
                                tipo_pasto, estado, descripcion)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            fincas_dict[nombre_finca],
                            nombre,
                            str(fila.get('sector') or "").strip() or None,
                            float(fila.get('area') or 0),
                            int(fila.get('capacidad') or 0),
                            int(fila.get('capacidad') or 0),
                            str(fila.get('pasto') or "Brachiaria").strip(),
                            str(fila.get('estado') or "Activo").strip(),
                            str(fila.get('descripcion') or "").strip() or None
                        ))
                        importados += 1
                    except sqlite3.IntegrityError:
                        errores.append(f"Fila {idx}: potrero duplicado para finca")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_potreros()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")