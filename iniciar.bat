@echo off
REM Script para iniciar FincaFácil v2.0.0
REM =====================================

title FincaFacil - Sistema de Gestión Ganadera

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════╗
echo ║   FINCA FACIL v2.0.0                   ║
echo ║   Sistema de Gestión Ganadera          ║
echo ╚════════════════════════════════════════╝
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en PATH
    echo.
    echo Por favor instale Python 3.10+ desde: https://www.python.org/
    pause
    exit /b 1
)

echo ✓ Python detectado
echo.
echo Iniciando aplicación...
echo.

REM Ejecutar la aplicación
python main.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar FincaFácil
    echo.
    pause
    exit /b 1
)

exit /b 0
