"""Constantes y helpers UI centralizados.
Permite estandarizar placeholders, textos y límites de longitud.
"""
PLACEHOLDERS = {
    "finca": "Seleccione una finca",
    "sector_codigo": "Código único",
    "sector_nombre": "Nombre del sector",
    "busqueda_general": "Buscar...",
    # Animales
    "animal_codigo": "Código Animal *",
    "animal_nombre": "Nombre Animal",
    "animal_peso_nac": "Peso al nacer",
    "animal_peso_compra": "Peso compra",
}

MAX_LENGTHS = {
    "codigo_sector": 20,
    "nombre_sector": 60,
    "comentario_sector": 300,
    # Animales
    "codigo_animal": 25,
    "nombre_animal": 80,
    "comentario_animal": 500,
    "hierro_animal": 50,
    "color_animal": 40,
}

def truncate(value: str, key: str) -> str:
    """Trunca un valor según la clave en MAX_LENGTHS si existe."""
    max_len = MAX_LENGTHS.get(key)
    if max_len and isinstance(value, str) and len(value) > max_len:
        return value[:max_len]
    return value
