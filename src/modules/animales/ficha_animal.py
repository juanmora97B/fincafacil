import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from pathlib import Path
from database.database import get_db_connection
from database.database import reubicar_animal
from modules.utils.date_picker import attach_date_picker
from modules.animales.bitacora_comentarios import BitacoraComentariosFrame
try:
    from PIL import Image
except Exception:
    Image = None


class FichaAnimalFrame(ctk.CTkFrame):
    def __init__(self, master, on_animal_selected=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.animal_actual = None
        self.on_animal_selected = on_animal_selected
        self.crear_widgets()

    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="📄 Ficha Completa del Animal", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)

        # Frame de búsqueda
        search_frame = ctk.CTkFrame(self, corner_radius=10)
        search_frame.pack(pady=10, padx=4, fill="x")

        self.codigo_entry = ctk.CTkEntry(search_frame, placeholder_text="Ingrese código del animal", width=300)
        self.codigo_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(search_frame, text="🔍 Buscar Ficha", command=self.buscar_animal).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(search_frame, text="🔄 Limpiar", command=self.limpiar_busqueda).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(search_frame, text="🗒️ Bitácora", command=self.abrir_bitacora).pack(side="left", padx=10, pady=10)

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

    def abrir_bitacora(self):
        """Abre la bitácora de comentarios para el animal actual o el código ingresado."""
        codigo = None
        try:
            if self.animal_actual and 'codigo' in self.animal_actual:
                codigo = self.animal_actual['codigo']
            else:
                codigo = self.codigo_entry.get().strip()
        except Exception:
            codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showwarning("Bitácora", "Ingrese o busque un código de animal primero.")
            return
        win = ctk.CTkToplevel(self)
        win.title(f"Bitácora de Comentarios - {codigo}")
        win.geometry("980x720")
        frame = BitacoraComentariosFrame(win, animal_codigo=codigo)
        frame.pack(fill="both", expand=True)

    def configurar_tab_general(self):
        """Configura la pestaña de información general"""
        frame = ctk.CTkScrollableFrame(self.tab_general)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Contenedor principal: izquierda info, derecha foto
        cont = ctk.CTkFrame(frame)
        cont.pack(fill='x', pady=6)
        cont.columnconfigure(0, weight=3)
        cont.columnconfigure(1, weight=1)

        self.info_general_label = ctk.CTkLabel(cont, text="Busque un animal para ver su información", 
                              font=("Segoe UI", 14), justify="left")
        self.info_general_label.grid(row=0, column=0, sticky='nw', padx=4, pady=4)

        # Marco para foto
        self.foto_frame = ctk.CTkFrame(cont, width=240, height=240, fg_color="#ECEFF1")
        self.foto_frame.grid(row=0, column=1, sticky='ne', padx=8, pady=4)
        self.foto_frame.pack_propagate(False)
        self.foto_label = ctk.CTkLabel(self.foto_frame, text="Sin foto", font=("Segoe UI", 12, 'italic'))
        self.foto_label.pack(expand=True)

        # Acciones rápidas (peso y comentario) bajo información
        acciones = ctk.CTkFrame(frame)
        acciones.pack(fill='x', pady=6)
        self.entry_peso = ctk.CTkEntry(acciones, placeholder_text="Peso kg", width=100)
        self.entry_peso.pack(side='left', padx=4, pady=4)
        self.entry_peso_fecha = ctk.CTkEntry(acciones, placeholder_text="Fecha YYYY-MM-DD", width=130)
        self.entry_peso_fecha.pack(side='left', padx=4, pady=4)
        ctk.CTkButton(acciones, text="Registrar Peso", command=self._registrar_peso_desde_info).pack(side='left', padx=6)
        self.entry_comentario = ctk.CTkEntry(acciones, placeholder_text="Comentario rápido", width=280)
        self.entry_comentario.pack(side='left', padx=4, pady=4)
        ctk.CTkButton(acciones, text="Agregar Comentario", command=self._registrar_comentario_desde_info).pack(side='left', padx=6)
        ctk.CTkButton(acciones, text="Exportar Ficha (PDF)", command=self._exportar_pdf).pack(side='right', padx=6)
        ctk.CTkButton(acciones, text="Reubicar", fg_color="#1565C0", command=self._mostrar_dialogo_reubicacion).pack(side='right', padx=6)

    def _mostrar_dialogo_reubicacion(self):
        if not self.animal_actual:
            messagebox.showinfo("Reubicación", "Busque un animal primero")
            return
        top = ctk.CTkToplevel(self)
        top.title("Reubicar Animal")
        frm = ctk.CTkFrame(top)
        frm.pack(fill='both', expand=True, padx=12, pady=12)
        # Layout limpio en grid
        for i in range(4):
            frm.columnconfigure(i, weight=1)
        row_idx = 0
        # Datos actuales + Finca Origen
        finca_origen = self.animal_actual.get('finca','-')
        potrero_origen = self.animal_actual.get('potrero','-')
        sector_origen = self.animal_actual.get('sector','-') if 'sector' in self.animal_actual else '-'
        lote_origen = self.animal_actual.get('lote','-')
        header = ctk.CTkLabel(frm, text=f"Código: {self.animal_actual.get('codigo','-')}  |  Finca Origen: {finca_origen}  |  Potrero: {potrero_origen}", font=("Segoe UI", 12, "bold"))
        header.grid(row=row_idx, column=0, columnspan=4, sticky='w', padx=4, pady=(0,8))
        row_idx += 1
        # Fecha con calendario
        fecha_row = ctk.CTkFrame(frm, fg_color="transparent")
        fecha_row.grid(row=row_idx, column=0, columnspan=4, sticky='ew')
        e_fecha = ctk.CTkEntry(fecha_row, placeholder_text="Fecha YYYY-MM-DD")
        e_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        e_fecha.pack(side='left', fill='x', expand=True, padx=4, pady=4)
        attach_date_picker(fecha_row, e_fecha)
        row_idx += 1
        # Selección de finca destino y potreros activos de esa finca
        finca_values = ["(Seleccione finca)"]
        finca_id_by_label = {}
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca WHERE estado IN ('Activo','Activa')")
                for fid, fname in [(row[0], row[1]) if not isinstance(row, sqlite3.Row) else (row['id'], row['nombre']) for row in cur.fetchall()]:
                    label = f"{fid} - {fname}"
                    finca_values.append(label)
                    finca_id_by_label[label] = fid
        except Exception:
            pass
        finca_row = ctk.CTkFrame(frm, fg_color="transparent")
        finca_row.grid(row=row_idx, column=0, columnspan=4, sticky='ew')
        ctk.CTkLabel(finca_row, text="Finca destino:", width=120).pack(side='left', padx=4)
        cb_finca = ctk.CTkComboBox(finca_row, values=finca_values)
        cb_finca.set(finca_values[0])
        cb_finca.pack(side='left', fill='x', expand=True, padx=4, pady=4)
        row_idx += 1

        # Potreros dependientes de finca
        potrero_values = ["(Seleccione)"]
        potrero_id_by_label = {}
        def cargar_potreros_para_finca(fid: int | None):
            nonlocal potrero_values, potrero_id_by_label
            potrero_values = ["(Seleccione)"]
            potrero_id_by_label = {}
            if not fid:
                cb_potrero.configure(values=potrero_values)
                cb_potrero.set(potrero_values[0])
                return
            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id, nombre FROM potrero WHERE estado='Activo' AND id_finca=?", (fid,))
                    rows = cur.fetchall()
                    for pid, pnom in [(row[0], row[1]) if not isinstance(row, sqlite3.Row) else (row['id'], row['nombre']) for row in rows]:
                        label = f"{pid} - {pnom}"
                        potrero_values.append(label)
                        potrero_id_by_label[label] = pid
                cb_potrero.configure(values=potrero_values)
                cb_potrero.set(potrero_values[0])
            except Exception:
                cb_potrero.configure(values=potrero_values)
                cb_potrero.set(potrero_values[0])

        cb_potrero = ctk.CTkComboBox(frm, values=potrero_values)
        cb_potrero.set(potrero_values[0])
        cb_potrero.configure(state="disabled")
        ctk.CTkLabel(frm, text="Potrero destino:").grid(row=row_idx, column=0, sticky='e', padx=4, pady=4)
        cb_potrero.grid(row=row_idx, column=1, sticky='ew', padx=4, pady=4)
        # Sector y Lote combos dependientes
        sector_values = ["(Seleccione)"]
        sector_id_by_label = {}
        cb_sector = ctk.CTkComboBox(frm, values=sector_values)
        cb_sector.set(sector_values[0])
        cb_sector.configure(state="disabled")
        ctk.CTkLabel(frm, text="Sector destino:").grid(row=row_idx, column=2, sticky='e', padx=4, pady=4)
        cb_sector.grid(row=row_idx, column=3, sticky='ew', padx=4, pady=4)
        row_idx += 1
        lote_values = ["(Seleccione)"]
        lote_id_by_label = {}
        cb_lote = ctk.CTkComboBox(frm, values=lote_values)
        cb_lote.set(lote_values[0])
        cb_lote.configure(state="disabled")
        ctk.CTkLabel(frm, text="Lote destino:").grid(row=row_idx, column=0, sticky='e', padx=4, pady=4)
        cb_lote.grid(row=row_idx, column=1, sticky='ew', padx=4, pady=4)
        e_autor = ctk.CTkEntry(frm, placeholder_text="Autor")
        # Motivo como lista desplegable
        motivos = [
            "Manejo",
            "Cambio de potrero",
            "Enfermedad",
            "Producción",
            "Venta interna",
            "Rotación de pasto",
            "Otro",
        ]
        cb_motivo = ctk.CTkComboBox(frm, values=motivos)
        cb_motivo.set(motivos[0])
        ctk.CTkLabel(frm, text="Motivo:").grid(row=row_idx, column=2, sticky='e', padx=4, pady=4)
        cb_motivo.grid(row=row_idx, column=3, sticky='ew', padx=4, pady=4)
        row_idx += 1
        ctk.CTkLabel(frm, text="Usuario/Autor:").grid(row=row_idx, column=2, sticky='e', padx=4, pady=4)
        e_autor.grid(row=row_idx, column=3, sticky='ew', padx=4, pady=4)
        row_idx += 1

        def on_change_finca(choice: str):
            fid = finca_id_by_label.get(choice)
            cargar_potreros_para_finca(fid)
            # Cargar sectores y lotes
            try:
                sector_values[:] = ["(Seleccione)"]
                sector_id_by_label.clear()
                lote_values[:] = ["(Seleccione)"]
                lote_id_by_label.clear()
                if fid:
                    with get_db_connection() as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT id, nombre FROM sector WHERE finca_id=? AND estado IN ('Activo','Activa')", (fid,))
                        for sid, snom in [(row[0], row[1]) if not isinstance(row, sqlite3.Row) else (row['id'], row['nombre']) for row in cur.fetchall()]:
                            lab = f"{sid} - {snom}"
                            sector_values.append(lab)
                            sector_id_by_label[lab] = sid
                        # Lotes filtrados por finca destino
                        cur.execute("SELECT id, nombre FROM lote WHERE estado IN ('Activo','Activa') AND finca_id=?", (fid,))
                        for lid, lnom in [(row[0], row[1]) if not isinstance(row, sqlite3.Row) else (row['id'], row['nombre']) for row in cur.fetchall()]:
                            lab = f"{lid} - {lnom}"
                            lote_values.append(lab)
                            lote_id_by_label[lab] = lid
                cb_sector.configure(values=sector_values, state=("normal" if fid else "disabled"))
                cb_sector.set(sector_values[0])
                cb_lote.configure(values=lote_values, state=("normal" if fid else "disabled"))
                cb_lote.set(lote_values[0])
                cb_potrero.configure(state=("normal" if fid else "disabled"))
            except Exception:
                cb_sector.configure(values=sector_values, state="disabled")
                cb_lote.configure(values=lote_values, state="disabled")
                cb_potrero.configure(state="disabled")
        # Botón: Refrescar Potreros (solo finca destino)
        ctk.CTkButton(frm, text="Refrescar Potreros", command=lambda: on_change_finca(cb_finca.get())).grid(row=row_idx, column=0, sticky='w', padx=4, pady=(8,6))
        # Botón: Ver Animal
        def ver_animal():
            a = self.animal_actual or {}
            info = [
                f"Código: {a.get('codigo','-')}",
                f"Nombre: {a.get('nombre','-')}",
                f"Raza: {a.get('raza','-')}",
                f"Finca: {a.get('finca','-')}",
                f"Ubicación: Potrero {a.get('potrero','-')} | Sector {sector_origen} | Lote {lote_origen}",
                f"Estado: {a.get('estado','-')}",
            ]
            messagebox.showinfo("Animal", "\n".join(info))
        ctk.CTkButton(frm, text="Ver Animal", command=ver_animal).grid(row=row_idx, column=1, sticky='w', padx=4, pady=(8,6))
        row_idx += 1
        cb_finca.bind("<<ComboboxSelected>>", lambda _e=None: on_change_finca(cb_finca.get()))
        def guardar():
            # Validar que animal_actual existe
            if not self.animal_actual:
                messagebox.showerror("Reubicación", "Seleccione un animal primero")
                return
            fecha = e_fecha.get().strip()
            destino = cb_potrero.get().strip()
            motivo = cb_motivo.get().strip()
            autor = e_autor.get().strip() or "Sistema"
            if cb_finca.get() == "(Seleccione finca)":
                messagebox.showerror("Reubicación", "Seleccione la finca destino")
                return
            if not destino or destino == "(Seleccione)":
                messagebox.showerror("Reubicación", "Ingrese potrero destino")
                return
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
            except Exception:
                messagebox.showerror("Reubicación", "Fecha inválida")
                return
            # Resolver selección a id y finca/sector/lote destino
            to_val = destino
            to_finca_id = None
            to_sector_id = None
            to_lote_id = None
            try:
                sel_finca = cb_finca.get()
                to_finca_id = finca_id_by_label.get(sel_finca)
                if destino in potrero_id_by_label:
                    to_val = potrero_id_by_label[destino]
                else:
                    # Si no coincide, intentar parsear "id - nombre" o número
                    try:
                        to_val = int(destino.split(' ')[0])
                    except Exception:
                        pass
                sel_sector = cb_sector.get()
                to_sector_id = sector_id_by_label.get(sel_sector)
                sel_lote = cb_lote.get()
                to_lote_id = lote_id_by_label.get(sel_lote)
            except Exception:
                pass
            # Validación: destino distinto al actual
            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id_potrero FROM animal WHERE id=?", (self.animal_actual['id'],))
                    rcur = cur.fetchone()
                    actual_id = rcur[0] if rcur and not isinstance(rcur, sqlite3.Row) else (rcur['id_potrero'] if rcur else None)
                    if str(actual_id) == str(to_val):
                        messagebox.showerror("Reubicación", "El destino es igual al potrero actual")
                        return
            except Exception:
                pass
            # Texto de origen/destino para confirmación
            origen_finca = finca_origen
            origen_potrero = potrero_origen
            destino_finca_txt = cb_finca.get()
            destino_finca = destino_finca_txt.split(' - ',1)[-1] if ' - ' in destino_finca_txt else destino_finca_txt
            destino_potrero = destino

            ok = reubicar_animal(self.animal_actual['id'], str(to_val), motivo, autor, fecha, to_finca_id, to_sector_id, to_lote_id)
            if ok:
                # Refrescar info general y comentarios/bitácora visible
                try:
                    self.buscar_animal()
                except Exception:
                    pass
                top.destroy()
                msg = (
                    "Reubicación registrada\n\n"
                    f"De: {origen_finca} / {origen_potrero}\n"
                    f"A: {destino_finca} / {destino_potrero}\n"
                    f"Fecha: {fecha}\n"
                )
                messagebox.showinfo("Reubicación", msg)
            else:
                messagebox.showerror("Reubicación", "No se pudo registrar la reubicación")
        ctk.CTkButton(frm, text="Guardar", command=guardar).grid(row=row_idx, column=3, sticky='e', padx=4, pady=6)

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
        # Resumen de tendencia
        self.lbl_tendencia = ctk.CTkLabel(self.tab_pesos, text="Tendencia: -", font=("Segoe UI", 12, 'italic'))
        self.lbl_tendencia.pack(anchor='w', padx=8, pady=(0,8))

    def configurar_tab_tratamientos(self):
        """Configura la pestaña de tratamientos"""
        frame = ctk.CTkFrame(self.tab_tratamientos)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        barra_t = ctk.CTkFrame(self.tab_tratamientos)
        barra_t.pack(fill='x', padx=10, pady=(10,0))
        ctk.CTkButton(barra_t, text="Nuevo", command=self._nuevo_tratamiento).pack(side='left', padx=4)
        ctk.CTkButton(barra_t, text="Editar", command=self._editar_tratamiento_sel).pack(side='left', padx=4)
        ctk.CTkButton(barra_t, text="Eliminar", fg_color="#C62828", hover_color="#EF5350", command=self._eliminar_tratamiento_sel).pack(side='left', padx=4)

        self.tabla_tratamientos = ttk.Treeview(frame, columns=("fecha_inicio", "fecha_fin", "tipo", "producto", "dosis", "estado"), show="headings", height=10)
        
        column_config = [
            ("fecha_inicio", "Fecha inicio", 120),
            ("fecha_fin", "Fecha fin", 120),
            ("tipo", "Tratamiento", 150),
            ("producto", "Producto", 150),
            ("dosis", "Dosis", 120),
            ("estado", "Estado", 120)
        ]
        
        for col, heading, width in column_config:
            self.tabla_tratamientos.heading(col, text=heading)
            self.tabla_tratamientos.column(col, width=width, anchor="center")

        self.tabla_tratamientos.pack(fill="both", expand=True)

    def configurar_tab_comentarios(self):
        """Configura la pestaña de comentarios"""
        frame = ctk.CTkFrame(self.tab_comentarios)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Simplificar a columnas existentes en BD
        barra_c = ctk.CTkFrame(self.tab_comentarios)
        barra_c.pack(fill='x', padx=10, pady=(10,0))
        ctk.CTkButton(barra_c, text="Editar", command=self._editar_comentario_sel).pack(side='left', padx=4)
        ctk.CTkButton(barra_c, text="Eliminar", fg_color="#C62828", hover_color="#EF5350", command=self._eliminar_comentario_sel).pack(side='left', padx=4)

        self.tabla_comentarios = ttk.Treeview(frame, columns=("id","fecha", "comentario"), show="headings", height=10)
        for col, heading, width in [("fecha","Fecha",140),("comentario","Comentario",480)]:
            self.tabla_comentarios.heading(col, text=heading)
            self.tabla_comentarios.column(col, width=width, anchor='center')
        # Ocultar id visualmente
        self.tabla_comentarios.heading("id", text="")
        self.tabla_comentarios.column("id", width=1, stretch=False, anchor='center')

        self.tabla_comentarios.pack(fill="both", expand=True)

    def buscar_animal(self):
        """Busca un animal y carga datos con acceso por nombre usando row_factory."""
        codigo = self.codigo_entry.get().strip().upper()
        if not codigo:
            messagebox.showwarning("Atención", "Ingrese un código para buscar.")
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    SELECT a.id, a.codigo, a.nombre, a.tipo_ingreso, a.sexo,
                           (SELECT nombre FROM finca WHERE id=a.id_finca) AS finca,
                           (SELECT nombre FROM raza WHERE id=a.raza_id) AS raza,
                           (SELECT nombre FROM potrero WHERE id=a.id_potrero) AS potrero,
                           (SELECT nombre FROM lote WHERE id=a.lote_id) AS lote,
                           a.fecha_nacimiento, a.fecha_compra,
                           a.salud, a.estado, a.inventariado,
                           a.color, a.hierro, a.numero_hierros,
                           a.composicion_racial, a.comentarios, a.fecha_registro,
                           a.foto_path,
                           madre.codigo AS codigo_madre, madre.nombre AS nombre_madre,
                           padre.codigo AS codigo_padre, padre.nombre AS nombre_padre
                    FROM animal a
                    LEFT JOIN animal madre ON a.id_madre = madre.id
                    LEFT JOIN animal padre ON a.id_padre = padre.id
                    WHERE a.codigo = ?
                    """,
                    (codigo,),
                )
                row = cur.fetchone()
            if not row:
                messagebox.showerror("No encontrado", "No existe un animal con ese código.")
                return
            animal = dict(row)
            self.animal_actual = animal
            self.mostrar_informacion_general(animal)
            self.cargar_historial_pesos(animal['id'])
            self.cargar_tratamientos(animal['id'])
            self.cargar_comentarios(animal['id'])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar el animal:\n{e}")

    def mostrar_informacion_general(self, animal: dict):
        """Muestra información general formateada del animal."""
        resumen = self._resumen_animal(animal.get('id'))
        lines = [
            "────────────────────────────────────────────────────────",
            f"Código: {animal.get('codigo','-')}  Nombre: {animal.get('nombre','-')}  Sexo: {animal.get('sexo','-')}",
            f"Raza: {animal.get('raza','-')}  Finca: {animal.get('finca','-')}  Potrero: {animal.get('potrero','-')}  Lote: {animal.get('lote','-')}",
            f"Estado: {animal.get('estado','-')}  Origen: {animal.get('tipo_ingreso','-')}",
            f"Fecha Nac.: {animal.get('fecha_nacimiento','-')}  Fecha Compra: {animal.get('fecha_compra','-')}",
            f"Padre: {animal.get('codigo_padre','-')} {animal.get('nombre_padre','')}  Madre: {animal.get('codigo_madre','-')} {animal.get('nombre_madre','')}",
            f"Color: {animal.get('color','-')}  Hierro: {animal.get('hierro','-')}  Nº Hierros: {animal.get('numero_hierros','-')}",
            f"Composición racial: {animal.get('composicion_racial','-')}",
            f"Notas: {animal.get('comentarios','') or '(Sin notas)'}",
            "────────────────────────────────────────────────────────",
            f"Resumen: Edad aprox. {resumen.get('edad','-')}, pesajes {resumen.get('num_pesajes',0)}, último {resumen.get('ultimo_peso','-')} el {resumen.get('fecha_ultimo','-')}",
            "────────────────────────────────────────────────────────",
        ]
        self.info_general_label.configure(text='\n'.join(lines))
        self._mostrar_foto(animal.get('foto_path'))

    def _resumen_animal(self, animal_id: int | None) -> dict:
        if not animal_id:
            return {"edad":"-","num_pesajes":0,"ultimo_peso":"-","fecha_ultimo":"-"}
        edad = "-"
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT fecha_nacimiento FROM animal WHERE id=?", (animal_id,))
                r = cur.fetchone()
                fn = r['fecha_nacimiento'] if r and isinstance(r, sqlite3.Row) else (r[0] if r else None)
                if fn:
                    try:
                        y = int(str(fn)[:4])
                        edad = f"{max(0, datetime.now().year - y)} años"
                    except Exception:
                        edad = "-"
                cur.execute("SELECT COUNT(*), MAX(fecha) FROM peso WHERE animal_id=?", (animal_id,))
                c = cur.fetchone()
                num = c[0] if c else 0
                fmax = c[1] if c else None
                ul = "-"
                if fmax:
                    cur.execute("SELECT peso FROM peso WHERE animal_id=? AND fecha=?", (animal_id, fmax))
                    r2 = cur.fetchone()
                    p = r2['peso'] if r2 and isinstance(r2, sqlite3.Row) else (r2[0] if r2 else None)
                    if p is not None:
                        ul = f"{float(p):.2f} kg"
                return {"edad":edad,"num_pesajes":num,"ultimo_peso":ul,"fecha_ultimo":fmax or '-'}
        except Exception:
            return {"edad":"-","num_pesajes":0,"ultimo_peso":"-","fecha_ultimo":"-"}

    def cargar_historial_pesos(self, id_animal):
        """Carga el historial de pesos del animal"""
        for fila in self.tabla_pesos.get_children():
            self.tabla_pesos.delete(fila)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fecha, peso, metodo, observaciones 
                    FROM peso 
                    WHERE animal_id = ? 
                    ORDER BY fecha DESC
                """, (id_animal,))
                for r in cursor.fetchall():
                    fecha = r['fecha'] if isinstance(r, sqlite3.Row) else r[0]
                    peso = r['peso'] if isinstance(r, sqlite3.Row) else r[1]
                    metodo = r['metodo'] if isinstance(r, sqlite3.Row) else r[2]
                    obs = r['observaciones'] if isinstance(r, sqlite3.Row) else r[3]
                    self.tabla_pesos.insert("", "end", values=(fecha, f"{float(peso):.2f}", metodo or "", obs or ""))
            # Actualizar tendencia
            self._calcular_tendencia_pesos()
        except Exception as e:
            messagebox.showerror("Pesos", f"Error al cargar pesos: {e}")

    def _calcular_tendencia_pesos(self):
        try:
            pesos = []
            for iid in self.tabla_pesos.get_children():
                vals = self.tabla_pesos.item(iid, 'values')
                if vals and vals[1]:
                    pesos.append((vals[0], float(vals[1])))
            if len(pesos) >= 2:
                pesos_sorted = sorted(pesos, key=lambda x: x[0])
                inicio = pesos_sorted[0][1]
                fin = pesos_sorted[-1][1]
                diff = fin - inicio
                self.lbl_tendencia.configure(text=f"Tendencia: {diff:+.2f} kg desde el primer registro")
            elif len(pesos) == 1:
                self.lbl_tendencia.configure(text="Tendencia: 0.00 kg (un solo registro)")
            else:
                self.lbl_tendencia.configure(text="Tendencia: -")
        except Exception:
            self.lbl_tendencia.configure(text="Tendencia: -")

    def _agregar_peso(self, peso: float | None = None, fecha: str | None = None):
        if not self.animal_actual:
            messagebox.showinfo("Pesos", "Busque primero un animal")
            return
        try:
            peso_val = float(peso) if peso is not None else None
            if peso_val is None:
                # Dialogo simple: tomar de selección actual en UI no disponible, usar messagebox
                messagebox.showinfo("Pesos", "Ingrese el peso en el módulo de inventario")
                return
            fecha_txt = fecha or datetime.now().strftime('%Y-%m-%d')
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("INSERT OR REPLACE INTO peso (animal_id, fecha, peso, metodo) VALUES (?,?,?,?)",
                            (self.animal_actual['id'], fecha_txt, peso_val, "Registro"))
                conn.commit()
            self.cargar_historial_pesos(self.animal_actual['id'])
            messagebox.showinfo("Pesos", "Peso registrado")
        except Exception as e:
            messagebox.showerror("Pesos", f"No se pudo registrar: {e}")

    def cargar_tratamientos(self, id_animal):
        """Carga el historial de tratamientos del animal"""
        for fila in self.tabla_tratamientos.get_children():
            self.tabla_tratamientos.delete(fila)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, fecha_inicio, fecha_fin, tipo_tratamiento AS tipo, producto, dosis, estado 
                    FROM tratamiento 
                    WHERE id_animal = ? 
                    ORDER BY fecha_inicio DESC
                """, (id_animal,))
                for r in cursor.fetchall():
                    if isinstance(r, sqlite3.Row):
                        iid = f"t_{r['id']}"
                        vals = [r['fecha_inicio'], r['fecha_fin'], r['tipo'], r['producto'], r['dosis'], r['estado']]
                    else:
                        iid = f"t_{r[0]}"
                        vals = [r[1], r[2], r[3], r[4], r[5], r[6]]
                    self.tabla_tratamientos.insert("", "end", iid=iid, values=vals)
        except Exception as e:
            messagebox.showerror("Tratamientos", f"Error al cargar tratamientos: {e}")

    def _nuevo_tratamiento(self):
        if not self.animal_actual:
            messagebox.showinfo("Tratamientos", "Seleccione un animal primero")
            return
        top = ctk.CTkToplevel(self)
        top.title("Nuevo Tratamiento")
        frm = ctk.CTkFrame(top)
        frm.pack(fill='both', expand=True, padx=8, pady=8)
        e_inicio = ctk.CTkEntry(frm, placeholder_text="Fecha inicio YYYY-MM-DD")
        e_fin = ctk.CTkEntry(frm, placeholder_text="Fecha fin YYYY-MM-DD")
        e_tipo = ctk.CTkEntry(frm, placeholder_text="Tipo")
        e_prod = ctk.CTkEntry(frm, placeholder_text="Producto")
        e_dosis = ctk.CTkEntry(frm, placeholder_text="Dosis")
        e_estado = ctk.CTkEntry(frm, placeholder_text="Estado")
        for w in (e_inicio,e_fin,e_tipo,e_prod,e_dosis,e_estado):
            w.pack(fill='x', padx=4, pady=4)
        def guardar():
            if not self.animal_actual:
                messagebox.showerror("Tratamientos", "Animal no disponible")
                return
            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO tratamiento (id_animal, fecha_inicio, fecha_fin, tipo_tratamiento, producto, dosis, estado)
                        VALUES (?,?,?,?,?,?,?)
                        """,
                        (self.animal_actual['id'], e_inicio.get().strip(), e_fin.get().strip(), e_tipo.get().strip(), e_prod.get().strip(), e_dosis.get().strip(), e_estado.get().strip())
                    )
                    conn.commit()
                self.cargar_tratamientos(self.animal_actual['id'])
                top.destroy()
                messagebox.showinfo("Tratamientos","Tratamiento guardado")
            except Exception as e:
                messagebox.showerror("Tratamientos", f"No se pudo guardar: {e}")
        ctk.CTkButton(frm, text="Guardar", command=guardar).pack(pady=6)

    def cargar_comentarios(self, id_animal):
        """Carga el historial de comentarios del animal"""
        for fila in self.tabla_comentarios.get_children():
            self.tabla_comentarios.delete(fila)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # soporte a nuestra tabla comentario (fecha, comentario)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comentario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        animal_id INTEGER NOT NULL,
                        fecha TEXT NOT NULL,
                        comentario TEXT NOT NULL,
                        FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
                    )
                """)
                conn.commit()
                cursor.execute("SELECT id, fecha, comentario FROM comentario WHERE animal_id = ? ORDER BY fecha DESC", (id_animal,))
                for r in cursor.fetchall():
                    if isinstance(r, sqlite3.Row):
                        cid, fecha, com = r['id'], r['fecha'], r['comentario']
                    else:
                        cid, fecha, com = r[0], r[1], r[2]
                    self.tabla_comentarios.insert("", "end", iid=f"c_{cid}", values=(cid, fecha, com))
        except Exception as e:
            messagebox.showerror("Comentarios", f"Error al cargar comentarios: {e}")

    def limpiar_busqueda(self):
        """Limpia la búsqueda y toda la información"""
        self.codigo_entry.delete(0, "end")
        self.animal_actual = None
        self.info_general_label.configure(text="Busque un animal para ver su información")
        
        # Limpiar tablas
        for tabla in [self.tabla_pesos, self.tabla_tratamientos, self.tabla_comentarios]:
            for fila in tabla.get_children():
                tabla.delete(fila)

    # ----- Foto handling -----
    def _mostrar_foto(self, foto_path: str | None):
        for child in self.foto_frame.winfo_children():
            child.destroy()
        if not foto_path:
            ctk.CTkLabel(self.foto_frame, text="Sin foto", font=("Segoe UI",12,'italic')).pack(expand=True)
            return
        p = Path(foto_path)
        if not p.exists() or not Image:
            ctk.CTkLabel(self.foto_frame, text="Sin foto", font=("Segoe UI",12,'italic')).pack(expand=True)
            return
        try:
            img = Image.open(p)
            img = img.resize((240,240))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240,240))
            ctk.CTkLabel(self.foto_frame, image=ctk_img, text="").pack(expand=True)
        except Exception:
            ctk.CTkLabel(self.foto_frame, text="Sin foto", font=("Segoe UI",12,'italic')).pack(expand=True)

    # ----- Acciones rápidas desde info -----
    def _registrar_peso_desde_info(self):
        if not self.animal_actual:
            messagebox.showinfo("Peso", "Busque un animal primero")
            return
        peso_txt = self.entry_peso.get().strip()
        if not peso_txt:
            messagebox.showinfo("Peso", "Ingrese peso")
            return
        fecha_txt = self.entry_peso_fecha.get().strip() or datetime.now().strftime('%Y-%m-%d')
        try:
            peso_val = float(peso_txt)
        except Exception:
            messagebox.showerror("Peso", "Formato de peso inválido")
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("INSERT OR REPLACE INTO peso (animal_id, fecha, peso, metodo) VALUES (?,?,?,?)",
                            (self.animal_actual['id'], fecha_txt, peso_val, "Ficha"))
                conn.commit()
            self.cargar_historial_pesos(self.animal_actual['id'])
            self.entry_peso.delete(0,'end')
            messagebox.showinfo("Peso", "Registrado")
        except Exception as e:
            messagebox.showerror("Peso", f"Error: {e}")

    def _registrar_comentario_desde_info(self):
        if not self.animal_actual:
            messagebox.showinfo("Comentario", "Busque un animal primero")
            return
        txt = self.entry_comentario.get().strip()
        if not txt:
            messagebox.showinfo("Comentario", "Ingrese texto")
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO comentario (animal_id, fecha, comentario) VALUES (?,?,?)",
                            (self.animal_actual['id'], datetime.now().strftime('%Y-%m-%d %H:%M'), txt))
                conn.commit()
            self.entry_comentario.delete(0,'end')
            self.cargar_comentarios(self.animal_actual['id'])
        except Exception as e:
            messagebox.showerror("Comentario", f"Error: {e}")

    # ----- CRUD Comentarios -----
    def _editar_comentario_sel(self):
        sel = self.tabla_comentarios.selection()
        if not sel:
            messagebox.showinfo("Comentarios", "Seleccione un comentario")
            return
        iid = sel[0]
        try:
            com_id = int(iid.split('_')[1])
        except Exception:
            messagebox.showerror("Comentarios", "No se pudo identificar el registro")
            return
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT fecha, comentario FROM comentario WHERE id=?", (com_id,))
            r = cur.fetchone()
        if not r:
            messagebox.showerror("Comentarios", "Registro no encontrado")
            return
        fecha = r['fecha'] if isinstance(r, sqlite3.Row) else r[0]
        txt = r['comentario'] if isinstance(r, sqlite3.Row) else r[1]
        top = ctk.CTkToplevel(self)
        top.title("Editar Comentario")
        frm = ctk.CTkFrame(top)
        frm.pack(fill='both', expand=True, padx=8, pady=8)
        e_fecha = ctk.CTkEntry(frm)
        e_fecha.insert(0, str(fecha or ''))
        e_fecha.pack(fill='x', padx=4, pady=4)
        e_txt = ctk.CTkEntry(frm)
        e_txt.insert(0, txt or '')
        e_txt.pack(fill='x', padx=4, pady=4)
        def guardar():
            if not self.animal_actual:
                messagebox.showerror("Comentarios", "Animal no disponible")
                return
            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE comentario SET fecha=?, comentario=? WHERE id=?", (e_fecha.get().strip(), e_txt.get().strip(), com_id))
                    conn.commit()
                self.cargar_comentarios(self.animal_actual['id'])
                top.destroy()
                messagebox.showinfo("Comentarios","Comentario actualizado")
            except Exception as e:
                messagebox.showerror("Comentarios", f"No se pudo actualizar: {e}")
        ctk.CTkButton(frm, text="Guardar", command=guardar).pack(pady=6)

    def _eliminar_comentario_sel(self):
        if not self.animal_actual:
            messagebox.showinfo("Comentarios", "Seleccione un animal primero")
            return
        sel = self.tabla_comentarios.selection()
        if not sel:
            messagebox.showinfo("Comentarios", "Seleccione un comentario")
            return
        iid = sel[0]
        try:
            com_id = int(iid.split('_')[1])
        except Exception:
            messagebox.showerror("Comentarios", "No se pudo identificar el registro")
            return
        if not messagebox.askyesno("Eliminar", "¿Eliminar comentario seleccionado?"):
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM comentario WHERE id=?", (com_id,))
                conn.commit()
            self.cargar_comentarios(self.animal_actual['id'])
        except Exception as e:
            messagebox.showerror("Comentarios", f"No se pudo eliminar: {e}")

    # ----- Exportación PDF -----
    def _exportar_pdf(self):
        if not self.animal_actual:
            messagebox.showinfo("Exportar", "Busque un animal primero")
            return
        try:
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import cm
                import tempfile
                import os
                tmp = Path(tempfile.gettempdir()) / f"ficha_{self.animal_actual['codigo']}.pdf"
                c = canvas.Canvas(str(tmp), pagesize=A4)
                w, h = A4
                y = h - 2*cm
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2*cm, y, f"Ficha del Animal - {self.animal_actual.get('codigo','')} ")
                y -= 1*cm
                c.setFont("Helvetica", 10)
                info_text = self.info_general_label.cget('text').split('\n')
                for line in info_text:
                    if y < 2*cm:
                        c.showPage(); y = h - 2*cm
                    c.drawString(2*cm, y, line)
                    y -= 0.6*cm
                c.showPage()
                c.save()
                messagebox.showinfo("Exportar", f"PDF generado: {tmp}")
                os.startfile(str(tmp))
            except Exception:
                # Fallback a HTML simple
                import tempfile, os
                tmp = Path(tempfile.gettempdir()) / f"ficha_{self.animal_actual['codigo']}.html"
                html = "<html><head><meta charset='utf-8'><title>Ficha</title></head><body>" + \
                       f"<h2>Ficha del Animal - {self.animal_actual.get('codigo','')}</h2>" + \
                       "<pre>" + self.info_general_label.cget('text') + "</pre>" + \
                       "</body></html>"
                tmp.write_text(html, encoding='utf-8')
                messagebox.showinfo("Exportar", f"HTML generado: {tmp}")
                os.startfile(str(tmp))
        except Exception as e:
            messagebox.showerror("Exportar", f"No se pudo exportar: {e}")

    # ----- CRUD Tratamientos -----
    def _editar_tratamiento_sel(self):
        sel = self.tabla_tratamientos.selection()
        if not sel:
            messagebox.showinfo("Tratamientos", "Seleccione un tratamiento")
            return
        iid = sel[0]
        try:
            trat_id = int(iid.split('_')[1])
        except Exception:
            messagebox.showerror("Tratamientos", "No se pudo identificar el registro")
            return
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT fecha_inicio, fecha_fin, tipo_tratamiento, producto, dosis, estado FROM tratamiento WHERE id=?", (trat_id,))
            r = cur.fetchone()
        if not r:
            messagebox.showerror("Tratamientos", "Registro no encontrado")
            return
        top = ctk.CTkToplevel(self)
        top.title("Editar Tratamiento")
        frm = ctk.CTkFrame(top)
        frm.pack(fill='both', expand=True, padx=8, pady=8)
        e_inicio = ctk.CTkEntry(frm)
        e_fin = ctk.CTkEntry(frm)
        e_tipo = ctk.CTkEntry(frm)
        e_prod = ctk.CTkEntry(frm)
        e_dosis = ctk.CTkEntry(frm)
        e_estado = ctk.CTkEntry(frm)
        vals = [r[0] if not isinstance(r, sqlite3.Row) else r['fecha_inicio'],
                r[1] if not isinstance(r, sqlite3.Row) else r['fecha_fin'],
                r[2] if not isinstance(r, sqlite3.Row) else r['tipo_tratamiento'],
                r[3] if not isinstance(r, sqlite3.Row) else r['producto'],
                r[4] if not isinstance(r, sqlite3.Row) else r['dosis'],
                r[5] if not isinstance(r, sqlite3.Row) else r['estado']]
        for w, val in zip((e_inicio,e_fin,e_tipo,e_prod,e_dosis,e_estado), vals):
            w.insert(0, str(val or ''))
            w.pack(fill='x', padx=4, pady=4)
        def guardar():
            if not self.animal_actual:
                messagebox.showerror("Tratamientos", "Animal no disponible")
                return
            try:
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE tratamiento SET fecha_inicio=?, fecha_fin=?, tipo_tratamiento=?, producto=?, dosis=?, estado=?
                        WHERE id=?
                    """, (e_inicio.get().strip(), e_fin.get().strip(), e_tipo.get().strip(), e_prod.get().strip(), e_dosis.get().strip(), e_estado.get().strip(), trat_id))
                    conn.commit()
                self.cargar_tratamientos(self.animal_actual['id'])
                top.destroy()
                messagebox.showinfo("Tratamientos","Tratamiento actualizado")
            except Exception as e:
                messagebox.showerror("Tratamientos", f"No se pudo actualizar: {e}")
        ctk.CTkButton(frm, text="Guardar", command=guardar).pack(pady=6)

    def _eliminar_tratamiento_sel(self):
        if not self.animal_actual:
            messagebox.showinfo("Tratamientos", "Seleccione un animal primero")
            return
        sel = self.tabla_tratamientos.selection()
        if not sel:
            messagebox.showinfo("Tratamientos", "Seleccione un tratamiento")
            return
        iid = sel[0]
        try:
            trat_id = int(iid.split('_')[1])
        except Exception:
            messagebox.showerror("Tratamientos", "No se pudo identificar el registro")
            return
        if not messagebox.askyesno("Eliminar", "¿Eliminar tratamiento seleccionado?"):
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM tratamiento WHERE id=?", (trat_id,))
                conn.commit()
            self.cargar_tratamientos(self.animal_actual['id'])
        except Exception as e:
            messagebox.showerror("Tratamientos", f"No se pudo eliminar: {e}")