"""
Script para crear un ícono .ico a partir del logo PNG
para usar como ícono de la aplicación en Windows
"""
from PIL import Image
from pathlib import Path

def crear_icono():
    """Convierte el logo PNG a formato ICO para Windows"""
    try:
        logo_path = Path(__file__).parent.parent / "assets" / "Logo.png"
        ico_path = Path(__file__).parent.parent / "assets" / "Logo.ico"
        
        if logo_path.exists():
            img = Image.open(logo_path)
            # Crear diferentes tamaños para el ícono
            img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
            print(f"✅ Ícono creado exitosamente: {ico_path}")
            return True
        else:
            print(f"❌ No se encontró el logo en: {logo_path}")
            return False
    except Exception as e:
        print(f"❌ Error al crear ícono: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Creando ícono de la aplicación...")
    crear_icono()
