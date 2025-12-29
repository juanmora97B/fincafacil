"""
Utilidades para búsquedas case-insensitive en la base de datos
"""
import sqlite3
from typing import Optional, Dict, List, Tuple


def normalizar_texto(texto: str) -> str:
    """
    Normaliza un texto para comparaciones case-insensitive
    Elimina tildes, diéresis y caracteres especiales
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto en minúsculas, sin tildes y sin espacios en los extremos
    """
    if texto is None:
        return ""
    
    # Convertir a minúsculas y quitar espacios
    texto = str(texto).strip().lower()
    
    # Reemplazar caracteres con tildes/diéresis
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ã': 'a', 'õ': 'o', 'ñ': 'n', 'ç': 'c'
    }
    
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    
    return texto


def buscar_id_por_nombre(cursor: sqlite3.Cursor, tabla: str, nombre: str, 
                         columna_nombre: str = "nombre", 
                         condicion_extra: str | None = None) -> Optional[int]:
    """
    Busca el ID de un registro por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        tabla: Nombre de la tabla
        nombre: Nombre a buscar
        columna_nombre: Nombre de la columna donde buscar (default: "nombre")
        condicion_extra: Condición SQL adicional (ej: "AND estado = 'Activo'")
        
    Returns:
        ID del registro o None si no se encuentra
    """
    if not nombre:
        return None
    
    nombre_normalizado = normalizar_texto(nombre)
    
    # Construir query con LOWER para comparación case-insensitive
    query = f"SELECT id FROM {tabla} WHERE LOWER(TRIM({columna_nombre})) = ?"
    params = [nombre_normalizado]
    
    if condicion_extra:
        query += f" {condicion_extra}"
    
    query += " LIMIT 1"
    
    try:
        cursor.execute(query, params)
        row = cursor.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Error buscando en {tabla}: {e}")
        return None


def obtener_diccionario_normalizado(cursor: sqlite3.Cursor, tabla: str,
                                   columna_nombre: str = "nombre",
                                   condicion: str | None = None) -> Dict[str, int]:
    """
    Obtiene un diccionario {nombre_normalizado: id} de una tabla
    
    Args:
        cursor: Cursor de la base de datos
        tabla: Nombre de la tabla
        columna_nombre: Nombre de la columna (default: "nombre")
        condicion: Condición SQL WHERE (ej: "estado = 'Activo'")
        
    Returns:
        Diccionario con nombres normalizados como claves e IDs como valores
    """
    query = f"SELECT id, {columna_nombre} FROM {tabla}"
    
    if condicion:
        query += f" WHERE {condicion}"
    
    try:
        cursor.execute(query)
        return {
            normalizar_texto(row[1]): row[0] 
            for row in cursor.fetchall() 
            if row[1] is not None
        }
    except Exception as e:
        print(f"Error obteniendo diccionario de {tabla}: {e}")
        return {}


def buscar_finca_id(cursor: sqlite3.Cursor, nombre_finca: str) -> Optional[int]:
    """
    Busca el ID de una finca por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_finca: Nombre de la finca
        
    Returns:
        ID de la finca o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor, 
        "finca", 
        nombre_finca,
        condicion_extra="AND (estado = 'Activa' OR estado = 'Activo')"
    )


def buscar_raza_id(cursor: sqlite3.Cursor, nombre_raza: str) -> Optional[int]:
    """
    Busca el ID de una raza por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_raza: Nombre de la raza
        
    Returns:
        ID de la raza o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor,
        "raza",
        nombre_raza,
        condicion_extra="AND (estado = 'Activa' OR estado = 'Activo')"
    )


def buscar_potrero_id(cursor: sqlite3.Cursor, nombre_potrero: str, id_finca: int | None = None) -> Optional[int]:
    """
    Busca el ID de un potrero por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_potrero: Nombre del potrero
        id_finca: ID de la finca (opcional, para filtrar)
        
    Returns:
        ID del potrero o None si no se encuentra
    """
    condicion = "AND (estado = 'Activo' OR estado = 'Activa')"
    if id_finca:
        condicion += f" AND id_finca = {id_finca}"
    
    return buscar_id_por_nombre(
        cursor,
        "potrero",
        nombre_potrero,
        condicion_extra=condicion
    )


def buscar_lote_id(cursor: sqlite3.Cursor, nombre_lote: str) -> Optional[int]:
    """
    Busca el ID de un lote por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_lote: Nombre del lote
        
    Returns:
        ID del lote o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor,
        "lote",
        nombre_lote,
        condicion_extra="AND estado = 'Activo'"
    )


def buscar_sector_id(cursor: sqlite3.Cursor, nombre_sector: str) -> Optional[int]:
    """
    Busca el ID de un sector por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_sector: Nombre del sector
        
    Returns:
        ID del sector o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor,
        "sector",
        nombre_sector,
        condicion_extra="AND estado = 'Activo'"
    )


def buscar_vendedor_id(cursor: sqlite3.Cursor, nombre_vendedor: str) -> Optional[int]:
    """
    Busca el ID de un vendedor por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_vendedor: Nombre del vendedor
        
    Returns:
        ID del vendedor o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor,
        "vendedor",
        nombre_vendedor,
        condicion_extra="AND estado = 'Activo'"
    )


def buscar_insumo_id(cursor: sqlite3.Cursor, nombre_insumo: str) -> Optional[int]:
    """
    Busca el ID de un insumo por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_insumo: Nombre del insumo
        
    Returns:
        ID del insumo o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor,
        "insumo",
        nombre_insumo,
        condicion_extra="AND estado = 'Activo'"
    )


def buscar_herramienta_id(cursor: sqlite3.Cursor, nombre_herramienta: str) -> Optional[int]:
    """
    Busca el ID de una herramienta por nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        nombre_herramienta: Nombre de la herramienta
        
    Returns:
        ID de la herramienta o None si no se encuentra
    """
    return buscar_id_por_nombre(
        cursor,
        "herramienta",
        nombre_herramienta,
        condicion_extra="AND estado = 'Activo'"
    )


def verificar_existe_nombre(cursor: sqlite3.Cursor, tabla: str, nombre: str,
                           columna_nombre: str = "nombre",
                           excluir_id: int | None = None) -> bool:
    """
    Verifica si ya existe un registro con ese nombre (case-insensitive)
    
    Args:
        cursor: Cursor de la base de datos
        tabla: Nombre de la tabla
        nombre: Nombre a verificar
        columna_nombre: Nombre de la columna (default: "nombre")
        excluir_id: ID a excluir de la búsqueda (útil para actualizaciones)
        
    Returns:
        True si existe, False si no existe
    """
    if not nombre:
        return False
    
    nombre_normalizado = normalizar_texto(nombre)
    
    query = f"SELECT COUNT(*) FROM {tabla} WHERE LOWER(TRIM({columna_nombre})) = ?"
    params: list[str | int] = [nombre_normalizado]
    
    if excluir_id:
        query += " AND id != ?"
        params.append(excluir_id)
    
    try:
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error verificando existencia en {tabla}: {e}")
        return False


# Ejemplos de uso:
"""
# En importación Excel:
id_finca = buscar_finca_id(cursor, "FINCA EL PRADO")  # Encuentra "finca el prado"
id_raza = buscar_raza_id(cursor, "Holstein")  # Encuentra "holstein" o "HOLSTEIN"

# En formularios:
if verificar_existe_nombre(cursor, "finca", "Nueva Finca"):
    messagebox.showerror("Error", "Ya existe una finca con ese nombre")

# Obtener diccionario completo:
fincas_dict = obtener_diccionario_normalizado(
    cursor, 
    "finca", 
    condicion="estado = 'Activa' OR estado = 'Activo'"
)
"""
