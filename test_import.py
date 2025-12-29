import sys
sys.path.insert(0, 'src')
sys.path.insert(0, '.')

# Test 1: Importar GlobalTour
try:
    from modules.utils.global_tour import GlobalTour
    print("✅ GlobalTour importado correctamente")
except Exception as e:
    print(f"❌ Error importando GlobalTour: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Crear instancia dummy
try:
    import customtkinter as ctk
    app = ctk.CTk()
    tour = GlobalTour(app)
    print(f"✅ GlobalTour instancia creada - {len(tour.pasos)} pasos definidos")
    app.destroy()
except Exception as e:
    print(f"❌ Error creando instancia: {e}")
    import traceback
    traceback.print_exc()
