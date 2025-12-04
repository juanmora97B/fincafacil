# 🐄 FincaFácil v1.0
### Sistema de Gestión Ganadera Profesional

**"La fuerza del campo, la precisión del software"**

FincaFácil es un sistema integral de gestión ganadera diseñado para optimizar la administración de fincas. Con una interfaz moderna y profesional, proporciona control completo sobre todos los aspectos de la operación ganadera.

💼 **Control Total** | 🌱 **Crecimiento Sostenible** | 💰 **Rentabilidad** | 📚 **Tour Interactivo** | 📦 **Instalador Profesional**

---

## 🚀 Inicio Rápido

### Para Usuarios (Instalación)

```batch
# Descargar e instalar
FincaFacil_Setup_v1.0.exe
```

**¡El tour interactivo se activará automáticamente en la primera ejecución!**

### Para Desarrolladores

```bash
# 1. Instalar dependencias
instalar_dependencias.bat

# 2. Ejecutar aplicación
ejecutar.bat

# 3. Generar instalador (NUEVO)
generar_instalador_completo.bat
```

---

## 📦 Distribución del Software

### Generar Instalador Profesional

FincaFacil incluye un sistema completo de generación de instalador:

```batch
# Opción 1: TODO-EN-UNO (Recomendado)
generar_instalador_completo.bat

# Opción 2: Paso a paso
compilar.bat              # Genera ejecutable
crear_instalador.bat      # Crea instalador
```

**Resultado:** `installer/FincaFacil_Setup_v1.0.exe` (150-250 MB)

📚 **Documentación completa:**
- [Guía de Distribución](GUIA_DISTRIBUCION.md) - Todo sobre distribución
- [Inicio Rápido Instalador](INICIO_RAPIDO_INSTALADOR.md) - Referencia rápida
- [Compilación README](COMPILACION_README.md) - Detalles técnicos

### Requisitos para Generar Instalador

- Python 3.8+ ✅
- PyInstaller 6.3.0 (se instala automáticamente)
- Inno Setup 6.x ([Descargar](https://jrsoftware.org/isdl.php))

### Métodos de Distribución

El instalador puede distribuirse mediante:

- 💾 **USB/Pendrive** - Copia y distribución física
- ☁️ **Nube** - Google Drive, Dropbox, OneDrive
- 🌐 **Servidor Web** - Descarga directa
- 📧 **Email** - Para tamaños permitidos
- 🏢 **Red Local** - Despliegue empresarial

---

## ✨ Características Principales

### 📊 Dashboard Inteligente
- Métricas en tiempo real (animales, valor inventario, tratamientos)
- Gráficos interactivos de producción y estado
- Eventos recientes y alertas del sistema
- KPIs actualizados automáticamente

### 🐄 Gestión de Animales
- Registro completo con código único
- Ficha detallada de cada animal
- Inventario con filtros avanzados
- Actualización de peso y producción
- Importación masiva desde Excel
- Historial completo de eventos

### 🤰 Control Reproductivo
- Registro de servicios (monta o IA)
- Monitoreo de hembras gestantes
- Cálculo automático de fecha de parto (280 días)
- Alertas de próximos partos
- Confirmación de nacimientos

### 🏥 Salud y Tratamientos
- Diagnósticos médicos con severidad
- Registro de tratamientos veterinarios
- Medicamentos, dosis y frecuencia
- Historial médico completo
- Control de costos

### 🌿 Gestión de Potreros
- Registro de potreros por finca
- Asignación y rotación de animales
- Control de capacidad animal
- Historial de ocupación
- Estados: Disponible, En uso, En descanso

### 💰 Ventas y Facturación
- Registro de ventas (animales, leche, otros)
- Control de precios y formas de pago
- Actualización automática de inventario
- Reportes de ventas por período

### 📦 Inventario de Insumos
- Control de stock (actual/mínimo/máximo)
- Movimientos de entrada y salida
- Alertas de bajo stock
- Control de vencimientos
- Proveedores

### 🔧 Herramientas y Equipos
- Catálogo de herramientas
- Mantenimientos preventivos
- Historial de reparaciones
- Control de estado operativo
- Gestión de stock (stock_total y stock_bodega) con asignación

### 📋 Reportes Profesionales
- Inventario de animales
- Producción de leche
- Ventas por período
- Tratamientos aplicados
- Exportación a Excel/CSV

### 👥 Gestión de Personal
- Registro de empleados
- Control de nómina
- Pagos y deducciones
- Historial laboral

---

## 📚 Documentación y Ayuda

### 🎓 Tour Interactivo
- **Se activa automáticamente en la primera ejecución**
- 12 pasos guiados por todos los módulos
- Explicaciones claras y concisas
- Reactivable desde **Ajustes > Tour Interactivo**

### 📖 Manual en PDF
- **Disponible en: Ajustes > Manual de Usuario (PDF)**
- 11 secciones completas
- 2.7 MB de contenido detallado
- Imprimible y descargable

### 🛠️ Scripts de Utilidad
```bash
# Ver base de datos
python scripts/utilities/ver_bd_simple.py

# Validar sistema
python scripts/utilities/validar_sistema.py

# Verificar demo y manual
python scripts/utilities/verificar_demo_manual.py

# Resetear tour
resetear_tour.bat

# Abrir manual PDF
abrir_manual.bat

# Abrir base de datos
abrir_bd.bat
```

### 📥 Importación de Condición Corporal (Formatos Compatibles)
El sistema soporta dos formatos para cargar datos de condición corporal desde Excel:

1. Formato Nuevo (recomendado):
    - Columnas mínimas: `codigo`, `descripcion`
    - Opcionales: `puntuacion`, `escala`, `especie`, `caracteristicas`, `recomendaciones`, `estado`
    - Ejemplo:
       ```
       codigo | descripcion             | puntuacion | caracteristicas          | recomendaciones
       CC1    | Muy flaca / crítico     | 1          | costillas muy visibles   | aumentar energia
       CC2    | Delgada                 | 2          | costillas parciales      | balance proteico
       ```

2. Formato Antiguo (compatibilidad):
    - Cualquier presencia de: `condicion_corporal`, `rango_inferior`, `rango_superior`, `recomendacion`, `comentario`
    - Reglas de mapeo:
       - `condicion_corporal` → `codigo`
       - `descripcion` → `descripcion`
       - `recomendacion`/`recomendaciones` → `recomendaciones`
       - `comentario` → `caracteristicas`
       - Si falta `puntuacion` se genera correlativa (1,2,3,...)
    - Ejemplo:
       ```
       condicion_corporal | rango_inferior | rango_superior | descripcion         | recomendacion              | comentario
       CC1                | 1.0            | 2.0            | Muy flaca / crítico | aumentar energia urgente   | costillas marcadas
       CC2                | 2.1            | 3.0            | Delgada             | ajustar dieta              | moderada cobertura
       ```

Notas:
- Filas sin `codigo` o `descripcion` se omiten con aviso.
- Valores vacíos → NULL interno.
- Se admite `recomendacion` o `recomendaciones` indistintamente.
- Evite mezclar encabezados de ambos formatos en una misma hoja.


---

## 📦 Instalación Detallada

### Requisitos del Sistema
- Windows 10/11
- Python 3.8 o superior
- 4GB RAM mínimo
- 500MB espacio en disco

### Paso 1: Clonar Repositorio
```bash
git clone https://github.com/juanmora97B/FincaFacil.git
cd FincaFacil
```

### Paso 2: Instalar Dependencias
```bash
# Opción 1: Script automático (recomendado)
instalar_dependencias.bat

# Opción 2: Manual
pip install -r requirements.txt
```

### Paso 3: Ejecutar
```bash
# Opción 1: Script (recomendado)
ejecutar.bat

# Opción 2: Manual
python main.py
```

---

## 🗂️ Estructura del Proyecto

```
FincaFacil/
├── main.py                     # Aplicación principal
├── config.py                   # Configuraciones globales
├── requirements.txt            # Dependencias Python
├── database/                   # Base de datos SQLite
│   ├── database.py
│   └── fincafacil.db
├── modules/                    # Módulos funcionales
│   ├── animales/
│   ├── reproduccion/
│   ├── salud/
│   ├── potreros/
│   ├── tratamientos/
│   ├── ventas/
│   ├── insumos/
│   ├── herramientas/
│   ├── reportes/
│   ├── nomina/
│   ├── dashboard/
│   ├── ajustes/
│   ├── configuracion/
│   └── utils/
├── scripts/                    # Scripts de utilidad
│   ├── utilities/
│   └── migrations/
├── utils/                      # Utilidades generales
│   ├── tour_interactivo.py
│   ├── pdf_generator.py
│   └── pdf_manual_generator.py
├── docs/                       # Documentación
│   ├── Manual_Usuario_FincaFacil.md
│   └── Manual_Usuario_FincaFacil.pdf
├── backup/                     # Copias de seguridad
├── logs/                       # Archivos de log
├── exports/                    # Reportes exportados
├── uploads/                    # Archivos subidos
└── assets/                     # Recursos (logos, iconos)
```

---

## 🔧 Tecnologías Utilizadas

| Tecnología | Uso | Versión |
|------------|-----|---------|
| **Python** | Lenguaje base | 3.8+ |
| **CustomTkinter** | Interfaz gráfica moderna | 5.2.2 |
| **SQLite** | Base de datos | 3.x |
| **Matplotlib** | Gráficos y visualizaciones | 3.8.3 |
| **ReportLab** | Generación de PDF | 4.0.8 |
| **OpenPyXL** | Manejo de Excel | 3.1.2 |
| **Pillow** | Procesamiento de imágenes | 10.2.0 |
| **Loguru** | Sistema de logs | 0.7.2 |
| **Markdown** | Procesamiento de docs | 3.5.2 |

---

## 💡 Flujos de Trabajo Comunes

### 1. Registrar Nuevo Animal
```
Animales > Registro > Ingresar datos > Guardar
```

### 2. Servicio Reproductivo
```
Reproducción > Nuevo Servicio > Seleccionar hembra > Guardar
→ El sistema calcula automáticamente la fecha de parto
```

### 3. Tratamiento Veterinario
```
Salud > Nuevo Diagnóstico > Registrar síntomas
→ Tratamientos > Nuevo Tratamiento > Vincular a diagnóstico
```

### 4. Venta de Animal
```
Ventas > Nueva Venta > Seleccionar animal > Confirmar
→ El sistema actualiza automáticamente el inventario
```

### 5. Gestión de Stock de Herramientas
```
Herramientas > Catálogo > (Filtrar / Editar / Importar Excel)
```
Reglas de stock:
- stock_total: unidades físicas representadas (mínimo 1).
- stock_bodega: unidades disponibles en bodega (>=0 y <= stock_total).
- Si la herramienta está asignada a un trabajador y stock_total = 1, el sistema fuerza stock_bodega = 0.
- Si asignada y stock_bodega = stock_total (>1), se ajusta automáticamente a stock_total - 1.
- Importación Excel: si faltan columnas de stock se asume stock_total=1 y stock_bodega=1 (o 0 si asignada).
- Para multiunidad ajustar manualmente stock_bodega cuando se asignan piezas.

Ejemplos:
| Escenario | Responsable | stock_total | stock_bodega guardado |
|-----------|-------------|-------------|-----------------------|
| Única asignada | Trabajador X | 1 | 0 |
| Única en bodega | Bodega | 1 | 1 |
| Lote 5 en bodega | Bodega | 5 | 5 |
| Lote 5 con 2 asignadas | Trabajador Y | 5 | 3 |

Excel (campos opcionales nuevos):
```
codigo | nombre | categoria | ... | stock_total | stock_bodega
HER-010 | Juego Destornilladores | Herramienta Manual | ... | 12 | 12
HER-011 | Motosierra Husqvarna | Herramienta Manual | ... | 1 | 1
HER-012 | Motosierra Husqvarna (Asignada) | Herramienta Manual | ... | 1 | 0
```

Catálogo muestra: Código, Nombre, Categoría, Stock Total, Asignación (Asignada / En Bodega), Stock Bodega, Estado.

---

## 💾 Sistema de Backups

### Backup Manual
```
Ajustes > Hacer Backup Ahora
```

### Ver Backups Disponibles
```
Ajustes > Ver Backups
```

### Restaurar Backup
```
Ajustes > Restaurar Backup > Seleccionar archivo
```

**⚠️ El sistema crea un backup de seguridad antes de restaurar**

---

## 🎯 Configuración Inicial Recomendada

1. **Configurar Fincas**
   - `Configuración > Fincas`
   - Agregar nombre, NIT, dirección, hectáreas

2. **Registrar Razas**
   - `Configuración > Razas`
   - Agregar razas que maneja

3. **Crear Potreros**
   - `Potreros > Nuevo Potrero`
   - Especificar hectáreas y tipo de pasto

4. **Agregar Empleados (opcional)**
   - `Configuración > Empleados`

5. **Registrar Primer Animal**
   - `Animales > Registro`

---

## 🔍 Solución de Problemas

### La aplicación no inicia
```bash
# 1. Verificar Python instalado
python --version

# 2. Reinstalar dependencias
pip install -r requirements.txt --force-reinstall

# 3. Revisar logs
type logs\fincafacil.log
```

### Error de base de datos
```bash
# 1. Verificar que existe
dir database\fincafacil.db

# 2. Ejecutar migraciones
migrar_tablas.bat

# 3. Restaurar desde backup
# Ajustes > Restaurar Backup
```

### No se ven los gráficos
```bash
# Reinstalar matplotlib
pip install matplotlib --force-reinstall
```

---

## 📞 Soporte y Contacto

- **Repositorio:** [github.com/juanmora97B/FincaFacil](https://github.com/juanmora97B/FincaFacil)
- **Issues:** [GitHub Issues](https://github.com/juanmora97B/FincaFacil/issues)
- **Documentación:** `docs/Manual_Usuario_FincaFacil.pdf`

---

## 📝 Changelog

### v2.0 (Noviembre 2025)
- ✨ Tour interactivo automático
- ✨ Manual de usuario en PDF integrado
- ✨ Dashboard mejorado con KPIs
- ✨ Sistema de backups completo
- 🐛 Corrección de bugs menores
- 📚 Documentación consolidada

### v1.0 (Octubre 2025)
- 🎉 Lanzamiento inicial
- ✅ Todos los módulos funcionales

---

## 📜 Licencia

Este proyecto está bajo licencia privada. Todos los derechos reservados © 2025.

---

## 🙏 Agradecimientos

Desarrollado con ❤️ para optimizar la gestión ganadera moderna.

**FincaFácil v2.0** - La fuerza del campo, la precisión del software.

---

