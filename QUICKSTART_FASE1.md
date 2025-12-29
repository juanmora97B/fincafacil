# 🚀 QUICKSTART - FASE 1 SEED DE DATOS

## ⚡ En 30 Segundos

### Opción 1: Interfaz Gráfica (Recomendado)

```
1. Abrir FincaFácil
2. Menú: Ajustes → Herramientas de Desarrollo
3. Click: "🌱 Cargar Datos de Prueba"
4. Confirmar
5. ✅ Datos listos en 2-5 segundos
```

### Opción 2: Terminal

```bash
# Opción A: Sin limpiar
python -m database.seed_data

# Opción B: Limpiar primero
python -m database.seed_data --clear
```

### Opción 3: Código Python

```python
from database.seed_data import run_seed

# Ejecutar
success = run_seed(clear_before_seed=False, mode="dev")
print("✅ OK" if success else "❌ Error")
```

---

## 📊 Qué Se Carga

- ✅ 40 animales (diferentes sexos, edades, estados)
- ✅ 3 fincas y 7 potreros
- ✅ 12 servicios reproductivos (10 gestantes)
- ✅ ~900 registros de leche (60 días)
- ✅ 12-15 tratamientos veterinarios
- ✅ 125+ pesajes históricos
- ✅ 6 insumos + 30 movimientos
- ✅ 7 herramientas

**Total: +1,300 registros** ✅

---

## ✅ Verificar Datos

### Desde UI (Ajustes → Herramientas Dev)
```
[🔍 Validar Integridad de BD]
[📊 Ver Estadísticas]
```

### Desde Terminal
```bash
python scripts/validate_seed.py
```

---

## 🧹 Limpiar Datos

```bash
# Opción 1: Desde terminal
python -m database.seed_data --clear

# Opción 2: Desde UI
Ajustes → Herramientas Dev → "🗑️ Limpiar + Recargar"
```

---

## 📈 Comprobar en Dashboard

Después de cargar, el Dashboard debe mostrar:
- **Total: ~40 animales**
- **Activos: ~30**
- **Gestantes: ~10**
- **Leche hoy: 20-30L** (si es hora de ordeño)

---

## 🐛 Si Hay Problemas

```bash
# 1. Revisar logs
tail -f logs/fincafacil.log

# 2. Validar BD
python scripts/validate_seed.py

# 3. Limpiar + recargar
python -m database.seed_data --clear
```

---

## 📝 Documentación Completa

- **docs/FASE1_SEED_DATOS_PRUEBA.md** - Guía detallada + checklist
- **FASE1_IMPLEMENTACION.md** - Técnico/arquitectura
- **FASE1_RESUMEN_EJECUTIVO.md** - Overview ejecutivo

---

**¡Listo para validar FincaFácil con datos realistas!** 🌱✅
