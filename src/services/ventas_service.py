"""
Servicio de Ventas (FASE 4)
- Enforce permisos en operaciones críticas
- Mantener separación UI ↔ Service ↔ Repository

Operaciones cubiertas:
- registrar_venta_animal
- eliminar_venta
- obtener_historial_ventas
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime
import logging

from src.core.permission_service import UserContext, require
from src.core.audit_service import log_event
from src.database.database import get_db_connection
from src.services.data_lock_service import get_data_lock_service
from src.core.permission_decorators import require_permission, audit_action
from src.core.permissions_manager import PermissionEnum

logger = logging.getLogger("ventas_service")


@dataclass
class VentaAnimal:
    animal_id: int
    fecha: str
    precio_total: float
    motivo_venta: Optional[str] = None
    destino_venta: Optional[str] = None
    observaciones: Optional[str] = None


@require_permission(PermissionEnum.VENTAS_CREAR)
@audit_action("ventas", "CREAR")
def registrar_venta_animal(user: UserContext, data: VentaAnimal) -> int:
    """
    Registra una venta de animal aplicando permisos y reglas básicas.
    Retorna el id de la venta creada.
    """
    require(user, "CREATE")

    # Validaciones mínimas (evitar dependencia de UI)
    if data.precio_total <= 0:
        raise ValueError("El precio total debe ser mayor a 0")
    
    # Validar que no sea período cerrado
    from datetime import datetime
    lock_service = get_data_lock_service()
    fecha_obj = datetime.strptime(data.fecha, "%Y-%m-%d").date() if isinstance(data.fecha, str) else data.fecha
    lock_service.validate_before_save(fecha_obj, "ventas")

    # Persistencia
    with get_db_connection() as conn:
        cur = conn.cursor()

        # Asegurar tabla (esquema según ventas_main)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                precio_total REAL NOT NULL,
                motivo_venta TEXT,
                destino_venta TEXT,
                observaciones TEXT,
                fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (animal_id) REFERENCES animal (id)
            )
            """
        )

        # Verificar animal existente y no vendido/muerto
        cur.execute("SELECT estado FROM animal WHERE id = ?", (data.animal_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Animal #{data.animal_id} no existe")
        estado = row[0]
        if estado and estado.lower() in {"vendido", "muerto"}:
            raise ValueError(f"Animal #{data.animal_id} con estado '{estado}' no puede venderse")

        # Insertar venta
        cur.execute(
            """
            INSERT INTO venta (
                animal_id, fecha, precio_total, motivo_venta,
                destino_venta, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.animal_id,
                data.fecha,
                float(data.precio_total),
                data.motivo_venta,
                data.destino_venta,
                (data.observaciones or None),
            ),
        )
        venta_id = cur.lastrowid or 0

        # Actualizar estado del animal
        cur.execute("UPDATE animal SET estado = 'Vendido' WHERE id = ?", (data.animal_id,))
        conn.commit()

    try:
        log_event(
            usuario=user.username,
            modulo="ventas",
            accion="CREAR",
            entidad=f"venta:{venta_id}",
            resultado="OK",
            mensaje=f"Animal #{data.animal_id} vendido por ${data.precio_total:,.0f}"
        )
    except Exception:
        pass

    logger.info(f"Venta creada (id={venta_id}) por {user.username}")
    return int(venta_id)


@require_permission(PermissionEnum.VENTAS_ELIMINAR)
@audit_action("ventas", "ELIMINAR")
def eliminar_venta(user: UserContext, venta_id: int) -> None:
    """Elimina una venta. Requiere rol con permiso DELETE (ADMIN u OPERADOR)."""
    require(user, "DELETE")

    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Verificar que no sea período cerrado
        cur.execute("SELECT fecha FROM venta WHERE id = ?", (venta_id,))
        row = cur.fetchone()
        if row:
            from datetime import datetime
            lock_service = get_data_lock_service()
            fecha_obj = datetime.strptime(row[0], "%Y-%m-%d").date() if isinstance(row[0], str) else row[0]
            lock_service.validate_before_save(fecha_obj, "ventas")
        
        cur.execute("DELETE FROM venta WHERE id = ?", (venta_id,))
        conn.commit()

    try:
        log_event(
            usuario=user.username,
            modulo="ventas",
            accion="ELIMINAR",
            entidad=f"venta:{venta_id}",
            resultado="OK",
            mensaje="Venta eliminada"
        )
    except Exception:
        pass

    logger.info(f"Venta {venta_id} eliminada por {user.username}")


@require_permission(PermissionEnum.VENTAS_VER)
def obtener_historial_ventas(user: UserContext, limit: int = 100) -> List[Dict]:
    """Obtiene historial de ventas (READ)."""
    require(user, "READ")

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                v.id,
                v.fecha,
                a.codigo || ' - ' || COALESCE(a.nombre, 'Sin nombre') as animal,
                v.precio_total,
                v.motivo_venta,
                v.destino_venta,
                v.observaciones
            FROM venta v
            JOIN animal a ON v.animal_id = a.id
            ORDER BY v.fecha DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()

    ventas: List[Dict] = []
    for r in rows:
        ventas.append(
            {
                "id": r[0],
                "fecha": r[1],
                "animal": r[2],
                "precio_total": float(r[3]) if r[3] is not None else 0.0,
                "motivo_venta": r[4],
                "destino_venta": r[5],
                "observaciones": r[6],
            }
        )
    return ventas
