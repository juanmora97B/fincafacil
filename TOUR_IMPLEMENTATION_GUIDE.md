# Tour Interactivo Profesional - Guía de Implementación

## Descripción General

Sistema completo de tour interactivo para FincaFácil con:
- ✅ Overlay oscuro con enfoque en elementos
- ✅ Tooltips estilizados con información
- ✅ Navegación (Anterior, Siguiente, Saltar)
- ✅ Auto-avance por tiempo
- ✅ Persistencia de estado (no molesta en futuras visitas)
- ✅ Totalmente personalizable
- ✅ Responsive (funciona en cualquier resolución)

## Arquitectura del Sistema

### Componentes Principales

1. **TourManager** (`tour_manager.py`)
   - Gestiona el ciclo de vida del tour
   - Coordina overlay, tooltips y controles
   - Persiste estado en JSON

2. **TourOverlay** 
   - Canvas con efecto de oscurecimiento
   - Resalta widgets específicos
   - Efecto spotlight autoadaptativo

3. **TourTooltip**
   - Popup estilizado con título y descripción
   - Posicionamiento automático (top, bottom, left, right)
   - Diseño profesional con colores coordinados

4. **ModuleTourHelper**
   - Wrapper para integración en módulos
   - Simplifica setup de tours
   - Crea botones de tour automáticamente

5. **TourStep**
   - Definición de cada paso
   - Soporta acciones personalizadas
   - Auto-avance configurable

### Archivos

```
modules/utils/
├── tour_manager.py                    # Sistema principal (350+ líneas)
├── tour_integration_examples.py       # Ejemplos de uso
├── __init__.py                        # Exports

config/
└── tour_config.json                   # Configuración de todos los tours

TOUR_IMPLEMENTATION_GUIDE.md           # Esta guía
```

## Configuración (tour_config.json)

### Estructura

```json
{
  "dashboard": {
    "name": "Dashboard / Inicio",
    "description": "Descripción breve",
    "steps": [
      {
        "title": "Título del paso",
        "description": "Explicación detallada",
        "widget_name": "id_del_widget",  // Null si es genérico
        "duration": 0                     // 0 = manual, >0 = auto-avanza
      }
    ]
  }
}
```

### Tours Predefinidos

1. **dashboard** - Dashboard principal
2. **animales** - Módulo de animales
3. **ficha_animal** - Ficha individual
4. **reubicacion** - Movimiento de animales
5. **reportes** - Reportes y gráficas
6. **ajustes** - Configuración
7. **quick_start** - Tour express para nuevos usuarios

## Integración en Módulos

### Paso 1: Importar

```python
from modules.utils.tour_manager import ModuleTourHelper
import json
from pathlib import Path
```

### Paso 2: Inicializar en __init__

```python
class AnimalModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Crear helper
        self.tour_helper = ModuleTourHelper("animales")
        self.tour_helper.initialize_tour(
            parent.master,  # App principal
            auto_start=False  # True para auto-iniciar primer uso
        )
```

### Paso 3: Registrar Widgets

```python
def create_widgets(self):
    # Crear widgets normalmente
    self.btn_nuevo = ctk.CTkButton(self, text="+ Nuevo")
    self.tabla = ttk.Treeview(self)
    
    # Registrar para tour (nombres deben coincidir con tour_config.json)
    self.tour_helper.tour_manager.register_widget("btn_new_animal", self.btn_nuevo)
    self.tour_helper.tour_manager.register_widget("tabla_animales", self.tabla)
```

### Paso 4: Cargar Configuración

```python
def setup_tour(self):
    try:
        with open("config/tour_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            steps = config.get("animales", {}).get("steps", [])
            self.tour_helper.add_steps(steps)
    except Exception as e:
        logger.error(f"Error en tour: {e}")
```

### Paso 5: Agregar Botón de Tour

```python
def create_toolbar(self):
    toolbar = ctk.CTkFrame(self)
    
    # Botón tour
    tour_btn = self.tour_helper.show_tour_button(toolbar)
    if tour_btn:
        tour_btn.pack(side="right", padx=10)
    
    toolbar.pack(side="top", fill="x", padx=10, pady=5)
```

## Ejemplo Completo

```python
import customtkinter as ctk
from modules.utils.tour_manager import ModuleTourHelper
import json
from pathlib import Path

class AnimalModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 1. Inicializar tour
        self.tour_helper = ModuleTourHelper("animales")
        self.tour_helper.initialize_tour(
            parent.master,
            auto_start=False
        )
        
        # 2. Crear widgets
        self.create_widgets()
        
        # 3. Registrar widgets
        self.register_widgets()
        
        # 4. Cargar configuración de tour
        self.setup_tour()
    
    def create_widgets(self):
        # Toolbar con botones
        toolbar = ctk.CTkFrame(self)
        
        self.btn_nuevo = ctk.CTkButton(toolbar, text="+ Nuevo Animal")
        self.btn_nuevo.pack(side="left", padx=5)
        
        # Agregar botón de tour
        tour_btn = self.tour_helper.show_tour_button(toolbar)
        if tour_btn:
            tour_btn.pack(side="right", padx=5)
        
        toolbar.pack(side="top", fill="x", padx=10, pady=5)
        
        # Tabla de animales
        self.tabla = ctk.CTkLabel(self, text="Tabla aquí")
        self.tabla.pack(fill="both", expand=True, padx=10, pady=10)
    
    def register_widgets(self):
        self.tour_helper.tour_manager.register_widget("btn_new_animal", self.btn_nuevo)
        self.tour_helper.tour_manager.register_widget("tabla_animales", self.tabla)
    
    def setup_tour(self):
        try:
            with open("config/tour_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
                steps = config.get("animales", {}).get("steps", [])
                self.tour_helper.add_steps(steps)
        except Exception as e:
            print(f"Error: {e}")
```

## Funciones Principales

### TourManager

```python
# Crear instancia
tour = TourManager(app, tour_name="my_tour")

# Registrar widget
tour.register_widget("widget_id", widget_instance)

# Agregar pasos
tour.add_step(TourStep(...))
tour.add_steps_from_config(steps_list)

# Controlar tour
tour.start_tour()      # Inicia desde el principio
tour.next_step()       # Siguiente paso
tour.previous_step()   # Paso anterior
tour.skip_tour()       # Salir
tour.end_tour()        # Limpiar y cerrar

# Consultar estado
tour.has_completed_tour()  # ¿Se completó antes?
tour.is_running            # ¿Está ejecutándose?
```

### ModuleTourHelper

```python
# Crear helper
helper = ModuleTourHelper("module_name")

# Inicializar
helper.initialize_tour(app, auto_start=False)

# Crear botón
btn = helper.show_tour_button(parent_frame)

# Agregar pasos
helper.add_steps(steps_config)

# Acceder al manager
helper.tour_manager.start_tour()
```

## Personalización

### Cambiar Colores

En `tour_manager.py`, modificar:

```python
# TourOverlay
self.highlight_color = "#1f538d"      # Color del highlight

# TourTooltip
border_color="#1f538d"                # Color borde
text_color="#1f538d"                  # Color título
```

### Agregar Pasos Personalizados

```python
from modules.utils.tour_manager import TourStep

step = TourStep(
    title="Mi Paso",
    description="Explicación...",
    widget=my_widget,
    duration=3  # Auto-avanza en 3 segundos
)

tour.add_step(step)
```

### Acciones Personalizadas

```python
def cambiar_a_tab():
    # Cambiar a tab específica
    notebook.select(0)

step = TourStep(
    title="Pestaña",
    description="Explicación",
    widget=tab_widget,
    action=cambiar_a_tab  # Se ejecuta antes de mostrar
)
```

## Estados y Persistencia

### Archivos de Estado

Los tours completados se guardan en:
```
config/tour_[tour_name]_state.json
```

Contenido:
```json
{
  "completed": true,
  "timestamp": 1701640000.123
}
```

### Resetear Tours

```python
# Eliminar archivo de estado
import os
os.remove("config/tour_animales_state.json")

# Tour volverá a mostrarse
```

## Debugging

### Logs

Los tours registran actividad en los logs:

```
DEBUG: Registered widget: btn_new_animal
INFO: TourManager initialized: animales
INFO: Tour started: animales
DEBUG: Showing step 1: Módulo de Animales
INFO: Tour marked as completed: animales
```

### Problemas Comunes

1. **Widget no se resalta**
   - Asegurar que está registrado: `register_widget()`
   - Verificar que `widget_name` en JSON coincide

2. **Tooltip aparece fuera de pantalla**
   - Sistema automáticamente ajusta posición
   - Si persiste, verificar coordenadas de widget

3. **Tour no aparece**
   - Verificar que existe `tour_config.json`
   - Revisar que tour_name coincide
   - Ver logs para errores

4. **Estado no se persiste**
   - Asegurar permisos de escritura en `config/`
   - Crear directorio si no existe

## Performance

- **Overlay**: Canvas nativo, muy eficiente
- **Tooltips**: Tkinter standard, ligero
- **Persistencia**: JSON simple, carga instantánea
- **Memoria**: ~50KB por tour en ejecución

## Seguridad

- ✅ Sin acceso a internet
- ✅ Datos guardados localmente
- ✅ Sin tracking externo
- ✅ Compatible con SQLite offline

## Próximas Mejoras (Opcionales)

1. Animaciones de fade in/out
2. Soporte para video en pasos
3. Analytics local de tours
4. Traductor de textos automático
5. Exportar tours como PDFs
6. Grabar videos de tours

## Contacto y Soporte

Para más información, revisar:
- `modules/utils/tour_manager.py` - Código fuente completo
- `config/tour_config.json` - Configuración actual
- `modules/utils/tour_integration_examples.py` - Ejemplos prácticos
