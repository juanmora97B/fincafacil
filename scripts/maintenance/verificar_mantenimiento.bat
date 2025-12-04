@echo off
chcp 65001 > nul
echo ======================================================================
echo VERIFICACIÓN DE ESTADO DE TABLA MANTENIMIENTO
echo ======================================================================
echo.
python verificar_triggers_fks.py
echo.
echo ======================================================================
echo PRUEBA DE REGISTRO DE MANTENIMIENTO
echo ======================================================================
echo.
python probar_registro_mantenimiento.py
echo.
pause
