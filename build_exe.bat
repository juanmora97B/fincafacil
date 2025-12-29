@echo off
cd /d c:\Users\lenovo\Desktop\FincaFacil
echo [%DATE% %TIME%] Iniciando build PyInstaller...
pyinstaller --noconfirm FincaFacil.spec
echo [%DATE% %TIME%] Build completado.
dir dist\FincaFacil.exe
pause
