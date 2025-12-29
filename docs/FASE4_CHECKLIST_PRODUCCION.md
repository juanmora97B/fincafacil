# ✅ FASE 4 - Checklist de Producción

Use esta lista antes de entregar a usuarios reales.

## Sistema
- [ ] Health Check sin errores (`python tools/health_check.py --json`)
- [ ] SQLite en modo WAL
- [ ] Sin SQL en UI (grep pasa)
- [ ] Auditoría `audit_log` creada y registrando
- [ ] Backups automáticos funcionando (cierre app, cierre mensual, error crítico)

## UI
- [ ] Callbacks críticos decorados con `@safe_ui_call`
- [ ] Cursor busy durante operaciones largas
- [ ] Botones deshabilitados en operaciones críticas
- [ ] Protección contra doble click

## Permisos
- [ ] Roles definidos (ADMIN/OPERADOR/CONSULTA)
- [ ] Reglas aplicadas en acciones sensibles

## Backups
- [ ] Directorio `backup/` con zip versionados
- [ ] Retención configurada (p.ej. 10)
- [ ] Restauración documentada

## Auditoría
- [ ] Eventos de cierre mensual registrados
- [ ] Exportaciones registradas
- [ ] Eliminaciones con soft delete registradas

## Documentación
- [ ] `FASE4_HARDENING.md`
- [ ] `FASE4_CHECKLIST_PRODUCCION.md`
- [ ] `FASE4_RESUMEN_EJECUTIVO.md`
- [ ] `FASE4_PLAN_RECUPERACION.md`
