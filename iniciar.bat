@echo off
REM Script para iniciar FincaFácil v2.0.0
REM =====================================

title FincaFacil - Sistema de Gestión Ganadera
chcp 65001 >nul

cd /d "%~dp0"

echo.
echo ==================================
echo   FINCA FACIL v2.0.0
echo   Sistema de Gestion Ganadera
echo ==================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo.
    echo Por favor instale Python 3.10+ desde: https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detectado
echo.
echo Iniciando aplicacion...
echo.

REM Ejecutar la aplicación
python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Error al ejecutar FincaFacil
    echo.
    pause
    exit /b 1
)

exit /b 0
