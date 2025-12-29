"""
Panel de Salud del Sistema (FASE 9)
Módulo independiente para mostrar métricas internas (solo ADMIN)

Visualiza:
- Tiempos de ejecución (detectores, KPI, snapshots)
- Tasas de cache
- Tamaño BD
- Alertas activas
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

try:
    from src.services.system_metrics_service import get_system_metrics_service
    from src.core.permissions_manager import get_permissions_manager, RoleEnum
    from src.core.error_handler import safe_ui_call, busy_ui
except ImportError:
    pass


class SaludSistemaPanel(ctk.CTkFrame):
    """Panel de salud del sistema para administradores."""

    COLORS = {
        "primary": "#1E88E5",
        "success": "#43A047",
        "warning": "#FB8C00",
        "danger": "#E53935",
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.logger = logging.getLogger(__name__)
        self.metrics_service = get_system_metrics_service()

        # Verificar permiso
        try:
            pm = get_permissions_manager()
            if pm.get_current_role() != RoleEnum.ADMINISTRADOR:
                self._crear_sin_permiso()
                return
        except Exception:
            pass

        self._crear_ui()
        self.after(500, self.actualizar_metricas)

    def _crear_sin_permiso(self):
        """Muestra mensaje de acceso denegado."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="🔒 Acceso Denegado",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=20)

        ctk.CTkLabel(
            frame,
            text="Este panel solo está disponible para administradores.",
            font=("Segoe UI", 14),
        ).pack()

    def _crear_ui(self):
        """Construye la interfaz del panel."""
        # Header
        header = ctk.CTkFrame(self, fg_color=self.COLORS["primary"])
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            header,
            text="⚙️ SALUD DEL SISTEMA - OBSERVABILIDAD",
            font=("Segoe UI", 18, "bold"),
            text_color="white",
        ).pack(pady=15)

        # Container scrollable
        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Sección 1: Tiempos de ejecución
        self._crear_seccion_tiempos(container)

        # Sección 2: Cache
        self._crear_seccion_cache(container)

        # Sección 3: Base de datos
        self._crear_seccion_bd(container)

        # Sección 4: Botones de acción
        botones_frame = ctk.CTkFrame(self)
        botones_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            botones_frame,
            text="🔄 Refrescar",
            command=self.actualizar_metricas,
            fg_color=self.COLORS["success"],
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            botones_frame,
            text="🗑️ Limpiar (>30 días)",
            command=self._limpiar_antiguas,
            fg_color=self.COLORS["warning"],
        ).pack(side="left", padx=5)

    def _crear_seccion_tiempos(self, parent):
        """Sección de tiempos de ejecución."""
        frame = ctk.CTkFrame(
            parent,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#F9F9F9",
        )
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="⏱️ Tiempos de Ejecución (últimas 24h)",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=10, pady=10)

        self.tiempos_text = ctk.CTkTextbox(frame, height=120)
        self.tiempos_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tiempos_text.configure(state="disabled")

    def _crear_seccion_cache(self, parent):
        """Sección de cache."""
        frame = ctk.CTkFrame(
            parent,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#F9F9F9",
        )
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="📦 Tasas de Cache (últimas 24h)",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=10, pady=10)

        self.cache_text = ctk.CTkTextbox(frame, height=100)
        self.cache_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.cache_text.configure(state="disabled")

    def _crear_seccion_bd(self, parent):
        """Sección de base de datos."""
        frame = ctk.CTkFrame(
            parent,
            border_width=1,
            border_color="#E0E0E0",
            fg_color="#F9F9F9",
        )
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text="🗄️ Base de Datos",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=10, pady=10)

        self.bd_text = ctk.CTkTextbox(frame, height=80)
        self.bd_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.bd_text.configure(state="disabled")

    @safe_ui_call
    def actualizar_metricas(self):
        """Actualiza todas las métricas mostradas."""
        busy_ui(self, True)

        try:
            # Tiempos de ejecución
            self._actualizar_tiempos()

            # Cache
            self._actualizar_cache()

            # BD
            self._actualizar_bd()

            self.logger.info("Métricas actualizadas")
        except Exception as e:
            self.logger.error(f"Error actualizando métricas: {e}")
        finally:
            busy_ui(self, False)

    def _actualizar_tiempos(self):
        """Actualiza sección de tiempos."""
        try:
            metricas = self.metrics_service.obtener_metricas_ultimas(
                horas=24,
                tipo="tiempo_ejecucion",
            )

            self.tiempos_text.configure(state="normal")
            self.tiempos_text.delete("1.0", "end")

            if not metricas:
                self.tiempos_text.insert("1.0", "No hay datos disponibles")
            else:
                componentes = {}
                for m in metricas:
                    comp = m["componente"]
                    if comp not in componentes:
                        componentes[comp] = []
                    componentes[comp].append(m["valor"])

                texto = ""
                for comp, tiempos in sorted(componentes.items()):
                    promedio = sum(tiempos) / len(tiempos)
                    min_t = min(tiempos)
                    max_t = max(tiempos)
                    texto += f"{comp}:\n  Promedio: {promedio:.1f}ms | Min: {min_t:.1f} | Max: {max_t:.1f}\n\n"

                self.tiempos_text.insert("1.0", texto)

            self.tiempos_text.configure(state="disabled")
        except Exception as e:
            self.logger.warning(f"Error actualizando tiempos: {e}")

    def _actualizar_cache(self):
        """Actualiza sección de cache."""
        try:
            caches = ["analytics_cache"]  # Expandible
            texto = ""

            for cache_name in caches:
                tasa = self.metrics_service.obtener_tasa_cache(cache_name, horas=24)
                if tasa["total"] > 0:
                    texto += f"{cache_name}:\n  Aciertos: {tasa['hits']} | Fallos: {tasa['misses']} | Tasa: {tasa['tasa_acierto_pct']}%\n\n"

            self.cache_text.configure(state="normal")
            self.cache_text.delete("1.0", "end")
            self.cache_text.insert("1.0", texto or "Sin datos")
            self.cache_text.configure(state="disabled")
        except Exception as e:
            self.logger.warning(f"Error actualizando cache: {e}")

    def _actualizar_bd(self):
        """Actualiza sección de BD."""
        try:
            tamaño_bytes = self.metrics_service.obtener_tamaño_bd_actual()
            tamaño_mb = tamaño_bytes / (1024 * 1024)

            texto = f"Tamaño actual: {tamaño_mb:.2f} MB\n"

            # Obtener métricas de tamaño histórico
            metricas_bd = self.metrics_service.obtener_metricas_ultimas(
                horas=24 * 7,  # Última semana
                tipo="db_size",
            )

            if metricas_bd:
                sizes = [m["valor"] / (1024 * 1024) for m in metricas_bd]
                texto += f"\nHistórico (7 días):\n"
                texto += f"  Mínimo: {min(sizes):.2f} MB\n"
                texto += f"  Máximo: {max(sizes):.2f} MB\n"
                texto += f"  Promedio: {sum(sizes) / len(sizes):.2f} MB"

            self.bd_text.configure(state="normal")
            self.bd_text.delete("1.0", "end")
            self.bd_text.insert("1.0", texto)
            self.bd_text.configure(state="disabled")
        except Exception as e:
            self.logger.warning(f"Error actualizando BD: {e}")

    @safe_ui_call
    def _limpiar_antiguas(self):
        """Limpia métricas antiguas."""
        try:
            eliminadas = self.metrics_service.limpiar_metricas_antiguas(dias=30)
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Limpieza", f"Métricas eliminadas: {eliminadas}")
            self.actualizar_metricas()
        except Exception as e:
            self.logger.error(f"Error limpiando: {e}")
