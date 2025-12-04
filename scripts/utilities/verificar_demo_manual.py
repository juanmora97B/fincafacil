"""
Script de verificación para el Demo Interactivo y Manual PDF
"""
import os
import sys
from pathlib import Path

def verificar_demo_interactivo():
    """Verifica la configuración del demo interactivo"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DEL DEMO INTERACTIVO")
    print("=" * 60)
    
    # 1. Verificar archivo de configuración del tour
    config_file = Path("config/tour_completado.json")
    print(f"\n1. Archivo de configuración del tour:")
    print(f"   Ruta: {config_file}")
    
    if config_file.exists():
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
        print(f"   ✅ Existe")
        print(f"   Estado: {'Completado' if config.get('completado') else 'Pendiente (se mostrará en próxima ejecución)'}")
    else:
        print(f"   ⚠️  No existe (se mostrará en próxima ejecución)")
    
    # 2. Verificar módulo tour_interactivo.py
    tour_file = Path("utils/tour_interactivo.py")
    print(f"\n2. Módulo del tour interactivo:")
    print(f"   Ruta: {tour_file}")
    
    if tour_file.exists():
        print(f"   ✅ Existe")
        # Contar pasos del tour
        with open(tour_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class TourInteractivo' in content:
                print(f"   ✅ Clase TourInteractivo encontrada")
            if 'def iniciar_tour' in content:
                print(f"   ✅ Método iniciar_tour encontrado")
    else:
        print(f"   ❌ No existe")
    
    # 3. Verificar integración en main.py
    main_file = Path("main.py")
    print(f"\n3. Integración en main.py:")
    
    if main_file.exists():
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'verificar_primer_uso' in content:
            print(f"   ✅ Método verificar_primer_uso encontrado")
        if 'TourInteractivo' in content:
            print(f"   ✅ Importación de TourInteractivo encontrada")
        if 'self.after(1000, self.verificar_primer_uso)' in content:
            print(f"   ✅ Llamada automática al tour configurada")
    else:
        print(f"   ❌ main.py no encontrado")
    
    print("\n" + "=" * 60)

def verificar_manual_pdf():
    """Verifica el manual en PDF"""
    print("=" * 60)
    print("📚 VERIFICACIÓN DEL MANUAL PDF")
    print("=" * 60)
    
    # 1. Verificar generador de PDF
    generador_file = Path("utils/pdf_manual_generator.py")
    print(f"\n1. Generador de PDF:")
    print(f"   Ruta: {generador_file}")
    
    if generador_file.exists():
        print(f"   ✅ Existe")
        with open(generador_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'class ManualPDFGenerator' in content:
            print(f"   ✅ Clase ManualPDFGenerator encontrada")
        if 'def generar_manual' in content:
            print(f"   ✅ Método generar_manual encontrado")
    else:
        print(f"   ❌ No existe")
    
    # 2. Verificar manual PDF generado
    pdf_file = Path("docs/Manual_Usuario_FincaFacil.pdf")
    print(f"\n2. Manual PDF generado:")
    print(f"   Ruta: {pdf_file}")
    
    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        print(f"   ✅ Existe")
        print(f"   Tamaño: {size_kb:.2f} KB")
    else:
        print(f"   ⚠️  No existe (se generará automáticamente)")
    
    # 3. Verificar módulo pdf_generator.py
    pdf_gen_file = Path("utils/pdf_generator.py")
    print(f"\n3. Módulo pdf_generator.py:")
    
    if pdf_gen_file.exists():
        print(f"   ✅ Existe")
        with open(pdf_gen_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'def abrir_manual_pdf' in content:
            print(f"   ✅ Función abrir_manual_pdf encontrada")
    else:
        print(f"   ❌ No existe")
    
    # 4. Verificar integración en ajustes
    ajustes_file = Path("modules/ajustes/ajustes_main.py")
    print(f"\n4. Integración en Ajustes:")
    
    if ajustes_file.exists():
        with open(ajustes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def abrir_manual_pdf' in content:
            print(f"   ✅ Método abrir_manual_pdf encontrado")
        if 'def iniciar_tour' in content:
            print(f"   ✅ Método iniciar_tour encontrado")
        if '📖 Manual de Usuario (PDF)' in content:
            print(f"   ✅ Botón de manual encontrado")
        if '🎓 Tour Interactivo' in content:
            print(f"   ✅ Botón de tour encontrado")
    else:
        print(f"   ❌ ajustes_main.py no encontrado")
    
    print("\n" + "=" * 60)

def verificar_dependencias():
    """Verifica las dependencias necesarias"""
    print("=" * 60)
    print("📦 VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 60)
    
    dependencias = [
        ("customtkinter", "Interfaz gráfica"),
        ("reportlab", "Generación de PDFs"),
        ("Pillow", "Manejo de imágenes"),
    ]
    
    for modulo, descripcion in dependencias:
        try:
            __import__(modulo)
            print(f"   ✅ {modulo:20s} - {descripcion}")
        except ImportError:
            print(f"   ❌ {modulo:20s} - {descripcion} (NO INSTALADO)")
    
    print("\n" + "=" * 60)

def main():
    """Función principal de verificación"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🐄 FincaFacil - Verificación de Demo y Manual PDF".ljust(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    verificar_demo_interactivo()
    print("\n")
    verificar_manual_pdf()
    print("\n")
    verificar_dependencias()
    
    print("\n")
    print("=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 60)
    print("\nRecomendaciones:")
    print("1. Si 'tour_completado.json' está en 'Completado', cámbialo a 'Pendiente'")
    print("   para probar el demo en la próxima ejecución.")
    print("2. El manual PDF se genera automáticamente si no existe.")
    print("3. Accede al manual desde: Ajustes > Manual de Usuario (PDF)")
    print("4. Reinicia el tour desde: Ajustes > Tour Interactivo")
    print("\n")

if __name__ == "__main__":
    main()
