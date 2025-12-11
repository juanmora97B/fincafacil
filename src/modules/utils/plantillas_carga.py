"""Utilidad para generar plantillas Excel (.xlsx) para los módulos de configuración.

Se generan en memoria usando openpyxl y se guardan en la ruta elegida por el usuario.
"""
from __future__ import annotations
from typing import Dict, List, Tuple
from openpyxl import Workbook
import os

# Definición de columnas por módulo (clave -> lista de encabezados)
# Aseguradas según los importadores existentes en el proyecto
TEMPLATE_SPECS: Dict[str, List[str]] = {
    # ===================== CONFIGURACIÓN BÁSICA =====================
    "animales": [
        "codigo", "nombre", "tipo_ingreso", "sexo", "fecha_nacimiento", "fecha_compra",
        "finca", "raza", "potrero", "peso_nacimiento", "peso_compra", "precio_compra",
        "salud", "estado", "inventariado", "color", "hierro", "condicion_corporal", "comentario"
    ],
    "animales_masiva": [
        "codigo", "nombre", "tipo_ingreso", "sexo", "fecha_nacimiento", "fecha_compra",
        "finca", "raza", "madre_codigo", "padre_codigo", "potrero", "lote", "grupo",
        "peso_nacimiento", "peso_compra", "precio_compra", "procedencia", "vendedor",
        "color", "hierro", "condicion_corporal", "calidad", "salud", "estado",
        "inventariado", "comentarios"
    ],
    "finca": [
        "codigo", "nombre", "propietario", "ubicacion", "area_hectareas", "telefono", "email", "descripcion", "comentario"
    ],
    "sector": ["codigo", "nombre", "finca", "descripcion", "comentario"],
    # Se añade 'finca' para permitir asociar el lote a una finca al importar.
    "lote": ["codigo", "nombre", "finca", "descripcion", "criterio", "comentario"],
    # Condición corporal: actualizado para alinearse con el importador actual.
    # Formato nuevo esperado por la UI/configuración:
    # codigo, descripcion, puntuacion, escala, especie, caracteristicas, recomendaciones, estado
    # Se mantiene compatibilidad en el importador para archivos antiguos con:
    # condicion_corporal, rango_inferior, rango_superior, descripcion, recomendacion, comentario
    "condicion_corporal": [
        "codigo", "descripcion", "puntuacion", "escala", "especie", "caracteristicas", "recomendaciones", "estado"
    ],
    "razas": ["codigo", "nombre", "tipo_ganado", "especie", "descripcion", "comentario"],
    "potreros": [
        "codigo", "finca", "nombre", "sector", "area_hectareas", "capacidad_maxima", "tipo_pasto", "descripcion", "estado", "comentario"
    ],
    "empleados": [
        "codigo", "numero_identificacion", "nombres", "apellidos", "cargo", "estado_actual",
        "fecha_ingreso", "fecha_contrato", "fecha_nacimiento", "fecha_retiro",
        "sexo", "estado_civil", "telefono", "direccion",
        "salario_diario", "bono_alimenticio", "bono_productividad",
        "seguro_social", "otras_deducciones", "comentarios"
    ],
    "proveedores": [
        "codigo", "nombre", "nit", "telefono", "email", "direccion", "ciudad", "contacto", "comentario"
    ],
    "procedencia": [
        "codigo", "nombre", "tipo", "ubicacion", "contacto", "telefono", "descripcion", "comentario"
    ],
    "motivos_venta": ["codigo", "descripcion", "comentario"],
    "destino_venta": [
        "codigo", "nombre", "tipo", "nit", "direccion", "telefono", "email", "comentario"
    ],
    "diagnosticos": [
        "codigo", "nombre", "categoria", "descripcion", "tratamiento_sugerido", "comentario"
    ],
    "causa_muerte": ["codigo", "descripcion", "tipo_causa", "comentario"],
    "calidad_animal": ["codigo", "descripcion", "comentario"],
    "tipo_explotacion": ["codigo", "descripcion", "categoria", "comentario"],
    # ===================== OPERACIONES / EVENTOS =====================
    "tratamientos": [
        "animal_codigo", "fecha", "tipo_tratamiento", "producto", "dosis", "veterinario", "comentario", "fecha_proxima"
    ],
    "servicios": [
        "animal_codigo_hembra", "fecha_cubricion", "tipo_cubricion", "toro_semen", "observaciones"
    ],
    "ventas": [
        "animal_codigo", "fecha_venta", "precio_total", "motivo_venta", "destino_venta", "observaciones"
    ],
    "diagnosticos_eventos": [
        "animal_codigo", "fecha", "tipo", "diagnostico_detalle", "severidad", "estado", "observaciones"
    ],
    "produccion_leche": [
        "animal_codigo", "fecha", "cantidad_litros", "numero_ordeno", "calidad", "observaciones"
    ],
    "pesajes": [
        "animal_codigo", "fecha_pesaje", "peso_kg", "condicion_corporal", "observaciones"
    ],
    # ===================== INSUMOS =====================
    "insumos": [
        "codigo", "nombre", "categoria", "descripcion", "unidad_medida", "stock_actual",
        "stock_minimo", "stock_maximo", "precio_unitario", "finca", "ubicacion",
        "proveedor_principal", "fecha_vencimiento", "lote_proveedor", "estado", "responsable"
    ],
}

# Nombres amigables -> claves (orden lógico para el combo)
FRIENDLY_NAMES: List[Tuple[str, str]] = [
    ("Animales (básico)", "animales"),
    ("Animales (masiva)", "animales_masiva"),
    ("Fincas", "finca"),
    ("Sectores", "sector"),
    ("Lotes", "lote"),
    ("Condición corporal", "condicion_corporal"),
    ("Razas", "razas"),
    ("Potreros", "potreros"),
    ("Empleados", "empleados"),
    ("Proveedores", "proveedores"),
    ("Procedencia", "procedencia"),
    ("Motivos de venta", "motivos_venta"),
    ("Destino de venta", "destino_venta"),
    ("Diagnósticos", "diagnosticos"),
    ("Causas de muerte", "causa_muerte"),
    ("Calidad animal", "calidad_animal"),
    ("Tipo de explotación", "tipo_explotacion"),
    ("Tratamientos", "tratamientos"),
    ("Servicios reproducción", "servicios"),
    ("Ventas", "ventas"),
    ("Eventos diagnóstico", "diagnosticos_eventos"),
    ("Producción leche", "produccion_leche"),
    ("Pesajes", "pesajes"),
    ("Insumos", "insumos"),
]


def get_template_names() -> List[str]:
    """Devuelve la lista de nombres amigables para el selector de plantillas."""
    return [n for n, _ in FRIENDLY_NAMES]


def resolve_key_from_name(name: str) -> str:
    for friendly, key in FRIENDLY_NAMES:
        if friendly == name:
            return key
    # fallback a key directa si ya es clave
    return name


def create_workbook_for_module(module_key: str) -> Workbook:
    """Crea un Workbook con la hoja y los encabezados según el módulo."""
    headers = TEMPLATE_SPECS.get(module_key)
    if not headers:
        raise ValueError(f"No hay especificación de plantilla para el módulo: {module_key}")

    wb = Workbook()
    ws = wb.active
    ws.title = module_key

    # Escribir encabezados en primera fila
    for idx, h in enumerate(headers, start=1):
        ws.cell(row=1, column=idx, value=h)

    # Opcional: ejemplo mínimo (dejar vacío para evitar confusiones)
    return wb


def default_templates_dir() -> str:
    """Carpeta por defecto para almacenar plantillas en el proyecto."""
    # Nombre solicitado por el usuario con espacios (Windows lo soporta)
    return os.path.join(os.getcwd(), "plantillas de carga")


def ensure_templates_dir(path: str | None = None) -> str:
    path = path or default_templates_dir()
    os.makedirs(path, exist_ok=True)
    return path


def save_template_to_path(module_key: str, out_path: str) -> None:
    """Genera y guarda la plantilla del módulo en `out_path`."""
    wb = create_workbook_for_module(module_key)
    # Asegurar la carpeta destino
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    wb.save(out_path)


def suggested_filename(module_key: str) -> str:
    return f"plantilla_{module_key}.xlsx"
