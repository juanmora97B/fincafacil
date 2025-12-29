"""
FASE 15: INCIDENT MANAGEMENT SERVICE
Sistema de gestión de incidentes y continuidad operativa

Responsabilidades:
- Registrar incidentes técnicos y operativos
- Clasificar por tipo (DATA, UX, PERFORMANCE, ERROR)
- Asociar a snapshots y métricas
- Timeline de resolución
- Knowledge base de soluciones
- Garantizar continuidad sin desarrollador
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid


class TipoIncidente(Enum):
    """Tipos de incidentes del sistema"""
    DATA = "data"                    # Problemas de datos/integridad
    UX = "ux"                        # Problemas de experiencia de usuario
    PERFORMANCE = "performance"      # Problemas de rendimiento
    ERROR = "error"                  # Errores técnicos/crashes
    CONFIGURACION = "configuracion"  # Problemas de configuración
    INTEGRACION = "integracion"      # Problemas de integración


class SeveridadIncidente(Enum):
    """Severidad del incidente"""
    BAJA = "baja"          # No impacta operación
    MEDIA = "media"        # Impacto moderado
    ALTA = "alta"          # Impacto significativo
    CRITICA = "critica"    # Sistema inoperable


class EstadoIncidente(Enum):
    """Estado del incidente"""
    ABIERTO = "abierto"
    EN_INVESTIGACION = "en_investigacion"
    EN_RESOLUCION = "en_resolucion"
    RESUELTO = "resuelto"
    CERRADO = "cerrado"


@dataclass
class Incidente:
    """Registro de un incidente del sistema"""
    titulo: str
    descripcion: str
    tipo: TipoIncidente
    severidad: SeveridadIncidente
    modulo_afectado: str
    usuario_reporta: Optional[str] = None
    timestamp_inicio: datetime = field(default_factory=datetime.now)
    estado: EstadoIncidente = EstadoIncidente.ABIERTO
    id_incidente: str = field(init=False)
    
    # Contexto técnico
    datos_contexto: Dict[str, Any] = field(default_factory=dict)
    snapshot_id: Optional[str] = None
    metrica_relacionada: Optional[str] = None
    
    # Timeline de resolución
    timestamp_resuelto: Optional[datetime] = None
    tiempo_resolucion_min: Optional[int] = None
    
    # Solución
    solucion_aplicada: Optional[str] = None
    pasos_resolucion: List[str] = field(default_factory=list)
    
    # Knowledge base
    se_puede_prevenir: bool = False
    causa_raiz: Optional[str] = None
    
    def __post_init__(self):
        # Generar ID único: INC-YYYYMMDD-HHMMSS-UUID corto
        timestamp = self.timestamp_inicio.strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]  # Primeros 8 caracteres del UUID
        self.id_incidente = f"INC-{timestamp}-{unique_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_incidente": self.id_incidente,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "tipo": self.tipo.value,
            "severidad": self.severidad.value,
            "estado": self.estado.value,
            "modulo_afectado": self.modulo_afectado,
            "usuario_reporta": self.usuario_reporta,
            "timestamp_inicio": self.timestamp_inicio.isoformat(),
            "timestamp_resuelto": self.timestamp_resuelto.isoformat() if self.timestamp_resuelto else None,
            "tiempo_resolucion_min": self.tiempo_resolucion_min,
            "datos_contexto": self.datos_contexto,
            "snapshot_id": self.snapshot_id,
            "metrica_relacionada": self.metrica_relacionada,
            "solucion_aplicada": self.solucion_aplicada,
            "pasos_resolucion": self.pasos_resolucion,
            "se_puede_prevenir": self.se_puede_prevenir,
            "causa_raiz": self.causa_raiz
        }


@dataclass
class SolucionKnowledgeBase:
    """Solución documentada en knowledge base"""
    problema: str
    sintomas: List[str]
    causa: str
    solucion: str
    pasos: List[str]
    prevencion: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    incidentes_relacionados: List[str] = field(default_factory=list)
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "problema": self.problema,
            "sintomas": self.sintomas,
            "causa": self.causa,
            "solucion": self.solucion,
            "pasos": self.pasos,
            "prevencion": self.prevencion,
            "tags": self.tags,
            "incidentes_relacionados": self.incidentes_relacionados,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }


@dataclass
class ChecklistOperativo:
    """Checklist operativo semanal/mensual"""
    nombre: str
    frecuencia: str  # "semanal", "mensual", "trimestral"
    items: List[Dict[str, Any]]  # {"tarea": str, "completado": bool, "fecha": str}
    ultimo_ejecutado: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "frecuencia": self.frecuencia,
            "items": self.items,
            "ultimo_ejecutado": self.ultimo_ejecutado.isoformat() if self.ultimo_ejecutado else None
        }


class IncidentManagementService:
    """
    Servicio de gestión de incidentes y continuidad operativa
    """
    
    def __init__(self):
        self.incidentes: Dict[str, Incidente] = {}  # id -> incidente
        self.knowledge_base: List[SolucionKnowledgeBase] = []
        self.checklists: List[ChecklistOperativo] = []
        
        # Inicializar knowledge base con soluciones comunes
        self._inicializar_knowledge_base()
        
        # Inicializar checklists operativos
        self._inicializar_checklists()
    
    def _inicializar_knowledge_base(self):
        """Inicializa knowledge base con soluciones comunes"""
        soluciones_base = [
            SolucionKnowledgeBase(
                problema="Base de datos bloqueada",
                sintomas=["Error: database is locked", "Operaciones lentas", "Timeouts"],
                causa="Múltiples escrituras concurrentes en SQLite",
                solucion="Reiniciar aplicación y reducir concurrencia",
                pasos=[
                    "1. Cerrar todas las ventanas de FincaFácil",
                    "2. Esperar 30 segundos",
                    "3. Reabrir aplicación",
                    "4. Si persiste: Verificar que no haya múltiples instancias abiertas"
                ],
                prevencion="No abrir múltiples instancias. Considerar migración a PostgreSQL.",
                tags=["database", "sqlite", "performance"]
            ),
            SolucionKnowledgeBase(
                problema="Datos de producción faltantes",
                sintomas=["Gráfico sin datos", "Reporte vacío", "0 registros"],
                causa="Filtros demasiado restrictivos o período sin datos",
                solucion="Revisar filtros y rango de fechas",
                pasos=[
                    "1. Ir a módulo de Producción",
                    "2. Clic en 'Limpiar Filtros'",
                    "3. Seleccionar 'Últimos 30 días'",
                    "4. Verificar que animales estén activos"
                ],
                prevencion="Documentar períodos sin registro para referencia futura",
                tags=["datos", "produccion", "filtros"]
            ),
            SolucionKnowledgeBase(
                problema="Alerta crítica persistente",
                sintomas=["Alerta roja no desaparece", "Notificación constante"],
                causa="Condición subyacente no resuelta o umbral mal configurado",
                solucion="Resolver causa raíz o ajustar umbral",
                pasos=[
                    "1. Hacer clic en la alerta para ver detalles",
                    "2. Leer explicación completa (FASE 10)",
                    "3. Si es falso positivo: Ajustar umbral en Configuración",
                    "4. Si es real: Tomar acción recomendada",
                    "5. Documentar decisión en notas"
                ],
                prevencion="Revisar umbrales mensualmente",
                tags=["alertas", "configuracion"]
            )
        ]
        
        self.knowledge_base.extend(soluciones_base)
    
    def _inicializar_checklists(self):
        """Inicializa checklists operativos"""
        checklist_semanal = ChecklistOperativo(
            nombre="Mantenimiento Semanal FincaFácil",
            frecuencia="semanal",
            items=[
                {"tarea": "Revisar alertas pendientes en dashboard", "completado": False, "fecha": None},
                {"tarea": "Verificar backup automático (debe existir archivo .bak)", "completado": False, "fecha": None},
                {"tarea": "Revisar usuarios con alto riesgo (FASE 14)", "completado": False, "fecha": None},
                {"tarea": "Validar integridad de datos críticos", "completado": False, "fecha": None},
                {"tarea": "Revisar logs de errores UX (FASE 13)", "completado": False, "fecha": None}
            ]
        )
        
        checklist_mensual = ChecklistOperativo(
            nombre="Revisión Mensual FincaFácil",
            frecuencia="mensual",
            items=[
                {"tarea": "Generar reporte mensual de riesgos (FASE 14)", "completado": False, "fecha": None},
                {"tarea": "Revisar y cerrar incidentes resueltos", "completado": False, "fecha": None},
                {"tarea": "Actualizar knowledge base con nuevas soluciones", "completado": False, "fecha": None},
                {"tarea": "Validar métricas de calidad (FASE 8)", "completado": False, "fecha": None},
                {"tarea": "Revisar configuración de umbrales y alertas", "completado": False, "fecha": None},
                {"tarea": "Hacer backup manual completo", "completado": False, "fecha": None},
                {"tarea": "Revisar performance del sistema (FASE 9)", "completado": False, "fecha": None}
            ]
        )
        
        self.checklists.extend([checklist_semanal, checklist_mensual])
    
    def registrar_incidente(self, incidente: Incidente) -> str:
        """
        Registra un nuevo incidente en el sistema
        
        Args:
            incidente: Información del incidente
            
        Returns:
            ID del incidente registrado
        """
        self.incidentes[incidente.id_incidente] = incidente
        
        # Buscar soluciones en knowledge base
        soluciones = self.buscar_solucion(incidente.titulo, incidente.descripcion)
        
        if soluciones:
            # Agregar nota de solución sugerida
            incidente.datos_contexto["soluciones_sugeridas"] = [s.problema for s in soluciones[:3]]
        
        return incidente.id_incidente
    
    def actualizar_estado(
        self, 
        id_incidente: str, 
        nuevo_estado: EstadoIncidente,
        notas: Optional[str] = None
    ) -> bool:
        """
        Actualiza el estado de un incidente
        
        Args:
            id_incidente: ID del incidente
            nuevo_estado: Nuevo estado
            notas: Notas adicionales (opcional)
            
        Returns:
            True si se actualizó correctamente
        """
        if id_incidente not in self.incidentes:
            return False
        
        incidente = self.incidentes[id_incidente]
        estado_anterior = incidente.estado
        incidente.estado = nuevo_estado
        
        # Registrar cambio de estado
        if "historial_estados" not in incidente.datos_contexto:
            incidente.datos_contexto["historial_estados"] = []
        
        incidente.datos_contexto["historial_estados"].append({
            "estado_anterior": estado_anterior.value,
            "estado_nuevo": nuevo_estado.value,
            "timestamp": datetime.now().isoformat(),
            "notas": notas
        })
        
        # Si se resolvió, calcular tiempo de resolución
        if nuevo_estado == EstadoIncidente.RESUELTO and not incidente.timestamp_resuelto:
            incidente.timestamp_resuelto = datetime.now()
            delta = incidente.timestamp_resuelto - incidente.timestamp_inicio
            incidente.tiempo_resolucion_min = int(delta.total_seconds() / 60)
        
        return True
    
    def resolver_incidente(
        self,
        id_incidente: str,
        solucion: str,
        pasos_resolucion: List[str],
        causa_raiz: Optional[str] = None,
        se_puede_prevenir: bool = False
    ) -> bool:
        """
        Marca un incidente como resuelto con su solución
        
        Args:
            id_incidente: ID del incidente
            solucion: Descripción de la solución aplicada
            pasos_resolucion: Lista de pasos seguidos
            causa_raiz: Causa raíz del problema (opcional)
            se_puede_prevenir: Si el incidente es prevenible
            
        Returns:
            True si se resolvió correctamente
        """
        if id_incidente not in self.incidentes:
            return False
        
        incidente = self.incidentes[id_incidente]
        incidente.solucion_aplicada = solucion
        incidente.pasos_resolucion = pasos_resolucion
        incidente.causa_raiz = causa_raiz
        incidente.se_puede_prevenir = se_puede_prevenir
        
        # Actualizar estado a RESUELTO
        self.actualizar_estado(id_incidente, EstadoIncidente.RESUELTO, "Incidente resuelto con solución documentada")
        
        return True
    
    def buscar_solucion(self, query: str, descripcion: Optional[str] = None) -> List[SolucionKnowledgeBase]:
        """
        Busca soluciones en knowledge base
        
        Args:
            query: Texto a buscar
            descripcion: Descripción adicional para contexto (opcional)
            
        Returns:
            Lista de soluciones relevantes ordenadas por relevancia
        """
        query_lower = query.lower()
        descripcion_lower = descripcion.lower() if descripcion else ""
        
        soluciones_relevantes = []
        
        for solucion in self.knowledge_base:
            score = 0
            
            # Buscar en problema
            if query_lower in solucion.problema.lower():
                score += 10
            
            # Buscar en síntomas
            for sintoma in solucion.sintomas:
                if query_lower in sintoma.lower():
                    score += 5
            
            # Buscar en tags
            for tag in solucion.tags:
                if query_lower in tag.lower():
                    score += 3
            
            # Buscar en descripción si está disponible
            if descripcion_lower:
                if descripcion_lower in solucion.problema.lower():
                    score += 5
                if descripcion_lower in solucion.causa.lower():
                    score += 3
            
            if score > 0:
                soluciones_relevantes.append((score, solucion))
        
        # Ordenar por score descendente
        soluciones_relevantes.sort(key=lambda x: x[0], reverse=True)
        
        return [s for _, s in soluciones_relevantes]
    
    def agregar_solucion_kb(self, solucion: SolucionKnowledgeBase) -> None:
        """Agrega una nueva solución a la knowledge base"""
        self.knowledge_base.append(solucion)
    
    def obtener_incidentes_activos(self) -> List[Incidente]:
        """
        Obtiene lista de incidentes activos (no cerrados)
        
        Returns:
            Lista de incidentes activos ordenados por severidad y fecha
        """
        incidentes_activos = [
            inc for inc in self.incidentes.values()
            if inc.estado != EstadoIncidente.CERRADO
        ]
        
        # Ordenar por severidad (crítica primero) y luego por fecha
        severidad_orden = {
            SeveridadIncidente.CRITICA: 0,
            SeveridadIncidente.ALTA: 1,
            SeveridadIncidente.MEDIA: 2,
            SeveridadIncidente.BAJA: 3
        }
        
        incidentes_activos.sort(
            key=lambda x: (severidad_orden[x.severidad], x.timestamp_inicio),
            reverse=False
        )
        
        return incidentes_activos
    
    def obtener_estadisticas_incidentes(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene estadísticas de incidentes de los últimos N días
        
        Args:
            dias: Cantidad de días hacia atrás
            
        Returns:
            Diccionario con estadísticas
        """
        fecha_limite = datetime.now() - timedelta(days=dias)
        
        incidentes_periodo = [
            inc for inc in self.incidentes.values()
            if inc.timestamp_inicio >= fecha_limite
        ]
        
        if not incidentes_periodo:
            return {
                "total_incidentes": 0,
                "periodo_dias": dias,
                "por_tipo": {},
                "por_severidad": {},
                "por_estado": {},
                "tiempo_resolucion_promedio_min": 0,
                "incidentes_prevenibles": 0
            }
        
        # Distribución por tipo
        por_tipo = {}
        for inc in incidentes_periodo:
            por_tipo[inc.tipo.value] = por_tipo.get(inc.tipo.value, 0) + 1
        
        # Distribución por severidad
        por_severidad = {}
        for inc in incidentes_periodo:
            por_severidad[inc.severidad.value] = por_severidad.get(inc.severidad.value, 0) + 1
        
        # Distribución por estado
        por_estado = {}
        for inc in incidentes_periodo:
            por_estado[inc.estado.value] = por_estado.get(inc.estado.value, 0) + 1
        
        # Tiempo de resolución promedio
        incidentes_resueltos = [
            inc for inc in incidentes_periodo
            if inc.tiempo_resolucion_min is not None
        ]
        
        tiempo_promedio = 0
        if incidentes_resueltos:
            # Asegurar tipos concretos para Pylance
            from typing import cast
            tiempos: List[int] = [cast(int, inc.tiempo_resolucion_min) for inc in incidentes_resueltos]
            tiempo_promedio = sum(tiempos) / len(tiempos)
        
        # Incidentes prevenibles
        prevenibles = sum(1 for inc in incidentes_periodo if inc.se_puede_prevenir)
        
        return {
            "total_incidentes": len(incidentes_periodo),
            "periodo_dias": dias,
            "por_tipo": por_tipo,
            "por_severidad": por_severidad,
            "por_estado": por_estado,
            "tiempo_resolucion_promedio_min": round(tiempo_promedio, 1),
            "incidentes_prevenibles": prevenibles,
            "porcentaje_prevenibles": round(prevenibles / len(incidentes_periodo) * 100, 1) if incidentes_periodo else 0
        }
    
    def obtener_checklist(self, frecuencia: str) -> Optional[ChecklistOperativo]:
        """
        Obtiene un checklist por frecuencia
        
        Args:
            frecuencia: "semanal", "mensual", etc.
            
        Returns:
            ChecklistOperativo o None si no existe
        """
        for checklist in self.checklists:
            if checklist.frecuencia == frecuencia:
                return checklist
        return None
    
    def completar_item_checklist(
        self,
        frecuencia: str,
        index_item: int,
        completado: bool = True
    ) -> bool:
        """
        Marca un item del checklist como completado
        
        Args:
            frecuencia: Frecuencia del checklist
            index_item: Índice del item (0-based)
            completado: Estado del item
            
        Returns:
            True si se actualizó correctamente
        """
        checklist = self.obtener_checklist(frecuencia)
        if not checklist or index_item >= len(checklist.items):
            return False
        
        checklist.items[index_item]["completado"] = completado
        checklist.items[index_item]["fecha"] = datetime.now().isoformat() if completado else None
        
        # Si se completaron todos los items, actualizar ultimo_ejecutado
        if all(item["completado"] for item in checklist.items):
            checklist.ultimo_ejecutado = datetime.now()
        
        return True
    
    def resetear_checklist(self, frecuencia: str) -> bool:
        """Resetea un checklist para nueva ejecución"""
        checklist = self.obtener_checklist(frecuencia)
        if not checklist:
            return False
        
        for item in checklist.items:
            item["completado"] = False
            item["fecha"] = None
        
        return True
    
    def exportar_datos(self, filepath: str) -> None:
        """Exporta todos los datos de incidentes a JSON"""
        datos = {
            "timestamp_exportacion": datetime.now().isoformat(),
            "total_incidentes": len(self.incidentes),
            "incidentes": {id_inc: inc.to_dict() for id_inc, inc in self.incidentes.items()},
            "knowledge_base": [sol.to_dict() for sol in self.knowledge_base],
            "checklists": [ch.to_dict() for ch in self.checklists]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)


# Singleton instance
_incident_management_service = None

def get_incident_management_service() -> IncidentManagementService:
    """Obtiene la instancia singleton del servicio de gestión de incidentes"""
    global _incident_management_service
    if _incident_management_service is None:
        _incident_management_service = IncidentManagementService()
    return _incident_management_service
