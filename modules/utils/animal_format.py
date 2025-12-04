"""Utilidades de formato para representación textual de animales.
Centraliza armado de ficha para reutilizar en GUI y futuros reportes.
"""
from typing import Mapping, Any

__all__ = ["build_animal_info_text"]


def build_animal_info_text(animal: Mapping[str, Any]) -> str:
    """Genera el bloque de texto formateado de información completa del animal.

    Args:
        animal: Diccionario/Mapping con claves del SELECT enriquecido.

    Returns:
        str: Texto listo para colocar en un CTkLabel / tooltip / exportación.

    Notas:
        - Usa get(...) para tolerar claves faltantes.
        - No hace traducción de unidades; asume pesos ya normalizados a kg.
        - Evita fallar si algún campo es None.
    """
    inventariado_flag = "Sí" if animal.get("inventariado") == 1 else "No"
    return (
        "🐄 **INFORMACIÓN COMPLETA DEL ANIMAL**\n\n"
        f"🏷️  **CÓDIGO:** {animal.get('codigo')}\n"
        f"📛  **NOMBRE:** {animal.get('nombre') or 'No asignado'}\n"
        f"🏞️  **FINCA:** {animal.get('finca') or 'No asignada'}\n"
        f"📥  **TIPO INGRESO:** {animal.get('tipo_ingreso')}\n\n"
        f"⚤  **SEXO:** {animal.get('sexo')}\n"
        f"🐄  **RAZA:** {animal.get('raza') or 'No especificada'}\n"
        "📍  **UBICACIÓN:** \n"
        f"    • Potrero: {animal.get('potrero') or 'No asignado'}\n"
        f"    • Lote: {animal.get('lote') or 'No asignado'}\n"
    f"    • Sector: {animal.get('sector') or 'No asignado'}\n\n"
        "📅  **FECHAS:**\n"
        f"    • Nacimiento: {animal.get('fecha_nacimiento') or 'No registrada'}\n"
        f"    • Compra: {animal.get('fecha_compra') or 'No aplica'}\n"
        f"    • Registro: {animal.get('fecha_registro') or 'No registrada'}\n\n"
        "👨‍👩‍👧  **INFORMACIÓN PADRES:**\n"
        f"    • Madre: {animal.get('codigo_madre') or 'No registrada'} ({animal.get('nombre_madre') or ''})\n"
        f"    • Padre: {animal.get('codigo_padre') or 'No registrada'} ({animal.get('nombre_padre') or ''})\n"
        f"    • Concepción: {animal.get('tipo_concepcion') or 'No aplica'}\n\n"
        "⚖️  **PESOS:**\n"
        f"    • Nacimiento: {animal.get('peso_nacimiento') or '0'} kg\n"
        f"    • Compra: {animal.get('peso_compra') or '0'} kg\n\n"
        f"🏥  **SALUD:** {animal.get('salud')}\n"
        f"✅  **ESTADO:** {animal.get('estado')}\n"
        f"📋  **INVENTARIADO:** {inventariado_flag}\n\n"
        "🎨  **CARACTERÍSTICAS FÍSICAS:**\n"
        f"    • Color: {animal.get('color') or 'No especificado'}\n"
        f"    • Hierro: {animal.get('hierro') or 'No especificado'}\n"
        f"    • N° Hierros: {animal.get('numero_hierros') or '0'}\n"
        f"    • Composición Racial: {animal.get('composicion_racial') or 'No especificada'}\n\n"
        "🛒  **INFORMACIÓN COMPRA:**\n"
        f"    • Vendedor: {animal.get('vendedor') or 'No aplica'}\n"
        f"    • Precio: ${animal.get('precio_compra') or '0'}\n\n"
        "💬  **COMENTARIOS:**\n"
        f"{animal.get('comentarios') or 'Sin comentarios'}\n\n"
        f"📁  **FOTO:** {animal.get('foto_path') or 'No disponible'}"
    )
