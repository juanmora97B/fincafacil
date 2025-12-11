"""
Sistema de iconos profesionales para FincaFacil.

Objetivo: iconos más limpios y consistentes (estilo "fluent"), con degradados
suaves, contorno sutil y glifos legibles (MDL2 si existe, si no, iniciales o
emoji). Se mantiene compatibilidad con el estilo anterior mediante el parámetro
"estilo" (moderno/degradado/plano).
"""

import os
import io
from pathlib import Path
from typing import Optional, Dict, Tuple
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

# Directorio de caché de iconos
ICONS_CACHE_DIR = Path(__file__).parent.parent / "assets" / "icons_cache"
ICONS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Paleta de colores profesionales (dobles tonos para degradado)
COLORS = {
    "dashboard": ("#0F6CBD", "#3FA9F5"),
    "animales": ("#2E7D32", "#52C41A"),
    "reproduccion": ("#C2185B", "#F06292"),
    "salud": ("#C62828", "#EF5350"),
    "potreros": ("#2F7D32", "#5FB760"),
    "tratamientos": ("#7B1FA2", "#AE7AE7"),
    "ventas": ("#EF6C00", "#FF9800"),
    "insumos": ("#0277BD", "#29B6F6"),
    "herramientas": ("#4E585F", "#90A4AE"),
    "reportes": ("#5E35B1", "#9575CD"),
    "nomina": ("#00695C", "#26A69A"),
    "empleados": ("#00838F", "#00ACC1"),
    "configuracion": ("#455A64", "#90A4AE"),
    "ajustes": ("#37474F", "#78909C"),
    "leche": ("#F57F17", "#FBC02D"),
}

# Mapeo de símbolos profesionales
ICON_SYMBOLS = {
    "dashboard": "📊",
    "animales": "🐄",
    "reproduccion": "🤰",
    "salud": "🏥",
    "potreros": "🌿",
    "tratamientos": "💊",
    "ventas": "💰",
    "insumos": "📦",
    "herramientas": "🔧",
    "reportes": "📋",
    "nomina": "👥",
    "empleados": "👨‍💼",
    "configuracion": "⚙️",
    "ajustes": "🎨",
    "leche": "🥛",
}

# Glifos MDL2 (Segoe MDL2 Assets). Si no está disponible la fuente, se usa fallback.
GLYPHS_MDL2 = {
    "dashboard": "\uE80F",      # ViewDashboard
    "animales": "\uE7C3",       # Contact
    "reproduccion": "\uE8D0",   # FavoriteStar
    "salud": "\uE95E",          # Health
    "potreros": "\uE811",       # Map
    "tratamientos": "\uE90A",   # Pill
    "ventas": "\uE7BF",         # Shop
    "insumos": "\uE8D1",        # DownloadBox
    "herramientas": "\uE75F",   # Repair
    "reportes": "\uE9F9",       # ReportDocument
    "nomina": "\uE716",         # People
    "empleados": "\uE77B",      # ContactInfo
    "configuracion": "\uE713",  # Settings
    "ajustes": "\uE15E",        # Edit
    "leche": "\uEA86",          # Drink
}


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _obtener_glyph(modulo: str) -> Tuple[str, Optional[str]]:
    """Devuelve (glyph, font_name) con prioridad a MDL2. Si no hay glifo, usa emoji/símbolo o iniciales."""
    glyph = GLYPHS_MDL2.get(modulo)
    if glyph:
        return glyph, "segmdl2.ttf"  # Fuente MDL2 en Windows
    if modulo in ICON_SYMBOLS:
        return ICON_SYMBOLS[modulo], None
    # Fallback: iniciales del módulo
    initials = modulo[:2].upper()
    return initials, None


def generar_icono_simple(
    nombre: str,
    texto: str,
    color_bg: str,
    color_fg: str = "#FFFFFF",
    size: int = 128,
    estilo: str = "fluent"
) -> Image.Image:
    """Genera un icono profesional.

    Estilos:
    - "fluent" (nuevo defecto): degradado vertical, halo y aro interior.
    - "moderno": estilo previo con fondo redondeado.
    - "degradado" / "plano": mantienen compatibilidad.
    """
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    rgb_bg = _hex_to_rgb(color_bg)
    rgb_fg = _hex_to_rgb(color_fg)

    if estilo == "fluent":
        # Relleno con color sólido - sin degradados
        draw.rectangle([0, 0, size - 1, size - 1], fill=rgb_bg)

    elif estilo == "moderno":
        # Estilo moderno mejorado: sombra + degradado suave + borde definido
        margin = 6
        bbox = [margin, margin, size - margin, size - margin]
        radius = size // 5
        
        # Sombra con blur suave (múltiples capas)
        sombra_bbox = [margin + 3, margin + 3, size - margin + 3, size - margin + 3]
        draw.rounded_rectangle(sombra_bbox, radius=radius, fill=(*rgb_bg, 40))
        sombra_bbox = [margin + 1, margin + 1, size - margin + 1, size - margin + 1]
        draw.rounded_rectangle(sombra_bbox, radius=radius, fill=(*rgb_bg, 70))
        
        # Degradado vertical suave
        r0, g0, b0 = rgb_bg
        r1 = min(255, int(r0 * 1.12))
        g1 = min(255, int(g0 * 1.12))
        b1 = min(255, int(b0 * 1.12))
        for i, y in enumerate(range(margin, size - margin)):
            t = (y - margin) / max(1, (size - 2 * margin))
            r = int(r0 + (r1 - r0) * t * 0.6)
            g = int(g0 + (g1 - g0) * t * 0.6)
            b = int(b0 + (b1 - b0) * t * 0.6)
            draw.line([(margin, y), (size - margin, y)], fill=(r, g, b, 255))
        
        # Borde redondeado con brillo
        draw.rounded_rectangle(bbox, radius=radius, outline=(*rgb_fg, 140), width=2)

    elif estilo == "degradado":
        for y in range(size):
            ratio = y / size
            r = int(rgb_bg[0] + (255 - rgb_bg[0]) * ratio * 0.1)
            g = int(rgb_bg[1] + (255 - rgb_bg[1]) * ratio * 0.1)
            b = int(rgb_bg[2] + (255 - rgb_bg[2]) * ratio * 0.1)
            draw.line([(0, y), (size, y)], fill=(r, g, b))
        draw.rectangle([0, 0, size - 1, size - 1], outline=rgb_bg, width=2)

    else:  # plano
        draw.rectangle([0, 0, size - 1, size - 1], fill=rgb_bg)

    # Dibujar texto/glifo centrado
    try:
        font_size = int(size * 0.5)
        font = None

        # Seleccionar fuente
        try:
            font = ImageFont.truetype("segmdl2.ttf", font_size)
        except Exception:
            try:
                font = ImageFont.truetype("Segoe UI Semibold.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), texto, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        draw.text((x, y), texto, font=font, fill=rgb_fg)
    except Exception as e:
        print(f"Error dibujando texto en icono: {e}")

    return img


def obtener_icono_ctk(modulo, size=40, estilo="fluent"):
    """
    Obtiene un icono CTkImage para un módulo específico.
    Prioridad: animado (assets/animated/*.png), luego personalizado (assets/flaticon), luego emoji/fluent.
    """

    # 1) Intentar icono animado si existe (múltiples frames)
    try:
        animated_dir = Path(__file__).parent.parent / "assets" / "animated"
        animated_dir.mkdir(parents=True, exist_ok=True)
        
        # Buscar frames del módulo (ej. salud_0.png, salud_1.png, etc)
        frame_files = sorted(animated_dir.glob(f"{modulo}_*.png"))
        if frame_files:
            frames = []
            for frame_path in frame_files:
                try:
                    raw = Image.open(frame_path).convert("RGBA")
                    target = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    margin = max(2, size // 8)
                    max_side = max(1, size - 2 * margin)
                    raw.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                    offset = ((size - raw.width) // 2, (size - raw.height) // 2)
                    target.paste(raw, offset, raw)
                    frames.append(target)
                except Exception:
                    pass
            
            if frames:
                # Retornar primer frame; la animación se manejaría con after() en el botón si se necesita
                return ctk.CTkImage(light_image=frames[0], dark_image=frames[0], size=(size, size))
    except Exception:
        pass

    # 2) Intentar icono personalizado (ej. flaticon) si existe
    try:
        custom_dir = Path(__file__).parent.parent / "assets" / "flaticon"
        custom_dir.mkdir(parents=True, exist_ok=True)
        custom_png = custom_dir / f"{modulo}.png"

        if custom_png.exists():
            try:
                # Contener y centrar el icono con un pequeño margen para que no se corte
                raw = Image.open(custom_png).convert("RGBA")
                target = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                margin = max(2, size // 8)  # ~12.5% de margen
                max_side = max(1, size - 2 * margin)
                raw.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                offset = ((size - raw.width) // 2, (size - raw.height) // 2)
                target.paste(raw, offset, raw)
                return ctk.CTkImage(light_image=target, dark_image=target, size=(size, size))
            except Exception:
                pass
    except Exception:
        pass

    # 3) Fallback al generador actual (emoji/fluent)
    return generar_icono_simple(modulo, size, estilo)


def obtener_frames_animados(modulo, size=40):
    """
    Obtiene lista de frames animados para un módulo (usado por animación en botones).
    Retorna lista de CTkImage o None si no hay animación.
    """
    try:
        animated_dir = Path(__file__).parent.parent / "assets" / "animated"
        frame_files = sorted(animated_dir.glob(f"{modulo}_*.png"))
        
        if not frame_files:
            return None
        
        frames = []
        for frame_path in frame_files:
            try:
                raw = Image.open(frame_path).convert("RGBA")
                target = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                margin = max(2, size // 8)
                max_side = max(1, size - 2 * margin)
                raw.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                offset = ((size - raw.width) // 2, (size - raw.height) // 2)
                target.paste(raw, offset, raw)
                frames.append(ctk.CTkImage(light_image=target, dark_image=target, size=(size, size)))
            except Exception:
                pass
        
        return frames if frames else None
    except Exception:
        return None


def obtener_icono_emoji_mejorado(
    emoji: str,
    color: str = "#1976D2",
    size: int = 45
) -> ctk.CTkImage:
    """
    Crea un icono mejorado alrededor de un emoji
    
    Args:
        emoji: Emoji a usar
        color: Color de fondo
        size: Tamaño del icono
    
    Returns:
        customtkinter.CTkImage: Icono con fondo
    """
    try:
        img = generar_icono_simple(
            f"emoji_{emoji}_{color}",
            emoji,
            color,
            "#FFFFFF",
            size=size * 2,
            estilo="moderno"
        )
        
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    except Exception as e:
        print(f"Error creando icono emoji: {e}")
        fallback = Image.new('RGBA', (size, size), (200, 200, 200, 100))
        return ctk.CTkImage(light_image=fallback, dark_image=fallback, size=(size, size))


# Funciones de conveniencia para UI
def crear_botones_iconos_mejorados(parent, config: Dict) -> Dict[str, ctk.CTkButton]:
    """
    Crea botones con iconos mejorados
    
    Args:
        parent: Widget padre
        config: Diccionario con configuración de botones
        
    Returns:
        Dict con referencia a los botones creados
    
    Ejemplo:
        config = {
            "animales": {"text": "🐄 Animales", "callback": func1, "size": 45},
            "ventas": {"text": "💰 Ventas", "callback": func2, "size": 45}
        }
        botones = crear_botones_iconos_mejorados(parent, config)
    """
    botones = {}
    
    for modulo, opciones in config.items():
        try:
            color_bg, color_hover = COLORS.get(modulo, ("#1976D2", "#42A5F5"))
            size = opciones.get("size", 45)
            
            # Crear icono
            icono = obtener_icono_ctk(modulo, size=size, estilo="moderno")
            
            # Crear botón
            btn = ctk.CTkButton(
                parent,
                text=opciones.get("text", ""),
                image=icono,
                width=opciones.get("width", 190),
                height=opciones.get("height", 45),
                font=("Segoe UI", 13, "bold"),
                fg_color=color_bg,
                hover_color=color_hover,
                corner_radius=12,
                border_width=0,
                command=opciones.get("callback")
            )
            
            botones[modulo] = btn
        
        except Exception as e:
            print(f"Error creando botón para {modulo}: {e}")
    
    return botones


__all__ = [
    "obtener_icono_ctk",
    "obtener_icono_emoji_mejorado",
    "generar_icono_simple",
    "crear_botones_iconos_mejorados",
    "COLORS",
    "ICON_SYMBOLS",
]
