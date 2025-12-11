@echo off
echo ============================================
echo   COMPILANDO FINCAFACIL v2.0
echo ============================================
echo.

echo Limpiando archivos anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist FincaFacil.spec del /q FincaFacil.spec

echo.
echo Compilando con PyInstaller...
echo Esto puede tardar varios minutos...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name=FincaFacil ^
    --icon=src\assets\Logo.ico ^
    --add-data="src\assets;assets" ^
    --add-data="config;config" ^
    --add-data="database;database" ^
    --add-data="docs;docs" ^
    --hidden-import=customtkinter ^
    --hidden-import=PIL ^
    --hidden-import=openpyxl ^
    --hidden-import=reportlab ^
    --hidden-import=matplotlib ^
    --hidden-import=tkcalendar ^
    --hidden-import=modules.dashboard.dashboard_main ^
    --hidden-import=modules.animales ^
    --hidden-import=modules.salud ^
    --hidden-import=modules.reproduccion ^
    --hidden-import=modules.leche ^
    --hidden-import=modules.potreros ^
    --hidden-import=modules.ventas ^
    --hidden-import=modules.nomina ^
    --hidden-import=modules.herramientas ^
    --hidden-import=modules.insumos ^
    --hidden-import=modules.reportes ^
    --hidden-import=modules.configuracion ^
    --hidden-import=modules.ajustes ^
    --hidden-import=modules.utils ^
    main.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo   COMPILACION EXITOSA
    echo ============================================
    echo.
    echo Ejecutable generado en: dist\FincaFacil.exe
    echo Tamano aproximado: 200-300 MB
    echo.
    echo Prueba el ejecutable antes de distribuir:
    echo   cd dist
    echo   FincaFacil.exe
    echo.
) else (
    echo ============================================
    echo   ERROR EN LA COMPILACION
    echo ============================================
    echo.
    echo Revisa los errores anteriores
    echo.
)

pause
