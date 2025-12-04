"""
Sistema de alertas para módulos críticos de FincaFacil
Permite generar alertas automáticas para reproducción, salud y tratamientos
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from database.database import get_db_connection
import logging

logger = logging.getLogger("SistemaAlertas")


class Alerta:
    """Representa una alerta del sistema"""
    
    def __init__(self, tipo: str, prioridad: str, titulo: str, descripcion: str, 
                 animal_id: Optional[int] = None, fecha_limite: Optional[str] = None):
        """
        Inicializa una alerta
        
        Args:
            tipo: Tipo de alerta (reproduccion, salud, tratamiento, etc.)
            prioridad: Prioridad (alta, media, baja)
            titulo: Título descriptivo
            descripcion: Descripción detallada
            animal_id: ID del animal relacionado (opcional)
            fecha_limite: Fecha límite de la alerta (opcional)
        """
        self.tipo = tipo
        self.prioridad = prioridad
        self.titulo = titulo
        self.descripcion = descripcion
        self.animal_id = animal_id
        self.fecha_limite = fecha_limite
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la alerta a diccionario"""
        return {
            "tipo": self.tipo,
            "prioridad": self.prioridad,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "animal_id": self.animal_id,
            "fecha_limite": self.fecha_limite,
            "fecha_creacion": self.fecha_creacion
        }


class SistemaAlertas:
    """Sistema centralizado de alertas"""
    
    def __init__(self):
        """Inicializa el sistema de alertas"""
        self.alertas: List[Alerta] = []
    
    def generar_alertas_reproduccion(self) -> List[Alerta]:
        """
        Genera alertas relacionadas con reproducción
        
        Returns:
            Lista de alertas generadas
        """
        alertas = []
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Alertas de próximos partos (dentro de 7 días)
                cursor.execute("""
                    SELECT a.id, a.codigo, a.nombre, s.fecha_servicio,
                           DATE(s.fecha_servicio, '+280 days') as fecha_parto_estimada
                    FROM animal a
                    JOIN servicio s ON a.id = s.id_animal
                    WHERE s.resultado = 'Gestante' 
                    AND DATE(s.fecha_servicio, '+280 days') BETWEEN DATE('now') AND DATE('now', '+7 days')
                    ORDER BY fecha_parto_estimada
                """)
                
                for row in cursor.fetchall():
                    animal_id, codigo, nombre, fecha_servicio, fecha_parto = row
                    animal_nombre = nombre or codigo
                    
                    alerta = Alerta(
                        tipo="reproduccion",
                        prioridad="alta",
                        titulo=f"Próximo parto: {animal_nombre}",
                        descripcion=f"Animal {animal_nombre} tiene parto estimado el {fecha_parto}",
                        animal_id=animal_id,
                        fecha_limite=fecha_parto
                    )
                    alertas.append(alerta)
                
                # Alertas de partos vencidos (más de 280 días y aún marcados como gestantes)
                cursor.execute("""
                    SELECT a.id, a.codigo, a.nombre, s.fecha_servicio,
                           DATE(s.fecha_servicio, '+280 days') as fecha_parto_estimada
                    FROM animal a
                    JOIN servicio s ON a.id = s.id_animal
                    WHERE s.resultado = 'Gestante' 
                    AND DATE(s.fecha_servicio, '+280 days') < DATE('now')
                    ORDER BY fecha_parto_estimada
                """)
                
                for row in cursor.fetchall():
                    animal_id, codigo, nombre, fecha_servicio, fecha_parto = row
                    animal_nombre = nombre or codigo
                    
                    alerta = Alerta(
                        tipo="reproduccion",
                        prioridad="alta",
                        titulo=f"Parto vencido: {animal_nombre}",
                        descripcion=f"Animal {animal_nombre} tiene parto vencido desde {fecha_parto}. Verificar estado.",
                        animal_id=animal_id,
                        fecha_limite=fecha_parto
                    )
                    alertas.append(alerta)
                
                logger.info(f"Generadas {len(alertas)} alertas de reproducción")
                
        except Exception as e:
            logger.error(f"Error generando alertas de reproducción: {e}")
        
        return alertas
    
    def generar_alertas_salud(self) -> List[Alerta]:
        """
        Genera alertas relacionadas con salud
        
        Returns:
            Lista de alertas generadas
        """
        alertas = []
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Alertas de animales enfermos sin resolución
                cursor.execute("""
                    SELECT a.id, a.codigo, a.nombre, d.fecha_diagnostico, d.diagnostico, d.estado
                    FROM animal a
                    JOIN diagnostico d ON a.id = d.id_animal
                    WHERE d.estado IN ('En Tratamiento', 'Crítico')
                    AND DATE(d.fecha_diagnostico) < DATE('now', '-7 days')
                    ORDER BY d.fecha_diagnostico
                """)
                
                for row in cursor.fetchall():
                    animal_id, codigo, nombre, fecha_diag, diagnostico, estado = row
                    animal_nombre = nombre or codigo
                    
                    dias_enfermo = (datetime.now() - datetime.strptime(fecha_diag, "%Y-%m-%d")).days
                    
                    alerta = Alerta(
                        tipo="salud",
                        prioridad="alta" if estado == "Crítico" else "media",
                        titulo=f"Enfermo prolongado: {animal_nombre}",
                        descripcion=f"Animal {animal_nombre} con {diagnostico} desde hace {dias_enfermo} días. Estado: {estado}",
                        animal_id=animal_id,
                        fecha_limite=None
                    )
                    alertas.append(alerta)
                
                logger.info(f"Generadas {len(alertas)} alertas de salud")
                
        except Exception as e:
            logger.error(f"Error generando alertas de salud: {e}")
        
        return alertas
    
    def generar_alertas_tratamientos(self) -> List[Alerta]:
        """
        Genera alertas relacionadas con tratamientos
        
        Returns:
            Lista de alertas generadas
        """
        alertas = []
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Alertas de próximos tratamientos (hoy y mañana)
                cursor.execute("""
                    SELECT a.id, a.codigo, a.nombre, t.fecha_proxima_aplicacion, t.medicamento
                    FROM animal a
                    JOIN tratamiento t ON a.id = t.id_animal
                    WHERE t.fecha_proxima_aplicacion BETWEEN DATE('now') AND DATE('now', '+1 day')
                    AND t.estado = 'Activo'
                    ORDER BY t.fecha_proxima_aplicacion
                """)
                
                for row in cursor.fetchall():
                    animal_id, codigo, nombre, fecha_prox, medicamento = row
                    animal_nombre = nombre or codigo
                    
                    alerta = Alerta(
                        tipo="tratamiento",
                        prioridad="alta",
                        titulo=f"Tratamiento pendiente: {animal_nombre}",
                        descripcion=f"Animal {animal_nombre} tiene aplicación de {medicamento} programada para {fecha_prox}",
                        animal_id=animal_id,
                        fecha_limite=fecha_prox
                    )
                    alertas.append(alerta)
                
                # Alertas de tratamientos vencidos
                cursor.execute("""
                    SELECT a.id, a.codigo, a.nombre, t.fecha_proxima_aplicacion, t.medicamento
                    FROM animal a
                    JOIN tratamiento t ON a.id = t.id_animal
                    WHERE t.fecha_proxima_aplicacion < DATE('now')
                    AND t.estado = 'Activo'
                    ORDER BY t.fecha_proxima_aplicacion
                """)
                
                for row in cursor.fetchall():
                    animal_id, codigo, nombre, fecha_prox, medicamento = row
                    animal_nombre = nombre or codigo
                    
                    alerta = Alerta(
                        tipo="tratamiento",
                        prioridad="alta",
                        titulo=f"Tratamiento vencido: {animal_nombre}",
                        descripcion=f"Animal {animal_nombre} tiene aplicación vencida de {medicamento} desde {fecha_prox}",
                        animal_id=animal_id,
                        fecha_limite=fecha_prox
                    )
                    alertas.append(alerta)
                
                logger.info(f"Generadas {len(alertas)} alertas de tratamientos")
                
        except Exception as e:
            logger.error(f"Error generando alertas de tratamientos: {e}")
        
        return alertas
    
    def obtener_todas_alertas(self) -> List[Alerta]:
        """
        Obtiene todas las alertas del sistema
        
        Returns:
            Lista de todas las alertas
        """
        todas_alertas = []
        
        todas_alertas.extend(self.generar_alertas_reproduccion())
        todas_alertas.extend(self.generar_alertas_salud())
        todas_alertas.extend(self.generar_alertas_tratamientos())
        
        # Ordenar por prioridad (alta primero) y luego por fecha límite
        prioridad_orden = {"alta": 0, "media": 1, "baja": 2}
        todas_alertas.sort(key=lambda x: (prioridad_orden.get(x.prioridad, 3), x.fecha_limite or "9999"))
        
        self.alertas = todas_alertas
        logger.info(f"Total de alertas generadas: {len(todas_alertas)}")
        
        return todas_alertas
    
    def obtener_alertas_por_tipo(self, tipo: str) -> List[Alerta]:
        """
        Obtiene alertas filtradas por tipo
        
        Args:
            tipo: Tipo de alerta a filtrar
            
        Returns:
            Lista de alertas del tipo especificado
        """
        return [a for a in self.alertas if a.tipo == tipo]
    
    def obtener_alertas_por_prioridad(self, prioridad: str) -> List[Alerta]:
        """
        Obtiene alertas filtradas por prioridad
        
        Args:
            prioridad: Prioridad a filtrar (alta, media, baja)
            
        Returns:
            Lista de alertas con la prioridad especificada
        """
        return [a for a in self.alertas if a.prioridad == prioridad]


# Instancia global del sistema de alertas
_sistema_alertas: Optional[SistemaAlertas] = None


def get_sistema_alertas() -> SistemaAlertas:
    """
    Obtiene la instancia global del sistema de alertas
    
    Returns:
        Instancia de SistemaAlertas
    """
    global _sistema_alertas
    if _sistema_alertas is None:
        _sistema_alertas = SistemaAlertas()
    return _sistema_alertas
