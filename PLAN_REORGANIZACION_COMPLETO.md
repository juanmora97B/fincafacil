# 📋 PLAN DE REORGANIZACIÓN COMPLETO - FINCAFACIL

**Fecha:** 3 de Diciembre de 2025  
**Objetivo:** Reestructurar completamente el proyecto eliminando código muerto, consolidando duplicados y creando una arquitectura profesional escalable.

---

## 🎯 RESUMEN EJECUTIVO

### Estado Actual:
- **244 archivos Python** en el proyecto
- **65+ scripts sueltos** en la raíz del proyecto
- **Código duplicado** en validaciones, utilidades y conexiones BD
- **Imports inconsistentes** (database.database vs database.conexion_unified)
- **Migraciones desordenadas** (numeración duplicada: 008, 009, 010)
- **Archivos legacy** (_old, _v1, _backup, etc.)

### Objetivo Final:
- Estructura profesional MVC/modular clara
- **Reducir 30-40%** el código actual eliminando duplicados
- Imports relativos consistentes
- Zero archivos en raíz (excepto main.py, config.py, requirements.txt)
- Documentación clara y actualizada

---

## 📊 FASE 1: AUDITORÍA Y ANÁLISIS (COMPLETADO) ✅

### Hallazgos Críticos:

#### 1. **Scripts en la Raíz (65+ archivos para reorganizar)**

**Verificación (27 archivos):**
```
verificar_estructura_insumos.py
verificar_insumos_final.py
verificar_fotos_herramientas.py
verificar_estado_migraciones.py
verificar_esquema_insumo.py
verificar_esquema_animal.py
verificar_eliminacion_movimientos.py
verificar_datos_ui.py
verificar_correcciones_insumos.py
verificar_y_corregir_mant.py
verificar_vendedor_cc.py
verificar_triggers_fks.py
verificar_tablas_bd.py
verificar_tablas.py
verificar_modulo_insumos.py
... (12 más)
```
**ACCIÓN:** Mover a `scripts/verificacion/` o ELIMINAR si ya no son necesarios

**Testing (15 archivos):**
```
test_state_parameter.py
test_readonly_combo.py
test_modulo_insumos.py
test_inventario_v2.py
test_insumos_fix.py
test_import_full.py
test_importacion_inventario.py
test_import.py
test_combobox_ui.py
test_case_insensitive.py
test_29_razas.py
... (4 más)
```
**ACCIÓN:** Mover a `tests/integration/` o `tests/ui/`

**Validación (3 archivos):**
```
validar_modulo_animales.py
validaciones_tipos_datos.py
validar_sistema.py (scripts/utilities/)
```
**ACCIÓN:** Consolidar en un solo módulo de validación

**Corrección/Migración (10 archivos):**
```
aplicar_correcciones_mapeo.py
aplicar_migracion_017_direct.py
aplicar_migracion_018_direct.py
aplicar_migracion_019_direct.py
aplicar_migracion_020_direct.py
completar_migraciones.py
corregir_animales_sin_finca.py
corregir_fk_mantenimiento.py
normalizar_y_migrar.py
migrar_inventario_v2.py
```
**ACCIÓN:** Mover a `scripts/migrations/manual/` o ELIMINAR después de confirmar que ya se aplicaron

**Auditoría/Análisis (5 archivos):**
```
auditar_import_animales.py
auditoria_mapeos_insumos.py
analizar_estados_herramientas.py
investigacion_completa.py
debug_animales_load.py
```
**ACCIÓN:** Mover a `scripts/audit/` o ELIMINAR

**Utilidades Generales (8 archivos):**
```
listar_catalogos.py
listar_tablas.py
listar_tablas_completo.py
limpiar_animales.py
mostrar_config.py
mostrar_configuracion_fincas.py
generar_modulo_insumos.py
ejemplo_case_insensitive.py
```
**ACCIÓN:** Consolidar y mover a ubicaciones apropiadas

**Datos de Prueba:**
```
probar_registro_mantenimiento.py
ver_razas_bd.py
```
**ACCIÓN:** Mover a `tests/manual/` o ELIMINAR

#### 2. **Archivos Duplicados/Legacy**

```python
# Insumos old
modules/insumos/insumos_main_old.py  # 550 líneas - ELIMINAR
modules/insumos/insumos_main.py      # MANTENER

# Database duplicado
database/database.py                  # MANTENER (principal)
database/conexion_unified.py          # ¿Eliminar o fusionar?

# Validaciones duplicadas
modules/utils/validaciones.py         # Consolidar
modules/utils/validators.py           # Consolidar
```

#### 3. **Migraciones con Numeración Duplicada**

```
008_allow_delete_finca.py
008B_complete_finca_fk_fix.py
008C_fix_sector_fk.py
008D_fix_lote_fk.py
009_consolidate_fk_cleanup.py
009_add_insumo_fields.py
010_fix_movimiento_insumo_pk.py
010_add_finca_to_vendor_origin.py
```
**ACCIÓN:** Renumerar correctamente (008, 009, 010, 011, 012, ...)

#### 4. **Imports Inconsistentes**

**Problema 1: Conexión a BD**
```python
# 50+ archivos usan:
from database.database import get_db_connection

# 50+ archivos usan:
from database import db
```
**SOLUCIÓN:** Estandarizar a `from database import get_connection`

**Problema 2: Logger duplicado**
```python
# Algunos archivos:
from modules.utils.logger import setup_logger, get_logger

# Otros:
import logging
logger = logging.getLogger(__name__)
```
**SOLUCIÓN:** Usar sistema de logging centralizado

---

## 🏗️ FASE 2: NUEVA ESTRUCTURA PROPUESTA

```
fincafacil/
│
├── main.py                          # ✅ Punto de entrada único
├── config.py                        # ✅ Configuración centralizada
├── requirements.txt                 # ✅ Dependencias
├── README.md                        # 📝 Documentación principal
├── .env.example                     # 🆕 Variables de entorno
│
├── src/                             # 🆕 Código fuente principal
│   ├── __init__.py
│   │
│   ├── app/                         # 🆕 Aplicación principal
│   │   ├── __init__.py
│   │   └── main_window.py          # GUI principal
│   │
│   ├── modules/                     # ✅ Módulos funcionales (refactorizado)
│   │   ├── animales/
│   │   │   ├── __init__.py
│   │   │   ├── registro.py
│   │   │   ├── inventario.py
│   │   │   ├── reubicacion.py
│   │   │   ├── modals/
│   │   │   └── services/            # 🆕 Lógica de negocio
│   │   │
│   │   ├── insumos/
│   │   ├── herramientas/
│   │   ├── nomina/
│   │   ├── ventas/
│   │   ├── reportes/
│   │   ├── dashboard/
│   │   └── configuracion/
│   │
│   ├── database/                    # ✅ Capa de datos
│   │   ├── __init__.py
│   │   ├── connection.py           # 🆕 Conexión unificada
│   │   ├── models.py               # 🆕 Modelos de datos
│   │   ├── migrations/             # ✅ Migraciones renumeradas
│   │   │   ├── __init__.py
│   │   │   ├── 001_extended_schema.py
│   │   │   ├── 002_normalize_animal.py
│   │   │   └── ... (renumeradas correctamente)
│   │   └── schema/                 # 🆕 Esquemas SQL
│   │
│   ├── utils/                      # ✅ Utilidades (consolidadas)
│   │   ├── __init__.py
│   │   ├── logger.py              # ✅ Sistema de logging
│   │   ├── validators.py          # 🔄 Consolidado
│   │   ├── ui_components.py       # 🆕 Componentes UI reutilizables
│   │   ├── date_utils.py
│   │   ├── file_utils.py
│   │   └── db_helpers.py
│   │
│   └── core/                       # 🆕 Funcionalidades core
│       ├── __init__.py
│       ├── constants.py
│       ├── exceptions.py
│       └── settings.py
│
├── tests/                          # ✅ Tests organizados
│   ├── __init__.py
│   ├── unit/                       # 🆕 Tests unitarios
│   ├── integration/                # 🆕 Tests de integración
│   ├── ui/                         # 🆕 Tests de interfaz
│   └── fixtures/                   # 🆕 Datos de prueba
│
├── scripts/                        # ✅ Scripts de utilidad
│   ├── migrations/                 # ✅ Ya existe
│   │   └── manual/                 # 🆕 Migraciones manuales
│   ├── setup/                      # 🆕 Instalación/configuración
│   ├── maintenance/                # 🆕 Mantenimiento
│   ├── audit/                      # 🆕 Auditoría
│   └── dev_tools/                  # 🆕 Herramientas desarrollo
│
├── data/                           # ✅ Datos
│   ├── templates/                  # Plantillas Excel
│   └── samples/                    # Datos de ejemplo
│
├── docs/                           # ✅ Documentación
│   ├── architecture/               # 🆕 Arquitectura
│   ├── api/                        # 🆕 API interna
│   ├── user_guides/                # 🆕 Guías usuario
│   └── changelog/                  # 🆕 Cambios por versión
│
├── assets/                         # ✅ Recursos
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── logs/                           # ✅ Logs de aplicación
├── backup/                         # ✅ Backups BD
└── build/                          # ✅ Compilación
```

---

## 🗑️ FASE 3: LIMPIEZA MASIVA

### 3.1 Archivos a ELIMINAR (después de validar)

```python
# === LEGACY/OLD ===
modules/insumos/insumos_main_old.py                    # 550 líneas muertas
database/conexion_unified.py                           # Duplicado

# === SCRIPTS YA APLICADOS (verificar primero) ===
aplicar_migracion_017_direct.py
aplicar_migracion_018_direct.py
aplicar_migracion_019_direct.py
aplicar_migracion_020_direct.py
completar_migraciones.py
normalizar_y_migrar.py
migrar_inventario_v2.py

# === DEBUGGING TEMPORAL ===
debug_animales_load.py
ejemplo_case_insensitive.py
investigacion_completa.py

# === VERIFICACIÓN REDUNDANTE (después de validar que funcionan) ===
verificar_estructura_insumos.py
verificar_insumos_final.py
verificar_correcciones_insumos.py
verificar_eliminacion_movimientos.py
# ... (revisar los 27 archivos de verificación uno por uno)
```

### 3.2 Archivos a CONSOLIDAR

```python
# === VALIDADORES ===
# Fusionar:
modules/utils/validaciones.py
modules/utils/validators.py
# En: src/utils/validators.py (único archivo)

# === CONFIGURACIÓN ===
# Fusionar:
mostrar_config.py
mostrar_configuracion_fincas.py
# En: scripts/dev_tools/show_config.py

# === LISTAR DATOS ===
# Fusionar:
listar_catalogos.py
listar_tablas.py
listar_tablas_completo.py
# En: scripts/dev_tools/inspect_db.py (ya existe similar)
```

### 3.3 Archivos a MOVER

```bash
# Tests
test_*.py (raíz) → tests/integration/

# Verificación
verificar_*.py → scripts/audit/ o scripts/maintenance/

# Utilidades
scripts/utilities/*.py → scripts/dev_tools/ o scripts/maintenance/

# Auditoría
auditar_*.py → scripts/audit/
auditoria_*.py → scripts/audit/
```

---

## 🔧 FASE 4: REFACTORIZACIÓN DE CÓDIGO

### 4.1 Estandarizar Imports

**ANTES (inconsistente):**
```python
# Archivo 1:
from database.database import get_db_connection
with get_db_connection() as conn:
    ...

# Archivo 2:
from database import db
with db.get_connection() as conn:
    ...

# Archivo 3:
import sqlite3
conn = sqlite3.connect("database/fincafacil.db")
```

**DESPUÉS (estandarizado):**
```python
# Todos los archivos:
from database import get_connection

with get_connection() as conn:
    cursor = conn.cursor()
    ...
```

### 4.2 Consolidar Validadores

**Crear: `src/utils/validators.py`**
```python
"""
Validadores centralizados para FincaFacil
"""
from typing import Optional, Any
from datetime import datetime

class ValidationError(Exception):
    """Error de validación personalizado"""
    pass

class DataValidator:
    """Validador centralizado para datos del sistema"""
    
    @staticmethod
    def validate_peso(peso: float, min_val: float = 0, max_val: float = 2000) -> bool:
        """Valida peso de animales"""
        if not isinstance(peso, (int, float)):
            raise ValidationError("El peso debe ser numérico")
        if not (min_val <= peso <= max_val):
            raise ValidationError(f"Peso fuera de rango ({min_val}-{max_val} kg)")
        return True
    
    @staticmethod
    def validate_fecha(fecha: str) -> bool:
        """Valida formato de fecha"""
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
            return True
        except ValueError:
            raise ValidationError("Formato de fecha inválido (use YYYY-MM-DD)")
    
    @staticmethod
    def validate_codigo_unico(codigo: str, tabla: str, conn) -> bool:
        """Valida que un código sea único en una tabla"""
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE codigo = ?", (codigo,))
        if cursor.fetchone()[0] > 0:
            raise ValidationError(f"El código '{codigo}' ya existe")
        return True

# Funciones legacy para compatibilidad (deprecadas)
def validar_peso_nacimiento(peso):
    return DataValidator.validate_peso(peso, 15, 60)

def validar_fecha_no_futura(fecha):
    return DataValidator.validate_fecha(fecha)
```

### 4.3 Crear Sistema de Conexión Unificado

**Crear: `src/database/connection.py`**
```python
"""
Sistema de conexión unificado a base de datos
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Configuración
BASE_DIR = Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "database" / "fincafacil.db"

@contextmanager
def get_connection(db_path: Optional[str] = None):
    """
    Context manager para conexiones a la base de datos
    
    Usage:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
    path = db_path or DB_PATH
    conn = None
    try:
        # Asegurar que existe el directorio
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        
        # Conectar con configuración optimizada
        conn = sqlite3.connect(path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        
        logger.debug(f"Conexión establecida a {path}")
        yield conn
        
    except sqlite3.Error as e:
        logger.error(f"Error de base de datos: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Conexión cerrada")

class DatabaseManager:
    """Manager de base de datos para operaciones comunes"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
    
    def execute_query(self, query: str, params: tuple = ()):
        """Ejecuta una query y retorna resultados"""
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: list):
        """Ejecuta múltiples inserts/updates"""
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

# Instancia global
db = DatabaseManager()
```

### 4.4 Renumerar Migraciones

```python
# scripts/migrations/ - ANTES:
001_extended_schema.py
002_normalize_animal.py
003_herramientas_insumos.py
004_add_servicio_table.py
005_add_finca_to_sector_lote.py
006_allow_delete_raza.py
007_add_destino_venta_fields.py
008_allow_delete_finca.py
008B_complete_finca_fk_fix.py        # ❌ DUPLICADO
008C_fix_sector_fk.py                # ❌ DUPLICADO
008D_fix_lote_fk.py                  # ❌ DUPLICADO
009_consolidate_fk_cleanup.py
009_add_insumo_fields.py             # ❌ DUPLICADO
010_fix_movimiento_insumo_pk.py
010_add_finca_to_vendor_origin.py   # ❌ DUPLICADO
011_normalize_estado_values.py
...

# DESPUÉS (renumeradas):
001_extended_schema.py
002_normalize_animal.py
003_herramientas_insumos.py
004_add_servicio_table.py
005_add_finca_to_sector_lote.py
006_allow_delete_raza.py
007_add_destino_venta_fields.py
008_allow_delete_finca.py
009_complete_finca_fk_fix.py         # ✅ Renombrado
010_fix_sector_fk.py                 # ✅ Renombrado
011_fix_lote_fk.py                   # ✅ Renombrado
012_consolidate_fk_cleanup.py        # ✅ Renumerado
013_add_insumo_fields.py             # ✅ Renumerado
014_fix_movimiento_insumo_pk.py      # ✅ Renumerado
015_add_finca_to_vendor_origin.py   # ✅ Renumerado
016_normalize_estado_values.py       # ✅ Renumerado
017_add_finca_to_empleado.py
018_drop_grupo_table.py
019_add_foto_trabajador_herramienta.py
020_add_stock_columns_herramienta.py
021_add_estado_mantenimiento.py
022_add_revision_estado.py
023_fix_mantenimiento_fk.py
024_add_insumo_fields.py
025_create_mantenimiento_insumo.py
```

---

## 📝 FASE 5: ACTUALIZAR IMPORTS

### 5.1 Script de Actualización Automática

**Crear: `scripts/setup/update_imports.py`**
```python
"""
Script para actualizar imports a la nueva estructura
"""
import re
from pathlib import Path

REPLACEMENTS = {
    # Database
    r'from database\.database import get_db_connection': 'from database import get_connection',
    r'from database import db': 'from database import get_connection',
    
    # Utils
    r'from modules\.utils\.validaciones import': 'from utils.validators import',
    r'from modules\.utils\.validators import': 'from utils.validators import',
    
    # Logger
    r'from modules\.utils\.logger import setup_logger, get_logger': 'from utils.logger import setup_logger',
}

def update_file(filepath: Path):
    """Actualiza imports en un archivo"""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        for pattern, replacement in REPLACEMENTS.items():
            content = re.sub(pattern, replacement, content)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            print(f"✅ Actualizado: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error en {filepath}: {e}")
        return False

def main():
    base = Path(__file__).parent.parent.parent
    updated = 0
    
    for py_file in base.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        if update_file(py_file):
            updated += 1
    
    print(f"\n🎉 Actualizados {updated} archivos")

if __name__ == "__main__":
    main()
```

---

## ✅ FASE 6: VALIDACIÓN

### 6.1 Checklist de Validación

```markdown
## Validación Pre-Reorganización
- [ ] Backup completo de la base de datos
- [ ] Backup completo del código actual
- [ ] Git commit de estado actual
- [ ] Tests actuales pasando (si existen)

## Validación Durante Reorganización
- [ ] Verificar imports después de cada movimiento
- [ ] Ejecutar tests después de cada cambio mayor
- [ ] Validar que main.py siga funcionando

## Validación Post-Reorganización
- [ ] main.py ejecuta correctamente
- [ ] Todos los módulos cargan sin errores
- [ ] Base de datos se conecta correctamente
- [ ] Interfaz gráfica se muestra
- [ ] CRUD básico funciona (Crear, Leer, Actualizar, Eliminar)
- [ ] Reports se generan
- [ ] Exports funcionan
- [ ] No hay imports rotos
- [ ] Tests pasando
```

### 6.2 Script de Validación

**Crear: `scripts/setup/validate_structure.py`**
```python
"""
Valida que la nueva estructura funcione correctamente
"""
import sys
from pathlib import Path

def validate_imports():
    """Valida que todos los imports funcionen"""
    print("🔍 Validando imports...")
    errors = []
    
    try:
        from database import get_connection
        print("  ✅ database.get_connection")
    except ImportError as e:
        errors.append(f"❌ database: {e}")
    
    try:
        from utils import validators
        print("  ✅ utils.validators")
    except ImportError as e:
        errors.append(f"❌ utils: {e}")
    
    # ... más validaciones
    
    return len(errors) == 0, errors

def validate_structure():
    """Valida que exista la estructura de directorios"""
    print("🔍 Validando estructura...")
    base = Path(__file__).parent.parent.parent
    
    required_dirs = [
        "src",
        "src/database",
        "src/modules",
        "src/utils",
        "tests",
        "scripts",
        "docs",
    ]
    
    missing = []
    for dir_path in required_dirs:
        full_path = base / dir_path
        if not full_path.exists():
            missing.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    if missing:
        print("\n⚠️  Directorios faltantes:")
        for d in missing:
            print(f"  ❌ {d}")
    
    return len(missing) == 0

def main():
    print("="*60)
    print("  VALIDACIÓN DE ESTRUCTURA - FincaFacil")
    print("="*60)
    
    structure_ok = validate_structure()
    print()
    imports_ok, errors = validate_imports()
    
    if not imports_ok:
        print("\n⚠️  Errores de importación:")
        for error in errors:
            print(f"  {error}")
    
    print("\n" + "="*60)
    if structure_ok and imports_ok:
        print("✅ VALIDACIÓN EXITOSA")
        return 0
    else:
        print("❌ VALIDACIÓN FALLIDA")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 📚 FASE 7: DOCUMENTACIÓN

### 7.1 Actualizar README.md

```markdown
# 🐄 FincaFácil - Sistema de Gestión Ganadera

Sistema profesional para la gestión integral de fincas ganaderas con interfaz gráfica moderna.

## 🚀 Características

- 📊 Dashboard con métricas en tiempo real
- 🐄 Gestión completa de animales
- 📦 Control de inventario e insumos
- 🔧 Administración de herramientas
- 💰 Módulo de ventas y reportes
- 👥 Gestión de nómina
- 📈 Reportes y gráficos

## 📋 Requisitos

- Python 3.10+
- Windows / Linux / macOS

## ⚡ Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/fincafacil.git
cd fincafacil

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar aplicación
python main.py
```

## 🏗️ Estructura del Proyecto

```
fincafacil/
├── main.py                 # Punto de entrada
├── config.py               # Configuración
├── src/                    # Código fuente
│   ├── modules/            # Módulos funcionales
│   ├── database/           # Capa de datos
│   └── utils/              # Utilidades
├── tests/                  # Tests
├── scripts/                # Scripts de mantenimiento
└── docs/                   # Documentación
```

## 📖 Documentación

- [Guía de Usuario](docs/user_guides/USER_GUIDE.md)
- [Arquitectura](docs/architecture/ARCHITECTURE.md)
- [API Interna](docs/api/API.md)
- [Changelog](docs/changelog/CHANGELOG.md)

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licencia

[MIT License](LICENSE.txt)
```

### 7.2 Crear Guías Específicas

- `docs/architecture/ARCHITECTURE.md` - Diseño del sistema
- `docs/user_guides/USER_GUIDE.md` - Guía de usuario
- `docs/api/DATABASE.md` - Esquema de base de datos
- `docs/changelog/CHANGELOG.md` - Historial de cambios

---

## 🎯 FASE 8: PLAN DE EJECUCIÓN

### Orden de Implementación (3-4 horas):

1. **PREPARACIÓN (15 min)**
   - [ ] Git commit: "Estado antes de reorganización"
   - [ ] Backup de database/
   - [ ] Listar todos los archivos actuales

2. **CREAR ESTRUCTURA (30 min)**
   - [ ] Crear directorio src/
   - [ ] Crear subdirectorios (database, utils, modules, core)
   - [ ] Crear __init__.py en cada directorio

3. **MOVER ARCHIVOS CORE (45 min)**
   - [ ] Mover database/* a src/database/
   - [ ] Consolidar validadores en src/utils/validators.py
   - [ ] Mover utilidades a src/utils/
   - [ ] Actualizar imports en archivos movidos

4. **REORGANIZAR MÓDULOS (60 min)**
   - [ ] Revisar y limpiar modules/animales/
   - [ ] Revisar y limpiar modules/insumos/
   - [ ] Eliminar modules/insumos/insumos_main_old.py
   - [ ] Mover modules/ a src/modules/
   - [ ] Actualizar imports

5. **LIMPIAR RAÍZ (45 min)**
   - [ ] Mover tests a tests/integration/
   - [ ] Mover scripts de verificación a scripts/audit/
   - [ ] Mover scripts de utilidad a scripts/dev_tools/
   - [ ] Eliminar archivos obsoletos (previa validación)

6. **ACTUALIZAR IMPORTS (30 min)**
   - [ ] Ejecutar script de actualización automática
   - [ ] Corregir imports manualmente si hay errores
   - [ ] Validar que no haya imports rotos

7. **RENUMERAR MIGRACIONES (20 min)**
   - [ ] Renombrar archivos de migración duplicados
   - [ ] Actualizar sistema de carga de migraciones

8. **VALIDACIÓN FINAL (30 min)**
   - [ ] Ejecutar python main.py
   - [ ] Probar cada módulo principal
   - [ ] Verificar conexión a BD
   - [ ] Ejecutar tests

9. **DOCUMENTACIÓN (20 min)**
   - [ ] Actualizar README.md
   - [ ] Crear ARCHITECTURE.md
   - [ ] Actualizar requirements.txt si es necesario

10. **GIT COMMIT FINAL (10 min)**
    - [ ] Git add .
    - [ ] Git commit -m "Reorganización completa del proyecto"
    - [ ] Git tag v2.0.0-restructured

---

## 📊 MÉTRICAS DE ÉXITO

### Antes vs Después:

| Métrica | Antes | Objetivo Después | Mejora |
|---------|-------|------------------|--------|
| Archivos .py en raíz | 65+ | 3 | -95% |
| Líneas de código | ~50,000 | ~35,000 | -30% |
| Archivos duplicados | 10+ | 0 | -100% |
| Imports inconsistentes | 100+ | 0 | -100% |
| Tests organizados | Parcial | Total | +100% |
| Tiempo para entender estructura | 2+ horas | 5 minutos | -96% |

---

## ⚠️ RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Imports rotos después de mover | Alta | Alto | Script de validación automática |
| Pérdida de funcionalidad | Media | Crítico | Tests y validación exhaustiva |
| Conflictos en Git | Media | Medio | Trabajar en rama separada |
| Errores en producción | Baja | Crítico | Backups completos antes de empezar |

---

## 🎉 RESULTADO ESPERADO

Al finalizar esta reorganización tendrás:

✅ **Estructura profesional** lista para escalar  
✅ **30-40% menos código** (eliminando duplicados y muertos)  
✅ **Imports consistentes** y claros  
✅ **Tests organizados** y ejecutables  
✅ **Documentación actualizada**  
✅ **Fácil de mantener** para cualquier desarrollador nuevo  
✅ **Base sólida** para futuras funcionalidades  

**El proyecto estará listo para ser mostrado en un portfolio profesional.**

---

## 📞 SIGUIENTE PASO

**¿ESTÁS LISTO PARA EMPEZAR LA REORGANIZACIÓN?**

Responde **"INICIAR REORGANIZACIÓN"** para que comience la ejecución automática del plan, o revisemos alguna parte específica antes de empezar.
