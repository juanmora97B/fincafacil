# FASE 25 — Multi-Tenant Engineering & Operación a Escala
**Versión:** 1.0  
**Fecha:** 2025-12-28  
**Responsable:** CTO + SRE Lead  
**Objetivo:** Asegurar operación simultánea de múltiples clientes/tenants sin interferencias ni fuga de datos, manteniendo compatibilidad con v2.0.0.

---
## 1. Principios de Arquitectura
- **Aislamiento por Tenant:** Datos separados lógicamente (schema/row-level), cifrado por tenant, `X-Tenant-ID` obligatorio.
- **Aislamiento por Región:** Elegir región de almacenamiento por país para cumplir soberanía donde aplique.
- **Configuración por Tenant:** Flags, límites de uso, planes, SLA individuales.
- **Modelos IA:** Pesos globales; opcional fine-tune por tenant si contrato enterprise. 
- **Compatibilidad:** No romper API v1; nuevas rutas con headers obligatorios.

---
## 2. Datos y Esquema
- Opción A: **Row-Level Security (RLS)** con columna `tenant_id` en todas las tablas y políticas estrictas.
- Opción B: **Schema-per-tenant** para clientes enterprise que lo exijan.
- Cifrado por tenant (clave en Vault); rotación semestral.
- Backups etiquetados por tenant para restauración selectiva.

---
## 3. Límites de Uso y Costeo
- **Por plan:** QPS, storage, eventos webhook, ancho de banda.
- **Por tipo de cliente:** Farmer individual, Cooperativa, Institucional.
- **Costeo técnico:** Storage + compute + soporte; margen objetivo 80–90% por tenant.

---
## 4. Operación
- **Backups por tenant:** Diario incremental; semanal full; retención según contrato (mín 30 días).
- **Recuperación selectiva:** Restaurar solo tenant afectado; checklist en RUNBOOK_MULTI_TENANT.
- **Migraciones sin downtime:** Blue-green + feature flags; migrar por cohortes de tenants.
- **Monitoreo:** Métricas por tenant (errores, latencia, consumo); alertas de aislamiento (cross-tenant anomalies).

---
## 5. Seguridad
- **Headers obligatorios:** `X-Tenant-ID`; validar en middleware.
- **Autorización:** Scopes y roles per-tenant; admins no cruzan tenants.
- **Logs:** Nunca incluir datos sensibles; trazas separadas por tenant.

---
## 6. Deliverables
- [RUNBOOK_MULTI_TENANT.md](RUNBOOK_MULTI_TENANT.md)
- Ajustes a OPENAPI si se agregan endpoints admin/tenant.
- Actualización CHANGELOG en v2.1.0.

---
## 7. Próximos Pasos
1) Implementar middleware obligatorio de tenant + pruebas RLS.  
2) Etiquetar backups existentes con `tenant_id`.  
3) Crear dashboards por tenant (errores, consumo).  
4) Simular restauración parcial de un tenant en sandbox.  
5) Definir precios por plan con costo marginal por tenant.
