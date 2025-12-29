"""
╔══════════════════════════════════════════════════════════════════════════╗
║                      EXPORTADOR PDF - FASE 3                             ║
╚══════════════════════════════════════════════════════════════════════════╝

Exporta reportes a formato PDF profesional.
Requiere: reportlab (pip install reportlab)
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging
from src.core.audit_service import log_event


class PDFExporter:
    """Exportador de reportes a formato PDF"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._verificar_dependencias()
    
    def _verificar_dependencias(self):
        """Verifica que reportlab esté instalado"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            
            self.reportlab_available = True
            self.letter = letter
            self.A4 = A4
            self.colors = colors
            self.inch = inch
            self.SimpleDocTemplate = SimpleDocTemplate
            self.Table = Table
            self.TableStyle = TableStyle
            self.Paragraph = Paragraph
            self.Spacer = Spacer
            self.getSampleStyleSheet = getSampleStyleSheet
            self.ParagraphStyle = ParagraphStyle
            self.TA_CENTER = TA_CENTER
            self.TA_RIGHT = TA_RIGHT
            self.TA_LEFT = TA_LEFT
            
        except ImportError:
            self.logger.warning(
                "reportlab no está instalado. "
                "Instalar con: pip install reportlab"
            )
            self.reportlab_available = False
    
    def exportar(self, reporte: Dict[str, Any], ruta_salida: str) -> str:
        """
        Exporta un reporte a PDF.
        
        Args:
            reporte: Diccionario con datos del reporte
            ruta_salida: Ruta del archivo PDF de salida
        
        Returns:
            Ruta del archivo generado
        
        Raises:
            Exception: Si hay error en la exportación o falta reportlab
        """
        if not self.reportlab_available:
            raise ImportError(
                "reportlab no está instalado. "
                "Instalar con: pip install reportlab"
            )
        
        try:
            # Asegurar que la ruta existe
            Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
            
            tipo = reporte.get('tipo', 'desconocido')
            self.logger.info(f"Exportando reporte '{tipo}' a PDF: {ruta_salida}")
            
            # Crear documento PDF
            doc = self.SimpleDocTemplate(
                ruta_salida,
                pagesize=self.letter,
                rightMargin=0.75*self.inch,
                leftMargin=0.75*self.inch,
                topMargin=0.75*self.inch,
                bottomMargin=0.75*self.inch
            )
            
            # Estilos
            styles = self.getSampleStyleSheet()
            title_style = self.ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=self.colors.HexColor('#1a237e'),
                spaceAfter=12,
                alignment=self.TA_CENTER
            )
            
            heading_style = self.ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors.HexColor('#283593'),
                spaceAfter=8,
                spaceBefore=12
            )
            
            # Construir contenido
            story = []
            
            # Delegar según tipo
            if tipo == 'animales':
                self._construir_pdf_animales(story, reporte, title_style, heading_style, styles)
            elif tipo == 'reproduccion':
                self._construir_pdf_reproduccion(story, reporte, title_style, heading_style, styles)
            elif tipo == 'produccion':
                self._construir_pdf_produccion(story, reporte, title_style, heading_style, styles)
            elif tipo == 'finanzas':
                self._construir_pdf_finanzas(story, reporte, title_style, heading_style, styles)
            elif tipo == 'completo':
                self._construir_pdf_completo(story, reporte, title_style, heading_style, styles)
            else:
                raise ValueError(f"Tipo de reporte no soportado: {tipo}")
            
            # Generar PDF
            doc.build(story)
            
            self.logger.info(f"✓ PDF exportado correctamente: {ruta_salida}")
            try:
                tipo = reporte.get('tipo', 'desconocido')
                log_event(usuario=None, modulo="export", accion="EXPORTAR", entidad=tipo, resultado="OK", mensaje=f"PDF -> {ruta_salida}")
            except Exception:
                pass
            return ruta_salida
        
        except Exception as e:
            self.logger.error(f"Error exportando PDF: {e}", exc_info=True)
            try:
                tipo = reporte.get('tipo', 'desconocido')
                log_event(usuario=None, modulo="export", accion="EXPORTAR", entidad=tipo, resultado="ERROR", mensaje=str(e))
            except Exception:
                pass
            raise

    def exportar_analitico(self, datos: Dict[str, Any], destino: Path) -> Path:
        if not self.reportlab_available:
            raise ImportError("reportlab no está instalado. Instalar con: pip install reportlab")
        destino.parent.mkdir(parents=True, exist_ok=True)
        doc = self.SimpleDocTemplate(str(destino), pagesize=self.A4)
        styles = self.getSampleStyleSheet()
        content: List = []
        content.append(self.Paragraph("Analytics Export", styles['Title']))
        content.append(self.Spacer(1, 12))
        # KPIs Financieros
        fk = datos.get('kpis_financieros') or {}
        if fk:
            content.append(self.Paragraph("KPIs Financieros", styles['Heading2']))
            table_data = [["KPI", "Valor"]]
            for label, key in [
                ("Ingresos totales", "ingresos_totales"),
                ("Ingresos animales", "ingresos_animales"),
                ("Ingresos leche", "ingresos_leche"),
                ("Costos totales", "costos_totales"),
                ("Nómina", "costos_nomina"),
                ("Insumos", "costos_insumos"),
                ("Margen bruto", "margen_bruto"),
                ("Rentabilidad mensual (%)", "rentabilidad_mensual"),
            ]:
                table_data.append([label, str(fk.get(key) or "-")])
            t = self.Table(table_data, hAlign='LEFT')
            t.setStyle(self.TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), self.colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, self.colors.lightgrey),
            ]))
            content.append(t)
            content.append(self.Spacer(1, 12))
        # KPIs Productivos
        pk = datos.get('kpis_productivos') or {}
        if pk:
            content.append(self.Paragraph("KPIs Productivos", styles['Heading2']))
            table_data = [["KPI", "Valor"]]
            for label, key in [
                ("Producción diaria (L)", "produccion_diaria"),
                ("Producción mensual (L)", "produccion_mensual"),
                ("Promedio por animal (L)", "produccion_promedio_por_animal"),
                ("Tasa gestación (%)", "tasa_gestacion"),
                ("Intervalo partos (días)", "intervalo_promedio_partos_dias"),
                ("Mortalidad (n)", "mortalidad"),
            ]:
                table_data.append([label, str(pk.get(key) or "-")])
            t = self.Table(table_data, hAlign='LEFT')
            t.setStyle(self.TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), self.colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, self.colors.lightgrey),
            ]))
            content.append(t)
            content.append(self.Spacer(1, 12))
        # Insights
        insights = datos.get('insights') or []
        if insights:
            content.append(self.Paragraph("Insights", styles['Heading2']))
            table_data = [["Nivel", "Categoria", "Mensaje", "Recomendacion"]]
            for ins in insights:
                table_data.append([
                    ins.get('nivel'), ins.get('categoria'), ins.get('mensaje'), ins.get('recomendacion')
                ])
            t = self.Table(table_data, hAlign='LEFT')
            t.setStyle(self.TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), self.colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, self.colors.lightgrey),
            ]))
            content.append(t)
        doc.build(content)
        try:
            log_event(usuario=None, modulo="analytics", accion="EXPORT_ANALYTICS", entidad=destino.name, resultado="OK")
        except Exception:
            pass
        return destino
    
    def _construir_pdf_animales(self, story: List, reporte: Dict, title_style, heading_style, styles):
        """Construye contenido PDF para reporte de animales"""
        # Título
        story.append(self.Paragraph("REPORTE DE ANIMALES", title_style))
        story.append(self.Paragraph("FincaFácil - Sistema de Gestión Ganadera", styles['Normal']))
        story.append(self.Spacer(1, 0.2*self.inch))
        
        # Info del reporte
        story.append(self.Paragraph(
            f"<b>Generado:</b> {reporte['generado_en']}<br/>"
            f"<b>Período:</b> {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}",
            styles['Normal']
        ))
        story.append(self.Spacer(1, 0.3*self.inch))
        
        # Inventario actual
        story.append(self.Paragraph("INVENTARIO ACTUAL", heading_style))
        
        inventario = reporte['datos']['inventario_actual']
        
        # Tabla de inventario por estado
        data = [['Estado', 'Cantidad', 'Machos', 'Hembras']]
        for estado, info in inventario['por_estado'].items():
            data.append([
                estado,
                str(info['cantidad']),
                str(info['machos']),
                str(info['hembras'])
            ])
        
        table = self.Table(data, colWidths=[2*self.inch, 1.5*self.inch, 1.5*self.inch, 1.5*self.inch])
        table.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.black)
        ]))
        
        story.append(table)
        story.append(self.Spacer(1, 0.2*self.inch))
        
        story.append(self.Paragraph(
            f"<b>Gestantes actuales:</b> {inventario['gestantes']}",
            styles['Normal']
        ))
        
        # Distribución por raza
        story.append(self.Spacer(1, 0.3*self.inch))
        story.append(self.Paragraph("DISTRIBUCIÓN POR RAZA", heading_style))
        
        data_raza = [['Raza', 'Cantidad']]
        for item in inventario['por_raza'][:10]:  # Top 10
            data_raza.append([item['raza'], str(item['cantidad'])])
        
        table_raza = self.Table(data_raza, colWidths=[4*self.inch, 2*self.inch])
        table_raza.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors.lightgrey)
        ]))
        
        story.append(table_raza)
    
    def _construir_pdf_reproduccion(self, story: List, reporte: Dict, title_style, heading_style, styles):
        """Construye contenido PDF para reporte de reproducción"""
        # Título
        story.append(self.Paragraph("REPORTE DE REPRODUCCIÓN", title_style))
        story.append(self.Paragraph("FincaFácil - Sistema de Gestión Ganadera", styles['Normal']))
        story.append(self.Spacer(1, 0.2*self.inch))
        
        # Info del reporte
        story.append(self.Paragraph(
            f"<b>Generado:</b> {reporte['generado_en']}<br/>"
            f"<b>Período:</b> {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}",
            styles['Normal']
        ))
        story.append(self.Spacer(1, 0.3*self.inch))
        
        datos = reporte['datos']
        
        # Servicios
        story.append(self.Paragraph("SERVICIOS REALIZADOS", heading_style))
        story.append(self.Paragraph(
            f"<b>Total de servicios:</b> {datos['servicios']['total']}",
            styles['Normal']
        ))
        story.append(self.Spacer(1, 0.1*self.inch))
        
        # Indicadores
        story.append(self.Spacer(1, 0.2*self.inch))
        story.append(self.Paragraph("INDICADORES REPRODUCTIVOS", heading_style))
        
        ind = datos['indicadores']
        data_ind = [
            ['Métrica', 'Valor'],
            ['Hembras aptas', str(ind['hembras_aptas'])],
            ['Gestantes', str(ind['gestantes'])],
            ['Tasa de preñez (%)', f"{ind['tasa_prenez_pct']}%"]
        ]
        
        table_ind = self.Table(data_ind, colWidths=[3*self.inch, 2*self.inch])
        table_ind.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors.lightgrey)
        ]))
        
        story.append(table_ind)
    
    def _construir_pdf_produccion(self, story: List, reporte: Dict, title_style, heading_style, styles):
        """Construye contenido PDF para reporte de producción"""
        # Título
        story.append(self.Paragraph("REPORTE DE PRODUCCIÓN", title_style))
        story.append(self.Paragraph("FincaFácil - Sistema de Gestión Ganadera", styles['Normal']))
        story.append(self.Spacer(1, 0.2*self.inch))
        
        # Info del reporte
        story.append(self.Paragraph(
            f"<b>Generado:</b> {reporte['generado_en']}<br/>"
            f"<b>Período:</b> {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}",
            styles['Normal']
        ))
        story.append(self.Spacer(1, 0.3*self.inch))
        
        datos = reporte['datos']
        prod = datos['produccion_periodo']
        
        # Resumen
        story.append(self.Paragraph("RESUMEN DE PRODUCCIÓN", heading_style))
        
        data_resumen = [
            ['Métrica', 'Valor'],
            ['Litros totales', f"{prod['litros_totales']:,.2f} L"],
            ['Días de producción', str(prod['dias_produccion'])],
            ['Vacas productivas', str(prod['vacas_productivas'])],
            ['Promedio litros/día', f"{datos['promedios']['promedio_litros_dia']:,.2f} L"],
            ['Promedio litros/vaca', f"{datos['promedios']['promedio_litros_vaca']:,.2f} L"]
        ]
        
        table_resumen = self.Table(data_resumen, colWidths=[3*self.inch, 2.5*self.inch])
        table_resumen.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors.lightgrey)
        ]))
        
        story.append(table_resumen)
    
    def _construir_pdf_finanzas(self, story: List, reporte: Dict, title_style, heading_style, styles):
        """Construye contenido PDF para reporte financiero"""
        # Título
        story.append(self.Paragraph("REPORTE FINANCIERO", title_style))
        story.append(self.Paragraph("FincaFácil - Sistema de Gestión Ganadera", styles['Normal']))
        story.append(self.Spacer(1, 0.2*self.inch))
        
        # Info del reporte
        story.append(self.Paragraph(
            f"<b>Generado:</b> {reporte['generado_en']}<br/>"
            f"<b>Período:</b> {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}",
            styles['Normal']
        ))
        story.append(self.Spacer(1, 0.3*self.inch))
        
        datos = reporte['datos']
        
        # Resumen financiero
        story.append(self.Paragraph("RESUMEN FINANCIERO", heading_style))
        
        data_fin = [
            ['Concepto', 'Valor (COP)'],
            ['Ingresos Totales', f"${datos['ingresos']['total']:,.0f}"],
            ['Costos Totales', f"${datos['costos']['total']:,.0f}"],
            ['Margen Bruto', f"${datos['margen']['valor']:,.0f}"],
            ['Margen (%)', f"{datos['margen']['porcentaje']:.1f}%"]
        ]
        
        table_fin = self.Table(data_fin, colWidths=[3*self.inch, 2.5*self.inch])
        table_fin.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors.lightgrey),
            # Resaltar margen
            ('BACKGROUND', (0, 3), (-1, 3), self.colors.HexColor('#c8e6c9')),
            ('BACKGROUND', (0, 4), (-1, 4), self.colors.HexColor('#c8e6c9'))
        ]))
        
        story.append(table_fin)
        
        # Desglose de ingresos
        story.append(self.Spacer(1, 0.3*self.inch))
        story.append(self.Paragraph("DESGLOSE DE INGRESOS", heading_style))
        
        data_ing = [
            ['Concepto', 'Valor (COP)'],
            ['Ventas de animales', f"${datos['ingresos']['ventas_animales']:,.0f}"],
            ['Ventas de leche', f"${datos['ingresos']['ventas_leche']:,.0f}"]
        ]
        
        table_ing = self.Table(data_ing, colWidths=[3*self.inch, 2.5*self.inch])
        table_ing.setStyle(self.TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, self.colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors.lightgrey)
        ]))
        
        story.append(table_ing)
    
    def _construir_pdf_completo(self, story: List, reporte: Dict, title_style, heading_style, styles):
        """Construye contenido PDF para reporte completo"""
        # Portada
        story.append(self.Paragraph("REPORTE COMPLETO", title_style))
        story.append(self.Paragraph("FincaFácil - Sistema de Gestión Ganadera", styles['Normal']))
        story.append(self.Spacer(1, 0.5*self.inch))
        
        story.append(self.Paragraph(
            f"<b>Generado:</b> {reporte['generado_en']}<br/>"
            f"<b>Período:</b> {reporte['periodo']['inicio']} → {reporte['periodo']['fin']}",
            styles['Normal']
        ))
        
        story.append(self.Spacer(1, 1*self.inch))
        
        # Índice de secciones
        story.append(self.Paragraph("ÍNDICE DE SECCIONES", heading_style))
        secciones = reporte.get('secciones', {})
        
        for nombre_seccion in secciones.keys():
            story.append(self.Paragraph(
                f"• {nombre_seccion.capitalize()}",
                styles['Normal']
            ))
        
        # Nota: En un PDF real, cada sección iría en una página separada
        # Por simplicidad, aquí mostramos solo el índice
        story.append(self.Spacer(1, 0.5*self.inch))
        story.append(self.Paragraph(
            "<i>Nota: Para reportes completos detallados, exporte cada sección individualmente.</i>",
            styles['Normal']
        ))


# Singleton
pdf_exporter = PDFExporter()
