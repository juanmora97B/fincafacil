"""
Test: CTkComboBox - verificar si acepta state='readonly'
"""
import customtkinter as ctk
import inspect

print("\n" + "="*70)
print("INVESTIGACIÓN: CTkComboBox y parámetro 'state'")
print("="*70)
print(f"CustomTkinter version: {ctk.__version__}")

# Verificar firma de CTkComboBox
print("\nParámetros de CTkComboBox.__init__:")
sig = inspect.signature(ctk.CTkComboBox.__init__)
for param_name, param in sig.parameters.items():
    if param_name != 'self':
        default = param.default if param.default != inspect.Parameter.empty else "No default"
        print(f"  - {param_name}: {default}")

# Test práctico
print("\n" + "="*70)
print("TEST PRÁCTICO")
print("="*70)

app = ctk.CTk()
app.title("Test state parameter")
app.geometry("500x300")

frame = ctk.CTkFrame(app)
frame.pack(fill="both", expand=True, padx=20, pady=20)

valores = ['Opción 1', 'Opción 2', 'Opción 3']

# Test 1: Sin state
try:
    combo1 = ctk.CTkComboBox(frame, values=valores, width=300)
    combo1.pack(pady=10)
    label1 = ctk.CTkLabel(frame, text="✅ ComboBox sin 'state' creado correctamente", text_color="green")
    label1.pack()
    print("✅ ComboBox sin 'state': OK")
except Exception as e:
    label1 = ctk.CTkLabel(frame, text=f"❌ Error: {e}", text_color="red")
    label1.pack()
    print(f"❌ Error sin 'state': {e}")

# Test 2: Con state='readonly'
try:
    combo2 = ctk.CTkComboBox(frame, values=valores, width=300, state="readonly")
    combo2.pack(pady=10)
    label2 = ctk.CTkLabel(frame, text="✅ ComboBox con state='readonly' creado correctamente", text_color="green")
    label2.pack()
    print("✅ ComboBox con state='readonly': OK")
    
    # Verificar si realmente es readonly
    print(f"   Estado del combo: {combo2.cget('state')}")
except Exception as e:
    label2 = ctk.CTkLabel(frame, text=f"❌ Error con state='readonly': {e}", text_color="red")
    label2.pack()
    print(f"❌ Error con state='readonly': {e}")

# Test 3: Con state='disabled'
try:
    combo3 = ctk.CTkComboBox(frame, values=valores, width=300, state="disabled")
    combo3.pack(pady=10)
    label3 = ctk.CTkLabel(frame, text="✅ ComboBox con state='disabled' creado correctamente", text_color="green")
    label3.pack()
    print("✅ ComboBox con state='disabled': OK")
except Exception as e:
    label3 = ctk.CTkLabel(frame, text=f"❌ Error con state='disabled': {e}", text_color="red")
    label3.pack()
    print(f"❌ Error con state='disabled': {e}")

print("="*70 + "\n")

app.mainloop()
