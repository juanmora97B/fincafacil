#!/usr/bin/env python3
"""
Test de tour con logging detallado
"""
import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

# Desactivar logging de DB para prueba limpia
os.environ['TESTING'] = '1'

import customtkinter as ctk
from modules.utils.global_tour import GlobalTour
import time

def test_app_with_logging():
    """Test de app con tour y logging detallado"""
    print("\n" + "="*60)
    print("[TEST] Iniciando test de tour sin bloqueos")
    print("="*60 + "\n")
    
    # Crear app
    print("[STEP 1] Creando aplicación CTk...")
    app = ctk.CTk()
    app.geometry("800x600")
    app.title("FincaFacil Test - Tour")
    app.withdraw()  # No mostrar por ahora
    
    # Label para ver que la app responde
    main_label = ctk.CTkLabel(app, text="App iniciada", text_color="green", font=("Arial", 20))
    main_label.pack(pady=20)
    print("[STEP 1] ✅ Aplicación creada\n")
    
    # Crear tour
    print("[STEP 2] Creando instancia de GlobalTour...")
    try:
        tour = GlobalTour(app)
        print(f"[STEP 2] ✅ GlobalTour creado con {len(tour.pasos)} pasos\n")
    except Exception as e:
        print(f"[STEP 2] ❌ Error creando GlobalTour: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Mostrar app
    print("[STEP 3] Mostrando ventana principal...")
    app.deiconify()
    print("[STEP 3] ✅ Ventana principal visible\n")
    
    # Verificar primer uso
    print("[STEP 4] Verificando si es primer uso...")
    try:
        should_start = tour.should_start_tour()
        print(f"[STEP 4] ✅ should_start_tour() = {should_start}\n")
    except Exception as e:
        print(f"[STEP 4] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Iniciar tour
    def iniciar_tour_si_necesario():
        print("[STEP 5] Iniciando tour (si es necesario)...")
        if tour.should_start_tour():
            try:
                print("[STEP 5] 🎬 Iniciando start_tour()...")
                tour.start_tour()
                print("[STEP 5] ✅ start_tour() retornó sin bloqueos\n")
                main_label.configure(text="Tour iniciado ✓")
            except Exception as e:
                print(f"[STEP 5] ❌ Error en start_tour(): {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("[STEP 5] ⏭️ Tour no necesario (ya completado)\n")
            main_label.configure(text="Tour ya completado")
    
    # Simular lo que hace main.py
    app.after(500, iniciar_tour_si_necesario)
    
    # Verificar que la app sigue respondiendo
    def check_responsive():
        print("[STEP 6] Verificando que app sigue respondiendo (3s después)...")
        main_label.configure(text="App Respondiendo (3s después) ✓")
        print("[STEP 6] ✅ App sigue respondiendo\n")
        print("[STEP 7] Esperando otros 5s y cerrando...")
        app.after(5000, app.quit)
    
    app.after(3000, check_responsive)
    
    print("[TEST] Ejecutando mainloop...\n")
    try:
        app.mainloop()
        print("\n" + "="*60)
        print("[TEST] ✅ TEST COMPLETADO SIN BLOQUEOS!")
        print("="*60 + "\n")
        return True
    except Exception as e:
        print(f"\n[TEST] ❌ Error en mainloop: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_with_logging()
    sys.exit(0 if success else 1)
