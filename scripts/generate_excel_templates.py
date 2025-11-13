"""
Script para generar plantillas Excel (.xlsx) en assets/templates.
Ejecutar desde la raíz del proyecto:

    python scripts\generate_excel_templates.py

Genera archivos como `assets/templates/fincas_template.xlsx` y otros.
"""
import os
from openpyxl import Workbook

TEMPLATES = {
    'fincas': ['codigo', 'nombre', 'propietario', 'ubicacion', 'area', 'telefono', 'email', 'descripcion'],
    'razas': ['codigo', 'nombre', 'tipo_ganado', 'descripcion'],
    'potreros': ['codigo', 'nombre', 'finca', 'area', 'descripcion'],
    'sectores': ['codigo', 'nombre', 'finca', 'descripcion'],
    'lotes': ['codigo', 'nombre', 'potrero', 'area', 'descripcion'],
    'diagnosticos': ['codigo', 'nombre', 'descripcion'],
    'condiciones_corporales': ['codigo', 'nombre', 'descripcion'],
    'tipo_explotacion': ['codigo', 'nombre', 'descripcion'],
    'procedencia': ['codigo', 'nombre', 'descripcion'],
    'destino_venta': ['codigo', 'nombre', 'descripcion'],
    'motivos_venta': ['codigo', 'nombre', 'descripcion'],
    'causa_muerte': ['codigo', 'nombre', 'descripcion'],
    'calidad_animal': ['codigo', 'nombre', 'descripcion'],
    'proveedores': ['codigo', 'nombre', 'telefono', 'email', 'direccion'],
    'empleados': ['codigo', 'nombre', 'identificacion', 'telefono', 'email', 'cargo'],
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'templates')


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def create_template(name, headers, path):
    wb = Workbook()
    ws = wb.active
    ws.title = name
    # Escribir encabezados
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col_idx, value=header)
    wb.save(path)


if __name__ == '__main__':
    ensure_dir(OUTPUT_DIR)
    created = []
    for name, headers in TEMPLATES.items():
        filename = f"{name}_template.xlsx"
        fullpath = os.path.join(OUTPUT_DIR, filename)
        create_template(name, headers, fullpath)
        created.append(fullpath)

    print("Plantillas generadas:")
    for p in created:
        print(' -', p)

    print('\nRevisa los archivos y úsalos como base para las importaciones en los submódulos.')
