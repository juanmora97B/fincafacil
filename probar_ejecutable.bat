@echo off
REM Script para diagnosticar problemas del ejecutable

echo ========================================
echo   DIAGNOSTICO DE FINCAFACIL
echo ========================================
echo.

echo Probando ejecutable desde dist...
cd dist\FincaFacil
echo.
echo Directorio actual: %CD%
echo.
echo Verificando archivos:
dir FincaFacil.exe
echo.
echo Intentando ejecutar...
echo Si no abre, presione Ctrl+C y describa que ve
echo.
pause

start FincaFacil.exe

echo.
echo Si el programa se abrio, presione cualquier tecla
echo Si NO se abrio, presione Ctrl+C y anote cualquier mensaje de error
pause

cd ..\..
