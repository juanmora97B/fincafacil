import sys
sys.path.insert(0, 'modules/utils')
from importador_excel import parse_excel_to_dicts

registros, errores = parse_excel_to_dicts('plantillas de carga/plantilla_animales.xlsx')
print(f'Registros leídos: {len(registros)}')
print(f'Errores: {errores}')
if registros:
    print(f'\nColumnas encontradas:')
    for col in sorted(registros[0].keys()):
        print(f'  - {col}')
    print(f'\nPrimera fila de datos:')
    for k, v in registros[0].items():
        if v:
            print(f'  {k}: {v}')
