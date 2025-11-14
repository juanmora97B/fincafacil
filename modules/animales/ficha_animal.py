import customtkinter as ctk
from tkinter import ttk, messagebox  # 👈 AGREGAR ttk
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class FichaAnimalFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.animal_actual = None
        self.crear_widgets()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="📄 Ficha Completa del Animal", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame de búsqueda
        search_frame = ctk.CTkFrame(self, corner_radius=10)
        search_frame.pack(pady=10, padx=20, fill="x")

        self.codigo_entry = ctk.CTkEntry(search_frame, placeholder_text="Ingrese código del animal", width=300)
        self.codigo_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(search_frame, text="🔍 Buscar Ficha", command=self.buscar_animal).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(search_frame, text="🔄 Limpiar", command=self.limpiar_busqueda).pack(side="left", padx=10, pady=10)

        # Notebook para diferentes secciones
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Pestaña Información General
        self.tab_general = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_general, text="📋 Información General")

        # Pestaña Historial de Pesos
        self.tab_pesos = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_pesos, text="⚖️ Historial de Pesos")

        # Pestaña Tratamientos
        self.tab_tratamientos = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_tratamientos, text="💊 Tratamientos")

        # Pestaña Comentarios
        self.tab_comentarios = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_comentarios, text="🗒️ Comentarios")

        # Inicializar pestañas
        self.configurar_tab_general()
        self.configurar_tab_pesos()
        self.configurar_tab_tratamientos()
        self.configurar_tab_comentarios()

    def configurar_tab_general(self):
        """Configura la pestaña de información general"""
        frame = ctk.CTkScrollableFrame(self.tab_general)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.info_general_label = ctk.CTkLabel(frame, text="Busque un animal para ver su información", 
                                              font=("Segoe UI", 14), justify="left")
        self.info_general_label.pack(pady=20)

    def configurar_tab_pesos(self):
        """Configura la pestaña de historial de pesos"""
        frame = ctk.CTkFrame(self.tab_pesos)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabla_pesos = ttk.Treeview(frame, columns=("fecha", "peso", "tipo", "comentario"), show="headings", height=10)
        
        column_config = [
            ("fecha", "Fecha", 120),
            ("peso", "Peso (kg)", 100),
            ("tipo", "Tipo", 100),
            ("comentario", "Comentario", 200)
        ]
        
        for col, heading, width in column_config:
            self.tabla_pesos.heading(col, text=heading)
            self.tabla_pesos.column(col, width=width, anchor="center")

        self.tabla_pesos.pack(fill="both", expand=True)

    def configurar_tab_tratamientos(self):
        """Configura la pestaña de tratamientos"""
        frame = ctk.CTkFrame(self.tab_tratamientos)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabla_tratamientos = ttk.Treeview(frame, columns=("fecha", "tratamiento", "producto", "veterinario", "comentario"), show="headings", height=10)
        
        column_config = [
            ("fecha", "Fecha", 120),
            ("tratamiento", "Tratamiento", 150),
            ("producto", "Producto", 150),
            ("veterinario", "Veterinario", 120),
            ("comentario", "Comentario", 200)
        ]
        
        for col, heading, width in column_config:
            self.tabla_tratamientos.heading(col, text=heading)
            self.tabla_tratamientos.column(col, width=width, anchor="center")

        self.tabla_tratamientos.pack(fill="both", expand=True)

    def configurar_tab_comentarios(self):
        """Configura la pestaña de comentarios"""
        frame = ctk.CTkFrame(self.tab_comentarios)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tabla_comentarios = ttk.Treeview(frame, columns=("fecha", "autor", "comentario"), show="headings", height=10)
        
        column_config = [
            ("fecha", "Fecha", 120),
            ("autor", "Autor", 150),
            ("comentario", "Comentario", 300)
        ]
        
        for col, heading, width in column_config:
            self.tabla_comentarios.heading(col, text=heading)
            self.tabla_comentarios.column(col, width=width, anchor="center")

        self.tabla_comentarios.pack(fill="both", expand=True)

    def buscar_animal(self):
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código para buscar.")
            return

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.*, f.nombre as finca, r.nombre as raza, p.nombre as potrero,
                           l.nombre as lote, g.nombre as grupo, v.nombre as vendedor,
                           madre.codigo as cod_madre, madre.nombre as nom_madre,
                           padre.codigo as cod_padre, padre.nombre as nom_padre
                    FROM animal a
                    LEFT JOIN finca f ON a.id_finca = f.id
                    LEFT JOIN raza r ON a.raza = r.nombre
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN lote l ON a.id_lote = l.id
                    LEFT JOIN grupo g ON a.id_grupo = g.id
                    LEFT JOIN vendedor v ON a.id_vendedor = v.id
                    LEFT JOIN animal madre ON a.id_madre = madre.id
                    LEFT JOIN animal padre ON a.id_padre = padre.id
                    WHERE a.codigo = ?
                """, (codigo,))
                animal = cursor.fetchone()

            if not animal:
                messagebox.showerror("No encontrado", "No existe un animal con ese código.")
                return

            self.animal_actual = animal
            self.mostrar_informacion_general(animal)
            self.cargar_historial_pesos(animal[0])
            self.cargar_tratamientos(animal[0])
            self.cargar_comentarios(animal[0])
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el animal:\n{e}")

    def mostrar_informacion_general(self, animal):
        """Muestra la información general del animal"""
        info_text = f"""
🐄 **INFORMACIÓN COMPLETA DEL ANIMAL**

🏷️  **CÓDIGO:** {animal[2]}
📛  **NOMBRE:** {animal[3] or 'No asignado'}
🏞️  **FINCA:** {animal[28] or 'No asignada'}
📥  **TIPO INGRESO:** {animal[4]}

⚤  **SEXO:** {animal[5]}
🐄  **RAZA:** {animal[29] or 'No especificada'}
📍  **UBICACIÓN:** 
   • Potrero: {animal[30] or 'No asignado'}
   • Lote: {animal[31] or 'No asignado'} 
   • Grupo: {animal[32] or 'No asignado'}

📅  **FECHAS:**
   • Nacimiento: {animal[10] or 'No registrada'}
   • Compra: {animal[11] or 'No aplica'}
   • Registro: {animal[27]}

👨‍👩‍👧  **INFORMACIÓN PADRES:**
   • Madre: {animal[37] or 'No registrada'} ({animal[38] or ''})
   • Padre: {animal[39] or 'No registrada'} ({animal[40] or ''})
   • Concepción: {animal[18] or 'No aplica'}

⚖️  **PESOS:**
   • Nacimiento: {animal[12] or '0'} kg
   • Compra: {animal[13] or '0'} kg

🏥  **SALUD:** {animal[19]}
✅  **ESTADO:** {animal[20]}
📋  **INVENTARIADO:** {'Sí' if animal[21] == 1 else 'No'}

🎨  **CARACTERÍSTICAS FÍSICAS:**
   • Color: {animal[22] or 'No especificado'}
   • Hierro: {animal[23] or 'No especificado'}
   • N° Hierros: {animal[24] or '0'}
   • Composición Racial: {animal[25] or 'No especificada'}

🛒  **INFORMACIÓN COMPRA:**
   • Vendedor: {animal[33] or 'No aplica'}
   • Precio: ${animal[15] or '0'}

💬  **COMENTARIOS:**
{animal[26] or 'Sin comentarios'}

📁  **FOTO:** {animal[27] or 'No disponible'}
"""
        self.info_general_label.configure(text=info_text)

    def cargar_historial_pesos(self, id_animal):
        """Carga el historial de pesos del animal"""
        for fila in self.tabla_pesos.get_children():
            self.tabla_pesos.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fecha, peso, tipo_peso, comentario 
                    FROM peso 
                    WHERE id_animal = ? 
                    ORDER BY fecha DESC
                """, (id_animal,))
                
                for fila in cursor.fetchall():
                    self.tabla_pesos.insert("", "end", values=fila)
                    
        except Exception as e:
            print(f"Error al cargar pesos: {e}")

    def cargar_tratamientos(self, id_animal):
        """Carga el historial de tratamientos del animal"""
        for fila in self.tabla_tratamientos.get_children():
            self.tabla_tratamientos.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fecha, tipo_tratamiento, producto, veterinario, comentario 
                    FROM tratamiento 
                    WHERE id_animal = ? 
                    ORDER BY fecha DESC
                """, (id_animal,))
                
                for fila in cursor.fetchall():
                    self.tabla_tratamientos.insert("", "end", values=fila)
                    
        except Exception as e:
            print(f"Error al cargar tratamientos: {e}")

    def cargar_comentarios(self, id_animal):
        """Carga el historial de comentarios del animal"""
        for fila in self.tabla_comentarios.get_children():
            self.tabla_comentarios.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fecha, autor, nota 
                    FROM comentario 
                    WHERE id_animal = ? 
                    ORDER BY fecha DESC
                """, (id_animal,))
                
                for fila in cursor.fetchall():
                    self.tabla_comentarios.insert("", "end", values=fila)
                    
        except Exception as e:
            print(f"Error al cargar comentarios: {e}")

    def limpiar_busqueda(self):
        """Limpia la búsqueda y toda la información"""
        self.codigo_entry.delete(0, "end")
        self.animal_actual = None
        self.info_general_label.configure(text="Busque un animal para ver su información")
        
        # Limpiar tablas
        for tabla in [self.tabla_pesos, self.tabla_tratamientos, self.tabla_comentarios]:
            for fila in tabla.get_children():
                tabla.delete(fila)