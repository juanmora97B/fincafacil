"""
Módulo de Reproducción - Control de servicios, gestación y partos
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db
from modules.utils.date_picker import attach_date_picker


class ReproduccionModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        # Título compacto
        titulo = ctk.CTkLabel(self, text="🐄 Gestión Reproductiva", font=("Segoe UI", 22, "bold"))
        titulo.pack(pady=(5, 3))

        # Notebook expandido para ocupar toda la altura disponible
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(3, 5))

        self.frame_servicios = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_servicios, text="➕ Nuevo Servicio")
        
        self.frame_gestantes = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_gestantes, text="🤰 Gestantes")
        
        self.frame_partos = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_partos, text="👶 Próximos Partos")

        self.crear_form_servicio()
        self.crear_lista_gestantes()
        self.crear_proximos_partos()

    def crear_form_servicio(self):
        main = ctk.CTkScrollableFrame(self.frame_servicios)
        main.pack(fill="both", expand=True, padx=2, pady=5)

        ctk.CTkLabel(main, text="📝 Registrar Servicio Reproductivo", 
                    font=("Segoe UI", 16, "bold")).pack(pady=(0, 8))

        form = ctk.CTkFrame(main, corner_radius=10)
        form.pack(fill="both", expand=True, pady=10)

        r1 = ctk.CTkFrame(form, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r1, text="Animal (Hembra)*:", width=150).pack(side="left", padx=5)
        self.cb_animal = ctk.CTkComboBox(r1, width=300)
        self.cb_animal.set("Seleccione la hembra")
        self.cb_animal.pack(side="left", padx=5)
        ctk.CTkButton(r1, text="🔄", command=self.cargar_hembras, width=40).pack(side="left", padx=5)

        r2 = ctk.CTkFrame(form, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r2, text="Fecha Servicio*:", width=150).pack(side="left", padx=5)
        self.e_fecha_serv = ctk.CTkEntry(r2, width=130, placeholder_text="YYYY-MM-DD")
        self.e_fecha_serv.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.e_fecha_serv.pack(side="left", padx=5)
        attach_date_picker(r2, self.e_fecha_serv)
        
        ctk.CTkLabel(r2, text="Tipo*:", width=80).pack(side="left", padx=5)
        self.cb_tipo_serv = ctk.CTkComboBox(r2, values=["Natural", "Inseminacion"], width=150)
        self.cb_tipo_serv.set("Seleccione tipo")
        self.cb_tipo_serv.pack(side="left", padx=5)

        r3 = ctk.CTkFrame(form, fg_color="transparent")
        r3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(r3, text="Toro/Semen:", width=150).pack(side="left", padx=5)
        self.e_toro = ctk.CTkEntry(r3, width=300)
        self.e_toro.pack(side="left", padx=5)

        r4 = ctk.CTkFrame(form, fg_color="transparent")
        r4.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(r4, text="Observaciones:", width=150).pack(side="left", padx=5, anchor="n")
        self.t_obs = ctk.CTkTextbox(r4, width=400, height=120)
        self.t_obs.pack(side="left", padx=5, fill="both", expand=True)

        ctk.CTkButton(form, text="💾 Registrar Servicio", command=self.guardar_servicio,
                     fg_color="green").pack(pady=10)

        # Info
        info = ctk.CTkFrame(main, corner_radius=10, fg_color=("gray85", "gray25"))
        info.pack(fill="x", pady=10)
        ctk.CTkLabel(info, text="ℹ️ Gestación promedio: 280 días (9 meses)", 
                    font=("Segoe UI", 11, "italic")).pack(pady=10)

    def crear_lista_gestantes(self):
        main = ctk.CTkFrame(self.frame_gestantes)
        # Reducción margen horizontal y vertical (20→4, 20→5)
        main.pack(fill="both", expand=True, padx=4, pady=5)

        ctk.CTkLabel(main, text="🤰 Animales en Gestación", 
                    font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.tabla_gest = ttk.Treeview(main, columns=("animal", "fecha_serv", "tipo", "dias", "parto_est"), 
                                       show="headings", height=15)
        for col, txt, w in [("animal", "Animal", 200), ("fecha_serv", "Fecha Servicio", 120),
                            ("tipo", "Tipo", 120), ("dias", "Días Gestación", 120), 
                            ("parto_est", "Parto Estimado", 120)]:
            self.tabla_gest.heading(col, text=txt)
            self.tabla_gest.column(col, width=w, anchor="center")
        self.tabla_gest.pack(fill="both", expand=True, pady=10)

        btn = ctk.CTkFrame(main, fg_color="transparent")
        btn.pack(pady=5)
        ctk.CTkButton(btn, text="✅ Confirmar Parto", command=self.confirmar_parto).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="❌ Marcar Vacía", command=self.marcar_vacia).pack(side="left", padx=5)

    def crear_proximos_partos(self):
        main = ctk.CTkFrame(self.frame_partos)
        # Reducción margen horizontal y vertical (20→4, 20→5)
        main.pack(fill="both", expand=True, padx=4, pady=5)

        ctk.CTkLabel(main, text="👶 Próximos Partos (30 días)", 
                    font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.tabla_partos = ttk.Treeview(main, columns=("animal", "fecha_est", "dias_falta", "tipo"), 
                                        show="headings", height=15)
        for col, txt, w in [("animal", "Animal", 250), ("fecha_est", "Fecha Estimada", 120),
                            ("dias_falta", "Días para Parto", 120), ("tipo", "Tipo Servicio", 120)]:
            self.tabla_partos.heading(col, text=txt)
            self.tabla_partos.column(col, width=w, anchor="center")
        self.tabla_partos.pack(fill="both", expand=True, pady=10)

    def cargar_datos(self):
        self.cargar_hembras()
        self.cargar_gestantes()
        self.cargar_proximos()

    def cargar_hembras(self):
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, codigo, nombre FROM animal 
                    WHERE sexo = 'Hembra' AND estado = 'Activo'
                    ORDER BY codigo
                """)
                hembras = [f"{r[0]}-{r[1]} {r[2] or ''}" for r in cur.fetchall()]
                if hasattr(self, 'cb_animal'):
                    self.cb_animal.configure(values=hembras)
                    if hembras: self.cb_animal.set(hembras[0])
        except: pass

    def guardar_servicio(self):
        if not self.cb_animal.get() or "Seleccione" in self.cb_animal.get():
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        
        if not self.cb_tipo_serv.get() or "Seleccione" in self.cb_tipo_serv.get():
            messagebox.showwarning("Atención", "Seleccione el tipo de servicio")
            return
        
        try:
            # Extraer el ID del formato "ID-CODIGO NOMBRE"
            animal_id = int(self.cb_animal.get().split("-")[0].strip())
            fecha = self.e_fecha_serv.get().strip()
            tipo = self.cb_tipo_serv.get()
            
            # Verificar que el animal existe
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM animal WHERE id = ?", (animal_id,))
                if not cur.fetchone():
                    messagebox.showerror("Error", "El animal seleccionado no existe en la base de datos")
                    return
                
                cur.execute("""
                    INSERT INTO reproduccion (animal_id, fecha_cubricion, tipo_cubricion, 
                                             estado, observaciones)
                    VALUES (?, ?, ?, 'Gestante', ?)
                """, (animal_id, fecha, tipo, self.t_obs.get("1.0", "end-1c").strip() or None))
                conn.commit()
            
            messagebox.showinfo("Éxito", "✅ Servicio registrado")
            self.t_obs.delete("1.0", "end")
            self.cargar_gestantes()
            self.cargar_proximos()
        except ValueError:
            messagebox.showerror("Error", "Formato de animal inválido. Seleccione un animal de la lista")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def cargar_gestantes(self):
        for item in self.tabla_gest.get_children():
            self.tabla_gest.delete(item)
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.codigo || ' ' || COALESCE(a.nombre, ''), r.fecha_cubricion,
                           r.tipo_cubricion, 
                           CAST((julianday('now') - julianday(r.fecha_cubricion)) AS INTEGER) as dias,
                           date(r.fecha_cubricion, '+280 days') as parto_est
                    FROM reproduccion r
                    JOIN animal a ON r.animal_id = a.id
                    WHERE r.estado = 'Gestante'
                    ORDER BY r.fecha_cubricion
                """)
                for r in cur.fetchall():
                    self.tabla_gest.insert("", "end", values=r)
        except: pass

    def cargar_proximos(self):
        for item in self.tabla_partos.get_children():
            self.tabla_partos.delete(item)
        
        try:
            with db.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.codigo || ' ' || COALESCE(a.nombre, ''),
                           date(r.fecha_cubricion, '+280 days') as parto_est,
                           CAST((julianday(date(r.fecha_cubricion, '+280 days')) - julianday('now')) AS INTEGER) as dias_falta,
                           r.tipo_cubricion
                    FROM reproduccion r
                    JOIN animal a ON r.animal_id = a.id
                    WHERE r.estado = 'Gestante' 
                      AND date(r.fecha_cubricion, '+280 days') BETWEEN date('now') AND date('now', '+30 days')
                    ORDER BY parto_est
                """)
                for r in cur.fetchall():
                    self.tabla_partos.insert("", "end", values=r)
        except: pass

    def confirmar_parto(self):
        sel = self.tabla_gest.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un animal gestante")
            return
        
        animal = self.tabla_gest.item(sel[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", f"¿Confirmar parto de {animal}?"):
            try:
                with db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE reproduccion SET estado = 'Parida', fecha_parto = date('now')
                        WHERE animal_id = (SELECT id FROM animal WHERE codigo = ?) 
                          AND estado = 'Gestante'
                    """, (animal.split()[0],))
                    conn.commit()
                messagebox.showinfo("Éxito", "Parto confirmado")
                self.cargar_gestantes()
                self.cargar_proximos()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def marcar_vacia(self):
        sel = self.tabla_gest.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un animal")
            return
        
        animal = self.tabla_gest.item(sel[0])["values"][0]
        
        if messagebox.askyesno("Confirmar", f"¿Marcar {animal} como vacía?"):
            try:
                with db.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE reproduccion SET estado = 'Vacía'
                        WHERE animal_id = (SELECT id FROM animal WHERE codigo = ?) 
                          AND estado = 'Gestante'
                    """, (animal.split()[0],))
                    conn.commit()
                messagebox.showinfo("Éxito", "Animal marcada como vacía")
                self.cargar_gestantes()
            except Exception as e:
                messagebox.showerror("Error", str(e))
