"""
Sistema de Notificaciones para FincaFacil
Gestiona alertas y notificaciones importantes
REFACTOR FASE 7.5: Usa inyección de DbConnectionService en lugar de acceso directo a BD.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database.services import get_db_service

class SistemaNotificaciones:
    """Gestiona las notificaciones del sistema"""
    
    def __init__(self):
        self.notificaciones = []
        self.db_service = get_db_service()
    
    def obtener_todas_notificaciones(self) -> List[Dict[str, Any]]:
        """Obtiene todas las notificaciones activas"""
        self.notificaciones = []
        
        # Obtener cada tipo de notificación
        self.notificaciones.extend(self.verificar_proximos_partos())
        self.notificaciones.extend(self.verificar_bajo_stock())
        self.notificaciones.extend(self.verificar_tratamientos_activos())
        self.notificaciones.extend(self.verificar_mantenimientos_pendientes())
        
        return self.notificaciones
    
    def verificar_proximos_partos(self, dias_anticipacion: int = 7) -> List[Dict[str, Any]]:
        """
        Verifica partos próximos en los próximos N días
        
        Args:
            dias_anticipacion: Días de anticipación para alertar
            
        Returns:
            Lista de notificaciones de partos próximos
        """
        notificaciones = []
        
        try:
            with self.db_service.connection() as conn:
                cursor = conn.cursor()
                
                # Obtener hembras gestantes con parto próximo
                fecha_limite = (datetime.now() + timedelta(days=dias_anticipacion)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT 
                        a.codigo,
                        a.nombre,
                        s.fecha_servicio,
                        DATE(s.fecha_servicio, '+280 days') as fecha_parto_estimada,
                        CAST((JULIANDAY(DATE(s.fecha_servicio, '+280 days')) - JULIANDAY('now')) AS INTEGER) as dias_faltantes
                    FROM servicio s
                    JOIN animal a ON s.id_hembra = a.id
                    WHERE s.estado = 'Gestante'
                      AND DATE(s.fecha_servicio, '+280 days') <= ?
                      AND DATE(s.fecha_servicio, '+280 days') >= DATE('now')
                    ORDER BY fecha_parto_estimada
                """, (fecha_limite,))
                
                partos = cursor.fetchall()
                
                for parto in partos:
                    codigo, nombre, fecha_servicio, fecha_parto, dias_faltantes = parto
                    
                    # Determinar prioridad según días faltantes
                    if dias_faltantes <= 3:
                        prioridad = "alta"
                        icono = "🔴"
                    elif dias_faltantes <= 7:
                        prioridad = "media"
                        icono = "🟡"
                    else:
                        prioridad = "baja"
                        icono = "🟢"
                    
                    notificaciones.append({
                        'tipo': 'parto_proximo',
                        'prioridad': prioridad,
                        'icono': icono,
                        'titulo': f'Parto Próximo: {codigo}',
                        'mensaje': f'{nombre} - Parto en {dias_faltantes} día(s) ({fecha_parto})',
                        'fecha': datetime.now().isoformat(),
                        'datos': {
                            'codigo': codigo,
                            'nombre': nombre,
                            'fecha_parto_estimada': fecha_parto,
                            'dias_faltantes': dias_faltantes
                        }
                    })
        
        except Exception as e:
            print(f"Error verificando próximos partos: {e}")
        
        return notificaciones
    
    def verificar_bajo_stock(self, porcentaje_alerta: int = 20) -> List[Dict[str, Any]]:
        """
        Verifica insumos con stock bajo
        
        Args:
            porcentaje_alerta: Porcentaje de stock mínimo para alertar
            
        Returns:
            Lista de notificaciones de bajo stock
        """
        notificaciones = []
        
        try:
            with self.db_service.connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existe la tabla insumos
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='insumos'
                """)
                
                if not cursor.fetchone():
                    return notificaciones
                
                # Obtener insumos con stock bajo
                cursor.execute("""
                    SELECT 
                        id,
                        nombre,
                        categoria,
                        stock_actual,
                        stock_minimo,
                        stock_maximo,
                        unidad_medida,
                        CAST((stock_actual * 100.0 / stock_minimo) AS INTEGER) as porcentaje_stock
                    FROM insumos
                    WHERE activo = 1
                      AND stock_actual <= stock_minimo
                    ORDER BY porcentaje_stock
                """)
                
                insumos = cursor.fetchall()
                
                for insumo in insumos:
                    id_insumo, nombre, categoria, stock_actual, stock_minimo, stock_maximo, unidad, porcentaje = insumo
                    
                    # Determinar prioridad
                    if stock_actual == 0:
                        prioridad = "alta"
                        icono = "🔴"
                        estado = "SIN STOCK"
                    elif porcentaje <= 50:
                        prioridad = "alta"
                        icono = "🔴"
                        estado = "CRÍTICO"
                    elif porcentaje <= 80:
                        prioridad = "media"
                        icono = "🟡"
                        estado = "BAJO"
                    else:
                        prioridad = "baja"
                        icono = "🟠"
                        estado = "Mínimo"
                    
                    notificaciones.append({
                        'tipo': 'bajo_stock',
                        'prioridad': prioridad,
                        'icono': icono,
                        'titulo': f'Stock {estado}: {nombre}',
                        'mensaje': f'{categoria} - Stock: {stock_actual}/{stock_minimo} {unidad}',
                        'fecha': datetime.now().isoformat(),
                        'datos': {
                            'id': id_insumo,
                            'nombre': nombre,
                            'categoria': categoria,
                            'stock_actual': stock_actual,
                            'stock_minimo': stock_minimo,
                            'porcentaje': porcentaje
                        }
                    })
        
        except Exception as e:
            print(f"Error verificando bajo stock: {e}")
        
        return notificaciones
    
    def verificar_tratamientos_activos(self) -> List[Dict[str, Any]]:
        """Verifica tratamientos que finalizan pronto"""
        notificaciones = []
        
        try:
            with self.db_service.connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existe la tabla tratamientos
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='tratamiento'
                """)
                
                if not cursor.fetchone():
                    return notificaciones
                
                # Obtener tratamientos que finalizan en los próximos 3 días
                fecha_limite = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT 
                        t.id,
                        a.codigo,
                        a.nombre as nombre_animal,
                        t.producto,
                        t.fecha_fin,
                        CAST((JULIANDAY(t.fecha_fin) - JULIANDAY('now')) AS INTEGER) as dias_restantes
                    FROM tratamiento t
                    JOIN animal a ON t.id_animal = a.id
                    WHERE t.estado = 'Activo'
                      AND t.fecha_fin <= ?
                      AND t.fecha_fin >= DATE('now')
                    ORDER BY t.fecha_fin
                """, (fecha_limite,))
                
                tratamientos = cursor.fetchall()
                
                for trat in tratamientos:
                    id_trat, codigo, nombre, producto, fecha_fin, dias_restantes = trat
                    
                    if dias_restantes <= 1:
                        prioridad = "media"
                        icono = "💊"
                    else:
                        prioridad = "baja"
                        icono = "💉"
                    
                    notificaciones.append({
                        'tipo': 'tratamiento_finalizando',
                        'prioridad': prioridad,
                        'icono': icono,
                        'titulo': f'Tratamiento finaliza: {codigo}',
                        'mensaje': f'{nombre} - {producto} termina en {dias_restantes} día(s)',
                        'fecha': datetime.now().isoformat(),
                        'datos': {
                            'id': id_trat,
                            'codigo': codigo,
                            'producto': producto,
                            'fecha_fin': fecha_fin,
                            'dias_restantes': dias_restantes
                        }
                    })
        
        except Exception as e:
            print(f"Error verificando tratamientos: {e}")
        
        return notificaciones
    
    def verificar_mantenimientos_pendientes(self) -> List[Dict[str, Any]]:
        """Verifica mantenimientos de herramientas pendientes"""
        notificaciones = []
        
        try:
            with self.db_service.connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existe la tabla mantenimientos
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='mantenimiento'
                """)
                
                if not cursor.fetchone():
                    return notificaciones
                
                # Obtener mantenimientos próximos
                fecha_limite = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT 
                        m.id,
                        h.nombre as herramienta,
                        m.tipo_mantenimiento,
                        m.fecha_proximo_mantenimiento,
                        CAST((JULIANDAY(m.fecha_proximo_mantenimiento) - JULIANDAY('now')) AS INTEGER) as dias_restantes
                    FROM mantenimiento m
                    JOIN herramienta h ON m.id_herramienta = h.id
                    WHERE m.fecha_proximo_mantenimiento <= ?
                      AND m.fecha_proximo_mantenimiento >= DATE('now')
                    ORDER BY m.fecha_proximo_mantenimiento
                """, (fecha_limite,))
                
                mantenimientos = cursor.fetchall()
                
                for mant in mantenimientos:
                    id_mant, herramienta, tipo, fecha_proxima, dias_restantes = mant
                    
                    if dias_restantes <= 2:
                        prioridad = "media"
                        icono = "🔧"
                    else:
                        prioridad = "baja"
                        icono = "🛠️"
                    
                    notificaciones.append({
                        'tipo': 'mantenimiento_pendiente',
                        'prioridad': prioridad,
                        'icono': icono,
                        'titulo': f'Mantenimiento: {herramienta}',
                        'mensaje': f'{tipo} en {dias_restantes} día(s) ({fecha_proxima})',
                        'fecha': datetime.now().isoformat(),
                        'datos': {
                            'id': id_mant,
                            'herramienta': herramienta,
                            'tipo': tipo,
                            'fecha_proxima': fecha_proxima,
                            'dias_restantes': dias_restantes
                        }
                    })
        
        except Exception as e:
            print(f"Error verificando mantenimientos: {e}")
        
        return notificaciones
    
    def contar_por_prioridad(self) -> Dict[str, int]:
        """Cuenta notificaciones por nivel de prioridad"""
        conteo = {'alta': 0, 'media': 0, 'baja': 0}
        
        for notif in self.notificaciones:
            prioridad = notif.get('prioridad', 'baja')
            conteo[prioridad] = conteo.get(prioridad, 0) + 1
        
        return conteo
    
    def obtener_resumen(self) -> str:
        """Genera un resumen textual de las notificaciones"""
        if not self.notificaciones:
            return "✅ No hay notificaciones pendientes"
        
        conteo = self.contar_por_prioridad()
        total = len(self.notificaciones)
        
        resumen = f"📢 {total} notificacion{'es' if total > 1 else ''}"
        
        if conteo['alta'] > 0:
            resumen += f" | 🔴 {conteo['alta']} urgente{'s' if conteo['alta'] > 1 else ''}"
        if conteo['media'] > 0:
            resumen += f" | 🟡 {conteo['media']} importante{'s' if conteo['media'] > 1 else ''}"
        if conteo['baja'] > 0:
            resumen += f" | 🟢 {conteo['baja']} info"
        
        return resumen


def obtener_notificaciones() -> List[Dict[str, Any]]:
    """Función de conveniencia para obtener todas las notificaciones"""
    sistema = SistemaNotificaciones()
    return sistema.obtener_todas_notificaciones()
