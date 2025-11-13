@echo off
echo ========================================
echo   Abriendo Base de Datos FincaFacil
echo ========================================
echo.
echo Ubicacion: database\fincafacil.db
echo.
echo Si tienes DB Browser for SQLite instalado,
echo se abrira automaticamente.
echo.
echo Si no, puedes usar el script Python:
echo   python ver_base_datos.py
echo.
pause

REM Intentar abrir con DB Browser si está instalado
start "" "database\fincafacil.db" 2>nul || (
    echo.
    echo No se pudo abrir automaticamente.
    echo Instala DB Browser for SQLite desde:
    echo https://sqlitebrowser.org/
    echo.
    pause
)

