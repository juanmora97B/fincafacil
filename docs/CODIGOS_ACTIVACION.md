# CÓDIGOS DE ACTIVACIÓN - GUÍA PARA EL PROGRAMADOR

## 📋 Resumen

Los códigos de activación son claves únicas que permiten convertir una licencia de prueba (6 meses) en una licencia permanente. Este documento explica dónde se almacenan, cómo se generan y cómo acceder a ellos como programador.

---

## 📍 UBICACIÓN DE LOS CÓDIGOS

### 1. Archivo JSON (Principal)

**Ruta:** `config/license.json`

Este archivo se crea automáticamente cuando se genera el primer código de activación.

**Estructura:**
```json
{
  "codigos_registrados": {
    "FINCA-ABCDE-12345-FGHIJ": {
      "usuario_id": 1,
      "fecha_generacion": "2025-12-10T14:30:00.123456",
      "valido": true
    },
    "FINCA-XYZAB-67890-KLMNO": {
      "usuario_id": 2,
      "fecha_generacion": "2025-12-11T10:15:00.654321",
      "valido": true
    }
  }
}
```

**Campos:**
- `codigo`: Clave única en formato `FINCA-XXXXX-XXXXX-XXXXX`
- `usuario_id`: ID del usuario al que pertenece el código
- `fecha_generacion`: Timestamp ISO 8601 de cuándo se generó
- `valido`: Boolean que indica si el código ya fue usado (false) o está disponible (true)

### 2. Base de Datos (Secundario)

**Tabla:** `licencia` en `src/database/fincafacil.db`

**Consulta SQL:**
```sql
SELECT codigo_activacion 
FROM licencia 
WHERE usuario_id = 1;
```

**Esquema de la tabla:**
```sql
CREATE TABLE licencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL UNIQUE,
    tipo_licencia TEXT NOT NULL,  -- 'PRUEBA' o 'PERMANENTE'
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_expiracion TIMESTAMP NOT NULL,
    codigo_activacion TEXT,  -- Código usado para activar (NULL si es prueba)
    estado TEXT NOT NULL,  -- 'ACTIVA', 'EXPIRADA', 'BLOQUEADA'
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

---

## 🔧 CÓMO GENERAR CÓDIGOS

### Opción 1: Desde Python (Recomendado)

Abre una terminal Python en la raíz del proyecto y ejecuta:

```python
from src.modules.utils.license_manager import LicenseManager

# Inicializar el gestor de licencias
lm = LicenseManager()

# Generar un código para un usuario específico
codigo = lm.generar_codigo_activacion(usuario_id=1)
print(f"Código generado: {codigo}")

# Ejemplo de salida:
# Código generado: FINCA-A7B3D-92F4E-C1H8K
```

**Parámetros:**
- `usuario_id` (int): ID del usuario en la base de datos

**Retorno:**
- String con el código en formato `FINCA-XXXXX-XXXXX-XXXXX`

### Opción 2: Desde un Script

Crea un archivo temporal `generar_codigo.py`:

```python
import sys
sys.path.insert(0, 'src')

from modules.utils.license_manager import LicenseManager

def generar_codigo_manual():
    lm = LicenseManager()
    usuario_id = int(input("Ingresa el ID del usuario: "))
    codigo = lm.generar_codigo_activacion(usuario_id)
    print("\n" + "="*50)
    print(f"CÓDIGO GENERADO: {codigo}")
    print("="*50)
    print(f"\nGuarda este código para el usuario ID {usuario_id}")
    print("El código ha sido registrado en config/license.json")

if __name__ == "__main__":
    generar_codigo_manual()
```

**Ejecutar:**
```bash
python generar_codigo.py
```

---

## 🔍 CÓMO ACCEDER A LOS CÓDIGOS

### Método 1: Leer el JSON directamente

```python
import json

# Leer todos los códigos registrados
with open('config/license.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Códigos registrados:")
for codigo, info in data['codigos_registrados'].items():
    print(f"  {codigo} -> Usuario ID: {info['usuario_id']}, Válido: {info['valido']}")
```

### Método 2: Consultar la base de datos

```python
import sqlite3

conn = sqlite3.connect('src/database/fincafacil.db')
cursor = conn.cursor()

# Ver todos los códigos activados
cursor.execute("""
    SELECT u.username, l.codigo_activacion, l.tipo_licencia, l.estado
    FROM licencia l
    JOIN usuarios u ON l.usuario_id = u.id
    WHERE l.codigo_activacion IS NOT NULL
""")

print("Códigos en uso:")
for row in cursor.fetchall():
    print(f"  Usuario: {row[0]}, Código: {row[1]}, Tipo: {row[2]}, Estado: {row[3]}")

conn.close()
```

### Método 3: Usar el LicenseManager

```python
from src.modules.utils.license_manager import LicenseManager

lm = LicenseManager()

# Obtener información de licencia de un usuario
usuario_id = 1
licencia = lm.obtener_licencia(usuario_id)

if licencia:
    print(f"Usuario ID: {usuario_id}")
    print(f"Tipo: {licencia['tipo_licencia']}")
    print(f"Estado: {licencia['estado']}")
    print(f"Código: {licencia.get('codigo_activacion', 'N/A')}")
    print(f"Expira: {licencia['fecha_expiracion']}")
```

---

## 🛠️ FORMATO DEL CÓDIGO

### Estructura
```
FINCA-XXXXX-XXXXX-XXXXX
```

- **Prefijo:** `FINCA-` (identificador del sistema)
- **Bloques:** 3 grupos de 5 caracteres alfanuméricos
- **Caracteres:** A-Z y 0-9 (excluye I, O, 0, 1 para evitar confusión)
- **Longitud total:** 23 caracteres (incluyendo guiones)

### Ejemplo de generación manual

```python
import random
import string

def generar_codigo_simple():
    chars = string.ascii_uppercase.replace('I', '').replace('O', '') + '23456789'
    bloques = [''.join(random.choices(chars, k=5)) for _ in range(3)]
    return f"FINCA-{'-'.join(bloques)}"

print(generar_codigo_simple())
# Salida: FINCA-K7B3D-92F4E-C8HJK
```

---

## ⚙️ FLUJO COMPLETO

### 1. Usuario solicita código (después de 6 meses)

El usuario contacta a:
- **Email:** jfburitica97@gmail.com
- **Teléfono:** 3013869653

### 2. Programador genera el código

```python
from src.modules.utils.license_manager import LicenseManager

lm = LicenseManager()
codigo = lm.generar_codigo_activacion(usuario_id=X)  # Reemplazar X con ID real
```

### 3. Programador envía el código al usuario

Enviar por email o mensaje el código generado.

### 4. Usuario activa la licencia

1. Abre FincaFácil
2. Va a **Ajustes → Estado de Licencia**
3. Hace clic en **"Activar Licencia"**
4. Ingresa el código recibido
5. La licencia se convierte en PERMANENTE (365 días desde activación)

### 5. Verificación

El sistema:
- Valida el código contra `config/license.json`
- Verifica que el usuario_id coincida
- Verifica que el código esté `valido: true`
- Actualiza la BD con el nuevo tipo de licencia
- Marca el código como `valido: false` para evitar reutilización

---

## 🚨 IMPORTANTE

### Seguridad
- Los códigos son de **un solo uso**
- Cada código está vinculado a un **usuario_id específico**
- No se puede usar el mismo código para múltiples usuarios
- Los códigos usados se marcan como `valido: false`

### Respaldo
- **Siempre respalda** `config/license.json` antes de modificarlo manualmente
- La base de datos también contiene registros de activación

### Regeneración
Si un código se pierde, NO se puede recuperar. Debes generar uno nuevo:

```python
lm = LicenseManager()
nuevo_codigo = lm.generar_codigo_activacion(usuario_id=X)
```

---

## 📞 SOPORTE

Si tienes dudas sobre la gestión de códigos:

- **Desarrollador:** Juan Felipe Buriticá
- **Email:** jfburitica97@gmail.com
- **Teléfono:** 3013869653

---

## 📝 HISTORIAL

- **v2.0** (Diciembre 2025): Sistema de licencias inicial con período de prueba de 6 meses
- Formato de código: `FINCA-XXXXX-XXXXX-XXXXX`
- Almacenamiento: JSON + SQLite
- Validación: Un solo uso por código

---

**FincaFácil v2.0 - Sistema de Licencias**  
*Última actualización: 10 de Diciembre de 2025*
