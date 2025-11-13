"""
Utilidad genérica para parsear archivos Excel (.xlsx/.xls) y devolver filas como diccionarios.
Diseñada para ser usada por los módulos de configuración sin modificar la lógica de inserción.
"""
import openpyxl
from typing import List, Tuple, Dict, Any


def parse_excel_to_dicts(path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Lee el archivo Excel y retorna una lista de diccionarios por fila y una lista de errores.

    - Los keys de cada diccionario son los encabezados normalizados (minúsculas, sin espacios alrededor).
    - Si el archivo no se puede leer o no tiene encabezados, devuelve una lista de errores.
    """
    rows = []
    errors = []

    try:
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active

        if ws.max_row < 2:
            errors.append("El archivo no contiene filas de datos (solo encabezados o vacío).")
            return rows, errors

        # Leer encabezados (primera fila)
        headers = [str(cell.value).strip() if cell.value is not None else "" for cell in ws[1]]
        if not any(headers):
            errors.append("No se encontraron encabezados en la primera fila.")
            return rows, errors

        # Normalizar encabezados
        norm_headers = [h.strip().lower() for h in headers]

        # Procesar filas
        for r in range(2, ws.max_row + 1):
            # Construir diccionario para la fila
            row_dict = {}
            empty_row = True
            for c_idx, header in enumerate(norm_headers, start=1):
                cell = ws.cell(row=r, column=c_idx).value
                if cell is not None and str(cell).strip() != "":
                    empty_row = False
                row_dict[header] = cell

            if empty_row:
                continue
            rows.append(row_dict)

        return rows, errors

    except Exception as e:
        errors.append(f"Error al leer el archivo Excel: {e}")
        return [], errors
