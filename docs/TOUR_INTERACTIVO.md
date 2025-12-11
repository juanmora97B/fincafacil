# Sistema de Tour Interactivo - FincaFácil

## Overview
El tour interactivo es una guía visual que se ejecuta automáticamente en el **primer uso** del sistema. Guía al usuario a través de los módulos principales y explica sus funciones.

## Características

### 1. **Auto-inicio en Primer Uso**
- Se ejecuta automáticamente cuando se abre la aplicación por primera vez
- No molesta en usos posteriores
- El usuario puede reiniciar el tour desde **Ajustes > Reiniciar Tour**

### 2. **Pasos del Tour Global**
El tour cubre:
1. Bienvenida al sistema
2. Dashboard (centro de control)
3. Módulo de Animales (gestión principal)
4. Módulo de Configuración (datos base)
5. Módulo de Reportes (análisis)
6. Otros módulos disponibles
7. Ajustes y ayuda
8. Conclusión y tips iniciales

### 3. **Interfaz de Usuario**
- Ventana con tooltip explicativo para cada paso
- Botones: **Anterior**, **Saltar**, **Siguiente/Finalizar**
- Indicador de progreso (ej: "Paso 3 de 8")
- Overlay oscuro que destaca el área enfocada

## Archivos Relacionados

### Archivo de Estado
- **`config/tour_state.json`**: Guarda si el usuario completó el tour
  - `primer_uso_completado`: true = tour ya se mostró
  - `tour_completado`: true = tour terminado
  - `modulos_tour_visitados`: lista de módulos visitados

### Código Principal
- **`modules/utils/tour_state_manager.py`**: Gestiona el estado persistente del tour
- **`modules/utils/global_tour.py`**: Define los pasos del tour global
- **`modules/utils/tour_manager.py`**: Motor del tour (mejorado con callbacks)
- **`main.py`**: Línea 185 - `verificar_primer_uso()` inicia el tour

## Cómo Funciona

### Arranque Inicial
```
main.py:157 -> after(1000, verificar_primer_uso)
                ↓
             GlobalTour(app)
                ↓
             should_start_tour() → es_primer_uso() == True
                ↓
             start_tour() → TourManager.start_tour()
                ↓
             Ejecuta 8 pasos con tooltips
                ↓
             Al finalizar: marcar_primer_uso_completado()
```

### En Arranques Posteriores
```
main.py:157 -> verificar_primer_uso()
                ↓
             GlobalTour.should_start_tour() == False
                ↓
             Tour no se ejecuta (sin mensajes)
```

### Reiniciar Tour (desde Ajustes)
```
Usuario click en "Reiniciar Tour"
                ↓
             TourStateManager.reset_tour()
                ↓
             Limpia config/tour_state.json
                ↓
             En próximo arranque: tour se muestra
```

## Personalización

### Agregar Nuevos Pasos
En `modules/utils/global_tour.py`, línea ~60:
```python
self.tour_manager.add_step(TourStep(
    title="Mi Módulo",
    text="Explicación del módulo...",
    widget=None,
    position="top",
    duration=0
))
```

### Cambiar Orden o Contenido
- Editar `modules/utils/global_tour.py` → `_setup_steps()`
- El contenido se actualiza automáticamente en el próximo arranque

### Desactivar Tour Completamente
```python
# En main.py, comentar línea 185:
# self.after(1000, self.verificar_primer_uso)
```

## Estados del Tour

| Estado | Descripción | Comportamiento |
|--------|-------------|-----------------|
| `primer_uso_completado: false` | Primer arranque | Tour se ejecuta automáticamente |
| `primer_uso_completado: true` | Usuario ya vio tour | Tour no se ejecuta |
| Usuario presiona Saltar | Tour interrumpido | `on_skip_callback()` ejecutado |
| Usuario presiona Finalizar | Tour completado | `on_complete_callback()` ejecutado |

## Archivos de Configuración

### `config/tour_state.json`
```json
{
  "app_version": "2.0.0",
  "primer_uso_completado": false,
  "tour_completado": false,
  "last_tour_module": "dashboard",
  "modulos_tour_visitados": []
}
```

## Resetear para Testing

```python
# En Python:
from modules.utils.tour_state_manager import TourStateManager
manager = TourStateManager()
manager.reset_tour()
```

El tour se mostrará en el próximo arranque.

## Notas Técnicas

- **Threading**: El tour se ejecuta en el hilo principal (no async)
- **Callbacks**: Soporta `on_complete_callback` y `on_skip_callback`
- **Encoding**: Usa UTF-8 para soportar caracteres especiales
- **Performance**: Sin impacto notable en arranque (se ejecuta en `after(1000)`)
