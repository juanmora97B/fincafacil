# ♻️ FASE 4 - Plan de Recuperación

Objetivo: garantizar continuidad ante fallos críticos.

## Backups
- Backups automáticos en:
  - Cierre de aplicación (`on_app_close`)
  - Cierre mensual (`on_monthly_close`)
  - Error crítico (`on_critical_error`)
- Comprimidos `.zip` con timestamp y motivo
- Retención configurable (default: últimos 10)

## Restauración (Manual)
1. Cerrar FincaFácil.
2. Ir a carpeta `backup/` y elegir el `.zip` deseado.
3. Extraer el archivo `fincafacil.db` del zip.
4. Reemplazar el `fincafacil.db` actual por el del backup.
5. Iniciar FincaFácil.

## Notas
- Restauración sin UI para evitar errores humanos.
- Mantener copias externas en almacenamiento seguro.
- Programar respaldo periódico adicional si se requiere.
