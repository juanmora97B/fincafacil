# 🗺️ ROADMAP FASE 9 — Ejecución y Escalado Controlado

Estado: Planificación estratégica (sin cambios de código)
Objetivo: Ruta clara y segura para gobernar los 10 dominios restantes.

---

## 🎯 Visión General de FASE 9

Convertir el sistema completo en una arquitectura gobernada, manteniendo estabilidad y permitiendo cambios seguros a largo plazo.

### Fases Secundarias
- **FASE 9.0:** Quick wins (5 dominios menores, bajo riesgo)
- **FASE 9.1:** Críticos tempranos (Ventas, Leche)
- **FASE 9.2:** Integraciones complejas (Dashboard, Nómina, Reportes)
- **FASE 9.3:** Eliminación de legacy y tests reales
- **FASE 10:** Optimización y performance

---

## 📅 FASE 9.0 — Quick Wins (Semanas 1–4, 1 developer)

### Objetivo
Gobernar 5 dominios menores, ganar experiencia, validar patrón.

### Dominios
1. Potreros (250L, 10 queries)
2. Ajustes (300L, 10 queries)
3. Configuración (400L, 15 queries)
4. Reportes (500L, 20 queries lectura)
5. Herramientas (600L, 15 queries)

### Ejecución
- 1 dominio por 4–5 días (auditoría → encapsulación → migración → validación)
- Validación: Auditor Exit 0, Pylance 0 errores
- Sin cambios en UX ni comportamiento
- Documentar lecciones aprendidas

### Salida
- ✅ 5 dominios gobernados (total 8/13)
- ✅ Experiencia operativa para críticos
- ✅ Validación de herramientas (auditor, Pylance)
- ✅ Confianza en patrón

---

## 🔴 FASE 9.1 — Críticos Tempranos (Semanas 5–12, 2 developers)

### Objetivo
Gobernar Ventas y Leche (impacto financiero alto, complejidad media-alta).

### Dominio 1: Leche (Semanas 5–7)
**Por qué primero:** Menos dependencias cruzadas que Ventas, pero igual importancia financiera.

- Auditoría: 20 queries, 3 reglas negocio
- Encapsulación: Leche_Repository (10 métodos), Leche_Service (5 métodos)
- Migración UI: 800 líneas a refactorizar
- Validación: trazabilidad de producción
- Documentación: FASE9_1_MIGRACION_LECHE.md

### Dominio 2: Ventas (Semanas 8–12)
**Por qué después:** Requiere experiencia con leche; más dependencias cruzadas.

- Auditoría: 50+ queries, 5+ reglas negocio
- Encapsulación: Ventas_Repository (25 métodos), Ventas_Service (10 métodos)
- Migración UI: 1000+ líneas a refactorizar
- Validación: integridad de transacciones, impacto en Dashboard/Reportes
- Documentación: FASE9_1_MIGRACION_VENTAS.md

### Salida
- ✅ 7 dominios gobernados (total 10/13)
- ✅ Flujos financieros protegidos
- ✅ Dashboard/Reportes dependen de servicios validados
- ⚠️ Potencial impacto en Dashboard (requiere validación post-migración)

---

## 🟡 FASE 9.2 — Integraciones Complejas (Semanas 13–20, 2 developers)

### Dominio 1: Dashboard (Semanas 13–16)
**Nota:** Se abordan DESPUÉS de Ventas/Leche/Insumos para evitar cambios de dependencias.

- Auditoría: 30 queries aggregadas, 8+ dependencias
- Encapsulación: Dashboard_Repository, Dashboard_Service (agregaciones)
- Migración UI: 1200+ líneas, cuidado con gráficos
- Validación: coherencia de datos entre dominios

### Dominio 2: Insumos (Semanas 17–19)
- Auditoría: 25 queries, 4 reglas negocio (stock, costo)
- Encapsulación: Insumos_Repository, Insumos_Service
- Migración UI: 700 líneas
- Validación: impacto en cálculo de costos (Reportes)

### Dominio 3: Nómina (Semana 20)
**⚠️ Riesgoso:** Impacto legal/laboral. Requiere auditoría intensiva post-migración.

- Auditoría: 20 queries, 6+ reglas negocio (salarios, deducciones)
- Encapsulación: Nomina_Repository, Nomina_Service (cálculos complejos)
- Migración UI: 600 líneas
- Validación: trazabilidad de cálculos, cumplimiento normativo

### Salida
- ✅ 10/13 dominios gobernados
- ⚠️ Nómina requiere verificación legal/audit externo
- ✅ Dashboard coherente con datos gobernados

---

## 🔄 FASE 9.3 — Eliminación de Legacy y Tests (Semanas 21–30)

### Objetivo
Remover duplicación, listas hardcoded, errores genéricos; introducir tests reales.

### Tareas
1. Centralizar catálogos en gateway (estados, tipos, unidades)
2. Crear `CatalogoService` y reemplazar hardcoded en 5+ servicios
3. Introducir taxonomía de errores (dominio-specific exceptions)
4. Escribir tests unitarios para validaciones clave
5. Documentar breaking changes hacia FASE 10

### Salida
- ✅ Sistema sin hardcoded lists
- ✅ Errores tipados (sin romper UI)
- ✅ Cobertura de tests >70%
- ✅ Pronto para FASE 10

---

## 🚀 FASE 10 — Optimización y Consolidación (No planificado aún)

- Performance: índices BD, query optimization
- Cleanup: eliminar adapters legacy
- Testing: pruebas de integración e2e
- Rollout: versión estable 3.0

---

## 📊 Timeline Consolidado

| Fase | Semanas | Dominios | Dev | Salida Esperada |
|------|---------|----------|-----|-----------------|
| 9.0 | 1–4 | 5 quick wins | 1 | 8/13 gobernados |
| 9.1 | 5–12 | Leche, Ventas | 2 | 10/13 gobernados |
| 9.2 | 13–20 | Dashboard, Insumos, Nómina | 2 | 13/13 gobernados |
| 9.3 | 21–30 | Legacy cleanup, tests | 2 | Sistema listo FASE 10 |
| **Total** | **30 semanas** | **13 dominios** | **2 devs** | **Arquitectura estable** |

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|------|--------|-----------|
| Ventas requiere más tiempo | 🟡 Media | 🔴 Alto | Iniciar early, 2 devs dedicados |
| Dashboard romperse por dependencias | 🟡 Media | 🔴 Alto | Validar post-migración cada depto |
| Nómina no pasar auditoría legal | 🟡 Media | 🔴 Crítico | Involucrar contador antes de 9.2 |
| Retraso en quick wins afecta ritmo | 🟢 Bajo | 🟡 Medio | Empezar ASAP, equipo dedicado |
| Nuevas features requieren refactor | 🟡 Media | 🟡 Medio | Congelar features durante 9.0–9.1 |

---

## ✅ Criterios de Éxito por Fase

### FASE 9.0
- [ ] 5 dominios con Auditor Exit 0
- [ ] Pylance 0 errores en nuevos services
- [ ] UI sin cambios (solo refactoring internal)
- [ ] Documentación de lecciones aprendidas

### FASE 9.1
- [ ] Ventas + Leche gobernados
- [ ] Dashboard / Reportes dependen de servicios validados
- [ ] Integridad de datos verificada post-migración
- [ ] 0 violaciones nuevas introducidas

### FASE 9.2
- [ ] Dashboard + Insumos + Nómina gobernados
- [ ] 13/13 dominios en patrón gobernado
- [ ] Nómina pasa auditoría interna
- [ ] Cobertura tests > 50%

### FASE 9.3
- [ ] Sin hardcoded lists
- [ ] Taxonomía de errores implementada
- [ ] Tests > 70% cobertura
- [ ] Documentación de FASE 10

---

## 📋 Entregables por Fase

### FASE 9.0
- 5 docs `FASE9_0_MIGRACION_<DOMINIO>.md`
- Service + Repository por dominio
- Actualización matriz madurez

### FASE 9.1
- 2 docs `FASE9_1_MIGRACION_<DOMINIO>.md`
- Validación de impacto Dashboard/Reportes
- Plan de rollback por dominio

### FASE 9.2
- 3 docs `FASE9_2_MIGRACION_<DOMINIO>.md`
- Certificación legal de Nómina (auditoría)
- Catálogo centralizado (CatalogoService)

### FASE 9.3
- Documento `FASE9_3_LEGACY_CLEANUP.md`
- Suite de tests
- Plan FASE 10

---

## 🎯 Definición de "Hecho"

El sistema estará listo para FASE 10 cuando:

1. **Todos los dominios (13/13) cumplen:**
   - Auditor Exit 0 (0 violaciones UI→BD)
   - Pylance 0 errores
   - UI sin SQL directo ni `ejecutar_consulta`
   - Validaciones centralizadas en Service
   - Catálogos desde gateway/tablas (no hardcoded)

2. **Testing:**
   - Tests unitarios para validaciones (cobertura > 70%)
   - Tests integración básicos para 3+ dominios críticos
   - Casos de error documentados

3. **Documentación:**
   - Guía de desarrollo completa y actualizada
   - Matriz de madurez con 100% gobernancia
   - Plan detallado FASE 10

4. **No hay deuda:**
   - Sin hardcoded lists
   - Sin SQL duplicado
   - Sin validaciones en UI
   - Sin errores genéricos

---

## 🔗 Referencias

- Inventario: [docs/FASE8_8_INVENTARIO_DOMINIOS.md](FASE8_8_INVENTARIO_DOMINIOS.md)
- Guía dev: [docs/GUIA_DESARROLLO_DOMINIOS.md](GUIA_DESARROLLO_DOMINIOS.md)
- Estado actual: [docs/FASE8_7_ESTADO_ESTABLE.md](FASE8_7_ESTADO_ESTABLE.md)

---

**Fin del roadmap FASE 9.**

Recomendación: Revisar con el equipo, ajustar timeline según recursos disponibles, y congelar features nuevas durante 9.0–9.1.
