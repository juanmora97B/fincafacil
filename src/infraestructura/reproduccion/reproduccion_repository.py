"""Repositorio de acceso a datos para el dominio Reproducción.

Encapsula todo el SQL relacionado con servicios reproductivos, gestaciones y partos.
No contiene lógica de negocio, solo acceso a datos.
"""
from typing import Any, Dict, List, Optional
from database.database import ejecutar_consulta


class ReproduccionRepository:
    """Repositorio para operaciones de persistencia del dominio Reproducción."""

    def _execute(self, sql: str, params: tuple, fetch: bool = False) -> Any:
        """Wrapper interno para ejecutar consultas SQL."""
        return ejecutar_consulta(sql, params, fetch=fetch)

    # ==================== CONSULTAS (SELECTs) ====================

    def contar_gestantes(self) -> int:
        """Contar animales actualmente gestantes."""
        sql = "SELECT COUNT(*) FROM servicio WHERE estado='Gestante'"
        result = self._execute(sql, (), fetch=True)
        return result[0][0] if result else 0

    def contar_proximos_partos(self, dias: int = 30) -> int:
        """Contar partos próximos en N días."""
        sql = """
            SELECT COUNT(*) FROM servicio
            WHERE estado='Gestante'
            AND fecha_parto_estimada BETWEEN DATE('now') AND DATE('now', '+' || ? || ' days')
        """
        result = self._execute(sql, (dias,), fetch=True)
        return result[0][0] if result else 0

    def contar_inseminaciones_ultimos_365_dias(self) -> int:
        """Contar inseminaciones del último año."""
        sql = """
            SELECT COUNT(*) FROM servicio
            WHERE tipo_servicio LIKE '%Inseminación%'
            AND DATE(fecha_servicio) >= DATE('now', '-365 days')
        """
        result = self._execute(sql, (), fetch=True)
        return result[0][0] if result else 0

    def contar_montas_naturales_ultimos_365_dias(self) -> int:
        """Contar montas naturales del último año."""
        sql = """
            SELECT COUNT(*) FROM servicio
            WHERE tipo_servicio = 'Monta Natural'
            AND DATE(fecha_servicio) >= DATE('now', '-365 days')
        """
        result = self._execute(sql, (), fetch=True)
        return result[0][0] if result else 0

    def listar_gestantes(self) -> List[Dict[str, Any]]:
        """Listar todas las hembras gestantes con detalles del servicio."""
        sql = """
            SELECT s.id, a.id, a.codigo, COALESCE(a.nombre,''), s.fecha_servicio, s.tipo_servicio,
                   COALESCE(m.codigo,'N/A'), s.fecha_parto_estimada, s.observaciones, s.estado
            FROM servicio s
            INNER JOIN animal a ON s.id_hembra = a.id
            LEFT JOIN animal m ON s.id_macho = m.id
            WHERE s.estado = 'Gestante'
            ORDER BY s.fecha_parto_estimada
        """
        results = self._execute(sql, (), fetch=True)
        if not results:
            return []

        from datetime import datetime, timedelta
        
        output = []
        for r in results:
            try:
                # r es un diccionario con nombres de columna como claves
                # La consulta retorna columnas en orden: id, a.id, codigo, nombre, fecha_servicio, tipo_servicio, codigo_macho, fecha_parto_estimada, observaciones, estado
                # Como no tenemos nombres de columna explícitos, usamos índices de diccionario
                keys = list(r.keys())
                
                fecha_parto = r[keys[7]] if len(keys) > 7 else None
                dias_gest = 0
                if fecha_parto:
                    try:
                        dias_gest = (datetime.strptime(fecha_parto, "%Y-%m-%d").date() - datetime.now().date()).days
                    except:
                        dias_gest = 0
                
                output.append({
                    "servicio_id": r[keys[0]],
                    "animal_id": r[keys[1]],
                    "codigo": r[keys[2]],
                    "nombre": r[keys[3]],
                    "fecha_servicio": r[keys[4]],
                    "tipo_servicio": r[keys[5]],
                    "toro_semen": r[keys[6]],
                    "fecha_parto_estimada": fecha_parto,
                    "observaciones": r[keys[8]] if len(keys) > 8 else None,
                    "estado": r[keys[9]] if len(keys) > 9 else None,
                    "dias_gestacion": dias_gest,
                })
            except Exception as e:
                print(f"[ERROR] Error procesando gestante: {e}, row keys: {list(r.keys())}, row: {r}")
                continue
        
        return output

    def listar_proximos_partos(self, dias: int = 60) -> List[Dict[str, Any]]:
        """Listar partos próximos en los siguientes N días."""
        sql = """
            SELECT s.id, a.id, a.codigo, COALESCE(a.nombre,''), s.fecha_servicio, s.tipo_servicio,
                   COALESCE(m.codigo,'N/A'), s.fecha_parto_estimada, s.estado
            FROM servicio s
            INNER JOIN animal a ON s.id_hembra = a.id
            LEFT JOIN animal m ON s.id_macho = m.id
            WHERE s.estado = 'Gestante'
            AND DATE(s.fecha_parto_estimada) BETWEEN DATE('now') AND DATE('now', '+' || ? || ' days')
            ORDER BY s.fecha_parto_estimada
        """
        results = self._execute(sql, (dias,), fetch=True)
        if not results:
            return []

        return [
            {
                "servicio_id": r[0],
                "animal_id": r[1],
                "codigo": r[2],
                "nombre": r[3],
                "fecha_servicio": r[4],
                "tipo_servicio": r[5],
                "toro_semen": r[6],
                "fecha_parto_estimada": r[7],
                "estado": r[8],
            }
            for r in results
        ]

    def obtener_hembra_por_servicio(self, servicio_id: int) -> Optional[int]:
        """Obtener id_hembra asociada a un servicio."""
        sql = "SELECT id_hembra FROM servicio WHERE id = ?"
        result = self._execute(sql, (servicio_id,), fetch=True)
        return result[0][0] if result else None

    def listar_fincas_activas(self) -> List[Dict[str, Any]]:
        """Listar fincas activas."""
        sql = "SELECT id, nombre FROM finca WHERE estado='Activo' ORDER BY nombre"
        results = self._execute(sql, (), fetch=True)
        output = []
        for r in results:
            try:
                keys = list(r.keys())
                output.append({"id": r[keys[0]], "nombre": r[keys[1]]})
            except Exception as e:
                print(f"[ERROR] Error procesando finca: {e}")
                continue
        return output if output else []

    def listar_hembras_por_finca(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Listar hembras, opcionalmente filtradas por finca."""
        if finca_id:
            sql = """
                SELECT id, codigo, COALESCE(nombre,'')
                FROM animal
                WHERE id_finca = ? AND sexo = 'Hembra'
                ORDER BY codigo
            """
            results = self._execute(sql, (finca_id,), fetch=True)
        else:
            sql = """
                SELECT id, codigo, COALESCE(nombre,'')
                FROM animal
                WHERE sexo = 'Hembra'
                ORDER BY codigo
            """
            results = self._execute(sql, (), fetch=True)

        output = []
        for r in results:
            try:
                keys = list(r.keys())
                output.append({"id": r[keys[0]], "codigo": r[keys[1]], "nombre": r[keys[2]]})
            except Exception as e:
                print(f"[ERROR] Error procesando hembra: {e}")
                continue
        return output if output else []

    def listar_machos_por_finca(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Listar machos, opcionalmente filtrados por finca."""
        if finca_id:
            sql = """
                SELECT id, codigo, COALESCE(nombre,'')
                FROM animal
                WHERE id_finca = ? AND sexo = 'Macho'
                ORDER BY codigo
            """
            results = self._execute(sql, (finca_id,), fetch=True)
        else:
            sql = """
                SELECT id, codigo, COALESCE(nombre,'')
                FROM animal
                WHERE sexo = 'Macho'
                ORDER BY codigo
            """
            results = self._execute(sql, (), fetch=True)

        output = []
        for r in results:
            try:
                keys = list(r.keys())
                output.append({"id": r[keys[0]], "codigo": r[keys[1]], "nombre": r[keys[2]]})
            except Exception as e:
                print(f"[ERROR] Error procesando macho: {e}")
                continue
        return output if output else []

    def contar_servicios_activos_hembra(self, hembra_id: int) -> int:
        """Contar servicios activos (gestante) para una hembra."""
        sql = "SELECT COUNT(*) FROM servicio WHERE id_hembra = ? AND estado = 'Gestante'"
        result = self._execute(sql, (hembra_id,), fetch=True)
        return result[0][0] if result else 0

    def contar_servicios_misma_fecha(self, hembra_id: int, fecha_servicio: str) -> int:
        """Verificar si existe servicio duplicado en misma fecha."""
        sql = "SELECT COUNT(*) FROM servicio WHERE id_hembra = ? AND fecha_servicio = ?"
        result = self._execute(sql, (hembra_id, fecha_servicio), fetch=True)
        return result[0][0] if result else 0

    def obtener_finca_de_animal(self, animal_id: int) -> Optional[int]:
        """Obtener finca a la que pertenece un animal."""
        sql = "SELECT id_finca FROM animal WHERE id = ?"
        result = self._execute(sql, (animal_id,), fetch=True)
        return result[0][0] if result else None

    def obtener_ultimo_codigo_cria(self) -> Optional[str]:
        """Obtener el último código de cría generado (formato A####)."""
        sql = "SELECT MAX(CAST(SUBSTR(codigo, 2) AS INTEGER)) FROM animal WHERE codigo LIKE 'A%'"
        result = self._execute(sql, (), fetch=True)
        return str(result[0][0]) if result and result[0][0] else None

    # ==================== ESCRITURA (INSERTs/UPDATEs) ====================

    def insertar_servicio(
        self,
        hembra_id: int,
        macho_id: Optional[int],
        fecha_servicio: str,
        tipo_servicio: str,
        estado: str,
        fecha_parto_estimada: str,
        observaciones: Optional[str] = None,
    ) -> None:
        """Insertar nuevo servicio reproductivo."""
        sql = """
            INSERT INTO servicio (id_hembra, id_macho, fecha_servicio, tipo_servicio, estado, fecha_parto_estimada, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self._execute(
            sql,
            (hembra_id, macho_id, fecha_servicio, tipo_servicio, estado, fecha_parto_estimada, observaciones),
            fetch=False,
        )

    def insertar_comentario(
        self,
        animal_id: int,
        fecha: str,
        tipo: str,
        nota: str,
        autor: str = "Sistema",
    ) -> None:
        """Insertar comentario en bitácora de animal."""
        sql = """
            INSERT INTO comentario (id_animal, fecha, tipo, nota, autor)
            VALUES (?, ?, ?, ?, ?)
        """
        self._execute(sql, (animal_id, fecha, tipo, nota, autor), fetch=False)

    def actualizar_servicio_parto(
        self,
        servicio_id: int,
        estado: str,
        fecha_parto_real: str,
        observaciones: Optional[str] = None,
    ) -> None:
        """Actualizar servicio con información de parto."""
        sql = "UPDATE servicio SET estado = ?, fecha_parto_real = ?, observaciones = ? WHERE id = ?"
        self._execute(sql, (estado, fecha_parto_real, observaciones, servicio_id), fetch=False)

    def insertar_cria(
        self,
        codigo: str,
        nombre: str,
        sexo: str,
        fecha_nacimiento: str,
        tipo_ingreso: str,
        madre_id: int,
        finca_id: int,
        peso_nacimiento: Optional[float] = None,
        estado_cria: Optional[str] = None,
    ) -> None:
        """Insertar nueva cría."""
        sql = """
            INSERT INTO animal (codigo, nombre, sexo, fecha_nacimiento, tipo_ingreso, id_madre,
                               id_finca, peso_nacimiento, estado, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'))
        """
        self._execute(
            sql,
            (codigo, nombre, sexo, fecha_nacimiento, tipo_ingreso, madre_id, finca_id, peso_nacimiento, estado_cria),
            fetch=False,
        )

    def actualizar_estado_servicio(self, servicio_id: int, estado: str) -> None:
        """Actualizar solo el estado de un servicio."""
        sql = "UPDATE servicio SET estado = ? WHERE id = ?"
        self._execute(sql, (estado, servicio_id), fetch=False)
