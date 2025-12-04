# Resumen de Cambios - Arquitectura de Datos por Finca

## ✅ Cambios Completados

### 1. Estructura de Base de Datos

#### ✅ Migración 013: Agregar id_finca a empleado
```sql
ALTER TABLE empleado ADD COLUMN id_finca INTEGER
CREATE INDEX idx_empleado_finca ON empleado(id_finca)
```
- **Estado**: ✅ Aplicada correctamente
- **Registros actualizados**: 2 empleados asignados a finca por defecto (id=20)

### 2. Verificación de Arquitectura

**Tablas con relación a finca** (✅ Todas correctas):
- `animal` → `id_finca`
- `potrero` → `id_finca`
- `lote` → `finca_id`
- `sector` → `finca_id`
- `empleado` → `id_finca` (✅ agregado)
- `insumo` → `id_finca`
- `herramienta` → `id_finca`

**Tablas globales** (✅ Todas correctas):
- `raza` (28 registros)
- `motivo_venta` (15 registros)
- `destino_venta` (10 registros)
- `condicion_corporal` (5 registros)
- `calidad_animal` (12 registros)
- `tipo_explotacion` (15 registros)

**Tablas especiales** (✅ Decisión tomada):
- `origen`, `procedencia`, `vendedor`: Globales con opción de finca específica (NULL por defecto)

---

## 🔄 Cambios Pendientes en UI

### Módulo: Nómina (`modules/nomina/nomina_main.py`)

#### Cambios Necesarios:

1. **Agregar filtro de finca en la interfaz**
   - Ubicación: `crear_tab_empleados()` - sección de filtros (línea ~75)
   - Agregar combo "Finca:" después del combo "Cargo:"
   
2. **Modificar consulta SQL de empleados**
   - Ubicación: `cargar_empleados()` (línea ~420)
   - Agregar `WHERE id_finca = ?` o permitir selección "Todas las fincas"
   
3. **Actualizar `cargar_empleados_combo()`**
   - Ubicación: línea ~512
   - Filtrar empleados por finca si está seleccionada

#### Código Sugerido:

```python
# En crear_tab_empleados(), después del combo_filtro_cargo_nomina:
ctk.CTkLabel(filtros_frame, text="Finca:").pack(side="left", padx=(4,2))
self.filtro_finca_nomina_var = ctk.StringVar(value="Todas")
self.combo_filtro_finca_nomina = ctk.CTkOptionMenu(
    filtros_frame,
    variable=self.filtro_finca_nomina_var,
    values=["Todas"],  # Se cargará dinámicamente
    width=200,
    command=lambda _: self.cargar_empleados()
)
self.combo_filtro_finca_nomina.pack(side="left", padx=(0,10))
self._cargar_opciones_finca_nomina()

# Nueva función para cargar fincas:
def _cargar_opciones_finca_nomina(self):
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre FROM finca WHERE estado NOT IN ('Inactivo', 'Eliminado') ORDER BY nombre")
            fincas = cur.fetchall()
        valores = ["Todas"] + [f"{f[0]}-{f[1]}" for f in fincas]
        if hasattr(self, 'combo_filtro_finca_nomina'):
            self.combo_filtro_finca_nomina.configure(values=valores)
    except Exception as e:
        self.logger.error(f"Error cargando fincas: {e}")

# Modificar cargar_empleados() - línea ~420:
def cargar_empleados(self):
    """Carga los empleados en la tabla"""
    for item in self.tabla_empleados.get_children():
        self.tabla_empleados.delete(item)

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Filtro de finca
            finca_val = self.filtro_finca_nomina_var.get() if hasattr(self, 'filtro_finca_nomina_var') else "Todas"
            
            sql = """
                SELECT rowid, codigo, nombres || ' ' || apellidos as nombre, 
                       cargo, salario_diario, 
                       COALESCE(bono_alimenticio, 0) + COALESCE(bono_productividad, 0) as total_bonos,
                       COALESCE(seguro_social, 0) + COALESCE(otras_deducciones, 0) as total_deducciones,
                       CASE WHEN estado_actual IS NULL THEN 'Activo' ELSE estado_actual END AS estado_actual,
                       id_finca
                FROM empleado
            """
            
            params = []
            if finca_val != "Todas":
                # Extraer ID de "20-finca el prado"
                finca_id = int(finca_val.split('-')[0])
                sql += " WHERE id_finca = ?"
                params.append(finca_id)
            
            cursor.execute(sql, params)
            # ... resto del código de filtrado
```

---

### Módulo: Empleados (Formulario crear/editar)

#### Ubicación Probable:
- `modules/configuracion/empleados.py` o similar (verificar si existe)
- Alternativamente: dentro de `nomina_main.py` si tiene formulario integrado

#### Cambios Necesarios:

1. **Agregar campo "Finca" al formulario**
   - Combo para seleccionar finca al crear empleado
   - Mostrar finca actual al editar
   
2. **Validar finca al guardar**
   - Asegurar que `id_finca` no sea NULL
   - Usar finca por defecto si no se selecciona

3. **Actualizar tabla de visualización**
   - Agregar columna "Finca" en `tabla_empleados`
   - Mostrar nombre de finca junto a datos del empleado

---

## 📋 Módulos Ya Correctos (No requieren cambios)

### ✅ Registro de Animales (`modules/animales/registro_animal.py`)
- Ya filtra potreros, lotes, sectores por finca
- Ya filtra padres/madres por finca
- Razas se mantienen globales (correcto)
- **Estado**: ✅ Funcionando correctamente

### ✅ Inventario de Insumos
- Ya tiene filtro por finca implementado
- **Estado**: ✅ Verificado anteriormente

### ✅ Configuración - Potreros/Lotes/Sectores
- Ya requieren selección de finca al crear
- Ya se filtran por finca en visualización
- **Estado**: ✅ Funcionando correctamente

---

## 🎯 Plan de Implementación Recomendado

### Fase 1: Nómina (Prioridad Alta)
1. [ ] Agregar combo de finca en filtros de empleados
2. [ ] Modificar consulta SQL para filtrar por finca
3. [ ] Actualizar combo de empleados en cálculo de nómina
4. [ ] Probar filtrado con ambas fincas (El Prado y El León)

### Fase 2: Formulario de Empleados (Prioridad Media)
1. [ ] Verificar si existe módulo separado de empleados
2. [ ] Agregar campo finca en formulario de creación
3. [ ] Agregar columna finca en tabla de visualización
4. [ ] Agregar validación de finca obligatoria

### Fase 3: Documentación (Prioridad Media)
1. [ ] Actualizar manual de usuario
2. [ ] Documentar separación por finca
3. [ ] Agregar ejemplos de uso

### Fase 4: Pruebas (Prioridad Alta)
1. [ ] Crear empleados en diferentes fincas
2. [ ] Verificar que filtro muestra solo empleados de finca seleccionada
3. [ ] Verificar cálculo de nómina por finca
4. [ ] Probar con datos reales de ambas fincas

---

## 📊 Estado Actual del Sistema

### Datos de Prueba:
- **Fincas activas**: 2
  - Finca El Prado (id=20): 10 potreros, 11 lotes, 5 sectores
  - Finca El León (id=22): 15 potreros, 11 lotes, 5 sectores
  
- **Empleados actuales**: 2
  - Ambos asignados a Finca El Prado (id=20) por defecto
  
- **Razas globales**: 28
- **Orígenes/Procedencias**: 10 (globales)

### Próximo Paso Inmediato:
**Implementar filtro de finca en módulo de nómina** para permitir gestionar empleados por finca.

---

**Fecha**: 2025-11-24  
**Estado**: 🔄 En progreso  
**Prioridad**: Alta (funcionalidad crítica para cliente)
