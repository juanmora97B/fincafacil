"""
Test de flujo completo: Nacimiento/Compra → Guardado → Inventario
===================================================================

Valida que los animales guardados desde las ventanas de Nacimiento y Compra
aparezcan correctamente en el Inventario General con todos sus datos.
"""

import sqlite3
import os
import pytest
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'fincafacil.db')

@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB_PATH)
    yield c
    c.close()

def test_guardar_animal_nacimiento_completo(conn):
    """Simula guardar un animal por nacimiento con todos los campos"""
    cursor = conn.cursor()
    
    # Obtener IDs necesarios
    cursor.execute("SELECT id FROM finca WHERE nombre LIKE '%prado%' LIMIT 1")
    finca_row = cursor.fetchone()
    assert finca_row, "No se encontró Finca El Prado"
    finca_id = finca_row[0]
    
    cursor.execute("SELECT id FROM raza WHERE nombre LIKE '%ceb%' LIMIT 1")
    raza_row = cursor.fetchone()
    assert raza_row, "No se encontró raza Cebú"
    raza_id = raza_row[0]
    
    # Detectar FK para potrero
    cursor.execute("PRAGMA table_info(potrero)")
    cols = [r[1] for r in cursor.fetchall()]
    fk_col = "id_finca" if "id_finca" in cols else "finca_id"
    
    cursor.execute(f"SELECT id FROM potrero WHERE {fk_col} = ? LIMIT 1", (finca_id,))
    potrero_row = cursor.fetchone()
    potrero_id = potrero_row[0] if potrero_row else None
    
    cursor.execute("SELECT id FROM sector WHERE finca_id = ? AND estado='Activo' LIMIT 1", (finca_id,))
    sector_row = cursor.fetchone()
    sector_id = sector_row[0] if sector_row else None
    
    # Código único para test
    codigo_test = f"NAC_TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Limpiar si existe
    cursor.execute("DELETE FROM animal WHERE codigo = ?", (codigo_test,))
    conn.commit()
    
    try:
        # Insertar animal simulando guardado desde ventana Nacimiento
        cursor.execute("""
            INSERT INTO animal (
                id_finca, codigo, nombre, tipo_ingreso, sexo, raza_id,
                id_potrero, lote_id, id_grupo, fecha_nacimiento,
                peso_nacimiento, id_padre, id_madre, tipo_concepcion,
                salud, estado, inventariado, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            finca_id, codigo_test, 'Animal Test Nacimiento', 'Nacimiento', 'Macho', raza_id,
            potrero_id, None, sector_id, '2024-11-01',
            45.5, None, None, 'Monta',
            'Sano', 'Activo', 0
        ))
        conn.commit()
        
        # Verificar que se guardó correctamente
        cursor.execute("""
            SELECT a.codigo, a.nombre, a.tipo_ingreso, a.sexo, 
                   f.nombre as finca, r.nombre as raza,
                   p.nombre as potrero, s.nombre as sector,
                   a.estado, a.salud
            FROM animal a
            LEFT JOIN finca f ON a.id_finca = f.id
            LEFT JOIN raza r ON a.raza_id = r.id
            LEFT JOIN potrero p ON a.id_potrero = p.id
            LEFT JOIN sector s ON a.id_grupo = s.id
            WHERE a.codigo = ?
        """, (codigo_test,))
        
        row = cursor.fetchone()
        assert row is not None, "Animal no se guardó en la base de datos"
        
        codigo, nombre, tipo_ingreso, sexo, finca, raza, potrero, sector, estado, salud = row
        
        # Validaciones
        assert codigo == codigo_test, f"Código incorrecto: {codigo}"
        assert nombre == 'Animal Test Nacimiento', f"Nombre incorrecto: {nombre}"
        assert tipo_ingreso == 'Nacimiento', f"Tipo ingreso incorrecto: {tipo_ingreso}"
        assert sexo == 'Macho', f"Sexo incorrecto: {sexo}"
        assert finca is not None, "Finca no se asoció correctamente"
        assert raza is not None, "Raza no se asoció correctamente"
        assert estado == 'Activo', f"Estado incorrecto: {estado}"
        assert salud == 'Sano', f"Salud incorrecta: {salud}"
        
        print(f"\n✅ Animal por Nacimiento guardado correctamente:")
        print(f"   Código: {codigo}")
        print(f"   Nombre: {nombre}")
        print(f"   Finca: {finca}")
        print(f"   Raza: {raza}")
        print(f"   Potrero: {potrero or 'N/A'}")
        print(f"   Sector: {sector or 'N/A'}")
        print(f"   Estado: {estado}")
        
    finally:
        # Limpiar
        cursor.execute("DELETE FROM animal WHERE codigo = ?", (codigo_test,))
        conn.commit()

def test_guardar_animal_compra_completo(conn):
    """Simula guardar un animal por compra con todos los campos"""
    cursor = conn.cursor()
    
    # Obtener IDs necesarios
    cursor.execute("SELECT id FROM finca WHERE nombre LIKE '%leon%' LIMIT 1")
    finca_row = cursor.fetchone()
    assert finca_row, "No se encontró Finca El León"
    finca_id = finca_row[0]
    
    cursor.execute("SELECT id FROM raza WHERE nombre LIKE '%holstein%' LIMIT 1")
    raza_row = cursor.fetchone()
    assert raza_row, "No se encontró raza Holstein"
    raza_id = raza_row[0]
    
    # Detectar FK para potrero
    cursor.execute("PRAGMA table_info(potrero)")
    cols = [r[1] for r in cursor.fetchall()]
    fk_col = "id_finca" if "id_finca" in cols else "finca_id"
    
    cursor.execute(f"SELECT id FROM potrero WHERE {fk_col} = ? LIMIT 1", (finca_id,))
    potrero_row = cursor.fetchone()
    potrero_id = potrero_row[0] if potrero_row else None
    
    cursor.execute("SELECT id FROM sector WHERE finca_id = ? AND estado='Activo' LIMIT 1", (finca_id,))
    sector_row = cursor.fetchone()
    sector_id = sector_row[0] if sector_row else None
    
    # Código único para test
    codigo_test = f"COMP_TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Limpiar si existe
    cursor.execute("DELETE FROM animal WHERE codigo = ?", (codigo_test,))
    conn.commit()
    
    try:
        # Insertar animal simulando guardado desde ventana Compra
        cursor.execute("""
            INSERT INTO animal (
                id_finca, codigo, nombre, tipo_ingreso, sexo, raza_id,
                id_potrero, lote_id, id_grupo, fecha_nacimiento, fecha_compra,
                peso_compra, precio_compra, id_vendedor,
                salud, estado, inventariado, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            finca_id, codigo_test, 'Animal Test Compra', 'Compra', 'Hembra', raza_id,
            potrero_id, None, sector_id, '2023-05-15', '2024-11-01',
            380.0, 2500000.0, None,
            'Sano', 'Activo', 0
        ))
        conn.commit()
        
        # Verificar que se guardó correctamente con JOIN
        cursor.execute("""
            SELECT a.codigo, a.nombre, a.tipo_ingreso, a.sexo, 
                   f.nombre as finca, r.nombre as raza,
                   p.nombre as potrero, s.nombre as sector,
                   a.precio_compra, a.peso_compra,
                   a.estado, a.salud
            FROM animal a
            LEFT JOIN finca f ON a.id_finca = f.id
            LEFT JOIN raza r ON a.raza_id = r.id
            LEFT JOIN potrero p ON a.id_potrero = p.id
            LEFT JOIN sector s ON a.id_grupo = s.id
            WHERE a.codigo = ?
        """, (codigo_test,))
        
        row = cursor.fetchone()
        assert row is not None, "Animal no se guardó en la base de datos"
        
        codigo, nombre, tipo_ingreso, sexo, finca, raza, potrero, sector, precio, peso, estado, salud = row
        
        # Validaciones
        assert codigo == codigo_test, f"Código incorrecto: {codigo}"
        assert nombre == 'Animal Test Compra', f"Nombre incorrecto: {nombre}"
        assert tipo_ingreso == 'Compra', f"Tipo ingreso incorrecto: {tipo_ingreso}"
        assert sexo == 'Hembra', f"Sexo incorrecto: {sexo}"
        assert finca is not None, "Finca no se asoció correctamente"
        assert raza is not None, "Raza no se asoció correctamente"
        assert precio == 2500000.0, f"Precio incorrecto: {precio}"
        assert peso == 380.0, f"Peso incorrecto: {peso}"
        assert estado == 'Activo', f"Estado incorrecto: {estado}"
        
        print(f"\n✅ Animal por Compra guardado correctamente:")
        print(f"   Código: {codigo}")
        print(f"   Nombre: {nombre}")
        print(f"   Finca: {finca}")
        print(f"   Raza: {raza}")
        print(f"   Potrero: {potrero or 'N/A'}")
        print(f"   Sector: {sector or 'N/A'}")
        print(f"   Precio: ${precio:,.0f}")
        print(f"   Peso: {peso} kg")
        print(f"   Estado: {estado}")
        
    finally:
        # Limpiar
        cursor.execute("DELETE FROM animal WHERE codigo = ?", (codigo_test,))
        conn.commit()

def test_inventario_muestra_animales_correctamente(conn):
    """Verifica que el inventario pueda consultar animales con todos sus datos relacionados"""
    cursor = conn.cursor()
    
    # Query similar a la que usa el módulo de inventario
    cursor.execute("""
        SELECT 
            a.codigo,
            a.nombre,
            f.nombre as finca,
            r.nombre as raza,
            a.sexo,
            a.estado,
            a.tipo_ingreso,
            p.nombre as potrero,
            s.nombre as sector
        FROM animal a
        LEFT JOIN finca f ON a.id_finca = f.id
        LEFT JOIN raza r ON a.raza_id = r.id
        LEFT JOIN potrero p ON a.id_potrero = p.id
        LEFT JOIN sector s ON a.id_grupo = s.id
        WHERE a.estado = 'Activo'
        LIMIT 5
    """)
    
    animales = cursor.fetchall()
    
    if len(animales) == 0:
        pytest.skip("No hay animales activos en la base de datos para validar inventario")
    
    print(f"\n✅ Inventario General muestra {len(animales)} animales (primeros 5):")
    print("=" * 100)
    
    for animal in animales:
        codigo, nombre, finca, raza, sexo, estado, tipo_ingreso, potrero, sector = animal
        print(f"   {codigo:15s} | {finca or 'N/A':20s} | {raza or 'N/A':15s} | {sexo:6s} | {tipo_ingreso:10s}")
    
    # Validar que al menos un animal tenga finca y raza asignadas
    animales_con_datos = [a for a in animales if a[2] is not None and a[3] is not None]
    assert len(animales_con_datos) > 0, "No hay animales con finca y raza asignadas correctamente"
    
    print(f"\n✅ {len(animales_con_datos)}/{len(animales)} animales tienen finca y raza correctamente asignadas")

def test_validar_todas_fincas_disponibles(conn):
    """Valida que todas las fincas activas estén disponibles para selección"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre, estado FROM finca WHERE estado != 'Inactiva'")
    fincas = cursor.fetchall()
    
    assert len(fincas) >= 2, f"Se esperaban al menos 2 fincas, se encontraron {len(fincas)}"
    
    nombres_fincas = [f[1].lower() for f in fincas]
    assert any('prado' in n for n in nombres_fincas), "No se encontró Finca El Prado"
    assert any('leon' in n or 'león' in n for n in nombres_fincas), "No se encontró Finca El León"
    
    print(f"\n✅ Validación de Fincas:")
    for finca in fincas:
        print(f"   ID: {finca[0]:3d} | Nombre: {finca[1]:30s} | Estado: {finca[2]}")

def test_validar_todas_razas_disponibles(conn):
    """Valida que todas las razas activas estén disponibles para selección"""
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre, estado FROM raza WHERE estado = 'Activa' OR estado IS NULL")
    razas = cursor.fetchall()
    
    assert len(razas) >= 10, f"Se esperaban al menos 10 razas, se encontraron {len(razas)}"
    
    nombres_razas = [r[1].lower() for r in razas]
    assert any('ceb' in n for n in nombres_razas), "No se encontró raza Cebú"
    assert any('holstein' in n for n in nombres_razas), "No se encontró raza Holstein"
    
    print(f"\n✅ Validación de Razas activas: {len(razas)} encontradas")
    print(f"   Incluye: {', '.join([r[1] for r in razas[:10]])}")
    if len(razas) > 10:
        print(f"   ... y {len(razas) - 10} más")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
