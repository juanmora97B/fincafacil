"""
Sistema de gestión de licencias con período de prueba de 6 meses.
"""
import sqlite3
import json
import hashlib
import string
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class LicenseManager:
    """Gestiona licencias, período de prueba y validación de fechas"""
    
    def __init__(self, db_path: str = "database/fincafacil.db"):
        self.db_path = db_path
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.license_file = self.config_dir / "license.json"
        
        # Asegurar tabla de licencias en BD
        self._asegurar_tabla_licencias()
        
        # Cargar o crear estado de licencia
        self._cargar_estado_licencia()
    
    def _asegurar_tabla_licencias(self):
        """Crea la tabla de licencias si no existe"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS licencia (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER,
                        tipo_licencia TEXT DEFAULT 'prueba',
                        fecha_inicio TEXT NOT NULL,
                        fecha_expiracion TEXT NOT NULL,
                        codigo_activacion TEXT,
                        estado TEXT DEFAULT 'activa',
                        fecha_creacion TEXT,
                        FOREIGN KEY(usuario_id) REFERENCES usuario(id)
                    )
                ''')
                conn.commit()
                logger.info("Tabla 'licencia' verificada/creada")
        except Exception as e:
            logger.error(f"Error al crear tabla de licencias: {e}")
    
    def _cargar_estado_licencia(self):
        """Carga o crea el estado de licencia desde archivo de configuración"""
        if self.license_file.exists():
            try:
                with open(self.license_file, 'r') as f:
                    self.license_data = json.load(f)
                logger.info("Estado de licencia cargado desde archivo")
            except Exception as e:
                logger.error(f"Error al cargar licencia.json: {e}")
                self.license_data = {}
        else:
            self.license_data = {}
    
    def _guardar_estado_licencia(self):
        """Guarda el estado de licencia en archivo"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(self.license_data, f, indent=2)
            logger.info("Estado de licencia guardado")
        except Exception as e:
            logger.error(f"Error al guardar licencia.json: {e}")
    
    def crear_licencia_prueba(self, usuario_id: int) -> bool:
        """
        Crea una licencia de prueba de 6 meses para un usuario.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            True si se creó exitosamente
        """
        try:
            fecha_inicio = datetime.now()
            fecha_expiracion = fecha_inicio + timedelta(days=180)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO licencia 
                    (usuario_id, tipo_licencia, fecha_inicio, fecha_expiracion, 
                     estado, fecha_creacion)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    usuario_id,
                    'prueba',
                    fecha_inicio.isoformat(),
                    fecha_expiracion.isoformat(),
                    'activa',
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            logger.info(f"Licencia de prueba creada para usuario {usuario_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error al crear licencia de prueba: {e}")
            return False
    
    def generar_codigo_activacion(self, usuario_id: int) -> str:
        """
        Genera un código de activación único.
        Formato: FINCA-XXXXX-XXXXX-XXXXX (20 caracteres)
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Código de activación
        """
        # Generar código aleatorio
        charset = string.ascii_uppercase + string.digits
        parte1 = ''.join(random.choices(charset, k=5))
        parte2 = ''.join(random.choices(charset, k=5))
        parte3 = ''.join(random.choices(charset, k=5))
        
        codigo = f"FINCA-{parte1}-{parte2}-{parte3}"
        
        # Guardar en JSON para validación offline
        if "codigos_registrados" not in self.license_data:
            self.license_data["codigos_registrados"] = {}
        
        self.license_data["codigos_registrados"][codigo] = {
            "usuario_id": usuario_id,
            "fecha_generacion": datetime.now().isoformat(),
            "valido": True
        }
        
        self._guardar_estado_licencia()
        return codigo
    
    def validar_codigo_activacion(self, codigo: str) -> tuple[bool, str]:
        """
        Valida un código de activación.
        
        Args:
            codigo: Código a validar
            
        Returns:
            (True, "Mensaje") si es válido, (False, "Error") si no
        """
        if "codigos_registrados" not in self.license_data:
            return False, "Código inválido"
        
        if codigo not in self.license_data["codigos_registrados"]:
            return False, "Código no registrado"
        
        código_data = self.license_data["codigos_registrados"][codigo]
        
        if not código_data.get("valido", False):
            return False, "Código ya fue utilizado"
        
        return True, "Código válido"
    
    def activar_licencia(self, usuario_id: int, codigo_activacion: str) -> tuple[bool, str]:
        """
        Activa una licencia permanente con un código.
        
        Args:
            usuario_id: ID del usuario
            codigo_activacion: Código generado
            
        Returns:
            (True, "Mensaje") si se activó, (False, "Error") si fallo
        """
        es_valido, msg = self.validar_codigo_activacion(codigo_activacion)
        
        if not es_valido:
            return False, msg
        
        try:
            # Marcar código como utilizado
            self.license_data["codigos_registrados"][codigo_activacion]["valido"] = False
            self.license_data["codigos_registrados"][codigo_activacion]["fecha_uso"] = datetime.now().isoformat()
            
            # Crear licencia permanente en BD
            fecha_inicio = datetime.now()
            fecha_expiracion = fecha_inicio + timedelta(days=365)  # 1 año desde activación
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE licencia 
                    SET tipo_licencia = ?, fecha_expiracion = ?, 
                        codigo_activacion = ?, fecha_creacion = ?
                    WHERE usuario_id = ? AND tipo_licencia = ?
                ''', (
                    'premium',
                    fecha_expiracion.isoformat(),
                    codigo_activacion,
                    datetime.now().isoformat(),
                    usuario_id,
                    'prueba'
                ))
                
                if cursor.rowcount == 0:
                    # Si no hay licencia de prueba, crear una nueva
                    cursor.execute('''
                        INSERT INTO licencia 
                        (usuario_id, tipo_licencia, fecha_inicio, fecha_expiracion,
                         codigo_activacion, estado, fecha_creacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        usuario_id,
                        'premium',
                        fecha_inicio.isoformat(),
                        fecha_expiracion.isoformat(),
                        codigo_activacion,
                        'activa',
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
            
            self._guardar_estado_licencia()
            logger.info(f"Licencia premium activada para usuario {usuario_id}")
            return True, "Licencia activada exitosamente"
            
        except Exception as e:
            logger.error(f"Error al activar licencia: {e}")
            return False, f"Error: {str(e)}"
    
    def obtener_estado_licencia(self, usuario_id: int) -> dict:
        """
        Obtiene el estado actual de la licencia.
        
        Returns:
            Dict con: tipo, días_restantes, fecha_expiracion, estado
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT tipo_licencia, fecha_expiracion, estado
                    FROM licencia
                    WHERE usuario_id = ? AND estado = 'activa'
                    ORDER BY fecha_creacion DESC
                    LIMIT 1
                ''', (usuario_id,))
                
                resultado = cursor.fetchone()
                
                if not resultado:
                    return {
                        "tipo": "sin_licencia",
                        "dias_restantes": 0,
                        "fecha_expiracion": None,
                        "estado": "inactiva"
                    }
                
                tipo_licencia, fecha_exp_str, estado = resultado
                fecha_expiracion = datetime.fromisoformat(fecha_exp_str)
                dias_restantes = (fecha_expiracion - datetime.now()).days
                
                return {
                    "tipo": tipo_licencia,
                    "dias_restantes": max(0, dias_restantes),
                    "fecha_expiracion": fecha_exp_str,
                    "estado": "activa" if dias_restantes > 0 else "expirada"
                }
                
        except Exception as e:
            logger.error(f"Error al obtener estado de licencia: {e}")
            return {
                "tipo": "error",
                "dias_restantes": 0,
                "fecha_expiracion": None,
                "estado": "error"
            }
    
    def es_licencia_valida(self, usuario_id: int) -> bool:
        """
        Verifica si la licencia es válida (no expirada).
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            True si la licencia está activa y no expiró
        """
        estado = self.obtener_estado_licencia(usuario_id)
        return estado["estado"] == "activa" and estado["dias_restantes"] > 0
    
    def detectar_manipulacion_fecha(self) -> bool:
        """
        Detecta si el usuario manipuló la fecha del sistema.
        Valida contra timestamps guardados en el archivo de licencia.
        
        Returns:
            True si se detectó manipulación
        """
        try:
            if not self.license_file.exists():
                return False
            
            # Obtener timestamp de creación del archivo
            import os
            file_stat = os.stat(self.license_file)
            archivo_ctime = datetime.fromtimestamp(file_stat.st_ctime)
            ahora = datetime.now()
            
            # Si el archivo es más antiguo que "ahora", algo está mal
            if file_stat.st_mtime > ahora.timestamp():
                logger.warning("Posible manipulación de fecha detectada (mtime > ahora)")
                return True
            
            # Comparar con fecha en JSON si existe
            if "fecha_creacion_original" in self.license_data:
                fecha_original = datetime.fromisoformat(self.license_data["fecha_creacion_original"])
                # Si la fecha actual es anterior a la fecha original, hubo manipulación
                if ahora < fecha_original:
                    logger.warning("Posible manipulación de fecha (fecha actual < fecha original)")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error al detectar manipulación de fecha: {e}")
            return False
    
    def bloquear_licencia(self, usuario_id: int, razon: str = "Manipulación detectada"):
        """
        Bloquea una licencia.
        
        Args:
            usuario_id: ID del usuario
            razon: Razón del bloqueo
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE licencia 
                    SET estado = 'bloqueada'
                    WHERE usuario_id = ?
                ''', (usuario_id,))
                conn.commit()
            
            logger.warning(f"Licencia bloqueada para usuario {usuario_id}: {razon}")
            
        except Exception as e:
            logger.error(f"Error al bloquear licencia: {e}")
