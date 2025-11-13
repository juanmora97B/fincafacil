import sqlite3
import os
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="database/fincafacil.db"):
        self.db_path = db_path
        self.ensure_database()

    def ensure_database(self):
        """Asegura que la base de datos y las tablas existan"""
        os.makedirs("database", exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla fincas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finca (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    ubicacion TEXT,
                    estado TEXT DEFAULT 'Activa'
                )
            """)
            
            # Tabla potreros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS potrero (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_finca INTEGER,
                    nombre TEXT NOT NULL,
                    area_hectareas REAL,
                    capacidad_maxima INTEGER,
                    estado TEXT DEFAULT 'Activo',
                    FOREIGN KEY (id_finca) REFERENCES finca (id)
                )
            """)
            
            # En el método ensure_database(), agregar después de la tabla lotes:

            # Tabla sectores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sector (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla lotes (actualizada)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lote (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    criterio TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla grupos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grupo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_finca INTEGER,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    criterio TEXT,
                    estado TEXT DEFAULT 'Activo',
                    FOREIGN KEY (id_finca) REFERENCES finca (id)
                )
            """)

            # Tabla diagnosticos_veterinarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diagnostico_veterinario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    tipo_diagnostico TEXT,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla condiciones_corporales
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS condicion_corporal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla tipos_explotacion
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tipo_explotacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla procedencias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS procedencia (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla destinos_ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS destino_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla motivos_venta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS motivo_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla causas_muerte
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS causa_muerte (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla calidad_animal
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calidad_animal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    comentario TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)

            # Tabla proveedores
            cursor.execute("""
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
            """)

            # Tabla empleados (expandida)
            cursor.execute("""
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
            """)

            # Tabla razas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raza (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    tipo_ganado TEXT,
                    estado TEXT DEFAULT 'Activa'
                )
            """)
            
            # Tabla vendedores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendedor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    direccion TEXT,
                    email TEXT,
                    estado TEXT DEFAULT 'Activo'
                )
            """)
            
            # Tabla animales (expandida)
            cursor.execute("""
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
                    tipo_concepcion TEXT, -- 'Monta' o 'Inseminación'
                    salud TEXT DEFAULT 'Sano',
                    estado TEXT DEFAULT 'Activo',
                    inventariado INTEGER DEFAULT 0, -- 0: No, 1: Sí
                    color TEXT,
                    hierro TEXT,
                    numero_hierros INTEGER,
                    composicion_racial TEXT,
                    comentarios TEXT,
                    foto_path TEXT,
                    fecha_registro TEXT,
                    -- Compatibilidad con módulos actuales
                    raza TEXT,
                    potrero TEXT,
                    FOREIGN KEY (id_finca) REFERENCES finca (id),
                    FOREIGN KEY (id_raza) REFERENCES raza (id),
                    FOREIGN KEY (id_potrero) REFERENCES potrero (id),
                    FOREIGN KEY (id_lote) REFERENCES lote (id),
                    FOREIGN KEY (id_grupo) REFERENCES grupo (id),
                    FOREIGN KEY (id_vendedor) REFERENCES vendedor (id),
                    FOREIGN KEY (id_padre) REFERENCES animal (id),
                    FOREIGN KEY (id_madre) REFERENCES animal (id)
                )
            """)

            # Tabla pesos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS peso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_animal INTEGER,
                    fecha TEXT,
                    peso REAL,
                    tipo_peso TEXT, -- 'Rutina', 'Destete', 'Venta', etc.
                    comentario TEXT,
                    FOREIGN KEY (id_animal) REFERENCES animal (id)
                )
            """)

            # Tabla tratamientos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tratamiento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_animal INTEGER,
                    fecha TEXT,
                    tipo_tratamiento TEXT,
                    producto TEXT,
                    dosis TEXT,
                    veterinario TEXT,
                    comentario TEXT,
                    FOREIGN KEY (id_animal) REFERENCES animal (id)
                )
            """)

            # Tabla reubicaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reubicacion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_animal INTEGER,
                    potrero_anterior TEXT,
                    potrero_nuevo TEXT,
                    fecha TEXT,
                    motivo TEXT,
                    FOREIGN KEY (id_animal) REFERENCES animal (id)
                )
            """)
            
            # Tabla comentarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comentario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_animal INTEGER,
                    fecha TEXT,
                    autor TEXT,
                    nota TEXT,
                    FOREIGN KEY (id_animal) REFERENCES animales (id)
                )
            """)
            
            # Insertar datos básicos
            self.insertar_datos_basicos(cursor)
            
            conn.commit()

    def insertar_datos_basicos(self, cursor):
        """Inserta datos básicos para que el sistema funcione"""
        # Insertar fincas de ejemplo
        fincas = [
            ('Finca El Prado', 'Finca principal para ganado de leche', 'Valle del Cauca'),
            ('Finca El León', 'Finca para engorde y ceba', 'Córdoba')
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO finca (nombre, descripcion, ubicacion) VALUES (?, ?, ?)",
            fincas
        )
        
        # Insertar razas comunes
        razas = [
            ('Holstein', 'Ganado lechero especializado', 'Lechero'),
            ('Angus', 'Ganado de carne de alta calidad', 'Carne'),
            ('Brahman', 'Ganado resistente al clima tropical', 'Doble propósito'),
            ('Gyr', 'Ganado lechero tropical', 'Lechero'),
            ('Cebú', 'Ganado resistente', 'Carne')
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO raza (nombre, descripcion, tipo_ganado) VALUES (?, ?, ?)",
            razas
        )
        
        # Insertar vendedores de ejemplo
        vendedores = [
            ('Ganadería San Marcos', '3101234567', 'Vía a Cereté', 'sanmarcos@email.com'),
            ('Hato La Esperanza', '3129876543', 'Km 15 Carretera', 'esperanza@email.com'),
            ('Cabaña El Triunfo', '3155558888', 'Finca El Triunfo', 'triunfo@email.com')
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO vendedor (nombre, telefono, direccion, email) VALUES (?, ?, ?, ?)",
            vendedores
        )

    def get_connection(self):
        """Retorna una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)

# Instancia global para usar en toda la aplicación
db = DatabaseManager()