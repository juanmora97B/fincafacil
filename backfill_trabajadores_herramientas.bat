@echo off
setlocal

echo ==============================================
echo Backfill de id_trabajador en herramientas
echo - Asigna empleados a partir de 'responsable'
echo ==============================================

python scripts\utilities\backfill_herramienta_trabajador.py

echo.
echo Listo. Revise el resumen anterior.
pause
