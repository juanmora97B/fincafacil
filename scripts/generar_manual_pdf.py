"""
Generador de Manual PDF profesional para FincaFácil
Usa ReportLab para crear un documento PDF completo con:
- Portada
- Tabla de contenidos
- Manual de usuario por módulo
- Guía rápida
- Preguntas frecuentes
- Troubleshooting
- Contacto y soporte
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import datetime
import sys

# Colores de marca
COLOR_PRINCIPAL = colors.HexColor("#2E7D32")  # Verde FincaFácil
COLOR_SECUNDARIO = colors.HexColor("#1B5E20")
COLOR_GRIS = colors.HexColor("#666666")
COLOR_TITULO = colors.HexColor("#1a1a1a")

def crear_manual_pdf(output_path: str = "docs/Manual_FincaFacil_v2.pdf"):
    """
    Crea el manual PDF completo
    
    Args:
        output_path: Ruta donde se guardará el PDF
    """
    # Crear directorio si no existe
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Crear documento
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch,
        title="Manual FincaFácil",
        author="FincaFácil Development Team",
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle(
        'TituloCustom',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=COLOR_TITULO,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_subtitulo = ParagraphStyle(
        'SubtituloCustom',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=COLOR_PRINCIPAL,
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    style_seccion = ParagraphStyle(
        'SeccionCustom',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=COLOR_SECUNDARIO,
        spaceAfter=6,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    style_cuerpo = ParagraphStyle(
        'CuerpoCustom',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=COLOR_GRIS,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    # Contenido del documento
    story = []
    
    # =================== PORTADA ===================
    story.append(Spacer(1, 2*inch))
    
    # Logo/Título
    story.append(Paragraph("FincaFácil", style_titulo))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Sistema de Gestión Ganadera", 
        ParagraphStyle('Subtitulo1', parent=styles['Normal'], fontSize=18, 
        textColor=COLOR_PRINCIPAL, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Manual de Usuario - v2.0", 
        ParagraphStyle('Subtitulo2', parent=styles['Normal'], fontSize=14, 
        textColor=COLOR_GRIS, alignment=TA_CENTER)))
    
    story.append(Spacer(1, 2*inch))
    
    # Información de documento
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    info_doc = f"""
    <b>Fecha de emisión:</b> {fecha_actual}<br/>
    <b>Versión:</b> 2.0<br/>
    <b>Licencia:</b> Prueba gratuita de 6 meses<br/>
    <b>Soporte:</b> jfburitica97@gmail.com | Tel: 3013869653<br/>
    """
    story.append(Paragraph(info_doc, 
        ParagraphStyle('Info', parent=styles['Normal'], fontSize=10, 
        textColor=COLOR_GRIS, alignment=TA_CENTER, leading=14)))
    
    story.append(PageBreak())
    
    # =================== ÍNDICE ===================
    story.append(Paragraph("Tabla de Contenidos", style_titulo))
    story.append(Spacer(1, 0.2*inch))
    
    indice_items = [
        "1. Introducción",
        "2. Primeros pasos",
        "3. Módulos del sistema",
        "   3.1. Dashboard",
        "   3.2. Animales",
        "   3.3. Potreros",
        "   3.4. Salud y Reproducción",
        "   3.5. Leche y Ordeño",
        "   3.6. Ventas",
        "   3.7. Herramientas e Insumos",
        "   3.8. Nómina",
        "   3.9. Reportes",
        "4. Configuración y Ajustes",
        "5. Guía rápida",
        "6. Preguntas frecuentes",
        "7. Troubleshooting",
        "8. Contacto y soporte",
    ]
    
    for item in indice_items:
        story.append(Paragraph(f"• {item}", style_cuerpo))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # =================== INTRODUCCIÓN ===================
    story.append(Paragraph("1. Introducción", style_subtitulo))
    
    intro_text = """
    <b>FincaFácil</b> es una aplicación profesional de gestión ganadera diseñada 
    para facilitar el manejo integral de fincas ganaderas. Desde el control de animales 
    hasta la gestión de ventas, FincaFácil centraliza todas tus operaciones en una 
    interfaz intuitiva y fácil de usar.
    """
    story.append(Paragraph(intro_text, style_cuerpo))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Características principales:", style_seccion))
    caracteristicas = [
        "✓ Gestión completa de animales y genealogía",
        "✓ Control de salud y reproducción",
        "✓ Registro de producción de leche",
        "✓ Gestión de potreros y pastos",
        "✓ Control de vendimia y ventas",
        "✓ Nómina y gestión de empleados",
        "✓ Reportes detallados y análisis",
        "✓ Importación/exportación de datos",
    ]
    for caract in caracteristicas:
        story.append(Paragraph(caract, style_cuerpo))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(PageBreak())
    
    # =================== PRIMEROS PASOS ===================
    story.append(Paragraph("2. Primeros pasos", style_subtitulo))
    
    story.append(Paragraph("2.1. Instalación", style_seccion))
    story.append(Paragraph(
        "FincaFácil viene como una aplicación ejecutable. Simplemente descarga e instala "
        "ejecutando el instalador. No se requiere ninguna configuración adicional.",
        style_cuerpo
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("2.2. Primer inicio", style_seccion))
    story.append(Paragraph(
        "Al ejecutar FincaFácil por primera vez, se te pedirá crear una cuenta. "
        "Ingresa un nombre de usuario y contraseña. ¡Eso es todo! Tu período de prueba "
        "de 6 meses comenzará automáticamente.",
        style_cuerpo
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("2.3. Tour interactivo", style_seccion))
    story.append(Paragraph(
        "En tu primer inicio, te ofreceremos un tour interactivo para familiarizarte "
        "con la interfaz. Puedes omitir este tour en cualquier momento desde los ajustes.",
        style_cuerpo
    ))
    
    story.append(PageBreak())
    
    # =================== MÓDULOS ===================
    story.append(Paragraph("3. Módulos del Sistema", style_subtitulo))
    
    modulos = [
        {
            "nombre": "3.1. Dashboard",
            "descripcion": "Vista general de tu finca con indicadores clave, últimas actividades y resúmenes de producción.",
        },
        {
            "nombre": "3.2. Animales",
            "descripcion": "Gestión completa de animales: registro, genealogía, fotos, historial de cambios y etiquetado.",
        },
        {
            "nombre": "3.3. Potreros",
            "descripcion": "Control de terrenos, capacidad de carga, rotación de pasto y distribución de animales.",
        },
        {
            "nombre": "3.4. Salud y Reproducción",
            "descripcion": "Registro de diagnósticos veterinarios, vacunaciones, tratamientos y eventos reproductivos.",
        },
        {
            "nombre": "3.5. Leche y Ordeño",
            "descripcion": "Control diario de producción de leche, calidad y registros de ordeño.",
        },
        {
            "nombre": "3.6. Ventas",
            "descripcion": "Gestión de transacciones comerciales, clientes y análisis de precios.",
        },
        {
            "nombre": "3.7. Herramientas e Insumos",
            "descripcion": "Inventario de herramientas, medicinas y suministros con control de stock.",
        },
        {
            "nombre": "3.8. Nómina",
            "descripcion": "Gestión de empleados, salarios y registros de asistencia.",
        },
        {
            "nombre": "3.9. Reportes",
            "descripcion": "Reportes profesionales exportables en PDF y Excel.",
        },
    ]
    
    for modulo in modulos:
        story.append(Paragraph(modulo["nombre"], style_seccion))
        story.append(Paragraph(modulo["descripcion"], style_cuerpo))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # =================== CONFIGURACIÓN ===================
    story.append(Paragraph("4. Configuración y Ajustes", style_subtitulo))
    
    story.append(Paragraph(
        "Accede a los ajustes desde el menú principal. Aquí puedes:",
        style_cuerpo
    ))
    
    ajustes_items = [
        "Cambiar el modo de interfaz (claro/oscuro)",
        "Establecer idioma y unidades de medida",
        "Ver estado de tu licencia",
        "Gestionar copias de seguridad",
        "Descargar plantillas de importación",
        "Acceder a la documentación",
    ]
    
    for ajuste in ajustes_items:
        story.append(Paragraph(f"• {ajuste}", style_cuerpo))
        story.append(Spacer(1, 0.05*inch))
    
    story.append(PageBreak())
    
    # =================== GUÍA RÁPIDA ===================
    story.append(Paragraph("5. Guía Rápida", style_subtitulo))
    
    guia_items = [
        ("Agregar un nuevo animal", "Módulo Animales → Botón [+] → Completa el formulario"),
        ("Registrar producción de leche", "Módulo Leche → Nueva entrada → Ingresa cantidad y calidad"),
        ("Ver reportes", "Módulo Reportes → Selecciona tipo → Exporta a PDF o Excel"),
        ("Hacer backup", "Ajustes → Copias de seguridad → [Hacer Backup Ahora]"),
        ("Cambiar contraseña", "Ajustes → Cambiar contraseña → Ingresa contraseña actual y nueva"),
    ]
    
    for accion, pasos in guia_items:
        story.append(Paragraph(f"<b>{accion}:</b> {pasos}", style_cuerpo))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # =================== FAQ ===================
    story.append(Paragraph("6. Preguntas Frecuentes", style_subtitulo))
    
    faqs = [
        {
            "pregunta": "¿Cuánto cuesta FincaFácil?",
            "respuesta": "FincaFácil ofrece 6 meses de prueba completamente gratis sin necesidad de tarjeta de crédito. "
                        "Después puedes activar una licencia permanente con un código de activación."
        },
        {
            "pregunta": "¿Mis datos están seguros?",
            "respuesta": "Sí. Todos los datos se almacenan localmente en tu computadora. Se recomienda hacer "
                        "copias de seguridad regularmente desde los ajustes."
        },
        {
            "pregunta": "¿Puedo importar datos de otra aplicación?",
            "respuesta": "Sí. FincaFácil proporciona plantillas de Excel que puedes usar para importar datos masivos."
        },
        {
            "pregunta": "¿Necesito conexión a internet?",
            "respuesta": "No. FincaFácil funciona completamente offline. No requiere conexión a internet."
        },
        {
            "pregunta": "¿Qué pasa después de los 6 meses de prueba?",
            "respuesta": "Recibirás un recordatorio para activar tu licencia. Sin activar, la aplicación dejará de funcionar."
        },
    ]
    
    for faq in faqs:
        story.append(Paragraph(f"<b>P: {faq['pregunta']}</b>", style_seccion))
        story.append(Paragraph(f"<b>R:</b> {faq['respuesta']}", style_cuerpo))
        story.append(Spacer(1, 0.15*inch))
    
    story.append(PageBreak())
    
    # =================== TROUBLESHOOTING ===================
    story.append(Paragraph("7. Troubleshooting", style_subtitulo))
    
    problems = [
        {
            "problema": "La aplicación no inicia",
            "solución": "Asegúrate de tener Python 3.11+ instalado. Intenta eliminar la carpeta 'config' "
                       "y vuelve a ejecutar la aplicación."
        },
        {
            "problema": "Olvide mi contraseña",
            "solución": "Contacta a jfburitica97@gmail.com (Tel: 3013869653) con detalles de tu cuenta para recuperarla."
        },
        {
            "problema": "La base de datos se corrompió",
            "solución": "Restaura desde una copia de seguridad previa en Ajustes → Copias de seguridad → Restaurar."
        },
        {
            "problema": "Los reportes no se exportan",
            "solución": "Verifica que tengas permisos de escritura en la carpeta de descargas. Intenta cambiar "
                       "de ubicación en Ajustes."
        },
    ]
    
    for problem in problems:
        story.append(Paragraph(f"<b>Problema:</b> {problem['problema']}", style_seccion))
        story.append(Paragraph(f"<b>Solución:</b> {problem['solución']}", style_cuerpo))
        story.append(Spacer(1, 0.15*inch))
    
    story.append(PageBreak())
    
    # =================== CONTACTO ===================
    story.append(Paragraph("8. Contacto y Soporte", style_subtitulo))
    
    story.append(Paragraph(
        "Si necesitas ayuda o tienes preguntas, no dudes en contactarnos:",
        style_cuerpo
    ))
    
    story.append(Spacer(1, 0.2*inch))
    
    contacto_data = [
        ["Email", "jfburitica97@gmail.com"],
        ["Teléfono", "3013869653"],
        ["Sitio web", "www.fincafacil.com"],
        ["Horario soporte", "Lunes a viernes, 8:00 AM a 5:00 PM"],
    ]
    
    contacto_table = Table(contacto_data, colWidths=[1.5*inch, 4*inch])
    contacto_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), COLOR_PRINCIPAL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(contacto_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph(
        "<b>Gracias por usar FincaFácil.</b><br/><br/>"
        "Versión 2.0 - Año 2025<br/>"
        "Desarrollado con 🐄",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=11, 
        textColor=COLOR_PRINCIPAL, alignment=TA_CENTER, leading=14)
    ))
    
    # Construir PDF
    doc.build(story)
    print(f"✓ Manual PDF creado exitosamente: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    try:
        output_path = crear_manual_pdf()
        print(f"\nManual guardado en: {output_path}")
    except Exception as e:
        print(f"Error al generar manual: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
