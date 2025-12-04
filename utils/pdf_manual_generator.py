"""
Generador de Manual PDF para FincaFacil
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
import os

class ManualPDFGenerator:
    """Genera el Manual de Usuario en formato PDF"""
    
    def __init__(self):
        self.output_dir = Path("docs")
        self.output_dir.mkdir(exist_ok=True)
        self.output_file = self.output_dir / "Manual_Usuario_FincaFacil.pdf"
        
    def generar_manual(self):
        """Genera el manual completo en PDF"""
        doc = SimpleDocTemplate(
            str(self.output_file),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Contenedor de elementos
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulo
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#455A64'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Estilo para encabezados de sección
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E7D32'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para sub-encabezados
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para texto normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )
        
        # Estilo para listas
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6
        )
        
        # PORTADA
        story.append(Spacer(1, 2*inch))
        
        # Intentar agregar logo
        try:
            logo_path = Path(__file__).parent.parent / "assets" / "Logo.png"
            if logo_path.exists():
                img = Image(str(logo_path), width=2*inch, height=2*inch)
                story.append(img)
                story.append(Spacer(1, 0.5*inch))
        except:
            pass
        
        story.append(Paragraph("Manual de Usuario", titulo_style))
        story.append(Paragraph("FincaFacil v2.0", subtitulo_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Sistema de Gestión Ganadera Profesional", subtitulo_style))
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y')}", normal_style))
        story.append(PageBreak())
        
        # ÍNDICE
        story.append(Paragraph("📋 Tabla de Contenido", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            "1. Introducción",
            "2. Instalación e Inicio",
            "3. Módulos del Sistema",
            "4. Configuración Inicial",
            "5. Flujos de Trabajo Comunes",
            "6. Respaldo y Restauración",
            "7. Soporte y Ayuda",
            "8. Consejos y Buenas Prácticas",
            "9. Solución de Problemas",
            "10. Información Técnica",
            "11. Glosario"
        ]
        
        for item in toc_items:
            story.append(Paragraph(f"• {item}", bullet_style))
        
        story.append(PageBreak())
        
        # 1. INTRODUCCIÓN
        story.append(Paragraph("1. INTRODUCCIÓN", heading_style))
        
        story.append(Paragraph(
            "<b>FincaFacil</b> es un sistema integral de gestión ganadera diseñado para optimizar "
            "la administración de fincas ganaderas. Permite el control completo de animales, "
            "reproducción, salud, producción, inventarios y finanzas.",
            normal_style
        ))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Características Principales:", subheading_style))
        
        caracteristicas = [
            "✅ Gestión completa de inventario animal",
            "✅ Control reproductivo con predicción de partos",
            "✅ Registro de eventos de salud y diagnósticos",
            "✅ Manejo de potreros y rotación de pastoreo",
            "✅ Administración de tratamientos veterinarios",
            "✅ Control de ventas y facturación",
            "✅ Inventario de insumos con alertas",
            "✅ Gestión de herramientas y mantenimientos",
            "✅ Dashboard con KPIs en tiempo real",
            "✅ Sistema de reportes y exportación",
            "✅ Nómina de empleados",
            "✅ Backups automáticos"
        ]
        
        for item in caracteristicas:
            story.append(Paragraph(item, bullet_style))
        
        story.append(PageBreak())
        
        # 2. INSTALACIÓN E INICIO
        story.append(Paragraph("2. INSTALACIÓN E INICIO", heading_style))
        
        story.append(Paragraph("Requisitos del Sistema:", subheading_style))
        requisitos = [
            "• Windows 10/11",
            "• Python 3.8 o superior",
            "• 4GB RAM mínimo",
            "• 500MB espacio en disco"
        ]
        for req in requisitos:
            story.append(Paragraph(req, bullet_style))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Instalación Paso a Paso:", subheading_style))
        
        story.append(Paragraph(
            "<b>1. Instalar Dependencias:</b> Ejecutar <i>instalar_dependencias.bat</i> y "
            "esperar a que se instalen todas las librerías.",
            normal_style
        ))
        
        story.append(Paragraph(
            "<b>2. Iniciar la Aplicación:</b> Ejecutar <i>ejecutar.bat</i> o ejecutar: "
            "<i>python main.py</i>",
            normal_style
        ))
        
        story.append(Paragraph(
            "<b>3. Primer Inicio:</b> La aplicación mostrará un tour interactivo automáticamente. "
            "Complete la configuración inicial y agregue su primera finca.",
            normal_style
        ))
        
        story.append(PageBreak())
        
        # 3. MÓDULOS DEL SISTEMA
        story.append(Paragraph("3. MÓDULOS DEL SISTEMA", heading_style))
        
        modulos = [
            {
                "icono": "📊",
                "nombre": "DASHBOARD",
                "descripcion": "Vista general del sistema con métricas y gráficos en tiempo real.",
                "caracteristicas": [
                    "Métricas principales (Total animales, Activos, Valor inventario)",
                    "Gráfico de estado de animales",
                    "Gráfico de producción de leche (30 días)",
                    "Eventos recientes y alertas del sistema"
                ]
            },
            {
                "icono": "🐄",
                "nombre": "ANIMALES",
                "descripcion": "Gestión completa del inventario ganadero.",
                "caracteristicas": [
                    "Registro de animales con código único",
                    "Ficha completa de cada animal",
                    "Inventario con filtros y búsqueda",
                    "Actualización de peso y producción",
                    "Importación masiva desde Excel"
                ]
            },
            {
                "icono": "🤰",
                "nombre": "REPRODUCCIÓN",
                "descripcion": "Control del ciclo reproductivo del ganado.",
                "caracteristicas": [
                    "Registro de servicios (monta o IA)",
                    "Hembras gestantes con días de gestación",
                    "Cálculo automático de fecha de parto (280 días)",
                    "Próximos partos y confirmación de nacimientos"
                ]
            },
            {
                "icono": "🏥",
                "nombre": "SALUD",
                "descripcion": "Registro de eventos médicos y diagnósticos veterinarios.",
                "caracteristicas": [
                    "Registro de diagnósticos con severidad",
                    "Estados: Activo, En Tratamiento, Recuperado, Crónico",
                    "Historial completo por animal",
                    "Vinculación con tratamientos"
                ]
            },
            {
                "icono": "🌿",
                "nombre": "POTREROS",
                "descripcion": "Gestión de terrenos y pastoreo.",
                "caracteristicas": [
                    "Registro de potreros por finca",
                    "Control de capacidad animal",
                    "Rotación de pastoreo",
                    "Estados: Disponible, En uso, En descanso"
                ]
            },
            {
                "icono": "💊",
                "nombre": "TRATAMIENTOS",
                "descripcion": "Administración de medicamentos y tratamientos veterinarios.",
                "caracteristicas": [
                    "Registro de tratamientos con dosis",
                    "Vinculación a diagnósticos",
                    "Control de duración y frecuencia",
                    "Registro de costos"
                ]
            },
            {
                "icono": "💰",
                "nombre": "VENTAS",
                "descripcion": "Control de ventas de animales y productos.",
                "caracteristicas": [
                    "Registro de ventas (animales, leche, otros)",
                    "Control de precios y formas de pago",
                    "Actualización automática de inventario",
                    "Historial y reportes de ventas"
                ]
            },
            {
                "icono": "📦",
                "nombre": "INSUMOS",
                "descripcion": "Control de inventario de suministros.",
                "caracteristicas": [
                    "Inventario con stock actual/mínimo/máximo",
                    "Movimientos de entrada y salida",
                    "Alertas de bajo stock",
                    "Control de vencimientos"
                ]
            },
            {
                "icono": "🔧",
                "nombre": "HERRAMIENTAS",
                "descripcion": "Gestión de equipos y maquinaria.",
                "caracteristicas": [
                    "Catálogo de herramientas y equipos",
                    "Control de estado operativo",
                    "Mantenimientos preventivos y correctivos",
                    "Historial de reparaciones"
                ]
            },
            {
                "icono": "📋",
                "nombre": "REPORTES",
                "descripcion": "Generación de reportes y análisis.",
                "caracteristicas": [
                    "Reportes de inventario, producción, ventas",
                    "Exportación a Excel y CSV",
                    "Filtros por período y categoría",
                    "Análisis para toma de decisiones"
                ]
            }
        ]
        
        for modulo in modulos:
            story.append(Paragraph(f"{modulo['icono']} {modulo['nombre']}", subheading_style))
            story.append(Paragraph(modulo['descripcion'], normal_style))
            story.append(Paragraph("Características:", ParagraphStyle('Bold', parent=normal_style, fontName='Helvetica-Bold')))
            for caract in modulo['caracteristicas']:
                story.append(Paragraph(f"• {caract}", bullet_style))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        
        # 4. CONFIGURACIÓN INICIAL
        story.append(Paragraph("4. CONFIGURACIÓN INICIAL", heading_style))
        
        config_steps = [
            {
                "titulo": "Paso 1: Configurar Fincas",
                "pasos": [
                    "Ir a Configuración > Fincas",
                    "Agregar finca con nombre, NIT/RUT, dirección, teléfono, hectáreas"
                ]
            },
            {
                "titulo": "Paso 2: Configurar Razas",
                "pasos": [
                    "Ir a Configuración > Razas",
                    "Agregar razas que maneja (Brahman, Holstein, Jersey, etc.)"
                ]
            },
            {
                "titulo": "Paso 3: Configurar Potreros",
                "pasos": [
                    "Ir a Potreros",
                    "Agregar potreros de cada finca",
                    "Especificar hectáreas y tipo de pasto"
                ]
            },
            {
                "titulo": "Paso 4: Agregar Primer Animal",
                "pasos": [
                    "Ir a Animales > Registro",
                    "Completar información básica",
                    "Asignar a finca y potrero"
                ]
            }
        ]
        
        for step in config_steps:
            story.append(Paragraph(step['titulo'], subheading_style))
            for paso in step['pasos']:
                story.append(Paragraph(f"• {paso}", bullet_style))
            story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
        
        # 5. FLUJOS DE TRABAJO COMUNES
        story.append(Paragraph("5. FLUJOS DE TRABAJO COMUNES", heading_style))
        
        story.append(Paragraph("Flujo 1: Nuevo Animal en la Finca", subheading_style))
        flujo1 = [
            "1. Ir a Animales > Registro",
            "2. Ingresar código único y datos básicos",
            "3. Establecer precio de compra y ubicación",
            "4. Confirmar registro",
            "5. Actualizar inventario (peso, producción)"
        ]
        for paso in flujo1:
            story.append(Paragraph(paso, bullet_style))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Flujo 2: Servicio Reproductivo", subheading_style))
        flujo2 = [
            "1. Ir a Reproducción > Nuevo Servicio",
            "2. Seleccionar hembra y registrar fecha",
            "3. Especificar tipo (Natural/IA) y toro/semen",
            "4. Monitorear en 'Gestantes' (280 días automáticos)",
            "5. Revisar 'Próximos Partos'",
            "6. Confirmar parto cuando ocurra"
        ]
        for paso in flujo2:
            story.append(Paragraph(paso, bullet_style))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Flujo 3: Tratamiento Veterinario", subheading_style))
        flujo3 = [
            "1. Salud > Nuevo Diagnóstico (registrar síntomas y severidad)",
            "2. Tratamientos > Nuevo Tratamiento (vincular a diagnóstico)",
            "3. Especificar medicamento, dosis y duración",
            "4. Actualizar estado del diagnóstico",
            "5. Insumos > Registrar Salida (descontar medicamento)"
        ]
        for paso in flujo3:
            story.append(Paragraph(paso, bullet_style))
        
        story.append(PageBreak())
        
        # 6. RESPALDO Y RESTAURACIÓN
        story.append(Paragraph("6. RESPALDO Y RESTAURACIÓN", heading_style))
        
        story.append(Paragraph("Hacer Backup Manual:", subheading_style))
        backup_steps = [
            "1. Ir a Ajustes",
            "2. Sección 'Copias de seguridad'",
            "3. Clic en 'Hacer Backup Ahora'",
            "4. Confirmar cuando aparezca mensaje de éxito",
            "5. Archivo guardado en carpeta backup/"
        ]
        for step in backup_steps:
            story.append(Paragraph(step, bullet_style))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Restaurar Backup:", subheading_style))
        restore_steps = [
            "1. Ir a Ajustes",
            "2. Clic en 'Restaurar Backup'",
            "3. Seleccionar archivo de backup",
            "4. Confirmar restauración",
            "5. Sistema crea backup de seguridad antes de restaurar",
            "6. Aplicación se reiniciará automáticamente"
        ]
        for step in restore_steps:
            story.append(Paragraph(step, bullet_style))
        
        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph(
            "<b>⚠️ IMPORTANTE:</b> El sistema crea backup automático antes de restaurar. "
            "No se pierde información y el proceso es reversible.",
            normal_style
        ))
        
        story.append(PageBreak())
        
        # 7. SOPORTE Y AYUDA
        story.append(Paragraph("7. SOPORTE Y AYUDA", heading_style))
        
        story.append(Paragraph("Tour Interactivo", subheading_style))
        story.append(Paragraph(
            "Se activa automáticamente en el primer uso. Puede reactivarse desde "
            "<b>Ajustes > Tour Interactivo</b>. Guía paso a paso por las funciones principales.",
            normal_style
        ))
        
        story.append(Paragraph("Manual PDF", subheading_style))
        story.append(Paragraph(
            "Disponible en <b>Ajustes > Manual de Usuario</b>. Se puede imprimir y "
            "es una referencia completa del sistema.",
            normal_style
        ))
        
        story.append(Paragraph("Logs del Sistema", subheading_style))
        story.append(Paragraph(
            "Ubicación: <i>logs/fincafacil.log</i>. Contiene historial de eventos "
            "útil para diagnóstico de problemas.",
            normal_style
        ))
        
        story.append(PageBreak())
        
        # 8. CONSEJOS Y BUENAS PRÁCTICAS
        story.append(Paragraph("8. CONSEJOS Y BUENAS PRÁCTICAS", heading_style))
        
        consejos_secciones = [
            {
                "titulo": "Gestión de Animales",
                "consejos": [
                    "✅ Use códigos únicos consistentes",
                    "✅ Actualice pesos regularmente",
                    "✅ Registre eventos importantes inmediatamente",
                    "✅ Mantenga actualizada la ubicación (potrero)"
                ]
            },
            {
                "titulo": "Reproducción",
                "consejos": [
                    "✅ Registre servicios el mismo día",
                    "✅ Monitoree hembras gestantes semanalmente",
                    "✅ Prepare partos con anticipación (30 días antes)",
                    "✅ Confirme partos inmediatamente"
                ]
            },
            {
                "titulo": "Respaldos",
                "consejos": [
                    "✅ Haga backup diario",
                    "✅ Mantenga múltiples copias",
                    "✅ Guarde backups en ubicación externa",
                    "✅ Pruebe restauración periódicamente"
                ]
            }
        ]
        
        for seccion in consejos_secciones:
            story.append(Paragraph(seccion['titulo'], subheading_style))
            for consejo in seccion['consejos']:
                story.append(Paragraph(consejo, bullet_style))
            story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
        
        # 9. SOLUCIÓN DE PROBLEMAS
        story.append(Paragraph("9. SOLUCIÓN DE PROBLEMAS", heading_style))
        
        problemas = [
            {
                "problema": "La aplicación no inicia",
                "soluciones": [
                    "Verificar que Python esté instalado",
                    "Ejecutar instalar_dependencias.bat",
                    "Revisar archivo logs/fincafacil.log"
                ]
            },
            {
                "problema": "Error de base de datos",
                "soluciones": [
                    "Verificar que exista archivo database/fincafacil.db",
                    "Restaurar desde backup",
                    "Ejecutar migrar_tablas.bat"
                ]
            },
            {
                "problema": "No se puede hacer backup",
                "soluciones": [
                    "Verificar permisos de escritura en carpeta backup/",
                    "Verificar espacio en disco",
                    "Cerrar otros programas que usen la BD"
                ]
            }
        ]
        
        for item in problemas:
            story.append(Paragraph(item['problema'], subheading_style))
            for solucion in item['soluciones']:
                story.append(Paragraph(f"• {solucion}", bullet_style))
            story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
        
        # 10. INFORMACIÓN TÉCNICA
        story.append(Paragraph("10. INFORMACIÓN TÉCNICA", heading_style))
        
        story.append(Paragraph("Versión del Sistema:", subheading_style))
        version_info = [
            "• Versión: 2.0",
            "• Fecha: Noviembre 2025",
            "• Base de datos: SQLite 3",
            "• Framework UI: CustomTkinter",
            "• Lenguaje: Python 3.8+"
        ]
        for info in version_info:
            story.append(Paragraph(info, bullet_style))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Módulos Python Utilizados:", subheading_style))
        modulos_python = [
            "• customtkinter: Interfaz gráfica moderna",
            "• matplotlib: Gráficos y visualizaciones",
            "• openpyxl: Manejo de archivos Excel",
            "• Pillow: Procesamiento de imágenes",
            "• reportlab: Generación de PDFs"
        ]
        for mod in modulos_python:
            story.append(Paragraph(mod, bullet_style))
        
        story.append(PageBreak())
        
        # 11. GLOSARIO
        story.append(Paragraph("11. GLOSARIO", heading_style))
        
        glosario = [
            ("Animal Activo", "Animal presente en la finca y en operación normal."),
            ("Condición Corporal", "Evaluación del estado físico del animal (escala 1-5)."),
            ("Gestación", "Período de embarazo (280 días promedio en bovinos)."),
            ("IA", "Inseminación Artificial - Método reproductivo con semen procesado."),
            ("Inventario", "Conteo físico de animales presentes en la finca."),
            ("KPI", "Indicador Clave de Desempeño (Key Performance Indicator)."),
            ("Potrero", "División de terreno para pastoreo de animales."),
            ("Rotación de Pastoreo", "Cambio periódico de animales entre potreros."),
            ("Stock", "Cantidad disponible de insumos en inventario.")
        ]
        
        for termino, definicion in glosario:
            story.append(Paragraph(f"<b>{termino}:</b> {definicion}", normal_style))
        
        story.append(PageBreak())
        
        # PÁGINA FINAL
        story.append(Spacer(1, 3*inch))
        story.append(Paragraph("FincaFacil v2.0", titulo_style))
        story.append(Paragraph("Sistema de Gestión Ganadera Profesional", subtitulo_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("© 2025 - Todos los derechos reservados", normal_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "Este manual está diseñado para ser una guía completa del sistema. "
            "Para información adicional o capacitación, consulte con el administrador.",
            normal_style
        ))
        
        # Construir PDF
        doc.build(story)
        return str(self.output_file)

def generar_manual_pdf():
    """Función principal para generar el manual"""
    try:
        generator = ManualPDFGenerator()
        output_path = generator.generar_manual()
        print(f"✅ Manual PDF generado exitosamente: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error generando manual PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    generar_manual_pdf()
