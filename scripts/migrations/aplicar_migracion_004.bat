@echo off
echo ========================================
echo Aplicando Migracion 004 - Tabla Servicio
echo ========================================
echo.

echo Creando copia de seguridad...
if exist "database\fincafacil.db" (
    copy "database\fincafacil.db" "backup\fincafacil_pre_migracion_004_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db" >nul 2>&1
    echo Backup creado en backup\
) else (
    echo Base de datos no encontrada
    pause
    exit /b 1
)

echo.
echo Ejecutando migracion 004...
python scripts\migrations\004_add_servicio_table.py

echo.
echo ========================================
echo Migracion completada
echo ========================================
pause
