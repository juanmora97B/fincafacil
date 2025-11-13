"""
Definiciones unificadas del esquema de la base de datos.
Este archivo centraliza todas las definiciones de tablas para mantener consistencia.
"""

# Diccionario con todas las tablas en ORDEN CORRECTO (para evitar problemas de dependencias)
create_tables = {
    # Tablas maestras básicas (sin dependencias)
    'finca': """
        CREATE TABLE IF NOT EXISTS finca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            propietario TEXT,
            ubicacion TEXT,
            area_hectareas REAL,
            telefono TEXT,
            email TEXT,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,

    'vendedor': """
        CREATE TABLE IF NOT EXISTS vendedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'raza': """
        CREATE TABLE IF NOT EXISTS raza (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            especie TEXT,
            tipo_ganado TEXT,
            descripcion TEXT,
            caracteristicas TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'lote': """
        CREATE TABLE IF NOT EXISTS lote (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            criterio TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'grupo': """
        CREATE TABLE IF NOT EXISTS grupo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            criterio TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    # Tablas con dependencias básicas
    'sector': """
        CREATE TABLE IF NOT EXISTS sector (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            id_finca INTEGER,
            area_hectareas REAL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            FOREIGN KEY (id_finca) REFERENCES finca (id)
        )
    """,

    'potrero': """
        CREATE TABLE IF NOT EXISTS potrero (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            id_sector INTEGER,
            area_hectareas REAL,
            capacidad_animales INTEGER,
            tipo_pasto TEXT,
            estado_potrero TEXT,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            FOREIGN KEY (id_sector) REFERENCES sector (id)
        )
    """,

    # Tabla animal (depende de varias)
    'animal': """
        CREATE TABLE IF NOT EXISTS animal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_finca INTEGER,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT,
            tipo_ingreso TEXT, -- 'Nacimiento' o 'Compra'
            sexo TEXT,
            id_raza INTEGER,
            id_potrero INTEGER,
            id_lote INTEGER,
            id_grupo INTEGER,
            fecha_nacimiento TEXT,
            fecha_compra TEXT,
            peso_nacimiento REAL,
            peso_compra REAL,
            id_vendedor INTEGER,
            precio_compra REAL,
            id_padre INTEGER,
            id_madre INTEGER,
            tipo_concepcion TEXT,
            salud TEXT DEFAULT 'Sano',
            estado TEXT DEFAULT 'Activo',
            inventariado INTEGER DEFAULT 0,
            color TEXT,
            hierro TEXT,
            numero_hierros INTEGER,
            composicion_racial TEXT,
            comentarios TEXT,
            foto_path TEXT,
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_finca) REFERENCES finca (id),
            FOREIGN KEY (id_raza) REFERENCES raza (id),
            FOREIGN KEY (id_potrero) REFERENCES potrero (id),
            FOREIGN KEY (id_lote) REFERENCES lote (id),
            FOREIGN KEY (id_grupo) REFERENCES grupo (id),
            FOREIGN KEY (id_vendedor) REFERENCES vendedor (id),
            FOREIGN KEY (id_padre) REFERENCES animal (id),
            FOREIGN KEY (id_madre) REFERENCES animal (id)
        )
    """,

    # Tablas maestras adicionales
    'diagnostico_veterinario': """
        CREATE TABLE IF NOT EXISTS diagnostico_veterinario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            tipo_diagnostico TEXT,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'condicion_corporal': """
        CREATE TABLE IF NOT EXISTS condicion_corporal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            puntuacion REAL,
            escala TEXT,
            especie TEXT,
            caracteristicas TEXT,
            recomendaciones TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'tipo_explotacion': """
        CREATE TABLE IF NOT EXISTS tipo_explotacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'procedencia': """
        CREATE TABLE IF NOT EXISTS procedencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            tipo_procedencia TEXT,
            ubicacion TEXT,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'destino_venta': """
        CREATE TABLE IF NOT EXISTS destino_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            tipo_destino TEXT,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'motivo_venta': """
        CREATE TABLE IF NOT EXISTS motivo_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'causa_muerte': """
        CREATE TABLE IF NOT EXISTS causa_muerte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            tipo_causa TEXT,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'calidad_animal': """
        CREATE TABLE IF NOT EXISTS calidad_animal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            descripcion TEXT NOT NULL,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'proveedor': """
        CREATE TABLE IF NOT EXISTS proveedor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            telefono TEXT,
            direccion TEXT,
            email TEXT,
            tipo_servicio TEXT,
            comentario TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    'empleado': """
        CREATE TABLE IF NOT EXISTS empleado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            numero_identificacion TEXT UNIQUE NOT NULL,
            cargo TEXT,
            estado_actual TEXT DEFAULT 'Activo',
            fecha_ingreso TEXT,
            fecha_contrato TEXT,
            fecha_nacimiento TEXT,
            fecha_retiro TEXT,
            sexo TEXT,
            estado_civil TEXT,
            telefono TEXT,
            direccion TEXT,
            salario_diario REAL DEFAULT 0,
            bono_alimenticio REAL DEFAULT 0,
            bono_productividad REAL DEFAULT 0,
            seguro_social REAL DEFAULT 0,
            otras_deducciones REAL DEFAULT 0,
            foto_path TEXT,
            comentarios TEXT,
            estado TEXT DEFAULT 'Activo'
        )
    """,

    # Tablas transaccionales (dependen de animal)
    'peso': """
        CREATE TABLE IF NOT EXISTS peso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_animal INTEGER,
            fecha TEXT,
            peso REAL,
            tipo_peso TEXT,
            comentario TEXT,
            FOREIGN KEY (id_animal) REFERENCES animal (id)
        )
    """,

    'tratamiento': """
        CREATE TABLE IF NOT EXISTS tratamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_animal INTEGER,
            fecha TEXT,
            tipo_tratamiento TEXT,
            producto TEXT,
            dosis TEXT,
            fecha_proxima TEXT,
            veterinario TEXT,
            comentario TEXT,
            FOREIGN KEY (id_animal) REFERENCES animal (id)
        )
    """,

    'reubicacion': """
        CREATE TABLE IF NOT EXISTS reubicacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_animal INTEGER,
            id_potrero_anterior INTEGER,
            id_potrero_nuevo INTEGER,
            fecha TEXT,
            motivo TEXT,
            FOREIGN KEY (id_animal) REFERENCES animal (id),
            FOREIGN KEY (id_potrero_anterior) REFERENCES potrero (id),
            FOREIGN KEY (id_potrero_nuevo) REFERENCES potrero (id)
        )
    """,

    'comentario': """
        CREATE TABLE IF NOT EXISTS comentario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_animal INTEGER,
            fecha TEXT,
            autor TEXT,
            nota TEXT,
            FOREIGN KEY (id_animal) REFERENCES animal (id)
        )
    """,

    'venta': """
        CREATE TABLE IF NOT EXISTS venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_animal INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            precio_total REAL NOT NULL,
            id_motivo_venta INTEGER,
            id_destino_venta INTEGER,
            observaciones TEXT,
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_animal) REFERENCES animal (id),
            FOREIGN KEY (id_motivo_venta) REFERENCES motivo_venta (id),
            FOREIGN KEY (id_destino_venta) REFERENCES destino_venta (id)
        )
    """
}