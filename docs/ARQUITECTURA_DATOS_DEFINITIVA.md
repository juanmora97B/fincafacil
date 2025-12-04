# Arquitectura de Datos Definitiva - FincaFacil

## 📋 Principios de Diseño

### Reglas de Asociación con Finca

1. **Datos Vinculados a Finca Específica** (tienen `id_finca` o `finca_id`):
   - **Infraestructura**: Potreros, Lotes, Sectores
   - **Recursos**: Animales, Herramientas, Insumos
   - **Personal**: Empleados, Nómina (a través de empleado)

2. **Datos Globales** (sin FK a finca, reutilizables):
   - **Catálogos de Animales**: Razas, Calidad Animal, Condiciones Corporales, Tipos de Explotación
   - **Catálogos Comerciales**: Motivos de Venta, Destinos de Venta
   - **Origen/Procedencia**: Considerados globales (ver decisión abajo)

---

## 🏗️ Estructura de Tablas

### ✅ Tablas con Relación a Finca (FK obligatoria)

| Tabla | FK Columna | Propósito | Estado |
|-------|-----------|-----------|--------|
| `animal` | `id_finca` | Animales registrados en cada finca | ✅ OK |
| `potrero` | `id_finca` | Potreros específicos de cada finca | ✅ OK |
| `lote` | `finca_id` | Lotes de animales por finca | ✅ OK |
| `sector` | `finca_id` | Sectores geográficos de cada finca | ✅ OK |
| `empleado` | `id_finca` | Personal asignado a cada finca | ✅ CORREGIDO (migración 013) |
| `insumo` | `id_finca` | Inventario de insumos por finca | ✅ OK |
| `herramienta` | `id_finca` | Herramientas y equipos por finca | ✅ OK |

### 🌍 Tablas Globales (sin FK a finca)

| Tabla | Registros | Propósito | Estado |
|-------|-----------|-----------|--------|
| `raza` | 28 | Catálogo de razas ganaderas | ✅ OK |
| `motivo_venta` | 15 | Razones de venta de animales | ✅ OK |
| `destino_venta` | 10 | Destinos/compradores | ✅ OK |
| `condicion_corporal` | 5 | Escala de condición corporal | ✅ OK |
| `calidad_animal` | 12 | Clasificación de calidad | ✅ OK |
| `tipo_explotacion` | 15 | Tipos de explotación ganadera | ✅ OK |

---

## 🔍 Decisiones sobre Tablas Especiales

### 📦 Origen, Procedencia y Vendedor

**Decisión Final**: **GLOBALES** (aunque tienen columna `id_finca`, se mantienen con valor NULL para uso universal)

**Justificación**:
- **Procedencias** son lugares de origen generales (feria, otra finca, importación) reutilizables
- **Vendedores** pueden operar en múltiples fincas
- **Origen consolidado** unifica ambos conceptos

**Estado Actual**:
- `origen`: Tiene `id_finca` pero todos los registros son NULL (10 registros globales) ✅ OK
- `procedencia`: Tiene `id_finca` pero todos son NULL (10 registros globales) ✅ OK  
- `vendedor`: Tiene `id_finca` sin registros ✅ OK

**Recomendación**: Permitir opcionalmente asignar `id_finca` si un origen/vendedor es específico de una finca, pero por defecto usar NULL para disponibilidad global.

---

## 📊 Relaciones Indirectas

### Nómina y Empleados

- **`empleado`** → tiene `id_finca` (relación directa)
- **`pago_nomina`** → referencia `codigo_empleado` (relación indirecta con finca a través de empleado)

**Filtrado**: Al mostrar nómina, filtrar por empleados de la finca seleccionada.

### Transacciones de Animales

Las siguientes tablas dependen de `animal`, que tiene `id_finca`:
- `peso`, `tratamiento`, `servicio`, `reproduccion`, `venta`, `muerte`
- Estas heredan la finca del animal asociado

---

## 🎯 Comportamiento por Módulo

### Módulo: Registro de Animales
**Finca seleccionada**: "Finca El Prado"
- ✅ Mostrar: Potreros de El Prado (10)
- ✅ Mostrar: Lotes de El Prado (11)
- ✅ Mostrar: Sectores de El Prado (5)
- ✅ Mostrar: Padres/Madres activos en El Prado
- 🌍 Mostrar: Todas las razas (28) - global
- 🌍 Mostrar: Todos los orígenes/procedencias (10) - global

**Finca seleccionada**: "Finca El León"
- ✅ Mostrar: Potreros de El León (15)
- ✅ Mostrar: Lotes de El León (11)
- ✅ Mostrar: Sectores de El León (5)
- ✅ Mostrar: Padres/Madres activos en El León
- 🌍 Mostrar: Todas las razas (28) - global
- 🌍 Mostrar: Todos los orígenes/procedencias (10) - global

### Módulo: Nómina
**Finca seleccionada**: "Finca El Prado"
- ✅ Mostrar: Solo empleados con `id_finca = 20`
- ✅ Mostrar: Pagos de nómina de empleados de El Prado

**Finca seleccionada**: "Finca El León"
- ✅ Mostrar: Solo empleados con `id_finca = 22`
- ✅ Mostrar: Pagos de nómina de empleados de El León

### Módulo: Inventario Insumos
**Finca seleccionada**: "Finca El Prado"
- ✅ Mostrar: Solo insumos con `id_finca = 20`
- ✅ Movimientos: Solo movimientos de insumos de El Prado

### Módulo: Ventas
**Finca seleccionada**: "Finca El Prado"
- ✅ Mostrar: Solo animales vendidos de El Prado
- 🌍 Destinos de venta: Todos (global)
- 🌍 Motivos de venta: Todos (global)

---

## ✅ Validaciones Implementadas

### Migración 013: Empleado con Finca
```sql
ALTER TABLE empleado ADD COLUMN id_finca INTEGER DEFAULT [finca_activa]
CREATE INDEX idx_empleado_finca ON empleado(id_finca)
```
- ✅ Todos los empleados existentes asignados a finca por defecto
- ✅ Índice creado para consultas eficientes

### Verificaciones Pendientes en Código
1. **Validar FK en empleado**: Al crear/editar empleado, verificar que `id_finca` existe
2. **Filtrado automático**: Asegurar que módulos de nómina filtren por finca
3. **Interfaz de empleados**: Agregar combo de selección de finca al crear empleado

---

## 📈 Resumen de Conformidad

### ✅ Cumple Totalmente (7/7)
- ✓ Potreros tienen `id_finca`
- ✓ Lotes tienen `finca_id`
- ✓ Sectores tienen `finca_id`
- ✓ Animales tienen `id_finca`
- ✓ Empleados tienen `id_finca` (CORREGIDO)
- ✓ Insumos tienen `id_finca`
- ✓ Herramientas tienen `id_finca`

### ✅ Datos Globales Correctos (6/6)
- ✓ Razas sin FK (global)
- ✓ Motivos de venta sin FK (global)
- ✓ Destinos de venta sin FK (global)
- ✓ Condiciones corporales sin FK (global)
- ✓ Calidad animal sin FK (global)
- ✓ Tipos de explotación sin FK (global)

### ✅ Casos Especiales Resueltos
- ✓ Origen/Procedencia/Vendedor: Globales con opción de finca específica (NULL por defecto)
- ✓ Nómina: Relación indirecta con finca vía empleado

---

## 🚀 Próximos Pasos

### 1. Actualizar Interfaz de Empleados
- [ ] Agregar campo "Finca" al formulario de registro de empleado
- [ ] Validar selección de finca al guardar
- [ ] Mostrar finca actual en listado de empleados

### 2. Filtrar Módulo de Nómina
- [ ] Agregar combo de finca en módulo de nómina
- [ ] Filtrar empleados por `id_finca`
- [ ] Filtrar pagos por empleados de la finca seleccionada

### 3. Documentación de Usuario
- [ ] Actualizar manual de usuario con explicación de fincas
- [ ] Agregar sección sobre separación de datos por finca
- [ ] Explicar qué datos son globales vs específicos

---

**Fecha**: 2025-11-24  
**Versión**: 1.0  
**Estado**: ✅ Arquitectura validada y corregida
