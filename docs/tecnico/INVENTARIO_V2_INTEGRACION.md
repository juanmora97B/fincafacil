# 🚀 Guía de Integración Rápida - Inventario V2

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Ejecutar Migración

```bash
python migrar_inventario_v2.py
```

**Salida esperada**:
```
======================================================================
🔧 MIGRACIÓN INVENTARIO V2 - INICIO
======================================================================

📋 Verificando columnas en tabla 'animal'...
   ✓ Columna 'ultimo_peso' ya existe
   ✓ Columna 'fecha_ultimo_peso' ya existe
   ...

✅ MIGRACIÓN COMPLETADA EXITOSAMENTE
======================================================================
```

### 2️⃣ Probar en Standalone

```bash
python test_inventario_v2.py
```

Esto abre una ventana de prueba independiente con el módulo completo.

### 3️⃣ Integrar en tu App

#### Opción A: Reemplazar módulo existente

En `modules/animales/__init__.py`:

```python
# Importar V2 en lugar de inventario_general
from modules.animales.inventario_v2 import InventarioGeneralFrame

# En tu método de construcción de tabs:
self.inventario_frame = InventarioGeneralFrame(self.tab_inventario)
self.inventario_frame.pack(fill="both", expand=True)
```

#### Opción B: Agregar como nueva pestaña

```python
# Crear nueva pestaña
self.tab_inventario_v2 = self.tabs.add("📋 Inventario V2")

from modules.animales.inventario_v2 import InventarioGeneralFrame
frame = InventarioGeneralFrame(self.tab_inventario_v2)
frame.pack(fill="both", expand=True)
```

## 📋 Checklist de Integración

- [ ] Ejecutar `migrar_inventario_v2.py` sin errores
- [ ] Probar `test_inventario_v2.py` y verificar:
  - [ ] Fincas se cargan en combobox
  - [ ] Filtros dependientes funcionan (cambiar finca → sectores/lotes/potreros cambian)
  - [ ] Búsqueda filtra en tiempo real (esperar 250ms)
  - [ ] Tabla muestra animales
  - [ ] Seleccionar animal habilita botones
  - [ ] Botón "Ver" abre modal con foto/datos
  - [ ] Botón "Editar" abre formulario
  - [ ] Botón "Gráficas" abre ventana con 6 charts
  - [ ] Exportar Excel genera archivo
  - [ ] Redimensionar ventana expande tabla
- [ ] Integrar en `main.py` o `modules/animales/__init__.py`
- [ ] Probar en app completa
- [ ] Verificar que no rompe módulos existentes

## 🔧 Integración Avanzada

### Compartir filtros entre módulos

```python
# En tu clase principal de Animales:
class AnimalesModule(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Estado compartido
        self.current_filters = {}
        
        # Tab Inventario
        self.inventario = InventarioGeneralFrame(self.tab1)
        
        # Tab Realizar Inventario (usa mismos filtros)
        self.realizar_inv = RealizarInventarioFrame(self.tab2)
        
    def on_filtros_change(self, filters):
        """Callback cuando cambian filtros"""
        self.current_filters = filters
        # Actualizar otros módulos si es necesario
```

### Exportar con callback personalizado

```python
from modules.animales.inventario_v2 import buscar_animales, exportar_animales_a_excel

def mi_exportacion_personalizada():
    filters = {'finca_id': 1}
    animales = buscar_animales(filters, "")
    
    # Transformar datos
    rows = []
    for a in animales:
        row = [
            a['id'],
            a['codigo'],
            a['nombre'],
            # ... agregar más columnas
        ]
        rows.append(row)
    
    # Exportar
    filepath = "mi_reporte.xlsx"
    exportar_animales_a_excel(rows, filepath)
    print(f"✓ Exportado a {filepath}")
```

### Abrir gráficas desde otro módulo

```python
from modules.animales.ventana_graficas import VentanaGraficas

def abrir_graficas_finca(finca_id):
    """Abrir gráficas de una finca específica"""
    filters = {'finca_id': finca_id}
    ventana = VentanaGraficas(parent, filters)
```

## 🎨 Personalización Post-Integración

### 1. Cambiar colores del tema

En `inventario_v2.py`, buscar `fg_color` y reemplazar:

```python
# Antes
fg_color="#1f538d"

# Después (usar tu color corporativo)
fg_color="#00796b"  # Ejemplo: teal
```

### 2. Agregar campos personalizados a tabla

En `inventario_v2.py`, método `_build_table`:

```python
# Agregar columna
columns = ["id", "codigo", "nombre", ..., "mi_campo_custom"]

# Configurar ancho
col_config = {
    ...
    "mi_campo_custom": ("Mi Campo", 120, "center")
}

# En buscar_animales, agregar campo al SELECT:
sql = """
    SELECT 
        ...,
        a.mi_campo_custom
    FROM animal a
    ...
"""
```

### 3. Agregar gráfico personalizado

En `ventana_graficas.py`, método `_renderizar_graficos`:

```python
# Agregar subplot
self._mi_grafico_custom(fig.add_subplot(2, 4, 7), finca1_id)

# Implementar método:
def _mi_grafico_custom(self, ax, finca_id):
    """Mi gráfico personalizado"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT ... FROM animal WHERE ...")
            data = cur.fetchall()
        
        # Renderizar
        ax.bar(...)
        ax.set_title('Mi Gráfico')
    except Exception as e:
        ax.text(0.5, 0.5, f'Error: {e}', ...)
```

## 🐛 Resolución de Problemas Comunes

### Problema: "No se encuentran animales"

**Solución**:
```bash
# Verificar que hay datos
python -c "from database.database import get_db_connection; conn = get_db_connection(); print(conn.execute('SELECT COUNT(*) FROM animal').fetchone())"

# Si devuelve 0, ejecutar:
python migrar_inventario_v2.py  # Insertará animal de prueba
```

### Problema: "Filtros no cargan"

**Solución**: Verificar nombres de columnas FK

```python
# En database.py o consola SQLite
PRAGMA table_info(potrero);
PRAGMA table_info(sector);
PRAGMA table_info(lote);

# Buscar columnas: finca_id vs id_finca
# El módulo detecta automáticamente, pero verifica que existan
```

### Problema: "Gráficas no se muestran"

**Solución**:
```bash
# Instalar matplotlib con backend TkAgg
pip install matplotlib

# Si persiste, agregar al inicio de ventana_graficas.py:
import matplotlib
matplotlib.use('TkAgg')
```

### Problema: "Excel no exporta"

**Solución**:
```bash
# Instalar openpyxl
pip install openpyxl

# Si falla, usa CSV como fallback (automático en el código)
```

## 📦 Archivos Generados

```
modules/animales/
├── inventario_v2.py              ✅ Módulo principal
├── modal_ver_animal.py           ✅ Modal detalle
├── modal_editar_animal.py        ✅ Modal edición
└── ventana_graficas.py           ✅ Panel gráficas

data/
└── fotos_animales/               📁 Fotos (creado automáticamente)

migrar_inventario_v2.py           ✅ Script migración
test_inventario_v2.py             ✅ Test standalone
INVENTARIO_V2_DOCS.md             📚 Documentación completa
INVENTARIO_V2_INTEGRACION.md      📋 Esta guía
```

## ✅ Verificación Final

Ejecuta este script para verificar todo:

```python
# verificar_v2.py
import sys
from pathlib import Path

print("🔍 Verificando Inventario V2...\n")

# 1. Archivos
archivos = [
    "modules/animales/inventario_v2.py",
    "modules/animales/modal_ver_animal.py",
    "modules/animales/modal_editar_animal.py",
    "modules/animales/ventana_graficas.py",
]

for archivo in archivos:
    if Path(archivo).exists():
        print(f"✅ {archivo}")
    else:
        print(f"❌ {archivo} - NO ENCONTRADO")

# 2. Imports
print("\n🔌 Verificando imports...")
try:
    from modules.animales.inventario_v2 import InventarioGeneralFrame
    print("✅ inventario_v2 importado")
except Exception as e:
    print(f"❌ Error: {e}")

try:
    from modules.animales.modal_ver_animal import ModalVerAnimal
    print("✅ modal_ver_animal importado")
except Exception as e:
    print(f"❌ Error: {e}")

try:
    from modules.animales.ventana_graficas import VentanaGraficas
    print("✅ ventana_graficas importado")
except Exception as e:
    print(f"❌ Error: {e}")

# 3. Database
print("\n🗄️  Verificando base de datos...")
try:
    from database.database import get_db_connection
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM animal")
        count = cur.fetchone()[0]
        print(f"✅ Base de datos OK - {count} animales")
except Exception as e:
    print(f"❌ Error BD: {e}")

print("\n✅ Verificación completada")
```

## 🎯 Próximos Pasos

1. **Personalizar colores** según tu branding
2. **Agregar campos** específicos de tu negocio
3. **Crear reportes** adicionales (PDF, impresión)
4. **Integrar con otros módulos** (ventas, reproducción, etc.)
5. **Implementar notificaciones** (animales sin inventariar, pesos bajos, etc.)

## 📞 Soporte

Si encuentras problemas:

1. Verifica la **consola** de Python para errores detallados
2. Ejecuta `python test_inventario_v2.py` para aislar el problema
3. Revisa `INVENTARIO_V2_DOCS.md` para troubleshooting
4. Comprueba que todas las **dependencias** están instaladas:
   ```bash
   pip install customtkinter matplotlib Pillow openpyxl
   ```

---

**¡Listo para producción! 🎉**

Tu módulo Inventario V2 está completamente funcional y documentado.
