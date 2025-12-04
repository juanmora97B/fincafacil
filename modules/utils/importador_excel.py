"""
Módulo utilitario para importar datos desde archivos Excel
NOTA: Usa helpers case-insensitive de database_helpers para búsquedas de fincas, razas, etc.
"""
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
import logging
import unicodedata
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Importar helpers para búsquedas case-insensitive
try:
    from modules.utils.database_helpers import (
        buscar_finca_id,
        buscar_raza_id,
        buscar_potrero_id,
        buscar_lote_id,
        buscar_sector_id,
        buscar_vendedor_id,
        normalizar_texto
    )
    HELPERS_DISPONIBLES = True
except ImportError:
    HELPERS_DISPONIBLES = False
    logger.warning("Helpers de database_helpers no disponibles, usando búsquedas básicas")

def normalizar_nombre_columna(nombre: str) -> str:
    """
    Normaliza el nombre de una columna de Excel para búsqueda flexible.
    Elimina tildes, espacios, paréntesis y convierte a minúsculas.
    
    Args:
        nombre: Nombre original de la columna
        
    Returns:
        str: Nombre normalizado
    """
    if not nombre:
        return ""
    
    # Convertir a string y minúsculas
    nombre = str(nombre).lower()
    
    # Eliminar tildes/acentos
    nombre = ''.join(c for c in unicodedata.normalize('NFD', nombre) 
                     if unicodedata.category(c) != 'Mn')
    
    # Eliminar caracteres especiales y reemplazar espacios con guión bajo
    nombre = nombre.replace(' ', '_').replace('(', '').replace(')', '').replace('.', '')
    nombre = nombre.replace('-', '_').replace('á', 'a').replace('é', 'e')
    nombre = nombre.replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    
    return nombre

def mapear_columnas_flexibles(registro: Dict, mapa_alternativas: Dict) -> Dict:
    """
    Mapea columnas de Excel usando nombres alternativos flexibles.
    
    Args:
        registro: Diccionario con los datos originales
        mapa_alternativas: Dict donde key es el nombre estándar y value es una lista de alternativas
        
    Returns:
        Dict: Registro con nombres de columnas estandarizados
    """
    registro_normalizado = {}
    
    # Crear un diccionario con claves normalizadas para búsqueda rápida
    registro_norm = {normalizar_nombre_columna(k): v for k, v in registro.items()}
    
    # Mapear cada campo estándar
    for campo_std, alternativas in mapa_alternativas.items():
        valor = None
        
        # Buscar en las alternativas
        for alt in alternativas:
            alt_norm = normalizar_nombre_columna(alt)
            if alt_norm in registro_norm:
                valor = registro_norm[alt_norm]
                break
        
        registro_normalizado[campo_std] = valor if valor not in (None, "") else None
    
    # Agregar campos que no están en el mapa (sin normalizar)
    for k, v in registro.items():
        k_std = k.lower().replace(' ', '_')
        if k_std not in registro_normalizado:
            registro_normalizado[k_std] = v
    
    return registro_normalizado

def parse_excel_to_dicts(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Parsea un archivo Excel y devuelve una lista de diccionarios.
    
    Args:
        file_path: Ruta al archivo Excel
        
    Returns:
        Tuple[List[Dict], List[str]]: (lista de registros, lista de errores)
    """
    registros = []
    errores = []
    
    try:
        # Cargar workbook
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook.active
        
        # Leer encabezados
        headers = []
        for cell in sheet[1]:
            if cell.value:
                header = normalizar_nombre_columna(str(cell.value).strip())
                headers.append(header)
            else:
                headers.append(f"columna_{cell.column}")
        
        # Validar que hay encabezados
        if not headers:
            errores.append("El archivo Excel no tiene encabezados válidos")
            return registros, errores
        
        # Procesar filas
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Saltar filas vacías
                if all(cell is None or str(cell).strip() == '' for cell in row):
                    continue
                
                registro = {}
                for idx, cell_value in enumerate(row):
                    if idx < len(headers):
                        header = headers[idx]
                        # Convertir valores None a string vacío
                        if cell_value is None:
                            registro[header] = ""
                        else:
                            registro[header] = str(cell_value).strip()
                
                if registro:  # Solo agregar si no está vacío
                    registros.append(registro)
                    
            except Exception as e:
                errores.append(f"Fila {row_num}: Error al procesar - {str(e)}")
                logger.warning(f"Error en fila {row_num}: {e}")
        
        logger.info(f"Archivo Excel procesado: {len(registros)} registros, {len(errores)} errores")
        
    except InvalidFileException:
        error_msg = "El archivo no es un Excel válido o está corrupto"
        errores.append(error_msg)
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"Error al procesar el archivo Excel: {str(e)}"
        errores.append(error_msg)
        logger.error(error_msg)
    
    return registros, errores

def validar_estructura_excel(registros: List[Dict], campos_requeridos: List[str]) -> List[str]:
    """
    Valida que los registros tengan los campos requeridos.
    
    Args:
        registros: Lista de diccionarios con los datos
        campos_requeridos: Lista de campos obligatorios
        
    Returns:
        List[str]: Lista de errores de validación
    """
    errores = []
    
    if not registros:
        errores.append("No hay registros para validar")
        return errores
    
    primera_fila = registros[0]
    
    for campo in campos_requeridos:
        if campo not in primera_fila:
            errores.append(f"Falta el campo requerido: '{campo}'")
    
    return errores

def mapear_campos(registro: Dict, mapeo: Dict[str, str]) -> Dict:
    """
    Mapea los campos del Excel a los nombres de la base de datos.
    
    Args:
        registro: Diccionario con datos del Excel
        mapeo: Diccionario de mapeo {campo_excel: campo_bd}
        
    Returns:
        Dict: Registro con campos mapeados
    """
    registro_mapeado = {}
    
    for campo_excel, campo_bd in mapeo.items():
        if campo_excel in registro:
            registro_mapeado[campo_bd] = registro[campo_excel]
        else:
            registro_mapeado[campo_bd] = None
    
    return registro_mapeado

def importar_animales_desde_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Función específica para importar animales desde Excel
    
    Args:
        file_path: Ruta al archivo Excel
        
    Returns:
        Tuple[List[Dict], List[str]]: (animales mapeados, lista de errores)
    """
    campos_requeridos = ['codigo', 'sexo']  # nombre y raza pueden ser opcionales en algunas compras
    
    # Parsear el Excel
    registros, errores = parse_excel_to_dicts(file_path)
    
    if errores:
        return [], errores
    
    # Validar estructura básica
    errores_validacion = validar_estructura_excel(registros, campos_requeridos)
    if errores_validacion:
        return [], errores_validacion
    
    # Mapeo de campos comunes de Excel a base de datos
    mapeo_campos = {
        # Identificación
        'arete': 'codigo', 'numero': 'codigo', 'identificacion': 'codigo', 'codigo': 'codigo',
        # Básicos
        'nombre_animal': 'nombre', 'nombre': 'nombre', 'raza': 'raza',
        # Tipo ingreso
        'tipo_ingreso': 'tipo_ingreso',
        # Sexo
        'sexo_animal': 'sexo', 'sexo': 'sexo',
        # Fechas
        'fecha_nac': 'fecha_nacimiento', 'fecha_nacimiento': 'fecha_nacimiento',
        'fecha_compra': 'fecha_compra',
        # Pesos
        'peso_nac': 'peso_nacimiento', 'peso_nacimiento': 'peso_nacimiento',
        'peso_compra': 'peso_compra', 'peso': 'peso_actual', 'peso_actual': 'peso_actual',
        # Compra específicos
        'precio_compra': 'precio_compra', 'procedencia': 'procedencia', 'vendedor': 'vendedor',
        # Ubicación
        'potrero': 'potrero', 'lote': 'lote', 'sector': 'sector', 'grupo': 'grupo', 'finca': 'finca',
        # Salud y características
        'salud': 'salud', 'color': 'color', 'hierro': 'hierro', 'numero_hierros': 'numero_hierros',
        'condicion_corporal': 'condicion_corporal',
        # Estado
        'estado': 'estado', 'inventariado': 'inventariado',
        # Observaciones
        'observaciones': 'observaciones', 'comentarios': 'observaciones', 'comentario': 'observaciones'
    }
    
    # Aplicar mapeo a todos los registros
    registros_mapeados = []
    for registro in registros:
        registro_mapeado = mapear_campos(registro, mapeo_campos)

        # Normalizar tipo_ingreso
        tipo_ingreso = (registro_mapeado.get('tipo_ingreso') or '').strip().capitalize()
        if tipo_ingreso not in ('Nacimiento', 'Compra'):
            # Inferir si trae campos de compra
            if registro_mapeado.get('fecha_compra') or registro_mapeado.get('precio_compra'):
                tipo_ingreso = 'Compra'
            else:
                tipo_ingreso = 'Nacimiento'
        registro_mapeado['tipo_ingreso'] = tipo_ingreso

        # Limpiar pesos (convertir a float si se puede)
        for campo_peso in ['peso_nacimiento', 'peso_compra', 'peso_actual']:
            val = registro_mapeado.get(campo_peso)
            if val is not None and str(val).strip() != '':
                try:
                    registro_mapeado[campo_peso] = float(str(val).replace(',', '.'))
                except ValueError:
                    registro_mapeado[campo_peso] = None
            else:
                registro_mapeado[campo_peso] = None

        # Precio compra
        precio = registro_mapeado.get('precio_compra')
        if precio is not None and str(precio).strip() != '':
            try:
                registro_mapeado['precio_compra'] = float(str(precio).replace(',', '.'))
            except ValueError:
                registro_mapeado['precio_compra'] = None
        else:
            registro_mapeado['precio_compra'] = None

        # Sexo normalizado
        sexo = (registro_mapeado.get('sexo') or '').strip().lower()
        if sexo.startswith('m'):
            registro_mapeado['sexo'] = 'Macho'
        elif sexo.startswith('h') or sexo.startswith('f'):
            registro_mapeado['sexo'] = 'Hembra'
        else:
            registro_mapeado['sexo'] = None

        registros_mapeados.append(registro_mapeado)

    return registros_mapeados, []

def importar_catalogo_generico(file_path: str, requerido: List[str]) -> Tuple[List[Dict], List[str]]:
    """Importa un catálogo genérico con columnas requeridas.
    Devuelve lista de registros y errores. Los encabezados se normalizan a minúsculas.
    """
    registros, errores = parse_excel_to_dicts(file_path)
    if errores:
        return [], errores
    # Validar requeridos
    errores_req = validar_estructura_excel(registros, requerido)
    if errores_req:
        return [], errores_req
    return registros, []

def importar_sector_desde_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """Importa sectores. Requerido: codigo, nombre. Opcional: finca (nombre de finca)."""
    registros, errores = importar_catalogo_generico(file_path, ['codigo', 'nombre'])
    if errores:
        return [], errores
    normalizados = []
    for r in registros:
        # Buscar finca_id si se proporciona nombre de finca (búsqueda case-insensitive)
        finca_id = None
        finca_nombre = r.get('finca', '').strip() if r.get('finca') else None
        if finca_nombre:
            from database.database import get_db_connection
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # Búsqueda case-insensitive usando LOWER()
                    cursor.execute("SELECT id FROM finca WHERE LOWER(nombre) = LOWER(?) AND estado = 'Activo' LIMIT 1", (finca_nombre,))
                    finca_row = cursor.fetchone()
                    if finca_row:
                        finca_id = finca_row[0]
            except Exception:
                pass  # Si falla, se deja finca_id como None
        
        normalizados.append({
            'codigo': r.get('codigo','').strip(),
            'nombre': r.get('nombre','').strip(),
            'finca_id': finca_id,
            'descripcion': r.get('descripcion') or None,
            'comentario': r.get('comentario') or None,
            'estado': r.get('estado') or 'Activo'
        })
    return normalizados, []

def importar_calidad_animal_desde_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """Importa calidad_animal. Requerido: codigo, descripcion."""
    registros, errores = importar_catalogo_generico(file_path, ['codigo', 'descripcion'])
    if errores:
        return [], errores
    return [{
        'codigo': r.get('codigo','').strip(),
        'descripcion': r.get('descripcion','').strip(),
        'comentario': r.get('comentario') or None,
        'estado': r.get('estado') or 'Activo'
    } for r in registros], []

def importar_tipo_explotacion_desde_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """Importa tipo_explotacion. Requerido: codigo, descripcion."""
    registros, errores = importar_catalogo_generico(file_path, ['codigo', 'descripcion'])
    if errores:
        return [], errores
    return [{
        'codigo': r.get('codigo','').strip(),
        'descripcion': r.get('descripcion','').strip(),
        'categoria': r.get('categoria') or None,
        'comentario': r.get('comentario') or None,
        'estado': r.get('estado') or 'Activo'
    } for r in registros], []

def importar_condicion_corporal_desde_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """Importa condicion_corporal soportando formato nuevo y antiguo.
    Formato nuevo esperado mínimo: codigo, descripcion (opcional: puntuacion, caracteristicas, recomendaciones)
    Formato antiguo (detectado si existe 'condicion_corporal' y/o rangos): condicion_corporal, rango_inferior, rango_superior, descripcion, recomendacion, comentario.
    Reglas:
      - condicion_corporal -> codigo
      - descripcion -> descripcion
      - Si faltan 'puntuacion' y existen rango_inferior/rango_superior numéricos, se genera 'puntuacion' como indice correlativo comenzando en 1.
      - recomendacion -> recomendaciones
      - comentario -> caracteristicas (se concatena " | Comentario: <texto>")
      - Valores vacíos normalizados a None.
    """
    registros_raw, errores_parse = parse_excel_to_dicts(file_path)
    if errores_parse:
        return [], errores_parse

    if not registros_raw:
        return [], ["El archivo no contiene registros válidos"]

    # Detectar formato antiguo por presencia de columnas claves
    encabezados_norm = {normalizar_nombre_columna(k) for k in registros_raw[0].keys()}
    formato_antiguo = 'condicion_corporal' in encabezados_norm or 'rango_inferior' in encabezados_norm

    registros = []
    errores = []

    if formato_antiguo:
        # Procesar formato antiguo
        puntuacion_auto = 1
        for raw in registros_raw:
            rn = {normalizar_nombre_columna(k): v for k,v in raw.items()}
            codigo = (rn.get('condicion_corporal') or rn.get('codigo') or '').strip()
            descripcion = (rn.get('descripcion') or '').strip()
            if not codigo or not descripcion:
                errores.append(f"Registro sin codigo/descripcion válido: {raw}")
                continue
            # Generar puntuacion correlativa si no existe
            puntuacion = rn.get('puntuacion') or rn.get('rango')
            if not puntuacion:
                puntuacion = str(puntuacion_auto)
                puntuacion_auto += 1
            recomendaciones = rn.get('recomendacion') or rn.get('recomendaciones') or None
            comentario = rn.get('comentario') or rn.get('caracteristicas') or None
            caracteristicas = comentario and f"{comentario}" or None
            registros.append({
                'codigo': codigo,
                'descripcion': descripcion,
                'puntuacion': puntuacion,
                'escala': rn.get('escala') or None,
                'especie': rn.get('especie') or None,
                'caracteristicas': caracteristicas,
                'recomendaciones': recomendaciones,
                'estado': (rn.get('estado') or 'Activo')
            })
    else:
        # Formato nuevo: validar requiridos flexibles codigo, descripcion
        for raw in registros_raw:
            codigo = (raw.get('codigo') or '').strip()
            descripcion = (raw.get('descripcion') or '').strip()
            if not codigo or not descripcion:
                errores.append(f"Registro sin codigo/descripcion: {raw}")
                continue
            registros.append({
                'codigo': codigo,
                'descripcion': descripcion,
                'puntuacion': (raw.get('puntuacion') or '').strip() or None,
                'escala': (raw.get('escala') or '').strip() or None,
                'especie': (raw.get('especie') or '').strip() or None,
                'caracteristicas': (raw.get('caracteristicas') or '').strip() or None,
                'recomendaciones': (raw.get('recomendaciones') or raw.get('recomendacion') or '').strip() or None,
                'estado': (raw.get('estado') or 'Activo')
            })

    return registros, errores

def importar_procedencia_desde_excel(file_path: str) -> Tuple[List[Dict], List[str]]:
    """Importa procedencia. Requerido: codigo, descripcion."""
    registros, errores = importar_catalogo_generico(file_path, ['codigo', 'descripcion'])
    if errores:
        return [], errores
    return [{
        'codigo': r.get('codigo','').strip(),
        'descripcion': r.get('descripcion','').strip(),
        'tipo_procedencia': r.get('tipo_procedencia') or None,
        'ubicacion': r.get('ubicacion') or None,
        'comentario': r.get('comentario') or None,
        'estado': r.get('estado') or 'Activo'
    } for r in registros], []