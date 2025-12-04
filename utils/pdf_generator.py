"""
Generador de Manual en PDF
"""
import os
import sys
from pathlib import Path
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import markdown
import re

def abrir_manual_pdf():
    """
    Genera (si no existe) y abre el manual de usuario en PDF
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    try:
        # Ruta del manual PDF
        pdf_path = Path(__file__).parent.parent / "docs" / "Manual_Usuario_FincaFacil.pdf"
        
        # Si no existe, generarlo
        if not pdf_path.exists():
            print("📄 Generando manual PDF por primera vez...")
            
            # Importar y ejecutar el generador
            try:
                resultado = generar_manual_pdf()
                
                if not resultado[0]:
                    return False, f"No se pudo generar el manual PDF: {resultado[1]}"
                
                pdf_path = Path(resultado[1]) if isinstance(resultado[1], str) else pdf_path
                
            except Exception as e:
                return False, f"Error generando manual: {e}"
        
        # Verificar que el archivo existe
        if not pdf_path.exists():
            return False, f"No se encontró el archivo: {pdf_path}"
        
        # Abrir el PDF según el sistema operativo
        try:
            if sys.platform == "win32":
                # Windows
                os.startfile(str(pdf_path))
            elif sys.platform == "darwin":
                # macOS
                subprocess.call(["open", str(pdf_path)])
            else:
                # Linux
                subprocess.call(["xdg-open", str(pdf_path)])
            
            return True, "Manual abierto correctamente"
            
        except Exception as e:
            return False, f"No se pudo abrir el archivo PDF: {e}"
    
    except Exception as e:
        return False, f"Error inesperado: {e}"

def generar_manual_pdf():
    """Genera el manual de usuario en formato PDF"""
    
    # Rutas
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(base_dir, "docs", "Manual_Usuario_FincaFacil.md")
    pdf_path = os.path.join(base_dir, "docs", "Manual_Usuario_FincaFacil.pdf")
    
    # Verificar que existe el archivo markdown
    if not os.path.exists(md_path):
        return False, "No se encontró el archivo markdown del manual"
    
    try:
        # Leer el archivo markdown
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Crear el PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para título principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#1f538d',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#1f538d',
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para encabezados de sección
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor='#2e7d32',
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        )
        
        # Lista de elementos del PDF
        story = []
        
        # Procesar el contenido markdown línea por línea
        lines = md_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Saltar líneas vacías
            if not line:
                i += 1
                continue
            
            # Título principal (# )
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 0.2*inch))
            
            # Subtítulo (## )
            elif line.startswith('## '):
                text = line[3:].strip()
                # Si es un nuevo capítulo principal, agregar salto de página
                if re.match(r'^\d+\.', text):
                    story.append(PageBreak())
                story.append(Paragraph(text, subtitle_style))
                story.append(Spacer(1, 0.1*inch))
            
            # Encabezado de sección (### )
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, heading_style))
                story.append(Spacer(1, 0.05*inch))
            
            # Línea horizontal (---)
            elif line.startswith('---'):
                story.append(Spacer(1, 0.1*inch))
            
            # Listas con viñetas o numeradas
            elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                # Convertir markdown a HTML simple
                if line.startswith('- ') or line.startswith('* '):
                    text = '• ' + line[2:].strip()
                else:
                    text = line
                
                # Reemplazar formato markdown
                text = text.replace('**', '<b>').replace('**', '</b>')
                text = text.replace('✅', '✓')
                text = text.replace('⚠️', '!')
                
                story.append(Paragraph(text, normal_style))
            
            # Párrafos normales
            else:
                text = line
                # Reemplazar formato markdown
                text = text.replace('**', '<b>').replace('**', '</b>')
                text = text.replace('✅', '✓')
                text = text.replace('⚠️', '!')
                text = text.replace('📋', '')
                text = text.replace('🐄', '')
                text = text.replace('🤰', '')
                text = text.replace('🏥', '')
                text = text.replace('🌿', '')
                text = text.replace('💊', '')
                text = text.replace('💰', '')
                text = text.replace('📦', '')
                text = text.replace('🔧', '')
                text = text.replace('📋', '')
                text = text.replace('👥', '')
                text = text.replace('⚙️', '')
                text = text.replace('📊', '')
                
                story.append(Paragraph(text, normal_style))
            
            i += 1
        
        # Generar el PDF
        doc.build(story)
        
        return True, pdf_path
    
    except Exception as e:
        return False, f"Error al generar PDF: {str(e)}"

def abrir_manual_pdf():
    """Abre el manual PDF con el visor predeterminado"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(base_dir, "docs", "Manual_Usuario_FincaFacil.pdf")
    
    # Generar si no existe
    if not os.path.exists(pdf_path):
        exito, resultado = generar_manual_pdf()
        if not exito:
            return False, resultado
    
    try:
        # Abrir con el visor predeterminado del sistema
        os.startfile(pdf_path)
        return True, "Manual abierto correctamente"
    except Exception as e:
        return False, f"Error al abrir manual: {str(e)}"
