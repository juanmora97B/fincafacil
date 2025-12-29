# ACTIVACION_FASE_37 - Guía de Instalación y Configuración

## 🚀 Pre-Requisitos

```bash
# Python 3.8+
python --version

# Dependencias existentes (ya instaladas)
pip list | grep Flask
pip list | grep sqlite3

# Nuevas dependencias a instalar
pip install Flask==2.3.0
pip install Recharts  # (para React frontend)
pip install APScheduler==3.10.0  # (para job scheduling)
pip install axios  # (para React HTTP)
```

## 📦 Instalación Paso a Paso

### 1. Copiar Archivos Nuevos

```bash
# Copiar directorio analytics a infraestructura
xcopy "src\infraestructura\analytics\*" "src\infraestructura\analytics\" /E

# Copiar jobs
xcopy "src\jobs\analytics_jobs_v2.py" "src\jobs\" 

# Copiar API
xcopy "src\api\analytics_api.py" "src\api\"

# Copiar módulo React (crear directorio si no existe)
mkdir "src\modules\analytics"
xcopy "src\modules\analytics\CentroDeAnalyticsIA.tsx" "src\modules\analytics\"
```

### 2. Ejecutar Migraciones BD

```bash
# Conectar a SQLite
sqlite3 fincafacil.db

# Ejecutar creación de tablas (automático en analytics_service)
python -c "from src.infraestructura.analytics.analytics_service import AnalyticsService; svc = AnalyticsService(); svc.crear_tablas_si_no_existen()"

# Verificar tablas creadas
SELECT name FROM sqlite_master WHERE type='table' LIKE 'analytics_%';
```

### 3. Validar Estructura BD

```sql
-- Verificar read models
SELECT COUNT(*) FROM analytics_productividad;
SELECT COUNT(*) FROM analytics_alertas;
SELECT COUNT(*) FROM analytics_ia;
SELECT COUNT(*) FROM analytics_autonomia;
SELECT COUNT(*) FROM analytics_audit;

-- Verificar índices
SELECT name FROM sqlite_master WHERE type='index' LIKE 'idx_analytics%';
```

### 4. Configurar Variables de Entorno

```bash
# .env file
FLASK_ENV=production
FLASK_DEBUG=0
ANALYTICS_API_PORT=5000
ANALYTICS_CACHE_TTL_OVERVIEW=300
ANALYTICS_CACHE_TTL_PRODUKTIVIDAD=600
ANALYTICS_RATE_LIMIT=100/minute

# Optional: Redis para cache distribuido
REDIS_URL=redis://localhost:6379/0
```

### 5. Configurar Jobs en APScheduler

```python
# En main.py o startup de aplicación
from apscheduler.schedulers.background import BackgroundScheduler
from src.jobs.analytics_jobs_v2 import (
    BuildProductivityAnalyticsJob,
    BuildAlertAnalyticsJob,
    BuildIAAnalyticsJob,
    BuildAutonomyAnalyticsJob,
    JOBS_CONFIG,
)
from src.infraestructura.analytics.analytics_service import AnalyticsService

# Inicializar
scheduler = BackgroundScheduler()
analytics_svc = AnalyticsService()

# Registrar jobs
for job_name, config in JOBS_CONFIG.items():
    job_class = config['class']
    job_instance = job_class(analytics_svc)
    
    scheduler.add_job(
        func=job_instance.ejecutar,
        args=(1,),  # empresa_id=1
        trigger=config['trigger'],
        hour=config.get('hour'),
        minute=config.get('minute'),
        second=config.get('second'),
        id=job_name,
        name=job_name,
    )

scheduler.start()
```

### 6. Iniciar API REST

```python
# main.py
from src.api.analytics_api import create_analytics_api

# Crear aplicación Flask
app = create_analytics_api()

# Ejecutar
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True,
    )
```

### 7. Integrar Frontend React

En el módulo Tkinter que renderiza la UI:

```python
# operaciones_module.py (o equivalente)
from src.modules.analytics.CentroDeAnalyticsIA import CentroDeAnalyticsIA

def abrir_analytics_ia():
    """Abre dashboard de Analytics IA"""
    # Renderizar CentroDeAnalyticsIA.tsx en WebView o Electron
    # O servir como página Web en http://127.0.0.1:5000/analytics

ventana_operaciones.add_menu_item(
    label="📊 Analytics IA",
    command=abrir_analytics_ia,
)
```

## ✅ Validación Post-Instalación

### Test 1: Verificar Conexión BD

```bash
python -c "
from src.database.database import ejecutar_consulta
result = ejecutar_consulta('SELECT COUNT(*) as total FROM analytics_productividad')
print(f'✓ BD conectada: {result}')
"
```

### Test 2: Verificar API REST

```bash
# Terminal 1: Iniciar API
python -m src.api.analytics_api

# Terminal 2: Hacer request
curl -X GET http://127.0.0.1:5000/health
# Response: {"status": "ok"}

curl -X GET "http://127.0.0.1:5000/api/v1/analytics/overview?empresa_id=1"
# Response: {"hoy": {...}, "ultimos_7_dias": {...}}
```

### Test 3: Ejecutar Job Manualmente

```bash
python -c "
from src.jobs.analytics_jobs_v2 import BuildProductivityAnalyticsJob
from src.infraestructura.analytics.analytics_service import AnalyticsService

svc = AnalyticsService()
job = BuildProductivityAnalyticsJob(svc)
result = job.ejecutar(empresa_id=1)
print(f'✓ Job result: {result}')
"
```

### Test 4: Validar Datos en Read Model

```bash
sqlite3 fincafacil.db "
SELECT fecha, nacimientos, destetes, muertes 
FROM analytics_productividad 
ORDER BY fecha DESC 
LIMIT 5;
"
```

### Test 5: Verificar Audit Trail

```bash
curl -X GET "http://127.0.0.1:5000/api/v1/analytics/overview?empresa_id=1" \
  -H "X-Usuario-ID: 123"

# Luego verificar en BD
sqlite3 fincafacil.db "
SELECT usuario_id, endpoint, parametros, resultado 
FROM analytics_audit 
ORDER BY fecha DESC 
LIMIT 5;
"
```

## 🔧 Configuración Avanzada

### Aumentar Frecuencia de Jobs

En `analytics_jobs_v2.py`:

```python
JOBS_CONFIG = {
    "BuildProductivityAnalyticsJob": {
        ...
        "minute": "*/5",  # Cada 5 minutos en lugar de :00
    },
}
```

### Configurar TTL Cache

En `analytics_api.py`:

```python
CACHE_CONFIG = {
    'overview': 300,        # 5 minutos
    'productividad': 900,   # 15 minutos
    'alertas': 300,         # 5 minutos
    'ia': 600,              # 10 minutos
    'autonomia': 300,       # 5 minutos
}
```

### Habilitar HTTPS

```python
# En create_analytics_api()
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(
    certfile='path/to/cert.pem',
    keyfile='path/to/key.pem'
)

app.run(ssl_context=ssl_context)
```

## 📊 Monitoreo

### Logs

```bash
# Verificar logs de jobs
tail -f logs/analytics.log

# Buscar errores
grep "ERROR" logs/analytics.log
```

### Métricas

```bash
# Tamaño de read models
SELECT 
    'analytics_productividad' as tabla,
    COUNT(*) as registros,
    ROUND(SUM(LENGTH(*))/1024.0, 2) as KB
FROM analytics_productividad;
```

### Alertas

Configurar monitoreo en:
- Error rate > 5% en jobs
- Latencia API > 200ms
- Tamaño read models > 1GB

## 🐛 Troubleshooting

### Problema: "ImportError: cannot import name 'AnalyticsService'"

**Solución:**
```bash
# Verificar que __init__.py existe en infraestructura/analytics/
ls -la src/infraestructura/analytics/__init__.py

# Regenerar cache Python
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Problema: "Table 'analytics_productividad' doesn't exist"

**Solución:**
```python
from src.infraestructura.analytics.analytics_service import AnalyticsService
svc = AnalyticsService()
svc.crear_tablas_si_no_existen()  # Force creation
```

### Problema: "API returns 500 Internal Server Error"

**Solución:**
```bash
# Verificar logs
cat logs/flask.log

# Validar queries SQL
sqlite3 fincafacil.db ".mode column" ".header on"
SELECT * FROM analytics_audit ORDER BY id DESC LIMIT 1;
```

### Problema: "Jobs no se ejecutan"

**Solución:**
```python
# Verificar scheduler está corriendo
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
print(scheduler.running)  # Debe ser True

# Ver jobs registrados
print(scheduler.get_jobs())
```

## 📈 Performance Tuning

### Problema: Queries lentas en read models

```sql
-- Crear índices adicionales
CREATE INDEX idx_analytics_prod_empresa_fecha ON analytics_productividad(empresa_id, fecha);
CREATE INDEX idx_analytics_alert_estado ON analytics_alertas(estado);
CREATE INDEX idx_analytics_audit_usuario ON analytics_audit(usuario_id);
```

### Problema: Cache hits bajos

```python
# Aumentar TTL
cache.set_cache(key, value, ttl=1800)  # 30 minutos

# O usar Redis
import redis
cache_redis = redis.Redis(host='localhost', port=6379, db=0)
```

## 🔐 Seguridad Post-Instalación

### 1. Cambiar empresa_id default

```python
# En analytics_api.py
# CAMBIAR DE: empresa_id = 1 (default)
# A: requerir empresa_id en header

@require_auth
def overview():
    empresa_id = g.empresa_id  # De request
```

### 2. Validar credenciales

```python
# Implementar auth provider
from src.infraestructura.autenticacion import validar_token

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        usuario = validar_token(token)
        g.usuario_id = usuario['id']
        g.empresa_id = usuario['empresa_id']
        return f(*args, **kwargs)
    return decorated
```

### 3. Auditar accesos sensibles

```python
@app.before_request
def log_access():
    logger.info(f"[AUDIT] {request.remote_addr} {request.method} {request.path}")
```

## 📋 Checklist Pre-Producción

- [ ] BD respaldada (backup completo)
- [ ] Tests API (curl/Postman funcional)
- [ ] Tests Jobs (manual execution OK)
- [ ] Índices BD creados y optimizados
- [ ] Variables de entorno configuradas
- [ ] Logs configurados
- [ ] HTTPS habilitado
- [ ] Rate limiting configurado
- [ ] Auditoría funcionando
- [ ] Documentación actualizada
- [ ] Equipo entrenado en dashboard
- [ ] SLA monitoreo activado

## 🎓 Próximas Sesiones

**Sesión 1:** Integración scheduler (APScheduler setup)
**Sesión 2:** Frontend wiring (Tkinter ↔ React bridge)
**Sesión 3:** Testing suite completa
**Sesión 4:** Production hardening (Redis, rate limiting)
**Sesión 5:** Documentación y training cliente

---

**Versión:** 2.0  
**Última actualización:** 2025-01-15  
**Responsable:** Sistema IA FincaFácil
