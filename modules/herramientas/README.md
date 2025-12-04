# Módulo de Herramientas y Equipos

## Descripción
Sistema completo de gestión de herramientas, equipos y maquinaria agrícola con seguimiento de inventario, mantenimiento y asignación a trabajadores.

## Características Principales

### 1. Gestión de Catálogo
- **Registro completo**: Código único, nombre, categoría, marca, modelo, número de serie
- **Información financiera**: Fecha y valor de adquisición, vida útil estimada
- **Control de stock**: Sistema de unidades únicas (stock_total = 1)
- **Ubicación y estado**: Seguimiento de ubicación física y estado operativo
- **Asignación**: Vinculación con trabajadores y fincas específicas
- **Documentación**: Observaciones y fotografías de cada equipo

### 2. Estados de Herramientas
El sistema maneja los siguientes estados:

- **Operativa**: Herramienta en condiciones normales de uso
- **En Mantenimiento**: Herramienta siendo objeto de mantenimiento preventivo/correctivo
- **En Revisión**: Herramienta siendo inspeccionada (requiere migración 018)
- **Dañada**: Herramienta con fallas que requieren reparación
- **Fuera de Servicio**: Herramienta no apta para uso

### 3. Sistema de Mantenimiento (Migraciones 017 y 018)

#### Seguimiento de Estado de Mantenimientos
- **Estado Activo**: Mantenimientos en curso que aparecen en el historial
- **Estado Completado**: Mantenimientos finalizados (ocultos automáticamente del historial)
- **Preservación del estado previo**: El sistema guarda el estado original de la herramienta

#### Tipos de Mantenimiento
- **Preventivo**: Mantenimiento programado
- **Correctivo**: Reparación de fallas
- **Inspección**: Revisión de condiciones

#### Funcionalidades
- **Registro de mantenimiento**: Al registrar, la herramienta cambia automáticamente a "En Mantenimiento" o "En Revisión"
- **Cambio rápido de estado**: Combo box para actualizar el estado desde la pestaña de mantenimiento
- **Completar mantenimiento**: Restaura el estado previo de la herramienta y marca el mantenimiento como completado
- **Historial inteligente**: Solo muestra mantenimientos activos (los completados se ocultan)
- **Gestión completa**: Editar, eliminar registros, ver detalles completos

#### Información Registrada
- Tipo de mantenimiento
- Fecha de realización
- Descripción detallada
- Costo y proveedor del servicio
- Próximo mantenimiento programado
- Personal responsable
- Observaciones adicionales

### 4. Control de Asignación
- **En Bodega**: Herramienta disponible sin asignar
- **Asignada**: Herramienta asignada a un trabajador específico
- **Validación**: Sistema verifica tanto id_trabajador como texto del campo responsable

### 5. Importación desde Excel
El sistema permite importar herramientas masivamente desde archivos Excel con las siguientes características:

#### Estructura del Archivo
- **Columnas requeridas**: codigo, nombre, categoria
- **Columnas opcionales**: descripcion, marca, modelo, numero_serie, ubicacion, estado, fecha_adquisicion, valor_adquisicion, vida_util_anos, responsable, observaciones, finca

#### Características de Importación
- **Normalización de finca**: Coincidencia flexible (mayúsculas/minúsculas, tildes, espacios)
- **Mapeo de responsables**: Convierte nombres de empleados a id_trabajador automáticamente
- **Conversión de valores**: Parsing seguro de fechas y valores monetarios
- **Validación**: Verifica existencia de finca y empleado antes de importar
- **Manejo de errores**: Reporta filas con problemas sin detener la importación

#### Ejemplo de Fila Excel
```
codigo: MAQ-001
nombre: Tractor agrícola
categoria: Maquinaria
marca: John Deere
modelo: 5075E
finca: La esperanza
responsable: Juan Pérez García
valor_adquisicion: 50000000
```

### 6. Interfaz de Usuario

#### Pestaña Catálogo
- Tabla principal con todas las herramientas
- Filtros por categoría, estado, disponibilidad
- Botones: Agregar, Editar, Eliminar, Ver Detalles
- Importación masiva desde Excel
- Exportación a Excel

#### Pestaña Mantenimiento
- **Formulario con scroll**: Permite ver todos los campos sin problemas de espacio
- **Botones organizados**: Ubicados en la parte inferior para fácil acceso
  - Guardar Mantenimiento
  - Completar Mantenimiento
  - Ver Detalles
  - Eliminar Registro
  - Editar Herramienta
- **Combo de estado rápido**: Cambiar estado de la herramienta sin salir de la vista
- **Historial dinámico**: Solo muestra mantenimientos activos

## Estructura de Base de Datos

### Tabla `herramienta`
```sql
CREATE TABLE herramienta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    categoria TEXT,
    descripcion TEXT,
    marca TEXT,
    modelo TEXT,
    numero_serie TEXT,
    id_finca INTEGER,
    ubicacion TEXT,
    estado TEXT DEFAULT 'Operativa' 
        CHECK(estado IN ('Operativa', 'En Mantenimiento', 'En Revisión', 'Dañada', 'Fuera de Servicio')),
    fecha_adquisicion DATE,
    valor_adquisicion REAL,
    vida_util_anos INTEGER,
    responsable TEXT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    foto_path TEXT,
    id_trabajador INTEGER,
    stock_total INTEGER DEFAULT 1,
    stock_bodega INTEGER DEFAULT 1,
    FOREIGN KEY (id_finca) REFERENCES finca(id) ON DELETE SET NULL
);
```

### Tabla `mantenimiento_herramienta`
```sql
CREATE TABLE mantenimiento_herramienta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    herramienta_id INTEGER NOT NULL,
    tipo_mantenimiento TEXT,
    fecha_mantenimiento DATE NOT NULL,
    descripcion TEXT,
    costo REAL,
    proveedor_servicio TEXT,
    proximo_mantenimiento DATE,
    realizado_por TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP,
    estado_actual TEXT DEFAULT 'Activo' CHECK(estado_actual IN ('Activo', 'Completado')),
    estado_previo_herramienta TEXT,
    fecha_completado DATE,
    FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
);
```

## Migraciones

### Migración 017: Estado de Mantenimientos
Agrega campos para seguimiento de estado:
- `estado_actual`: 'Activo' o 'Completado'
- `estado_previo_herramienta`: Estado original de la herramienta
- `fecha_completado`: Fecha de finalización del mantenimiento

### Migración 018: Estado 'En Revisión'
Actualiza el CHECK constraint de la tabla `herramienta` para incluir el estado 'En Revisión'.

### Aplicar Migraciones
```bash
# Verificar estado de migraciones
verificar_migraciones.bat

# O manualmente con Python
python verificar_estado_migraciones.py
```

## Modo de Compatibilidad
El módulo funciona en dos modos:

### Con Migraciones Aplicadas (Modo Completo)
- Seguimiento completo de estado de mantenimientos
- Auto-ocultación de mantenimientos completados
- Restauración automática del estado de herramientas
- Estado 'En Revisión' disponible

### Sin Migraciones (Modo Degradado)
- Funcionalidad básica de registro de mantenimientos
- Todos los mantenimientos visibles en historial
- Estado manual de herramientas
- Estado 'En Revisión' genera advertencia al intentar usar

El sistema detecta automáticamente qué columnas existen en la base de datos usando `PRAGMA table_info` y adapta su comportamiento.

## Reglas de Negocio

### Stock
- **Una unidad por herramienta**: `stock_total` siempre es 1
- **Validación en UI**: Los campos de stock están deshabilitados y muestran valor 1
- **Importación**: Sistema ignora valores de stock diferentes a 1

### Eliminación
- **Catálogo**: Eliminar una herramienta elimina todos sus mantenimientos (CASCADE)
- **Mantenimiento**: Eliminar un registro de mantenimiento NO elimina la herramienta del catálogo

### Asignación
- **Por ID**: Cuando `id_trabajador` tiene valor, la herramienta está "Asignada"
- **Por texto**: Cuando `id_trabajador` es NULL pero `responsable` tiene texto diferente de "bodega", también se considera "Asignada"
- **Validación**: Al guardar se valida que el trabajador exista en la tabla `empleado`

## Archivos Principales

```
modules/herramientas/
├── herramientas_main.py       # Lógica principal del módulo
├── README.md                   # Esta documentación
└── __init__.py

scripts/migrations/
├── 017_add_estado_mantenimiento.py    # Migración para seguimiento de estado
└── 018_add_revision_estado.py         # Migración para estado 'En Revisión'

Raíz del proyecto:
├── verificar_migraciones.bat           # Script para verificar estado de migraciones
├── verificar_estado_migraciones.py    # Script de verificación Python
├── normalizar_y_migrar.py             # Script de normalización de estados
└── aplicar_migracion_017_direct.py    # Aplicación directa de migración 017
```

## Uso

### Registrar Nueva Herramienta
1. Ir a pestaña "Catálogo"
2. Click en "Agregar Herramienta"
3. Llenar formulario (código y nombre son obligatorios)
4. Opcionalmente asignar a finca y/o trabajador
5. Guardar

### Registrar Mantenimiento
1. Ir a pestaña "Mantenimiento"
2. Seleccionar herramienta del combo
3. Llenar datos del mantenimiento
4. Click en "Guardar Mantenimiento"
   - La herramienta cambiará automáticamente a "En Mantenimiento" o "En Revisión"

### Completar Mantenimiento
1. En pestaña "Mantenimiento", seleccionar registro del historial
2. Click en "Completar Mantenimiento"
   - El estado de la herramienta se restaura al estado previo
   - El registro desaparece del historial (queda marcado como Completado en BD)

### Cambiar Estado Rápido
1. En pestaña "Mantenimiento"
2. Seleccionar herramienta del combo superior
3. Cambiar el combo "Estado Herramienta"
   - El cambio se aplica inmediatamente

### Importar desde Excel
1. Preparar archivo Excel con las columnas requeridas
2. Click en "Importar desde Excel"
3. Seleccionar archivo
4. Revisar resumen de importación
5. Confirmar importación

## Notas Técnicas

### Detección de Migraciones
```python
cur.execute('PRAGMA table_info(mantenimiento_herramienta)')
columnas = [col[1] for col in cur.fetchall()]
tiene_estado_actual = 'estado_actual' in columnas
```

### Normalización de Finca
```python
def _normalize_text(text):
    if not text:
        return ""
    text = text.lower().strip()
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text
```

### Validación de Responsable
```python
responsable_txt = row.get('responsable', '').strip()
asignada_por_texto = bool(responsable_txt and responsable_txt.lower() != "bodega")
disponibilidad = "Asignada" if (id_trabajador or asignada_por_texto) else "En Bodega"
```

## Solución de Problemas

### "No such table: trabajador"
- **Causa**: Tabla incorrecta
- **Solución**: La tabla correcta es `empleado`, usar `id_trabajador` que referencia `empleado(rowid)`

### "Estado 'En Revisión' no permitido"
- **Causa**: Migración 018 no aplicada
- **Solución**: Ejecutar `python normalizar_y_migrar.py`

### Herramientas con responsable aparecen "En Bodega"
- **Causa**: `id_trabajador` es NULL y solo hay texto en `responsable`
- **Solución**: Ejecutar script de backfill o corregir lógica de asignación

### Mantenimientos completados aparecen en historial
- **Causa**: Migración 017 no aplicada
- **Solución**: Ejecutar `python aplicar_migracion_017_direct.py`

### Error "CHECK constraint failed: estado..."
- **Causa**: Datos con estados no permitidos (ej: 'activo' en minúsculas)
- **Solución**: Ejecutar `python normalizar_y_migrar.py` para normalizar estados

## Historial de Cambios

### Versión 2.0 (Actual)
- ✅ Sistema de seguimiento de estado de mantenimientos
- ✅ Auto-ocultación de mantenimientos completados
- ✅ Restauración automática del estado de herramientas
- ✅ Estado 'En Revisión' agregado
- ✅ Interfaz con scroll en formulario de mantenimiento
- ✅ Botones organizados en la parte inferior
- ✅ Cambio rápido de estado desde pestaña mantenimiento
- ✅ Corrección de eliminación (solo registro, no herramienta)
- ✅ Modo de compatibilidad para bases de datos sin migraciones

### Versión 1.0
- Gestión básica de catálogo
- Registro simple de mantenimientos
- Importación desde Excel
- Control de stock unitario
