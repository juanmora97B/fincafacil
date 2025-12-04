@echo off
echo ==================================================
echo Aplicando Migracion 020 - columnas extra tabla animal
echo procedencia, vendedor, color, hierro, inventariado, comentarios, tipo_reproduccion
echo ==================================================
echo.
python aplicar_migracion_020_direct.py
echo.
echo ==================================================
echo Migracion 020 finalizada
echo ==================================================
pause
