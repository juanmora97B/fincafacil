# FincaFácil v2.0 - Sistema de Gestión Ganadera

![FincaFácil](src/assets/Logo.png)

**FincaFácil** es una aplicación profesional de gestión ganadera diseñada para facilitar el manejo integral de fincas ganaderas. Desde el control de animales hasta la gestión de ventas, FincaFácil centraliza todas tus operaciones en una interfaz intuitiva y fácil de usar.

## 🚀 Características Principales

- ✅ **Gestión integral de animales**: Registro, genealogía, fotos e historial
- ✅ **Control de salud y reproducción**: Diagnósticos, vacunaciones, eventos reproductivos
- ✅ **Producción de leche**: Registro diario de ordeño y calidad
- ✅ **Gestión de potreros**: Control de terrenos y rotación de pasto
- ✅ **Ventas y clientes**: Registro completo de transacciones comerciales
- ✅ **Nómina de empleados**: Gestión de personal y salarios
- ✅ **Herramientas e insumos**: Inventario con control de stock
- ✅ **Reportes avanzados**: Exportación a PDF y Excel
- ✅ **Período de prueba**: 6 meses gratuitos sin tarjeta de crédito
- ✅ **Sistema de autenticación**: Login seguro con protección

## 📋 Requisitos del Sistema

### Mínimos
- Windows 10 o superior (64 bits)
- 200 MB de espacio en disco
- 4 GB de RAM

### Recomendados
- Windows 11
- 500 MB de espacio libre
- 8 GB de RAM

## 📦 Instalación

### Opción 1: Instalador ejecutable (Recomendado)
1. Descarga `FincaFacil_Installer_v2.0.exe`
2. Ejecuta el instalador
3. Sigue el asistente
4. Disponible en Menú Inicio

### Opción 2: Ejecutable standalone
1. Descarga `FincaFacil.exe`
2. Ejecuta sin instalación requerida
3. No necesita Python instalado

### Opción 3: Desde código fuente
```bash
pip install -r src/utils/requirements.txt
python src/main.py
```

## 🎯 Primeros Pasos

1. **Crear cuenta**: Usuario y contraseña
2. **Período de prueba**: 6 meses completamente gratis
3. **Tour interactivo**: Recorrido por la aplicación
4. **Comenzar a usar**: Agregar animales, fincas, etc.

## 📚 Documentación

- **Manual completo**: [docs/Manual_FincaFacil_v2.pdf](docs/Manual_FincaFacil_v2.pdf)
- **Licencia de uso**: [docs/LICENCIA.txt](docs/LICENCIA.txt)
- **Antes de instalar**: [docs/ANTES_DE_INSTALAR.txt](docs/ANTES_DE_INSTALAR.txt)
- **Después de instalar**: [docs/DESPUES_DE_INSTALAR.txt](docs/DESPUES_DE_INSTALAR.txt)

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

**Contacto:**
- 📧 Email: jfburitica97@gmail.com
- 📱 Teléfono: 3013869653

---

## 📄 Licencia

Ver [LICENSE.txt](LICENSE.txt)

---

**FincaFácil v2.0.0 - Reorganizado para Producción ✨**

*Última actualización: 3 de Diciembre de 2025*

