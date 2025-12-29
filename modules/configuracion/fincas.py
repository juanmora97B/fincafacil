import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from src.database import get_connection


def mapear_columnas_flexibles(registro, destinos, variantes_dict):
    """
    Mapea columnas con soporte para variantes.
    variantes_dict: {destino: [lista_variantes]}
    """
    for destino, variantes in variantes_dict.items():
        if destino in registro:
            continue
        for variante in variantes:
            if variante in registro:
                registro[destino] = registro.get(variante)
                break


class FincasFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._finca_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_fincas()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="🏠 Configuración de Fincas", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Finca", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Nombre *:", width=100).pack(side="left", padx=5)
        self.entry_nombre = ctk.CTkEntry(row1, width=200)
        self.entry_nombre.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Área (ha):", width=100).pack(side="left", padx=5)
        self.entry_area = ctk.CTkEntry(row2, width=150)
        self.entry_area.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Ubicación:", width=100).pack(side="left", padx=5)
        self.entry_ubicacion = ctk.CTkEntry(row2, width=200)
        self.entry_ubicacion.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Propietario:", width=100).pack(side="left", padx=5)
        self.entry_propietario = ctk.CTkEntry(row3, width=200)
        self.entry_propietario.pack(side="left", padx=5)

        row4 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row4, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Finca", command=self.guardar_finca, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Fincas Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombre", "area", "ubicacion", "propietario"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 120),
            ("nombre", "Nombre", 200),
            ("area", "Área (ha)", 100),
            ("ubicacion", "Ubicación", 200),
            ("propietario", "Propietario", 200)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_finca).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_finca, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_fincas).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_finca)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_finca)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_fincas)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_finca())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_finca(self):
        """Guarda una nueva finca o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        
        if not codigo or not nombre:
            messagebox.showwarning("Atención", "Código y Nombre son campos obligatorios.")
            return

        try:
            area_str = self.entry_area.get().strip()
            area = float(area_str) if area_str else 0.0
            ubicacion = self.entry_ubicacion.get().strip()
            propietario = self.entry_propietario.get().strip()
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                if self._finca_editando_codigo:
                    # Modo edición
                    cursor.execute("""
                        UPDATE finca 
                        SET nombre=?, area=?, ubicacion=?, propietario=?, comentario=?, estado='Activo'
                        WHERE codigo=? AND estado IN ('Activo', 'Inactivo')
                    """, (nombre, area, ubicacion, propietario, comentario, self._finca_editando_codigo))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Finca actualizada correctamente.")
                else:
                    # Modo creación
                    cursor.execute("""
                        INSERT INTO finca (codigo, nombre, area, ubicacion, propietario, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, 'Activo')
                    """, (codigo, nombre, area, ubicacion, propietario, comentario))
                    conn.commit()
                    messagebox.showinfo("Éxito", "Finca guardada correctamente.")
            
            self.limpiar_formulario()
            self.cargar_fincas()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", f"Área debe ser un número válido: {e}")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El código de finca ya existe.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la finca:\n{e}")

    def cargar_fincas(self):
        """Carga las fincas en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, area, ubicacion, propietario FROM finca WHERE estado='Activo'")
                
                for row in cursor.fetchall():
                    self.tabla.insert("", "end", values=row)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def editar_finca(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, area, ubicacion, propietario, comentario FROM finca WHERE codigo=?", (codigo,))
                finca = cursor.fetchone()
            
            if not finca:
                messagebox.showerror("Error", "No se pudo obtener la finca.")
                return
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, finca[0])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, finca[1])
            
            self.entry_area.delete(0, "end")
            self.entry_area.insert(0, str(finca[2]) if finca[2] else "")
            
            self.entry_ubicacion.delete(0, "end")
            self.entry_ubicacion.insert(0, finca[3] or "")
            
            self.entry_propietario.delete(0, "end")
            self.entry_propietario.insert(0, finca[4] or "")
            
            self.text_comentario.delete("1.0", "end")
            if finca[5]:
                self.text_comentario.insert("1.0", finca[5])
            
            # Tracking para saber que estamos editando
            self._finca_editando_codigo = codigo
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la finca:\n{e}")

    def eliminar_finca(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una finca para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactiva la finca '{codigo}'?\n\nPodrá reactivarla desde la base de datos."):
            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE finca SET estado='Inactivo' WHERE codigo=?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Finca marcada como inactiva.")
                self.cargar_fincas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.entry_ubicacion.delete(0, "end")
        self.entry_propietario.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self._finca_editando_codigo = None
        
    def importar_excel(self):
        """Importar fincas desde un archivo Excel.
        Se esperan encabezados: codigo,nombre,area,ubicacion,propietario,comentario
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

        # Validar y adaptar columnas
        variantes = {
            'codigo': ['codigo', 'codigos', 'código'],
            'nombre': ['nombre', 'nomb', 'razon_social', 'razón_social'],
            'area': ['area', 'área', 'hectareas', 'hectáreas', 'ha'],
            'ubicacion': ['ubicacion', 'ubicación', 'localidad', 'municipio'],
            'propietario': ['propietario', 'propietaria', 'dueño', 'dueña'],
        }

        for fila in filas:
            mapear_columnas_flexibles(fila, [], variantes)

        primera = filas[0]
        if 'codigo' not in primera or 'nombre' not in primera:
            messagebox.showerror(
                "Error",
                "El archivo debe contener encabezados equivalentes a: codigo, nombre.\n"
                "Variantes aceptadas: codigos/código, nomb/razon_social.\n"
                "Los campos area, ubicación, propietario, comentario son opcionales."
            )
            return

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            nombre = str(fila.get('nombre') or "").strip()
            area_str = str(fila.get('area') or "").strip()
            ubicacion = str(fila.get('ubicacion') or "").strip()
            propietario = str(fila.get('propietario') or "").strip()
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not nombre:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, nombre)")
                continue

            try:
                area = float(area_str) if area_str else 0.0
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO finca (codigo, nombre, area, ubicacion, propietario, comentario, estado)
                        VALUES (?, ?, ?, ?, ?, ?, 'Activo')
                    """, (codigo, nombre, area, ubicacion, propietario, comentario))
                    conn.commit()
                importados += 1
            except ValueError:
                errores.append(f"Fila {idx}: área debe ser un número válido")
            except sqlite3.IntegrityError:
                errores.append(f"Fila {idx}: el código '{codigo}' ya existe")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_fincas()
