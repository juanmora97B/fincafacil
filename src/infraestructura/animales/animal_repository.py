"""Repositorio de acceso a datos para Animales (Infraestructura).

Contiene SQL crudo y delega la ejecución a `ejecutar_consulta` (legacy) para
mantener compatibilidad y formato de resultados existente.
"""
from typing import Any, Dict, List, Optional

from database.database import ejecutar_consulta


class AnimalRepository:
    """Repositorio que encapsula las operaciones CRUD sobre animales."""

    def __init__(self, executor=None) -> None:
        self._execute = executor or ejecutar_consulta

    # CRUD principales
    def crear(self, data: Dict[str, Any]) -> None:
        columnas = list(data.keys())
        valores = list(data.values())
        placeholders = ["?"] * len(columnas)
        sql = f"INSERT INTO animal ({', '.join(columnas)}) VALUES ({', '.join(placeholders)})"
        self._execute(sql, tuple(valores), fetch=False)

    def actualizar(self, animal_id: int, cambios: Dict[str, Any]) -> None:
        if not cambios:
            return
        sets = [f"{k} = ?" for k in cambios.keys()]
        valores = list(cambios.values()) + [animal_id]
        sql = f"UPDATE animal SET {', '.join(sets)} WHERE id = ?"
        self._execute(sql, tuple(valores), fetch=False)

    def eliminar(self, animal_id: int) -> None:
        self._execute("DELETE FROM animal WHERE id = ?", (animal_id,), fetch=False)

    def obtener_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        res = self._execute("SELECT * FROM animal WHERE codigo = ?", (codigo,), fetch=True)
        return res[0] if res else None

    def existe_codigo(self, codigo: str) -> bool:
        res = self._execute("SELECT id FROM animal WHERE codigo = ?", (codigo,), fetch=True)
        return bool(res)

    def listar(self, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        base = "SELECT * FROM animal"
        where = []
        params: List[Any] = []
        filtros = filtros or {}

        for clave in ("estado", "raza_id", "id_finca", "lote_id", "id_sector"):
            if clave in filtros and filtros[clave] not in (None, ""):
                where.append(f"{clave} = ?")
                params.append(filtros[clave])

        if where:
            base += " WHERE " + " AND ".join(where)

        base += " ORDER BY fecha_creacion DESC"
        return self._execute(base, tuple(params) if params else (), fetch=True) or []

    # Operaciones complementarias
    def registrar_peso(
        self,
        animal_id: int,
        fecha: str,
        peso: float,
        metodo: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> None:
        self._execute(
            """
            INSERT INTO peso (animal_id, fecha, peso, metodo, observaciones)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(animal_id, fecha) DO UPDATE SET peso=excluded.peso, metodo=excluded.metodo, observaciones=excluded.observaciones
            """,
            (animal_id, fecha, peso, metodo, observaciones),
            fetch=False,
        )

    def registrar_movimiento(
        self,
        animal_id: int,
        lote_destino_id: int,
        fecha_movimiento: str,
        tipo_movimiento: str = "Traslado",
        lote_origen_id: Optional[int] = None,
        motivo: Optional[str] = None,
        observaciones: Optional[str] = None,
    ) -> None:
        self._execute(
            """
            INSERT INTO movimiento (animal_id, lote_origen_id, lote_destino_id, fecha_movimiento, tipo_movimiento, motivo, observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (animal_id, lote_origen_id, lote_destino_id, fecha_movimiento, tipo_movimiento, motivo, observaciones),
            fetch=False,
        )

    # ==================== LECTURA PARA UI: Catálogos ====================
    def listar_fincas(self, excluir_estados: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Listar fincas activas/no eliminadas."""
        excluir = excluir_estados or ["eliminada", "eliminado", "inactiva", "inactivo"]
        sql = "SELECT id, nombre, estado FROM finca ORDER BY nombre"
        results = self._execute(sql, (), fetch=True) or []
        return [r for r in results if (r.get("estado") or "").lower() not in excluir]

    def listar_razas(self, excluir_estados: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Listar razas activas."""
        excluir = excluir_estados or ["inactiva", "eliminada"]
        sql = "SELECT id, nombre, estado FROM raza ORDER BY nombre"
        results = self._execute(sql, (), fetch=True) or []
        return [r for r in results if (r.get("estado") or "").lower() not in excluir]

    def listar_condiciones_corporales(self) -> List[Dict[str, Any]]:
        """Listar condiciones corporales activas."""
        sql = "SELECT codigo, descripcion FROM condicion_corporal WHERE estado='Activo' ORDER BY codigo"
        return self._execute(sql, (), fetch=True) or []

    def listar_potreros_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Listar potreros de una finca."""
        sql = "SELECT id, nombre FROM potrero WHERE id_finca = ? OR finca_id = ? ORDER BY nombre"
        return self._execute(sql, (finca_id, finca_id), fetch=True) or []

    def listar_lotes_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Listar lotes de una finca."""
        sql = "SELECT id, nombre FROM lote WHERE id_finca = ? OR finca_id = ? ORDER BY nombre"
        return self._execute(sql, (finca_id, finca_id), fetch=True) or []

    def listar_sectores_por_finca(self, finca_id: int) -> List[Dict[str, Any]]:
        """Listar sectores de una finca."""
        sql = "SELECT id, nombre FROM sector WHERE id_finca = ? OR finca_id = ? ORDER BY nombre"
        return self._execute(sql, (finca_id, finca_id), fetch=True) or []

    def listar_animales_por_finca_y_sexo(self, finca_id: int, sexo: str) -> List[Dict[str, Any]]:
        """Listar animales de una finca con sexo específico (madres/padres)."""
        finca_col = self._detectar_columna_finca()
        sql = f"SELECT id, codigo, nombre FROM animal WHERE {finca_col} = ? AND sexo = ? ORDER BY codigo"
        return self._execute(sql, (finca_id, sexo), fetch=True) or []

    def listar_procedencias(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Listar procedencias, opcionalmente filtradas por finca."""
        if finca_id:
            sql = "SELECT id, descripcion FROM procedencia WHERE id_finca = ? OR finca_id = ? OR id_finca IS NULL ORDER BY descripcion"
            return self._execute(sql, (finca_id, finca_id), fetch=True) or []
        else:
            sql = "SELECT id, descripcion FROM procedencia ORDER BY descripcion"
            return self._execute(sql, (), fetch=True) or []

    def listar_vendedores(self, finca_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Listar vendedores, opcionalmente filtrados por finca."""
        if finca_id:
            sql = "SELECT id, nombre FROM vendedor WHERE id_finca = ? OR finca_id = ? OR id_finca IS NULL ORDER BY nombre"
            return self._execute(sql, (finca_id, finca_id), fetch=True) or []
        else:
            sql = "SELECT id, nombre FROM vendedor ORDER BY nombre"
            return self._execute(sql, (), fetch=True) or []

    def listar_calidades(self) -> List[Dict[str, Any]]:
        """Listar calidades desde catálogo calidad_animal."""
        try:
            sql = "SELECT descripcion FROM calidad_animal ORDER BY descripcion"
            results = self._execute(sql, (), fetch=True) or []
            return [r for r in results if r.get("descripcion")]
        except Exception:
            sql = "SELECT DISTINCT calidad FROM animal WHERE calidad IS NOT NULL AND TRIM(calidad) <> '' ORDER BY calidad"
            results = self._execute(sql, (), fetch=True) or []
            return [{"descripcion": r.get("calidad")} for r in results if r.get("calidad")]

    def listar_estados_salud_distintos(self) -> List[str]:
        """Listar valores distintos de salud desde animal."""
        sql = "SELECT DISTINCT salud FROM animal WHERE salud IS NOT NULL AND TRIM(salud) <> '' ORDER BY salud"
        results = self._execute(sql, (), fetch=True) or []
        return [str(r.get("salud")) for r in results if r.get("salud")]

    def listar_estados_distintos(self) -> List[str]:
        """Listar valores distintos de estado desde animal."""
        sql = "SELECT DISTINCT estado FROM animal WHERE estado IS NOT NULL AND TRIM(estado) <> '' ORDER BY estado"
        results = self._execute(sql, (), fetch=True) or []
        return [str(r.get("estado")) for r in results if r.get("estado")]

    # Helper privado para detectar nombres de columna dinámicamente
    def _detectar_columna_finca(self, tabla: str = "animal") -> str:
        """Detecta si la tabla usa 'finca_id' o 'id_finca'."""
        sql = f"PRAGMA table_info({tabla})"
        cols = self._execute(sql, (), fetch=True) or []
        col_names = {c.get("name") for c in cols}
        return "finca_id" if "finca_id" in col_names else "id_finca"
