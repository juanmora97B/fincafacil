# FincaFácil - Guía de Instalación para el Cliente

## 📦 Instalación

1. **Descargar/Recibir el instalador**
   - Archivo: `FincaFacil_Setup_v1.0.exe` (51 MB aprox.)

2. **Ejecutar el instalador**
   - Doble clic en `FincaFacil_Setup_v1.0.exe`
   - Aceptar permisos de administrador si Windows lo solicita
   - Seguir el asistente de instalación

3. **Configuración sugerida**
   - Ruta de instalación: `C:\Program Files\FincaFacil` (por defecto)
   - Marcar "Crear acceso directo en el escritorio" (recomendado)

## 🚀 Primer Uso

1. **Abrir FincaFácil**
   - Desde el acceso directo del escritorio, o
   - Menú Inicio > FincaFacil

2. **Tour interactivo** (opcional)
   - Al abrir por primera vez, aparecerá un tour guiado
   - Puedes completarlo o saltarlo
   - Se puede reactivar desde: Ajustes > Tour Interactivo

3. **Configuración inicial recomendada**
   - Ir a: **Configuración** (ícono de engranaje)
   - Registrar tu finca:
     - Fincas > Agregar Finca
     - Completar: Nombre, Ubicación, Área, Propietario
   - Agregar razas de animales:
     - Razas > Agregar Raza
     - Ejemplos: Holstein, Brahman, Criollo, etc.
   - Crear potreros:
     - Potreros > Agregar Potrero
     - Nombre, área, capacidad

## 📝 Uso Básico

1. **Registrar animales**
   - Módulo: **Animales**
   - Botón: "Registrar Nuevo Animal"
   - Completar: Código, Nombre, Raza, Sexo, Fecha Nacimiento/Compra
   - También puedes importar desde Excel (ver plantillas en Herramientas)

2. **Actualizar inventario**
   - Animales > Actualizar Inventario
   - Registrar pesos, producción de leche

3. **Control reproductivo**
   - Módulo: **Reproducción**
   - Registrar servicios, gestaciones, partos

4. **Salud y tratamientos**
   - Módulo: **Salud**: diagnósticos médicos
   - Módulo: **Tratamientos**: medicamentos, vacunas

5. **Generar reportes**
   - Módulo: **Reportes**
   - Exportar a Excel/PDF: inventario, producción, ventas

## 💾 Copias de Seguridad (IMPORTANTE)

1. **Hacer backup manual**
   - Ir a: **Ajustes** > Copias de Seguridad
   - Clic: "Crear Backup Ahora"
   - Guardar en lugar seguro (USB, nube)

2. **Frecuencia recomendada**
   - Diario si actualizas datos críticos
   - Semanal para uso normal
   - Antes de importar grandes lotes de datos

3. **Restaurar desde backup**
   - Ajustes > Copias de Seguridad
   - Seleccionar archivo `.db` del backup
   - Confirmar restauración

## 📍 Rutas Importantes

- **Instalación**: `C:\Program Files\FincaFacil`
- **Base de datos**: `C:\Program Files\FincaFacil\database\fincafacil.db`
- **Backups**: `C:\Program Files\FincaFacil\backup\`
- **Logs (errores)**: `C:\Program Files\FincaFacil\logs\fincafacil.log`
- **Exportaciones**: `C:\Program Files\FincaFacil\exports\`

## 🔧 Solución de Problemas

### El programa no abre
1. Verificar que se instaló correctamente en `C:\Program Files\FincaFacil`
2. Revisar el log: `C:\Program Files\FincaFacil\logs\fincafacil.log`
3. Ejecutar directamente: `C:\Program Files\FincaFacil\FincaFacil.exe`

### Faltan datos o error de base de datos
1. Restaurar desde backup reciente
2. Si es primera vez, reiniciar la aplicación (se crea BD automáticamente)

### Problema con permisos
1. Clic derecho en acceso directo > "Ejecutar como administrador"

## 📞 Soporte

- Consultar: `Manual_Usuario_FincaFacil.md` (en carpeta docs/)
- Log de errores: enviar archivo `logs\fincafacil.log`

---

✅ **Sistema listo para gestión profesional de tu finca ganadera**
