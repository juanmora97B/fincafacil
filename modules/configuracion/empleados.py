import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.importador_excel import parse_excel_to_dicts


class EmpleadosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.foto_path = None
        self.crear_widgets()
        self.cargar_empleados()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(self, text="👨‍💼 Configuración de Empleados", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña Datos Principales
        self.tab_principal = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_principal, text="📋 Datos Principales")

        # Pestaña Asignaciones y Deducciones
        self.tab_salario = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_salario, text="💰 Salario y Deducciones")

        self.configurar_tab_principal()
        self.configurar_tab_salario()

        # Botones generales
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="💾 Guardar Empleado", command=self.guardar_empleado, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)

        # Tabla de empleados
        self.crear_tabla_empleados()

    def configurar_tab_principal(self):
        """Configura la pestaña de datos principales"""
        main_frame = ctk.CTkScrollableFrame(self.tab_principal)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # DATOS BÁSICOS
        frame_basicos = ctk.CTkFrame(main_frame)
        frame_basicos.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_basicos, text="📝 Datos Básicos", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Código y N° Identificación
        row1 = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Código *:", width=120).pack(side="left", padx=5)
        self.entry_codigo = ctk.CTkEntry(row1, width=150,)
        self.entry_codigo.pack(side="left", padx=5)
        ctk.CTkLabel(row1, text="N° Identificación *:", width=140).pack(side="left", padx=5)
        self.entry_identificacion = ctk.CTkEntry(row1, width=150,)
        self.entry_identificacion.pack(side="left", padx=5)

        # Nombres y Apellidos
        row2 = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Nombres *:", width=120).pack(side="left", padx=5)
        self.entry_nombres = ctk.CTkEntry(row2, width=200,)
        self.entry_nombres.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Apellidos *:", width=120).pack(side="left", padx=5)
        self.entry_apellidos = ctk.CTkEntry(row2, width=200,)
        self.entry_apellidos.pack(side="left", padx=5)

        # Cargo y Estado
        row3 = ctk.CTkFrame(frame_basicos, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Cargo *:", width=120).pack(side="left", padx=5)
        self.combo_cargo = ctk.CTkComboBox(row3, values=["Administrador", "Vaquero", "Ordeñador", "Veterinario", "Secretario", "Otro"], width=200)
        self.combo_cargo.set("Vaquero")
        self.combo_cargo.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Estado *:", width=100).pack(side="left", padx=5)
        self.combo_estado = ctk.CTkComboBox(row3, values=["Activo", "Inactivo", "Vacaciones", "Licencia"], width=150)
        self.combo_estado.set("Activo")
        self.combo_estado.pack(side="left", padx=5)

        # DATOS PERSONALES
        frame_personales = ctk.CTkFrame(main_frame)
        frame_personales.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_personales, text="👤 Datos Personales", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Sexo y Estado Civil
        row4 = ctk.CTkFrame(frame_personales, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Sexo:", width=120).pack(side="left", padx=5)
        self.combo_sexo = ctk.CTkComboBox(row4, values=["Masculino", "Femenino", "Otro"], width=150)
        self.combo_sexo.set("Masculino")
        self.combo_sexo.pack(side="left", padx=5)
        ctk.CTkLabel(row4, text="Estado Civil:", width=120).pack(side="left", padx=5)
        self.combo_estado_civil = ctk.CTkComboBox(row4, values=["Soltero", "Casado", "Unión Libre", "Divorciado", "Viudo"], width=150)
        self.combo_estado_civil.set("Soltero")
        self.combo_estado_civil.pack(side="left", padx=5)

        # Fechas importantes
        row5 = ctk.CTkFrame(frame_personales, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Fecha Nacimiento:", width=140).pack(side="left", padx=5)
        self.entry_fecha_nacimiento = ctk.CTkEntry(row5, width=150,)
        self.entry_fecha_nacimiento.pack(side="left", padx=5)
        ctk.CTkLabel(row5, text="Fecha Ingreso *:", width=120).pack(side="left", padx=5)
        self.entry_fecha_ingreso = ctk.CTkEntry(row5, width=150,)
        self.entry_fecha_ingreso.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_ingreso.pack(side="left", padx=5)

        # Fecha Contrato y Retiro
        row6 = ctk.CTkFrame(frame_personales, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        ctk.CTkLabel(row6, text="Fecha Contrato:", width=140).pack(side="left", padx=5)
        self.entry_fecha_contrato = ctk.CTkEntry(row6, width=150, )
        self.entry_fecha_contrato.pack(side="left", padx=5)
        ctk.CTkLabel(row6, text="Fecha Retiro:", width=120).pack(side="left", padx=5)
        self.entry_fecha_retiro = ctk.CTkEntry(row6, width=150,)
        self.entry_fecha_retiro.pack(side="left", padx=5)

        # CONTACTO
        frame_contacto = ctk.CTkFrame(main_frame)
        frame_contacto.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_contacto, text="📞 Información de Contacto", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Teléfono y Dirección
        row7 = ctk.CTkFrame(frame_contacto, fg_color="transparent")
        row7.pack(fill="x", pady=5)
        ctk.CTkLabel(row7, text="Teléfono:", width=120).pack(side="left", padx=5)
        self.entry_telefono = ctk.CTkEntry(row7, width=200,)
        self.entry_telefono.pack(side="left", padx=5)
        ctk.CTkLabel(row7, text="Dirección:", width=120).pack(side="left", padx=5)
        self.entry_direccion = ctk.CTkEntry(row7, width=200,)
        self.entry_direccion.pack(side="left", padx=5)

        # FOTO Y COMENTARIOS
        frame_adicional = ctk.CTkFrame(main_frame)
        frame_adicional.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_adicional, text="📷 Foto y Comentarios", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Foto
        row8 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row8.pack(fill="x", pady=5)
        ctk.CTkLabel(row8, text="Foto:", width=120).pack(side="left", padx=5)
        self.btn_foto = ctk.CTkButton(row8, text="📷 Cargar Foto", command=self.cargar_foto)
        self.btn_foto.pack(side="left", padx=5)
        self.label_foto = ctk.CTkLabel(row8, text="No hay foto seleccionada")
        self.label_foto.pack(side="left", padx=5)

        # Comentarios
        row9 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row9.pack(fill="x", pady=5)
        ctk.CTkLabel(row9, text="Comentarios:", width=120).pack(side="left", padx=5, anchor="n")
        self.text_comentarios = ctk.CTkTextbox(row9, width=400, height=80)
        self.text_comentarios.pack(side="left", padx=5, fill="x", expand=True)

    def configurar_tab_salario(self):
        """Configura la pestaña de salario y deducciones"""
        main_frame = ctk.CTkScrollableFrame(self.tab_salario)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # SALARIO BASE
        frame_salario = ctk.CTkFrame(main_frame)
        frame_salario.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_salario, text="💰 Salario Base", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        row1 = ctk.CTkFrame(frame_salario, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Salario Diario ($):", width=150).pack(side="left", padx=5)
        self.entry_salario_diario = ctk.CTkEntry(row1, width=200,)
        self.entry_salario_diario.pack(side="left", padx=5)

        # ASIGNACIONES
        frame_asignaciones = ctk.CTkFrame(main_frame)
        frame_asignaciones.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_asignaciones, text="📈 Asignaciones Adicionales", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        ctk.CTkLabel(frame_asignaciones, text="Bonos y adicionales al salario base", font=("Segoe UI", 12)).pack(anchor="w", pady=5)

        row2 = ctk.CTkFrame(frame_asignaciones, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Bono Alimenticio ($):", width=150).pack(side="left", padx=5)
        self.entry_bono_alimenticio = ctk.CTkEntry(row2, width=200,)
        self.entry_bono_alimenticio.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(frame_asignaciones, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Bono Productividad ($):", width=150).pack(side="left", padx=5)
        self.entry_bono_productividad = ctk.CTkEntry(row3, width=200,)
        self.entry_bono_productividad.pack(side="left", padx=5)

        # DEDUCCIONES
        frame_deducciones = ctk.CTkFrame(main_frame)
        frame_deducciones.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_deducciones, text="📉 Deducciones Obligatorias", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        ctk.CTkLabel(frame_deducciones, text="Deducciones según ley colombiana", font=("Segoe UI", 12)).pack(anchor="w", pady=5)

        row4 = ctk.CTkFrame(frame_deducciones, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Seguro Social (%):", width=150).pack(side="left", padx=5)
        self.entry_seguro_social = ctk.CTkEntry(row4, width=200,)
        self.entry_seguro_social.pack(side="left", padx=5)

        row5 = ctk.CTkFrame(frame_deducciones, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        ctk.CTkLabel(row5, text="Otras Deducciones ($):", width=150).pack(side="left", padx=5)
        self.entry_otras_deducciones = ctk.CTkEntry(row5, width=200,)
        self.entry_otras_deducciones.pack(side="left", padx=5)

        # RESUMEN
        frame_resumen = ctk.CTkFrame(main_frame)
        frame_resumen.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_resumen, text="🧮 Resumen Estimado", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        self.label_resumen = ctk.CTkLabel(frame_resumen, text="Complete los campos para ver el resumen", font=("Segoe UI", 12))
        self.label_resumen.pack(anchor="w", pady=5)

    def crear_tabla_empleados(self):
        """Crea la tabla de empleados registrados"""
        # Separador
        ctk.CTkLabel(self, text="📋 Empleados Registrados", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20,5), padx=20)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Tabla
        self.tabla = ttk.Treeview(table_frame, columns=("codigo", "nombres", "cargo", "estado", "salario", "fecha_ingreso"), show="headings", height=12)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombres", "Nombres", 200),
            ("cargo", "Cargo", 150),
            ("estado", "Estado", 100),
            ("salario", "Salario Diario", 120),
            ("fecha_ingreso", "Fecha Ingreso", 120)
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
        
        ctk.CTkButton(action_frame, text="✏️ Editar Seleccionado", command=self.editar_empleado).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Eliminar Seleccionado", command=self.eliminar_empleado, 
                     fg_color="red", hover_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🔄 Actualizar Lista", command=self.cargar_empleados).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📥 Importar Excel", command=self.importar_excel).pack(side="left", padx=5)

    def cargar_foto(self):
        """Carga una foto para el empleado"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto del empleado",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.foto_path = file_path
            self.label_foto.configure(text=f"Foto: {os.path.basename(file_path)}")

    def guardar_empleado(self):
        """Guarda un nuevo empleado"""
        # Validaciones básicas
        if not self.entry_codigo.get().strip() or not self.entry_identificacion.get().strip():
            messagebox.showwarning("Atención", "Código y N° Identificación son obligatorios.")
            return

        if not self.entry_nombres.get().strip() or not self.entry_apellidos.get().strip():
            messagebox.showwarning("Atención", "Nombres y Apellidos son obligatorios.")
            return

        if not self.entry_fecha_ingreso.get().strip():
            messagebox.showwarning("Atención", "Fecha de Ingreso es obligatoria.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO empleado (
                        codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                        fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                        sexo, estado_civil, telefono, direccion,
                        salario_diario, bono_alimenticio, bono_productividad,
                        seguro_social, otras_deducciones, foto_path, comentarios, estado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.entry_codigo.get().strip(),
                    self.entry_nombres.get().strip(),
                    self.entry_apellidos.get().strip(),
                    self.entry_identificacion.get().strip(),
                    self.combo_cargo.get(),
                    self.combo_estado.get(),
                    self.entry_fecha_ingreso.get().strip(),
                    self.entry_fecha_contrato.get().strip() or None,
                    self.entry_fecha_nacimiento.get().strip() or None,
                    self.entry_fecha_retiro.get().strip() or None,
                    self.combo_sexo.get(),
                    self.combo_estado_civil.get(),
                    self.entry_telefono.get().strip(),
                    self.entry_direccion.get().strip(),
                    float(self.entry_salario_diario.get() or 0),
                    float(self.entry_bono_alimenticio.get() or 0),
                    float(self.entry_bono_productividad.get() or 0),
                    float(self.entry_seguro_social.get() or 0),
                    float(self.entry_otras_deducciones.get() or 0),
                    self.foto_path,
                    self.text_comentarios.get("1.0", "end-1c").strip(),
                    "Activo"
                ))
                conn.commit()

            messagebox.showinfo("Éxito", "Empleado guardado correctamente.")
            self.limpiar_formulario()
            self.cargar_empleados()
            
        except sqlite3.IntegrityError as e:
            if "numero_identificacion" in str(e):
                messagebox.showerror("Error", "Ya existe un empleado con ese número de identificación.")
            else:
                messagebox.showerror("Error", "Ya existe un empleado con ese código.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el empleado:\n{e}")

    def cargar_empleados(self):
        """Carga los empleados en la tabla"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, nombres || ' ' || apellidos, cargo, estado_actual, 
                           salario_diario, fecha_ingreso
                    FROM empleado 
                    WHERE estado = 'Activo'
                    ORDER BY fecha_ingreso DESC
                """)
                
                for fila in cursor.fetchall():
                    salario = f"${fila[4]:,.0f}" if fila[4] else "No definido"
                    self.tabla.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], salario, fila[5]))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los empleados:\n{e}")

    def editar_empleado(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para editar.")
            return
        messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")

    def eliminar_empleado(self):
        seleccionado = self.tabla.selection()
        if not seleccionado:
            messagebox.showwarning("Atención", "Seleccione un empleado para eliminar.")
            return
        
        codigo = self.tabla.item(seleccionado[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el empleado '{codigo}'?"):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE empleado SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                    conn.commit()
                messagebox.showinfo("Éxito", "Empleado eliminado.")
                self.cargar_empleados()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def importar_excel(self):
        """Importar empleados desde Excel. Se esperan como mínimo: codigo,nombres,apellidos
        Se pueden incluir columnas opcionales que coincidan con los campos del formulario.
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

        primera = filas[0]
        if 'codigo' not in primera or 'nombres' not in primera or 'apellidos' not in primera:
            messagebox.showerror("Error", "El archivo debe tener al menos las columnas 'codigo', 'nombres' y 'apellidos'.")
            return

        def safe_float(val):
            try:
                return float(val)
            except Exception:
                return 0.0

        importados = 0
        errores = []

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                for idx, fila in enumerate(filas, start=2):
                    codigo = str(fila.get('codigo') or "").strip()
                    nombres = str(fila.get('nombres') or "").strip()
                    apellidos = str(fila.get('apellidos') or "").strip()

                    if not codigo or not nombres or not apellidos:
                        errores.append(f"Fila {idx}: faltan campos requeridos (codigo, nombres o apellidos)")
                        continue

                    try:
                        cursor.execute("SELECT COUNT(*) FROM empleado WHERE codigo = ? OR numero_identificacion = ?", (codigo, fila.get('numero_identificacion')))
                        if cursor.fetchone()[0] > 0:
                            errores.append(f"Fila {idx}: empleado con código o identificación ya existe")
                            continue

                        cursor.execute("""
                            INSERT INTO empleado (
                                codigo, nombres, apellidos, numero_identificacion, cargo, estado_actual,
                                fecha_ingreso, fecha_contrato, fecha_nacimiento, fecha_retiro,
                                sexo, estado_civil, telefono, direccion,
                                salario_diario, bono_alimenticio, bono_productividad,
                                seguro_social, otras_deducciones, foto_path, comentarios, estado
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombres,
                            apellidos,
                            str(fila.get('numero_identificacion') or "").strip() or None,
                            str(fila.get('cargo') or self.combo_cargo.get()).strip(),
                            str(fila.get('estado_actual') or self.combo_estado.get()).strip(),
                            str(fila.get('fecha_ingreso') or self.entry_fecha_ingreso.get()).strip() or None,
                            str(fila.get('fecha_contrato') or "").strip() or None,
                            str(fila.get('fecha_nacimiento') or "").strip() or None,
                            str(fila.get('fecha_retiro') or "").strip() or None,
                            str(fila.get('sexo') or self.combo_sexo.get()).strip(),
                            str(fila.get('estado_civil') or self.combo_estado_civil.get()).strip(),
                            str(fila.get('telefono') or "").strip() or None,
                            str(fila.get('direccion') or "").strip() or None,
                            safe_float(fila.get('salario_diario') or 0),
                            safe_float(fila.get('bono_alimenticio') or 0),
                            safe_float(fila.get('bono_productividad') or 0),
                            safe_float(fila.get('seguro_social') or 0),
                            safe_float(fila.get('otras_deducciones') or 0),
                            str(fila.get('foto_path') or "").strip() or None,
                            str(fila.get('comentarios') or "").strip() or None,
                            str(fila.get('estado') or "Activo").strip()
                        ))
                        importados += 1
                    except sqlite3.IntegrityError as e:
                        errores.append(f"Fila {idx}: empleado duplicado ({e})")
                    except Exception as e:
                        errores.append(f"Fila {idx}: {str(e)}")

                conn.commit()

            mensaje = f"Importación finalizada. Importados: {importados}. Errores: {len(errores)}"
            if errores:
                mensaje += "\nPrimeros errores:\n" + "\n".join(errores[:10])
            messagebox.showinfo("Importación", mensaje)
            self.cargar_empleados()

        except Exception as e:
            messagebox.showerror("Error", f"Error al importar:\n{e}")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        # Limpiar campos de texto
        campos_texto = [
            self.entry_codigo, self.entry_identificacion, self.entry_nombres,
            self.entry_apellidos, self.entry_fecha_nacimiento, self.entry_fecha_ingreso,
            self.entry_fecha_contrato, self.entry_fecha_retiro, self.entry_telefono,
            self.entry_direccion, self.entry_salario_diario, self.entry_bono_alimenticio,
            self.entry_bono_productividad, self.entry_seguro_social, self.entry_otras_deducciones
        ]
        
        for campo in campos_texto:
            campo.delete(0, "end")

        # Restablecer combos
        self.combo_cargo.set("Vaquero")
        self.combo_estado.set("Activo")
        self.combo_sexo.set("Masculino")
        self.combo_estado_civil.set("Soltero")

        # Limpiar áreas de texto
        self.text_comentarios.delete("1.0", "end")

        # Limpiar foto
        self.foto_path = None
        self.label_foto.configure(text="No hay foto seleccionada")

        # Establecer fecha de ingreso actual
        self.entry_fecha_ingreso.insert(0, datetime.now().strftime("%Y-%m-%d"))