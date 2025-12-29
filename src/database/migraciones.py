"""
MIGRACIONES DE SCHEMA - FincaFácil
==================================

Agregaciones de tablas para:
- Sistema de usuarios y roles
- Auditoría y logs
- Tracking de cierres mensuales
- Tracking de KPIs

Se ejecutan automáticamente en asegurar_esquema_minimo()
"""

# Migraciones por orden de ejecución
MIGRACIONES_SISTEMA = [
    # Migración 1: Crear tabla de usuarios
    """
    CREATE TABLE IF NOT EXISTS usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        rol TEXT NOT NULL DEFAULT 'Operador', -- Rol por defecto
        estado TEXT NOT NULL DEFAULT 'activo',  -- activo, inactivo, bloqueado
        contraseña_hash TEXT,  -- Opcional, para login futuro
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_ultimo_acceso TIMESTAMP,
        intentos_fallidos INTEGER DEFAULT 0,
        bloqueado_hasta TIMESTAMP,
        notas TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_nombre ON usuario(nombre);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
    """,
    
    # Migración 2: Crear tabla de roles de usuario (soporte multi-rol futuro)
    """
    CREATE TABLE IF NOT EXISTS usuario_rol (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        rol TEXT NOT NULL,
        fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        asignado_por TEXT,  -- Usuario que asignó el rol
        motivo TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
        UNIQUE(usuario_id, rol)
    );
    CREATE INDEX IF NOT EXISTS idx_usuario_rol ON usuario_rol(usuario_id);
    """,
    
    # Migración 3: Crear tabla de auditoría
    """
    CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER,
        usuario_nombre TEXT,
        modulo TEXT NOT NULL,  -- 'ventas', 'nomina', 'cierre', etc.
        accion TEXT NOT NULL,  -- 'CREAR', 'EDITAR', 'ELIMINAR', 'PAGAR', etc.
        entidad TEXT,  -- Descripción de qué se modificó
        entidad_id INTEGER,
        resultado TEXT DEFAULT 'OK',  -- 'OK', 'ERROR', 'DENEGADO'
        detalles TEXT,  -- JSON con antes/después
        ip_address TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    );
    CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id);
    CREATE INDEX IF NOT EXISTS idx_auditoria_modulo ON auditoria(modulo);
    CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(timestamp);
    """,
    
    # Migración 4: Crear tabla de cierres mensuales (tracking)
    """
    CREATE TABLE IF NOT EXISTS cierre_mensual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        año INTEGER NOT NULL,
        mes INTEGER NOT NULL CHECK(mes BETWEEN 1 AND 12),
        fecha_cierre TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER,
        usuario_nombre TEXT,
        estado TEXT DEFAULT 'Completado',  -- Completado, Revertido
        resumen_ventas REAL,
        resumen_gastos REAL,
        resumen_nomina REAL,
        margen_neto REAL,
        observaciones TEXT,
        UNIQUE(año, mes),
        FOREIGN KEY (usuario_id) REFERENCES usuario(id)
    );
    CREATE INDEX IF NOT EXISTS idx_cierre_fecha ON cierre_mensual(año, mes);
    """,
    
    # Migración 5: Crear tabla de datos cerrados (bloqueo de edición)
    """
    CREATE TABLE IF NOT EXISTS datos_cerrados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        año INTEGER NOT NULL,
        mes INTEGER NOT NULL,
        modulo TEXT NOT NULL,  -- 'ventas', 'gastos', 'nomina', etc.
        entidad_id INTEGER,
        fecha_cierre TIMESTAMP,
        UNIQUE(año, mes, modulo, entidad_id)
    );
    CREATE INDEX IF NOT EXISTS idx_datos_cerrados ON datos_cerrados(año, mes, modulo);
    """,
    
    # Migración 6: Crear tabla de KPIs (preparación para BI)
    """
    CREATE TABLE IF NOT EXISTS kpi_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        año INTEGER,
        mes INTEGER,
        indicador TEXT NOT NULL,  -- 'margen_neto', 'produccion_diaria', etc.
        valor REAL NOT NULL,
        valor_previo REAL,  -- Para comparativas
        unidad TEXT,  -- '%', 'L', '$', etc.
        notas TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_kpi_tracking ON kpi_tracking(año, mes, indicador);
    """,
    
    # Migración 7: Crear tabla de alertas (reglas heurísticas simples)
    """
    CREATE TABLE IF NOT EXISTS alertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tipo TEXT NOT NULL,  -- 'gastos_altos', 'produccion_baja', etc.
        severidad TEXT DEFAULT 'INFO',  -- 'INFO', 'WARN', 'ERROR'
        mensaje TEXT NOT NULL,
        entidad TEXT,
        entidad_id INTEGER,
        resuelta INTEGER DEFAULT 0,
        fecha_resolucion TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_alertas_fecha ON alertas(timestamp);
    CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas(tipo);
    """,
    
    # Migración 8: Tabla de snapshots analíticos mensuales
    """
    CREATE TABLE IF NOT EXISTS bi_snapshots_mensual (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        año INTEGER NOT NULL,
        mes INTEGER NOT NULL,
        data_json TEXT NOT NULL,
        fecha_snapshot TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        version INTEGER DEFAULT 1,
        generado_por TEXT DEFAULT 'Sistema',
        md5_hash TEXT,
        UNIQUE(año, mes)
    );
    CREATE INDEX IF NOT EXISTS idx_bi_snapshot_periodo ON bi_snapshots_mensual(año, mes);
    CREATE INDEX IF NOT EXISTS idx_bi_snapshot_fecha ON bi_snapshots_mensual(fecha_snapshot);
    """,
    
    # Migración 9: Tabla de cache de análisis
    """
    CREATE TABLE IF NOT EXISTS analytics_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cache_key TEXT UNIQUE NOT NULL,
        valor_json TEXT NOT NULL,
        fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expira_en INTEGER DEFAULT 3600,
        invalidar_si_nuevos_kpis BOOLEAN DEFAULT 1,
        hits INTEGER DEFAULT 0,
        version INTEGER DEFAULT 1,
        UNIQUE(cache_key)
    );
    CREATE INDEX IF NOT EXISTS idx_cache_key ON analytics_cache(cache_key);
    CREATE INDEX IF NOT EXISTS idx_cache_expira ON analytics_cache(expira_en);
    """,
]


def ejecutar_migraciones(conn):
    """
    Ejecuta todas las migraciones necesarias.
    Idempotente y seguro para ejecutar en cada arranque.
    
    Args:
        conn: Conexión SQLite
    """
    cursor = conn.cursor()
    
    for i, migracion in enumerate(MIGRACIONES_SISTEMA, 1):
        try:
            cursor.executescript(migracion)
            conn.commit()
            print(f"[OK] Migracion {i}: Tabla creada/verificada")
        except Exception as e:
            print(f"[WARN] Migracion {i}: {e}")
            conn.rollback()
    
    # Crear usuario por defecto si no existe
    try:
        cursor.execute("SELECT COUNT(*) FROM usuario")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuario (nombre, email, rol, estado)
                VALUES ('admin', 'admin@fincafacil.local', 'Administrador', 'activo')
            """)
            conn.commit()
            print("[OK] Usuario admin creado")
    except Exception as e:
        print(f"[WARN] Usuario admin: {e}")
        conn.rollback()
