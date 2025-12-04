"""
Constantes del sistema FincaFacil
"""

# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================
APP_NAME = "FincaFácil"
APP_VERSION = "2.0.0"
APP_TITLE = f"{APP_NAME} 🐄 - Gestión Ganadera Profesional"

# ============================================
# CONFIGURACIÓN DE UI
# ============================================
UI_APPEARANCE_MODE = "light"
UI_COLOR_THEME = "blue"
UI_GEOMETRY = "1400x820"

# ============================================
# TEMAS Y COLORES
# ============================================
COLORS = {
    "primary": "#0066cc",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40",
}

# ============================================
# ICONOS
# ============================================
ICONS = {
    "dashboard": "📊",
    "animales": "🐄",
    "insumos": "📦",
    "herramientas": "🔧",
    "ventas": "💰",
    "reportes": "📈",
    "nomina": "👥",
    "configuracion": "⚙️",
}

# ============================================
# VALIDACIONES
# ============================================
WEIGHT_MIN = 0
WEIGHT_MAX = 2000
WEIGHT_BIRTH_MIN = 15
WEIGHT_BIRTH_MAX = 60
WEIGHT_PURCHASE_MIN = 50
WEIGHT_PURCHASE_MAX = 1000

# ============================================
# BASES DE DATOS
# ============================================
DB_TIMEOUT = 30
DB_JOURNAL_MODE = "WAL"
DB_PRAGMA_FOREIGN_KEYS = True

# ============================================
# LOGGING
# ============================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5
