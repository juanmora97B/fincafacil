# 📊 FASE 3 - SISTEMA DE REPORTES
## Documentación Técnica

**Versión**: 1.0  
**Fecha**: 2024  
**Autor**: Equipo FincaFácil  

---

## 📑 Índice

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Servicio Principal](#servicio-principal)
4. [Reportes Específicos](#reportes-específicos)
5. [Uso y Ejemplos](#uso-y-ejemplos)
6. [API Reference](#api-reference)

---

## 🎯 Introducción

El sistema de reportes de FASE 3 proporciona una capa de servicios **desacoplada y reutilizable** para generar reportes operacionales en FincaFácil.

### Principios de Diseño

✅ **Service Layer Pattern** - Lógica de negocio en servicios, no en UI  
✅ **Singleton Pattern** - Instancias globales reutilizables  
✅ **Separation of Concerns** - Reports generan datos, Exporters formatean  
✅ **DRY (Don't Repeat Yourself)** - Reutilización de Phase 2 services  

### Reportes Disponibles

| Tipo | Descripción | Servicio Base |
|------|-------------|---------------|
| **animales** | Inventario, movimientos, estadísticas | reporte_animales |
| **reproduccion** | Servicios, gestantes, partos, tasas | reporte_reproduccion |
| **produccion** | Litros, promedios, top productores | reporte_produccion |
| **finanzas** | Ingresos, costos, márgenes | financial_service (Phase 2) |
| **completo** | Todos los anteriores agregados | reportes_service |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        UI LAYER                              │
│  (reportes_fase3.py / reportes_main.py / API endpoints)    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER (ORCHESTRATOR)              │
│                   reportes_service.py                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  generar_reporte(tipo, fecha_inicio, fecha_fin)     │   │
│  │  obtener_resumen_rapido()                           │   │
│  │  validar_periodo()                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┼────────────┬──────────────┐
              ▼            ▼            ▼              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ reporte_animales │ │reporte_reprod... │ │reporte_produc... │
│                  │ │                  │ │                  │
│ - inventario     │ │ - servicios      │ │ - produccion     │
│ - movimientos    │ │ - gestantes      │ │ - promedios      │
│ - estadisticas   │ │ - partos         │ │ - top_animals    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
              │            │            │              │
              └────────────┴────────────┴──────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                           │
│           (get_db_connection + business_rules)              │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **UI** solicita reporte con parámetros (tipo, fechas, filtros)
2. **reportes_service** valida período y delega al generador específico
3. **Generador** consulta BD y aplica business_rules
4. **Servicio** agrega metadatos y devuelve estructura estandarizada
5. **UI/Exporter** recibe diccionario con datos estructurados

---

## 🔧 Servicio Principal

### `reportes_service.py`

**Orchestrador central** que coordina todos los reportes.

#### Importación

```python
from src.services.reportes_service import reportes_service
```

#### Métodos Principales

##### `generar_reporte()`

```python
def generar_reporte(
    tipo: str,
    fecha_inicio: date,
    fecha_fin: date,
    filtros: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Genera un reporte completo.
    
    Args:
        tipo: 'animales', 'reproduccion', 'produccion', 'finanzas', 'completo'
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha de fin del período
        filtros: Filtros opcionales (finca_id, raza_id, estado, etc.)
    
    Returns:
        {
            'tipo': str,
            'periodo': {
                'inicio': 'YYYY-MM-DD',
                'fin': 'YYYY-MM-DD',
                'dias': int
            },
            'generado_en': 'ISO8601',
            'datos': {...},  # Específico del tipo
            'totales': {...},  # Resumen numérico
            'metadatos': {
                'registros': int,
                'filtros_aplicados': {...}
            }
        }
    
    Raises:
        ValueError: Si tipo no válido o fechas incorrectas
    """
```

**Ejemplo**:

```python
from datetime import date

reporte = reportes_service.generar_reporte(
    tipo='animales',
    fecha_inicio=date(2024, 1, 1),
    fecha_fin=date(2024, 1, 31)
)

print(f"Total activos: {reporte['totales']['total_activos']}")
print(f"Gestantes: {reporte['totales']['gestantes']}")
```

##### `obtener_resumen_rapido()`

```python
def obtener_resumen_rapido(dias: int = 7) -> Dict[str, Any]:
    """
    Resumen de los últimos N días (ideal para dashboards).
    
    Args:
        dias: Número de días a incluir (default 7)
    
    Returns:
        {
            'periodo': {...},
            'animales': {
                'total_activos': int,
                'gestantes': int,
                'altas': int,
                'bajas': int
            },
            'produccion': {
                'litros_totales': float,
                'promedio_dia': float
            },
            'finanzas': {
                'ingresos': float,
                'costos': float,
                'margen': float
            }
        }
    """
```

**Ejemplo**:

```python
# Para panel de control
resumen = reportes_service.obtener_resumen_rapido(dias=7)

print(f"Últimos 7 días:")
print(f"- Activos: {resumen['animales']['total_activos']}")
print(f"- Litros: {resumen['produccion']['litros_totales']:,.1f}")
print(f"- Margen: ${resumen['finanzas']['margen']:,.2f}")
```

##### `validar_periodo()`

```python
def validar_periodo(fecha_inicio: date, fecha_fin: date) -> None:
    """
    Valida que el período sea lógico.
    
    Raises:
        ValueError: Si fechas inválidas
    """
```

---

## 📈 Reportes Específicos

### 1. Reporte de Animales

**Archivo**: `src/reports/reporte_animales.py`  
**Clase**: `ReporteAnimales`  
**Singleton**: `reporte_animales`

#### Estructura de Datos

```python
{
    'inventario_actual': {
        'por_estado': {
            'Activo': int,
            'Vendido': int,
            'Muerto': int
        },
        'por_raza': {
            'Holstein': int,
            'Jersey': int,
            ...
        },
        'gestantes': int
    },
    'movimientos': {
        'altas': [
            {
                'animal_id': int,
                'numero': str,
                'fecha': 'YYYY-MM-DD',
                'tipo': 'Compra' | 'Nacimiento',
                'valor': float
            },
            ...
        ],
        'bajas': [...]  # Estructura similar
    },
    'estadisticas': {
        'edad_promedio_meses': float,
        'peso_promedio_kg': float,
        'edad_min': float,
        'edad_max': float
    }
}
```

#### Métodos Públicos

```python
# Inventario actual
inventario = reporte_animales.obtener_inventario_actual()

# Movimientos del período
movimientos = reporte_animales.obtener_movimientos_periodo(
    fecha_inicio, fecha_fin
)

# Estadísticas generales
stats = reporte_animales.obtener_estadisticas_generales()
```

#### Ejemplo de Uso

```python
from src.reports.reporte_animales import reporte_animales
from datetime import date

# Generar reporte completo
reporte = reporte_animales.generar(
    fecha_inicio=date(2024, 1, 1),
    fecha_fin=date(2024, 1, 31)
)

# Acceder a datos
activos = reporte['inventario_actual']['por_estado']['Activo']
altas = len(reporte['movimientos']['altas'])
edad_prom = reporte['estadisticas']['edad_promedio_meses']

print(f"Activos: {activos} | Altas: {altas} | Edad: {edad_prom:.1f} meses")
```

---

### 2. Reporte de Reproducción

**Archivo**: `src/reports/reporte_reproduccion.py`  
**Clase**: `ReporteReproduccion`  
**Singleton**: `reporte_reproduccion`

#### Estructura de Datos

```python
{
    'servicios': {
        'total': int,
        'por_tipo': {
            'Monta Natural': int,
            'Inseminacion Artificial': int
        },
        'detalle': [
            {
                'servicio_id': int,
                'animal_numero': str,
                'fecha_servicio': 'YYYY-MM-DD',
                'tipo_servicio': str,
                'toro': str
            },
            ...
        ]
    },
    'gestantes': {
        'total': int,
        'detalle': [
            {
                'animal_id': int,
                'numero': str,
                'fecha_servicio': 'YYYY-MM-DD',
                'fecha_estimada_parto': 'YYYY-MM-DD',
                'dias_gestacion': int,
                'dias_restantes': int
            },
            ...
        ]
    },
    'partos': {
        'total': int,
        'detalle': [...]
    },
    'tasas': {
        'tasa_prenez': float,  # %
        'servicios_por_concepcion': float
    }
}
```

#### Métodos Clave

```python
# Servicios del período
servicios = reporte_reproduccion.obtener_servicios_periodo(
    fecha_inicio, fecha_fin
)

# Gestantes actuales con días restantes
gestantes = reporte_reproduccion.obtener_gestantes_actuales()

# Partos del período
partos = reporte_reproduccion.obtener_partos_periodo(
    fecha_inicio, fecha_fin
)

# Calcular tasa de preñez
tasas = reporte_reproduccion.calcular_tasas_reproduccion(
    fecha_inicio, fecha_fin
)
```

#### Ejemplo

```python
from src.reports.reporte_reproduccion import reporte_reproduccion

reporte = reporte_reproduccion.generar(fecha_inicio, fecha_fin)

print(f"Servicios realizados: {reporte['servicios']['total']}")
print(f"Gestantes: {reporte['gestantes']['total']}")
print(f"Tasa de preñez: {reporte['tasas']['tasa_prenez']:.1f}%")

# Gestantes próximas a parir (< 30 días)
proximas = [
    g for g in reporte['gestantes']['detalle']
    if g['dias_restantes'] < 30
]
print(f"Partos próximos: {len(proximas)}")
```

---

### 3. Reporte de Producción

**Archivo**: `src/reports/reporte_produccion.py`  
**Clase**: `ReporteProduccion`  
**Singleton**: `reporte_produccion`

#### Estructura de Datos

```python
{
    'produccion_total': {
        'litros_totales': float,
        'litros_AM': float,
        'litros_PM': float,
        'vacas_productivas': int,
        'dias_periodo': int
    },
    'promedios': {
        'litros_por_dia': float,
        'litros_por_vaca': float,
        'litros_por_vaca_dia': float
    },
    'top_productores': [
        {
            'animal_id': int,
            'numero': str,
            'nombre': str,
            'litros_totales': float,
            'litros_promedio_dia': float,
            'dias_produccion': int
        },
        ...  # Top 20
    ],
    'produccion_diaria': [
        {
            'fecha': 'YYYY-MM-DD',
            'litros_AM': float,
            'litros_PM': float,
            'litros_totales': float
        },
        ...
    ]
}
```

#### Métodos

```python
# Producción del período
produccion = reporte_produccion.obtener_produccion_periodo(
    fecha_inicio, fecha_fin
)

# Top productores
top_animals = reporte_produccion.obtener_produccion_por_animal(
    fecha_inicio, fecha_fin, limite=20
)

# Promedios
promedios = reporte_produccion.calcular_promedios(
    fecha_inicio, fecha_fin
)

# Últimos N días
ultimos = reporte_produccion.obtener_ultimos_dias(dias=7)
```

#### Ejemplo

```python
from src.reports.reporte_produccion import reporte_produccion

reporte = reporte_produccion.generar(fecha_inicio, fecha_fin)

print(f"Total: {reporte['produccion_total']['litros_totales']:,.1f} L")
print(f"Promedio/día: {reporte['promedios']['litros_por_dia']:.1f} L")
print(f"Promedio/vaca: {reporte['promedios']['litros_por_vaca']:.1f} L")

# Top 3 productoras
for i, animal in enumerate(reporte['top_productores'][:3], 1):
    print(f"{i}. {animal['numero']} - {animal['litros_totales']:.1f} L")
```

---

### 4. Reporte de Finanzas

**Archivo**: `src/reports/reporte_finanzas.py`  
**Clase**: `ReporteFinanzas`  
**Singleton**: `reporte_finanzas`

⚠️ **Nota**: Este reporte **reutiliza** `financial_service` de Phase 2.

#### Estructura de Datos

```python
{
    'ingresos': {
        'total': float,
        'por_animales': float,
        'por_leche': float,
        'otros': float,
        'detalle': [...]
    },
    'costos': {
        'total': float,
        'por_nomina': float,
        'por_tratamientos': float,
        'por_insumos': float,
        'detalle': [...]
    },
    'margen': {
        'bruto': float,
        'porcentaje': float
    },
    'kpis': {
        'precio_promedio_leche': float,  # Por litro
        'costo_por_litro': float,
        'costo_por_animal': float,
        'ingreso_por_animal': float
    }
}
```

#### Métodos

```python
# Reporte completo
reporte = reporte_finanzas.generar(fecha_inicio, fecha_fin)

# KPIs rápidos
kpis = reporte_finanzas.obtener_kpis_rapidos(fecha_inicio, fecha_fin)
```

#### Ejemplo

```python
from src.reports.reporte_finanzas import reporte_finanzas

reporte = reporte_finanzas.generar(fecha_inicio, fecha_fin)

print(f"Ingresos: ${reporte['ingresos']['total']:,.2f}")
print(f"Costos: ${reporte['costos']['total']:,.2f}")
print(f"Margen: ${reporte['margen']['bruto']:,.2f} ({reporte['margen']['porcentaje']:.1f}%)")
print(f"Precio leche: ${reporte['kpis']['precio_promedio_leche']:.2f}/L")
```

---

## 💡 Uso y Ejemplos

### Escenario 1: Dashboard General

```python
from src.services.reportes_service import reportes_service

# Resumen de últimos 7 días para panel principal
resumen = reportes_service.obtener_resumen_rapido(dias=7)

# Mostrar en UI
panel_animales.actualizar(resumen['animales'])
panel_produccion.actualizar(resumen['produccion'])
panel_finanzas.actualizar(resumen['finanzas'])
```

### Escenario 2: Reporte Mensual Completo

```python
from datetime import date
from src.services.reportes_service import reportes_service
from src.utils.export.export_pdf import pdf_exporter

# Generar reporte completo del mes
reporte = reportes_service.generar_reporte(
    tipo='completo',
    fecha_inicio=date(2024, 1, 1),
    fecha_fin=date(2024, 1, 31)
)

# Exportar a PDF
pdf_exporter.exportar(reporte, 'reporte_enero_2024.pdf')
```

### Escenario 3: Análisis de Producción

```python
from src.reports.reporte_produccion import reporte_produccion

# Producción del mes
reporte = reporte_produccion.generar(fecha_inicio, fecha_fin)

# Identificar vacas de baja producción
bajo_promedio = [
    animal for animal in reporte['top_productores']
    if animal['litros_promedio_dia'] < reporte['promedios']['litros_por_vaca_dia']
]

# Enviar alerta
alertar_animales_baja_produccion(bajo_promedio)
```

### Escenario 4: API REST Endpoint

```python
from fastapi import APIRouter, HTTPException
from src.services.reportes_service import reportes_service

router = APIRouter()

@router.get("/api/reportes/{tipo}")
def obtener_reporte(
    tipo: str,
    fecha_inicio: str,
    fecha_fin: str
):
    try:
        reporte = reportes_service.generar_reporte(
            tipo=tipo,
            fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d").date(),
            fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        )
        return reporte
    except ValueError as e:
        raise HTTPException(400, str(e))
```

---

## 📚 API Reference

### Tipos de Datos

```python
# Período
Periodo = TypedDict('Periodo', {
    'inicio': str,  # 'YYYY-MM-DD'
    'fin': str,
    'dias': int
})

# Filtros
Filtros = TypedDict('Filtros', {
    'finca_id': Optional[int],
    'raza_id': Optional[int],
    'estado': Optional[str],  # 'Activo', 'Vendido', 'Muerto'
    'sexo': Optional[str],  # 'Macho', 'Hembra'
}, total=False)

# Reporte Base
ReporteBase = TypedDict('ReporteBase', {
    'tipo': str,
    'periodo': Periodo,
    'generado_en': str,  # ISO8601
    'datos': Dict[str, Any],
    'totales': Dict[str, Any],
    'metadatos': Dict[str, Any]
})
```

### Constantes

```python
# Tipos de reporte válidos
TIPOS_REPORTE = [
    'animales',
    'reproduccion',
    'produccion',
    'finanzas',
    'completo'
]

# Estados de animales
ESTADOS_ANIMAL = ['Activo', 'Vendido', 'Muerto']

# Tipos de servicio
TIPOS_SERVICIO = ['Monta Natural', 'Inseminacion Artificial']

# Jornadas de ordeño
JORNADAS = ['AM', 'PM']
```

---

## ⚙️ Configuración y Logging

### Logging

Todos los servicios usan el módulo `logging` de Python:

```python
import logging

# El servicio registra operaciones
logger = logging.getLogger('reportes_service')
logger.info(f"Generando reporte {tipo} para {periodo}")
```

Para activar logs en tu aplicación:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Conexión a Base de Datos

Los servicios usan `get_db_connection()` del proyecto:

```python
from database.db_manager import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    # ...
```

---

## 🧪 Testing

### Unit Tests (Ejemplo)

```python
import unittest
from datetime import date
from src.services.reportes_service import reportes_service

class TestReportesService(unittest.TestCase):
    
    def test_generar_reporte_animales(self):
        reporte = reportes_service.generar_reporte(
            'animales',
            date(2024, 1, 1),
            date(2024, 1, 31)
        )
        
        self.assertEqual(reporte['tipo'], 'animales')
        self.assertIn('inventario_actual', reporte['datos'])
        self.assertIn('total_activos', reporte['totales'])
    
    def test_validar_periodo_invalido(self):
        with self.assertRaises(ValueError):
            reportes_service.validar_periodo(
                date(2024, 1, 31),
                date(2024, 1, 1)  # Fin antes de inicio
            )
```

---

## 📦 Dependencias

```
# requirements.txt
# (Sin dependencias externas para reportes básicos)
```

Los reportes **NO requieren** dependencias externas. Toda la lógica usa:
- SQLite (incluido en Python)
- datetime, logging, typing (stdlib)

---

## 🔗 Ver También

- [FASE3_EXPORTACION.md](./FASE3_EXPORTACION.md) - Sistema de exportación
- [FASE3_CIERRE_MENSUAL.md](./FASE3_CIERRE_MENSUAL.md) - Cierre contable
- [FASE3_RESUMEN_EJECUTIVO.md](./FASE3_RESUMEN_EJECUTIVO.md) - Resumen ejecutivo

---

**Documentación generada para FASE 3 - FincaFácil**  
*Sistema de Reportes Operacionales*
