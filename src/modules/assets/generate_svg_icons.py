"""
Generador de iconos SVG profesionales para cada módulo FincaFacil
"""
from pathlib import Path

SVG_ICONS = {
    "dashboard": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <rect x="3" y="3" width="7" height="7" rx="1"></rect>
  <rect x="14" y="3" width="7" height="7" rx="1"></rect>
  <rect x="14" y="14" width="7" height="7" rx="1"></rect>
  <rect x="3" y="14" width="7" height="7" rx="1"></rect>
</svg>''',
    
    "animales": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Vaca estilizada -->
  <ellipse cx="50" cy="50" rx="30" ry="35" fill="currentColor"/>
  <!-- Cabeza -->
  <circle cx="50" cy="25" r="15" fill="currentColor"/>
  <!-- Orejas -->
  <ellipse cx="40" cy="12" rx="5" ry="8" fill="currentColor"/>
  <ellipse cx="60" cy="12" rx="5" ry="8" fill="currentColor"/>
  <!-- Cuernos -->
  <path d="M 38 10 Q 30 5 28 0" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M 62 10 Q 70 5 72 0" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>
</svg>''',
    
    "reproduccion": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Vaca preñada con ternero -->
  <ellipse cx="50" cy="55" rx="35" ry="28" fill="currentColor"/>
  <!-- Barriga hinchada -->
  <ellipse cx="50" cy="60" rx="32" ry="25" fill="currentColor" opacity="0.7"/>
  <!-- Cabeza madre -->
  <circle cx="50" cy="25" r="12" fill="currentColor"/>
  <!-- Patas -->
  <rect x="35" y="75" width="5" height="20" fill="currentColor"/>
  <rect x="60" y="75" width="5" height="20" fill="currentColor"/>
  <!-- Pequeño ternero interno (representación) -->
  <circle cx="50" cy="58" r="8" fill="white" opacity="0.3"/>
</svg>''',
    
    "salud": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Jeringa/Medicamento -->
  <rect x="15" y="35" width="70" height="12" rx="6" fill="currentColor"/>
  <!-- Aguja -->
  <polygon points="80,35 85,40 80,45" fill="currentColor"/>
  <!-- Marcas de dosis -->
  <line x1="25" y1="28" x2="25" y2="32" stroke="currentColor" stroke-width="2"/>
  <line x1="40" y1="28" x2="40" y2="32" stroke="currentColor" stroke-width="2"/>
  <line x1="55" y1="28" x2="55" y2="32" stroke="currentColor" stroke-width="2"/>
  <line x1="70" y1="28" x2="70" y2="32" stroke="currentColor" stroke-width="2"/>
  <!-- Émbolo -->
  <circle cx="20" cy="41" r="5" fill="currentColor"/>
</svg>''',
    
    "potreros": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Pasto/Cerca -->
  <!-- Postes -->
  <rect x="10" y="40" width="6" height="40" fill="currentColor"/>
  <rect x="47" y="40" width="6" height="40" fill="currentColor"/>
  <rect x="84" y="40" width="6" height="40" fill="currentColor"/>
  <!-- Alambre horizontal -->
  <line x1="13" y1="50" x2="87" y2="50" stroke="currentColor" stroke-width="2"/>
  <line x1="13" y1="65" x2="87" y2="65" stroke="currentColor" stroke-width="2"/>
  <!-- Pasto debajo -->
  <path d="M 20 75 Q 22 70 24 75 Q 26 70 28 75 Q 30 70 32 75" stroke="currentColor" stroke-width="2" fill="none"/>
  <path d="M 50 75 Q 52 70 54 75 Q 56 70 58 75 Q 60 70 62 75" stroke="currentColor" stroke-width="2" fill="none"/>
</svg>''',
    
    "tratamientos": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Caja de medicamentos -->
  <rect x="15" y="25" width="70" height="50" rx="5" fill="none" stroke="currentColor" stroke-width="3"/>
  <!-- Cruz/Plus en la caja -->
  <line x1="45" y1="40" x2="55" y2="40" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <line x1="50" y1="35" x2="50" y2="55" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <!-- Pastillas adentro -->
  <circle cx="30" cy="65" r="4" fill="currentColor"/>
  <circle cx="45" cy="68" r="4" fill="currentColor"/>
  <circle cx="70" cy="65" r="4" fill="currentColor"/>
</svg>''',
    
    "leche": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Botella/Vaso de leche -->
  <rect x="25" y="15" width="50" height="65" rx="5" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2"/>
  <!-- Tapa -->
  <rect x="30" y="8" width="40" height="8" rx="2" fill="currentColor" stroke="currentColor" stroke-width="2"/>
  <!-- Línea de leche -->
  <path d="M 28 60 L 72 60" stroke="currentColor" stroke-width="2"/>
  <!-- Gota -->
  <path d="M 50 35 Q 48 45 50 55 Q 52 45 50 35" fill="currentColor"/>
</svg>''',
    
    "ventas": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Dinero/Cartera -->
  <rect x="15" y="30" width="70" height="45" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- Solapa -->
  <path d="M 15 35 L 50 50 L 85 35" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- Moneda/Símbolo $ -->
  <circle cx="50" cy="58" r="12" fill="currentColor" opacity="0.5"/>
  <text x="50" y="65" font-size="20" text-anchor="middle" fill="currentColor">$</text>
</svg>''',
    
    "insumos": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Caja de insumos/Bodega -->
  <rect x="15" y="30" width="70" height="55" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- Tapa -->
  <path d="M 15 30 L 50 15 L 85 30" fill="currentColor" opacity="0.3" stroke="currentColor" stroke-width="2"/>
  <!-- Línea divisoria -->
  <line x1="15" y1="45" x2="85" y2="45" stroke="currentColor" stroke-width="1"/>
  <!-- Items dentro -->
  <rect x="25" y="50" width="12" height="15" fill="currentColor" opacity="0.5"/>
  <rect x="44" y="50" width="12" height="15" fill="currentColor" opacity="0.5"/>
  <rect x="63" y="50" width="12" height="15" fill="currentColor" opacity="0.5"/>
</svg>''',
    
    "herramientas": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Llave inglesa -->
  <rect x="10" y="35" width="50" height="10" rx="5" fill="currentColor"/>
  <!-- Cabezal móvil -->
  <circle cx="65" cy="40" r="12" fill="none" stroke="currentColor" stroke-width="2"/>
  <circle cx="65" cy="40" r="8" fill="currentColor" opacity="0.3"/>
  <!-- Tornillo central -->
  <circle cx="40" cy="40" r="3" fill="currentColor"/>
  <!-- Destornillador superpuesto -->
  <path d="M 45 20 L 50 65" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <path d="M 48 18 L 52 22" stroke="currentColor" stroke-width="2"/>
</svg>''',
    
    "reportes": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Documento/Gráfico -->
  <rect x="15" y="15" width="70" height="70" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- Líneas de texto -->
  <line x1="20" y1="25" x2="80" y2="25" stroke="currentColor" stroke-width="1.5"/>
  <!-- Gráfico de barras -->
  <rect x="20" y="50" width="8" height="20" fill="currentColor" opacity="0.6"/>
  <rect x="35" y="40" width="8" height="30" fill="currentColor" opacity="0.6"/>
  <rect x="50" y="45" width="8" height="25" fill="currentColor" opacity="0.6"/>
  <rect x="65" y="35" width="8" height="35" fill="currentColor" opacity="0.6"/>
  <!-- Eje X -->
  <line x1="18" y1="75" x2="78" y2="75" stroke="currentColor" stroke-width="1.5"/>
</svg>''',
    
    "nomina": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Personas/Equipo -->
  <circle cx="30" cy="25" r="8" fill="currentColor"/>
  <path d="M 22 35 Q 22 40 30 40 Q 38 40 38 35" fill="currentColor"/>
  <circle cx="70" cy="25" r="8" fill="currentColor"/>
  <path d="M 62 35 Q 62 40 70 40 Q 78 40 78 35" fill="currentColor"/>
  <!-- Persona en medio (más grande) -->
  <circle cx="50" cy="35" r="10" fill="currentColor"/>
  <path d="M 40 48 Q 40 55 50 55 Q 60 55 60 48" fill="currentColor"/>
  <!-- Línea que conecta -->
  <line x1="30" y1="38" x2="40" y2="48" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
  <line x1="70" y1="38" x2="60" y2="48" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
</svg>''',
    
    "empleados": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Usuario/Perfil -->
  <circle cx="50" cy="30" r="12" fill="currentColor"/>
  <!-- Cuerpo/Uniforme -->
  <path d="M 38 45 Q 38 50 50 50 Q 62 50 62 45" fill="currentColor"/>
  <!-- Brazos -->
  <line x1="38" y1="47" x2="20" y2="55" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <line x1="62" y1="47" x2="80" y2="55" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <!-- Piernas -->
  <line x1="43" y1="50" x2="40" y2="75" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <line x1="57" y1="50" x2="60" y2="75" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
</svg>''',
    
    "configuracion": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Engranaje -->
  <circle cx="50" cy="50" r="15" fill="none" stroke="currentColor" stroke-width="2"/>
  <circle cx="50" cy="50" r="8" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- Dientes -->
  <rect x="48" y="30" width="4" height="5" fill="currentColor"/>
  <rect x="48" y="65" width="4" height="5" fill="currentColor"/>
  <rect x="65" y="48" width="5" height="4" fill="currentColor"/>
  <rect x="30" y="48" width="5" height="4" fill="currentColor"/>
  <rect x="62" y="38" width="4" height="4" fill="currentColor" transform="rotate(45 64 40)"/>
  <rect x="30" y="58" width="4" height="4" fill="currentColor" transform="rotate(45 32 60)"/>
</svg>''',
    
    "ajustes": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Paleta de colores -->
  <circle cx="50" cy="50" r="30" fill="none" stroke="currentColor" stroke-width="2"/>
  <!-- Colores -->
  <circle cx="50" cy="28" r="6" fill="#FF6B6B"/>
  <circle cx="65" cy="35" r="6" fill="#4ECDC4"/>
  <circle cx="70" cy="50" r="6" fill="#FFD93D"/>
  <circle cx="65" cy="65" r="6" fill="#6BCB77"/>
  <circle cx="50" cy="72" r="6" fill="#4D96FF"/>
  <circle cx="35" cy="65" r="6" fill="#A78BFA"/>
  <circle cx="30" cy="50" r="6" fill="#FF8FAB"/>
  <circle cx="35" cy="35" r="6" fill="#FFB347"/>
  <!-- Centro -->
  <circle cx="50" cy="50" r="3" fill="currentColor"/>
</svg>''',
}

def generar_svgs():
    """Genera archivos SVG para cada módulo"""
    svg_dir = Path(__file__).parent / "svg_icons"
    svg_dir.mkdir(exist_ok=True)
    
    for modulo, svg_content in SVG_ICONS.items():
        filepath = svg_dir / f"{modulo}.svg"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"✅ Creado: {filepath}")

if __name__ == "__main__":
    generar_svgs()
    print("\n✅ Todos los iconos SVG generados correctamente")
