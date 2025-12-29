"""
Seed de tratamientos (Salud)
- Usa SaludService y ConfiguracionService
- Idempotente: evita duplicar por (animal, fecha_inicio, producto)
"""
import random
from datetime import datetime, timedelta

from src.infraestructura.salud.salud_service import SaludService
from src.infraestructura.salud.salud_repository import SaludRepository
from src.infraestructura.configuracion.configuracion_service import ConfiguracionService
from src.database.database import ejecutar_consulta


def ensure_salud_tables() -> None:
    """Asegura tablas de salud creadas (diagnóstico/tratamiento)."""
    SaludRepository().crear_tablas_si_no_existen()


def cargar_veterinarios(config_service: ConfiguracionService) -> list[str]:
    """Obtiene nombres de empleados activos para usar como 'veterinario'."""
    try:
        empleados = config_service.listar_empleados_activos()
        nombres: list[str] = []
        for e in empleados:
            nombre = " ".join([n for n in [e.get("nombres"), e.get("apellidos")] if n])
            if nombre.strip():
                nombres.append(nombre.strip())
        return nombres or ["Veterinario Externo"]
    except Exception:
        return ["Veterinario Externo"]


def cargar_animales_activos(salud_service: SaludService) -> list[dict]:
    """Obtiene animales activos desde SaludService (JOIN interno)."""
    try:
        animales = salud_service.cargar_animales()
        return [
            {"id": a.get("id"), "codigo": a.get("codigo"), "nombre": a.get("nombre")}
            for a in animales
            if a.get("id") is not None
        ]
    except Exception:
        return []


def tratamiento_existe(animal_id: int, fecha_inicio: str, producto: str) -> bool:
    """Idempotencia: verifica si ya existe tratamiento igual para ese día."""
    res = ejecutar_consulta(
        "SELECT COUNT(*) AS c FROM tratamiento WHERE id_animal = ? AND fecha_inicio = ? AND producto = ?",
        (animal_id, fecha_inicio, producto),
        fetch=True,
    )
    try:
        return bool(res and int(res[0].get("c", 0)) > 0)
    except Exception:
        return False


def seed_tratamientos(cantidad: int = 10) -> None:
    ensure_salud_tables()
    salud = SaludService()
    config = ConfiguracionService()

    animales = cargar_animales_activos(salud)
    if not animales:
        print("⚠ No hay animales activos; se omiten tratamientos.")
        return

    veterinarios = cargar_veterinarios(config)

    # Catálogo base de tratamientos (tipo, producto, días para próxima dosis)
    catalogo = [
        ("Vacunación", "Fiebre Aftosa", 180, "5 ml IM"),
        ("Desparasitación", "Ivermectina 1%", 90, "1 ml/50 kg"),
        ("Antibiótico", "Oxitetraciclina", None, "10 ml IM"),
        ("Vitaminas", "ADE inyectable", 180, "5 ml IM"),
        ("Minerales", "Sales minerales", 30, "Según etiqueta"),
        ("Vacunación", "Brucelosis", 365, "5 ml SC"),
        ("Desparasitación", "Albendazol", 120, "7.5 mg/kg"),
        ("Antibiótico", "Penicilina", None, "10 ml IM"),
        ("Vitaminas", "Complejo B", 60, "5 ml IM"),
        ("Otro", "Curación de heridas", None, None),
    ]

    hoy = datetime.now().date()
    creados = 0
    for i in range(cantidad):
        tipo, producto, prox_dias, dosis = random.choice(catalogo)
        animal = random.choice(animales)
        # Fechas realistas en los últimos ~120 días
        delta = random.randint(0, 120)
        fecha_inicio = (hoy - timedelta(days=delta)).strftime("%Y-%m-%d")
        fecha_proxima = (
            (hoy + timedelta(days=prox_dias)).strftime("%Y-%m-%d") if prox_dias else None
        )
        veterinario = random.choice(veterinarios)

        if tratamiento_existe(int(animal["id"]), fecha_inicio, producto):
            print(f"↪ Tratamiento existente: {animal['codigo']} {producto} ({fecha_inicio})")
            continue

        try:
            salud.registrar_tratamiento(
                animal_id=int(animal["id"]),
                fecha_inicio=fecha_inicio,
                tipo_tratamiento=tipo,
                producto=producto,
                dosis=dosis,
                veterinario=veterinario,
                comentario=f"Programa: {tipo} - {producto}",
                fecha_proxima=fecha_proxima,
            )
            creados += 1
            print(
                f"✔ Tratamiento creado: {animal['codigo']} {tipo}/{producto} por {veterinario}"
            )
        except Exception as e:
            print(
                f"⚠ Error creando tratamiento para {animal['codigo']}: {e}"
            )

    print(f"Total tratamientos creados: {creados}. Animales considerados: {len(animales)}")


if __name__ == "__main__":
    seed_tratamientos(cantidad=10)
