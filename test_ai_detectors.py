"""
Test FASE 3: AI Detectors
Runs anomaly and pattern detectors and prints results.
"""

from datetime import datetime

from src.services.ai_anomaly_detector import get_ai_anomaly_detector_service
from src.services.ai_pattern_detector import get_ai_pattern_detector_service


def run_tests():
    print("\n=== FASE 3 - AI DETECTORS TEST ===")

    # Anomaly detector
    try:
        anomaly_service = get_ai_anomaly_detector_service()
        results = anomaly_service.evaluar_anomalias(usuario_id=None, incluir_alertas=False)
        print(f"[Anomalies] {len(results)} resultados")
        for r in results[:5]:
            print(f"  - {r.metrica}: score={r.score} ({r.nivel}) → {r.explicacion}")
    except Exception as e:
        print(f"[ERROR] Anomaly detector: {e}")
        import traceback; traceback.print_exc()

    # Pattern detector
    try:
        pattern_service = get_ai_pattern_detector_service()
        insights = pattern_service.detectar_patrones(usuario_id=None, incluir_alertas=False)
        print(f"[Patterns] {len(insights)} insights")
        for i in insights[:5]:
            print(f"  - {i.tipo}/{i.metrica}: {i.nivel} → {i.descripcion}")
    except Exception as e:
        print(f"[ERROR] Pattern detector: {e}")
        import traceback; traceback.print_exc()

    print("=== TEST COMPLETED ===\n")


if __name__ == "__main__":
    run_tests()
