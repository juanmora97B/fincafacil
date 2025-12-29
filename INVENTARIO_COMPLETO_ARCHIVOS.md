# 📋 INVENTARIO COMPLETO DE ARCHIVOS - FINCAFACIL

**Fecha:** 16 de Diciembre de 2025  
**Versión:** 2.0.0  
**Total de archivos:** 108 archivos Python + documentación

---

## 📑 TABLA DE CONTENIDOS

1. [Archivos Raíz (Root)](#archivos-raíz)
2. [Carpeta SRC - Estructura Principal](#carpeta-src)
3. [Módulos Funcionales](#módulos-funcionales)
4. [Scripts de Utilidad](#scripts-de-utilidad)
5. [Documentación](#documentación)
6. [Configuración y Base de Datos](#configuración-y-base-de-datos)
7. [Otros Directorios](#otros-directorios)

---

## ARCHIVOS RAÍZ

### Punto de Entrada y Lanzadores

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **main.py** | `/` | Punto de entrada principal de la aplicación. Inicializa la interfaz gráfica con CustomTkinter, gestiona la barra lateral y carga los módulos. |
| **launcher.py** | `/` | Lanzador Python alternativo. Ejecuta la aplicación desde Python directamente sin depender de BAT. |
| **FincaFacil.bat** | `/` | Lanzador Windows. Script batch para ejecutar la aplicación desde Windows sin abrir terminal. |
| **iniciar.bat** | `/` | Alias de FincaFacil.bat para acceso rápido. |

### Configuración

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **config.py** | `/` | Configuración global del sistema. Define rutas, constantes, parámetros de la BD, colores, fuentes. |
| **conftest.py** | `/` | Configuración para pytest. Define fixtures y configuración para pruebas unitarias. |
| **pyproject.toml** | `/` | Metadatos del proyecto. Nombre, versión, dependencias, información de autor. |
| **requirements.txt** | `/` | Dependencias Python. Lista todas las librerías necesarias (CustomTkinter, Pillow, openpyxl, etc). |

### Instalación y Compilación

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **FincaFacil.iss** | `/` | Configuración Inno Setup. Define cómo se genera el instalador EXE para Windows. |
| **FincaFacil.spec** | `/` | Configuración PyInstaller. Define cómo compilar la aplicación Python a ejecutable. |
| **FincaFacil_Debug.spec** | `/` | Configuración PyInstaller (versión debug). Para desarrollo con información adicional. |

### Documentación Técnica

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **README.md** | `/` | Documentación principal consolidada. Guía de instalación, características, estructura, requisitos. |
| **START_HERE.md** | `/` | Guía de inicio rápido. Instrucciones para comenzar a usar la aplicación. |
| **ENTREGA.md** | `/` | Documento técnico de entrega. Especificaciones técnicas, arquitectura, cambios. |
| **.gitignore** | `/` | Control de versiones. Define qué archivos ignorar en Git. |
| **LICENSE.txt** | `/` | Licencia del software. Términos legales de uso. |

### Informes y Resúmenes

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **DELIVERY_COMPLETE.txt** | `/` | Checklist final de entrega. Verifica que todo esté listo para cliente. |
| **DELIVERY_README.txt** | `/` | Instrucciones para cliente. Cómo instalar y ejecutar la aplicación. |
| **RESUMEN_ENTREGA.txt** | `/` | Resumen ejecutivo. Características, módulos, tecnología utilizada. |
| **LIMPIEZA_FINAL_RESUMEN.txt** | `/` | Reporte de limpieza final. Cambios realizados, archivo obsoletos eliminados. |
| **EMPAQUETAMIENTO_ZIP.txt** | `/` | Guía de empaquetamiento. Cómo preparar el ZIP para distribución. |
| **REORGANIZACION_INFORME.txt** | `/` | Informe de reorganización de estructura. Cambios en carpetas. |
| **REPORTE_ANALISIS_PROYECTO.md** | `/` | Análisis del proyecto. Métricas, problemas potenciales, propuestas. |
| **INFORME_AUDITORIA_TECNICA_FINAL.md** | `/` | Auditoría técnica final. Validación de código, seguridad, estándares. |
| **FASE_3_OPTIMIZACION_ENPROGRESO.md** | `/` | Documentación de optimizaciones en progreso. |

---

## CARPETA SRC

### Estructura Principal (src/)

```
src/
├── main.py                 # Punto de entrada (duplicado en src/)
├── config/                 # Configuración
├── database/               # Base de datos
├── modules/                # Módulos funcionales
├── assets/                 # Recursos
├── styles/                 # Estilos
├── utils/                  # Utilidades compartidas
└── logs/                   # Registros de aplicación
```

### src/main.py

| Archivo | Función |
|---------|---------|
| **main.py** | Punto de entrada principal. Inicializa CustomTkinter, crea ventana principal, gestiona barra lateral con botones de módulos, maneja navegación entre módulos, inicializa tour interactivo. |

---

## CARPETA DATABASE

### Gestión de Base de Datos (src/database/)

| Archivo | Función |
|---------|-----------|
| **database.py** | Gestor de base de datos. Crea y valida esquema, ejecuta migraciones, inicializa tablas, gestiona índices. |
| **connection.py** | Conexión SQLite. Crea pool de conexiones, aplica PRAGMAs (WAL, foreign keys, busy_timeout), recuperación de errores. |
| **__init__.py** | Inicializador. Expone funciones públicas de BD. |

**Tablas SQLite (21 tablas):**
- animales
- movimientos_animales
- salud_animal
- reproduccion
- destete
- leche
- ventas
- insumos
- movimientos_insumos
- herramientas
- movimientos_herramientas
- empleados
- trabajadores_herramientas
- nómina
- pagos
- potreros
- fincas
- razas
- empleado_roles
- tratamientos_medicamentos
- catalogo_datos

---

## MÓDULOS FUNCIONALES

### Módulo Animales (src/modules/animales/)

**Descripción:** Gestión completa de inventario animal con genealogía, historial, movimientos.

| Archivo | Función |
|---------|---------|
| **animales_main.py** | Interfaz principal de animales. TreeView con búsqueda avanzada, filtros, botones CRUD, gestión de movimientos. |
| **service.py** | Lógica de negocio de animales. Validaciones, cálculos de edades, reglas de reproducción. |
| **registro_animal.py** | Ventana para registrar nuevo animal. Formulario con campos: ID, nombre, raza, finca, fecha nacimiento. |
| **modal_editar_animal.py** | Modal para editar animal existente. Permite modificar datos principales. |
| **modal_ver_animal.py** | Modal para ver detalles animal. Mostrar información completa (historial, movimientos, fotos). |
| **modal_reubicar_animal.py** | Modal para cambiar potreros/fincas. Registra movimiento de animal. |
| **ficha_animal.py** | Ficha técnica del animal. Información personalizada, genealogía, árbol familiar. |
| **inventario_v2.py** | Nuevo sistema de inventario (v2). Carga masiva de cambios de stock. |
| **inventario_rapido.py** | Inventario rápido. Entrada ágil de cambios de estado. |
| **importar_excel.py** | Importación de Excel. Lee plantillas, valida datos, carga animales masivamente. |
| **realizar_inventario.py** | Realizar inventario físico. Contar animales por potreros/fincas. |
| **actualizacion_inventario.py** | Actualización de cambios de inventario. Procesa cambios de estado (venta, muerte, etc). |
| **reubicacion.py** | Gestión de reubicaciones. Registra cambios de ubicación de animales. |
| **bitacora_comentarios.py** | Historial de comentarios. Notas y observaciones sobre animales. |
| **bitacora_reubicaciones.py** | Historial de reubicaciones. Log de movimientos entre potreros. |
| **bitacora_historial_reubicaciones.py** | Histórico detallado de reubicaciones. Vista temporal. |
| **ventana_graficas.py** | Gráficos y estadísticas de animales. Análisis visual de datos. |

### Módulo Dashboard (src/modules/dashboard/)

**Descripción:** Panel de control con indicadores clave en tiempo real.

| Archivo | Función |
|---------|---------|
| **dashboard_main.py** | Interfaz principal del dashboard. Widgets KPI (animales totales, producción, ventas), gráficos, últimas actividades, resumen de producción. |

### Módulo Reproducción (src/modules/reproduccion/)

**Descripción:** Gestión de reproducción animal y genealogía.

| Archivo | Función |
|---------|---------|
| **reproduccion_main.py** | Interfaz de reproducción. Registra cruces, gestiona progenitores, monitorea gestaciones, calcula fechas parto. |

### Módulo Salud (src/modules/salud/)

**Descripción:** Control de salud veterinaria y tratamientos.

| Archivo | Función |
|---------|---------|
| **salud_main.py** | Interfaz de salud. Registra diagnósticos, vacunaciones, tratamientos, medicamentos, alertas automáticas. |

### Módulo Leche (src/modules/leche/)

**Descripción:** Registro y seguimiento de producción lechera.

| Archivo | Función |
|---------|---------|
| **pesaje_leche.py** | Sistema de pesaje de leche. Registra producción diaria, genera reportes de lactancia. |

### Módulo Ventas (src/modules/ventas/)

**Descripción:** Gestión de ventas de productos y animales.

| Archivo | Función |
|---------|---------|
| **ventas_main.py** | Interfaz de ventas. Registra ventas de animales/productos, genera facturas, calcula ingresos. |

### Módulo Reportes (src/modules/reportes/)

**Descripción:** Generación de reportes y análisis de datos.

| Archivo | Función |
|---------|---------|
| **reportes_main.py** | Interfaz principal de reportes. Opciones de filtrado, generación de reportes customizados. |
| **reportes_profesional.py** | Generación de reportes profesionales. Formato PDF con logos, tablas, gráficos. |

### Módulo Insumos (src/modules/insumos/)

**Descripción:** Control de inventario de insumos y materiales.

| Archivo | Función |
|---------|---------|
| **insumos_main.py** | Interfaz de insumos. Gestiona stock, proveedores, compras, movimientos de materiales. |

### Módulo Herramientas (src/modules/herramientas/)

**Descripción:** Gestión de herramientas y equipos.

| Archivo | Función |
|---------|---------|
| **herramientas_main.py** | Interfaz de herramientas. Registra equipos, asignación a trabajadores, mantenimiento, depreciación. |

### Módulo Nómina (src/modules/nomina/)

**Descripción:** Gestión de nómina y pagos a empleados.

| Archivo | Función |
|---------|---------|
| **nomina_main.py** | Interfaz de nómina. Calcula salarios, genera comprobantes, registra pagos. |

### Módulo Potreros (src/modules/potreros/)

**Descripción:** Gestión de potreros y áreas de pastoreo.

| Archivo | Función |
|---------|---------|
| **potreros_main.py** | Interfaz de potreros. Registra áreas de pastoreo, capacidad, rotación de animales. |

### Módulo Configuración (src/modules/configuracion/)

**Descripción:** Gestión de catálogos y datos maestros del sistema.

| Archivo | Función |
|---------|---------|
| **__main__.py** | Ejecutable del módulo. Entry point para ejecutar configuración independientemente. |
| **fincas.py** | Catálogo de fincas. Registra propiedades, ubicaciones, información de contacto. |
| **razas.py** | Catálogo de razas. Define tipos de ganado disponibles en el sistema. |
| **empleados.py** | Catálogo de empleados. Registra trabajadores, roles, datos de contacto. |
| **proveedores.py** | Catálogo de proveedores. Información de suministradores de insumos. |
| **sectores.py** | Catálogo de sectores. Áreas o divisiones de fincas. |
| **lotes.py** | Catálogo de lotes. Grupos de animales con características similares. |
| **potreros.py** | Catálogo de potreros. Actualiza información de pastizales. |
| **motivos_venta.py** | Catálogo de motivos venta. Razones para vender animales (carne, reproducción, etc). |
| **destino_venta.py** | Catálogo de destinos venta. Dónde van los animales vendidos. |
| **causa_muerte.py** | Catálogo de causas de muerte. Razones de deceso de animales. |
| **diagnosticos.py** | Catálogo de diagnósticos. Enfermedades y problemas de salud. |
| **procedencia.py** | Catálogo de procedencia. De dónde vinieron los animales (compra, nacimiento). |
| **tipo_explotacion.py** | Catálogo de tipos de explotación. Tipo de ganadería (lechería, cría, etc). |
| **condiciones_corporales.py** | Catálogo de condiciones corporales. Estados físicos de animales. |
| **calidad_animal.py** | Catálogo de calidad animal. Clasificación de calidad genética. |

### Módulo Ajustes (src/modules/ajustes/)

**Descripción:** Configuración general de la aplicación.

| Archivo | Función |
|---------|---------|
| **ajustes_main.py** | Interfaz de ajustes. Preferencias de usuario, configuración de copia seguridad, tour interactivo, tema. |

---

## CARPETA UTILITIES (Utilidades Compartidas)

### src/modules/utils/

**Descripción:** Módulo centralizado de utilidades reutilizables en toda la aplicación.

| Archivo | Función |
|---------|-----------|
| **app_paths.py** | Gestión de rutas. Define rutas para documentos, bases de datos, logs, assets. |
| **colores.py** | Paleta de colores. Define colores de tema, accesibilidad, constantes visuales. |
| **constants_ui.py** | Constantes de UI. Dimensiones, fuentes, bordes, espaciados. |
| **data_filters.py** | Filtros de datos. Lógica de búsqueda y filtrado avanzado. |
| **date_picker.py** | Selector de fechas custom. Widget de fecha personalizado. |
| **database_helpers.py** | Helpers de BD. Funciones auxiliares para consultas comunes. |
| **animal_format.py** | Formato de datos de animales. Convierte datos a formato visualizable. |
| **validators.py** | Validadores. Verifica formato de emails, teléfonos, IDs, etc. |
| **validaciones.py** | Validaciones de negocio. Reglas de validación específicas del dominio. |
| **ui.py** | Componentes UI comunes. Widgets reutilizables: botones, campos, etc. |
| **icons.py** | Sistema de iconos. Genera/proporciona iconos para botones y menús. |
| **units_helper.py** | Conversión de unidades. Convierte kg↔libras, etc. |
| **logger.py** | Sistema de logging. Registra eventos, errores, auditoría. |
| **db_logging.py** | Logging en BD. Registra eventos importantes en base de datos. |
| **notificaciones.py** | Sistema de notificaciones. Alertas, confirmaciones, avisos. |
| **sistema_alertas.py** | Sistema de alertas automáticas. Notifica eventos críticos. |
| **tour_manager.py** | Gestor de tour interactivo. Pasos, instrucciones para primer uso. |
| **tour_state_manager.py** | Estado del tour. Guarda progreso del tour interactivo. |
| **global_tour.py** | Tour global. Pasos adicionales del tour en múltiples módulos. |
| **preferences_manager.py** | Gestor de preferencias. Guarda configuración de usuario. |
| **usuario_manager.py** | Gestor de usuarios. Gestiona cuentas de usuario y permisos. |
| **login_ui.py** | Interfaz de login. Pantalla de inicio de sesión. |
| **license_manager.py** | Gestor de licencias. Valida licencia, maneja expiración. |
| **license_ui.py** | Interfaz de licencias. Muestra información de licencia. |
| **metadata.py** | Metadatos de la aplicación. Versión, autor, información del build. |
| **importador_excel.py** | Importador de Excel. Lee archivos Excel, valida datos, carga información. |
| **exportador_datos.py** | Exportador de datos. Exporta a Excel, CSV, PDF. |
| **plantillas_carga.py** | Plantillas de carga. Genera templates Excel para importación. |
| **pdf_generator.py** | Generador de PDF. Crea reportes en PDF con reportlab. |
| **pdf_manual_generator.py** | Generador de manual PDF. Crea manual de usuario en PDF. |

---

## CARPETA SCRIPTS

### Scripts de Compilación (scripts/)

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **build_exe_simple.py** | `scripts/` | Constructor simple de ejecutable. Compila con PyInstaller versión simplificada. |
| **build_pyinstaller.py** | `scripts/` | Constructor PyInstaller completo. Compilación avanzada con optimizaciones. |
| **generar_manual_pdf.py** | `scripts/` | Generador de manual PDF. Crea manual de usuario en PDF desde Markdown. |
| **generar_plantillas_completas.py** | `scripts/` | Generador de plantillas Excel. Crea templates para importación masiva. |
| **reorganizar_proyecto.py** | `scripts/` | Script de reorganización. Reestructura proyecto (crear src/, mover módulos, etc). |

### Scripts de Utilidad (scripts/utilities/)

| Archivo | Ubicación | Función |
|---------|-----------|---------|
| **verificar_demo_manual.py** | `scripts/utilities/` | Verificador de manual. Valida que manual PDF esté generado correctamente. |

---

## CARPETA ASSETS

### Recursos (src/assets/)

| Archivo | Función |
|---------|---------|
| **generate_svg_icons.py** | Generador de iconos SVG. Script para crear iconos gráficos vectoriales. |
| **[imágenes, iconos]** | Assets visuales para la interfaz (logos, botones, etc). |

---

## CARPETA STYLES

### Estilos (src/styles/)

| Archivo | Función |
|---------|---------|
| **[CSS/temas]** | Definición de temas visuales, colores, fuentes para CustomTkinter. |

---

## CARPETA CONFIG

### Configuración (src/config/)

| Archivo | Función |
|---------|---------|
| **[archivos configuración]** | Archivos de configuración específicos por módulo. |

---

## CARPETA LOGS

### Registros (src/logs/)

| Archivo | Función |
|---------|---------|
| **[archivos .log]** | Registros de eventos, errores, auditoría de la aplicación. |

---

## CARPETA DOCS

### Documentación (docs/)

**Estructura:**

```
docs/
├── INDEX.md                              # Índice de documentación
├── Manual_Usuario_FincaFacil.md         # Manual usuario Markdown
├── Manual_Usuario_FincaFacil.pdf        # Manual usuario PDF
├── Manual_FincaFacil_v2.pdf             # Manual v2 PDF
├── MANUAL_PROFESIONAL.md                # Manual técnico profesional
├── TOUR_INTERACTIVO.md                  # Documentación tour
├── ARQUITECTURA_DATOS_DEFINITIVA.md     # Arquitectura de datos
├── RESUMEN_CAMBIOS_ARQUITECTURA_FINCA.md # Cambios en arquitectura
├── CODIGOS_ACTIVACION.md                # Códigos de licencia
├── LICENCIA.txt                         # Archivo de licencia
├── licencia.html                        # Licencia en HTML
├── ANTES_DE_INSTALAR.txt                # Info preinstalación
├── DESPUES_DE_INSTALAR.txt              # Info posinstalación
├── PRIMER_USO.txt                       # Primer uso
├── INSTALACION.txt                      # Instrucciones instalación
│
├── guias/                               # Guías de usuario
│   ├── GUIA_DISTRIBUCION.md
│   ├── GUIA_RAPIDA_CLIENTE.md
│   ├── GUIA_RAPIDA_FOTOS_HERRAMIENTAS.md
│   ├── INSTRUCCIONES_CLIENTE.txt
│   ├── INSTRUCCIONES_IMPORTACION.md
│   ├── INSTRUCCIONES_INSTALACION_CLIENTE.md
│   ├── INSTRUCCIONES_VERIFICACION_COMBOBOX.md
│   ├── INICIO_RAPIDO_INSTALADOR.md
│   └── [más guías]
│
├── tecnico/                             # Documentación técnica
│   ├── COMPILACION_README.md
│   └── [especificaciones técnicas]
│
├── reportes/                            # Reportes y análisis
│   ├── ANALISIS_COMPLETO_PROYECTO.md
│   ├── ARQUITECTURA_FINCA_COMPLETADA.md
│   ├── INFORME_LIMPIEZA_CODIGO.md
│   ├── INFORME_PRUEBAS_DATOS_REALES.md
│   ├── INVENTARIO_V2_DOCS.md
│   ├── INVENTARIO_V2_ENTREGA.md
│   ├── INVENTARIO_V2_INTEGRACION.md
│   ├── INVENTARIO_V2_INDICE.md
│   ├── INVENTARIO_V2_RESUMEN_FINAL.md
│   └── [más reportes]
│
├── historico/                           # Historial de cambios
│   ├── CHANGELOG.md
│   └── [histórico de versiones]
│
├── historico_correcciones/              # Correcciones aplicadas
│   ├── LIMPIEZA_COMPLETADA.md
│   ├── CORRECCION_ANIMALES_NACIMIENTO_COMPRA.md
│   ├── CORRECCION_ELIMINACION_MOVIMIENTOS.md
│   ├── CORRECCION_ERRORES_CRITICOS.md
│   ├── CORRECCION_FILTRADO_FINCAS_COMPLETADA.md
│   ├── CORRECCION_MAPEOS_INSUMOS_COMPLETADA.md
│   ├── CORRECCION_STOCK_ACTUAL.md
│   ├── CORRECCIONES_MODULO_INSUMOS.md
│   ├── IMPLEMENTACION_CASE_INSENSITIVE.md
│   ├── DIAGNOSTICO_COMBOBOX_FINCAS_RAZAS.md
│   └── [más correcciones]
│
├── cambios/                             # Documentación de cambios
│   ├── CAMBIOS_RUTAS_APPDATA.md
│   └── [cambios varios]
│
├── api/                                 # Documentación API
└── referencias/                         # Referencias técnicas
```

---

## OTROS DIRECTORIOS

| Directorio | Función |
|-----------|---------|
| **database/** | Almacena base de datos SQLite (fincafacil.db). Base de datos de la aplicación. |
| **config/** | Archivos de configuración adicionales. Parámetros específicos del sistema. |
| **exports/** | Exportaciones de datos. Archivos generados (PDF, Excel) guardados aquí. |
| **uploads/** | Cargas de usuario. Archivos importados o subidos por usuario. |
| **plantillas de carga/** | Plantillas Excel. Templates para importación masiva de datos. |
| **backup/** | Copias de seguridad. Backups automáticos de base de datos. |
| **build/** | Archivos de compilación. Archivos intermedios de PyInstaller. |
| **dist/** | Distribución. Ejecutables generados por PyInstaller. |
| **.git/** | Control de versiones. Repositorio Git. |
| **.venv/** | Entorno virtual. Librerías Python aisladas del sistema. |
| **.vscode/** | Configuración VS Code. Settings, extensiones recomendadas. |
| **logs/** | Registros de aplicación. Archivos de log (.log). |
| **__pycache__/** | Caché de Python. Archivos compilados .pyc (ignorar). |

---

## RESUMEN ESTADÍSTICO

### Por Categoría

| Categoría | Cantidad | Ejemplos |
|-----------|----------|----------|
| **Módulos principales** | 13 | animales, dashboard, ventas, reportes, etc |
| **Utilidades compartidas** | 27 | logger, validators, icons, tour_manager, etc |
| **Scripts** | 6 | build, generar_manual, reorganizar, etc |
| **Documentación** | 30+ | Guías, manuales, reportes, análisis |
| **Configuración** | 4 | config.py, conftest.py, pyproject.toml, requirements.txt |
| **Base de Datos** | 3 | database.py, connection.py, schema |
| **Lanzadores** | 3 | main.py, launcher.py, FincaFacil.bat |

### Total de Archivos Python

```
Módulos:                 13 * 2-17 archivos = ~80 archivos
Utilidades:              27 archivos
Scripts:                 6 archivos
Configuración:           4 archivos
Database:                3 archivos
Lanzadores:              3 archivos
─────────────────────────────────────
TOTAL:                   ~108 archivos Python
```

---

## MAPEO DE DEPENDENCIAS

### Flujo Principal

```
main.py (Raíz)
    ├── Inicializa CustomTkinter
    ├── Carga config.py
    ├── Conecta a database/connection.py
    └── Carga módulos desde modules/
        ├── dashboard_main
        ├── animales_main
        ├── reproduccion_main
        ├── salud_main
        ├── leche/pesaje_leche
        ├── ventas_main
        ├── reportes_main
        ├── insumos_main
        ├── herramientas_main
        ├── nómina_main
        ├── potreros_main
        ├── configuracion/* (catálogos)
        └── ajustes_main
            ├── tour_manager
            ├── preferences_manager
            └── license_manager
        
        Todos usan:
        ├── modules/utils/* (iconos, validadores, logger, etc)
        ├── database/connection
        └── config.py
```

---

## ACCESO A ARCHIVOS IMPORTANTES

| Necesidad | Archivo |
|-----------|---------|
| Ver todas las funciones del módulo X | `src/modules/X/*_main.py` |
| Cambiar colores/tema | `src/modules/utils/colores.py` |
| Agregar validaciones | `src/modules/utils/validators.py` |
| Ver rutas de sistema | `src/modules/utils/app_paths.py` |
| Cambiar configuración global | `config.py` |
| Ver esquema BD | `src/database/database.py` |
| Cambiar credenciales BD | `src/database/connection.py` |
| Ver logs | `src/logs/*.log` |
| Generar reportes | `scripts/generar_manual_pdf.py` |
| Compilar ejecutable | `scripts/build_exe_simple.py` |
| Importar datos masivamente | `docs/guias/INSTRUCCIONES_IMPORTACION.md` |
| Contactar soporte | Ver info en `DELIVERY_README.txt` |

---

## CONVENCIONES DE NOMENCLATURA

### Archivos Python
- **_main.py**: Interfaz principal de cada módulo
- **service.py**: Lógica de negocio
- **modal_*.py**: Ventanas emergentes
- ***_manager.py**: Gestores de recursos
- ***_helpers.py**: Funciones auxiliares

### Carpetas
- `src/`: Código fuente principal
- `modules/`: Módulos funcionales
- `utils/`: Utilidades compartidas
- `database/`: Acceso a datos
- `scripts/`: Scripts de utilidad
- `docs/`: Documentación
- `assets/`: Recursos gráficos

---

## NOTAS IMPORTANTES

1. **Duplicados legados**: Existen archivos en `/modules/` (legacy) que son réplicas de `src/modules/`. Los de `src/` son los actuales.

2. **Migraciones**: Scripts históricos de migraciones están documentados en `docs/historico_correcciones/`.

3. **Base de datos**: Automáticamente se crea en primera ejecución (`database/fincafacil.db`).

4. **Tour interactivo**: 30+ pasos para guiar al usuario en primer uso.

5. **Licencia**: Sistema de códigos de activación integrado.

6. **Exportación**: Genera reportes en PDF y Excel automáticamente.

---

**Generado:** 16 de Diciembre de 2025  
**Versión:** FincaFácil v2.0.0  
**Estado:** ✅ PRODUCCIÓN
