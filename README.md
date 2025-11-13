# 🐄 FincaFácil - Sistema de Gestión Ganadera

Sistema integral y moderno para la gestión de fincas ganaderas. Desarrollado con Python y CustomTkinter para una experiencia de usuario intuitiva y moderna.

## ✨ Características

- 📊 **Dashboard** con estadísticas en tiempo real
- 🐄 **Gestión de Animales** completa (registro, inventario, fichas, reubicaciones)
- 🌿 **Gestión de Potreros** y áreas de pastoreo
- 💰 **Módulo de Ventas** con historial completo
- 🏥 **Tratamientos y Vacunas** con seguimiento de próximas aplicaciones
- 📈 **Reportes** detallados y estadísticas
- ⚙️ **Configuración** completa del sistema
- 👥 **Gestión de Personal** (Nómina)

## 🚀 Instalación y Ejecución

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos para Ejecutar

1. **Instalar las dependencias:**

   Abre una terminal en la carpeta del proyecto y ejecuta:

   ```bash
   pip install -r requirements.txt
   ```

   O instala manualmente:

   ```bash
   pip install customtkinter Pillow
   ```

2. **Ejecutar el programa:**

   ```bash
   python main.py
   ```

   O si usas Python 3 específicamente:

   ```bash
   python3 main.py
   ```

3. **En Windows (doble clic):**

   También puedes hacer doble clic en el archivo `main.py` si tienes Python configurado correctamente.

## 📁 Estructura del Proyecto

```
FincaFacil/
├── main.py                 # Archivo principal de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── database/               # Gestión de base de datos
│   ├── conexion.py
│   └── actualizar_db.py
├── modules/                # Módulos de la aplicación
│   ├── dashboard/         # Dashboard principal
│   ├── animales/          # Gestión de animales
│   ├── ventas/            # Módulo de ventas
│   ├── tratamientos/      # Tratamientos y vacunas
│   ├── reportes/          # Reportes y estadísticas
│   ├── potreros/          # Gestión de potreros
│   └── configuracion/     # Configuración del sistema
└── assets/                 # Recursos (imágenes, logos)
```

## 🎯 Uso del Sistema

### Primera Vez

1. Al ejecutar por primera vez, el sistema creará automáticamente la base de datos.
2. Ve a **Configuración** para configurar:
   - Fincas
   - Potreros
   - Razas
   - Otros catálogos necesarios

3. Luego puedes empezar a:
   - Registrar animales en **Animales**
   - Registrar ventas en **Ventas**
   - Registrar tratamientos en **Tratamientos**
   - Ver estadísticas en **Dashboard**

## 🔧 Solución de Problemas

### Error: "No module named 'customtkinter'"

**Solución:** Instala las dependencias:
```bash
pip install customtkinter Pillow
```

### Error: "No module named 'PIL'"

**Solución:** Instala Pillow:
```bash
pip install Pillow
```

### La ventana no se muestra correctamente

**Solución:** Asegúrate de tener una versión reciente de Python (3.8+) y CustomTkinter:
```bash
pip install --upgrade customtkinter
```

## 📝 Notas

- La base de datos se crea automáticamente en `database/fincafacil.db`
- El sistema incluye datos de ejemplo para facilitar las pruebas
- Todos los datos se guardan localmente en SQLite

## 👨‍💻 Desarrollo

Este sistema fue desarrollado como una alternativa moderna e intuitiva a sistemas ganaderos tradicionales, con un enfoque en la usabilidad y experiencia del usuario.

---

**Desarrollado con ❤️ para la gestión ganadera eficiente**

