# Correcciones de Errores Críticos - Sesión 2
**Fecha:** 16 de noviembre de 2025  
**Estado:** ✅ Completado

---

## Problemas Reportados por el Usuario

### 🔴 Problema 1: Error "cannot operate on a closed database" en Fincas
**Módulo:** Configuración de Fincas  
**Acción:** Editar finca → Guardar cambios  
**Error:** `cannot operate on a closed database`

**Causa raíz:**
La función anidada `guardar_cambios()` dentro de `editar_finca()` intentaba usar variables `cursor` y `conn` que ya estaban fuera del contexto `with`, causando que la conexión estuviera cerrada.

```python
# ANTES (INCORRECTO):
with db.get_connection() as conn:
    cursor = conn.cursor()
    # ... código ...
    
    def guardar_cambios():
        cursor.execute(...)  # ❌ cursor ya no válido
        conn.commit()         # ❌ conexión cerrada
```

**Solución implementada:**
Crear una nueva conexión dentro de `guardar_cambios()`:

```python
# DESPUÉS (CORRECTO):
def guardar_cambios():
    with db.get_connection() as conn_update:
        cursor_update = conn_update.cursor()
        cursor_update.execute(...)
        conn_update.commit()  # ✅ Conexión activa
```

**Archivo:** `modules/configuracion/fincas.py` (línea ~300)

---

### 🔴 Problema 2: Datos se muestran como `<sqlite3.Row`, `object`, `at` en Sectores

**Módulo:** Configuración de Sectores (y otros)  
**Síntoma visual:** 
```
Código         | Nombre  | Comentario
<sqlite3.Row   | object  | at
```

**Causa raíz:**
Los objetos `Row` de SQLite se estaban insertando directamente en el Treeview sin convertir a tipos primitivos. Cuando Tkinter intenta renderizarlos, muestra la representación del objeto en lugar de los valores.

```python
# ANTES (INCORRECTO):
for fila in cursor.fetchall():
    self.tabla.insert("", "end", values=fila)  # ❌ fila es sqlite3.Row
```

**Solución implementada:**
Convertir explícitamente cada campo a `str`:

```python
# DESPUÉS (CORRECTO):
for fila in cursor.fetchall():
    valores = (
        str(fila[0]) if fila[0] is not None else "",
        str(fila[1]) if fila[1] is not None else "",
        str(fila[2]) if fila[2] is not None else ""
    )
    self.tabla.insert("", "end", values=valores)  # ✅ Tupla de strings
```

---

## Correcciones Aplicadas

### ✅ 1. Fincas - Error "closed database"
**Archivo:** `modules/configuracion/fincas.py`  
**Función:** `editar_finca() → guardar_cambios()`  
**Cambio:** Nueva conexión en función anidada

---

### ✅ 2. Sectores - Serialización + Error "closed database"
**Archivo:** `modules/configuracion/sectores.py`  
**Funciones modificadas:**
- `cargar_sectores()` - Conversión explícita a strings
- `editar_sector() → guardar_cambios()` - Nueva conexión

**Antes:**
```python
for fila in cursor.fetchall():
    self.tabla.insert("", "end", values=fila)
```

**Después:**
```python
for fila in cursor.fetchall():
    valores = (
        str(fila[0]) if fila[0] is not None else "",
        str(fila[1]) if fila[1] is not None else "",
        str(fila[2]) if fila[2] is not None else ""
    )
    self.tabla.insert("", "end", values=valores)
```

---

### ✅ 3. Potreros - Serialización
**Archivo:** `modules/configuracion/potreros.py`  
**Función:** `cargar_potreros()`  
**Cambio:** Conversión de 8 campos (id, finca, nombre, sector, area, capacidad, pasto, estado)

---

### ✅ 4. Fincas - Serialización preventiva
**Archivo:** `modules/configuracion/fincas.py`  
**Función:** `cargar_fincas()`  
**Cambio:** Conversión de 5 campos (codigo, nombre, propietario, area, ubicacion)

---

### ✅ 5. Lotes - Serialización
**Archivo:** `modules/configuracion/lotes.py`  
**Función:** `cargar_lotes()`  
**Cambio:** Conversión de 4 campos (codigo, nombre, descripcion, criterio)

---

## Resumen Técnico

### Patrón de corrección aplicado:

**1. Para funciones de carga (cargar_xxx):**
```python
# Patrón estándar implementado:
for fila in cursor.fetchall():
    valores = tuple(str(campo) if campo is not None else "" for campo in fila)
    self.tabla.insert("", "end", values=valores)
```

**2. Para funciones de edición anidadas:**
```python
# Patrón estándar implementado:
def guardar_cambios():
    with db.get_connection() as conn_nueva:
        cursor_nueva = conn_nueva.cursor()
        cursor_nueva.execute(...)
        conn_nueva.commit()
```

---

## Archivos Modificados

| Archivo | Funciones Corregidas | Tipo de Corrección |
|---------|---------------------|-------------------|
| `fincas.py` | `cargar_fincas()`, `editar_finca()` | Serialización + Conexión |
| `sectores.py` | `cargar_sectores()`, `editar_sector()` | Serialización + Conexión |
| `potreros.py` | `cargar_potreros()` | Serialización |
| `lotes.py` | `cargar_lotes()` | Serialización |

**Total:** 4 archivos, 6 funciones corregidas

---

## Pruebas Recomendadas

### Sectores
- [ ] Crear sector → Verificar que aparezca con datos correctos (no `<sqlite3.Row`)
- [ ] Editar sector → Guardar → Verificar que no dé error "closed database"
- [ ] Verificar que código, nombre y comentario se muestren correctamente

### Fincas
- [ ] Crear finca → Verificar datos en listado
- [ ] Editar finca → Cambiar datos → Guardar → Verificar que se actualice sin error
- [ ] Verificar que todos los campos se muestren como texto legible

### Potreros y Lotes
- [ ] Verificar que los listados muestren datos correctos (no objetos)
- [ ] Probar crear y editar registros

---

## Explicación del Problema Técnico

### ¿Por qué ocurría `<sqlite3.Row`?

SQLite3 en Python puede retornar resultados como objetos `Row` en lugar de tuplas simples. Estos objetos tienen una representación de string que muestra `<sqlite3.Row object at 0x...>`.

Cuando Tkinter Treeview recibe un objeto `Row`:
- Intenta convertirlo a string llamando `str(row_object)`
- Resultado: `"<sqlite3.Row object at 0x...>"`
- En pantalla se ve: `<sqlite3.Row`, `object`, `at` (truncado por columnas)

### ¿Por qué ocurría "closed database"?

Las conexiones `with` se cierran automáticamente al salir del bloque:
```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Dentro: conn ABIERTA ✅
# Fuera: conn CERRADA ❌

def funcion_anidada():
    cursor.execute()  # ❌ ERROR: conexión ya cerrada
```

**Solución:** Crear nueva conexión dentro de la función que la necesita.

---

## Notas Importantes

⚠️ **Estos cambios solo afectan el código fuente**. Para que surtan efecto:

1. **Si ejecuta desde Python:**
   ```bash
   python main.py
   ```
   ✅ Los cambios ya están activos

2. **Si ejecuta desde .exe compilado:**
   ```bash
   python -m PyInstaller FincaFacil.spec --clean
   ```
   ⚠️ Debe recompilar para que los cambios se apliquen

---

## Prevención de Problemas Similares

### Regla 1: Conversión explícita en cargas
```python
# ✅ CORRECTO - Siempre convertir a tipos primitivos
valores = tuple(str(v) if v is not None else "" for v in fila)

# ❌ INCORRECTO - Insertar objetos directamente
self.tabla.insert("", "end", values=fila)
```

### Regla 2: Conexiones en scope correcto
```python
# ✅ CORRECTO - Conexión en el scope que la usa
def guardar():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(...)
        conn.commit()

# ❌ INCORRECTO - Usar conexión fuera de su scope
with db.get_connection() as conn:
    cursor = conn.cursor()
    
    def guardar():
        cursor.execute(...)  # ❌ Fuera de scope
```

---

**Estado final:** ✅ Todos los problemas reportados corregidos  
**Próximo paso:** Probar en la aplicación y recompilar si es necesario

---

**Documentos relacionados:**
- `INFORME_PRUEBAS_DATOS_REALES.md` - Análisis inicial
- `CORRECCIONES_IMPLEMENTADAS.md` - Primera sesión de correcciones
