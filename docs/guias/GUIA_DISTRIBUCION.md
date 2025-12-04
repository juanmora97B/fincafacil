# 📦 Guía de Distribución - FincaFacil Instalador

## 🎯 Resumen Ejecutivo

Esta guía explica cómo generar y distribuir el instalador profesional de FincaFacil para que los clientes puedan instalarlo fácilmente en cualquier equipo Windows.

---

## 🚀 Proceso de Generación del Instalador

### Opción 1: Generación Automática (Recomendado)

Ejecute el script maestro que realiza todo el proceso:

```batch
generar_instalador_completo.bat
```

Este script ejecuta automáticamente:
1. ✅ Instalación de dependencias
2. ✅ Compilación del ejecutable
3. ✅ Creación del instalador
4. ✅ Verificación de integridad

**Tiempo estimado:** 10-15 minutos

---

### Opción 2: Generación Manual (Paso a Paso)

#### Paso 1: Compilar el Ejecutable

```batch
compilar.bat
```

Este proceso:
- Instala PyInstaller
- Crea el icono de la aplicación
- Compila main.py y todas las dependencias
- Genera la carpeta `dist/FincaFacil/`

**Resultado:** Ejecutable funcional en `dist/FincaFacil/FincaFacil.exe`

---

#### Paso 2: Crear el Instalador

```batch
crear_instalador.bat
```

Este proceso:
- Busca Inno Setup Compiler
- Compila el script `instalador.iss`
- Genera el instalador en `installer/`

**Resultado:** Archivo instalador `FincaFacil_Setup_v1.0.exe`

---

## 📋 Requisitos Previos

### En el Equipo de Desarrollo

1. **Python 3.8+** instalado y en PATH
   ```batch
   python --version
   ```

2. **PyInstaller** (se instala automáticamente)
   ```batch
   pip install pyinstaller==6.3.0
   ```

3. **Inno Setup 6.x** (para crear instalador)
   - Descarga: https://jrsoftware.org/isdl.php
   - Instalación: Ejecutar el instalador y seguir asistente

4. **Dependencias del proyecto**
   ```batch
   pip install -r requirements.txt
   ```

---

## 📦 Contenido del Instalador

El instalador incluye:

### Archivos Principales
- ✅ `FincaFacil.exe` - Ejecutable principal
- ✅ Base de datos SQLite
- ✅ Módulos del sistema completos
- ✅ Assets (imágenes, iconos, recursos)

### Documentación
- ✅ Manual de usuario PDF
- ✅ Guía de instalación
- ✅ Guía de primer uso
- ✅ README.md

### Características
- ✅ Tour interactivo automático
- ✅ Sistema de backup automático
- ✅ Generador de reportes PDF/Excel
- ✅ Sistema de notificaciones
- ✅ Validaciones automáticas

---

## 🌐 Métodos de Distribución

### 1. USB / Pendrive (Recomendado para Instalaciones Locales)

**Ventajas:**
- ✅ No requiere internet
- ✅ Instalación rápida
- ✅ Control total sobre la distribución

**Proceso:**
1. Copie `FincaFacil_Setup_v1.0.exe` al USB
2. Incluya opcionalmente:
   - `Manual_Usuario_FincaFacil.pdf`
   - `GUIA_INSTALACION.txt`
3. Entregue al cliente
4. Cliente ejecuta el instalador desde el USB

**Tamaño aproximado:** 150-250 MB

---

### 2. Descarga en Línea (Google Drive / Dropbox / OneDrive)

**Ventajas:**
- ✅ Distribución masiva
- ✅ Actualizaciones centralizadas
- ✅ Acceso desde cualquier lugar

**Proceso Google Drive:**
```
1. Ir a: https://drive.google.com
2. Subir archivo: FincaFacil_Setup_v1.0.exe
3. Clic derecho > Compartir
4. Configurar permisos: "Cualquiera con el enlace puede ver"
5. Copiar enlace
6. Enviar enlace al cliente
```

**Proceso Dropbox:**
```
1. Ir a: https://dropbox.com
2. Subir archivo al Dropbox
3. Clic derecho > Compartir
4. Crear enlace
5. Enviar al cliente
```

**Proceso OneDrive:**
```
1. Ir a: https://onedrive.live.com
2. Subir archivo
3. Compartir > Obtener enlace
4. Configurar permisos
5. Enviar enlace
```

---

### 3. Servidor Web Propio

**Ventajas:**
- ✅ Control total
- ✅ Estadísticas de descarga
- ✅ Branding personalizado

**Configuración Básica (Apache/Nginx):**

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Descargar FincaFacil</title>
</head>
<body>
    <h1>FincaFacil v1.0</h1>
    <p>Sistema de Gestión Ganadera</p>
    <a href="FincaFacil_Setup_v1.0.exe" download>
        Descargar Instalador (150 MB)
    </a>
</body>
</html>
```

**Requisitos del servidor:**
- Espacio: 500 MB mínimo
- Ancho de banda: Depende del número de descargas

---

### 4. Email (Para Grupos Pequeños)

**Limitaciones:**
- ⚠️ Límite de tamaño típico: 25 MB (Gmail, Outlook)
- ⚠️ No recomendado para archivos grandes

**Alternativa:** Enviar enlace de descarga en lugar del archivo

```
Asunto: FincaFacil - Software de Gestión Ganadera

Estimado Cliente,

Adjunto encontrará el instalador de FincaFacil v1.0.

Enlace de descarga:
https://drive.google.com/file/d/xxxxx

Instrucciones:
1. Descargar el archivo
2. Ejecutar como Administrador
3. Seguir el asistente de instalación

Saludos,
Equipo FincaFacil
```

---

### 5. Red Local (Empresas/Organizaciones)

**Ventajas:**
- ✅ Despliegue rápido a múltiples equipos
- ✅ Sin uso de internet

**Configuración:**

```batch
REM En el servidor
net share FincaFacil=C:\Instaladores\FincaFacil /GRANT:Everyone,READ

REM En los clientes
\\SERVIDOR\FincaFacil\FincaFacil_Setup_v1.0.exe
```

---

## 👤 Instrucciones para el Cliente

### Requisitos del Sistema Cliente

| Componente | Requisito |
|------------|-----------|
| Sistema Operativo | Windows 10/11 (64 bits) |
| Procesador | Intel Core i3 o equivalente |
| RAM | 4 GB mínimo (8 GB recomendado) |
| Disco Duro | 500 MB libres |
| Resolución | 1366x768 mínimo |
| Internet | NO requerido |

### Proceso de Instalación (Cliente)

#### Paso 1: Descargar o Copiar el Instalador
```
Obtenga el archivo: FincaFacil_Setup_v1.0.exe
```

#### Paso 2: Ejecutar como Administrador
```
1. Clic derecho en FincaFacil_Setup_v1.0.exe
2. Seleccionar "Ejecutar como administrador"
3. Confirmar en el UAC (Control de Cuentas de Usuario)
```

#### Paso 3: Seguir el Asistente
```
1. Leer información de bienvenida
2. Aceptar licencia
3. Elegir ubicación (recomendado: C:\Program Files\FincaFacil)
4. Seleccionar componentes (dejar todo marcado)
5. Confirmar instalación
6. Esperar finalización (2-5 minutos)
7. Marcar "Iniciar FincaFacil" si desea abrirlo inmediatamente
```

#### Paso 4: Primer Uso
```
1. Se inicia automáticamente el tour interactivo
2. Seguir las instrucciones en pantalla
3. Configurar datos básicos de la finca
4. Comenzar a usar el sistema
```

---

## 🔧 Solución de Problemas

### Problema: "Windows protegió tu PC"

**Causa:** SmartScreen de Windows bloquea ejecutables no firmados

**Solución:**
```
1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"
```

**Solución permanente (Desarrollador):**
- Firmar el ejecutable con certificado de código
- Costo: ~$100-300 USD anuales

---

### Problema: "No se puede instalar en esta ubicación"

**Causa:** Permisos insuficientes

**Solución:**
```
1. Ejecutar instalador como Administrador
2. O cambiar ubicación a carpeta del usuario
```

---

### Problema: "Falta archivo DLL"

**Causa:** Dependencias no incluidas

**Solución:**
```
1. Instalar Visual C++ Redistributable
   Descarga: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Reintentar instalación
```

---

### Problema: Instalador no se ejecuta

**Causa:** Archivo corrupto

**Solución:**
```
1. Verificar integridad del archivo
2. Re-descargar el instalador
3. Verificar antivirus no lo bloqueó
```

---

## 📊 Instalación Silenciosa (Despliegue Masivo)

Para instalar sin interacción del usuario:

```batch
FincaFacil_Setup_v1.0.exe /VERYSILENT /NORESTART /DIR="C:\FincaFacil"
```

**Parámetros:**
- `/VERYSILENT` - Sin ventanas ni mensajes
- `/SILENT` - Barra de progreso visible
- `/NORESTART` - No reiniciar equipo
- `/DIR="ruta"` - Directorio específico
- `/LOG="archivo.log"` - Guardar log de instalación

**Ejemplo con log:**
```batch
FincaFacil_Setup_v1.0.exe /VERYSILENT /NORESTART /LOG="C:\Temp\install.log"
```

---

## 🔄 Actualización del Software

### Para Actualizar a una Nueva Versión:

1. **Generar nuevo instalador** con nueva versión
2. **Cliente ejecuta nuevo instalador**
3. **Instalador detecta versión anterior**
4. **Datos se conservan automáticamente**

**IMPORTANTE:** La base de datos NO se sobrescribe

---

## 🗑️ Desinstalación

### Proceso de Desinstalación:

```
1. Panel de Control > Programas > Desinstalar un programa
2. Seleccionar "FincaFacil"
3. Clic en "Desinstalar"
4. El sistema pregunta si conservar la base de datos:
   - SÍ: Mantiene datos para reinstalación
   - NO: Elimina todo permanentemente
```

---

## 🔐 Seguridad y Privacidad

### Datos del Cliente

✅ **Todos los datos permanecen en el equipo del cliente**
- No se envía información a servidores externos
- No hay telemetría
- No hay rastreo de uso
- Privacidad total garantizada

### Base de Datos

```
Ubicación: C:\Program Files\FincaFacil\database\fincafacil.db
Tipo: SQLite (archivo local)
Backups: C:\Program Files\FincaFacil\backup\
```

---

## 📈 Tamaño y Rendimiento

### Tamaño del Instalador

| Componente | Tamaño Aproximado |
|------------|-------------------|
| Ejecutable base | 80-100 MB |
| Dependencias Python | 40-60 MB |
| Assets y recursos | 10-20 MB |
| Documentación | 5-10 MB |
| **TOTAL** | **150-250 MB** |

### Rendimiento

| Métrica | Valor |
|---------|-------|
| Tiempo de instalación | 2-5 minutos |
| Tiempo de inicio | 2-4 segundos |
| Uso de RAM | 150-300 MB |
| Uso de disco (instalado) | 300-400 MB |

---

## ✅ Checklist de Distribución

Antes de distribuir, verifique:

- [ ] Instalador generado exitosamente
- [ ] Instalador probado en equipo limpio
- [ ] Documentación incluida y actualizada
- [ ] Manual PDF generado
- [ ] Tour interactivo funcional
- [ ] Base de datos se crea correctamente
- [ ] Backups automáticos funcionan
- [ ] Todas las funcionalidades probadas
- [ ] Sin errores en logs
- [ ] Método de distribución elegido
- [ ] Instrucciones preparadas para cliente

---

## 📞 Soporte Post-Distribución

### Canales de Soporte

1. **Documentación incluida**
   - Manual PDF en el sistema
   - Tour interactivo
   - Ayuda contextual

2. **Repositorio GitHub**
   - https://github.com/juanmora97B/FincaFacil
   - Issues y tickets

3. **Contacto directo**
   - Email de soporte
   - WhatsApp/Teléfono

---

## 🎓 Capacitación del Cliente

### Materiales Incluidos

1. ✅ Tour interactivo automático (primera ejecución)
2. ✅ Manual de usuario PDF completo
3. ✅ Guía de primeros pasos
4. ✅ Ejemplos de uso

### Capacitación Adicional (Opcional)

- Sesión virtual de 1 hora
- Video tutoriales
- Soporte telefónico inicial
- Visita presencial

---

## 📝 Notas Finales

### Ventajas de este Sistema de Distribución

✅ **Profesional:** Instalador con asistente gráfico
✅ **Completo:** Todo incluido en un solo archivo
✅ **Fácil:** Cliente solo ejecuta el instalador
✅ **Seguro:** Sin dependencias externas
✅ **Offline:** Funciona sin internet
✅ **Actualizable:** Proceso de actualización simple

### Próximos Pasos

1. Generar el instalador con los scripts proporcionados
2. Probar en un equipo limpio
3. Elegir método de distribución
4. Distribuir a clientes
5. Proporcionar soporte según sea necesario

---

## 📂 Archivos Relacionados

- `generar_instalador_completo.bat` - Script maestro
- `compilar.bat` - Compilador de ejecutable
- `crear_instalador.bat` - Generador de instalador
- `instalador.iss` - Configuración Inno Setup
- `FincaFacil.spec` - Configuración PyInstaller
- `docs/INSTALACION.txt` - Guía para instalador
- `docs/PRIMER_USO.txt` - Guía de primer uso

---

**Documento generado:** Noviembre 2024  
**Versión:** 1.0  
**Proyecto:** FincaFacil - Sistema de Gestión Ganadera
