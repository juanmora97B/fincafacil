"""
Test de CTkComboBox con state='readonly'
"""
import customtkinter as ctk

fincas = ['finca el prado', 'finca el leon']
razas = ['Cebú', 'Gyr', 'Guzerá', 'Holstein', 'Jersey', 'Normando', 'Simmental', 
         'Angus', 'Brangus', 'Gyrolando', 'BON (Blanco Orejinegro)', 'Lucerna',
         'Costeño con Cuernos', 'Romosinuano', 'Sanmartinero', 'Pardo Suizo',
         'Beefmaster', 'Charolais', 'Senepol', 'Limousin', 'Hereford', 'Shorthorn',
         'Wagyu', 'Holstein x Cebú', 'Braunvieh', 'Fleckvieh', 'Braford', 'Brahman', 'Criollo']

print(f"\nFincas: {len(fincas)}")
print(f"Razas: {len(razas)}")

app = ctk.CTk()
app.title("Test ComboBox readonly")
app.geometry("600x400")

frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=20, pady=20)

# Test 1: ComboBox SIN readonly
label1 = ctk.CTkLabel(frame, text="1. ComboBox NORMAL (permite escribir):", font=("Arial", 12, "bold"))
label1.pack(pady=(10, 5))

combo1 = ctk.CTkComboBox(frame, values=fincas, width=300)
combo1.set(fincas[0])
combo1.pack(pady=5)

info1 = ctk.CTkLabel(frame, text=f"Configurado con {len(fincas)} fincas. Puedes escribir texto libre.", 
                     font=("Arial", 10), text_color="orange")
info1.pack(pady=2)

# Test 2: ComboBox CON readonly
label2 = ctk.CTkLabel(frame, text="2. ComboBox READONLY (solo selección):", font=("Arial", 12, "bold"))
label2.pack(pady=(20, 5))

try:
    combo2 = ctk.CTkComboBox(frame, values=razas[:10], width=300, state="readonly")
    combo2.set(razas[0])
    combo2.pack(pady=5)
    info2 = ctk.CTkLabel(frame, text=f"✅ state='readonly' funciona. Configurado con {len(razas[:10])} razas.", 
                         font=("Arial", 10), text_color="green")
    info2.pack(pady=2)
except Exception as e:
    error_label = ctk.CTkLabel(frame, text=f"❌ ERROR: {str(e)}", text_color="red")
    error_label.pack(pady=5)
    print(f"Error al crear ComboBox readonly: {e}")

# Test 3: ComboBox con TODAS las razas
label3 = ctk.CTkLabel(frame, text="3. ComboBox con 29 razas:", font=("Arial", 12, "bold"))
label3.pack(pady=(20, 5))

combo3 = ctk.CTkComboBox(frame, values=razas, width=300, state="readonly")
combo3.set(razas[0])
combo3.pack(pady=5)

info3 = ctk.CTkLabel(frame, text=f"Configurado con {len(razas)} razas. Haz clic para ver todas.", 
                     font=("Arial", 10), text_color="green")
info3.pack(pady=2)

# Botón para verificar valores
def mostrar_valores():
    print("\n" + "="*60)
    print("VALORES ACTUALES:")
    print(f"Combo 1 (normal): {combo1.get()}")
    print(f"Combo 3 (readonly): {combo3.get()}")
    print("="*60)

btn = ctk.CTkButton(frame, text="📋 Mostrar Valores Seleccionados", command=mostrar_valores)
btn.pack(pady=20)

print("\n" + "="*60)
print("TEST DE COMBOBOX")
print("="*60)
print(f"Fincas: {fincas}")
print(f"Razas (primeras 10): {razas[:10]}")
print(f"Total razas: {len(razas)}")
print("="*60)

app.mainloop()
