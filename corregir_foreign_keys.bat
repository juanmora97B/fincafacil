@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo    CORRECCIÓN DE ERRORES DE FOREIGN KEYS - FincaFácil
echo ═══════════════════════════════════════════════════════════════
echo.

python scripts\fix_foreign_keys.py

echo.
echo ═══════════════════════════════════════════════════════════════
echo    Proceso completado
echo ═══════════════════════════════════════════════════════════════
echo.
pause
