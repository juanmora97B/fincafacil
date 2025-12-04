import sys
import traceback

sys.path.insert(0, '.')
sys.path.insert(0, './src')

tests = [
    ("DashboardModule", "from modules.dashboard.dashboard_main import DashboardModule"),
    ("AjustesFrame", "from modules.ajustes.ajustes_main import AjustesFrame"),
    ("VentasModule", "from modules.ventas.ventas_main import VentasModule"),
    ("logger", "from modules.utils.logger import setup_logger, get_logger"),
    ("database", "from database import inicializar_base_datos, verificar_base_datos, asegurar_esquema_minimo, asegurar_esquema_completo"),
    ("config", "from config import config"),
]

for name, import_str in tests:
    print(f"Importando {name}...", end=' ')
    try:
        exec(import_str)
        print("✅")
    except Exception as e:
        print(f"❌\n{e}")
        traceback.print_exc()
        break

print("\n✅ Todos los imports OK!")
