# CHANGELOG - FincaFácil

Registro consolidado de cambios, mejoras y correcciones del sistema.

---

## [2.1.0] - 28 Diciembre 2025

### 🚀 FASES 23–27 (Enterprise & Expansión)
- ✅ FASE 23: Matriz legal LATAM y términos base (propiedad de datos, DPA/SLA, transferencias internacionales)
- ✅ FASE 24: API pública y ecosistema (OpenAPI, OAuth2/api keys, rate limiting, webhooks seguros)
- ✅ FASE 25: Ingeniería multi-tenant (aislamiento por esquema/RLS, cifrado por tenant, runbook de migraciones/backup)
- ✅ FASE 26: Partnerships y expansión (canales, ISV, revenue share, SLAs por socio)
- ✅ FASE 27: Estrategia 2030 (crecimiento orgánico, inversión, M&A, spin-off institucional)

### 📄 Documentos
- [FASE_23_MATRIZ_LEGAL_Y_COMPLIANCE.md](../../FASE_23_MATRIZ_LEGAL_Y_COMPLIANCE.md)
- [LEGAL_MATRIX_LATAM.md](../../LEGAL_MATRIX_LATAM.md)
- [TERMINOS_Y_RESPONSABILIDADES_BASE.md](../../TERMINOS_Y_RESPONSABILIDADES_BASE.md)
- [FASE_24_API_Y_ECOSISTEMA.md](../../FASE_24_API_Y_ECOSISTEMA.md)
- [OPENAPI_FINCAFACIL.yaml](../../OPENAPI_FINCAFACIL.yaml)
- [GUIA_INTEGRACIONES_TERCEROS.md](../../GUIA_INTEGRACIONES_TERCEROS.md)
- [FASE_25_MULTI_TENANT_ENGINEERING.md](../../FASE_25_MULTI_TENANT_ENGINEERING.md)
- [RUNBOOK_MULTI_TENANT.md](../../RUNBOOK_MULTI_TENANT.md)
- [FASE_26_PARTNERSHIPS_Y_EXPANSION.md](../../FASE_26_PARTNERSHIPS_Y_EXPANSION.md)
- [PARTNERSHIP_PLAYBOOK.md](../../PARTNERSHIP_PLAYBOOK.md)
- [FASE_27_ESTRATEGIA_Y_SALIDA.md](../../FASE_27_ESTRATEGIA_Y_SALIDA.md)
- [ESCENARIOS_ESTRATEGICOS_2030.md](../../ESCENARIOS_ESTRATEGICOS_2030.md)

### 📊 Estado
- **Status:** ✅ Documentado; pendiente smoke test UI/backend para etiquetar v2.1.0
- **Notas:** Mantener compatibilidad con v2.0.x y feature flags por tenant/país.

---

## [Limpieza de Código] - 23 Noviembre 2025

### 🧹 Limpieza General
- ✅ Eliminados scripts de debug temporales (`main_debug.py`, `check_empleado.py`)
- ✅ Consolidados 15+ archivos markdown redundantes en `docs/historico_correcciones/`
- ✅ Eliminado código de prueba en módulos utils (`validators.py`, `importador_excel.py`, `logger.py`)
- ✅ Convertidos prints DEBUG a logger en `registro_animal.py`
- ✅ Creado script automatizado de limpieza (`scripts/utilities/limpiar_proyecto.py`)
- ✅ Generado informe completo de análisis (`INFORME_LIMPIEZA_CODIGO.md`)

### 📊 Estado del Proyecto
- **Errores de compilación:** 0 ✅
- **Archivos Python:** 212
- **Estado:** SALUDABLE

---

## [Optimización de Espacios] - 22 Noviembre 2025

### 🎨 Mejoras de UX/UI
- ✅ Eliminada barra de estado inferior (26px recuperados)
- ✅ Reducido padding vertical (pady 20/15 → 5) en TODOS los módulos
- ✅ Optimizado sidebar (230px → 200px)
- ✅ Ventana principal ampliada (1280x750 → 1400x820)
- ✅ Maximización automática en Windows con `state('zoomed')`

### Módulos Optimizados (11 total)
- ventas (4 cambios)
- reproduccion (2 cambios)
- potreros (2 cambios)
- tratamientos (3 cambios)
- nomina (3 cambios)
- reportes (7 cambios)
- salud (1 cambio)
- dashboard (1 cambio)
- ajustes (2 cambios)
- herramientas (1 cambio)
- animales (múltiples)

---

## [Sistema de Plantillas] - 23 Noviembre 2025

### 📦 Nueva Funcionalidad
- ✅ Expandidas definiciones de plantillas de 7 → 23 en `modules/utils/plantillas_carga.py`
- ✅ Agregado botón "Selección múltiple" en módulo Ajustes
- ✅ Implementado diálogo con checkboxes para generar plantillas específicas
- ✅ Corregido error Unicode (✓/✅ → ASCII) en `generar_plantillas_completas.py`
- ✅ Mantiene compatibilidad con generación individual y masiva

### Plantillas Disponibles (23)
Configuración: animales, fincas, sectores, lotes, razas, potreros, empleados, proveedores, etc.
Operaciones: tratamientos, servicios, ventas, diagnósticos, producción leche, pesajes

---

## [Correcciones de Base de Datos] - Noviembre 2025

### 🔧 Foreign Keys
- ✅ Validación de `animal_id` antes de INSERT en reproducción, salud, tratamientos, ventas
- ✅ Manejo mejorado de formatos "ID-CODIGO NOMBRE" en combos
- ✅ Corrección de queries `rowid` en lugar de `id` en nómina
- ✅ Migración 009: Consolidación final de FKs hacia `finca` con ON DELETE SET NULL y limpieza de referencias a tablas temporales

### 🗄️ Esquema
- ✅ Migración 005: Agregado campo `finca_id` a sectores y lotes
- ✅ Normalización de datos en módulos configuración
- ✅ Verificación de integridad referencial
 - ✅ Reconstrucción idempotente de `animal` para eliminar referencias a `lote_old` y `potrero_old`
 - ✅ Eliminación segura de tablas residuales `*_old` tras migraciones parciales
 - ✅ Script consolidado `009_consolidate_fk_cleanup.py` asegura consistencia futura

---

## [Correcciones de Errores] - Noviembre 2025

### 🐛 Bugs Corregidos
- ✅ Variable `form_frame` no definida en `tratamientos_main.py` → reemplazada por `campos_frame`
- ✅ Display 'sqlite3.row' en historial insumos → conversión correcta a tuplas
- ✅ Error "no such column:id" en nómina → uso de `rowid`
- ✅ UnicodeEncodeError cp1252 en generación plantillas → eliminados caracteres Unicode

### 🔍 Validaciones
- ✅ Sistema de validación robusto en `modules/utils/validators.py`
- ✅ Validación de aretes, pesos, fechas
- ✅ Modo sin BD para desarrollo/testing

---

## [Características Principales] - Estado Actual

### ✨ Funcionalidades Core
1. **Dashboard** - Métricas en tiempo real, alertas, eventos recientes
2. **Animales** - Registro completo, inventario, reubicaciones, fichas
3. **Reproducción** - Servicios, gestaciones, partos, cálculo automático
4. **Salud** - Diagnósticos, tratamientos, historial médico
5. **Producción** - Leche, pesajes, condición corporal
6. **Ventas** - Registro de ventas, motivos, destinos
7. **Nómina** - Empleados, cálculo de salarios, liquidaciones
8. **Potreros** - Gestión de pasturas, capacidad, rotación
9. **Insumos** - Inventario, movimientos, stock mínimo
10. **Herramientas** - Control de equipos y mantenimiento
11. **Reportes** - Exportación Excel/PDF, análisis
12. **Configuración** - Fincas, razas, sectores, lotes, etc.

### 🎯 Características Técnicas
- **Base de datos:** SQLite con migraciones automáticas
- **UI Framework:** CustomTkinter (look moderno)
- **Logging:** Sistema robusto con rotación
- **Importación:** Excel masiva con validaciones
- **Exportación:** CSV, Excel, PDF
- **Tour Interactivo:** 12 pasos guiados
- **Manual PDF:** Generación automática
- **Instalador:** Inno Setup + PyInstaller

---

## [Próximas Mejoras Sugeridas]

### 🚀 Roadmap
- [ ] Refactorizar duplicación de código en módulos similares
- [ ] Implementar sistema de backup automático programado
- [ ] Agregar gráficas de producción (matplotlib/plotly)
- [ ] Modo offline completo con sincronización
- [ ] API REST para integración externa
- [ ] App móvil companion (React Native/Flutter)
- [ ] Sistema de permisos/usuarios múltiples
- [ ] Integración con básculas/lectores RFID

---

## Versión Actual
**Versión:** 1.0 (Estable)  
**Última actualización:** 23 Noviembre 2025  
**Estado:** ✅ Producción

---

## Notas de Desarrollo

### Estructura del Proyecto
```
FincaFacil/
├── main.py                 # Punto de entrada principal
├── database/               # Capa de datos SQLite
├── modules/                # Módulos funcionales
│   ├── dashboard/
│   ├── animales/
│   ├── reproduccion/
│   ├── salud/
│   ├── ventas/
│   ├── nomina/
│   ├── potreros/
│   ├── insumos/
│   ├── herramientas/
│   ├── reportes/
│   ├── configuracion/
│   ├── ajustes/
│   └── utils/              # Utilidades compartidas
├── scripts/                # Scripts de mantenimiento
│   ├── migrations/         # Migraciones de BD
│   └── utilities/          # Utilidades de desarrollo
├── tests/                  # Tests unitarios
├── docs/                   # Documentación
├── assets/                 # Recursos (iconos, logos)
└── installer/              # Archivos de instalador
```

### Convenciones de Código
- **Nombres:** snake_case para funciones/variables, PascalCase para clases
- **Docstrings:** Usar formato Google style
- **Logging:** Preferir logger sobre prints
- **Excepciones:** Capturar específicas, no genéricas
- **Comentarios:** Explicar el "por qué", no el "qué"

---

*Documento vivo - se actualiza con cada cambio significativo*# CHANGELOG - FincaFácil

Registro consolidado de cambios, mejoras y correcciones del sistema.

---

## [Limpieza de Código] - 23 Noviembre 2025

### 🧹 Limpieza General
- ✅ Eliminados scripts de debug temporales (`main_debug.py`, `check_empleado.py`)
- ✅ Consolidados 15+ archivos markdown redundantes en `docs/historico_correcciones/`
- ✅ Eliminado código de prueba en módulos utils (`validators.py`, `importador_excel.py`, `logger.py`)
- ✅ Convertidos prints DEBUG a logger en `registro_animal.py`
- ✅ Creado script automatizado de limpieza (`scripts/utilities/limpiar_proyecto.py`)
- ✅ Generado informe completo de análisis (`INFORME_LIMPIEZA_CODIGO.md`)

### 📊 Estado del Proyecto
- **Errores de compilación:** 0 ✅
- **Archivos Python:** 212
- **Estado:** SALUDABLE

---

## [Optimización de Espacios] - 22 Noviembre 2025

### 🎨 Mejoras de UX/UI
- ✅ Eliminada barra de estado inferior (26px recuperados)
- ✅ Reducido padding vertical (pady 20/15 → 5) en TODOS los módulos
- ✅ Optimizado sidebar (230px → 200px)
- ✅ Ventana principal ampliada (1280x750 → 1400x820)
- ✅ Maximización automática en Windows con `state('zoomed')`

### Módulos Optimizados (11 total)
- ventas (4 cambios)
- reproduccion (2 cambios)
- potreros (2 cambios)
- tratamientos (3 cambios)
- nomina (3 cambios)
- reportes (7 cambios)
- salud (1 cambio)
- dashboard (1 cambio)
- ajustes (2 cambios)
- herramientas (1 cambio)
- animales (múltiples)

---

## [Sistema de Plantillas] - 23 Noviembre 2025

### 📦 Nueva Funcionalidad
- ✅ Expandidas definiciones de plantillas de 7 → 23 en `modules/utils/plantillas_carga.py`
- ✅ Agregado botón "Selección múltiple" en módulo Ajustes
- ✅ Implementado diálogo con checkboxes para generar plantillas específicas
- ✅ Corregido error Unicode (✓/✅ → ASCII) en `generar_plantillas_completas.py`
- ✅ Mantiene compatibilidad con generación individual y masiva

### Plantillas Disponibles (23)
Configuración: animales, fincas, sectores, lotes, razas, potreros, empleados, proveedores, etc.
Operaciones: tratamientos, servicios, ventas, diagnósticos, producción leche, pesajes

---

## [Correcciones de Base de Datos] - Noviembre 2025

### 🔧 Foreign Keys
- ✅ Validación de `animal_id` antes de INSERT en reproducción, salud, tratamientos, ventas
- ✅ Manejo mejorado de formatos "ID-CODIGO NOMBRE" en combos
- ✅ Corrección de queries `rowid` en lugar de `id` en nómina
- ✅ Migración 009: Consolidación final de FKs hacia `finca` con ON DELETE SET NULL y limpieza de referencias a tablas temporales

### 🗄️ Esquema
- ✅ Migración 005: Agregado campo `finca_id` a sectores y lotes
- ✅ Normalización de datos en módulos configuración
- ✅ Verificación de integridad referencial
 - ✅ Reconstrucción idempotente de `animal` para eliminar referencias a `lote_old` y `potrero_old`
 - ✅ Eliminación segura de tablas residuales `*_old` tras migraciones parciales
 - ✅ Script consolidado `009_consolidate_fk_cleanup.py` asegura consistencia futura

---

## [Correcciones de Errores] - Noviembre 2025

### 🐛 Bugs Corregidos
- ✅ Variable `form_frame` no definida en `tratamientos_main.py` → reemplazada por `campos_frame`
- ✅ Display 'sqlite3.row' en historial insumos → conversión correcta a tuplas
- ✅ Error "no such column:id" en nómina → uso de `rowid`
- ✅ UnicodeEncodeError cp1252 en generación plantillas → eliminados caracteres Unicode

### 🔍 Validaciones
- ✅ Sistema de validación robusto en `modules/utils/validators.py`
- ✅ Validación de aretes, pesos, fechas
- ✅ Modo sin BD para desarrollo/testing

---

## [Características Principales] - Estado Actual

### ✨ Funcionalidades Core
1. **Dashboard** - Métricas en tiempo real, alertas, eventos recientes
2. **Animales** - Registro completo, inventario, reubicaciones, fichas
3. **Reproducción** - Servicios, gestaciones, partos, cálculo automático
4. **Salud** - Diagnósticos, tratamientos, historial médico
5. **Producción** - Leche, pesajes, condición corporal
6. **Ventas** - Registro de ventas, motivos, destinos
7. **Nómina** - Empleados, cálculo de salarios, liquidaciones
8. **Potreros** - Gestión de pasturas, capacidad, rotación
9. **Insumos** - Inventario, movimientos, stock mínimo
10. **Herramientas** - Control de equipos y mantenimiento
11. **Reportes** - Exportación Excel/PDF, análisis
12. **Configuración** - Fincas, razas, sectores, lotes, etc.

### 🎯 Características Técnicas
- **Base de datos:** SQLite con migraciones automáticas
- **UI Framework:** CustomTkinter (look moderno)
- **Logging:** Sistema robusto con rotación
- **Importación:** Excel masiva con validaciones
- **Exportación:** CSV, Excel, PDF
- **Tour Interactivo:** 12 pasos guiados
- **Manual PDF:** Generación automática
- **Instalador:** Inno Setup + PyInstaller

---

## [Próximas Mejoras Sugeridas]

### 🚀 Roadmap
- [ ] Refactorizar duplicación de código en módulos similares
- [ ] Implementar sistema de backup automático programado
- [ ] Agregar gráficas de producción (matplotlib/plotly)
- [ ] Modo offline completo con sincronización
- [ ] API REST para integración externa
- [ ] App móvil companion (React Native/Flutter)
- [ ] Sistema de permisos/usuarios múltiples
- [ ] Integración con básculas/lectores RFID

---

## Versión Actual
**Versión:** 1.0 (Estable)  
**Última actualización:** 23 Noviembre 2025  
**Estado:** ✅ Producción

---

## Notas de Desarrollo

### Estructura del Proyecto
```
FincaFacil/
├── main.py                 # Punto de entrada principal
├── database/               # Capa de datos SQLite
├── modules/                # Módulos funcionales
│   ├── dashboard/
│   ├── animales/
│   ├── reproduccion/
│   ├── salud/
│   ├── ventas/
│   ├── nomina/
│   ├── potreros/
│   ├── insumos/
│   ├── herramientas/
│   ├── reportes/
│   ├── configuracion/
│   ├── ajustes/
│   └── utils/              # Utilidades compartidas
├── scripts/                # Scripts de mantenimiento
│   ├── migrations/         # Migraciones de BD
│   └── utilities/          # Utilidades de desarrollo
├── tests/                  # Tests unitarios
├── docs/                   # Documentación
├── assets/                 # Recursos (iconos, logos)
└── installer/              # Archivos de instalador
```

### Convenciones de Código
- **Nombres:** snake_case para funciones/variables, PascalCase para clases
- **Docstrings:** Usar formato Google style
- **Logging:** Preferir logger sobre prints
- **Excepciones:** Capturar específicas, no genéricas
- **Comentarios:** Explicar el "por qué", no el "qué"

---

*Documento vivo - se actualiza con cada cambio significativo*
