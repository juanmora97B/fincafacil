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
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="📍 Configuración de Potreros", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nuevo Potrero", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        self.widgets = {}
        
        # Finca
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Finca *:", width=120).pack(side="left", padx=5)
        self.combo_finca = ctk.CTkComboBox(row1, width=300, command=self.on_finca_seleccionada)
        self.combo_finca.pack(side="left", padx=5, fill="x", expand=True)

        # Nombre y Sector
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Nombre Potrero *:", width=120).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row2, width=140)
        self.entry_nombre.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Sector:", width=80).pack(side="left", padx=5)
        self.combo_sector = ctk.CTkComboBox(row2, width=140, values=["Sin Sector"])
        self.combo_sector.set("Sin Sector")
        self.combo_sector.pack(side="left", padx=5)
        
        # Mapa para sectores {nombre: id}
        self._sector_map = {}

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
        ctk.CTkLabel(scroll_container, text="📋 Potreros Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=4)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla (incluir columna id oculta para búsqueda confiable)
        self.tabla = ttk.Treeview(table_frame, 
                                  columns=("id", "finca", "nombre", "sector", "area", "capacidad", "pasto", "estado"), 
                                  show="headings", 
                                  displaycolumns=("finca", "nombre", "sector", "area", "capacidad", "pasto", "estado"),  # Ocultar id
                                  height=12)
        
        column_config = [
            ("id", "ID", 50),  # Oculto pero necesario
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
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
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
                rows = cursor.fetchall()
                # Mapa interno nombre->id (en minúsculas para búsqueda robusta)
                self._finca_map = {str(r[1]).strip(): int(r[0]) for r in rows if r[1] is not None}
                nombres = list(self._finca_map.keys())
                self.combo_finca.configure(values=nombres)
                if nombres:
                    self.combo_finca.set(nombres[0])
                    self.on_finca_seleccionada(nombres[0])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def on_finca_seleccionada(self, nombre_finca):
        """Carga los sectores de la finca seleccionada"""
        finca_id = self._finca_map.get(nombre_finca)
        if not finca_id:
            return
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, nombre FROM sector 
                    WHERE finca_id = ? AND (estado = 'Activo' OR estado = 'Activa')
                    ORDER BY nombre
                """, (finca_id,))
                rows = cursor.fetchall()
                
                # Mapa interno nombre->id para sectores
                self._sector_map = {str(r[1]).strip(): int(r[0]) for r in rows if r[1] is not None}
                nombres_sectores = ["Sin Sector"] + list(self._sector_map.keys())
                
                self.combo_sector.configure(values=nombres_sectores)
                self.combo_sector.set("Sin Sector")
        except Exception as e:
            print(f"Error cargando sectores: {e}")

    def actualizar_potrero(self, id_finca, nombre_original):
        """Actualiza un potrero existente"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # Obtener id_sector del combo
                sector_seleccionado = self.combo_sector.get().strip()
                id_sector = self._sector_map.get(sector_seleccionado) if sector_seleccionado != "Sin Sector" else None
                
                cursor.execute("""
                    UPDATE potrero SET 
                        id_finca = ?,
                        nombre = ?,
                        id_sector = ?,
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
                    id_sector,
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
            # Obtener id_finca desde el mapa interno usando el nombre seleccionado
            nombre_finca_sel = self.combo_finca.get().strip()
            id_finca = self._finca_map.get(nombre_finca_sel)
            if not id_finca:
                messagebox.showwarning("Atención", "La finca seleccionada no es válida.")
                return
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
                    
                    # Obtener id_sector del mapa
                    sector_seleccionado = self.combo_sector.get().strip()
                    id_sector = self._sector_map.get(sector_seleccionado) if sector_seleccionado != "Sin Sector" else None
                    
                    cursor.execute("""
                        INSERT INTO potrero (codigo, id_finca, nombre, id_sector, area_hectareas, capacidad_maxima, 
                                            tipo_pasto, descripcion, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        codigo,
                        id_finca,
                        nombre,
                        id_sector,
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
                    SELECT p.id, f.nombre as finca, p.nombre, s.nombre as sector, p.area_hectareas, 
                           p.capacidad_maxima, p.tipo_pasto, p.estado
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN sector s ON p.id_sector = s.id
                    WHERE p.estado = 'Activo'
                """)

                for fila in cursor.fetchall():
                    # Convertir explícitamente cada valor a string para evitar problemas de serialización
                    valores = (
                        str(fila[0]) if fila[0] is not None else "",  # id
                        str(fila[1]) if fila[1] is not None else "Sin Finca",  # finca
                        str(fila[2]) if fila[2] is not None else "",  # nombre
                        str(fila[3]) if fila[3] is not None else "Sin Sector",  # sector
                        str(fila[4]) if fila[4] is not None else "0",  # area
                        str(fila[5]) if fila[5] is not None else "0",  # capacidad
                        str(fila[6]) if fila[6] is not None else "",  # pasto
                        str(fila[7]) if fila[7] is not None else ""   # estado
                    )
                    self.tabla.insert("", "end", values=valores)
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
                potrero_id = self.tabla.item(seleccionado[0])["values"][0]  # ID del potrero
                
                # Obtener datos completos del potrero usando el ID
                cursor.execute("""
                    SELECT p.*, f.nombre as finca_nombre 
                    FROM potrero p
                    JOIN finca f ON p.id_finca = f.id
                    WHERE p.id = ?
                """, (potrero_id,))
                potrero = cursor.fetchone()
                
                if not potrero:
                    messagebox.showerror("Error", "No se encontró el potrero")
                    return
                
                # Cargar datos en formulario
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                rows = cursor.fetchall()
                self._finca_map = {str(r[1]).strip(): int(r[0]) for r in rows if r[1] is not None}
                nombres = list(self._finca_map.keys())
                self.combo_finca.configure(values=nombres)
                # Establecer seleccionado por id_finca
                nombre_sel = next((n for n, fid in self._finca_map.items() if fid == potrero["id_finca"]), None)
                if nombre_sel:
                    self.combo_finca.set(nombre_sel)
                
                self.entry_nombre.delete(0, "end")
                self.entry_nombre.insert(0, potrero["nombre"])
                
                # Cargar sectores de la finca y establecer el seleccionado
                self.on_finca_seleccionada(nombre_sel)
                # sqlite3.Row no implementa .get(), usamos acceso directo y comprobación explícita
                potrero_id_sector = potrero["id_sector"] if "id_sector" in potrero.keys() else None
                if potrero_id_sector:
                    # Buscar nombre del sector por id
                    sector_nombre = next((n for n, sid in self._sector_map.items() if sid == potrero_id_sector), "Sin Sector")
                    self.combo_sector.set(sector_nombre)
                else:
                    self.combo_sector.set("Sin Sector")
                
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
        # Usar ID de potrero para eliminar de forma segura
        potrero_id = self.tabla.item(seleccionado[0])["values"][0]
        nombre = self.tabla.item(seleccionado[0])["values"][2]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el potrero '{nombre}'?\n\nEsta acción no se puede deshacer."):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM potrero WHERE id = ?", (potrero_id,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Potrero eliminado correctamente.")
                self.cargar_potreros()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self):
        self.entry_nombre.delete(0, "end")
        self.combo_sector.set("Sin Sector")
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
                cursor.execute("SELECT id, nombre FROM finca")
                fincas_dict = {}
                for row in cursor.fetchall():
                    finca_id = row[0]
                    finca_nombre = str(row[1]).strip().lower() if row[1] else ""
                    fincas_dict[finca_nombre] = finca_id

                for idx, fila in enumerate(filas, start=2):
                    nombre_finca_raw = str(fila.get('finca') or "").strip()
                    nombre = str(fila.get('nombre') or "").strip()

                    if not nombre_finca_raw or not nombre:
                        errores.append(f"Fila {idx}: falta finca o nombre")
                        continue

                    # Buscar finca por nombre (ignorando el formato "id-nombre")
                    nombre_finca_buscar = nombre_finca_raw.lower()
                    # Si tiene formato "4-finca el prado", extraer solo "finca el prado"
                    if '-' in nombre_finca_buscar:
                        partes = nombre_finca_buscar.split('-', 1)
                        if len(partes) == 2:
                            nombre_finca_buscar = partes[1].strip()
                    
                    if nombre_finca_buscar not in fincas_dict:
                        errores.append(f"Fila {idx}: finca '{nombre_finca_raw}' no encontrada")
                        continue
                    
                    id_finca = fincas_dict[nombre_finca_buscar]

                    try:
                        # Obtener código del Excel o generar uno
                        codigo = str(fila.get('codigo') or f"P{id_finca}-{idx}").strip()
                        
                        # Buscar id_sector si se proporciona nombre de sector
                        id_sector = None
                        sector_nombre = str(fila.get('sector') or "").strip()
                        if sector_nombre:
                            cursor.execute("SELECT id FROM sector WHERE LOWER(nombre) = LOWER(?) LIMIT 1", (sector_nombre,))
                            sector_row = cursor.fetchone()
                            if sector_row:
                                id_sector = sector_row[0]
                        
                        cursor.execute("""
                            INSERT INTO potrero (codigo, id_finca, nombre, id_sector, area_hectareas, capacidad_maxima, 
                                tipo_pasto, estado, descripcion)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            id_finca,
                            nombre,
                            id_sector,
                            float(fila.get('area_hectareas') or fila.get('area') or 0),
                            int(fila.get('capacidad_maxima') or fila.get('capacidad') or 0),
                            str(fila.get('tipo_pasto') or fila.get('pasto') or "").strip() or None,
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