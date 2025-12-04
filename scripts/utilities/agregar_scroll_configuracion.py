"""
Script para agregar scroll a ventanas de configuración que lo necesitan
"""
import os
import re

# Lista de archivos a modificar
archivos = [
    "condiciones_corporales.py",
    "tipo_explotacion.py",
    "motivos_venta.py",
    "destino_venta.py",
    "procedencia.py",
    "causa_muerte.py",
    "diagnosticos.py",
    "proveedores.py"
]

base_path = r"C:\Users\lenovo\Desktop\FincaFacil\modules\configuracion"

def agregar_scroll_a_archivo(filepath):
    """Agrega scroll container a un archivo de configuración"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        modificado = False
        
        # Patrón 1: Reemplazar el inicio de crear_widgets para agregar scroll_container
        patron1 = r'(def crear_widgets\(self\):\s+# Título\s+titulo = ctk\.CTkLabel\(self,)'
        reemplazo1 = r'''def crear_widgets(self):
        # Frame scrollable principal para toda la interfaz
        scroll_container = ctk.CTkScrollableFrame(self)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(scroll_container,'''
        
        if re.search(patron1, contenido):
            contenido = re.sub(patron1, reemplazo1, contenido)
            modificado = True
        
        # Patrón 2: Reemplazar referencias a self por scroll_container en elementos principales
        # Frame del formulario
        contenido = re.sub(
            r'(\s+form_frame = ctk\.CTkFrame\(self)',
            r'\1'.replace('self', 'scroll_container'),
            contenido
        )
        
        # Frame de tabla
        contenido = re.sub(
            r'(\s+table_frame = ctk\.CTkFrame\(self\))',
            r'\1'.replace('self)', 'scroll_container)'),
            contenido
        )
        
        # Frame de acciones
        contenido = re.sub(
            r'(\s+action_frame = ctk\.CTkFrame\(self, fg_color="transparent"\))',
            r'\1'.replace('self,', 'scroll_container,'),
            contenido
        )
        
        # Etiquetas de separadores/títulos
        contenido = re.sub(
            r'(ctk\.CTkLabel\(self, text="[^"]*Registrad[^"]*")',
            lambda m: m.group(0).replace('self,', 'scroll_container,'),
            contenido
        )
        
        if modificado:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"✓ Actualizado: {os.path.basename(filepath)}")
            return True
        else:
            print(f"⚠ No se encontró el patrón en: {os.path.basename(filepath)}")
            return False
            
    except Exception as e:
        print(f"✗ Error en {os.path.basename(filepath)}: {e}")
        return False

def main():
    print("Agregando scroll a ventanas de configuración...\n")
    actualizados = 0
    
    for archivo in archivos:
        filepath = os.path.join(base_path, archivo)
        if os.path.exists(filepath):
            if agregar_scroll_a_archivo(filepath):
                actualizados += 1
        else:
            print(f"⚠ No se encontró: {archivo}")
    
    print(f"\n✓ Proceso completado. Archivos actualizados: {actualizados}/{len(archivos)}")

if __name__ == "__main__":
    main()
