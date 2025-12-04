@echo off
REM ============================================
REM  Abrir Manual PDF - FincaFacil
REM ============================================

echo.
echo ========================================
echo   ABRIENDO MANUAL PDF
echo ========================================
echo.

REM Verificar si existe el PDF
if not exist "docs\Manual_Usuario_FincaFacil.pdf" (
    echo ERROR: Manual PDF no encontrado
    echo Generando manual...
    python utils\pdf_manual_generator.py
    echo.
)

REM Abrir el PDF
echo Abriendo Manual_Usuario_FincaFacil.pdf...
start "" "docs\Manual_Usuario_FincaFacil.pdf"

echo.
echo Manual PDF abierto correctamente
echo.
pause
