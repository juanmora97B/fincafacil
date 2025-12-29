# 🔒 FASE 4 - HARDENING (Endurecimiento)

Objetivo: convertir FincaFácil en un producto robusto, confiable y gobernable.

## Alcance
- Manejo de errores global (sin try/except silenciosos)
- Backups automáticos (cierre app, cierre mensual, error crítico)
- Auditoría operativa (tabla audit_log)
- Permisos básicos (ADMIN, OPERADOR, CONSULTA)
- Estabilidad UI (threading/after, cursor busy, disable botones)
- Validaciones finales y health check

## Entregables
- `src/core/error_handler.py` (BusinessError, ValidationError, DataIntegrityError, PermissionError, `@safe_ui_call`)
- `src/core/backup_service.py` (zip con timestamp, retención)
- `src/core/audit_service.py` (tabla audit_log + `log_event()`)
- `src/core/permission_service.py` (roles y `require()`)
- `tools/health_check.py` (validaciones BD, UI sin SQL, backups)

## Integraciones clave
- Cierre mensual: auditoría + backup automático
- Exportadores: auditoría en éxito/error
- UI: usar `@safe_ui_call` en callbacks críticos, usar `busy_ui()`

## Reglas de arquitectura (obligatorias)
- UI → Services → Repository → SQLite (WAL)
- ❌ Sin SQL en la UI
- ❌ Sin lógica de negocio en Repository
- ❌ Sin `print()` en producción

## Logging
- Errores: `logs/app_errors.log`
- Backups: `logs/backups.log`

## Próximos pasos
- Añadir `@safe_ui_call` a callbacks UI principales (reportes, exportación, cierre mensual)
- Configurar retención de backups en `DEFAULT_RETENTION`
- Asegurar carga de roles en contexto de usuario
