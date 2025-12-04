import pytest
from modules.utils.validators import animal_validator, DB_DISPONIBLE

# NOTA: Si la BD no está disponible (DB_DISPONIBLE False) las pruebas de unicidad
# se limitarán a validar formato; se marcan con skip condicional.

def test_peso_nacimiento_fuera_de_rango():
    datos = {"codigo": "ABC123", "peso_nacimiento": 5}  # menor al mínimo 10 para ternero
    ok, errores = animal_validator.validar_animal_completo(datos)
    assert not ok
    assert any("Peso nacimiento" in e for e in errores)

def test_peso_compra_fuera_de_rango():
    datos = {"codigo": "ABC124", "peso_compra": 10}  # menor al mínimo adulto 200
    ok, errores = animal_validator.validar_animal_completo(datos)
    assert not ok
    assert any("Peso compra" in e for e in errores)

def test_fecha_futura():
    from datetime import date, timedelta
    futura = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
    datos = {"codigo": "ABC125", "fecha_nacimiento": futura}
    ok, errores = animal_validator.validar_animal_completo(datos)
    assert not ok
    assert any("Fecha nacimiento" in e and "no puede ser futura" in e for e in errores)

@pytest.mark.skipif(not DB_DISPONIBLE, reason="BD no disponible para prueba de unicidad")
def test_codigo_duplicado(monkeypatch):
    # Simular existencia de código duplicado usando monkeypatch sobre get_db_connection
    from modules.utils.validators import get_db_connection
    import sqlite3

    def fake_conn():
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE animal (id INTEGER PRIMARY KEY, codigo TEXT)")
        conn.execute("INSERT INTO animal (codigo) VALUES ('DUP123')")
        return conn

    monkeypatch.setattr("modules.utils.validators.get_db_connection", lambda: fake_conn())

    datos = {"codigo": "DUP123"}
    ok, errores = animal_validator.validar_animal_completo(datos)
    assert not ok
    assert any("Arete" in e and "ya existe" in e for e in errores)
