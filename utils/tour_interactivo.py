"""
Tour Interactivo para Nuevos Usuarios
"""
import customtkinter as ctk
from tkinter import messagebox
import json
import os

class TourInteractivo:
    """
    Sistema de tour interactivo que guía al usuario por primera vez
    """
    
    def __init__(self, app):
        self.app = app
        self.paso_actual = 0
        self.tour_window = None
        self.config_file = "config/tour_completado.json"
        
        # Pasos del tour
        self.pasos = [
            {
                "titulo": "¡Bienvenido a FincaFacil! 🎉",
                "mensaje": "Este sistema profesional te ayudará a gestionar tu finca ganadera de manera eficiente.\n\n¿Te gustaría hacer un recorrido rápido por las funciones principales?",
                "boton": "dashboard",
                "tipo": "bienvenida"
            },
            {
                "titulo": "1. Dashboard 📊",
                "mensaje": "Aquí verás un resumen completo de tu finca:\n\n• Total de animales\n• Animales activos\n• Valor del inventario\n• Tratamientos activos\n• Gráficos de producción\n• Eventos recientes\n• Alertas importantes\n\nEs tu centro de control principal.",
                "boton": "dashboard",
                "tipo": "explicacion"
            },
            {
                "titulo": "2. Configuración Inicial ⚙️",
                "mensaje": "Antes de comenzar, necesitas configurar:\n\n✓ Tu finca (nombre, ubicación)\n✓ Razas de animales que manejas\n✓ Potreros disponibles\n✓ Empleados (opcional)\n\n¿Quieres ir a Configuración ahora?",
                "boton": "configuracion",
                "tipo": "accion"
            },
            {
                "titulo": "3. Registrar Animales 🐄",
                "mensaje": "El módulo de Animales te permite:\n\n• Registrar nuevos animales\n• Ver ficha completa de cada animal\n• Actualizar inventario (peso, producción)\n• Importar desde Excel\n• Registrar comentarios\n\nCada animal tendrá su historial completo.",
                "boton": "animales",
                "tipo": "explicacion"
            },
            {
                "titulo": "4. Control Reproductivo 🤰",
                "mensaje": "Gestiona el ciclo reproductivo:\n\n• Registrar servicios (monta o IA)\n• Ver hembras gestantes\n• Calcular fecha de parto automático\n• Próximos partos\n• Confirmar nacimientos\n\nEl sistema calcula todo por ti (280 días).",
                "boton": "reproduccion",
                "tipo": "explicacion"
            },
            {
                "titulo": "5. Salud Veterinaria 🏥",
                "mensaje": "Mantén registro completo de salud:\n\n• Diagnósticos médicos\n• Severidad de eventos\n• Historial por animal\n• Seguimiento de tratamientos\n\nVincula tratamientos a diagnósticos.",
                "boton": "salud",
                "tipo": "explicacion"
            },
            {
                "titulo": "6. Gestión de Potreros 🌿",
                "mensaje": "Controla tus terrenos:\n\n• Registrar potreros\n• Asignar animales\n• Rotación de pastoreo\n• Control de capacidad\n• Estado del potrero\n\nOptimiza el uso de tus pasturas.",
                "boton": "potreros",
                "tipo": "explicacion"
            },
            {
                "titulo": "7. Inventario de Insumos 📦",
                "mensaje": "Controla tus suministros:\n\n• Inventario de insumos\n• Entradas y salidas\n• Alertas de bajo stock\n• Control de vencimientos\n• Costos\n\nNunca te quedarás sin medicamentos.",
                "boton": "insumos",
                "tipo": "explicacion"
            },
            {
                "titulo": "8. Herramientas y Equipos 🔧",
                "mensaje": "Gestiona tus activos:\n\n• Catálogo de herramientas\n• Estado operativo\n• Mantenimientos preventivos\n• Historial de reparaciones\n• Control de costos\n\nProlonga la vida útil de tus equipos.",
                "boton": "herramientas",
                "tipo": "explicacion"
            },
            {
                "titulo": "9. Ventas 💰",
                "mensaje": "Registra todas tus ventas:\n\n• Ventas de animales\n• Ventas de leche\n• Cliente/destino\n• Precios\n• Actualización automática de inventario\n\nControl financiero total.",
                "boton": "ventas",
                "tipo": "explicacion"
            },
            {
                "titulo": "10. Reportes 📋",
                "mensaje": "Genera reportes profesionales:\n\n• Inventario de animales\n• Producción de leche\n• Ventas por período\n• Tratamientos\n• Exportar a Excel/CSV\n\nAnálisis para toma de decisiones.",
                "boton": "reportes",
                "tipo": "explicacion"
            },
            {
                "titulo": "11. Respaldos de Seguridad 💾",
                "mensaje": "Protege tu información:\n\n• Backups manuales\n• Ver copias disponibles\n• Restaurar cuando necesites\n\nVe a Ajustes > Copias de seguridad\n\n¡Haz backups regularmente!",
                "boton": "ajustes",
                "tipo": "explicacion"
            },
            {
                "titulo": "¡Tour Completado! 🎓",
                "mensaje": "Ya conoces las funciones principales de FincaFacil.\n\nRecomendaciones:\n1. Configura tu finca primero\n2. Registra tus animales\n3. Actualiza información regularmente\n4. Haz backups frecuentes\n5. Consulta el Manual PDF en Ajustes\n\n¿Quieres empezar con la configuración?",
                "boton": "configuracion",
                "tipo": "final"
            }
        ]
    
    def debe_mostrar_tour(self):
        """Verifica si el tour debe mostrarse (primera vez)"""
        if not os.path.exists(self.config_file):
            return True
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return not config.get('completado', False)
        except:
            return True
    
    def marcar_tour_completado(self):
        """Marca el tour como completado"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({'completado': True}, f)
    
    def iniciar_tour(self):
        """Inicia el tour interactivo"""
        self.paso_actual = 0
        self.mostrar_paso()
    
    def mostrar_paso(self):
        """Muestra el paso actual del tour"""
        if self.paso_actual >= len(self.pasos):
            self.finalizar_tour()
            return
        
        paso = self.pasos[self.paso_actual]
        
        # Cerrar ventana anterior si existe
        if self.tour_window:
            self.tour_window.destroy()
        
        # Crear ventana del tour
        self.tour_window = ctk.CTkToplevel(self.app)
        self.tour_window.title("Tour Interactivo - FincaFacil")
        self.tour_window.geometry("600x450")
        self.tour_window.transient(self.app)
        self.tour_window.grab_set()
        
        # Centrar ventana
        self.tour_window.update_idletasks()
        x = (self.tour_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.tour_window.winfo_screenheight() // 2) - (450 // 2)
        self.tour_window.geometry(f"600x450+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.tour_window)
        # Compactar ancho (20→4)
        main_frame.pack(fill="both", expand=True, padx=4, pady=20)
        
        # Indicador de progreso
        progreso_label = ctk.CTkLabel(
            main_frame,
            text=f"Paso {self.paso_actual + 1} de {len(self.pasos)}",
            font=("Roboto", 12),
            text_color="gray"
        )
        progreso_label.pack(pady=(0, 10))
        
        # Título
        titulo_label = ctk.CTkLabel(
            main_frame,
            text=paso["titulo"],
            font=("Roboto", 20, "bold")
        )
        titulo_label.pack(pady=10)
        
        # Mensaje
        mensaje_frame = ctk.CTkFrame(main_frame)
        mensaje_frame.pack(fill="both", expand=True, pady=20, padx=10)
        
        mensaje_label = ctk.CTkLabel(
            mensaje_frame,
            text=paso["mensaje"],
            font=("Roboto", 13),
            wraplength=520,
            justify="left"
        )
        # Reducir padding lateral del mensaje (20→10)
        mensaje_label.pack(pady=20, padx=10)
        
        # Frame de botones
        botones_frame = ctk.CTkFrame(main_frame)
        botones_frame.pack(fill="x", pady=10)
        
        # Botón Omitir (solo si no es el primero)
        if self.paso_actual > 0:
            btn_omitir = ctk.CTkButton(
                botones_frame,
                text="Omitir Tour",
                command=self.omitir_tour,
                fg_color="gray",
                hover_color="darkgray",
                width=120
            )
            btn_omitir.pack(side="left", padx=5)
        
        # Botón Anterior (solo si no es el primero)
        if self.paso_actual > 0:
            btn_anterior = ctk.CTkButton(
                botones_frame,
                text="← Anterior",
                command=self.paso_anterior,
                width=120
            )
            btn_anterior.pack(side="left", padx=5)
        
        # Botón principal
        if paso["tipo"] == "bienvenida":
            btn_texto = "¡Empezar Tour!"
            btn_comando = self.siguiente_paso
        elif paso["tipo"] == "accion":
            btn_texto = f"Ir a {paso['boton'].title()}"
            btn_comando = lambda: self.ir_a_modulo_y_continuar(paso["boton"])
        elif paso["tipo"] == "final":
            btn_texto = "Ir a Configuración"
            btn_comando = lambda: self.finalizar_y_configurar()
        else:
            btn_texto = "Siguiente →"
            btn_comando = self.siguiente_paso
        
        btn_principal = ctk.CTkButton(
            botones_frame,
            text=btn_texto,
            command=btn_comando,
            width=150,
            font=("Roboto", 13, "bold")
        )
        btn_principal.pack(side="right", padx=5)
    
    def siguiente_paso(self):
        """Avanza al siguiente paso"""
        self.paso_actual += 1
        self.mostrar_paso()
    
    def paso_anterior(self):
        """Retrocede al paso anterior"""
        self.paso_actual -= 1
        self.mostrar_paso()
    
    def ir_a_modulo_y_continuar(self, modulo):
        """Navega al módulo y continúa el tour"""
        if self.tour_window:
            self.tour_window.destroy()
            self.tour_window = None
        
        # Navegar al módulo
        self.app.show_screen(modulo)
        
        # Continuar tour después de un momento
        self.app.after(1500, self.siguiente_paso)
    
    def omitir_tour(self):
        """Omite el resto del tour"""
        respuesta = messagebox.askyesno(
            "Omitir Tour",
            "¿Estás seguro de que quieres omitir el tour?\n\nPuedes volver a iniciarlo desde Ajustes > Tour Interactivo.",
            parent=self.tour_window
        )
        
        if respuesta:
            self.finalizar_tour()
    
    def finalizar_tour(self):
        """Finaliza el tour"""
        if self.tour_window:
            self.tour_window.destroy()
            self.tour_window = None
        
        self.marcar_tour_completado()
        
        messagebox.showinfo(
            "Tour Completado",
            "¡Has completado el tour de FincaFacil!\n\nSi necesitas ayuda, consulta el Manual PDF en Ajustes.\n\n¡Mucho éxito con tu finca!"
        )
    
    def finalizar_y_configurar(self):
        """Finaliza el tour y va a configuración"""
        if self.tour_window:
            self.tour_window.destroy()
            self.tour_window = None
        
        self.marcar_tour_completado()
        self.app.show_screen("configuracion")
        
        messagebox.showinfo(
            "¡Comencemos!",
            "Ahora configuraremos tu finca.\n\nAgrega los datos básicos en los catálogos de configuración."
        )
    
    def resetear_tour(self):
        """Resetea el tour para volver a mostrarlo"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
