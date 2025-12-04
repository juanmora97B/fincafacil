import openpyxl

# Abrir plantilla
wb = openpyxl.load_workbook('plantillas de carga/plantilla_animales.xlsx')
ws = wb.active

# Agregar una fila de prueba
ws.append([
    'TEST001',  # Código
    'Animal Prueba',  # Nombre
    'Compra',  # Tipo Ingreso
    'Macho',  # Sexo
    '2024-01-15',  # Fecha Nacimiento
    '2024-02-20',  # Fecha Compra
    'Finca Principal',  # Finca
    'Brahman',  # Raza
    'Potrero 1',  # Potrero
    'Lote A',  # Lote
    'Sector Norte',  # Sector
    'Novillos',  # Grupo
    150,  # Peso Nacimiento
    320,  # Peso Compra
    800000,  # Precio Compra
    'Juan Pérez',  # Vendedor
    'Valle',  # Procedencia
    'Sano',  # Salud
    'Activo',  # Estado
    'No',  # Inventariado
    'Rojo',  # Color
    'X123',  # Hierro
    '3',  # Condición Corporal
    'Animal de prueba'  # Comentario
])

# Guardar
wb.save('plantillas de carga/plantilla_animales_test.xlsx')
print('✓ Plantilla de prueba creada')

# Ahora probar importación
import sys
sys.path.insert(0, 'modules/utils')
from importador_excel import parse_excel_to_dicts, importar_animales_desde_excel

registros, errores = parse_excel_to_dicts('plantillas de carga/plantilla_animales_test.xlsx')
print(f'\n✓ Registros leídos: {len(registros)}')
print(f'  Errores de parseo: {errores}')

if registros:
    print(f'\n✓ Columnas normalizadas encontradas:')
    for col in sorted(registros[0].keys()):
        print(f'  - {col}')
    
    # Probar importación completa
    animales, errores_import = importar_animales_desde_excel('plantillas de carga/plantilla_animales_test.xlsx')
    print(f'\n✓ Animales procesados: {len(animales)}')
    print(f'  Errores de validación: {errores_import}')
    
    if animales:
        print(f'\n✓ Primer animal mapeado:')
        for k, v in sorted(animales[0].items()):
            if v is not None:
                print(f'  {k}: {v}')
