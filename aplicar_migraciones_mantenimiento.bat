@echo off
echo ========================================
echo Aplicando Migraciones 017 y 018
echo - Agrega campos de estado a mantenimiento
echo - Agrega estado En Revision a herramientas
echo ========================================
echo.

python scripts\run_migrations.py 017
echo.
python scripts\run_migrations.py 018

echo.
echo ========================================
echo Migraciones completadas
echo ========================================
pause
