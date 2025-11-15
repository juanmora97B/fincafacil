import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

# Asegurar que el directorio padre esté en el path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class AjustesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        
        # Crear widgets
        self.crear_widgets()
        
        # Cargar ajustes existentes
        self.cargar_ajustes()

    def crear_widgets(self):
        """Crea la interfaz de usuario para los ajustes"""
        # Título principal
        titulo = ctk.CTkLabel(
            self, 
            text="⚙️ Ajustes del Sistema", 
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=20)

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Configuración", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Clave *:", width=100).pack(side="left", padx=5)
        self.entry_clave = ctk.CTkEntry(row1, width=200)
        self.entry_clave.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Valor *:", width=100).pack(side="left", padx=5)
        self.entry_valor = ctk.CTkEntry(row2, width=200)
        self.entry_valor.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Descripción:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_descripcion = ctk.CTkTextbox(row3, width=300, height=60)
        self.text_descripcion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones del formulario
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Ajuste", command=self.guardar_ajuste,
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="⚙️ Configuraciones Predefinidas", 
                     command=self.cargar_configuraciones_predefinidas).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(main_frame, text="📋 Configuraciones Registradas", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 5))

        # Frame de la tabla
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=10)

        # Crear tabla
        self.tabla = ttk.Treeview(table_frame, columns=("clave", "valor", "descripcion"), show="headings", height=12)
        
        # Configurar columnas
        column_config = [
            ("clave", "Clave", 150),
            ("valor", "Valor", 200),
            ("descripcion", "Descripción", 300)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)

        # Empacar tabla y scrollbar
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(pady=10)
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", 
                     command=self.editar_ajuste).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", 
                     command=self.eliminar_ajuste, fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", 
                     command=self.cargar_ajustes).pack(side="left", padx=5)

    def crear_tabla_configuracion(self):
        """Crea la tabla de configuración si no existe"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configuracion (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        clave TEXT UNIQUE NOT NULL,
                        valor TEXT NOT NULL,
                        descripcion TEXT,
                        categoria TEXT DEFAULT 'General',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        estado TEXT DEFAULT 'Activo'
                    )
                """)
                conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla de configuración:\n{e}")

    def guardar_ajuste(self):
        """Guarda un nuevo ajuste en la base de datos"""
        clave = self.entry_clave.get().strip()
        valor = self.entry_valor.get().strip()
        
        if not clave or not valor:
            messagebox.showwarning("Atención", "Clave y Valor son campos obligatorios.")
            return

        try:
            # Asegurar que la tabla existe
            self.crear_tabla_configuracion()
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO configuracion (clave, valor, descripcion)
                    VALUES (?, ?, ?)
                """, (
                    clave,
                    valor,
                    self.text_descripcion.get("1.0", "end-1c").strip()
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
            self.limpiar_formulario()
            self.cargar_ajustes()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe una configuración con esa clave.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{e}")

    def cargar_ajustes(self):
        """Carga los ajustes en la tabla"""
        # Asegurar que la tabla existe
        self.crear_tabla_configuracion()
        
        # Limpiar tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave, valor, descripcion 
                    FROM configuracion 
                    WHERE estado = 'Activo'
                    ORDER BY clave
                """)
                
                for fila in cursor.fetchall():
                    self.tabla.insert("", "end", values=fila)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las configuraciones:\n{e}")

    def editar_ajuste(self):
        """Edita el ajuste seleccionado"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una configuración para editar.")
            return

        clave = self.tabla.item(seleccionado[0])["values"][0]
        valor_actual = self.tabla.item(seleccionado[0])["values"][1]
        descripcion_actual = self.tabla.item(seleccionado[0])["values"][2]

        # Crear ventana de edición
        ventana_edicion = ctk.CTkToplevel(self)
        ventana_edicion.title(f"Editar Configuración: {clave}")
        ventana_edicion.geometry("500x400")
        ventana_edicion.transient(self)
        ventana_edicion.grab_set()

        # Formulario de edición
        form_frame = ctk.CTkFrame(ventana_edicion)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(form_frame, text=f"Editando: {clave}", 
                    font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Clave (solo lectura)
        ctk.CTkLabel(form_frame, text="Clave:").pack(anchor="w", pady=5)
        entry_clave = ctk.CTkEntry(form_frame, width=300)
        entry_clave.insert(0, clave)
        entry_clave.configure(state="disabled")
        entry_clave.pack(anchor="w", pady=5)

        # Valor
        ctk.CTkLabel(form_frame, text="Valor:").pack(anchor="w", pady=5)
        entry_valor = ctk.CTkEntry(form_frame, width=300)
        entry_valor.insert(0, valor_actual)
        entry_valor.pack(anchor="w", pady=5)

        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción:").pack(anchor="w", pady=5)
        text_descripcion = ctk.CTkTextbox(form_frame, width=300, height=100)
        text_descripcion.insert("1.0", descripcion_actual or "")
        text_descripcion.pack(anchor="w", pady=5)

        def guardar_cambios():
            nuevo_valor = entry_valor.get().strip()
            if not nuevo_valor:
                messagebox.showwarning("Atención", "El valor no puede estar vacío.")
                return

            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE configuracion 
                        SET valor = ?, descripcion = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                        WHERE clave = ?
                    """, (
                        nuevo_valor,
                        text_descripcion.get("1.0", "end-1c").strip(),
                        clave
                    ))
                    conn.commit()

                messagebox.showinfo("Éxito", "Configuración actualizada correctamente.")
                ventana_edicion.destroy()
                self.cargar_ajustes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la configuración:\n{e}")

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Cambios", 
                     command=guardar_cambios, fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="❌ Cancelar", 
                     command=ventana_edicion.destroy, fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)

    def eliminar_ajuste(self):
        """Elimina el ajuste seleccionado"""
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una configuración para eliminar.")
            return
        
        clave = self.tabla.item(seleccionado[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar la configuración '{clave}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE configuracion SET estado = 'Inactivo' WHERE clave = ?", (clave,))
                    conn.commit()
                
                messagebox.showinfo("Éxito", "Configuración eliminada.")
                self.cargar_ajustes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la configuración:\n{e}")

    def limpiar_formulario(self):
        """Limpia el formulario"""
        self.entry_clave.delete(0, "end")
        self.entry_valor.delete(0, "end")
        self.text_descripcion.delete("1.0", "end")

    def cargar_configuraciones_predefinidas(self):
        """Carga configuraciones predefinidas en el sistema"""
        configuraciones_predefinidas = [
            ("empresa_nombre", "FincaFácil", "Nombre de la empresa o finca"),
            ("empresa_telefono", "", "Teléfono de contacto de la empresa"),
            ("empresa_direccion", "", "Dirección de la empresa"),
            ("moneda_local", "COP", "Moneda local para transacciones"),
            ("formato_fecha", "YYYY-MM-DD", "Formato de fecha preferido"),
            ("idioma_sistema", "es", "Idioma del sistema"),
            ("backup_automatico", "1", "Realizar backup automático (1=Sí, 0=No)"),
            ("notificaciones_activas", "1", "Notificaciones activas (1=Sí, 0=No)"),
            ("registro_animal_auto", "1", "Registro automático de animales (1=Sí, 0=No)")
        ]

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                insertadas = 0
                actualizadas = 0

                for clave, valor, descripcion in configuraciones_predefinidas:
                    cursor.execute("SELECT COUNT(*) FROM configuracion WHERE clave = ?", (clave,))
                    existe = cursor.fetchone()[0] > 0

                    if existe:
                        cursor.execute("""
                            UPDATE configuracion 
                            SET valor = ?, descripcion = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                            WHERE clave = ?
                        """, (valor, descripcion, clave))
                        actualizadas += 1
                    else:
                        cursor.execute("""
                            INSERT INTO configuracion (clave, valor, descripcion, categoria)
                            VALUES (?, ?, ?, 'Sistema')
                        """, (clave, valor, descripcion))
                        insertadas += 1

                conn.commit()

            mensaje = f"Configuraciones predefinidas cargadas:\n"
            mensaje += f"• Nuevas: {insertadas}\n"
            mensaje += f"• Actualizadas: {actualizadas}"
            messagebox.showinfo("Configuraciones Predefinidas", mensaje)
            self.cargar_ajustes()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las configuraciones predefinidas:\n{e}")

    def obtener_configuracion(self, clave, valor_por_defecto=None):
        """Obtiene el valor de una configuración específica"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT valor FROM configuracion WHERE clave = ? AND estado = 'Activo'", (clave,))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else valor_por_defecto
        except Exception:
            return valor_por_defecto