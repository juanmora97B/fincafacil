"""
╔══════════════════════════════════════════════════════════════════════════╗
║              EXPORTADORES DE REPORTES - FASE CONSOLIDACIÓN               ║
╚══════════════════════════════════════════════════════════════════════════╝

Exporta datos de análisis a formatos estándar (CSV, Excel, PDF).

Exportadores disponibles:
- Resumen mensual → CSV/Excel
- KPIs con tendencias → CSV/Excel  
- Alertas activas → CSV/Excel
- Reporte ejecutivo → PDF (básico)
"""

from __future__ import annotations
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging
import csv
import os
from pathlib import Path

logger = logging.getLogger("report_exporters")


class ReportExportersService:
    """Servicio para exportar reportes a diferentes formatos"""
    
    def __init__(self):
        self.logger = logger
        self.exports_dir = Path("exports")
        self.exports_dir.mkdir(exist_ok=True)
    
    def exportar_resumen_mensual_csv(
        self,
        año: int,
        mes: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta el resumen mensual a CSV.
        
        Args:
            año: Año del resumen
            mes: Mes del resumen (1-12)
            output_path: Ruta de salida personalizada
        
        Returns:
            Ruta del archivo generado
        """
        from database.database import get_db_connection
        
        if output_path is None:
            output_path = str(self.exports_dir / f"resumen_mensual_{año}_{mes:02d}.csv")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM resumen_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            row = cursor.fetchone()
            
            if not row:
                raise ValueError(f"No existe resumen para {año}-{mes:02d}")
            
            # Obtener nombres de columnas
            columnas = [desc[0] for desc in cursor.description]
            
            # Escribir CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Encabezados
                writer.writerow(columnas)
                
                # Datos
                writer.writerow(row)
        
        self.logger.info(f"Resumen mensual exportado a: {output_path}")
        return str(output_path)
    
    def exportar_kpis_csv(
        self,
        nombre_kpi: Optional[str] = None,
        meses_atras: int = 6,
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta KPIs con tendencias a CSV.
        
        Args:
            nombre_kpi: Filtrar por KPI específico (None = todos)
            meses_atras: Número de meses hacia atrás
            output_path: Ruta de salida personalizada
        
        Returns:
            Ruta del archivo generado
        """
        from database.database import get_db_connection
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.exports_dir / f"kpis_{timestamp}.csv")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    año, mes, nombre_kpi, valor, categoria, fecha_calculo
                FROM kpi_tracking
                WHERE 1=1
            """
            
            params = []
            if nombre_kpi:
                query += " AND nombre_kpi = ?"
                params.append(nombre_kpi)
            
            query += " ORDER BY año DESC, mes DESC, nombre_kpi LIMIT ?"
            params.append(meses_atras * 50)  # Aproximado
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if not rows:
                raise ValueError("No hay KPIs para exportar")
            
            # Escribir CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Encabezados
                writer.writerow(['Año', 'Mes', 'Período', 'Nombre KPI', 'Valor', 'Categoría', 'Fecha Cálculo'])
                
                # Datos
                for row in rows:
                    periodo = f"{row[0]}-{row[1]:02d}"
                    writer.writerow([row[0], row[1], periodo, row[2], row[3], row[4], row[5]])
        
        self.logger.info(f"KPIs exportados a: {output_path}")
        return str(output_path)
    
    def exportar_alertas_csv(
        self,
        prioridad: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta alertas activas a CSV.
        
        Args:
            prioridad: Filtrar por prioridad (alta, media, baja)
            output_path: Ruta de salida personalizada
        
        Returns:
            Ruta del archivo generado
        """
        from database.database import get_db_connection
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.exports_dir / f"alertas_{timestamp}.csv")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, tipo, prioridad, titulo, descripcion,
                    entidad_tipo, valor_actual, valor_referencia,
                    fecha_deteccion, estado
                FROM alertas
                WHERE estado = 'activa'
            """
            
            params = []
            if prioridad:
                query += " AND prioridad = ?"
                params.append(prioridad)
            
            query += " ORDER BY prioridad DESC, fecha_deteccion DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Escribir CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Encabezados
                writer.writerow([
                    'ID', 'Tipo', 'Prioridad', 'Título', 'Descripción',
                    'Entidad', 'Valor Actual', 'Valor Referencia',
                    'Fecha Detección', 'Estado'
                ])
                
                # Datos
                for row in rows:
                    writer.writerow(row)
        
        self.logger.info(f"Alertas exportadas a: {output_path}")
        return str(output_path)
    
    def exportar_resumen_ejecutivo_txt(
        self,
        año: int,
        mes: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta un resumen ejecutivo en formato texto para BI/Analytics.
        
        Args:
            año: Año del resumen
            mes: Mes del resumen
            output_path: Ruta de salida personalizada
        
        Returns:
            Ruta del archivo generado
        """
        from database.database import get_db_connection
        
        if output_path is None:
            output_path = str(self.exports_dir / f"resumen_ejecutivo_{año}_{mes:02d}.txt")
        
        # Obtener datos
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Resumen mensual
            cursor.execute("""
                SELECT * FROM resumen_mensual
                WHERE año = ? AND mes = ?
            """, (año, mes))
            
            resumen = cursor.fetchone()
            if not resumen:
                raise ValueError(f"No existe resumen para {año}-{mes:02d}")
            
            # KPIs del mes
            cursor.execute("""
                SELECT nombre_kpi, valor, categoria
                FROM kpi_tracking
                WHERE año = ? AND mes = ?
                ORDER BY categoria, nombre_kpi
            """, (año, mes))
            
            kpis = cursor.fetchall()
            
            # Alertas activas
            cursor.execute("""
                SELECT COUNT(*), prioridad
                FROM alertas
                WHERE estado = 'activa'
                AND fecha_deteccion >= date(?, '-30 days')
                GROUP BY prioridad
            """, (f"{año}-{mes:02d}-01",))
            
            alertas = dict(cursor.fetchall())
        
        # Generar reporte
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("═" * 80 + "\n")
            f.write(f"RESUMEN EJECUTIVO - {año}-{mes:02d}\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("═" * 80 + "\n\n")
            
            # Sección Financiera
            f.write("💰 RESUMEN FINANCIERO\n")
            f.write("─" * 80 + "\n")
            f.write(f"Ingresos Totales:     ${resumen[14]:>15,.0f}\n")
            f.write(f"  • Venta Animales:   ${resumen[15]:>15,.0f}\n")
            f.write(f"  • Venta Leche:      ${resumen[16]:>15,.0f}\n")
            f.write(f"Costos Totales:       ${resumen[17]:>15,.0f}\n")
            f.write(f"  • Nómina:           ${resumen[18]:>15,.0f}\n")
            f.write(f"  • Tratamientos:     ${resumen[19]:>15,.0f}\n")
            f.write(f"  • Insumos:          ${resumen[20]:>15,.0f}\n")
            f.write(f"Margen Bruto:         ${resumen[21]:>15,.0f}\n")
            f.write(f"Margen %:             {resumen[22]:>15.1f}%\n\n")
            
            # Sección Producción
            f.write("🥛 PRODUCCIÓN LECHERA\n")
            f.write("─" * 80 + "\n")
            f.write(f"Litros Totales:       {resumen[7]:>15,.0f} L\n")
            f.write(f"Promedio Diario:      {resumen[8]:>15,.1f} L/día\n")
            f.write(f"Promedio por Vaca:    {resumen[9]:>15,.1f} L/vaca\n")
            f.write(f"Vacas Productivas:    {resumen[10]:>15.0f}\n\n")
            
            # Sección Animales
            f.write("🐄 GESTIÓN ANIMAL\n")
            f.write("─" * 80 + "\n")
            f.write(f"Total Activos:        {resumen[3]:>15.0f}\n")
            f.write(f"Gestantes:            {resumen[4]:>15.0f}\n")
            f.write(f"Altas en el Mes:      {resumen[5]:>15.0f}\n")
            f.write(f"Bajas en el Mes:      {resumen[6]:>15.0f}\n\n")
            
            # Sección Reproducción
            f.write("🔬 REPRODUCCIÓN\n")
            f.write("─" * 80 + "\n")
            f.write(f"Servicios Realizados: {resumen[11]:>15.0f}\n")
            f.write(f"Partos en el Mes:     {resumen[12]:>15.0f}\n")
            f.write(f"Tasa de Preñez:       {resumen[13]:>15.1f}%\n\n")
            
            # KPIs
            if kpis:
                f.write("📊 KEY PERFORMANCE INDICATORS (KPIs)\n")
                f.write("─" * 80 + "\n")
                categoria_actual = None
                for kpi_nombre, kpi_valor, kpi_cat in kpis:
                    if kpi_cat != categoria_actual:
                        if categoria_actual:
                            f.write("\n")
                        f.write(f"[{kpi_cat.upper()}]\n")
                        categoria_actual = kpi_cat
                    f.write(f"  • {kpi_nombre:<40} {kpi_valor:>15,.2f}\n")
                f.write("\n")
            
            # Alertas
            if alertas:
                f.write("⚠️ ALERTAS ACTIVAS\n")
                f.write("─" * 80 + "\n")
                for prioridad in ['alta', 'media', 'baja']:
                    if prioridad in alertas:
                        f.write(f"  • {prioridad.upper()}: {alertas[prioridad]} alerta(s)\n")
                f.write("\n")
            
            f.write("═" * 80 + "\n")
            f.write("Fin del Resumen Ejecutivo\n")
            f.write("═" * 80 + "\n")
        
        self.logger.info(f"Resumen ejecutivo exportado a: {output_path}")
        return str(output_path)
    
    def exportar_todos_formatos(
        self,
        año: int,
        mes: int
    ) -> Dict[str, str]:
        """
        Exporta todos los reportes disponibles para un período.
        
        Args:
            año: Año del período
            mes: Mes del período
        
        Returns:
            Diccionario con rutas de archivos generados
        """
        archivos = {}
        
        try:
            archivos['resumen_csv'] = self.exportar_resumen_mensual_csv(año, mes)
        except Exception as e:
            self.logger.error(f"Error exportando resumen CSV: {e}")
        
        try:
            archivos['kpis_csv'] = self.exportar_kpis_csv()
        except Exception as e:
            self.logger.error(f"Error exportando KPIs CSV: {e}")
        
        try:
            archivos['alertas_csv'] = self.exportar_alertas_csv()
        except Exception as e:
            self.logger.error(f"Error exportando alertas CSV: {e}")
        
        try:
            archivos['resumen_ejecutivo'] = self.exportar_resumen_ejecutivo_txt(año, mes)
        except Exception as e:
            self.logger.error(f"Error exportando resumen ejecutivo: {e}")
        
        self.logger.info(f"Exportación completa: {len(archivos)} archivo(s) generado(s)")
        return archivos


# Singleton
_report_exporters_instance: Optional[ReportExportersService] = None


def get_report_exporters() -> ReportExportersService:
    """Obtiene la instancia singleton del servicio de exportadores"""
    global _report_exporters_instance
    if _report_exporters_instance is None:
        _report_exporters_instance = ReportExportersService()
    return _report_exporters_instance
