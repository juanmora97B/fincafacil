# RUNBOOK OPERATIVO FINCAFÁCIL v1.0

**Documento:** Manual operativo para administradores y operadores  
**Versión:** 1.0.0  
**Audiencia:** Administrador de sistemas, operadores técnicos  
**Última actualización:** 28 dic 2024

---

## 📋 TABLA DE CONTENIDOS

1. **Inicio rápido**
2. **Procedimientos operativos diarios**
3. **Troubleshooting**
4. **Escenarios de crisis**
5. **Mantenimiento programado**
6. **Contactos y escalamiento**

---

## 🚀 INICIO RÁPIDO (5 min)

### Verificación de Salud Diaria

**Antes de que operadores empiecen a trabajar:**

```bash
# Terminal del administrador
$ curl -f http://localhost:8000/health
{
  "status": "healthy",
  "uptime_hours": 24.5,
  "database": "connected",
  "services": {
    "data_quality": "ok",
    "observability": "ok",
    "risk_management": "ok"
  }
}
```

**Si el status NO es "healthy":**
- ⚠️ Ver sección **Troubleshooting** → **Base de datos no responde**
- ⚠️ Contactar soporte (ver Contactos)

### Acceso de Usuarios

**Operador (rol: operario)**
- URL: http://localhost:3000
- Usuario: nombre@finca.com
- Puede: Registrar animales, ver alertas, generar reportes
- No puede: Cambiar configuración, ver datos de otros usuarios

**Administrador (rol: admin)**
- URL: http://localhost:8000/admin
- Usuario: admin@fincafacil.com
- Puede: Configurar sistema, ver todos los datos, gestionar usuarios

---

## 🔄 PROCEDIMIENTOS OPERATIVOS DIARIOS

### P1: Revisar Alertas Críticas (cada 2h)

**Tiempo:** 5–10 minutos

**Pasos:**

1. Abre dashboard: http://localhost:8000/admin/alertas
2. Filtra por `nivel = CRITICA`
3. Para cada alerta:
   - Lee la explicación (FASE 10)
   - Verifica el animal/lote afectado
   - Notifica al operador responsable
   - Marca como "visto"

**Ejemplo:**
```
⚠️ ALERTA CRÍTICA
Animal: Vaca #42 (Hato "El Dorado")
Tipo: Producción anormalmente baja
Explicación: Producción cayó 40% vs promedio histórico. 
             Posibles causas: Enfermedad, manejo inadecuado, 
             problemas de ordeño
Acción sugerida: Examen veterinario urgente
Operador: notificado via SMS

Checkbox: ✓ Revisado
```

### P2: Backup Diario (cada 24h, 3 AM)

**Tiempo:** 30 segundos (automático)

**Verificación manual (si necesario):**

```bash
$ ls -lh database/backup/
-rw-r--r-- 1 root root 45M Dec 28 03:00 finca_20241228_0300.db

# Validar integridad
$ sqlite3 database/backup/finca_20241228_0300.db "SELECT COUNT(*) FROM animales;"
1250
```

**Si el backup está vacío o con 0 bytes:**
- ⚠️ Problema crítico
- Ejecutar backup manual:
  ```bash
  $ python scripts/backup_database.py --output database/backup/manual_$(date +%s).db
  ```
- Contactar soporte

### P3: Registro de Datos Diario

**Tiempo:** 15 min (al cierre del día)

**Checklist:**

- [ ] ¿Se registraron todos los ordeños?
  ```bash
  $ sqlite3 database/current/finca.db \
    "SELECT COUNT(*) FROM eventos WHERE tipo='ORDENO' AND fecha=TODAY();"
  ```
  
- [ ] ¿Se validaron pesos de animales?
  ```bash
  $ sqlite3 database/current/finca.db \
    "SELECT COUNT(*) FROM eventos WHERE tipo='PESO' AND validado=0;"
  # Si > 10, pedir validación manual
  ```

- [ ] ¿Hay alertas no revisadas?
  ```bash
  $ curl -s http://localhost:8000/admin/alertas?revisadas=false | jq '.total'
  ```
  Si > 0: Revisar P1 (Alertas)

---

## 🔧 TROUBLESHOOTING

### Problema 1: Sistema lento (response time > 1 seg)

**Síntomas:**
- Dashboard tarda > 3 seg en cargar
- Registrar un animal toma > 2 seg

**Diagnóstico (30 seg):**

```bash
# Paso 1: Ver qué queries son lentas
$ sqlite3 database/current/finca.db ".eqtiming on"
$ sqlite3 database/current/finca.db \
  "SELECT animal_id, COUNT(*) as eventos FROM eventos GROUP BY animal_id LIMIT 10;"
# Fíjate en el tiempo de ejecución

# Paso 2: Ver espacio en disco
$ df -h
# Si < 10% libre: ⚠️ problema crítico
```

**Soluciones:**

1. **Si disco lleno (< 10% libre):**
   ```bash
   # Comprimir logs viejos
   $ gzip logs/app_2024_11*.log
   # Limpiar backups viejos (guardar últimos 7)
   $ ls -1 database/backup/finca_* | head -n -7 | xargs rm
   ```

2. **Si queries lentas:**
   ```bash
   # Optimizar índices
   $ sqlite3 database/current/finca.db < scripts/optimize_indexes.sql
   # Reiniciar servicio
   $ systemctl restart fincafacil
   ```

3. **Si memoria alta:**
   ```bash
   # Ver memoria usada
   $ free -h
   # Reiniciar servicio (libera memoria caché)
   $ systemctl restart fincafacil
   ```

**Si nada funciona:** Contactar soporte + ejecutar ROLLBACK (P5)

---

### Problema 2: Base de datos bloqueada

**Síntomas:**
- Usuarios ven error: "database is locked"
- No pueden registrar datos
- Dashboard no carga

**Diagnóstico (15 seg):**

```bash
# Ver qué proceso está usando BD
$ lsof | grep finca.db
# o
$ sqlite3 database/current/finca.db ".open_new"
# Si falla: BD está locked

# Ver logs
$ tail -50 logs/app.log | grep -i "lock"
```

**Solución (2–5 min):**

1. **Opción A: Esperar (30–60 seg)**
   - A veces SQLite se desbloquea solo
   - Avisa a usuarios: "Sistema en mantenimiento breve (2 min)"

2. **Opción B: Reiniciar servicio**
   ```bash
   $ systemctl restart fincafacil
   # Esperar 10 seg
   $ curl -f http://localhost:8000/health
   # Si health = "healthy": ✅ Resuelto
   ```

3. **Opción C: Usar backup (último recurso)**
   - Si no se desbloquea en 5 min
   - Ejecutar ROLLBACK (ver P5)

---

### Problema 3: Alertas no se generan

**Síntomas:**
- Usuarios ven nivel de alertas MUY BAJO
- Incluso animales enfermos no generan CRÍTICA

**Diagnóstico (1 min):**

```bash
# Ver si servicio de alertas está corriendo
$ ps aux | grep observability
# Debe haber un proceso activo

# Ver si hay errores en logs
$ tail -100 logs/observability.log | grep -i "error"

# Probar alerta manualmente
$ curl -X POST http://localhost:8000/test/trigger-alerta \
  -H "Content-Type: application/json" \
  -d '{"tipo": "CRITICA", "animal_id": "TEST"}'
# Debe retornar 200 OK
```

**Soluciones:**

1. **Si servicio no está corriendo:**
   ```bash
   $ systemctl restart fincafacil
   # Validar
   $ systemctl status fincafacil | grep "active"
   ```

2. **Si hay errores en logs:**
   - Revisar FASE 15 (Incident Management) para saber causa
   - Contactar soporte con logs

3. **Si test de alerta no funciona:**
   - Verificar que feature flag está habilitado
   ```bash
   $ cat config/feature_flags.json | grep "OBSERVABILITY"
   # Debe tener "habilitado": true
   ```

---

### Problema 4: Usuarios no pueden iniciar sesión

**Síntomas:**
- "Error de autenticación"
- "Usuario no existe" aunque cuenta fue creada

**Diagnóstico (30 seg):**

```bash
# Verificar que BD de usuarios existe
$ sqlite3 database/current/finca.db "SELECT COUNT(*) FROM usuarios;"
# Debe ser > 0

# Verificar usuario específico
$ sqlite3 database/current/finca.db \
  "SELECT email, activo FROM usuarios WHERE email='user@finca.com';"
# Debe mostrar: user@finca.com | 1 (1 = activo)
```

**Soluciones:**

1. **Si usuario existe pero no activo:**
   ```bash
   $ sqlite3 database/current/finca.db \
     "UPDATE usuarios SET activo=1 WHERE email='user@finca.com';"
   ```

2. **Si usuario no existe:**
   - Ir a Admin Panel → Crear usuario
   - Enviar credenciales temporales por email
   - Usuario debe cambiar contraseña en primer login

3. **Si error persiste:**
   - Verificar que servicio de autenticación está corriendo
   - Ver logs: `tail -50 logs/auth.log`

---

## 🚨 ESCENARIOS DE CRISIS

### Crisis 1: Datos Incorrectos Masivos

**Escenario:** Operador ingresa 500 registros errados (ej: pesos de 2000kg)

**Impacto:** ⚠️ ALTO - Afecta histórico y decisiones futuras

**Acción (15–30 min):**

1. **Inmediato (1 min):**
   - Notificar a todos los usuarios: "Datos comprometidos, en recuperación"
   - PAUSAR ingesta de datos nuevos

2. **Diagnóstico (5 min):**
   ```bash
   # Identificar registros errados
   $ sqlite3 database/current/finca.db \
     "SELECT COUNT(*) FROM eventos WHERE peso > 1000 AND tipo='PESO';"
   # Resultado: 500 registros malos
   ```

3. **Recuperación (5–10 min):**
   - **Opción A:** Si < 1 hora atrás: Rollback a versión anterior + re-entrada manual
   - **Opción B:** Si > 1 hora: Contactar soporte + hacer rollback selectivo (ver P5)

4. **Validación (5 min):**
   ```bash
   $ python scripts/validate_data_quality.py --fix
   # Corrige automáticamente outliers
   ```

---

### Crisis 2: Pérdida de Poder/Desconexión

**Escenario:** Se va luz o desconexión internet en medio de transacción

**Impacto:** ⚠️ MEDIO - Riesgo de corrupción de BD

**Acción (5–10 min):**

1. **Inmediato (30 seg):**
   - Sistema debería detectar automáticamente
   - Ver error en dashboard: "Conexión perdida"

2. **Recuperación (5 min):**
   ```bash
   # Si power vuelve, restart automático
   $ systemctl status fincafacil
   # Si no inicia: ejecutar validación
   $ python scripts/validate_database.py --repair
   ```

3. **Validación:**
   - Verificar que todos los usuarios pueden acceder
   - Revisar últimas 10 transacciones en log
   - Confirmar backup pre-pérdida existe

**Prevención:**
- Usar UPS/generador si es posible
- Sincronizar BD a cloud (FASE 22)

---

### Crisis 3: Seguridad Comprometida

**Escenario:** Sospechas que alguien accedió sin autorización

**Impacto:** 🔴 CRÍTICO - Confidencialidad de datos

**Acción (< 5 min):**

1. **Inmediato (1 min):**
   - Cambiar contraseña de admin
   - Revisar logs: `tail -100 logs/auth.log | grep "failed"`

2. **Investigación (5–10 min):**
   ```bash
   # Ver quién accedió
   $ sqlite3 database/current/finca.db \
     "SELECT usuario_id, timestamp, ip_address FROM audit_log \
      ORDER BY timestamp DESC LIMIT 50;"
   
   # Ver qué se modificó
   $ sqlite3 database/current/finca.db \
     "SELECT objeto, accion, usuario_id FROM audit_log \
      WHERE timestamp > datetime('now', '-1 hour');"
   ```

3. **Respuesta:**
   - Si viste actividad sospechosa: ROLLBACK inmediato (P5)
   - Investigar qué datos se vieron/modificaron
   - Notificar a propietarios de finca
   - Contactar soporte de seguridad

**Prevención:**
- Cambiar contraseña cada 90 días
- No compartir credenciales
- Usar 2FA si está disponible (FASE 22)

---

## 🔧 MANTENIMIENTO PROGRAMADO

### Ventana de Mantenimiento Semanal

**Día/Hora:** Domingo 2–4 AM (Zona Colombia)

**Actividades:**
1. Actualizar sistema operativo
2. Optimizar BD
3. Limpiar logs viejos
4. Validar backups

**Checklist:**

```bash
#!/bin/bash
# scripts/mantenimiento_semanal.sh

echo "📋 Mantenimiento semanal: $(date)"

# 1. Avisar a usuarios
curl -X POST http://localhost:8000/admin/notificar \
  -d "Sistema en mantenimiento 2–4 AM. Servicio puede estar lento."

# 2. Optimizar BD
sqlite3 database/current/finca.db << EOF
VACUUM;
ANALYZE;
EOF

# 3. Limpiar logs > 30 días
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;

# 4. Validar últimos 7 backups
for backup in $(ls -1t database/backup/finca_* | head -7); do
  sqlite3 "$backup" "SELECT COUNT(*) FROM animales;" > /dev/null
  if [ $? -eq 0 ]; then
    echo "✅ Backup OK: $backup"
  else
    echo "❌ Backup CORRUPTO: $backup"
  fi
done

# 5. Reportar
echo "✅ Mantenimiento completado: $(date)"
```

---

## 📞 CONTACTOS Y ESCALAMIENTO

### Niveles de Soporte

| Nivel | Tiempo Respuesta | Quién | Problema |
|-------|------------------|-------|----------|
| **1** | 30 min | Operador | Alerta no crítica, pregunta de uso |
| **2** | 4 horas | Admin + Soporte | Funcionalidad no anda, performance |
| **3** | 1 hora | Soporte especializado | Datos incorrectos, crisis |
| **4** | 15 min | Equipo DevOps | Downtime, seguridad |

### Contactar Soporte

**Email:** soporte@fincafacil.co  
**Teléfono:** +57-1-XXXXXXX (opción 1)  
**WhatsApp:** +57-315-XXXXXXX (solo emergencias)  
**Slack:** #fincafacil-soporte (si tienes acceso)

**Al contactar, incluye:**

```
REPORTE DE SOPORTE
=================
Severidad: [BAJA / MEDIA / ALTA / CRÍTICA]
Problema: [descripción clara]
Cuándo empezó: [timestamp]
Pasos para reproducir: [1. ... 2. ...]
Capturas: [adjuntar si es posible]
Logs: [adjuntar últimos 50 líneas relevantes]

Información del sistema:
- Versión FincaFácil: v1.0.0
- BD: sqlite3, 45 GB
- Uptime: 48 horas
- Usuarios activos hoy: 8
```

---

## 📝 TEMPLATE DE REPORTE DE INCIDENTE

**Ubicación:** `incidents/INC-TIMESTAMP-UUID.md`

```markdown
# INCIDENTE: [Título corto]

**ID:** INC-20241228-abc123  
**Severidad:** [BAJA / MEDIA / ALTA / CRÍTICA]  
**Tiempo inicio:** 28 dic 2024, 14:30 AM  
**Tiempo resolución:** 28 dic 2024, 14:45 AM  
**Duración:** 15 minutos  

## Descripción

Operador No. 3 no podía registrar datos. Todos los demás usuarios funcionaban normal.

## Impacto

- Usuarios afectados: 1 de 8
- Datos perdidos: No
- Dinero perdido: No
- Confianza afectada: Sí (operador revisó 2 veces si el sistema "funcionaba")

## Causa Raíz

El usuario había actualizado su navegador a Chrome v120, que tiene un bug de compatibility con formularios HTML legacy de FincaFácil. 

## Solución

Limpiar cache del navegador. Usuario actualizó a Chrome v121 (fix en navegador).

## Acciones Preventivas

1. Actualizar navegadores recomendados en documentación
2. Agregar validación de navegador en FASE 13 (UX Guardrails)

## Lecciones

Los bugs de user-agent son difíciles de diagnosticar. Considerar agregar "system info" en logs de error.
```

---

## ✅ CHECKLIST DE OPERACIÓN DIARIA

**Usar este checklist cada día de trabajo:**

```
CHECKLIST DIARIO - FINCAFÁCIL v1.0
==================================
Fecha: ___________
Operador: ___________
Turno: [ ] Mañana [ ] Tarde [ ] Noche

Inicio de turno:
[ ] Salud del sistema: HEALTHY
[ ] Dashboard accesible
[ ] Usuarios pueden iniciar sesión
[ ] No hay alertas CRÍTICAS no revisadas

Durante el turno (cada 2h):
[ ] Revisar alertas CRÍTICAS
[ ] Verificar que datos se ingresan correctamente
[ ] No hay usuarios reportando problemas

Cierre de turno:
[ ] Backup último del día: COMPLETADO
[ ] Todos los registros del día validados
[ ] Ningún problema pendiente

Problemas encontrados hoy:
___________________________
___________________________

Contactado soporte: [ ] Sí [ ] No
Ticket número: ___________

Firma: ___________
```

---

**RUNBOOK COMPLETO: FincaFácil está listo para operación diaria.**

*Versión 1.0 | Última actualización: 28 dic 2024*
