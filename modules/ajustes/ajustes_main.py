import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil
from datetime import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from database import db


class AjustesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.crear_widgets()

    def crear_widgets(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="🔧 Ajustes del Sistema",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=15)

        # Frame principal con tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab: Respaldo
        self.frame_respaldo = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_respaldo, text="💾 Respaldo de Datos")

        # Tab: Información del Sistema
        self.frame_info = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_info, text="ℹ️ Información")

        # Tab: Mantenimiento
        self.frame_mantenimiento = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.frame_mantenimiento, text="🔧 Mantenimiento")

        # Crear contenido
        self.crear_tab_respaldo()
        self.crear_tab_info()
        self.crear_tab_mantenimiento()

    def crear_tab_respaldo(self):
        """Tab de respaldo de datos"""
        main_frame = ctk.CTkFrame(self.frame_respaldo)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="💾 Respaldo de Base de Datos",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Información
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=10)

        info_text = """
📋 IMPORTANTE: Realiza respaldos periódicos de tu base de datos.

El respaldo creará una copia completa de todos tus datos.
Guarda el archivo de respaldo en un lugar seguro.
        """
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Segoe UI", 12),
            justify="left",
            wraplength=600
        ).pack(pady=15, padx=15)

        # Ubicación actual
        ubicacion_frame = ctk.CTkFrame(main_frame)
        ubicacion_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(ubicacion_frame, text="Ubicación actual:", width=150).pack(side="left", padx=5)
        db_path = os.path.abspath("database/fincafacil.db")
        self.label_ubicacion = ctk.CTkLabel(
            ubicacion_frame,
            text=db_path,
            font=("Segoe UI", 10),
            anchor="w"
        )
        self.label_ubicacion.pack(side="left", padx=5, fill="x", expand=True)

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="💾 Crear Respaldo",
            command=self.crear_respaldo,
            fg_color="green",
            hover_color="#006400",
            width=200,
            height=40
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="📂 Restaurar desde Respaldo",
            command=self.restaurar_respaldo,
            width=200,
            height=40
        ).pack(side="left", padx=10)

    def crear_tab_info(self):
        """Tab de información del sistema"""
        main_frame = ctk.CTkScrollableFrame(self.frame_info)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="ℹ️ Información del Sistema",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Información de la base de datos
        info_db_frame = ctk.CTkFrame(main_frame)
        info_db_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            info_db_frame,
            text="📊 Base de Datos",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=10, padx=15)

        self.label_info_db = ctk.CTkLabel(
            info_db_frame,
            text="Cargando información...",
            font=("Segoe UI", 12),
            justify="left",
            anchor="w"
        )
        self.label_info_db.pack(pady=10, padx=15, fill="x")

        # Información del sistema
        info_sistema_frame = ctk.CTkFrame(main_frame)
        info_sistema_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            info_sistema_frame,
            text="💻 Sistema",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", pady=10, padx=15)

        info_sistema = f"""
Versión: FincaFácil 1.0
Python: {sys.version.split()[0]}
Sistema Operativo: {os.name}
Directorio de Trabajo: {os.getcwd()}
        """
        ctk.CTkLabel(
            info_sistema_frame,
            text=info_sistema,
            font=("Segoe UI", 12),
            justify="left",
            anchor="w"
        ).pack(pady=10, padx=15, fill="x")

        # Actualizar información
        btn_actualizar = ctk.CTkButton(
            main_frame,
            text="🔄 Actualizar Información",
            command=self.actualizar_info,
            width=200
        )
        btn_actualizar.pack(pady=10)

        # Cargar información inicial
        self.actualizar_info()

    def crear_tab_mantenimiento(self):
        """Tab de mantenimiento"""
        main_frame = ctk.CTkFrame(self.frame_mantenimiento)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text="🔧 Mantenimiento de Base de Datos",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 20))

        # Opciones de mantenimiento
        opciones_frame = ctk.CTkFrame(main_frame)
        opciones_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            opciones_frame,
            text="Opciones de Mantenimiento:",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=10, padx=15)

        # Botones de mantenimiento
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Actualizar Estructura BD",
            command=self.actualizar_estructura,
            width=250,
            height=40
        ).pack(pady=5)

        ctk.CTkButton(
            btn_frame,
            text="🧹 Optimizar Base de Datos",
            command=self.optimizar_bd,
            width=250,
            height=40
        ).pack(pady=5)

        ctk.CTkButton(
            btn_frame,
            text="📊 Ver Estadísticas de BD",
            command=self.ver_estadisticas,
            width=250,
            height=40
        ).pack(pady=5)

    def crear_respaldo(self):
        """Crea un respaldo de la base de datos"""
        try:
            db_path = "database/fincafacil.db"
            if not os.path.exists(db_path):
                messagebox.showerror("Error", "La base de datos no existe")
                return

            # Nombre del archivo con fecha
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_respaldo = f"fincafacil_backup_{fecha}.db"

            # Seleccionar ubicación
            archivo = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")],
                initialfile=nombre_respaldo,
                title="Guardar Respaldo"
            )

            if archivo:
                shutil.copy2(db_path, archivo)
                messagebox.showinfo("Éxito", f"Respaldo creado exitosamente en:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el respaldo:\n{e}")

    def restaurar_respaldo(self):
        """Restaura la base de datos desde un respaldo"""
        try:
            archivo = filedialog.askopenfilename(
                filetypes=[("Base de datos SQLite", "*.db"), ("Todos los archivos", "*.*")],
                title="Seleccionar Respaldo"
            )

            if archivo:
                respuesta = messagebox.askyesno(
                    "Confirmar",
                    "⚠️ ADVERTENCIA: Esta acción reemplazará la base de datos actual.\n"
                    "¿Desea continuar?"
                )

                if respuesta:
                    # Crear respaldo de la BD actual antes de restaurar
                    db_path = "database/fincafacil.db"
                    if os.path.exists(db_path):
                        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                        respaldo_actual = f"database/fincafacil_backup_antes_restaurar_{fecha}.db"
                        shutil.copy2(db_path, respaldo_actual)

                    # Restaurar
                    shutil.copy2(archivo, db_path)
                    messagebox.showinfo("Éxito", "Base de datos restaurada exitosamente.\nReinicia la aplicación.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo restaurar el respaldo:\n{e}")

    def actualizar_info(self):
        """Actualiza la información de la base de datos"""
        try:
            db_path = "database/fincafacil.db"
            if not os.path.exists(db_path):
                self.label_info_db.configure(text="Base de datos no encontrada")
                return

            # Tamaño del archivo
            tamaño = os.path.getsize(db_path)
            tamaño_mb = tamaño / (1024 * 1024)

            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Contar tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tablas = cursor.fetchall()
                num_tablas = len(tablas)

                # Contar registros en tablas principales
                info_text = f"""
Ubicación: {os.path.abspath(db_path)}
Tamaño: {tamaño_mb:.2f} MB
Número de Tablas: {num_tablas}

Registros en Tablas Principales:
"""
                tablas_principales = ['animales', 'potreros', 'fincas', 'empleados', 'ventas', 'tratamientos']
                for tabla in tablas_principales:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                        count = cursor.fetchone()[0]
                        info_text += f"  • {tabla.capitalize()}: {count} registros\n"
                    except:
                        pass

            self.label_info_db.configure(text=info_text)
        except Exception as e:
            self.label_info_db.configure(text=f"Error al cargar información: {e}")

    def actualizar_estructura(self):
        """Actualiza la estructura de la base de datos"""
        try:
            from database.actualizar_db import actualizar_base_datos
            actualizar_base_datos()
            messagebox.showinfo("Éxito", "Estructura de la base de datos actualizada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar estructura:\n{e}")

    def optimizar_bd(self):
        """Optimiza la base de datos"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("VACUUM")
                cursor.execute("ANALYZE")
                conn.commit()
            messagebox.showinfo("Éxito", "Base de datos optimizada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al optimizar:\n{e}")

    def ver_estadisticas(self):
        """Muestra estadísticas de la base de datos"""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                stats = "📊 ESTADÍSTICAS DE LA BASE DE DATOS\n\n"

                # Tablas y registros
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tablas = cursor.fetchall()

                for tabla in tablas:
                    nombre = tabla[0]
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {nombre}")
                        count = cursor.fetchone()[0]
                        stats += f"• {nombre}: {count} registros\n"
                    except:
                        pass

                messagebox.showinfo("Estadísticas", stats)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener estadísticas:\n{e}")

