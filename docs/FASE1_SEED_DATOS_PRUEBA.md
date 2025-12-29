# 🌱 FASE 1: CARGA DE DATOS DE PRUEBA - FINCAFÁCIL

## 📋 Objetivo

Implementar una carga completa de **datos de prueba realistas** que permita validar flujos completos del sistema, probar rendimiento, verificar KPIs y detectar errores antes de producción.

## 📦 Alcance

Se generan datos para **11 módulos principales**:

- ✅ **Animales** (40 cabezas) - Diferentes sexos, edades, estados, razas
- ✅ **Potreros** (7 potreros) - Con capacidades, tipos de pasto
- ✅ **Salud** (Tratamientos, diagnósticos)
- ✅ **Reproducción** (Servicios, gestaciones, partos)
- ✅ **Producción de Leche** (Registros diarios últimos 60 días)
- ✅ **Insumos** (Alimentos, medicamentos, fertilizantes)
- ✅ **Movimientos de Insumos** (Entradas y salidas)
- ✅ **Herramientas** (Maquinaria, equipos médicos)
- ✅ **Pesos** (Histórico de pesajes)
- ✅ **Nómina** (En desarrollo)
- ✅ **Ventas** (En desarrollo)

## 🚀 Cómo Usar

### Opción 1: Desde la aplicación (interfaz gráfica)

En modo **desarrollo**, debe haber un botón "Cargar Datos de Prueba" en:
- **Menú: Ajustes → Herramientas de Desarrollo**
- **Botón: "🌱 Cargar Datos de Prueba"**
- Confirmar antes de ejecutar
- Opción para limpiar datos previos

### Opción 2: Ejecución manual desde terminal

```bash
# Cargar datos SIN limpiar previos
python -m database.seed_data

# Cargar datos LIMPIANDO previos
python -m database.seed_data --clear
```

### Opción 3: Desde código Python

```python
from database.seed_data import run_seed

# Sin limpiar
success = run_seed(clear_before_seed=False, mode="dev")

# Con limpieza
success = run_seed(clear_before_seed=True, mode="dev")

if success:
    print("✅ Datos cargados exitosamente")
else:
    print("❌ Error cargando datos")
```

## 📊 Datos Generados

### Fincas (3)
- **La Esperanza** (150.5 ha) - Valle del Cauca
- **San Miguel** (200 ha) - Antioquia
- **Los Llanos** (350 ha) - Córdoba

### Razas (8)
- Holstein, Jersey, Guernsey (Lecheras)
- Simmental (Doble Propósito)
- Brahman, Angus, Hereford, Cebú (Carne)

### Potreros (7)
- Distribuidos entre las 3 fincas
- Tipos de pasto: Brahaquiareo, Kikuyo
- Capacidades: 80 a 250 animales

### Animales (40+)
- **Distribución:**
  - ~60% Hembras, ~40% Machos
  - Edades: 0 a 3 años
  - Estados: Activo (30), Vendido (6), Muerto (4)
  
- **Características realistas:**
  - Pesos acordes a edad/raza
  - Colores variados
  - Asignados a potreros y lotes

### Reproducción (12 servicios)
- Servicios hace 60-90 días
- Estados: Gestante (10), Parida (2)
- Tipos: Monta Natural, Inseminación Artificial
- Partos registrados: ~5 con crías nacidas

### Salud
- **Tratamientos:** ~12-15 registros
- **Enfermedades:** Mastitis, Cojera, Neumonía, Diarrea, Fiebre Vitular
- **Veterinarios:** 3 ficticios
- Estados: Activos y completados

### Producción de Leche
- **Período:** Últimos 60 días
- **Animales:** 15 hembras lecheras
- **Volumen:** 15-35 L/día por animal (realista)
- **Registros:** ~900 total (15 animales × 60 días)

### Pesos
- **Histórico:** 5 pesajes por animal en 90 días
- **Variación:** ±50kg de la línea base

### Insumos (6)
- Alimento concentrado (500 kg)
- Hay de alfalfa (200 fardos)
- Vacunas (100 dosis)
- Medicamentos (50 ml)
- Fertilizantes y semillas

### Movimientos de Insumos (30)
- Entradas y salidas últimos 90 días
- Variación de costos realista

### Herramientas (7)
- Ordeñadora automática, Tractor, Motobomba
- Equipos médicos: Bascula, Estetoscopio, Botiquín
- Estados: Mayormente operativas, algunas en mantenimiento

## ✅ CHECKLIST DE VALIDACIÓN POST-SEED

Después de ejecutar el seed, **verificar los siguientes KPIs y funcionalidades**:

### 1. Dashboard
- [ ] **KPI Total de Animales:** Debe mostrar ~40 animales
- [ ] **KPI Activos:** ~30 animales
- [ ] **KPI Vendidos:** ~6 animales
- [ ] **KPI Muertos:** ~4 animales
- [ ] **KPI Gestantes:** ~10 hembras
- [ ] **KPI Producción de Hoy:** Debe mostrar litros (suma del día actual)
- [ ] **KPI Nacimientos mes:** Debe mostrar ~5
- [ ] **Gráfico Producción de Leche:** Debe renderizar sin errores
- [ ] **Gráfico Estados de Animales:** Pie chart con distribución
- [ ] **Panel de Alertas:** Debe mostrar eventos sanitarios próximos

### 2. Módulo Animales
- [ ] **Listado:** Mostrar 40 animales paginados correctamente
- [ ] **Filtros:** Filtrar por:
  - [ ] Estado (Activo, Vendido, Muerto)
  - [ ] Sexo (Hembra, Macho)
  - [ ] Raza
  - [ ] Finca
  - [ ] Potrero
- [ ] **Búsqueda:** Buscar por código y nombre
- [ ] **Detalles Animal:** Abrir ficha completa
  - [ ] Datos básicos
  - [ ] Foto (si aplica)
  - [ ] Historial de pesos
  - [ ] Comentarios
  - [ ] Genealogía (padres/crías)
  
### 3. Módulo Reproducción
- [ ] **Badge Gestantes:** Mostrar ~10
- [ ] **Badge Próximos Partos (7d):** Mostrar 2-3
- [ ] **Listado de Servicios:** Mostrar 12 servicios
- [ ] **Estados correctos:** Gestante, Parida, Vacía
- [ ] **Fechas estimadas:** Coincidir con servicios
- [ ] **Tab Gestantes:** Mostrar ~10 hembras
- [ ] **Tab Próximos Partos:** Mostrar hembras a parir en próximos 7 días
- [ ] **Registro de Parto:** Poder registrar nuevo parto manualmente

### 4. Módulo Salud
- [ ] **Tratamientos activos:** Mostrar ~7
- [ ] **Tratamientos completados:** Mostrar ~8
- [ ] **Ficha de animal enfermo:** Mostrar tratamientos asociados
- [ ] **Diagnósticos:** Mostrar enfermedades registradas
- [ ] **Búsqueda por enfermedad:** Funcionar correctamente

### 5. Módulo Producción de Leche
- [ ] **Registros últimos 60 días:** Mostrar ~900 registros
- [ ] **Gráfico de tendencias:** Renderizar sin errores
- [ ] **Total producción:** Calcular correctamente (suma de litros)
- [ ] **Promedio por animal:** Mostrar ~20-25 L/día
- [ ] **Filtro por animal:** Funcionar correctamente
- [ ] **Exportar a PDF:** Generar reportes sin errores

### 6. Módulo Potreros
- [ ] **Listado:** Mostrar 7 potreros
- [ ] **Capacidad:** Mostrar animales asignados vs capacidad
- [ ] **Estado de pastos:** Mostrar tipo de pasto
- [ ] **Búsqueda:** Funcionar por nombre
- [ ] **Asignación de animales:** Mostrar correctamente

### 7. Módulo Insumos
- [ ] **Inventario:** Mostrar 6 insumos
- [ ] **Stock actual:** Mostrar cantidades correctas
- [ ] **Alertas de stock:** Resaltar insumos bajo mínimo
- [ ] **Movimientos:** Mostrar 30 movimientos
- [ ] **Historial:** Tabla de entradas/salidas
- [ ] **Costo total:** Calcularse correctamente

### 8. Módulo Herramientas
- [ ] **Listado:** Mostrar 7 equipos
- [ ] **Estados:** Mostrar operativas, en mantenimiento
- [ ] **Valor de adquisición:** Mostrar correctamente
- [ ] **Deprecación:** Calcular según vida útil
- [ ] **Mantenimientos:** Poder registrar nuevo mantenimiento

### 9. Reportes
- [ ] **Reporte de Animales:** Exportar PDF con 40 animales
- [ ] **Reporte de Producción:** Mostrar 60 días de datos
- [ ] **Reporte de Salud:** Listar tratamientos activos
- [ ] **Reporte de Reproducción:** Mostrar gestantes y partos próximos
- [ ] **Gráficos:** Todos deben renderizar sin errores

### 10. Búsqueda y Filtros (Global)
- [ ] **Búsqueda rápida:** Encontrar animales por código
- [ ] **Filtros avanzados:** Combinar múltiples criterios
- [ ] **Paginación:** Navegar correctamente con 40+ animales
- [ ] **Ordenamiento:** Sortear por columnas

### 11. Integridad de Base de Datos
- [ ] **Sin registros huérfanos:**
  ```sql
  -- Verificar que no hay FKs rotas
  SELECT COUNT(*) FROM animal WHERE id_finca NOT IN (SELECT id FROM finca);
  -- Debe retornar 0
  ```
- [ ] **Cascada de eliminaciones:** Soft delete funciona
- [ ] **Índices:** Consultas se ejecutan rápido
- [ ] **Transacciones:** No hay datos parciales

### 12. Performance
- [ ] **Dashboard:** Carga en < 2 segundos
- [ ] **Listados:** Respuesta rápida con 40+ registros
- [ ] **Gráficos:** Renderización < 1 segundo
- [ ] **Reportes:** Generación PDF < 3 segundos
- [ ] **Búsquedas:** Resultados < 500ms

## 🔄 Scripts de Validación

### Script 1: Verificar Integridad de FKs

```python
# scripts/validate_seed.py
from database import get_db_connection

def validate_fks():
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        tables_to_check = [
            ("animal", "id_finca", "finca", "id"),
            ("animal", "raza_id", "raza", "id"),
            ("animal", "id_potrero", "potrero", "id"),
            ("servicio", "id_hembra", "animal", "id"),
            ("servicio", "id_macho", "animal", "id"),
        ]
        
        errors = []
        for table, fk_col, ref_table, ref_col in tables_to_check:
            cur.execute(f"""
                SELECT COUNT(*) FROM {table}
                WHERE {fk_col} IS NOT NULL 
                AND {fk_col} NOT IN (SELECT {ref_col} FROM {ref_table})
            """)
            count = cur.fetchone()[0]
            if count > 0:
                errors.append(f"{table}.{fk_col}: {count} registros huérfanos")
        
        if errors:
            print("❌ Errores de integridad encontrados:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ Integridad de FKs verificada")
            return True
```

### Script 2: Contar Registros

```sql
-- scripts/count_records.sql
SELECT 'animal' as tabla, COUNT(*) as cantidad FROM animal UNION ALL
SELECT 'finca', COUNT(*) FROM finca UNION ALL
SELECT 'potrero', COUNT(*) FROM potrero UNION ALL
SELECT 'servicio', COUNT(*) FROM servicio UNION ALL
SELECT 'produccion_leche', COUNT(*) FROM produccion_leche UNION ALL
SELECT 'tratamiento', COUNT(*) FROM tratamiento UNION ALL
SELECT 'peso', COUNT(*) FROM peso UNION ALL
SELECT 'insumo', COUNT(*) FROM insumo UNION ALL
SELECT 'herramienta', COUNT(*) FROM herramienta
ORDER BY cantidad DESC;
```

## 📝 Notas Importantes

1. **Modo Desarrollo Only:** El seed solo se ejecuta en modo `dev`. En producción está deshabilitado.

2. **Datos No Persistentes:** Los datos de prueba se generan cada vez. No están hardcodeados en la BD.

3. **Transacciones:** Cada módulo usa transacciones para garantizar consistencia.

4. **Logging Detallado:** Se registra cada operación en `logs/fincafacil.log`.

5. **Sin Destrucción Automática:** Por defecto NO limpia datos previos. Usar `--clear` si se necesita.

6. **Relaciones Coherentes:** 
   - Animales vinculados a fincas reales
   - Servicios entre animales existentes
   - Producción solo en hembras lecheras
   - Tratamientos en animales activos

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| No carga datos | Verificar permisos de BD, no está en uso |
| FK violations | Revisar orden de inserción en `run()` |
| Datos incompletos | Revisar logs para errores silenciosos |
| Performance lenta | Verificar índices en BD, aumentar `count` de animales |
| Gráficos no cargan | Verificar matplotlib, datos de producción |

## 📈 Resultados Esperados

Al finalizar la Fase 1:

✅ **Dashboard:** Muestra KPIs reales basados en datos simulated  
✅ **Módulos:** Todos funcionan sin errores  
✅ **Reportes:** Se generan correctamente  
✅ **Performance:** Sistema responde rápido  
✅ **Integridad:** BD consistente y sin registros huérfanos  
✅ **UX:** Flujos completos validados  

## 📞 Contacto & Soporte

Para reportar errores o sugerencias:
- Revisar logs: `logs/fincafacil.log`
- Ejecutar validación: `python scripts/validate_seed.py`
- Reportar issue con contexto completo

---

**Versión:** 1.0  
**Última actualización:** Diciembre 2025  
**Autor:** FincaFácil Dev Team
