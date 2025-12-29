# 📤 FASE 3 - SISTEMA DE EXPORTACIÓN
## Documentación Técnica

**Versión**: 1.0  
**Fecha**: 2024  
**Autor**: Equipo FincaFácil  

---

## 📑 Índice

1. [Introducción](#introducción)
2. [Formatos Disponibles](#formatos-disponibles)
3. [CSV Exporter](#csv-exporter)
4. [Excel Exporter](#excel-exporter)
5. [PDF Exporter](#pdf-exporter)
6. [Uso y Ejemplos](#uso-y-ejemplos)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

El sistema de exportación de FASE 3 convierte los reportes generados en archivos profesionales listos para distribución.

### Características

✅ **3 Formatos**: CSV (respaldo), Excel (contador), PDF (gerencia)  
✅ **Formateo Profesional**: Tablas, colores, estilos  
✅ **Dependencias Opcionales**: Funciona sin librerías externas (CSV nativo)  
✅ **Singleton Pattern**: Instancias reutilizables  
✅ **Error Handling**: Validación de rutas, creación de directorios  

### Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                    REPORTES SERVICE                          │
│         (genera estructura de datos estándar)               │
└────────────────────────┬─────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Reporte Dict     │  │   Filtros        │
    │ {tipo, periodo,  │  │   {ruta, opciones}│
    │  datos, totales} │  │                  │
    └────────┬─────────┘  └────────┬─────────┘
             │                     │
             └──────────┬──────────┘
                        ▼
        ┌───────────────────────────────────┐
        │      EXPORTER SELECTOR            │
        │  (csv/excel/pdf según formato)   │
        └───────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ CSV Exporter   │ │ Excel Exporter │ │  PDF Exporter  │
│                │ │                │ │                │
│ ✅ Sin deps    │ │ ⚙️ openpyxl    │ │ ⚙️ reportlab   │
│ ✅ UTF-8       │ │ ✅ Styled      │ │ ✅ Platypus    │
│ ✅ Tabular     │ │ ✅ Formulas    │ │ ✅ Colors      │
└────────────────┘ └────────────────┘ └────────────────┘
         │              │              │
         └──────────────┴──────────────┘
                        ▼
            ┌─────────────────────┐
            │   ARCHIVO FINAL     │
            │  (listo para usar)  │
            └─────────────────────┘
```

---

## 📄 Formatos Disponibles

### Comparativa

| Formato | Dependencias | Tamaño | Caso de Uso | Ventajas |
|---------|--------------|--------|-------------|----------|
| **CSV** | Ninguna | Pequeño | Respaldo, importación | Universal, rápido |
| **Excel** | openpyxl | Mediano | Contabilidad, análisis | Fórmulas, estilos |
| **PDF** | reportlab | Grande | Presentación, impresión | Profesional, inmutable |

### Cuándo Usar Cada Uno

```
CSV    ➜  Backup diario, carga a otros sistemas, análisis con R/Python
Excel  ➜  Análisis financiero, planillas contador, dashboards
PDF    ➜  Presentaciones gerenciales, reportes auditables, impresión
```

---

## 📊 CSV Exporter

**Archivo**: `src/utils/export/export_csv.py`  
**Clase**: `CSVExporter`  
**Singleton**: `csv_exporter`

### Características

- ✅ **Sin dependencias externas** (usa módulo `csv` de stdlib)
- ✅ Encoding UTF-8 con BOM (compatible con Excel)
- ✅ Separador configurable (default: `;`)
- ✅ Formato tabular con encabezados
- ✅ Reportes completos en múltiples archivos

### Estructura de Archivo

```csv
REPORTE: ANIMALES
Período: 2024-01-01 → 2024-01-31
Generado: 2024-01-31T15:30:00

=== INVENTARIO ACTUAL ===
Estado;Cantidad
Activo;150
Vendido;20
Muerto;3

=== MOVIMIENTOS DEL PERÍODO ===
Fecha;Número;Tipo;Valor
2024-01-05;A-001;Compra;1200000
2024-01-12;A-002;Nacimiento;0
...

=== TOTALES ===
Total Activos;150
Gestantes;45
Altas;12
Bajas;5
```

### Importación

```python
from src.utils.export.export_csv import csv_exporter
```

### Método Principal

```python
def exportar(reporte: Dict[str, Any], ruta_salida: str) -> None:
    """
    Exporta reporte a CSV.
    
    Args:
        reporte: Dict generado por reportes_service
        ruta_salida: Ruta del archivo (ej: 'reportes/enero.csv')
    
    Raises:
        ValueError: Si reporte inválido o ruta no accesible
        IOError: Si error escribiendo archivo
    """
```

### Ejemplos

#### Exportar Reporte Simple

```python
from datetime import date
from src.services.reportes_service import reportes_service
from src.utils.export.export_csv import csv_exporter

# Generar reporte
reporte = reportes_service.generar_reporte(
    'animales',
    date(2024, 1, 1),
    date(2024, 1, 31)
)

# Exportar a CSV
csv_exporter.exportar(reporte, 'reportes/animales_enero.csv')
```

#### Exportar Reporte Completo

```python
# Reporte completo genera 4 archivos
reporte = reportes_service.generar_reporte('completo', inicio, fin)
csv_exporter.exportar(reporte, 'reportes/completo.csv')

# Resultado:
# - reportes/completo_animales.csv
# - reportes/completo_reproduccion.csv
# - reportes/completo_produccion.csv
# - reportes/completo_finanzas.csv
```

#### Configurar Separador

```python
# Por defecto usa ';' (punto y coma)
# Para cambiar, modificar CSV_SEPARATOR en el código
```

### Formato por Tipo de Reporte

#### Animales

```csv
=== INVENTARIO ===
Estado;Cantidad
Activo;150

=== MOVIMIENTOS ===
Fecha;Número;Tipo;Valor

=== ESTADÍSTICAS ===
Métrica;Valor
Edad Promedio;24.5
```

#### Reproducción

```csv
=== SERVICIOS ===
Fecha;Animal;Tipo;Toro

=== GESTANTES ===
Animal;Días Gestación;Fecha Parto

=== TASAS ===
Tasa de Preñez;75.5%
```

#### Producción

```csv
=== PRODUCCIÓN TOTAL ===
Litros Totales;15250.5
Promedio Día;492.3

=== TOP PRODUCTORES ===
Número;Nombre;Litros
A-001;Bella;450.2
```

#### Finanzas

```csv
=== INGRESOS ===
Concepto;Monto
Venta Animales;5000000
Venta Leche;3500000

=== COSTOS ===
Concepto;Monto
Nómina;2000000

=== RESUMEN ===
Margen Bruto;6500000
```

---

## 📊 Excel Exporter

**Archivo**: `src/utils/export/export_excel.py`  
**Clase**: `ExcelExporter`  
**Singleton**: `excel_exporter`

### Características

- ⚙️ **Requiere**: `openpyxl` (instalación opcional)
- ✅ Formato profesional con estilos
- ✅ Headers en negrita (tamaño 14)
- ✅ Filas de título con color (#1a237e)
- ✅ Formato de moneda ($#,##0)
- ✅ Autoajuste de columnas
- ✅ Múltiples hojas para reporte completo

### Instalación de Dependencias

```bash
pip install openpyxl
```

O agregar a `requirements.txt`:

```
openpyxl>=3.1.0
```

### Importación

```python
from src.utils.export.export_excel import excel_exporter
```

### Verificación de Dependencias

```python
# El exporter verifica automáticamente
if not excel_exporter.openpyxl_disponible:
    print("Instalar: pip install openpyxl")
    # Usa CSV como fallback
```

### Método Principal

```python
def exportar(reporte: Dict[str, Any], ruta_salida: str) -> None:
    """
    Exporta reporte a Excel (.xlsx).
    
    Args:
        reporte: Dict generado por reportes_service
        ruta_salida: Ruta del archivo (debe terminar en .xlsx)
    
    Raises:
        RuntimeError: Si openpyxl no instalado
        ValueError: Si reporte inválido
        IOError: Si error escribiendo archivo
    """
```

### Ejemplos

#### Exportar con Estilos

```python
from src.services.reportes_service import reportes_service
from src.utils.export.export_excel import excel_exporter

reporte = reportes_service.generar_reporte('finanzas', inicio, fin)
excel_exporter.exportar(reporte, 'finanzas_enero.xlsx')

# Abre el archivo automáticamente
import os
os.startfile('finanzas_enero.xlsx')
```

#### Reporte Completo Multisheet

```python
reporte = reportes_service.generar_reporte('completo', inicio, fin)
excel_exporter.exportar(reporte, 'reporte_completo.xlsx')

# Genera archivo con 4 hojas:
# 1. Animales
# 2. Reproducción
# 3. Producción
# 4. Finanzas
```

#### Manejo de Errores

```python
try:
    excel_exporter.exportar(reporte, ruta)
except RuntimeError as e:
    # openpyxl no instalado
    print(f"Excel no disponible: {e}")
    # Usar CSV como fallback
    csv_exporter.exportar(reporte, ruta.replace('.xlsx', '.csv'))
```

### Estilos Aplicados

```python
# Header Style (títulos de sección)
font = Font(size=14, bold=True, color='FFFFFF')
fill = PatternFill(start_color='1a237e', fill_type='solid')
alignment = Alignment(horizontal='center', vertical='center')

# Data Style (celdas numéricas)
number_format = '#,##0.00'  # Miles con 2 decimales

# Currency Style (moneda)
number_format = '$#,##0.00'
```

### Estructura de Hojas

#### Hoja "Animales"

| A | B |
|---|---|
| **INVENTARIO ACTUAL** | |
| Estado | Cantidad |
| Activo | 150 |
| ... | ... |
| | |
| **MOVIMIENTOS** | |
| Fecha | Número | Tipo | Valor |

#### Hoja "Finanzas"

| A | B | C |
|---|---|---|
| **INGRESOS** | | |
| Concepto | Monto | % |
| Venta Animales | $5,000,000 | 58.8% |
| Venta Leche | $3,500,000 | 41.2% |
| **TOTAL** | **$8,500,000** | **100%** |

---

## 📄 PDF Exporter

**Archivo**: `src/utils/export/export_pdf.py`  
**Clase**: `PDFExporter`  
**Singleton**: `pdf_exporter`

### Características

- ⚙️ **Requiere**: `reportlab` (instalación opcional)
- ✅ Formato profesional tipo informe
- ✅ Platypus framework (layout automático)
- ✅ Tablas con bordes y colores
- ✅ Estilos personalizados
- ✅ Paginación automática
- ✅ Headers y footers

### Instalación de Dependencias

```bash
pip install reportlab
```

O en `requirements.txt`:

```
reportlab>=4.0.0
```

### Importación

```python
from src.utils.export.export_pdf import pdf_exporter
```

### Verificación

```python
if not pdf_exporter.reportlab_disponible:
    raise RuntimeError("Instalar: pip install reportlab")
```

### Método Principal

```python
def exportar(reporte: Dict[str, Any], ruta_salida: str) -> None:
    """
    Exporta reporte a PDF.
    
    Args:
        reporte: Dict generado por reportes_service
        ruta_salida: Ruta del archivo (debe terminar en .pdf)
    
    Raises:
        RuntimeError: Si reportlab no instalado
        ValueError: Si reporte inválido
        IOError: Si error escribiendo archivo
    """
```

### Ejemplos

#### PDF Simple

```python
from src.services.reportes_service import reportes_service
from src.utils.export.export_pdf import pdf_exporter

reporte = reportes_service.generar_reporte('produccion', inicio, fin)
pdf_exporter.exportar(reporte, 'produccion_enero.pdf')
```

#### PDF con Logo (Personalización)

```python
# Modificar en export_pdf.py:
def _crear_header(self):
    logo = Image('assets/logo.png', width=100, height=50)
    # ...
```

#### Generar Múltiples PDFs

```python
from datetime import date
import calendar

# Reportes mensuales del año
for mes in range(1, 13):
    inicio = date(2024, mes, 1)
    fin = date(2024, mes, calendar.monthrange(2024, mes)[1])
    
    reporte = reportes_service.generar_reporte('completo', inicio, fin)
    pdf_exporter.exportar(reporte, f'reportes/2024_{mes:02d}.pdf')
```

### Estilos de PDF

```python
# Título principal
estiloTitulo = ParagraphStyle(
    'Titulo',
    fontSize=18,
    textColor=colors.HexColor('#1a237e'),
    alignment=TA_CENTER,
    spaceAfter=20
)

# Encabezado de sección
estiloHeading = ParagraphStyle(
    'Heading',
    fontSize=14,
    textColor=colors.HexColor('#283593'),
    spaceBefore=15,
    spaceAfter=10
)

# Tabla con colores
tableStyle = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
])
```

### Componentes Platypus

```python
from reportlab.platypus import (
    SimpleDocTemplate,  # Gestor de documento
    Table,             # Tablas
    Paragraph,         # Texto con estilos
    Spacer,            # Espacios
    PageBreak          # Saltos de página
)
```

### Estructura de PDF

```
┌───────────────────────────────────────────┐
│           FINCAFÁCIL                      │
│      REPORTE DE ANIMALES                  │
│                                           │
│  Período: 2024-01-01 → 2024-01-31        │
│  Generado: 2024-01-31 15:30              │
├───────────────────────────────────────────┤
│                                           │
│  INVENTARIO ACTUAL                        │
│  ┌──────────┬──────────┐                 │
│  │ Estado   │ Cantidad │                 │
│  ├──────────┼──────────┤                 │
│  │ Activo   │   150    │                 │
│  │ Vendido  │    20    │                 │
│  └──────────┴──────────┘                 │
│                                           │
│  MOVIMIENTOS DEL PERÍODO                  │
│  ┌────────┬────────┬──────┬──────────┐   │
│  │ Fecha  │ Número │ Tipo │  Valor   │   │
│  └────────┴────────┴──────┴──────────┘   │
│                                           │
├───────────────────────────────────────────┤
│              Página 1 de 1                │
└───────────────────────────────────────────┘
```

---

## 💡 Uso y Ejemplos

### Caso 1: Exportar Todos los Formatos

```python
from src.services.reportes_service import reportes_service
from src.utils.export import csv_exporter, excel_exporter, pdf_exporter

# Generar reporte una vez
reporte = reportes_service.generar_reporte('finanzas', inicio, fin)

# Exportar a los 3 formatos
csv_exporter.exportar(reporte, 'finanzas.csv')
excel_exporter.exportar(reporte, 'finanzas.xlsx')
pdf_exporter.exportar(reporte, 'finanzas.pdf')
```

### Caso 2: Exportación Condicional

```python
def exportar_inteligente(reporte, formato, ruta):
    """Exporta con fallback si dependencias faltantes"""
    
    if formato == 'pdf':
        try:
            pdf_exporter.exportar(reporte, ruta)
        except RuntimeError:
            print("PDF no disponible, usando CSV")
            csv_exporter.exportar(reporte, ruta.replace('.pdf', '.csv'))
    
    elif formato == 'excel':
        try:
            excel_exporter.exportar(reporte, ruta)
        except RuntimeError:
            print("Excel no disponible, usando CSV")
            csv_exporter.exportar(reporte, ruta.replace('.xlsx', '.csv'))
    
    else:
        csv_exporter.exportar(reporte, ruta)
```

### Caso 3: Exportación Batch

```python
from pathlib import Path

# Crear directorio
Path('exports/2024-01').mkdir(parents=True, exist_ok=True)

# Exportar todos los tipos
for tipo in ['animales', 'reproduccion', 'produccion', 'finanzas']:
    reporte = reportes_service.generar_reporte(tipo, inicio, fin)
    
    csv_exporter.exportar(reporte, f'exports/2024-01/{tipo}.csv')
    excel_exporter.exportar(reporte, f'exports/2024-01/{tipo}.xlsx')
    pdf_exporter.exportar(reporte, f'exports/2024-01/{tipo}.pdf')
```

### Caso 4: UI con Selector de Formato

```python
import customtkinter as ctk
from tkinter import filedialog

def btn_exportar_click():
    formato = combo_formato.get()  # 'CSV', 'Excel', 'PDF'
    
    ext = {'CSV': '.csv', 'Excel': '.xlsx', 'PDF': '.pdf'}[formato]
    ruta = filedialog.asksaveasfilename(
        defaultextension=ext,
        filetypes=[(formato, f'*{ext}')]
    )
    
    if not ruta:
        return
    
    try:
        if formato == 'CSV':
            csv_exporter.exportar(reporte_actual, ruta)
        elif formato == 'Excel':
            excel_exporter.exportar(reporte_actual, ruta)
        else:
            pdf_exporter.exportar(reporte_actual, ruta)
        
        messagebox.showinfo("Éxito", f"Exportado a {ruta}")
    
    except Exception as e:
        messagebox.showerror("Error", str(e))
```

---

## 🔧 Troubleshooting

### Error: "No module named 'openpyxl'"

**Problema**: Intentas exportar a Excel sin tener la librería.

**Solución**:

```bash
pip install openpyxl
```

O usa CSV como alternativa:

```python
try:
    excel_exporter.exportar(reporte, ruta)
except RuntimeError:
    csv_exporter.exportar(reporte, ruta.replace('.xlsx', '.csv'))
```

### Error: "No module named 'reportlab'"

**Problema**: Intentas exportar a PDF sin la librería.

**Solución**:

```bash
pip install reportlab
```

### Error: "Permission denied" al escribir archivo

**Problema**: El archivo está abierto en otra aplicación.

**Solución**: Cierra Excel/PDF viewer antes de exportar.

```python
# Verificar antes de exportar
import os
if os.path.exists(ruta):
    try:
        os.remove(ruta)  # Intenta eliminar
    except PermissionError:
        raise ValueError("Archivo en uso, ciérralo primero")
```

### Excel abre CSV con caracteres raros

**Problema**: Encoding incorrecto.

**Solución**: El exporter ya usa UTF-8 con BOM. Si persiste:

```python
# En export_csv.py, línea de apertura:
with open(ruta, 'w', encoding='utf-8-sig', newline='') as f:
    # utf-8-sig agrega BOM para Excel
```

### PDF genera tablas cortadas

**Problema**: Datos muy anchos.

**Solución**: Reduce tamaño de fuente o rota página:

```python
# En export_pdf.py:
doc = SimpleDocTemplate(
    ruta,
    pagesize=landscape(letter),  # Horizontal
    # ...
)
```

### Archivos muy grandes

**Problema**: Reportes de años completos generan PDFs pesados.

**Solución**: Limita registros o usa paginación:

```python
# Top 100 en lugar de todos
top_100 = reporte['datos']['detalle'][:100]
```

---

## 📚 API Reference

### CSVExporter

```python
class CSVExporter:
    def exportar(self, reporte: Dict[str, Any], ruta_salida: str) -> None
    def _exportar_animales(self, datos: Dict, writer) -> None
    def _exportar_reproduccion(self, datos: Dict, writer) -> None
    def _exportar_produccion(self, datos: Dict, writer) -> None
    def _exportar_finanzas(self, datos: Dict, writer) -> None
    def _exportar_completo(self, reporte: Dict, ruta_base: str) -> None
```

### ExcelExporter

```python
class ExcelExporter:
    openpyxl_disponible: bool  # Property
    
    def exportar(self, reporte: Dict[str, Any], ruta_salida: str) -> None
    def _verificar_dependencias(self) -> None
    def _exportar_animales(self, ws, datos: Dict) -> None
    def _exportar_reproduccion(self, ws, datos: Dict) -> None
    def _exportar_produccion(self, ws, datos: Dict) -> None
    def _exportar_finanzas(self, ws, datos: Dict) -> None
    def _exportar_completo(self, reporte: Dict, ruta_salida: str) -> None
```

### PDFExporter

```python
class PDFExporter:
    reportlab_disponible: bool  # Property
    
    def exportar(self, reporte: Dict[str, Any], ruta_salida: str) -> None
    def _verificar_dependencias(self) -> None
    def _construir_pdf_animales(self, reporte: Dict) -> List[Flowable]
    def _construir_pdf_reproduccion(self, reporte: Dict) -> List[Flowable]
    def _construir_pdf_produccion(self, reporte: Dict) -> List[Flowable]
    def _construir_pdf_finanzas(self, reporte: Dict) -> List[Flowable]
    def _construir_pdf_completo(self, reporte: Dict) -> List[Flowable]
```

---

## 🔗 Ver También

- [FASE3_REPORTES.md](./FASE3_REPORTES.md) - Sistema de reportes
- [FASE3_CIERRE_MENSUAL.md](./FASE3_CIERRE_MENSUAL.md) - Cierre contable
- [FASE3_RESUMEN_EJECUTIVO.md](./FASE3_RESUMEN_EJECUTIVO.md) - Resumen ejecutivo

---

**Documentación generada para FASE 3 - FincaFácil**  
*Sistema de Exportación Profesional*
