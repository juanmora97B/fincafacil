"""
Sistema de autenticación y gestión de usuarios.
Incluye registro, login y cambio de contraseña.
REFACTOR FASE 7.5: Usa inyección de PathService en lugar de acceso directo a BD paths.
"""
import sqlite3
import hashlib
import json
from typing import Optional, Tuple
from datetime import datetime
import logging

from database.services import get_path_service
from modules.utils.app_paths import get_config_file

logger = logging.getLogger(__name__)


class UsuarioManager:
    """Gestión de usuarios y autenticación"""
    
    def __init__(self, db_path: str | None = None):
        path_service = get_path_service()
        self.db_path = str(db_path or path_service.get_db_path())
        self._asegurar_tabla_usuarios()
    
    def _asegurar_tabla_usuarios(self):
        """Crea tabla de usuarios si no existe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE,
                        contraseña TEXT NOT NULL,
                        rol TEXT DEFAULT 'usuario',
                        estado TEXT DEFAULT 'activo',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_ultimo_login TIMESTAMP,
                        intentos_fallidos INTEGER DEFAULT 0,
                        bloqueado_hasta TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("Tabla usuario verificada/creada")
        except Exception as e:
            logger.error(f"Error creando tabla usuario: {e}")
            raise
    
    @staticmethod
    def _hash_contraseña(contraseña: str) -> str:
        """Hash seguro de contraseña usando SHA256"""
        return hashlib.sha256(contraseña.encode()).hexdigest()
    
    def registrar_usuario(self, nombre: str, contraseña: str, email: str | None = None) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario
        
        Returns:
            (éxito: bool, mensaje: str)
        """
        if len(nombre) < 3:
            return False, "El nombre debe tener al menos 3 caracteres"
        
        if len(contraseña) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        try:
            contraseña_hash = self._hash_contraseña(contraseña)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO usuario (nombre, contraseña, email)
                    VALUES (?, ?, ?)
                """, (nombre, contraseña_hash, email))
                conn.commit()
            
            logger.info(f"Usuario registrado: {nombre}")
            return True, "Usuario registrado exitosamente"
        
        except sqlite3.IntegrityError:
            return False, f"El usuario '{nombre}' ya existe"
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            return False, f"Error: {e}"
    
    def validar_login(self, nombre: str, contraseña: str) -> Tuple[bool, str]:
        """
        Valida credenciales de login
        
        Returns:
            (éxito: bool, mensaje: str)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, contraseña, estado, bloqueado_hasta, intentos_fallidos
                    FROM usuario WHERE nombre = ?
                """, (nombre,))
                
                resultado = cursor.fetchone()
                
                if not resultado:
                    return False, f"Usuario '{nombre}' no encontrado"
                
                usuario_id, contraseña_hash, estado, bloqueado_hasta, intentos = resultado
                
                # Verificar bloqueo temporal
                if bloqueado_hasta:
                    bloqueado_fecha = datetime.fromisoformat(bloqueado_hasta)
                    if datetime.now() < bloqueado_fecha:
                        minutos = int((bloqueado_fecha - datetime.now()).total_seconds() / 60)
                        return False, f"Cuenta bloqueada temporalmente. Intenta en {minutos} minutos"
                    else:
                        # Desbloquear
                        cursor.execute("UPDATE usuario SET bloqueado_hasta = NULL, intentos_fallidos = 0 WHERE id = ?", (usuario_id,))
                
                if estado != 'activo':
                    return False, f"Cuenta desactivada"
                
                # Validar contraseña
                contraseña_validada = self._hash_contraseña(contraseña)
                if contraseña_validada != contraseña_hash:
                    # Incrementar intentos fallidos
                    nuevos_intentos = intentos + 1
                    if nuevos_intentos >= 5:
                        # Bloquear 30 minutos
                        bloqueado_hasta = datetime.now().isoformat()
                        bloqueado_hasta = datetime.fromisoformat(bloqueado_hasta)
                        bloqueado_hasta = bloqueado_hasta.replace(minute=bloqueado_hasta.minute + 30).isoformat()
                        cursor.execute(
                            "UPDATE usuario SET intentos_fallidos = ?, bloqueado_hasta = ? WHERE id = ?",
                            (nuevos_intentos, bloqueado_hasta, usuario_id)
                        )
                        conn.commit()
                        return False, "Demasiados intentos fallidos. Cuenta bloqueada 30 minutos"
                    else:
                        cursor.execute("UPDATE usuario SET intentos_fallidos = ? WHERE id = ?", (nuevos_intentos, usuario_id))
                        conn.commit()
                        return False, f"Contraseña incorrecta ({5 - nuevos_intentos} intentos restantes)"
                
                # Login exitoso
                cursor.execute(
                    "UPDATE usuario SET fecha_ultimo_login = CURRENT_TIMESTAMP, intentos_fallidos = 0 WHERE id = ?",
                    (usuario_id,)
                )
                conn.commit()
                logger.info(f"Login exitoso: {nombre}")
                return True, "Login exitoso"
        
        except Exception as e:
            logger.error(f"Error validando login: {e}")
            return False, f"Error: {e}"
    
    def cambiar_contraseña(self, nombre: str, contraseña_actual: str, contraseña_nueva: str) -> Tuple[bool, str]:
        """Cambia la contraseña de un usuario"""
        
        # Validar nueva contraseña
        if len(contraseña_nueva) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        # Validar contraseña actual
        exito, _ = self.validar_login(nombre, contraseña_actual)
        if not exito:
            return False, "Contraseña actual incorrecta"
        
        try:
            contraseña_hash = self._hash_contraseña(contraseña_nueva)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE usuario SET contraseña = ? WHERE nombre = ?", (contraseña_hash, nombre))
                conn.commit()
            
            logger.info(f"Contraseña cambiada: {nombre}")
            return True, "Contraseña cambiada exitosamente"
        
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            return False, f"Error: {e}"
    
    def obtener_usuario_actual(self) -> Optional[dict]:
        """Retorna el diccionario del usuario actualmente logueado (desde archivo de sesión)"""
        try:
            session_file = get_config_file("session.json")
            if session_file.exists():
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    usuario_nombre = data.get('usuario')
                    
                    # Obtener datos del usuario desde BD
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT id, nombre, email, rol, estado, fecha_creacion
                            FROM usuario WHERE nombre = ?
                        """, (usuario_nombre,))
                        resultado = cursor.fetchone()
                        
                        if resultado:
                            return {
                                "id": resultado[0],
                                "nombre": resultado[1],
                                "email": resultado[2],
                                "rol": resultado[3],
                                "estado": resultado[4],
                                "fecha_creacion": resultado[5]
                            }
        except Exception as e:
            logger.warning(f"Error leyendo sesión: {e}")
        return None
    
    def db_connection(self):
        """Context manager para conexión a la base de datos"""
        import contextlib
        
        @contextlib.contextmanager
        def _connection():
            conn = sqlite3.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()
        
        return _connection()
    
    def guardar_sesion(self, nombre: str):
        """Guarda la sesión del usuario actual"""
        try:
            session_file = get_config_file("session.json")
            with open(session_file, 'w') as f:
                json.dump({'usuario': nombre, 'timestamp': datetime.now().isoformat()}, f)
            logger.info(f"Sesión guardada: {nombre}")
        except Exception as e:
            logger.error(f"Error guardando sesión: {e}")
    
    def cerrar_sesion(self):
        """Cierra la sesión actual"""
        try:
            session_file = get_config_file("session.json")
            if session_file.exists():
                session_file.unlink()
            logger.info("Sesión cerrada")
        except Exception as e:
            logger.error(f"Error cerrando sesión: {e}")
    
    def existe_algun_usuario(self) -> bool:
        """Verifica si existe al menos un usuario registrado"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM usuario")
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Error verificando usuarios: {e}")
            return False
