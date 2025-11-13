import customtkinter as ctk
from tkinter import ttk, messagebox  # 👈 AGREGAR ttk
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database.conexion import db


class InventarioFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.finca_seleccionada = None
        self.crear_widgets()
        self.cargar_fincas()

    def crear_widgets(self):
        # ======== TÍTULO ========
        titulo = ctk.CTkLabel(self, text="📋 Inventario General de Animales", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # ======== FILTROS ========
        filtros_frame = ctk.CTkFrame(self, corner_radius=10)
        filtros_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(filtros_frame, text="🔍 FILTROS", 
                    font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=10)

        # Selección de finca
        row1 = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row1, text="Seleccionar Finca:", width=120).pack(side="left", padx=5)
        self.combo_fincas = ctk.CTkComboBox(row1, width=300, command=self.finca_seleccionada_cambio)
        self.combo_fincas.pack(side="left", padx=5)

        # Filtros adicionales
        row2 = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row2, text="Estado:", width=80).pack(side="left", padx=5)
        self.combo_estado = ctk.CTkComboBox(row2, values=["Todos", "Activo", "Vendido", "Muerto", "Enfermo"], width=150)
        self.combo_estado.set("Activo")
        self.combo_estado.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Inventariado:", width=100).pack(side="left", padx=5)
        self.combo_inventariado = ctk.CTkComboBox(row2, values=["Todos", "Sí", "No"], width=120)
        self.combo_inventariado.set("Todos")
        self.combo_inventariado.pack(side="left", padx=5)

        # Botones de filtro
        row3 = ctk.CTkFrame(filtros_frame, fg_color="transparent")
        row3.pack(fill="x", pady=10)
        
        ctk.CTkButton(row3, text="🔍 Aplicar Filtros", command=self.aplicar_filtros).pack(side="left", padx=5)
        ctk.CTkButton(row3, text="🔄 Mostrar Todos", command=self.mostrar_todos).pack(side="left", padx=5)
        ctk.CTkButton(row3, text="📊 Estadísticas", command=self.mostrar_estadisticas).pack(side="left", padx=5)

        # ======== ESTADÍSTICAS RÁPIDAS ========
        self.stats_frame = ctk.CTkFrame(self, corner_radius=10)
        self.stats_frame.pack(pady=5, padx=20, fill="x")
        
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="Seleccione una finca para ver estadísticas", 
                                       font=("Segoe UI", 12))
        self.stats_label.pack(pady=10)

        # ======== TABLA ========
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar tabla
        self.tabla = ttk.Treeview(table_frame, 
                                 columns=("codigo", "nombre", "sexo", "raza", "potrero", "estado", "inventariado", "salud", "tipo_ingreso"), 
                                 show="headings",
                                 height=20)
        
        # Configurar columnas
        column_config = [
            ("codigo", "Código", 100),
            ("nombre", "Nombre", 150),
            ("sexo", "Sexo", 80),
            ("raza", "Raza", 120),
            ("potrero", "Potrero", 120),
            ("estado", "Estado", 100),
            ("inventariado", "Inventariado", 100),
            ("salud", "Salud", 100),
            ("tipo_ingreso", "Tipo Ingreso", 120)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Doble click para ver detalles
        self.tabla.bind("<Double-1>", self.ver_detalles_animal)

    def cargar_fincas(self):
        """Carga la lista de fincas en el combobox"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM finca WHERE estado = 'Activa' OR estado = 'Activo'")
                fincas = [f"{row[0]}-{row[1]}" for row in cursor.fetchall()]
                
                self.combo_fincas.configure(values=fincas)
                if fincas:
                    self.combo_fincas.set(fincas[0])
                    self.finca_seleccionada_cambio(fincas[0])
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las fincas:\n{e}")

    def finca_seleccionada_cambio(self, choice):
        """Cuando se selecciona una finca diferente"""
        if choice:
            try:
                id_finca = int(choice.split("-")[0])
                self.finca_seleccionada = id_finca
                self.mostrar_animales_finca(id_finca)
                self.actualizar_estadisticas(id_finca)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar finca:\n{e}")

    def mostrar_animales_finca(self, id_finca):
        """Muestra los animales de la finca seleccionada"""
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.codigo, a.nombre, a.sexo, COALESCE(r.nombre, 'Sin raza') as raza, 
                           COALESCE(p.nombre, 'Sin potrero') as potrero, 
                           a.estado, COALESCE(a.inventariado, 0) as inventariado, 
                           COALESCE(a.salud, 'Sano') as salud, 
                           COALESCE(a.tipo_ingreso, 'N/A') as tipo_ingreso
                    FROM animal a
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    WHERE a.id_finca = ? AND a.estado = 'Activo'
                    ORDER BY a.codigo
                """, (id_finca,))
                
                for fila in cursor.fetchall():
                    inventariado = "Sí" if fila[6] == 1 else "No"
                    valores = fila[:6] + (inventariado,) + fila[7:]
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los animales:\n{e}")

    def actualizar_estadisticas(self, id_finca):
        """Actualiza las estadísticas de la finca seleccionada"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Total animales
                cursor.execute("SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo'", (id_finca,))
                total = cursor.fetchone()[0]
                
                # Por sexo
                cursor.execute("SELECT sexo, COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' GROUP BY sexo", (id_finca,))
                sexos = cursor.fetchall()
                
                # Por tipo ingreso
                cursor.execute("SELECT tipo_ingreso, COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' GROUP BY tipo_ingreso", (id_finca,))
                ingresos = cursor.fetchall()
                
                # Inventariados
                cursor.execute("SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND inventariado = 1", (id_finca,))
                inventariados = cursor.fetchone()[0]
                
                # Formatear estadísticas
                stats_text = f"📊 ESTADÍSTICAS - Total Animales: {total} | Inventariados: {inventariados}\n"
                
                if sexos:
                    stats_text += "👥 Sexos: " + ", ".join([f"{sexo}: {cant}" for sexo, cant in sexos]) + " | "
                
                if ingresos:
                    stats_text += "📥 Ingresos: " + ", ".join([f"{tipo}: {cant}" for tipo, cant in ingresos])
                
                self.stats_label.configure(text=stats_text)
                
        except Exception as e:
            self.stats_label.configure(text=f"Error al cargar estadísticas: {e}")

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados"""
        if not self.finca_seleccionada:
            messagebox.showwarning("Atención", "Seleccione una finca primero.")
            return

        estado = self.combo_estado.get()
        inventariado = self.combo_inventariado.get()

        # Limpiar tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT a.codigo, a.nombre, a.sexo, COALESCE(r.nombre, 'Sin raza') as raza, 
                           COALESCE(p.nombre, 'Sin potrero') as potrero, 
                           a.estado, COALESCE(a.inventariado, 0) as inventariado, 
                           COALESCE(a.salud, 'Sano') as salud, 
                           COALESCE(a.tipo_ingreso, 'N/A') as tipo_ingreso
                    FROM animal a
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    WHERE a.id_finca = ?
                """
                params = [self.finca_seleccionada]
                
                # Aplicar filtro de estado
                if estado != "Todos":
                    query += " AND a.estado = ?"
                    params.append(estado)
                else:
                    query += " AND a.estado != 'Eliminado'"
                
                # Aplicar filtro de inventariado
                if inventariado != "Todos":
                    inv_value = 1 if inventariado == "Sí" else 0
                    query += " AND a.inventariado = ?"
                    params.append(inv_value)
                
                query += " ORDER BY a.codigo"
                
                cursor.execute(query, params)
                
                for fila in cursor.fetchall():
                    inventariado_str = "Sí" if fila[6] == 1 else "No"
                    valores = fila[:6] + (inventariado_str,) + fila[7:]
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron aplicar los filtros:\n{e}")

    def mostrar_todos(self):
        """Muestra todos los animales de la finca"""
        if self.finca_seleccionada:
            self.combo_estado.set("Todos")
            self.combo_inventariado.set("Todos")
            self.mostrar_animales_finca(self.finca_seleccionada)

    def mostrar_estadisticas(self):
        """Muestra estadísticas detalladas"""
        if not self.finca_seleccionada:
            messagebox.showwarning("Atención", "Seleccione una finca primero.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener nombre de la finca
                cursor.execute("SELECT nombre FROM finca WHERE id = ?", (self.finca_seleccionada,))
                nombre_finca = cursor.fetchone()[0]
                
                stats = f"📊 ESTADÍSTICAS DETALLADAS - {nombre_finca}\n\n"
                
                # Totales por categoría
                categorias = [
                    ("Total Animales", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo'"),
                    ("Machos", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND sexo = 'Macho'"),
                    ("Hembras", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND sexo = 'Hembra'"),
                    ("Nacimientos", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND tipo_ingreso = 'Nacimiento'"),
                    ("Compras", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND tipo_ingreso = 'Compra'"),
                    ("Inventariados", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND inventariado = 1"),
                    ("Sin Inventariar", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND inventariado = 0"),
                    ("Sanos", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND salud = 'Sano'"),
                    ("Enfermos", "SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo' AND salud = 'Enfermo'")
                ]
                
                for nombre, consulta in categorias:
                    cursor.execute(consulta, (self.finca_seleccionada,))
                    count = cursor.fetchone()[0]
                    stats += f"• {nombre}: {count}\n"
                
                messagebox.showinfo("Estadísticas Detalladas", stats)
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las estadísticas:\n{e}")

    def ver_detalles_animal(self, event):
        """Muestra los detalles del animal seleccionado al hacer doble click"""
        seleccionado = self.tabla.selection()
        if seleccionado:
            codigo = self.tabla.item(seleccionado[0])["values"][0]
            self.mostrar_detalles_animal(codigo)

    def mostrar_detalles_animal(self, codigo):
        """Muestra una ventana con los detalles completos del animal"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.*, f.nombre as finca, r.nombre as raza, p.nombre as potrero,
                           l.nombre as lote, g.nombre as grupo, v.nombre as vendedor
                    FROM animal a
                    LEFT JOIN finca f ON a.id_finca = f.id
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN lote l ON a.id_lote = l.id
                    LEFT JOIN grupo g ON a.id_grupo = g.id
                    LEFT JOIN vendedor v ON a.id_vendedor = v.id
                    WHERE a.codigo = ?
                """, (codigo,))
                
                animal = cursor.fetchone()
                
                if animal:
                    # Crear ventana de detalles
                    detalles_window = ctk.CTkToplevel(self)
                    detalles_window.title(f"Detalles Animal - {codigo}")
                    detalles_window.geometry("600x500")
                    detalles_window.transient(self)
                    detalles_window.grab_set()
                    
                    # Contenido de detalles
                    frame = ctk.CTkFrame(detalles_window)
                    frame.pack(fill="both", expand=True, padx=20, pady=20)
                    
                    info_text = f"""
🐄 **INFORMACIÓN DETALLADA DEL ANIMAL**

🏷️  **CÓDIGO:** {animal[2]}
📛  **NOMBRE:** {animal[3] or 'No asignado'}
🏞️  **FINCA:** {animal[28] or 'No asignada'}
📥  **TIPO INGRESO:** {animal[4]}

⚤  **SEXO:** {animal[5]}
🐄  **RAZA:** {animal[29] or 'No especificada'}
📍  **UBICACIÓN:** Potrero: {animal[30] or 'No asignado'} | Lote: {animal[31] or 'No asignado'} | Grupo: {animal[32] or 'No asignado'}

📅  **FECHA NACIMIENTO:** {animal[10] or 'No registrada'}
💰  **FECHA COMPRA:** {animal[11] or 'No aplica'}
⚖️  **PESO COMPRA:** {animal[13] or '0'} kg

👨‍👩‍👧  **INFORMACIÓN PADRES:**
   • Madre: {animal[17] or 'No registrada'}
   • Padre: {animal[16] or 'No registrada'}
   • Concepción: {animal[18] or 'No aplica'}

🏥  **SALUD:** {animal[19]}
✅  **ESTADO:** {animal[20]}
📋  **INVENTARIADO:** {'Sí' if animal[21] == 1 else 'No'}

🎨  **CARACTERÍSTICAS:**
   • Color: {animal[22] or 'No especificado'}
   • Hierro: {animal[23] or 'No especificado'}
   • N° Hierros: {animal[24] or '0'}
   • Composición Racial: {animal[25] or 'No especificada'}

💬  **COMENTARIOS:**
{animal[26] or 'Sin comentarios'}

🛒  **INFORMACIÓN COMPRA:**
   • Vendedor: {animal[33] or 'No aplica'}
   • Precio: ${animal[15] or '0'}

📅  **FECHA REGISTRO:** {animal[27]}
"""
                    
                    text_widget = ctk.CTkTextbox(frame, wrap="word", font=("Segoe UI", 12))
                    text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                    text_widget.insert("1.0", info_text)
                    text_widget.configure(state="disabled")
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")