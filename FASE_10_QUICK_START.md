# FASE 10: Quick Start Guide

## 🚀 Verificar que FASE 10 está funcionando

### 1. Ejecutar Smoke Tests

```bash
cd c:\Users\lenovo\Desktop\FincaFacil
python test_fase10_explainability.py
```

**Resultado esperado:** 6/6 tests PASSING ✅

```
======================================================================
TOTAL: 6/6 tests exitosos ✅

✓ test_explicar_anomalia_produccion_baja
✓ test_explicar_anomalia_costos_altos
✓ test_pasos_estructura
✓ test_confianza_segun_datos
✓ test_emojis_segun_severidad
✓ test_explicar_patron
```

---

## 💡 Usar InsightExplainerService en tu Código

### Opción 1: Generar Explicación para Anomalía

```python
from src.services.insight_explainer_service import get_insight_explainer_service

# Obtener instancia (singleton)
explainer = get_insight_explainer_service()

# Datos de anomalía
anomalia = {
    'metrica': 'produccion_total',
    'valor_observado': 600,          # Litros de hoy
    'valor_esperado': 1200,          # Promedio histórico
    'umbral_alerta': 0.25,           # 25% de desviación
    'periodo': '2025-12-28',
    'datos_historicos': [1100, 1150, 1200, 1250, ...],  # 180+ valores
    'estacion': 'invierno',          # Contexto
    'cambios': []                    # Cambios recientes (opcional)
}

# Generar explicación
explicacion = explainer.explicar_anomalia(anomalia)

# Acceder a campos
print(f"Título: {explicacion.titulo}")                # ⚠️ ANOMALÍA: Producción anormalmente baja (50%)
print(f"Resumen: {explicacion.resumen}")              # Texto explicativo
print(f"Confianza: {explicacion.confianza_pct}%")     # 80-85%
print(f"Recomendación: {explicacion.recomendacion}")  # Acción sugierida

# Acceder a 5 pasos
for paso in explicacion.pasos:
    print(f"Paso {paso.numero}: {paso.accion}")
    print(f"  Detalle: {paso.detalle}")

# Acceder a evidencia
for evidencia in explicacion.evidencia:
    print(f"{evidencia.metrica_nombre}: {evidencia.valor_observado:.1f} vs {evidencia.valor_esperado:.1f} ({evidencia.desviacion_pct:+.1f}%)")
```

### Opción 2: Generar Explicación para Patrón

```python
patron = {
    'tipo': 'estacionalidad',
    'nombre': 'Producción baja en invierno',
    'periodo': '2025-12-28',
    'frecuencia': 'mensual',
    'confianza_patron': 0.87,
    'datos_historicos': [...]
}

explicacion = explainer.explicar_patron(patron)
```

---

## 🎨 Mostrar en Dashboard

### Opción 1: Usar PopupExplicacion (Recomendado)

```python
from src.modules.dashboard.explicacion_popup import mostrar_explicacion_alerta

# En el callback del botón "¿Por qué?"
def boton_por_que_click(alerta_id, titulo, explicacion_dict):
    mostrar_explicacion_alerta(
        parent=root_widget,
        alerta_id=alerta_id,
        titulo=titulo,
        explicacion_dict=explicacion_dict
    )
```

### Opción 2: Usar con IntegrationModule

```python
from src.modules.dashboard.explicaciones_integracion import obtener_explicacion_para_alerta
from src.modules.dashboard.explicacion_popup import mostrar_explicacion_alerta

# Obtener explicación (con cache automático)
alerta_dict = {
    'id': 'alerta_123',
    'tipo': 'anomalia_productiva',
    'metrica': 'produccion_total',
    'valor_observado': 600,
    'valor_esperado': 1200,
    'periodo': '2025-12-28',
    'datos_historicos': [...]
}

explicacion = obtener_explicacion_para_alerta(alerta_dict)

if explicacion:
    mostrar_explicacion_alerta(
        parent=root_widget,
        alerta_id='alerta_123',
        titulo='ANOMALÍA DETECTADA',
        explicacion_dict=explicacion
    )
```

---

## 📊 Estructura de ExplanationReport

```python
@dataclass
class ExplanationReport:
    titulo: str              # "⚠️ ANOMALÍA: Producción anormalmente baja (50%)"
    resumen: str             # "Producción 50% bajo promedio..."
    evidencia: list          # [ExplanationEvidence(...)]
    pasos: list              # [ExplanationStep(...)] - 5 pasos
    contexto: dict           # {"estacion": "invierno", "mes_anterior": "...", ...}
    recomendacion: str       # "Investiga salud del hato, equipamiento..."
    confianza_pct: int       # 50-95%
    fecha_generacion: str    # "2025-12-28T17:02:18"
```

### ExplanationStep
```python
@dataclass
class ExplanationStep:
    numero: int              # 1-5
    accion: str             # "Obtuve datos históricos"
    detalle: str            # "180 días de datos"
    resultado: dict         # {"datos_cantidad": 180, ...}
```

### ExplanationEvidence
```python
@dataclass
class ExplanationEvidence:
    metrica_nombre: str      # "Producción Total"
    valor_observado: float   # 600.0
    valor_esperado: float    # 1200.0
    desviacion_pct: float    # -50.0
```

---

## 🎯 Cálculo de Confianza

**Fórmula:**
```
confianza = 80%  (base)
          - 15%  (si < 20 datos históricos)
          - 10%  (si cambios recientes)
          + 5%   (si contexto abundante)
          
Rango final: 50% - 95%
```

**Ejemplo:**
```python
# 180 datos + sin cambios + contexto: 80% + 5% = 85%
# 5 datos + cambios recientes: 80% - 15% - 10% = 55% (mínimo 50%)
```

---

## 🎨 Emojis Automáticos

| Desviación | Emoji | Significado | Acciones |
|-----------|-------|-------------|---------:|
| > 50% | 🚨 | CRÍTICA | Intervención inmediata |
| 25-50% | ⚠️ | IMPORTANTE | Investigar |
| < 25% | ℹ️ | INFORMATIVA | Monitorear |

---

## 🧪 Ejemplo Completo

```python
from src.services.insight_explainer_service import get_insight_explainer_service
from src.modules.dashboard.explicacion_popup import mostrar_explicacion_alerta
import tkinter as tk

# Crear ventana ejemplo
root = tk.Tk()
root.title("FASE 10: Explainability Demo")

# Crear explainer
explainer = get_insight_explainer_service()

# Datos de anomalía
anomalia_produccion_baja = {
    'metrica': 'produccion_total',
    'valor_observado': 600,
    'valor_esperado': 1200,
    'umbral_alerta': 0.25,
    'periodo': '2025-12-28',
    'datos_historicos': list(range(180)),  # 180 valores
    'estacion': 'invierno',
    'cambios': []
}

# Generar explicación
explicacion = explainer.explicar_anomalia(anomalia_produccion_baja)

# Convertir a dict para UI
explicacion_dict = {
    "titulo": explicacion.titulo,
    "resumen": explicacion.resumen,
    "evidencia": [
        {
            "metrica_nombre": e.metrica_nombre,
            "valor_observado": e.valor_observado,
            "valor_esperado": e.valor_esperado,
            "desviacion_pct": e.desviacion_pct
        } for e in explicacion.evidencia
    ],
    "pasos": [
        {
            "numero": p.numero,
            "accion": p.accion,
            "detalle": p.detalle,
            "resultado": p.resultado
        } for p in explicacion.pasos
    ],
    "contexto": explicacion.contexto,
    "recomendacion": explicacion.recomendacion,
    "confianza_pct": explicacion.confianza_pct,
    "fecha_generacion": explicacion.fecha_generacion
}

# Crear botón para ver explicación
def mostrar_explicacion():
    mostrar_explicacion_alerta(
        parent=root,
        alerta_id="demo_123",
        titulo="ANOMALÍA DETECTADA",
        explicacion_dict=explicacion_dict
    )

boton = tk.Button(root, text="Ver Explicación (¿Por qué?)", command=mostrar_explicacion)
boton.pack(pady=20)

root.mainloop()
```

**Resultado:** Popup con 5 pasos, evidencia, contexto y recomendación ✅

---

## 🔍 Troubleshooting

### Error: "InsightExplainerService not initialized"
```python
# Solución: Importar correctamente
from src.services.insight_explainer_service import get_insight_explainer_service
explainer = get_insight_explainer_service()
```

### PopupExplicacion no muestra emojis correctamente
```python
# Verificar encoding de terminal
# PowerShell en Windows necesita UTF-8
# Alternativa: Usar keywords en lugar de emojis
```

### Cache de explicaciones no se limpia
```python
from src.modules.dashboard.explicaciones_integracion import limpiar_cache_explicaciones
limpiar_cache_explicaciones()
```

---

## 📚 Archivos Relacionados

- `src/services/insight_explainer_service.py` - Servicio principal
- `src/modules/dashboard/explicacion_popup.py` - UI popup
- `src/modules/dashboard/explicaciones_integracion.py` - Integración + cache
- `src/modules/dashboard/alertas_ui.py` - Componentes UI auxiliares
- `test_fase10_explainability.py` - Tests
- `FASE_10_EXPLAINABILITY_COMPLETADA.md` - Documentación completa

---

## ✅ Checklist de Implementación

Si estás integrando FASE 10 en tu módulo:

- [ ] Importar `get_insight_explainer_service`
- [ ] Llamar `explicar_anomalia()` o `explicar_patron()`
- [ ] Convertir resultado a dict (si necesario para UI)
- [ ] Mostrar `PopupExplicacion` en botón "¿Por qué?"
- [ ] Verificar que confianza está en rango 50-95%
- [ ] Validar que 5 pasos aparecen correctamente
- [ ] Probar con datos reales de BD

---

**¿Preguntas?** Ver FASE_10_EXPLAINABILITY_COMPLETADA.md para documentación completa.

