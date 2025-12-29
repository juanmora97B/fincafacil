"""
Analytics Repository - Acceso a datos de read models
Encapsula todas las operaciones con tablas de analytics
"""
from typing import Dict, Any, List, Optional
from database.database import ejecutar_consulta
import sqlite3


class AnalyticsRepository:
    """Repository para operaciones de base de datos del dominio Analytics."""

    def crear_tablas_si_no_existen(self) -> None:
        """Crea tablas de analytics si no existen."""
        # Tabla de productividad
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS analytics_productividad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER DEFAULT 1,
                fecha DATE NOT NULL,
                lote_id INTEGER,
                sector_id INTEGER,
                animales_totales INTEGER DEFAULT 0,
                nacimientos INTEGER DEFAULT 0,
                destetes INTEGER DEFAULT 0,
                muertes INTEGER DEFAULT 0,
                traslados INTEGER DEFAULT 0,
                servicios INTEGER DEFAULT 0,
                partos INTEGER DEFAULT 0,
                mortalidad_pct REAL DEFAULT 0.0,
                natalidad_pct REAL DEFAULT 0.0,
                peso_promedio REAL,
                refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(empresa_id, fecha, lote_id, sector_id)
            )
        """)
        
        # Índices
        ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_prod_empresa_fecha ON analytics_productividad(empresa_id, fecha)")
        
        # Tabla de alertas
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS analytics_alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER DEFAULT 1,
                fecha DATE NOT NULL,
                tipo_alerta TEXT,
                total_activas INTEGER DEFAULT 0,
                total_resueltas INTEGER DEFAULT 0,
                criticas_activas INTEGER DEFAULT 0,
                tiempo_promedio_resolucion INTEGER,
                refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(empresa_id, fecha, tipo_alerta)
            )
        """)
        ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_alert_empresa_fecha ON analytics_alertas(empresa_id, fecha)")
        
        # Tabla de IA
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS analytics_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER DEFAULT 1,
                fecha DATE NOT NULL,
                sugerencias_generadas INTEGER DEFAULT 0,
                sugerencias_aceptadas INTEGER DEFAULT 0,
                sugerencias_rechazadas INTEGER DEFAULT 0,
                tasa_aceptacion_pct REAL DEFAULT 0.0,
                impacto_estimado_pesos REAL DEFAULT 0.0,
                precision_historica_pct REAL DEFAULT 0.0,
                modelo_version TEXT,
                refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(empresa_id, fecha)
            )
        """)
        ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_ia_empresa_fecha ON analytics_ia(empresa_id, fecha)")
        
        # Tabla de autonomía
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS analytics_autonomia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER DEFAULT 1,
                fecha DATE NOT NULL,
                orquestaciones_ejecutadas INTEGER DEFAULT 0,
                orquestaciones_exitosas INTEGER DEFAULT 0,
                orquestaciones_fallidas INTEGER DEFAULT 0,
                rollbacks_activados INTEGER DEFAULT 0,
                autonomia_estado TEXT DEFAULT 'ON',
                kill_switch_activaciones INTEGER DEFAULT 0,
                refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(empresa_id, fecha)
            )
        """)
        ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_aut_empresa_fecha ON analytics_autonomia(empresa_id, fecha)")
        
        # Tabla de comparativos
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS analytics_comparativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER DEFAULT 1,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                comparador TEXT,
                metrica_nombre TEXT,
                valor_actual REAL,
                valor_anterior REAL,
                variacion_pct REAL,
                refresh_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(empresa_id, comparador, fecha_inicio, fecha_fin, metrica_nombre)
            )
        """)
        ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_comp_empresa ON analytics_comparativos(empresa_id, comparador)")
        
        # Tabla de auditoría
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS analytics_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER DEFAULT 1,
                usuario_id INTEGER,
                endpoint TEXT,
                metodo TEXT,
                parametros TEXT,
                resultado TEXT,
                razon TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        ejecutar_consulta("CREATE INDEX IF NOT EXISTS idx_audit_empresa_ts ON analytics_audit(empresa_id, timestamp)")

    # ==================== PRODUCTIVIDAD ====================
    
    def insertar_productividad(self, data: Dict[str, Any]) -> None:
        """Inserta o actualiza registro de productividad."""
        ejecutar_consulta("""
            INSERT OR REPLACE INTO analytics_productividad
            (empresa_id, fecha, lote_id, sector_id, animales_totales, nacimientos, destetes, muertes,
             traslados, servicios, partos, mortalidad_pct, natalidad_pct, peso_promedio, refresh_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('empresa_id', 1),
            data.get('fecha'),
            data.get('lote_id'),
            data.get('sector_id'),
            data.get('animales_totales', 0),
            data.get('nacimientos', 0),
            data.get('destetes', 0),
            data.get('muertes', 0),
            data.get('traslados', 0),
            data.get('servicios', 0),
            data.get('partos', 0),
            data.get('mortalidad_pct', 0.0),
            data.get('natalidad_pct', 0.0),
            data.get('peso_promedio'),
        ))

    def obtener_productividad(self, empresa_id: int, fecha: str, lote_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene datos de productividad por fecha."""
        if lote_id:
            resultado = ejecutar_consulta(
                """SELECT * FROM analytics_productividad 
                   WHERE empresa_id = ? AND fecha = ? AND lote_id = ?
                   ORDER BY sector_id""",
                (empresa_id, fecha, lote_id),
                fetch=True
            )
        else:
            resultado = ejecutar_consulta(
                """SELECT * FROM analytics_productividad 
                   WHERE empresa_id = ? AND fecha = ?
                   ORDER BY lote_id, sector_id""",
                (empresa_id, fecha),
                fetch=True
            )
        return [dict(r) for r in (resultado or [])]

    def obtener_productividad_rango(self, empresa_id: int, fecha_desde: str, fecha_hasta: str) -> List[Dict[str, Any]]:
        """Obtiene datos de productividad en un rango de fechas."""
        resultado = ejecutar_consulta(
            """SELECT * FROM analytics_productividad 
               WHERE empresa_id = ? AND fecha BETWEEN ? AND ?
               ORDER BY fecha DESC, lote_id""",
            (empresa_id, fecha_desde, fecha_hasta),
            fetch=True
        )
        return [dict(r) for r in (resultado or [])]

    # ==================== ALERTAS ====================
    
    def insertar_alerta(self, data: Dict[str, Any]) -> None:
        """Inserta o actualiza registro de alertas."""
        ejecutar_consulta("""
            INSERT OR REPLACE INTO analytics_alertas
            (empresa_id, fecha, tipo_alerta, total_activas, total_resueltas, criticas_activas,
             tiempo_promedio_resolucion, refresh_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('empresa_id', 1),
            data.get('fecha'),
            data.get('tipo_alerta'),
            data.get('total_activas', 0),
            data.get('total_resueltas', 0),
            data.get('criticas_activas', 0),
            data.get('tiempo_promedio_resolucion'),
        ))

    def obtener_alertas(self, empresa_id: int, fecha: str) -> List[Dict[str, Any]]:
        """Obtiene alertas por fecha."""
        resultado = ejecutar_consulta(
            """SELECT * FROM analytics_alertas 
               WHERE empresa_id = ? AND fecha = ?
               ORDER BY tipo_alerta""",
            (empresa_id, fecha),
            fetch=True
        )
        return [dict(r) for r in (resultado or [])]

    # ==================== IA ====================
    
    def insertar_ia(self, data: Dict[str, Any]) -> None:
        """Inserta o actualiza registro de IA."""
        ejecutar_consulta("""
            INSERT OR REPLACE INTO analytics_ia
            (empresa_id, fecha, sugerencias_generadas, sugerencias_aceptadas, sugerencias_rechazadas,
             tasa_aceptacion_pct, impacto_estimado_pesos, precision_historica_pct, modelo_version, refresh_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('empresa_id', 1),
            data.get('fecha'),
            data.get('sugerencias_generadas', 0),
            data.get('sugerencias_aceptadas', 0),
            data.get('sugerencias_rechazadas', 0),
            data.get('tasa_aceptacion_pct', 0.0),
            data.get('impacto_estimado_pesos', 0.0),
            data.get('precision_historica_pct', 0.0),
            data.get('modelo_version'),
        ))

    def obtener_ia(self, empresa_id: int, fecha: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de IA por fecha."""
        resultado = ejecutar_consulta(
            """SELECT * FROM analytics_ia 
               WHERE empresa_id = ? AND fecha = ?""",
            (empresa_id, fecha),
            fetch=True
        )
        return dict(resultado[0]) if resultado else None

    # ==================== AUTONOMÍA ====================
    
    def insertar_autonomia(self, data: Dict[str, Any]) -> None:
        """Inserta o actualiza registro de autonomía."""
        ejecutar_consulta("""
            INSERT OR REPLACE INTO analytics_autonomia
            (empresa_id, fecha, orquestaciones_ejecutadas, orquestaciones_exitosas, 
             orquestaciones_fallidas, rollbacks_activados, autonomia_estado, kill_switch_activaciones, refresh_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('empresa_id', 1),
            data.get('fecha'),
            data.get('orquestaciones_ejecutadas', 0),
            data.get('orquestaciones_exitosas', 0),
            data.get('orquestaciones_fallidas', 0),
            data.get('rollbacks_activados', 0),
            data.get('autonomia_estado', 'ON'),
            data.get('kill_switch_activaciones', 0),
        ))

    def obtener_autonomia(self, empresa_id: int, fecha: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de autonomía por fecha."""
        resultado = ejecutar_consulta(
            """SELECT * FROM analytics_autonomia 
               WHERE empresa_id = ? AND fecha = ?""",
            (empresa_id, fecha),
            fetch=True
        )
        return dict(resultado[0]) if resultado else None

    # ==================== COMPARATIVOS ====================
    
    def insertar_comparativo(self, data: Dict[str, Any]) -> None:
        """Inserta o actualiza comparativo."""
        ejecutar_consulta("""
            INSERT OR REPLACE INTO analytics_comparativos
            (empresa_id, fecha_inicio, fecha_fin, comparador, metrica_nombre, 
             valor_actual, valor_anterior, variacion_pct, refresh_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            data.get('empresa_id', 1),
            data.get('fecha_inicio'),
            data.get('fecha_fin'),
            data.get('comparador'),
            data.get('metrica_nombre'),
            data.get('valor_actual'),
            data.get('valor_anterior'),
            data.get('variacion_pct'),
        ))

    def obtener_comparativos(self, empresa_id: int, comparador: str) -> List[Dict[str, Any]]:
        """Obtiene comparativos por tipo."""
        resultado = ejecutar_consulta(
            """SELECT * FROM analytics_comparativos 
               WHERE empresa_id = ? AND comparador = ?
               ORDER BY fecha_fin DESC
               LIMIT 7""",
            (empresa_id, comparador),
            fetch=True
        )
        return [dict(r) for r in (resultado or [])]

    # ==================== AUDITORÍA ====================
    
    def registrar_acceso(self, data: Dict[str, Any]) -> None:
        """Registra acceso a endpoints de analytics."""
        ejecutar_consulta("""
            INSERT INTO analytics_audit
            (empresa_id, usuario_id, endpoint, metodo, parametros, resultado, razon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('empresa_id', 1),
            data.get('usuario_id'),
            data.get('endpoint'),
            data.get('metodo'),
            data.get('parametros'),
            data.get('resultado'),
            data.get('razon'),
        ))

    def obtener_auditoria(self, empresa_id: int, ultimos_n: int = 100) -> List[Dict[str, Any]]:
        """Obtiene últimas N auditorías."""
        resultado = ejecutar_consulta(
            """SELECT * FROM analytics_audit 
               WHERE empresa_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (empresa_id, ultimos_n),
            fetch=True
        )
        return [dict(r) for r in (resultado or [])]
