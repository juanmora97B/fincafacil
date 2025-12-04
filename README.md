# 🐄 FincaFácil - Sistema de Gestión Ganadera Profesional

> **v2.0.0** | *La fuerza del campo, la precisión del software*

---

## 🚀 Inicio Rápido

### Para Usuarios
```bash
# Opción 1: Usar instalador ejecutable
FincaFacil_Setup_v2.0.exe

# Opción 2: Scripts batch
.\scripts\setup\instalar_dependencias.bat
.\scripts\setup\ejecutar.bat
```

### Para Desarrolladores
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py

# Ejecutar tests
pytest tests/
```

---

## 📚 Documentación

### 📖 Guías de Usuario
- [Inicio Rápido](docs/guias/INICIO_RAPIDO_INSTALADOR.md) - Cómo empezar
- [Guía de Cliente](docs/guias/GUIA_RAPIDA_CLIENTE.md) - Manual del usuario
- [Instrucciones de Instalación](docs/guias/INSTRUCCIONES_INSTALACION_CLIENTE.md) - Pasos detallados

### 🔧 Documentación Técnica
- [Plan de Reorganización v2.0.0](docs/tecnico/PLAN_REORGANIZACION_COMPLETO.md) - Cambios de estructura
- [Arquitectura del Proyecto](docs/tecnico/ARQUITECTURA_FINCA_COMPLETADA.md) - Estructura interna

### 📊 Reportes
- [Reporte Final](docs/reportes/REPORTE_FINAL_REORGANIZACION.md) - Resumen ejecutivo
- [Estructura Final](ESTRUCTURA_FINAL.md) - Organización de carpetas

---

## 🏗️ Estructura del Proyecto

```
FincaFacil/
├── main.py                   # ← EJECUTAR ESTO
├── config.py                 # Configuración
├── requirements.txt          # Dependencias
│
├── src/                      # Código fuente nuevo (v2.0.0)
│   ├── core/                 # Excepciones y constantes
│   ├── database/             # Conexión unificada
│   ├── utils/                # Validadores centralizados
│   └── modules/              # Módulos funcionales
│
├── database/                 # Base de datos
│   └── fincafacil.db         # SQLite con WAL
│
├── modules/                  # Código legacy (funcional)
│   ├── animales/
│   ├── insumos/
│   ├── herramientas/
│   └── ...
│
├── docs/                     # Documentación (30+ archivos)
│   ├── guias/
│   ├── tecnico/
│   └── reportes/
│
├── scripts/                  # Scripts de utilidad
│   ├── setup/
│   ├── migrations/
│   ├── maintenance/
│   └── debug/
│
└── tests/                    # Tests (53 scripts)
```

---

## 📊 Cambios en v2.0.0

✅ **Completado**
- Raíz limpia (reducida de 150+ a 12 archivos)
- 80+ archivos reorganizados en carpetas lógicas
- Sistema de validación centralizado
- Conexión BD unificada
- 550+ líneas de código muerto eliminadas
- Documentación completa y organizada

📈 **Métricas**
- `src/` estructura profesional creada
- `docs/` con 30+ archivos organizados
- `scripts/` con 53 utilidades distribuidas
- 92% reducción en raíz del proyecto
- 100% de imports estandarizados

---

## 🔑 API Principal

### Conectar a BD
```python
from database import get_connection

with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM animal")
```

### Usar DatabaseManager
```python
from database import db

animales = db.execute_query(
    "SELECT * FROM animal WHERE finca_id = ?", 
    (1,)
)
```

### Validar Datos
```python
from src.utils.validators import DataValidator

try:
    DataValidator.validate_peso(450)
    DataValidator.validate_nombre("Bessie")
except ValidationError as e:
    print(f"Error: {e}")
```

---

## 🧪 Tests

```bash
# Todos los tests
pytest tests/

# Con cobertura
pytest tests/ --cov=src

# Tests específicos
pytest tests/test_animales.py -v
```

---

## 🛠️ Scripts Disponibles

### Setup
```bash
.\scripts\setup\instalar_dependencias.bat  # Instalar
.\scripts\setup\ejecutar.bat               # Ejecutar app
```

### Build
```bash
.\scripts\build\compilar.bat                  # Compilar
.\scripts\build\generar_instalador_completo.bat  # Crear installer
```

### Migraciones
```bash
.\scripts\migrations\aplicar_migracion_017.bat
.\scripts\migrations\verificar_estado_migraciones.py
```

### Mantenimiento
```bash
.\scripts\maintenance\abrir_bd.bat
.\scripts\maintenance\resetear_tour.bat
```

### Debug
```bash
python .\scripts\debug\listar_tablas.py
python .\scripts\debug\mostrar_config.py
```

---

## ❓ Preguntas Frecuentes

**P: ¿Dónde está la raíz de la BD?**  
R: `database/fincafacil.db`

**P: ¿Cómo inicio la aplicación?**  
R: `python main.py` o `.\scripts\setup\ejecutar.bat`

**P: ¿Dónde está la documentación?**  
R: En `docs/` organizada por tipo (guias, tecnico, reportes)

**P: ¿Los imports han cambiado?**  
R: Ahora usamos `from database import get_connection` (estandardizado)

**P: ¿Hay tests?**  
R: Sí, 53 scripts en `tests/` organizados por tipo

---

## 📞 Soporte

Para más información consulta:
- 📖 [Guías completas](docs/guias/)
- 🔧 [Documentación técnica](docs/tecnico/)
- 📊 [Reportes](docs/reportes/)
- 📋 [Ver estructura completa](ESTRUCTURA_FINAL.md)

---

## 📄 Licencia

Ver [LICENSE.txt](LICENSE.txt)

---

**FincaFácil v2.0.0 - Reorganizado para Producción ✨**

*Última actualización: 3 de Diciembre de 2025*

