from contextlib import contextmanager
from typing import Iterator
import errno

# -------------------------
# Helper: asegurar carpeta
# -------------------------
def _ensure_db_dir(path: Optional[str] = None) -> None:
    path = path or DB_PATH
    dirpath = os.path.dirname(path)
    try:
        os.makedirs(dirpath, exist_ok=True)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            log.error("No se pudo crear el directorio de la BD: %s", dirpath)
            raise

# -------------------------
# Context manager de conexión (recomendado)
# -------------------------
@contextmanager
def connection_context(db_path: Optional[str] = None) -> Iterator[sqlite3.Connection]:
    """Context manager para abrir/usar/cerrar una conexión correctamente."""
    conn = get_db_connection(db_path)
    try:
        yield conn
    finally:
        try:
            conn.close()
        except Exception:
            pass

# -------------------------
# Init DB usando schema.create_tables
# -------------------------
def init_database(use_create_tables: bool = True, db_path: Optional[str] = None):
    """
    Inicializa la BD.
    - Si use_create_tables=True, importa database.schema.create_tables y aplica en orden.
    - Crea índices básicos después de crear tablas.
    """
    path = db_path or DB_PATH
    _ensure_db_dir(path)

    # Si ya existe y tiene tablas, no recreamos (solo si no hay tablas)
    if check_database_exists(path):
        # Si existe, comprobar si al menos hay una tabla 'animal' o 'finca'
        with connection_context(path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animal'")
            if cur.fetchone():
                log.info("BD ya inicializada (tabla 'animal' detectada).")
                return

    # Crear tablas desde schema.create_tables si existe
    if use_create_tables:
        try:
            from database import schema
            create_tables = getattr(schema, "create_tables", {})
        except Exception as e:
            log.error("No se pudo importar database.schema: %s", e)
            create_tables = {}

        if not create_tables:
            log.warning("No se encontró create_tables en schema. Creando BD vacía.")
            # crear archivo vacío si no existe
            conn = get_db_connection(path)
            conn.commit()
            conn.close()
            return

        with connection_context(path) as conn:
            cur = conn.cursor()
            # activar fk por seguridad (aunque get_db_connection ya lo hace)
            cur.execute("PRAGMA foreign_keys = ON;")

            tables_created = 0
            for name, stmt in create_tables.items():
                try:
                    cur.execute(stmt)
                    tables_created += 1
                    log.info("Tabla creada/asegurada: %s", name)
                except sqlite3.Error as e:
                    log.warning("No se pudo crear tabla %s: %s", name, e)

            conn.commit()

            # Crear índices recomendados
            _create_recommended_indexes(cur)
            conn.commit()

            # crear tabla meta si no existe (versionamiento)
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS meta (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    );
                """)
                conn.commit()
            except Exception as e:
                log.warning("No se pudo crear tabla meta: %s", e)

            log.info("Inicialización completada. Tablas creadas: %d", tables_created)
    else:
        # Fallback: crear archivo si no existe
        conn = get_db_connection(path)
        conn.commit()
        conn.close()

# -------------------------
# Índices recomendados (ajustar si cambias nombres de tablas)
# -------------------------
def _create_recommended_indexes(cursor: sqlite3.Cursor):
    """
    Crea índices básicos que mejoran rendimiento.
    Modifícalo si cambias nombres de tablas/columnas.
    """
    indexes = [
        # animal
        ("idx_animal_codigo", "animal", "codigo"),
        ("idx_animal_potrero", "animal", "id_potrero"),
        ("idx_animal_raza", "animal", "id_raza"),
        # potrero / sector / finca
        ("idx_potrero_sector", "potrero", "id_sector"),
        ("idx_sector_finca", "sector", "id_finca"),
        ("idx_finca_codigo", "finca", "codigo"),
        # ventas / peso / tratamiento
        ("idx_venta_animal", "venta", "id_animal"),
        ("idx_peso_animal", "peso", "id_animal"),
        ("idx_tratamiento_animal", "tratamiento", "id_animal"),
    ]

    for idx_name, table, column in indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column});")
            log.debug("Índice creado/asegurado: %s", idx_name)
        except Exception as e:
            log.warning("No se pudo crear índice %s: %s", idx_name, e)
