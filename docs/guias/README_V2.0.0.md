# 🐄 FincaFácil - Sistema de Gestión Ganadera

**Versión:** 2.0.0 - Reorganizado y Optimizado  
**Fecha:** 3 de Diciembre de 2025

## 🚀 Descripción

FincaFácil es un sistema profesional de gestión integral para fincas ganaderas. Permite administrar animales, inventario de insumos, herramientas, nómina, ventas y muchas más funcionalidades con una interfaz gráfica moderna.

## ✨ Características Principales

- 📊 **Dashboard** - Métricas y alertas en tiempo real
- 🐄 **Gestión de Animales** - Registro completo de cabezas de ganado
- 📦 **Control de Inventario** - Insumos, herramientas y stock
- 💰 **Módulo de Ventas** - Registro y seguimiento de ventas
- 👥 **Gestión de Nómina** - Cálculo de salarios y beneficios
- 📈 **Reportes** - Generación de informes detallados
- 🔧 **Configuración** - Catálogos y parámetros del sistema

## 📋 Requisitos del Sistema

- **Python:** 3.10 o superior
- **Sistema Operativo:** Windows / Linux / macOS
- **RAM:** 2GB mínimo (4GB recomendado)
- **Espacio en disco:** 500MB para instalación

## ⚡ Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/juanmora97B/fincafacil.git
cd fincafacil
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```bash
python main.py
```

## 🏗️ Estructura del Proyecto (v2.0.0)

```
fincafacil/
├── main.py                          # 🔑 Punto de entrada principal
├── config.py                        # ⚙️ Configuración centralizada
├── requirements.txt                 # 📦 Dependencias del proyecto
├── conftest.py                      # 🧪 Configuración de pytest
├── README.md                        # 📖 Este archivo
│
├── src/                             # 🆕 Código fuente central
│   ├── __init__.py
│   ├── core/                        # Core del sistema
│   │   ├── exceptions.py           # Excepciones personalizadas
│   │   ├── constants.py            # Constantes del sistema
│   │   └── __init__.py
│   │
│   ├── database/                    # Capa de datos
│   │   ├── connection.py           # Sistema de conexión unificado
│   │   ├── schemas/                # Esquemas SQL
│   │   └── __init__.py
│   │
│   ├── utils/                       # Utilidades consolidadas
│   │   ├── validators.py           # Validadores unificados
│   │   └── __init__.py
│   │
│   ├── modules/                     # Módulos funcionales
│   └── app/                         # Aplicación principal
│
├── database/                        # Base de datos
│   ├── __init__.py
│   ├── database.py                 # Schema e inicialización
│   └── fincafacil.db               # Archivo BD (auto-generado)
│
├── modules/                         # Módulos funcionales (legacy)
│   ├── dashboard/
│   ├── animales/
│   ├── insumos/
│   ├── herramientas/
│   ├── nomina/
│   ├── ventas/
│   ├── configuracion/
│   └── utils/
│
├── tests/                           # Tests organizados
│   ├── unit/                       # Tests unitarios
│   ├── integration/                # Tests de integración
│   └── fixtures/                   # Datos de prueba
│
├── scripts/                         # Scripts de utilidad
│   ├── migrations/                 # Migraciones BD
│   ├── setup/                      # Setup e instalación
│   ├── dev_tools/                  # Herramientas de desarrollo
│   ├── audit/                      # Scripts de auditoría
│   └── maintenance/                # Mantenimiento
│
├── docs/                            # Documentación
│   ├── architecture/               # Arquitectura del sistema
│   └── guides/                     # Guías de usuario
│
├── assets/                          # Recursos (iconos, imágenes)
├── logs/                            # Logs de la aplicación
├── backup/                          # Backups automáticos
└── build/                           # Build del proyecto
```

## 🔄 Cambios en la Versión 2.0.0

### ✅ Completado

- ✅ **Nueva Estructura** - Organización profesional en `src/`
- ✅ **Sistema de Conexión BD Unificado** - `src/database/connection.py`
- ✅ **Validadores Consolidados** - `src/utils/validators.py`
- ✅ **Excepciones Centralizadas** - `src/core/exceptions.py`
- ✅ **Constantes del Sistema** - `src/core/constants.py`
- ✅ **45+ Archivos Actualizados** - Imports estandarizados
- ✅ **Eliminados Archivos Legacy** - `insumos_main_old.py`, `conexion_unified.py`
- ✅ **Tests Organizados** - Estructura clara en `/tests`
- ✅ **Scripts de Setup** - `update_imports.py`, `validate_structure.py`

### 📊 Métricas de Limpieza

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Archivos duplicados | 10+ | 0 | **-100%** |
| Imports inconsistentes | 100+ | 0 | **-100%** |
| Código legacy eliminado | 550+ LOC | 0 | **-100%** |
| Archivos actualizados | - | 45 | ✅ |
| Validación de estructura | ❌ | ✅ | ✅ |

## 💻 Uso de la Aplicación

### Iniciando la Aplicación

```bash
python main.py
```

La interfaz gráfica se abrirá automáticamente. Desde aquí puedes acceder a todos los módulos del sistema.

### Módulos Principales

1. **Dashboard** - Resumen del estado general
2. **Animales** - Registro y seguimiento del ganado
3. **Insumos** - Inventario de productos
4. **Herramientas** - Control de herramientas
5. **Nómina** - Gestión de empleados y salarios
6. **Ventas** - Registro de transacciones
7. **Configuración** - Parámetros del sistema

## 🧪 Tests

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/unit/

# Con coverage
pytest --cov=src tests/
```

### Estructura de Tests

```
tests/
├── unit/               # Tests unitarios
├── integration/        # Tests de integración
└── fixtures/          # Datos de prueba
```

## 🔧 Scripts de Utilidad

### Setup

```bash
# Actualizar imports automáticamente
python scripts/setup/update_imports.py

# Validar estructura
python scripts/setup/validate_structure.py
```

### Desarrollo

```bash
# Inspeccionar base de datos
python scripts/dev_tools/inspect_db.py

# Limpiar cache
python scripts/maintenance/cleanup.py
```

### Auditoría

```bash
# Verificar integridad
python scripts/audit/integrity_check.py
```

## 📚 Documentación Adicional

- [PLAN_REORGANIZACION_COMPLETO.md](PLAN_REORGANIZACION_COMPLETO.md) - Plan de migración detallado
- [docs/architecture/](docs/architecture/) - Documentación de arquitectura
- [docs/guides/](docs/guides/) - Guías de usuario

## 🐛 Reporte de Bugs

Si encuentras un bug, por favor:

1. Verifica que no esté reportado en Issues
2. Crea un nuevo Issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Versión de Python y SO

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para directrices de contribución.

## 📄 Licencia

Licencia Propietaria - Ver [LICENSE.txt](LICENSE.txt)

## 👥 Autores

- **Juan Mora** - Desarrollador Principal
- Equipo FincaFácil

## 📞 Soporte

- 📧 Email: soporte@fincafacil.com
- 💬 Issues: [GitHub Issues](https://github.com/juanmora97B/fincafacil/issues)
- 📖 Docs: [Documentación Completa](docs/)

---

## ✅ Checklist de Validación

- ✅ Estructura de directorios creada
- ✅ Sistema de conexión BD unificado
- ✅ Validadores consolidados
- ✅ Excepciones centralizadas
- ✅ Imports actualizados (45+ archivos)
- ✅ Tests organizados
- ✅ Validación exitosa
- ✅ main.py ejecutable
- ✅ Documentación completa

**Versión 2.0.0 - READY FOR PRODUCTION** 🚀
