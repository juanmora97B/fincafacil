"""
Test específico: ¿CTkComboBox muestra todas las opciones?
"""
import customtkinter as ctk

# Simular exactamente las 29 razas activas
razas = [
    'Cebú', 'Gyr', 'Guzerá', 'Holstein', 'Jersey', 'Normando', 'Simmental',
    'Angus', 'Brangus', 'Gyrolando', 'BON (Blanco Orejinegro)', 'Lucerna',
    'Costeño con Cuernos', 'Romosinuano', 'Sanmartinero', 'Pardo Suizo',
    'Beefmaster', 'Charolais', 'Senepol', 'Limousin', 'Hereford', 'Shorthorn',
    'Wagyu', 'Holstein x Cebú', 'Braunvieh', 'Fleckvieh', 'Braford', 'Brahman', 'Criollo'
]

app = ctk.CTk()
app.title(f"Test: {len(razas)} razas en ComboBox")
app.geometry("700x500")

frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=20, pady=20)

title = ctk.CTkLabel(frame, text=f"ComboBox con {len(razas)} razas", font=("Arial", 16, "bold"))
title.pack(pady=10)

# Info
info_frame = ctk.CTkFrame(frame, fg_color="transparent")
info_frame.pack(pady=10)

info = ctk.CTkLabel(info_frame, 
                    text=f"📊 Total de razas configuradas: {len(razas)}\n"
                         f"🔍 Haz clic en la flecha ▼ del ComboBox\n"
                         f"✅ Deberían aparecer TODAS las {len(razas)} opciones",
                    font=("Arial", 12),
                    justify="left")
info.pack()

# ComboBox readonly
combo_frame = ctk.CTkFrame(frame)
combo_frame.pack(pady=20)

ctk.CTkLabel(combo_frame, text="Raza:", font=("Arial", 12, "bold"), width=100).pack(side="left", padx=5)

combo = ctk.CTkComboBox(combo_frame, values=razas, width=400, state="readonly")
combo.set(razas[0])
combo.pack(side="left", padx=5)

# Lista de todas las razas
list_label = ctk.CTkLabel(frame, text="Lista de las 29 razas que DEBERÍAN aparecer:", 
                          font=("Arial", 12, "bold"))
list_label.pack(pady=(20, 5))

# Scrollable frame para mostrar todas
scroll_frame = ctk.CTkScrollableFrame(frame, width=650, height=200)
scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

for i, raza in enumerate(razas, 1):
    label = ctk.CTkLabel(scroll_frame, text=f"{i:2d}. {raza}", anchor="w", font=("Arial", 10))
    label.pack(fill="x", padx=5, pady=1)

# Botón de verificación
def verificar():
    seleccionada = combo.get()
    print(f"\n{'='*60}")
    print(f"Raza seleccionada: {seleccionada}")
    if seleccionada in razas:
        idx = razas.index(seleccionada) + 1
        print(f"✅ Es la raza #{idx} de {len(razas)}")
    else:
        print(f"❌ NO está en la lista de razas")
    print(f"{'='*60}\n")

btn = ctk.CTkButton(frame, text="✓ Verificar Selección", command=verificar, fg_color="green")
btn.pack(pady=10)

print("\n" + "="*70)
print(f"TEST: ComboBox con {len(razas)} razas")
print("="*70)
print("\nRazas configuradas en el ComboBox:")
for i, r in enumerate(razas, 1):
    print(f"{i:2d}. {r}")
print("="*70)
print("\nINSTRUCCIONES:")
print("1. Haz clic en la FLECHA ▼ del ComboBox")
print("2. Verifica que aparezcan TODAS las 29 razas")
print("3. Selecciona una raza")
print("4. Haz clic en 'Verificar Selección'")
print("="*70 + "\n")

app.mainloop()
