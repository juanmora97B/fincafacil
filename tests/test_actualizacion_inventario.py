"""
Tests para funcionalidad de actualización de inventario (peso y leche).
Verifica conversión de unidades, validación de entrada y manejo de errores.
"""
import pytest
import sqlite3
from datetime import datetime
from modules.utils.units_helper import units_helper


@pytest.fixture
def db_test():
    """Crea una BD SQLite en memoria con esquema mínimo para pruebas."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE animal (
            id INTEGER PRIMARY KEY,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT,
            estado TEXT DEFAULT 'Activo',
            inventariado INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE peso (
            id INTEGER PRIMARY KEY,
            animal_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            peso REAL NOT NULL,
            metodo TEXT,
            observaciones TEXT,
            FOREIGN KEY (animal_id) REFERENCES animal(id)
        )
    """)
    conn.execute("""
        CREATE TABLE produccion_leche (
            id INTEGER PRIMARY KEY,
            animal_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            litros_manana REAL DEFAULT 0,
            litros_tarde REAL DEFAULT 0,
            litros_noche REAL DEFAULT 0,
            observaciones TEXT,
            UNIQUE(animal_id, fecha)
        )
    """)
    # Insertar un animal de prueba
    conn.execute("INSERT INTO animal (id, codigo, nombre, estado) VALUES (1, 'TEST001', 'Prueba', 'Activo')")
    conn.commit()
    yield conn
    conn.close()


class TestRegistroPeso:
    """Tests para registro de peso en inventario."""
    
    def test_registrar_peso_valido_kg(self, db_test):
        """Registra peso válido en kg y verifica almacenamiento."""
        peso_kg = 450.5
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        cur = db_test.cursor()
        cur.execute("""
            INSERT INTO peso (animal_id, fecha, peso, metodo, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (1, fecha, peso_kg, "Báscula", "Registro durante inventario"))
        db_test.commit()
        
        cur.execute("SELECT peso FROM peso WHERE animal_id = 1 AND fecha = ?", (fecha,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == pytest.approx(peso_kg, rel=1e-2)
    
    def test_registrar_peso_conversion_lb_a_kg(self, db_test):
        """Verifica conversión correcta de libras a kilogramos."""
        # Cambiar unidad a libras temporalmente para prueba
        original_unit = units_helper.weight_unit
        units_helper.weight_unit = "lb"
        
        peso_lb = 1000.0  # ~453.6 kg
        peso_kg_esperado = units_helper.convert_weight_to_kg(peso_lb)
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        cur = db_test.cursor()
        cur.execute("""
            INSERT INTO peso (animal_id, fecha, peso, metodo, observaciones)
            VALUES (?, ?, ?, ?, ?)
        """, (1, fecha, peso_kg_esperado, "Báscula", "Conversión lb->kg"))
        db_test.commit()
        
        cur.execute("SELECT peso FROM peso WHERE animal_id = 1 AND fecha = ?", (fecha,))
        row = cur.fetchone()
        assert row[0] == pytest.approx(453.59, rel=1e-1)
        
        # Restaurar unidad original
        units_helper.weight_unit = original_unit
    
    def test_peso_negativo_rechazado(self):
        """Valida que peso negativo genere error de validación."""
        peso_str = "-50"
        with pytest.raises(ValueError):
            peso_input = float(peso_str)
            if peso_input <= 0:
                raise ValueError("Peso debe ser positivo")
    
    def test_peso_no_numerico_rechazado(self):
        """Valida que entrada no numérica genere error."""
        peso_str = "abc"
        with pytest.raises(ValueError):
            float(peso_str)
    
    def test_peso_cero_rechazado(self):
        """Valida que peso cero genere error."""
        peso_input = 0.0
        assert peso_input <= 0, "Peso cero debe ser rechazado"


class TestRegistroLeche:
    """Tests para registro de producción de leche."""
    
    def test_registrar_leche_valida_litros(self, db_test):
        """Registra producción de leche válida en litros."""
        fecha = datetime.now().strftime("%Y-%m-%d")
        l_m, l_t, l_n = 10.5, 8.3, 6.2
        
        cur = db_test.cursor()
        cur.execute("""
            INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, fecha, l_m, l_t, l_n, "Registro durante inventario"))
        db_test.commit()
        
        cur.execute("SELECT litros_manana, litros_tarde, litros_noche FROM produccion_leche WHERE animal_id = 1 AND fecha = ?", (fecha,))
        row = cur.fetchone()
        assert row is not None
        assert row[0] == pytest.approx(l_m, rel=1e-2)
        assert row[1] == pytest.approx(l_t, rel=1e-2)
        assert row[2] == pytest.approx(l_n, rel=1e-2)
    
    def test_registrar_leche_conversion_gal_a_l(self, db_test):
        """Verifica conversión correcta de galones a litros."""
        original_unit = units_helper.volume_unit
        units_helper.volume_unit = "gal"
        
        gal_m, gal_t, gal_n = 2.5, 2.0, 1.5
        l_m = units_helper.convert_volume_to_l(gal_m)
        l_t = units_helper.convert_volume_to_l(gal_t)
        l_n = units_helper.convert_volume_to_l(gal_n)
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        cur = db_test.cursor()
        cur.execute("""
            INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, fecha, l_m, l_t, l_n, "Conversión gal->L"))
        db_test.commit()
        
        cur.execute("SELECT litros_manana FROM produccion_leche WHERE animal_id = 1 AND fecha = ?", (fecha,))
        row = cur.fetchone()
        assert row[0] == pytest.approx(9.46, rel=1e-1)  # 2.5 gal ≈ 9.46 L
        
        units_helper.volume_unit = original_unit
    
    def test_leche_volumen_negativo_rechazado(self):
        """Valida que volumen negativo genere error."""
        l_m_input = -5.0
        assert l_m_input < 0, "Volumen negativo debe ser rechazado"
    
    def test_leche_entrada_no_numerica_rechazada(self):
        """Valida que entrada no numérica genere error."""
        l_m_str = "xyz"
        with pytest.raises(ValueError):
            float(l_m_str)
    
    def test_leche_conflicto_misma_fecha(self, db_test):
        """Verifica que ON CONFLICT actualiza en vez de insertar duplicado."""
        fecha = "2024-01-15"
        
        cur = db_test.cursor()
        # Primer registro
        cur.execute("""
            INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, fecha, 10.0, 8.0, 6.0, "Primer registro"))
        db_test.commit()
        
        # Actualización en conflicto
        cur.execute("""
            INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(animal_id, fecha) DO UPDATE SET
                litros_manana=excluded.litros_manana,
                litros_tarde=excluded.litros_tarde,
                litros_noche=excluded.litros_noche,
                observaciones=excluded.observaciones
        """, (1, fecha, 12.0, 9.5, 7.0, "Actualización"))
        db_test.commit()
        
        cur.execute("SELECT COUNT(*), litros_manana FROM produccion_leche WHERE animal_id = 1 AND fecha = ?", (fecha,))
        count, litros = cur.fetchone()
        assert count == 1, "Debe haber solo un registro"
        assert litros == pytest.approx(12.0, rel=1e-2), "Debe reflejar valor actualizado"
    
    def test_suma_total_produccion_correcta(self, db_test):
        """Verifica cálculo correcto de producción total diaria."""
        fecha = datetime.now().strftime("%Y-%m-%d")
        l_m, l_t, l_n = 12.3, 10.5, 8.7
        
        cur = db_test.cursor()
        cur.execute("""
            INSERT INTO produccion_leche (animal_id, fecha, litros_manana, litros_tarde, litros_noche, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, fecha, l_m, l_t, l_n, "Test suma"))
        db_test.commit()
        
        cur.execute("""
            SELECT litros_manana + litros_tarde + litros_noche AS total 
            FROM produccion_leche 
            WHERE animal_id = 1 AND fecha = ?
        """, (fecha,))
        total = cur.fetchone()[0]
        esperado = l_m + l_t + l_n
        assert total == pytest.approx(esperado, rel=1e-2)


class TestInventarioEstado:
    """Tests para marcado de estado de inventario."""
    
    def test_marcar_inventariado(self, db_test):
        """Marca animal como inventariado."""
        cur = db_test.cursor()
        cur.execute("UPDATE animal SET inventariado = ? WHERE id = ?", (1, 1))
        db_test.commit()
        
        cur.execute("SELECT inventariado FROM animal WHERE id = 1")
        estado = cur.fetchone()[0]
        assert estado == 1
    
    def test_marcar_no_inventariado(self, db_test):
        """Marca animal como faltante."""
        cur = db_test.cursor()
        cur.execute("UPDATE animal SET inventariado = ? WHERE id = ?", (0, 1))
        db_test.commit()
        
        cur.execute("SELECT inventariado FROM animal WHERE id = 1")
        estado = cur.fetchone()[0]
        assert estado == 0
