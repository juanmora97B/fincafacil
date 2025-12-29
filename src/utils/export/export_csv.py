"""
╔══════════════════════════════════════════════════════════════════════════╗
║                      EXPORTADOR CSV - FASE 3                             ║
╚══════════════════════════════════════════════════════════════════════════╝

Exporta reportes a formato CSV para respaldo y análisis externo.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging
from src.core.audit_service import log_event


class CSVExporter:
    """Exportador de reportes a formato CSV"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def exportar(self, reporte: Dict[str, Any], ruta_salida: str) -> str:
        """
        Exporta un reporte a CSV.
        
        Args:
            reporte: Diccionario con datos del reporte
            ruta_salida: Ruta del archivo CSV de salida
        
        Returns:
            Ruta del archivo generado
        
        Raises:
            Exception: Si hay error en la exportación
        """
        try:
            # Asegurar que la ruta existe
            Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
            
            tipo = reporte.get('tipo', 'desconocido')
            self.logger.info(f"Exportando reporte '{tipo}' a CSV: {ruta_salida}")
            
            # Delegar según tipo
            if tipo == 'animales':
                self._exportar_animales(reporte, ruta_salida)
            elif tipo == 'reproduccion':
                self._exportar_reproduccion(reporte, ruta_salida)
            elif tipo == 'produccion':
                self._exportar_produccion(reporte, ruta_salida)
            elif tipo == 'finanzas':
                self._exportar_finanzas(reporte, ruta_salida)
            elif tipo == 'completo':
                self._exportar_completo(reporte, ruta_salida)
            else:
                raise ValueError(f"Tipo de reporte no soportado: {tipo}")
            
            self.logger.info(f"✓ CSV exportado correctamente: {ruta_salida}")
            try:
                log_event(usuario=None, modulo="export", accion="EXPORTAR", entidad=tipo, resultado="OK", mensaje=f"CSV -> {ruta_salida}")
            except Exception:
                pass
            return ruta_salida
        
        except Exception as e:
            self.logger.error(f"Error exportando CSV: {e}", exc_info=True)
            try:
                tipo = reporte.get('tipo', 'desconocido')
                log_event(usuario=None, modulo="export", accion="EXPORTAR", entidad=tipo, resultado="ERROR", mensaje=str(e))
            except Exception:
                pass
            raise

    def exportar_analitico(self, datos: Dict[str, Any], destino: Path) -> Path:
        """Exporta datos analíticos (KPIs, tendencias, insights) a CSV."""
        destino.parent.mkdir(parents=True, exist_ok=True)
        with open(destino, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["ANALYTICS EXPORT", datetime.now().isoformat(sep=' ', timespec='seconds')])
            # KPIs financieros
            fk = datos.get('kpis_financieros') or {}
            if fk:
                w.writerow([]); w.writerow(["KPIs Financieros"])
                for k in [
                    ('Ingresos totales', fk.get('ingresos_totales')),
                    ('Ingresos animales', fk.get('ingresos_animales')),
                    ('Ingresos leche', fk.get('ingresos_leche')),
                    ('Costos totales', fk.get('costos_totales')),
                    ('Nómina', fk.get('costos_nomina')),
                    ('Insumos', fk.get('costos_insumos')),
                    ('Margen bruto', fk.get('margen_bruto')),
                    ('Rentabilidad mensual (%)', fk.get('rentabilidad_mensual')),
                ]:
                    w.writerow([k[0], k[1]])
            # KPIs productivos
            pk = datos.get('kpis_productivos') or {}
            if pk:
                w.writerow([]); w.writerow(["KPIs Productivos"])
                for k in [
                    ('Producción diaria (L)', pk.get('produccion_diaria')),
                    ('Producción mensual (L)', pk.get('produccion_mensual')),
                    ('Promedio por animal (L)', pk.get('produccion_promedio_por_animal')),
                    ('Tasa gestación (%)', pk.get('tasa_gestacion')),
                    ('Intervalo partos (días)', pk.get('intervalo_promedio_partos_dias')),
                    ('Mortalidad (n)', pk.get('mortalidad')),
                ]:
                    w.writerow([k[0], k[1]])
            # Tendencias
            tendencias = datos.get('tendencias') or []
            if tendencias:
                w.writerow([]); w.writerow(["Tendencias"])
                for serie in tendencias:
                    w.writerow([serie.get('nombre', 'serie')])
                    w.writerow(["Periodo", "Valor"])
                    for p in serie.get('puntos', []):
                        w.writerow([p.get('periodo'), p.get('valor')])
            # Insights
            insights = datos.get('insights') or []
            if insights:
                w.writerow([]); w.writerow(["Insights"])
                w.writerow(["Nivel", "Categoria", "Mensaje", "Recomendacion"])
                for ins in insights:
                    w.writerow([ins.get('nivel'), ins.get('categoria'), ins.get('mensaje'), ins.get('recomendacion')])
        try:
            log_event(usuario=None, modulo="analytics", accion="EXPORT_ANALYTICS", entidad=destino.name, resultado="OK")
        except Exception:
            pass
        return destino
    
    def _exportar_animales(self, reporte: Dict[str, Any], ruta: str):
        """Exporta reporte de animales"""
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezado
            writer.writerow(['REPORTE DE ANIMALES'])
            writer.writerow([f"Generado: {reporte['generado_en']}"])
            writer.writerow([f"Período: {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}"])
            writer.writerow([])
            
            # Inventario actual
            writer.writerow(['INVENTARIO ACTUAL'])
            writer.writerow(['Estado', 'Cantidad', 'Machos', 'Hembras'])
            
            inventario = reporte['datos']['inventario_actual']
            for estado, info in inventario['por_estado'].items():
                writer.writerow([
                    estado,
                    info['cantidad'],
                    info['machos'],
                    info['hembras']
                ])
            
            writer.writerow([])
            writer.writerow([f"Gestantes actuales: {inventario['gestantes']}"])
            writer.writerow([])
            
            # Distribución por raza
            writer.writerow(['DISTRIBUCIÓN POR RAZA'])
            writer.writerow(['Raza', 'Cantidad'])
            for item in inventario['por_raza']:
                writer.writerow([item['raza'], item['cantidad']])
    
    def _exportar_reproduccion(self, reporte: Dict[str, Any], ruta: str):
        """Exporta reporte de reproducción"""
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezado
            writer.writerow(['REPORTE DE REPRODUCCIÓN'])
            writer.writerow([f"Generado: {reporte['generado_en']}"])
            writer.writerow([f"Período: {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}"])
            writer.writerow([])
            
            datos = reporte['datos']
            
            # Servicios
            writer.writerow(['SERVICIOS REALIZADOS'])
            writer.writerow([f"Total: {datos['servicios']['total']}"])
            writer.writerow(['Tipo', 'Cantidad'])
            for item in datos['servicios']['por_tipo']:
                writer.writerow([item['tipo'], item['cantidad']])
            
            writer.writerow([])
            
            # Gestantes actuales
            writer.writerow(['GESTANTES ACTUALES'])
            writer.writerow([f"Total: {datos['gestantes_actuales']['total']}"])
            writer.writerow(['Código', 'Hembra', 'Fecha Servicio', 'Fecha Est. Parto', 'Días Restantes'])
            for item in datos['gestantes_actuales']['listado']:
                writer.writerow([
                    item['codigo'],
                    item['hembra'],
                    item['fecha_servicio'],
                    item['fecha_estimada_parto'],
                    item['dias_restantes']
                ])
            
            writer.writerow([])
            
            # Indicadores
            writer.writerow(['INDICADORES REPRODUCTIVOS'])
            ind = datos['indicadores']
            writer.writerow(['Métrica', 'Valor'])
            writer.writerow(['Hembras aptas', ind['hembras_aptas']])
            writer.writerow(['Gestantes', ind['gestantes']])
            writer.writerow(['Tasa de preñez (%)', ind['tasa_prenez_pct']])
    
    def _exportar_produccion(self, reporte: Dict[str, Any], ruta: str):
        """Exporta reporte de producción"""
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezado
            writer.writerow(['REPORTE DE PRODUCCIÓN'])
            writer.writerow([f"Generado: {reporte['generado_en']}"])
            writer.writerow([f"Período: {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}"])
            writer.writerow([])
            
            datos = reporte['datos']
            
            # Resumen
            writer.writerow(['RESUMEN DE PRODUCCIÓN'])
            prod = datos['produccion_periodo']
            writer.writerow(['Litros totales', prod['litros_totales']])
            writer.writerow(['Días de producción', prod['dias_produccion']])
            writer.writerow(['Vacas productivas', prod['vacas_productivas']])
            writer.writerow(['Jornada mañana (L)', prod['por_jornada']['mañana']])
            writer.writerow(['Jornada tarde (L)', prod['por_jornada']['tarde']])
            
            writer.writerow([])
            
            # Promedios
            writer.writerow(['PROMEDIOS'])
            prom = datos['promedios']
            writer.writerow(['Promedio litros/día', prom['promedio_litros_dia']])
            writer.writerow(['Promedio litros/vaca', prom['promedio_litros_vaca']])
            
            writer.writerow([])
            
            # Por animal
            writer.writerow(['PRODUCCIÓN POR ANIMAL (TOP 20)'])
            writer.writerow(['Código', 'Nombre', 'Litros Totales', 'Días', 'Promedio Diario'])
            for item in datos['por_animal']:
                writer.writerow([
                    item['codigo'],
                    item['nombre'],
                    item['litros_totales'],
                    item['dias_registrados'],
                    item['promedio_diario']
                ])
    
    def _exportar_finanzas(self, reporte: Dict[str, Any], ruta: str):
        """Exporta reporte financiero"""
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezado
            writer.writerow(['REPORTE FINANCIERO'])
            writer.writerow([f"Generado: {reporte['generado_en']}"])
            writer.writerow([f"Período: {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}"])
            writer.writerow([])
            
            datos = reporte['datos']
            
            # Ingresos
            writer.writerow(['INGRESOS'])
            writer.writerow(['Concepto', 'Valor (COP)'])
            writer.writerow(['Ventas de animales', f"${datos['ingresos']['ventas_animales']:,.0f}"])
            writer.writerow(['Ventas de leche', f"${datos['ingresos']['ventas_leche']:,.0f}"])
            writer.writerow(['TOTAL INGRESOS', f"${datos['ingresos']['total']:,.0f}"])
            
            writer.writerow([])
            
            # Costos
            writer.writerow(['COSTOS'])
            writer.writerow(['Concepto', 'Valor (COP)'])
            writer.writerow(['Nómina', f"${datos['costos']['nomina']:,.0f}"])
            writer.writerow(['Tratamientos', f"${datos['costos']['tratamientos']:,.0f}"])
            writer.writerow(['Insumos', f"${datos['costos']['insumos']:,.0f}"])
            writer.writerow(['TOTAL COSTOS', f"${datos['costos']['total']:,.0f}"])
            
            writer.writerow([])
            
            # Margen
            writer.writerow(['MARGEN BRUTO'])
            writer.writerow(['Valor (COP)', f"${datos['margen']['valor']:,.0f}"])
            writer.writerow(['Porcentaje', f"{datos['margen']['porcentaje']:.1f}%"])
            
            writer.writerow([])
            
            # Precios
            writer.writerow(['PRECIOS PROMEDIO'])
            writer.writerow(['Concepto', 'Valor'])
            if datos['precios']['precio_promedio_animal']:
                writer.writerow(['Animal', f"${datos['precios']['precio_promedio_animal']:,.0f}"])
            if datos['precios']['precio_promedio_leche']:
                writer.writerow(['Leche (por litro)', f"${datos['precios']['precio_promedio_leche']:,.0f}"])
            if datos['precios']['costo_por_litro']:
                writer.writerow(['Costo por litro', f"${datos['precios']['costo_por_litro']:,.0f}"])
    
    def _exportar_completo(self, reporte: Dict[str, Any], ruta: str):
        """Exporta reporte completo (genera múltiples CSVs)"""
        # Para reporte completo, generamos un CSV por sección
        base_path = Path(ruta).stem
        directorio = Path(ruta).parent
        
        secciones = reporte.get('secciones', {})
        
        for nombre_seccion, datos_seccion in secciones.items():
            ruta_seccion = directorio / f"{base_path}_{nombre_seccion}.csv"
            
            # Crear mini-reporte para cada sección
            mini_reporte = {
                'tipo': nombre_seccion,
                'periodo': reporte['periodo'],
                'generado_en': reporte['generado_en'],
                'datos': datos_seccion.get('datos', {}),
                'totales': datos_seccion.get('totales', {})
            }
            
            # Exportar recursivamente
            self.exportar(mini_reporte, str(ruta_seccion))


# Singleton
csv_exporter = CSVExporter()
