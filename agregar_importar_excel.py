"""
Script temporal para agregar el método importar_excel al módulo de registro
"""
import re

archivo = "modules/animales/registro_animal.py"

with open(archivo, 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar el final de la clase (antes del último método)
if "def limpiar_formulario(self):" in contenido:
    # Agregar el método después de limpiar_formulario
    metodo_nuevo = """
    def importar_excel(self):
        \"\"\"Importa animales desde Excel\"\"\"
        from modules.animales.importar_excel import importar_animales_desde_excel
        importar_animales_desde_excel()
        # Recargar datos si es necesario
        self.cargar_datos_combos()
"""
    
    # Buscar el final del método limpiar_formulario
    patron = r'(self\.foto_path = None\n)'
    if re.search(patron, contenido):
        contenido = re.sub(
            patron,
            r'\1' + metodo_nuevo,
            contenido
        )
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print("✅ Método importar_excel agregado correctamente")
    else:
        print("⚠️ No se pudo encontrar el lugar para agregar el método")
        print("Agregue manualmente después de limpiar_formulario:")
        print(metodo_nuevo)

