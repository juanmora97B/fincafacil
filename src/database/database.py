"""
Módulo unificado de base de datos para FincaFacil
Gestión centralizada de operaciones con la base de datos SQLite
"""

import os
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator
from contextlib import contextmanager


logger = logging.getLogger(__name__)

# Importar migraciones
try:
    from database.migraciones import ejecutar_migraciones
except ImportError:
    # Fallback si está en src/
    try:
        from migraciones import ejecutar_migraciones
    except ImportError:
        def ejecutar_migraciones(conn):
            logger.warning("Módulo de migraciones no disponible")
# Import app_paths lazily to avoid circular imports
_DB_PATH = None
_SEED_DB_PATH = None
_initialized = False


def _get_paths():
    """Initialize paths if not already done."""
    global _DB_PATH, _SEED_DB_PATH
    if _DB_PATH is None:
        try:
            from modules.utils.app_paths import get_db_path, get_seed_path
            _DB_PATH = get_db_path()
            _SEED_DB_PATH = get_seed_path(Path("database") / "fincafacil.db")
        except Exception as e:
            logger.error(f"Error importing app_paths: {e}")
            # Fallback to local paths
            base = Path(__file__).parent.parent
            _DB_PATH = base / "database" / "fincafacil.db"
            _SEED_DB_PATH = _DB_PATH


# Expose as module-level variable (will be set on first access)
DB_PATH = None


def get_db_path_safe() -> Path:
    """Get database path, initializing if needed."""
    global DB_PATH
    if DB_PATH is None:
        _get_paths()
        DB_PATH = _DB_PATH
    assert DB_PATH is not None, "Failed to initialize database path"
    return DB_PATH


def ensure_local_db() -> None:
    """Garantiza que la BD exista en el directorio de usuario."""
    global _initialized
    if _initialized:
        return
    
    try:
        _get_paths()
        db_path = _DB_PATH
        seed_path = _SEED_DB_PATH
        
        if db_path and db_path.parent:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        if db_path and not db_path.exists():
            if seed_path and seed_path.exists():
                shutil.copy2(seed_path, db_path)
                logger.info("Base de datos copiada a directorio de usuario: %s", db_path)
            else:
                logger.warning("Seed de base de datos no encontrada: %s", seed_path)
        _initialized = True
    except Exception as exc:
        logger.error("No se pudo preparar la base de datos en el directorio de usuario: %s", exc)


# Initialize DB_PATH for first use
get_db_path_safe()
ensure_local_db()

@contextmanager
def get_db_connection(db_path: Optional[Path | str] = None) -> Iterator[sqlite3.Connection]:
    """
    Obtiene una conexión SQLite configurada.
    Args:
        db_path: Ruta opcional a la base de datos.
    Yields:
        sqlite3.Connection
    """
    path = db_path or get_db_path_safe()
    try:
        Path(path).parent.mkdir(exist_ok=True, parents=True)
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Error al conectar con la base de datos: {e}")
        raise
    finally:
        try:
            if 'conn' in locals():
                conn.close()
        except Exception:
            pass

def inicializar_base_datos() -> bool:
    """
    Inicializa la base de datos con todas las tablas y datos básicos
    
    Returns:
        bool: True si la inicialización fue exitosa
    """
    try:
        logger.info("Inicializando base de datos...")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Ejecutar esquema completo
            cursor.executescript(SCHEMA_COMPLETO)

            # Migración ligera: asegurar columnas claves
            _migrar_esquema_basico(conn)
            
            # Insertar datos básicos
            cursor.executescript(DATOS_BASICOS)
            
            conn.commit()
            logger.info("Base de datos inicializada exitosamente")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        return False

def verificar_base_datos() -> bool:
    """
    Verifica que la base de datos existe y contiene tablas esenciales.
    Returns:
        bool: True si es válida.
    """
    try:
        path = get_db_path_safe()
        if not path.exists():
            logger.warning("Base de datos no encontrada: %s", DB_PATH)
            return False
        with get_db_connection() as conn:
            cur = conn.cursor()
            esenciales = ['animal','finca','potrero','lote']
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN (?,?,?,?)",
                esenciales
            )
            nombres = [r[0] for r in cur.fetchall()]
            return len(nombres) == len(esenciales)
    except Exception as e:
        logger.error("Error verificando BD: %s", e)
        return False

def asegurar_esquema_minimo() -> None:
    """
    Garantiza que las tablas y valores mínimos existan incluso si la BD ya
    existía de versiones previas. Esta función es idempotente y segura para
    ejecutar en cada arranque.

    Cubre los problemas observados donde algunos módulos consultan la tabla
    app_settings en instalaciones con BD antigua que no tenía dicha tabla.
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            # Asegurar existencia de tabla app_settings
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    clave TEXT PRIMARY KEY,
                    valor TEXT
                )
                """
            )

            # Insertar valores por defecto si no existen
            cur.execute(
                "INSERT OR IGNORE INTO app_settings (clave, valor) VALUES ('units_weight', 'kg')"
            )
            cur.execute(
                "INSERT OR IGNORE INTO app_settings (clave, valor) VALUES ('units_volume', 'L')"
            )

            conn.commit()
            logger.info("Esquema mínimo verificado (app_settings y valores por defecto)")

            # Ejecutar migraciones del sistema (usuarios, roles, auditoría, KPIs)
            try:
                ejecutar_migraciones(conn)
            except Exception as e:
                logger.warning(f"No se pudieron ejecutar migraciones adicionales: {e}")

            # Limpieza de tablas legacy residuales que causan errores FK
            try:
                # Verificar que tabla animal principal tiene datos
                cur.execute("SELECT COUNT(*) FROM animal")
                animal_count = cur.fetchone()
                if animal_count and animal_count[0] > 0:
                    # Eliminar tablas legacy si existen
                    legacy_tables = ['animal_legacy', 'animal_legacy_temp']
                    for legacy_table in legacy_tables:
                        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (legacy_table,))
                        if cur.fetchone():
                            cur.execute(f"DROP TABLE IF EXISTS {legacy_table}")
                            logger.info(f"Tabla legacy '{legacy_table}' eliminada durante inicialización")
                    
                    # Eliminar triggers con referencias legacy
                    cur.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND sql LIKE '%legacy%'")
                    legacy_triggers = cur.fetchall()
                    for (trigger_name,) in legacy_triggers:
                        cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                        logger.info(f"Trigger legacy '{trigger_name}' eliminado")
                    
                    conn.commit()
                    logger.info("Limpieza de referencias legacy completada")
                # Normalizar tabla comentario a esquema unificado
                try:
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comentario'")
                    exists = cur.fetchone() is not None
                    if not exists:
                        cur.execute(
                            """
                            CREATE TABLE comentario (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                animal_id INTEGER NOT NULL,
                                fecha TEXT NOT NULL,
                                comentario TEXT NOT NULL,
                                FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
                            )
                            """
                        )
                        logger.info("Tabla 'comentario' creada con esquema estándar")
                    else:
                        # Detectar columnas legacy (id_animal, autor, nota)
                        cur.execute("PRAGMA table_info(comentario)")
                        cols = [row[1] for row in cur.fetchall()]
                        if 'animal_id' not in cols or 'comentario' not in cols:
                            logger.info("Reconstruyendo 'comentario' para esquema estándar")
                            cur.execute("ALTER TABLE comentario RENAME TO comentario_backup")
                            cur.execute(
                                """
                                CREATE TABLE comentario (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    animal_id INTEGER NOT NULL,
                                    fecha TEXT NOT NULL,
                                    comentario TEXT NOT NULL,
                                    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
                                )
                                """
                            )
                            # Migrar datos si existen columnas compatibles
                            # Mapear: id_animal -> animal_id, nota -> comentario
                            try:
                                cur.execute(
                                    """
                                    INSERT INTO comentario (animal_id, fecha, comentario)
                                    SELECT 
                                        COALESCE(id_animal, animal_id),
                                        fecha,
                                        COALESCE(nota, comentario)
                                    FROM comentario_backup
                                    """
                                )
                            except Exception:
                                # Si no coinciden, insertar nada
                                pass
                            cur.execute("DROP TABLE comentario_backup")
                            logger.info("Tabla 'comentario' normalizada correctamente")
                    conn.commit()
                except Exception as ce:
                    logger.warning(f"No se pudo normalizar tabla comentario: {ce}")

                # Asegurar tabla reubicacion (nuevo modelo explícito)
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reubicacion'")
                if cur.fetchone() is None:
                    cur.execute(
                        """
                        CREATE TABLE reubicacion (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            animal_id INTEGER NOT NULL,
                            fecha TEXT NOT NULL,
                            from_potrero TEXT,
                            to_potrero TEXT,
                            motivo TEXT,
                            autor TEXT,
                            FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
                        )
                        """
                    )
                    logger.info("Tabla 'reubicacion' creada")
                # Índices útiles para reportes
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reub_animal_fecha ON reubicacion(animal_id, fecha)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_reub_potreros ON reubicacion(from_potrero, to_potrero)")

                # Historial de reubicaciones para reportes
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historial_reubicaciones'")
                if cur.fetchone() is None:
                    cur.execute(
                        """
                        CREATE TABLE historial_reubicaciones (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            animal_codigo TEXT NOT NULL,
                            finca_origen TEXT,
                            finca_destino TEXT,
                            potrero_origen TEXT,
                            potrero_destino TEXT,
                            fecha TEXT NOT NULL,
                            motivo TEXT,
                            usuario TEXT,
                            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                    cur.execute("CREATE INDEX IF NOT EXISTS idx_hist_reub_fecha ON historial_reubicaciones(fecha)")

                # Inventario animales por finca (conteo rápido)
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventario_animales'")
                if cur.fetchone() is None:
                    cur.execute(
                        """
                        CREATE TABLE inventario_animales (
                            finca_id INTEGER PRIMARY KEY,
                            cantidad INTEGER NOT NULL DEFAULT 0,
                            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (finca_id) REFERENCES finca(id)
                        )
                        """
                    )

                conn.commit()
            except Exception as e:
                logger.warning(f"No se pudo limpiar tablas legacy: {e}")
    except Exception as e:
        # No debe impedir el arranque, solo registrar advertencia
        logger.warning(f"No se pudo asegurar esquema mínimo: {e}")

def asegurar_esquema_completo() -> None:
    """
    Ejecuta la migración ligera para asegurar que todas las columnas esperadas
    existan en tablas clave (animal, sector, lote, etc.). Idempotente.
    """
    try:
        with get_db_connection() as conn:
            _migrar_esquema_basico(conn)
            logger.info("Esquema completo verificado/migrado")
    except Exception as e:
        logger.warning(f"No se pudo asegurar esquema completo: {e}")

def ejecutar_consulta(query: str, parametros: Optional[tuple[Any, ...]] = None, fetch: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    Ejecuta una consulta SQL de forma segura
    
    Args:
        query: Consulta SQL a ejecutar
        parametros: Parámetros para la consulta
        fetch: Si debe retornar resultados
        
    Returns:
        List[Dict] o None: Resultados si fetch=True, sino None
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if parametros:
                cursor.execute(query, parametros)
            else:
                cursor.execute(query)
            
            if fetch:
                resultados = cursor.fetchall()
                return [dict(row) for row in resultados]
            else:
                conn.commit()
                return None
                
    except sqlite3.Error as e:
        logger.error(f"Error en consulta: {e}\nConsulta: {query}")
        raise

def obtener_tablas() -> List[str]:
    """
    Obtiene lista de todas las tablas en la base de datos
    
    Returns:
        List[str]: Nombres de las tablas
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error obteniendo tablas: {e}")
        return []

def reubicar_animal(
    animal_id: int,
    to_potrero: str,
    motivo: str,
    autor: str,
    fecha: str,
    to_finca_id: int | None = None,
    to_sector_id: int | None = None,
    to_lote_id: int | None = None,
) -> bool:
    """
    Registra una reubicación de animal de manera transaccional:
    - Lee potrero actual
    - Inserta en `reubicacion`
    - Actualiza `animal.id_potrero`
    - Inserta `comentario` con metadata

    Args:
        animal_id: ID del animal
        to_potrero: Potrero destino (texto o id)
        motivo: Motivo de reubicación
        autor: Autor de la acción
        fecha: Fecha en formato YYYY-MM-DD

    Returns:
        bool: True si se completó correctamente
    """
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Leer potrero actual
            cur.execute("SELECT id_potrero FROM animal WHERE id=?", (animal_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Animal no encontrado")
            from_potrero = row[0] if row[0] is not None else "-"

            # Insertar reubicación
            cur.execute(
                """
                INSERT INTO reubicacion (animal_id, fecha, from_potrero, to_potrero, motivo, autor)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (animal_id, fecha, str(from_potrero), str(to_potrero), motivo or "", autor or "")
            )

            # Leer finca origen
            cur.execute("SELECT id_finca FROM animal WHERE id=?", (animal_id,))
            rfin = cur.fetchone()
            from_finca_id = rfin[0] if rfin and not isinstance(rfin, sqlite3.Row) else (rfin['id_finca'] if rfin else None)

            # Actualizar animal: finca (si aplica), potrero, sector y lote
            if to_finca_id is not None:
                cur.execute("UPDATE animal SET id_finca=? WHERE id=?", (to_finca_id, animal_id))
            cur.execute("UPDATE animal SET id_potrero=? WHERE id=?", (to_potrero, animal_id))
            if to_sector_id is not None:
                cur.execute("UPDATE animal SET id_sector=? WHERE id=?", (to_sector_id, animal_id))
            if to_lote_id is not None:
                cur.execute("UPDATE animal SET lote_id=? WHERE id=?", (to_lote_id, animal_id))

            # Comentario con metadata
            meta_json = ("{"
                        f"\"tipo\":\"reubicacion\",\"from\":\"{from_potrero}\",\"to\":\"{to_potrero}\","\
                        f"\"motivo\":\"{(motivo or '').replace('"','\"')}\",\"autor\":\"{(autor or '').replace('"','\"')}\""\
                        "}")
            comentario_texto = f"REUBICACIÓN: {from_potrero} → {to_potrero}. Motivo: {(motivo or '').strip()}\n[META]{meta_json}"
            cur.execute(
                "INSERT INTO comentario (animal_id, fecha, comentario) VALUES (?, ?, ?)",
                (animal_id, fecha, comentario_texto)
            )

            # Actualizar inventarios (conteo por finca)
            if from_finca_id and to_finca_id and str(from_finca_id) != str(to_finca_id):
                # Restar origen
                cur.execute("INSERT OR IGNORE INTO inventario_animales (finca_id, cantidad) VALUES (?, 0)", (from_finca_id,))
                cur.execute("UPDATE inventario_animales SET cantidad = cantidad - 1, fecha_actualizacion = CURRENT_TIMESTAMP WHERE finca_id=?", (from_finca_id,))
                # Sumar destino
                cur.execute("INSERT OR IGNORE INTO inventario_animales (finca_id, cantidad) VALUES (?, 0)", (to_finca_id,))
                cur.execute("UPDATE inventario_animales SET cantidad = cantidad + 1, fecha_actualizacion = CURRENT_TIMESTAMP WHERE finca_id=?", (to_finca_id,))

            # Registrar historial reubicaciones (texto legible)
            # Obtener nombres amigables
            cur.execute("SELECT nombre FROM finca WHERE id=?", (from_finca_id,))
            from_finca_name = (cur.fetchone() or [None])[0]
            cur.execute("SELECT nombre FROM finca WHERE id=?", (to_finca_id,))
            to_finca_name = (cur.fetchone() or [None])[0]
            cur.execute("SELECT nombre FROM potrero WHERE id=?", (from_potrero if isinstance(from_potrero, int) else None,))
            from_potrero_name = (cur.fetchone() or [None])[0] if isinstance(from_potrero, int) else str(from_potrero)
            cur.execute("SELECT nombre FROM potrero WHERE id=?", (to_potrero if isinstance(to_potrero, int) else None,))
            to_potrero_name = (cur.fetchone() or [None])[0] if isinstance(to_potrero, int) else str(to_potrero)
            # Código animal
            cur.execute("SELECT codigo FROM animal WHERE id=?", (animal_id,))
            animal_codigo = (cur.fetchone() or [None])[0] or "?"
            cur.execute(
                """
                INSERT INTO historial_reubicaciones (
                    animal_codigo, finca_origen, finca_destino, potrero_origen, potrero_destino, fecha, motivo, usuario
                ) VALUES (?,?,?,?,?,?,?,?)
                """,
                (animal_codigo, from_finca_name, to_finca_name, from_potrero_name, to_potrero_name, fecha, motivo or "", autor or "")
            )

            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error reubicando animal: {e}")
        return False

# Esquema completo de la base de datos
SCHEMA_COMPLETO = """
-- Tabla de razas

CREATE TABLE IF NOT EXISTS raza (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT UNIQUE NOT NULL,
    tipo_ganado TEXT, -- Lechero/Carne/Doble Propósito/Registro
    descripcion TEXT,
    estado TEXT DEFAULT 'Activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de fincas
CREATE TABLE IF NOT EXISTS finca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    nombre TEXT UNIQUE NOT NULL,
    propietario TEXT,
    ubicacion TEXT,
    area_hectareas REAL,
    telefono TEXT,
    email TEXT,
    descripcion TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de potreros
CREATE TABLE IF NOT EXISTS potrero (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    id_finca INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    sector TEXT,
    id_sector INTEGER,
    area_hectareas REAL,
    capacidad_maxima INTEGER,
    tipo_pasto TEXT,
    descripcion TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_finca) REFERENCES finca (id),
    FOREIGN KEY (id_sector) REFERENCES sector (id)
);

-- Tabla de lotes
CREATE TABLE IF NOT EXISTS lote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    finca_id INTEGER,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    criterio TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (finca_id) REFERENCES finca(id)
);

CREATE TABLE IF NOT EXISTS animal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_finca INTEGER,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT,
    tipo_ingreso TEXT,
    sexo TEXT,
    -- Clave foránea normalizada
    raza_id INTEGER,
    -- Ubicación y agrupación
    id_potrero INTEGER,
    lote_id INTEGER,
    id_sector INTEGER, -- Nueva columna para sectores (reemplaza concepto de grupo en UI)
    id_vendedor INTEGER,
    -- Fechas y pesos
    fecha_nacimiento DATE,
    fecha_compra DATE,
    peso_nacimiento REAL,
    peso_compra REAL,
    precio_compra REAL,
    -- Parentesco y reproducción
    id_padre INTEGER,
    id_madre INTEGER,
    tipo_concepcion TEXT,
    -- Estado y salud
    salud TEXT,
    estado TEXT DEFAULT 'Activo',
    inventariado INTEGER DEFAULT 0,
    -- Características
    color TEXT,
    hierro TEXT,
    numero_hierros INTEGER,
    composicion_racial TEXT,
    -- Varios
    comentarios TEXT,
    foto_path TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raza_id) REFERENCES raza (id),
    FOREIGN KEY (id_finca) REFERENCES finca (id),
    FOREIGN KEY (id_potrero) REFERENCES potrero (id),
    FOREIGN KEY (lote_id) REFERENCES lote (id),
    FOREIGN KEY (id_sector) REFERENCES sector (id),
    FOREIGN KEY (id_vendedor) REFERENCES vendedor (id),
    FOREIGN KEY (id_padre) REFERENCES animal (id),
    FOREIGN KEY (id_madre) REFERENCES animal (id)
);

-- Tabla de reproducción
CREATE TABLE IF NOT EXISTS reproduccion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    fecha_cubricion DATE,
    fecha_parto DATE,
    tipo_cubricion TEXT CHECK(tipo_cubricion IN ('Natural', 'Inseminacion')),
    estado TEXT CHECK(estado IN ('Gestante', 'Parida', 'Vacía', 'Aborto')),
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animal (id)
);

-- Tabla de servicios de reproducción (para notificaciones de partos)
CREATE TABLE IF NOT EXISTS servicio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_hembra INTEGER NOT NULL,
    id_macho INTEGER,
    fecha_servicio DATE NOT NULL,
    tipo_servicio TEXT CHECK(tipo_servicio IN ('Monta Natural', 'Inseminación Artificial')),
    estado TEXT DEFAULT 'Servida' CHECK(estado IN ('Servida', 'Gestante', 'Vacía', 'Parida', 'Aborto')),
    fecha_parto_estimada DATE,
    fecha_parto_real DATE,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_hembra) REFERENCES animal (id),
    FOREIGN KEY (id_macho) REFERENCES animal (id)
);

-- Tabla de tratamientos (módulo Tratamientos)
CREATE TABLE IF NOT EXISTS tratamiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_animal INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    tipo_tratamiento TEXT NOT NULL,
    producto TEXT NOT NULL,
    dosis TEXT,
    veterinario TEXT,
    comentario TEXT,
    fecha_proxima DATE,
    estado TEXT DEFAULT 'Activo',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_animal) REFERENCES animal(id)
);

-- Tabla de comentarios (bitácora ligera de notas por animal)
CREATE TABLE IF NOT EXISTS comentario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_animal INTEGER NOT NULL,
    fecha DATE NOT NULL,
    autor TEXT,
    nota TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_animal) REFERENCES animal(id) ON DELETE CASCADE
);

-- Tabla de movimientos
CREATE TABLE IF NOT EXISTS movimiento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    lote_origen_id INTEGER,
    lote_destino_id INTEGER NOT NULL,
    fecha_movimiento DATE NOT NULL,
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('Entrada', 'Salida', 'Traslado')),
    motivo TEXT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animal (id),
    FOREIGN KEY (lote_origen_id) REFERENCES lote (id),
    FOREIGN KEY (lote_destino_id) REFERENCES lote (id)
);

-- Tabla de pesos (histórico de pesajes)
CREATE TABLE IF NOT EXISTS peso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    peso REAL NOT NULL,
    metodo TEXT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(animal_id, fecha),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
);

-- Tabla de producción de leche (por día y animal)
CREATE TABLE IF NOT EXISTS produccion_leche (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    litros_manana REAL DEFAULT 0,
    litros_tarde REAL DEFAULT 0,
    litros_noche REAL DEFAULT 0,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(animal_id, fecha),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
);

-- Tabla de registros de muerte
CREATE TABLE IF NOT EXISTS muerte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    causa TEXT,
    diagnostico_presuntivo TEXT,
    diagnostico_confirmado TEXT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(animal_id),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
);

-- Tabla de diagnósticos veterinarios
CREATE TABLE IF NOT EXISTS diagnostico_veterinario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    tipo TEXT,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de eventos diagnósticos / sanitarios
CREATE TABLE IF NOT EXISTS diagnostico_evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    tipo TEXT,
    detalle TEXT,
    severidad TEXT,
    estado TEXT,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
);

-- Tabla de ajustes de la aplicación (clave-valor)
CREATE TABLE IF NOT EXISTS app_settings (
    clave TEXT PRIMARY KEY,
    valor TEXT
);

-- Tabla de grupos (agrupación de animales)

-- Tabla de vendedores (para compras)
CREATE TABLE IF NOT EXISTS vendedor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    contacto TEXT,
    telefono TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- MÓDULO DE INSUMOS E INVENTARIO
-- ========================================

-- Tabla de insumos (inventario mejorado)
CREATE TABLE IF NOT EXISTS insumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    categoria TEXT CHECK(categoria IN ('Medicamento', 'Alimento', 'Fertilizante', 'Semilla', 'Herramienta', 'Otro')) NOT NULL,
    descripcion TEXT,
    unidad_medida TEXT NOT NULL, -- kg, L, unidades, sacos, etc.
    stock_actual REAL DEFAULT 0,
    stock_minimo REAL DEFAULT 0,
    stock_maximo REAL,
    precio_unitario REAL,
    id_finca INTEGER,
    ubicacion TEXT,
    proveedor_principal TEXT,
    responsable TEXT,
    observaciones TEXT,
    id_trabajador INTEGER,
    stock_bodega REAL DEFAULT 0,
    foto_path TEXT,
    fecha_adquisicion DATE,
    fecha_vencimiento DATE,
    lote_proveedor TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_finca) REFERENCES finca(id)
);

-- Tabla de movimientos de insumos (entradas/salidas)
CREATE TABLE IF NOT EXISTS movimiento_insumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_id INTEGER NOT NULL,
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('Entrada', 'Salida', 'Ajuste')) NOT NULL,
    cantidad REAL NOT NULL,
    motivo TEXT,
    referencia TEXT, -- Puede ser código de compra, tratamiento, etc.
    animal_id INTEGER, -- Si se usó en un animal específico
    potrero_id INTEGER, -- Si se usó en un potrero
    usuario TEXT,
    costo_unitario REAL,
    costo_total REAL,
    observaciones TEXT,
    fecha_movimiento DATE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (insumo_id) REFERENCES insumo(id) ON DELETE CASCADE,
    FOREIGN KEY (animal_id) REFERENCES animal(id),
    FOREIGN KEY (potrero_id) REFERENCES potrero(id)
);

-- ========================================
-- MÓDULO DE HERRAMIENTAS Y EQUIPOS
-- ========================================

-- Tabla de herramientas y equipos de la finca
CREATE TABLE IF NOT EXISTS herramienta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    categoria TEXT CHECK(categoria IN ('Maquinaria', 'Herramienta Manual', 'Equipo Medico', 'Vehiculo', 'Equipo Oficina', 'Otro')),
    descripcion TEXT,
    marca TEXT,
    modelo TEXT,
    numero_serie TEXT,
    id_finca INTEGER,
    ubicacion TEXT, -- Bodega, Potrero X, Oficina, etc.
    estado TEXT CHECK(estado IN ('Operativa', 'En Mantenimiento', 'Dañada', 'Fuera de Servicio')) DEFAULT 'Operativa',
    fecha_adquisicion DATE,
    valor_adquisicion REAL,
    vida_util_anos INTEGER,
    responsable TEXT, -- Empleado asignado
    observaciones TEXT,
    stock_total INTEGER DEFAULT 1,
    stock_bodega INTEGER DEFAULT 0,
    id_trabajador INTEGER,
    foto_path TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_finca) REFERENCES finca(id)
);

-- Tabla de mantenimientos de herramientas
CREATE TABLE IF NOT EXISTS mantenimiento_herramienta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    herramienta_id INTEGER NOT NULL,
    tipo_mantenimiento TEXT CHECK(tipo_mantenimiento IN ('Preventivo', 'Correctivo', 'Calibración', 'Inspección')),
    fecha_mantenimiento DATE NOT NULL,
    descripcion TEXT,
    costo REAL,
    proveedor_servicio TEXT,
    proximo_mantenimiento DATE,
    realizado_por TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (herramienta_id) REFERENCES herramienta(id) ON DELETE CASCADE
);

-- Tabla legacy de inventario (opcional - mantener por compatibilidad)
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT NOT NULL,
    categoria TEXT CHECK(categoria IN ('Medicamento', 'Alimento', 'Equipo', 'Insumo')),
    cantidad_actual REAL NOT NULL,
    cantidad_minima REAL,
    unidad TEXT NOT NULL,
    precio_unitario REAL,
    ubicacion TEXT,
    proveedor TEXT,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de eventos, opcional
CREATE TABLE IF NOT EXISTS evento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_evento DATE NOT NULL,
    tipo_evento TEXT CHECK(tipo_evento IN ('Sanitario', 'Reproductivo', 'Movimiento', 'General')),
    animal_id INTEGER,
    lote_id INTEGER,
    completado BOOLEAN DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animal (id),
    FOREIGN KEY (lote_id) REFERENCES lote (id)
);

-- Tabla de ventas (para el módulo de ventas)
CREATE TABLE IF NOT EXISTS venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    precio_total REAL NOT NULL,
    comprador TEXT,
    motivo_venta TEXT, -- Puede referenciar motivo_venta.codigo
    destino_venta TEXT, -- Puede referenciar destino_venta.codigo
    observaciones TEXT,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animal (id)
);

-- Tabla de empleados (módulo Configuración/ Nómina)
CREATE TABLE IF NOT EXISTS empleado (
    codigo TEXT PRIMARY KEY,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    numero_identificacion TEXT UNIQUE,
    cargo TEXT,
    estado_actual TEXT,
    fecha_ingreso DATE,
    fecha_contrato DATE,
    fecha_nacimiento DATE,
    fecha_retiro DATE,
    sexo TEXT,
    estado_civil TEXT,
    telefono TEXT,
    direccion TEXT,
    salario_diario REAL,
    bono_alimenticio REAL,
    bono_productividad REAL,
    seguro_social REAL,
    otras_deducciones REAL,
    foto_path TEXT,
    comentarios TEXT,
    id_finca INTEGER,
    estado TEXT DEFAULT 'Activo',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_finca) REFERENCES finca(id)
);

-- Tabla de pagos de nómina
CREATE TABLE IF NOT EXISTS pago_nomina (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_empleado TEXT NOT NULL,
    fecha_pago DATE DEFAULT CURRENT_DATE,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    dias_trabajados INTEGER NOT NULL,
    salario_base REAL NOT NULL,
    bonos REAL NOT NULL,
    deducciones REAL NOT NULL,
    total_pagado REAL NOT NULL,
    estado TEXT DEFAULT 'Pagado',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (codigo_empleado) REFERENCES empleado(codigo)
);

-- Catálogos de ventas
CREATE TABLE IF NOT EXISTS motivo_venta (
    codigo TEXT PRIMARY KEY,
    descripcion TEXT NOT NULL,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo'
);

CREATE TABLE IF NOT EXISTS destino_venta (
    codigo TEXT PRIMARY KEY,
    descripcion TEXT NOT NULL,
    tipo_destino TEXT,
    nit TEXT,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo'
);

CREATE TABLE IF NOT EXISTS sector (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    comentario TEXT,
    finca_id INTEGER, -- Relación directa con finca (agregado en migración 005, ahora parte del esquema base)
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (finca_id) REFERENCES finca(id)
);

-- Catálogo de calidad de animal (atributos de clasificación)
CREATE TABLE IF NOT EXISTS calidad_animal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catálogo de tipos de explotación
CREATE TABLE IF NOT EXISTS tipo_explotacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    categoria TEXT,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catálogo de condiciones corporales (escala BCS)
CREATE TABLE IF NOT EXISTS condicion_corporal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    puntuacion INTEGER,
    escala TEXT,
    especie TEXT,
    caracteristicas TEXT,
    recomendaciones TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de diagnósticos veterinarios
CREATE TABLE IF NOT EXISTS diagnostico_veterinario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    tipo TEXT,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catálogo de procedencias (origen de animales)
CREATE TABLE IF NOT EXISTS procedencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    tipo_procedencia TEXT,
    ubicacion TEXT,
    comentario TEXT,
    estado TEXT DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- Índices de rendimiento
-- =============================
CREATE INDEX IF NOT EXISTS idx_animal_codigo ON animal (codigo);
CREATE INDEX IF NOT EXISTS idx_animal_estado ON animal (estado);
CREATE INDEX IF NOT EXISTS idx_animal_finca ON animal (id_finca);
CREATE INDEX IF NOT EXISTS idx_animal_raza ON animal (raza_id);
CREATE INDEX IF NOT EXISTS idx_animal_lote ON animal (lote_id);
CREATE INDEX IF NOT EXISTS idx_animal_sector ON animal (id_sector);
CREATE INDEX IF NOT EXISTS idx_venta_fecha ON venta (fecha);
CREATE INDEX IF NOT EXISTS idx_venta_animal ON venta (animal_id);
CREATE INDEX IF NOT EXISTS idx_tratamiento_animal_fecha ON tratamiento (id_animal, fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_empleado_estado ON empleado (estado_actual);
CREATE INDEX IF NOT EXISTS idx_potrero_finca ON potrero (id_finca);
CREATE INDEX IF NOT EXISTS idx_movimiento_animal ON movimiento (animal_id);
CREATE INDEX IF NOT EXISTS idx_comentario_animal_fecha ON comentario (id_animal, fecha);
CREATE INDEX IF NOT EXISTS idx_peso_animal_fecha ON peso (animal_id, fecha);
CREATE INDEX IF NOT EXISTS idx_leche_animal_fecha ON produccion_leche (animal_id, fecha);
CREATE INDEX IF NOT EXISTS idx_muerte_animal ON muerte (animal_id);
CREATE INDEX IF NOT EXISTS idx_diag_evento_animal_fecha ON diagnostico_evento (animal_id, fecha);
CREATE INDEX IF NOT EXISTS idx_sector_codigo ON sector (codigo);
CREATE INDEX IF NOT EXISTS idx_sector_finca ON sector (finca_id);
CREATE INDEX IF NOT EXISTS idx_calidad_animal_codigo ON calidad_animal (codigo);
CREATE INDEX IF NOT EXISTS idx_tipo_explotacion_codigo ON tipo_explotacion (codigo);
CREATE INDEX IF NOT EXISTS idx_condicion_corporal_codigo ON condicion_corporal (codigo);
CREATE INDEX IF NOT EXISTS idx_procedencia_codigo ON procedencia (codigo);

-- Índices para módulos nuevos
CREATE INDEX IF NOT EXISTS idx_insumo_codigo ON insumo (codigo);
CREATE INDEX IF NOT EXISTS idx_insumo_finca ON insumo (id_finca);
CREATE INDEX IF NOT EXISTS idx_insumo_categoria ON insumo (categoria);
CREATE INDEX IF NOT EXISTS idx_insumo_estado ON insumo (estado);
CREATE INDEX IF NOT EXISTS idx_mov_insumo_insumo ON movimiento_insumo (insumo_id);
CREATE INDEX IF NOT EXISTS idx_mov_insumo_fecha ON movimiento_insumo (fecha_movimiento);
CREATE INDEX IF NOT EXISTS idx_mov_insumo_tipo ON movimiento_insumo (tipo_movimiento);
CREATE INDEX IF NOT EXISTS idx_herramienta_codigo ON herramienta (codigo);
CREATE INDEX IF NOT EXISTS idx_herramienta_finca ON herramienta (id_finca);
CREATE INDEX IF NOT EXISTS idx_herramienta_estado ON herramienta (estado);
CREATE INDEX IF NOT EXISTS idx_mant_herramienta ON mantenimiento_herramienta (herramienta_id);
CREATE INDEX IF NOT EXISTS idx_mant_fecha ON mantenimiento_herramienta (fecha_mantenimiento);
CREATE INDEX IF NOT EXISTS idx_reproduccion_animal ON reproduccion (animal_id);
CREATE INDEX IF NOT EXISTS idx_reproduccion_estado ON reproduccion (estado);
-- Índice compuesto para mejorar consultas de nómina por empleado y período
CREATE INDEX IF NOT EXISTS idx_pago_nomina_empleado_periodo ON pago_nomina (codigo_empleado, periodo_inicio, periodo_fin);
-- Índice de lote-finca si la migración ya agregó la columna
CREATE INDEX IF NOT EXISTS idx_lote_finca ON lote (finca_id);
-- Trigger para mantener fecha_actualizacion coherente al modificar animales
CREATE TRIGGER IF NOT EXISTS trg_animal_update
AFTER UPDATE ON animal
BEGIN
    UPDATE animal SET fecha_actualizacion = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
"""

# Datos básicos para inicialización (vacío para entregar base limpia sin registros)
DATOS_BASICOS = """"""

# Migración ligera: asegurar columnas esperadas en tablas existentes
def _migrar_esquema_basico(conn: sqlite3.Connection) -> None:
    try:
        cursor = conn.cursor()

        def columnas_existentes(tabla: str) -> List[str]:
            cursor.execute(f"PRAGMA table_info({tabla})")
            return [row[1] for row in cursor.fetchall()]

        def asegurar_columnas(tabla: str, columnas: Dict[str, str]):
            existentes = set(columnas_existentes(tabla))
            for nombre, definicion in columnas.items():
                if nombre not in existentes:
                    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {definicion}")

        # Animal (post-normalización: sin columnas legacy 'raza', 'id_raza', 'id_lote')
        asegurar_columnas("animal", {
            "raza_id": "INTEGER",
            "id_finca": "INTEGER",
            "id_potrero": "INTEGER",
            "lote_id": "INTEGER",
            "id_sector": "INTEGER",
            "id_vendedor": "INTEGER",
            "inventariado": "INTEGER DEFAULT 0",
            "salud": "TEXT",
            "tipo_ingreso": "TEXT",
            "precio_compra": "REAL",
            "id_padre": "INTEGER",
            "id_madre": "INTEGER",
            "tipo_concepcion": "TEXT",
            "color": "TEXT",
            "hierro": "TEXT",
            "numero_hierros": "INTEGER",
            "composicion_racial": "TEXT",
            "comentarios": "TEXT",
            "fecha_registro": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "grupo_compra": "TEXT",
            "condicion_corporal": "TEXT",
            "ultimo_peso": "REAL",
            "fecha_ultimo_peso": "DATE",
            "categoria": "TEXT",
            "procedencia_id": "INTEGER"
        })

        # Raza
        asegurar_columnas("raza", {
            "codigo": "TEXT",
            "tipo_ganado": "TEXT",
            "especie": "TEXT",
            "estado": "TEXT DEFAULT 'Activa'"
        })

        # Finca
        # (creada por esquema)

        # Potrero
        asegurar_columnas("potrero", {
            "id_sector": "INTEGER"
        })

        # Empleado
        asegurar_columnas("empleado", {
            "id_finca": "INTEGER"
        })

        # Insumo
        asegurar_columnas("insumo", {
            "responsable": "TEXT",
            "observaciones": "TEXT",
            "id_trabajador": "INTEGER",
            "stock_bodega": "REAL DEFAULT 0",
            "foto_path": "TEXT",
            "fecha_adquisicion": "DATE"
        })

        # Herramienta
        asegurar_columnas("herramienta", {
            "stock_total": "INTEGER DEFAULT 1",
            "stock_bodega": "INTEGER DEFAULT 0",
            "id_trabajador": "INTEGER",
            "foto_path": "TEXT"
        })

        # Venta
        asegurar_columnas("venta", {
            "comprador": "TEXT",
            "motivo_venta": "TEXT",
            "destino_venta": "TEXT",
            "observaciones": "TEXT"
        })

        # Sector (asegurar columna finca_id si BD procede de versión previa a inclusión en esquema base)
        asegurar_columnas("sector", {
            "finca_id": "INTEGER"
        })

        # Lote (según migración 005)
        asegurar_columnas("lote", {
            "finca_id": "INTEGER"
        })

        # Destino de venta (nuevos campos usados en UI)
        asegurar_columnas("destino_venta", {
            "nit": "TEXT",
            "direccion": "TEXT",
            "telefono": "TEXT",
            "email": "TEXT"
        })

        # Asegurar tabla de ajustes
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                clave TEXT PRIMARY KEY,
                valor TEXT
            )
            """
        )

        conn.commit()
    except Exception as e:
        logger.warning(f"Migración ligera: {e}")

# Prueba básica de la base de datos
if __name__ == "__main__":
    print("🧪 Probando módulo de base de datos...")
    
    # Verificar conexión
    try:
        with get_db_connection() as conn:
            print("✅ Conexión a BD exitosa")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    
    # Verificar estructura
    if verificar_base_datos():
        print("✅ Estructura de BD válida")
    else:
        print("❌ Estructura de BD inválida o no existe")
        
    # Mostrar tablas
    tablas = obtener_tablas()
    print(f"📊 Tablas en BD: {len(tablas)}")
    for tabla in tablas:
        print(f"  - {tabla}")
        
    print("✅ Módulo de base de datos listo")