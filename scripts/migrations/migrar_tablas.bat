@echo off
echo Creando copia de seguridad...
copy "database\fincafacil.db" "database\fincafacil_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%.db"

echo Ejecutando migración final...
python database\complete_migration.py

pause