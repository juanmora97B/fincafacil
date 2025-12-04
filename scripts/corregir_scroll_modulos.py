"""
Script para corregir el problema de scroll en módulos principales
Cambia CTkScrollableFrame por CTkFrame con scroll interno
"""
import re
from pathlib import Path

# Módulos a corregir
modulos = [
    "modules/insumos/insumos_main.py",
    "modules/nomina/nomina_main.py",
    "modules/potreros/potreros_main.py",
    "modules/reportes/reportes_main.py",
    "modules/reproduccion/reproduccion_main.py",
    "modules/salud/salud_main.py",
    "modules/tratamientos/tratamientos_main.py",
    "modules/ventas/ventas_main.py",
]

def corregir_modulo(ruta):
    """Corrige un módulo"""
    archivo = Path(ruta)
    
    if not archivo.exists():
        print(f"❌ No existe: {ruta}")
        return False
    
    contenido = archivo.read_text(encoding='utf-8')
    original = contenido
    
    # 1. Cambiar clase de CTkScrollableFrame a CTkFrame
    contenido = re.sub(
        r'class\s+(\w+)\(ctk\.CTkScrollableFrame\):',
        r'class \1(ctk.CTkFrame):',
        contenido
    )
    
    # 2. Buscar el __init__ y su self.pack
    # Cambiar self.pack(fill="both", expand=True, padx=X, pady=Y) por self.pack(fill="both", expand=True)
    contenido = re.sub(
        r'(def __init__\(self, master\):.*?super\(\).__init__\(master\).*?)self\.pack\(fill="both", expand=True(?:, padx=\d+(?:, pady=\d+)?)?\)',
        r'\1self.pack(fill="both", expand=True)',
        contenido,
        flags=re.DOTALL
    )
    
    # 3. Encontrar el primer método después de __init__ (normalmente crear_widgets)
    # e insertar el scroll_container al inicio
    patron_crear = r'(def crear_widgets\(self\):.*?\n)([ \t]+)(#.*?\n|[^#])'
    
    def agregar_scroll(match):
        inicio = match.group(1)
        indent = match.group(2)
        siguiente = match.group(3)
        
        scroll_code = f'''{inicio}{indent}# Frame scrollable interno
{indent}scroll_container = ctk.CTkScrollableFrame(self)
{indent}scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
{indent}
{indent}{siguiente}'''
        return scroll_code
    
    contenido = re.sub(patron_crear, agregar_scroll, contenido, count=1)
    
    # 4. Cambiar primera referencia self a scroll_container en crear_widgets
    # (solo la primera referencia después de crear scroll_container)
    def reemplazar_primer_self(texto):
        lineas = texto.split('\n')
        scroll_encontrado = False
        primera_referencia = False
        
        nuevas_lineas = []
        for linea in lineas:
            if 'scroll_container = ctk.CTkScrollableFrame(self)' in linea:
                scroll_encontrado = True
                nuevas_lineas.append(linea)
            elif scroll_encontrado and not primera_referencia:
                # Buscar self. pero no self.crear, self.cargar, self.mostrar, etc
                if re.search(r'([^a-zA-Z_])self\s*,', linea) or 'titulo = ctk.CTkLabel(\n            self,' in linea or re.search(r'= ctk\.\w+\(\s*self\s*[,)]', linea):
                    linea = re.sub(r'(\W)self(\s*[,)])', r'\1scroll_container\2', linea, count=1)
                    primera_referencia = True
                nuevas_lineas.append(linea)
            else:
                nuevas_lineas.append(linea)
        
        return '\n'.join(nuevas_lineas)
    
    contenido = reemplazar_primer_self(contenido)
    
    if contenido != original:
        archivo.write_text(contenido, encoding='utf-8')
        print(f"✓ Corregido: {ruta}")
        return True
    else:
        print(f"⚠ Sin cambios: {ruta}")
        return False

def main():
    print("Corrigiendo módulos principales...\n")
    
    corregidos = 0
    for modulo in modulos:
        if corregir_modulo(modulo):
            corregidos += 1
    
    print(f"\n✅ {corregidos}/{len(modulos)} módulos corregidos")

if __name__ == "__main__":
    main()
