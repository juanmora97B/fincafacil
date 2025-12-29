import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os
import sqlite3

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.units_helper import units_helper
from modules.utils.animal_format import build_animal_info_text
from modules.utils.db_logging import safe_execute

def build_meta_note(event_type, resumen, metadata=None):
    """Construye una nota con metadatos (interfaz unificada)."""
    try:
        from modules.utils.metadata import GestorMetadatos
        # Si GestorMetadatos expone algún constructor estándar, úsalo.
        return GestorMetadatos.build(event_type, resumen, metadata)  # type: ignore[attr-defined]
    except (ImportError, Exception):
        # Fallback básico si la API no coincide
        base = f"{event_type}: {resumen}"
        return base if not metadata else base + f" | meta={metadata}"

class ActualizacionInventarioFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.animal_actual = None
        self.finca_seleccionada = None
        self.crear_widgets()
        self.cargar_fincas()

    def crear_widgets(self):
        # ======== TÍTULO ========
        titulo = ctk.CTkLabel(self, text="🔄 Actualización de Inventario", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # ======== SELECCIÓN DE FINCA ========
        finca_frame = ctk.CTkFrame(self, corner_radius=10)
        finca_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(finca_frame, text="🏞️ Seleccionar Finca:", 
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        row1 = ctk.CTkFrame(finca_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.combo_fincas = ctk.CTkComboBox(row1, width=300, command=self.finca_seleccionada_cambio)
        self.combo_fincas.pack(side="left", padx=5)
        
        ctk.CTkButton(row1, text="🔄 Cargar Animales", command=self.cargar_animales_finca).pack(side="left", padx=5)

        # ======== BÚSQUEDA DE ANIMAL ========
        busqueda_frame = ctk.CTkFrame(self, corner_radius=10)
        busqueda_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(busqueda_frame, text="🔍 Buscar Animal por Código:", 
                    font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=5)

        row2 = ctk.CTkFrame(busqueda_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.entry_codigo_busqueda = ctk.CTkEntry(row2, placeholder_text="Ingrese código del animal", width=250)
        self.entry_codigo_busqueda.pack(side="left", padx=5)
        
        ctk.CTkButton(row2, text="🔍 Buscar", command=self.buscar_animal).pack(side="left", padx=5)
        self.entry_codigo_busqueda.bind("<Return>", lambda e: self.buscar_animal())

        # ======== INFORMACIÓN DEL ANIMAL ========
        self.info_frame = ctk.CTkFrame(self, corner_radius=10)
        self.info_frame.pack(pady=10, padx=4, fill="x")
        
        self.label_info_animal = ctk.CTkLabel(self.info_frame, text="Ingrese un código para buscar el animal", 
                                            font=("Segoe UI", 12), justify="left")
        self.label_info_animal.pack(pady=10)

        # ======== ACTUALIZACIONES ========
        actualizaciones_frame = ctk.CTkFrame(self, corner_radius=10)
        actualizaciones_frame.pack(pady=10, padx=4, fill="x")

        ctk.CTkLabel(actualizaciones_frame, text="📝 Actualizar Información", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Peso actual
        row3 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self.label_peso = ctk.CTkLabel(row3, text=f"{units_helper.get_weight_label()}:", width=120)
        self.label_peso.pack(side="left", padx=5)
        self.entry_peso_actual = ctk.CTkEntry(row3, placeholder_text="Peso del animal", width=150)
        self.entry_peso_actual.pack(side="left", padx=5)
        
        ctk.CTkButton(row3, text="⚖️ Registrar Peso", command=self.registrar_peso).pack(side="left", padx=5)

        # Producción de leche (diaria)
        row3b = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row3b.pack(fill="x", pady=5)

        ctk.CTkLabel(row3b, text="Fecha:", width=60).pack(side="left", padx=5)
        self.entry_fecha_leche = ctk.CTkEntry(row3b, width=120)
        self.entry_fecha_leche.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_leche.pack(side="left", padx=5)

        vol_unit = units_helper.volume_unit
        ctk.CTkLabel(row3b, text=f"{vol_unit} Mañana:", width=90).pack(side="left", padx=5)
        self.entry_lts_manana = ctk.CTkEntry(row3b, width=70)
        self.entry_lts_manana.insert(0, "0")
        self.entry_lts_manana.pack(side="left", padx=2)

        ctk.CTkLabel(row3b, text=f"{vol_unit} Tarde:", width=80).pack(side="left", padx=5)
        self.entry_lts_tarde = ctk.CTkEntry(row3b, width=70)
        self.entry_lts_tarde.insert(0, "0")
        self.entry_lts_tarde.pack(side="left", padx=2)

        ctk.CTkLabel(row3b, text=f"{vol_unit} Noche:", width=80).pack(side="left", padx=5)
        self.entry_lts_noche = ctk.CTkEntry(row3b, width=70)
        self.entry_lts_noche.insert(0, "0")
        self.entry_lts_noche.pack(side="left", padx=2)

        ctk.CTkButton(row3b, text="🥛 Registrar Leche", command=self.registrar_leche).pack(side="left", padx=8)

        # Tratamiento
        row4 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row4, text="Tratamiento:", width=120).pack(side="left", padx=5)
        self.entry_tratamiento = ctk.CTkEntry(row4, placeholder_text="Tipo de tratamiento", width=200)
        self.entry_tratamiento.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Producto:", width=80).pack(side="left", padx=5)
        self.entry_producto = ctk.CTkEntry(row4, placeholder_text="Producto aplicado", width=150)
        self.entry_producto.pack(side="left", padx=5)
        
        ctk.CTkButton(row4, text="💊 Registrar Tratamiento", command=self.registrar_tratamiento).pack(side="left", padx=5)

        # Estado de inventario
        row5 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row5.pack(fill="x", pady=10)
        
        ctk.CTkLabel(row5, text="Estado de Inventario:", width=140).pack(side="left", padx=5)
        
        self.btn_inventariado = ctk.CTkButton(row5, text="✅ Marcar como INVENTARIADO", 
                                            fg_color="green", hover_color="#006400",
                                            command=lambda: self.marcar_inventario(1))
        self.btn_inventariado.pack(side="left", padx=5)
        
        self.btn_no_inventariado = ctk.CTkButton(row5, text="❌ Marcar como FALTANTE", 
                                               fg_color="red", hover_color="#8B0000",
                                               command=lambda: self.marcar_inventario(0))
        self.btn_no_inventariado.pack(side="left", padx=5)

        # Registro de muerte
        row5b = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row5b.pack(fill="x", pady=5)
        
        ctk.CTkButton(row5b, text="💀 Registrar Muerte", 
                     fg_color="#8B0000", hover_color="#660000",
                     command=self.registrar_muerte).pack(side="left", padx=5)

        # Comentario rápido
        row6 = ctk.CTkFrame(actualizaciones_frame, fg_color="transparent")
        row6.pack(fill="both", expand=True, pady=5)
        
        ctk.CTkLabel(row6, text="Comentario Rápido:", width=120).pack(side="left", padx=5, anchor="n")
        self.text_comentario_rapido = ctk.CTkTextbox(row6, width=300, height=100)
        self.text_comentario_rapido.pack(side="left", padx=5, fill="both", expand=True)
        
        ctk.CTkButton(row6, text="💬 Guardar Comentario", command=self.guardar_comentario_rapido).pack(side="left", padx=5)

        # ======== LISTA DE ANIMALES SIN INVENTARIAR ========
        lista_frame = ctk.CTkFrame(self)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(lista_frame, text="📋 Animales Sin Inventariar", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=5)

        # Tabla de animales sin inventariar
        self.tabla_sin_inventariar = ttk.Treeview(lista_frame, 
                                                 columns=("codigo", "nombre", "sexo", "raza", "potrero", "ultimo_peso"), 
                                                 show="headings",
                                                 height=8)
        
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("sexo", "Sexo", 80),
            ("raza", "Raza", 120),
            ("potrero", "Potrero", 120),
            ("ultimo_peso", "Último Peso", 100)
        ]
        
        for col, heading, width in column_config:
            self.tabla_sin_inventariar.heading(col, text=heading)
            self.tabla_sin_inventariar.column(col, width=width, anchor="center")

        self.tabla_sin_inventariar.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.tabla_sin_inventariar.yview)
        self.tabla_sin_inventariar.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Doble click para seleccionar
        self.tabla_sin_inventariar.bind("<Double-1>", self.seleccionar_de_lista)

    def cargar_fincas(self):
        """Carga la lista de fincas"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                
                self.combo_fincas.configure(values=fincas)
                if fincas:
                    # Intentar seleccionar la finca por defecto desde preferencias
                    default_key = None
                    try:
                        cursor.execute("SELECT valor FROM app_settings WHERE clave = 'default_finca_id'")
                        row = cursor.fetchone()
                        if row and row[0]:
                            dfid = str(row[0]).strip()
                            for item in fincas:
                                if item.split('-', 1)[0].strip() == dfid:
                                    default_key = item
                                    break
                    except Exception:
                        pass

                    choice = default_key or fincas[0]
                    self.combo_fincas.set(choice)
                    self.finca_seleccionada_cambio(choice)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def finca_seleccionada_cambio(self, choice):
        """Cuando se selecciona una finca diferente"""
        if choice:
            try:
                self.finca_seleccionada = int(choice.split("-")[0])
            except:
                self.finca_seleccionada = None

    def cargar_animales_finca(self):
        """Carga los animales sin inventariar de la finca seleccionada - VERSIÓN CORREGIDA"""
        if not self.finca_seleccionada:
            messagebox.showwarning("Atención", "Seleccione una finca primero.")
            return

        # Limpiar tabla
        for fila in self.tabla_sin_inventariar.get_children():
            self.tabla_sin_inventariar.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.codigo, a.nombre, a.sexo, COALESCE(r.nombre,'Sin raza') as raza, p.nombre,
                           (SELECT peso FROM peso WHERE animal_id = a.id ORDER BY fecha DESC LIMIT 1) as ultimo_peso
                    FROM animal a
                    LEFT JOIN raza r ON a.raza_id = r.id
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    WHERE a.id_finca = ? AND a.estado = 'Activo' AND a.inventariado = 0
                    ORDER BY a.codigo
                """, (self.finca_seleccionada,))
                
                for fila in cursor.fetchall():
                    ultimo_peso = f"{fila[5]} kg" if fila[5] else "No registrado"
                    valores = fila[:5] + (ultimo_peso,)
                    self.tabla_sin_inventariar.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los animales:\n{e}")

    def buscar_animal(self):
        """Busca un animal por código y carga un dict consistente para operaciones posteriores."""
        codigo = self.entry_codigo_busqueda.get().strip().upper()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código para buscar.")
            return
        try:
            with db.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                safe_execute(cur,
                    """
                    SELECT a.id, a.codigo, a.nombre, a.tipo_ingreso, a.sexo,
                           f.nombre AS finca, r.nombre AS raza, p.nombre AS potrero,
                           l.nombre AS lote, s.nombre AS sector, a.salud, a.estado, a.inventariado,
                           a.fecha_nacimiento, a.fecha_compra, a.peso_nacimiento, a.peso_compra,
                           a.precio_compra, a.id_padre, a.id_madre, a.tipo_concepcion, a.color, a.hierro,
                           a.numero_hierros, a.composicion_racial, a.comentarios, a.foto_path, a.fecha_registro,
                           madre.codigo AS codigo_madre, madre.nombre AS nombre_madre,
                           padre.codigo AS codigo_padre, padre.nombre AS nombre_padre
                    FROM animal a
                    LEFT JOIN finca f ON a.id_finca = f.id
                    LEFT JOIN raza r ON a.raza_id = r.id
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN lote l ON a.lote_id = l.id
                    LEFT JOIN sector s ON a.id_sector = s.id
                    LEFT JOIN animal madre ON a.id_madre = madre.id
                    LEFT JOIN animal padre ON a.id_padre = padre.id
                    WHERE a.codigo = ? AND a.estado = 'Activo'
                    """,
                    (codigo,),
                )
                row = cur.fetchone()
            if row:
                self.animal_actual = dict(row)
                self.mostrar_info_animal(self.animal_actual)
                self.limpiar_campos_actualizacion()
            else:
                messagebox.showerror("No encontrado", f"No se encontró un animal activo con código: {codigo}")
                self.animal_actual = None
                self.label_info_animal.configure(text="Animal no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el animal:\n{e}")

    def mostrar_info_animal(self, animal):
        """Muestra la información del animal reutilizando helper central para consistencia."""
        self.label_info_animal.configure(text=build_animal_info_text(animal))

    def seleccionar_de_lista(self, event):
        """Selecciona un animal de la lista de sin inventariar"""
        seleccionado = self.tabla_sin_inventariar.selection()
        if seleccionado:
            codigo = self.tabla_sin_inventariar.item(seleccionado[0])["values"][0]
            self.entry_codigo_busqueda.delete(0, "end")
            self.entry_codigo_busqueda.insert(0, codigo)
            self.buscar_animal()

    def registrar_peso(self):
        """Registra el peso actual del animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        peso_str = self.entry_peso_actual.get().strip()
        if not peso_str:
            messagebox.showwarning("Atención", "Ingrese el peso del animal.")
            return

        try:
            peso_input = float(peso_str)
            # Convertir a kg para almacenar en BD
            peso_kg = units_helper.convert_weight_to_kg(peso_input)
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                safe_execute(cursor,"""
                    INSERT INTO peso (animal_id, fecha, peso, metodo, observaciones)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.animal_actual['id'], datetime.now().strftime("%Y-%m-%d"), peso_kg, "Báscula", "Registro durante inventario"))
                conn.commit()

            messagebox.showinfo("Éxito", f"Peso de {units_helper.format_weight(peso_kg)} registrado correctamente para {self.animal_actual['codigo']}")
            self.entry_peso_actual.delete(0, "end")
            
        except ValueError:
            messagebox.showerror("Error", "El peso debe ser un número válido.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el peso:\n{e}")

    def registrar_tratamiento(self):
        """Registra un tratamiento aplicado al animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        tratamiento = self.entry_tratamiento.get().strip()
        producto = self.entry_producto.get().strip()

        if not tratamiento or not producto:
            messagebox.showwarning("Atención", "Complete ambos campos: tratamiento y producto.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                safe_execute(cursor,
                    """
                    INSERT INTO tratamiento (
                        id_animal, fecha_inicio, tipo_tratamiento, producto, dosis, veterinario, comentario
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.animal_actual['id'],
                        datetime.now().strftime("%Y-%m-%d"),
                        tratamiento,
                        producto,
                        "Según indicaciones",
                        "Veterinario de finca",
                        "Aplicado durante inventario",
                    ),
                )
                conn.commit()

            messagebox.showinfo("Éxito", f"Tratamiento '{tratamiento}' registrado correctamente para {self.animal_actual['codigo']}")
            self.entry_tratamiento.delete(0, "end")
            self.entry_producto.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el tratamiento:\n{e}")

    def registrar_leche(self):
        """Registra la producción de leche del animal para una fecha"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        fecha = (self.entry_fecha_leche.get() or datetime.now().strftime("%Y-%m-%d")).strip()
        try:
            l_m_input = float(self.entry_lts_manana.get() or 0)
            l_t_input = float(self.entry_lts_tarde.get() or 0)
            l_n_input = float(self.entry_lts_noche.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Los volúmenes deben ser números válidos.")
            return

        # Convertir a litros para almacenar en BD
        l_m = units_helper.convert_volume_to_l(l_m_input) or 0.0
        l_t = units_helper.convert_volume_to_l(l_t_input) or 0.0
        l_n = units_helper.convert_volume_to_l(l_n_input) or 0.0

        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                safe_execute(cur,
                    """
                    INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(animal_id, fecha) DO UPDATE SET
                        litros_manana=excluded.litros_manana,
                        litros_tarde=excluded.litros_tarde,
                        litros_noche=excluded.litros_noche,
                        observaciones=excluded.observaciones
                    """,
                    (self.animal_actual['id'], fecha, l_m, l_t, l_n, "Registro durante inventario")
                )
                conn.commit()

            total = l_m + l_t + l_n
            messagebox.showinfo("Éxito", f"Producción registrada ({fecha}): {units_helper.format_volume(total, decimal_places=1)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la leche:\n{e}")

    def marcar_inventario(self, estado):
        """Marca el animal como inventariado o no inventariado"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                safe_execute(cursor, "UPDATE animal SET inventariado = ? WHERE id = ?", 
                             (estado, self.animal_actual['id']))
                conn.commit()

            estado_text = "INVENTARIADO" if estado == 1 else "NO INVENTARIADO (FALTANTE)"
            messagebox.showinfo("Éxito", f"Animal {self.animal_actual['codigo']} marcado como {estado_text}")
            
            # Actualizar lista
            self.cargar_animales_finca()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el estado de inventario:\n{e}")

    def guardar_comentario_rapido(self):
        """Guarda un comentario rápido para el animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Busque un animal primero.")
            return

        comentario = self.text_comentario_rapido.get("1.0", "end-1c").strip()
        if not comentario:
            messagebox.showwarning("Atención", "Escriba un comentario.")
            return

        try:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            # Construir metadata estándar para comentarios rápidos de inventario
            resumen = comentario.split('\n')[0][:120]
            meta = {
                "codigo": self.animal_actual.get('codigo'),
                "finca": self.animal_actual.get('finca'),
                "fecha": fecha_hoy,
                "contexto": "inventario"
            }
            nota_completa = build_meta_note("comentario_inventario", resumen, meta)
            with db.get_connection() as conn:
                cursor = conn.cursor()
                safe_execute(cursor,
                    """
                    INSERT INTO comentario (id_animal, fecha, autor, nota)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        self.animal_actual['id'],
                        fecha_hoy,
                        "Sistema Inventario",
                        nota_completa,
                    ),
                )
                conn.commit()

            messagebox.showinfo("Éxito", "Comentario guardado correctamente")
            self.text_comentario_rapido.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el comentario:\n{e}")

    def limpiar_campos_actualizacion(self):
        """Limpia los campos de actualización"""
        self.entry_peso_actual.delete(0, "end")
        self.entry_tratamiento.delete(0, "end")
        self.entry_producto.delete(0, "end")
        self.text_comentario_rapido.delete("1.0", "end")

    def registrar_muerte(self):
        """Registra la muerte de un animal"""
        if not self.animal_actual:
            messagebox.showwarning("Atención", "Seleccione un animal primero")
            return
        
        # Ventana de registro
        ventana = ctk.CTkToplevel(self)
        ventana.title("Registrar Muerte")
        ventana.geometry("500x450")
        ventana.grab_set()
        
        ctk.CTkLabel(ventana, text="💀 Registrar Muerte del Animal", 
                    font=("Segoe UI", 18, "bold")).pack(pady=15)
        
        ctk.CTkLabel(ventana, text=f"Animal: {self.animal_actual['codigo']} {self.animal_actual.get('nombre', '')}", 
                    font=("Segoe UI", 12)).pack(pady=5)
        
        form = ctk.CTkFrame(ventana, corner_radius=10)
        # Compactar ancho (20→4)
        form.pack(fill="both", expand=True, padx=4, pady=10)
        
        # Fecha
        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(r1, text="Fecha*:", width=150).pack(side="left", padx=5)
        e_fecha = ctk.CTkEntry(r1, width=200)
        e_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        e_fecha.pack(side="left", padx=5)
        
        # Causa (cargar de catálogo)
        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(r2, text="Causa*:", width=150).pack(side="left", padx=5)
        cb_causa = ctk.CTkComboBox(r2, width=200)
        cb_causa.pack(side="left", padx=5)
        
        # Cargar causas
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM causa_muerte WHERE estado = 'Activo' ORDER BY nombre")
                causas = [r[0] for r in cur.fetchall()]
                if causas:
                    cb_causa.configure(values=causas)
                    cb_causa.set(causas[0])
                else:
                    cb_causa.configure(values=["Enfermedad", "Accidente", "Natural", "Desconocida"])
                    cb_causa.set("Desconocida")
        except:
            cb_causa.configure(values=["Enfermedad", "Accidente", "Natural", "Desconocida"])
            cb_causa.set("Desconocida")
        
        # Diagnóstico presuntivo
        r3 = ctk.CTkFrame(form, fg_color="transparent")
        r3.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(r3, text="Diagnóstico Presuntivo:", width=150, anchor="w").pack(side="top", padx=5)
        t_diag_pres = ctk.CTkTextbox(r3, width=350, height=80)
        t_diag_pres.pack(side="top", padx=5, pady=5, fill="both", expand=True)
        
        # Diagnóstico confirmado
        r4 = ctk.CTkFrame(form, fg_color="transparent")
        r4.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(r4, text="Diagnóstico Confirmado:", width=150, anchor="w").pack(side="top", padx=5)
        t_diag_conf = ctk.CTkTextbox(r4, width=350, height=80)
        t_diag_conf.pack(side="top", padx=5, pady=5, fill="both", expand=True)
        
        # Observaciones
        r5 = ctk.CTkFrame(form, fg_color="transparent")
        r5.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(r5, text="Observaciones:", width=150, anchor="w").pack(side="top", padx=5)
        t_obs = ctk.CTkTextbox(r5, width=350, height=80)
        t_obs.pack(side="top", padx=5, pady=5, fill="both", expand=True)
        
        def guardar():
            # Revalidar que animal_actual existe (protección contra timing issues)
            if not self.animal_actual:
                messagebox.showwarning("Atención", "Animal no disponible")
                return
            
            try:
                fecha = e_fecha.get().strip()
                causa = cb_causa.get()
                diag_pres = t_diag_pres.get("1.0", "end-1c").strip() or None
                diag_conf = t_diag_conf.get("1.0", "end-1c").strip() or None
                obs = t_obs.get("1.0", "end-1c").strip() or None
                
                if not fecha or not causa:
                    messagebox.showwarning("Atención", "Complete los campos obligatorios")
                    return
                
                with db.get_connection() as conn:
                    cur = conn.cursor()
                    
                    # Verificar si ya existe registro de muerte
                    safe_execute(cur, "SELECT id FROM muerte WHERE animal_id = ?", (self.animal_actual['id'],))
                    if cur.fetchone():
                        messagebox.showwarning("Atención", "Este animal ya tiene un registro de muerte")
                        return
                    
                    # Registrar muerte
                    safe_execute(cur,"""
                        INSERT INTO muerte (animal_id, fecha, causa, diagnostico_presuntivo, 
                                          diagnostico_confirmado, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (self.animal_actual['id'], fecha, causa, diag_pres, diag_conf, obs))
                    
                    # Actualizar estado del animal
                    safe_execute(cur, "UPDATE animal SET estado = 'Muerto' WHERE id = ?", (self.animal_actual['id'],))
                    
                    conn.commit()
                
                messagebox.showinfo("Éxito", "✅ Muerte registrada correctamente")
                ventana.destroy()
                
                # Limpiar animal actual
                self.animal_actual = None
                self.label_info_animal.configure(text="Animal marcado como Muerto. Busque otro animal.")
                self.limpiar_campos_actualizacion()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar:\n{e}")
        
        # Botones
        btns = ctk.CTkFrame(ventana, fg_color="transparent")
        btns.pack(pady=10)
        ctk.CTkButton(btns, text="💾 Guardar", command=guardar, fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Cancelar", command=ventana.destroy).pack(side="left", padx=5)