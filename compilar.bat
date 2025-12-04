@echo off
REM ========================================
REM   COMPILADOR DE FINCAFACIL
REM   Genera ejecutable para distribución
REM ========================================

echo.
echo ========================================
echo   FINCAFACIL - COMPILADOR
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ERROR: Este script debe ejecutarse desde la raiz del proyecto
    echo Asegurate de estar en la carpeta FincaFacil
    pause
    exit /b 1
)

REM ========================================
REM PASO 1: Instalar PyInstaller
REM ========================================
echo [1/5] Instalando PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo     OK - PyInstaller instalado
echo.

REM ========================================
REM PASO 2: Crear icono
REM ========================================
echo [2/5] Generando icono de aplicacion...
python scripts\crear_icono_instalador.py
if errorlevel 1 (
    echo ADVERTENCIA: No se pudo crear el icono
    echo La compilacion continuara sin icono personalizado
)
echo.

REM ========================================
REM PASO 3: Limpiar compilaciones anteriores
REM ========================================
echo [3/5] Limpiando archivos de compilaciones anteriores...
if exist "build" (
    rmdir /s /q build
    echo     - Carpeta build eliminada
)
if exist "dist" (
    rmdir /s /q dist
    echo     - Carpeta dist eliminada
)
echo     OK - Limpieza completada
echo.

REM ========================================
REM PASO 4: Compilar con PyInstaller
REM ========================================
echo [4/5] Compilando aplicacion con PyInstaller...
echo.
echo Esto puede tomar varios minutos...
echo Por favor espere...
echo.

pyinstaller --clean FincaFacil.spec

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo
    echo Revise los errores mostrados arriba
    pause
    exit /b 1
)
echo.
echo     OK - Compilacion exitosa
echo.

REM ========================================
REM PASO 5: Copiar base de datos y archivos
REM ========================================
echo [5/5] Copiando archivos adicionales...

REM Crear carpetas necesarias en dist
if not exist "dist\FincaFacil\database" mkdir "dist\FincaFacil\database"
if not exist "dist\FincaFacil\backup" mkdir "dist\FincaFacil\backup"
if not exist "dist\FincaFacil\exports" mkdir "dist\FincaFacil\exports"
if not exist "dist\FincaFacil\logs" mkdir "dist\FincaFacil\logs"
if not exist "dist\FincaFacil\uploads" mkdir "dist\FincaFacil\uploads"
if not exist "dist\FincaFacil\assets" mkdir "dist\FincaFacil\assets"
if not exist "dist\FincaFacil\modules" mkdir "dist\FincaFacil\modules"

REM Copiar archivos importantes
echo     - Creando estructura de carpetas
if not exist "dist\FincaFacil\docs" mkdir "dist\FincaFacil\docs"
echo F | xcopy /Y /Q "README.md" "dist\FincaFacil\README.md" > nul
echo F | xcopy /Y /Q "docs\Manual_Usuario_FincaFacil.md" "dist\FincaFacil\docs\Manual_Usuario_FincaFacil.md" > nul

REM Copiar recursos visuales y modulos de la app (por si el .spec no los incluyo)
echo     - Copiando assets y modules
echo D | xcopy /E /I /Y "assets" "dist\FincaFacil\assets" > nul
echo D | xcopy /E /I /Y "modules" "dist\FincaFacil\modules" > nul

REM Crear archivo de base de datos vacío si no existe
if not exist "dist\FincaFacil\database\fincafacil.db" (
    echo. > "dist\FincaFacil\database\fincafacil.db"
    echo     - Base de datos vacia creada
)

echo     OK - Archivos copiados
echo.

REM ========================================
REM RESUMEN FINAL
REM ========================================
echo ========================================
echo   COMPILACION COMPLETADA
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\FincaFacil\
echo.
echo Contenido:
echo   - FincaFacil.exe         (Ejecutable principal)
echo   - assets\                (Recursos visuales)
echo   - modules\               (Modulos del sistema)
echo   - database\              (Base de datos)
echo   - docs\                  (Documentacion)
echo.
echo Siguiente paso:
echo   Ejecutar: crear_instalador.bat
echo.
echo ========================================
pause
