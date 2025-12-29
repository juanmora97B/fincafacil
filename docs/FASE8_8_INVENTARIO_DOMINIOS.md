# 📊 FASE 8.8 — Inventario Completo de Dominios

Estado: ✅ Auditoría pasiva completada (sin cambios de código)
Objetivo: Mapeo completo, priorización y plan de FASE 9.

---

## 🎯 Resumen Ejecutivo

| Categoría | Cantidad | Detalle |
|-----------|----------|---------|
| **Gobernados (100%)** | 3 | Animales, Reproducción, Salud |
| **Pendientes (Críticos)** | 4 | Ventas, Dashboard, Leche, Herramientas |
| **Pendientes (Medianos)** | 3 | Insumos, Reportes, Nómina |
| **Pendientes (Menores)** | 3 | Ajustes, Configuración, Potreros |
| **Total dominios** | 13 | 3 gobernados + 10 pendientes |

**Riesgo promedio pendientes:** 🟡 Medio (SQL directo, validaciones dispersas, estados hardcoded)

---

## 📋 Dominios Gobernados (Cerrados)

### ✅ Animales
- **Estado:** 100% gobernado, 0 violaciones
- **Patrón:** Repository + Service
- **UI:** `src/modules/animales/`
- **Infraestructura:** `src/infraestructura/animales/`

### ✅ Reproducción
- **Estado:** 100% gobernado, 0 violaciones
- **Patrón:** Repository + Service
- **UI:** `src/modules/reproduccion/`
- **Infraestructura:** `src/infraestructura/reproduccion/`

### ✅ Salud
- **Estado:** 100% gobernado, 0 violaciones
- **Patrón:** Repository + Service
- **UI:** `src/modules/salud/`
- **Infraestructura:** `src/infraestructura/salud/`

---

## 🔴 Dominios Pendientes (Críticos — Alto riesgo, Alta prioridad)

### 1. Ventas
**UI:** `src/modules/ventas/ventas_main.py` (1000+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 50+ queries (`cursor.execute(...)`)
- ✗ `db.get_connection()` repetido (20+ instancias)
- ✗ `cursor.fetchall/fetchone()` en UI
- ✗ `conn.commit()` en UI (múltiples)

**Reglas de Negocio:**
- Validación de precios: inline en UI
- Validación de animales disponibles: SQL condicional en UI
- Generación de códigos de venta: lógica en handlers

**Estados Hardcoded:**
- Estados de animales: `Activo`, `Muerto`, `Vendido` (en SQL)

**Dependencias:**
- Animales (FK animal_id)
- Dashboard (impacto en gráficos de ventas)
- Reportes (datos agregados)

**Complejidad Estimada:** 🔴 **Alta**
- 50+ queries a encapsular
- 3+ métodos principales de escritura
- Lógica de precios y validaciones complejas
- Impacto crítico en flujo de negocio

**Riesgo Técnico:** 🔴 **Crítico**
- Si se rompe, el sistema no puede registrar ventas
- Impacto directo en ingresos/reportes financieros

**Riesgo por Dependencias:**
- Dashboard depende de datos de ventas
- Reportes financieros dependen de integridad de datos

---

### 2. Dashboard
**UI:** `src/modules/dashboard/dashboard_main.py` (1200+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 30+ queries
- ✗ `db.get_connection()` (15+ instancias)
- ✗ Cursor directo para cálculos en UI
- ✗ `_actualizar_grafico_*()` con SQL embebido

**Reglas de Negocio:**
- Conteos agregados: sin validación
- Cálculos de producción: lógica en handlers
- Alertas dinámicas: SQL condicional en método privado

**Estados Hardcoded:**
- Estados de animales: `Activo`, `Muerto`, `Vendido`, `Gestante`
- Estados de producción: valores hardcoded

**Dependencias:**
- Animales (estadísticas)
- Reproducción (gestantes, partos)
- Salud (tratamientos, diagnósticos)
- Leche (producción del día)
- Ventas (ingresos agregados)

**Complejidad Estimada:** 🟡 **Media-Alta**
- 30+ queries pero muchas son simples COUNTs
- Agregaciones complejas con múltiples JOINs
- Gráficos dinámicos

**Riesgo Técnico:** 🟡 **Medio**
- Dashboard es informativo (no transaccional)
- Bugs aquí no corrompen datos
- Pero impactan decisiones de negocio

**Nota:** Dashboard depende de 5 dominios, pero aquí se focaliza en infraestructura interna.

---

### 3. Leche (Producción)
**UI:** `src/modules/leche/` (estimado 800+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 20+ queries
- ✗ `db.get_connection()` (10+ instancias)
- ✗ Registros de producción diaria sin validación central

**Reglas de Negocio:**
- Validación de volúmenes: inline en UI
- Cálculos de promedio: lógica dispersa
- Calidad de leche: enumeración sin catálogo

**Estados Hardcoded:**
- Calidad: `A`, `B`, `C` (sin tabla dedicada)

**Dependencias:**
- Animales (referencia de vacas)
- Dashboard (agregados de producción)

**Complejidad Estimada:** 🟡 **Media**
- 20+ queries moderadamente complejas
- Registro transaccional simple
- Cálculos agregados

**Riesgo Técnico:** 🔴 **Medio-Alto**
- Producción es KPI financiero crítico
- Errores en validación impactan facturación lechería
- Datos históricos críticos para trazabilidad

---

### 4. Herramientas (Inventario de Equipos)
**UI:** `src/modules/herramientas/` (estimado 600+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 15+ queries
- ✗ Cursor directo para listados y búsquedas
- ✗ Sin validación de existencia antes de UPDATE/DELETE

**Reglas de Negocio:**
- Control de disponibilidad: sin reglas
- Asignación a trabajadores: SQL condicional en UI
- Mantenimiento: estado disperso

**Estados Hardcoded:**
- Estado de herramientas: `Disponible`, `En uso`, `Mantenimiento`, `Dañada`

**Dependencias:**
- Nómina/Trabajadores (asignación)
- Potreros (ubicación)

**Complejidad Estimada:** 🟢 **Baja-Media**
- 15+ queries simples
- Operaciones CRUD estándar
- Baja complejidad de lógica

**Riesgo Técnico:** 🟡 **Medio**
- Control de inventario importante pero no crítico
- Pérdida de historial de herramientas afecta trazabilidad

---

## 🟡 Dominios Pendientes (Medianos — Riesgo medio, Prioridad media)

### 5. Insumos (Piensos, medicinas, etc.)
**UI:** `src/modules/insumos/` (estimado 700+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 25+ queries
- ✗ Cursor directo para inventario
- ✗ Validaciones de stock inline

**Reglas de Negocio:**
- Validación de unidades: sin catálogo
- Alertas de stock bajo: SQL condicional
- Cálculo de costos: disperso

**Estados Hardcoded:**
- Unidades: `Kg`, `Litro`, `Unidad`, `Bolsa`
- Categorías: `Pienso`, `Medicina`, `Vitaminas`, `Minerales`

**Dependencias:**
- Reportes (costos)
- Dashboard (agregados)

**Complejidad Estimada:** 🟡 **Media**
- 25+ queries de inventario
- Cálculos de costos
- Múltiples movimientos (entrada/salida)

**Riesgo Técnico:** 🟡 **Medio**
- Impacta cálculo de costos de producción
- Errores en validación pueden generar sobreventa

---

### 6. Reportes
**UI:** `src/modules/reportes/` (estimado 500+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 20+ queries aggregadas
- ✗ Generación de PDF con SQL embebido
- ✗ Sin validación de parámetros de filtro

**Reglas de Negocio:**
- Cálculos de márgenes: lógica en handlers
- Consolidación de datos: múltiples queries
- Formatos de reporte: hardcoded

**Dependencias:**
- Animales, Ventas, Leche, Insumos, Reproducción (5 dominios)

**Complejidad Estimada:** 🟡 **Media**
- 20+ queries complejas con agregaciones
- Pero sin lógica transaccional (solo lectura)

**Riesgo Técnico:** 🟢 **Bajo** (lectura pura)
- No afecta integridad de datos
- Errores son informativos

**Nota:** Buen candidato para refactor temprano (lectura, bajo riesgo).

---

### 7. Nómina (Payroll)
**UI:** `src/modules/nomina/` (estimado 600+ líneas)

**Violaciones de Frontera:**
- ✗ SQL directo: 20+ queries
- ✗ Cálculos de salario en UI
- ✗ Sin validación de escalas salariales

**Reglas de Negocio:**
- Cálculo de bonificaciones: lógica dispersa
- Deducciones: hardcoded
- Generación de nómina: SQL condicional

**Estados Hardcoded:**
- Tipos de deducción: `ISAPRE`, `AFP`, `Impuesto`
- Estados de pago: `Pagado`, `Pendiente`, `Anulado`

**Dependencias:**
- Trabajadores (catálogo)
- Reportes (consolidados)

**Complejidad Estimada:** 🟡 **Media**
- 20+ queries de nómina
- Cálculos de múltiples conceptos
- Validación de integridad importante

**Riesgo Técnico:** 🔴 **Medio-Alto**
- Errores en cálculo impactan legalmente (impuestos, leyes laborales)
- Requiere auditoría de cambios

---

## 🟢 Dominios Pendientes (Menores — Bajo riesgo, Baja prioridad)

### 8. Ajustes (Correcciones de inventario)
**UI:** `src/modules/ajustes/` (estimado 300+ líneas)

**Violaciones:** SQL directo: 10+ queries  
**Complejidad:** 🟢 **Baja**  
**Riesgo:** 🟢 **Bajo** (operaciones administrativas)

---

### 9. Configuración (Catálogos globales)
**UI:** `src/modules/configuracion/` (estimado 400+ líneas)

**Violaciones:** SQL directo: 15+ queries  
**Complejidad:** 🟢 **Baja**  
**Riesgo:** 🟢 **Bajo** (administración de datos)

---

### 10. Potreros (Parcelas)
**UI:** `src/modules/potreros/` (estimado 250+ líneas)

**Violaciones:** SQL directo: 10+ queries  
**Complejidad:** 🟢 **Baja**  
**Riesgo:** 🟢 **Bajo** (poco transaccional)

---

## 📊 Matriz de Priorización

| Dominio | Riesgo Técnico | Impacto Negocio | Esfuerzo | Prioridad | Candidato 9.0? |
|---------|---|---|---|---|---|
| **Ventas** | 🔴 Crítico | 🔴 Crítico | 🔴 Alto | 1 | ✅ SÍ |
| **Leche** | 🔴 Alto | 🔴 Alto | 🟡 Medio | 2 | ✅ SÍ |
| **Dashboard** | 🟡 Medio | 🟡 Alto | 🟡 Medio | 3 | ✅ SÍ (post-deptos) |
| **Herramientas** | 🟡 Medio | 🟡 Medio | 🟢 Bajo | 4 | ✅ SÍ |
| **Insumos** | 🟡 Medio | 🟡 Medio | 🟡 Medio | 5 | ✅ SÍ |
| **Nómina** | 🔴 Medio-Alto | 🔴 Alto | 🟡 Medio | 6 | 🤔 Riesgoso |
| **Reportes** | 🟢 Bajo | 🟡 Medio | 🟡 Medio | 7 | ✅ SÍ |
| **Potreros** | 🟢 Bajo | 🟢 Bajo | 🟢 Bajo | 8 | ✅ SÍ |
| **Configuración** | 🟢 Bajo | 🟢 Bajo | 🟢 Bajo | 9 | ✅ SÍ |
| **Ajustes** | 🟢 Bajo | 🟢 Bajo | 🟢 Bajo | 10 | ✅ SÍ |

---

## 🚀 "Quick Wins" (FASE 9.0 Iniciales)

### Definición
Dominios con:
- Bajo esfuerzo (< 50 queries, lógica simple)
- Riesgo técnico bajo o bajo-medio
- Bajo impacto si fallan (no transaccionales o lectura)
- Sin dependencias críticas en otros dominios

### Candidatos
1. **Potreros** (250 líneas, 10 queries, bajo riesgo)
2. **Ajustes** (300 líneas, 10 queries, bajo riesgo)
3. **Configuración** (400 líneas, 15 queries, bajo riesgo)
4. **Reportes** (500 líneas, 20 queries, lectura pura, bajo riesgo)
5. **Herramientas** (600 líneas, 15 queries, bajo-medio riesgo)

**Esfuerzo total estimado:** 3–4 semanas (1 dev)  
**Impacto:** 5 dominios estables, experiencia para críticos

---

## ⚠️ Dominios Críticos (Requieren cuidado especial)

1. **Ventas** — El más crítico; transaccional, requiere auditoría de integridad
2. **Nómina** — Riesgos legales/laborales; requiere validación exhaustiva
3. **Leche** — KPI financiero; requiere trazabilidad de cambios

**Recomendación:** Iniciar FASE 9.0 con quick wins, luego abordar críticos uno por uno.

---

## 📎 Referencias

- [docs/GUIA_DESARROLLO_DOMINIOS.md](GUIA_DESARROLLO_DOMINIOS.md) — Patrón a aplicar
- [docs/CHECKLIST_NUEVO_DOMINIO.md](CHECKLIST_NUEVO_DOMINIO.md) — Pasos por dominio
- [docs/FASE8_7_ESTADO_ESTABLE.md](FASE8_7_ESTADO_ESTABLE.md) — Criterios de éxito

---

Fin del inventario.
