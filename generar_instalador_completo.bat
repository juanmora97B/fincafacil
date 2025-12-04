@echo off
REM ========================================
REM   GENERADOR COMPLETO DE INSTALADOR
REM   Ejecuta todo el proceso automaticamente
REM ========================================

title FincaFacil - Generador de Instalador

echo.
echo ============================================================
echo         FINCAFACIL - GENERADOR DE INSTALADOR COMPLETO
echo ============================================================
echo.
echo Este script ejecutara automaticamente:
echo   1. Instalacion de dependencias
echo   2. Compilacion del ejecutable
echo   3. Creacion del instalador
echo.
echo Tiempo estimado: 10-15 minutos
echo.
pause

REM ========================================
REM FASE 1: INSTALACIÓN DE DEPENDENCIAS
REM ========================================
echo.
echo ============================================================
echo   FASE 1/3: INSTALACION DE DEPENDENCIAS
echo ============================================================
echo.

REM Verificar Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo.
    echo Por favor instale Python 3.8 o superior
    echo Descarga: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python detectado:
python --version
echo.

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip --quiet
echo OK - pip actualizado
echo.

REM Instalar dependencias del proyecto
echo Instalando dependencias del proyecto...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Fallo la instalacion de dependencias
    pause
    exit /b 1
)
echo OK - Dependencias instaladas
echo.

REM Instalar PyInstaller
echo Instalando PyInstaller...
pip install pyinstaller==6.3.0 --quiet
if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo OK - PyInstaller instalado
echo.

echo ============================================================
echo   FASE 1 COMPLETADA
echo ============================================================
timeout /t 3 /nobreak > nul

REM ========================================
REM FASE 2: COMPILACIÓN DEL EJECUTABLE
REM ========================================
echo.
echo ============================================================
echo   FASE 2/3: COMPILACION DEL EJECUTABLE
echo ============================================================
echo.

call compilar.bat

if errorlevel 1 (
    echo.
    echo ERROR: La compilacion fallo
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   FASE 2 COMPLETADA
echo ============================================================
timeout /t 3 /nobreak > nul

REM ========================================
REM FASE 3: CREACIÓN DEL INSTALADOR
REM ========================================
echo.
echo ============================================================
echo   FASE 3/3: CREACION DEL INSTALADOR
echo ============================================================
echo.

call crear_instalador.bat

if errorlevel 1 (
    echo.
    echo ERROR: La creacion del instalador fallo
    pause
    exit /b 1
)

REM ========================================
REM RESUMEN FINAL COMPLETO
REM ========================================
cls
echo.
echo ============================================================
echo               PROCESO COMPLETADO EXITOSAMENTE
echo ============================================================
echo.
echo   _____ _                ______           _ _ 
echo  ^|  ___^(_^)              ^|  ____^|         ^(_^) ^|
echo  ^| ^|_   _ _ __   ___ __ ^| ^|__ __ _  ___ _^| ^|
echo  ^|  _^| ^| ^| '_ \ / __/ _`^|  __/ _` ^|/ __^| ^| ^|
echo  ^| ^|   ^| ^| ^| ^| ^| (_^| (_^| ^| ^| ^| (_^| ^| (__^| ^| ^|
echo  ^\_^|   ^|_^|_^| ^|_^|\___\__,_^|_^|  \__,_^|\___^|_^|_^|
echo.
echo ============================================================
echo.

REM Obtener tamaño del instalador
for %%F in (installer\*.exe) do (
    echo INSTALADOR GENERADO:
    echo   Archivo: %%~nxF
    echo   Ubicacion: %CD%\installer\
    echo   Tamano: %%~zF bytes
    set INSTALLER_NAME=%%~nxF
)

echo.
echo ============================================================
echo   CONTENIDO DEL INSTALADOR
echo ============================================================
echo.
echo El instalador incluye:
echo   [X] Ejecutable FincaFacil.exe
echo   [X] Base de datos SQLite
echo   [X] Modulos del sistema completos
echo   [X] Assets y recursos visuales
echo   [X] Manual de usuario PDF
echo   [X] Tour interactivo
echo   [X] Sistema de backup automatico
echo   [X] Generador de reportes
echo   [X] Exportador Excel
echo   [X] Sistema de notificaciones
echo   [X] Configuracion inicial
echo.
echo ============================================================
echo   METODOS DE DISTRIBUCION
echo ============================================================
echo.
echo Puede distribuir el instalador mediante:
echo.
echo   1. USB / Pendrive
echo      - Copie el archivo .exe al dispositivo
echo      - Entregue al cliente
echo.
echo   2. Descarga en Linea
echo      - Suba a Google Drive / Dropbox / OneDrive
echo      - Comparta el enlace de descarga
echo.
echo   3. Servidor Web
echo      - Suba a su servidor
echo      - Proporcione URL de descarga
echo.
echo   4. Email (si tamano lo permite)
echo      - Adjunte el archivo
echo      - Envie al cliente
echo.
echo   5. Red Local
echo      - Compartir carpeta en red
echo      - Cliente copia y ejecuta
echo.
echo ============================================================
echo   INSTRUCCIONES PARA EL CLIENTE
echo ============================================================
echo.
echo El cliente debe:
echo   1. Ejecutar: %INSTALLER_NAME%
echo   2. Seguir el asistente de instalacion
echo   3. Elegir ubicacion de instalacion
echo   4. Confirmar instalacion
echo   5. Iniciar FincaFacil desde el Menu Inicio
echo.
echo PRIMER USO:
echo   - Se mostrara un tour interactivo automatico
echo   - La base de datos se crea automaticamente
echo   - Manual PDF disponible en Ajustes
echo.
echo ============================================================
echo   REQUISITOS DEL CLIENTE
echo ============================================================
echo.
echo El equipo del cliente debe tener:
echo   [X] Windows 10/11 (64 bits)
echo   [X] 4 GB RAM minimo (8 GB recomendado)
echo   [X] 500 MB espacio en disco
echo   [X] Resolucion minima: 1366x768
echo.
echo NO REQUIERE:
echo   [ ] Python instalado
echo   [ ] Dependencias adicionales
echo   [ ] Conexion a internet
echo   [ ] Configuracion tecnica
echo.
echo ============================================================
echo   SOPORTE Y DOCUMENTACION
echo ============================================================
echo.
echo Documentacion incluida:
echo   - Manual de usuario PDF completo
echo   - Tour interactivo paso a paso
echo   - Ayuda contextual en cada modulo
echo.
echo Archivos generados en este proceso:
echo   - dist\FincaFacil\           (Ejecutable y recursos)
echo   - installer\%INSTALLER_NAME% (Instalador final)
echo.
echo ============================================================
echo.
echo Presione cualquier tecla para abrir la carpeta del instalador...
pause > nul

REM Abrir carpeta del instalador
explorer /select,"%CD%\installer\%INSTALLER_NAME%"

echo.
echo Proceso finalizado. Puede cerrar esta ventana.
echo.
pause
