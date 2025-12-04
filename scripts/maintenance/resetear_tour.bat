@echo off
REM ============================================
REM  Resetear Tour Interactivo - FincaFacil
REM ============================================

echo.
echo ========================================
echo   RESETEAR TOUR INTERACTIVO
echo ========================================
echo.
echo Este script reseteara el tour interactivo
echo para que se muestre nuevamente en el
echo proximo inicio de FincaFacil.
echo.
pause

REM Verificar si existe el directorio config
if not exist "config\" (
    echo Creando directorio config...
    mkdir config
)

REM Crear/actualizar archivo de configuracion
echo {"completado": false} > config\tour_completado.json

echo.
echo ========================================
echo   TOUR RESETEADO CORRECTAMENTE
echo ========================================
echo.
echo El tour interactivo se mostrara en la
echo proxima ejecucion de FincaFacil.
echo.
echo Ejecute: ejecutar.bat
echo.
pause
