# 📅 FASE 3 - CIERRE MENSUAL
## Documentación Técnica

**Versión**: 1.0  
**Fecha**: 2024  
**Autor**: Equipo FincaFácil  

---

## 📑 Índice

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Base de Datos](#base-de-datos)
4. [Servicio de Cierre](#servicio-de-cierre)
5. [Uso y Ejemplos](#uso-y-ejemplos)
6. [Workflows](#workflows)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

El sistema de **Cierre Mensual** permite consolidar todos los indicadores operacionales y financieros del mes en un snapshot permanente para análisis histórico y auditoría.

### ¿Qué es un Cierre Mensual?

Un **cierre mensual** es:

- 📸 **Snapshot** de todos los indicadores del mes
- 🔒 **Inmutable** una vez realizado (solo se crea, no se edita)
- 📊 **Comparable** con otros meses para análisis de tendencias
- 📜 **Auditable** con registro de usuario y fecha

### Objetivos

✅ **Consolidación**: Todos los KPIs en una sola tabla  
✅ **Histórico**: Base de datos permanente de cierres  
✅ **Comparación**: Análisis mes a mes, año a año  
✅ **Auditoría**: Trazabilidad de cambios operacionales  
✅ **Reporteo**: Datos listos para gráficos de tendencia  

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                    UI / TRIGGER                              │
│   (Botón "Realizar Cierre Mensual" o Job automático)       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              CIERRE_MENSUAL_SERVICE                          │
│                                                              │
│  1. Validar período (año, mes)                              │
│  2. Verificar si existe cierre previo                       │
│  3. Generar reporte completo (llamar reportes_service)      │
│  4. Extraer métricas clave                                  │
│  5. Insertar en tabla resumen_mensual                       │
│  6. Retornar resumen del cierre                             │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              REPORTES_SERVICE.generar_reporte()              │
│  (Genera reporte 'completo' con todos los datos del mes)   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│            TABLA: resumen_mensual (SQLite)                   │
│                                                              │
│  Columnas (25):                                             │
│  - año, mes, fecha_cierre                                   │
│  - total_activos, gestantes, altas_mes, bajas_mes           │
│  - litros_totales, litros_promedio_dia, vacas_productivas   │
│  - servicios_realizados, partos_mes, tasa_prenez            │
│  - ingresos_totales, costos_totales, margen_bruto           │
│  - observaciones, usuario                                   │
└──────────────────────────────────────────────────────────────┘
```

### Flujo del Proceso

1. **Usuario** solicita cierre del mes (ej: Enero 2024)
2. **Servicio** valida que no exista cierre previo
3. **Servicio** genera reporte completo de todo el mes
4. **Servicio** extrae 25 métricas clave
5. **Servicio** inserta registro en `resumen_mensual`
6. **Usuario** recibe confirmación con resumen

---

## 💾 Base de Datos

### Tabla: `resumen_mensual`

```sql
CREATE TABLE IF NOT EXISTS resumen_mensual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificación
    año INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    fecha_cierre TIMESTAMP NOT NULL,
    
    -- Animales
    total_activos INTEGER,
    gestantes INTEGER,
    altas_mes INTEGER,
    bajas_mes INTEGER,
    
    -- Producción
    litros_totales REAL,
    litros_promedio_dia REAL,
    litros_promedio_vaca REAL,
    vacas_productivas INTEGER,
    
    -- Reproducción
    servicios_realizados INTEGER,
    partos_mes INTEGER,
    tasa_prenez REAL,
    
    -- Finanzas
    ingresos_totales REAL,
    ingresos_animales REAL,
    ingresos_leche REAL,
    costos_totales REAL,
    costos_nomina REAL,
    costos_tratamientos REAL,
    costos_insumos REAL,
    margen_bruto REAL,
    margen_porcentaje REAL,
    
    -- Auditoría
    observaciones TEXT,
    usuario TEXT,
    
    -- Constraint
    UNIQUE(año, mes)
);
```

### Columnas Detalladas

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| **año** | INT | Año del cierre | 2024 |
| **mes** | INT | Mes del cierre (1-12) | 1 (Enero) |
| **fecha_cierre** | TIMESTAMP | Cuándo se realizó el cierre | 2024-02-01 08:30:00 |
| **total_activos** | INT | Animales activos al final del mes | 150 |
| **gestantes** | INT | Vacas gestantes al final del mes | 45 |
| **altas_mes** | INT | Compras + nacimientos en el mes | 12 |
| **bajas_mes** | INT | Ventas + muertes en el mes | 5 |
| **litros_totales** | REAL | Litros producidos en el mes | 15250.5 |
| **litros_promedio_dia** | REAL | Promedio diario del mes | 492.3 |
| **litros_promedio_vaca** | REAL | Litros por vaca por día | 12.5 |
| **vacas_productivas** | INT | Vacas que produjeron en el mes | 40 |
| **servicios_realizados** | INT | Servicios (monta/IA) del mes | 15 |
| **partos_mes** | INT | Partos ocurridos en el mes | 8 |
| **tasa_prenez** | REAL | % de preñez del mes | 75.5 |
| **ingresos_totales** | REAL | Total ingresos del mes | 8500000 |
| **ingresos_animales** | REAL | Ingresos por venta de animales | 5000000 |
| **ingresos_leche** | REAL | Ingresos por venta de leche | 3500000 |
| **costos_totales** | REAL | Total costos del mes | 6000000 |
| **costos_nomina** | REAL | Costos de nómina | 2000000 |
| **costos_tratamientos** | REAL | Costos de tratamientos veterinarios | 500000 |
| **costos_insumos** | REAL | Costos de insumos (alimento, etc.) | 3500000 |
| **margen_bruto** | REAL | Ingresos - Costos | 2500000 |
| **margen_porcentaje** | REAL | (Margen / Ingresos) * 100 | 29.4 |
| **observaciones** | TEXT | Notas del cierre | "Mes con alta producción" |
| **usuario** | TEXT | Quién realizó el cierre | "admin" |

### Índices (Recomendados)

```sql
-- Para búsquedas por año
CREATE INDEX idx_resumen_año ON resumen_mensual(año);

-- Para búsquedas por período
CREATE INDEX idx_resumen_año_mes ON resumen_mensual(año, mes);
```

---

## 🔧 Servicio de Cierre

**Archivo**: `src/services/cierre_mensual_service.py`  
**Clase**: `CierreMensualService`  
**Singleton**: `cierre_mensual_service`

### Importación

```python
from src.services.cierre_mensual_service import cierre_mensual_service
```

### Métodos Principales

#### 1. `realizar_cierre()`

```python
def realizar_cierre(
    año: int,
    mes: int,
    usuario: str = "Sistema",
    observaciones: Optional[str] = None
) -> Dict[str, Any]:
    """
    Realiza el cierre mensual.
    
    Args:
        año: Año del cierre (ej: 2024)
        mes: Mes del cierre (1-12)
        usuario: Nombre del usuario que realiza el cierre
        observaciones: Notas opcionales sobre el cierre
    
    Returns:
        {
            'año': int,
            'mes': int,
            'fecha_cierre': str,
            'total_activos': int,
            'margen_bruto': float,
            'margen_porcentaje': float,
            ...  # Todas las 25 métricas
        }
    
    Raises:
        ValueError: Si ya existe cierre para ese mes
        ValueError: Si fecha futura
        RuntimeError: Si error en BD
    """
```

**Ejemplo**:

```python
from src.services.cierre_mensual_service import cierre_mensual_service

# Realizar cierre de Enero 2024
resumen = cierre_mensual_service.realizar_cierre(
    año=2024,
    mes=1,
    usuario="Juan Pérez",
    observaciones="Mes con alta producción de leche"
)

print(f"Cierre completado:")
print(f"- Activos: {resumen['total_activos']}")
print(f"- Margen: ${resumen['margen_bruto']:,.0f}")
print(f"- Litros: {resumen['litros_totales']:,.1f}")
```

#### 2. `existe_cierre()`

```python
def existe_cierre(año: int, mes: int) -> bool:
    """
    Verifica si ya existe cierre para el mes.
    
    Args:
        año: Año a verificar
        mes: Mes a verificar
    
    Returns:
        True si existe cierre, False si no
    """
```

**Ejemplo**:

```python
if cierre_mensual_service.existe_cierre(2024, 1):
    print("Ya existe cierre de Enero 2024")
else:
    print("Puede realizar cierre de Enero 2024")
```

#### 3. `obtener_cierre()`

```python
def obtener_cierre(año: int, mes: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene el cierre de un mes específico.
    
    Args:
        año: Año del cierre
        mes: Mes del cierre
    
    Returns:
        Dict con todas las métricas, o None si no existe
    """
```

**Ejemplo**:

```python
cierre = cierre_mensual_service.obtener_cierre(2024, 1)

if cierre:
    print(f"Cierre de {cierre['año']}-{cierre['mes']:02d}")
    print(f"Realizado: {cierre['fecha_cierre']}")
    print(f"Por: {cierre['usuario']}")
    print(f"Observaciones: {cierre['observaciones']}")
else:
    print("No existe cierre para ese mes")
```

#### 4. `comparar_meses()`

```python
def comparar_meses(
    año1: int,
    mes1: int,
    año2: int,
    mes2: int
) -> Dict[str, Any]:
    """
    Compara dos meses y calcula variaciones.
    
    Args:
        año1, mes1: Primera fecha
        año2, mes2: Segunda fecha
    
    Returns:
        {
            'periodo1': {...},  # Datos del primer mes
            'periodo2': {...},  # Datos del segundo mes
            'variaciones': {
                'total_activos': {
                    'valor1': int,
                    'valor2': int,
                    'diferencia': int,
                    'porcentaje': float
                },
                ...  # Para cada métrica numérica
            }
        }
    
    Raises:
        ValueError: Si no existen cierres para ambas fechas
    """
```

**Ejemplo**:

```python
# Comparar Enero vs Febrero
comparacion = cierre_mensual_service.comparar_meses(2024, 1, 2024, 2)

print("Variaciones Enero → Febrero:")
for metrica, datos in comparacion['variaciones'].items():
    print(f"{metrica}: {datos['diferencia']:+} ({datos['porcentaje']:+.1f}%)")

# Output:
# total_activos: +5 (+3.3%)
# litros_totales: -200.5 (-1.3%)
# margen_bruto: +150000 (+6.0%)
```

#### 5. `listar_cierres()`

```python
def listar_cierres(año: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Lista todos los cierres.
    
    Args:
        año: Si se especifica, filtra por año. Si None, todos.
    
    Returns:
        Lista de dicts con todos los cierres, ordenados por fecha
    """
```

**Ejemplo**:

```python
# Todos los cierres de 2024
cierres_2024 = cierre_mensual_service.listar_cierres(año=2024)

print(f"Total cierres de 2024: {len(cierres_2024)}")
for c in cierres_2024:
    print(f"{c['año']}-{c['mes']:02d}: Margen ${c['margen_bruto']:,.0f}")
```

---

## 💡 Uso y Ejemplos

### Escenario 1: Cierre Manual al Final del Mes

```python
from src.services.cierre_mensual_service import cierre_mensual_service
from datetime import date

# Al finalizar Enero
hoy = date.today()
año = hoy.year
mes = hoy.month - 1 if hoy.month > 1 else 12

# Verificar si ya existe
if cierre_mensual_service.existe_cierre(año, mes):
    print(f"Ya existe cierre de {año}-{mes:02d}")
else:
    # Realizar cierre
    observaciones = input("Observaciones del mes (opcional): ")
    
    resumen = cierre_mensual_service.realizar_cierre(
        año=año,
        mes=mes,
        usuario="Administrador",
        observaciones=observaciones or None
    )
    
    print(f"\n✓ Cierre de {año}-{mes:02d} completado")
    print(f"  - Activos: {resumen['total_activos']}")
    print(f"  - Margen: ${resumen['margen_bruto']:,.0f}")
```

### Escenario 2: Cierre Automático (Job Mensual)

```python
import schedule
from src.services.cierre_mensual_service import cierre_mensual_service
from datetime import date

def job_cierre_mensual():
    """Ejecutar el primer día de cada mes a las 8 AM"""
    
    hoy = date.today()
    
    # Calcular mes anterior
    if hoy.month == 1:
        año_anterior = hoy.year - 1
        mes_anterior = 12
    else:
        año_anterior = hoy.year
        mes_anterior = hoy.month - 1
    
    # Realizar cierre
    try:
        if not cierre_mensual_service.existe_cierre(año_anterior, mes_anterior):
            resumen = cierre_mensual_service.realizar_cierre(
                año=año_anterior,
                mes=mes_anterior,
                usuario="Sistema Automático",
                observaciones="Cierre automático programado"
            )
            
            logging.info(f"Cierre automático completado: {año_anterior}-{mes_anterior:02d}")
            
            # Enviar notificación
            enviar_email_cierre(resumen)
    
    except Exception as e:
        logging.error(f"Error en cierre automático: {e}")

# Programar para el día 1 a las 8:00 AM
schedule.every().day.at("08:00").do(
    lambda: job_cierre_mensual() if date.today().day == 1 else None
)
```

### Escenario 3: Dashboard de Tendencias

```python
from src.services.cierre_mensual_service import cierre_mensual_service
import matplotlib.pyplot as plt

# Obtener cierres del año
cierres = cierre_mensual_service.listar_cierres(año=2024)

# Extraer datos para gráfico
meses = [c['mes'] for c in cierres]
ingresos = [c['ingresos_totales'] for c in cierres]
costos = [c['costos_totales'] for c in cierres]
margen = [c['margen_bruto'] for c in cierres]

# Graficar
plt.figure(figsize=(12, 6))
plt.plot(meses, ingresos, label='Ingresos', marker='o')
plt.plot(meses, costos, label='Costos', marker='o')
plt.plot(meses, margen, label='Margen', marker='o')
plt.xlabel('Mes')
plt.ylabel('Monto ($)')
plt.title('Tendencia Financiera 2024')
plt.legend()
plt.grid(True)
plt.savefig('tendencia_2024.png')
```

### Escenario 4: Comparación Año a Año

```python
from src.services.cierre_mensual_service import cierre_mensual_service

# Comparar Enero 2023 vs Enero 2024
comparacion = cierre_mensual_service.comparar_meses(2023, 1, 2024, 1)

print("COMPARACIÓN ENE-2023 vs ENE-2024")
print("=" * 50)

for metrica, datos in comparacion['variaciones'].items():
    if abs(datos['porcentaje']) > 5:  # Solo variaciones > 5%
        emoji = "📈" if datos['porcentaje'] > 0 else "📉"
        print(f"{emoji} {metrica}: {datos['porcentaje']:+.1f}%")
```

### Escenario 5: Auditoría de Cierres

```python
from src.services.cierre_mensual_service import cierre_mensual_service

# Obtener todos los cierres
todos_cierres = cierre_mensual_service.listar_cierres()

print("AUDITORÍA DE CIERRES")
print("=" * 70)
print(f"{'Período':<15} {'Fecha Cierre':<20} {'Usuario':<15} {'Margen':<15}")
print("-" * 70)

for c in todos_cierres:
    periodo = f"{c['año']}-{c['mes']:02d}"
    fecha = c['fecha_cierre'][:16]  # Solo fecha sin segundos
    usuario = c['usuario'] or "N/A"
    margen = f"${c['margen_bruto']:,.0f}"
    
    print(f"{periodo:<15} {fecha:<20} {usuario:<15} {margen:<15}")
```

---

## 🔄 Workflows

### Workflow 1: Cierre End-of-Month (Manual)

```
1. Usuario: Abre módulo de reportes
   ↓
2. Usuario: Click en "Cierre Mensual"
   ↓
3. Sistema: Abre diálogo con año/mes precargados (mes anterior)
   ↓
4. Usuario: Confirma o modifica año/mes
   ↓
5. Usuario: Agrega observaciones (opcional)
   ↓
6. Usuario: Click "Realizar Cierre"
   ↓
7. Sistema: Valida que no exista cierre previo
   ↓
8. Sistema: Genera reporte completo del mes
   ↓
9. Sistema: Extrae 25 métricas clave
   ↓
10. Sistema: Inserta registro en resumen_mensual
    ↓
11. Sistema: Muestra confirmación con resumen
    ↓
12. Usuario: Cierra diálogo
```

### Workflow 2: Cierre Automático (Job)

```
1. Cron: Dispara job el día 1 a las 8 AM
   ↓
2. Job: Calcula mes anterior
   ↓
3. Job: Verifica si existe cierre
   ↓
4. Job: Si NO existe → Ejecuta cierre_mensual_service.realizar_cierre()
   ↓
5. Job: Log resultado (éxito o error)
   ↓
6. Job: Envía email de notificación
   ↓
7. Job: Finaliza
```

### Workflow 3: Análisis de Tendencias

```
1. Usuario: Accede a dashboard de analytics
   ↓
2. Sistema: Carga cierres del año actual
   ↓
3. Sistema: Genera gráficos de tendencias
   ↓
4. Usuario: Selecciona 2 meses para comparar
   ↓
5. Sistema: Llama comparar_meses()
   ↓
6. Sistema: Muestra tabla de variaciones
   ↓
7. Usuario: Exporta comparación a PDF
```

---

## 🔧 Troubleshooting

### Error: "Ya existe un cierre para ese mes"

**Problema**: Intentas crear cierre duplicado.

**Solución**: Verificar antes con `existe_cierre()`:

```python
if not cierre_mensual_service.existe_cierre(año, mes):
    cierre_mensual_service.realizar_cierre(año, mes, usuario)
else:
    print("Cierre ya realizado. Use obtener_cierre() para consultarlo.")
```

### Error: "No se puede realizar cierre de fecha futura"

**Problema**: Intentas cerrar un mes que aún no termina.

**Solución**: Solo cerrar meses pasados:

```python
from datetime import date

hoy = date.today()
if año > hoy.year or (año == hoy.year and mes >= hoy.month):
    raise ValueError("No puede cerrar un mes futuro o en curso")
```

### Cierre con métricas en 0

**Problema**: El cierre se guarda pero todas las métricas están en 0.

**Solución**: Verificar que el mes tenga datos:

```python
from src.services.reportes_service import reportes_service
from datetime import date

# Generar reporte antes de cerrar
reporte = reportes_service.generar_reporte(
    'completo',
    date(año, mes, 1),
    date(año, mes, calendar.monthrange(año, mes)[1])
)

if reporte['totales'].get('total_activos', 0) == 0:
    print("Advertencia: No hay datos para este mes")
```

### Comparación arroja error "Cierre no encontrado"

**Problema**: Intentas comparar meses sin cierre.

**Solución**: Verificar existencia antes:

```python
if not (cierre_mensual_service.existe_cierre(año1, mes1) and
        cierre_mensual_service.existe_cierre(año2, mes2)):
    print("Ambos meses deben tener cierre para comparar")
else:
    comp = cierre_mensual_service.comparar_meses(año1, mes1, año2, mes2)
```

---

## 📊 Reportes con Cierres

### Generar Informe Anual

```python
from src.services.cierre_mensual_service import cierre_mensual_service
from src.utils.export.export_pdf import pdf_exporter

# Obtener cierres del año
cierres = cierre_mensual_service.listar_cierres(año=2024)

# Crear estructura para exportar
reporte_anual = {
    'tipo': 'resumen_anual',
    'periodo': {'inicio': '2024-01-01', 'fin': '2024-12-31'},
    'generado_en': datetime.now().isoformat(),
    'datos': {
        'cierres_mensuales': cierres
    },
    'totales': {
        'ingresos_anuales': sum(c['ingresos_totales'] for c in cierres),
        'costos_anuales': sum(c['costos_totales'] for c in cierres),
        'margen_anual': sum(c['margen_bruto'] for c in cierres)
    }
}

# Exportar
pdf_exporter.exportar(reporte_anual, 'informe_anual_2024.pdf')
```

---

## 🔗 Ver También

- [FASE3_REPORTES.md](./FASE3_REPORTES.md) - Sistema de reportes
- [FASE3_EXPORTACION.md](./FASE3_EXPORTACION.md) - Exportación de datos
- [FASE3_RESUMEN_EJECUTIVO.md](./FASE3_RESUMEN_EJECUTIVO.md) - Resumen ejecutivo

---

**Documentación generada para FASE 3 - FincaFácil**  
*Sistema de Cierre Mensual Contable*
