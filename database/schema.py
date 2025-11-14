# database/schema.py

CREATE_TABLES = [
    # -------------------------
    # Tabla de versión del esquema para migraciones
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS meta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schema_version INTEGER NOT NULL
    );
    """,

    # -------------------------
    # Tabla FINCAS
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS finca (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        municipio TEXT,
        departamento TEXT
    );
    """,

    # -------------------------
    # Tabla ESTADO POTRERO
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS estado_potrero (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """,

    # -------------------------
    # Tabla POTRERO
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS potrero (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        area REAL,
        sector TEXT,
        id_finca INTEGER NOT NULL,
        id_estado_potrero INTEGER,
        FOREIGN KEY (id_finca) REFERENCES finca (id) ON DELETE CASCADE,
        FOREIGN KEY (id_estado_potrero) REFERENCES estado_potrero (id)
    );
    """,


    # -------------------------
    # Tabla TIPO EXPLOTACIÓN
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS tipo_explotacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """,

    # -------------------------
    # Tabla INVENTARIADO
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS inventariado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """,

    # -------------------------
    # Tabla TIPO CONCEPCIÓN
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS tipo_concepcion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """,

    # -------------------------
    # Tabla ANIMAL
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS animal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT,
        id_finca INTEGER,
        id_potrero INTEGER,
        id_tipo_explotacion INTEGER,
        id_inventariado INTEGER,
        id_tipo_concepcion INTEGER,
        numero_hierros INTEGER,
        fecha_nacimiento TEXT,
        sexo TEXT,
        FOREIGN KEY (id_finca) REFERENCES finca (id),
        FOREIGN KEY (id_potrero) REFERENCES potrero (id),
        FOREIGN KEY (id_tipo_explotacion) REFERENCES tipo_explotacion (id),
        FOREIGN KEY (id_inventariado) REFERENCES inventariado (id),
        FOREIGN KEY (id_tipo_concepcion) REFERENCES tipo_concepcion (id)
    );
    """,

    # -------------------------
    # Tabla CRITERIO
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS criterio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """,

    # -------------------------
    # Tabla LOTES
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS lote (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        id_criterio INTEGER,
        FOREIGN KEY (id_criterio) REFERENCES criterio (id)
    );
    """,

    # -------------------------
    # Tabla GRUPOS
    # -------------------------
    """
    CREATE TABLE IF NOT EXISTS grupo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        id_criterio INTEGER,
        FOREIGN KEY (id_criterio) REFERENCES criterio (id)
    );
    """
]


# -------------------------
# ÍNDICES RECOMENDADOS
# -------------------------
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_animal_codigo ON animal (codigo);",
    "CREATE INDEX IF NOT EXISTS idx_potrero_codigo ON potrero (codigo);",
    "CREATE INDEX IF NOT EXISTS idx_finca_codigo ON finca (codigo);",
    "CREATE INDEX IF NOT EXISTS idx_lote_codigo ON lote (codigo);",
    "CREATE INDEX IF NOT EXISTS idx_grupo_codigo ON grupo (codigo);"
]

# -------------------------
# Versión de esquema actual
# -------------------------
SCHEMA_VERSION = 1
