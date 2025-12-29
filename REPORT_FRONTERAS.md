# REPORT_FRONTERAS

Fecha de generación: 2025-12-22 20:02:39
Archivos escaneados: 128
Violaciones detectadas: 78

| Archivo | Regla violada | Import detectado | Severidad |
|---------|---------------|------------------|-----------|
| main.py | UI no puede importar Infraestructura (BD/IO) | from database import inicializar_base_datos | CRÍTICA |
| main.py | UI no puede importar Infraestructura (BD/IO) | from database import verificar_base_datos | CRÍTICA |
| main.py | UI no puede importar Infraestructura (BD/IO) | from database import asegurar_esquema_minimo | CRÍTICA |
| main.py | UI no puede importar Infraestructura (BD/IO) | from database import asegurar_esquema_completo | CRÍTICA |
| main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_path_safe | CRÍTICA |
| modules/ajustes/ajustes_main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/main.py | UI no puede importar Infraestructura (BD/IO) | from database import inicializar_base_datos | CRÍTICA |
| src/main.py | UI no puede importar Infraestructura (BD/IO) | from database import verificar_base_datos | CRÍTICA |
| src/main.py | UI no puede importar Infraestructura (BD/IO) | from database import asegurar_esquema_minimo | CRÍTICA |
| src/main.py | UI no puede importar Infraestructura (BD/IO) | from database import asegurar_esquema_completo | CRÍTICA |
| src/main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_path_safe | CRÍTICA |
| src/modules/ajustes/ajustes_main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/ajustes/ajustes_main.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.ajustes import AjustesService | CRÍTICA |
| src/modules/ajustes/ajustes_main.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.ajustes import AjustesRepository | CRÍTICA |
| src/modules/ajustes/ajustes_main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_path_safe | CRÍTICA |
| src/modules/ajustes/ajustes_main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_path_safe | CRÍTICA |
| src/modules/animales/__init__.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/actualizacion_inventario.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/animales/bitacora_comentarios.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/bitacora_comentarios.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/animales/bitacora_historial_reubicaciones.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/bitacora_reubicaciones.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/animales/ficha_animal.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/ficha_animal.py | UI no puede importar Infraestructura (BD/IO) | from database.database import reubicar_animal | CRÍTICA |
| src/modules/animales/importar_excel.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/animales/inventario_v2.py | UI no puede importar Infraestructura (BD/IO) | from database import get_db_connection | CRÍTICA |
| src/modules/animales/inventario_v2.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/modal_reubicar_animal.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.animales.animal_service import AnimalService | CRÍTICA |
| src/modules/animales/realizar_inventario.py | UI no puede importar Infraestructura (BD/IO) | from database import get_db_connection | CRÍTICA |
| src/modules/animales/realizar_inventario.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/registro_animal.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.animales.animal_service import AnimalService | CRÍTICA |
| src/modules/animales/registro_animal.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/reubicacion.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/animales/reubicacion.py | UI no puede importar Infraestructura (BD/IO) | from database.database import reubicar_animal | CRÍTICA |
| src/modules/animales/ventana_graficas.py | UI no puede importar Infraestructura (BD/IO) | from database import get_db_connection | CRÍTICA |
| src/modules/animales/ventana_graficas.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/configuracion/calidad_animal.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/calidad_animal.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionRepository | CRÍTICA |
| src/modules/configuracion/causa_muerte.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/causa_muerte.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionRepository | CRÍTICA |
| src/modules/configuracion/condiciones_corporales.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/configuracion/destino_venta.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/configuracion/diagnosticos.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/diagnosticos.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionRepository | CRÍTICA |
| src/modules/configuracion/empleados.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/empleados.py | UI no puede importar Infraestructura (BD/IO) | from database.database import DB_PATH | CRÍTICA |
| src/modules/configuracion/fincas.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/motivos_venta.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/potreros.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/configuracion/procedencia.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/procedencia.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionRepository | CRÍTICA |
| src/modules/configuracion/proveedores.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/configuracion/razas.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/sectores.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion.configuracion_service import ConfiguracionService | CRÍTICA |
| src/modules/configuracion/tipo_explotacion.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.configuracion.configuracion_service import ConfiguracionService | CRÍTICA |
| src/modules/dashboard/dashboard_main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |
| src/modules/herramientas/herramientas_main.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/insumos/insumos_main.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/leche/pesaje_leche.py | UI no puede importar Infraestructura (BD/IO) | from database import get_db_connection | CRÍTICA |
| src/modules/nomina/nomina_main.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/potreros/potreros_main.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.potreros import PotrerosService | CRÍTICA |
| src/modules/potreros/potreros_main.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.potreros import PotrerosRepository | CRÍTICA |
| src/modules/reportes/reportes_main.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/reportes/reportes_profesional.py | UI no puede importar Infraestructura (BD/IO) | from database import db | CRÍTICA |
| src/modules/reproduccion/reproduccion_main.py | UI no puede importar Infraestructura (BD/IO) | from infraestructura.reproduccion import ReproduccionService | CRÍTICA |
| src/modules/utils/__init__.py | Uso de legacy validaciones.py en código nuevo | from modules.utils.validaciones import validar_texto | CRÍTICA |
| src/modules/utils/__init__.py | Uso de legacy validaciones.py en código nuevo | from modules.utils.validaciones import validar_numero | CRÍTICA |
| src/modules/utils/__init__.py | Uso de legacy validaciones.py en código nuevo | from modules.utils.validaciones import validar_email | CRÍTICA |
| src/modules/utils/__init__.py | Uso de legacy validaciones.py en código nuevo | from modules.utils.validaciones import validar_telefono | CRÍTICA |
| src/modules/utils/data_filters.py | Utils no puede depender de Infraestructura | from database.services import get_db_service | CRÍTICA |
| src/modules/utils/importador_excel.py | Utils no puede depender de Infraestructura | from database.database import get_db_connection | CRÍTICA |
| src/modules/utils/license_manager.py | Utils no puede depender de Infraestructura | from database.services import get_path_service | CRÍTICA |
| src/modules/utils/notificaciones.py | Utils no puede depender de Infraestructura | from database.services import get_db_service | CRÍTICA |
| src/modules/utils/sistema_alertas.py | Utils no puede depender de Infraestructura | from database.services import get_db_service | CRÍTICA |
| src/modules/utils/units_helper.py | Utils no puede depender de Infraestructura | from database.services import get_db_service | CRÍTICA |
| src/modules/utils/usuario_manager.py | Utils no puede depender de Infraestructura | from database.services import get_path_service | CRÍTICA |
| src/modules/utils/validators.py | Utils no puede depender de Infraestructura | from database.database import get_db_connection | CRÍTICA |
| src/modules/ventas/ventas_main.py | UI no puede importar Infraestructura (BD/IO) | from database.database import get_db_connection | CRÍTICA |