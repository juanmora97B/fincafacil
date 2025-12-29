# MANUAL OPERATIVO FINCAFÁCIL
## Guía Completa para Operación Sin Asistencia Técnica

**Versión:** 1.0  
**Fecha:** 28 de diciembre de 2024  
**Audiencia:** Operadores, Administradores, Propietarios de finca  
**Objetivo:** Operar el sistema sin dependencia del desarrollador

---

## 📖 ÍNDICE

1. [Inicio Rápido](#inicio-rápido)
2. [Problemas Comunes y Soluciones](#problemas-comunes-y-soluciones)
3. [Interpretación de Alertas](#interpretación-de-alertas)
4. [Procedimientos de Backup](#procedimientos-de-backup)
5. [Checklists Operativos](#checklists-operativos)
6. [Mantenimiento Preventivo](#mantenimiento-preventivo)
7. [Procedimientos de Emergencia](#procedimientos-de-emergencia)
8. [Contactos y Escalamiento](#contactos-y-escalamiento)

---

## 🚀 INICIO RÁPIDO

### Arranque Diario del Sistema

1. **Abrir FincaFácil**
   - Hacer doble clic en el ícono del escritorio
   - Esperar 5-10 segundos para que cargue completamente
   - Verificar que aparece la pantalla principal con el dashboard

2. **Verificación Rápida (2 minutos)**
   - ✅ Dashboard muestra datos actualizados
   - ✅ No hay alertas rojas en la parte superior
   - ✅ Fecha y hora del sistema son correctas
   - ✅ Última sincronización muestra "Hoy"

3. **Si algo no se ve bien:**
   - NO CERRAR inmediatamente
   - Leer el mensaje de alerta completo
   - Seguir las instrucciones de este manual
   - Si es crítico, consultar sección "Emergencias"

---

## 🔧 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "Database is Locked" (Base de Datos Bloqueada)

**Síntomas:**
- Error: "database is locked"
- Operaciones muy lentas
- Timeout al guardar

**Causa:**
Hay múltiples instancias de FincaFácil abiertas o un proceso no se cerró correctamente.

**Solución (10 minutos):**

1. **Cerrar TODAS las ventanas de FincaFácil**
   - Verificar barra de tareas
   - Buscar ventanas minimizadas
   - Cerrar cualquier reporte abierto

2. **Esperar 30 segundos**
   - Contar hasta 30 mentalmente
   - No apurar el proceso

3. **Reabrir FincaFácil**
   - Doble clic en ícono del escritorio
   - Esperar carga completa

4. **Verificar**
   - Intentar guardar un registro de prueba
   - Si funciona, problema resuelto

**Si el problema persiste:**
1. Verificar que no hay múltiples instancias en Administrador de Tareas:
   - Presionar `Ctrl + Shift + Esc`
   - Buscar "FincaFacil.exe"
   - Si hay más de uno, cerrar todos y reiniciar

2. Reiniciar la computadora

3. Si aún persiste después de reiniciar, contactar soporte técnico

**Prevención:**
- No abrir múltiples ventanas de FincaFácil
- Cerrar correctamente el programa (no forzar cierre)
- Considerar migración a PostgreSQL si es recurrente

---

### Problema 2: Datos Faltantes en Reportes

**Síntomas:**
- Gráfico sin datos
- Reporte muestra "0 registros"
- Producción aparece vacía
- Dashboard sin información

**Causa:**
Los filtros están demasiado restrictivos o el período seleccionado no tiene datos.

**Solución (5 minutos):**

1. **Limpiar Filtros**
   - Ir al módulo donde falta data (ej: Producción)
   - Buscar botón "Limpiar Filtros" o "Reset"
   - Hacer clic

2. **Seleccionar Período Amplio**
   - Cambiar rango de fechas a "Últimos 30 días"
   - Si aún no aparece data, probar "Últimos 90 días"

3. **Verificar Animales Activos**
   - Ir a módulo de Animales
   - Verificar que hay animales con estado "Activo"
   - Si todos están "Vendidos" o "Muertos", no habrá data reciente

4. **Revisar Filtros Ocultos**
   - Algunos módulos tienen filtros avanzados
   - Verificar que no esté filtrado por lote/finca específica
   - Asegurarse que "Mostrar todos" está seleccionado

**Verificación:**
- Los datos deben aparecer inmediatamente
- Si no aparecen, podría ser un período genuinamente sin registros

**Prevención:**
- Documentar períodos sin actividad (ej: vacaciones, sequía)
- Revisar filtros antes de generar reportes importantes
- Mantener hábito de registro diario

---

### Problema 3: Alerta Crítica No Desaparece

**Síntomas:**
- Alerta roja persistente en dashboard
- Notificación constante
- Mensaje de "CRITICO" no se va

**Causa:**
La condición subyacente no se ha resuelto, o el umbral está mal configurado.

**Solución (15 minutos):**

1. **Leer Explicación Completa**
   - Hacer clic en la alerta para expandir
   - Leer TODA la explicación (no solo el título)
   - La alerta incluye 5 pasos de razonamiento

2. **Identificar Tipo de Problema**

   **Si es Falso Positivo:**
   - La alerta dice "crítico" pero no es urgente
   - Ejemplo: "Animal sin registro 8 días" pero está de vacaciones
   - **Acción:** Ajustar umbral en Configuración

   **Si es Real:**
   - El problema existe y requiere acción
   - Ejemplo: "Caída producción 40%" y efectivamente bajó
   - **Acción:** Tomar la acción recomendada

3. **Ajustar Umbral (si es falso positivo)**
   ```
   Dashboard → Configuración → Alertas → [Nombre de Alerta]
   - Cambiar umbral de 7 días a 14 días
   - Guardar cambios
   - Verificar que alerta desaparece
   ```

4. **Tomar Acción (si es real)**
   - Seguir recomendación específica de la alerta
   - Documentar acción tomada en notas
   - Marcar alerta como "Revisada"

5. **Documentar Decisión**
   - Ir a módulo de Incidentes
   - Crear incidente con tipo "UX"
   - Describir por qué se ajustó umbral o qué acción se tomó

**Prevención:**
- Revisar umbrales mensualmente
- Ajustar según realidad de la finca
- No ignorar alertas, siempre investigar

---

### Problema 4: Sistema Lento / Performance Degradado

**Síntomas:**
- Dashboard tarda >10 segundos en cargar
- Guardado de registros es lento
- Aplicación "se cuelga"
- Cursor en modo "cargando" constantemente

**Causa:**
Exceso de datos sin filtrar, falta de mantenimiento, o recursos de PC insuficientes.

**Solución Inmediata (5 minutos):**

1. **Cerrar Programas No Esenciales**
   - Cerrar navegador web
   - Cerrar correo electrónico
   - Dejar solo FincaFácil abierto

2. **Aplicar Filtros de Fecha**
   - En cada módulo, seleccionar "Últimos 30 días"
   - No intentar cargar "Todos los registros" si hay >10,000

3. **Reiniciar FincaFácil**
   - Cerrar y volver a abrir
   - A veces libera memoria

**Solución a Mediano Plazo (mensual):**

1. **Verificar Tamaño de Base de Datos**
   ```
   - Ir a C:\Users\[Usuario]\AppData\Local\FincaFacil\
   - Buscar archivo "fincafacil.db"
   - Si >500 MB, considerar limpieza
   ```

2. **Ejecutar Mantenimiento de BD**
   ```
   Dashboard → Herramientas → Mantenimiento → Optimizar Base de Datos
   - Hacer clic en "Ejecutar"
   - Esperar 2-5 minutos
   - Reiniciar aplicación
   ```

3. **Archivar Datos Antiguos**
   ```
   Dashboard → Herramientas → Archivar → Datos >2 años
   - Seleccionar año a archivar
   - Sistema crea backup antes de archivar
   - Libera espacio en BD activa
   ```

**Verificación de Hardware:**
- RAM recomendada: 8 GB mínimo
- Disco duro: SSD preferido (10x más rápido que HDD)
- Si PC tiene <4 GB RAM, considerar upgrade

---

### Problema 5: Reporte PDF No Se Genera

**Síntomas:**
- Error al exportar PDF
- Archivo vacío o corrupto
- Botón "Exportar" no responde
- Timeout

**Causa:**
Falta librería reportlab, datos muy grandes, o permisos de archivo.

**Solución (10 minutos):**

1. **Verificar Librería ReportLab**
   - Abrir terminal/consola
   - Ejecutar: `pip list | findstr reportlab`
   - Si no aparece, instalar: `pip install reportlab`

2. **Reducir Datos a Exportar**
   - Si reporte tiene >1000 páginas, dividir
   - Seleccionar rango de fechas más corto
   - Ejemplo: En vez de "Todo el año", hacer "Por trimestre"

3. **Verificar Permisos de Carpeta**
   - Reporte se guarda en: `C:\Users\[Usuario]\Documents\FincaFacil\Reportes\`
   - Verificar que carpeta existe
   - Verificar que tienes permiso de escritura

4. **Generación en Background (si reporte es grande)**
   - Seleccionar opción "Generar en segundo plano"
   - Continuar trabajando mientras se genera
   - Recibirás notificación cuando termine

**Si nada funciona:**
- Exportar a Excel primero (.xlsx)
- Abrir en Excel
- Guardar como PDF desde Excel

**Prevención:**
- Validar dependencias en instalación
- Paginar reportes grandes
- Mantener reportes <100 páginas cuando sea posible

---

## 🚨 INTERPRETACIÓN DE ALERTAS

FincaFácil usa 4 niveles de severidad. Cada alerta incluye:
1. **Título:** Qué pasó
2. **Descripción:** Por qué es problema
3. **Explicación 5-pasos:** Razonamiento completo (FASE 10)
4. **Recomendación:** Qué hacer
5. **Alternativas:** Otras opciones

### Nivel 1: BAJA (Verde) 📗
**Significado:** Información, no requiere acción inmediata  
**Ejemplo:** "Animal sin registro de peso en 14 días"  
**Acción:** Revisar cuando tengas tiempo, no urgente  
**Frecuencia esperada:** 5-10 por semana

### Nivel 2: MEDIA (Amarillo) 📙
**Significado:** Atención requerida en 24-48 horas  
**Ejemplo:** "Producción promedio bajó 15%"  
**Acción:**  
- Leer explicación completa
- Investigar causa (¿cambio de alimento?, ¿clima?)
- Documentar hallazgos
- Tomar acción correctiva si corresponde

**Frecuencia esperada:** 2-5 por semana

### Nivel 3: ALTA (Naranja) 📙
**Significado:** Acción requerida HOY  
**Ejemplo:** "Calidad de datos degradada, score 6.2/10"  
**Acción:**  
- Dejar lo que estás haciendo
- Leer alerta completa
- Seguir recomendación específica
- Resolver en <4 horas
- Documentar solución

**Frecuencia esperada:** 0-2 por semana  
**Si hay >3 alertas ALTAS a la vez:** Escalar a administrador

### Nivel 4: CRITICA (Rojo) 📕
**Significado:** URGENTE - Sistema en riesgo o datos en peligro  
**Ejemplo:** "Base de datos con errores, 45 registros afectados"  
**Acción:**  
- **DETENER operaciones inmediatamente**
- Leer alerta completa
- Seguir procedimiento de emergencia (ver sección específica)
- NO ignorar ni postponer
- Contactar soporte si no puedes resolver en 30 minutos

**Frecuencia esperada:** 0-1 por mes  
**Si hay alerta CRITICA:** Es genuinamente crítico, actuar YA

---

### Alertas con Explicación de 5 Pasos (FASE 10)

Cada alerta incluye razonamiento completo:

**Paso 1: Observación**
- Qué vio el sistema exactamente
- Números y datos concretos

**Paso 2: Análisis**
- Por qué eso es un problema
- Contexto histórico

**Paso 3: Impacto**
- Qué puede pasar si no se resuelve
- Consecuencias potenciales

**Paso 4: Recomendación**
- Qué hacer específicamente
- Pasos concretos y medibles

**Paso 5: Alternativas**
- Otras opciones disponibles
- Casos especiales

**Ejemplo Real:**
```
ALERTA: Producción Baja Detectada

Paso 1 - Observación:
La producción promedio de la vaca #142 bajó de 22 L/día a 15 L/día 
en los últimos 7 días (caída de 32%).

Paso 2 - Análisis:
Una caída >30% en <14 días es anormal y sugiere problema de salud, 
nutrición o estrés. El histórico muestra que esta vaca mantenía 
20-23 L/día consistentemente en los últimos 3 meses.

Paso 3 - Impacto:
Si no se atiende, la producción podría bajar más. Pérdida estimada: 
7 L/día × $1,500/L = $10,500/día. En un mes: $315,000.

Paso 4 - Recomendación:
1. Examinar salud de la vaca (temperatura, apetito, comportamiento)
2. Revisar calidad del alimento reciente
3. Verificar condiciones del establo (limpieza, ventilación)
4. Si no mejora en 3 días, llamar veterinario

Paso 5 - Alternativas:
- Si es época de celo, producción baja es normal (3-4 días)
- Si hubo cambio de alimento reciente, dar 7 días de adaptación
- Si todas las vacas bajaron, revisar sistema completo (agua, clima)
```

---

## 💾 PROCEDIMIENTOS DE BACKUP

### Backup Automático Diario

FincaFácil hace backup automático todos los días a las 2:00 AM.

**Verificación Diaria (1 minuto):**
```
1. Abrir carpeta: C:\Users\[Usuario]\AppData\Local\FincaFacil\Backups\
2. Verificar que existe archivo con fecha de HOY
   Ejemplo: fincafacil_backup_20240115.db
3. Verificar tamaño >1 MB
```

**Si NO hay backup de hoy:**
- Hacer backup manual inmediatamente
- Revisar si PC estuvo encendida a las 2 AM
- Considerar cambiar hora de backup a horario laboral

---

### Backup Manual (Hazlo Semanalmente)

**Procedimiento (5 minutos):**

1. **Abrir FincaFácil**
   ```
   Dashboard → Herramientas → Backup → Backup Manual
   ```

2. **Seleccionar Ubicación**
   - Recomendado: USB externa o nube (Dropbox/Google Drive)
   - NO guardar solo en misma PC

3. **Nombrar Backup**
   ```
   Formato: FincaFacil_YYYYMMDD_Manual
   Ejemplo: FincaFacil_20240115_Manual.db
   ```

4. **Ejecutar**
   - Hacer clic en "Crear Backup"
   - Esperar mensaje "Backup completado exitosamente"
   - Verificar archivo en ubicación seleccionada

5. **Verificación**
   - Verificar tamaño >1 MB
   - Anotar en bitácora: "Backup manual [fecha]"

---

### Restauración desde Backup

**CUÁNDO USAR:**
- Base de datos corrupta
- Datos perdidos/borrados accidentalmente
- Necesitas volver a estado anterior

**IMPORTANTE:** Restaurar borra datos actuales. Hacer backup primero.

**Procedimiento (10 minutos):**

1. **Hacer Backup del Estado Actual (por si acaso)**
   - Seguir procedimiento de backup manual
   - Nombrar: "PreRestauracion_[fecha]"

2. **Cerrar FincaFácil Completamente**
   - Cerrar todas las ventanas
   - Verificar que no hay procesos abiertos

3. **Restaurar**
   ```
   Opción A (desde UI):
   - Abrir FincaFácil
   - Dashboard → Herramientas → Backup → Restaurar
   - Seleccionar archivo .db a restaurar
   - Confirmar (leer advertencia)
   - Esperar "Restauración exitosa"
   - Reiniciar aplicación

   Opción B (manual):
   - Ir a: C:\Users\[Usuario]\AppData\Local\FincaFacil\
   - Renombrar "fincafacil.db" a "fincafacil_old.db"
   - Copiar backup seleccionado
   - Renombrar copia a "fincafacil.db"
   - Abrir FincaFácil
   ```

4. **Verificar**
   - Revisar que datos se ven correctos
   - Verificar fecha de última modificación
   - Hacer prueba de guardado

---

### Estrategia de Backup Recomendada (Regla 3-2-1)

**3 Copias:**
1. Base de datos activa (C:\Users\...\FincaFacil\)
2. Backup automático diario (misma carpeta)
3. Backup manual semanal (USB o nube)

**2 Tipos de Medios:**
1. Disco duro de PC
2. USB externa o nube

**1 Copia Offsite:**
- Nube (Dropbox, Google Drive, OneDrive)
- O USB que llevas a casa

---

## ✅ CHECKLISTS OPERATIVOS

### Checklist Diario (10 minutos al inicio del día)

- [ ] **Verificar Dashboard**
  - Dashboard carga correctamente
  - Datos se ven actualizados
  - No hay alertas CRITICAS

- [ ] **Revisar Alertas Pendientes**
  - Leer nuevas alertas
  - Marcar como "Revisadas" las leídas
  - Escalar ALTAS o CRITICAS si no puedes resolver

- [ ] **Verificar Backup**
  - Existe archivo backup de ayer
  - Tamaño >1 MB
  - Si falta, hacer backup manual

- [ ] **Sincronización**
  - Última sincronización muestra "Hoy"
  - Si no, verificar conexión

---

### Checklist Semanal (30 minutos cada lunes)

- [ ] **Revisar Usuarios de Alto Riesgo (FASE 14)**
  ```
  Dashboard → Riesgos → Usuarios Alto Riesgo
  - Ver usuarios con score >60
  - Revisar patrones detectados
  - Tomar acción si score >80
  ```

- [ ] **Backup Manual**
  - Hacer backup manual
  - Guardar en USB o nube
  - Verificar backup se creó correctamente

- [ ] **Validar Integridad de Datos Críticos**
  ```
  Dashboard → Data Quality → Ver Score
  - Score debe ser >7.5
  - Si <7, investigar causa
  - Revisar registros con problemas
  ```

- [ ] **Revisar Logs de Errores UX (FASE 13)**
  ```
  Dashboard → UX Guardrails → Errores UX
  - Ver errores de última semana
  - Identificar patrones repetitivos
  - Educar usuarios si es necesario
  ```

- [ ] **Revisar Incidentes Abiertos**
  ```
  Dashboard → Incidentes → Activos
  - Cerrar incidentes resueltos
  - Actualizar estado de in-progress
  - Escalar si >3 días sin avance
  ```

---

### Checklist Mensual (2 horas primer viernes del mes)

- [ ] **Generar Reporte Mensual de Riesgos (FASE 14)**
  ```
  Dashboard → Riesgos → Reporte Mensual
  - Seleccionar mes anterior
  - Revisar estadísticas
  - Identificar tendencias
  - Documentar acciones preventivas
  ```

- [ ] **Revisar y Cerrar Incidentes Resueltos**
  ```
  Dashboard → Incidentes → Resueltos
  - Confirmar que están realmente resueltos
  - Cerrar definitivamente
  - Agregar a Knowledge Base si es necesario
  ```

- [ ] **Actualizar Knowledge Base**
  ```
  Dashboard → Incidentes → Knowledge Base
  - Revisar incidentes recurrentes
  - Crear soluciones nuevas si aplica
  - Actualizar soluciones existentes
  ```

- [ ] **Validar Métricas de Calidad (FASE 8)**
  ```
  Dashboard → Data Quality → Métricas
  - Completeness score
  - Accuracy score
  - Consistency score
  - Todos deben ser >7.5
  ```

- [ ] **Revisar Configuración de Umbrales y Alertas**
  ```
  Dashboard → Configuración → Alertas
  - Revisar cada umbral
  - Ajustar según realidad del mes
  - Documentar cambios
  ```

- [ ] **Backup Manual Completo**
  - Hacer backup manual
  - Guardar en 2 ubicaciones (USB + nube)
  - Etiquetar como "Mensual [Mes]"

- [ ] **Revisar Performance del Sistema (FASE 9)**
  ```
  Dashboard → Métricas → Sistema
  - Tiempo de respuesta <2s
  - Uso de memoria <1 GB
  - Overhead AI <1%
  - Si >10% degradación, optimizar
  ```

---

## 🛠️ MANTENIMIENTO PREVENTIVO

### Mensual

**Optimizar Base de Datos (15 minutos):**
```
Dashboard → Herramientas → Mantenimiento → Optimizar BD
- Ejecutar optimización
- Esperar 5-10 minutos
- Reiniciar aplicación
- Verificar mejora en velocidad
```

**Limpiar Logs Antiguos (5 minutos):**
```
- Ir a: C:\Users\[Usuario]\AppData\Local\FincaFacil\logs\
- Borrar archivos >3 meses
- Dejar últimos 3 meses
```

---

### Trimestral

**Archivar Datos Antiguos (30 minutos):**
```
Dashboard → Herramientas → Archivar
- Seleccionar datos >1 año
- Sistema crea backup automáticamente
- Datos archivados siguen disponibles pero no ralentizan sistema
```

**Revisar Espacio en Disco (10 minutos):**
```
- Verificar que queda >10 GB libre en C:\
- Si <10 GB, limpiar archivos temporales
- Considerar mover backups a disco externo
```

---

### Anual

**Auditoría Completa (4 horas):**
- Revisar todos los módulos
- Validar configuraciones
- Actualizar documentación interna
- Capacitar nuevos usuarios
- Considerar actualizaciones de software

**Renovar Backups Offsite:**
- Crear backup maestro anual
- Guardar en ubicación segura física
- Etiquetar: "FincaFacil_MasterBackup_[Año]"

---

## 🚨 PROCEDIMIENTOS DE EMERGENCIA

### Emergencia Nivel 1: Base de Datos Corrupta

**Señales:**
- Error: "database disk image is malformed"
- Aplicación no abre
- Datos desaparecieron

**Acción Inmediata (30 minutos):**

1. **NO PÁNICO**
   - Los backups existen
   - Datos se pueden recuperar

2. **Verificar Backups Disponibles**
   ```
   - Ir a: C:\Users\[Usuario]\AppData\Local\FincaFacil\Backups\
   - Identificar backup más reciente
   - Verificar tamaño >1 MB
   ```

3. **Restaurar desde Backup**
   - Seguir procedimiento de restauración (ver sección Backup)
   - Usar backup más reciente

4. **Verificar Restauración**
   - Abrir FincaFácil
   - Verificar que datos se ven correctos
   - Hacer prueba de guardado

5. **Documentar Incidente**
   ```
   Dashboard → Incidentes → Nuevo
   - Tipo: ERROR
   - Severidad: CRITICA
   - Descripción completa de qué pasó
   - Solución aplicada
   ```

6. **Contactar Soporte**
   - Reportar incidente
   - Enviar logs si están disponibles

---

### Emergencia Nivel 2: Pérdida de Datos Recientes

**Señales:**
- Registros de hoy no aparecen
- Últimas entradas desaparecieron
- Backup más reciente es de hace 2 días

**Acción Inmediata (1 hora):**

1. **Evaluar Pérdida**
   - ¿Cuántos registros se perdieron?
   - ¿De qué período?
   - ¿Son recuperables de otra fuente?

2. **Verificar si Hay Exportaciones Recientes**
   ```
   - Ir a: C:\Users\[Usuario]\Documents\FincaFacil\Reportes\
   - Buscar Excel/PDF con datos recientes
   - Si existen, usar para re-ingreso manual
   ```

3. **Re-Ingresar Datos Manualmente (si es poco)**
   - Si son <50 registros, ingresar a mano
   - Marcar como "Re-ingresado post-incidente"
   - Documentar fuente original

4. **O Restaurar y Actualizar**
   - Restaurar backup más reciente
   - Ingresar solo datos faltantes
   - Verificar no hay duplicados

5. **Prevención Futura**
   - Aumentar frecuencia de backups a cada 4 horas
   - Configurar backup en nube automático
   - Considerar replicación en tiempo real

---

### Emergencia Nivel 3: Sistema No Responde / Se Cuelga

**Señales:**
- Aplicación congelada
- No responde a clics
- CPU al 100%

**Acción Inmediata (15 minutos):**

1. **Esperar 2 Minutos**
   - Podría ser operación lenta normal
   - No forzar cierre aún

2. **Si Sigue Congelado:**
   ```
   - Presionar Ctrl + Shift + Esc
   - Buscar "FincaFacil.exe"
   - Clic derecho → Finalizar tarea
   ```

3. **Esperar 30 Segundos**
   - Dejar que proceso termine completamente

4. **Reabrir FincaFácil**
   - Doble clic en ícono
   - Verificar que abre normalmente

5. **Si Vuelve a Pasar:**
   - Reiniciar computadora
   - Verificar espacio en disco
   - Revisar uso de memoria (debería ser <2 GB)

6. **Si Es Recurrente:**
   - Ejecutar optimización de BD
   - Aplicar filtros de fecha en módulos
   - Considerar archivar datos antiguos

---

### Emergencia Nivel 4: Datos Incorrectos / Inconsistentes

**Señales:**
- Producción muestra valores absurdos (ej: 500 L/día)
- Sumas no cuadran
- Reportes con números imposibles

**Acción Inmediata (1 hora):**

1. **NO MODIFICAR NADA**
   - No intentar "arreglar" manualmente
   - Podría empeorar el problema

2. **Hacer Backup del Estado Actual**
   - Backup manual inmediato
   - Nombrar: "PreCorreccion_[fecha]"

3. **Identificar Alcance del Problema**
   ```
   Dashboard → Data Quality → Ver Problemas
   - Revisar score de calidad
   - Identificar registros con issues
   - Anotar cantidad afectada
   ```

4. **Si Son Pocos Registros (<20):**
   - Corregir manualmente uno por uno
   - Documentar cambios
   - Verificar con fuente original (notas, cuadernos)

5. **Si Son Muchos (>20):**
   - NO intentar corregir manualmente
   - Contactar soporte técnico
   - Proporcionar backup "PreCorreccion"
   - Describir qué crees que pasó

6. **Prevención:**
   - Revisar validaciones de entrada
   - Capacitar usuarios en ingreso correcto
   - Activar modo NOVATO para nuevos usuarios (FASE 13)

---

## 📞 CONTACTOS Y ESCALAMIENTO

### Niveles de Escalamiento

#### Nivel 1: Auto-Resolución (0-30 minutos)
**Usar para:**
- Problemas comunes de este manual
- Alertas BAJAS y MEDIAS
- Dudas de operación normal

**Recursos:**
- Este manual
- Knowledge Base del sistema
- Tooltips del sistema (FASE 13)

---

#### Nivel 2: Administrador Interno (30 minutos - 4 horas)
**Usar para:**
- Alertas ALTAS
- Problemas que no están en el manual
- Decisiones de configuración
- Incidentes recurrentes

**Contacto:**
- Nombre: [Administrador Finca]
- Teléfono: [Número]
- Email: [Email]
- Horario: Lunes a Viernes 8 AM - 6 PM

---

#### Nivel 3: Soporte Técnico (4-24 horas)
**Usar para:**
- Alertas CRITICAS sin solución
- Base de datos corrupta
- Sistema no responde después de reiniciar
- Pérdida significativa de datos (>100 registros)
- Problemas de performance persistentes

**Contacto:**
- Email: soporte@fincafacil.com
- Teléfono: [Número soporte]
- WhatsApp: [Número]
- Horario: 24/7 para emergencias, horario laboral para consultas

**Información a Proporcionar:**
```
1. Descripción del problema
2. Cuándo empezó
3. Qué se ha intentado
4. Logs si están disponibles:
   C:\Users\[Usuario]\AppData\Local\FincaFacil\logs\latest.log
5. Screenshot del error (si aplica)
```

---

#### Nivel 4: Desarrollador Original (>24 horas)
**Usar SOLO para:**
- Bugs del sistema
- Nuevas funcionalidades requeridas
- Migraciones mayores
- Capacitación avanzada

**Proceso:**
1. Primero contactar Soporte Técnico
2. Soporte evalúa y escala si es necesario
3. NO contactar directo al desarrollador para operación diaria

---

## 📚 RECURSOS ADICIONALES

### Documentación de Referencia

- **FASE_13_UX_GUARDRAILS_COMPLETADA.md:** Modos de usuario y protecciones
- **FASE_14_RISK_MANAGEMENT_COMPLETADA.md:** Scoring de riesgo y patrones
- **FASE_15_INCIDENT_MANAGEMENT_COMPLETADA.md:** Sistema de incidentes

### Videos de Capacitación (si existen)

- Inicio rápido (5 min)
- Interpretación de alertas (10 min)
- Procedimientos de backup (8 min)
- Resolución de problemas comunes (15 min)

---

## 📝 BITÁCORA DE OPERACIÓN

Se recomienda mantener una bitácora física o digital con:

**Registro Diario:**
```
Fecha: [DD/MM/YYYY]
Operador: [Nombre]
Hora inicio: [HH:MM]

Verificaciones:
[ ] Dashboard OK
[ ] Backup existe
[ ] Sin alertas críticas

Incidentes (si hubo):
- [Descripción breve]
- [Acción tomada]
- [Resultado]

Notas adicionales:
[Cualquier cosa relevante]

Hora fin: [HH:MM]
Firma: ___________
```

---

## ✅ CERTIFICACIÓN DE LECTURA

Al terminar de leer este manual, cada operador debe:

1. Leer el manual completo (estimado: 45 minutos)
2. Practicar 1 backup manual
3. Practicar 1 búsqueda en Knowledge Base
4. Identificar dónde están los backups en su PC
5. Anotar contactos de escalamiento

**Confirmación:**
```
Yo, [Nombre], confirmo que leí y comprendí el Manual Operativo FincaFácil.

Fecha: ___________
Firma: ___________
```

---

## 🎯 OBJETIVO FINAL

**Este manual te hace autosuficiente.**

- ✅ 90% de problemas resuelves sin ayuda
- ✅ Sabes cuándo escalar y a quién
- ✅ Entiendes las alertas del sistema
- ✅ Puedes recuperarte de emergencias
- ✅ Mantienes el sistema saludable

**FincaFácil está diseñado para que lo operes sin depender de desarrolladores.**

---

*Manual Operativo FincaFácil v1.0*  
*Última actualización: 28 de diciembre de 2024*  
*Autor: Sistema FincaFácil - FASE 15*
