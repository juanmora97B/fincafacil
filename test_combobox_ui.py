"""
Script de prueba para verificar ComboBox de customtkinter
"""
import customtkinter as ctk
from tkinter import messagebox

# Simular datos cargados
fincas = ['finca el prado', 'finca el leon']
razas = ['Cebú', 'Gyr', 'Guzerá', 'Holstein', 'Jersey', 'Normando', 'Simmental', 
         'Angus', 'Brangus', 'Gyrolando']

def mostrar_seleccion():
    finca_sel = combo_finca.get()
    raza_sel = combo_raza.get()
    messagebox.showinfo("Selección", f"Finca: {finca_sel}\nRaza: {raza_sel}")

# Crear ventana
app = ctk.CTk()
app.title("Test ComboBox - Registro Animales")
app.geometry("500x300")

frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Label informativo
info = ctk.CTkLabel(frame, 
                    text="🔍 Prueba de ComboBox\n\nHaz clic en cada combo para ver todas las opciones",
                    font=("Arial", 12))
info.pack(pady=10)

# Combo Finca
label_finca = ctk.CTkLabel(frame, text="Finca:", font=("Arial", 12, "bold"))
label_finca.pack(pady=(10, 5))

combo_finca = ctk.CTkComboBox(frame, values=fincas, width=300)
combo_finca.set(fincas[0])  # Establece valor inicial
combo_finca.pack(pady=5)

info_finca = ctk.CTkLabel(frame, 
                          text=f"Cargadas {len(fincas)} fincas: {', '.join(fincas)}",
                          text_color="green", font=("Arial", 10))
info_finca.pack(pady=2)

# Combo Raza
label_raza = ctk.CTkLabel(frame, text="Raza:", font=("Arial", 12, "bold"))
label_raza.pack(pady=(10, 5))

combo_raza = ctk.CTkComboBox(frame, values=razas, width=300)
combo_raza.set(razas[0])  # Establece valor inicial
combo_raza.pack(pady=5)

info_raza = ctk.CTkLabel(frame, 
                         text=f"Cargadas {len(razas)} razas (mostrando primeras 10)",
                         text_color="green", font=("Arial", 10))
info_raza.pack(pady=2)

# Botón para verificar selección
btn_verificar = ctk.CTkButton(frame, text="Verificar Selección", command=mostrar_seleccion)
btn_verificar.pack(pady=20)

print("=" * 60)
print("TEST DE COMBOBOX")
print("=" * 60)
print(f"Fincas configuradas: {fincas}")
print(f"Razas configuradas (primeras 10): {razas}")
print("=" * 60)
print("\nINSTRUCCIONES:")
print("1. Haz clic en el combo 'Finca'")
print("2. Verifica que aparezcan las 2 fincas")
print("3. Haz clic en el combo 'Raza'")
print("4. Verifica que aparezcan las 10 razas")
print("5. Selecciona valores y presiona 'Verificar Selección'")
print("=" * 60)

app.mainloop()
