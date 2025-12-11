import customtkinter as ctk
from tkinter import ttk, messagebox
from modules.utils import database_helpers as db

class InventarioRapido(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.finca_seleccionada = None
        self.animales = []
        self.crear_widgets()

    def crear_widgets(self):
        # Dropdown de fincas
        fincas = self.obtener_fincas()
        self.combo_finca = ctk.CTkComboBox(self, values=[f[1] for f in fincas], width=250)
        self.combo_finca.pack(pady=10)
        self.combo_finca.bind("<<ComboboxSelected>>", self.cargar_animales_finca)

        # Búsqueda rápida
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10)
        ctk.CTkLabel(search_frame, text="Buscar por ID animal:").pack(side="left", padx=5)
        self.entry_busqueda = ctk.CTkEntry(search_frame, width=120)
        self.entry_busqueda.pack(side="left", padx=5)
        self.entry_busqueda.bind("<KeyRelease>", self.buscar_animal)

        # Filtros
        self.filtro_var = ctk.StringVar(value="Todos")
        filtro_frame = ctk.CTkFrame(self)
        filtro_frame.pack(fill="x", padx=10, pady=4)
        for txt in ["Todos", "Sin inventariar", "Inventariados"]:
            ctk.CTkRadioButton(filtro_frame, text=txt, variable=self.filtro_var, value=txt, command=self.actualizar_filtro).pack(side="left", padx=5)

        # Tabla de animales
        self.tabla = ttk.Treeview(self, columns=("id", "nombre", "peso_anterior", "peso_actual", "ganancia", "tratamientos", "observaciones", "inventariado"), show="headings", height=18)
        for col, txt, w in zip(self.tabla["columns"], ["ID", "Nombre", "Peso Anterior", "Peso Actual", "Ganancia/Pérdida", "Tratamientos", "Observaciones", "Inventariado"], [60, 140, 100, 100, 120, 140, 180, 100]):
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabla.bind("<Double-1>", self.editar_fila)

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Botones de guardado
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", pady=8)
        ctk.CTkButton(btn_frame, text="Guardar fila", command=self.guardar_fila).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Guardar todo", command=self.guardar_todo).pack(side="left", padx=10)

    def obtener_fincas(self):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM finca WHERE activo = 1")
            return cursor.fetchall()

    def cargar_animales_finca(self, event=None):
        finca_nombre = self.combo_finca.get()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM finca WHERE nombre = ?", (finca_nombre,))
            finca_id = cursor.fetchone()[0]
            cursor.execute("SELECT codigo, nombre, peso_actual, peso_anterior, inventariado FROM animal WHERE id_finca = ? AND estado = 'Activo'", (finca_id,))
            self.animales = cursor.fetchall()
        self.refrescar_tabla()

    def refrescar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        filtro = self.filtro_var.get()
        for a in self.animales:
            mostrar = (
                filtro == "Todos" or
                (filtro == "Sin inventariar" and not a[4]) or
                (filtro == "Inventariados" and a[4])
            )
            if mostrar:
                ganancia = (a[2] or 0) - (a[3] or 0)
                color = "#d4ffd4" if a[4] else "white"
                self.tabla.insert("", "end", values=(a[0], a[1], a[3], a[2], ganancia, "", "", a[4]), tags=("inventariado" if a[4] else "normal",))
                self.tabla.tag_configure("inventariado", background=color)
                self.tabla.tag_configure("normal", background="white")

    def buscar_animal(self, event=None):
        query = self.entry_busqueda.get().strip()
        for item in self.tabla.get_children():
            vals = self.tabla.item(item)["values"]
            if query and not str(vals[0]).startswith(query):
                self.tabla.detach(item)
            else:
                self.tabla.reattach(item, "", "end")

    def actualizar_filtro(self):
        self.refrescar_tabla()

    def editar_fila(self, event):
        item = self.tabla.focus()
        vals = self.tabla.item(item)["values"]
        win = ctk.CTkToplevel(self)
        win.title(f"Editar animal {vals[0]}")
        win.geometry("500x400")
        ctk.CTkLabel(win, text=f"Animal: {vals[1]}", font=("Segoe UI", 16)).pack(pady=10)
        ctk.CTkLabel(win, text="Peso Actual:").pack(anchor="w", padx=10)
        entry_peso = ctk.CTkEntry(win, width=120)
        entry_peso.insert(0, vals[3])
        entry_peso.pack(pady=4)
        ctk.CTkLabel(win, text="Tratamientos:").pack(anchor="w", padx=10)
        combo_trat = ctk.CTkComboBox(win, values=["Vitaminas", "Desparasitante", "Vacunas", "Otro"], width=180)
        combo_trat.pack(pady=4)
        ctk.CTkLabel(win, text="Observaciones:").pack(anchor="w", padx=10)
        entry_obs = ctk.CTkEntry(win, width=250)
        entry_obs.pack(pady=4)
        invent_var = ctk.BooleanVar(value=bool(vals[7]))
        ctk.CTkCheckBox(win, text="Inventariado", variable=invent_var).pack(pady=4)
        def guardar():
            try:
                peso_actual = float(entry_peso.get())
                if peso_actual <= 0:
                    messagebox.showwarning("Validación", "El peso actual debe ser mayor a 0.")
                    return
                peso_anterior = float(vals[2]) if vals[2] else 0
                if abs(peso_actual - peso_anterior) > max(0.2 * peso_anterior, 10):
                    messagebox.showwarning("Advertencia", "El peso actual difiere más de un 20% del anterior.")
                # Guardar en BD
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE animal SET peso_actual = ?, tratamientos = ?, observaciones = ?, inventariado = ? WHERE codigo = ?", (peso_actual, combo_trat.get(), entry_obs.get(), invent_var.get(), vals[0]))
                    conn.commit()
                self.cargar_animales_finca()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        ctk.CTkButton(win, text="Guardar", command=guardar).pack(pady=10)

    def guardar_fila(self):
        self.editar_fila(None)

    def guardar_todo(self):
        for item in self.tabla.get_children():
            vals = self.tabla.item(item)["values"]
            try:
                peso_actual = float(vals[3])
                if peso_actual <= 0:
                    continue
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE animal SET peso_actual = ?, inventariado = ? WHERE codigo = ?", (peso_actual, vals[7], vals[0]))
                    conn.commit()
            except:
                continue
        messagebox.showinfo("Inventario Rápido", "Guardado masivo completado.")
