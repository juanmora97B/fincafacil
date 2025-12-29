# 🔧 GUÍA DE INTEGRACIÓN RÁPIDA - FASE CONSOLIDACIÓN

## ⚡ Inicio Rápido (5 minutos)

Esta guía explica cómo usar los nuevos componentes implementados en la Fase de Consolidación.

---

## 1. 🔐 Sistema de Permisos

### Configurar Usuario Actual

```python
# En main.py (líneas 120-128)
from src.core.permissions_manager import get_permissions_manager, RoleEnum

# Después del login exitoso
self.permissions_manager = get_permissions_manager()
self.permissions_manager.set_current_user(
    usuario_id=usuario_logueado['id'],
    rol=RoleEnum[usuario_logueado['rol'].upper()]
)
```

### Proteger una Función

```python
# En cualquier servicio (e.g., ventas_service.py)
from src.core.permission_decorators import require_permission, audit_action
from src.core.permissions_manager import PermissionEnum

@require_permission(PermissionEnum.VENTAS_CREAR)
@audit_action("ventas", "CREAR")
def registrar_venta_animal(user: UserContext, data: VentaAnimal) -> int:
    # Si el usuario no tiene permiso → PermissionDeniedException
    # Si tiene permiso → ejecuta normalmente + registra en auditoría
    ...
```

### Verificar Permisos en UI

```python
# En UI para mostrar/ocultar botones
from src.core.permissions_manager import get_permissions_manager, PermissionEnum

perms = get_permissions_manager()

if perms.has_permission(PermissionEnum.VENTAS_CREAR):
    btn_nueva_venta.configure(state="normal")
else:
    btn_nueva_venta.configure(state="disabled")
```

---

## 2. 🔒 Bloqueo de Datos Cerrados

### Validar Antes de Guardar

```python
# En cualquier servicio que modifique datos
from src.services.data_lock_service import get_data_lock_service
from datetime import datetime

lock_service = get_data_lock_service()

# Convertir fecha string a date object
fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()

# Validar (lanza ValueError si período cerrado)
lock_service.validate_before_save(fecha_obj, "ventas")

# Si no lanza error → OK para guardar
guardar_en_bd(...)
```

### Bloquear Datos en Cierre Mensual

```python
# En cierre_mensual_service.py (ya implementado)
lock_service = get_data_lock_service()

# Después de conn.commit()
lock_service.block_data(año, mes, "ventas")
lock_service.block_data(año, mes, "gastos")
lock_service.block_data(año, mes, "nomina")
lock_service.block_data(año, mes, "produccion")
```

### Reabrir Período (Solo Administrador)

```python
from src.services.data_lock_service import get_data_lock_service

lock_service = get_data_lock_service()

# Requiere permiso CIERRE_REABRIR
lock_service.unblock_period(año=2025, mes=1)
```

---

## 3. 📊 Calcular y Guardar KPIs

### Calcular KPIs Mensualmente

```python
# En cierre_mensual_service.py después del cierre
from src.services.kpi_calculator_service import get_kpi_calculator
from datetime import date

kpi_calc = get_kpi_calculator()

# Calcular todos los KPIs del mes
fecha_inicio = date(año, mes, 1)
fecha_fin = ultimo_dia_mes(año, mes)

kpis = kpi_calc.calcular_kpis_periodo(
    fecha_inicio=fecha_inicio,
    fecha_fin=fecha_fin,
    categoria="general"  # o "financiero", "produccion", etc.
)

# Guardar en BD
kpi_calc.guardar_kpis_en_bd(
    año=año,
    mes=mes,
    kpis=kpis,
    categoria="general"
)

print(f"✅ {len(kpis)} KPIs guardados para {año}-{mes:02d}")
```

### Consultar Tendencia de un KPI

```python
from src.services.kpi_calculator_service import get_kpi_calculator

kpi_calc = get_kpi_calculator()

# Últimos 6 meses de margen neto
tendencia = kpi_calc.obtener_tendencia_kpi(
    nombre_kpi="margen_neto_pct",
    meses_atras=6
)

# tendencia = [
#   {'año': 2025, 'mes': 1, 'valor': 35.2, 'periodo': '2025-01'},
#   {'año': 2024, 'mes': 12, 'valor': 32.8, 'periodo': '2024-12'},
#   ...
# ]

# Mostrar en gráfica
for item in tendencia:
    print(f"{item['periodo']}: {item['valor']}%")
```

---

## 4. ⚠️ Evaluar y Guardar Alertas

### Ejecutar Evaluación de Reglas

```python
# Ejecutar diariamente (cron/scheduler) o manualmente
from src.services.alert_rules_service import get_alert_rules_service

alert_service = get_alert_rules_service()

# Evaluar todas las reglas
alertas = alert_service.evaluar_todas_reglas()

# Guardar en BD (evita duplicados)
alert_service.guardar_alertas_en_bd(alertas, usuario="sistema")

print(f"✅ {len(alertas)} alertas generadas")
```

### Consultar Alertas Activas

```python
from src.services.alert_rules_service import get_alert_rules_service

alert_service = get_alert_rules_service()

# Todas las alertas activas
todas = alert_service.obtener_alertas_activas()

# Solo alertas de alta prioridad
altas = alert_service.obtener_alertas_activas(prioridad="alta")

# Mostrar en UI
for alerta in altas:
    print(f"[{alerta['prioridad'].upper()}] {alerta['titulo']}")
    print(f"  → {alerta['descripcion']}")
```

### Resolver una Alerta

```python
# En UI cuando usuario marca alerta como resuelta
from database.database import get_db_connection

with get_db_connection() as conn:
    conn.execute("""
        UPDATE alertas
        SET estado = 'resuelta',
            fecha_resolucion = CURRENT_TIMESTAMP,
            resuelto_por = ?,
            notas_resolucion = ?
        WHERE id = ?
    """, (usuario_actual, notas, alerta_id))
    conn.commit()
```

---

## 5. 📥 Exportar Reportes

### Exportar Resumen Mensual

```python
from src.services.report_exporters_service import get_report_exporters

exporter = get_report_exporters()

# Exportar resumen de enero 2025 a CSV
ruta = exporter.exportar_resumen_mensual_csv(año=2025, mes=1)
print(f"Resumen exportado a: {ruta}")
# Output: exports/resumen_mensual_2025_01.csv
```

### Exportar KPIs con Tendencias

```python
from src.services.report_exporters_service import get_report_exporters

exporter = get_report_exporters()

# Exportar últimos 6 meses de todos los KPIs
ruta = exporter.exportar_kpis_csv(meses_atras=6)
print(f"KPIs exportados a: {ruta}")
# Output: exports/kpis_20250115_143022.csv

# Exportar solo margen_neto_pct de últimos 12 meses
ruta = exporter.exportar_kpis_csv(
    nombre_kpi="margen_neto_pct",
    meses_atras=12
)
```

### Exportar Resumen Ejecutivo

```python
from src.services.report_exporters_service import get_report_exporters

exporter = get_report_exporters()

# Resumen ejecutivo en formato texto
ruta = exporter.exportar_resumen_ejecutivo_txt(año=2025, mes=1)
print(f"Resumen ejecutivo exportado a: {ruta}")
# Output: exports/resumen_ejecutivo_2025_01.txt

# Contenido del archivo:
# ═══════════════════════════════════════════
# RESUMEN EJECUTIVO - 2025-01
# ═══════════════════════════════════════════
# 💰 RESUMEN FINANCIERO
# Ingresos Totales:     $12,345,678
# ...
```

### Exportar Todo de una Vez

```python
from src.services.report_exporters_service import get_report_exporters

exporter = get_report_exporters()

# Generar todos los reportes
archivos = exporter.exportar_todos_formatos(año=2025, mes=1)

# archivos = {
#   'resumen_csv': 'exports/resumen_mensual_2025_01.csv',
#   'kpis_csv': 'exports/kpis_20250115_143022.csv',
#   'alertas_csv': 'exports/alertas_20250115_143022.csv',
#   'resumen_ejecutivo': 'exports/resumen_ejecutivo_2025_01.txt'
# }

for tipo, ruta in archivos.items():
    print(f"{tipo}: {ruta}")
```

---

## 6. 🔄 Ciclo de Vida en Cierre de Aplicación

### Ya Implementado en main.py

```python
# main.py líneas 598-658
def on_closing(self):
    """Cierre ordenado con validaciones"""
    try:
        # Ejecutar lifecycle de forma síncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Llamar a lifecycle.on_app_close()
        loop.run_until_complete(self.lifecycle.on_app_close())
        loop.close()
        
    except Exception as e:
        self.logger.error(f"Error en cierre: {e}")
    finally:
        self.root.quit()
```

### Registrar Callbacks Personalizados

```python
# En cualquier módulo que necesite limpieza
from src.core.app_lifecycle import get_lifecycle_manager

lifecycle = get_lifecycle_manager()

# Pre-close callback
def mi_limpieza_pre_close():
    print("Ejecutando limpieza antes de cerrar...")
    # Guardar configuraciones
    # Cerrar conexiones
    ...

lifecycle.register_pre_close_callback(mi_limpieza_pre_close)

# Post-close callback
def mi_limpieza_post_close():
    print("Ejecutando limpieza después de cerrar...")
    # Liberar recursos
    ...

lifecycle.register_post_close_callback(mi_limpieza_post_close)
```

---

## 7. 📝 Auditoría Automática

### Usar Decorator

```python
from src.core.permission_decorators import audit_action

@audit_action("ventas", "ELIMINAR")
def eliminar_venta(user: UserContext, venta_id: int):
    # Automáticamente registra en tabla auditoria:
    # - usuario
    # - modulo = "ventas"
    # - accion = "ELIMINAR"
    # - entidad = f"venta:{venta_id}"
    # - timestamp
    # - resultado = "OK" o "ERROR"
    ...
```

### Auditoría Manual

```python
from src.core.audit_service import log_event

log_event(
    usuario=usuario_actual,
    modulo="configuracion",
    accion="CAMBIAR_CONFIGURACION",
    entidad=f"finca:{finca_id}",
    valores_anteriores={"nombre": "Finca A"},
    valores_nuevos={"nombre": "Finca B"},
    resultado="OK",
    mensaje="Nombre de finca actualizado"
)
```

---

## 8. 🗄️ Migraciones de BD

### Ya Ejecutadas Automáticamente

Las migraciones se ejecutan automáticamente al iniciar la aplicación:

```python
# En database/database.py líneas 206-209
from database.migraciones import ejecutar_migraciones

ejecutar_migraciones(conn)
```

### Verificar Estado de Migraciones

```python
from database.database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # Verificar tablas creadas
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    
    tablas = [row[0] for row in cursor.fetchall()]
    
    esperadas = [
        'usuario', 'usuario_rol', 'auditoria',
        'cierre_mensual', 'datos_cerrados',
        'kpi_tracking', 'alertas'
    ]
    
    for tabla in esperadas:
        if tabla in tablas:
            print(f"✅ {tabla}")
        else:
            print(f"❌ {tabla} - FALTA")
```

---

## 9. 🧪 Testing

### Test Manual Rápido

```python
# test_consolidacion.py
from src.core.permissions_manager import get_permissions_manager, RoleEnum, PermissionEnum
from src.services.data_lock_service import get_data_lock_service
from src.services.kpi_calculator_service import get_kpi_calculator
from datetime import date

# Test 1: Permisos
print("Test 1: Permisos...")
perms = get_permissions_manager()
perms.set_current_user(1, RoleEnum.ADMINISTRADOR)
assert perms.has_permission(PermissionEnum.VENTAS_CREAR)
print("✅ Permisos OK")

# Test 2: Data Locking
print("\nTest 2: Data Locking...")
lock = get_data_lock_service()
lock.block_data(2024, 12, "ventas")
assert lock.is_period_closed(2024, 12)
print("✅ Data Locking OK")

# Test 3: KPIs
print("\nTest 3: KPIs...")
kpi_calc = get_kpi_calculator()
kpis = kpi_calc.calcular_kpis_periodo(
    date(2025, 1, 1),
    date(2025, 1, 31),
    "financiero"
)
assert 'margen_neto_pct' in kpis
print(f"✅ KPIs OK - {len(kpis)} calculados")

print("\n🎉 Todos los tests pasaron!")
```

---

## 10. 📊 Flujo Completo de Cierre Mensual

### Proceso Recomendado

```python
# 1. Verificar que todos los datos del mes estén registrados
# (Manual - revisar con usuario)

# 2. Ejecutar cierre mensual
from src.services.cierre_mensual_service import cierre_mensual_service

resumen = cierre_mensual_service.realizar_cierre(
    año=2025,
    mes=1,
    usuario=usuario_actual,
    observaciones="Cierre normal - Sin observaciones"
)

# Esto automáticamente:
# - Genera resumen_mensual con métricas
# - Bloquea datos (ventas, gastos, nomina, produccion)
# - Registra en auditoría

# 3. Calcular KPIs del mes cerrado
from src.services.kpi_calculator_service import get_kpi_calculator
from datetime import date

kpi_calc = get_kpi_calculator()
kpis = kpi_calc.calcular_kpis_periodo(
    date(2025, 1, 1),
    date(2025, 1, 31),
    "general"
)
kpi_calc.guardar_kpis_en_bd(2025, 1, kpis)

# 4. Evaluar alertas del período
from src.services.alert_rules_service import get_alert_rules_service

alert_service = get_alert_rules_service()
alertas = alert_service.evaluar_todas_reglas()
alert_service.guardar_alertas_en_bd(alertas, usuario_actual)

# 5. Exportar reportes para BI
from src.services.report_exporters_service import get_report_exporters

exporter = get_report_exporters()
archivos = exporter.exportar_todos_formatos(2025, 1)

print(f"✅ Cierre completado - {len(archivos)} reportes generados")
```

---

## 🎯 Checklist de Integración

Antes de desplegar a producción:

- [ ] **Permisos:** Usuario actual se pasa correctamente desde login
- [ ] **Data Locking:** Cierre mensual bloquea datos automáticamente
- [ ] **KPIs:** Se calculan y guardan mensualmente
- [ ] **Alertas:** Se evalúan y notifican semanalmente
- [ ] **Exportaciones:** Reportes generan sin errores
- [ ] **Auditoría:** Acciones críticas se registran
- [ ] **UI:** Botones/menús respetan permisos de usuario
- [ ] **Documentación:** Usuarios capacitados en nuevas funcionalidades

---

## 📚 Referencias Rápidas

| Componente | Archivo | Singleton |
|------------|---------|-----------|
| Permisos | `src/core/permissions_manager.py` | `get_permissions_manager()` |
| Lifecycle | `src/core/app_lifecycle.py` | `get_lifecycle_manager()` |
| Data Lock | `src/services/data_lock_service.py` | `get_data_lock_service()` |
| KPIs | `src/services/kpi_calculator_service.py` | `get_kpi_calculator()` |
| Alertas | `src/services/alert_rules_service.py` | `get_alert_rules_service()` |
| Exportadores | `src/services/report_exporters_service.py` | `get_report_exporters()` |

---

## 🆘 Solución de Problemas

### Error: "PermissionDeniedException"
**Causa:** Usuario no tiene permiso requerido  
**Solución:** Verificar rol del usuario o asignar permiso adicional

### Error: "ValueError: Período cerrado"
**Causa:** Intentando modificar datos de mes cerrado  
**Solución:** Reabrir período con `unblock_period()` (solo Admin)

### Error: "No existe resumen para..."
**Causa:** Cierre mensual no ejecutado  
**Solución:** Ejecutar `realizar_cierre()` primero

### Error: "Tabla X no existe"
**Causa:** Migraciones no ejecutadas  
**Solución:** Ejecutar manualmente `ejecutar_migraciones(conn)`

---

**Última actualización:** ${new Date().toISOString()}  
**Versión:** 1.0.0-consolidacion
