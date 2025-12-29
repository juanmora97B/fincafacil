# 📊 REPORTE COMPLETO DE ANÁLISIS - FINCAFÁCIL

**Fecha:** 11 de Diciembre de 2025  
**Versión del Proyecto:** 2.0  
**Tipo:** Software de Gestión Ganadera (Desktop)  
**Plataforma:** Windows (Python 3.14 + CustomTkinter)

---

## 📋 TABLA DE CONTENIDOS

1. [Descripción General](#descripción-general)
2. [Arquitectura de Base de Datos](#arquitectura-de-base-de-datos)
3. [Estructura de Módulos](#estructura-de-módulos)
4. [Funcionamiento de Cada Módulo](#funcionamiento-de-cada-módulo)
5. [Componentes Técnicos](#componentes-técnicos)
6. [Flujo de Datos](#flujo-de-datos)
7. [Resumen Ejecutivo](#resumen-ejecutivo)

---

## 📖 Descripción General

### ¿Qué es FincaFácil?

**FincaFácil** es un sistema integral de gestión ganadera diseñado para administrar todas las operaciones de una finca de ganado. Permite:

✅ Registrar y gestionar animales individuales  
✅ Controlar potreros, sectores y ubicaciones  
✅ Seguimiento sanitario y veterinario  
✅ Gestión de reproducción y genealogía  
✅ Control de producción lechera  
✅ Gestión de ventas y movimientos  
✅ Inventario de herramientas e insumos  
✅ Nómina de empleados  
✅ Reportes profesionales y análisis  

### Tecnologías Utilizadas

- **Lenguaje:** Python 3.14
- **GUI:** CustomTkinter (interfaz moderna)
- **Base de Datos:** SQLite (fincafacil.db)
- **Empaquetamiento:** PyInstaller (ejecutable único)
- **Instalador:** Inno Setup 6

### Características Principales

- Interfaz gráfica moderna y profesional
- Base de datos normalizada con relaciones
- Módulos independientes pero integrados
- Sistema de usuarios y licencias
- Tour interactivo para primer uso
- Reportes exportables
- Logo y branding personalizado

---

## 🗄️ ARQUITECTURA DE BASE DE DATOS

### Estructura General

La base de datos contiene **20+ tablas** organizadas por funcionalidad:

#### **Tablas Maestras (Configuración)**
```
┌─────────────────────────────────────────┐
│  MAESTROS - Datos Base del Sistema      │
├─────────────────────────────────────────┤
│  raza               (razas de ganado)    │
│  finca              (propiedades)        │
│  potrero            (pasturas/terrenos)  │
│  sector             (divisiones finca)   │
│  lote               (agrupaciones)       │
│  vendedor           (proveedores)        │
│  diagnostico_veterinario (catálogo)     │
│  app_settings       (configuraciones)    │
└─────────────────────────────────────────┘
```

#### **Tabla Principal: ANIMAL**
```sql
CREATE TABLE animal (
    id INTEGER PRIMARY KEY,
    codigo TEXT UNIQUE,              -- Identificador único
    nombre TEXT,
    sexo TEXT,                       -- Macho/Hembra
    tipo_ingreso TEXT,               -- Nacimiento/Compra
    raza_id INTEGER,
    id_finca INTEGER,
    id_potrero INTEGER,
    id_sector INTEGER,
    
    -- Fechas clave
    fecha_nacimiento DATE,
    fecha_compra DATE,
    
    -- Pesos
    peso_nacimiento REAL,
    peso_compra REAL,
    precio_compra REAL,
    
    -- Genealogía
    id_padre INTEGER,
    id_madre INTEGER,
    
    -- Características
    color TEXT,
    hierro TEXT,
    composicion_racial TEXT,
    
    -- Estado
    estado TEXT,                     -- Activo/Inactivo
    salud TEXT,
    inventariado INTEGER,
    
    fecha_creacion TIMESTAMP,
    fecha_actualizacion TIMESTAMP
);
```

**Relaciones Principales:**
- animal ← raza (muchos a uno)
- animal ← finca (muchos a uno)
- animal ← potrero (muchos a uno)
- animal → animal (padre/madre - autorreferencia)

#### **Tablas de Eventos/Historial**
```
┌──────────────────────────────────────────────┐
│  EVENTOS - Seguimiento del Animal            │
├──────────────────────────────────────────────┤
│  reproduccion    (servicios, partos)         │
│  servicio        (monta/inseminación)        │
│  tratamiento     (veterinaria)               │
│  diagnostico_evento (eventos sanitarios)     │
│  comentario      (bitácora de notas)         │
│  peso            (histórico de pesajes)      │
│  produccion_leche (registro diario)          │
│  movimiento      (movimientos entre lotes)   │
│  muerte          (registro de defunciones)   │
│  reubicacion     (cambios de ubicación)      │
└──────────────────────────────────────────────┘
```

#### **Tablas de Inventario**
```
┌──────────────────────────────────────────────┐
│  INVENTARIO - Insumos y Herramientas         │
├──────────────────────────────────────────────┤
│  insumo              (medicamentos, alimentos) │
│  movimiento_insumo   (entradas/salidas)      │
│  herramienta         (equipos de finca)      │
│  mantenimiento_herramienta (servicios)       │
└──────────────────────────────────────────────┘
```

### Estadísticas de la BD
- **Tablas Totales:** 20+
- **Campos Totales:** ~150+
- **Relaciones Foráneas:** 25+
- **Índices Únicos:** 10+
- **Tipo Almacenamiento:** SQLite (portátil, sin servidor)

---

## 🏗️ ESTRUCTURA DE MÓDULOS

### Árbol de Directorios

```
src/
├── modules/                    # Módulos funcionales
│   ├── dashboard/             # Centro de control
│   ├── animales/              # Gestión animal (principal)
│   ├── configuracion/          # Setup maestros
│   ├── potreros/              # Gestión de potreros
│   ├── salud/                 # Módulo veterinario
│   ├── reproduccion/          # Reproducción animal
│   ├── leche/                 # Producción lechera
│   ├── ventas/                # Movimiento de ventas
│   ├── herramientas/          # Inventario de equipos
│   ├── insumos/               # Inventario de materiales
│   ├── nomina/                # Gestión empleados
│   ├── reportes/              # Generación de reportes
│   ├── ajustes/               # Configuración app
│   └── utils/                 # Funciones compartidas
│       ├── login_ui.py        # Login y registro
│       ├── tour_manager.py    # Sistema de tour
│       ├── logger.py          # Logging
│       ├── app_paths.py       # Rutas de datos
│       └── ... (más utilidades)
│
├── database/                  # Módulo de BD
│   ├── database.py           # Conexión y esquema
│   ├── connection.py         # Pool de conexiones
│   └── fincafacil.db         # Archivo SQLite
│
├── config.py                 # Configuración global
├── main.py                   # Punto de entrada
└── assets/                   # Imágenes e iconos
    ├── Logo.png
    ├── Logo.ico
    └── ... (módulos icons)
```

### Módulos Principales

| Módulo | Archivo | Funcionalidad | Tablas BD |
|--------|---------|---------------|-----------|
| **Dashboard** | `dashboard_main.py` | Centro de control, métricas y alertas | animal, tratamiento |
| **Animales** | `animales/__init__.py` | Registro, inventario, fichas individuales | animal, peso, comentario |
| **Configuración** | `configuracion/__main__.py` | Setup maestros (fincas, razas, sectores) | finca, raza, potrero, sector |
| **Potreros** | `potreros_main.py` | Gestión de potreros y ocupación | potrero, animal |
| **Salud** | `salud/*.py` | Seguimiento veterinario y tratamientos | tratamiento, diagnostico_evento |
| **Reproducción** | `reproduccion/*.py` | Servicios, partos, genealogía | reproduccion, servicio |
| **Leche** | `leche/*.py` | Registro de producción diaria | produccion_leche, animal |
| **Ventas** | `ventas/*.py` | Movimiento de animales vendidos | movimiento, animal |
| **Herramientas** | `herramientas/*.py` | Inventario de equipos | herramienta, mantenimiento_herramienta |
| **Insumos** | `insumos/*.py` | Inventario de materiales | insumo, movimiento_insumo |
| **Nómina** | `nomina/*.py` | Gestión de empleados | (tabla empleado - futura) |
| **Reportes** | `reportes_main.py` | Generación de reportes profesionales | todas |
| **Ajustes** | `ajustes_main.py` | Preferencias del sistema | app_settings |

---

## 🔧 FUNCIONAMIENTO DE CADA MÓDULO

### 1. 📊 DASHBOARD (Centro de Control)

**Propósito:** Pantalla inicial con resumen del sistema

**Funcionalidades:**
- Métricas rápidas: Total animales, activos, valor inventario, en tratamiento
- Gráfico circular: Distribución por razas
- Gráfico de barras: Estados de animales (Activo/Vendido/Muerto)
- Tabla de eventos recientes
- Sistema de alertas automáticas

**Alertas Generadas:**
- Animales sin raza asignada
- Animales sin potrero
- Tratamientos próximos a vencer
- Partos esperados en 30 días
- Animales en estado crítico

**Datos Mostrados:**
```
├── MÉTRICAS
│   ├── 🐄 Total Animales: COUNT(animal)
│   ├── ✅ Activos: COUNT(animal WHERE estado='Activo')
│   ├── 💰 Valor Inventario: SUM(precio_compra)
│   └── 🏥 En Tratamiento: COUNT(DISTINCT tratamiento)
├── GRÁFICOS
│   ├── Pie: Razas por cantidad
│   └── Bar: Estados de animales
├── EVENTOS
│   ├── Nuevos registros
│   ├── Tratamientos recientes
│   └── Movimientos
└── ALERTAS
    ├── Sanitarias
    ├── Reproductivas
    └── De inventario
```

---

### 2. 🐄 ANIMALES (Módulo Principal)

**Propósito:** Gestión integral del inventario ganadero

**Sub-módulos:**

#### **A) Registro Animal** (`registro_animal.py`)
- Registrar nuevos animales por:
  - **Nacimiento:** Padre, madre, fecha
  - **Compra:** Vendedor, precio, fecha
- Campos capturados:
  - Identificación (código, nombre)
  - Biología (sexo, raza, color, hierro)
  - Ubicación (finca, potrero, sector)
  - Características (peso nacimiento/compra, composición racial)
  - Foto del animal

#### **B) Inventario General** (`inventario.py`)
- Tabla listado de TODOS los animales
- Filtros por:
  - Finca
  - Sexo
  - Raza
  - Estado (Activo/Vendido/Muerto)
- Acciones:
  - Ver detalles
  - Editar
  - Buscar
  - Estadísticas

#### **C) Ficha Individual del Animal** (`ficha_animal.py`)
Información completa por animal en pestañas:
- **Pestaña 1: General**
  - Código, nombre, sexo, raza
  - Fechas (nacimiento, compra)
  - Precio, procedencia
  - Padres (genealogía)

- **Pestaña 2: Pesos**
  - Histórico de pesajes
  - Gráfico de ganancia de peso
  - Comparativas

- **Pestaña 3: Tratamientos**
  - Diagnósticos aplicados
  - Medicinas usadas
  - Fechas de aplicación
  - Próximos tratamientos

- **Pestaña 4: Comentarios**
  - Bitácora de notas
  - Observaciones por fecha

#### **D) Reubicación** (`reubicacion.py`)
- Mover animales entre:
  - Fincas
  - Potreros
  - Sectores
  - Lotes
- Registra motivo y fecha
- Actualiza automáticamente ubicación

#### **E) Actualización Inventario** (`actualizacion_inventario.py`)
- Cambiar estado masivo de animales
- Marcar como: Activo/Vendido/Muerto
- Bulk operations

---

### 3. ⚙️ CONFIGURACIÓN (Setup Maestros)

**Propósito:** Definir datos base que usa todo el sistema

**Sub-módulos:**

| Submódulo | Tabla | Descripción |
|-----------|-------|-------------|
| **Fincas** | `finca` | Propiedades principales, ubicación, propietario |
| **Sectores** | `sector` | Divisiones dentro de fincas |
| **Potreros** | `potrero` | Pasturas, tipo de pasto, capacidad |
| **Lotes** | `lote` | Agrupaciones de animales por criterio |
| **Razas** | `raza` | Tipos de ganado (Holstein, Jersey, Brahman, etc.) |
| **Calidad Animal** | `calidad_animal` | Estándares de calidad |
| **Condiciones Corporales** | `condicion_corporal` | Escala BCS (Body Condition Score) |
| **Tipos Explotación** | `tipo_explotacion` | Lechero, Carne, Doble Propósito |
| **Vendedores** | `vendedor` | Proveedores de ganado |
| **Motivos Venta** | `motivo_venta` | Razones de venta (descarte, reproducción) |
| **Diagnósticos** | `diagnostico_veterinario` | Catálogo de enfermedades |
| **Causas Muerte** | `causa_muerte` | Tipos de muertes |
| **Empleados** | `empleado` | Personal de la finca |

**Interfaz:** Menú lateral con 4 secciones:
1. **Ubicación:** Fincas, Sectores, Potreros, Lotes
2. **Animales:** Razas, Calidad, Condiciones, Explotación
3. **Comercial:** Vendedores, Motivos Venta, Destinos, Procedencias
4. **Salud:** Causas Muerte, Diagnósticos
5. **Personal:** Proveedores, Empleados

---

### 4. 🌿 POTREROS (Gestión de Pasturas)

**Propósito:** Control de ocupación y movimiento en potreros

**Funcionalidades:**
- Tabla de potreros con detalles
- Métricas rápidas:
  - Área hectáreas
  - Capacidad máxima
  - Animales actuales
  - % de ocupación
- Ver animales por potrero
- Detalles: tipo pasto, sector, estado

**Cálculos:**
```
Ocupación % = (Animales Actuales / Capacidad Máxima) × 100
```

---

### 5. 🏥 SALUD (Módulo Veterinario)

**Propósito:** Seguimiento sanitario y tratamientos

**Funcionalidades:**
- Registrar diagnósticos
- Aplicar tratamientos:
  - Medicamentos
  - Dosis
  - Duración (fecha inicio/fin)
- Seguimiento de recuperación
- Próximos tratamientos
- Historial por animal

**Tablas:**
- `tratamiento` (tratamientos aplicados)
- `diagnostico_evento` (eventos sanitarios)
- `diagnostico_veterinario` (catálogo de diagnósticos)

---

### 6. 🤰 REPRODUCCIÓN (Control Reproductivo)

**Propósito:** Gestión de servicios y genealogía

**Funcionalidades:**
- Registrar servicios:
  - Monta natural
  - Inseminación artificial
- Seguimiento de preñez
- Registro de partos:
  - Fecha real
  - Descendientes
- Genealogía (árbol familiar)
- Alertas de partos próximos

**Tablas:**
- `reproduccion` (estado reproductivo)
- `servicio` (servicios = monta/IA)

---

### 7. 🥛 LECHE (Producción Lechera)

**Propósito:** Registro y análisis de producción diaria

**Funcionalidades:**
- Registrar producción por:
  - Ordeño matutino
  - Ordeño vespertino
  - Ordeño nocturno
- Calidad de leche (grasa, proteína)
- Gráficas de tendencias
- Identificar vacas bajo rendimiento
- Proyecciones

**Tabla:** `produccion_leche`

---

### 8. 💰 VENTAS (Movimiento de Animales)

**Propósito:** Registro de ventas y salidas

**Funcionalidades:**
- Registrar venta:
  - Comprador
  - Precio
  - Motivo (descarte, reproducción)
  - Documentación
- Historial de transacciones
- Reportes de ingresos
- Trazabilidad

**Tabla:** `movimiento` (tipo='Salida')

---

### 9. 🔧 HERRAMIENTAS (Inventario de Equipos)

**Propósito:** Control de maquinaria y equipos

**Funcionalidades:**
- Registrar equipos:
  - Máquinas
  - Herramientas manuales
  - Equipos médicos
  - Vehículos
- Categorías por tipo
- Seguimiento:
  - Ubicación
  - Estado (Operativa/Mantenimiento/Dañada)
  - Responsable
- Mantenimiento preventivo/correctivo
- Valor de adquisición y depreciación

**Tablas:**
- `herramienta`
- `mantenimiento_herramienta`

---

### 10. 📦 INSUMOS (Inventario de Materiales)

**Propósito:** Control de medicamentos, alimentos, fertilizantes

**Funcionalidades:**
- Categorías:
  - Medicamentos
  - Alimentos
  - Fertilizantes
  - Semillas
  - Otros
- Stock control:
  - Stock actual
  - Stock mínimo
  - Stock máximo
  - Alertas de bajo stock
- Movimientos:
  - Entradas (compras)
  - Salidas (uso)
  - Ajustes
- Trazabilidad:
  - Proveedor
  - Fecha de vencimiento
  - Lote proveedor

**Tablas:**
- `insumo`
- `movimiento_insumo`

---

### 11. 👥 NÓMINA (Gestión de Empleados)

**Propósito:** Administración de personal

**Funcionalidades:**
- Registro de empleados
- Asignación de responsabilidades
- Salarios (módulo incompleto)
- Rol en operaciones

---

### 12. 📈 REPORTES (Análisis y Exportación)

**Propósito:** Generación de reportes profesionales

**Reportes Disponibles:**

| Reporte | Contenido | Formato |
|---------|-----------|---------|
| **Resumen General** | Overview del sistema | Texto |
| **Inventario Animal** | Tabla de todos los animales con detalles | Tabla |
| **Ventas** | Histórico de ventas, precios, ingresos | Tabla |
| **Tratamientos** | Tratamientos aplicados, medicinas | Tabla |
| **Potreros** | Estado de potreros, ocupación | Tabla |
| **Actividad Reciente** | Eventos últimos 30 días | Texto |
| **Empleados** | Nómina del personal | Tabla |
| **Lotes** | Estado de lotes (placeholder) | - |

**Exportación:** Excel (.xlsx), PDF (futuro)

---

### 13. ⚙️ AJUSTES (Configuración App)

**Propósito:** Personalización del sistema

**Funcionalidades:**
- Preferencias visuales
- Manual PDF descargable
- Plantillas Excel para importar
- Opción reiniciar tour
- Información de licencia

---

## 🔄 FLUJO DE DATOS

### Flujo Típico de Registro de Animal

```
┌──────────────────────┐
│  LOGIN              │  ← Usuario ingresa credenciales
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  DASHBOARD          │  ← Pantalla inicial
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  MÓDULO ANIMALES    │  
│  → Pestaña REGISTRO │  ← Usuario selecciona "Registro Animal"
└──────────┬───────────┘
           │
       ┌───┴────┐
       │        │
       ▼        ▼
    NACIMIENTO  COMPRA
       │        │
       └───┬────┘
           │
           ▼
   Captura de datos:
   • Código (ÚNICO)
   • Nombre
   • Sexo
   • Raza (FK→raza.id)
   • Finca (FK→finca.id)
   • Potrero (FK→potrero.id)
   • Fechas
   • Pesos
   • Foto
           │
           ▼
   ✓ VALIDACIÓN
   - Código único
   - Campos requeridos
   - Formato datos
           │
           ▼
   INSERT INTO animal (...) VALUES (...)
           │
           ▼
   Registro guardado en BD
           │
           ▼
   ✅ Confirmación en UI
```

### Flujo de Reporte

```
Usuario → Módulo Reportes → Selecciona tipo
  │
  └─→ Query BD (SELECT ...)
      │
      └─→ Procesa datos en memoria
          │
          └─→ Genera tabla/gráfico/texto
              │
              └─→ Muestra en interfaz
                  │
                  └─→ Opción exportar (Excel/PDF)
```

---

## 🛠️ COMPONENTES TÉCNICOS

### Utilidades Compartidas (`modules/utils/`)

| Archivo | Función |
|---------|---------|
| `login_ui.py` | Pantalla de login/registro primer usuario |
| `tour_manager.py` | Sistema de tour interactivo |
| `tour_state_manager.py` | Persistencia de estado del tour |
| `global_tour.py` | Orquestación del tour global |
| `logger.py` | Logging a archivos |
| `app_paths.py` | Rutas de configuración y datos (AppData) |
| `usuario_manager.py` | Gestión de usuarios/contraseñas |
| `license_manager.py` | Control de licencias de prueba |

### Estructura de Datos de Usuario

```
%LOCALAPPDATA%\FincaFacil\
├── logs/
│   ├── app.log
│   └── startup.log
├── database/
│   └── fincafacil.db
├── config/
│   ├── tour_state.json
│   ├── preferences.json
│   └── app_settings.json
└── exports/
    └── reportes/
```

### Sistema de Autenticación

1. **Primer Uso:**
   - No hay usuarios
   - Login solicita crear usuario/contraseña
   - Se crea licencia de prueba (6 meses)
   - Se dispara tour automático

2. **Usos Posteriores:**
   - Login valida usuario/contraseña en BD
   - Sesión guardada en AppData
   - Tour no se repite (estado persistido)

---

## 📌 RESUMEN EJECUTIVO

### Estadísticas del Proyecto

| Categoría | Cantidad |
|-----------|----------|
| **Módulos Principales** | 13 |
| **Sub-módulos** | 40+ |
| **Tablas BD** | 20+ |
| **Campos BD** | 150+ |
| **Relaciones FK** | 25+ |
| **Funciones Principales** | 100+ |
| **Líneas de Código** | ~30,000+ |

### Capacidades

✅ **Gestión Animal:** Registro completo, genealogía, fichas individuales  
✅ **Seguimiento Sanitario:** Tratamientos, diagnósticos, alertas  
✅ **Reproducción:** Servicios, partos, control gestante  
✅ **Producción Lechera:** Registro diario, análisis tendencias  
✅ **Inventario Maestro:** Fincas, potreros, razas, empleados  
✅ **Ventas:** Movimiento de animales, trazabilidad  
✅ **Reportes:** 7+ tipos, exportación Excel  
✅ **Seguridad:** Login de usuarios, licencias  
✅ **UX:** Tour automático, interfaz moderna, alertas proactivas

### Casos de Uso

1. **Ganadero lechero:** Rastrea producción diaria, mantiene calendario reproductivo
2. **Ganadero de carne:** Monitorea peso de animales, registra ventas
3. **Reproductor:** Gestiona genealogía, servicios, partos
4. **Administrador finca:** Reportes operacionales, control de inventario

### Próximas Mejoras (Roadmap)

- [ ] Integración con básculas automáticas (IoT)
- [ ] Módulo de costos y rentabilidad
- [ ] Sincronización en la nube
- [ ] App mobile (complementaria)
- [ ] Análisis predictivo (ML)
- [ ] Integración con proveedores

---

## 📞 CONCLUSIÓN

**FincaFácil** es un sistema profesional, completo y escalable para la gestión integral de fincas ganaderas. Cubre todas las áreas operacionales, desde registro animal hasta análisis financiero, con una interfaz moderna y accesible.

**Estado Actual:** Versión 2.0 en producción, con 13 módulos funcionales.

---

*Reporte generado: 11 de Diciembre de 2025*
*Versión: 2.0*
