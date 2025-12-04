@echo off
echo ========================================
echo Aplicando Migracion 019
echo Columnas compra/nacimiento/productivos en tabla animal
echo ========================================
echo.

python aplicar_migracion_019_direct.py

echo.
echo ========================================
echo Migracion 019 completada
echo ========================================
pause
