"""
Prueba Integrada del Módulo Inventario V2
Ejecuta el módulo en una ventana standalone para testing
"""

import customtkinter as ctk
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar módulo
from modules.animales.inventario_v2 import InventarioGeneralFrame, ejecutar_migracion_inventario


class TestApp(ctk.CTk):
    """Aplicación de prueba"""
    
    def __init__(self):
        super().__init__()
        
        self.title("🧪 Test: Inventario General V2")
        self.geometry("1600x900")
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Ejecutar migración
        print("\n🔧 Ejecutando migración previa...")
        ejecutar_migracion_inventario()
        
        # Crear frame del módulo
        self.frame = InventarioGeneralFrame(self)
        self.frame.pack(fill="both", expand=True)
        
        print("\n✅ Módulo cargado correctamente")
        print("📋 Prueba los siguientes elementos:")
        print("   - Selector de finca (debe cargar filtros dependientes)")
        print("   - Búsqueda por código/nombre")
        print("   - Botones de acción (Ver, Editar, Reubicar, Eliminar)")
        print("   - Botón Gráficas (abre ventana con 6 charts)")
        print("   - Exportar a Excel")
        print("   - Colores de fila (verde = inventariado)")
        print("   - Scroll vertical y horizontal")
        print("   - Redimensionar ventana (tabla debe expandirse)\n")


if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
