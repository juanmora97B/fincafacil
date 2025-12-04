@echo off
echo ========================================
echo Aplicando Migracion 017
echo Agrega campos de estado a mantenimiento
echo ========================================
echo.

python scripts\run_migrations.py 017

echo.
echo ========================================
echo Migracion completada
echo ========================================
pause
