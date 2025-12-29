"""
FASE 14: RISK MANAGEMENT SERVICE
Detección de patrones peligrosos y resiliencia humana

Responsabilidades:
- Calcular score de riesgo por usuario (0-100)
- Detectar patrones de comportamiento peligroso
- Alertas de riesgo operativo
- Reportes mensuales de comportamiento
- Prevenir corrupción de datos antes de que ocurra
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json


class NivelRiesgoUsuario(Enum):
    """Nivel de riesgo operativo de un usuario"""
    MUY_BAJO = "muy_bajo"      # Score 0-20
    BAJO = "bajo"              # Score 21-40
    MEDIO = "medio"            # Score 41-60
    ALTO = "alto"              # Score 61-80
    CRITICO = "critico"        # Score 81-100


class TipoPatronPeligroso(Enum):
    """Tipos de patrones de comportamiento peligroso"""
    OVERRIDES_FRECUENTES = "overrides_frecuentes"
    ELIMINACIONES_MASIVAS = "eliminaciones_masivas"
    CAMBIOS_POST_CIERRE = "cambios_post_cierre"
    DESACTIVACION_VALIDACIONES = "desactivacion_validaciones"
    OPERACIONES_SOSPECHOSAS = "operaciones_sospechosas"
    HORARIOS_INUSUALES = "horarios_inusuales"
    ERRORES_REPETIDOS = "errores_repetidos"


@dataclass
class AccionRiesgosa:
    """Registro de una acción que genera riesgo"""
    usuario: str
    tipo_accion: str
    modulo: str
    descripcion: str
    gravedad: int  # 1-10
    timestamp: datetime = field(default_factory=datetime.now)
    datos_contexto: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "usuario": self.usuario,
            "tipo_accion": self.tipo_accion,
            "modulo": self.modulo,
            "descripcion": self.descripcion,
            "gravedad": self.gravedad,
            "timestamp": self.timestamp.isoformat(),
            "datos_contexto": self.datos_contexto
        }


@dataclass
class PatronDetectado:
    """Patrón peligroso detectado en un usuario"""
    tipo_patron: TipoPatronPeligroso
    usuario: str
    descripcion: str
    ocurrencias: int
    periodo_dias: int
    gravedad: int  # 1-10
    timestamp_deteccion: datetime = field(default_factory=datetime.now)
    acciones_relacionadas: List[AccionRiesgosa] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo_patron": self.tipo_patron.value,
            "usuario": self.usuario,
            "descripcion": self.descripcion,
            "ocurrencias": self.ocurrencias,
            "periodo_dias": self.periodo_dias,
            "gravedad": self.gravedad,
            "timestamp_deteccion": self.timestamp_deteccion.isoformat(),
            "acciones_relacionadas": [a.to_dict() for a in self.acciones_relacionadas]
        }


@dataclass
class ScoreRiesgo:
    """Score de riesgo de un usuario"""
    usuario: str
    score: float  # 0-100 (puede ser decimal por penalizaciones progresivas)
    nivel: NivelRiesgoUsuario
    causas: List[str]
    patrones_detectados: List[PatronDetectado]
    recomendacion: str
    requiere_accion: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "usuario": self.usuario,
            "score": self.score,
            "nivel": self.nivel.value,
            "causas": self.causas,
            "patrones_detectados": [p.to_dict() for p in self.patrones_detectados],
            "recomendacion": self.recomendacion,
            "requiere_accion": self.requiere_accion,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AlertaRiesgoOperativo:
    """Alerta de riesgo operativo para administradores"""
    usuario: str
    nivel_alerta: str  # "ATENCION", "URGENTE", "CRITICO"
    mensaje: str
    score_riesgo: float
    patrones: List[str]
    acciones_sugeridas: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "usuario": self.usuario,
            "nivel_alerta": self.nivel_alerta,
            "mensaje": self.mensaje,
            "score_riesgo": self.score_riesgo,
            "patrones": self.patrones,
            "acciones_sugeridas": self.acciones_sugeridas,
            "timestamp": self.timestamp.isoformat()
        }


class RiskManagementService:
    """
    Servicio de gestión de riesgos humanos y resiliencia operativa
    """
    
    def __init__(self):
        self.acciones_riesgosas: Dict[str, List[AccionRiesgosa]] = {}  # usuario -> acciones
        self.patrones_detectados: Dict[str, List[PatronDetectado]] = {}  # usuario -> patrones
        self.scores_riesgo: Dict[str, ScoreRiesgo] = {}  # usuario -> score
        self.alertas_operativas: List[AlertaRiesgoOperativo] = []
        
        # Configuración de detección
        self._configurar_umbrales()
    
    def _configurar_umbrales(self):
        """Define umbrales para detección de patrones"""
        self.umbrales = {
            TipoPatronPeligroso.OVERRIDES_FRECUENTES: {
                "ocurrencias": 5,
                "periodo_dias": 7,
                "gravedad": 7
            },
            TipoPatronPeligroso.ELIMINACIONES_MASIVAS: {
                "ocurrencias": 3,
                "periodo_dias": 14,
                "gravedad": 9
            },
            TipoPatronPeligroso.CAMBIOS_POST_CIERRE: {
                "ocurrencias": 2,
                "periodo_dias": 7,
                "gravedad": 8
            },
            TipoPatronPeligroso.DESACTIVACION_VALIDACIONES: {
                "ocurrencias": 2,
                "periodo_dias": 14,
                "gravedad": 9
            },
            TipoPatronPeligroso.ERRORES_REPETIDOS: {
                "ocurrencias": 10,
                "periodo_dias": 7,
                "gravedad": 6
            }
        }
    
    def registrar_accion_riesgosa(self, accion: AccionRiesgosa) -> None:
        """
        Registra una acción que genera riesgo operativo
        
        Args:
            accion: Información de la acción riesgosa
        """
        if accion.usuario not in self.acciones_riesgosas:
            self.acciones_riesgosas[accion.usuario] = []
        
        self.acciones_riesgosas[accion.usuario].append(accion)
        
        # Detectar patrones después de registrar
        self._detectar_patrones_usuario(accion.usuario)
        
        # Recalcular score de riesgo
        self._calcular_score_riesgo(accion.usuario)
    
    def _detectar_patrones_usuario(self, usuario: str) -> List[PatronDetectado]:
        """
        Detecta patrones peligrosos en las acciones de un usuario
        
        Args:
            usuario: ID del usuario a analizar
            
        Returns:
            Lista de patrones detectados
        """
        if usuario not in self.acciones_riesgosas:
            return []
        
        acciones = self.acciones_riesgosas[usuario]
        patrones_nuevos = []
        
        # Detectar cada tipo de patrón
        for tipo_patron, config in self.umbrales.items():
            patron = self._detectar_patron_especifico(
                usuario, 
                acciones, 
                tipo_patron, 
                config
            )
            
            if patron:
                patrones_nuevos.append(patron)
        
        # Guardar patrones detectados
        if patrones_nuevos:
            if usuario not in self.patrones_detectados:
                self.patrones_detectados[usuario] = []
            
            self.patrones_detectados[usuario].extend(patrones_nuevos)
            
            # Generar alerta si es necesario
            self._generar_alerta_si_necesario(usuario, patrones_nuevos)
        
        return patrones_nuevos
    
    def _detectar_patron_especifico(
        self, 
        usuario: str, 
        acciones: List[AccionRiesgosa],
        tipo_patron: TipoPatronPeligroso,
        config: Dict[str, Any]
    ) -> Optional[PatronDetectado]:
        """Detecta un patrón específico en las acciones"""
        periodo_dias = config["periodo_dias"]
        ocurrencias_minimas = config["ocurrencias"]
        gravedad = config["gravedad"]
        
        # Filtrar acciones relevantes para este patrón
        fecha_limite = datetime.now() - timedelta(days=periodo_dias)
        acciones_relevantes = self._filtrar_acciones_por_patron(
            acciones, 
            tipo_patron, 
            fecha_limite
        )
        
        if len(acciones_relevantes) >= ocurrencias_minimas:
            return PatronDetectado(
                tipo_patron=tipo_patron,
                usuario=usuario,
                descripcion=self._generar_descripcion_patron(tipo_patron, len(acciones_relevantes), periodo_dias),
                ocurrencias=len(acciones_relevantes),
                periodo_dias=periodo_dias,
                gravedad=gravedad,
                acciones_relacionadas=acciones_relevantes
            )
        
        return None
    
    def _filtrar_acciones_por_patron(
        self,
        acciones: List[AccionRiesgosa],
        tipo_patron: TipoPatronPeligroso,
        fecha_limite: datetime
    ) -> List[AccionRiesgosa]:
        """Filtra acciones relevantes para un patrón específico"""
        acciones_filtradas = []
        
        for accion in acciones:
            if accion.timestamp < fecha_limite:
                continue
            
            # Filtrar por tipo de patrón
            if tipo_patron == TipoPatronPeligroso.OVERRIDES_FRECUENTES:
                if "override" in accion.tipo_accion.lower():
                    acciones_filtradas.append(accion)
            
            elif tipo_patron == TipoPatronPeligroso.ELIMINACIONES_MASIVAS:
                if "eliminacion" in accion.tipo_accion.lower() and accion.gravedad >= 7:
                    acciones_filtradas.append(accion)
            
            elif tipo_patron == TipoPatronPeligroso.CAMBIOS_POST_CIERRE:
                if "post_cierre" in accion.tipo_accion.lower():
                    acciones_filtradas.append(accion)
            
            elif tipo_patron == TipoPatronPeligroso.DESACTIVACION_VALIDACIONES:
                if "desactivar_validacion" in accion.tipo_accion.lower():
                    acciones_filtradas.append(accion)
            
            elif tipo_patron == TipoPatronPeligroso.ERRORES_REPETIDOS:
                if accion.gravedad >= 5:
                    acciones_filtradas.append(accion)
        
        return acciones_filtradas
    
    def _generar_descripcion_patron(
        self, 
        tipo_patron: TipoPatronPeligroso, 
        ocurrencias: int, 
        periodo_dias: int
    ) -> str:
        """Genera descripción legible de un patrón"""
        descripciones = {
            TipoPatronPeligroso.OVERRIDES_FRECUENTES: f"{ocurrencias} overrides de alertas en {periodo_dias} días",
            TipoPatronPeligroso.ELIMINACIONES_MASIVAS: f"{ocurrencias} eliminaciones masivas en {periodo_dias} días",
            TipoPatronPeligroso.CAMBIOS_POST_CIERRE: f"{ocurrencias} cambios post-cierre en {periodo_dias} días",
            TipoPatronPeligroso.DESACTIVACION_VALIDACIONES: f"{ocurrencias} desactivaciones de validación en {periodo_dias} días",
            TipoPatronPeligroso.ERRORES_REPETIDOS: f"{ocurrencias} errores repetidos en {periodo_dias} días"
        }
        
        return descripciones.get(tipo_patron, f"{ocurrencias} acciones en {periodo_dias} días")
    
    def _calcular_score_riesgo(self, usuario: str) -> ScoreRiesgo:
        """
        Calcula el score de riesgo de un usuario (0-100)
        
        Args:
            usuario: ID del usuario
            
        Returns:
            ScoreRiesgo con score, nivel, causas, recomendación
        """
        score = 0
        causas = []
        
        # Obtener patrones del usuario
        patrones = self.patrones_detectados.get(usuario, [])
        
        # Calcular score basado en patrones
        for patron in patrones:
            # Score base por gravedad del patrón (más moderado)
            score += patron.gravedad * 2  # 2-20 puntos por patrón
            
            # Bonus por frecuencia (reducido)
            if patron.ocurrencias > self.umbrales[patron.tipo_patron]["ocurrencias"]:
                score += (patron.ocurrencias - self.umbrales[patron.tipo_patron]["ocurrencias"]) * 3
            
            causas.append(patron.descripcion)
        
        # Obtener acciones recientes (últimos 30 días)
        acciones_recientes = self._obtener_acciones_recientes(usuario, dias=30)
        
        # Penalizar por cantidad de acciones riesgosas recientes (más progresivo)
        if len(acciones_recientes) > 10:
            score += (len(acciones_recientes) - 10) * 1.5
            causas.append(f"{len(acciones_recientes)} acciones riesgosas en 30 días")
        elif len(acciones_recientes) > 5:
            score += (len(acciones_recientes) - 5) * 0.5
        
        # Calcular gravedad promedio
        if acciones_recientes:
            gravedad_promedio = sum(a.gravedad for a in acciones_recientes) / len(acciones_recientes)
            if gravedad_promedio >= 7:
                score += 8
                causas.append(f"Gravedad promedio alta: {gravedad_promedio:.1f}/10")
            elif gravedad_promedio >= 6:
                score += 4
        
        # Limitar score a 0-100
        score = min(100, max(0, score))
        
        # Determinar nivel
        if score <= 20:
            nivel = NivelRiesgoUsuario.MUY_BAJO
        elif score <= 40:
            nivel = NivelRiesgoUsuario.BAJO
        elif score <= 60:
            nivel = NivelRiesgoUsuario.MEDIO
        elif score <= 80:
            nivel = NivelRiesgoUsuario.ALTO
        else:
            nivel = NivelRiesgoUsuario.CRITICO
        
        # Generar recomendación
        recomendacion = self._generar_recomendacion(nivel, patrones, usuario)
        
        # Determinar si requiere acción
        requiere_accion = score >= 60
        
        score_obj = ScoreRiesgo(
            usuario=usuario,
            score=score,
            nivel=nivel,
            causas=causas if causas else ["Sin patrones detectados"],
            patrones_detectados=patrones,
            recomendacion=recomendacion,
            requiere_accion=requiere_accion
        )
        
        self.scores_riesgo[usuario] = score_obj
        return score_obj
    
    def _obtener_acciones_recientes(self, usuario: str, dias: int) -> List[AccionRiesgosa]:
        """Obtiene acciones recientes de un usuario"""
        if usuario not in self.acciones_riesgosas:
            return []
        
        fecha_limite = datetime.now() - timedelta(days=dias)
        return [
            a for a in self.acciones_riesgosas[usuario]
            if a.timestamp >= fecha_limite
        ]
    
    def _generar_recomendacion(
        self, 
        nivel: NivelRiesgoUsuario, 
        patrones: List[PatronDetectado],
        usuario: str
    ) -> str:
        """Genera recomendación basada en nivel de riesgo"""
        if nivel == NivelRiesgoUsuario.MUY_BAJO:
            return "✅ Usuario opera dentro de parámetros normales. Monitoreo estándar."
        
        elif nivel == NivelRiesgoUsuario.BAJO:
            return "⚠️ Monitoreo regular. Considerar recordatorio de mejores prácticas."
        
        elif nivel == NivelRiesgoUsuario.MEDIO:
            return "⚠️ Revisar con el usuario. Puede requerir capacitación en áreas específicas."
        
        elif nivel == NivelRiesgoUsuario.ALTO:
            recomendacion = "🔴 REQUIERE ACCIÓN: "
            if any(p.tipo_patron == TipoPatronPeligroso.OVERRIDES_FRECUENTES for p in patrones):
                recomendacion += "Capacitación en interpretación de alertas. "
            if any(p.tipo_patron == TipoPatronPeligroso.ELIMINACIONES_MASIVAS for p in patrones):
                recomendacion += "Supervisión en operaciones de eliminación. "
            recomendacion += "Revisar permisos."
            return recomendacion
        
        else:  # CRITICO
            return "🚨 ACCIÓN URGENTE: Suspender permisos críticos hasta capacitación obligatoria. Supervisión 100%."
    
    def _generar_alerta_si_necesario(self, usuario: str, patrones: List[PatronDetectado]) -> None:
        """Genera alerta operativa si el riesgo es alto"""
        score_obj = self.scores_riesgo.get(usuario)
        
        if not score_obj or score_obj.score < 60:
            return  # No genera alerta si riesgo < 60
        
        # Determinar nivel de alerta
        if score_obj.score >= 80:
            nivel_alerta = "CRITICO"
        elif score_obj.score >= 70:
            nivel_alerta = "URGENTE"
        else:
            nivel_alerta = "ATENCION"
        
        # Mensaje
        mensaje = f"Usuario '{usuario}' con score de riesgo {score_obj.score}/100 ({score_obj.nivel.value.upper()})"
        
        # Listar patrones
        patrones_lista = [p.descripcion for p in patrones]
        
        # Acciones sugeridas
        acciones_sugeridas = [
            "Revisar historial de acciones del usuario",
            "Agendar capacitación o recordatorio",
            "Evaluar ajuste de permisos"
        ]
        
        if score_obj.score >= 80:
            acciones_sugeridas.insert(0, "⚠️ URGENTE: Supervisión inmediata requerida")
        
        alerta = AlertaRiesgoOperativo(
            usuario=usuario,
            nivel_alerta=nivel_alerta,
            mensaje=mensaje,
            score_riesgo=score_obj.score,
            patrones=patrones_lista,
            acciones_sugeridas=acciones_sugeridas
        )
        
        self.alertas_operativas.append(alerta)
    
    def obtener_score_usuario(self, usuario: str) -> Optional[ScoreRiesgo]:
        """
        Obtiene el score de riesgo actual de un usuario
        
        Args:
            usuario: ID del usuario
            
        Returns:
            ScoreRiesgo o None si no tiene score
        """
        return self.scores_riesgo.get(usuario)
    
    def obtener_usuarios_alto_riesgo(self, umbral: int = 60) -> List[ScoreRiesgo]:
        """
        Obtiene lista de usuarios con score >= umbral
        
        Args:
            umbral: Score mínimo para considerar alto riesgo (default 60)
            
        Returns:
            Lista de ScoreRiesgo ordenada por score descendente
        """
        usuarios_riesgo = [
            score for score in self.scores_riesgo.values()
            if score.score >= umbral
        ]
        
        return sorted(usuarios_riesgo, key=lambda x: x.score, reverse=True)
    
    def obtener_alertas_operativas(self, ultimas_n: Optional[int] = None) -> List[AlertaRiesgoOperativo]:
        """
        Obtiene alertas operativas generadas
        
        Args:
            ultimas_n: Cantidad de alertas más recientes (None = todas)
            
        Returns:
            Lista de alertas ordenadas por timestamp descendente
        """
        alertas = sorted(self.alertas_operativas, key=lambda x: x.timestamp, reverse=True)
        
        if ultimas_n:
            return alertas[:ultimas_n]
        
        return alertas
    
    def generar_reporte_mensual(self, mes: Optional[int] = None, anio: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera reporte mensual de riesgos operativos
        
        Args:
            mes: Mes del reporte (default: mes actual)
            anio: Año del reporte (default: año actual)
            
        Returns:
            Diccionario con estadísticas del mes
        """
        ahora = datetime.now()
        mes = mes or ahora.month
        anio = anio or ahora.year
        
        # Filtrar acciones del mes
        acciones_mes = []
        for usuario, acciones in self.acciones_riesgosas.items():
            acciones_mes.extend([
                a for a in acciones
                if a.timestamp.month == mes and a.timestamp.year == anio
            ])
        
        # Estadísticas
        total_acciones = len(acciones_mes)
        usuarios_con_acciones = len(set(a.usuario for a in acciones_mes))
        
        # Distribución por gravedad
        distribucion_gravedad = {}
        for accion in acciones_mes:
            gravedad = accion.gravedad
            distribucion_gravedad[gravedad] = distribucion_gravedad.get(gravedad, 0) + 1
        
        # Top usuarios riesgosos
        usuarios_riesgo = self.obtener_usuarios_alto_riesgo(umbral=60)
        top_usuarios = [
            {"usuario": u.usuario, "score": u.score, "nivel": u.nivel.value}
            for u in usuarios_riesgo[:10]
        ]
        
        # Patrones más comunes
        patrones_comunes = {}
        for patrones in self.patrones_detectados.values():
            for patron in patrones:
                tipo = patron.tipo_patron.value
                patrones_comunes[tipo] = patrones_comunes.get(tipo, 0) + 1
        
        return {
            "mes": mes,
            "anio": anio,
            "timestamp_generacion": datetime.now().isoformat(),
            "total_acciones_riesgosas": total_acciones,
            "usuarios_con_acciones": usuarios_con_acciones,
            "distribucion_gravedad": distribucion_gravedad,
            "top_usuarios_riesgo": top_usuarios,
            "patrones_mas_comunes": patrones_comunes,
            "total_alertas_generadas": len(self.alertas_operativas)
        }
    
    def exportar_datos(self, filepath: str) -> None:
        """Exporta todos los datos de riesgos a JSON"""
        datos = {
            "timestamp_exportacion": datetime.now().isoformat(),
            "total_usuarios": len(self.acciones_riesgosas),
            "scores_riesgo": {u: s.to_dict() for u, s in self.scores_riesgo.items()},
            "alertas_operativas": [a.to_dict() for a in self.alertas_operativas],
            "patrones_detectados": {
                u: [p.to_dict() for p in patrones]
                for u, patrones in self.patrones_detectados.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)


# Singleton instance
_risk_management_service = None

def get_risk_management_service() -> RiskManagementService:
    """Obtiene la instancia singleton del servicio de gestión de riesgos"""
    global _risk_management_service
    if _risk_management_service is None:
        _risk_management_service = RiskManagementService()
    return _risk_management_service
