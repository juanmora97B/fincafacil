from typing import Optional, List, Dict, Any
from database.database import ejecutar_consulta


def crear_animal(data: Dict[str, Any]) -> None:
    """
    Crea un animal asegurando unicidad de codigo y presencia de claves básicas.
    Campos mínimos: codigo, sexo, estado (por defecto 'Activo'). Opcionalmente raza_id, id_finca.
    """
    # Validaciones mínimas
    codigo = data.get("codigo")
    if not codigo:
        raise ValueError("El campo 'codigo' es obligatorio")

    sexo = data.get("sexo")
    if sexo not in ("Macho", "Hembra", None, ""):
        raise ValueError("El campo 'sexo' debe ser 'Macho' o 'Hembra'")

    # Unicidad de código
    existe = ejecutar_consulta(
        "SELECT id FROM animal WHERE codigo = ?",
        (codigo,),
        fetch=True,
    )
    if existe:
        raise ValueError(f"Ya existe un animal con código '{codigo}'")

    # Construir INSERT dinámico según claves presentes
    columnas = []
    valores = []
    placeholders = []
    for k, v in data.items():
        columnas.append(k)
        valores.append(v)
        placeholders.append("?")

    sql = f"INSERT INTO animal ({', '.join(columnas)}) VALUES ({', '.join(placeholders)})"
    ejecutar_consulta(sql, tuple(valores), fetch=False)


def actualizar_animal(animal_id: int, cambios: Dict[str, Any]) -> None:
    """Actualiza columnas específicas del animal."""
    if not cambios:
        return
    sets = []
    valores = []
    for k, v in cambios.items():
        sets.append(f"{k} = ?")
        valores.append(v)
    valores.append(animal_id)
    sql = f"UPDATE animal SET {', '.join(sets)} WHERE id = ?"
    ejecutar_consulta(sql, tuple(valores), fetch=False)


def eliminar_animal(animal_id: int) -> None:
    """Elimina un animal por id."""
    ejecutar_consulta("DELETE FROM animal WHERE id = ?", (animal_id,), fetch=False)


def obtener_animal_por_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """Devuelve un animal por su código."""
    res = ejecutar_consulta("SELECT * FROM animal WHERE codigo = ?", (codigo,), fetch=True)
    return res[0] if res else None


def listar_animales(filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Lista animales con filtros opcionales: estado, raza_id, id_finca, lote_id, id_sector.
    """
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
    return ejecutar_consulta(base, tuple(params) if params else None, fetch=True) or []


def registrar_peso(animal_id: int, fecha: str, peso: float, metodo: Optional[str] = None, observaciones: Optional[str] = None) -> None:
    """Registra o actualiza un pesaje para un animal en una fecha (UNIQUE por animal_id, fecha)."""
    ejecutar_consulta(
        """
        INSERT INTO peso (animal_id, fecha, peso, metodo, observaciones)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(animal_id, fecha) DO UPDATE SET peso=excluded.peso, metodo=excluded.metodo, observaciones=excluded.observaciones
        """,
        (animal_id, fecha, peso, metodo, observaciones),
        fetch=False,
    )


def registrar_movimiento(animal_id: int, lote_destino_id: int, fecha_movimiento: str, tipo_movimiento: str = "Traslado", lote_origen_id: Optional[int] = None, motivo: Optional[str] = None, observaciones: Optional[str] = None) -> None:
    """Registra un movimiento en la tabla movimiento."""
    ejecutar_consulta(
        """
        INSERT INTO movimiento (animal_id, lote_origen_id, lote_destino_id, fecha_movimiento, tipo_movimiento, motivo, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (animal_id, lote_origen_id, lote_destino_id, fecha_movimiento, tipo_movimiento, motivo, observaciones),
        fetch=False,
    )
