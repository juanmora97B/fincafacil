# FEATURE FLAGS CONFIGURATION — v2.1.0
**Actualizado:** 28 de Diciembre de 2025  
**Formato:** YAML (también disponible en config/feature_flags.ini o .env)  
**Responsable:** Product / Engineering Lead

---

## Descripción General

Feature flags permiten activar/desactivar FASES 23–27 por:
- **Entorno:** development, staging, production
- **País/Región:** Colombia, Brasil, Argentina, México, Perú, Ecuador, etc.
- **Tenant:** Por cliente (si multi-tenant activo)
- **Rollout:** Gradual (10% → 50% → 100% adopción)

---

## Flags Principales (FASES 23–27)

### FASE_23_LEGAL_COMPLIANCE
```yaml
FASE_23_LEGAL_COMPLIANCE:
  enabled: true
  description: "Matriz legal multipaís, DPA/SLA, términos base"
  default: true  # Habilitar en producción siempre
  rollout: 100%
  countries:
    COLOMBIA: true
    BRASIL: true
    ARGENTINA: true
    MEXICO: true
    PERU: true
    ECUADOR: true
    CHILE: true
    PARAGUAY: true
    URUGUAY: true
  notes: "No UI changes; backend compliance enforcement"
```

**Impacto:**
- ✅ Auditoría legal automática habilitada
- ✅ SLA checking en reportes
- ✅ Términos y responsabilidades mostrados en login (primera vez)
- ✅ Matriz legal disponible en `config/legal_matrix.yaml`

---

### FASE_24_API_PUBLIC
```yaml
FASE_24_API_PUBLIC:
  enabled: false  # Beta: activar solo si tenés ISVs
  description: "API REST pública, OpenAPI spec, webhooks, rate limiting"
  rollout: 25%  # Canary: solo early adopters
  countries:
    COLOMBIA: true    # Activo para pilotos
    BRASIL: false     # Esperar Q2 2026
    ARGENTINA: true   # Activo para pilotos
    MEXICO: false     # Esperar Q2 2026
  partner_whitelist:
    - partner_id: "partner_abc123"
      api_tier: "premium"
      rate_limit: 5000  # req/min (vs default 1000)
    - partner_id: "partner_xyz789"
      api_tier: "standard"
      rate_limit: 1000
  notes: |
    - Requiere setup de API gateway (FastAPI, OAuth2 provider)
    - ISVs deben usar api key o OAuth2
    - Webhooks enviados automáticamente a endpoints registrados
    - Monitor API metrics en dashboard ops
```

**Impacto:**
- ✅ Endpoints públicos `/api/v1/*` disponibles (si enabled)
- ✅ OpenAPI spec servido en `/api/docs` (Swagger UI)
- ✅ Rate limiting aplicado (429 Too Many Requests si excedido)
- ✅ Webhooks enviados a partners registrados

**Cómo activar:**
```bash
# En config/feature_flags.yaml o .env
FEATURE_FLAGS__FASE_24_API_PUBLIC=true
API_GATEWAY_ENABLED=true
WEBHOOK_ENABLED=true
```

---

### FASE_25_MULTI_TENANT
```yaml
FASE_25_MULTI_TENANT:
  enabled: false  # Beta: pilotos solo
  description: "Aislamiento multi-tenant (RLS o schemas), cifrado por tenant"
  rollout: 10%
  model: "RLS"  # Options: RLS, SCHEMA_ISOLATION
  countries:
    COLOMBIA: false
    BRASIL: false
    ARGENTINA: false
  pilot_tenants:
    - tenant_id: "tenant_corporativo_001"
      name: "Corporativo XYZ (20 fincas)"
      model: "RLS"
      encryption: "AES-256"
    - tenant_id: "tenant_cooperativa_001"
      name: "Cooperativa ABC (50 fincas)"
      model: "SCHEMA_ISOLATION"
      encryption: "AES-256"
  notes: |
    - RLS recomendado para <100 tenants
    - SCHEMA_ISOLATION recomendado para >100 tenants
    - Migración de tenants vía scripts/migrate_tenant.py
    - Backup/restore per tenant habilitado
    - Soporta disaster recovery (RTO <4h, RPO <1h)
```

**Impacto:**
- ✅ Cada tenant ve solo sus datos (aislamiento de BD)
- ✅ Datos cifrados con clave per-tenant
- ✅ Migraciones seguras (backup → restore en nuevo schema/RLS)
- ✅ Auditoría de accesos a datos por tenant

**Cómo activar (pilotos):**
```bash
# En config/.env para tenant específico
FEATURE_FLAGS__FASE_25_MULTI_TENANT=true
TENANT_ISOLATION_MODEL=RLS  # O SCHEMA_ISOLATION
TENANT_ENCRYPTION_KEY=<generated key>
```

---

### FASE_26_PARTNERSHIPS
```yaml
FASE_26_PARTNERSHIPS:
  enabled: false  # Beta: partnership program Q1 2026
  description: "Module partnerships, revenue share, SLAs por partner"
  rollout: 5%
  pilot_partners:
    - partner_id: "partner_veterinario_001"
      name: "Asesor Veterinario ABC"
      channel: "RESELLER"
      revenue_share: 30  # %
      api_tier: "standard"
      sla_uptime: 99.5
      sla_response: "< 4h"
    - partner_id: "partner_erp_001"
      name: "ERP Integrator XYZ"
      channel: "ISV"
      revenue_share: 25  # %
      api_tier: "premium"
      sla_uptime: 99.9
      sla_response: "< 1h"
  notes: |
    - Partnership module en UI (si enabled)
    - Dashboards por partner (adoptions, revenue)
    - Documentación playbook en PARTNERSHIP_PLAYBOOK.md
    - Contatos y acuerdos master requieren setup manual
```

**Impacto:**
- ✅ Partnership module visible en sidebar (si enabled)
- ✅ Dashboards de partners y revenue disponibles
- ✅ API access controlado por partner (via api key)
- ✅ SLA tracking automático per partner

---

### FASE_27_STRATEGY_2030
```yaml
FASE_27_STRATEGY_2030:
  enabled: true
  description: "Estrategia 2030, escenarios, triggers de decisión"
  rollout: 100%
  ui_visible: false  # Solo para leadership, no usuario final
  quarterly_review: true  # Triggers revisión Q1, Q2, Q3, Q4
  scenarios:
    - name: "Crecimiento Orgánico"
      code: "organic"
      enabled: true
      targets:
        users_2030: 50000
        revenue_2030: 40000000000  # $40B
        ebitda_margin: 90
    - name: "Aceleración con Inversión"
      code: "investment"
      enabled: true
      targets:
        users_2030: 100000
        revenue_2030: 80000000000  # $80B
        ebitda_margin: 75
    - name: "M&A / Venta"
      code: "ma"
      enabled: true
      targets:
        valuation: 30000000000  # $30B+
        exit_year: 2027
    - name: "Spin-off Institucional"
      code: "spinoff"
      enabled: false  # Activar si gobierno/ONG solicita
      targets:
        institutional_contracts: 5
        revenue_source: "annual_licenses"
  kpi_triggers:
    green:
      dau_pct: 70  # DAU > 70% de usuarios totales
      nps: 75
      churn_monthly: 1.0  # < 1%
      arr_growth: 15  # % trimestral
    yellow:
      dau_pct: 50  # Alerta: revisar adopción
      nps: 60
      churn_monthly: 2.0
      arr_growth: 5
    red:
      dau_pct: 30  # Crítico: evaluar pivote
      nps: 40
      churn_monthly: 5.0
      arr_growth: -5  # Decrecimiento
  notes: |
    - KPI review trimestral (Q1, Q2, Q3, Q4)
    - Triggers automáticos alertan si semáforo cambia
    - Leadership evalúa escenario y toma decisión
    - Documentación en ESCENARIOS_ESTRATEGICOS_2030.md
```

**Impacto:**
- ✅ Tracking automático de KPIs vs. triggers
- ✅ Alertas cuando semáforo pasa a Yellow/Red
- ✅ Dashboard interno (no usuario) con escenarios
- ✅ Quarterly business review facilitado

---

## Configuración por Entorno

### Development (local)
```yaml
# config/feature_flags.dev.yaml
environment: development
FASE_23_LEGAL_COMPLIANCE: true
FASE_24_API_PUBLIC: true  # Habilitar para testing
FASE_25_MULTI_TENANT: true
FASE_26_PARTNERSHIPS: true
FASE_27_STRATEGY_2030: true
api_gateway_enabled: true
webhook_enabled: true
rollout: 100%  # Dev: todas activas
```

### Staging (pre-prod)
```yaml
# config/feature_flags.staging.yaml
environment: staging
FASE_23_LEGAL_COMPLIANCE: true
FASE_24_API_PUBLIC: true  # Testing with real partners
FASE_25_MULTI_TENANT: false  # Esperar prod
FASE_26_PARTNERSHIPS: true  # Partner testing
FASE_27_STRATEGY_2030: true
rollout: 50%  # Staged rollout
partner_whitelist:
  - "staging_partner_001"
```

### Production (live)
```yaml
# config/feature_flags.production.yaml
environment: production
FASE_23_LEGAL_COMPLIANCE: true
FASE_24_API_PUBLIC: false  # Q2 2026
FASE_25_MULTI_TENANT: false  # Q3 2026 (pilotos)
FASE_26_PARTNERSHIPS: false  # Q1 2026 (pilotos)
FASE_27_STRATEGY_2030: true  # Internal only
api_gateway_enabled: false
webhook_enabled: false
rollout: 0%  # Conservador: solo si explícitamente enabled
```

---

## Cómo Usar Feature Flags en Código

### Ejemplo: Verificar FASE 24 habilitada antes de retornar API endpoint
```python
# src/core/feature_flags.py
from config import feature_flags

def is_phase_enabled(phase_name: str, country: str = "COLOMBIA", tenant_id: str = None) -> bool:
    """Verifica si una FASE está habilitada."""
    flag = feature_flags.get(phase_name, {})
    
    # Check global enabled
    if not flag.get("enabled", False):
        return False
    
    # Check país/región
    if country and flag.get("countries", {}).get(country) == False:
        return False
    
    # Check tenant (si aplica)
    if tenant_id and flag.get("pilot_tenants"):
        pilot_tenants = [t["tenant_id"] for t in flag["pilot_tenants"]]
        if tenant_id not in pilot_tenants:
            return False
    
    return True

# En tu handler/endpoint
def get_api_endpoints():
    if is_phase_enabled("FASE_24_API_PUBLIC"):
        return api_service.get_public_endpoints()
    else:
        return {"error": "API no disponible en tu región"}
```

### Ejemplo: Log de FASE habilitada al startup
```python
# main.py o inicialización
from src.core.feature_flags import is_phase_enabled

logger.info(f"FASE 23 (Legal): {is_phase_enabled('FASE_23_LEGAL_COMPLIANCE')}")
logger.info(f"FASE 24 (API): {is_phase_enabled('FASE_24_API_PUBLIC')}")
logger.info(f"FASE 25 (Multi-tenant): {is_phase_enabled('FASE_25_MULTI_TENANT')}")
logger.info(f"FASE 26 (Partnerships): {is_phase_enabled('FASE_26_PARTNERSHIPS')}")
logger.info(f"FASE 27 (Strategy 2030): {is_phase_enabled('FASE_27_STRATEGY_2030')}")
```

---

## Rollout Strategy

### FASE 23 — Legal Compliance
- **Día 1:** 100% (siempre activo)
- **Impacto:** Backend only, no UI changes

### FASE 24 — API Public
- **Día 1:** 0% (esperar partners onboarding)
- **Q1 2026:** 10% (3 partners pilotos)
- **Q2 2026:** 50% (15+ partners)
- **Q3 2026:** 100% (open para todos)

### FASE 25 — Multi-Tenant
- **Día 1:** 0% (esperar arquitectura confirmada)
- **Q1 2026:** 5% (2 pilotos corporativos)
- **Q2 2026:** 25% (expansion pilots)
- **Q3 2026:** 100% (nueva arquitectura de customer)

### FASE 26 — Partnerships
- **Día 1:** 0% (program preparation)
- **Q1 2026:** 10% (5 partners pilotos)
- **Q2 2026:** 50% (25+ partners)
- **Q3 2026:** 100% (full partnership program)

### FASE 27 — Strategy 2030
- **Día 1:** 100% (internal only)
- **Ongoing:** Quarterly KPI review + trigger alerts

---

## Monitoreo de Feature Flags

### Métricas a Trackear
```yaml
FASE_24_API_PUBLIC:
  metric_api_requests: "requests/min"
  metric_api_errors: "error_rate %"
  metric_partner_adoption: "count of active partners"
  alert_if_error_rate_gt: 0.1  # >0.1% error rate
  
FASE_25_MULTI_TENANT:
  metric_tenant_migrations: "migrations completed"
  metric_data_isolation: "FK violations (should be 0)"
  metric_backup_success: "backup completion %"
  alert_if_backup_lt: 95  # <95% success rate
  
FASE_27_STRATEGY_2030:
  metric_kpi_dau_pct: "DAU / total users"
  metric_nps: "Net Promoter Score"
  metric_churn_monthly: "churn %"
  alert_trigger_yellow: "if KPI outside yellow range"
  alert_trigger_red: "if KPI outside red range"
```

### Dashboard de Monitoreo (futuro)
Crear dashboard en `modules/dashboard/feature_flags_dashboard.py`:
- KPIs por FASE
- Rollout % por país
- Health checks por feature
- Triggers y alerts activos

---

## Cambiar Flags en Tiempo de Ejecución (Gradual Rollout)

### Opción 1: Archivo YAML (requiere restart)
```yaml
# config/feature_flags.yaml
FASE_24_API_PUBLIC:
  enabled: true
  rollout: 10  # Cambiar de 0% a 10%
```
Luego: `systemctl restart fincafacil` (o similar)

### Opción 2: Base de Datos (sin restart)
```sql
-- Tabla: feature_flags (futuro)
INSERT INTO feature_flags (flag_name, enabled, rollout_percent, updated_at)
VALUES ('FASE_24_API_PUBLIC', true, 10, datetime('now'))
ON CONFLICT(flag_name) DO UPDATE SET
  enabled=excluded.enabled,
  rollout_percent=excluded.rollout_percent,
  updated_at=excluded.updated_at;
```

Código:
```python
# src/core/feature_flags.py (versión DB)
from database import get_db

def is_phase_enabled(phase_name: str, user_id: int = None) -> bool:
    db = get_db()
    flag = db.execute(
        "SELECT enabled, rollout_percent FROM feature_flags WHERE flag_name = ?",
        (phase_name,)
    ).fetchone()
    
    if not flag or not flag["enabled"]:
        return False
    
    # Rollout: 10% → user_id % 100 < 10
    rollout = flag["rollout_percent"] or 0
    if user_id:
        return (user_id % 100) < rollout
    
    return True
```

---

## Desactivar Rápidamente (Emergency)

Si crítica: desactivar FASE 24 (API) inmediatamente:

```bash
# SSH a servidor prod
# Opción 1: Editar config y restart
vim config/feature_flags.production.yaml
# Cambiar: FASE_24_API_PUBLIC: false
systemctl restart fincafacil

# Opción 2: Kill API process (si separado)
pkill -f "fastapi" || pkill -f "uvicorn"

# Opción 3: Update DB (si soporta)
sqlite3 database/fincafacil.db <<EOF
UPDATE feature_flags SET enabled=0 WHERE flag_name='FASE_24_API_PUBLIC';
EOF
# App releerá config dentro de 5 min

# Verifica
curl https://api.fincafacil.com/api/v1/health
# Debe retornar error o 404
```

---

## Próximos Pasos

1. **Hoy (28 dic 2025):** Deploy v2.1.0 con todos los flags en default
2. **Q1 2026:** Activar FASE 23 (audit), FASE 26 (partnership module)
3. **Q2 2026:** Beta FASE 24 (API) con 3–5 partners pilotos
4. **Q3 2026:** Beta FASE 25 (multi-tenant) con 2 clientes grandes
5. **Q4 2026:** Evaluar triggers FASE 27 y decidir ruta a 2030

---

**Creado:** 28 Diciembre 2025  
**Responsable:** Product / Engineering Lead  
**Próxima revisión:** Q1 2026 (pre-activation FASE 24)
