"""
Seed de ventas
- Crea tabla `venta` si falta (esquema del módulo UI)
- Inserta ventas idempotentes y actualiza estado del animal a 'Vendido'
"""
import random
from datetime import datetime, timedelta

from src.infraestructura.salud.salud_service import SaludService
from src.database.database import ejecutar_consulta


def ensure_tabla_venta() -> None:
    """Crea tabla de ventas si no existe (siguiendo el módulo de UI)."""
    ejecutar_consulta(
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


def venta_existe(animal_id: int, fecha: str) -> bool:
    """Idempotencia: evita duplicar venta del mismo animal en misma fecha."""
    res = ejecutar_consulta(
        "SELECT COUNT(*) AS c FROM venta WHERE animal_id = ? AND fecha = ?",
        (animal_id, fecha),
        fetch=True,
    )
    try:
        return bool(res and int(res[0].get("c", 0)) > 0)
    except Exception:
        return False


def marcar_animal_vendido(animal_id: int) -> None:
    ejecutar_consulta("UPDATE animal SET estado = 'Vendido' WHERE id = ?", (animal_id,))


def seed_ventas(cantidad: int = 5) -> None:
    ensure_tabla_venta()
    salud = SaludService()

    # Animales activos (el service ya filtra por estado)
    animales = salud.cargar_animales()
    candidatos = [a for a in animales if a.get("id") is not None]
    if not candidatos:
        print("⚠ No hay animales activos; se omiten ventas.")
        return

    motivos = [
        "Venta directa",
        "Subasta",
        "Consignación",
        "Emergencia",
        "Renovación de stock",
        "Otro",
    ]
    destinos = [
        "Mercado local",
        "Frigorífico",
        "Exportación",
        "Consumidor final",
        "Otro productor",
        "Otro",
    ]

    hoy = datetime.now().date()
    creados = 0
    # Selección aleatoria sin exceder disponibles
    seleccion = random.sample(candidatos, k=min(cantidad, len(candidatos)))
    for a in seleccion:
        animal_id = int(a["id"])  # type: ignore[index]
        codigo = str(a.get("codigo", ""))
        # Fecha en los últimos ~60 días
        fecha = (hoy - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
        precio = float(random.randint(1_200_000, 3_500_000))  # precio total en moneda local
        motivo = random.choice(motivos)
        destino = random.choice(destinos)
        observaciones = f"{motivo} hacia {destino}."

        if venta_existe(animal_id, fecha):
            print(f"↪ Venta existente: {codigo} ({fecha})")
            continue

        try:
            ejecutar_consulta(
                """
                INSERT INTO venta (animal_id, fecha, precio_total, motivo_venta, destino_venta, observaciones)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (animal_id, fecha, precio, motivo, destino, observaciones),
            )
            marcar_animal_vendido(animal_id)
            creados += 1
            print(
                f"✔ Venta creada: {codigo} por ${precio:,.0f} ({motivo} → {destino})"
            )
        except Exception as e:
            print(f"⚠ Error registrando venta de {codigo}: {e}")

    print(f"Total ventas creadas: {creados}. Animales considerados: {len(candidatos)}")


if __name__ == "__main__":
    seed_ventas(cantidad=5)
