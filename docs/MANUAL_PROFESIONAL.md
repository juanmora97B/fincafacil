# 📘 MANUAL PROFESIONAL FINCAFÁCIL v2.0

**Versión**: 2.0  
**Fecha**: 9 Diciembre 2025  
**Descripción**: Manual completo para usuarios finales y administradores

---

## 📑 TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Instalación Rápida](#instalación-rápida)
3. [Tour Interactivo](#tour-interactivo)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Flujos de Trabajo Comunes](#flujos-de-trabajo-comunes)
6. [Tips y Trucos](#tips-y-trucos)
7. [Solución de Problemas](#solución-de-problemas)
8. [Glosario](#glosario)

---

## 🎯 Introducción

### ¿Qué es FincaFácil?

FincaFácil es un **sistema integral de gestión ganadera** diseñado para ayudarte a administrar eficientemente tu finca o ganadería. Incluye:

- 📊 **Dashboard** con métricas clave
- 🐄 **Gestión de animales** (fichas completas, genealogía, salud)
- 🥛 **Control de producción de leche**
- 💰 **Módulo de ventas**
- 👶 **Reproducción y palpación**
- 📋 **Reportes automáticos**
- ⚙️ **Configuración de maestros** (razas, fincas, empleados)

### Requisitos del Sistema

```
- Windows 7 o superior
- Python 3.10+
- 500 MB de espacio en disco
- Internet (solo para updates iniciales)
```

---

## ⚡ Instalación Rápida

### Paso 1: Descargar
Descarga FincaFácil desde: `www.fincafacil.com/descargar`

### Paso 2: Instalar
```
1. Descomprime el archivo
2. Doble-click en: FincaFacil_Setup_v1.0.exe
3. Sigue los pasos del instalador
4. Click en "Finalizar"
```

### Paso 3: Ejecutar
```
1. Desktop → FincaFácil (icono)
2. O: Menú Inicio → FincaFácil
3. ¡Listo! La aplicación se abre automáticamente
```

### Paso 4: Primera Configuración
```
1. Módulo: Configuración
2. Datos Maestros → Fincas
3. Agregar tu finca principal
4. Agregar empleados
5. Configurar razas
```

**Tiempo total**: 10-15 minutos

---

## 🎓 Tour Interactivo

Cuando inicies FincaFácil por primera vez, verás el **Tour Interactivo**.

### Qué incluye:
- ✅ Explicación del dashboard
- ✅ Cómo registrar un animal
- ✅ Cómo registrar pesaje de leche
- ✅ Cómo crear una venta
- ✅ Dónde encontrar reportes

**Duración**: 10-15 minutos

### Activar manualmente:
```
Menú: Help → Iniciar Tour
```

---

## 📊 Módulos del Sistema

### 1. DASHBOARD

**¿Qué es?**  
Panel principal que muestra el estado general de tu finca.

**Métricas principales:**
- 🐄 Total de animales
- ✅ Activos
- ⚰️ Muertos
- 🛒 Vendidos
- 🏥 En tratamiento
- 🤰 Gestantes
- 🥛 Producción HOY
- 👶 Nacimientos del mes

**Gráficos:**
- Estado de animales (Activos, Muertos, Vendidos)
- Producción de leche (últimos 30 días)

**Alertas automáticas:**
- Animales sin raza
- Animales sin lote
- Próximos tratamientos
- Gestantes con próximos partos
- Problemas de salud

**¿Cómo usar?**
1. Abre FincaFácil
2. Mira el dashboard automáticamente
3. Lee las alertas rojas (urgentes)
4. Haz click en cualquier métrica para ver detalles

---

### 2. ANIMALES

**¿Qué es?**  
Módulo completo para gestionar cada animal de tu finca.

**Funcionalidades:**

#### Registrar nuevo animal
```
1. Click: Módulo ANIMALES
2. Button: "Nuevo animal"
3. Completa:
   - Código (ej: "LEC-001")
   - Nombre (opcional)
   - Tipo: Vaca, Novilla, Toro, Ternero
   - Sexo
   - Raza
   - Fecha de nacimiento
   - Finca
   - Potrero
4. Click: "Guardar"
```

#### Ver ficha del animal
```
1. Lista de animales
2. Doble-click en un animal
3. Abre su ficha completa con:
   - Datos generales
   - Genealogía (madre, padre)
   - Producción de leche
   - Historial de salud
   - Historial de ventas
   - Fotografía
   - Comentarios/notas
```

#### Filtrar animales
```
1. Lista de animales
2. Selector "Finca" → elige tu finca
3. Filtro "Estado" → Activo/Vendido/Muerto/Perdido
4. Buscar por código
```

#### Reubicación
```
1. Selecciona un animal
2. Button: "Reubicación"
3. Elige: Finca origen → Finca destino
4. Elige: Potrero destino
5. Click: "Mover"
6. Sistema actualiza automáticamente inventarios
```

---

### 3. LECHE

**¿Qué es?**  
Módulo para registrar pesaje de leche diario.

**Registro diario:**
```
1. Click: Módulo LECHE
2. Button: "Nuevo pesaje"
3. Selecciona animal
4. Ingresa:
   - Litros mañana
   - Litros tarde
   - Litros noche
5. Click: "Guardar"
```

**Reportes de producción:**
```
1. Click: Módulo LECHE
2. Selector: Rango de fechas
3. Selector: Por animal, por finca, o total
4. Click: "Generar reporte"
5. Opción: Exportar a Excel
```

---

### 4. REPRODUCCIÓN

**¿Qué es?**  
Control de ciclos reproductivos y gestaciones.

#### Nuevo servicio
```
1. Click: Módulo REPRODUCCIÓN
2. Click: "Nuevo servicio"
3. Selecciona animal (solo hembras)
4. Tipo de servicio: Monta natural, IA, etc.
5. Fecha del servicio
6. Click: "Guardar"
```

#### Registrar gestante
```
1. Click: "Palpación"
2. Selecciona finca
3. Sistema muestra solo vacas/novillas
4. Para cada animal:
   - ¿Gestante? SÍ / NO
   - Semanas de gestación
   - Observaciones veterinarias
5. Click: "Guardar"
6. Sistema calcula fecha estimada de parto
```

#### Ver próximos partos
```
1. Click: "Próximos partos"
2. Lista de gestantes ordenadas por fecha
3. Alertas rojas para partos próximos (<10 días)
4. Observaciones de cada animal
```

---

### 5. VENTAS

**¿Qué es?**  
Registro de ventas de animales.

#### Nueva venta
```
1. Click: Módulo VENTAS
2. Button: "Nueva venta"
3. Selecciona:
   - Finca
   - Animal (carga automáticamente)
4. Ingresa:
   - Fecha
   - Precio
   - Comprador
   - Concepto (reposo, carne, etc)
5. Click: "Guardar"
6. Sistema marca animal como "Vendido" automáticamente
```

#### Reportes de ventas
```
1. Click: "Reportes"
2. Rango de fechas
3. Opción: Por vendedor, por concepto, etc.
4. Exportar a Excel
```

---

### 6. SALUD

**¿Qué es?**  
Registro de tratamientos, diagnósticos y medicinas.

#### Nuevo tratamiento
```
1. Click: Módulo SALUD
2. Click: "Nuevo tratamiento"
3. Selecciona animal
4. Ingresa:
   - Diagnóstico
   - Producto usado
   - Dosis
   - Veterinario
   - Fecha inicio
   - Fecha fin estimada
5. Click: "Guardar"
```

#### Alertas de medicinas
```
1. El sistema monitorea vencimientos
2. Alertas automáticas 3 días antes
3. Dashboard muestra tratamientos vencidos
```

---

### 7. REPORTES

**¿Qué es?**  
Generación de reportes profesionales.

#### Tipos de reportes:
- 📊 Inventario actual
- 📈 Producción de leche
- 💰 Ventas
- 🏥 Salud y tratamientos
- 👶 Reproducción y nacimientos
- 📋 Movimientos de animales

#### Generar reporte
```
1. Click: Módulo REPORTES
2. Elige tipo de reporte
3. Configura:
   - Rango de fechas
   - Finca(s)
   - Filtros adicionales
4. Click: "Generar"
5. Opción: Ver en pantalla o descargar Excel
```

---

### 8. CONFIGURACIÓN

**¿Qué es?**  
Datos maestros de tu sistema.

#### Maestros disponibles:
- **Fincas**: Tus unidades de producción
- **Razas**: Razas ganaderas disponibles
- **Empleados**: Personal que trabaja
- **Potreros**: Sectores/pastos
- **Calidades**: Clasificación de animales
- **Diagnósticos**: Enfermedades/problemas
- **Medicinas**: Inventario de medicinas
- **Destinos de venta**: Tipos de venta

#### Agregar maestro
```
1. Click: Módulo CONFIGURACIÓN
2. Click: Datos Maestros
3. Elige tipo (ej: Razas)
4. Button: "Nuevo"
5. Completa datos
6. Click: "Guardar"
```

---

## 🔄 Flujos de Trabajo Comunes

### Flujo 1: Comprar 10 animales nuevos

```
PASO 1: Registrar animales
├─ Módulo ANIMALES → Nuevo animal
├─ Llena datos de cada uno
├─ Finca: Tu finca principal
├─ Potrero: Asigna a potrero de cuarentena
└─ Guarda cada animal

PASO 2: Configurar potreros
├─ Módulo CONFIGURACIÓN
├─ Potreros → Nuevo potrero
├─ Nombre: "Cuarentena nuevos"
└─ Guardar

PASO 3: Asignar medicinas
├─ Módulo SALUD
├─ Para cada animal:
│  ├─ Nuevo tratamiento
│  ├─ Diagnóstico: "Prevención"
│  ├─ Producto: Vitaminas
│  └─ Guardar
└─ Listo, animales bajo control

RESULTADO: 10 animales registrados, en cuarentena, bajo tratamiento preventivo
```

---

### Flujo 2: Registrar parto y producto

```
PASO 1: Verificar gestante
├─ Módulo REPRODUCCIÓN
├─ Próximos partos
├─ Busca la gestante
└─ Verifica fecha estimada

PASO 2: Registrar parto
├─ Módulo ANIMALES
├─ Ficha de la madre
├─ Click: "Nuevo parto"
├─ Llena:
│  ├─ Fecha del parto
│  ├─ Sexo del producto
│  ├─ Peso
│  └─ Observaciones
└─ Guardar

PASO 3: Registrar cría
├─ Módulo ANIMALES
├─ Nuevo animal
├─ Madre: (auto-llena)
├─ Tipo: Ternero/Ternera
├─ Fecha nacimiento: (hoy)
└─ Guardar

PASO 4: Cambiar estado madre
├─ Ficha de madre
├─ Estado: Activa
├─ Próximo servicio: en 60 días
└─ Guardar

RESULTADO: Parto registrado, cría en el sistema, madre lista para nuevo ciclo
```

---

### Flujo 3: Vender un animal

```
PASO 1: Marcar como vendido
├─ Módulo ANIMALES
├─ Selecciona animal
├─ Estado: VENDIDO
└─ Guardar

PASO 2: Registrar venta
├─ Módulo VENTAS
├─ Nuevo registro
├─ Selecciona el animal
├─ Llena:
│  ├─ Fecha
│  ├─ Precio
│  ├─ Comprador
│  └─ Concepto
└─ Guardar

PASO 3: Generar reporte
├─ Módulo REPORTES
├─ Reporte de ventas
├─ Rango: hoy
├─ Ver ganancia del día
└─ Exportar a Excel

RESULTADO: Animal marcado como vendido, venta registrada, reporte actualizado
```

---

## 💡 Tips y Trucos

### Tip 1: Búsqueda rápida
```
• En cualquier lista, presiona Ctrl+F
• Escribe código del animal
• Sistema filtra en tiempo real
```

### Tip 2: Exportar a Excel
```
• Cualquier reporte o tabla
• Click derecho → "Exportar"
• Se abre Excel automáticamente
• Puedes imprimir desde ahí
```

### Tip 3: Atajos de teclado
```
Ctrl+N     Nueva entrada
Ctrl+E     Editar
Ctrl+G     Guardar
Ctrl+Q     Salir
Ctrl+F     Buscar
```

### Tip 4: Copia de seguridad
```
• Sistema hace backup automático cada día
• Ubicación: C:\Users\[tu usuario]\FincaFacil\backup\
• Puedes restaurar desde Módulo AJUSTES
```

### Tip 5: Calendario
```
• Todas las fechas tienen calendario
• Click en campo de fecha
• Elige fecha visualmente
```

---

## 🔧 Solución de Problemas

### Problema: "Base de datos bloqueada"
**Solución:**
1. Cierra FincaFácil completamente
2. Espera 30 segundos
3. Abre nuevamente

### Problema: "Módulo no carga"
**Solución:**
1. Módulo → Reload (icono recarga)
2. Si persiste: Módulo AJUSTES → Reparar sistema

### Problema: "No puedo crear usuario"
**Solución:**
1. Verifica tener permisos de administrador
2. Menú: Ajustes → Permisos → Administrador

### Problema: "Reporte no muestra datos"
**Solución:**
1. Verifica rango de fechas
2. Verifica finca seleccionada
3. Click: "Refrescar datos"

### Problema: "Error de conexión"
**Solución:**
1. Verifica conexión a internet (opcional)
2. Reinicia la aplicación
3. Si persiste: Contacta soporte

---

## 📚 Glosario Ganadero

### Términos básicos:

**Vaca**: Hembra bovina adulta, madre

**Novilla**: Hembra joven que no ha parido

**Toro**: Macho adulto reproductor

**Ternero/Ternera**: Animal joven (0-1 año)

**Gestante**: Hembra embarazada

**Preñez**: Embarazo

**Parto**: Nacimiento

**Servicio**: Monta o inseminación

**IA** (Inseminación Artificial): Reproducción técnica

**Monta natural**: Reproducción tradicional

**Potrero**: Pastura o sector

**Lote**: Grupo de animales

**Condición corporal**: Estado físico (delgado, normal, gordo)

**Calostro**: Primera leche de la madre

**Producción**: Litros de leche diarios

**Rendimiento**: % de producción útil

**Composición**: Proteína, grasa, lactosa en la leche

---

## 📞 Soporte y Ayuda

### Recursos disponibles:

- **Manual completo**: Este documento
- **Tour interactivo**: Help → Iniciar Tour
- **Video tutoriales**: www.fincafacil.com/videos
- **FAQ**: www.fincafacil.com/faq
- **Email soporte**: jfburitica97@gmail.com
- **Teléfono**: 3013869653
- **Forum**: www.fincafacil.com/forum

### Horarios de soporte:
```
Lunes a Viernes: 8:00 AM - 5:00 PM
Sábados: 9:00 AM - 12:00 PM
(Hora local)
```

---

## ✅ Checklist para Empezar

- [ ] Instalación completada
- [ ] Primera configuración (finca, empleados)
- [ ] Datos maestros completos (razas, potreros)
- [ ] Tour interactivo completado
- [ ] Primer animal registrado
- [ ] Dashboard revisado
- [ ] Primer pesaje registrado
- [ ] Contacto de soporte guardado

**¡Listo!** Ya puedes usar FincaFácil completamente.

---

**Versión del manual**: 2.0  
**Fecha de actualización**: 9 Diciembre 2025  
**Próxima revisión**: Diciembre 2025

Para reportar errores o sugerencias: **feedback@fincafacil.com**
