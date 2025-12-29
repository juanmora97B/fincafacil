# Cambios de Rutas para Instalación en Program Files

## Resumen Ejecutivo
Se han movido todos los archivos modificables (base de datos y archivos de configuración) desde las carpetas de instalación a directorios de usuario, evitando problemas de permisos en `Program Files`.

## Cambios Implementados

### 1. Nuevo Módulo `app_paths.py`
**Ubicación:** `src/modules/utils/app_paths.py`

Proporciona funciones centralizadas para resolver rutas:
- `get_user_data_dir()`: Directorio base en `%LOCALAPPDATA%\FincaFacil`
- `get_database_dir()`: Subdirectorio para la base de datos
- `get_config_dir()`: Subdirectorio para configuraciones
- `get_db_path()`: Ruta completa a `fincafacil.db` en datos de usuario
- `get_config_file(name)`: Ruta a archivo de configuración específico
- `get_seed_path(relative)`: Ruta a archivos semilla empaquetados

### 2. Modificaciones en `database.py`
**Ubicación:** `src/database/database.py`

- **Importa** `app_paths` para rutas dinámicas
- **Define** `DB_PATH = get_db_path()` (ahora apunta a `%LOCALAPPDATA%\FincaFacil\database\fincafacil.db`)
- **Nueva función** `ensure_local_db()`: Copia la BD semilla al directorio de usuario en primera ejecución
- **Ejecuta** `ensure_local_db()` automáticamente al importar el módulo

### 3. Actualizaciones en `license_manager.py`
**Ubicación:** `src/modules/utils/license_manager.py`

- Usa `get_config_dir()` y `get_config_file("license.json")`
- Archivo de licencia ahora en `%LOCALAPPDATA%\FincaFacil\config\license.json`

### 4. Actualizaciones en `usuario_manager.py`
**Ubicación:** `src/modules/utils/usuario_manager.py`

- Usa `get_config_file("session.json")` para sesión de usuario
- Archivo de sesión ahora en `%LOCALAPPDATA%\FincaFacil\config\session.json`

### 5. Actualizaciones en `tour_state_manager.py`
**Ubicación:** `src/modules/utils/tour_state_manager.py`

- Usa `get_config_file("tour_state.json")`
- Estado del tour ahora en `%LOCALAPPDATA%\FincaFacil\config\tour_state.json`

### 6. Backups en `main.py` y `ajustes_main.py`
- Código de backup ahora usa `DB_PATH` dinámico
- Los backups se guardan en la carpeta `backup` relativa (podría moverse también a datos de usuario si es necesario)

### 7. Actualización de `FincaFacil.spec`
- **Añadido** `('database', 'database')` a `datas` para empaquetar la BD semilla
- Esto asegura que `database/fincafacil.db` se incluya en el ejecutable

## Estructura de Directorios (Después)

### En Program Files (solo lectura):
```
C:\Program Files\FincaFácil\
  ├── FincaFacil.exe
  ├── assets\           (iconos, recursos)
  ├── database\         (BD semilla, solo lectura)
  │   └── fincafacil.db
  └── docs\            (documentación)
```

### En Datos de Usuario (lectura/escritura):
```
%LOCALAPPDATA%\FincaFacil\
  ├── database\
  │   └── fincafacil.db  (copia activa)
  └── config\
      ├── license.json
      ├── session.json
      └── tour_state.json
```

## Flujo de Primera Ejecución

1. Usuario instala el programa en `C:\Program Files\FincaFácil`
2. Al iniciar `FincaFacil.exe`:
   - Se importa `database.database`
   - Se ejecuta `ensure_local_db()`
   - Si no existe `%LOCALAPPDATA%\FincaFacil\database\fincafacil.db`:
     - Se crea el directorio
     - Se copia desde el seed empaquetado
3. Todas las operaciones posteriores usan `DB_PATH` (en datos de usuario)
4. Archivos de configuración se crean automáticamente en `config/` cuando se necesitan

## Ventajas

✅ **Sin problemas de permisos:** Escritura en carpeta de usuario
✅ **Portable:** BD y configs se mueven con el perfil de usuario
✅ **Multi-usuario:** Cada usuario de Windows tiene sus propios datos
✅ **Backups seguros:** No requiere permisos de administrador
✅ **Actualizable:** Reinstalar no sobreescribe datos de usuario

## Próximos Pasos

1. ✅ Recompilar ejecutable con PyInstaller
2. ⏳ Actualizar instalador Inno Setup (si es necesario)
3. ⏳ Probar instalación y primera ejecución
4. ⏳ Verificar que la app se inicia correctamente desde Program Files
