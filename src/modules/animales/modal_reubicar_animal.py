"""
Modal Reubicar Animal - Cambiar ubicación (finca, sector, lote, potrero)
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import List, Tuple

try:
    from database import get_db_connection
except Exception:
    from database.database import get_db_connection

class ModalReubicarAnimal(ctk.CTkToplevel):
    def __init__(self, master, animal_data, on_saved=None):
        super().__init__(master)
        self.animal = animal_data
        self.on_saved = on_saved
        self.title(f"Reubicar: {animal_data.get('codigo','')} - {animal_data.get('nombre','')}")
        self.geometry("700x420")
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()
        self._load_fincas()

    def _build_ui(self):
        header = ctk.CTkFrame(self, corner_radius=12, fg_color="#1f2937")
        header.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(header, text="🚚 Reubicar Animal", font=("Segoe UI", 22, "bold"), text_color="white").pack(pady=14)

        form = ctk.CTkFrame(self, corner_radius=12)
        form.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Finca
        ctk.CTkLabel(form, text="Finca *", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=10, pady=(14, 6), sticky="w")
        self.cmb_finca = ctk.CTkComboBox(form, width=280, command=lambda *_: self._on_finca_change())
        self.cmb_finca.grid(row=1, column=0, padx=10, pady=(0, 12), sticky="w")

        # Sector
        ctk.CTkLabel(form, text="Sector", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, padx=10, pady=(14, 6), sticky="w")
        self.cmb_sector = ctk.CTkComboBox(form, width=220)
        self.cmb_sector.grid(row=1, column=1, padx=10, pady=(0, 12), sticky="w")

        # Lote
        ctk.CTkLabel(form, text="Lote", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, padx=10, pady=(6, 6), sticky="w")
        self.cmb_lote = ctk.CTkComboBox(form, width=220)
        self.cmb_lote.grid(row=3, column=0, padx=10, pady=(0, 12), sticky="w")

        # Potrero
        ctk.CTkLabel(form, text="Potrero", font=("Segoe UI", 12, "bold")).grid(row=2, column=1, padx=10, pady=(6, 6), sticky="w")
        self.cmb_potrero = ctk.CTkComboBox(form, width=220)
        self.cmb_potrero.grid(row=3, column=1, padx=10, pady=(0, 12), sticky="w")

        # Botones
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=8)
        ctk.CTkButton(actions, text="✓ Guardar", fg_color="#2d6a4f", width=160, command=self._guardar).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="✗ Cancelar", fg_color="gray40", width=140, command=self.destroy).pack(side="left", padx=6)

    def _col_finca(self, tabla: str) -> str:
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"PRAGMA table_info({tabla})")
                cols = [r[1] for r in cur.fetchall()]
                return 'finca_id' if 'finca_id' in cols else 'id_finca'
        except Exception:
            return 'id_finca'

    def _load_fincas(self):
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
                fincas = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            self.cmb_finca.configure(values=fincas)
            if fincas:
                # intentar preselect actual
                finca_nombre = self.animal.get('finca') or ''
                preset = next((v for v in fincas if finca_nombre and finca_nombre in v), None)
                self.cmb_finca.set(preset or fincas[0])
                self._on_finca_change()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar fincas:\n{e}")

    def _on_finca_change(self):
        try:
            val = self.cmb_finca.get()
            if not val or '-' not in val:
                return
            finca_id = int(val.split(' - ')[0])
            # Sectores
            col = self._col_finca('sector')
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT id, nombre FROM sector WHERE {col} = ? ORDER BY nombre", (finca_id,))
                sectores = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            self.cmb_sector.configure(values=["Ninguno"] + sectores)
            self.cmb_sector.set("Ninguno")
            # Lotes
            col = self._col_finca('lote')
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT id, nombre FROM lote WHERE {col} = ? ORDER BY nombre", (finca_id,))
                lotes = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            self.cmb_lote.configure(values=["Ninguno"] + lotes)
            self.cmb_lote.set("Ninguno")
            # Potreros
            col = self._col_finca('potrero')
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(f"SELECT id, nombre FROM potrero WHERE {col} = ? ORDER BY nombre", (finca_id,))
                potreros = [f"{r[0]} - {r[1]}" for r in cur.fetchall()]
            self.cmb_potrero.configure(values=["Ninguno"] + potreros)
            self.cmb_potrero.set("Ninguno")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar dependientes:\n{e}")

    def _guardar(self):
        try:
            finca_val = self.cmb_finca.get()
            if not finca_val or '-' not in finca_val:
                messagebox.showerror("Error", "Seleccione una finca")
                return
            finca_id = int(finca_val.split(' - ')[0])
            sector_id = None
            if self.cmb_sector.get() and self.cmb_sector.get() != 'Ninguno' and '-' in self.cmb_sector.get():
                sector_id = int(self.cmb_sector.get().split(' - ')[0])
            lote_id = None
            if self.cmb_lote.get() and self.cmb_lote.get() != 'Ninguno' and '-' in self.cmb_lote.get():
                lote_id = int(self.cmb_lote.get().split(' - ')[0])
            potrero_id = None
            if self.cmb_potrero.get() and self.cmb_potrero.get() != 'Ninguno' and '-' in self.cmb_potrero.get():
                potrero_id = int(self.cmb_potrero.get().split(' - ')[0])

            # Detectar columnas en animal
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA table_info(animal)")
                cols = [r[1] for r in cur.fetchall()]
                col_finca = 'finca_id' if 'finca_id' in cols else 'id_finca'
                col_sector = 'sector_id' if 'sector_id' in cols else 'id_sector'
                col_potrero = 'potrero_id' if 'potrero_id' in cols else 'id_potrero'

                sql = f"""
                    UPDATE animal SET
                        {col_finca} = ?,
                        {col_sector} = ?,
                        lote_id = ?,
                        {col_potrero} = ?
                    WHERE id = ?
                """
                cur.execute(sql, (finca_id, sector_id, lote_id, potrero_id, self.animal['id']))
                conn.commit()

            messagebox.showinfo("Éxito", "Animal reubicado correctamente")
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reubicar:\n{e}")
