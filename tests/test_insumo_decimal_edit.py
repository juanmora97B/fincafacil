import sqlite3
import os
import pytest

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()

def test_insert_insumo_decimal(conn):
    cursor = conn.cursor()
    # Insert minimal insumo (campos obligatorios según código)
    cursor.execute("""
        INSERT INTO insumo (codigo, nombre, categoria, unidad_medida, stock_actual, stock_minimo, precio_unitario, id_finca, estado, responsable, stock_bodega)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'TDEC001', 'Test Decimal', 'Prueba', 'UND', 3.0, 1.5, 2.75, 1, 'Disponible', 'Bodega', 3.0
    ))
    conn.commit()

    cursor.execute("SELECT precio_unitario, stock_minimo, stock_actual FROM insumo WHERE codigo = ?", ('TDEC001',))
    row = cursor.fetchone()
    assert row is not None
    precio_unitario, stock_minimo, stock_actual = row
    assert abs(precio_unitario - 2.75) < 1e-6, 'precio_unitario no se guardó como decimal'
    assert abs(stock_minimo - 1.5) < 1e-6, 'stock_minimo no se guardó como decimal'
    assert abs(stock_actual - 3.0) < 1e-6, 'stock_actual no se guardó como decimal'


def test_update_insumo_decimal(conn):
    cursor = conn.cursor()
    # Actualizar insumo previo
    cursor.execute("""
        UPDATE insumo SET precio_unitario = ?, stock_minimo = ?, stock_actual = ? WHERE codigo = ?
    """, (5.35, 2.25, 10.0, 'TDEC001'))
    conn.commit()

    cursor.execute("SELECT precio_unitario, stock_minimo, stock_actual FROM insumo WHERE codigo = ?", ('TDEC001',))
    row = cursor.fetchone()
    assert row is not None
    precio_unitario, stock_minimo, stock_actual = row
    assert abs(precio_unitario - 5.35) < 1e-6, 'precio_unitario no se actualizó correctamente'
    assert abs(stock_minimo - 2.25) < 1e-6, 'stock_minimo no se actualizó correctamente'
    assert abs(stock_actual - 10.0) < 1e-6, 'stock_actual no se actualizó correctamente'
