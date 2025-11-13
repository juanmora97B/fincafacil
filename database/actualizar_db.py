import sqlite3
import os

def actualizar_base_datos():
    db_path = "database/fincafacil.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        print("Actualizando base de datos...")
        
        # ======================
        # TABLA FINCAS
        # ======================
        cursor.execute("""
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
        """)
        
        # ======================
        # TABLA SECTORES
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sector (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                id_finca INTEGER,
                area_hectareas REAL,
                descripcion TEXT,
                estado TEXT DEFAULT 'Activo',
                FOREIGN KEY (id_finca) REFERENCES fincas (id)
            )
        """)
        
        # ======================
        # TABLA POTREROS
        # ======================
        cursor.execute("""
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
                FOREIGN KEY (id_sector) REFERENCES sectores (id)
            )
        """)
        
        # ======================
        # TABLA LOTES
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lote (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA RAZAS
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raza (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                especie TEXT,
                descripcion TEXT,
                caracteristicas TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA PROVEEDORES
        # ======================
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
        
        # ======================
        # TABLA CALIDAD ANIMAL
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calidad_animal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                comentario TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA MOTIVOS VENTA
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS motivo_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                comentario TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA CAUSAS MUERTE
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS causa_muerte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                tipo_causa TEXT,
                comentario TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA DESTINOS VENTA
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS destino_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                tipo_destino TEXT,
                comentario TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA PROCEDENCIAS
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS procedencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                tipo_procedencia TEXT,
                ubicacion TEXT,
                comentario TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA TIPOS EXPLOTACION
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipo_explotacion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                categoria TEXT,
                comentario TEXT,
                estado TEXT DEFAULT 'Activo'
            )
        """)
        
        # ======================
        # TABLA CONDICIONES CORPORALES
        # ======================
        cursor.execute("""
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
        """)
        
        # ======================
        # VERIFICAR Y AGREGAR COLUMNAS FALTANTES
        # ======================
        
        # Función para agregar columnas si no existen
        def agregar_columna(tabla, columna, tipo):
            try:
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
                print(f"Columna {columna} agregada a {tabla}")
            except sqlite3.OperationalError:
                pass  # La columna ya existe
        
        # Agregar columnas faltantes
        agregar_columna("proveedores", "tipo_servicio", "TEXT")
        agregar_columna("proveedores", "comentario", "TEXT")
        agregar_columna("calidad_animal", "comentario", "TEXT")
        agregar_columna("motivos_venta", "comentario", "TEXT")
        agregar_columna("causas_muerte", "tipo_causa", "TEXT")
        agregar_columna("causas_muerte", "comentario", "TEXT")
        agregar_columna("destinos_venta", "tipo_destino", "TEXT")
        agregar_columna("destinos_venta", "comentario", "TEXT")
        agregar_columna("procedencias", "tipo_procedencia", "TEXT")
        agregar_columna("procedencias", "ubicacion", "TEXT")
        agregar_columna("procedencias", "comentario", "TEXT")
        agregar_columna("tipos_explotacion", "categoria", "TEXT")
        agregar_columna("tipos_explotacion", "comentario", "TEXT")
        agregar_columna("condiciones_corporales", "puntuacion", "REAL")
        agregar_columna("condiciones_corporales", "escala", "TEXT")
        agregar_columna("condiciones_corporales", "especie", "TEXT")
        agregar_columna("condiciones_corporales", "caracteristicas", "TEXT")
        agregar_columna("condiciones_corporales", "recomendaciones", "TEXT")
        
        # Columnas importantes para razas (compatibilidad con conexion.py)
        agregar_columna("razas", "tipo_ganado", "TEXT")
        agregar_columna("razas", "especie", "TEXT")
        
        # Columnas para sectores (compatibilidad)
        agregar_columna("sectores", "comentario", "TEXT")
        
        # Columnas para potreros (compatibilidad)
        agregar_columna("potreros", "id_finca", "INTEGER")
        agregar_columna("potreros", "sector", "TEXT")
        agregar_columna("potreros", "capacidad_maxima", "INTEGER")
        agregar_columna("potreros", "descripcion", "TEXT")
        
        # Columnas para lotes (compatibilidad)
        agregar_columna("lotes", "criterio", "TEXT")
        
        # Columnas para animales (compatibilidad)
        agregar_columna("animales", "id_finca", "INTEGER")
        agregar_columna("animales", "tipo_ingreso", "TEXT")
        agregar_columna("animales", "fecha_compra", "TEXT")
        agregar_columna("animales", "peso_nacimiento", "REAL")
        agregar_columna("animales", "peso_compra", "REAL")
        agregar_columna("animales", "id_vendedor", "INTEGER")
        agregar_columna("animales", "precio_compra", "REAL")
        agregar_columna("animales", "id_padre", "INTEGER")
        agregar_columna("animales", "id_madre", "INTEGER")
        agregar_columna("animales", "tipo_concepcion", "TEXT")
        agregar_columna("animales", "salud", "TEXT")
        agregar_columna("animales", "inventariado", "INTEGER")
        agregar_columna("animales", "color", "TEXT")
        agregar_columna("animales", "hierro", "TEXT")
        agregar_columna("animales", "numero_hierros", "INTEGER")
        agregar_columna("animales", "composicion_racial", "TEXT")
        agregar_columna("animales", "comentarios", "TEXT")
        agregar_columna("animales", "foto_path", "TEXT")
        agregar_columna("animales", "fecha_registro", "TEXT")
        
        # ======================
        # TABLA VENTAS
        # ======================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_animal INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                precio_total REAL NOT NULL,
                motivo_venta TEXT,
                destino_venta TEXT,
                observaciones TEXT,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_animal) REFERENCES animales (id)
            )
        """)
        
        # Agregar columna fecha_proxima a tratamientos si no existe
        try:
            cursor.execute("ALTER TABLE tratamiento ADD COLUMN fecha_proxima TEXT")
            print("Columna fecha_proxima agregada a tratamientos")
        except sqlite3.OperationalError:
            pass
        
        # Corregir nombre de tabla destinos_ventas (puede ser destinos_venta)
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='destinos_ventas'")
            if not cursor.fetchone():
                # Si no existe destinos_ventas, renombrar destinos_venta
                cursor.execute("ALTER TABLE destino_venta RENAME TO destinos_ventas")
                print("Tabla destinos_venta renombrada a destinos_ventas")
        except:
            pass
        
    conn.commit()
    print("Base de datos actualizada correctamente")

if __name__ == "__main__":
    actualizar_base_datos()