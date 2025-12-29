# GOBERNANZA Y ÉTICA - FINCAFACIL IA

**Fecha:** 28 de diciembre de 2024  
**Versión:** 1.0  
**Estado:** FINAL  
**Propósito:** Marco de gobernanza, ética y límites del AI para operación responsable  

---

## 📋 RESUMEN EJECUTIVO

Este documento establece las **reglas de operación responsable** del sistema FincaFácil, definiendo:

1. **Límites del AI:** Qué puede y NO puede decidir el sistema autónomamente
2. **Responsabilidad:** Quién es responsable de cada tipo de decisión
3. **Transparencia:** Cómo garantizamos explicabilidad total
4. **Ética:** Principios de uso justo, privado y seguro
5. **Gobernanza:** Marco operativo de supervisión y control

**Principio fundamental:** 
> **El AI es un ASISTENTE INTELIGENTE, no un DECISOR AUTÓNOMO.**  
> **Todas las decisiones críticas requieren aprobación humana.**

---

## 🚦 LÍMITES DEL AI: MATRIZ DE DECISIONES

### Nivel 1: DECISIONES AUTOMÁTICAS (AI autónomo)

El sistema **PUEDE decidir y ejecutar automáticamente**:

| Decisión | Fase | Límite | Ejemplo |
|----------|------|--------|---------|
| **Corrección datos formato** | FASE 8 | Formato, no valor | "01/13/2024" → "13/01/2024" |
| **Alerta BAJA generada** | FASE 9 | Solo notificar | "Temperatura fuera de rango histórico" |
| **Tooltip mostrado** | FASE 13 | UX mejorada | Explicar campo "Intervalo entre partos" |
| **Explicación generada** | FASE 10 | Solo informar | "Esta alerta se debe a..." |
| **Registro KB** | FASE 15 | Solo documentar | "Incidente #234 resuelto con solución X" |

**Justificación:** Decisiones de **bajo riesgo**, **reversibles** y que **no afectan operación**.

---

### Nivel 2: DECISIONES SUGERIDAS (AI asistido, humano decide)

El sistema **SUGIERE pero NO ejecuta**:

| Decisión | Fase | Requiere | Ejemplo |
|----------|------|----------|---------|
| **Corrección datos valor** | FASE 8 | Aprobación operador | "Peso 50kg → 500kg (probablemente typo)" |
| **Alerta MEDIA generada** | FASE 9 | Revisión en 2-4h | "3 vacas sin registro peso en 7 días" |
| **Patrón riesgo detectado** | FASE 14 | Revisión admin | "Usuario X con 5 overrides en 2 días" |
| **Recomendación simulación** | FASE 11 | Validación gerente | "Escenario B tiene ROI +15% vs actual" |
| **Insight BI generado** | FASE 37 | Interpretación humana | "Producción bajó 8% en Lote 3" |

**Justificación:** Decisiones de **riesgo medio**, **impacto moderado**, humano tiene **contexto adicional**.

---

### Nivel 3: DECISIONES CRÍTICAS (Humano decide, AI informa)

El sistema **INFORMA pero NO sugiere**:

| Decisión | Fase | Requiere | Ejemplo |
|----------|------|----------|---------|
| **Alerta CRÍTICA** | FASE 9 | Acción inmediata gerente | "10 animales sin registro 14+ días" |
| **Venta/descarte animal** | Core | Decisión propietario | AI solo muestra datos, no recomienda |
| **Cambio configuración sistema** | FASE 15 | Admin o desarrollador | Cambiar umbrales de alertas |
| **Modificación datos pasados** | FASE 8 | Auditoría + aprobación | Corregir registro histórico importante |
| **Inversión económica** | FASE 16 | Decisión financiera propietario | Basada en ROI pero humano decide |

**Justificación:** Decisiones **irreversibles**, **alto impacto económico**, requieren **juicio humano**.

---

### NIVEL 4: DECISIONES PROHIBIDAS (AI NUNCA decide)

El sistema **NUNCA** puede:

❌ **Borrar datos** sin autorización explícita  
❌ **Vender o transferir información** de la finca a terceros  
❌ **Modificar configuración de seguridad** (permisos, usuarios)  
❌ **Tomar decisiones clínicas veterinarias** (diagnósticos, tratamientos)  
❌ **Decisiones legales o regulatorias** (cumplimiento normativo)  
❌ **Modificar código en producción** sin validación humana  
❌ **Compartir datos entre fincas** sin consentimiento  

**Justificación:** Decisiones con **implicaciones legales**, **riesgo vital** o **privacidad crítica**.

---

## 👤 RESPONSABILIDAD: MATRIZ RACI

| Decisión | Operador | Admin | Gerente | Propietario | Sistema |
|----------|----------|-------|---------|-------------|---------|
| **Corregir typo formato** | I | I | I | I | **R** |
| **Corregir valor dato** | **R** | A | I | I | C |
| **Responder alerta BAJA** | **R** | A | I | I | C |
| **Responder alerta MEDIA** | **R** | **A** | I | I | C |
| **Responder alerta CRÍTICA** | I | **R** | **A** | I | C |
| **Vender animal** | I | C | **R** | **A** | I |
| **Configurar sistema** | I | **R** | A | I | C |
| **Invertir en sistema** | I | C | **R** | **A** | I |
| **Cambiar gobernanza** | I | I | C | **R** | I |

**Leyenda RACI:**
- **R** (Responsible): Ejecuta la tarea
- **A** (Accountable): Responsable final, aprueba
- **C** (Consulted): Consultado, provee input
- **I** (Informed): Informado del resultado

---

## 🔍 TRANSPARENCIA: GARANTÍAS DE EXPLICABILIDAD

### Principio de Caja de Cristal

> **"Todo lo que el sistema hace debe ser explicable en lenguaje humano."**

**Implementación (FASE 10):**

1. **Toda alerta tiene explicación**
   ```python
   {
       "mensaje": "Alerta: Peso anormal detectado",
       "explicacion": "El peso 850kg está 3σ sobre promedio (650kg ± 80kg)",
       "datos_usados": ["peso_actual", "peso_promedio", "desv_estandar"],
       "confianza": 95,
       "acciones_recomendadas": ["Verificar báscula", "Revisar animal"]
   }
   ```

2. **Todo cálculo AI es auditable**
   - FASE 8: Log de correcciones con razón
   - FASE 14: Log de detección de patrones de riesgo
   - FASE 16: Cada $COP tiene fórmula explícita

3. **Todo cambio es trazable**
   - Timestamp + usuario + acción
   - Antes / después
   - Razón del cambio

**Derecho del usuario:**
- Preguntar "¿Por qué?" y recibir respuesta clara
- Ver qué datos usó el sistema
- Revertir decisión si no está de acuerdo

---

## 🔒 PRIVACIDAD Y SEGURIDAD DE DATOS

### Principios

1. **Propiedad:** Los datos pertenecen 100% al propietario de la finca
2. **Aislamiento:** Datos de una finca NUNCA se mezclan con otra
3. **Acceso:** Solo usuarios autorizados ven datos sensibles
4. **Portabilidad:** Propietario puede exportar o eliminar datos en cualquier momento

### Clasificación de Datos

| Nivel | Tipo | Acceso | Ejemplo |
|-------|------|--------|---------|
| **PÚBLICO** | Configuración no sensible | Todos | Nombre finca (si autorizado) |
| **INTERNO** | Operacional | Operadores + Admin | Registros diarios, alertas |
| **CONFIDENCIAL** | Estratégico | Admin + Gerente + Propietario | ROI, valor económico |
| **CRÍTICO** | Legal/Financiero | Solo propietario | Datos fiscales, contratos |

### Medidas de Seguridad

- **Encriptación:** Base de datos SQLite con encriptación opcional
- **Backup:** Automático diario + offsite semanal (FASE 15)
- **Logs de auditoría:** Quién accedió qué y cuándo
- **Permisos granulares:** Acceso por rol (FASE 14)

### Cumplimiento Normativo

- **Ley 1581/2012 (Habeas Data Colombia):** Protección datos personales
- **Resolución 3651/2014 ICA:** Trazabilidad bovina
- **ISO 27001 (opcional):** Gestión seguridad información

---

## ⚖️ ÉTICA DE USO

### Código Ético FincaFácil

1. **No discriminación**
   - El AI NO puede sesgar por:
     - Tamaño finca (pequeño/grande)
     - Ubicación geográfica
     - Nivel educativo del operador
     - Recursos económicos
   - Todos los usuarios reciben el mismo nivel de servicio

2. **No manipulación**
   - El AI NO puede:
     - Ocultar información para forzar decisión
     - Exagerar alertas para crear dependencia
     - Sesgar recomendaciones por interés comercial

3. **Bienestar animal**
   - El sistema prioriza salud animal sobre productividad
   - Alertas de bienestar tienen prioridad alta
   - No recomienda prácticas perjudiciales

4. **Sostenibilidad**
   - Recomendaciones consideran impacto ambiental
   - Optimización incluye uso eficiente de recursos
   - No priorizar solo rentabilidad a corto plazo

5. **Transparencia comercial**
   - Si sistema recomienda producto/servicio externo → Declarar si hay comisión
   - Costo total del sistema debe ser claro
   - No costos ocultos

---

## 🎯 DETECCIÓN Y MITIGACIÓN DE SESGOS

### Fuentes Potenciales de Sesgo

| Sesgo | Fuente | Mitigación |
|-------|--------|------------|
| **Datos históricos** | Finca tiene historial de mala práctica | Validar contra benchmarks nacionales |
| **Algoritmo** | Modelo entrenado con fincas grandes | Validar con fincas pequeñas/medianas |
| **Interfaz** | UX difícil para usuarios poco técnicos | Tooltips + tours + KB (FASE 13) |
| **Acceso** | Solo gerentes acceden a insights | Democratizar dashboards por rol |

### Proceso de Auditoría de Sesgos

**Frecuencia:** Trimestral

**Checklist:**
- [ ] ¿Alertas se disparan más para fincas pequeñas? → Revisar umbrales
- [ ] ¿Usuarios con baja educación tienen más overrides? → Mejorar UX
- [ ] ¿Recomendaciones favorecen raza X sobre Y sin justificación? → Revisar modelo
- [ ] ¿Insights BI solo útiles para grandes productores? → Ampliar contextos

**Responsable:** Comité de Ética (ver siguiente sección)

---

## 🏛️ MARCO DE GOBERNANZA

### Estructura de Gobierno

```
┌──────────────────────────────────┐
│      PROPIETARIO FINCA           │
│  (Decisión final en todo)        │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│    COMITÉ DE ÉTICA (opcional)    │
│  - Propietario + Gerente + Admin │
│  - Revisa decisiones críticas    │
│  - Audita sesgos trimestralmente │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│    ADMINISTRADOR SISTEMA         │
│  - Configura reglas              │
│  - Gestiona usuarios             │
│  - Revisa alertas críticas       │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│       OPERADORES                 │
│  - Uso diario sistema            │
│  - Responden alertas bajas/medias│
│  - Registran datos               │
└──────────────────────────────────┘
```

### Reuniones de Gobierno

| Frecuencia | Participantes | Agenda |
|------------|--------------|--------|
| **Diaria** | Operadores | Revisar alertas, incidentes del día |
| **Semanal** | Admin + Operadores | Tendencias, ajustes operativos |
| **Mensual** | Gerente + Admin | Insights BI, decisiones estratégicas |
| **Trimestral** | Comité de Ética | Auditoría sesgos, ROI, mejoras |
| **Anual** | Propietario + Todos | Evaluación completa, roadmap |

---

## 📜 POLÍTICAS OPERATIVAS

### Política 1: Modificación de Datos Históricos

**Problema:** ¿Podemos cambiar registros pasados si encontramos error?

**Política:**
1. **Datos <30 días:** Admin puede corregir con log de auditoría
2. **Datos 30-90 días:** Requiere aprobación gerente + razón documentada
3. **Datos >90 días:** Requiere aprobación propietario + auditoría formal
4. **Nunca borrar:** Solo marcar como "corregido" (mantener historial)

**Justificación:** Balance entre corrección de errores y integridad histórica.

---

### Política 2: Compartir Datos con Terceros

**Problema:** ¿Podemos compartir datos de la finca con veterinario externo, consultor, ICA?

**Política:**
1. **Requiere consentimiento explícito** del propietario (por escrito o digital)
2. **Especificar qué datos** se comparten (no "todos")
3. **Especificar duración** del acceso (ej: 30 días)
4. **Log de auditoría:** Quién accedió qué y cuándo
5. **Revocable:** Propietario puede revocar acceso en cualquier momento

**Excepción:** Obligaciones legales (ej: ICA requiere trazabilidad) → No requiere consentimiento pero sí notificación.

---

### Política 3: Actualización del Sistema

**Problema:** ¿Cómo actualizamos el sistema sin interrumpir operación?

**Política:**
1. **Actualizaciones menores (bugfixes):** Automáticas con notificación
2. **Actualizaciones mayores (features):** Notificar 7 días antes, opción aplazar
3. **Cambios críticos (arquitectura):** Requiere aprobación admin + backup pre-actualización
4. **Rollback:** Siempre posible volver a versión anterior (máx 3 versiones)

**Ventana de mantenimiento:** Domingos 2-4 AM (mínimo impacto)

---

### Política 4: Incidentes Críticos

**Problema:** ¿Qué hacemos si sistema falla críticamente?

**Política (ver MANUAL_OPERATIVO_FINCAFACIL.md):**
1. **<5 min:** Auto-diagnóstico del sistema (FASE 15)
2. **5-30 min:** Operador intenta solución con KB
3. **30 min-4h:** Admin escala problema
4. **4-24h:** Soporte externo
5. **>24h:** Desarrollador interviene

**Comunicación:**
- Usuario siempre informado del estado
- ETA de resolución (best effort)
- Compensación si downtime >24h (SLA)

---

## 📊 MÉTRICAS DE GOBERNANZA

### KPIs Éticos (revisión trimestral)

| Métrica | Target | Actual (ejemplo) | Estado |
|---------|--------|------------------|--------|
| **Transparencia: % alertas con explicación** | 100% | 100% | ✅ |
| **Autonomía: % decisiones críticas sin aprobación** | 0% | 0% | ✅ |
| **Sesgo: Diferencia satisfacción pequeño vs grande** | <10% | 8% | ✅ |
| **Privacidad: # incidentes de fuga de datos** | 0 | 0 | ✅ |
| **Disponibilidad: % uptime sistema** | >99% | 99.2% | ✅ |
| **Adopción: % operadores usando sistema** | >80% | 85% | ✅ |
| **Confianza: % overrides sobre recomendaciones** | <20% | 18% | ✅ |

**Acción si métrica en rojo:** Reunión extraordinaria Comité de Ética.

---

## 🚨 ESCALAMIENTO DE DECISIONES ÉTICAS

### Casos Complejos

**Ejemplo 1:** Sistema recomienda descartar animal económicamente no viable pero con posibilidad de recuperación.

**Conflicto:** Rentabilidad vs bienestar animal

**Proceso:**
1. **Sistema informa** (no recomienda) ambas opciones con datos
2. **Gerente decide** basándose en valores de la finca
3. **Se documenta** decisión y razón
4. **No hay "decisión correcta"** - es decisión humana ética

---

**Ejemplo 2:** Usuario solicita ocultar datos para auditoría externa.

**Conflicto:** Privacidad vs transparencia legal

**Proceso:**
1. **Sistema NO permite** ocultar datos si hay obligación legal
2. **Admin consulta** políticas legales aplicables
3. **Si obligación legal existe:** Compartir datos mínimos necesarios
4. **Si no hay obligación:** Usuario decide pero se advierte consecuencias

---

**Ejemplo 3:** IA detecta que usuario está ingresando datos falsos sistemáticamente.

**Conflicto:** Confianza vs autonomía del usuario

**Proceso:**
1. **Sistema genera alerta** a admin (no bloquea usuario)
2. **Admin investiga:** ¿Error de comprensión o fraude intencional?
3. **Si error:** Capacitación adicional (FASE 13)
4. **Si fraude:** Decisión propietario (puede incluir despido)
5. **Sistema NO castiga** automáticamente - solo alerta

---

## 📖 DERECHOS DEL USUARIO

### Carta de Derechos FincaFácil

Todo usuario tiene derecho a:

1. **Saber:** Entender cómo funciona el sistema (FASE 10)
2. **Preguntar:** Pedir explicación de cualquier decisión
3. **Revertir:** Deshacer acción del sistema (si técnicamente posible)
4. **Apelar:** Cuestionar recomendación y proveer contexto adicional
5. **Exportar:** Obtener copia de todos sus datos en formato legible
6. **Eliminar:** Borrar sus datos si ya no usa el sistema (sujeto a obligaciones legales)
7. **Privacidad:** Saber quién accedió sus datos y cuándo
8. **No discriminación:** Recibir mismo servicio independiente de características personales
9. **Capacitación:** Acceder a documentación y soporte para usar sistema
10. **Voz:** Proponer mejoras y ser escuchado

### Ejercicio de Derechos

**Canal:** Email: soporte@fincafacil.co o Admin del sistema  
**Plazo respuesta:** 5 días hábiles  
**Costo:** Gratuito (incluido en licencia)  

---

## 🔄 PROCESO DE MEJORA CONTINUA

### Ciclo de Retroalimentación

```
┌─────────────────┐
│  USO DIARIO     │
│  (Operadores)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OBSERVACIÓN    │
│  (FASE 9 + 15)  │ ──────► ¿Patrón problemático?
└────────┬────────┘                │
         │                         │
         │ ◄───────────────────────┘
         ▼
┌─────────────────┐
│  ANÁLISIS       │
│  (Admin)        │ ──────► ¿Sesgo? ¿Bug? ¿Mejora UX?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DECISIÓN       │
│  (Comité Ética) │ ──────► Aprobar cambio
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  IMPLEMENTACIÓN │
│  (Desarrollador)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VALIDACIÓN     │
│  (Tests)        │ ──────► ¿Funciona? ¿Mejora métricas?
└────────┬────────┘
         │
         ▼
    [USO DIARIO]
```

**Frecuencia:** Ciclo completo cada 3-6 meses (FASE 12: Roadmap)

---

## 📚 REFERENCIAS Y RECURSOS

### Documentos Relacionados

| Documento | Propósito | Ubicación |
|-----------|-----------|-----------|
| **MANUAL_OPERATIVO_FINCAFACIL.md** | Operación diaria | Raíz proyecto |
| **FASE_10_EXPLAINABILITY_COMPLETADA.md** | Transparencia técnica | docs/ |
| **FASE_14_RISK_MANAGEMENT_COMPLETADA.md** | Gestión de riesgos | docs/ |
| **FASE_15_INCIDENT_MANAGEMENT_COMPLETADA.md** | Soporte y continuidad | docs/ |
| **FASE_16_VALUE_METRICS_COMPLETADA.md** | ROI y valor económico | Raíz proyecto |
| **EVOLUTION_ROADMAP.md** | Roadmap de mejoras | Raíz proyecto |

### Frameworks Éticos de Referencia

- **IEEE P7000™ Series:** Estándares de sistemas autónomos éticos
- **EU AI Act (2024):** Marco regulatorio AI en Europa
- **OECD AI Principles:** Principios de AI responsable
- **ISO/IEC 42001 (draft):** Gestión de sistemas AI

### Contactos

- **Soporte técnico:** soporte@fincafacil.co
- **Comité de Ética:** etica@fincafacil.co
- **Reportar sesgo/abuso:** reporte@fincafacil.co

---

## ✅ CHECKLIST DE CUMPLIMIENTO

### Para Administradores

- [ ] Matriz de decisiones configurada en sistema
- [ ] Roles y permisos asignados correctamente
- [ ] Backup automático funcionando (FASE 15)
- [ ] Logs de auditoría activos
- [ ] Políticas de privacidad comunicadas a usuarios
- [ ] KB con soluciones a problemas comunes (FASE 15)
- [ ] Reunión semanal de gobierno agendada

### Para Operadores

- [ ] Capacitación en límites del AI completada
- [ ] Conocen cómo apelar decisión del sistema
- [ ] Saben responder alertas BAJAS y MEDIAS
- [ ] Conocen proceso de escalamiento (Nivel 3 y 4)
- [ ] Tienen acceso a Manual Operativo

### Para Propietario/Gerente

- [ ] ROI del sistema revisado (FASE 16)
- [ ] Comité de Ética establecido (si aplica)
- [ ] Políticas de privacidad aprobadas
- [ ] Proceso de compartir datos con terceros definido
- [ ] SLA con proveedor del sistema acordado
- [ ] Revisión trimestral de métricas de gobernanza agendada

### Para Desarrolladores

- [ ] Todas las decisiones del AI son explicables (FASE 10)
- [ ] Tests de sesgo incluidos en suite de tests
- [ ] Logs de auditoría implementados
- [ ] Proceso de rollback funcional
- [ ] Documentación de gobernanza actualizada
- [ ] Alertas críticas requieren aprobación humana (validado)

---

## 🎉 CONCLUSIÓN

**Este documento NO es un manual técnico - es un CONTRATO ÉTICO entre el sistema y sus usuarios.**

### Compromisos de FincaFácil:

✅ **Nunca decidirá por ti** en temas críticos  
✅ **Siempre explicará** sus recomendaciones  
✅ **Protegerá tus datos** como si fueran propios  
✅ **No discriminará** por tamaño o recursos  
✅ **Priorizará bienestar animal** sobre rentabilidad pura  
✅ **Será auditable** en todo momento  
✅ **Mejorará continuamente** con tu feedback  

### Tu compromiso:

✅ **Usar el sistema responsablemente** (no ingresar datos falsos)  
✅ **Revisar alertas críticas** en tiempo y forma  
✅ **Reportar problemas** para mejorar el sistema  
✅ **Capacitar tu equipo** en uso ético  
✅ **Respetar privacidad** de datos de terceros  

---

**El AI es poderoso, pero la responsabilidad final siempre es humana.**

**FincaFácil es una herramienta para potenciar tu inteligencia - no para reemplazarla.**

---

*Documento revisado y aprobado como parte de FASE 17*  
*Última actualización: 28 de diciembre de 2024*  
*Próxima revisión: Marzo 2025*
