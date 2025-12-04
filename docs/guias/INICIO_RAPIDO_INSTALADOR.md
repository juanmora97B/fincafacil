# 🚀 INICIO RÁPIDO - Generar Instalador de FincaFacil

## ⚡ Opción Rápida (Recomendado)

Ejecute un solo comando:

```batch
generar_instalador_completo.bat
```

Espere 10-15 minutos y tendrá su instalador listo en la carpeta `installer/`

---

## 📋 Requisitos Previos

1. **Python 3.8+** instalado
2. **Inno Setup 6** instalado (descarga: https://jrsoftware.org/isdl.php)

---

## 🎯 Proceso Manual (Si lo Prefiere)

### Paso 1: Compilar Ejecutable
```batch
compilar.bat
```
**Resultado:** `dist/FincaFacil/FincaFacil.exe`

### Paso 2: Crear Instalador
```batch
crear_instalador.bat
```
**Resultado:** `installer/FincaFacil_Setup_v1.0.exe`

---

## 📦 Distribuir al Cliente

El archivo generado (`FincaFacil_Setup_v1.0.exe`) puede distribuirse mediante:

- ✅ USB/Pendrive
- ✅ Google Drive / Dropbox / OneDrive
- ✅ Servidor web
- ✅ Email (si el tamaño lo permite)
- ✅ Red local

---

## 👤 Instrucciones para el Cliente

1. Ejecutar `FincaFacil_Setup_v1.0.exe` como **Administrador**
2. Seguir el asistente de instalación
3. Iniciar FincaFacil desde el Menú Inicio
4. El tour interactivo se inicia automáticamente

---

## ✅ Verificación

Después de generar el instalador:

- [ ] Archivo existe en `installer/`
- [ ] Tamaño aproximado: 150-250 MB
- [ ] Probado en equipo limpio (recomendado)

---

## 📚 Documentación Completa

Para más detalles, consulte:
- `GUIA_DISTRIBUCION.md` - Guía completa de distribución
- `docs/INSTALACION.txt` - Información para el instalador
- `docs/PRIMER_USO.txt` - Guía de primer uso

---

## 🆘 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| Python no encontrado | Instalar Python y agregarlo al PATH |
| PyInstaller falla | `pip install pyinstaller==6.3.0` |
| Inno Setup no encontrado | Descargar e instalar desde jrsoftware.org |
| Compilación lenta | Normal, espere 10-15 minutos |

---

## 📞 Soporte

- Repositorio: https://github.com/juanmora97B/FincaFacil
- Issues: Use la sección de Issues en GitHub

---

**¡Listo para Distribuir!** 🎉
