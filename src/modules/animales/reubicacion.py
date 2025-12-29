import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from database.database import get_db_connection, reubicar_animal
from modules.utils.date_picker import attach_date_picker

class ReubicacionFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.animal_actual = None
        self.finca_id_map = {}
        self.potrero_id_map = {}
        self.sector_id_map = {}
        self.lote_id_map = {}
        self.crear_widgets()

    def _cargar_fincas_destino(self):
        self.finca_id_map.clear()
        values = ["(Seleccione finca)"]
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca WHERE estado IN ('Activo','Activa')")
                for r in cur.fetchall():
                    try:
                        fid = r['id'] if hasattr(r, 'keys') else r[0]
                        fname = r['nombre'] if hasattr(r, 'keys') else r[1]
                    except (KeyError, IndexError):
                        continue
                    label = f"{fid} - {fname}"
                    self.finca_id_map[label] = fid
                    values.append(label)
        except Exception as e:
            messagebox.showerror("Fincas", f"No se pudieron cargar fincas: {e}")
        self.cb_finca_destino.configure(values=values)
        self.cb_finca_destino.set(values[0])

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="🚚 Reubicación de Animales", font=("Segoe UI", 22, "bold"))
        titulo.pack(pady=15)

        # Frame principal con scroll
        main_container = ctk.CTkScrollableFrame(self, corner_radius=10)
        main_container.pack(pady=10, padx=20, fill="both", expand=True)

        # Sección 1: Búsqueda del Animal
        seccion1 = ctk.CTkFrame(main_container, corner_radius=10, fg_color=("#f0f0f0", "#2b2b2b"))
        seccion1.pack(pady=(0, 15), padx=10, fill="x")
        
        ctk.CTkLabel(seccion1, text="📋 Búsqueda del Animal", font=("Segoe UI", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
        
        search_frame = ctk.CTkFrame(seccion1, fg_color="transparent")
        search_frame.pack(pady=5, padx=10, fill="x")
        search_frame.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Código Animal:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky='e', padx=(0,10), pady=8)
        self.codigo_entry = ctk.CTkEntry(search_frame, placeholder_text="Ingrese código del animal", height=35)
        self.codigo_entry.grid(row=0, column=1, sticky='ew', padx=(0,10), pady=8)
        ctk.CTkButton(search_frame, text="🔍 Buscar", command=self.ver_animal, width=120, height=35).grid(row=0, column=2, padx=(0,10), pady=8)
        
        # Info del animal
        self.label_info_animal = ctk.CTkLabel(seccion1, text="Ingrese el código del animal para ver su información", font=("Segoe UI", 11), justify="left", text_color="gray")
        self.label_info_animal.pack(pady=(5, 10), padx=10, anchor="w")
        
        # Finca origen
        self.lbl_origen = ctk.CTkLabel(seccion1, text="Finca Origen: -", font=("Segoe UI", 12, "bold"))
        self.lbl_origen.pack(pady=(0, 10), padx=10, anchor="w")

        # Sección 2: Ubicación Destino
        seccion2 = ctk.CTkFrame(main_container, corner_radius=10, fg_color=("#f0f0f0", "#2b2b2b"))
        seccion2.pack(pady=(0, 15), padx=10, fill="x")
        
        ctk.CTkLabel(seccion2, text="📍 Ubicación Destino", font=("Segoe UI", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
        
        dest_frame = ctk.CTkFrame(seccion2, fg_color="transparent")
        dest_frame.pack(pady=5, padx=10, fill="x")
        dest_frame.columnconfigure(1, weight=1)
        dest_frame.columnconfigure(3, weight=1)
        
        ctk.CTkLabel(dest_frame, text="Finca Destino:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky='e', padx=(0,10), pady=8)
        self.cb_finca_destino = ctk.CTkComboBox(dest_frame, values=["(Seleccione finca)"], height=35)
        self.cb_finca_destino.grid(row=0, column=1, columnspan=3, sticky='ew', padx=(0,10), pady=8)
        
        ctk.CTkLabel(dest_frame, text="Potrero:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky='e', padx=(0,10), pady=8)
        self.cb_potrero = ctk.CTkComboBox(dest_frame, values=["(Seleccione)"], state="disabled", height=35)
        self.cb_potrero.grid(row=1, column=1, sticky='ew', padx=(0,10), pady=8)
        
        ctk.CTkLabel(dest_frame, text="Sector:", font=("Segoe UI", 12)).grid(row=1, column=2, sticky='e', padx=(10,10), pady=8)
        self.cb_sector = ctk.CTkComboBox(dest_frame, values=["(Seleccione)"], state="disabled", height=35)
        self.cb_sector.grid(row=1, column=3, sticky='ew', padx=(0,10), pady=8)
        
        ctk.CTkLabel(dest_frame, text="Lote:", font=("Segoe UI", 12)).grid(row=2, column=0, sticky='e', padx=(0,10), pady=8)
        self.cb_lote = ctk.CTkComboBox(dest_frame, values=["(Seleccione)"], state="disabled", height=35)
        self.cb_lote.grid(row=2, column=1, sticky='ew', padx=(0,10), pady=8)
        
        ctk.CTkButton(dest_frame, text="🔄 Refrescar", command=self._refrescar_destino, width=120, height=35).grid(row=2, column=2, columnspan=2, padx=(10,10), pady=8)
        
        # Sección 3: Detalles de la Reubicación
        seccion3 = ctk.CTkFrame(main_container, corner_radius=10, fg_color=("#f0f0f0", "#2b2b2b"))
        seccion3.pack(pady=(0, 15), padx=10, fill="x")
        
        ctk.CTkLabel(seccion3, text="📝 Detalles de la Reubicación", font=("Segoe UI", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
        
        details_frame = ctk.CTkFrame(seccion3, fg_color="transparent")
        details_frame.pack(pady=5, padx=10, fill="x")
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(3, weight=1)
        
        ctk.CTkLabel(details_frame, text="Fecha:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky='e', padx=(0,10), pady=8)
        fecha_row = ctk.CTkFrame(details_frame, fg_color="transparent")
        self.fecha_entry = ctk.CTkEntry(fecha_row, placeholder_text="YYYY-MM-DD", height=35)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.fecha_entry.pack(side='left', fill='x', expand=True)
        attach_date_picker(fecha_row, self.fecha_entry)
        fecha_row.grid(row=0, column=1, sticky='ew', padx=(0,10), pady=8)
        
        motivos = [
            "Manejo",
            "Cambio de potrero",
            "Enfermedad",
            "Producción",
            "Venta interna",
            "Rotación de pasto",
            "Otro",
        ]
        ctk.CTkLabel(details_frame, text="Motivo:", font=("Segoe UI", 12)).grid(row=0, column=2, sticky='e', padx=(10,10), pady=8)
        self.cb_motivo = ctk.CTkComboBox(details_frame, values=motivos, height=35)
        self.cb_motivo.set(motivos[0])
        self.cb_motivo.grid(row=0, column=3, sticky='ew', padx=(0,10), pady=8)
        
        ctk.CTkLabel(details_frame, text="Usuario:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky='e', padx=(0,10), pady=8)
        self.autor_entry = ctk.CTkEntry(details_frame, placeholder_text="Nombre del usuario", height=35)
        self.autor_entry.grid(row=1, column=1, sticky='ew', padx=(0,10), pady=(8,10))
        
        # Botón de acción
        btn_frame = ctk.CTkFrame(seccion3, fg_color="transparent")
        btn_frame.pack(pady=(5, 15))
        ctk.CTkButton(btn_frame, text="💾 Guardar Reubicación", command=self.guardar, width=200, height=40, font=("Segoe UI", 13, "bold")).pack()

        # Bind cambios
        self.cb_finca_destino.bind("<<ComboboxSelected>>", lambda _e=None: self._on_finca_destino())
        self.codigo_entry.bind("<Return>", lambda e: self.ver_animal())
        # Inicializar fincas destino
        self._cargar_fincas_destino()

    def ver_animal(self):
        """Muestra información del animal y setea Finca Origen"""
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código de animal.")
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.id, a.codigo, a.nombre,
                           p.nombre as potrero_actual,
                           f.nombre as finca,
                           a.id_finca,
                           (SELECT nombre FROM sector WHERE id=a.id_sector) as sector_actual,
                           (SELECT nombre FROM lote WHERE id=a.lote_id) as lote_actual
                    FROM animal a
                    LEFT JOIN potrero p ON a.id_potrero = p.id
                    LEFT JOIN finca f ON a.id_finca = f.id
                    WHERE a.codigo = ? AND a.estado = 'Activo'
                """, (codigo,))
                
                animal = cursor.fetchone()

                if animal:
                    try:
                        animal_id = animal['id'] if hasattr(animal, 'keys') else animal[0]
                        codigo_animal = animal['codigo'] if hasattr(animal, 'keys') else animal[1]
                        nombre = animal['nombre'] if hasattr(animal, 'keys') else animal[2]
                        potrero_actual = animal['potrero_actual'] if hasattr(animal, 'keys') else animal[3]
                        finca = animal['finca'] if hasattr(animal, 'keys') else animal[4]
                        id_finca = animal['id_finca'] if hasattr(animal, 'keys') else animal[5]
                        sector_actual = animal['sector_actual'] if hasattr(animal, 'keys') else animal[6]
                        lote_actual = animal['lote_actual'] if hasattr(animal, 'keys') else animal[7]
                    except (KeyError, IndexError) as e:
                        messagebox.showerror("Error", f"Error al leer datos del animal: {e}")
                        return
                    self.animal_actual = {
                        'id': animal_id,
                        'codigo': codigo_animal,
                        'nombre': nombre,
                        'finca': finca,
                        'potrero': potrero_actual,
                        'sector': sector_actual,
                        'lote': lote_actual,
                        'id_finca': id_finca,
                    }
                    info_text = f"""
🐄 **INFORMACIÓN DEL ANIMAL**

🏷️  **CÓDIGO:** {codigo_animal}
📛  **NOMBRE:** {nombre or 'No asignado'}
🏞️  **FINCA:** {finca or 'No asignada'}
📍  **POTRERO ACTUAL:** {potrero_actual or 'No asignado'}
🧱  **SECTOR:** {sector_actual or 'No asignado'}
📦  **LOTE:** {lote_actual or 'No asignado'}

*Listo para reubicación*
"""
                    self.label_info_animal.configure(text=info_text, text_color="black")
                    self.lbl_origen.configure(text=f"Finca Origen: {finca or '-'}")
                    # Sugerir finca destino igual a origen por defecto
                    if self.cb_finca_destino.get() == "(Seleccione finca)" and id_finca:
                        # set by label match
                        for label, fid in self.finca_id_map.items():
                            if fid == id_finca:
                                self.cb_finca_destino.set(label)
                                break
                        self._on_finca_destino()
                else:
                    self.label_info_animal.configure(text="❌ Animal no encontrado o inactivo", text_color="red")
                    self._cargar_fincas_destino()
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el animal:\n{e}")

    def _on_finca_destino(self):
        choice = self.cb_finca_destino.get()
        fid = self.finca_id_map.get(choice)
        # reset combos
        self.cb_potrero.configure(values=["(Seleccione)"], state=("normal" if fid else "disabled"))
        self.cb_potrero.set("(Seleccione)")
        self.cb_sector.configure(values=["(Seleccione)"], state=("normal" if fid else "disabled"))
        self.cb_sector.set("(Seleccione)")
        self.cb_lote.configure(values=["(Seleccione)"], state=("normal" if fid else "disabled"))
        self.cb_lote.set("(Seleccione)")
        self.potrero_id_map.clear()
        self.sector_id_map.clear()
        self.lote_id_map.clear()
        if not fid:
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM potrero WHERE estado='Activo' AND id_finca=? ORDER BY nombre", (fid,))
                potreros = cur.fetchall()
                pot_vals = ["(Seleccione)"]
                for r in potreros:
                    try:
                        pid = r['id'] if hasattr(r, 'keys') else r[0]
                        pnom = r['nombre'] if hasattr(r, 'keys') else r[1]
                    except (KeyError, IndexError):
                        continue
                    lab = f"{pid} - {pnom}"
                    self.potrero_id_map[lab] = pid
                    pot_vals.append(lab)
                self.cb_potrero.configure(values=pot_vals)
                self.cb_potrero.set(pot_vals[0])

                cur.execute("SELECT id, nombre FROM sector WHERE estado IN ('Activo','Activa') AND finca_id=? ORDER BY nombre", (fid,))
                sectores = cur.fetchall()
                sec_vals = ["(Seleccione)"]
                for r in sectores:
                    try:
                        sid = r['id'] if hasattr(r, 'keys') else r[0]
                        snom = r['nombre'] if hasattr(r, 'keys') else r[1]
                    except (KeyError, IndexError):
                        continue
                    lab = f"{sid} - {snom}"
                    self.sector_id_map[lab] = sid
                    sec_vals.append(lab)
                self.cb_sector.configure(values=sec_vals)
                self.cb_sector.set(sec_vals[0])

                cur.execute("SELECT id, nombre FROM lote WHERE estado IN ('Activo','Activa') AND finca_id=? ORDER BY nombre", (fid,))
                lotes = cur.fetchall()
                lot_vals = ["(Seleccione)"]
                for r in lotes:
                    try:
                        lid = r['id'] if hasattr(r, 'keys') else r[0]
                        lnom = r['nombre'] if hasattr(r, 'keys') else r[1]
                    except (KeyError, IndexError):
                        continue
                    lab = f"{lid} - {lnom}"
                    self.lote_id_map[lab] = lid
                    lot_vals.append(lab)
                self.cb_lote.configure(values=lot_vals)
                self.cb_lote.set(lot_vals[0])
        except Exception as e:
            messagebox.showerror("Destino", f"No se pudieron cargar datos de la finca destino: {e}")

    def validar_datos(self):
        codigo = self.codigo_entry.get().strip()
        fecha = self.fecha_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese código del animal.")
            return False
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atención", "Formato de fecha inválido. Use YYYY-MM-DD")
            return False
        if self.cb_finca_destino.get() == "(Seleccione finca)":
            messagebox.showwarning("Atención", "Seleccione la finca destino.")
            return False
        if self.cb_potrero.get() == "(Seleccione)":
            messagebox.showwarning("Atención", "Seleccione el potrero destino.")
            return False
        return True

    def guardar(self):
        if not self.validar_datos():
            return

        if not self.animal_actual:
            messagebox.showwarning("Atención", "Primero busque el animal.")
            return

        fecha = self.fecha_entry.get().strip()
        motivo = self.cb_motivo.get().strip()
        autor = self.autor_entry.get().strip() or "Sistema"

        # IDs destino
        finca_label = self.cb_finca_destino.get()
        to_finca_id = self.finca_id_map.get(finca_label)
        pot_label = self.cb_potrero.get()
        to_potrero_id = self.potrero_id_map.get(pot_label)
        sec_label = self.cb_sector.get()
        to_sector_id = self.sector_id_map.get(sec_label)
        lot_label = self.cb_lote.get()
        to_lote_id = self.lote_id_map.get(lot_label)

        if not to_potrero_id:
            messagebox.showerror("Reubicación", "Seleccione un potrero destino válido.")
            return

        # Validar que destino no sea igual al actual
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id_potrero FROM animal WHERE id=?", (self.animal_actual['id'],))
                r = cur.fetchone()
                actual_id = r['id_potrero'] if hasattr(r, 'keys') else (r[0] if r else None)
                if str(actual_id) == str(to_potrero_id):
                    messagebox.showerror("Reubicación", "El destino es igual al potrero actual.")
                    return
        except Exception:
            pass

        # Ejecutar operación de reubicación transaccional
        ok = reubicar_animal(
            self.animal_actual['id'],
            str(to_potrero_id),
            motivo,
            autor,
            fecha,
            to_finca_id,
            to_sector_id,
            to_lote_id,
        )
        if ok:
            # Confirmación
            destino_finca_txt = finca_label.split(' - ',1)[-1] if ' - ' in finca_label else finca_label
            msg = (
                "Reubicación registrada\n\n"
                f"De: {self.animal_actual.get('finca','-')} / {self.animal_actual.get('potrero','-')}\n"
                f"A: {destino_finca_txt} / {pot_label}\n"
                f"Fecha: {fecha}\n"
            )
            messagebox.showinfo("Reubicación", msg)
            self.limpiar_formulario()
        else:
            messagebox.showerror("Reubicación", "No se pudo registrar la reubicación")

    def limpiar_formulario(self):
        self.codigo_entry.delete(0, "end")
        self.label_info_animal.configure(text="Ingrese el código del animal para ver su información actual", text_color="gray")
        self.lbl_origen.configure(text="Finca Origen: -")
        self.cb_finca_destino.set("(Seleccione finca)")
        self.cb_potrero.configure(values=["(Seleccione)"], state="disabled")
        self.cb_sector.configure(values=["(Seleccione)"], state="disabled")
        self.cb_lote.configure(values=["(Seleccione)"], state="disabled")
        self.cb_motivo.set(self.cb_motivo.cget('values')[0])
        self.autor_entry.delete(0, "end")
        self.fecha_entry.delete(0, "end")
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def _refrescar_destino(self):
        # Refrescar solo datos de la finca destino seleccionada
        choice = self.cb_finca_destino.get()
        if choice == "(Seleccione finca)":
            self._cargar_fincas_destino()
            return
        self._on_finca_destino()

    # ------------------- Tooltip ID potrero -------------------
    def _mostrar_tooltip_id(self, _event=None):
        nombre = self.cb_potrero.get().strip()
        potrero_id = self.potrero_id_map.get(nombre)
        if not nombre or potrero_id is None:
            self._ocultar_tooltip_id()
            return
        if getattr(self, "_tooltip", None):
            # Actualizar texto si existe
            self._tooltip_label.configure(text=f"ID: {potrero_id}")
            return
        self._tooltip = ctk.CTkToplevel(self)
        self._tooltip.overrideredirect(True)
        self._tooltip_label = ctk.CTkLabel(self._tooltip, text=f"ID: {potrero_id}", font=("Segoe UI", 11))
        self._tooltip_label.pack(padx=6, pady=4)
        # Posicionar
        try:
            x = self.cb_potrero.winfo_rootx() + self.cb_potrero.winfo_width() + 6
            y = self.cb_potrero.winfo_rooty()
            self._tooltip.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _ocultar_tooltip_id(self, _event=None):
        tooltip = getattr(self, "_tooltip", None)
        if tooltip:
            try:
                tooltip.destroy()
            except Exception:
                pass
            self._tooltip = None

    # ------------------- Autocomplete Mode Persistence -------------------
    def _get_autocomplete_mode(self) -> str:
        return "contains"

    def _save_autocomplete_mode(self, modo: str):
        pass

    def _init_autocomplete_switch(self):
        pass

    def _toggle_autocomplete_mode(self):
        pass

    # ------------------- Refresh listas -------------------
    def refrescar_listas(self):
        self._refrescar_destino()
        messagebox.showinfo("Refrescado", "Datos de la finca destino actualizados.")