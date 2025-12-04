import time

def test_app_startup_smoke():
    """Smoke test de inicio: crea la app, procesa unos ciclos y destruye.
    Se fuerza backend no interactivo de matplotlib para evitar hilos GUI pesados.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
    except Exception:
        pass

    from main import FincaFacilApp
    app = FincaFacilApp()
    try:
        app.withdraw()
    except Exception:
        pass
    # Procesar algunos ciclos para disparar callbacks iniciales
    for _ in range(3):
        app.update_idletasks()
        app.update()
        time.sleep(0.05)
    app.destroy()
