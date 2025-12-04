# Informe de Pruebas con Datos Reales - FincaFácil
**Fecha:** 16 de noviembre de 2025  
**Módulos analizados:** Configuración (Fincas, Sectores, Potreros, Lotes, Razas, Calidad Animal, Condición Corporal)

---

## Resumen Ejecutivo

Se han identificado **problemas críticos y recurrentes** en múltiples módulos de configuración que impiden el correcto funcionamiento de las operaciones CRUD (Crear, Leer, Actualizar, Eliminar) y la importación masiva desde Excel. Los hallazgos se agrupan en cinco categorías principales:

1. **Funcionalidad de edición bloqueada o incompleta**
2. **Código duplicado que genera inconsistencias**
3. **Problemas de serialización/mapeo en listados**
4. **Validaciones incorrectas de unicidad**
5. **Importación Excel con mapeo erróneo de columnas**

---

## 1. Módulo: Configuración de Fincas
**Archivo:** `modules/configuracion/fincas.py`

### Problemas Identificados

#### 1.1 Edición bloqueada (Línea 194)
```python
def editar_finca(self):
    seleccionado = self.tabla.selection()
    if not seleccionado:
        messagebox.showwarning("Atención", "Seleccione una finca para editar.")
        return
    messagebox.showinfo("Editar", "Funcionalidad de edición en desarrollo")
```

**Impacto:** Imposible editar registros existentes.  
**Causa:** Función stub sin implementación.

**Solución propuesta:**
- Crear ventana modal de edición similar a la implementada en `razas.py` (líneas 189-260)
- Cargar datos del registro seleccionado en formulario
- Implementar UPDATE en base de datos con validaciones

---

#### 1.2 Código duplicado dentro de funciones anidadas (Líneas 346-521)

**Problema crítico:** Las funciones `guardar_finca`, `cargar_fincas`, `editar_finca`, `eliminar_finca` e `importar_excel` están **duplicadas dentro de la función `importar_excel`** como funciones anidadas (indentadas incorrectamente).

```python
def importar_excel(self):
    # ... código de importación ...
    except Exception as e:
        messagebox.showerror("Error", f"Error al importar:\n{e}")

        def guardar_finca(self):  # ← DUPLICADO ANIDADO (Línea 346)
            """Guarda una nueva finca"""
            codigo = self.entry_codigo.get().strip()
            # ...
        
        def cargar_fincas(self):  # ← DUPLICADO ANIDADO (Línea 377)
            # ...
        
        def editar_finca(self):  # ← DUPLICADO ANIDADO
        
        def eliminar_finca(self):  # ← DUPLICADO ANIDADO
        
        def importar_excel(self):  # ← DUPLICADO ANIDADO (Línea 427)
```

**Impacto:** 
- Las funciones correctas (líneas 114-227) son sobrescritas por versiones anidadas que nunca se ejecutan
- Código confuso y difícil de mantener
- Posibles comportamientos inesperados

**Solución:**
- **ELIMINAR completamente las líneas 346-521** (funciones duplicadas anidadas)
- Mantener solo las versiones originales (líneas 114-227)

---

#### 1.3 Validación de unicidad incorrecta
**Problema:** El sistema indica "ya existe" aunque el registro no aparece en el listado.

**Causa raíz:** La validación se hace contra **todos los registros** (incluyendo inactivos), pero el listado solo muestra registros con `estado = 'Activo'`.

```python
# Línea 157: Validación en INSERT
except sqlite3.IntegrityError:
    messagebox.showerror("Error", "Ya existe una finca con ese código.")

# Línea 172: Consulta en listado
cursor.execute(
    "SELECT codigo, nombre, propietario, area_hectareas, ubicacion FROM finca WHERE estado = 'Activo'"
)
```

**Solución propuesta:**
1. **Opción A (Recomendada):** Permitir reutilización de códigos de registros inactivos
   ```python
   # Antes de INSERT, verificar si existe un registro inactivo
   cursor.execute("SELECT id FROM finca WHERE codigo = ? AND estado = 'Inactivo'", (codigo,))
   inactivo = cursor.fetchone()
   if inactivo:
       # Reactivar y actualizar
       cursor.execute("UPDATE finca SET estado='Activo', nombre=?, ... WHERE id=?", (..., inactivo[0]))
   else:
       # INSERT normal
   ```

2. **Opción B:** Mejorar mensaje de error
   ```python
   except sqlite3.IntegrityError:
       messagebox.showerror("Error", 
           "Ya existe una finca con ese código.\n"
           "Puede estar marcada como inactiva. Contacte al administrador.")
   ```

---

#### 1.4 Importación Excel: Mapeo incorrecto de columnas

**Problema 1:** Campo `area_hectareas` se guarda como 0

**Causa:** El código busca columnas `area` o `area_hectareas`, pero el archivo Excel puede tener nombres diferentes (ej: "Área (Ha)", "Area", "area_ha").

```python
# Línea 299-305: Mapeo rígido
area_raw = fila.get("area")
if area_raw in (None, ""):
    area_raw = fila.get("area_hectareas")
try:
    area_val = float(area_raw) if area_raw not in (None, "") else 0
except Exception:
    area_val = 0
```

**Solución:**
```python
# Normalizar nombres de columnas al leer Excel
def normalizar_columna(nombre):
    """Normaliza nombres de columnas para búsqueda flexible"""
    return nombre.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("á", "a").replace("é", "e")

# En parse_excel_to_dicts, normalizar keys del diccionario
def parse_excel_to_dicts(ruta):
    # ... código existente ...
    for fila in ws.iter_rows(min_row=2, values_only=True):
        dict_fila = {}
        for i, valor in enumerate(fila):
            if i < len(encabezados):
                col_normalizada = normalizar_columna(encabezados[i])
                dict_fila[col_normalizada] = valor
        # ...
```

**Problema 2:** Campo `ubicacion` no se toma del archivo

**Causa:** Similar al área, falta flexibilidad en el mapeo de columnas.

```python
# Línea 314: Solo busca 'ubicacion'
fila.get("ubicacion") or None
```

**Solución:** Aplicar la misma normalización propuesta arriba.

---

#### 1.5 Falta botón "Exportar" para plantilla Excel

**Propuesta:** Agregar botón para generar archivo Excel con estructura esperada.

```python
def exportar_plantilla(self):
    """Genera plantilla Excel con estructura correcta"""
    import pandas as pd
    from datetime import datetime
    
    # Crear DataFrame con columnas y fila de ejemplo
    plantilla = pd.DataFrame([{
        'codigo': 'FINCA001',
        'nombre': 'Ejemplo Finca',
        'propietario': 'Juan Pérez',
        'area': 100.5,
        'ubicacion': 'Vereda El Ejemplo',
        'telefono': '3001234567',
        'email': 'ejemplo@correo.com',
        'descripcion': 'Finca de ejemplo'
    }])
    
    ruta = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialfile=f"plantilla_fincas_{datetime.now().strftime('%Y%m%d')}.xlsx"
    )
    
    if ruta:
        plantilla.to_excel(ruta, index=False)
        messagebox.showinfo("Éxito", f"Plantilla generada en:\n{ruta}")

# Agregar botón en action_frame (después de línea 112)
ctk.CTkButton(action_frame, text="📤 Exportar Plantilla", 
              command=self.exportar_plantilla).pack(side="left", padx=5)
```

---

## 2. Módulo: Configuración de Sectores
**Archivo:** `modules/configuracion/sectores.py`

### Problemas Identificados

#### 2.1 Serialización incorrecta en tabla (Problema crítico reportado por usuario)

**Síntoma:** Los datos se muestran como:
- `codigo: <sqlite3.row`
- `nombre: object`
- `comentario: at`

**Causa raíz:** **No encontrada en el código analizado**. El código actual (líneas 124-138) es correcto:

```python
def cargar_sectores(self):
    """Carga los sectores en la tabla"""
    for fila in self.tabla.get_children():
        self.tabla.delete(fila)

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, COALESCE(comentario, descripcion, '') as comentario FROM sector WHERE estado = 'Activo' OR estado = 'Activa'")
            
            for fila in cursor.fetchall():
                self.tabla.insert("", "end", values=fila)  # ← Correcto
```

**Hipótesis:**
1. **Versión antigua del archivo en ejecución:** El código actual no coincide con el ejecutable compilado
2. **Error en database.py:** El método `fetchall()` retorna objetos Row mal configurados
3. **Corrupción de base de datos:** La tabla `sector` tiene datos corruptos

**Acciones de diagnóstico requeridas:**
```python
# Agregar debug temporal en línea 136
for fila in cursor.fetchall():
    print(f"DEBUG: Tipo fila: {type(fila)}, Contenido: {fila}")  # ← AGREGAR
    print(f"DEBUG: fila[0]={fila[0]}, fila[1]={fila[1]}, fila[2]={fila[2]}")
    self.tabla.insert("", "end", values=fila)
```

**Solución preventiva (conversión explícita):**
```python
for fila in cursor.fetchall():
    # Forzar conversión a tupla de strings
    valores = (str(fila[0]), str(fila[1]), str(fila[2] if fila[2] else ""))
    self.tabla.insert("", "end", values=valores)
```

---

#### 2.2 Edición bloqueada (Línea 140)
Mismo problema que fincas. **Solución:** Implementar ventana de edición modal.

#### 2.3 Eliminación no actualiza vista

**Problema:** El registro no desaparece tras eliminación exitosa.

**Causa:** El código es correcto (línea 162: `self.cargar_sectores()`), pero posiblemente:
1. La operación UPDATE no se confirma (aunque `conn.commit()` está presente)
2. El filtro `WHERE estado = 'Activo'` en `cargar_sectores` no coincide con el valor después del UPDATE

**Verificación necesaria:**
```python
# Línea 159: Agregar debug
cursor.execute("UPDATE sector SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
print(f"DEBUG: Filas afectadas: {cursor.rowcount}")  # ← AGREGAR
conn.commit()
```

**Solución alternativa (eliminación física):**
```python
def eliminar_sector(self):
    # ... código existente ...
    if messagebox.askyesno("Confirmar", f"¿Eliminar el sector '{codigo}'?"):
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar dependencias
                cursor.execute("SELECT COUNT(*) FROM potrero WHERE sector = ?", (codigo,))
                count = cursor.fetchone()[0]
                if count > 0:
                    messagebox.showerror("Error", 
                        f"No se puede eliminar: hay {count} potrero(s) asignado(s) a este sector.")
                    return
                
                # Eliminación lógica o física según preferencia
                cursor.execute("UPDATE sector SET estado = 'Inactivo' WHERE codigo = ?", (codigo,))
                conn.commit()
                
            messagebox.showinfo("Éxito", "Sector eliminado.")
            self.cargar_sectores()
```

---

## 3. Módulo: Configuración de Potreros
**Archivo:** `modules/configuracion/potreros.py`

### Problemas Identificados

#### 3.1 Mapeo incorrecto similar a sectores

**Problema reportado:** Valores como `finca: <sqlite3.row`, `potrero: object`, etc.

**Análisis del código:** La consulta JOIN es correcta (líneas 238-245):
```python
cursor.execute("""
    SELECT f.nombre as finca, p.nombre, p.sector, p.area_hectareas, 
           p.capacidad_maxima, p.tipo_pasto, p.estado
    FROM potrero p
    JOIN finca f ON p.id_finca = f.id
    WHERE p.estado = 'Activo'
""")
```

**Mismo problema que sectores:** El código actual no debería generar este error. Se requiere:
1. Recompilar ejecutable
2. Agregar conversión explícita a strings
3. Verificar configuración de `database.py`

---

#### 3.2 Edición no encuentra registros

**Problema:** Al editar, indica "No se encontró el potrero" aunque está en el listado.

**Causa:** Discrepancia en la búsqueda (líneas 267-273):
```python
# Busca por NOMBRE de finca y potrero obtenidos de la tabla
cursor.execute("""
    SELECT p.*, f.nombre as finca_nombre 
    FROM potrero p
    JOIN finca f ON p.id_finca = f.id
    WHERE p.nombre = ? AND f.nombre = ?
""", (potrero_nombre, finca_nombre))
```

**Problema:** Si hay fincas con nombres similares o espacios extra, la búsqueda falla.

**Solución:** Usar el ID del potrero (almacenar en la tabla con columna oculta):
```python
# En crear_widgets, agregar columna id oculta
self.tabla = ttk.Treeview(table_frame, 
    columns=("id", "finca", "nombre", "sector", "area", "capacidad", "pasto", "estado"), 
    show="headings", 
    displaycolumns=("finca", "nombre", "sector", "area", "capacidad", "pasto", "estado"),  # Ocultar 'id'
    height=12)

# En cargar_potreros, incluir p.id
cursor.execute("""
    SELECT p.id, f.nombre as finca, p.nombre, p.sector, p.area_hectareas, 
           p.capacidad_maxima, p.tipo_pasto, p.estado
    FROM potrero p
    JOIN finca f ON p.id_finca = f.id
    WHERE p.estado = 'Activo'
""")

# En editar_potrero, buscar por ID
potrero_id = self.tabla.item(seleccionado[0])["values"][0]  # Ahora es el ID
cursor.execute("SELECT p.*, f.nombre as finca_nombre FROM potrero p JOIN finca f ON p.id_finca = f.id WHERE p.id = ?", (potrero_id,))
```

---

#### 3.3 Importación Excel: Validación FK incorrecta

**Problema reportado:** `fila2 finca finca el prado no encontrada o inactiva`

**Causa:** El código de importación no está visible en las líneas leídas, pero probablemente busca finca por nombre exacto sin normalización.

**Solución:** Normalizar búsqueda de finca (case-insensitive, sin espacios extra):
```python
# En importación
finca_nombre = str(fila.get('finca') or "").strip().lower()
cursor.execute(
    "SELECT id FROM finca WHERE LOWER(TRIM(nombre)) = ? AND (estado = 'Activo' OR estado = 'Activa')",
    (finca_nombre,)
)
finca_id = cursor.fetchone()
if not finca_id:
    errores.append(f"Fila {idx}: Finca '{fila.get('finca')}' no encontrada o inactiva")
    continue
```

---

## 4. Módulo: Configuración de Lotes
**Archivo:** `modules/configuracion/lotes.py` (no leído aún)

**Pendiente:** Análisis similar a potreros (problemas esperados idénticos).

---

## 5. Módulo: Configuración de Razas
**Archivo:** `modules/configuracion/razas.py`

### Problemas Identificados

#### 5.1 Edición correctamente implementada ✓

**Hallazgo positivo:** La edición **SÍ funciona correctamente** (líneas 170-263):
- Abre ventana modal
- Carga datos del registro
- **Tiene botón "Guardar"** (línea 257)

```python
ctk.CTkButton(btn_frame, text="💾 Guardar", command=guardar_cambios,
            fg_color="green", hover_color="#006400").pack(side="left", padx=5)
```

**Contradicción con reporte del usuario:** El reporte indica "no existe opción para guardar los cambios", pero el código muestra que sí existe.

**Posibles causas:**
1. **Versión antigua ejecutándose:** El .exe no coincide con el código fuente actual
2. **Error de interfaz:** El botón no es visible por problema de layout
3. **Usuario revisó archivo equivocado**

**Acción:** Recompilar con PyInstaller y verificar.

---

#### 5.2 Importación solo simula

**Problema:** No se encontró el código de `importar_excel` en las líneas leídas (392 líneas totales).

**Acción requerida:** Leer líneas 270-392 para analizar la función.

---

## 6. Módulo: Calidad Animal
**Archivo:** `modules/configuracion/calidad_animal.py`

### Problemas Identificados

#### 6.1 Registros guardados no aparecen en listado

**Código de guardado (líneas 97-127):**
```python
def guardar_calidad(self):
    # ... validaciones ...
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if self.entry_codigo.cget("state") == "disabled":
                # UPDATE
                cursor.execute("""
                    UPDATE calidad_animal 
                    SET descripcion = ?, comentario = ?
                    WHERE codigo = ?
                """, (descripcion, comentario, codigo))
            else:
                # INSERT
                cursor.execute("""
                    INSERT INTO calidad_animal (codigo, descripcion, comentario)
                    VALUES (?, ?, ?)
                """, (codigo, descripcion, comentario))
            # ¿Falta conn.commit()?  ← PROBLEMA POTENCIAL
```

**PROBLEMA CRÍTICO:** No hay `conn.commit()` después del INSERT/UPDATE.

**Código de carga (líneas 130-141):**
```python
def cargar_calidades(self):
    for item in self.tabla.get_children():
        self.tabla.delete(item)

    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, descripcion, comentario FROM calidad_animal")
            for calidad in cursor.fetchall():
                self.tabla.insert("", "end", values=calidad)
```

**Análisis:**
- La consulta **NO filtra por estado** (correcto, no hay columna `estado` en `calidad_animal`)
- **Falta `conn.commit()`** en guardado

**Solución:**
```python
def guardar_calidad(self):
    # ... código existente ...
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if self.entry_codigo.cget("state") == "disabled":
                cursor.execute("""...""")
                messagebox.showinfo("Éxito", "Calidad animal actualizada")
            else:
                cursor.execute("""...""")
                messagebox.showinfo("Éxito", "Calidad animal guardada")
            
            conn.commit()  # ← AGREGAR ESTA LÍNEA
        
        self.limpiar_formulario()
        self.cargar_calidades()
```

---

## 7. Módulo: Condición Corporal
**Archivo:** `modules/configuracion/condiciones_corporales.py`

**Análisis pendiente:** Leer líneas 139-184 para función `guardar_condicion` y `cargar_condiciones`.

**Problema esperado:** Falta de `conn.commit()` similar a `calidad_animal.py`.

---

## Resumen de Correcciones Prioritarias

### Prioridad CRÍTICA (impide uso básico)

1. **fincas.py**: Eliminar código duplicado (líneas 346-521)
2. **fincas.py**: Implementar función `editar_finca()`
3. **calidad_animal.py** y **condiciones_corporales.py**: Agregar `conn.commit()`
4. **Todos los módulos**: Verificar y corregir serialización de datos en tablas (recompilar ejecutable)

### Prioridad ALTA (funcionalidad importante)

5. **fincas.py**, **potreros.py**: Mejorar mapeo de columnas Excel con normalización
6. **sectores.py**: Implementar función `editar_sector()`
7. **potreros.py**: Usar ID en lugar de nombre para edición
8. **fincas.py**: Mejorar validación de unicidad (permitir reactivación)

### Prioridad MEDIA (mejoras de UX)

9. **Todos los módulos**: Agregar botón "Exportar Plantilla Excel"
10. **potreros.py**, **lotes.py**: Validar dependencias antes de eliminar
11. **razas.py**: Verificar visibilidad del botón "Guardar" en ventana de edición

---

## Recomendaciones Generales

### 1. Estándar de código para operaciones CRUD

Crear una clase base `CRUDFrame` con métodos genéricos:

```python
class CRUDFrame(ctk.CTkFrame):
    """Clase base para módulos CRUD"""
    
    def __init__(self, master, tabla_db, columnas, campos_form):
        super().__init__(master)
        self.tabla_db = tabla_db
        self.columnas = columnas
        self.campos_form = campos_form
        # ... inicialización común
    
    def guardar_registro(self):
        """Guardado genérico con commit garantizado"""
        # ...
        conn.commit()  # ← Siempre presente
        self.cargar_registros()
    
    def editar_registro(self):
        """Edición genérica con ventana modal"""
        # ...
    
    def cargar_registros(self):
        """Carga con conversión explícita a strings"""
        for fila in cursor.fetchall():
            valores = tuple(str(v) if v is not None else "" for v in fila)
            self.tabla.insert("", "end", values=valores)
```

### 2. Normalización de importaciones Excel

Crear utilidad centralizada:

```python
# modules/utils/excel_normalizer.py
def normalizar_diccionario_excel(dict_fila):
    """Normaliza nombres de columnas para mapeo flexible"""
    mapa_estandar = {
        'area': ['area', 'area_ha', 'area_hectareas', 'hectareas'],
        'ubicacion': ['ubicacion', 'ubicación', 'direccion', 'dirección'],
        'finca': ['finca', 'finca_nombre', 'nombre_finca'],
        # ...
    }
    
    resultado = {}
    for key_std, variantes in mapa_estandar.items():
        for var in variantes:
            valor = dict_fila.get(var)
            if valor not in (None, ""):
                resultado[key_std] = valor
                break
    
    return resultado
```

### 3. Testing antes de compilación

Crear script de validación:

```bash
# scripts/validar_modulos.py
import sqlite3
from modules.configuracion import fincas, sectores, potreros

def test_crud(modulo, datos_prueba):
    """Prueba operaciones CRUD básicas"""
    # 1. Crear registro
    # 2. Verificar que aparezca en listado
    # 3. Editar registro
    # 4. Verificar cambios
    # 5. Eliminar registro
    # 6. Verificar desaparición
```

---

## Anexo: Checklist de Validación

Antes de marcar como "resuelto", verificar:

- [ ] El código compila sin errores
- [ ] El ejecutable se genera correctamente
- [ ] Crear registro → Aparece en tabla
- [ ] Editar registro → Abre ventana y guarda cambios
- [ ] Eliminar registro → Desaparece de tabla
- [ ] Importar Excel con plantilla → Todos los campos se mapean
- [ ] Importar Excel con nombres variantes → Funcionan alternativas
- [ ] No hay código duplicado en ningún archivo
- [ ] Todas las transacciones tienen `conn.commit()`
- [ ] Las consultas SELECT usan conversión explícita de tipos

---

**Fin del informe**

*Este documento debe actualizarse conforme se implementen correcciones.*
