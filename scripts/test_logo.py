"""
Script de prueba para verificar que el logo se carga correctamente
"""
import customtkinter as ctk
from PIL import Image
from pathlib import Path

def test_logo():
    """Prueba la carga del logo"""
    app = ctk.CTk()
    app.title("Test Logo FincaFácil")
    app.geometry("400x500")
    
    # Probar ícono de ventana
    try:
        ico_path = Path(__file__).parent.parent / "assets" / "Logo.ico"
        if ico_path.exists():
            app.iconbitmap(str(ico_path))
            print(f"✅ Ícono de ventana cargado: {ico_path}")
    except Exception as e:
        print(f"❌ Error cargando ícono de ventana: {e}")
    
    frame = ctk.CTkFrame(app)
    frame.pack(fill="both", expand=True, padx=4, pady=20)
    
    # Probar logo en el frame
    try:
        logo_path = Path(__file__).parent.parent / "assets" / "Logo.png"
        if logo_path.exists():
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)
            logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(150, 150))
            
            logo_label = ctk.CTkLabel(frame, image=logo_ctk, text="")
            logo_label.pack(pady=20)
            
            title = ctk.CTkLabel(frame, text="FincaFácil", font=("Roboto", 24, "bold"))
            title.pack(pady=10)
            
            slogan = ctk.CTkLabel(frame, text="Gestión Ganadera Profesional", 
                                 font=("Roboto", 12, "italic"))
            slogan.pack()
            
            status = ctk.CTkLabel(frame, text="✅ Logo cargado correctamente", 
                                 font=("Roboto", 14), text_color="green")
            status.pack(pady=20)
            
            print(f"✅ Logo cargado correctamente desde: {logo_path}")
        else:
            status = ctk.CTkLabel(frame, text="❌ Logo no encontrado", 
                                 font=("Roboto", 14), text_color="red")
            status.pack(pady=20)
            print(f"❌ Logo no encontrado en: {logo_path}")
    except Exception as e:
        status = ctk.CTkLabel(frame, text=f"❌ Error: {str(e)[:50]}", 
                             font=("Roboto", 12), text_color="red")
        status.pack(pady=20)
        print(f"❌ Error cargando logo: {e}")
    
    close_btn = ctk.CTkButton(frame, text="Cerrar", command=app.quit)
    close_btn.pack(pady=10)
    
    app.mainloop()

if __name__ == "__main__":
    print("🎨 Probando visualización del logo...")
    test_logo()
