@echo off
echo ========================================
echo Aplicando migraciones de ANIMALES (019 y 020)
echo ========================================
echo.
echo Ejecutando migracion 019...
python aplicar_migracion_019_direct.py
echo.
echo Ejecutando migracion 020...
python aplicar_migracion_020_direct.py
echo.
echo ========================================
echo Migraciones de animales completadas
echo ========================================
pause
