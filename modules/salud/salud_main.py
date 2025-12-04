"""
Módulo de Eventos de Salud - Diagnósticos veterinarios
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.date_picker import attach_date_picker


class SaludModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Título compacto
        titulo = ctk.CTkLabel(self, text="🏥 Eventos de Salud", font=("Segoe UI", 22, "bold"))
        titulo.pack(pady=(5, 3))

        # Notebook expandido para ocupar toda la altura disponible
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        self.frame_registro = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_registro, text="➕ Nuevo Diagnóstico")
        
        self.frame_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_historial, text="📋 Historial")

        self.crear_form_diagnostico()
        self.crear_historial()

    def crear_form_diagnostico(self):
        main = ctk.CTkScrollableFrame(self.frame_registro)
        main.pack(fill="both", expand=True, padx=2, pady=5)

        ctk.CTkLabel(main, text="📝 Registrar Evento de Salud", 
                    font=("Segoe UI", 16, "bold")).pack(pady=(3, 8))

        form = ctk.CTkFrame(main, corner_radius=10)
        form.pack(fill="both", expand=True, pady=5)

        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r1, text="Animal*:", width=150).pack(side="left", padx=5)
        self.cb_animal = ctk.CTkComboBox(r1, width=300)
        self.cb_animal.set("Seleccione el animal")
        self.cb_animal.pack(side="left", padx=5)
        ctk.CTkButton(r1, text="🔄", command=self.cargar_animales, width=40).pack(side="left", padx=5)

        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r2, text="Fecha*:", width=150).pack(side="left", padx=5)
        self.e_fecha = ctk.CTkEntry(r2, width=130, placeholder_text="YYYY-MM-DD")
        self.e_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha.pack(side="left", padx=5)
        attach_date_picker(r2, self.e_fecha)
        
        ctk.CTkLabel(r2, text="Tipo*:", width=80).pack(side="left", padx=5)
        self.cb_tipo = ctk.CTkComboBox(r2, values=["Enfermedad", "Lesión", "Revisión", "Vacunación", "Otro"], width=150)
        self.cb_tipo.set("Seleccione tipo")
        self.cb_tipo.pack(side="left", padx=5)

        r3 = ctk.CTkFrame(form, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r3, text="Diagnóstico*:", width=150).pack(side="left", padx=5, anchor="n")
        self.t_diagnostico = ctk.CTkTextbox(r3, width=400, height=120)
        self.t_diagnostico.pack(side="left", padx=5, fill="both", expand=True)

        r4 = ctk.CTkFrame(form, fg_color="transparent")
        r4.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r4, text="Severidad*:", width=150).pack(side="left", padx=5)
        self.cb_severidad = ctk.CTkComboBox(r4, values=["Leve", "Moderada", "Grave", "Crítica"], width=150)
        self.cb_severidad.set("Seleccione severidad")
        self.cb_severidad.pack(side="left", padx=5)
        
        ctk.CTkLabel(r4, text="Estado*:", width=100).pack(side="left", padx=5)
        self.cb_estado = ctk.CTkComboBox(r4, values=["Activo", "En Tratamiento", "Recuperado", "Crónico"], width=150)
        self.cb_estado.set("Seleccione estado")
        self.cb_estado.pack(side="left", padx=5)

        r5 = ctk.CTkFrame(form, fg_color="transparent")
        r5.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(r5, text="Observaciones:", width=150).pack(side="left", padx=5, anchor="n")
        self.t_obs = ctk.CTkTextbox(r5, width=400, height=100)
        self.t_obs.pack(side="left", padx=5, fill="both", expand=True)

        ctk.CTkButton(form, text="💾 Registrar Diagnóstico", command=self.guardar_diagnostico,
                     fg_color="green").pack(pady=10)

    def crear_historial(self):
        main = ctk.CTkFrame(self.frame_historial)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        top = ctk.CTkFrame(main, fg_color="transparent")
        top.pack(fill="x", pady=10)
        
        ctk.CTkLabel(top, text="🏥 Historial de Eventos", 
                    font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        
        ctk.CTkButton(top, text="🔄 Actualizar", command=self.cargar_historial).pack(side="right", padx=5)

        self.tabla_hist = ttk.Treeview(main, columns=("fecha", "animal", "tipo", "diagnostico", "severidad", "estado"), 
                                       show="headings", height=15)
        for col, txt, w in [("fecha", "Fecha", 100), ("animal", "Animal", 150),
                            ("tipo", "Tipo", 100), ("diagnostico", "Diagnóstico", 200),
                            ("severidad", "Severidad", 100), ("estado", "Estado", 120)]:
            self.tabla_hist.heading(col, text=txt)
            self.tabla_hist.column(col, width=w, anchor="center" if col in ["fecha", "tipo", "severidad", "estado"] else "w")
        self.tabla_hist.pack(fill="both", expand=True, pady=10)
        self.tabla_hist.bind("<Double-1>", lambda e: self.ver_detalle())

        btn = ctk.CTkFrame(main, fg_color="transparent")
        btn.pack(pady=5)
        ctk.CTkButton(btn, text="👁️ Ver Detalle", command=self.ver_detalle).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="✏️ Actualizar Estado", command=self.actualizar_estado).pack(side="left", padx=5)

    def cargar_datos(self):
        self.cargar_animales()
        self.cargar_historial()

    def cargar_animales(self):
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, codigo, nombre FROM animal 
                    WHERE estado = 'Activo'
                    ORDER BY codigo
                """)
                animales = [f"{r[0]}-{r[1]} {r[2] or ''}" for r in cur.fetchall()]
                if hasattr(self, 'cb_animal'):
                    self.cb_animal.configure(values=animales)
                    if animales: self.cb_animal.set(animales[0])
        except: pass

    def guardar_diagnostico(self):
        if not self.cb_animal.get() or "Seleccione" in self.cb_animal.get():
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        
        if not self.t_diagnostico.get("1.0", "end-1c").strip():
            messagebox.showwarning("Atención", "Ingrese el diagnóstico")
            return
        
        try:
            # Extraer el ID del formato "ID-CODIGO NOMBRE"
            animal_id = int(self.cb_animal.get().split("-")[0].strip())
            fecha = self.e_fecha.get().strip()
            tipo = self.cb_tipo.get()
            diagnostico = self.t_diagnostico.get("1.0", "end-1c").strip()
            severidad = self.cb_severidad.get()
            estado = self.cb_estado.get()
            obs = self.t_obs.get("1.0", "end-1c").strip() or None
            
            with db.get_connection() as conn:
                cur = conn.cursor()
                
                # Verificar que el animal existe
                cur.execute("SELECT id FROM animal WHERE id = ?", (animal_id,))
                if not cur.fetchone():
                    messagebox.showerror("Error", "El animal seleccionado no existe en la base de datos")
                    return
                
                cur.execute("""
                    INSERT INTO diagnostico_evento (animal_id, fecha, tipo, detalle, 
                                                   severidad, estado, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (animal_id, fecha, tipo, diagnostico, severidad, estado, obs))
                conn.commit()
            
            messagebox.showinfo("Éxito", "✅ Diagnóstico registrado")
            self.t_diagnostico.delete("1.0", "end")
            self.t_obs.delete("1.0", "end")
            self.cargar_historial()
        except ValueError:
            messagebox.showerror("Error", "Formato de animal inválido. Seleccione un animal de la lista")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def cargar_historial(self):
        for item in self.tabla_hist.get_children():
            self.tabla_hist.delete(item)
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT d.id, d.fecha, a.codigo || ' ' || COALESCE(a.nombre, ''),
                           d.tipo, SUBSTR(d.detalle, 1, 50) || CASE WHEN LENGTH(d.detalle) > 50 THEN '...' ELSE '' END,
                           d.severidad, d.estado
                    FROM diagnostico_evento d
                    JOIN animal a ON d.animal_id = a.id
                    ORDER BY d.fecha DESC
                    LIMIT 100
                """)
                for r in cur.fetchall():
                    self.tabla_hist.insert("", "end", iid=r[0], values=r[1:])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar historial:\n{e}")

    def ver_detalle(self):
        sel = self.tabla_hist.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un registro")
            return
        
        try:
            evento_id = sel[0]
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT d.fecha, a.codigo || ' ' || COALESCE(a.nombre, ''),
                           d.tipo, d.detalle, d.severidad, d.estado, d.observaciones
                    FROM diagnostico_evento d
                    JOIN animal a ON d.animal_id = a.id
                    WHERE d.id = ?
                """, (evento_id,))
                r = cur.fetchone()
            
            if r:
                ventana = ctk.CTkToplevel(self)
                ventana.title("Detalle Diagnóstico")
                ventana.geometry("600x500")
                
                ctk.CTkLabel(ventana, text="🏥 Detalle del Diagnóstico", 
                            font=("Segoe UI", 18, "bold")).pack(pady=5)
                
                info = ctk.CTkFrame(ventana, corner_radius=10)
                # Compactar ancho (padx 20→4)
                info.pack(fill="both", expand=True, padx=4, pady=10)
                
                datos = [
                    ("📅 Fecha:", r[0]),
                    ("🐄 Animal:", r[1]),
                    ("🏷️ Tipo:", r[2]),
                    ("💊 Severidad:", r[4]),
                    ("📊 Estado:", r[5]),
                    ("📝 Diagnóstico:", r[3]),
                    ("💬 Observaciones:", r[6] or "Sin observaciones")
                ]
                
                for label, valor in datos:
                    f = ctk.CTkFrame(info, fg_color="transparent")
                    f.pack(fill="x", padx=10, pady=5)
                    ctk.CTkLabel(f, text=label, font=("Segoe UI", 11, "bold"), width=150, anchor="w").pack(side="left", padx=5)
                    ctk.CTkLabel(f, text=str(valor), wraplength=380, anchor="w").pack(side="left", padx=5, fill="x", expand=True)
                
                ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_estado(self):
        sel = self.tabla_hist.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un diagnóstico")
            return
        
        ventana = ctk.CTkToplevel(self)
        ventana.title("Actualizar Estado")
        ventana.geometry("400x200")
        
        ctk.CTkLabel(ventana, text="Nuevo Estado:", font=("Segoe UI", 12, "bold")).pack(pady=10)
        cb_nuevo = ctk.CTkComboBox(ventana, values=["Activo", "En Tratamiento", "Recuperado", "Crónico"], width=250)
        cb_nuevo.pack(pady=10)
        
        def guardar():
            try:
                with db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE diagnostico_evento SET estado = ? WHERE id = ?", 
                               (cb_nuevo.get(), sel[0]))
                    conn.commit()
                messagebox.showinfo("Éxito", "Estado actualizado")
                ventana.destroy()
                self.cargar_historial()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ctk.CTkButton(ventana, text="💾 Guardar", command=guardar, fg_color="green").pack(pady=10)
