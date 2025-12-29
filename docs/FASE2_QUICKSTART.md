# ⚡ QUICKSTART - FASE 2

## Activación en 3 Minutos

### 1️⃣ Verificar Instalación (30 segundos)

```bash
# Desde el directorio raíz de FincaFacil
python -c "from src.core.business_rules import business_rules; print('✓ Core instalado')"
python -c "from src.services.financial_service import financial_service; print('✓ Servicios instalados')"
```

### 2️⃣ Ejecutar Auditoría (1 minuto)

```bash
python scripts/audit_operations.py
```

**Resultado esperado:**
```
═══════════════════════════════════════════════════════
         AUDITORÍA OPERATIVA - FINCAFÁCIL
═══════════════════════════════════════════════════════

✓ Base de datos: OK
✓ Reglas de negocio: 3 alertas
✓ Finanzas: Margen 43.2%
✓ Producción: 900L en 30 días
```

### 3️⃣ Probar Validaciones (1.5 minutos)

**En Python Console:**
```python
from src.core.business_rules import business_rules

# Probar validación de venta
es_valido, msg = business_rules.validate_animal_sale(1, "2025-12-27")
print(f"Validación: {es_valido} - {msg}")

# Probar cálculo de precio sugerido
precio = business_rules.calculate_animal_sale_price_suggestion(1)
print(f"Precio sugerido: ${precio:,.0f}")
```

**En la Aplicación:**
1. Abrir FincaFácil
2. Ir a **Ventas** → Nueva Venta
3. Seleccionar animal
4. Click **💡 Sugerido** (ver precio calculado)
5. Intentar vender el mismo animal dos veces → ¡Debe rechazar!

---

## 🎯 Funcionalidades Principales

### ✅ Validaciones Automáticas
- Animal muerto → **NO se puede vender**
- Animal vendido dos veces → **RECHAZADO**
- Stock de leche insuficiente → **ALERTADO**
- Contratos superpuestos → **BLOQUEADO**

### 💰 KPIs Financieros (Dashboard)
- **Ingresos** vs **Costos** → Margen visual
- **Costo por litro** → Rentabilidad de producción
- **Alertas financieras** → Déficit detectado
- **Comparativa** → Mes actual vs anterior

### 🔍 Auditoría Operativa (CLI)
```bash
python scripts/audit_operations.py --detailed --output both
```
Genera:
- Reporte de consola
- Archivo JSON: `logs/audit_YYYYMMDD_HHMMSS.json`

---

## 📊 Demo: Validación de Venta

### Escenario 1: Venta Válida ✅

```python
from src.modules.ventas.ventas_helpers_fase2 import validar_venta_animal_fase2

# Animal vivo, nunca vendido
es_valido, msg = validar_venta_animal_fase2(
    animal_id=5,
    fecha_venta="2025-12-27",
    precio=2500000,
    logger=None
)
# Resultado: (True, "OK")
```

### Escenario 2: Venta Inválida ❌

```python
# Animal ya vendido
es_valido, msg = validar_venta_animal_fase2(
    animal_id=10,  # Vendido previamente
    fecha_venta="2025-12-27",
    precio=2500000,
    logger=None
)
# Resultado: (False, "Animal #10 ya fue vendido previamente...")
```

### Escenario 3: Precio Bajo ⚠️

```python
# Precio sospechoso (muy bajo)
es_valido, msg = validar_venta_animal_fase2(
    animal_id=5,
    fecha_venta="2025-12-27",
    precio=50000,  # Solo $50k
    logger=None
)
# Resultado: (False, "Precio muy bajo ($50,000). Sugerido: $2,400,000...")
```

---

## 🚨 Alertas Automáticas

### Ver Alertas Críticas

**Desde la UI:**
1. Dashboard → Click **🔍 Ver Alertas Críticas**

**Desde Python:**
```python
from src.services.validation_service import validation_service

alertas = validation_service.get_critical_alerts_only()
print(f"Alertas críticas: {len(alertas)}")

for alert in alertas:
    print(f"- {alert['message']}")
```

**Desde CLI:**
```bash
python scripts/audit_operations.py --scope all
```

---

## 📈 KPIs en Dashboard

### Visualización Mejorada

```
┌────────────────────────────────────────┐
│ 💰 KPIs Financieros (Mes Actual)  🔄  │
├────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐      │
│ │ 💵 Ingresos │  │ 💸 Costos   │      │
│ │ $15,240,000 │  │ $8,650,000  │      │
│ └─────────────┘  └─────────────┘      │
│ ┌─────────────┐  ┌─────────────┐      │
│ │ 📈 Margen   │  │ 🥛 Costo/L  │      │
│ │ $6,590,000  │  │ $850/L      │      │
│ │ 43.2%       │  │             │      │
│ └─────────────┘  └─────────────┘      │
└────────────────────────────────────────┘
```

### Acceso Rápido

```python
from src.services.financial_service import financial_service

kpis = financial_service.get_dashboard_kpis('mes_actual')
print(f"Margen: {kpis['margen_porcentaje']:.1f}%")
```

---

## 🔧 Integración Rápida

### En Módulo de Ventas

**Agregar 3 líneas en `ventas_main.py`:**

```python
# 1. Import
from src.modules.ventas.ventas_helpers_fase2 import validar_venta_animal_fase2

# 2. En guardar_venta(), reemplazar validación:
es_valido, msg = validar_venta_animal_fase2(id_animal, fecha, precio, self.logger)
if not es_valido:
    messagebox.showerror("Validación", msg)
    return

# 3. Listo! ✅
```

### En Dashboard

**Agregar 2 líneas en `dashboard_main.py`:**

```python
# 1. Import
from src.modules.dashboard.dashboard_helpers_fase2 import crear_seccion_kpis_financieros

# 2. En crear_widgets():
crear_seccion_kpis_financieros(self.scrollable_frame)

# 3. Listo! ✅
```

---

## 📚 Documentación Completa

Ver: [`docs/FASE2_CONSOLIDACION_OPERATIVA.md`](FASE2_CONSOLIDACION_OPERATIVA.md)

---

## ✅ Checklist Post-Instalación

- [ ] Auditoría completa ejecutada sin errores
- [ ] KPIs visibles en dashboard
- [ ] Validaciones de ventas funcionando
- [ ] Script CLI genera reportes JSON
- [ ] Sin errores de importación

---

## 🆘 Problemas Comunes

### Error: Module not found

```bash
# Solución: Agregar src/ al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### KPIs muestran $0

```bash
# Solución: Cargar datos de prueba (Fase 1)
python -c "from src.database.seed_data import run_seed; run_seed(False, 'all')"
```

---

**¡Listo para usar! 🚀**
