# Manual de Usuario - FincaFacil v2.0
## Sistema de Gestión Ganadera Profesional

---

## 📋 Tabla de Contenido

1. Introducción
2. Instalación e Inicio
3. Módulos del Sistema
4. Configuración Inicial
5. Flujos de Trabajo Comunes
6. Respaldo y Restauración
7. Soporte y Ayuda

---

## 1. INTRODUCCIÓN

**FincaFacil** es un sistema integral de gestión ganadera diseñado para optimizar la administración de fincas ganaderas. Permite el control completo de animales, reproducción, salud, producción, inventarios y finanzas.

### Características Principales:
- ✅ Gestión completa de inventario animal
- ✅ Control reproductivo con predicción de partos
- ✅ Registro de eventos de salud y diagnósticos
- ✅ Manejo de potreros y rotación de pastoreo
- ✅ Administración de tratamientos veterinarios
- ✅ Control de ventas y facturación
- ✅ Inventario de insumos con alertas
- ✅ Gestión de herramientas y mantenimientos
- ✅ Dashboard con KPIs en tiempo real
- ✅ Sistema de reportes y exportación
- ✅ Nómina de empleados
- ✅ Backups automáticos

---

## 2. INSTALACIÓN E INICIO

### Requisitos del Sistema:
- Windows 10/11
- Python 3.8 o superior
- 4GB RAM mínimo
- 500MB espacio en disco

### Instalación Paso a Paso:

1. **Instalar Dependencias:**
   - Ejecutar `instalar_dependencias.bat`
   - Esperar a que se instalen todas las librerías

2. **Iniciar la Aplicación:**
   - Ejecutar `ejecutar.bat`
   - O ejecutar: `python main.py`

3. **Primer Inicio:**
   - La aplicación mostrará un tour interactivo
   - Complete la configuración inicial
   - Agregue su primera finca

---

## 3. MÓDULOS DEL SISTEMA

### 📊 DASHBOARD
**Función:** Vista general del sistema con métricas y gráficos en tiempo real.

**Características:**
- Métricas principales (Total animales, Activos, Valor inventario, Tratamientos)
- Gráfico de estado de animales
- Gráfico de producción de leche (30 días)
- Eventos recientes
- Alertas del sistema

**Uso:**
- Se actualiza automáticamente
- Haga clic en "Actualizar" para refrescar datos
- Los gráficos son interactivos

---

### 🐄 ANIMALES
**Función:** Gestión completa del inventario ganadero.

**Sub-módulos:**
1. **Registro de Animal:**
   - Código único del animal
   - Datos básicos (nombre, sexo, raza, fecha nacimiento)
   - Información de origen (procedencia, precio compra)
   - Ubicación (finca, potrero)
   - Estado y condición corporal

2. **Ficha del Animal:**
   - Visualización completa de información
   - Historial de eventos
   - Edición de datos

3. **Inventario:**
   - Lista completa de animales activos
   - Filtros por finca, sexo, raza
   - Búsqueda por código
   - Exportación a Excel

4. **Actualización de Inventario:**
   - Registro de peso
   - Registro de producción de leche
   - Registro de tratamientos
   - Marcar como inventariado
   - Comentarios rápidos

5. **Importar desde Excel:**
   - Carga masiva de animales
   - Validación automática
   - Plantilla incluida

**Flujo de Trabajo:**
1. Registre un nuevo animal desde "Registro"
2. Asigne ubicación (finca y potrero)
3. Actualice información periódicamente
4. Consulte ficha para ver historial completo

---

### 🤰 REPRODUCCIÓN
**Función:** Control del ciclo reproductivo del ganado.

**Características:**
1. **Registro de Servicios:**
   - Fecha de servicio (monta o IA)
   - Animal hembra
   - Tipo de servicio (Natural/Inseminación)
   - Toro o semen utilizado

2. **Hembras Gestantes:**
   - Lista de animales en gestación
   - Días de gestación calculados automáticamente
   - Fecha estimada de parto (280 días)
   - Confirmar parto
   - Marcar como vacía

3. **Próximos Partos:**
   - Partos esperados en los próximos 30 días
   - Días faltantes
   - Preparación anticipada

**Uso:**
1. Registre servicio cuando cubra una hembra
2. El sistema calcula automáticamente fecha estimada de parto
3. Monitoree hembras gestantes
4. Confirme parto cuando ocurra
5. Si la hembra no queda gestante, márquela como "vacía"

---

### 🏥 SALUD
**Función:** Registro de eventos médicos y diagnósticos veterinarios.

**Tipos de Eventos:**
- Enfermedad
- Lesión
- Revisión
- Vacunación
- Otro

**Severidad:**
- Leve
- Moderada
- Grave
- Crítica

**Estados:**
- Activo
- En Tratamiento
- Recuperado
- Crónico

**Uso:**
1. Registre diagnóstico cuando detecte problema de salud
2. Ingrese detalles del diagnóstico
3. Establezca severidad y estado
4. Actualice estado según evolución
5. Consulte historial completo por animal

---

### 🌿 POTREROS
**Función:** Gestión de terrenos y pastoreo.

**Características:**
- Registro de potreros por finca
- Control de hectáreas
- Tipo de pasto
- Estado (Disponible/En uso/En descanso/Mantenimiento)
- Capacidad animal
- Asignación de animales
- Historial de ocupación

**Uso:**
1. Registre potreros de cada finca
2. Asigne animales a potreros
3. Rote animales para descanso del pasto
4. Monitoree capacidad vs ocupación

---

### 💊 TRATAMIENTOS
**Función:** Administración de medicamentos y tratamientos veterinarios.

**Características:**
- Registro de tratamiento
- Tipo de tratamiento
- Medicamento/producto
- Dosis y frecuencia
- Fecha inicio y fin
- Veterinario responsable
- Costo del tratamiento
- Estado (Activo/Completado/Suspendido)

**Uso:**
1. Registre tratamiento vinculado a diagnóstico
2. Especifique medicamento y dosis
3. Establezca duración
4. Marque como completado al finalizar
5. Registre costo para control financiero

---

### 💰 VENTAS
**Función:** Control de ventas de animales y productos.

**Características:**
- Registro de venta
- Tipo (Animal/Leche/Otro)
- Cliente/Destino
- Precio y forma de pago
- Fecha de venta
- Observaciones
- Actualización automática de inventario

**Uso:**
1. Registre venta cuando venda animal o producto
2. Especifique precio y condiciones
3. El sistema actualiza estado del animal automáticamente
4. Consulte historial de ventas
5. Exporte reportes de ventas

---

### 📦 INSUMOS
**Función:** Control de inventario de suministros y materiales.

**Módulos:**
1. **Inventario:**
   - Registro de insumos
   - Categorías (Medicamento/Alimento/Fertilizante/Semilla)
   - Control de stock (actual/mínimo/máximo)
   - Precio unitario
   - Ubicación
   - Proveedor
   - Fecha de vencimiento

2. **Movimientos:**
   - Entrada (compras)
   - Salida (consumo)
   - Ajuste (correcciones)
   - Actualización automática de stock
   - Tracking de costos

3. **Alertas:**
   - Bajo stock (actual < mínimo)
   - Productos próximos a vencer
   - Déficit calculado

**Uso:**
1. Registre insumos con stock inicial
2. Registre entradas al comprar
3. Registre salidas al consumir
4. Monitoree alertas de bajo stock
5. Reordene cuando sea necesario

---

### 🔧 HERRAMIENTAS
**Función:** Gestión de equipos, maquinaria y herramientas.

**Características:**
1. **Catálogo:**
   - Código único
   - Nombre y categoría
   - Marca y modelo
   - Número de serie
   - Ubicación
   - Estado (Operativa/En mantenimiento/Dañada)
   - Responsable
   - Valor de adquisición
   - Vida útil

2. **Mantenimientos:**
   - Preventivo
   - Correctivo
   - Calibración
   - Inspección
   - Programación de próximo mantenimiento
   - Historial completo
   - Control de costos

**Uso:**
1. Registre herramientas y equipos
2. Asigne responsables
3. Programe mantenimientos preventivos
4. Registre mantenimientos realizados
5. Actualice estado según condición

---

### 📋 REPORTES
**Función:** Generación de reportes y análisis.

**Tipos de Reportes:**
- Inventario de animales
- Producción de leche
- Ventas por período
- Tratamientos aplicados
- Eventos reproductivos
- Gastos e ingresos
- Reportes personalizados

**Formatos:**
- Excel (.xlsx)
- CSV
- PDF (próximamente)

**Uso:**
1. Seleccione tipo de reporte
2. Defina período de fechas
3. Aplique filtros necesarios
4. Genere reporte
5. Exporte en formato deseado

---

### 👥 NÓMINA
**Función:** Gestión de pagos a empleados.

**Características:**
- Registro de empleados
- Control de salarios
- Registro de pagos
- Deducciones
- Historial de pagos
- Cálculo automático

**Uso:**
1. Registre empleados con salario base
2. Registre pagos periódicos
3. Aplique deducciones si necesario
4. Consulte historial
5. Exporte nómina para contabilidad

---

### ⚙️ CONFIGURACIÓN
**Función:** Catálogos maestros del sistema.

**Catálogos Disponibles:**
- Fincas
- Razas
- Empleados
- Proveedores
- Sectores
- Lotes
- Potreros
- Procedencia
- Destino de venta
- Motivos de venta
- Calidad animal
- Condiciones corporales
- Causas de muerte
- Diagnósticos
- Tipo de explotación

**Uso:**
1. Configure catálogos antes de usar el sistema
2. Agregue registros según necesidad
3. Active/Desactive según uso
4. Edite información cuando sea necesario

---

### 🔧 AJUSTES
**Función:** Preferencias y configuración del sistema.

**Opciones:**
1. **Apariencia:**
   - Modo claro/oscuro
   
2. **Preferencias Generales:**
   - Finca por defecto
   - Idioma
   - Unidades de peso (kg/lb)
   - Unidades de volumen (L/gal)

3. **Backups:**
   - Hacer backup manual
   - Ver backups disponibles
   - Restaurar backup
   - Configurar ruta de backups

4. **Manual de Usuario:**
   - Acceso al manual PDF
   - Tour interactivo

---

## 4. CONFIGURACIÓN INICIAL

### Paso 1: Configurar Fincas
1. Ir a **Configuración > Fincas**
2. Agregar finca con:
   - Nombre
   - NIT/RUT
   - Dirección
   - Teléfono
   - Hectáreas totales

### Paso 2: Configurar Razas
1. Ir a **Configuración > Razas**
2. Agregar razas que maneja:
   - Brahman, Holstein, Jersey, etc.

### Paso 3: Configurar Potreros
1. Ir a **Potreros**
2. Agregar potreros de cada finca
3. Especificar hectáreas y tipo de pasto

### Paso 4: Configurar Empleados
1. Ir a **Configuración > Empleados**
2. Registrar personal de la finca

### Paso 5: Agregar Primer Animal
1. Ir a **Animales > Registro**
2. Completar información básica
3. Asignar a finca y potrero

---

## 5. FLUJOS DE TRABAJO COMUNES

### Flujo 1: Nuevo Animal en la Finca

1. **Animales > Registro**
   - Ingresar código único
   - Datos básicos
   - Precio de compra
   - Ubicación

2. **Confirmar Registro**
   - Verificar datos
   - Guardar

3. **Actualizar Inventario**
   - Pesar animal
   - Marcar como inventariado

### Flujo 2: Servicio Reproductivo

1. **Reproducción > Nuevo Servicio**
   - Seleccionar hembra
   - Fecha de servicio
   - Tipo (Natural/IA)
   - Toro/semen

2. **Monitorear Gestación**
   - Ver en "Gestantes"
   - Revisar días de gestación

3. **Preparar Parto**
   - Ver "Próximos Partos"
   - Preparar con anticipación

4. **Confirmar Parto**
   - Botón "Confirmar Parto"
   - Registrar cría si nació

### Flujo 3: Tratamiento Veterinario

1. **Salud > Nuevo Diagnóstico**
   - Registrar síntomas
   - Establecer severidad

2. **Tratamientos > Nuevo Tratamiento**
   - Vincular a diagnóstico
   - Especificar medicamento
   - Dosis y duración

3. **Seguimiento**
   - Actualizar estado del diagnóstico
   - Completar tratamiento

4. **Insumos > Registrar Salida**
   - Descontar medicamento del inventario

### Flujo 4: Venta de Animal

1. **Ventas > Nueva Venta**
   - Seleccionar animal
   - Cliente/Destino
   - Precio

2. **Confirmar Venta**
   - Sistema actualiza estado automáticamente
   - Animal pasa a "Vendido"

3. **Generar Reporte**
   - Reportes > Ventas
   - Exportar para contabilidad

---

## 6. RESPALDO Y RESTAURACIÓN

### Hacer Backup Manual

1. Ir a **Ajustes**
2. Sección "Copias de seguridad"
3. Clic en **"Hacer Backup Ahora"**
4. Confirmar cuando aparezca mensaje de éxito
5. Archivo guardado en carpeta `backup/`

### Ver Backups Disponibles

1. Ir a **Ajustes**
2. Clic en **"Ver Backups"**
3. Se muestra lista con:
   - Nombre del archivo
   - Fecha y hora
   - Tamaño

### Restaurar Backup

1. Ir a **Ajustes**
2. Clic en **"Restaurar Backup"**
3. Seleccionar archivo de backup
4. Confirmar restauración
5. Sistema hace backup de seguridad antes de restaurar
6. Aplicación se reiniciará automáticamente

**⚠️ IMPORTANTE:**
- El sistema crea backup automático antes de restaurar
- No se pierde información
- Proceso es reversible

---

## 7. SOPORTE Y AYUDA

### Tour Interactivo
- Se activa automáticamente en primer uso
- Puede activarse desde **Ajustes > Tour Interactivo**
- Guía paso a paso por funciones principales

### Manual PDF
- Disponible en **Ajustes > Manual de Usuario**
- Se puede imprimir
- Referencia completa del sistema

### Logs del Sistema
- Ubicación: `logs/fincafacil.log`
- Contiene historial de eventos
- Útil para diagnóstico de problemas

### Base de Datos
- Ubicación: `database/fincafacil.db`
- Formato: SQLite
- Se puede abrir con navegador SQLite

### Archivos de Configuración
- `config.py`: Configuraciones generales
- `requirements.txt`: Dependencias Python

### Scripts de Utilidad
- `ejecutar.bat`: Inicia aplicación
- `instalar_dependencias.bat`: Instala librerías
- `abrir_bd.bat`: Abre base de datos
- `migrar_tablas.bat`: Aplica migraciones

---

## 8. CONSEJOS Y BUENAS PRÁCTICAS

### Gestión de Animales
✅ Use códigos únicos consistentes
✅ Actualice pesos regularmente
✅ Registre eventos importantes inmediatamente
✅ Mantenga actualizada la ubicación (potrero)

### Reproducción
✅ Registre servicios el mismo día
✅ Monitoree hembras gestantes semanalmente
✅ Prepare partos con anticipación (30 días antes)
✅ Confirme partos inmediatamente

### Salud
✅ Registre diagnósticos ante primer síntoma
✅ Vincule tratamientos a diagnósticos
✅ Actualice estados regularmente
✅ Consulte historial antes de nuevos tratamientos

### Inventarios
✅ Haga conteo físico mensual
✅ Registre movimientos de insumos inmediatamente
✅ Revise alertas de bajo stock semanalmente
✅ Programe mantenimientos preventivos

### Respaldos
✅ Haga backup diario
✅ Mantenga múltiples copias
✅ Guarde backups en ubicación externa
✅ Pruebe restauración periódicamente

### Reportes
✅ Genere reportes periódicos para análisis
✅ Compare períodos para detectar tendencias
✅ Use reportes para toma de decisiones
✅ Exporte para archivo y auditoría

---

## 9. SOLUCIÓN DE PROBLEMAS

### La aplicación no inicia
1. Verificar que Python esté instalado
2. Ejecutar `instalar_dependencias.bat`
3. Revisar archivo `logs/fincafacil.log`

### Error de base de datos
1. Verificar que exista archivo `database/fincafacil.db`
2. Restaurar desde backup
3. Ejecutar `migrar_tablas.bat`

### Los gráficos no se ven
1. Verificar instalación de matplotlib
2. Reinstalar dependencias
3. Reiniciar aplicación

### No se puede hacer backup
1. Verificar permisos de escritura en carpeta `backup/`
2. Verificar espacio en disco
3. Cerrar otros programas que usen la BD

### Datos no se actualizan
1. Hacer clic en botón "Actualizar"
2. Salir y volver a entrar al módulo
3. Reiniciar aplicación

---

## 10. INFORMACIÓN TÉCNICA

### Versión del Sistema
- **Versión:** 2.0
- **Fecha:** Noviembre 2025
- **Base de datos:** SQLite 3
- **Framework UI:** CustomTkinter
- **Lenguaje:** Python 3.8+

### Módulos Python Utilizados
- customtkinter: Interfaz gráfica moderna
- matplotlib: Gráficos y visualizaciones
- openpyxl: Manejo de archivos Excel
- Pillow: Procesamiento de imágenes

### Estructura de Archivos
```
FincaFacil/
├── main.py                 # Archivo principal
├── config.py              # Configuraciones
├── requirements.txt       # Dependencias
├── database/             # Base de datos
│   ├── fincafacil.db
│   └── database.py
├── modules/              # Módulos del sistema
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
│   └── configuracion/
├── backup/               # Copias de seguridad
├── logs/                 # Registros del sistema
├── exports/              # Reportes exportados
└── assets/              # Recursos (imágenes, logos)
```

---

## 11. GLOSARIO

**Animal Activo:** Animal presente en la finca y en operación normal.

**Condición Corporal:** Evaluación del estado físico del animal (1-5).

**Gestación:** Período de embarazo (280 días promedio en bovinos).

**Inseminación Artificial (IA):** Método reproductivo con semen procesado.

**Inventario:** Conteo físico de animales presentes.

**KPI:** Indicador Clave de Desempeño (Key Performance Indicator).

**Monta Natural:** Reproducción por contacto directo con toro.

**Potrero:** División de terreno para pastoreo.

**Rotación de Pastoreo:** Cambio periódico de animales entre potreros.

**Stock:** Cantidad disponible de insumos.

---

## CONTACTO Y SOPORTE

Para soporte técnico, consultas o sugerencias, por favor contacte con el administrador del sistema o consulte la documentación técnica adicional.

---

**FincaFacil v2.0**  
Sistema de Gestión Ganadera Profesional  
© 2025 - Todos los derechos reservados

---

*Este manual está diseñado para ser una guía completa del sistema. Para información adicional o capacitación, consulte con el administrador del sistema.*
