# 📦 Sistema de Generación de Instalador - FincaFacil

Este directorio contiene todos los scripts y configuraciones necesarios para generar un instalador profesional de FincaFacil.

## 📁 Estructura de Archivos

```
FincaFacil/
│
├── 🎯 generar_instalador_completo.bat    # Script maestro (TODO EN UNO)
├── ⚙️ compilar.bat                        # Paso 1: Compilar ejecutable
├── 📦 crear_instalador.bat                # Paso 2: Crear instalador
│
├── 🔧 FincaFacil.spec                     # Configuración PyInstaller
├── 📜 instalador.iss                      # Configuración Inno Setup
│
├── 📚 GUIA_DISTRIBUCION.md               # Guía completa
├── 🚀 INICIO_RAPIDO_INSTALADOR.md        # Inicio rápido
│
├── 📄 LICENSE.txt                         # Licencia del software
├── 📖 docs/
│   ├── INSTALACION.txt                    # Info para instalador
│   └── PRIMER_USO.txt                     # Guía primer uso
│
└── 📂 scripts/
    └── crear_icono_instalador.py          # Generador de icono
```

## 🚀 Inicio Rápido

### Opción 1: Automático (Recomendado)

```batch
generar_instalador_completo.bat
```

Este script ejecuta todo el proceso automáticamente:
- ✅ Instala dependencias
- ✅ Compila el ejecutable
- ✅ Crea el instalador
- ✅ Verifica la integridad

**Tiempo:** 10-15 minutos

---

### Opción 2: Manual

#### Paso 1: Compilar
```batch
compilar.bat
```

#### Paso 2: Crear Instalador
```batch
crear_instalador.bat
```

---

## 📋 Requisitos

### Software Necesario

1. **Python 3.8+**
   - Descargar: https://www.python.org/downloads/
   - Asegúrese de marcar "Add to PATH"

2. **PyInstaller** (se instala automáticamente)
   ```batch
   pip install pyinstaller==6.3.0
   ```

3. **Inno Setup 6.x** (para crear instalador)
   - Descargar: https://jrsoftware.org/isdl.php
   - Instalar con opciones por defecto

4. **Pillow** (para generar icono)
   ```batch
   pip install Pillow
   ```

---

## 🔧 Configuración

### FincaFacil.spec

Archivo de configuración de PyInstaller que define:
- Archivos a incluir
- Módulos ocultos (hidden imports)
- Recursos (assets, modules, utils)
- Configuración del ejecutable

**Modificar si:**
- Agrega nuevos módulos
- Cambia estructura de carpetas
- Incluye recursos adicionales

---

### instalador.iss

Script de Inno Setup que configura:
- Información del instalador
- Ubicación de instalación
- Accesos directos
- Permisos de carpetas
- Código personalizado

**Modificar para:**
- Cambiar versión: `#define MyAppVersion "1.0"`
- Cambiar nombre: `#define MyAppName "FincaFacil"`
- Ajustar permisos de carpetas
- Personalizar mensajes

---

## 📦 Resultado Final

Después de ejecutar el proceso:

```
installer/
└── FincaFacil_Setup_v1.0.exe    (150-250 MB)
```

Este archivo es **completamente autónomo** y contiene:
- ✅ Ejecutable de FincaFacil
- ✅ Todas las dependencias
- ✅ Base de datos SQLite
- ✅ Módulos del sistema
- ✅ Assets y recursos
- ✅ Documentación
- ✅ Tour interactivo

---

## 🌐 Distribución

El instalador puede distribuirse mediante:

### 1. USB/Pendrive
- Copiar archivo al dispositivo
- Entregar al cliente

### 2. Nube (Google Drive, Dropbox, OneDrive)
- Subir archivo
- Compartir enlace
- Cliente descarga e instala

### 3. Servidor Web
- Hospedar en servidor
- Proporcionar URL de descarga

### 4. Email
- Solo si el tamaño lo permite
- Mejor enviar enlace de descarga

### 5. Red Local
- Compartir carpeta
- Acceso desde múltiples equipos

---

## 👤 Instalación (Cliente)

El cliente solo necesita:

1. **Ejecutar** `FincaFacil_Setup_v1.0.exe`
2. **Clic derecho** > "Ejecutar como administrador"
3. **Seguir** el asistente de instalación
4. **Iniciar** FincaFacil desde Menú Inicio

**Primer uso:**
- Tour interactivo automático
- Base de datos se crea automáticamente
- No requiere configuración técnica

---

## 📊 Detalles Técnicos

### Proceso de Compilación

1. **PyInstaller analiza** `main.py`
2. **Detecta dependencias** automáticamente
3. **Incluye hidden imports** del spec
4. **Empaqueta recursos** (assets, modules)
5. **Genera ejecutable** en `dist/`

### Proceso de Instalación (Inno Setup)

1. **Comprime archivos** con LZMA2
2. **Crea instalador** autoextraíble
3. **Incluye desinstalador** automático
4. **Registra** en Windows
5. **Crea accesos directos**

---

## 🔍 Verificación

### Después de Compilar

Verifique que existe:
```
dist/FincaFacil/
├── FincaFacil.exe          ✅
├── assets/                 ✅
├── modules/                ✅
├── database/               ✅
└── [otros archivos DLL]    ✅
```

### Después de Crear Instalador

Verifique:
```
installer/
└── FincaFacil_Setup_v1.0.exe  ✅ (150-250 MB)
```

---

## 🐛 Solución de Problemas

### Error: "Python no encontrado"
```batch
python --version
```
Si falla, reinstale Python y marque "Add to PATH"

---

### Error: "PyInstaller no encontrado"
```batch
pip install pyinstaller==6.3.0
```

---

### Error: "Inno Setup no encontrado"

El script busca en:
- `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
- `C:\Program Files\Inno Setup 6\ISCC.exe`

Si está en otra ubicación, edite `crear_instalador.bat`

---

### Error: "Falta módulo XXX"

Agregue a `FincaFacil.spec` en la sección `hiddenimports`:
```python
hiddenimports = [
    # ... módulos existentes ...
    'nombre_del_modulo',
]
```

---

### Compilación muy lenta

Es normal. PyInstaller analiza todas las dependencias.
Primera compilación: 10-15 minutos
Compilaciones posteriores: 5-10 minutos

---

## 📈 Optimización

### Reducir Tamaño del Instalador

1. **Excluir módulos no usados:**
   ```python
   excludes=[
       'test',
       'unittest',
       'email',
       'xml',
   ]
   ```

2. **Usar UPX compression:**
   - Descargar UPX: https://upx.github.io/
   - PyInstaller lo usará automáticamente

3. **One-file vs One-folder:**
   - One-folder: Más rápido de ejecutar
   - One-file: Más fácil de distribuir
   - Actual: One-folder (recomendado)

---

## 🔐 Firma de Código

Para evitar advertencias de Windows SmartScreen:

1. **Obtener certificado de código**
   - Proveedores: DigiCert, Sectigo, GlobalSign
   - Costo: $100-300 USD/año

2. **Firmar ejecutable:**
   ```batch
   signtool sign /f certificado.pfx /p contraseña /t http://timestamp.digicert.com FincaFacil.exe
   ```

3. **Firmar instalador:**
   En `instalador.iss` agregar:
   ```ini
   SignTool=signtool sign /f certificado.pfx $f
   ```

---

## 📝 Notas de Versión

### v1.0 - Release Inicial
- ✅ Sistema de compilación completo
- ✅ Instalador profesional
- ✅ Documentación completa
- ✅ Scripts automatizados

---

## 📚 Documentación Adicional

- **`GUIA_DISTRIBUCION.md`** - Guía completa de distribución
- **`INICIO_RAPIDO_INSTALADOR.md`** - Referencia rápida
- **`docs/INSTALACION.txt`** - Para el instalador
- **`docs/PRIMER_USO.txt`** - Para nuevos usuarios

---

## 🆘 Soporte

Si encuentra problemas:

1. Revise la sección de solución de problemas
2. Consulte la documentación completa
3. Abra un issue en GitHub

---

## ✅ Checklist Pre-Distribución

Antes de distribuir al cliente:

- [ ] Compilación exitosa
- [ ] Instalador creado
- [ ] Probado en equipo limpio
- [ ] Tour interactivo funcional
- [ ] Manual PDF generado
- [ ] Base de datos se crea correctamente
- [ ] Todas las funcionalidades verificadas
- [ ] Sin errores en logs
- [ ] Documentación incluida
- [ ] Método de distribución elegido

---

**Última actualización:** Noviembre 2024  
**Versión del instalador:** 1.0  
**Plataforma:** Windows 10/11 (64-bit)
