"""
Capa de Servicio - Dominio Configuración
FASE 9.0.3 - Encapsulación Catálogo Calidad Animal

Responsabilidad: Orquestar reglas de negocio, validaciones y delegación al repository.
Sin SQL directo, sin acceso a UI, sin conocimiento de CustomTkinter.

Métodos para catálogo Calidad Animal (fase inicial).
Patrón: Service pattern (validación + orchestración).
"""

from typing import List, Dict, Optional, Tuple, Any
from .configuracion_repository import ConfiguracionRepository
import sqlite3


class ConfiguracionService:
    """
    Service para dominio Configuración (inicialmente Calidad Animal).
    
    Responsabilidades:
    1. Validaciones de negocio (campos requeridos, uniqueness, existencia)
    2. Orchestración (caja negra para repository)
    3. Normalización de retornos (Dict siempre con todos los campos)
    4. Conversión de excepciones en mensajes amigables
    
    Patrón: Inyección de dependencias (repository mockeable para tests).
    """
    
    def __init__(self, repository: Optional[ConfiguracionRepository] = None):
        """
        Inicializa service con inyección de dependencia.
        
        Args:
            repository: ConfiguracionRepository (optional para testing)
        """
        self._repo = repository or ConfiguracionRepository()
    
    # ============================================================
    # LECTURA - Calidad Animal
    # ============================================================
    
    def listar_calidades(self) -> List[Dict[str, str]]:
        """
        Obtiene lista de todas las calidades normalizadas.
        
        Returns:
            List[Dict]: [{'codigo': str, 'descripcion': str, 'comentario': str}, ...]
            
        Normalización:
        - comentario None → ""
        - Todos los valores como str
        - Ordenado por código
        """
        try:
            calidades = self._repo.listar_calidades()
            # Normalizar: None → ""
            result = [
                {
                    'codigo': str(cal.get('codigo', '')).strip(),
                    'descripcion': str(cal.get('descripcion', '')).strip(),
                    'comentario': str(cal.get('comentario', '') or '').strip()
                }
                for cal in calidades
            ]
            # Ordenar por código para consistencia
            return sorted(result, key=lambda x: x['codigo'])
        except Exception as e:
            # Log y re-lanzar como ValueError genérico
            raise ValueError(f"Error al listar calidades: {str(e)}")
    
    def obtener_calidad(self, codigo: str) -> Optional[Dict[str, str]]:
        """
        Obtiene detalle de una calidad.
        
        Args:
            codigo: Código de la calidad
            
        Returns:
            Dict normalizado o None si no existe
        """
        try:
            calidad = self._repo.obtener_calidad(codigo)
            if not calidad:
                return None
            return {
                'codigo': str(calidad.get('codigo', '')).strip(),
                'descripcion': str(calidad.get('descripcion', '')).strip(),
                'comentario': str(calidad.get('comentario', '') or '').strip()
            }
        except Exception as e:
            raise ValueError(f"Error al obtener calidad: {str(e)}")
    
    # ============================================================
    # ESCRITURA - Calidad Animal
    # ============================================================
    
    def crear_calidad(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str] = None
    ) -> None:
        """
        Crea una nueva calidad con validaciones.
        
        Args:
            codigo: Código único (requerido)
            descripcion: Descripción (requerido)
            comentario: Comentario (opcional)
            
        Raises:
            ValueError: Si validación falla (código vacío, ya existe, desc vacía)
            
        Validaciones:
        1. Código no vacío
        2. Código no existe (prevalidación preventiva)
        3. Descripción no vacía
        """
        # VALIDACIÓN 1: Campos requeridos
        codigo = str(codigo).strip() if codigo else ""
        descripcion = str(descripcion).strip() if descripcion else ""
        
        if not codigo:
            raise ValueError("El código es obligatorio")
        
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        
        # VALIDACIÓN 2: No existe
        if self._repo.existe_calidad(codigo):
            raise ValueError(f"Ya existe una calidad con código '{codigo}'")
        
        # VALIDACIÓN 3: Comentario
        comentario = (str(comentario).strip() if comentario else "") or None
        
        # INSERCIÓN
        try:
            self._repo.crear_calidad(codigo, descripcion, comentario)
        except sqlite3.IntegrityError:
            # Fallback si prevalidación falla
            raise ValueError(f"Error: Código '{codigo}' duplicado")
        except Exception as e:
            raise ValueError(f"Error al crear calidad: {str(e)}")
    
    def actualizar_calidad(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str] = None
    ) -> None:
        """
        Actualiza una calidad existente.
        
        Args:
            codigo: Código de la calidad a actualizar
            descripcion: Nueva descripción (requerido)
            comentario: Nuevo comentario (opcional)
            
        Raises:
            ValueError: Si validación falla (código no existe, desc vacía, etc.)
            
        Validaciones:
        1. Código existe
        2. Descripción no vacía
        """
        # VALIDACIÓN 1: Código existe
        codigo = str(codigo).strip() if codigo else ""
        
        if not codigo:
            raise ValueError("El código es obligatorio")
        
        if not self._repo.existe_calidad(codigo):
            raise ValueError(f"No existe calidad con código '{codigo}'")
        
        # VALIDACIÓN 2: Descripción
        descripcion = str(descripcion).strip() if descripcion else ""
        
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        
        # VALIDACIÓN 3: Comentario
        comentario = (str(comentario).strip() if comentario else "") or None
        
        # ACTUALIZACIÓN
        try:
            self._repo.actualizar_calidad(codigo, descripcion, comentario)
        except Exception as e:
            raise ValueError(f"Error al actualizar calidad: {str(e)}")
    
    def eliminar_calidad(self, codigo: str) -> None:
        """
        Elimina una calidad.
        
        Args:
            codigo: Código de la calidad a eliminar
            
        Raises:
            ValueError: Si no existe
            
        Validaciones:
        1. Código existe
        """
        codigo = str(codigo).strip() if codigo else ""
        
        if not codigo:
            raise ValueError("El código es obligatorio")
        
        if not self._repo.existe_calidad(codigo):
            raise ValueError(f"No existe calidad con código '{codigo}'")
        
        try:
            self._repo.eliminar_calidad(codigo)
        except Exception as e:
            raise ValueError(f"Error al eliminar calidad: {str(e)}")
    
    # ============================================================
    # ESCRITURA BULK - Calidad Animal
    # ============================================================
    
    def importar_calidades_bulk(
        self,
        calidades: List[Dict[str, Any]]
    ) -> Tuple[int, List[str]]:
        """
        Importa múltiples calidades desde lista (e.g., Excel).
        
        Args:
            calidades: List[Dict] con 'codigo', 'descripcion', 'comentario'
            
        Returns:
            Tuple: (importados_exitosos: int, errores: List[str])
            
        Notas:
        - Intenta insertar todos, reporta errores por fila
        - Errores no abortarán el flujo
        - Cada error incluye índice de fila
        - Validación básica por cada registro
        """
        importados = 0
        errores = []
        
        if not calidades:
            return (0, [])
        
        for idx, cal in enumerate(calidades, start=1):
            try:
                # Extrae datos
                codigo = str(cal.get('codigo', '')).strip()
                descripcion = str(cal.get('descripcion', '')).strip()
                comentario = str(cal.get('comentario', '') or '').strip() or None
                
                # Validaciones básicas
                if not codigo:
                    raise ValueError("Código requerido")
                
                if not descripcion:
                    raise ValueError("Descripción requerida")
                
                if self._repo.existe_calidad(codigo):
                    raise ValueError("Código duplicado")
                
                # Inserción
                self._repo.crear_calidad(codigo, descripcion, comentario)
                importados += 1
                
            except sqlite3.IntegrityError as e:
                errores.append(f"Fila {idx}: Código duplicado")
            except ValueError as e:
                errores.append(f"Fila {idx}: {str(e)}")
            except Exception as e:
                errores.append(f"Fila {idx}: Error inesperado: {str(e)}")
        
        return (importados, errores)

    # ============================================================
    # CAUSA DE MUERTE
    # ============================================================

    def listar_causas_muerte(self) -> List[Dict[str, str]]:
        """Lista causas activas normalizadas."""
        try:
            filas = self._repo.listar_causas_muerte()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip(),
                    'descripcion': str(f.get('descripcion', '')).strip(),
                    'tipo_causa': str(f.get('tipo_causa', '') or '').strip(),
                    'comentario': str(f.get('comentario', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar causas: {str(e)}")

    def crear_causa_muerte(
        self,
        codigo: str,
        descripcion: str,
        tipo_causa: Optional[str] = None,
        comentario: Optional[str] = None,
        estado: str = "Activo",
    ) -> None:
        """Crea nueva causa validando campos y estado permitido."""
        # Validaciones
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        tipo_causa = (str(tipo_causa or '').strip() or None)
        comentario = (str(comentario or '').strip() or None)
        estado = str(estado or '').strip() or "Activo"

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        if self._repo.existe_causa_muerte(codigo):
            raise ValueError(f"Ya existe una causa con código '{codigo}'")

        try:
            self._repo.crear_causa_muerte(codigo, descripcion, tipo_causa, comentario, estado)
        except sqlite3.IntegrityError:
            raise ValueError(f"Código duplicado: '{codigo}'")
        except Exception as e:
            raise ValueError(f"Error al crear causa: {str(e)}")

    def actualizar_causa_muerte(
        self,
        codigo: str,
        descripcion: str,
        tipo_causa: Optional[str] = None,
        comentario: Optional[str] = None,
    ) -> None:
        """Actualiza campos de una causa existente."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        tipo_causa = (str(tipo_causa or '').strip() or None)
        comentario = (str(comentario or '').strip() or None)

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        if not self._repo.existe_causa_muerte(codigo):
            raise ValueError(f"No existe causa con código '{codigo}'")

        try:
            self._repo.actualizar_causa_muerte(codigo, descripcion, tipo_causa, comentario)
        except Exception as e:
            raise ValueError(f"Error al actualizar causa: {str(e)}")

    def cambiar_estado_causa_muerte(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva causa de muerte (soft delete por estado)."""
        codigo = str(codigo or '').strip()
        nuevo_estado = str(nuevo_estado or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not self._repo.existe_causa_muerte(codigo):
            raise ValueError(f"No existe causa con código '{codigo}'")

        estados_validos = {"Activo", "Inactivo"}
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_causa_muerte(codigo, nuevo_estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado: {str(e)}")

    # ============================================================
    # DIAGNÓSTICOS
    # ============================================================

    def listar_diagnosticos(self) -> List[Dict[str, str]]:
        """Lista diagnósticos activos normalizados."""
        try:
            filas = self._repo.listar_diagnosticos()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip(),
                    'descripcion': str(f.get('descripcion', '')).strip(),
                    'tipo_diagnostico': str(f.get('tipo_diagnostico', '') or '').strip(),
                    'comentario': str(f.get('comentario', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar diagnósticos: {str(e)}")

    def crear_diagnostico(
        self,
        codigo: str,
        descripcion: str,
        tipo_diagnostico: Optional[str] = None,
        comentario: Optional[str] = None,
        estado: str = "Activo",
    ) -> None:
        """Crea nuevo diagnóstico validando campos y estado permitido."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        tipo_diagnostico = (str(tipo_diagnostico or '').strip() or None)
        comentario = (str(comentario or '').strip() or None)
        estado = str(estado or '').strip() or "Activo"

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        if self._repo.existe_diagnostico(codigo):
            raise ValueError(f"Ya existe un diagnóstico con código '{codigo}'")

        try:
            self._repo.crear_diagnostico(codigo, descripcion, tipo_diagnostico, comentario, estado)
        except sqlite3.IntegrityError:
            raise ValueError(f"Código duplicado: '{codigo}'")
        except Exception as e:
            raise ValueError(f"Error al crear diagnóstico: {str(e)}")

    def actualizar_diagnostico(
        self,
        codigo: str,
        descripcion: str,
        tipo_diagnostico: Optional[str] = None,
        comentario: Optional[str] = None,
    ) -> None:
        """Actualiza campos de un diagnóstico existente."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        tipo_diagnostico = (str(tipo_diagnostico or '').strip() or None)
        comentario = (str(comentario or '').strip() or None)

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        if not self._repo.existe_diagnostico(codigo):
            raise ValueError(f"No existe diagnóstico con código '{codigo}'")

        try:
            self._repo.actualizar_diagnostico(codigo, descripcion, tipo_diagnostico, comentario)
        except Exception as e:
            raise ValueError(f"Error al actualizar diagnóstico: {str(e)}")

    def cambiar_estado_diagnostico(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva diagnóstico (soft delete por estado)."""
        codigo = str(codigo or '').strip()
        nuevo_estado = str(nuevo_estado or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not self._repo.existe_diagnostico(codigo):
            raise ValueError(f"No existe diagnóstico con código '{codigo}'")

        estados_validos = {"Activo", "Inactivo"}
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_diagnostico(codigo, nuevo_estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado: {str(e)}")

    # ============================================================
    # PROCEDENCIA
    # ============================================================

    def listar_procedencias(self) -> List[Dict[str, str]]:
        """Lista procedencias activas normalizadas."""
        try:
            filas = self._repo.listar_procedencias()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip(),
                    'descripcion': str(f.get('descripcion', '')).strip(),
                    'tipo_procedencia': str(f.get('tipo_procedencia', '') or '').strip(),
                    'ubicacion': str(f.get('ubicacion', '') or '').strip(),
                    'comentario': str(f.get('comentario', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar procedencias: {str(e)}")

    def obtener_procedencia(self, codigo: str) -> Optional[Dict[str, str]]:
        """Obtiene una procedencia por código (para edición)."""
        try:
            proc = self._repo.obtener_procedencia(codigo)
            if not proc:
                return None
            return {
                'codigo': str(proc.get('codigo', '')).strip(),
                'descripcion': str(proc.get('descripcion', '')).strip(),
                'tipo_procedencia': str(proc.get('tipo_procedencia', '') or '').strip(),
                'ubicacion': str(proc.get('ubicacion', '') or '').strip(),
                'comentario': str(proc.get('comentario', '') or '').strip(),
                'estado': str(proc.get('estado', '') or '').strip(),
            }
        except Exception as e:
            raise ValueError(f"Error al obtener procedencia: {str(e)}")

    def crear_procedencia(
        self,
        codigo: str,
        descripcion: str,
        tipo_procedencia: Optional[str] = None,
        ubicacion: Optional[str] = None,
        comentario: Optional[str] = None,
        estado: str = "Activo",
    ) -> None:
        """Crea nueva procedencia validando campos y estado permitido."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        tipo_procedencia = (str(tipo_procedencia or '').strip() or None)
        ubicacion = (str(ubicacion or '').strip() or None)
        comentario = (str(comentario or '').strip() or None)
        estado = str(estado or '').strip() or "Activo"

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        if self._repo.existe_procedencia(codigo):
            raise ValueError(f"Ya existe una procedencia con código '{codigo}'")

        try:
            self._repo.crear_procedencia(codigo, descripcion, tipo_procedencia, ubicacion, comentario, estado)
        except sqlite3.IntegrityError:
            raise ValueError(f"Código duplicado: '{codigo}'")
        except Exception as e:
            raise ValueError(f"Error al crear procedencia: {str(e)}")

    def actualizar_procedencia(
        self,
        codigo: str,
        descripcion: str,
        tipo_procedencia: Optional[str] = None,
        ubicacion: Optional[str] = None,
        comentario: Optional[str] = None,
    ) -> None:
        """Actualiza campos de una procedencia existente."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        tipo_procedencia = (str(tipo_procedencia or '').strip() or None)
        ubicacion = (str(ubicacion or '').strip() or None)
        comentario = (str(comentario or '').strip() or None)

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        if not self._repo.existe_procedencia(codigo):
            raise ValueError(f"No existe procedencia con código '{codigo}'")

        try:
            self._repo.actualizar_procedencia(codigo, descripcion, tipo_procedencia, ubicacion, comentario)
        except Exception as e:
            raise ValueError(f"Error al actualizar procedencia: {str(e)}")

    def cambiar_estado_procedencia(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva procedencia (soft delete por estado)."""
        codigo = str(codigo or '').strip()
        nuevo_estado = str(nuevo_estado or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not self._repo.existe_procedencia(codigo):
            raise ValueError(f"No existe procedencia con código '{codigo}'")

        estados_validos = {"Activo", "Inactivo"}
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_procedencia(codigo, nuevo_estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado: {str(e)}")

    # ============================================================
    # MOTIVOS DE VENTA
    # ============================================================

    def listar_motivos_venta(self) -> List[Dict[str, str]]:
        """Lista motivos de venta normalizados (incluye estado)."""
        try:
            filas = self._repo.listar_motivos_venta()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip(),
                    'descripcion': str(f.get('descripcion', '')).strip(),
                    'comentario': str(f.get('comentario', '') or '').strip(),
                    'estado': str(f.get('estado', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar motivos de venta: {str(e)}")

    def obtener_motivo_venta(self, codigo: str) -> Optional[Dict[str, str]]:
        """Obtiene un motivo de venta por código."""
        try:
            motivo = self._repo.obtener_motivo_venta(codigo)
            if not motivo:
                return None
            return {
                'codigo': str(motivo.get('codigo', '')).strip(),
                'descripcion': str(motivo.get('descripcion', '')).strip(),
                'comentario': str(motivo.get('comentario', '') or '').strip(),
                'estado': str(motivo.get('estado', '') or '').strip(),
            }
        except Exception as e:
            raise ValueError(f"Error al obtener motivo de venta: {str(e)}")

    def existe_motivo_venta(self, codigo: str) -> bool:
        """Revisa existencia de motivo por código."""
        codigo = str(codigo or '').strip()
        if not codigo:
            return False
        try:
            return self._repo.existe_motivo_venta(codigo)
        except Exception as e:
            raise ValueError(f"Error al validar existencia: {str(e)}")

    def crear_motivo_venta(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str] = None,
        estado: str = "Activo",
    ) -> None:
        """Crea un motivo de venta validando campos y estado."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        comentario = (str(comentario or '').strip() or None)
        estado = str(estado or '').strip() or "Activo"

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        if self._repo.existe_motivo_venta(codigo):
            raise ValueError(f"Ya existe un motivo con código '{codigo}'")

        try:
            self._repo.crear_motivo_venta(codigo, descripcion, comentario, estado)
        except sqlite3.IntegrityError:
            raise ValueError(f"Código duplicado: '{codigo}'")
        except Exception as e:
            raise ValueError(f"Error al crear motivo de venta: {str(e)}")

    def actualizar_motivo_venta(
        self,
        codigo: str,
        descripcion: str,
        comentario: Optional[str] = None,
    ) -> None:
        """Actualiza campos de un motivo existente."""
        codigo = str(codigo or '').strip()
        descripcion = str(descripcion or '').strip()
        comentario = (str(comentario or '').strip() or None)

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        if not self._repo.existe_motivo_venta(codigo):
            raise ValueError(f"No existe motivo con código '{codigo}'")

        try:
            self._repo.actualizar_motivo_venta(codigo, descripcion, comentario)
        except Exception as e:
            raise ValueError(f"Error al actualizar motivo de venta: {str(e)}")

    def cambiar_estado_motivo_venta(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva motivo de venta (soft delete por estado)."""
        codigo = str(codigo or '').strip()
        nuevo_estado = str(nuevo_estado or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not self._repo.existe_motivo_venta(codigo):
            raise ValueError(f"No existe motivo con código '{codigo}'")

        estados_validos = {"Activo", "Inactivo"}
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_motivo_venta(codigo, nuevo_estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado: {str(e)}")

    # ============================================================
    # RAZAS
    # ============================================================

    def listar_razas(self) -> List[Dict[str, str]]:
        """Lista razas activas normalizadas."""
        try:
            filas = self._repo.listar_razas()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip(),
                    'nombre': str(f.get('nombre', '')).strip(),
                    'tipo_ganado': str(f.get('tipo_ganado', '') or '').strip(),
                    'especie': str(f.get('especie', '') or '').strip(),
                    'descripcion': str(f.get('descripcion', '') or '').strip(),
                    'estado': str(f.get('estado', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar razas: {str(e)}")

    def obtener_raza(self, codigo: str) -> Optional[Dict[str, str]]:
        """Obtiene una raza por código."""
        try:
            raza = self._repo.obtener_raza(codigo)
            if not raza:
                return None
            return {
                'codigo': str(raza.get('codigo', '')).strip(),
                'nombre': str(raza.get('nombre', '')).strip(),
                'tipo_ganado': str(raza.get('tipo_ganado', '') or '').strip(),
                'especie': str(raza.get('especie', '') or '').strip(),
                'descripcion': str(raza.get('descripcion', '') or '').strip(),
                'estado': str(raza.get('estado', '') or '').strip(),
            }
        except Exception as e:
            raise ValueError(f"Error al obtener raza: {str(e)}")

    def existe_raza(self, codigo: str) -> bool:
        """Revisa existencia de raza por código."""
        codigo = str(codigo or '').strip()
        if not codigo:
            return False
        try:
            return self._repo.existe_raza(codigo)
        except Exception as e:
            raise ValueError(f"Error al validar existencia: {str(e)}")

    def crear_raza(
        self,
        codigo: str,
        nombre: str,
        tipo_ganado: Optional[str] = None,
        especie: Optional[str] = None,
        descripcion: Optional[str] = None,
        estado: str = "Activo",
    ) -> None:
        """Crea una raza validando campos y estado."""
        codigo = str(codigo or '').strip()
        nombre = str(nombre or '').strip()
        tipo_ganado = (str(tipo_ganado or '').strip() or None)
        especie = (str(especie or '').strip() or None)
        descripcion = (str(descripcion or '').strip() or None)
        estado = str(estado or '').strip() or "Activo"

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        if self._repo.existe_raza(codigo):
            raise ValueError(f"Ya existe una raza con código '{codigo}'")

        try:
            self._repo.crear_raza(codigo, nombre, tipo_ganado, especie, descripcion, estado)
        except sqlite3.IntegrityError:
            raise ValueError(f"Código duplicado: '{codigo}'")
        except Exception as e:
            raise ValueError(f"Error al crear raza: {str(e)}")

    def actualizar_raza(
        self,
        codigo: str,
        nombre: str,
        tipo_ganado: Optional[str] = None,
        especie: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> None:
        """Actualiza campos de una raza existente."""
        codigo = str(codigo or '').strip()
        nombre = str(nombre or '').strip()
        tipo_ganado = (str(tipo_ganado or '').strip() or None)
        especie = (str(especie or '').strip() or None)
        descripcion = (str(descripcion or '').strip() or None)

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not self._repo.existe_raza(codigo):
            raise ValueError(f"No existe raza con código '{codigo}'")

        try:
            self._repo.actualizar_raza(codigo, nombre, tipo_ganado, especie, descripcion)
        except Exception as e:
            raise ValueError(f"Error al actualizar raza: {str(e)}")

    def cambiar_estado_raza(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva raza (soft delete por estado)."""
        codigo = str(codigo or '').strip()
        nuevo_estado = str(nuevo_estado or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not self._repo.existe_raza(codigo):
            raise ValueError(f"No existe raza con código '{codigo}'")

        estados_validos = {"Activo", "Inactivo"}
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_raza(codigo, nuevo_estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado: {str(e)}")

    # ============================================================
    # EMPLEADOS (BASE)
    # ============================================================
    # Empleados (SIMPLIFIED scope - base fields only)
    # ============================================================

    def listar_empleados_activos(self) -> List[Dict[str, Any]]:
        """Lista empleados activos normalizados."""
        try:
            filas = self._repo.listar_empleados_activos()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip(),
                    'numero_identificacion': str(f.get('numero_identificacion', '')).strip(),
                    'nombres': str(f.get('nombres', '')).strip(),
                    'apellidos': str(f.get('apellidos', '')).strip(),
                    'cargo': str(f.get('cargo', '') or '').strip(),
                    'id_finca': f.get('id_finca'),
                    'estado': str(f.get('estado', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar empleados: {str(e)}")

    def obtener_empleado(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un empleado por código."""
        try:
            empleado = self._repo.obtener_empleado(codigo)
            if not empleado:
                return None
            return {
                'codigo': str(empleado.get('codigo', '')).strip(),
                'numero_identificacion': str(empleado.get('numero_identificacion', '')).strip(),
                'nombres': str(empleado.get('nombres', '')).strip(),
                'apellidos': str(empleado.get('apellidos', '')).strip(),
                'cargo': str(empleado.get('cargo', '') or '').strip(),
                'id_finca': empleado.get('id_finca'),
                'estado': str(empleado.get('estado', '') or '').strip(),
            }
        except Exception as e:
            raise ValueError(f"Error al obtener empleado: {str(e)}")

    def existe_empleado_por_documento(self, numero_identificacion: str) -> bool:
        """Revisa existencia por documento."""
        numero_identificacion = str(numero_identificacion or '').strip()
        if not numero_identificacion:
            return False
        try:
            return self._repo.existe_empleado(numero_identificacion)
        except Exception as e:
            raise ValueError(f"Error al validar existencia: {str(e)}")

    def existe_codigo_empleado(self, codigo: str) -> bool:
        """Revisa existencia por código."""
        codigo = str(codigo or '').strip()
        if not codigo:
            return False
        try:
            return self._repo.existe_codigo_empleado(codigo)
        except Exception as e:
            raise ValueError(f"Error al validar existencia: {str(e)}")

    def crear_empleado(
        self,
        codigo: str,
        numero_identificacion: str,
        nombres: str,
        apellidos: str,
        cargo: str,
        id_finca: Optional[int] = None,
        estado: str = "Activo",
    ) -> None:
        """Crea un empleado (base) validando campos."""
        codigo = str(codigo or '').strip()
        numero_identificacion = str(numero_identificacion or '').strip()
        nombres = str(nombres or '').strip()
        apellidos = str(apellidos or '').strip()
        cargo = str(cargo or '').strip()
        estado = str(estado or '').strip() or "Activo"

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not numero_identificacion:
            raise ValueError("El número de identificación es obligatorio")
        if not nombres:
            raise ValueError("Los nombres son obligatorios")
        if not apellidos:
            raise ValueError("Los apellidos son obligatorios")
        if not cargo:
            raise ValueError("El cargo es obligatorio")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        if self._repo.existe_codigo_empleado(codigo):
            raise ValueError(f"Ya existe un empleado con código '{codigo}'")

        if self._repo.existe_empleado(numero_identificacion):
            raise ValueError(f"Ya existe un empleado con identificación '{numero_identificacion}'")

        try:
            self._repo.crear_empleado_base(codigo, numero_identificacion, nombres, apellidos, cargo, id_finca, estado)
        except sqlite3.IntegrityError:
            raise ValueError(f"Error de integridad: código o identificación duplicado")
        except Exception as e:
            raise ValueError(f"Error al crear empleado: {str(e)}")

    def actualizar_empleado(
        self,
        codigo: str,
        numero_identificacion: str,
        nombres: str,
        apellidos: str,
        cargo: str,
        id_finca: Optional[int] = None,
    ) -> None:
        """Actualiza campos base de un empleado."""
        codigo = str(codigo or '').strip()
        numero_identificacion = str(numero_identificacion or '').strip()
        nombres = str(nombres or '').strip()
        apellidos = str(apellidos or '').strip()
        cargo = str(cargo or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not numero_identificacion:
            raise ValueError("El número de identificación es obligatorio")
        if not nombres:
            raise ValueError("Los nombres son obligatorios")
        if not apellidos:
            raise ValueError("Los apellidos son obligatorios")
        if not cargo:
            raise ValueError("El cargo es obligatorio")

        if not self._repo.existe_codigo_empleado(codigo):
            raise ValueError(f"No existe empleado con código '{codigo}'")

        try:
            self._repo.actualizar_empleado_base(codigo, numero_identificacion, nombres, apellidos, cargo, id_finca)
        except Exception as e:
            raise ValueError(f"Error al actualizar empleado: {str(e)}")

    def cambiar_estado_empleado(self, codigo: str, nuevo_estado: str) -> None:
        """Activa/Desactiva empleado (soft delete por estado)."""
        codigo = str(codigo or '').strip()
        nuevo_estado = str(nuevo_estado or '').strip()

        if not codigo:
            raise ValueError("El código es obligatorio")
        if not self._repo.existe_codigo_empleado(codigo):
            raise ValueError(f"No existe empleado con código '{codigo}'")

        estados_validos = {"Activo", "Inactivo"}
        if nuevo_estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_empleado(codigo, nuevo_estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado: {str(e)}")

    # ============================================================
    # Fincas (SIMPLIFIED scope - base fields only)
    # ============================================================

    def listar_fincas_activas(self) -> List[Dict[str, Any]]:
        """Lista fincas activas normalizadas."""
        try:
            filas = self._repo.listar_fincas_activas()
            return [
                {
                    'codigo': str(f.get('codigo', '')).strip().upper(),
                    'nombre': str(f.get('nombre', '')).strip().title(),
                    'ubicacion': str(f.get('ubicacion', '') or '').strip().title(),
                    'estado': str(f.get('estado', '') or '').strip(),
                }
                for f in filas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar fincas: {str(e)}")

    def obtener_finca(self, codigo_finca: str) -> Dict[str, Any]:
        """Obtiene una finca por código. Lanza error si no existe."""
        codigo_finca = str(codigo_finca or '').strip().upper()

        if not codigo_finca:
            raise ValueError("El código de finca es obligatorio")

        try:
            finca = self._repo.obtener_finca(codigo_finca)
            if not finca:
                raise ValueError(f"No existe finca con código '{codigo_finca}'")

            return {
                'codigo': str(finca.get('codigo', '')).strip().upper(),
                'nombre': str(finca.get('nombre', '')).strip().title(),
                'ubicacion': str(finca.get('ubicacion', '') or '').strip().title(),
                'estado': str(finca.get('estado', '') or '').strip(),
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al obtener finca: {str(e)}")

    def crear_finca(self, codigo_finca: str, nombre: str, ubicacion: str = '') -> None:
        """Crea una finca con validaciones."""
        codigo_finca = str(codigo_finca or '').strip().upper()
        nombre = str(nombre or '').strip().title()
        ubicacion = str(ubicacion or '').strip().title()

        if not codigo_finca:
            raise ValueError("El código de finca es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not ubicacion:
            raise ValueError("La ubicación es obligatoria")

        if self._repo.existe_codigo_finca(codigo_finca):
            raise ValueError(f"Ya existe una finca con código '{codigo_finca}'")

        try:
            self._repo.crear_finca_base(codigo_finca, nombre, ubicacion, 'Activo')
        except Exception as e:
            raise ValueError(f"Error al crear finca: {str(e)}")

    def actualizar_finca(self, codigo_finca: str, nombre: str, ubicacion: str = '') -> None:
        """Actualiza una finca existente."""
        codigo_finca = str(codigo_finca or '').strip().upper()
        nombre = str(nombre or '').strip().title()
        ubicacion = str(ubicacion or '').strip().title()

        if not codigo_finca:
            raise ValueError("El código de finca es obligatorio")
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not ubicacion:
            raise ValueError("La ubicación es obligatoria")

        if not self._repo.existe_codigo_finca(codigo_finca):
            raise ValueError(f"No existe finca con código '{codigo_finca}'")

        try:
            self._repo.actualizar_finca_base(codigo_finca, nombre, ubicacion)
        except Exception as e:
            raise ValueError(f"Error al actualizar finca: {str(e)}")

    def cambiar_estado_finca(self, codigo_finca: str, estado: str) -> None:
        """Activa/Desactiva finca (soft delete por estado)."""
        codigo_finca = str(codigo_finca or '').strip().upper()
        estado = str(estado or '').strip()

        if not codigo_finca:
            raise ValueError("El código de finca es obligatorio")
        if not self._repo.existe_codigo_finca(codigo_finca):
            raise ValueError(f"No existe finca con código '{codigo_finca}'")

        estados_validos = {"Activo", "Inactivo"}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")

        try:
            self._repo.cambiar_estado_finca(codigo_finca, estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado de finca: {str(e)}")

    # ============================================================
    # LECTURA - Lotes
    # ============================================================

    def listar_fincas_para_combo_lotes(self) -> List[Dict[str, Any]]:
        """
        Obtiene fincas activas para combo en módulo Lotes, normalizadas.

        Returns:
            List[Dict]: [{'id': int, 'codigo': str, 'nombre': str}, ...]
            Ordenado por nombre, con nombres capitalizados.
        """
        try:
            fincas = self._repo.listar_fincas_activas_para_lotes()
            return [
                {
                    'id': f['id'],
                    'codigo': f['codigo'].strip().upper() if f['codigo'] else '',
                    'nombre': f['nombre'].strip().title() if f['nombre'] else ''
                }
                for f in fincas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar fincas: {str(e)}")

    def listar_lotes_activos(self) -> List[Dict[str, Any]]:
        """
        Obtiene lotes activos con nombre de finca, normalizados.

        Returns:
            List[Dict]: [{'id': int, 'codigo': str, 'nombre': str, 'descripcion': str,
                          'criterio': str, 'finca_id': int, 'finca_nombre': str}, ...]
        
        Normalización:
        - codigo: UPPER
        - nombre: title()
        - criterio: default 'Por Peso' si vacío
        - finca_nombre: default 'Sin Finca' si vacío
        """
        try:
            lotes = self._repo.listar_lotes_activos_con_finca()
            return [
                {
                    'id': lote['id'],
                    'codigo': lote['codigo'].strip().upper() if lote['codigo'] else '',
                    'nombre': lote['nombre'].strip().title() if lote['nombre'] else '',
                    'descripcion': lote['descripcion'].strip() if lote['descripcion'] else '',
                    'criterio': lote['criterio'].strip() if lote['criterio'] else 'Por Peso',
                    'finca_id': lote['finca_id'],
                    'finca_nombre': lote['finca_nombre'].strip().title() if lote['finca_nombre'] else 'Sin Finca'
                }
                for lote in lotes
            ]
        except Exception as e:
            raise ValueError(f"Error al listar lotes: {str(e)}")

    def obtener_lote(self, lote_id: int) -> Dict[str, Any]:
        """
        Obtiene un lote por ID, validando existencia.

        Args:
            lote_id: ID del lote
        
        Returns:
            Dict con datos del lote normalizados.
        
        Raises:
            ValueError: Si lote no existe.
        """
        if not lote_id:
            raise ValueError("El ID del lote es obligatorio")
    
        lote = self._repo.obtener_lote(lote_id)
        if not lote:
            raise ValueError(f"No existe lote con ID {lote_id}")
    
        return {
            'id': lote['id'],
            'codigo': lote['codigo'].strip().upper() if lote['codigo'] else '',
            'nombre': lote['nombre'].strip().title() if lote['nombre'] else '',
            'descripcion': lote['descripcion'].strip() if lote['descripcion'] else '',
            'criterio': lote['criterio'].strip() if lote['criterio'] else 'Por Peso',
            'estado': lote['estado'].strip() if lote['estado'] else '',
            'finca_id': lote['finca_id']
        }

    def obtener_finca_por_nombre(self, nombre: str) -> Dict[str, Any]:
        """
        Obtiene una finca activa por nombre (case-insensitive), validando existencia.

        Args:
            nombre: Nombre de la finca
        
        Returns:
            Dict con datos de la finca normalizados.
        
        Raises:
            ValueError: Si finca no existe o está inactiva.
        """
        nombre = str(nombre or '').strip()
        if not nombre:
            raise ValueError("El nombre de finca es obligatorio")
    
        finca = self._repo.obtener_finca_por_nombre(nombre)
        if not finca:
            raise ValueError(f"No existe finca activa con nombre '{nombre}'")
    
        return {
            'id': finca['id'],
            'codigo': finca['codigo'].strip().upper() if finca['codigo'] else '',
            'nombre': finca['nombre'].strip().title() if finca['nombre'] else '',
            'ubicacion': finca['ubicacion'].strip().title() if finca['ubicacion'] else '',
            'estado': finca['estado'].strip() if finca['estado'] else ''
        }

    # ============================================================
    # ESCRITURA - Lotes
    # ============================================================

    def crear_lote(
        self,
        codigo: str,
        nombre: str,
        finca_id: int,
        descripcion: str = '',
        criterio: str = 'Por Peso'
    ) -> None:
        """
        Crea un nuevo lote con validaciones y normalización.

        Args:
            codigo: Código del lote (requerido, único por finca)
            nombre: Nombre del lote (requerido)
            finca_id: ID de la finca (requerido, debe existir)
            descripcion: Descripción (opcional)
            criterio: Criterio de agrupación (opcional, default 'Por Peso')
        
        Raises:
            ValueError: Si validaciones fallan o código duplicado en finca.
        
        Validaciones:
        - Código requerido
        - Nombre requerido
        - Finca ID requerido y debe existir
        - Código único por finca
        - Criterio debe estar en lista de valores válidos
    
        Normalización:
        - codigo: UPPER
        - nombre: title()
        - estado: siempre 'Activo' al crear
        """
        # Validaciones básicas
        codigo = str(codigo or '').strip().upper()
        nombre = str(nombre or '').strip().title()
        descripcion = str(descripcion or '').strip()
        criterio = str(criterio or 'Por Peso').strip()
    
        if not codigo:
            raise ValueError("El código del lote es obligatorio")
        if not nombre:
            raise ValueError("El nombre del lote es obligatorio")
        if not finca_id:
            raise ValueError("Debe seleccionar una finca")
    
        # Validar finca existe (activa)
        finca = self._repo.obtener_finca_por_id(finca_id)
        if not finca:
            raise ValueError("La finca seleccionada no existe o está inactiva")
    
        # Validar criterio
        criterios_validos = [
            'Por Peso', 'Por Edad', 'Por Origen', 'Por Salud', 
            'Por Producción', 'Personalizado'
        ]
        if criterio not in criterios_validos:
            raise ValueError(f"Criterio inválido. Valores permitidos: {', '.join(criterios_validos)}")
    
        # Validar unicidad de código en finca
        if self._repo.existe_lote_en_finca(codigo, finca_id):
            raise ValueError(f"Ya existe un lote con código '{codigo}' en esta finca")
    
        # Crear lote
        try:
            self._repo.crear_lote(
                codigo=codigo,
                nombre=nombre,
                finca_id=finca_id,
                descripcion=descripcion,
                criterio=criterio,
                estado='Activo'
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Error de integridad: código '{codigo}' duplicado en finca")
        except Exception as e:
            raise ValueError(f"Error al crear lote: {str(e)}")

    def actualizar_lote(
        self,
        lote_id: int,
        nombre: str,
        descripcion: str,
        criterio: str,
        finca_id: int
    ) -> None:
        """
        Actualiza un lote existente con validaciones y normalización.

        Args:
            lote_id: ID del lote (requerido, debe existir)
            nombre: Nuevo nombre (requerido)
            descripcion: Nueva descripción (opcional)
            criterio: Nuevo criterio (requerido)
            finca_id: Nueva finca (requerido, permite reasignar)
        
        Raises:
            ValueError: Si validaciones fallan.
        
        Validaciones:
        - Lote ID requerido y debe existir
        - Nombre requerido
        - Finca ID requerido
        - Criterio debe estar en lista de valores válidos
    
        Normalización:
        - nombre: title()
    
        Nota: No actualiza código ni estado.
        """
        # Validaciones básicas
        if not lote_id:
            raise ValueError("El ID del lote es obligatorio")
        nombre = str(nombre or '').strip().title()
        descripcion = str(descripcion or '').strip()
        criterio = str(criterio or 'Por Peso').strip()
    
        if not nombre:
            raise ValueError("El nombre del lote es obligatorio")
        if not finca_id:
            raise ValueError("Debe seleccionar una finca")
    
        # Validar lote existe
        lote = self._repo.obtener_lote(lote_id)
        if not lote:
            raise ValueError(f"No existe lote con ID {lote_id}")
    
        # Validar finca existe (activa)
        finca = self._repo.obtener_finca_por_id(finca_id)
        if not finca:
            raise ValueError("La finca seleccionada no existe o está inactiva")
    
        # Validar criterio
        criterios_validos = [
            'Por Peso', 'Por Edad', 'Por Origen', 'Por Salud', 
            'Por Producción', 'Personalizado'
        ]
        if criterio not in criterios_validos:
            raise ValueError(f"Criterio inválido. Valores permitidos: {', '.join(criterios_validos)}")
    
        # Actualizar lote
        try:
            self._repo.actualizar_lote(
                lote_id=lote_id,
                nombre=nombre,
                descripcion=descripcion,
                criterio=criterio,
                finca_id=finca_id
            )
        except Exception as e:
            raise ValueError(f"Error al actualizar lote: {str(e)}")

    def cambiar_estado_lote(self, lote_id: int, estado: str) -> None:
        """
        Cambia el estado de un lote (soft delete).

        Args:
            lote_id: ID del lote
            estado: Nuevo estado ('Activo' o 'Inactivo')
        
        Raises:
            ValueError: Si validaciones fallan.
        
        Validaciones:
        - Lote ID requerido y debe existir
        - Estado debe ser 'Activo' o 'Inactivo'
        """
        if not lote_id:
            raise ValueError("El ID del lote es obligatorio")
    
        estado = str(estado or '').strip()
        estados_validos = {'Activo', 'Inactivo'}
        if estado not in estados_validos:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")
    
        # Validar lote existe
        lote = self._repo.obtener_lote(lote_id)
        if not lote:
            raise ValueError(f"No existe lote con ID {lote_id}")
    
        # Cambiar estado
        try:
            self._repo.cambiar_estado_lote(lote_id, estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado del lote: {str(e)}")
    
    # ============================================================
    # LECTURA - Sectores
    # ============================================================
    
    def listar_fincas_para_combo_sectores(self) -> List[Dict[str, Any]]:
        """Obtiene fincas activas para combo Sectores, normalizadas."""
        try:
            fincas = self._repo.listar_fincas_activas_para_sectores()
            return [
                {
                    'id': f['id'],
                    'codigo': f['codigo'].strip().upper() if f['codigo'] else '',
                    'nombre': f['nombre'].strip().title() if f['nombre'] else ''
                }
                for f in fincas
            ]
        except Exception as e:
            raise ValueError(f"Error al listar fincas: {str(e)}")
    
    def listar_sectores_activos(self) -> List[Dict[str, Any]]:
        """Obtiene sectores activos con finca, normalizados."""
        try:
            sectores = self._repo.listar_sectores_activos()
            return [
                {
                    'id': s['id'],
                    'codigo': s['codigo'].strip().upper() if s['codigo'] else '',
                    'nombre': s['nombre'].strip().title() if s['nombre'] else '',
                    'comentario': s['comentario'].strip() if s['comentario'] else '',
                    'finca_id': s['finca_id'],
                    'finca_nombre': s['finca_nombre'].strip().title() if s['finca_nombre'] else 'Sin Finca'
                }
                for s in sectores
            ]
        except Exception as e:
            raise ValueError(f"Error al listar sectores: {str(e)}")
    
    def obtener_sector(self, sector_id: int) -> Dict[str, Any]:
        """Obtiene sector por ID, validando existencia."""
        if not sector_id:
            raise ValueError("El ID del sector es obligatorio")
        
        sector = self._repo.obtener_sector(sector_id)
        if not sector:
            raise ValueError(f"No existe sector con ID {sector_id}")
        
        return {
            'id': sector['id'],
            'codigo': sector['codigo'].strip().upper() if sector['codigo'] else '',
            'nombre': sector['nombre'].strip().title() if sector['nombre'] else '',
            'comentario': sector['comentario'].strip() if sector['comentario'] else '',
            'estado': sector['estado'].strip() if sector['estado'] else '',
            'finca_id': sector['finca_id']
        }
    
    # ============================================================
    # ESCRITURA - Sectores
    # ============================================================
    
    def crear_sector(
        self,
        codigo: str,
        nombre: str,
        finca_id: int,
        comentario: str = ''
    ) -> None:
        """Crea sector con validaciones."""
        codigo = str(codigo or '').strip().upper()
        nombre = str(nombre or '').strip().title()
        comentario = str(comentario or '').strip()
        
        if not codigo:
            raise ValueError("El código del sector es obligatorio")
        if not nombre:
            raise ValueError("El nombre del sector es obligatorio")
        if not finca_id:
            raise ValueError("Debe seleccionar una finca")
        
        # Valida finca activa
        finca = self._repo.obtener_finca_por_id(finca_id)
        if not finca:
            raise ValueError("La finca seleccionada no existe o está inactiva")
        
        # Valida unicidad por finca
        if self._repo.existe_codigo_sector_en_finca(codigo, finca_id):
            raise ValueError(f"Ya existe un sector con código '{codigo}' en esta finca")
        
        try:
            self._repo.crear_sector(codigo, nombre, finca_id, comentario, 'Activo')
        except sqlite3.IntegrityError:
            raise ValueError(f"Error de integridad: código '{codigo}' duplicado")
        except Exception as e:
            raise ValueError(f"Error al crear sector: {str(e)}")
    
    def actualizar_sector(
        self,
        sector_id: int,
        nombre: str,
        comentario: str,
        finca_id: int
    ) -> None:
        """Actualiza sector con validaciones."""
        if not sector_id:
            raise ValueError("El ID del sector es obligatorio")
        nombre = str(nombre or '').strip().title()
        comentario = str(comentario or '').strip()
        
        if not nombre:
            raise ValueError("El nombre del sector es obligatorio")
        if not finca_id:
            raise ValueError("Debe seleccionar una finca")
        
        # Valida sector existe
        sector = self._repo.obtener_sector(sector_id)
        if not sector:
            raise ValueError(f"No existe sector con ID {sector_id}")
        
        # Valida finca activa
        finca = self._repo.obtener_finca_por_id(finca_id)
        if not finca:
            raise ValueError("La finca seleccionada no existe o está inactiva")
        
        try:
            self._repo.actualizar_sector(sector_id, nombre, comentario, finca_id)
        except Exception as e:
            raise ValueError(f"Error al actualizar sector: {str(e)}")
    
    def cambiar_estado_sector(self, sector_id: int, estado: str) -> None:
        """Cambia estado de sector (soft delete)."""
        if not sector_id:
            raise ValueError("El ID del sector es obligatorio")
        
        estado = str(estado or '').strip()
        if estado not in {'Activo', 'Inactivo'}:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")
        
        # Valida sector existe
        sector = self._repo.obtener_sector(sector_id)
        if not sector:
            raise ValueError(f"No existe sector con ID {sector_id}")
        
        try:
            self._repo.cambiar_estado_sector(sector_id, estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado del sector: {str(e)}")


    # LECTURA - Tipos de Explotación
    # ============================================================
    
    CATEGORIAS_VALIDAS = {
        'Carne', 'Leche', 'Doble Propósito', 
        'Reproducción', 'Huevos', 'Otros'
    }
    
    def listar_tipos_explotacion_activos(self) -> List[Dict[str, Any]]:
        """
        Obtiene tipos de explotación activos con normalización.
        
        Returns:
            List[Dict]: Tipos ordenados por código.
        """
        tipos = self._repo.listar_tipos_explotacion_activos()
        for tipo in tipos:
            tipo['codigo'] = tipo['codigo'].upper()
            tipo['descripcion'] = tipo['descripcion'].title()
            tipo['categoria'] = tipo['categoria'].title()
        return tipos
    
    def obtener_tipo_explotacion(self, codigo: str) -> Dict[str, Any]:
        """
        Obtiene un tipo de explotación por código.
        
        Args:
            codigo: Código del tipo
            
        Returns:
            Dict con datos del tipo
            
        Raises:
            ValueError: Si el tipo no existe
        """
        codigo = str(codigo or '').strip().upper()
        if not codigo:
            raise ValueError("El código es obligatorio")
        
        tipo = self._repo.obtener_tipo_explotacion(codigo)
        if not tipo:
            raise ValueError(f"No existe tipo de explotación con código '{codigo}'")
        
        # Normalizar salida
        tipo['codigo'] = tipo['codigo'].upper()
        tipo['descripcion'] = tipo['descripcion'].title()
        tipo['categoria'] = tipo['categoria'].title()
        return tipo


    # ESCRITURA - Tipos de Explotación
    # ============================================================
    
    def crear_tipo_explotacion(
        self, 
        codigo: str, 
        descripcion: str, 
        categoria: str, 
        comentario: str = ''
    ) -> None:
        """
        Crea un nuevo tipo de explotación con validaciones.
        
        Args:
            codigo: Código único del tipo
            descripcion: Descripción del tipo
            categoria: Categoría (debe estar en CATEGORIAS_VALIDAS)
            comentario: Comentario opcional
            
        Raises:
            ValueError: Si faltan campos requeridos, categoría inválida, o código duplicado
        """
        # Normalizar entrada
        codigo = str(codigo or '').strip().upper()
        descripcion = str(descripcion or '').strip().title()
        categoria = str(categoria or '').strip().title()
        comentario = str(comentario or '').strip()
        
        # Validar campos requeridos
        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        if not categoria:
            raise ValueError("La categoría es obligatoria")
        
        # Validar categoría válida
        if categoria not in self.CATEGORIAS_VALIDAS:
            categorias_str = ', '.join(sorted(self.CATEGORIAS_VALIDAS))
            raise ValueError(f"Categoría inválida. Valores permitidos: {categorias_str}")
        
        # Validar unicidad
        if self._repo.existe_codigo_tipo_explotacion(codigo):
            raise ValueError(f"Ya existe un tipo de explotación con código '{codigo}'")
        
        try:
            self._repo.crear_tipo_explotacion_base(
                codigo=codigo,
                descripcion=descripcion,
                categoria=categoria,
                comentario=comentario,
                estado='Activo'
            )
        except Exception as e:
            raise ValueError(f"Error al crear tipo de explotación: {str(e)}")
    
    def actualizar_tipo_explotacion(
        self,
        codigo: str,
        descripcion: str,
        categoria: str,
        comentario: str = ''
    ) -> None:
        """
        Actualiza un tipo de explotación existente.
        
        Args:
            codigo: Código del tipo (no se modifica, es PK)
            descripcion: Nueva descripción
            categoria: Nueva categoría
            comentario: Nuevo comentario
            
        Raises:
            ValueError: Si el tipo no existe, faltan campos, o categoría inválida
        """
        # Normalizar entrada
        codigo = str(codigo or '').strip().upper()
        descripcion = str(descripcion or '').strip().title()
        categoria = str(categoria or '').strip().title()
        comentario = str(comentario or '').strip()
        
        # Validar campos requeridos
        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descripcion:
            raise ValueError("La descripción es obligatoria")
        if not categoria:
            raise ValueError("La categoría es obligatoria")
        
        # Validar categoría válida
        if categoria not in self.CATEGORIAS_VALIDAS:
            categorias_str = ', '.join(sorted(self.CATEGORIAS_VALIDAS))
            raise ValueError(f"Categoría inválida. Valores permitidos: {categorias_str}")
        
        # Validar existencia
        tipo_actual = self._repo.obtener_tipo_explotacion(codigo)
        if not tipo_actual:
            raise ValueError(f"No existe tipo de explotación con código '{codigo}'")
        
        try:
            self._repo.actualizar_tipo_explotacion_base(
                codigo=codigo,
                descripcion=descripcion,
                categoria=categoria,
                comentario=comentario
            )
        except Exception as e:
            raise ValueError(f"Error al actualizar tipo de explotación: {str(e)}")
    
    def cambiar_estado_tipo_explotacion(self, codigo: str, estado: str) -> None:
        """
        Cambia estado de tipo de explotación (soft delete).
        
        Args:
            codigo: Código del tipo
            estado: Nuevo estado ('Activo' o 'Inactivo')
            
        Raises:
            ValueError: Si el tipo no existe o estado inválido
        """
        codigo = str(codigo or '').strip().upper()
        if not codigo:
            raise ValueError("El código es obligatorio")
        
        estado = str(estado or '').strip()
        if estado not in {'Activo', 'Inactivo'}:
            raise ValueError("Estado inválido. Use 'Activo' o 'Inactivo'")
        
        # Validar existencia
        tipo_actual = self._repo.obtener_tipo_explotacion(codigo)
        if not tipo_actual:
            raise ValueError(f"No existe tipo de explotación con código '{codigo}'")
        
        try:
            self._repo.cambiar_estado_tipo_explotacion(codigo, estado)
        except Exception as e:
            raise ValueError(f"Error al cambiar estado del tipo: {str(e)}")
