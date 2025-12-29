# 🌱 FASE 1: IMPLEMENTACIÓN COMPLETA DE SEED DE DATOS

## ✅ Entregables

Esta fase incluye implementación completa de carga de datos de prueba realistas para FincaFácil.

### 📦 Archivos Nuevos

1. **`src/database/seed_data.py`** (850+ líneas)
   - Módulo central con clase `SeedDataGenerator`
   - Métodos por módulo (animales, potreros, reproducción, leche, etc.)
   - Transacciones seguras
   - Logging detallado
   - Función pública `run_seed()`

2. **`src/modules/ajustes/ajustes_main.py`** (Actualizado)
   - Nueva sección "Herramientas de Desarrollo" (solo modo dev)
   - Botones: "Cargar Datos de Prueba" y "Limpiar + Recargar"
   - Validación de integridad de BD
   - Estadísticas en tiempo real

3. **`scripts/validate_seed.py`** (400+ líneas)
   - Script standalone de validación
   - Chequea FKs, registros huérfanos
   - Genera reporte completo
   - Ejecutable desde CLI o UI

4. **`docs/FASE1_SEED_DATOS_PRUEBA.md`** (Documentación completa)
   - Guía de uso (3 opciones)
   - Checklist post-seed (40+ items)
   - Troubleshooting
   - Scripts de validación SQL

---

## 🚀 Cómo Usar

### Opción 1: Desde la Interfaz Gráfica (Recomendado)

1. Abrir FincaFácil
2. Ir a **Ajustes → Herramientas de Desarrollo** (si está en modo dev)
3. Click **"🌱 Cargar Datos de Prueba"**
4. Confirmar operación
5. ✅ Datos cargados en segundos

### Opción 2: Desde Terminal

```bash
# Sin limpiar (agrega datos)
python -m database.seed_data

# Con limpieza (reemplaza todos los datos)
python -m database.seed_data --clear
```

### Opción 3: Desde Código Python

```python
from database.seed_data import run_seed

# Ejecutar
success = run_seed(clear_before_seed=False, mode="dev")

if success:
    print("✅ Datos cargados")
```

---

## 📊 Datos Generados (Resumen)

| Entidad | Cantidad | Descripción |
|---------|----------|-------------|
| **Fincas** | 3 | La Esperanza, San Miguel, Los Llanos |
| **Razas** | 8 | Holstein, Jersey, Simmental, Brahman, Angus, etc. |
| **Potreros** | 7 | Distribuidos entre fincas, capacidades realistas |
| **Lotes** | 4 | Agrupaciones por tipo (hembras, machos, etc.) |
| **Animales** | 40+ | Sexo, edad, peso, estado variados |
| **Servicios Reproductivos** | 12 | Servicios con 10 gestantes, 2 paridas |
| **Crías Nacidas** | 5 | Nacimientos simulados con datos genealógicos |
| **Registros de Leche** | ~900 | 15 hembras × 60 días (realista: 15-35L/día) |
| **Tratamientos** | 12-15 | Mastitis, cojera, neumonía, etc. |
| **Pesos** | ~125 | Histórico de 5 pesajes × 25 animales |
| **Insumos** | 6 | Alimentos, medicamentos, fertilizantes |
| **Movimientos Insumos** | 30 | Entradas/salidas último 90 días |
| **Herramientas** | 7 | Maquinaria, equipos médicos |

**Total: +1,300 registros** con FK válidas e integridad garantizada

---

## ✅ CHECKLIST DE VALIDACIÓN

Después de cargar datos, verificar:

### 🎯 Dashboard
- [ ] KPI Total Animales: ~40
- [ ] KPI Activos: ~30
- [ ] KPI Gestantes: ~10
- [ ] Gráfico Producción: Renderiza sin errores
- [ ] Gráficos Estado: Pie chart correcto

### 📋 Módulos
- [ ] **Animales**: Listado pagina, filtros funcionan
- [ ] **Reproducción**: Gestantes/Partos muestran datos
- [ ] **Salud**: Tratamientos visibles
- [ ] **Leche**: 900 registros, gráficos renderizan
- [ ] **Potreros**: 7 potreros, capacidad correcta
- [ ] **Insumos**: 6 insumos, movimientos visible
- [ ] **Herramientas**: 7 equipos, estados correctos

### 🔐 Integridad
- [ ] Sin FK violations
- [ ] Sin registros huérfanos
- [ ] Cascadas de eliminación funcionan
- [ ] Índices optimizados

### ⚡ Performance
- [ ] Dashboard: < 2 segundos
- [ ] Listados: Respuesta rápida (40+ registros)
- [ ] Gráficos: < 1 segundo
- [ ] Reportes PDF: < 3 segundos

---

## 🔍 Validar Datos

### Desde UI (Ajustes → Herramientas de Desarrollo)
```
🔍 Validar Integridad de BD
📊 Ver Estadísticas
```

### Desde Terminal
```bash
python scripts/validate_seed.py
```

Genera reporte completo con:
- Conteo de registros por tabla
- Validación de FKs
- Detección de registros huérfanos
- Estadísticas de producción y reproducción

---

## 🧪 Validación SQL Manual

```sql
-- Contar animales
SELECT COUNT(*) FROM animal;  -- Debe ser ~40

-- Hembras lecheras
SELECT COUNT(*) FROM animal 
WHERE sexo='Hembra' AND raza_id IN 
  (SELECT id FROM raza WHERE tipo_ganado='Lechero');

-- Gestantes activas
SELECT COUNT(*) FROM servicio WHERE estado='Gestante';  -- ~10

-- Producción total
SELECT SUM(litros_manana + litros_tarde + litros_noche) 
FROM produccion_leche;  -- Debe ser > 10,000L

-- Verificar FKs
SELECT COUNT(*) FROM animal 
WHERE id_finca NOT IN (SELECT id FROM finca);  -- Debe ser 0
```

---

## 🛠️ Troubleshooting

| Problema | Solución |
|----------|----------|
| No carga datos | Verificar modo dev, permisos BD |
| FK violations | Revisar order de inserción |
| Gráficos no cargan | Verificar matplotlib, datos de leche |
| Performance lenta | Validar índices, aumentar animales |
| Datos incompletos | Revisar logs: `logs/fincafacil.log` |

---

## 📈 Próximas Fases

**Fase 2:** Módulos Nómina y Ventas
**Fase 3:** Reportes avanzados
**Fase 4:** BI/Analytics
**Fase 5:** Optimización y limpieza

---

## 📝 Notas Técnicas

### Arquit ectura
- `SeedDataGenerator`: Clase central, inyectable
- Transacciones por bloque (seguridad)
- Cache de IDs para relaciones
- Logging detallado por módulo

### Características
- ✅ Datos coherentes (FKs válidas)
- ✅ Estados realistas (activo, vendido, muerto)
- ✅ Fechas cronológicamente válidas
- ✅ Pesos acordes a edad/raza
- ✅ Producción variable y realista
- ✅ Soft delete respetado
- ✅ Sin datos hardcodeados

### Modo Desarrollo
- Activable via `FINCAFACIL_DEV=1` env var
- O presencia de archivo `.dev`
- O siempre visible en fase 1 (ajustable)
- Deshabilitada en producción automáticamente

---

## 📞 Contacto

Para reportar bugs o sugerencias:
1. Revisar logs: `logs/fincafacil.log`
2. Ejecutar validación: `python scripts/validate_seed.py`
3. Incluir contexto completo en reporte

---

**Versión:** 1.0  
**Completado:** Diciembre 2025  
**Estado:** ✅ Implementación Completa
