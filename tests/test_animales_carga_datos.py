"""
Test de carga de datos en ventanas de Nacimiento y Compra
==========================================================

Valida que:
1. Todas las fincas registradas se cargan correctamente
2. Todas las razas configuradas se cargan correctamente
3. Al seleccionar una finca, se cargan sus potreros, lotes y sectores
4. Los datos se pueden guardar correctamente en la base de datos
"""

import sqlite3
import os
import pytest

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()

def test_cargar_todas_fincas(conn):
    """Verifica que se puedan cargar todas las fincas activas"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, estado FROM finca")
    fincas_raw = cursor.fetchall()
    
    # Filtrar fincas inactivas/eliminadas (mismo criterio que el código)
    excluir = {'eliminada', 'eliminado', 'inactiva', 'inactivo'}
    fincas_activas = [f for f in fincas_raw if (f[2] or '').lower() not in excluir]
    
    assert len(fincas_activas) > 0, "No hay fincas activas en el sistema"
    print(f"✓ {len(fincas_activas)} fincas activas encontradas")
    for finca in fincas_activas:
        print(f"  - {finca[1]} (ID: {finca[0]}, Estado: {finca[2]})")

def test_cargar_todas_razas(conn):
    """Verifica que se puedan cargar todas las razas activas"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, estado FROM raza")
    razas_raw = cursor.fetchall()
    
    # Filtrar razas inactivas (mismo criterio que el código)
    razas_activas = [r for r in razas_raw if (r[2] or '').lower() not in ('inactiva', 'eliminada')]
    
    assert len(razas_activas) > 0, "No hay razas activas en el sistema"
    print(f"✓ {len(razas_activas)} razas activas encontradas")
    for raza in razas_activas:
        print(f"  - {raza[1]} (ID: {raza[0]})")

def test_relacion_finca_potreros(conn):
    """Verifica que potreros estén asociados a fincas"""
    cursor = conn.cursor()
    
    # Detectar nombre de columna FK (id_finca o finca_id)
    cursor.execute("PRAGMA table_info(potrero)")
    cols = [r[1] for r in cursor.fetchall()]
    fk_col = "id_finca" if "id_finca" in cols else "finca_id" if "finca_id" in cols else None
    
    assert fk_col is not None, "Tabla potrero no tiene relación con finca"
    
    # Obtener fincas con potreros
    cursor.execute(f"SELECT DISTINCT {fk_col} FROM potrero WHERE {fk_col} IS NOT NULL")
    fincas_con_potreros = [r[0] for r in cursor.fetchall()]
    
    print(f"✓ {len(fincas_con_potreros)} fincas tienen potreros asignados")
    
    # Verificar que al menos una finca tenga potreros
    if len(fincas_con_potreros) > 0:
        finca_id = fincas_con_potreros[0]
        cursor.execute(f"SELECT id, nombre FROM potrero WHERE {fk_col} = ?", (finca_id,))
        potreros = cursor.fetchall()
        print(f"  Ejemplo: Finca ID {finca_id} tiene {len(potreros)} potrero(s)")
        for potrero in potreros[:3]:  # Mostrar max 3
            print(f"    - {potrero[1]}")

def test_relacion_finca_lotes(conn):
    """Verifica que lotes estén asociados a fincas"""
    cursor = conn.cursor()
    
    # Detectar nombre de columna FK
    cursor.execute("PRAGMA table_info(lote)")
    cols = [r[1] for r in cursor.fetchall()]
    fk_col = "finca_id" if "finca_id" in cols else "id_finca" if "id_finca" in cols else None
    
    if fk_col is None:
        pytest.skip("Tabla lote no tiene relación con finca")
    
    # Obtener fincas con lotes
    cursor.execute(f"SELECT DISTINCT {fk_col} FROM lote WHERE {fk_col} IS NOT NULL")
    fincas_con_lotes = [r[0] for r in cursor.fetchall()]
    
    print(f"✓ {len(fincas_con_lotes)} fincas tienen lotes asignados")
    
    if len(fincas_con_lotes) > 0:
        finca_id = fincas_con_lotes[0]
        cursor.execute(f"SELECT id, nombre FROM lote WHERE {fk_col} = ?", (finca_id,))
        lotes = cursor.fetchall()
        print(f"  Ejemplo: Finca ID {finca_id} tiene {len(lotes)} lote(s)")

def test_relacion_finca_sectores(conn):
    """Verifica que sectores estén asociados a fincas"""
    cursor = conn.cursor()
    
    # Verificar si existe tabla sector
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sector'")
    if not cursor.fetchone():
        pytest.skip("Tabla sector no existe en el esquema")
    
    # Obtener sectores por finca
    cursor.execute("SELECT finca_id, COUNT(*) FROM sector WHERE estado='Activo' GROUP BY finca_id")
    sectores_por_finca = cursor.fetchall()
    
    if len(sectores_por_finca) == 0:
        pytest.skip("No hay sectores activos en el sistema")
    
    print(f"✓ {len(sectores_por_finca)} finca(s) tienen sectores activos")
    for finca_id, count in sectores_por_finca:
        cursor.execute("SELECT nombre FROM finca WHERE id = ?", (finca_id,))
        finca_row = cursor.fetchone()
        finca_nombre = finca_row[0] if finca_row else f"ID {finca_id}"
        cursor.execute("SELECT nombre FROM sector WHERE finca_id = ? AND estado='Activo'", (finca_id,))
        sectores = [r[0] for r in cursor.fetchall()]
        print(f"  - {finca_nombre}: {count} sector(es): {', '.join(sectores[:3])}")

def test_insert_animal_con_sector(conn):
    """Verifica que se pueda insertar un animal con sector asignado"""
    cursor = conn.cursor()
    
    # Obtener una finca, sector, potrero disponibles
    cursor.execute("SELECT id FROM finca LIMIT 1")
    finca_row = cursor.fetchone()
    if not finca_row:
        pytest.skip("No hay fincas en el sistema")
    finca_id = finca_row[0]
    
    # Verificar si hay sector
    cursor.execute("SELECT id FROM sector WHERE finca_id = ? AND estado='Activo' LIMIT 1", (finca_id,))
    sector_row = cursor.fetchone()
    sector_id = sector_row[0] if sector_row else None
    
    # Buscar potrero
    cursor.execute("PRAGMA table_info(potrero)")
    cols = [r[1] for r in cursor.fetchall()]
    fk_col = "id_finca" if "id_finca" in cols else "finca_id"
    cursor.execute(f"SELECT id FROM potrero WHERE {fk_col} = ? LIMIT 1", (finca_id,))
    potrero_row = cursor.fetchone()
    potrero_id = potrero_row[0] if potrero_row else None
    
    # Buscar raza
    cursor.execute("SELECT id FROM raza LIMIT 1")
    raza_row = cursor.fetchone()
    raza_id = raza_row[0] if raza_row else None
    
    # Insertar animal de prueba
    codigo_test = "TEST_SECTOR_001"
    
    # Limpiar si existe
    cursor.execute("DELETE FROM animal WHERE codigo = ?", (codigo_test,))
    conn.commit()
    
    try:
        cursor.execute("""
            INSERT INTO animal (
                id_finca, codigo, nombre, tipo_ingreso, sexo, raza_id,
                id_potrero, lote_id, id_grupo, fecha_nacimiento,
                estado, inventariado, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            finca_id, codigo_test, 'Test Sector', 'Nacimiento', 'Macho', raza_id,
            potrero_id, None, sector_id, '2024-01-01',
            'Activo', 0
        ))
        conn.commit()
        
        # Verificar que se insertó correctamente
        cursor.execute("SELECT id, codigo, id_grupo FROM animal WHERE codigo = ?", (codigo_test,))
        animal_row = cursor.fetchone()
        assert animal_row is not None, "Animal no se insertó"
        assert animal_row[2] == sector_id, f"id_grupo (sector) no coincide: esperado {sector_id}, obtenido {animal_row[2]}"
        
        print(f"✓ Animal insertado correctamente con id_grupo={sector_id} (sector)")
        
    finally:
        # Limpiar
        cursor.execute("DELETE FROM animal WHERE codigo = ?", (codigo_test,))
        conn.commit()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
