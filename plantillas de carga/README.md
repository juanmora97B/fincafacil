Carpeta de plantillas de carga

Aquí puedes guardar/descargar las plantillas Excel para los diferentes módulos de configuración.

Desde Ajustes > Plantillas de carga puedes generar la planilla del módulo que necesites (por ejemplo: Razas, Potreros, Calidad animal) y guardarla aquí o en cualquier otra carpeta.

## 🆕 Campos Nuevos en Plantilla de Animales

La plantilla `plantilla_animales.xlsx` ha sido actualizada con los siguientes campos:

### Nuevos Campos Obligatorios/Recomendados:
- **Lote**: Nombre del lote al que pertenece el animal (opcional)
- **Sector**: Nombre del sector dentro de la finca (opcional)
- **Grupo**: Clasificación del animal - opciones: `Toros`, `Vacas`, `Terneros`, `Novillos`
- **Condición Corporal**: Código de condición corporal (ej: BCS1, BCS2, etc.) - debe existir en catálogo

### Campos Existentes Actualizados:
- **Vendedor**: Nombre del vendedor (para compras)
- **Procedencia**: Lugar de procedencia del animal (para compras)

### Estructura Completa de la Plantilla:
```
Código, Nombre, Tipo Ingreso, Sexo, Fecha Nacimiento, Fecha Compra,
Finca, Raza, Potrero, Lote, Sector, Grupo, Peso Nacimiento, Peso Compra,
Precio Compra, Vendedor, Procedencia, Salud, Estado, Inventariado,
Color, Hierro, Condición Corporal, Comentario
```

### Notas Importantes:
- **Grupo** es especialmente importante para clasificación y reportes
- **Condición Corporal** debe coincidir con un código existente en el catálogo (tabla `condicion_corporal`)
- Si no especifica Lote/Sector, el animal se asignará sin estos filtros adicionales

## Formatos soportados - Condición Corporal

El importador ahora acepta DOS formatos de plantilla para `condicion_corporal`:

### Formato Nuevo (recomendado)
Columnas mínimas:
```
codigo, descripcion
```
Columnas opcionales:
```
puntuacion, escala, especie, caracteristicas, recomendaciones, estado
```

Ejemplo:
```
codigo | descripcion                   | puntuacion | caracteristicas                | recomendaciones
CC1    | Muy flaca / crítico           | 1          | costillas muy visibles         | aumentar energia
CC2    | Delgada                       | 2          | costillas visibles parcial     | mejorar balance
```

### Formato Antiguo (compatibilidad)
Columnas aceptadas (cualquiera de ellas activa compatibilidad):
```
condicion_corporal, rango_inferior, rango_superior, descripcion, recomendacion, comentario
```

Reglas de conversión:
- condicion_corporal -> codigo
- descripcion -> descripcion
- recomendacion -> recomendaciones
- comentario -> caracteristicas
- Si no hay puntuacion se genera correlativa iniciando en 1
- estado por defecto = 'Activo'

Ejemplo antiguo:
```
condicion_corporal | rango_inferior | rango_superior | descripcion        | recomendacion            | comentario
CC1                | 1.0            | 2.0            | Muy flaca / crítico| aumentar energia urgente | costillas marcadas
CC2                | 2.1            | 3.0            | Delgada            | ajustar dieta            | moderada cobertura
```

### Notas
- Filas vacías se ignoran automáticamente.

---

## 🔧 Plantilla de Herramientas

**Archivo:** `plantilla_herramientas.xlsx`

### Columnas Obligatorias (*)
- `codigo`: Código único de la herramienta (ej: HER-001)
- `nombre`: Nombre descriptivo de la herramienta
- `categoria`: Debe ser una de las siguientes:
  - Maquinaria
  - Herramienta Manual
  - Equipo Medico
  - Vehiculo
  - Equipo Oficina
  - Otro

### Columnas Opcionales
- `finca`: Nombre exacto de la finca (debe existir en el sistema)
- `marca`: Marca del equipo o herramienta
- `modelo`: Modelo específico
- `numero_serie`: Número de serie del fabricante
- `estado`: Operativa / En Mantenimiento / Dañada / Fuera de Servicio
- `ubicacion`: Ubicación física (ej: Bodega Principal, Potrero 1, etc.)
- `responsable`: Nombre del trabajador asignado o "Bodega"
- `fecha_adquisicion`: Formato AAAA-MM-DD (ej: 2023-01-15)
- `valor_adquisicion`: Valor numérico sin símbolos (ej: 45000.00)
- `vida_util_anos`: Años de vida útil estimada (número entero)
- `descripcion`: Descripción detallada de la herramienta
- `observaciones`: Notas adicionales

### Ejemplo de Datos
```
codigo   | nombre                      | categoria           | finca           | estado     | ubicacion       | responsable
HER-001  | Tractor John Deere 5075E   | Maquinaria          | Finca El Prado  | Operativa  | Bodega Principal| Bodega
HER-002  | Motosierra Husqvarna 450e  | Herramienta Manual  | Finca El León   | Operativa  | Bodega Herram.  | Bodega
```

### Notas Importantes
1. Los códigos deben ser únicos (no duplicados)
2. Las fincas deben existir previamente en el sistema
3. El estado por defecto es "Operativa" si no se especifica
4. Si no asigna responsable, quedará como "Bodega"
5. Las fechas deben usar formato: AAAA-MM-DD
6. Los trabajadores deben estar registrados como activos en el módulo de Nómina
7. Para más detalles, consulte la hoja "Instrucciones" dentro del archivo Excel
- Los valores vacíos se normalizan a `NULL` (None interno).
- Se permite `recomendacion` o `recomendaciones` indistintamente.
- Si alguna fila carece de `codigo` o `descripcion` se descarta con aviso.

### Errores Comunes
- "Registro sin codigo/descripcion" → Fila incompleta.
- "El archivo no contiene registros válidos" → Todas las filas estaban vacías.

### Buenas Prácticas
1. Mantener solo las columnas necesarias para menor riesgo de errores.
2. Evitar mezclar encabezados de ambos formatos en la misma hoja.
3. Usar UTF-8 y evitar caracteres especiales no estándar.

