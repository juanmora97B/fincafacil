"""
Módulo de carga de datos de prueba realistas para FincaFácil
Fase 1: Seed de datos completo para validación integral del sistema

Características:
- Genera datos coherentes entre tablas (FKs válidas)
- Respeta soft delete y estados realistas
- Transacciones seguras por bloque
- Logging detallado por módulo
- Modo desarrollo (sin comprometer producción)
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import random
import string

from src.database.database import get_db_connection, get_db_path_safe

logger = logging.getLogger(__name__)


class SeedDataGenerator:
    """Generador centralizado de datos de prueba realistas."""
    
    def __init__(self, clear_before_seed: bool = False):
        """
        Inicializa el generador.
        
        Args:
            clear_before_seed: Si True, limpia datos previos antes de insertar
        """
        self.clear_before_seed = clear_before_seed
        self.db_path = get_db_path_safe()
        self.stats = {}
        
        # Cache de IDs inseridos para relaciones
        self.fincas: Dict[str, int] = {}
        self.razas: Dict[str, int] = {}
        self.potreros: Dict[str, int] = {}
        self.lotes: Dict[str, int] = {}
        self.animales: Dict[str, int] = {}
        self.vendedores: Dict[str, int] = {}
        self.insumos: Dict[str, int] = {}
        self.herramientas: Dict[str, int] = {}
        self.empleados: Dict[str, int] = {}
        self.servicios: Dict[str, int] = {}
        
    # ==================== UTILIDADES ====================
    
    @contextmanager
    def transaction(self):
        """Context manager para transacciones seguras."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            yield conn
            conn.commit()
            logger.info("Transacción completada exitosamente")
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en transacción: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _random_codigo(self, prefix: str = "TEST", length: int = 6) -> str:
        """Genera código único aleatorio."""
        chars = string.ascii_uppercase + string.digits
        return f"{prefix}-{''.join(random.choices(chars, k=length))}"
    
    def _random_date(self, days_back: int = 365) -> str:
        """Genera fecha aleatoria en los últimos N días."""
        delta = random.randint(0, days_back)
        date = datetime.now() - timedelta(days=delta)
        return date.strftime("%Y-%m-%d")
    
    def _random_datetime(self) -> str:
        """Genera timestamp actual."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_insert(self, table: str, count: int):
        """Registra inserción en log."""
        self.stats[table] = self.stats.get(table, 0) + count
        logger.info(f"✓ {table}: {count} registros insertados ({self.stats[table]} total)")
    
    # ==================== LIMPIEZA DE DATOS ====================
    
    def clear_data(self):
        """Limpia todos los datos (mantiene esquema) en orden de FKs."""
        if not self.clear_before_seed:
            return
        
        logger.info("🗑️  Limpiando datos previos...")
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Orden inverso de FKs (dependencias primero)
                tables_order = [
                    'muerte', 'diagnostico_evento', 'tratamiento', 'produccion_leche',
                    'peso', 'movimiento', 'servicio', 'reproduccion', 'comentario',
                    'reubicacion', 'historial_reubicaciones',
                    'mantenimiento_herramienta', 'herramienta',
                    'movimiento_insumo', 'insumo',
                    'animal', 'movimiento',
                    'inventario_animales',
                    'potrero', 'lote', 'finca',
                    'raza', 'vendedor'
                ]
                
                for table in tables_order:
                    cur.execute(f"DELETE FROM {table}")
                    count = cur.rowcount
                    if count > 0:
                        logger.info(f"  - {table}: {count} registros eliminados")
                
                # Reset auto_increment (SQLite)
                cur.execute("DELETE FROM sqlite_sequence")
                
        except Exception as e:
            logger.error(f"Error limpiando datos: {e}")
            raise
    
    # ==================== RAZAS ====================
    
    def seed_razas(self):
        """Inserta razas ganaderas realistas."""
        logger.info("📍 Insertando razas...")
        
        razas_data = [
            ("HOL", "Holstein", "Lechero", "Raza lechera holandesa de alta producción"),
            ("JAR", "Jersey", "Lechero", "Raza pequeña lechera, buena composición"),
            ("JAG", "Guernsey", "Lechero", "Lechera con buena adaptabilidad"),
            ("SIM", "Simmental", "Doble Propósito", "Carne y leche, versátil"),
            ("BRH", "Brahman", "Carne", "Carne, rústica y resistente"),
            ("ANG", "Angus", "Carne", "Carne de excelente calidad"),
            ("HER", "Hereford", "Carne", "Carne rústica y rustic"),
            ("CEV", "Cebú", "Carne", "Adaptada a climas tropicales"),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                for codigo, nombre, tipo, desc in razas_data:
                    cur.execute(
                        """
                        INSERT INTO raza (codigo, nombre, tipo_ganado, descripcion, estado)
                        VALUES (?, ?, ?, ?, 'Activa')
                        """,
                        (codigo, nombre, tipo, desc)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.razas[codigo] = last_id
                
                self._log_insert("raza", len(razas_data))
        except Exception as e:
            logger.error(f"Error insertando razas: {e}")
            raise
    
    # ==================== FINCAS ====================
    
    def seed_fincas(self):
        """Inserta fincas ficticias."""
        logger.info("📍 Insertando fincas...")
        
        fincas_data = [
            ("F001", "La Esperanza", "Juan Pérez", "Valle del Cauca", 150.5),
            ("F002", "San Miguel", "María García", "Antioquia", 200.0),
            ("F003", "Los Llanos", "Carlos López", "Córdoba", 350.0),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                for codigo, nombre, prop, ubicacion, area in fincas_data:
                    cur.execute(
                        """
                        INSERT INTO finca (codigo, nombre, propietario, ubicacion, area_hectareas, estado)
                        VALUES (?, ?, ?, ?, ?, 'Activo')
                        """,
                        (codigo, nombre, prop, ubicacion, area)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.fincas[codigo] = last_id
                
                self._log_insert("finca", len(fincas_data))
        except Exception as e:
            logger.error(f"Error insertando fincas: {e}")
            raise
    
    # ==================== POTREROS ====================
    
    def seed_potreros(self):
        """Inserta potreros asignados a fincas."""
        logger.info("📍 Insertando potreros...")
        
        potreros_data = [
            ("F001", "P001", "Potrero Norte", "Brahaquiareo", 25.0, 100),
            ("F001", "P002", "Potrero Sur", "Brahaquiareo", 30.0, 120),
            ("F001", "P003", "Potrero Este", "Kikuyo", 20.0, 80),
            ("F002", "P004", "Potrero A", "Brahaquiareo", 40.0, 180),
            ("F002", "P005", "Potrero B", "Brahaquiareo", 35.0, 150),
            ("F003", "P006", "Potrero Nuevo", "Brahaquiareo", 60.0, 250),
            ("F003", "P007", "Potrero Viejo", "Kikuyo", 50.0, 200),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                for finca_cod, potrero_cod, nombre, pasto, area, cap in potreros_data:
                    finca_id = self.fincas.get(finca_cod)
                    if not finca_id:
                        logger.warning(f"Finca {finca_cod} no encontrada, skipping potrero")
                        continue
                    
                    cur.execute(
                        """
                        INSERT INTO potrero (codigo, id_finca, nombre, tipo_pasto, area_hectareas, capacidad_maxima, estado)
                        VALUES (?, ?, ?, ?, ?, ?, 'Activo')
                        """,
                        (potrero_cod, finca_id, nombre, pasto, area, cap)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.potreros[potrero_cod] = last_id
                
                self._log_insert("potrero", len(potreros_data))
        except Exception as e:
            logger.error(f"Error insertando potreros: {e}")
            raise
    
    # ==================== LOTES ====================
    
    def seed_lotes(self):
        """Inserta lotes (agrupaciones de animales)."""
        logger.info("📍 Insertando lotes...")
        
        lotes_data = [
            ("F001", "L001", "Hembras Lecheras", "Grupo de hembras en ordeño"),
            ("F001", "L002", "Machos de Venta", "Terneros para engorde"),
            ("F002", "L003", "Madres", "Hembras gestantes"),
            ("F003", "L004", "Terneras", "Hembras jóvenes"),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                for finca_cod, lote_cod, nombre, desc in lotes_data:
                    finca_id = self.fincas.get(finca_cod)
                    if not finca_id:
                        logger.warning(f"Finca {finca_cod} no encontrada, skipping lote")
                        continue
                    
                    cur.execute(
                        """
                        INSERT INTO lote (codigo, finca_id, nombre, descripcion, estado)
                        VALUES (?, ?, ?, ?, 'Activo')
                        """,
                        (lote_cod, finca_id, nombre, desc)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.lotes[lote_cod] = last_id
                
                self._log_insert("lote", len(lotes_data))
        except Exception as e:
            logger.error(f"Error insertando lotes: {e}")
            raise
    
    # ==================== VENDEDORES ====================
    
    def seed_vendedores(self):
        """Inserta vendedores (para compras de animales)."""
        logger.info("📍 Insertando vendedores...")
        
        vendedores_data = [
            ("Ganadería Central", "Juan Vendedor", "3001234567"),
            ("Reprodutores Ltda", "María Santos", "3002345678"),
            ("Hacienda Los Pinos", "Carlos Gómez", "3003456789"),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                for nombre, contacto, tel in vendedores_data:
                    cur.execute(
                        """
                        INSERT INTO vendedor (nombre, contacto, telefono, estado)
                        VALUES (?, ?, ?, 'Activo')
                        """,
                        (nombre, contacto, tel)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.vendedores[nombre] = last_id
                
                self._log_insert("vendedor", len(vendedores_data))
        except Exception as e:
            logger.error(f"Error insertando vendedores: {e}")
            raise
    
    # ==================== ANIMALES ====================
    
    def seed_animales(self, count: int = 40):
        """Inserta animales con características realistas."""
        logger.info(f"📍 Insertando {count} animales...")
        
        sexos = ["Hembra", "Macho"]
        estados = ["Activo", "Vendido", "Muerto"]
        colores = ["Negro", "Rojo", "Blanco", "Pinto", "Gris"]
        tipos_ingreso = ["Compra", "Nacimiento", "Transferencia"]
        
        razas_list = list(self.razas.values())
        fincas_list = list(self.fincas.values())
        potreros_list = list(self.potreros.values())
        lotes_list = list(self.lotes.values())
        vendedores_list = list(self.vendedores.values())
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                for i in range(count):
                    sexo = random.choice(sexos)
                    estado = random.choice(estados)
                    
                    # Datos realistas
                    codigo = f"ANI-{i+1:04d}"
                    nombre = random.choice([
                        "Bessie", "Luna", "Star", "Daisy", "Molly", "Bonita", 
                        "Negra", "Blanca", "Marta", "Rosa", "Bella"
                    ]) if sexo == "Hembra" else random.choice([
                        "Rocky", "Max", "Thor", "Duke", "Bruno", "Simón"
                    ])
                    
                    fecha_nac = self._random_date(365 * 3)  # Hasta 3 años atrás
                    edad_dias = (datetime.now() - datetime.strptime(fecha_nac, "%Y-%m-%d")).days
                    peso_nac = random.uniform(25, 45)
                    peso_actual = peso_nac + (edad_dias / 365) * random.uniform(200, 400)
                    
                    # Si es vendido/muerto, fue hace poco
                    if estado == "Vendido":
                        fecha_venta = (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
                    elif estado == "Muerto":
                        fecha_muerte = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")
                    
                    cur.execute(
                        """
                        INSERT INTO animal (
                            id_finca, codigo, nombre, sexo, raza_id, id_potrero, lote_id,
                            fecha_nacimiento, peso_nacimiento, peso_compra, color, estado,
                            tipo_ingreso, tipo_concepcion
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            random.choice(fincas_list),  # finca
                            codigo,
                            nombre,
                            sexo,
                            random.choice(razas_list),  # raza
                            random.choice(potreros_list),  # potrero
                            random.choice(lotes_list),  # lote
                            fecha_nac,
                            peso_nac,
                            peso_actual,
                            random.choice(colores),
                            estado,
                            random.choice(tipos_ingreso),
                            "Natural"
                        )
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.animales[codigo] = last_id
                
                self._log_insert("animal", count)
        except Exception as e:
            logger.error(f"Error insertando animales: {e}")
            raise
    
    # ==================== REGISTROS DE MUERTE ====================
    
    def seed_muertes(self):
        """Inserta registros de muertes para animales con estado 'Muerto'."""
        logger.info("📍 Insertando registros de muerte...")
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Buscar animales muertos
                cur.execute("SELECT id, fecha_actualizacion FROM animal WHERE estado='Muerto'")
                muertos = cur.fetchall()
                
                for animal in muertos:
                    animal_id = animal[0] if isinstance(animal, sqlite3.Row) else animal[0]
                    
                    # Generar fecha de muerte (hace poco)
                    fecha_muerte = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime("%Y-%m-%d")
                    
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO muerte (animal_id, fecha, causa, diagnostico_presuntivo)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            animal_id,
                            fecha_muerte,
                            random.choice(["Enfermedad", "Accidente", "Vejez", "Complicación"]),
                            random.choice(["Mastitis", "Cólico", "Neumonía", "Falla cardíaca"])
                        )
                    )
                
                count = cur.rowcount
                self._log_insert("muerte", count)
        except Exception as e:
            logger.error(f"Error insertando muertes: {e}")
            raise
    
    # ==================== REPRODUCCIÓN ====================
    
    def seed_reproduccion(self):
        """Inserta datos de reproducción (servicios y gestaciones)."""
        logger.info("📍 Insertando datos de reproducción...")
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Obtener hembras activas
                cur.execute("""
                    SELECT id FROM animal 
                    WHERE sexo='Hembra' AND estado='Activo' 
                    LIMIT 15
                """)
                hembras = [row[0] for row in cur.fetchall()]
                
                # Obtener machos activos
                cur.execute("""
                    SELECT id FROM animal 
                    WHERE sexo='Macho' AND estado='Activo' 
                    LIMIT 5
                """)
                machos = [row[0] for row in cur.fetchall()]
                
                if not hembras or not machos:
                    logger.warning("No hay suficientes hembras o machos para reproducción")
                    return
                
                servicios_count = 0
                for hembra_id in hembras[:12]:  # 12 servicios
                    macho_id = random.choice(machos)
                    
                    # Servicio hace 60-90 días
                    fecha_servicio = (datetime.now() - timedelta(days=random.randint(60, 90))).strftime("%Y-%m-%d")
                    fecha_parto_est = (datetime.strptime(fecha_servicio, "%Y-%m-%d") + timedelta(days=280)).strftime("%Y-%m-%d")
                    
                    tipo_servicio = random.choice(["Monta Natural", "Inseminación Artificial"])
                    
                    cur.execute(
                        """
                        INSERT INTO servicio (
                            id_hembra, id_macho, fecha_servicio, tipo_servicio, 
                            estado, fecha_parto_estimada
                        ) VALUES (?, ?, ?, ?, 'Gestante', ?)
                        """,
                        (hembra_id, macho_id, fecha_servicio, tipo_servicio, fecha_parto_est)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.servicios[f"SRV-{servicios_count}"] = last_id
                    servicios_count += 1
                
                self._log_insert("servicio", servicios_count)
        except Exception as e:
            logger.error(f"Error insertando datos de reproducción: {e}")
            raise
    
    # ==================== PARTOS Y NACIMIENTOS ====================
    
    def seed_partos(self):
        """Inserta partos simulados con crías."""
        logger.info("📍 Insertando partos y nacimientos...")
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Obtener servicios que pueden haber parido
                cur.execute("""
                    SELECT id, id_hembra FROM servicio 
                    WHERE estado='Gestante' AND fecha_parto_estimada <= ?
                    LIMIT 5
                """, (datetime.now().strftime("%Y-%m-%d"),))
                servicios = cur.fetchall()
                
                if not servicios:
                    logger.info("  No hay servicios listos para registrar parto")
                    return
                
                partos_count = 0
                for servicio_row in servicios:
                    servicio_id = servicio_row[0] if isinstance(servicio_row, sqlite3.Row) else servicio_row[0]
                    hembra_id = servicio_row[1] if isinstance(servicio_row, sqlite3.Row) else servicio_row[1]
                    
                    # Registrar parto
                    fecha_parto = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                    
                    cur.execute(
                        """
                        UPDATE servicio SET estado='Parida', fecha_parto_real=? WHERE id=?
                        """,
                        (fecha_parto, servicio_id)
                    )
                    
                    # Crear cría (si fue exitoso)
                    if random.random() > 0.1:  # 90% de nacimientos exitosos
                        sexo_cria = random.choice(["Hembra", "Macho"])
                        peso_cria = random.uniform(25, 40)
                        
                        # Obtener raza de madre
                        cur.execute("SELECT raza_id FROM animal WHERE id=?", (hembra_id,))
                        raza_row = cur.fetchone()
                        raza_id = raza_row[0] if raza_row else random.choice(list(self.razas.values()))
                        
                        # Obtener finca de madre
                        cur.execute("SELECT id_finca, id_potrero, lote_id FROM animal WHERE id=?", (hembra_id,))
                        animal_row = cur.fetchone()
                        finca_id = animal_row[0] if animal_row else None
                        potrero_id = animal_row[1] if animal_row else None
                        lote_id = animal_row[2] if animal_row else None
                        
                        codigo_cria = f"NES-{datetime.now().strftime('%Y%m%d')}-{partos_count:02d}"
                        
                        cur.execute(
                            """
                            INSERT INTO animal (
                                id_finca, codigo, nombre, sexo, raza_id,
                                id_potrero, lote_id, fecha_nacimiento, peso_nacimiento,
                                id_madre, tipo_ingreso, estado
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Nacimiento', 'Activo')
                            """,
                            (
                                finca_id,
                                codigo_cria,
                                f"Cría-{partos_count}",
                                sexo_cria,
                                raza_id,
                                potrero_id,
                                lote_id,
                                fecha_parto,
                                peso_cria,
                                hembra_id
                            )
                        )
                    
                    partos_count += 1
                
                self._log_insert("servicio (partos)", partos_count)
        except Exception as e:
            logger.error(f"Error insertando partos: {e}")
            raise
    
    # ==================== SALUD ====================
    
    def seed_salud(self):
        """Inserta registros de salud (tratamientos, eventos diagnósticos)."""
        logger.info("📍 Insertando registros de salud...")
        
        enfermedades = [
            ("Mastitis", "Inflamación de la glándula mamaria"),
            ("Cojera", "Problemas de locomoción"),
            ("Neumonía", "Infección respiratoria"),
            ("Diarrea", "Problemas digestivos"),
            ("Fiebre vitular", "Hipocalcemia posparto"),
        ]
        
        tratamientos = ["Antibiótico", "Antiinflamatorio", "Suplemento", "Inyectable"]
        veterinarios = ["Dr. Rodríguez", "Dra. López", "Dr. Martínez"]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Obtener animales activos
                cur.execute("SELECT id FROM animal WHERE estado='Activo' LIMIT 20")
                animales = [row[0] for row in cur.fetchall()]
                
                tratamientos_count = 0
                for animal_id in animales:
                    # 60% probabilidad de tener tratamiento
                    if random.random() < 0.6:
                        fecha_inicio = self._random_date(90)
                        fecha_fin = None
                        if random.random() > 0.3:  # Algunos terminados
                            fecha_fin = (datetime.strptime(fecha_inicio, "%Y-%m-%d") + timedelta(days=random.randint(7, 30))).strftime("%Y-%m-%d")
                        
                        enfermedad, desc = random.choice(enfermedades)
                        
                        cur.execute(
                            """
                            INSERT INTO tratamiento (
                                id_animal, fecha_inicio, fecha_fin, tipo_tratamiento,
                                producto, dosis, veterinario, estado
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                animal_id,
                                fecha_inicio,
                                fecha_fin,
                                enfermedad,
                                random.choice(tratamientos),
                                f"{random.randint(1, 5)}ml/día",
                                random.choice(veterinarios),
                                "Completado" if fecha_fin else "Activo"
                            )
                        )
                        tratamientos_count += 1
                
                self._log_insert("tratamiento", tratamientos_count)
        except Exception as e:
            logger.error(f"Error insertando registros de salud: {e}")
            raise
    
    # ==================== PRODUCCIÓN DE LECHE ====================
    
    def seed_produccion_leche(self):
        """Inserta registros de producción de leche (últimos 60 días)."""
        logger.info("📍 Insertando producción de leche...")
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Obtener hembras activas para producción
                cur.execute("""
                    SELECT id FROM animal 
                    WHERE sexo='Hembra' AND estado='Activo' AND raza_id IN (
                        SELECT id FROM raza WHERE tipo_ganado='Lechero'
                    )
                    LIMIT 15
                """)
                hembras_lecheras = [row[0] for row in cur.fetchall()]
                
                if not hembras_lecheras:
                    logger.warning("No hay hembras lecheras para simular producción")
                    return
                
                registros_count = 0
                # Últimos 60 días
                for days_back in range(60, 0, -1):
                    fecha = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
                    
                    for hembra_id in hembras_lecheras:
                        # Variación realista: 15-35L/día
                        manana = round(random.uniform(8, 15), 2)
                        tarde = round(random.uniform(5, 12), 2)
                        noche = round(random.uniform(2, 8), 2)
                        
                        try:
                            cur.execute(
                                """
                                INSERT OR IGNORE INTO produccion_leche (
                                    animal_id, fecha, litros_manana, litros_tarde, litros_noche
                                ) VALUES (?, ?, ?, ?, ?)
                                """,
                                (hembra_id, fecha, manana, tarde, noche)
                            )
                            registros_count += 1
                        except sqlite3.IntegrityError:
                            # Puede que ya exista
                            pass
                
                self._log_insert("produccion_leche", registros_count)
        except Exception as e:
            logger.error(f"Error insertando producción de leche: {e}")
            raise
    
    # ==================== PESOS ====================
    
    def seed_pesos(self):
        """Inserta histórico de pesajes."""
        logger.info("📍 Insertando histórico de pesos...")
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                # Obtener animales
                cur.execute("SELECT id, peso_compra FROM animal WHERE estado='Activo' LIMIT 25")
                animales = cur.fetchall()
                
                registros_count = 0
                for animal in animales:
                    animal_id = animal[0] if isinstance(animal, sqlite3.Row) else animal[0]
                    peso_base = animal[1] if isinstance(animal, sqlite3.Row) else animal[1]
                    peso_base = peso_base or 300
                    
                    # 5 pesajes en los últimos 90 días
                    for _ in range(5):
                        fecha = self._random_date(90)
                        peso = peso_base + random.uniform(-50, 100)
                        
                        try:
                            cur.execute(
                                """
                                INSERT OR IGNORE INTO peso (animal_id, fecha, peso, metodo)
                                VALUES (?, ?, ?, ?)
                                """,
                                (animal_id, fecha, peso, "Bascula")
                            )
                            registros_count += 1
                        except sqlite3.IntegrityError:
                            pass
                
                self._log_insert("peso", registros_count)
        except Exception as e:
            logger.error(f"Error insertando pesos: {e}")
            raise
    
    # ==================== INSUMOS ====================
    
    def seed_insumos(self):
        """Inserta insumos e inventario."""
        logger.info("📍 Insertando insumos...")
        
        insumos_data = [
            ("INS-001", "Alimento Concentrado", "Alimento", "Bolsa 50kg", "kg", 500, 100, 1000, 25.50),
            ("INS-002", "Hay de Alfalfa", "Alimento", "Fardo", "fardo", 200, 50, 500, 15.00),
            ("INS-003", "Vacuna Aftosa", "Medicamento", "Frasco 50 dosis", "dosis", 100, 20, 200, 0.50),
            ("INS-004", "Antibiótico Penicilina", "Medicamento", "Frasco 500ml", "ml", 50, 10, 100, 2.00),
            ("INS-005", "Urea", "Fertilizante", "Bolsa 50kg", "kg", 300, 50, 1000, 12.00),
            ("INS-006", "Semilla Bracharia", "Semilla", "Bolsa 25kg", "kg", 100, 20, 500, 8.50),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                for codigo, nombre, cat, desc, unidad, stock, minimo, maximo, precio in insumos_data:
                    finca_id = random.choice(list(self.fincas.values()))
                    
                    cur.execute(
                        """
                        INSERT INTO insumo (
                            codigo, nombre, categoria, descripcion, unidad_medida,
                            stock_actual, stock_minimo, stock_maximo, precio_unitario,
                            id_finca, estado
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Activo')
                        """,
                        (codigo, nombre, cat, desc, unidad, stock, minimo, maximo, precio, finca_id)
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.insumos[codigo] = last_id
                
                self._log_insert("insumo", len(insumos_data))
        except Exception as e:
            logger.error(f"Error insertando insumos: {e}")
            raise
    
    # ==================== MOVIMIENTOS DE INSUMOS ====================
    
    def seed_movimientos_insumos(self):
        """Inserta movimientos de entrada y salida de insumos."""
        logger.info("📍 Insertando movimientos de insumos...")
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                insumos_list = list(self.insumos.values())
                if not insumos_list:
                    logger.warning("No hay insumos para movimientos")
                    return
                
                movimientos_count = 0
                # Últimos 90 días
                for _ in range(30):
                    insumo_id = random.choice(insumos_list)
                    fecha = self._random_date(90)
                    
                    # Entrada o salida
                    tipo = random.choice(["Entrada", "Salida"])
                    cantidad = random.uniform(10, 200)
                    costo_unit = random.uniform(1, 50)
                    
                    cur.execute(
                        """
                        INSERT INTO movimiento_insumo (
                            insumo_id, tipo_movimiento, cantidad, motivo,
                            costo_unitario, costo_total, fecha_movimiento
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            insumo_id,
                            tipo,
                            cantidad,
                            "Compra" if tipo == "Entrada" else "Consumo",
                            costo_unit,
                            cantidad * costo_unit,
                            fecha
                        )
                    )
                    movimientos_count += 1
                
                self._log_insert("movimiento_insumo", movimientos_count)
        except Exception as e:
            logger.error(f"Error insertando movimientos de insumos: {e}")
            raise
    
    # ==================== HERRAMIENTAS ====================
    
    def seed_herramientas(self):
        """Inserta herramientas y equipos."""
        logger.info("📍 Insertando herramientas...")
        
        herramientas_data = [
            ("HER-001", "Ordeñadora Automática", "Maquinaria", "Máquina de ordeño", "John Deere", "M2000", 50000),
            ("HER-002", "Tractor Agrícola", "Maquinaria", "Tractor 75HP", "Massey Ferguson", "290", 35000),
            ("HER-003", "Motobomba", "Maquinaria", "Bomba de agua 2HP", "Pedrollo", "3-80", 8000),
            ("HER-004", "Picadora de Alimento", "Maquinaria", "Picadora pequeña", "Local", "Manual", 3000),
            ("HER-005", "Balanza Digital", "Equipo Medico", "Bascula 500kg", "Shimazu", "BW500", 1500),
            ("HER-006", "Estetoscopio", "Equipo Medico", "Equipo diagnóstico", "Littman", "XYZ", 200),
            ("HER-007", "Botiquín Veterinario", "Equipo Medico", "Kit básico", "GenéricO", "-", 1000),
        ]
        
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                
                for codigo, nombre, cat, desc, marca, modelo, valor in herramientas_data:
                    finca_id = random.choice(list(self.fincas.values()))
                    estado = random.choice(["Operativa", "Operativa", "En Mantenimiento"])  # Mayormente operativas
                    
                    cur.execute(
                        """
                        INSERT INTO herramienta (
                            codigo, nombre, categoria, descripcion,
                            marca, modelo, id_finca, ubicacion,
                            estado, valor_adquisicion, vida_util_anos
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            codigo, nombre, cat, desc, marca, modelo, finca_id,
                            "Bodega Principal",
                            estado,
                            valor,
                            random.randint(5, 20)
                        )
                    )
                    last_id = cur.lastrowid
                    if last_id is not None:
                        self.herramientas[codigo] = last_id
                
                self._log_insert("herramienta", len(herramientas_data))
        except Exception as e:
            logger.error(f"Error insertando herramientas: {e}")
            raise
    
    # ==================== EJECUCIÓN COMPLETA ====================
    
    def run(self) -> bool:
        """Ejecuta el seed completo en orden de dependencias."""
        logger.info("=" * 70)
        logger.info("🌱 INICIANDO CARGA DE DATOS DE PRUEBA - FINCAFÁCIL")
        logger.info(f"   Base de datos: {self.db_path}")
        logger.info(f"   Modo limpieza: {'SÍ' if self.clear_before_seed else 'NO'}")
        logger.info("=" * 70)
        
        try:
            # Orden de ejecución (respeta FKs)
            self.clear_data()
            self.seed_razas()
            self.seed_fincas()
            self.seed_potreros()
            self.seed_lotes()
            self.seed_vendedores()
            self.seed_animales(count=40)
            self.seed_muertes()
            self.seed_reproduccion()
            self.seed_partos()
            self.seed_salud()
            self.seed_produccion_leche()
            self.seed_pesos()
            self.seed_insumos()
            self.seed_movimientos_insumos()
            self.seed_herramientas()
            
            logger.info("\n" + "=" * 70)
            logger.info("✅ SEED DE DATOS COMPLETADO EXITOSAMENTE")
            logger.info("\n📊 RESUMEN DE INSERCIONES:")
            for table, count in sorted(self.stats.items()):
                logger.info(f"   {table:.<40} {count:>5} registros")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error("\n" + "=" * 70)
            logger.error(f"❌ ERROR EN SEED DE DATOS: {e}")
            logger.error("=" * 70)
            return False


def run_seed(clear_before_seed: bool = False, mode: str = "dev") -> bool:
    """
    Función pública para ejecutar el seed de datos.
    
    Args:
        clear_before_seed: Si True, elimina datos previos
        mode: "dev" o "prod" (solo aplica en dev)
        
    Returns:
        bool: True si fue exitoso
    """
    if mode != "dev":
        logger.warning("⚠️  Seed de datos solo disponible en modo DESARROLLO")
        return False
    
    generator = SeedDataGenerator(clear_before_seed=clear_before_seed)
    return generator.run()


if __name__ == "__main__":
    # Para ejecución manual: python -m database.seed_data
    import sys
    
    clear = "--clear" in sys.argv
    logger.info(f"Ejecutando seed manualmente (clear={clear})")
    success = run_seed(clear_before_seed=clear, mode="dev")
    sys.exit(0 if success else 1)
