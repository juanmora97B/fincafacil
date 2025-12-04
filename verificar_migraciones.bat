@echo off
chcp 65001 > nul
echo ======================================================================
echo VERIFICACIÓN DE MIGRACIONES DE MANTENIMIENTO
echo ======================================================================
echo.
python verificar_estado_migraciones.py
echo.
pause
