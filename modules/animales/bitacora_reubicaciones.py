import customtkinter as ctk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db

class BitacoraReubicacionesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.mostrar()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="📦 Bitácora de Reubicaciones", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame de la tabla
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar tabla
        self.tabla = ttk.Treeview(table_frame, 
                                 columns=("codigo", "potrero_ant", "potrero_nuevo", "fecha", "motivo"), 
                                 show="headings",
                                 height=15)
        
        # Configurar columnas
        column_config = [
            ("codigo", "Código Animal", 120),
            ("potrero_ant", "Potrero Anterior", 150),
            ("potrero_nuevo", "Potrero Nuevo", 150),
            ("fecha", "Fecha", 120),
            ("motivo", "Motivo", 200)
        ]
        
        for col, heading, width in column_config:
            self.tabla.heading(col, text=heading)
            self.tabla.column(col, width=width, anchor="center")

        self.tabla.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Botón actualizar
        btn_actualizar = ctk.CTkButton(self, text="🔄 Actualizar Lista", command=self.mostrar)
        btn_actualizar.pack(pady=5)

    def mostrar(self):
        """Muestra el historial de reubicaciones - VERSIÓN CORREGIDA"""
        # Limpiar tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Consulta alternativa usando comentarios para reubicaciones
                cursor.execute("""
                    SELECT a.codigo, 
                           'Ver historial' as potrero_anterior,
                           'Ver historial' as potrero_nuevo,
                           c.fecha, 
                           c.nota
                    FROM comentario c
                    JOIN animal a ON c.id_animal = a.id
                    WHERE (c.nota LIKE '%reubicación%' OR c.nota LIKE '%potrero%' 
                           OR c.nota LIKE '%Reubicación%' OR c.nota LIKE '%traslado%')
                    ORDER BY c.fecha DESC
                """)
                
                for fila in cursor.fetchall():
                    # Limitar longitud del motivo para mejor visualización
                    motivo = fila[4]
                    if len(motivo) > 100:
                        motivo = motivo[:100] + "..."
                    
                    valores = (
                        fila[0],  # código
                        fila[1],  # potrero anterior
                        fila[2],  # potrero nuevo  
                        fila[3],  # fecha
                        motivo    # motivo
                    )
                    self.tabla.insert("", "end", values=valores)
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las reubicaciones:\n{e}")