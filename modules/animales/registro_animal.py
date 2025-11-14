import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import sqlite3
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import get_db_connection
from utils.validators import animal_validator  # ✅ NUEVO IMPORT


class RegistroAnimalFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.foto_path = None
        self.crear_widgets()
        self.cargar_datos_combos()

    def crear_widgets(self):
        # ======== TÍTULO ========
        titulo = ctk.CTkLabel(self, text="📝 Registro de Animales", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # ======== NOTEBOOK PARA TIPO DE REGISTRO ========
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña Nacimiento
        self.tab_nacimiento = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_nacimiento, text="👶 Nacimiento")

        # Pestaña Compra
        self.tab_compra = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_compra, text="💰 Compra")

        # Configurar ambas pestañas
        self.configurar_tab_nacimiento()
        self.configurar_tab_compra()

        # Botones generales
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="💾 Guardar Animal", command=self.guardar_animal, 
                     fg_color="green", hover_color="#006400").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📥 Importar desde Excel", command=self.importar_excel,
                     fg_color="#1976D2", hover_color="#1565C0").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Limpiar Formulario", command=self.limpiar_formulario).pack(side="left", padx=5)

    def configurar_tab_nacimiento(self):
        """Configura la pestaña de registro por nacimiento"""
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self.tab_nacimiento)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # INFORMACIÓN BÁSICA
        frame_basica = ctk.CTkFrame(main_frame)
        frame_basica.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_basica, text="📋 INFORMACIÓN BÁSICA", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Código y Nombre
        row1 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.entry_codigo_nac = ctk.CTkEntry(row1, placeholder_text="Código Animal *", width=200)
        self.entry_codigo_nac.pack(side="left", padx=5)
        
        self.entry_nombre_nac = ctk.CTkEntry(row1, placeholder_text="Nombre Animal", width=200)
        self.entry_nombre_nac.pack(side="left", padx=5)

        # Fecha y Sexo
        row2 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.entry_fecha_nac = ctk.CTkEntry(row2, placeholder_text="Fecha Nacimiento (YYYY-MM-DD) *", width=200)
        self.entry_fecha_nac.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_nac.pack(side="left", padx=5)
        
        self.combo_sexo_nac = ctk.CTkComboBox(row2, values=["Macho", "Hembra"], width=200)
        self.combo_sexo_nac.set("Macho")
        self.combo_sexo_nac.pack(side="left", padx=5)

        # INFORMACIÓN DE PADRES
        frame_padres = ctk.CTkFrame(main_frame)
        frame_padres.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_padres, text="👨‍👩‍👧 INFORMACIÓN DE PADRES", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Madre
        row3 = ctk.CTkFrame(frame_padres, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row3, text="Madre:", width=100).pack(side="left", padx=5)
        self.combo_madre_nac = ctk.CTkComboBox(row3, width=300)
        self.combo_madre_nac.pack(side="left", padx=5)

        # Padre y Tipo Concepción
        row4 = ctk.CTkFrame(frame_padres, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="Padre:", width=100).pack(side="left", padx=5)
        self.combo_padre_nac = ctk.CTkComboBox(row4, width=200)
        self.combo_padre_nac.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Concepción:", width=80).pack(side="left", padx=5)
        self.combo_concepcion_nac = ctk.CTkComboBox(row4, values=["Monta", "Inseminación"], width=150)
        self.combo_concepcion_nac.set("Monta")
        self.combo_concepcion_nac.pack(side="left", padx=5)

        # UBICACIÓN
        self.configurar_ubicacion(main_frame, "nac")

        # INFORMACIÓN ADICIONAL
        self.configurar_informacion_adicional(main_frame, "nac")

    def configurar_tab_compra(self):
        """Configura la pestaña de registro por compra"""
        main_frame = ctk.CTkScrollableFrame(self.tab_compra)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # INFORMACIÓN BÁSICA
        frame_basica = ctk.CTkFrame(main_frame)
        frame_basica.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_basica, text="📋 INFORMACIÓN BÁSICA", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Código y Nombre
        row1 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.entry_codigo_comp = ctk.CTkEntry(row1, placeholder_text="Código Animal *", width=200)
        self.entry_codigo_comp.pack(side="left", padx=5)
        
        self.entry_nombre_comp = ctk.CTkEntry(row1, placeholder_text="Nombre Animal", width=200)
        self.entry_nombre_comp.pack(side="left", padx=5)

        # Fechas y Sexo
        row2 = ctk.CTkFrame(frame_basica, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.entry_fecha_nac_comp = ctk.CTkEntry(row2, placeholder_text="Fecha Nacimiento (YYYY-MM-DD)", width=200)
        self.entry_fecha_nac_comp.pack(side="left", padx=5)
        
        self.entry_fecha_compra = ctk.CTkEntry(row2, placeholder_text="Fecha Compra (YYYY-MM-DD) *", width=200)
        self.entry_fecha_compra.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_compra.pack(side="left", padx=5)
        
        self.combo_sexo_comp = ctk.CTkComboBox(row2, values=["Macho", "Hembra"], width=150)
        self.combo_sexo_comp.set("Macho")
        self.combo_sexo_comp.pack(side="left", padx=5)

        # INFORMACIÓN COMPRA
        frame_compra = ctk.CTkFrame(main_frame)
        frame_compra.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_compra, text="💰 INFORMACIÓN DE COMPRA", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Vendedor y Precio
        row3 = ctk.CTkFrame(frame_compra, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row3, text="Vendedor:", width=100).pack(side="left", padx=5)
        self.combo_vendedor = ctk.CTkComboBox(row3, width=300)
        self.combo_vendedor.pack(side="left", padx=5)
        
        ctk.CTkLabel(row3, text="Precio $:", width=80).pack(side="left", padx=5)
        self.entry_precio = ctk.CTkEntry(row3, placeholder_text="0.00", width=150)
        self.entry_precio.pack(side="left", padx=5)

        # Peso Compra
        row4 = ctk.CTkFrame(frame_compra, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="Peso Compra (kg):", width=120).pack(side="left", padx=5)
        self.entry_peso_compra = ctk.CTkEntry(row4, placeholder_text="Peso al momento de compra", width=200)
        self.entry_peso_compra.pack(side="left", padx=5)

        # UBICACIÓN
        self.configurar_ubicacion(main_frame, "comp")

        # INFORMACIÓN ADICIONAL
        self.configurar_informacion_adicional(main_frame, "comp")

    def configurar_ubicacion(self, parent, tipo):
        """Configura la sección de ubicación"""
        frame_ubicacion = ctk.CTkFrame(parent)
        frame_ubicacion.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_ubicacion, text="📍 UBICACIÓN", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Finca
        row1 = ctk.CTkFrame(frame_ubicacion, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row1, text="Finca:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_finca_nac = ctk.CTkComboBox(row1, width=300)
            self.combo_finca_nac.pack(side="left", padx=5)
        else:
            self.combo_finca_comp = ctk.CTkComboBox(row1, width=300)
            self.combo_finca_comp.pack(side="left", padx=5)

        # Potrero, Lote y Grupo
        row2 = ctk.CTkFrame(frame_ubicacion, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row2, text="Potrero:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_potrero_nac = ctk.CTkComboBox(row2, width=200)
            self.combo_potrero_nac.pack(side="left", padx=5)
        else:
            self.combo_potrero_comp = ctk.CTkComboBox(row2, width=200)
            self.combo_potrero_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Lote:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_lote_nac = ctk.CTkComboBox(row2, width=150)
            self.combo_lote_nac.pack(side="left", padx=5)
        else:
            self.combo_lote_comp = ctk.CTkComboBox(row2, width=150)
            self.combo_lote_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Grupo:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_grupo_nac = ctk.CTkComboBox(row2, width=150)
            self.combo_grupo_nac.pack(side="left", padx=5)
        else:
            self.combo_grupo_comp = ctk.CTkComboBox(row2, width=150)
            self.combo_grupo_comp.pack(side="left", padx=5)

    def configurar_informacion_adicional(self, parent, tipo):
        """Configura la sección de información adicional"""
        frame_adicional = ctk.CTkFrame(parent)
        frame_adicional.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_adicional, text="📝 INFORMACIÓN ADICIONAL", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Raza y Salud
        row1 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row1, text="Raza:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_raza_nac = ctk.CTkComboBox(row1, width=200)
            self.combo_raza_nac.pack(side="left", padx=5)
        else:
            self.combo_raza_comp = ctk.CTkComboBox(row1, width=200)
            self.combo_raza_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Salud:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_salud_nac = ctk.CTkComboBox(row1, values=["Sano", "Enfermo"], width=150)
            self.combo_salud_nac.set("Sano")
            self.combo_salud_nac.pack(side="left", padx=5)
        else:
            self.combo_salud_comp = ctk.CTkComboBox(row1, values=["Sano", "Enfermo"], width=150)
            self.combo_salud_comp.set("Sano")
            self.combo_salud_comp.pack(side="left", padx=5)

        # Estado
        row2 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row2, text="Estado:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.combo_estado_nac = ctk.CTkComboBox(row2, values=["Activo", "Vendido", "Muerto"], width=200)
            self.combo_estado_nac.set("Activo")
            self.combo_estado_nac.pack(side="left", padx=5)
        else:
            self.combo_estado_comp = ctk.CTkComboBox(row2, values=["Activo", "Vendido", "Muerto"], width=200)
            self.combo_estado_comp.set("Activo")
            self.combo_estado_comp.pack(side="left", padx=5)

        # Características físicas
        row3 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row3, text="Color:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_color_nac = ctk.CTkEntry(row3, placeholder_text="Color del animal", width=150)
            self.entry_color_nac.pack(side="left", padx=5)
        else:
            self.entry_color_comp = ctk.CTkEntry(row3, placeholder_text="Color del animal", width=150)
            self.entry_color_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row3, text="Hierro:", width=80).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_hierro_nac = ctk.CTkEntry(row3, placeholder_text="Marca de hierro", width=150)
            self.entry_hierro_nac.pack(side="left", padx=5)
        else:
            self.entry_hierro_comp = ctk.CTkEntry(row3, placeholder_text="Marca de hierro", width=150)
            self.entry_hierro_comp.pack(side="left", padx=5)

        # Número de hierros y composición racial
        row4 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="N° Hierros:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_num_hierros_nac = ctk.CTkEntry(row4, placeholder_text="0", width=100)
            self.entry_num_hierros_nac.pack(side="left", padx=5)
        else:
            self.entry_num_hierros_comp = ctk.CTkEntry(row4, placeholder_text="0", width=100)
            self.entry_num_hierros_comp.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Composición Racial:", width=140).pack(side="left", padx=5)
        if tipo == "nac":
            self.entry_composicion_nac = ctk.CTkEntry(row4, placeholder_text="Ej: 75% Holstein, 25% Gyr", width=250)
            self.entry_composicion_nac.pack(side="left", padx=5)
        else:
            self.entry_composicion_comp = ctk.CTkEntry(row4, placeholder_text="Ej: 75% Holstein, 25% Gyr", width=250)
            self.entry_composicion_comp.pack(side="left", padx=5)

        # Comentarios
        row5 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row5, text="Comentarios:", width=100).pack(side="left", padx=5, anchor="n")
        if tipo == "nac":
            self.text_comentarios_nac = ctk.CTkTextbox(row5, width=400, height=60)
            self.text_comentarios_nac.pack(side="left", padx=5, fill="x", expand=True)
        else:
            self.text_comentarios_comp = ctk.CTkTextbox(row5, width=400, height=60)
            self.text_comentarios_comp.pack(side="left", padx=5, fill="x", expand=True)

        # Foto
        row6 = ctk.CTkFrame(frame_adicional, fg_color="transparent")
        row6.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row6, text="Foto:", width=100).pack(side="left", padx=5)
        if tipo == "nac":
            self.btn_foto_nac = ctk.CTkButton(row6, text="📷 Cargar Foto", command=self.cargar_foto_nac)
            self.btn_foto_nac.pack(side="left", padx=5)
            self.label_foto_nac = ctk.CTkLabel(row6, text="No hay foto seleccionada")
            self.label_foto_nac.pack(side="left", padx=5)
        else:
            self.btn_foto_comp = ctk.CTkButton(row6, text="📷 Cargar Foto", command=self.cargar_foto_comp)
            self.btn_foto_comp.pack(side="left", padx=5)
            self.label_foto_comp = ctk.CTkLabel(row6, text="No hay foto seleccionada")
            self.label_foto_comp.pack(side="left", padx=5)

    def cargar_datos_combos(self):
        """Carga los datos en los combobox"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Cargar fincas
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                
                # Cargar razas
                cursor.execute("SELECT id, nombre FROM raza WHERE estado = 'Activa' OR estado = 'Activo'")
                razas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                
                # Cargar animales para padres
                cursor.execute("SELECT id, codigo, nombre FROM animal WHERE estado = 'Activo'")
                animales = [f"{row[0]}-{row[1]} ({row[2] or 'Sin nombre'})" for row in cursor.fetchall()]
                
                # Cargar vendedores
                cursor.execute("SELECT id, nombre FROM vendedor WHERE estado = 'Activo'")
                vendedores = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{e}")
            return
        
        # Asignar a combos de nacimiento
        if hasattr(self, 'combo_finca_nac'):
            self.combo_finca_nac.configure(values=fincas)
            if fincas: self.combo_finca_nac.set(fincas[0])
            
        if hasattr(self, 'combo_raza_nac'):
            self.combo_raza_nac.configure(values=razas)
            if razas: self.combo_raza_nac.set(razas[0])
            
        if hasattr(self, 'combo_madre_nac'):
            self.combo_madre_nac.configure(values=animales)
            
        if hasattr(self, 'combo_padre_nac'):
            self.combo_padre_nac.configure(values=animales)
        
        # Asignar a combos de compra
        if hasattr(self, 'combo_finca_comp'):
            self.combo_finca_comp.configure(values=fincas)
            if fincas: self.combo_finca_comp.set(fincas[0])
            
        if hasattr(self, 'combo_raza_comp'):
            self.combo_raza_comp.configure(values=razas)
            if razas: self.combo_raza_comp.set(razas[0])
            
        if hasattr(self, 'combo_vendedor'):
            self.combo_vendedor.configure(values=vendedores)
            if vendedores: self.combo_vendedor.set(vendedores[0])

    def cargar_foto_nac(self):
        self.cargar_foto("nac")

    def cargar_foto_comp(self):
        self.cargar_foto("comp")

    def cargar_foto(self, tipo):
        """Carga una foto del animal"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto del animal",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.foto_path = file_path
            if tipo == "nac":
                self.label_foto_nac.configure(text=f"Foto: {os.path.basename(file_path)}")
            else:
                self.label_foto_comp.configure(text=f"Foto: {os.path.basename(file_path)}")

    def guardar_animal(self):
        """Guarda el animal según la pestaña activa"""
        tab_actual = self.notebook.index(self.notebook.select())
        
        if tab_actual == 0:  # Nacimiento
            self.guardar_nacimiento()
        else:  # Compra
            self.guardar_compra()

    def guardar_nacimiento(self):
        """Guarda un animal registrado por nacimiento con validación"""
        try:
            # Recoger datos del formulario
            datos_animal = {
                'codigo': self.entry_codigo_nac.get().strip().upper(),
                'nombre': self.entry_nombre_nac.get().strip(),
                'sexo': self.combo_sexo_nac.get(),
                'fecha_nacimiento': self.entry_fecha_nac.get().strip(),
                'peso_nacimiento': self.entry_peso_nacimiento.get() if hasattr(self, 'entry_peso_nacimiento') else None,
                'color': self.entry_color_nac.get().strip(),
                'comentarios': self.text_comentarios_nac.get("1.0", "end-1c").strip(),
                'precio_compra': None  # No aplica para nacimiento
            }
            
            # ✅ VALIDAR DATOS ANTES DE GUARDAR
            es_valido, errores = animal_validator.validar_animal_completo(datos_animal)
            
            if not es_valido:
                mensaje_errores = "❌ Errores de validación:\n• " + "\n• ".join(errores)
                messagebox.showerror("Errores de Validación", mensaje_errores)
                return False
            
            # Validaciones adicionales específicas
            if not datos_animal['codigo']:
                messagebox.showwarning("Atención", "El código del animal es obligatorio.")
                return False
                
            if not datos_animal['fecha_nacimiento']:
                messagebox.showwarning("Atención", "La fecha de nacimiento es obligatoria.")
                return False

            # Obtener IDs de combos
            id_finca = int(self.combo_finca_nac.get().split("-")[0]) if self.combo_finca_nac.get() else None
            raza_nombre = self.combo_raza_nac.get().split("-", 1)[1] if self.combo_raza_nac.get() and "-" in self.combo_raza_nac.get() else (self.combo_raza_nac.get() or None)
            id_madre = int(self.combo_madre_nac.get().split("-")[0]) if self.combo_madre_nac.get() else None
            id_padre = int(self.combo_padre_nac.get().split("-")[0]) if self.combo_padre_nac.get() else None

            # Preparar datos para inserción
            datos_insercion = (
                id_finca,
                datos_animal['codigo'],
                datos_animal['nombre'],
                'Nacimiento',
                datos_animal['sexo'],
                raza_nombre,
                None,  # id_potrero
                None,  # id_lote
                None,  # id_grupo
                datos_animal['fecha_nacimiento'],
                None,  # fecha_compra
                float(datos_animal['peso_nacimiento']) if datos_animal['peso_nacimiento'] else None,
                None,  # peso_compra
                None,  # id_vendedor
                None,  # precio_compra
                id_padre,
                id_madre,
                self.combo_concepcion_nac.get(),
                self.combo_salud_nac.get(),
                self.combo_estado_nac.get(),
                0,  # inventariado
                datos_animal['color'],
                self.entry_hierro_nac.get().strip(),
                int(self.entry_num_hierros_nac.get().strip()) if self.entry_num_hierros_nac.get().strip() else 0,
                self.entry_composicion_nac.get().strip(),
                datos_animal['comentarios'],
                self.foto_path,
                datetime.now().strftime("%Y-%m-%d")
            )
            
            # ✅ DATOS VÁLIDOS - Proceder con guardado
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO animal (
                        id_finca, codigo, nombre, tipo_ingreso, sexo, raza, id_potrero, 
                        id_lote, id_grupo, fecha_nacimiento, fecha_compra, peso_nacimiento, 
                        peso_compra, id_vendedor, precio_compra, id_padre, id_madre, 
                        tipo_concepcion, salud, estado, inventariado, color, hierro, 
                        numero_hierros, composicion_racial, comentarios, foto_path, fecha_registro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos_insercion)
                conn.commit()
                
            messagebox.showinfo("Éxito", "✅ Animal registrado por nacimiento correctamente.")
            self.limpiar_formulario()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ No se pudo guardar el animal:\n{e}")
            return False

    def guardar_compra(self):
        """Guarda un animal registrado por compra con validación"""
        try:
            # Recoger datos del formulario
            datos_animal = {
                'codigo': self.entry_codigo_comp.get().strip().upper(),
                'nombre': self.entry_nombre_comp.get().strip(),
                'sexo': self.combo_sexo_comp.get(),
                'fecha_nacimiento': self.entry_fecha_nac_comp.get().strip() or None,
                'fecha_compra': self.entry_fecha_compra.get().strip(),
                'peso_compra': self.entry_peso_compra.get() or None,
                'precio_compra': self.entry_precio.get() or None,
                'color': self.entry_color_comp.get().strip(),
                'comentarios': self.text_comentarios_comp.get("1.0", "end-1c").strip()
            }
            
            # ✅ VALIDAR DATOS ANTES DE GUARDAR
            es_valido, errores = animal_validator.validar_animal_completo(datos_animal)
            
            if not es_valido:
                mensaje_errores = "❌ Errores de validación:\n• " + "\n• ".join(errores)
                messagebox.showerror("Errores de Validación", mensaje_errores)
                return False
            
            # Validaciones adicionales específicas
            if not datos_animal['codigo']:
                messagebox.showwarning("Atención", "El código del animal es obligatorio.")
                return False
                
            if not datos_animal['fecha_compra']:
                messagebox.showwarning("Atención", "La fecha de compra es obligatoria.")
                return False

            # Obtener IDs de combos
            id_finca = int(self.combo_finca_comp.get().split("-")[0]) if self.combo_finca_comp.get() else None
            raza_nombre = self.combo_raza_comp.get().split("-", 1)[1] if self.combo_raza_comp.get() and "-" in self.combo_raza_comp.get() else (self.combo_raza_comp.get() or None)
            id_vendedor = int(self.combo_vendedor.get().split("-")[0]) if self.combo_vendedor.get() else None
            
            # Preparar datos para inserción
            datos_insercion = (
                id_finca,
                datos_animal['codigo'],
                datos_animal['nombre'],
                'Compra',
                datos_animal['sexo'],
                raza_nombre,
                None,  # id_potrero
                None,  # id_lote
                None,  # id_grupo
                datos_animal['fecha_nacimiento'],
                datos_animal['fecha_compra'],
                None,  # peso_nacimiento
                float(datos_animal['peso_compra']) if datos_animal['peso_compra'] else None,
                id_vendedor,
                float(datos_animal['precio_compra']) if datos_animal['precio_compra'] else None,
                None,  # id_padre
                None,  # id_madre
                None,  # tipo_concepcion
                self.combo_salud_comp.get(),
                self.combo_estado_comp.get(),
                0,  # inventariado
                datos_animal['color'],
                self.entry_hierro_comp.get().strip(),
                int(self.entry_num_hierros_comp.get().strip()) if self.entry_num_hierros_comp.get().strip() else 0,
                self.entry_composicion_comp.get().strip(),
                datos_animal['comentarios'],
                self.foto_path,
                datetime.now().strftime("%Y-%m-%d")
            )
            
            # ✅ DATOS VÁLIDOS - Proceder con guardado
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO animal (
                        id_finca, codigo, nombre, tipo_ingreso, sexo, raza, id_potrero, 
                        id_lote, id_grupo, fecha_nacimiento, fecha_compra, peso_nacimiento, 
                        peso_compra, id_vendedor, precio_compra, id_padre, id_madre, 
                        tipo_concepcion, salud, estado, inventariado, color, hierro, 
                        numero_hierros, composicion_racial, comentarios, foto_path, fecha_registro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, datos_insercion)
                conn.commit()
                
            messagebox.showinfo("Éxito", "✅ Animal registrado por compra correctamente.")
            self.limpiar_formulario()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ No se pudo guardar el animal:\n{e}")
            return False

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        # Limpiar pestaña nacimiento
        if hasattr(self, 'entry_codigo_nac'):
            self.entry_codigo_nac.delete(0, "end")
            self.entry_nombre_nac.delete(0, "end")
            self.entry_fecha_nac.delete(0, "end")
            self.entry_fecha_nac.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.combo_sexo_nac.set("Macho")
            self.combo_madre_nac.set("")
            self.combo_padre_nac.set("")
            self.combo_concepcion_nac.set("Monta")
            self.entry_color_nac.delete(0, "end")
            self.entry_hierro_nac.delete(0, "end")
            self.entry_num_hierros_nac.delete(0, "end")
            self.entry_composicion_nac.delete(0, "end")
            self.text_comentarios_nac.delete("1.0", "end")
            self.label_foto_nac.configure(text="No hay foto seleccionada")
        
        # Limpiar pestaña compra
        if hasattr(self, 'entry_codigo_comp'):
            self.entry_codigo_comp.delete(0, "end")
            self.entry_nombre_comp.delete(0, "end")
            self.entry_fecha_nac_comp.delete(0, "end")
            self.entry_fecha_compra.delete(0, "end")
            self.entry_fecha_compra.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.combo_sexo_comp.set("Macho")
            self.entry_peso_compra.delete(0, "end")
            self.entry_precio.delete(0, "end")
            self.entry_color_comp.delete(0, "end")
            self.entry_hierro_comp.delete(0, "end")
            self.entry_num_hierros_comp.delete(0, "end")
            self.entry_composicion_comp.delete(0, "end")
            self.text_comentarios_comp.delete("1.0", "end")
            self.label_foto_comp.configure(text="No hay foto seleccionada")
        
        self.foto_path = None
    
    def importar_excel(self):
        """Importa animales desde Excel"""
        from modules.animales.importar_excel import importar_animales_desde_excel
        importar_animales_desde_excel()
        # Recargar datos si es necesario
        self.cargar_datos_combos()