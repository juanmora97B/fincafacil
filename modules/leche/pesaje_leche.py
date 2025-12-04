import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from database import get_db_connection
from modules.utils.date_picker import attach_date_picker
from modules.utils.ui import add_tooltip

class PesajeLecheFrame(ctk.CTkFrame):
    """Registro diario de producción de leche por animal.
    Usa la tabla produccion_leche (migration 001).
    """
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self._animal_map = {}  # 'codigo - nombre' -> id
        self.crear_widgets()
        self.cargar_animales_combo()
        self.cargar_ultimos_registros()

    # ================= UI =================
    def crear_widgets(self):
        titulo = ctk.CTkLabel(self, text="🥛 Pesaje / Producción de Leche", font=("Segoe UI", 20, "bold"))
        titulo.pack(pady=10)
        add_tooltip(titulo, "Registre litros ordeñados por vaca en cada turno")

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=2, pady=8)

        # Formulario
        form_frame = ctk.CTkFrame(scroll)
        form_frame.pack(fill="x", pady=5)

        header_form = ctk.CTkLabel(form_frame, text="📝 Nuevo Registro", font=("Segoe UI", 16, "bold"))
        header_form.pack(anchor="w", pady=(10, 2))
        helper = ctk.CTkLabel(form_frame, text="Campos con * son obligatorios. Puede dejar vacíos los turnos no ordeñados.", font=("Segoe UI", 11, "italic"))
        helper.pack(anchor="w", pady=(0, 8))
        add_tooltip(header_form, "Crear o actualizar registro diario por animal")
        add_tooltip(helper, "Si ya existe registro para la fecha se actualizará")

        # Fecha y Animal
        row1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Fecha *:", width=80).pack(side="left", padx=5)
        self.entry_fecha = ctk.CTkEntry(row1, width=140, placeholder_text="YYYY-MM-DD")
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha.pack(side="left", padx=5)
        attach_date_picker(row1, self.entry_fecha)
        add_tooltip(self.entry_fecha, "Día del ordeño")

        ctk.CTkLabel(row1, text="Vaca *:", width=80).pack(side="left", padx=5)
        self.combo_vaca = ctk.CTkComboBox(row1, width=260)
        self.combo_vaca.set("Seleccione la vaca")
        self.combo_vaca.pack(side="left", padx=5)
        add_tooltip(self.combo_vaca, "Solo hembras vivas")

        # Turnos
        row2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Mañana (L):", width=110).pack(side="left", padx=5)
        self.entry_manana = ctk.CTkEntry(row2, width=100, placeholder_text="0.0")
        self.entry_manana.pack(side="left", padx=5)
        add_tooltip(self.entry_manana, "Litros ordeñados en la mañana")

        ctk.CTkLabel(row2, text="Tarde (L):", width=90).pack(side="left", padx=5)
        self.entry_tarde = ctk.CTkEntry(row2, width=100, placeholder_text="0.0")
        self.entry_tarde.pack(side="left", padx=5)
        add_tooltip(self.entry_tarde, "Litros ordeñados en la tarde")

        ctk.CTkLabel(row2, text="Noche (L):", width=90).pack(side="left", padx=5)
        self.entry_noche = ctk.CTkEntry(row2, width=100, placeholder_text="0.0")
        self.entry_noche.pack(side="left", padx=5)
        add_tooltip(self.entry_noche, "Litros ordeñados en la noche")

        # Observaciones
        row3 = ctk.CTkFrame(form_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        ctk.CTkLabel(row3, text="Observaciones:", width=110).pack(side="left", padx=5)
        self.text_obs = ctk.CTkTextbox(row3, width=400, height=60)
        self.text_obs.pack(side="left", padx=5, fill="x", expand=True)
        add_tooltip(self.text_obs, "Anote variaciones, causas de baja producción, estado de salud, etc.")

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="💾 Guardar / Actualizar", fg_color="green", hover_color="#006400", command=self.guardar_registro).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🧹 Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Refrescar Lista", command=self.cargar_ultimos_registros).pack(side="left", padx=5)

        # Listado
        list_frame = ctk.CTkFrame(scroll)
        list_frame.pack(fill="both", expand=True, pady=10)
        header_list = ctk.CTkLabel(list_frame, text="📊 Registros Recientes", font=("Segoe UI", 16, "bold"))
        header_list.pack(anchor="w", pady=(10, 5))
        add_tooltip(header_list, "Ultimos 30 días de producción")

        cols = ("id","fecha","animal","total","mañana","tarde","noche","observaciones")
        self.tabla = ttk.Treeview(list_frame, columns=cols, show="headings", displaycolumns=("fecha","animal","total","mañana","tarde","noche","observaciones"), height=14)
        headings = {
            "id":"ID","fecha":"Fecha","animal":"Vaca","total":"Total (L)","mañana":"Mañana","tarde":"Tarde","noche":"Noche","observaciones":"Observaciones"
        }
        widths = {"id":50,"fecha":90,"animal":180,"total":80,"mañana":80,"tarde":80,"noche":80,"observaciones":260}
        for c in cols:
            self.tabla.heading(c, text=headings[c])
            self.tabla.column(c, width=widths[c], anchor="center")
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Acción eliminar
        action_row = ctk.CTkFrame(list_frame, fg_color="transparent")
        action_row.pack(anchor="w", pady=5)
        ctk.CTkButton(action_row, text="🗑️ Eliminar Seleccionado", fg_color="red", hover_color="#8B0000", command=self.eliminar_registro).pack(side="left", padx=5)

    # ================= Datos =================
    def cargar_animales_combo(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT a.id, a.codigo, COALESCE(a.nombre,'')
                    FROM animal a
                    LEFT JOIN muerte m ON m.animal_id = a.id
                    WHERE a.sexo='Hembra' AND m.id IS NULL
                    ORDER BY a.codigo
                """)
                rows = cur.fetchall()
                self._animal_map = {}
                display = []
                for r in rows:
                    label = f"{r['codigo']} - {r['nombre']}".strip().rstrip('- ')
                    self._animal_map[label] = r['id']
                    display.append(label)
                self.combo_vaca.configure(values=display)
                if display:
                    self.combo_vaca.set(display[0])
                else:
                    self.combo_vaca.set("Sin vacas disponibles")
        except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar vacas:\n{e}")

    def guardar_registro(self):
        fecha = self.entry_fecha.get().strip()
        vaca_label = self.combo_vaca.get().strip()
        if not fecha:
            messagebox.showwarning("Atención", "La fecha es obligatoria.")
            return
        if vaca_label in ("Seleccione la vaca","Sin vacas disponibles",""):
            messagebox.showwarning("Atención", "Debe seleccionar una vaca.")
            return
        animal_id = self._animal_map.get(vaca_label)
        if not animal_id:
            messagebox.showwarning("Atención", "Vaca no válida.")
            return
        def parse_litros(val):
            val = (val or '').strip()
            if not val:
                return 0.0
            val = val.replace(',', '.')
            try:
                x = float(val)
                return max(x,0.0)
            except ValueError:
                return 0.0
        l_man = parse_litros(self.entry_manana.get())
        l_tar = parse_litros(self.entry_tarde.get())
        l_noc = parse_litros(self.entry_noche.get())
        obs = self.text_obs.get("1.0","end-1c").strip() or None
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
                    VALUES (?,?,?,?,?,?)
                    ON CONFLICT(animal_id, fecha) DO UPDATE SET
                        litros_manana=excluded.litros_manana,
                        litros_tarde=excluded.litros_tarde,
                        litros_noche=excluded.litros_noche,
                        observaciones=excluded.observaciones
                """, (animal_id, fecha, l_man, l_tar, l_noc, obs))
                conn.commit()
            messagebox.showinfo("Éxito", "Registro guardado correctamente.")
            self.limpiar_formulario(reset_date=False)
            self.cargar_ultimos_registros()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Conflicto al guardar registro.")
        except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def cargar_ultimos_registros(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        desde = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT pl.id, pl.fecha, a.codigo, COALESCE(a.nombre,'') AS nombre,
                           pl.litros_manana, pl.litros_tarde, pl.litros_noche, pl.observaciones
                    FROM produccion_leche pl
                    JOIN animal a ON a.id = pl.animal_id
                    WHERE pl.fecha >= ?
                    ORDER BY pl.fecha DESC, a.codigo
                """, (desde,))
                for r in cur.fetchall():
                    total = (r[4] or 0) + (r[5] or 0) + (r[6] or 0)
                    valores = (
                        str(r[0]),
                        str(r[1]),
                        f"{r[2]} - {r[3]}",
                        f"{total:.1f}",
                        f"{(r[4] or 0):.1f}",
                        f"{(r[5] or 0):.1f}",
                        f"{(r[6] or 0):.1f}",
                        (r[7] or '')
                    )
                    self.tabla.insert('', 'end', values=valores)
        except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar registros:\n{e}")

    def eliminar_registro(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un registro para eliminar.")
            return
        reg_id = self.tabla.item(sel[0])['values'][0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar registro seleccionado?"):
            return
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM produccion_leche WHERE id = ?", (reg_id,))
                conn.commit()
            messagebox.showinfo("Éxito", "Registro eliminado.")
            self.cargar_ultimos_registros()
        except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def limpiar_formulario(self, reset_date=True):
        if reset_date:
            self.entry_fecha.delete(0,'end')
            self.entry_fecha.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.entry_manana.delete(0,'end')
        self.entry_tarde.delete(0,'end')
        self.entry_noche.delete(0,'end')
        self.text_obs.delete('1.0','end')
        # Mantener selección de vaca para agilizar múltiples registros

# Helper para probar rápida standalone
if __name__ == '__main__':
    app = ctk.CTk()
    app.title('Test Pesaje Leche')
    frame = PesajeLecheFrame(app)
    app.geometry('1000x700')
    app.mainloop()
