"""
SaludRepository - Capa de acceso a datos para el dominio Salud
Encapsula TODO el SQL relacionado con diagnósticos y tratamientos
"""
from typing import Dict, Any, List, Optional
from database.database import ejecutar_consulta


class SaludRepository:
    """Repository para operaciones de base de datos del dominio Salud."""

    # ==================== INICIALIZACIÓN ====================
    
    def crear_tablas_si_no_existen(self) -> None:
        """Crea las tablas de salud si no existen (migrado desde UI)."""
        # Crear tabla diagnostico_evento
        ejecutar_consulta("""
            CREATE TABLE IF NOT EXISTS diagnostico_evento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha DATE NOT NULL,
                tipo TEXT NOT NULL,
                detalle TEXT,
                severidad TEXT,
                estado TEXT DEFAULT 'Activo',
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (animal_id) REFERENCES animal(id)
            )
        """)
        
        # Crear tabla tratamiento
        ejecutar_consulta("""
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
            )
        """)

    # ==================== DIAGNÓSTICOS ====================
    
    def insertar_diagnostico(
        self,
        animal_id: int,
        fecha: str,
        tipo: str,
        detalle: str,
        severidad: str,
        estado: str,
        observaciones: Optional[str] = None
    ) -> None:
        """Inserta un nuevo diagnóstico."""
        ejecutar_consulta(
            """
            INSERT INTO diagnostico_evento (animal_id, fecha, tipo, detalle, 
                                           severidad, estado, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (animal_id, fecha, tipo, detalle, severidad, estado, observaciones)
        )
    
    def listar_diagnosticos(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Lista diagnósticos con datos del animal (JOIN)."""
        resultado = ejecutar_consulta(
            """
            SELECT d.id, d.fecha, a.codigo || ' ' || COALESCE(a.nombre, '') as animal,
                   d.tipo, SUBSTR(d.detalle, 1, 50) || CASE WHEN LENGTH(d.detalle) > 50 THEN '...' ELSE '' END as detalle_corto,
                   d.severidad, d.estado
            FROM diagnostico_evento d
            JOIN animal a ON d.animal_id = a.id
            ORDER BY d.fecha DESC
            LIMIT ?
            """,
            (limite,),
            fetch=True
        )
        
        if not resultado:
            return []
        return resultado
    
    def obtener_diagnostico_por_id(self, diagnostico_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene el detalle completo de un diagnóstico."""
        resultado = ejecutar_consulta(
            """
            SELECT d.fecha, a.codigo || ' ' || COALESCE(a.nombre, '') as animal,
                   d.tipo, d.detalle, d.severidad, d.estado, d.observaciones
            FROM diagnostico_evento d
            JOIN animal a ON d.animal_id = a.id
            WHERE d.id = ?
            """,
            (diagnostico_id,),
            fetch=True
        )
        
        if not resultado:
            return None
        return resultado[0]
    
    def actualizar_estado_diagnostico(self, diagnostico_id: int, nuevo_estado: str) -> None:
        """Actualiza el estado de un diagnóstico."""
        ejecutar_consulta(
            "UPDATE diagnostico_evento SET estado = ? WHERE id = ?",
            (nuevo_estado, diagnostico_id)
        )
    
    def contar_diagnosticos(self) -> int:
        """Cuenta el total de diagnósticos activos."""
        resultado = ejecutar_consulta(
            "SELECT COUNT(*) AS total FROM diagnostico_evento WHERE estado = 'Activo'",
            fetch=True
        )
        return int(resultado[0].get('total', 0)) if resultado else 0

    # ==================== TRATAMIENTOS ====================
    
    def insertar_tratamiento(
        self,
        animal_id: int,
        fecha_inicio: str,
        tipo_tratamiento: str,
        producto: str,
        dosis: Optional[str] = None,
        veterinario: Optional[str] = None,
        comentario: Optional[str] = None,
        fecha_proxima: Optional[str] = None
    ) -> None:
        """Inserta un nuevo tratamiento."""
        ejecutar_consulta(
            """
            INSERT INTO tratamiento (
                id_animal, fecha_inicio, tipo_tratamiento, producto, 
                dosis, veterinario, comentario, fecha_proxima
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (animal_id, fecha_inicio, tipo_tratamiento, producto, dosis, veterinario, comentario, fecha_proxima)
        )
    
    def listar_tratamientos(self, limite: int = 100) -> List[Dict[str, Any]]:
        """Lista tratamientos con datos del animal (JOIN)."""
        resultado = ejecutar_consulta(
            """
            SELECT 
                t.id,
                t.fecha_inicio,
                a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                t.tipo_tratamiento,
                t.producto,
                t.dosis,
                t.veterinario,
                t.fecha_proxima,
                t.comentario
            FROM tratamiento t
            JOIN animal a ON t.id_animal = a.id
            WHERE t.estado = 'Activo'
            ORDER BY t.fecha_inicio DESC
            LIMIT ?
            """,
            (limite,),
            fetch=True
        )
        
        if not resultado:
            return []
        return resultado
    
    def listar_proximos_tratamientos(self, limite: int = 20) -> List[Dict[str, Any]]:
        """Lista tratamientos programados a futuro."""
        resultado = ejecutar_consulta(
            """
            SELECT 
                a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                t.tipo_tratamiento,
                t.producto,
                t.fecha_proxima,
                t.comentario
            FROM tratamiento t
            JOIN animal a ON t.id_animal = a.id
            WHERE t.fecha_proxima IS NOT NULL 
            AND t.fecha_proxima >= date('now')
            AND t.estado = 'Activo'
            ORDER BY t.fecha_proxima ASC
            LIMIT ?
            """,
            (limite,),
            fetch=True
        )
        
        if not resultado:
            return []
        return resultado
    
    def obtener_tratamiento_por_id(self, tratamiento_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene el detalle completo de un tratamiento."""
        resultado = ejecutar_consulta(
            """
            SELECT 
                t.fecha_inicio,
                a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                t.tipo_tratamiento,
                t.producto,
                t.dosis,
                t.veterinario,
                t.fecha_proxima,
                t.comentario,
                t.fecha_registro
            FROM tratamiento t
            JOIN animal a ON t.id_animal = a.id
            WHERE t.id = ?
            """,
            (tratamiento_id,),
            fetch=True
        )
        
        if not resultado:
            return None
        return resultado[0]
    
    def contar_tratamientos(self) -> int:
        """Cuenta el total de tratamientos activos."""
        resultado = ejecutar_consulta(
            "SELECT COUNT(*) AS total FROM tratamiento WHERE estado = 'Activo'",
            fetch=True
        )
        return int(resultado[0].get('total', 0)) if resultado else 0
    
    def contar_proximos_tratamientos(self) -> int:
        """Cuenta tratamientos programados a futuro."""
        resultado = ejecutar_consulta(
            """
            SELECT COUNT(*) AS total FROM tratamiento 
            WHERE fecha_proxima IS NOT NULL 
            AND fecha_proxima >= date('now')
            AND estado = 'Activo'
            """,
            fetch=True
        )
        return int(resultado[0].get('total', 0)) if resultado else 0

    # ==================== CATÁLOGOS ====================
    
    def listar_fincas_activas(self) -> List[Dict[str, Any]]:
        """Lista fincas activas."""
        resultado = ejecutar_consulta(
            "SELECT id, nombre FROM finca WHERE estado = 'Activo' ORDER BY nombre",
            fetch=True
        )
        
        if not resultado:
            return []
        return resultado
    
    def listar_animales_por_finca(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """Lista animales activos filtrados por finca."""
        resultado = ejecutar_consulta(
            """
            SELECT a.id, a.codigo, COALESCE(a.nombre, '') as nombre 
            FROM animal a
            WHERE a.id_finca = (SELECT id FROM finca WHERE nombre = ? AND estado = 'Activo')
            AND a.estado = 'Activo'
            ORDER BY a.codigo
            """,
            (finca_nombre,),
            fetch=True
        )
        
        if not resultado:
            return []
        return resultado
    
    def listar_animales_activos(self) -> List[Dict[str, Any]]:
        """Lista todos los animales activos."""
        resultado = ejecutar_consulta(
            """
            SELECT id, codigo, COALESCE(nombre, '') as nombre 
            FROM animal 
            WHERE estado = 'Activo'
            ORDER BY codigo
            """,
            fetch=True
        )
        
        if not resultado:
            return []
        return resultado
    
    def validar_animal_activo(self, animal_id: int) -> bool:
        """Valida si un animal existe y está activo."""
        resultado = ejecutar_consulta(
            "SELECT id FROM animal WHERE id = ? AND estado = 'Activo'",
            (animal_id,),
            fetch=True
        )
        return bool(resultado)
