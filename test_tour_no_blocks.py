#!/usr/bin/env python3
"""
Test de tour sin bloqueos - simula lo que hace la app
"""
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

import customtkinter as ctk
from modules.utils.global_tour import GlobalTour

def test_app():
    """Test de app con tour"""
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("FincaFacil Test")
    
    # Label para ver que la app responde
    label = ctk.CTkLabel(app, text="App iniciada", text_color="green", font=("Arial", 20))
    label.pack(pady=20)
    
    # Crear tour
    tour = GlobalTour(app)
    
    # Verificar primer uso
    print(f"[TEST] should_start_tour() = {tour.should_start_tour()}")
    
    # Si es primer uso, iniciar tour
    def iniciar_tour_si_necesario():
        if tour.should_start_tour():
            print("[TEST] 🎬 Iniciando tour...")
            tour.start_tour()
            print("[TEST] ✅ Tour iniciado exitosamente")
        else:
            print("[TEST] ⏭️ Tour no necesario (ya completado)")
            label.configure(text="Tour ya completado - saltando")
    
    # Simular lo que hace main.py
    app.after(500, iniciar_tour_si_necesario)
    
    # Verificar que la app sigue respondiendo
    def check_responsive():
        print("[TEST] App sigue respondiendo después de 3 segundos ✅")
        label.configure(text="App Respondiendo (3s después) ✅")
        app.after(5000, app.quit)
    
    app.after(3000, check_responsive)
    
    print("[TEST] Ejecutando mainloop...")
    try:
        app.mainloop()
        print("[TEST] ✅ Test completado sin bloqueos!")
    except Exception as e:
        print(f"[TEST] ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app()
