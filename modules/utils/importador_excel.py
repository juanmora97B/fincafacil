"""
Módulo utilitario para importar datos desde archivos Excel
"""
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

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
                header = str(cell.value).strip().lower()
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