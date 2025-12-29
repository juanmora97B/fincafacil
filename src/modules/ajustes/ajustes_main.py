from modules.utils.colores import obtener_colores
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import sys
import os
from pathlib import Path
from typing import Any, cast

# Importaciones corregidas
try:
    from database.database import get_db_connection
    from config import config as app_config
    from modules.utils.logger import get_logger
    from modules.utils.plantillas_carga import (
        get_template_names,
        resolve_key_from_name,
        save_template_to_path,
        suggested_filename,
        ensure_templates_dir,
    )
    from modules.utils.license_ui import LicenseFrame
    from infraestructura.ajustes import AjustesService, AjustesRepository
except ImportError as e:
    print(f"[ERROR] Error importando dependencias: {e}")

class AjustesFrame(ctk.CTkFrame):
    """Módulo de Ajustes: preferencias de la aplicación (tema, etc.)."""

    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        # Colores del módulo
        self.color_bg, self.color_hover = obtener_colores('ajustes')
        
        # Configurar logger
        self.logger = get_logger("Ajustes")
        self.logger.info("Módulo Ajustes iniciado")
        # Servicio de Ajustes
        self.ajustes_service = AjustesService(repository=AjustesRepository())
        
        # Inicializar interfaz
        self.crear_widgets()

    # =========================================================
    #                      CREACIÓN DE UI
    # =========================================================
    def crear_widgets(self):
        """Interfaz de Ajustes: solo preferencias (tema, etc.)."""
        # Contenedor principal scrollable con ancho completo
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Título de ajustes con color del módulo
        titulo_frame = ctk.CTkFrame(scroll_container, fg_color=(self.color_bg, "#1a1a1a"), corner_radius=15)
        titulo_frame.pack(fill="x", pady=(0, 20), padx=10)
        ctk.CTkLabel(titulo_frame, text="⚙️ Ajustes", font=("Segoe UI", 24, "bold"), text_color="white").pack(side="left", padx=15, pady=10)

        # Preferencias de apariencia
        prefs_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        prefs_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(prefs_frame, text="🎨 Preferencias", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        apariencia_row = ctk.CTkFrame(prefs_frame, fg_color="transparent")
        apariencia_row.pack(padx=10, pady=10, fill="x")
        ctk.CTkLabel(apariencia_row, text="Modo de interfaz:", width=130).pack(side="left")
        modo_actual = ctk.get_appearance_mode()
        self.appearance_var_local = ctk.StringVar(value="Claro" if modo_actual.lower() == "light" else "Oscuro")
        ctk.CTkOptionMenu(
            apariencia_row,
            values=["Claro", "Oscuro"],
            variable=self.appearance_var_local,
            command=self._change_appearance_via_app
        ).pack(side="left", padx=5)

        # Preferencias generales
        general_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        general_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(general_frame, text="⚙️ Preferencias generales", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        grid = ctk.CTkFrame(general_frame, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=10)
        for i in range(2):
            grid.columnconfigure(i, weight=1)
        ctk.CTkLabel(grid, text="Finca por defecto:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.finca_combo = ctk.CTkComboBox(grid, values=[], width=280)
        self.finca_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(grid, text="Idioma:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.lang_var = ctk.StringVar(value="es")
        self.lang_option = ctk.CTkOptionMenu(grid, values=["es", "en"], variable=self.lang_var)
        self.lang_option.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(grid, text="Unidades de peso:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.units_weight_var = ctk.StringVar(value="kg")
        self.units_weight = ctk.CTkOptionMenu(grid, values=["kg", "lb"], variable=self.units_weight_var)
        self.units_weight.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(grid, text="Unidades de volumen:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.units_volume_var = ctk.StringVar(value="L")
        self.units_volume = ctk.CTkOptionMenu(grid, values=["L", "gal"], variable=self.units_volume_var)
        self.units_volume.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Toggle: auto switch a Bitácora
        ctk.CTkLabel(grid, text="Auto cambiar a Bitácora:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.auto_switch_var = ctk.StringVar(value="Sí")
        self.auto_switch_opt = ctk.CTkOptionMenu(grid, values=["Sí","No"], variable=self.auto_switch_var)
        self.auto_switch_opt.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Copias de seguridad
        backup_frame = ctk.CTkFrame(scroll_container, corner_radius=10)
        backup_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(backup_frame, text="💾 Copias de seguridad", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        back_row = ctk.CTkFrame(backup_frame, fg_color="transparent")
        back_row.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(back_row, text="Carpeta de backups:").pack(side="left", padx=(0, 8))
        self.backup_entry = ctk.CTkEntry(back_row, width=380)
        self.backup_entry.pack(side="left", padx=5)
        ctk.CTkButton(back_row, text="Seleccionar…", width=120, command=self._choose_backup_dir).pack(side="left", padx=8)
        backup_btns = ctk.CTkFrame(backup_frame, fg_color="transparent")
        backup_btns.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(backup_btns, text="💾 Hacer Backup Ahora", command=self.hacer_backup_manual, fg_color="green", width=200).pack(side="left", padx=5)
        ctk.CTkButton(backup_btns, text="📂 Ver Backups", command=self.ver_backups, width=150).pack(side="left", padx=5)
        ctk.CTkButton(backup_btns, text="♻️ Restaurar Backup", command=self.restaurar_backup, fg_color="orange", width=150).pack(side="left", padx=5)

        # Cargar datos iniciales
        self._populate_fincas()

    def _populate_fincas(self):
        """Carga las fincas disponibles en el combobox."""
        try:
            from src.database.database import get_db_connection
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
                fincas = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
                self.finca_combo.configure(values=fincas)
                if fincas:
                    self.finca_combo.set(fincas[0])
        except Exception as e:
            self.logger.error(f"No se pudieron cargar fincas: {e}")

    # Navegación hacia módulos desde Ajustes
    def _navigate(self, destino: str):
        try:
            app = self.winfo_toplevel()
            if hasattr(app, "show_screen"):
                cast(Any, app).show_screen(destino)
        except Exception:
            pass

    def _change_appearance_via_app(self, modo: str):
        """Propaga el cambio de modo al app si está disponible."""
        try:
            app = self.winfo_toplevel()
            if hasattr(app, "change_appearance_mode"):
                cast(Any, app).change_appearance_mode(modo)
            else:
                # Fallback directo si no existe método en app
                ctk.set_appearance_mode("light" if modo == "Claro" else "dark")
            # Persistir preferencia
            self._set_setting("appearance", "Claro" if modo == "Claro" else "Oscuro")
        except Exception:
            # Último recurso
            ctk.set_appearance_mode("light" if modo == "Claro" else "dark")
            self._set_setting("appearance", "Claro" if modo == "Claro" else "Oscuro")

    # =========================================================
    #                   MÉTODOS ADICIONALES
    # =========================================================
    def exportar_reporte(self):
        """(Reservado) Exportar configuración o preferencias."""
        self.logger.info("Solicitada exportación de ajustes (no implementado)")

    # =============================== HERRAMIENTAS DE DESARROLLO ===============================
    
    def _is_dev_mode(self) -> bool:
        """Verifica si la aplicación está en modo desarrollo."""
        # Puede verificarse por variable de entorno, archivo de config, etc.
        return os.getenv("FINCAFACIL_DEV") == "1" or Path(".dev").exists() or True  # True por ahora (fase 1)
    
    def _create_dev_tools_section(self, parent):
        """Crea sección de herramientas para modo desarrollo."""
        dev_frame = ctk.CTkFrame(parent, corner_radius=10, border_width=2, border_color="#ff9800")
        dev_frame.pack(fill="x", pady=10)
        
        # Encabezado
        header = ctk.CTkFrame(dev_frame, fg_color="#fff3e0", corner_radius=8)
        header.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(
            header,
            text="⚙️ HERRAMIENTAS DE DESARROLLO",
            font=("Segoe UI", 14, "bold"),
            text_color="#e65100"
        ).pack(anchor="w", padx=10, pady=8)
        
        # Advertencia
        ctk.CTkLabel(
            dev_frame,
            text="⚠️  Estas herramientas solo están disponibles en modo DESARROLLO",
            font=("Segoe UI", 10, "italic"),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(5, 10))
        
        # Sección: Datos de Prueba
        test_frame = ctk.CTkFrame(dev_frame, fg_color="transparent")
        test_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            test_frame,
            text="🌱 Datos de Prueba",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 8))
        
        desc_label = ctk.CTkLabel(
            test_frame,
            text="Carga datos realistas para validar el sistema (40 animales, 7 potreros, producción de leche, "
                 "reproducción, etc.)",
            font=("Segoe UI", 11),
            text_color="gray",
            wraplength=600
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        buttons_frame = ctk.CTkFrame(test_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        ctk.CTkButton(
            buttons_frame,
            text="🌱 Cargar Datos de Prueba",
            command=self._load_test_data,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            font=("Segoe UI", 12, "bold"),
            height=38
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            buttons_frame,
            text="🗑️  Limpiar + Recargar",
            command=self._load_test_data_clear,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            font=("Segoe UI", 12),
            height=38
        ).pack(side="left")
        
        ctk.CTkLabel(
            test_frame,
            text="Sin limpiar: agrega datos  |  Limpiar: elimina previos y recarga",
            font=("Segoe UI", 9),
            text_color="gray"
        ).pack(anchor="w", pady=(8, 0))
        
        # Separador
        ctk.CTkLabel(dev_frame, text="", fg_color="transparent").pack(pady=2)
        
        # Sección: Validación
        val_frame = ctk.CTkFrame(dev_frame, fg_color="transparent")
        val_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            val_frame,
            text="✅ Validación",
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 8))
        
        ctk.CTkButton(
            val_frame,
            text="🔍 Validar Integridad de BD",
            command=self._validate_database,
            fg_color="#1f538d",
            hover_color="#164070",
            font=("Segoe UI", 12),
            height=38
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            val_frame,
            text="📊 Ver Estadísticas",
            command=self._show_statistics,
            fg_color="#6a4c93",
            hover_color="#503d7f",
            font=("Segoe UI", 12),
            height=38
        ).pack(side="left")
    
    def _load_test_data(self):
        """Carga datos de prueba sin limpiar previos."""
        from database.seed_data import run_seed
        
        respuesta = messagebox.askyesno(
            "Cargar Datos de Prueba",
            "¿Desea cargar datos de prueba realistas?\n\n"
            "Se agregarán:\n"
            "  • 40 animales\n"
            "  • 3 fincas y 7 potreros\n"
            "  • 12 servicios de reproducción\n"
            "  • 60 días de producción de leche\n"
            "  • Registros de salud y herramientas\n\n"
            "Los datos previos NO serán eliminados."
        )
        
        if not respuesta:
            return
        
        try:
            # Mostrar progreso
            progress_window = messagebox.showinfo(
                "Cargando...",
                "⏳ Cargando datos de prueba...\n\nEsto puede tomar algunos segundos."
            )
            
            self.logger.info("Iniciando carga de datos de prueba (sin limpiar)")
            success = run_seed(clear_before_seed=False, mode="dev")
            
            if success:
                messagebox.showinfo(
                    "✅ Éxito",
                    "Los datos de prueba han sido cargados correctamente.\n\n"
                    "Puedes ver los datos en los módulos:\n"
                    "  • Dashboard (KPIs actualizados)\n"
                    "  • Animales (40 cabezas)\n"
                    "  • Reproducción (gestantes, partos)\n"
                    "  • Leche (últimos 60 días)\n\n"
                    "Para más información, consulta:\n"
                    "docs/FASE1_SEED_DATOS_PRUEBA.md"
                )
                self.logger.info("✅ Datos de prueba cargados exitosamente")
            else:
                messagebox.showerror(
                    "❌ Error",
                    "No se pudieron cargar los datos de prueba.\n"
                    "Revisa los logs para más detalles:\n"
                    "logs/fincafacil.log"
                )
                self.logger.error("❌ Error al cargar datos de prueba")
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"Excepción al cargar datos de prueba:\n{e}"
            )
            self.logger.error(f"Error cargando datos de prueba: {e}")
    
    def _load_test_data_clear(self):
        """Carga datos de prueba LIMPIANDO previos."""
        respuesta = messagebox.askyesno(
            "⚠️ Limpiar y Recargar",
            "ADVERTENCIA: Esto eliminará TODOS los datos previos y cargará nuevos.\n\n"
            "Se recomienda hacer un backup antes.\n\n"
            "¿Desea continuar?"
        )
        
        if not respuesta:
            return
        
        try:
            from database.seed_data import run_seed
            
            self.logger.info("Iniciando carga de datos de prueba (CON LIMPIEZA)")
            success = run_seed(clear_before_seed=True, mode="dev")
            
            if success:
                messagebox.showinfo(
                    "✅ Éxito",
                    "✅ Base de datos limpiada y recargada con datos de prueba.\n\n"
                    "Todos los módulos ahora tienen datos frescos.\n"
                    "Los cambios se reflejarán tras reiniciar módulos o hacer refresh."
                )
                self.logger.info("✅ Datos de prueba recargados (con limpieza)")
            else:
                messagebox.showerror(
                    "❌ Error",
                    "No se pudieron cargar los datos de prueba.\n"
                    "Revisa los logs."
                )
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"Excepción: {e}"
            )
            self.logger.error(f"Error en limpiar+recargar: {e}")
    
    def _validate_database(self):
        """Valida integridad de FK y registros huérfanos."""
        try:
            from database import get_db_connection
            
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                errors = []
                
                # Validar FKs clave
                checks = [
                    ("animal", "id_finca", "finca", "id"),
                    ("animal", "raza_id", "raza", "id"),
                    ("animal", "id_potrero", "potrero", "id"),
                    ("servicio", "id_hembra", "animal", "id"),
                    ("servicio", "id_macho", "animal", "id"),
                    ("tratamiento", "id_animal", "animal", "id"),
                    ("produccion_leche", "animal_id", "animal", "id"),
                ]
                
                for table, fk_col, ref_table, ref_col in checks:
                    cur.execute(f"""
                        SELECT COUNT(*) FROM {table}
                        WHERE {fk_col} IS NOT NULL 
                        AND {fk_col} NOT IN (SELECT {ref_col} FROM {ref_table})
                    """)
                    count = cur.fetchone()[0]
                    if count > 0:
                        errors.append(f"  ❌ {table}.{fk_col}: {count} registros huérfanos")
                
                # Contar totales
                cur.execute("SELECT COUNT(*) FROM animal")
                animal_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM produccion_leche")
                leche_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM servicio")
                servicio_count = cur.fetchone()[0]
                
                if errors:
                    msg = "❌ ERRORES DE INTEGRIDAD ENCONTRADOS:\n\n" + "\n".join(errors)
                else:
                    msg = "✅ INTEGRIDAD VERIFICADA - NO HAY ERRORES\n\n"
                    msg += f"  Animales: {animal_count}\n"
                    msg += f"  Producción de leche: {leche_count}\n"
                    msg += f"  Servicios: {servicio_count}"
                
                messagebox.showinfo("Validación de BD", msg)
                self.logger.info(f"Validación: {msg}")
        except Exception as e:
            messagebox.showerror("Error en validación", f"No se pudo validar:\n{e}")
            self.logger.error(f"Error validando BD: {e}")
    
    def _show_statistics(self):
        """Muestra estadísticas de la base de datos."""
        try:
            from database import get_db_connection
            
            with get_db_connection() as conn:
                cur = conn.cursor()
                
                stats = {}
                tables = [
                    'animal', 'finca', 'potrero', 'lote', 'raza',
                    'servicio', 'reproduccion', 'tratamiento', 'peso',
                    'produccion_leche', 'muerte', 'insumo', 'herramienta'
                ]
                
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    if count > 0:
                        stats[table] = count
                
                # Crear ventana de estadísticas
                win = ctk.CTkToplevel(self)
                win.title("📊 Estadísticas de BD")
                win.geometry("400x500")
                win.grab_set()
                
                ctk.CTkLabel(
                    win,
                    text="📊 Estadísticas de Base de Datos",
                    font=("Segoe UI", 16, "bold")
                ).pack(pady=(15, 10))
                
                frame = ctk.CTkScrollableFrame(win, width=380, height=400)
                frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                total = sum(stats.values())
                for table, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
                    row = ctk.CTkFrame(frame, fg_color="transparent")
                    row.pack(fill="x", pady=4)
                    
                    ctk.CTkLabel(row, text=f"  {table}", width=180).pack(side="left", anchor="w")
                    ctk.CTkLabel(
                        row,
                        text=f"{count} registros",
                        font=("Segoe UI", 12, "bold"),
                        text_color="#2e7d32" if count > 0 else "gray"
                    ).pack(side="left")
                
                ctk.CTkLabel(
                    frame,
                    text=f"\nTotal: {total} registros",
                    font=("Segoe UI", 13, "bold"),
                    text_color="#1f538d"
                ).pack(pady=(10, 0))
                
                ctk.CTkButton(win, text="Cerrar", command=win.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener estadísticas:\n{e}")
            self.logger.error(f"Error en estadísticas: {e}")

    
        try:
            fincas = self.ajustes_service.listar_fincas_combo()
            self.finca_combo.configure(values=fincas)
        except Exception as e:
            self.logger.error(f"No se pudieron cargar fincas: {e}")

    def _choose_backup_dir(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta de backups")
        if path:
            self.backup_entry.delete(0, "end")
            self.backup_entry.insert(0, path)

    def _load_preferences(self):
        prefs = self._get_settings({
            "default_finca_id": None,
            "language": "es",
            "units_weight": "kg",
            "units_volume": "L",
            "backup_dir": str(app_config.BACKUP_DIR),
            "appearance": ctk.get_appearance_mode(),
            "auto_switch_bitacora": "true",
        })

        # Apariencia
        try:
            if prefs.get("appearance") in ("Claro", "Oscuro"):
                self.appearance_var_local.set(prefs["appearance"])
                self._change_appearance_via_app(prefs["appearance"])
        except Exception:
            pass

        # Finca por defecto
        finca_id = prefs.get("default_finca_id")
        if finca_id:
            # encontrar item que comienza con "{id} - "
            for val in self.finca_combo.cget("values"):
                if val.startswith(f"{finca_id} ") or val.startswith(f"{finca_id}-") or val.startswith(f"{finca_id} -"):
                    self.finca_combo.set(val)
                    break

        # Idioma y unidades
        self.lang_var.set(prefs.get("language", "es"))
        self.units_weight_var.set(prefs.get("units_weight", "kg"))
        self.units_volume_var.set(prefs.get("units_volume", "L"))
        self.backup_entry.delete(0, "end")
        self.backup_entry.insert(0, prefs.get("backup_dir") or str(app_config.BACKUP_DIR))
        # Auto switch bitácora
        try:
            val = prefs.get("auto_switch_bitacora", "true")
            self.auto_switch_var.set("Sí" if str(val).strip().lower() in ("1","true","sí","si","on","yes") else "No")
        except Exception:
            pass

    def _save_preferences(self):
        """Guarda las preferencias usando el gestor centralizado"""
        from modules.utils.preferences_manager import get_preferences_manager

        prefs_manager = get_preferences_manager()

        # Finca id seleccionado
        finca_val = self.finca_combo.get().strip()
        finca_id = None
        if finca_val:
            try:
                finca_id = int(finca_val.split("-", 1)[0].strip())
            except Exception:
                finca_id = None

        settings = {
            "default_finca_id": finca_id,
            "language": self.lang_var.get(),
            "units_weight": self.units_weight_var.get(),
            "units_volume": self.units_volume_var.get(),
            "backup_dir": self.backup_entry.get().strip() or str(app_config.BACKUP_DIR),
            "appearance": self.appearance_var_local.get(),
            "auto_switch_bitacora": "true" if self.auto_switch_var.get() == "Sí" else "false",
        }

        # Guardar usando el gestor centralizado
        prefs_manager.update(settings)
        if prefs_manager.save_preferences():
            # También persistir en base de datos para compatibilidad
            for k, v in settings.items():
                self._set_setting(k, str(v) if v is not None else "")

            # Ajustar backup dir en runtime (best-effort)
            try:
                from pathlib import Path
                new_dir = Path(settings["backup_dir"])
                new_dir.mkdir(parents=True, exist_ok=True)
                app_config.BACKUP_DIR = new_dir
            except Exception as e:
                self.logger.warning(f"No se pudo actualizar BACKUP_DIR en runtime: {e}")

            messagebox.showinfo("Ajustes", "Preferencias guardadas correctamente.")
            self.logger.info("Preferencias guardadas exitosamente")
        else:
            messagebox.showerror("Error", "No se pudieron guardar las preferencias.")
            self.logger.error("Error al guardar preferencias")

    def _get_settings(self, defaults: dict) -> dict:
        try:
            return self.ajustes_service.obtener_settings(defaults)
        except Exception as e:
            self.logger.warning(f"No se pudieron leer preferencias: {e}")
            return dict(defaults)

    def _set_setting(self, key: str, value: str):
        try:
            self.ajustes_service.guardar_setting(key, value)
        except Exception as e:
            self.logger.error(f"No se pudo guardar preferencia {key}: {e}")

    # Métodos duplicados eliminados: _load_preferences / _save_preferences

    def hacer_backup_manual(self):
        """Crea una copia de seguridad de la base de datos"""
        import shutil
        try:
            # Ruta de la BD actual
            from database.database import get_db_path_safe
            db_path = get_db_path_safe()
            if not db_path.exists():
                messagebox.showerror("Error", "No se encontró la base de datos")
                return
            
            # Carpeta de backup
            backup_dir = Path("backup")
            backup_dir.mkdir(exist_ok=True)
            
            # Nombre con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"fincafacil_backup_{timestamp}.db"
            backup_path = backup_dir / backup_name
            
            # Copiar BD
            shutil.copy2(db_path, backup_path)
            
            messagebox.showinfo("Éxito", f"✅ Backup creado:\n{backup_name}")
            self.logger.info(f"Backup creado: {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear backup:\n{e}")
            self.logger.error(f"Error en backup: {e}")

    def ver_backups(self):
        """Muestra lista de backups disponibles"""
        try:
            backup_dir = Path("backup")
            if not backup_dir.exists():
                messagebox.showinfo("Info", "No hay backups disponibles")
                return
            
            backups = sorted(backup_dir.glob("*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
            
            if not backups:
                messagebox.showinfo("Info", "No hay backups disponibles")
                return
            
            # Ventana con lista
            ventana = ctk.CTkToplevel(self)
            ventana.title("Backups Disponibles")
            ventana.geometry("600x400")
            
            ctk.CTkLabel(ventana, text="💾 Backups Disponibles", 
                        font=("Segoe UI", 18, "bold")).pack(pady=5)
            
            tabla = ttk.Treeview(ventana, columns=("nombre", "fecha", "tamaño"), show="headings", height=12)
            tabla.heading("nombre", text="Archivo")
            tabla.heading("fecha", text="Fecha")
            tabla.heading("tamaño", text="Tamaño")
            tabla.column("nombre", width=300)
            tabla.column("fecha", width=150)
            tabla.column("tamaño", width=100)
            # Compactar ancho (padx 20→4)
            tabla.pack(fill="both", expand=True, padx=4, pady=10)
            
            for backup in backups:
                stat = backup.stat()
                fecha = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                tamaño = f"{stat.st_size / 1024:.1f} KB"
                tabla.insert("", "end", values=(backup.name, fecha, tamaño))
            
            ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo listar backups:\n{e}")

    def restaurar_backup(self):
        """Restaura la BD desde un backup seleccionado"""
        import shutil
        try:
            backup_dir = Path("backup")
            if not backup_dir.exists():
                messagebox.showwarning("Atención", "No hay backups disponibles")
                return
            
            # Selector de archivo
            archivo = filedialog.askopenfilename(
                title="Seleccionar Backup",
                initialdir=backup_dir,
                filetypes=[("Base de datos", "*.db"), ("Todos", "*.*")]
            )
            
            if not archivo:
                return
            
            # Confirmar
            if not messagebox.askyesno("Confirmar", 
                                      "⚠️ ADVERTENCIA ⚠️\n\n"
                                      "Esto reemplazará la base de datos actual.\n"
                                      "Se recomienda hacer un backup antes.\n\n"
                                      "¿Desea continuar?"):
                return
            
            # Backup de seguridad de la BD actual
            from database.database import get_db_path_safe
            db_path = get_db_path_safe()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_backup = backup_dir / f"fincafacil_pre_restauracion_{timestamp}.db"
            shutil.copy2(db_path, safety_backup)
            
            # Restaurar
            shutil.copy2(archivo, db_path)
            
            messagebox.showinfo("Éxito", 
                              "✅ Base de datos restaurada\n\n"
                              "La aplicación se reiniciará.\n"
                              f"Backup de seguridad: {safety_backup.name}")
            self.logger.info(f"BD restaurada desde: {archivo}")
            
            # Reiniciar app
            import sys
            self.quit()
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar:\n{e}")
            self.logger.error(f"Error en restauración: {e}")

    def abrir_manual_pdf(self):
        """Abre el manual de usuario en PDF"""
        try:
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from modules.utils.pdf_generator import abrir_manual_pdf
            
            exito, mensaje = abrir_manual_pdf()
            
            if exito:
                self.logger.info("Manual PDF abierto correctamente")
            else:
                messagebox.showerror("Error", mensaje)
                self.logger.error(f"Error abriendo manual: {mensaje}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el manual:\n{e}")
            self.logger.error(f"Error abriendo manual: {e}")

    def iniciar_tour(self):
        """Inicia el tour interactivo usando el nuevo TourManager"""
        try:
            sys.path.append(str(Path(__file__).parent.parent.parent))
            from modules.utils.tour_manager import TourManager, TourStep

            app_ctk = cast(ctk.CTk, self.winfo_toplevel())

            tour = TourManager(app_ctk, tour_name="ajustes")

            # Tour básico para evitar arrancar sin pasos (se mejora en fase 5)
            tour.add_step(TourStep(
                title="Panel de Ajustes",
                description="Aquí puedes configurar copias de seguridad, reinicios y preferencias del sistema.",
                widget=None,
                duration=0
            ))

            if not tour.steps:
                messagebox.showinfo("Tour", "No hay pasos configurados para este módulo.")
                return

            tour.start_tour()
            self.logger.info("Tour interactivo iniciado con TourManager")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el tour:\n{e}")
            self.logger.error(f"Error iniciando tour: {e}")

    def _generar_todas_plantillas(self):
        """Genera todas las plantillas Excel ejecutando el script"""
        import subprocess
        try:
            # Ejecutar script de generación de plantillas
            script_path = Path("scripts/generar_plantillas_completas.py")
            if not script_path.exists():
                messagebox.showerror("Error", f"No se encontró el script:\n{script_path}")
                return
            
            # Mostrar mensaje de progreso
            respuesta = messagebox.askyesno(
                "Generar Plantillas",
                "Se generarán 23 plantillas Excel en la carpeta 'plantillas de carga'.\n\n¿Desea continuar?"
            )
            
            if not respuesta:
                return
            
            # Ejecutar script
            resultado = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.returncode == 0:
                messagebox.showinfo(
                    "Éxito",
                    f"✅ Plantillas generadas exitosamente\n\n{resultado.stdout}\n\nUbicación: plantillas de carga/"
                )
                self.logger.info("Plantillas generadas exitosamente")
                
                # Preguntar si desea abrir la carpeta
                if messagebox.askyesno("Abrir carpeta", "¿Desea abrir la carpeta de plantillas?"):
                    import platform
                    plantillas_dir = Path("plantillas de carga")
                    if platform.system() == "Windows":
                        os.startfile(plantillas_dir)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", str(plantillas_dir)])
                    else:  # Linux
                        subprocess.run(["xdg-open", str(plantillas_dir)])
            else:
                messagebox.showerror(
                    "Error",
                    f"Error al generar plantillas:\n{resultado.stderr}"
                )
                self.logger.error(f"Error generando plantillas: {resultado.stderr}")
                
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "La generación de plantillas tardó demasiado")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron generar las plantillas:\n{e}")
            self.logger.error(f"Error en _generar_todas_plantillas: {e}")

    def _download_template(self):
        """Permite descargar una plantilla Excel de un módulo seleccionado."""
        try:
            nombre = self.plantilla_combo.get().strip()
            if not nombre:
                messagebox.showwarning("Plantillas", "Seleccione un módulo para generar la plantilla.")
                return

            key = resolve_key_from_name(nombre)
            # Ruta sugerida en la carpeta solicitada por el usuario
            base_dir = ensure_templates_dir()
            default_name = suggested_filename(key)
            initial = os.path.join(base_dir, default_name)

            out_path = filedialog.asksaveasfilename(
                title="Guardar plantilla como…",
                defaultextension=".xlsx",
                initialfile=default_name,
                initialdir=base_dir,
                filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")],
            )
            if not out_path:
                return

            save_template_to_path(key, out_path)
            messagebox.showinfo("Plantillas", f"Plantilla generada:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Plantillas", f"No se pudo generar la plantilla:\n{e}")

    # ===================== SELECCIÓN MÚLTIPLE DE PLANTILLAS =====================
    def _abrir_selector_multiple(self):
        """Abre un diálogo con checkboxes para generar varias plantillas a la vez."""
        try:
            nombres = get_template_names()
            if not nombres:
                messagebox.showerror("Plantillas", "No hay plantillas disponibles")
                return

            win = ctk.CTkToplevel(self)
            win.title("Generar varias plantillas")
            win.geometry("540x620")
            win.grab_set()

            ctk.CTkLabel(win, text="Seleccione las plantillas a generar", font=("Segoe UI", 16, "bold")).pack(pady=(10,5))
            ctk.CTkLabel(win, text="Se guardarán en 'plantillas de carga'", font=("Segoe UI", 12)).pack(pady=(0,10))

            scroll = ctk.CTkScrollableFrame(win, width=500, height=430)
            scroll.pack(fill="both", expand=True, padx=10, pady=10)

            self._multi_checks = []
            for nombre in nombres:
                var = ctk.BooleanVar(value=False)
                fila = ctk.CTkFrame(scroll, fg_color="transparent")
                fila.pack(fill="x", pady=2)
                ctk.CTkCheckBox(fila, text=nombre, variable=var).pack(anchor="w")
                self._multi_checks.append((nombre, var))

            acciones = ctk.CTkFrame(win, fg_color="transparent")
            acciones.pack(fill="x", pady=10)
            ctk.CTkButton(acciones, text="Generar seleccionadas", fg_color="#1f538d", hover_color="#164070", command=lambda: self._generar_seleccionadas(win)).pack(side="left", padx=5)
            ctk.CTkButton(acciones, text="Cerrar", fg_color="#444", hover_color="#222", command=win.destroy).pack(side="right", padx=5)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el selector múltiple:\n{e}")
            if self.logger:
                self.logger.error(f"Error en _abrir_selector_multiple: {e}")

    def _generar_seleccionadas(self, win):
        """Genera las plantillas marcadas en el selector múltiple."""
        try:
            seleccionadas = [nombre for nombre, var in self._multi_checks if var.get()]
            if not seleccionadas:
                messagebox.showwarning("Plantillas", "No seleccionó ninguna plantilla")
                return

            destino = ensure_templates_dir()
            generadas = []
            errores = []
            for friendly in seleccionadas:
                key = resolve_key_from_name(friendly)
                try:
                    nombre_archivo = suggested_filename(key)
                    out_path = os.path.join(destino, nombre_archivo)
                    save_template_to_path(key, out_path)
                    generadas.append(nombre_archivo)
                except Exception as e:
                    errores.append(f"{friendly}: {e}")

            mensaje = f"Plantillas generadas: {len(generadas)}\n" + "\n".join(generadas)
            if errores:
                mensaje += "\n\nErrores:\n" + "\n".join(errores)
            messagebox.showinfo("Resultado", mensaje)
            if self.logger:
                self.logger.info(f"Generadas múltiples plantillas: {generadas}")

            # Ofrecer abrir carpeta si hubo alguna
            if generadas and messagebox.askyesno("Abrir carpeta", "¿Desea abrir la carpeta de plantillas?"):
                import subprocess, platform
                plantillas_dir = Path(destino)
                if platform.system() == "Windows":
                    os.startfile(plantillas_dir)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", str(plantillas_dir)])
                else:
                    subprocess.run(["xdg-open", str(plantillas_dir)])
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron generar las plantillas seleccionadas:\n{e}")
            if self.logger:
                self.logger.error(f"Error en _generar_seleccionadas: {e}")

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Ajustes Test")
    app.geometry("1000x700")
    
    ajustes = AjustesFrame(app)
    ajustes.pack(fill="both", expand=True)
    
    app.mainloop()