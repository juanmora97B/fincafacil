#!/usr/bin/env python3
"""
Test simple del tour para verificar que no se bloquea
"""
import customtkinter as ctk
from src.modules.utils.global_tour import GlobalTour
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

def test_tour():
    """Test básico del tour"""
    print("[TEST] Iniciando aplicación y tour...")
    
    # Crear app
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("Test Tour")
    
    # Crear tour
    tour = GlobalTour(app)
    
    # Label para verificar que la app está respondiendo
    label = ctk.CTkLabel(app, text="App Respondiendo ✓", text_color="green")
    label.pack(pady=20)
    
    # Usar after para iniciar el tour sin bloquear
    def iniciar_tour():
        print("[TEST] Iniciando start_tour()...")
        tour.start_tour()
        print("[TEST] start_tour() retornó sin bloqueos")
    
    # Schedule después de 1 segundo
    app.after(1000, iniciar_tour)
    
    # Verificar que la app sigue respondiendo
    def check_responsive():
        label.configure(text="App Respondiendo ✓ - Label actualizado")
        print("[TEST] App sigue respondiendo después de 3 segundos")
        # Cerrar app después de 10 segundos
        app.after(7000, app.quit)
    
    app.after(3000, check_responsive)
    
    print("[TEST] Ejecutando mainloop...")
    app.mainloop()
    print("[TEST] Test completado sin bloqueos!")

if __name__ == "__main__":
    test_tour()
