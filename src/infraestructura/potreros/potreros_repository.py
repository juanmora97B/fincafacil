"""
Módulo: Potreros Repository
Responsabilidad: Acceso a datos (SQL-only)
No contiene: Lógica de negocio, validaciones, orquestación

Métodos:
  - Lectura: obtener_fincas_activas, obtener_potreros_todos, obtener_potreros_por_finca
  - Consultas complejas: obtener_detalles_potrero, obtener_animales_potrero
  - Métricas: obtener_metricas_potreros
"""

from typing import List, Dict, Any, Optional
from database import db


class PotrerosRepository:
    """Repositorio para acceder a datos de Potreros desde SQLite"""

    def obtener_fincas_activas(self) -> List[str]:
        """
        Obtiene lista de nombres de fincas activas, ordenadas alfabéticamente.
        
        Returns:
            List[str]: Lista de nombres de fincas ej. ["Finca A", "Finca B"]
        
        Raises:
            Exception: Si la consulta falla
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM finca WHERE estado = 'Activo' ORDER BY nombre")
                fincas = [row[0] for row in cursor.fetchall()]
                return fincas
        except Exception as e:
            raise Exception(f"Error obteniendofincas activas: {e}")

    def obtener_potreros_todos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los potreros sin filtro.
        
        Returns:
            List[Dict]: Lista de diccionarios con estructura:
            {
                'finca_nombre': str,
                'nombre': str,
                'sector': str,
                'area_hectareas': float,
                'capacidad_maxima': int,
                'tipo_pasto': str,
                'estado': str,
                'id': int
            }
        
        Raises:
            Exception: Si la consulta falla
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        f.nombre as finca,
                        p.nombre,
                        COALESCE(s.nombre, 'N/A') as sector,
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.tipo_pasto,
                        p.estado,
                        p.id
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN sector s ON p.id_sector = s.id
                    ORDER BY f.nombre, p.nombre
                """
                cursor.execute(query)
                potreros = []
                for row in cursor.fetchall():
                    potreros.append({
                        'finca_nombre': row[0],
                        'nombre': row[1],
                        'sector': row[2],
                        'area_hectareas': row[3],
                        'capacidad_maxima': row[4],
                        'tipo_pasto': row[5],
                        'estado': row[6],
                        'id': row[7]
                    })
                return potreros
        except Exception as e:
            raise Exception(f"Error obteniendo potreros: {e}")

    def obtener_potreros_por_finca(self, finca_nombre: str) -> List[Dict[str, Any]]:
        """
        Obtiene potreros filtrados por nombre de finca.
        
        Args:
            finca_nombre: Nombre exacto de la finca (ej. "Finca A")
        
        Returns:
            List[Dict]: Lista de diccionarios con estructura de potrero
        
        Raises:
            Exception: Si la consulta falla
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        f.nombre as finca,
                        p.nombre,
                        COALESCE(s.nombre, 'N/A') as sector,
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.tipo_pasto,
                        p.estado,
                        p.id
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN sector s ON p.id_sector = s.id
                    WHERE f.nombre = ?
                    ORDER BY p.nombre
                """
                cursor.execute(query, (finca_nombre,))
                potreros = []
                for row in cursor.fetchall():
                    potreros.append({
                        'finca_nombre': row[0],
                        'nombre': row[1],
                        'sector': row[2],
                        'area_hectareas': row[3],
                        'capacidad_maxima': row[4],
                        'tipo_pasto': row[5],
                        'estado': row[6],
                        'id': row[7]
                    })
                return potreros
        except Exception as e:
            raise Exception(f"Error obteniendo potreros por finca '{finca_nombre}': {e}")

    def obtener_detalles_potrero(self, nombre_potrero: str, finca_nombre: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos de un potrero específico.
        
        Args:
            nombre_potrero: Nombre del potrero
            finca_nombre: Nombre de la finca propietaria
        
        Returns:
            Dict: Diccionario con detalles del potrero, o None si no existe
        
        Raises:
            Exception: Si la consulta falla
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        p.id,
                        p.nombre,
                        COALESCE(s.nombre, 'N/A') as sector,
                        p.area_hectareas,
                        p.capacidad_maxima,
                        p.tipo_pasto,
                        p.descripcion,
                        p.estado,
                        f.nombre as finca_nombre
                    FROM potrero p
                    LEFT JOIN finca f ON p.id_finca = f.id
                    LEFT JOIN sector s ON p.id_sector = s.id
                    WHERE p.nombre = ? AND f.nombre = ?
                """
                cursor.execute(query, (nombre_potrero, finca_nombre))
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'nombre': row[1],
                        'sector': row[2],
                        'area_hectareas': row[3],
                        'capacidad_maxima': row[4],
                        'tipo_pasto': row[5],
                        'descripcion': row[6],
                        'estado': row[7],
                        'finca_nombre': row[8]
                    }
                return None
        except Exception as e:
            raise Exception(f"Error obteniendo detalles del potrero '{nombre_potrero}': {e}")

    def obtener_animales_potrero(self, nombre_potrero: str, finca_nombre: str) -> List[Dict[str, Any]]:
        """
        Obtiene animales activos asignados a un potrero específico.
        
        Args:
            nombre_potrero: Nombre del potrero
            finca_nombre: Nombre de la finca propietaria
        
        Returns:
            List[Dict]: Lista de animales con estructura:
            {
                'codigo': str,
                'nombre': str,
                'raza': str,
                'sexo': str,
                'estado': str
            }
        
        Raises:
            Exception: Si la consulta falla
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT 
                        a.codigo,
                        a.nombre,
                        r.nombre as raza,
                        a.sexo,
                        a.estado
                    FROM animal a
                    LEFT JOIN raza r ON a.raza_id = r.id
                    WHERE a.id_potrero = (
                        SELECT p.id
                        FROM potrero p
                        LEFT JOIN finca f ON p.id_finca = f.id
                        WHERE p.nombre = ? AND f.nombre = ?
                    ) AND a.estado = 'Activo'
                    ORDER BY a.codigo
                """
                cursor.execute(query, (nombre_potrero, finca_nombre))
                animales = []
                for row in cursor.fetchall():
                    animales.append({
                        'codigo': row[0],
                        'nombre': row[1],
                        'raza': row[2],
                        'sexo': row[3],
                        'estado': row[4]
                    })
                return animales
        except Exception as e:
            raise Exception(f"Error obteniendo animales del potrero '{nombre_potrero}': {e}")

    def contar_animales_por_potrero(self, id_potrero: int) -> int:
        """
        Cuenta animales activos en un potrero por ID.
        
        Args:
            id_potrero: ID único del potrero
        
        Returns:
            int: Cantidad de animales activos
        
        Raises:
            Exception: Si la consulta falla
        """
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM animal 
                    WHERE id_potrero = ? AND estado = 'Activo'
                """, (id_potrero,))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            raise Exception(f"Error contando animales en potrero {id_potrero}: {e}")

    def obtener_metricas_potreros(self, potreros_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula métricas agregadas sobre lista de potreros.
        
        Args:
            potreros_data: Lista de diccionarios de potreros (ej. de obtener_potreros_todos)
        
        Returns:
            Dict: Métricas con estructura:
            {
                'total': int,
                'activos': int,
                'area_total_ha': float,
                'capacidad_total': int
            }
        """
        total = len(potreros_data)
        activos = sum(1 for p in potreros_data if p['estado'] == 'Activo')
        area_total = sum(p['area_hectareas'] for p in potreros_data if p['area_hectareas'] is not None)
        capacidad_total = sum(p['capacidad_maxima'] for p in potreros_data if p['capacidad_maxima'] is not None)
        
        return {
            'total': total,
            'activos': activos,
            'area_total_ha': area_total,
            'capacidad_total': capacidad_total
        }
