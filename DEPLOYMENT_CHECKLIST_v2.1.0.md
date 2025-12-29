# DEPLOYMENT CHECKLIST — v2.1.0
**Responsable:** Operations / DevOps Lead  
**Fecha creación:** 28 Diciembre 2025  
**Estado:** 🟢 Ready for Production  

---

## Pre-Despliegue (72h antes)

### Preparación de Infraestructura
- [ ] Verificar capacidad de storage (BD + logs)
- [ ] Confirmar backups automáticos están activos
- [ ] Validar ventanas de maintenance disponibles
- [ ] Revisar SLAs: 99.5% uptime, <15min MTTR

### Preparación de Código
- [ ] Code review completado (FASES 23–27)
- [ ] Todos los tests pasando (si existen)
- [ ] Security scan ejecutado (SAST/DAST)
- [ ] Documentación actualizada en docs/

### Preparación de Datos
- [ ] Backup full de BD actual ejecutado
- [ ] Backup verificado (restore test en staging)
- [ ] Logs archivados de últimos 30 días
- [ ] Data retention policies clarificadas (GDPR, LGPD, etc.)

### Preparación de Equipo
- [ ] Ops team briefing completado (FASES 23–27)
- [ ] Runbooks distribuidos (RUNBOOK_MULTI_TENANT.md, etc.)
- [ ] Escalation contacts confirmados (24/7 availability)
- [ ] Communication plan activado (usuarios, partners)

---

## Despliegue (Día D)

### Windows de Despliegue
- [ ] Ventana de mantenimiento abierta (< 1h en horario low-traffic)
- [ ] Team notificado en Slack #engineering #ops
- [ ] Usuarios notificados: "Mantenimiento 2025-12-28 22:00–23:00 UTC"
- [ ] Partners notificados de cambios API (si aplica)

### Pasos Técnicos de Despliegue

#### 1. Preparar Staging
```bash
# [ ] Clonar producción a staging (BD, configs)
# [ ] Ejecutar v2.1.0 en staging
# [ ] Verificar imports, datos intactos
# [ ] Smoke test: Dashboard, Ventas, Reportes
# [ ] Validar APIs si están activas
```

#### 2. Backup Pre-Despliegue
- [ ] Backup full: `database/fincafacil.db` → `backups/fincafacil_pre_v2.1.0.db`
- [ ] Backup logs: `logs/` → `backups/logs_pre_v2.1.0.tar.gz`
- [ ] Snapshot BD en cloud (si aplica)
- [ ] Documentar hash/checksum de backups

#### 3. Desplegar v2.1.0
```bash
# [ ] Git checkout v2.1.0 (o download release)
# [ ] pip install -r requirements.txt (si cambios)
# [ ] Validar imports: python -m py_compile modules/**/*.py
# [ ] Ejecutar migraciones: python scripts/migrations/run_migrations.py
# [ ] Verificar base datos intacta
# [ ] Iniciar aplicación
```

#### 4. Smoke Test Post-Despliegue
- [ ] App inicia sin errores en logs
- [ ] Dashboard carga y muestra datos
- [ ] Módulo Animales accesible y datos correctos
- [ ] Módulo Salud accesible
- [ ] Módulo Ventas accesible
- [ ] Reportes genera sin error
- [ ] Feature flags leídos correctamente (log check)
- [ ] API endpoints responden (si están activos)

#### 5. Validación de Datos
- [ ] Contar registros animales = pre-deploy
- [ ] Spot check: 5 registros aleatorios íntegros
- [ ] Audit log iniciado correctamente
- [ ] No errores SQL en logs

#### 6. Validación de Features FASE 23–27
- [ ] [ ] FASE 23: Legal matrix se cargó (no requiere UI, verificar logs)
- [ ] [ ] FASE 24: API endpoints responden si enabled (curl GET /api/health)
- [ ] [ ] FASE 25: Multi-tenant checks si enabled (verificar `tenant_id` aislamiento)
- [ ] [ ] FASE 26: Partnership module no rompe UI (navegar sin error)
- [ ] [ ] FASE 27: Estrategia docs presentes (no código, solo documentación)

---

## Post-Despliegue (24h después)

### Monitoreo Inmediato
- [ ] **0–15min:** Monitor logs cada 2–3 min, verificar cero errores críticos
- [ ] **15–60min:** Smoke test cada 15 min (login, navegar, crear un registro)
- [ ] **1–4h:** Revisar logs cada 30 min, buscar patterns anormales
- [ ] **4h+:** Monitoreo normal (alertas automáticas si configuradas)

### Métricas a Validar
- [ ] **Uptime:** 100% (idealmente sin downtime notado)
- [ ] **Response time:** < 2s para dashboard (comparable a v2.0.0)
- [ ] **DB connections:** < 10 activas (normal para Tkinter + API si enabled)
- [ ] **Disk usage:** Sin crecimiento anormal
- [ ] **User reports:** Cero complaints en primeras 2h

### Rollback Decision
Si alguno de estos ocurre, activar rollback inmediato:
- 🔴 **CRITICAL:** Dashboard o módulo principal no carga
- 🔴 **CRITICAL:** Errores de BD (FK violation, corrupted data)
- 🔴 **CRITICAL:** Seguridad breached (unauthorized access detected)
- 🟡 **HIGH:** Performance degradation (responses > 5s)
- 🟡 **HIGH:** Feature flag misconfiguration bloqueando usuarios

**Procedimiento Rollback (< 5 min):**
```bash
# [ ] Verificar último backup íntegro
# [ ] Parar aplicación actual
# [ ] Restaurar database: sqlite3 fincafacil.db < backups/fincafacil_pre_v2.1.0.db
# [ ] Checkout v2.0.0 (o último estable)
# [ ] Reiniciar aplicación
# [ ] Verificar smoke test pasa
# [ ] Notificar usuarios: "Rollback a v2.0.0, investigating issue"
# [ ] Post-mortem en 24h
```

---

## 48h Post-Despliegue

### Validaciones Extendidas
- [ ] **Rendimiento:** Compara KPIs v2.0.0 vs v2.1.0 (dashboard load time, etc.)
- [ ] **Datos:** Auditoría de integridad completa (query count, sums, etc.)
- [ ] **Usuarios:** Confirmar 0 new support tickets relacionados a v2.1.0
- [ ] **Partners:** Si API habilitada, verificar 3+ partners pueden conectar
- [ ] **Legal/Compliance:** Matriz legal matriz se aplica (audit log check)

### Documentación Post-Deploy
- [ ] [ ] Actualizar runbook con v2.1.0 specifics
- [ ] [ ] Documentar issues encontrados (si las hay) en issue tracker
- [ ] [ ] Comunicar success a stakeholders
- [ ] [ ] Archive deployment logs + configs para future reference

---

## Rollback Automático (Opcional)

Si tenés CI/CD pipeline:
- [ ] Configurar health check endpoint (p. ej., `GET /health` → `{"status": "ok"}`)
- [ ] Activar canary deployment (10% traffic → v2.1.0, monitor 30 min)
- [ ] Si error rate > 0.1%, trigger automatic rollback
- [ ] Alertar team vía Slack

---

## Sign-Off

| Rol | Responsable | Status | Fecha |
|-----|-------------|--------|-------|
| **Ops Lead** | [Name] | [ ] Aprobado | __/__/____ |
| **Security** | [Name] | [ ] Aprobado | __/__/____ |
| **Product/PM** | [Name] | [ ] Aprobado | __/__/____ |
| **CTO/Tech Lead** | [Name] | [ ] Aprobado | __/__/____ |

---

## Documentos de Referencia

- [RELEASE_NOTES_v2.1.0.md](RELEASE_NOTES_v2.1.0.md) — Qué hay nuevo
- [RUNBOOK_MULTI_TENANT.md](RUNBOOK_MULTI_TENANT.md) — Ops procedures
- [CHANGELOG.md](CHANGELOG.md) — Full changelog
- [ESTADO_FINAL_PROYECTO.md](ESTADO_FINAL_PROYECTO.md) — Project status

---

**Creado:** 28 Diciembre 2025  
**Última revisión:** [DATE]  
**Próxima revisión:** Post v2.2.0 (recomendado actualizar template)
