import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog, Menu
from typing import Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from modules.utils.importador_excel import parse_excel_to_dicts
from infraestructura.configuracion.configuracion_service import ConfiguracionService
from infraestructura.configuracion.configuracion_repository import ConfiguracionRepository


class CausaMuerteFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._service = ConfiguracionService()
        self._repo = ConfiguracionRepository()
        self._causa_editando_codigo: Optional[str] = None
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_causas_muerte()

    def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container, text="☠️ Configuración de Causas de Muerte", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text="📝 Nueva Causa de Muerte", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Campos del formulario
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=100).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="Descripción *:", width=100).pack(side="left", padx=5)
        self.entry_descripcion = ctk.CTkEntry(row1, width=200)
        self.entry_descripcion.pack(side="left", padx=5)

        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Tipo:", width=100).pack(side="left", padx=5)
        self.combo_tipo = ctk.CTkComboBox(row2, 
            values=["Enfermedad", "Accidente", "Natural", "Sacrificio", "Depredación", "Otros"],
            width=150)
        self.combo_tipo.set("Enfermedad")
        self.combo_tipo.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Comentario:", width=100).pack(side="left", padx=5, anchor="n")
        self.text_comentario = ctk.CTkTextbox(row3, width=300, height=60)
        self.text_comentario.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar Causa", command=self.guardar_causa_muerte, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Separador
        ctk.CTkLabel(scroll_container, text="📋 Causas de Muerte Registradas", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(scroll_container)
        table_frame.pack(fill="both", expand=True, padx=4, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "descripcion", "tipo", "comentario"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 150),
            ("descripcion", "Descripción", 300),
            ("tipo", "Tipo", 150),
            ("comentario", "Comentario", 350)
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

        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_causa_muerte).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_causa_muerte, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_causas_muerte).pack(side="left", padx=5)

        # Menú contextual (clic derecho)
        self.menu_contextual = Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="✏️ Editar", command=self.editar_causa_muerte)
        self.menu_contextual.add_command(label="🗑️ Eliminar", command=self.eliminar_causa_muerte)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="🔄 Actualizar", command=self.cargar_causas_muerte)
        
        # Vincular eventos de la tabla
        self.tabla.bind("<Button-3>", self.mostrar_menu_contextual)
        self.tabla.bind("<Double-1>", lambda e: self.editar_causa_muerte())

    def mostrar_menu_contextual(self, event):
        try:
            row_id = self.tabla.identify_row(event.y)
            if row_id:
                self.tabla.selection_set(row_id)
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
        
    def guardar_causa_muerte(self):
        """Guarda una nueva causa de muerte o actualiza si está en modo edición"""
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_descripcion.get().strip()
        
        if not codigo or not descripcion:
            messagebox.showwarning("Atención", "Código y Descripción son campos obligatorios.")
            return

        try:
            tipo = self.combo_tipo.get()
            comentario = self.text_comentario.get("1.0", "end-1c").strip()
            
            if self._causa_editando_codigo:
                # Modo edición
                self._repo.actualizar_causa_muerte(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_causa=tipo,
                    comentario=comentario
                )
                messagebox.showinfo("Éxito", "Causa de muerte actualizada correctamente.")
            else:
                # Modo creación
                self._repo.crear_causa_muerte(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_causa=tipo,
                    comentario=comentario,
                    estado="Activo"
                )
                messagebox.showinfo("Éxito", "Causa de muerte guardada correctamente.")
            
            self.limpiar_formulario()
            self.cargar_causas_muerte()
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la causa:\n{e}")

    def cargar_causas_muerte(self):
        """Carga las causas de muerte en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            causas = self._repo.listar_causas_muerte()
            for causa in causas:
                valores = (
                    causa.get('codigo', ''),
                    causa.get('descripcion', ''),
                    causa.get('tipo', ''),
                    causa.get('comentario', '')
                )
                self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las causas:\n{e}")

    def editar_causa_muerte(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una causa para editar.")
            return
        
        valores = self.tabla.item(seleccionado[0])["values"]
        codigo = valores[0]
        
        try:
            causa = self._repo.obtener_causa_muerte(codigo)
            if not causa:
                messagebox.showerror("Error", "No se encontró la causa de muerte")
                return
            
            # Cargar en formulario (inline editing)
            self.entry_codigo.delete(0, "end")
            self.entry_codigo.insert(0, causa['codigo'])
            self.entry_codigo.configure(state="disabled")
            
            self.entry_descripcion.delete(0, "end")
            self.entry_descripcion.insert(0, causa['descripcion'])
            
            self.combo_tipo.set(causa.get('tipo_causa', 'Enfermedad'))
            
            self.text_comentario.delete("1.0", "end")
            if causa.get('comentario'):
                self.text_comentario.insert("1.0", causa['comentario'])
            
            # Tracking para saber que estamos editando
            self._causa_editando_codigo = codigo
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la causa:\n{e}")

    def eliminar_causa_muerte(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione una causa para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Marcar como inactiva la causa '{codigo}'?\n\nPodrá reactivarla desde la base de datos."):
            try:
                self._repo.cambiar_estado_causa_muerte(codigo, 'Inactivo')
                messagebox.showinfo("Éxito", "Causa marcada como inactiva.")
                self.cargar_causas_muerte()
            except ValueError as e:
                messagebox.showerror("Error de Validación", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado:\n{e}")

    def limpiar_formulario(self):
        self.entry_codigo.configure(state="normal")
        self.entry_codigo.delete(0, "end")
        self.entry_descripcion.delete(0, "end")
        self.text_comentario.delete("1.0", "end")
        self.combo_tipo.set("Enfermedad")
        self._causa_editando_codigo = None
        
    def importar_excel(self):
        """Importar causas de muerte desde un archivo Excel."""
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

        importados = 0
        errores = []

        for idx, fila in enumerate(filas, start=2):
            codigo = str(fila.get('codigo') or "").strip()
            descripcion = str(fila.get('descripcion') or "").strip()
            tipo = str(fila.get('tipo') or "Enfermedad").strip()
            comentario = str(fila.get('comentario') or "").strip()

            if not codigo or not descripcion:
                errores.append(f"Fila {idx}: faltan campos requeridos (código, descripción)")
                continue

            try:
                self._repo.crear_causa_muerte(
                    codigo=codigo,
                    descripcion=descripcion,
                    tipo_causa=tipo,
                    comentario=comentario,
                    estado="Activo"
                )
                importados += 1
            except ValueError as e:
                errores.append(f"Fila {idx}: {str(e)}")
            except Exception as e:
                errores.append(f"Fila {idx}: {str(e)}")

        mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
        if errores:
            mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación", mensaje)
        self.cargar_causas_muerte()
