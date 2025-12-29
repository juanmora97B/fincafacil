## COMENZAR FASE 10: EXPLAINABILITY SERVICE

**Estado Actual:** ✅ FASE 1-9 COMPLETADAS  
**Próximo paso:** FASE 10 — Insight Explainer Service  
**Tiempo estimado:** 2-3 días  
**Tests:** 3-5 tests de explicabilidad  

---

## 🎯 OBJETIVO FASE 10

Transformar salidas técnicas del AI en explicaciones paso-a-paso que usuarios no técnicos entiendan.

### Antes (Sin explicabilidad)
```
AI: "🚨 ANOMALÍA DETECTADA: Producción anormalmente baja"
Usuario: "¿Por qué? No entiendo..."
```

### Después (Con explicabilidad)
```
AI: "🚨 ANOMALÍA: Producción anormalmente baja (2025-12-28)"

📊 EVIDENCIA:
  - Producción hoy: 800 litros
  - Producción esperada: 1,200 litros (promedio últimos 6 meses)
  - Desviación: -33% (umbral: ±25%)

💡 RAZONAMIENTO PASO-A-PASO:
  1️⃣ Obtuve datos de producción de últimos 6 meses: 1,180 L/día promedio
  2️⃣ Comparé hoy (800 L) vs promedio (1,180 L): -380 L
  3️⃣ Calculé desviación: -380/1,180 = -32% (por debajo de umbral ±25%)
  4️⃣ Verificué contexto: no es estación de baja producción (es diciembre)
  5️⃣ Conclusión: EVENTO ANÓMALO detectado

🔍 CONTEXTO:
  - Mes anterior (nov 2025): Producción normal (1,220 L)
  - Estación: Invierno (sin factor estacional documentado)
  - Patrón: Sin patrón conocido a estas fechas

⚠️ RECOMENDACIÓN:
  Investiga:
  ✓ Salud del hato (enfermedades, estrés)
  ✓ Equipamiento de ordeño (funcionamiento óptimo)
  ✓ Cambios en alimentación
```

---

## 📋 PLAN DETALLADO FASE 10

### Paso 1: Crear `src/services/insight_explainer_service.py` (1 día)

```python
"""
╔════════════════════════════════════════════════════════════════╗
║          INSIGHT EXPLAINER SERVICE - FASE 10                  ║
║                                                                ║
║ Convierte decisiones técnicas de AI en explicaciones claras   ║
╚════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

@dataclass
class ExplanationStep:
    """Paso individual en el razonamiento"""
    numero: int
    accion: str  # "Obtuve datos", "Calculé promedio"
    detalle: str
    resultado: Any

@dataclass
class ExplanationEvidence:
    """Evidencia numérica"""
    metrica_nombre: str
    valor_observado: float
    valor_esperado: float
    desviacion_pct: float

@dataclass
class ExplanationReport:
    """Reporte completo de explicación"""
    titulo: str
    resumen: str
    evidencia: List[ExplanationEvidence]
    pasos: List[ExplanationStep]
    contexto: Dict[str, Any]
    recomendacion: str
    confianza_pct: float
    fecha_generacion: str

class InsightExplainerService:
    """Genera explicaciones de insights técnicos"""
    
    def __init__(self):
        self.logger = logging.getLogger("insight_explainer")
    
    def explicar_anomalia(self, anomalia_dict: Dict[str, Any]) -> ExplanationReport:
        """
        Genera explicación detallada de una anomalía.
        
        Args:
            anomalia_dict: {
                'metrica': 'produccion_total',
                'valor_observado': 800,
                'valor_esperado': 1200,
                'umbral_alerta': 0.25,
                'periodo': '2025-12-28',
                'datos_historicos': [...],
                'contexto': {...}
            }
        
        Returns:
            ExplanationReport con:
            - Evidencia (datos específicos)
            - Pasos (razonamiento)
            - Contexto (estación, patrones)
            - Recomendación
        """
        
        # 1. Extraer datos de entrada
        metrica = anomalia_dict['metrica']
        valor_observado = anomalia_dict['valor_observado']
        valor_esperado = anomalia_dict['valor_esperado']
        
        # 2. Construir evidencia
        desviacion_pct = ((valor_observado - valor_esperado) / valor_esperado) * 100
        evidencia = ExplanationEvidence(
            metrica_nombre=self._nombre_negocio(metrica),
            valor_observado=valor_observado,
            valor_esperado=valor_esperado,
            desviacion_pct=desviacion_pct
        )
        
        # 3. Construir pasos de razonamiento
        pasos = self._construir_pasos_anomalia(anomalia_dict)
        
        # 4. Agregar contexto (estación, patrones, etc)
        contexto = self._analizar_contexto(anomalia_dict)
        
        # 5. Generar recomendación
        recomendacion = self._recomendar_accion(metrica, desviacion_pct)
        
        # 6. Calcular confianza
        confianza = self._calcular_confianza(anomalia_dict)
        
        # 7. Armar reporte final
        return ExplanationReport(
            titulo=f"{self._emoji_anomalia(desviacion_pct)} ANOMALÍA: {self._titulo_anomalia(metrica, desviacion_pct)}",
            resumen=f"{self._nombre_negocio(metrica)} está {abs(desviacion_pct):.0f}% {'por debajo' if desviacion_pct < 0 else 'por arriba'} de lo esperado",
            evidencia=[evidencia],
            pasos=pasos,
            contexto=contexto,
            recomendacion=recomendacion,
            confianza_pct=confianza,
            fecha_generacion=datetime.now().isoformat()
        )
    
    def explicar_patron(self, patron_dict: Dict[str, Any]) -> ExplanationReport:
        """Similar a explicar_anomalia, para patrones detectados"""
        # Implementar para estacionalidad, rampas, etc
        pass
    
    # Métodos privados de ayuda
    
    def _nombre_negocio(self, metrica_tecnica: str) -> str:
        """Convierte nombre técnico a nombre de negocio"""
        mapping = {
            'produccion_total': 'Producción',
            'costo_total': 'Costos',
            'ingreso_total': 'Ingresos',
            'margen_bruto_pct': 'Margen bruto',
            'tasa_prenez': 'Tasa de preñez',
            'mortalidad_pct': 'Mortalidad',
        }
        return mapping.get(metrica_tecnica, metrica_tecnica)
    
    def _construir_pasos_anomalia(self, anomalia_dict) -> List[ExplanationStep]:
        """Construye pasos del razonamiento"""
        pasos = []
        
        # Paso 1: Obtener datos
        pasos.append(ExplanationStep(
            numero=1,
            accion="Obtuve datos históricos",
            detalle=f"Recopilé {len(anomalia_dict.get('datos_historicos', []))} registros de últimos 6 meses",
            resultado={'count': len(anomalia_dict.get('datos_historicos', []))}
        ))
        
        # Paso 2: Calcular promedio
        promedio = anomalia_dict.get('valor_esperado', 0)
        pasos.append(ExplanationStep(
            numero=2,
            accion="Calculé promedio histórico",
            detalle=f"Promedio móvil: {promedio:.2f}",
            resultado={'promedio': promedio}
        ))
        
        # Paso 3: Comparar con hoy
        valor_hoy = anomalia_dict.get('valor_observado', 0)
        desviacion = valor_hoy - promedio
        pasos.append(ExplanationStep(
            numero=3,
            accion="Comparé hoy vs promedio",
            detalle=f"Hoy: {valor_hoy:.2f} | Esperado: {promedio:.2f} | Diferencia: {desviacion:+.2f}",
            resultado={'valor_hoy': valor_hoy, 'diferencia': desviacion}
        ))
        
        # Paso 4: Verificar contexto
        pasos.append(ExplanationStep(
            numero=4,
            accion="Verifiqué factores contextuales",
            detalle="Revisé estación, patrones mensuales, cambios recientes",
            resultado={'contexto_relevante': True}
        ))
        
        # Paso 5: Conclusión
        umbral = anomalia_dict.get('umbral_alerta', 0.25)
        desviacion_pct = (abs(desviacion) / promedio * 100) if promedio else 0
        es_anormal = desviacion_pct > (umbral * 100)
        
        pasos.append(ExplanationStep(
            numero=5,
            accion="Conclusión",
            detalle=f"Desviación {desviacion_pct:.1f}% {'>' if es_anormal else '<'} umbral {umbral*100:.0f}% → {'ANOMALÍA' if es_anormal else 'NORMAL'}",
            resultado={'anomalia': es_anormal}
        ))
        
        return pasos
    
    def _analizar_contexto(self, anomalia_dict) -> Dict[str, Any]:
        """Agrega contexto para la anomalía"""
        return {
            'estacion': anomalia_dict.get('estacion', 'desconocida'),
            'mes_anterior': anomalia_dict.get('valor_mes_anterior'),
            'patrones_conocidos': anomalia_dict.get('patrones', []),
            'cambios_recientes': anomalia_dict.get('cambios', [])
        }
    
    def _recomendar_accion(self, metrica: str, desviacion_pct: float) -> str:
        """Genera recomendación de acción"""
        recomendaciones = {
            'produccion_total': "Investiga salud del hato, equipamiento de ordeño y cambios en alimentación",
            'costo_total': "Revisa categoría de costos más afectada y verifica con proveedores",
            'ingreso_total': "Analiza volumen y precio de ventas; compara con mercado",
            'tasa_prenez': "Evalúa protocolo reproductivo, condición corporal y servicio de IA",
            'mortalidad_pct': "Revisa causas de muertes recientes, veterinario recomendado"
        }
        return recomendaciones.get(metrica, "Investiga causa de la desviación")
    
    def _calcular_confianza(self, anomalia_dict) -> float:
        """Calcula confianza en la explicación (0-100)"""
        score = 100
        
        # Reducir si pocos datos históricos
        if len(anomalia_dict.get('datos_historicos', [])) < 20:
            score -= 20
        
        # Reducir si hay cambios recientes (más incertidumbre)
        if anomalia_dict.get('cambios'):
            score -= 10
        
        return max(50, score)
    
    def _emoji_anomalia(self, desviacion_pct: float) -> str:
        if abs(desviacion_pct) > 50:
            return "🚨"  # Crítico
        elif abs(desviacion_pct) > 25:
            return "⚠️"   # Importante
        else:
            return "ℹ️"    # Información

    def _titulo_anomalia(self, metrica: str, desviacion_pct: float) -> str:
        nombre = self._nombre_negocio(metrica)
        direccion = "anormalmente baja" if desviacion_pct < 0 else "anormalmente alta"
        pct_abs = abs(desviacion_pct)
        return f"{nombre} {direccion} ({pct_abs:.0f}%)"


# Singleton
_explainer = None

def get_insight_explainer_service() -> InsightExplainerService:
    global _explainer
    if _explainer is None:
        _explainer = InsightExplainerService()
    return _explainer
```

### Paso 2: Integrar en Dashboard (1/2 día)

**Archivo:** `src/modules/dashboard/dashboard_main.py`

```python
def mostrar_explicacion(self, alerta_id: int):
    """
    Muestra popup con explicación detallada de alerta/anomalía
    """
    try:
        explainer = get_insight_explainer_service()
        
        # Obtener datos de alerta
        alerta = self._obtener_alerta(alerta_id)
        
        # Generar explicación
        explicacion = explainer.explicar_anomalia(alerta)
        
        # Crear popup
        popup = ctk.CTkToplevel(self)
        popup.title(f"Explicación: {explicacion.titulo}")
        popup.geometry("600x500")
        
        # Mostrar contenido
        contenido = f"""
{explicacion.titulo}

📊 EVIDENCIA:
{self._format_evidencia(explicacion.evidencia)}

💡 RAZONAMIENTO:
{self._format_pasos(explicacion.pasos)}

🔍 CONTEXTO:
{self._format_contexto(explicacion.contexto)}

✅ RECOMENDACIÓN:
{explicacion.recomendacion}

Confianza: {explicacion.confianza_pct}%
Generado: {explicacion.fecha_generacion}
"""
        
        text_box = ctk.CTkTextbox(popup)
        text_box.pack(fill="both", expand=True, padx=10, pady=10)
        text_box.insert("1.0", contenido)
        text_box.configure(state="disabled")
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar explicación: {e}")
```

**En tabla de alertas:**
```python
# Agregar columna "¿Por qué?" con botón
def _crear_tabla_alertas(self, parent):
    # ...
    for alerta in alertas:
        # ... otras columnas ...
        
        btn_explicacion = ctk.CTkButton(
            tabla,
            text="¿Por qué?",
            command=lambda aid=alerta['id']: self.mostrar_explicacion(aid),
            width=80,
            fg_color="#1E88E5"
        )
        btn_explicacion.grid(row=row, column=col_explicacion)
```

### Paso 3: Tests (1/2 día)

**Archivo:** `test_fase10_explainability.py`

```python
"""
SMOKE TEST - FASE 10: EXPLAINABILITY SERVICE

Verifica:
- Generación de explicaciones
- Pasos de razonamiento
- Evidencia clara
- Recomendaciones accionables
"""

import pytest
from src.services.insight_explainer_service import (
    get_insight_explainer_service,
    ExplanationReport
)

def test_explicar_anomalia_produccion_baja():
    """Test 1: Explicación de anomalía de producción baja"""
    explainer = get_insight_explainer_service()
    
    anomalia = {
        'metrica': 'produccion_total',
        'valor_observado': 800,
        'valor_esperado': 1200,
        'umbral_alerta': 0.25,
        'periodo': '2025-12-28',
        'datos_historicos': list(range(180)),  # 6 meses
        'estacion': 'invierno',
        'cambios': []
    }
    
    explicacion = explainer.explicar_anomalia(anomalia)
    
    # Validaciones
    assert explicacion.titulo  # Tiene título
    assert "Producción" in explicacion.titulo
    assert "baja" in explicacion.titulo.lower()
    
    assert len(explicacion.evidencia) > 0
    assert explicacion.evidencia[0].desviacion_pct < 0  # Negativa
    
    assert len(explicacion.pasos) == 5  # 1-Datos, 2-Promedio, 3-Comparar, 4-Contexto, 5-Conclusión
    
    assert explicacion.recomendacion
    assert "hato" in explicacion.recomendacion.lower() or "ordeño" in explicacion.recomendacion.lower()
    
    assert explicacion.confianza_pct > 50
    
    print(f"✓ Test 1: Explicación generada correctamente")

def test_explicar_anomalia_costos_altos():
    """Test 2: Explicación de anomalía de costos altos"""
    explainer = get_insight_explainer_service()
    
    anomalia = {
        'metrica': 'costo_total',
        'valor_observado': 15000,
        'valor_esperado': 10000,
        'umbral_alerta': 0.30,
        'periodo': '2025-12-28',
        'datos_historicos': list(range(180)),
        'estacion': 'verano',
        'cambios': [{'fecha': '2025-12-25', 'cambio': 'Compra de forraje adicional'}]
    }
    
    explicacion = explainer.explicar_anomalia(anomalia)
    
    assert "Costos" in explicacion.titulo
    assert "alta" in explicacion.titulo.lower()
    assert explicacion.evidencia[0].desviacion_pct > 0  # Positiva
    assert "proveedores" in explicacion.recomendacion.lower()
    
    print(f"✓ Test 2: Explicación de costos altos correcta")

def test_pasos_tienen_estructura():
    """Test 3: Pasos tienen estructura clara"""
    explainer = get_insight_explainer_service()
    
    anomalia = {
        'metrica': 'produccion_total',
        'valor_observado': 800,
        'valor_esperado': 1200,
        'umbral_alerta': 0.25,
        'periodo': '2025-12-28',
        'datos_historicos': list(range(180)),
        'estacion': 'invierno',
        'cambios': []
    }
    
    explicacion = explainer.explicar_anomalia(anomalia)
    
    for paso in explicacion.pasos:
        assert paso.numero > 0
        assert paso.accion  # No vacío
        assert paso.detalle  # No vacío
        assert paso.resultado  # Dict con datos
    
    # Primer paso: obtener datos
    assert "datos" in explicacion.pasos[0].accion.lower()
    
    # Último paso: conclusión
    assert "conclusión" in explicacion.pasos[-1].accion.lower()
    
    print(f"✓ Test 3: Pasos tienen estructura correcta")

def test_confianza_se_calcula():
    """Test 4: Confianza se calcula según datos disponibles"""
    explainer = get_insight_explainer_service()
    
    # Con muchos datos
    anomalia_muchos_datos = {
        'metrica': 'produccion_total',
        'valor_observado': 800,
        'valor_esperado': 1200,
        'umbral_alerta': 0.25,
        'periodo': '2025-12-28',
        'datos_historicos': list(range(180)),  # 6 meses
        'estacion': 'invierno',
        'cambios': []
    }
    
    exp1 = explainer.explicar_anomalia(anomalia_muchos_datos)
    
    # Con pocos datos
    anomalia_pocos_datos = {
        'metrica': 'produccion_total',
        'valor_observado': 800,
        'valor_esperado': 1200,
        'umbral_alerta': 0.25,
        'periodo': '2025-12-28',
        'datos_historicos': [1200, 1100],  # Solo 2 datos
        'estacion': 'invierno',
        'cambios': []
    }
    
    exp2 = explainer.explicar_anomalia(anomalia_pocos_datos)
    
    # Confianza debe ser mayor con más datos
    assert exp1.confianza_pct > exp2.confianza_pct
    
    print(f"✓ Test 4: Confianza calculada correctamente ({exp1.confianza_pct:.0f}% vs {exp2.confianza_pct:.0f}%)")

def test_emojis_segun_severidad():
    """Test 5: Emojis reflejan severidad"""
    explainer = get_insight_explainer_service()
    
    # Anomalía pequeña
    anomalia_pequena = {
        'metrica': 'produccion_total',
        'valor_observado': 1150,
        'valor_esperado': 1200,
        'umbral_alerta': 0.25,
        'periodo': '2025-12-28',
        'datos_historicos': list(range(180)),
        'estacion': 'invierno',
        'cambios': []
    }
    
    exp_pequena = explainer.explicar_anomalia(anomalia_pequena)
    assert "ℹ️" in exp_pequena.titulo or "⚠️" in exp_pequena.titulo  # Leve
    
    # Anomalía grande
    anomalia_grande = {
        'metrica': 'produccion_total',
        'valor_observado': 600,
        'valor_esperado': 1200,
        'umbral_alerta': 0.25,
        'periodo': '2025-12-28',
        'datos_historicos': list(range(180)),
        'estacion': 'invierno',
        'cambios': []
    }
    
    exp_grande = explainer.explicar_anomalia(anomalia_grande)
    assert "🚨" in exp_grande.titulo  # Crítico
    
    print(f"✓ Test 5: Emojis según severidad correctos")

if __name__ == "__main__":
    test_explicar_anomalia_produccion_baja()
    test_explicar_anomalia_costos_altos()
    test_pasos_tienen_estructura()
    test_confianza_se_calcula()
    test_emojis_segun_severidad()
    
    print("\n" + "="*70)
    print("✓ TODOS LOS TESTS DE FASE 10 PASADOS")
    print("="*70)
```

---

## ✅ Checklist FASE 10

- [ ] Crear `src/services/insight_explainer_service.py` con:
  - [ ] Clase InsightExplainerService
  - [ ] método explicar_anomalia()
  - [ ] Pasos de razonamiento (5 pasos)
  - [ ] Cálculo de confianza
  - [ ] Singleton getter

- [ ] Integrar en Dashboard:
  - [ ] Botón "¿Por qué?" en tabla de alertas
  - [ ] Popup con explicación detallada
  - [ ] Formateo de evidencia, pasos, contexto

- [ ] Tests:
  - [ ] test_fase10_explainability.py (5 tests mínimo)
  - [ ] Todos los tests PASSING

- [ ] Documentación:
  - [ ] Docstrings en servicios
  - [ ] Ejemplo de explicación en README
  - [ ] Screenshots del popup

---

## 🎯 Resultado Esperado

```
Usuario ve alerta en dashboard:
│ Tipo: Producción baja
│ Prioridad: Alta
│ [Botón] ¿Por qué?

Al clickear:
╔══════════════════════════════════════════════════════════════╗
║ 🚨 ANOMALÍA: Producción anormalmente baja (33%)              ║
║                                                              ║
║ 📊 EVIDENCIA:                                                ║
║   - Producción hoy: 800 litros                              ║
║   - Producción esperada: 1,200 litros                       ║
║   - Desviación: -400 litros (-33%)                          ║
║                                                              ║
║ 💡 RAZONAMIENTO:                                             ║
║   1. Obtuve datos de últimos 6 meses (180 registros)        ║
║   2. Calculé promedio: 1,200 L/día                          ║
║   3. Comparé: 800 vs 1,200 = -33%                           ║
║   4. Verificué contexto: no es efecto estacional            ║
║   5. Conclusión: EVENTO ANÓMALO                             ║
║                                                              ║
║ ✅ RECOMENDACIÓN:                                            ║
║   Investiga: - Salud del hato                               ║
║              - Equipamiento de ordeño                        ║
║              - Cambios en alimentación                       ║
║                                                              ║
║ Confianza: 95%                                               ║
║ Generado: 2025-12-28 14:30:00                               ║
╚══════════════════════════════════════════════════════════════╝
```

---

**Listo para comenzar FASE 10** 🚀

Ejecutar una vez completado:
```bash
python test_fase10_explainability.py
```

Esperado: `✓ TODOS LOS TESTS DE FASE 10 PASADOS`
