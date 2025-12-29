"""
Capa de Repositorio - Dominio Configuración
FASE 9.0.3 - Encapsulación Catálogo Calidad Animal

Responsabilidad: Encapsular TODA interacción con la BD de Configuración.
Sin lógica de negocio, sin validaciones, solo SQL puro.

Métodos para catálogo Calidad Animal (fase inicial).
Patrón: Repository pattern (una operación = un método).
"""

from typing import List, Dict, Optional, Any
from database import db
import sqlite3


class ConfiguracionRepository:
    """
    Repository para dominio Configuración (inicialmente Calidad Animal).
    
    Patrón: 
    - Un método por operación SQL
    - Type hints exhaustivos
    - Sin lógica de negocio
    - Sin excepciones custom (dejar propagar SQLite)
    """
    
    def __init__(self):
        """Inicializa repository sin estado."""
        pass
    
    # ============================================================
    # LECTURA - Calidad Animal
    # ============================================================
    
    def listar_calidades(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista completa de calidades de animal.
        
        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'comentario': str}, ...]
            
        Nota: comentario puede ser None en DB, pero service normaliza.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, comentario FROM calidad_animal"
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'comentario': row[2]
                    }
                    for row in rows
                ]
        except Exception as e:
            # Propagar excepción para que service la maneje
            raise
    
    def obtener_calidad(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalle de una calidad específica.
        
        Args:
            codigo: Código único de la calidad
            
        Returns:
            Dict o None si no existe
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, comentario FROM calidad_animal WHERE codigo = ?",
                    (codigo,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'comentario': row[2]
                    }
                return None
        except Exception:
            raise
    
    # ============================================================
    # LECTURA - Causa de Muerte
    # ============================================================

    def listar_causas_muerte(self) -> List[Dict[str, Any]]:
        """
        Lista causas de muerte activas.

        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'tipo_causa': str, 'comentario': Optional[str]}]
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, tipo_causa, comentario FROM causa_muerte WHERE estado = 'Activo'"
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'tipo_causa': row[2],
                        'comentario': row[3],
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def obtener_causa_muerte(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una causa de muerte por código.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, tipo_causa, comentario, estado FROM causa_muerte WHERE codigo = ?",
                    (codigo,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'tipo_causa': row[2],
                        'comentario': row[3],
                        'estado': row[4],
                    }
                return None
        except Exception:
            raise

    def existe_causa_muerte(self, codigo: str) -> bool:
        """Verifica existencia por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM causa_muerte WHERE codigo = ?", (codigo,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    # ============================================================
    # ESCRITURA - Causa de Muerte
    # ============================================================

    def crear_causa_muerte(
        self,
        codigo: str,
        descripcion: str,
        tipo_causa: Optional[str],
        comentario: Optional[str],
        estado: str,
    ) -> None:
        """Inserta nueva causa de muerte."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO causa_muerte (codigo, descripcion, tipo_causa, comentario, estado)
                           VALUES (?, ?, ?, ?, ?)""",
                    (codigo, descripcion, tipo_causa, comentario, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_causa_muerte(
        self,
        codigo: str,
        descripcion: str,
        tipo_causa: Optional[str],
        comentario: Optional[str],
    ) -> None:
        """Actualiza campos de una causa por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE causa_muerte
                           SET descripcion = ?, tipo_causa = ?, comentario = ?
                           WHERE codigo = ?""",
                    (descripcion, tipo_causa, comentario, codigo)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_causa_muerte(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva una causa (soft delete por estado)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE causa_muerte SET estado = ? WHERE codigo = ?",
                    (nuevo_estado, codigo)
                )
                conn.commit()
        except Exception:
            raise
    
    # ============================================================
    # CONFIGURACIÓN - Diagnósticos
    # ============================================================

    def listar_diagnosticos(self) -> List[Dict[str, Any]]:
        """
        Lista diagnósticos veterinarios activos.

        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'tipo_diagnostico': str, 'comentario': Optional[str]}]
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, tipo_diagnostico, comentario FROM diagnostico_veterinario WHERE estado = 'Activo'"
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'tipo_diagnostico': row[2],
                        'comentario': row[3],
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def existe_diagnostico(self, codigo: str) -> bool:
        """Verifica existencia por código en diagnostico_veterinario."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM diagnostico_veterinario WHERE codigo = ?", (codigo,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def crear_diagnostico(
        self,
        codigo: str,
        descripcion: str,
        tipo_diagnostico: Optional[str],
        comentario: Optional[str],
        estado: str,
    ) -> None:
        """Inserta nuevo diagnóstico veterinario."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO diagnostico_veterinario (codigo, descripcion, tipo_diagnostico, comentario, estado)
                           VALUES (?, ?, ?, ?, ?)""",
                    (codigo, descripcion, tipo_diagnostico, comentario, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

        
    def actualizar_diagnostico(
        self,
        codigo: str,
        descripcion: str,
        tipo_diagnostico: Optional[str],
        comentario: Optional[str],
    ) -> None:
        """Actualiza campos de un diagnóstico por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE diagnostico_veterinario
                           SET descripcion = ?, tipo_diagnostico = ?, comentario = ?
                           WHERE codigo = ?""",
                    (descripcion, tipo_diagnostico, comentario, codigo)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_diagnostico(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva diagnóstico (soft delete por estado)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE diagnostico_veterinario SET estado = ? WHERE codigo = ?",
                    (nuevo_estado, codigo)
                )
                conn.commit()
        except Exception:
            raise

    # ============================================================
    # CONFIGURACIÓN - Procedencia
    # ============================================================

    def listar_procedencias(self) -> List[Dict[str, Any]]:
        """
        Lista procedencias activas.

        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'tipo_procedencia': str, 
                          'ubicacion': Optional[str], 'comentario': Optional[str]}]
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, tipo_procedencia, ubicacion, comentario FROM procedencia WHERE estado = 'Activo'"
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'tipo_procedencia': row[2],
                        'ubicacion': row[3],
                        'comentario': row[4],
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def obtener_procedencia(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una procedencia por código (para edición)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, tipo_procedencia, ubicacion, comentario, estado FROM procedencia WHERE codigo = ?",
                    (codigo,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'tipo_procedencia': row[2],
                        'ubicacion': row[3],
                        'comentario': row[4],
                        'estado': row[5],
                    }
                return None
        except Exception:
            raise

    def existe_procedencia(self, codigo: str) -> bool:
        """Verifica existencia por código en procedencia."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM procedencia WHERE codigo = ?", (codigo,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def crear_procedencia(
        self,
        codigo: str,
        descripcion: str,
        tipo_procedencia: Optional[str],
        ubicacion: Optional[str],
        comentario: Optional[str],
        estado: str,
    ) -> None:
        """Inserta nueva procedencia."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO procedencia (codigo, descripcion, tipo_procedencia, ubicacion, comentario, estado)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                    (codigo, descripcion, tipo_procedencia, ubicacion, comentario, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_procedencia(
        self,
        codigo: str,
        descripcion: str,
        tipo_procedencia: Optional[str],
        ubicacion: Optional[str],
        comentario: Optional[str],
    ) -> None:
        """Actualiza campos de una procedencia por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE procedencia
                           SET descripcion = ?, tipo_procedencia = ?, ubicacion = ?, comentario = ?
                           WHERE codigo = ?""",
                    (descripcion, tipo_procedencia, ubicacion, comentario, codigo)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_procedencia(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva procedencia (soft delete por estado)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE procedencia SET estado = ? WHERE codigo = ?",
                    (nuevo_estado, codigo)
                )
                conn.commit()
        except Exception:
            raise

    # ============================================================
    # CONFIGURACIÓN - Motivos de Venta
    # ============================================================

    def listar_motivos_venta(self) -> List[Dict[str, Any]]:
        """
        Lista motivos de venta (incluye estado para soft delete).

        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'comentario': Optional[str], 'estado': str}]
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT codigo, descripcion, comentario, estado
                           FROM motivo_venta
                           ORDER BY codigo"""
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'comentario': row[2],
                        'estado': row[3],
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def obtener_motivo_venta(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un motivo de venta por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT codigo, descripcion, comentario, estado FROM motivo_venta WHERE codigo = ?",
                    (codigo,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0],
                        'descripcion': row[1],
                        'comentario': row[2],
                        'estado': row[3],
                    }
                return None
        except Exception:
            raise

    def existe_motivo_venta(self, codigo: str) -> bool:
        """Verifica existencia por código en motivo_venta."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM motivo_venta WHERE codigo = ?", (codigo,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def crear_motivo_venta(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str],
        estado: str,
    ) -> None:
        """Inserta un nuevo motivo de venta."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO motivo_venta (codigo, descripcion, comentario, estado)
                           VALUES (?, ?, ?, ?)""",
                    (codigo, descripcion, comentario, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_motivo_venta(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str],
    ) -> None:
        """Actualiza descripción/comentario de un motivo por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE motivo_venta
                           SET descripcion = ?, comentario = ?
                           WHERE codigo = ?""",
                    (descripcion, comentario, codigo)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_motivo_venta(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva motivo de venta (soft delete por estado)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE motivo_venta SET estado = ? WHERE codigo = ?",
                    (nuevo_estado, codigo)
                )
                conn.commit()
        except Exception:
            raise

    # ============================================================
    # CONFIGURACIÓN - Razas
    # ============================================================

    def listar_razas(self) -> List[Dict[str, Any]]:
        """
        Lista razas activas.

        Returns:
            List[Dict]: [{'codigo': str, 'nombre': str, 'tipo_ganado': Optional[str],
                          'especie': Optional[str], 'descripcion': Optional[str], 'estado': str}]
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT codigo, nombre, tipo_ganado, especie, descripcion, estado
                           FROM raza
                           WHERE estado = 'Activo'
                           ORDER BY codigo"""
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'nombre': row[1],
                        'tipo_ganado': row[2],
                        'especie': row[3],
                        'descripcion': row[4],
                        'estado': row[5],
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def obtener_raza(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una raza por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT codigo, nombre, tipo_ganado, especie, descripcion, estado
                           FROM raza WHERE codigo = ?""",
                    (codigo,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0],
                        'nombre': row[1],
                        'tipo_ganado': row[2],
                        'especie': row[3],
                        'descripcion': row[4],
                        'estado': row[5],
                    }
                return None
        except Exception:
            raise

    def existe_raza(self, codigo: str) -> bool:
        """Verifica existencia por código en raza."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM raza WHERE codigo = ?", (codigo,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def crear_raza(
        self,
        codigo: str,
        nombre: str,
        tipo_ganado: Optional[str],
        especie: Optional[str],
        descripcion: Optional[str],
        estado: str,
    ) -> None:
        """Inserta una nueva raza."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO raza (codigo, nombre, tipo_ganado, especie, descripcion, estado)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                    (codigo, nombre, tipo_ganado, especie, descripcion, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_raza(
        self,
        codigo: str,
        nombre: str,
        tipo_ganado: Optional[str],
        especie: Optional[str],
        descripcion: Optional[str],
    ) -> None:
        """Actualiza campos de una raza por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE raza
                           SET nombre = ?, tipo_ganado = ?, especie = ?, descripcion = ?
                           WHERE codigo = ?""",
                    (nombre, tipo_ganado, especie, descripcion, codigo)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_raza(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva raza (soft delete por estado)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE raza SET estado = ? WHERE codigo = ?",
                    (nuevo_estado, codigo)
                )
                conn.commit()
        except Exception:
            raise

    # ============================================================
    # CONFIGURACIÓN - Empleados (Base)
    # ============================================================

    def listar_empleados_activos(self) -> List[Dict[str, Any]]:
        """
        Lista empleados activos (estado='Activo').

        Returns:
            List[Dict]: [{'codigo': str, 'numero_identificacion': str, 'nombres': str, 
                          'apellidos': str, 'cargo': str, 'id_finca': Optional[int], 'estado': str}]
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT codigo, numero_identificacion, nombres, apellidos, cargo, id_finca, estado_actual
                           FROM empleado
                           WHERE estado_actual = 'Activo' OR estado_actual IS NULL
                           ORDER BY apellidos, nombres"""
                )
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0],
                        'numero_identificacion': row[1],
                        'nombres': row[2],
                        'apellidos': row[3],
                        'cargo': row[4],
                        'id_finca': row[5],
                        'estado': row[6] or 'Activo',
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def obtener_empleado(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un empleado por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT codigo, numero_identificacion, nombres, apellidos, cargo, id_finca, estado_actual
                           FROM empleado WHERE codigo = ?""",
                    (codigo,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0],
                        'numero_identificacion': row[1],
                        'nombres': row[2],
                        'apellidos': row[3],
                        'cargo': row[4],
                        'id_finca': row[5],
                        'estado': row[6] or 'Activo',
                    }
                return None
        except Exception:
            raise

    def existe_empleado(self, numero_identificacion: str) -> bool:
        """Verifica existencia por número de identificación."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM empleado WHERE numero_identificacion = ?", (numero_identificacion,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def existe_codigo_empleado(self, codigo: str) -> bool:
        """Verifica existencia por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM empleado WHERE codigo = ?", (codigo,))
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def crear_empleado_base(
        self,
        codigo: str,
        numero_identificacion: str,
        nombres: str,
        apellidos: str,
        cargo: str,
        id_finca: Optional[int],
        estado: str,
    ) -> None:
        """Inserta un nuevo empleado (campos base solamente)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO empleado (codigo, numero_identificacion, nombres, apellidos, cargo, id_finca, estado_actual, estado)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (codigo, numero_identificacion, nombres, apellidos, cargo, id_finca, estado, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_empleado_base(
        self,
        codigo: str,
        numero_identificacion: str,
        nombres: str,
        apellidos: str,
        cargo: str,
        id_finca: Optional[int],
    ) -> None:
        """Actualiza campos base de un empleado."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE empleado
                           SET numero_identificacion = ?, nombres = ?, apellidos = ?, cargo = ?, id_finca = ?
                           WHERE codigo = ?""",
                    (numero_identificacion, nombres, apellidos, cargo, id_finca, codigo)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_empleado(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva empleado (soft delete por estado)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE empleado SET estado_actual = ?, estado = ? WHERE codigo = ?",
                    (nuevo_estado, nuevo_estado, codigo)
                )
                conn.commit()
        except Exception:
            raise

    # ============================================================
    # LECTURA/ESCRITURA - Fincas (scope base)
    # ============================================================

    def listar_fincas_activas(self) -> List[Dict[str, Any]]:
        """Devuelve fincas con estado Activo."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT codigo, nombre, ubicacion, estado
                    FROM finca
                    WHERE estado = 'Activo'
                    ORDER BY nombre
                    """
                )
                columnas = [col[0] for col in cursor.description]
                return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        except Exception:
            raise

    def obtener_finca(self, codigo_finca: str) -> Optional[Dict[str, Any]]:
        """Obtiene una finca por código."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT codigo, nombre, ubicacion, estado
                    FROM finca
                    WHERE codigo = ?
                    LIMIT 1
                    """,
                    (codigo_finca,)
                )
                fila = cursor.fetchone()
                if not fila:
                    return None
                columnas = [col[0] for col in cursor.description]
                return dict(zip(columnas, fila))
        except Exception:
            raise

    def existe_codigo_finca(self, codigo_finca: str) -> bool:
        """Verifica existencia por código de finca."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM finca WHERE codigo = ?",
                    (codigo_finca,)
                )
                return (cursor.fetchone() or [0])[0] > 0
        except Exception:
            raise

    def crear_finca_base(self, codigo_finca: str, nombre: str, ubicacion: Optional[str], estado: str) -> None:
        """Inserta una finca (campos base)."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO finca (codigo, nombre, ubicacion, estado)
                    VALUES (?, ?, ?, ?)
                    """,
                    (codigo_finca, nombre, ubicacion, estado)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_finca_base(self, codigo_finca: str, nombre: str, ubicacion: Optional[str]) -> None:
        """Actualiza campos base de una finca."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE finca
                    SET nombre = ?, ubicacion = ?
                    WHERE codigo = ?
                    """,
                    (nombre, ubicacion, codigo_finca)
                )
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_finca(self, codigo_finca: str, estado: str) -> None:
        """Soft delete/restore de finca mediante estado."""
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE finca SET estado = ? WHERE codigo = ?",
                    (estado, codigo_finca)
                )
                conn.commit()
        except Exception:
            raise

    def existe_calidad(self, codigo: str) -> bool:
        """
        Verifica si una calidad existe.
        
        Args:
            codigo: Código a verificar
            
        Returns:
            True si existe, False si no
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM calidad_animal WHERE codigo = ?",
                    (codigo,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            raise
    
    # ============================================================
    # ESCRITURA - Calidad Animal
    # ============================================================
    
    def crear_calidad(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str] = None
    ) -> None:
        """
        Crea una nueva calidad.
        
        Args:
            codigo: Código único (PK)
            descripcion: Descripción de la calidad
            comentario: Comentario opcional
            
        Raises:
            sqlite3.IntegrityError: Si código duplicado
            Exception: Otros errores de BD
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO calidad_animal (codigo, descripcion, comentario)
                       VALUES (?, ?, ?)""",
                    (codigo, descripcion, comentario)
                )
                conn.commit()
        except sqlite3.IntegrityError:
            # Re-lanzar para que service lo interprete
            raise
        except Exception:
            raise
    
    def actualizar_calidad(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str] = None
    ) -> None:
        """
        Actualiza una calidad existente.
        
        Args:
            codigo: Código de la calidad a actualizar
            descripcion: Nueva descripción
            comentario: Nuevo comentario
            
        Raises:
            Exception: Errores de BD
            
        Nota: Service debe validar que codigo existe antes de llamar.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE calidad_animal 
                       SET descripcion = ?, comentario = ?
                       WHERE codigo = ?""",
                    (descripcion, comentario, codigo)
                )
                conn.commit()
        except Exception:
            raise
    
    def eliminar_calidad(self, codigo: str) -> None:
        """
        Elimina una calidad.
        
        Args:
            codigo: Código de la calidad a eliminar
            
        Raises:
            Exception: Errores de BD
            
        Nota: Service debe validar que codigo existe antes de llamar.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM calidad_animal WHERE codigo = ?",
                    (codigo,)
                )
                conn.commit()
        except Exception:
            raise
    
    # ============================================================
    # ESCRITURA BULK - Calidad Animal
    # ============================================================
    
    def insertar_calidades_bulk(
        self,
        calidades: List[Dict[str, Any]]
    ) -> None:
        """
        Inserta múltiples calidades en una transacción.
        
        Args:
            calidades: Lista de dicts con 'codigo', 'descripcion', 'comentario'
            
        Raises:
            sqlite3.IntegrityError: Si algún código duplicado (rollback all)
            Exception: Otros errores
            
        Nota: Si falla, hace ROLLBACK automático.
              Service debe capturar excepciones y reportar fila con error.
        """
        if not calidades:
            return
        
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                # BEGIN por defecto en SQLite con get_connection
                for calidad in calidades:
                    cursor.execute(
                        """INSERT INTO calidad_animal (codigo, descripcion, comentario)
                           VALUES (?, ?, ?)""",
                        (
                            calidad.get('codigo'),
                            calidad.get('descripcion'),
                            calidad.get('comentario')
                        )
                    )
                conn.commit()
        except sqlite3.IntegrityError:
            # Rollback automático al salir del context manager
            pass

    # ============================================================
    # LECTURA - Lotes
    # ============================================================

    def listar_fincas_activas_para_lotes(self) -> List[Dict[str, Any]]:
        """
        Obtiene fincas activas para combo en módulo Lotes.

        Returns:
            List[Dict]: [{'id': int, 'codigo': str, 'nombre': str}, ...]
            Ordenado por nombre.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
    "SELECT id, codigo, nombre FROM finca WHERE estado = 'Activo' ORDER BY nombre"
                )
                rows = cursor.fetchall()
                return [
    {
        'id': row[0],
        'codigo': row[1] if row[1] is not None else '',
        'nombre': row[2] if row[2] is not None else ''
    }
    for row in rows
                ]
        except Exception:
            raise
    

    def listar_lotes_activos_con_finca(self) -> List[Dict[str, Any]]:
        """
        Obtiene lotes activos con nombre de finca (LEFT JOIN).

        Returns:
            List[Dict]: [{'id': int, 'codigo': str, 'nombre': str, 'descripcion': str,
                          'criterio': str, 'finca_id': int, 'finca_nombre': str}, ...]
            Ordenado por código.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.id, l.codigo, l.nombre, l.descripcion, l.criterio, l.estado,
                           l.finca_id, COALESCE(f.nombre, 'Sin Finca')
                    FROM lote l
                    LEFT JOIN finca f ON l.finca_id = f.id
                    WHERE l.estado = 'Activo'
                    ORDER BY l.codigo
                """)
                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else '',
                        'descripcion': row[3] if row[3] is not None else '',
                        'criterio': row[4] if row[4] is not None else '',
                        'estado': row[5] if row[5] is not None else '',
                        'finca_id': row[6],
                        'finca_nombre': row[7] if row[7] is not None else 'Sin Finca'
                    }
                    for row in rows
                ]
        except Exception:
            raise

    def obtener_lote(self, lote_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un lote por ID.

        Args:
            lote_id: ID del lote
        
        Returns:
            Dict con datos del lote, o None si no existe.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, codigo, nombre, descripcion, criterio, estado, finca_id
                    FROM lote
                    WHERE id = ?
                    LIMIT 1
                """, (lote_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else '',
                        'descripcion': row[3] if row[3] is not None else '',
                        'criterio': row[4] if row[4] is not None else '',
                        'estado': row[5] if row[5] is not None else '',
                        'finca_id': row[6]
                    }
                return None
        except Exception:
            raise

    def existe_lote_en_finca(self, codigo: str, finca_id: int) -> bool:
        """
        Verifica si existe un lote con el código dado en la finca especificada.

        Args:
            codigo: Código del lote
            finca_id: ID de la finca
        
        Returns:
            True si existe, False en caso contrario.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM lote WHERE codigo = ? AND finca_id = ?",
                    (codigo, finca_id)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            raise

    def obtener_finca_por_nombre(self, nombre: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una finca activa por nombre (case-insensitive).

        Args:
            nombre: Nombre de la finca
        
        Returns:
            Dict con datos de la finca, o None si no existe o está inactiva.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, codigo, nombre, ubicacion, estado
                    FROM finca
                    WHERE LOWER(nombre) = LOWER(?) AND estado = 'Activo'
                    LIMIT 1
                """, (nombre,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else '',
                        'ubicacion': row[3] if row[3] is not None else '',
                        'estado': row[4] if row[4] is not None else ''
                    }
                return None
        except Exception:
            raise

    def obtener_finca_por_id(self, finca_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una finca por ID si está activa.

        Args:
            finca_id: ID de la finca
        
        Returns:
            Dict con datos de la finca, o None si no existe o está inactiva.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, codigo, nombre, ubicacion, estado
                    FROM finca
                    WHERE id = ? AND estado = 'Activo'
                    LIMIT 1
                    """,
                    (finca_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else '',
                        'ubicacion': row[3] if row[3] is not None else '',
                        'estado': row[4] if row[4] is not None else ''
                    }
                return None
        except Exception:
            raise

    # ============================================================
    # ESCRITURA - Lotes
    # ============================================================

    def crear_lote(
        self,
        codigo: str,
        nombre: str,
        finca_id: int,
        descripcion: str,
        criterio: str,
        estado: str
    ) -> None:
        """
        Inserta un nuevo lote.

        Args:
            codigo: Código del lote (debe ser único por finca)
            nombre: Nombre del lote
            finca_id: ID de la finca
            descripcion: Descripción (opcional, puede ser '')
            criterio: Criterio de agrupación
            estado: Estado del lote ('Activo' o 'Inactivo')
        
        Raises:
            sqlite3.IntegrityError: Si código duplicado en la finca
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lote (codigo, nombre, descripcion, criterio, estado, finca_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (codigo, nombre, descripcion, criterio, estado, finca_id))
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise

    def actualizar_lote(
        self,
        lote_id: int,
        nombre: str,
        descripcion: str,
        criterio: str,
        finca_id: int
    ) -> None:
        """
        Actualiza un lote existente (no actualiza código ni estado).

        Args:
            lote_id: ID del lote
            nombre: Nuevo nombre
            descripcion: Nueva descripción
            criterio: Nuevo criterio
            finca_id: Nueva finca (permite reasignar lote a otra finca)
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE lote
                    SET nombre = ?, descripcion = ?, criterio = ?, finca_id = ?
                    WHERE id = ?
                """, (nombre, descripcion, criterio, finca_id, lote_id))
                conn.commit()
        except Exception:
            raise

    def cambiar_estado_lote(self, lote_id: int, estado: str) -> None:
        """
        Cambia el estado de un lote (soft delete).

        Args:
            lote_id: ID del lote
            estado: Nuevo estado ('Activo' o 'Inactivo')
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE lote SET estado = ? WHERE id = ?",
                    (estado, lote_id)
                )
                conn.commit()
        except Exception:
            raise


    # LECTURA - Sectores
    # ============================================================
    
    def listar_fincas_activas_para_sectores(self) -> List[Dict[str, Any]]:
        """
        Obtiene fincas activas para combo en módulo Sectores.
        
        Returns:
            List[Dict]: [{'id': int, 'codigo': str, 'nombre': str}, ...]
            Ordenado por nombre.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, codigo, nombre FROM finca WHERE estado = 'Activo' ORDER BY nombre"
                )
                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else ''
                    }
                    for row in rows
                ]
        except Exception:
            raise
    
    def listar_sectores_activos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los sectores activos con nombre de finca (LEFT JOIN).
        
        Returns:
            List[Dict]: [{'id': int, 'codigo': str, 'nombre': str, 'comentario': str,
                          'finca_id': int, 'finca_nombre': str}, ...]
            Ordenado por código.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT s.id, s.codigo, s.nombre, s.comentario, s.finca_id, f.nombre as finca_nombre
                    FROM sector s
                    LEFT JOIN finca f ON s.finca_id = f.id
                    WHERE s.estado = 'Activo'
                    ORDER BY s.codigo
                """)
                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else '',
                        'comentario': row[3] if row[3] is not None else '',
                        'finca_id': row[4],
                        'finca_nombre': row[5] if row[5] is not None else ''
                    }
                    for row in rows
                ]
        except Exception:
            raise
    
    def obtener_sector(self, sector_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un sector por ID.
        
        Args:
            sector_id: ID del sector
            
        Returns:
            Dict con datos del sector, o None si no existe.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, codigo, nombre, comentario, estado, finca_id
                    FROM sector
                    WHERE id = ?
                    LIMIT 1
                """, (sector_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'codigo': row[1] if row[1] is not None else '',
                        'nombre': row[2] if row[2] is not None else '',
                        'comentario': row[3] if row[3] is not None else '',
                        'estado': row[4] if row[4] is not None else '',
                        'finca_id': row[5]
                    }
                return None
        except Exception:
            raise
    
    def existe_codigo_sector_en_finca(self, codigo: str, finca_id: int) -> bool:
        """
        Verifica si existe un sector con el código dado en la finca especificada.
        
        Args:
            codigo: Código del sector
            finca_id: ID de la finca
            
        Returns:
            True si existe, False en caso contrario.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM sector WHERE codigo = ? AND finca_id = ?",
                    (codigo, finca_id)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            raise
    
    # ============================================================
    # ESCRITURA - Sectores
    # ============================================================
    
    def crear_sector(
        self,
        codigo: str,
        nombre: str,
        finca_id: int,
        comentario: str,
        estado: str
    ) -> None:
        """
        Inserta un nuevo sector.
        
        Args:
            codigo: Código del sector (único por finca)
            nombre: Nombre del sector
            finca_id: ID de la finca
            comentario: Comentario (opcional, puede ser '')
            estado: Estado del sector ('Activo' o 'Inactivo')
            
        Raises:
            sqlite3.IntegrityError: Si código duplicado en la finca
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sector (codigo, nombre, comentario, estado, finca_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (codigo, nombre, comentario, estado, finca_id))
                conn.commit()
        except sqlite3.IntegrityError:
            raise
        except Exception:
            raise
    
    def actualizar_sector(
        self,
        sector_id: int,
        nombre: str,
        comentario: str,
        finca_id: int
    ) -> None:
        """
        Actualiza un sector existente (no actualiza código ni estado).
        
        Args:
            sector_id: ID del sector
            nombre: Nuevo nombre
            comentario: Nuevo comentario
            finca_id: Nueva finca
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sector
                    SET nombre = ?, comentario = ?, finca_id = ?
                    WHERE id = ?
                """, (nombre, comentario, finca_id, sector_id))
                conn.commit()
        except Exception:
            raise
    
    def cambiar_estado_sector(self, sector_id: int, estado: str) -> None:
        """
        Cambia el estado de un sector (soft delete).
        
        Args:
            sector_id: ID del sector
            estado: Nuevo estado ('Activo' o 'Inactivo')
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sector SET estado = ? WHERE id = ?",
                    (estado, sector_id)
                )
                conn.commit()
        except Exception:
            raise


    # LECTURA - Tipos de Explotación
    # ============================================================
    
    def listar_tipos_explotacion_activos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los tipos de explotación activos.
        
        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'categoria': str, 
                          'comentario': str}, ...]
            Ordenado por código.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, descripcion, categoria, comentario
                    FROM tipo_explotacion
                    WHERE estado = 'Activo'
                    ORDER BY codigo
                """)
                rows = cursor.fetchall()
                return [
                    {
                        'codigo': row[0] if row[0] is not None else '',
                        'descripcion': row[1] if row[1] is not None else '',
                        'categoria': row[2] if row[2] is not None else '',
                        'comentario': row[3] if row[3] is not None else ''
                    }
                    for row in rows
                ]
        except Exception:
            raise
    
    def obtener_tipo_explotacion(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un tipo de explotación por código.
        
        Args:
            codigo: Código del tipo de explotación
            
        Returns:
            Dict con datos del tipo, o None si no existe.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT codigo, descripcion, categoria, comentario, estado
                    FROM tipo_explotacion
                    WHERE codigo = ?
                """, (codigo,))
                row = cursor.fetchone()
                if row:
                    return {
                        'codigo': row[0] if row[0] is not None else '',
                        'descripcion': row[1] if row[1] is not None else '',
                        'categoria': row[2] if row[2] is not None else '',
                        'comentario': row[3] if row[3] is not None else '',
                        'estado': row[4] if row[4] is not None else 'Activo'
                    }
                return None
        except Exception:
            raise
    
    def existe_codigo_tipo_explotacion(self, codigo: str) -> bool:
        """
        Verifica si existe un tipo de explotación con el código dado.
        
        Args:
            codigo: Código a verificar
            
        Returns:
            True si existe, False si no.
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM tipo_explotacion WHERE codigo = ?",
                    (codigo,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            raise


    # ESCRITURA - Tipos de Explotación
    # ============================================================
    
    def crear_tipo_explotacion_base(
        self, 
        codigo: str, 
        descripcion: str, 
        categoria: str, 
        comentario: str,
        estado: str
    ) -> None:
        """
        Crea un nuevo tipo de explotación (sin validaciones, solo SQL).
        
        Args:
            codigo: Código del tipo
            descripcion: Descripción del tipo
            categoria: Categoría ('Carne', 'Leche', etc)
            comentario: Comentario opcional
            estado: Estado ('Activo' o 'Inactivo')
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tipo_explotacion (codigo, descripcion, categoria, comentario, estado)
                    VALUES (?, ?, ?, ?, ?)
                """, (codigo, descripcion, categoria, comentario, estado))
                conn.commit()
        except Exception:
            raise
    
    def actualizar_tipo_explotacion_base(
        self,
        codigo: str,
        descripcion: str,
        categoria: str,
        comentario: str
    ) -> None:
        """
        Actualiza un tipo de explotación existente (sin validaciones, solo SQL).
        
        Args:
            codigo: Código del tipo (PK, no se modifica)
            descripcion: Nueva descripción
            categoria: Nueva categoría
            comentario: Nuevo comentario
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tipo_explotacion
                    SET descripcion = ?, categoria = ?, comentario = ?
                    WHERE codigo = ?
                """, (descripcion, categoria, comentario, codigo))
                conn.commit()
        except Exception:
            raise
    
    def cambiar_estado_tipo_explotacion(self, codigo: str, estado: str) -> None:
        """
        Cambia el estado de un tipo de explotación (soft delete).
        
        Args:
            codigo: Código del tipo
            estado: Nuevo estado ('Activo' o 'Inactivo')
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE tipo_explotacion SET estado = ? WHERE codigo = ?",
                    (estado, codigo)
                )
                conn.commit()
        except Exception:
            raise
