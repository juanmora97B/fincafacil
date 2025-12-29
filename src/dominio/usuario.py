"""
MODELO DE USUARIO - FincaFácil
==============================

Define la estructura de usuarios y su relación con roles/permisos.
Incluye auditoría de cambios sensibles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UsuarioEstado(Enum):
    """Estados posibles de un usuario"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    BLOQUEADO = "bloqueado"
    
    def __str__(self):
        return self.value


@dataclass
class UsuarioRol:
    """Relación Usuario-Rol"""
    usuario_id: int
    rol: str  # "Administrador", "Operador", "Consulta"
    fecha_asignacion: datetime = field(default_factory=datetime.now)
    asignado_por: Optional[str] = None  # Usuario que asignó el rol
    motivo: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "usuario_id": self.usuario_id,
            "rol": self.rol,
            "fecha_asignacion": self.fecha_asignacion.isoformat(),
            "asignado_por": self.asignado_por,
            "motivo": self.motivo,
        }


@dataclass
class Usuario:
    """Modelo de Usuario"""
    id: int
    nombre: str
    email: str
    rol: str  # Rol principal
    estado: UsuarioEstado = UsuarioEstado.ACTIVO
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_ultimo_acceso: Optional[datetime] = None
    intentos_fallidos: int = 0
    bloqueado_hasta: Optional[datetime] = None
    notas: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte a diccionario (sin datos sensibles)"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "estado": self.estado.value,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_ultimo_acceso": self.fecha_ultimo_acceso.isoformat() if self.fecha_ultimo_acceso else None,
        }
    
    def esta_activo(self) -> bool:
        """Verifica si el usuario está activo"""
        if self.estado != UsuarioEstado.ACTIVO:
            return False
        
        if self.bloqueado_hasta:
            if datetime.now() < self.bloqueado_hasta:
                return False
        
        return True
    
    def registrar_acceso(self):
        """Registra el último acceso del usuario"""
        self.fecha_ultimo_acceso = datetime.now()
        self.intentos_fallidos = 0
    
    def registrar_intento_fallido(self):
        """Registra un intento fallido de login"""
        self.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos durante 15 minutos
        if self.intentos_fallidos >= 5:
            from datetime import timedelta
            self.bloqueado_hasta = datetime.now() + timedelta(minutes=15)
    
    def desbloquear(self):
        """Desbloquea el usuario"""
        self.bloqueado_hasta = None
        self.intentos_fallidos = 0


@dataclass
class EventoAuditoria:
    """Evento de auditoría para acciones sensibles"""
    timestamp: datetime = field(default_factory=datetime.now)
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
    modulo: Optional[str] = None  # "ventas", "nomina", "cierre", etc.
    accion: Optional[str] = None  # "CREAR", "EDITAR", "ELIMINAR", "PAGAR"
    entidad: Optional[str] = None  # Descripción de qué se modificó
    entidad_id: Optional[int] = None  # ID del registro afectado
    resultado: str = "OK"  # "OK", "ERROR", "DENEGADO"
    detalles: Optional[dict] = None  # Datos adicionales (antes/después)
    ip_address: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario_nombre,
            "modulo": self.modulo,
            "accion": self.accion,
            "entidad": self.entidad,
            "entidad_id": self.entidad_id,
            "resultado": self.resultado,
            "detalles": self.detalles,
            "ip_address": self.ip_address,
        }


class UsuarioRepository:
    """Repositorio para gestionar usuarios (interfaz)"""
    
    def crear_usuario(self, nombre: str, email: str, rol: str) -> Usuario:
        """Crea un nuevo usuario"""
        raise NotImplementedError()
    
    def obtener_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        raise NotImplementedError()
    
    def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email"""
        raise NotImplementedError()
    
    def actualizar_usuario(self, usuario: Usuario) -> bool:
        """Actualiza un usuario"""
        raise NotImplementedError()
    
    def listar_usuarios(self, estado: Optional[UsuarioEstado] = None) -> List[Usuario]:
        """Lista todos los usuarios"""
        raise NotImplementedError()
    
    def asignar_rol(self, usuario_id: int, rol: str, asignado_por: str, motivo: Optional[str] = None) -> bool:
        """Asigna un rol a un usuario"""
        raise NotImplementedError()
    
    def obtener_roles_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene todos los roles de un usuario"""
        raise NotImplementedError()
    
    def registrar_evento_auditoria(self, evento: EventoAuditoria) -> bool:
        """Registra un evento de auditoría"""
        raise NotImplementedError()
    
    def obtener_auditoria(self, usuario_id: Optional[int] = None, modulo: Optional[str] = None, dias: int = 30) -> List[EventoAuditoria]:
        """Obtiene eventos de auditoría filtrados"""
        raise NotImplementedError()
