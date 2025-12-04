@echo off
REM ========================================
REM   CREADOR DE INSTALADOR - FINCAFACIL
REM   Genera instalador.exe con Inno Setup
REM ========================================

echo.
echo ========================================
echo   FINCAFACIL - CREADOR DE INSTALADOR
echo ========================================
echo.

REM Verificar que existe el compilado
if not exist "dist\FincaFacil\FincaFacil.exe" (
    echo ERROR: No se encontro el ejecutable compilado
    echo.
    echo Por favor ejecute primero: compilar.bat
    echo.
    pause
    exit /b 1
)

REM ========================================
REM Buscar Inno Setup en ubicaciones comunes
REM ========================================
echo [1/3] Buscando Inno Setup Compiler...

set ISCC_PATH=""

REM Verificar en Program Files
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    echo     OK - Encontrado en Program Files ^(x86^)
    goto :found_iscc
)

if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
    echo     OK - Encontrado en Program Files
    goto :found_iscc
)

REM No encontrado
echo.
echo ERROR: No se encontro Inno Setup Compiler
echo.
echo Inno Setup es necesario para crear el instalador.
echo.
echo SOLUCION:
echo   1. Descargue Inno Setup desde: https://jrsoftware.org/isdl.php
echo   2. Instale Inno Setup 6.x
echo   3. Ejecute nuevamente este script
echo.
pause
exit /b 1

:found_iscc
echo.

REM ========================================
REM Verificacion rapida: contar archivos en dist
REM ========================================
echo Verificando contenido de dist\FincaFacil...
setlocal EnableDelayedExpansion
set FILE_COUNT=0
for /f "delims=" %%F in ('dir /b /s dist\FincaFacil 2^>nul') do set /a FILE_COUNT+=1
echo Archivos detectados: !FILE_COUNT!
set /a MIN_COUNT=500
if !FILE_COUNT! LSS !MIN_COUNT! (
    echo.
    echo ADVERTENCIA: Carpeta dist incompleta ^(^<!MIN_COUNT! archivos^).
    echo Ejecute compilar.bat o rebuild_completo.bat antes de continuar.
    echo.
    pause
)
endlocal
echo.

REM ========================================
REM Crear carpeta de salida
REM ========================================
echo [2/3] Preparando carpeta de salida...
if not exist "installer" mkdir installer
echo     OK - Carpeta installer\ creada
echo.

REM ========================================
REM Compilar con Inno Setup
REM ========================================
echo [3/3] Compilando instalador con Inno Setup...
echo.
echo Esto puede tomar algunos minutos...
echo.

%ISCC_PATH% /Q instalador.iss

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion del instalador fallo
    echo.
    echo Revise el archivo instalador.iss
    echo O ejecute manualmente Inno Setup Compiler
    echo.
    pause
    exit /b 1
)

echo.
echo     OK - Instalador creado exitosamente
echo.

REM ========================================
REM RESUMEN FINAL
REM ========================================
echo ========================================
echo   INSTALADOR COMPLETADO
echo ========================================
echo.
echo El instalador se encuentra en: installer\
echo.
echo Archivo generado:
for %%F in (installer\*.exe) do echo   - %%~nxF
echo.
echo Detalles del instalador:
echo   - Incluye todos los archivos necesarios
echo   - Crea accesos directos automaticamente
echo   - Instalacion silenciosa disponible
echo   - Desinstalador incluido
echo.
echo DISTRIBUCION:
echo   El archivo .exe puede distribuirse via:
echo   - USB/Pendrive
echo   - Email (si el tamano lo permite)
echo   - Descarga directa
echo   - Servidor web
echo   - Google Drive / Dropbox
echo.
echo El cliente solo necesita:
echo   1. Ejecutar el instalador
echo   2. Seguir el asistente
echo   3. Iniciar FincaFacil
echo.
echo ========================================
echo.
pause
