"""
FASE 13: UX GUARDRAILS SERVICE
Protección contra errores humanos y mejora de adopción

Responsabilidades:
- Detectar flujos peligrosos antes de ejecución
- Confirmaciones inteligentes contextuales
- Modo "Usuario Novato" con tooltips progresivos
- Logs de errores UX para análisis
- Advertencias por impacto real
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import json


class NivelRiesgo(Enum):
    """Nivel de riesgo de una acción"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class TipoAccion(Enum):
    """Tipos de acciones del usuario"""
    ELIMINAR_DATOS = "eliminar_datos"
    MODIFICAR_MASIVO = "modificar_masivo"
    CIERRE_PERIODO = "cierre_periodo"
    CAMBIO_CONFIGURACION = "cambio_configuracion"
    EXPORTAR_DATOS = "exportar_datos"
    IMPORTAR_DATOS = "importar_datos"
    OVERRIDE_ALERTA = "override_alerta"
    DESACTIVAR_VALIDACION = "desactivar_validacion"


class ModoUsuario(Enum):
    """Modos de operación del usuario"""
    NOVATO = "novato"          # Primeras 2 semanas
    INTERMEDIO = "intermedio"  # 2 semanas - 3 meses
    AVANZADO = "avanzado"      # 3+ meses o certificado


@dataclass
class ContextoAccion:
    """Contexto completo de una acción del usuario"""
    tipo_accion: TipoAccion
    usuario: str
    modulo: str
    datos_afectados: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    sesion_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo_accion": self.tipo_accion.value,
            "usuario": self.usuario,
            "modulo": self.modulo,
            "datos_afectados": self.datos_afectados,
            "timestamp": self.timestamp.isoformat(),
            "sesion_id": self.sesion_id
        }


@dataclass
class AnalisisRiesgo:
    """Resultado del análisis de riesgo de una acción"""
    nivel_riesgo: NivelRiesgo
    requiere_confirmacion: bool
    mensaje_advertencia: str
    consecuencias: List[str]
    acciones_recomendadas: List[str]
    puede_revertirse: bool
    tiempo_estimado_impacto: str  # "inmediato", "1-5 min", "5-30 min", etc.
    alternativas_seguras: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nivel_riesgo": self.nivel_riesgo.value,
            "requiere_confirmacion": self.requiere_confirmacion,
            "mensaje_advertencia": self.mensaje_advertencia,
            "consecuencias": self.consecuencias,
            "acciones_recomendadas": self.acciones_recomendadas,
            "puede_revertirse": self.puede_revertirse,
            "tiempo_estimado_impacto": self.tiempo_estimado_impacto,
            "alternativas_seguras": self.alternativas_seguras
        }


@dataclass
class ErrorUX:
    """Registro de un error de UX (usuario intentó algo y falló)"""
    usuario: str
    accion_intentada: str
    modulo: str
    mensaje_error: str
    timestamp: datetime = field(default_factory=datetime.now)
    modo_usuario: ModoUsuario = ModoUsuario.INTERMEDIO
    pasos_previos: List[str] = field(default_factory=list)
    sugerencia_mejora: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "usuario": self.usuario,
            "accion_intentada": self.accion_intentada,
            "modulo": self.modulo,
            "mensaje_error": self.mensaje_error,
            "timestamp": self.timestamp.isoformat(),
            "modo_usuario": self.modo_usuario.value,
            "pasos_previos": self.pasos_previos,
            "sugerencia_mejora": self.sugerencia_mejora
        }


@dataclass
class Tooltip:
    """Tooltip contextual para modo novato"""
    elemento: str
    mensaje: str
    duracion_dias: int  # Cuántos días mostrar este tooltip
    prioridad: int = 1  # 1=alta, 2=media, 3=baja
    mostrar_solo_una_vez: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "elemento": self.elemento,
            "mensaje": self.mensaje,
            "duracion_dias": self.duracion_dias,
            "prioridad": self.prioridad,
            "mostrar_solo_una_vez": self.mostrar_solo_una_vez
        }


class UXGuardrailsService:
    """
    Servicio de protección UX contra errores humanos
    """
    
    def __init__(self):
        self.errores_ux: List[ErrorUX] = []
        self.tooltips_activos: Dict[str, List[Tooltip]] = {}
        self.confirmaciones_pendientes: List[ContextoAccion] = []
        
        # Reglas de riesgo predefinidas
        self._inicializar_reglas_riesgo()
        
    def _inicializar_reglas_riesgo(self):
        """Define reglas de riesgo para cada tipo de acción"""
        self.reglas_riesgo = {
            TipoAccion.ELIMINAR_DATOS: {
                "nivel_base": NivelRiesgo.ALTO,
                "requiere_confirmacion": True,
                "puede_revertirse": False
            },
            TipoAccion.MODIFICAR_MASIVO: {
                "nivel_base": NivelRiesgo.MEDIO,
                "requiere_confirmacion": True,
                "puede_revertirse": True
            },
            TipoAccion.CIERRE_PERIODO: {
                "nivel_base": NivelRiesgo.CRITICO,
                "requiere_confirmacion": True,
                "puede_revertirse": False
            },
            TipoAccion.CAMBIO_CONFIGURACION: {
                "nivel_base": NivelRiesgo.MEDIO,
                "requiere_confirmacion": True,
                "puede_revertirse": True
            },
            TipoAccion.OVERRIDE_ALERTA: {
                "nivel_base": NivelRiesgo.MEDIO,
                "requiere_confirmacion": False,
                "puede_revertirse": False
            },
            TipoAccion.DESACTIVAR_VALIDACION: {
                "nivel_base": NivelRiesgo.ALTO,
                "requiere_confirmacion": True,
                "puede_revertirse": True
            }
        }
    
    def analizar_riesgo(self, contexto: ContextoAccion) -> AnalisisRiesgo:
        """
        Analiza el riesgo de una acción antes de ejecutarla
        
        Args:
            contexto: Información completa de la acción
            
        Returns:
            AnalisisRiesgo con nivel, mensaje, consecuencias
        """
        regla = self.reglas_riesgo.get(contexto.tipo_accion)
        if not regla:
            # Acción sin riesgo especial
            return AnalisisRiesgo(
                nivel_riesgo=NivelRiesgo.BAJO,
                requiere_confirmacion=False,
                mensaje_advertencia="",
                consecuencias=[],
                acciones_recomendadas=[],
                puede_revertirse=True,
                tiempo_estimado_impacto="inmediato"
            )
        
        # Construir análisis según tipo de acción
        if contexto.tipo_accion == TipoAccion.ELIMINAR_DATOS:
            return self._analizar_eliminacion(contexto, regla)
        elif contexto.tipo_accion == TipoAccion.CIERRE_PERIODO:
            return self._analizar_cierre_periodo(contexto, regla)
        elif contexto.tipo_accion == TipoAccion.MODIFICAR_MASIVO:
            return self._analizar_modificacion_masiva(contexto, regla)
        elif contexto.tipo_accion == TipoAccion.CAMBIO_CONFIGURACION:
            return self._analizar_cambio_configuracion(contexto, regla)
        elif contexto.tipo_accion == TipoAccion.OVERRIDE_ALERTA:
            return self._analizar_override_alerta(contexto, regla)
        else:
            return self._analizar_generico(contexto, regla)
    
    def _analizar_eliminacion(self, contexto: ContextoAccion, regla: Dict) -> AnalisisRiesgo:
        """Analiza riesgo de eliminación de datos"""
        registros = contexto.datos_afectados.get("cantidad_registros", 0)
        tipo_dato = contexto.datos_afectados.get("tipo_dato", "datos")
        
        consecuencias = [
            f"Se eliminarán {registros} {tipo_dato} permanentemente",
            "No se pueden recuperar sin backup",
            "Impacta reportes históricos"
        ]
        
        if registros > 100:
            nivel = NivelRiesgo.CRITICO
            consecuencias.append(f"⚠️ ELIMINACIÓN MASIVA: {registros} registros")
        else:
            nivel = regla["nivel_base"]
        
        return AnalisisRiesgo(
            nivel_riesgo=nivel,
            requiere_confirmacion=True,
            mensaje_advertencia=f"⚠️ Estás a punto de ELIMINAR {registros} {tipo_dato}. Esta acción es IRREVERSIBLE.",
            consecuencias=consecuencias,
            acciones_recomendadas=[
                "Verificar que seleccionaste los registros correctos",
                "Hacer backup antes de eliminar",
                "Considerar archivar en lugar de eliminar"
            ],
            puede_revertirse=False,
            tiempo_estimado_impacto="inmediato",
            alternativas_seguras=[
                "Archivar registros (mantiene histórico)",
                "Marcar como inactivo",
                "Exportar antes de eliminar"
            ]
        )
    
    def _analizar_cierre_periodo(self, contexto: ContextoAccion, regla: Dict) -> AnalisisRiesgo:
        """Analiza riesgo de cierre de período contable/operativo"""
        periodo = contexto.datos_afectados.get("periodo", "desconocido")
        modulos_bloqueados = contexto.datos_afectados.get("modulos_bloqueados", [])
        alertas_generadas = contexto.datos_afectados.get("alertas_esperadas", 0)
        
        consecuencias = [
            f"El período '{periodo}' quedará BLOQUEADO para ediciones",
            f"Se bloquearán {len(modulos_bloqueados)} módulos",
            f"Se generarán aprox. {alertas_generadas} alertas de validación",
            "Solo un administrador podrá reabrir el período"
        ]
        
        return AnalisisRiesgo(
            nivel_riesgo=NivelRiesgo.CRITICO,
            requiere_confirmacion=True,
            mensaje_advertencia=f"🔒 CIERRE DE PERÍODO '{periodo}': Esta acción bloqueará {len(modulos_bloqueados)} módulos y generará {alertas_generadas} alertas. ¿Continuar?",
            consecuencias=consecuencias,
            acciones_recomendadas=[
                "Verificar que todos los datos del período están completos",
                "Revisar alertas pendientes",
                "Confirmar con supervisor si es necesario",
                "Hacer backup antes del cierre"
            ],
            puede_revertirse=False,
            tiempo_estimado_impacto="5-30 min",
            alternativas_seguras=[
                "Hacer pre-cierre (simulación sin bloquear)",
                "Revisar reporte de inconsistencias primero"
            ]
        )
    
    def _analizar_modificacion_masiva(self, contexto: ContextoAccion, regla: Dict) -> AnalisisRiesgo:
        """Analiza riesgo de modificación masiva"""
        registros = contexto.datos_afectados.get("cantidad_registros", 0)
        campos = contexto.datos_afectados.get("campos_modificados", [])
        
        return AnalisisRiesgo(
            nivel_riesgo=NivelRiesgo.MEDIO if registros < 50 else NivelRiesgo.ALTO,
            requiere_confirmacion=True,
            mensaje_advertencia=f"⚠️ Vas a modificar {registros} registros en {len(campos)} campos. Puedes revertir esta acción.",
            consecuencias=[
                f"Se modificarán {registros} registros",
                f"Campos afectados: {', '.join(campos[:3])}{'...' if len(campos) > 3 else ''}",
                "Se registrará en auditoría"
            ],
            acciones_recomendadas=[
                "Verificar filtros aplicados",
                "Hacer prueba con 1-2 registros primero",
                "Revisar vista previa si está disponible"
            ],
            puede_revertirse=True,
            tiempo_estimado_impacto="1-5 min"
        )
    
    def _analizar_cambio_configuracion(self, contexto: ContextoAccion, regla: Dict) -> AnalisisRiesgo:
        """Analiza cambio en configuración del sistema"""
        parametro = contexto.datos_afectados.get("parametro", "")
        valor_anterior = contexto.datos_afectados.get("valor_anterior", "")
        valor_nuevo = contexto.datos_afectados.get("valor_nuevo", "")
        
        return AnalisisRiesgo(
            nivel_riesgo=NivelRiesgo.MEDIO,
            requiere_confirmacion=True,
            mensaje_advertencia=f"⚙️ Cambiarás '{parametro}' de '{valor_anterior}' a '{valor_nuevo}'. Esto puede afectar operaciones futuras.",
            consecuencias=[
                f"Parámetro '{parametro}' cambiará a '{valor_nuevo}'",
                "Afecta operaciones futuras, no históricas",
                "Se puede revertir si es necesario"
            ],
            acciones_recomendadas=[
                "Anotar valor anterior por seguridad",
                "Avisar al equipo del cambio",
                "Monitorear comportamiento después"
            ],
            puede_revertirse=True,
            tiempo_estimado_impacto="inmediato"
        )
    
    def _analizar_override_alerta(self, contexto: ContextoAccion, regla: Dict) -> AnalisisRiesgo:
        """Analiza override de una alerta"""
        tipo_alerta = contexto.datos_afectados.get("tipo_alerta", "desconocida")
        gravedad = contexto.datos_afectados.get("gravedad", "MEDIA")
        
        return AnalisisRiesgo(
            nivel_riesgo=NivelRiesgo.MEDIO if gravedad != "ALTA" else NivelRiesgo.ALTO,
            requiere_confirmacion=False,  # Se permite pero se registra
            mensaje_advertencia=f"⚠️ Ignorarás alerta '{tipo_alerta}' de gravedad {gravedad}. Se registrará en auditoría.",
            consecuencias=[
                f"Alerta '{tipo_alerta}' será marcada como vista",
                "No afecta datos, solo visibilidad",
                "Se registra en log de overrides"
            ],
            acciones_recomendadas=[
                "Anotar razón del override",
                "Verificar causa raíz de la alerta",
                "No hacer overrides frecuentes (genera riesgo)"
            ],
            puede_revertirse=False,
            tiempo_estimado_impacto="inmediato"
        )
    
    def _analizar_generico(self, contexto: ContextoAccion, regla: Dict) -> AnalisisRiesgo:
        """Análisis genérico para acciones sin handler específico"""
        return AnalisisRiesgo(
            nivel_riesgo=regla["nivel_base"],
            requiere_confirmacion=regla["requiere_confirmacion"],
            mensaje_advertencia=f"Esta acción requiere confirmación: {contexto.tipo_accion.value}",
            consecuencias=["La acción afectará datos del sistema"],
            acciones_recomendadas=["Verificar antes de continuar"],
            puede_revertirse=regla["puede_revertirse"],
            tiempo_estimado_impacto="1-5 min"
        )
    
    def registrar_error_ux(self, error: ErrorUX) -> None:
        """
        Registra un error de UX para análisis posterior
        
        Args:
            error: Información del error UX ocurrido
        """
        self.errores_ux.append(error)
        
        # Auto-generar sugerencia si no tiene
        if not error.sugerencia_mejora:
            error.sugerencia_mejora = self._generar_sugerencia(error)
    
    def _generar_sugerencia(self, error: ErrorUX) -> str:
        """Genera sugerencia de mejora basada en el error"""
        if "no encontrado" in error.mensaje_error.lower():
            return "💡 Tip: Usa el buscador para encontrar el registro primero"
        elif "permiso" in error.mensaje_error.lower():
            return "💡 Tip: Esta acción requiere permisos de supervisor"
        elif "formato" in error.mensaje_error.lower():
            return "💡 Tip: Revisa el formato esperado en el tooltip"
        elif "requerido" in error.mensaje_error.lower():
            return "💡 Tip: Los campos con (*) son obligatorios"
        else:
            return "💡 Tip: Consulta la ayuda o contacta soporte"
    
    def obtener_tooltips_para_usuario(self, modo: ModoUsuario, modulo: str) -> List[Tooltip]:
        """
        Obtiene tooltips activos para un usuario según su modo y módulo
        
        Args:
            modo: Nivel del usuario (novato, intermedio, avanzado)
            modulo: Módulo actual donde está el usuario
            
        Returns:
            Lista de tooltips aplicables
        """
        if modo == ModoUsuario.AVANZADO:
            return []  # Usuarios avanzados no necesitan tooltips
        
        # Tooltips generales para novatos
        tooltips_base = self._obtener_tooltips_base(modulo)
        
        if modo == ModoUsuario.NOVATO:
            return tooltips_base
        else:
            # Intermedios solo ven tooltips de alta prioridad
            return [t for t in tooltips_base if t.prioridad == 1]
    
    def _obtener_tooltips_base(self, modulo: str) -> List[Tooltip]:
        """Define tooltips base por módulo"""
        tooltips_globales = [
            Tooltip(
                elemento="btn_guardar",
                mensaje="Guarda los cambios en la base de datos. Usa Ctrl+S para guardar rápido.",
                duracion_dias=7,
                prioridad=2  # Prioridad media para intermedio
            ),
            Tooltip(
                elemento="btn_eliminar",
                mensaje="⚠️ Eliminar es permanente. Considera 'Archivar' si no estás seguro.",
                duracion_dias=14,
                prioridad=1  # Alta prioridad - siempre mostrar
            )
        ]
        
        tooltips_por_modulo = {
            "dashboard": [
                Tooltip(
                    elemento="alertas_panel",
                    mensaje="Las alertas rojas requieren acción inmediata. Haz clic para ver detalles.",
                    duracion_dias=3,
                    prioridad=1  # Alta prioridad
                )
            ],
            "animales": [
                Tooltip(
                    elemento="estado_animal",
                    mensaje="El estado afecta reportes y alertas. Actualízalo al vender o dar de baja.",
                    duracion_dias=7,
                    prioridad=2
                )
            ],
            "produccion": [
                Tooltip(
                    elemento="registro_diario",
                    mensaje="Registra la producción diaria antes de las 9 AM para mejores insights.",
                    duracion_dias=14,
                    prioridad=1
                )
            ]
        }
        
        return tooltips_globales + tooltips_por_modulo.get(modulo, [])
    
    def validar_modo_usuario(self, usuario: str, accion: TipoAccion, modo: ModoUsuario) -> Dict[str, Any]:
        """
        Valida si un usuario en cierto modo puede ejecutar una acción
        
        Args:
            usuario: ID del usuario
            accion: Tipo de acción a ejecutar
            modo: Modo actual del usuario
            
        Returns:
            Dict con 'permitido' (bool) y 'razon' (str)
        """
        # Acciones bloqueadas para novatos
        acciones_bloqueadas_novato = [
            TipoAccion.CIERRE_PERIODO,
            TipoAccion.DESACTIVAR_VALIDACION,
            TipoAccion.MODIFICAR_MASIVO
        ]
        
        if modo == ModoUsuario.NOVATO and accion in acciones_bloqueadas_novato:
            return {
                "permitido": False,
                "razon": f"⚠️ Acción '{accion.value}' no disponible en modo Novato. Requiere modo Intermedio o superior.",
                "recomendacion": "Completa el tutorial o consulta con un supervisor."
            }
        
        # Acciones bloqueadas para intermedios
        acciones_bloqueadas_intermedio = [
            TipoAccion.DESACTIVAR_VALIDACION
        ]
        
        if modo == ModoUsuario.INTERMEDIO and accion in acciones_bloqueadas_intermedio:
            return {
                "permitido": False,
                "razon": f"⚠️ Acción '{accion.value}' requiere modo Avanzado o permisos especiales.",
                "recomendacion": "Contacta a un administrador."
            }
        
        return {
            "permitido": True,
            "razon": "",
            "recomendacion": ""
        }
    
    def obtener_estadisticas_errores_ux(self, dias: int = 7) -> Dict[str, Any]:
        """
        Obtiene estadísticas de errores UX de los últimos N días
        
        Args:
            dias: Cantidad de días hacia atrás para analizar
            
        Returns:
            Estadísticas de errores UX
        """
        desde = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        errores_recientes = [
            e for e in self.errores_ux
            if (desde - e.timestamp).days <= dias
        ]
        
        if not errores_recientes:
            return {
                "total_errores": 0,
                "errores_por_modulo": {},
                "errores_por_usuario": {},
                "acciones_mas_problematicas": []
            }
        
        # Agrupar por módulo
        errores_por_modulo = {}
        for error in errores_recientes:
            errores_por_modulo[error.modulo] = errores_por_modulo.get(error.modulo, 0) + 1
        
        # Agrupar por usuario
        errores_por_usuario = {}
        for error in errores_recientes:
            errores_por_usuario[error.usuario] = errores_por_usuario.get(error.usuario, 0) + 1
        
        # Acciones más problemáticas
        acciones_problematicas = {}
        for error in errores_recientes:
            acciones_problematicas[error.accion_intentada] = acciones_problematicas.get(error.accion_intentada, 0) + 1
        
        return {
            "total_errores": len(errores_recientes),
            "periodo_dias": dias,
            "errores_por_modulo": errores_por_modulo,
            "errores_por_usuario": errores_por_usuario,
            "acciones_mas_problematicas": sorted(
                acciones_problematicas.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def exportar_logs_ux(self, filepath: str) -> None:
        """Exporta logs UX a archivo JSON"""
        datos = {
            "timestamp_exportacion": datetime.now().isoformat(),
            "total_errores": len(self.errores_ux),
            "errores": [e.to_dict() for e in self.errores_ux]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)


# Singleton instance
_ux_guardrails_service = None

def get_ux_guardrails_service() -> UXGuardrailsService:
    """Obtiene la instancia singleton del servicio UX Guardrails"""
    global _ux_guardrails_service
    if _ux_guardrails_service is None:
        _ux_guardrails_service = UXGuardrailsService()
    return _ux_guardrails_service
