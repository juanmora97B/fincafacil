@echo off
REM ========================================
REM   LIMPIEZA PROFUNDA + REBUILD COMPLETO
REM   Garantiza compilacion desde cero
REM ========================================

echo.
echo ========================================
echo   LIMPIEZA Y REBUILD COMPLETO
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ERROR: Este script debe ejecutarse desde la raiz del proyecto
    pause
    exit /b 1
)

REM ========================================
REM PASO 1: LIMPIEZA PROFUNDA
REM ========================================
echo [1/6] Limpieza profunda de archivos antiguos...

REM Cerrar cualquier instancia de FincaFacil en ejecucion
echo   - Cerrando procesos de FincaFacil...
taskkill /f /im FincaFacil.exe >nul 2>&1
taskkill /f /im FincaFacil_Debug.exe >nul 2>&1
timeout /t 2 /nobreak >nul

if exist "build" (
    echo   - Eliminando carpeta build...
    rmdir /s /q build
)

if exist "dist" (
    echo   - Eliminando carpeta dist...
    rmdir /s /q dist
    REM Si falla por archivos bloqueados, intentar con eliminacion forzada
    if exist "dist" (
        echo   - Forzando eliminacion de dist...
        rd /s /q dist 2>nul
        if exist "dist" (
            echo   ADVERTENCIA: No se pudo eliminar dist completamente
            echo   Cierre manualmente cualquier archivo/proceso en dist
            pause
            rmdir /s /q dist
        )
    )
)

if exist "installer\FincaFacil_Setup_v1.0.exe" (
    echo   - Eliminando instalador antiguo...
    del /f /q "installer\FincaFacil_Setup_v1.0.exe"
)

REM Eliminar cache de Python
echo   - Limpiando cache de Python...
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist "*.pyc" del /f /q *.pyc

echo   OK - Limpieza completada
echo.

REM ========================================
REM PASO 2: VERIFICAR DEPENDENCIAS
REM ========================================
echo [2/6] Verificando dependencias...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet --upgrade pyinstaller pyinstaller-hooks-contrib
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo instalacion de dependencias
    pause
    exit /b 1
)
echo   OK - Dependencias actualizadas
echo.

REM ========================================
REM PASO 3: VERIFICAR ARCHIVOS CRITICOS
REM ========================================
echo [3/6] Verificando archivos criticos...

if not exist "assets\Logo.ico" (
    echo ERROR: Falta assets\Logo.ico
    pause
    exit /b 1
)

if not exist "FincaFacil.spec" (
    echo ERROR: Falta FincaFacil.spec
    pause
    exit /b 1
)

echo   - main.py: OK
echo   - FincaFacil.spec: OK
echo   - assets\Logo.ico: OK
echo.

REM ========================================
REM PASO 4: COMPILAR CON PYINSTALLER
REM ========================================
echo [4/6] Compilando con PyInstaller...
echo.
echo   Esto puede tomar 5-10 minutos. Por favor espere...
echo.

pyinstaller --clean --noconfirm FincaFacil.spec

if errorlevel 1 (
    echo.
    echo ERROR: Fallo la compilacion
    echo Revise los mensajes de error arriba
    pause
    exit /b 1
)

echo.
echo   OK - Compilacion exitosa
echo.

REM ========================================
REM PASO 5: VERIFICAR RESULTADO
REM ========================================
echo [5/6] Verificando resultado de compilacion...

if not exist "dist\FincaFacil\FincaFacil.exe" (
    echo ERROR: No se genero el ejecutable
    pause
    exit /b 1
)

REM Contar archivos en dist para verificar que no esta vacio
for /f %%A in ('dir /b /s "dist\FincaFacil" ^| find /c /v ""') do set FILE_COUNT=%%A
echo   - Archivos en dist\FincaFacil: %FILE_COUNT%

if %FILE_COUNT% LSS 50 (
    echo ADVERTENCIA: Muy pocos archivos en dist (esperado: cientos)
    echo La compilacion puede estar incompleta
    pause
)

REM Copiar archivos adicionales (carpetas runtime)
echo   - Copiando archivos adicionales...
if not exist "dist\FincaFacil\assets" mkdir "dist\FincaFacil\assets"
if not exist "dist\FincaFacil\modules" mkdir "dist\FincaFacil\modules"
if not exist "dist\FincaFacil\database" mkdir "dist\FincaFacil\database"
if not exist "dist\FincaFacil\backup" mkdir "dist\FincaFacil\backup"
if not exist "dist\FincaFacil\logs" mkdir "dist\FincaFacil\logs"
if not exist "dist\FincaFacil\exports" mkdir "dist\FincaFacil\exports"

echo D | xcopy /E /I /Y "assets" "dist\FincaFacil\assets" >nul 2>&1
echo D | xcopy /E /I /Y "modules" "dist\FincaFacil\modules" >nul 2>&1

echo   OK - Dist verificado
echo.

REM ========================================
REM PASO 6: PRUEBA RAPIDA
REM ========================================
echo [6/6] Probando ejecutable...
echo.
echo   Abriendo FincaFacil.exe para prueba rapida...
echo   Si la ventana se abre correctamente, cierre la aplicacion.
echo.

start /wait "" "dist\FincaFacil\FincaFacil.exe"

echo.
echo   Si el programa abrio correctamente, presione cualquier tecla.
echo   Si NO abrio, presione Ctrl+C y reporte el problema.
pause >nul

REM ========================================
REM RESUMEN FINAL
REM ========================================
echo.
echo ========================================
echo   REBUILD COMPLETADO
echo ========================================
echo.
echo Ejecutable generado: dist\FincaFacil\FincaFacil.exe
echo.
echo SIGUIENTE PASO:
echo   Ejecutar: crear_instalador.bat
echo.
echo   O probar directamente desde:
echo   dist\FincaFacil\FincaFacil.exe
echo.
echo ========================================
pause
