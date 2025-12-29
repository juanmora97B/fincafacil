# RUNBOOK MULTI-TENANT
**Versión:** 1.0  
**Fecha:** 2025-12-28  
**Responsable:** SRE Lead  
**Objetivo:** Procedimientos operativos para entornos multi-tenant sin downtime.

---
## 1. Previos
- Validar `X-Tenant-ID` activo en API Gateway y backend.
- Confirmar claves por tenant en Vault y rotación vigente.
- Dashboards por tenant listos (errores, latencia, consumo, billing).

---
## 2. Backups y Restauración Selectiva
- **Backup diario incremental** + **semanal full** etiquetado con `tenant_id`.
- **Restauración selectiva:**
  1) Pausar writes del tenant afectado.
  2) Restaurar snapshot aislado en DB temporal.
  3) Validar checksums y conteos clave.
  4) Swap de schema/tablas del tenant.
  5) Rehabilitar writes y monitorear 24h.
- **RPO/RTO objetivo:** RPO 24h; RTO <2h por tenant.

---
## 3. Migraciones sin Downtime
- Usar feature flag por tenant.
- Desplegar migración en shadow (blue-green); copiar datos; validar con checks.
- Cambiar puntero de conexiones al nuevo schema/versión.
- Rollback: revertir puntero a versión previa; limpiar migración parcial.

---
## 4. Incidentes Comunes
- **Fuga cross-tenant detectada:**
  - Acción inmediata: bloquear endpoint sospechoso + rotar claves + activar modo read-only.
  - Revisar políticas RLS y middleware; auditar logs.
- **Degradación de rendimiento en un tenant heavy:**
  - Rate limit específico; aislar en pool separado; sugerir upgrade de plan.
- **Corrupción de datos de un tenant:**
  - Restaurar selectivo; ejecutar verificación de integridad; comunicar al cliente.

---
## 5. Monitoreo y Alertas
- Métricas por tenant: QPS, p95/p99, errores 4xx/5xx, consumo storage, eventos webhooks, uso IA.
- Alertas:
  - Latencia p99 >2s por tenant (15 min) 
  - Errores 5xx >1% por tenant (5 min)
  - Uso >90% de cuota asignada
  - Eventos de RLS denegados inesperados

---
## 6. Seguridad y Accesos
- Roles admin no cruzan tenants; separación de deberes.
- Logs sin PII; masking obligatorio.
- Rotación de llaves por tenant (6 meses o incidente).

---
## 7. Comunicación con Clientes
- Canal P1: respuesta <30min; actualización cada 60min.
- Notificar incidentes de seguridad en ≤72h.
- Proveer informe post-mortem en 5 días hábiles.

---
## 8. Checklist Pre-Go-Live Multi-Tenant
- [ ] Middleware de tenant habilitado y probado.  
- [ ] RLS o schema por tenant aplicado.  
- [ ] Backups etiquetados por tenant.  
- [ ] Procedimiento de restauración testado en sandbox.  
- [ ] Dashboards y alertas por tenant.  
- [ ] Claves en Vault con rotación programada.  
- [ ] Equipo soporte entrenado en flujos multi-tenant.  
