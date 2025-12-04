"""
Script para crear el icono .ico desde el logo PNG
Ejecutar antes de compilar con PyInstaller
"""

from PIL import Image
from pathlib import Path

def crear_icono():
    """Convierte el logo PNG a formato ICO para Windows"""
    
    assets_dir = Path('assets')
    logo_path = assets_dir / 'Logo.png'
    ico_path = assets_dir / 'logo.ico'
    
    if not logo_path.exists():
        print(f"❌ Error: No se encontró {logo_path}")
        return False
    
    try:
        # Abrir imagen original
        img = Image.open(logo_path)
        
        # Convertir a RGBA si no lo está
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Crear icono con múltiples tamaños
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        print("🎨 Generando icono con múltiples resoluciones...")
        img.save(
            ico_path,
            format='ICO',
            sizes=sizes
        )
        
        print(f"✅ Icono creado exitosamente: {ico_path}")
        print(f"   Tamaños incluidos: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando icono: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  GENERADOR DE ICONO - FincaFacil")
    print("=" * 60)
    crear_icono()
    print("=" * 60)
