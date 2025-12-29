"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   REGLAS DE NEGOCIO CENTRALIZADAS                        ║
║                         FASE 2 - FincaFácil                              ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Centralizar todas las reglas de negocio críticas del sistema para garantizar
    consistencia, trazabilidad y prevención de errores operativos.

Módulos cubiertos:
    - Ventas (animales y leche)
    - Nómina (empleados y contratos)
    - Producción (costos e insumos)
    - Inventarios (animales y recursos)

Autor: Arquitecto Senior - Fase 2
Fecha: Diciembre 2025
"""

from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any
import logging
from database.database import get_db_connection


class BusinessRuleViolation(Exception):
    """Excepción específica para violaciones de reglas de negocio"""
    def __init__(self, rule: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.rule = rule
        self.message = message
        self.details = details or {}
        super().__init__(f"[{rule}] {message}")


class BusinessRules:
    """
    Clase central para validar y aplicar reglas de negocio.
    
    Principios de diseño:
        1. Una regla = una función pública
        2. Retorna (bool, mensaje) para validaciones
        3. Lanza BusinessRuleViolation para operaciones críticas
        4. Logging detallado para auditoría
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # ═══════════════════════════════════════════════════════════════════════
    #                         REGLAS DE VENTAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_animal_sale(self, animal_id: int, fecha_venta: Optional[date] = None) -> Tuple[bool, str]:
        """
        Valida que un animal pueda ser vendido.
        
        Reglas aplicadas:
            1. El animal debe existir
            2. El animal no puede estar muerto
            3. El animal no puede haber sido vendido previamente
            4. La fecha de venta no puede ser anterior a la fecha de nacimiento
            5. La fecha de venta no puede ser futura
        
        Returns:
            (True, "OK") si todas las validaciones pasan
            (False, "Razón del error") si alguna falla
        """
        if fecha_venta is None:
            fecha_venta = date.today()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1: Verificar existencia
            cursor.execute("SELECT id FROM animal WHERE id = ?", (animal_id,))
            if not cursor.fetchone():
                return False, f"Animal #{animal_id} no existe en el sistema"
            
            # Regla 2 y 3: Verificar estado
            cursor.execute("""
                SELECT 
                    estado,
                    fecha_nacimiento,
                    (SELECT COUNT(*) FROM venta WHERE animal_id = ? AND tipo = 'animal') as ventas_previas
                FROM animal 
                WHERE id = ?
            """, (animal_id, animal_id))
            
            row = cursor.fetchone()
            estado, fecha_nacimiento, ventas_previas = row
            
            if estado == 'muerto':
                return False, f"Animal #{animal_id} está registrado como MUERTO. No se puede vender."
            
            if ventas_previas > 0:
                return False, f"Animal #{animal_id} ya fue vendido previamente. Revisar historial de ventas."
            
            # Regla 4: Fecha de venta vs nacimiento
            if fecha_nacimiento:
                fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
                if fecha_venta < fecha_nac:
                    return False, f"Fecha de venta ({fecha_venta}) anterior a nacimiento ({fecha_nac})"
            
            # Regla 5: Fecha futura
            if fecha_venta > date.today():
                return False, f"Fecha de venta ({fecha_venta}) no puede ser futura"
            
            self.logger.info(f"✓ Animal #{animal_id} validado para venta en {fecha_venta}")
            return True, "OK"
    
    def validate_milk_sale(self, litros: float, fecha_venta: Optional[date] = None) -> Tuple[bool, str]:
        """
        Valida que una venta de leche sea posible.
        
        Reglas aplicadas:
            1. Litros debe ser > 0
            2. Debe existir producción registrada para la fecha
            3. No se puede vender más de lo producido (stock disponible)
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si no cumple
        """
        if fecha_venta is None:
            fecha_venta = date.today()
        
        # Regla 1: Cantidad válida
        if litros <= 0:
            return False, "La cantidad de litros debe ser mayor a cero"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 2 y 3: Verificar producción disponible
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(litros_am + litros_pm), 0) as producido,
                    COALESCE(
                        (SELECT SUM(cantidad) 
                         FROM venta 
                         WHERE tipo = 'leche' 
                         AND DATE(fecha) = DATE(?)), 
                        0
                    ) as vendido
                FROM produccion_leche
                WHERE DATE(fecha) = DATE(?)
            """, (fecha_venta, fecha_venta))
            
            row = cursor.fetchone()
            producido, vendido = row if row else (0, 0)
            
            disponible = producido - vendido
            
            if producido == 0:
                return False, f"No hay producción registrada para {fecha_venta}"
            
            if litros > disponible:
                return False, f"Stock insuficiente. Disponible: {disponible:.2f}L, Solicitado: {litros:.2f}L"
            
            self.logger.info(f"✓ Venta de leche validada: {litros}L de {disponible:.2f}L disponibles")
            return True, "OK"
    
    def calculate_animal_sale_price_suggestion(self, animal_id: int) -> Optional[float]:
        """
        Calcula un precio de venta sugerido basado en:
            - Peso actual
            - Edad
            - Raza
            - Historial de producción (si es vaca lechera)
        
        Returns:
            Precio sugerido en COP o None si no hay suficiente información
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    a.sexo,
                    a.fecha_nacimiento,
                    r.nombre as raza,
                    (SELECT peso FROM peso WHERE animal_id = a.id ORDER BY fecha DESC LIMIT 1) as peso_actual,
                    (SELECT AVG(litros_am + litros_pm) 
                     FROM produccion_leche 
                     WHERE animal_id = a.id 
                     AND fecha >= DATE('now', '-30 days')
                    ) as promedio_leche_30d
                FROM animal a
                LEFT JOIN raza r ON a.raza_id = r.id
                WHERE a.id = ?
            """, (animal_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            sexo, fecha_nac, raza, peso, promedio_leche = row
            
            # Base: $5,000 COP por kg
            precio_base_kg = 5000
            precio = 0
            
            if peso:
                precio = peso * precio_base_kg
            
            # Bonificación por producción lechera
            if sexo == 'Hembra' and promedio_leche and promedio_leche > 15:
                bonificacion = (promedio_leche - 15) * 50000  # $50k extra por litro sobre 15L
                precio += bonificacion
            
            # Ajuste por edad (animales muy jóvenes o muy viejos valen menos)
            if fecha_nac:
                edad_dias = (date.today() - datetime.strptime(fecha_nac, '%Y-%m-%d').date()).days
                edad_anios = edad_dias / 365
                
                if edad_anios < 1:  # Terneros
                    precio *= 0.6
                elif edad_anios > 8:  # Animales viejos
                    precio *= 0.7
            
            return round(precio, 2) if precio > 0 else None
    
    # ═══════════════════════════════════════════════════════════════════════
    #                         REGLAS DE NÓMINA
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_employee_contract(self, empleado_id: int, fecha_inicio: date, 
                                   fecha_fin: Optional[date] = None) -> Tuple[bool, str]:
        """
        Valida que un empleado pueda tener un nuevo contrato.
        
        Reglas aplicadas:
            1. El empleado debe existir
            2. No puede tener otro contrato activo en el mismo período
            3. Fecha inicio no puede ser futura
            4. Fecha fin debe ser posterior a fecha inicio
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si falla
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1: Verificar existencia
            cursor.execute("SELECT id FROM empleado WHERE id = ?", (empleado_id,))
            if not cursor.fetchone():
                return False, f"Empleado #{empleado_id} no existe"
            
            # Regla 3: Fecha inicio no futura
            if fecha_inicio > date.today():
                return False, f"Fecha de inicio ({fecha_inicio}) no puede ser futura"
            
            # Regla 4: Coherencia de fechas
            if fecha_fin and fecha_fin <= fecha_inicio:
                return False, "Fecha de finalización debe ser posterior a fecha de inicio"
            
            # Regla 2: No contratos superpuestos
            if fecha_fin:
                cursor.execute("""
                    SELECT COUNT(*) FROM contrato
                    WHERE empleado_id = ?
                    AND (
                        (fecha_inicio <= ? AND (fecha_fin IS NULL OR fecha_fin >= ?))
                        OR
                        (fecha_inicio <= ? AND (fecha_fin IS NULL OR fecha_fin >= ?))
                        OR
                        (fecha_inicio >= ? AND fecha_inicio <= ?)
                    )
                """, (empleado_id, fecha_inicio, fecha_inicio, fecha_fin, fecha_fin, 
                      fecha_inicio, fecha_fin))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM contrato
                    WHERE empleado_id = ?
                    AND (fecha_fin IS NULL OR fecha_fin >= ?)
                """, (empleado_id, fecha_inicio))
            
            contratos_conflicto = cursor.fetchone()[0]
            
            if contratos_conflicto > 0:
                return False, f"Empleado #{empleado_id} ya tiene {contratos_conflicto} contrato(s) activo(s) en ese período"
            
            self.logger.info(f"✓ Contrato validado para empleado #{empleado_id}")
            return True, "OK"
    
    def validate_payroll_payment(self, empleado_id: int, fecha_pago: date, monto: float) -> Tuple[bool, str]:
        """
        Valida que un pago de nómina sea correcto.
        
        Reglas aplicadas:
            1. Debe existir un contrato activo para la fecha de pago
            2. Monto debe ser > 0
            3. No debe existir pago duplicado para el mismo mes
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si falla
        """
        # Regla 2: Monto válido
        if monto <= 0:
            return False, "El monto del pago debe ser mayor a cero"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1: Contrato activo
            cursor.execute("""
                SELECT id FROM contrato
                WHERE empleado_id = ?
                AND fecha_inicio <= ?
                AND (fecha_fin IS NULL OR fecha_fin >= ?)
            """, (empleado_id, fecha_pago, fecha_pago))
            
            if not cursor.fetchone():
                return False, f"Empleado #{empleado_id} no tiene contrato activo para {fecha_pago}"
            
            # Regla 3: No pagos duplicados en el mismo mes
            year_month = fecha_pago.strftime('%Y-%m')
            cursor.execute("""
                SELECT COUNT(*) FROM pago_nomina
                WHERE empleado_id = ?
                AND strftime('%Y-%m', fecha_pago) = ?
            """, (empleado_id, year_month))
            
            pagos_mes = cursor.fetchone()[0]
            if pagos_mes > 0:
                return False, f"Ya existe pago registrado para empleado #{empleado_id} en {year_month}"
            
            self.logger.info(f"✓ Pago de nómina validado: Empleado #{empleado_id}, ${monto:,.0f}")
            return True, "OK"
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      REGLAS DE PRODUCCIÓN
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_milk_production(self, animal_id: int, fecha: date, 
                                litros_am: float, litros_pm: float) -> Tuple[bool, str]:
        """
        Valida que un registro de producción de leche sea coherente.
        
        Reglas aplicadas:
            1. Animal debe existir y ser hembra
            2. Animal debe estar vivo
            3. Litros AM y PM deben ser >= 0
            4. Total de litros debe ser razonable (< 50L por día)
            5. No debe existir registro duplicado para la misma fecha
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si falla
        """
        # Regla 3: Cantidades válidas
        if litros_am < 0 or litros_pm < 0:
            return False, "Los litros no pueden ser negativos"
        
        total_litros = litros_am + litros_pm
        
        # Regla 4: Límite razonable
        if total_litros > 50:
            return False, f"Producción diaria ({total_litros}L) excede límite razonable (50L). Verificar datos."
        
        if total_litros == 0:
            return False, "Debe registrar al menos producción AM o PM"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1 y 2: Animal válido
            cursor.execute("""
                SELECT sexo, estado 
                FROM animal 
                WHERE id = ?
            """, (animal_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, f"Animal #{animal_id} no existe"
            
            sexo, estado = row
            
            if sexo != 'Hembra':
                return False, f"Animal #{animal_id} es {sexo}, solo hembras producen leche"
            
            if estado == 'muerto':
                return False, f"Animal #{animal_id} está muerto, no puede producir leche"
            
            # Regla 5: No duplicados
            cursor.execute("""
                SELECT COUNT(*) FROM produccion_leche
                WHERE animal_id = ?
                AND DATE(fecha) = DATE(?)
            """, (animal_id, fecha))
            
            duplicados = cursor.fetchone()[0]
            if duplicados > 0:
                return False, f"Ya existe registro de producción para animal #{animal_id} en {fecha}"
            
            self.logger.info(f"✓ Producción validada: Animal #{animal_id}, {total_litros}L ({fecha})")
            return True, "OK"
    
    def validate_treatment_cost(self, animal_id: int, tipo_tratamiento: str, 
                               costo: float, fecha: Optional[date] = None) -> Tuple[bool, str]:
        """
        Valida que un tratamiento veterinario sea coherente.
        
        Reglas aplicadas:
            1. Animal debe existir
            2. Costo debe ser >= 0
            3. Fecha no puede ser futura
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si falla
        """
        if fecha is None:
            fecha = date.today()
        
        # Regla 2: Costo válido
        if costo < 0:
            return False, "El costo no puede ser negativo"
        
        # Regla 3: Fecha válida
        if fecha > date.today():
            return False, f"Fecha del tratamiento ({fecha}) no puede ser futura"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1: Animal existe
            cursor.execute("SELECT id FROM animal WHERE id = ?", (animal_id,))
            if not cursor.fetchone():
                return False, f"Animal #{animal_id} no existe"
            
            self.logger.info(f"✓ Tratamiento validado: Animal #{animal_id}, {tipo_tratamiento}, ${costo:,.0f}")
            return True, "OK"
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      REGLAS DE INVENTARIO
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_supply_movement(self, insumo_id: int, tipo: str, 
                                cantidad: float, fecha: Optional[date] = None) -> Tuple[bool, str]:
        """
        Valida movimientos de inventario de insumos.
        
        Reglas aplicadas:
            1. Insumo debe existir
            2. Cantidad > 0
            3. Para salidas, debe haber stock suficiente
            4. Tipo debe ser 'entrada' o 'salida'
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si falla
        """
        if fecha is None:
            fecha = date.today()
        
        # Regla 4: Tipo válido
        if tipo not in ['entrada', 'salida']:
            return False, f"Tipo '{tipo}' inválido. Debe ser 'entrada' o 'salida'"
        
        # Regla 2: Cantidad válida
        if cantidad <= 0:
            return False, "La cantidad debe ser mayor a cero"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1: Insumo existe
            cursor.execute("SELECT nombre, stock_actual FROM insumo WHERE id = ?", (insumo_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, f"Insumo #{insumo_id} no existe"
            
            nombre, stock_actual = row
            
            # Regla 3: Stock suficiente para salidas
            if tipo == 'salida':
                if stock_actual < cantidad:
                    return False, f"Stock insuficiente de '{nombre}'. Disponible: {stock_actual}, Solicitado: {cantidad}"
            
            self.logger.info(f"✓ Movimiento de insumo validado: {nombre}, {tipo}, {cantidad} unidades")
            return True, "OK"
    
    def validate_animal_pasture_assignment(self, animal_id: int, potrero_id: int) -> Tuple[bool, str]:
        """
        Valida que un animal pueda ser asignado a un potrero.
        
        Reglas aplicadas:
            1. Animal y potrero deben existir
            2. Animal debe estar vivo
            3. Potrero debe tener capacidad disponible
        
        Returns:
            (True, "OK") si es válido
            (False, "Razón") si falla
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Regla 1: Existencia
            cursor.execute("SELECT estado FROM animal WHERE id = ?", (animal_id,))
            row = cursor.fetchone()
            if not row:
                return False, f"Animal #{animal_id} no existe"
            
            estado = row[0]
            
            # Regla 2: Animal vivo
            if estado == 'muerto':
                return False, f"Animal #{animal_id} está muerto, no puede asignarse a potrero"
            
            cursor.execute("""
                SELECT 
                    nombre, 
                    capacidad,
                    (SELECT COUNT(*) FROM animal WHERE potrero_id = p.id AND estado != 'muerto') as ocupacion
                FROM potrero p
                WHERE id = ?
            """, (potrero_id,))
            
            row = cursor.fetchone()
            if not row:
                return False, f"Potrero #{potrero_id} no existe"
            
            nombre, capacidad, ocupacion = row
            
            # Regla 3: Capacidad disponible
            if ocupacion >= capacidad:
                return False, f"Potrero '{nombre}' está lleno ({ocupacion}/{capacidad})"
            
            self.logger.info(f"✓ Asignación validada: Animal #{animal_id} → Potrero '{nombre}' ({ocupacion + 1}/{capacidad})")
            return True, "OK"
    
    # ═══════════════════════════════════════════════════════════════════════
    #                      UTILIDADES Y CONSULTAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_validation_summary(self) -> Dict[str, int]:
        """
        Retorna resumen de validaciones disponibles.
        
        Returns:
            Diccionario con conteo de reglas por categoría
        """
        return {
            "ventas": 3,  # validate_animal_sale, validate_milk_sale, calculate_price
            "nomina": 2,  # validate_contract, validate_payment
            "produccion": 2,  # validate_milk_production, validate_treatment
            "inventario": 2,  # validate_supply_movement, validate_pasture_assignment
            "total": 9
        }
    
    def run_all_validations(self, scope: str = "all") -> Dict[str, Any]:
        """
        Ejecuta un conjunto de validaciones para auditoría.
        
        Args:
            scope: "all", "ventas", "nomina", "produccion", "inventario"
        
        Returns:
            Diccionario con resultados de validación
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "scope": scope,
            "violations": [],
            "warnings": [],
            "stats": {}
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if scope in ["all", "ventas"]:
                # Detectar ventas de animales muertos
                cursor.execute("""
                    SELECT v.id, v.animal_id, a.identificacion
                    FROM venta v
                    INNER JOIN animal a ON v.animal_id = a.id
                    WHERE v.tipo = 'animal' AND a.estado = 'muerto'
                """)
                for row in cursor.fetchall():
                    results["violations"].append({
                        "category": "ventas",
                        "severity": "CRITICAL",
                        "message": f"Venta #{row[0]} registrada para animal muerto (ID: {row[1]}, {row[2]})"
                    })
                
                # Detectar ventas duplicadas
                cursor.execute("""
                    SELECT animal_id, COUNT(*) as ventas
                    FROM venta
                    WHERE tipo = 'animal'
                    GROUP BY animal_id
                    HAVING ventas > 1
                """)
                for row in cursor.fetchall():
                    results["violations"].append({
                        "category": "ventas",
                        "severity": "CRITICAL",
                        "message": f"Animal #{row[0]} vendido {row[1]} veces"
                    })
            
            if scope in ["all", "nomina"]:
                # Detectar contratos superpuestos
                cursor.execute("""
                    SELECT c1.empleado_id, COUNT(*) as contratos
                    FROM contrato c1
                    WHERE (c1.fecha_fin IS NULL OR c1.fecha_fin >= DATE('now'))
                    GROUP BY c1.empleado_id
                    HAVING contratos > 1
                """)
                for row in cursor.fetchall():
                    results["violations"].append({
                        "category": "nomina",
                        "severity": "HIGH",
                        "message": f"Empleado #{row[0]} tiene {row[1]} contratos activos simultáneamente"
                    })
            
            if scope in ["all", "produccion"]:
                # Detectar producción sin animal válido
                cursor.execute("""
                    SELECT pl.id, pl.animal_id
                    FROM produccion_leche pl
                    LEFT JOIN animal a ON pl.animal_id = a.id
                    WHERE a.id IS NULL OR a.sexo != 'Hembra'
                """)
                for row in cursor.fetchall():
                    results["violations"].append({
                        "category": "produccion",
                        "severity": "CRITICAL",
                        "message": f"Producción #{row[0]} asociada a animal inválido (ID: {row[1]})"
                    })
            
            if scope in ["all", "inventario"]:
                # Detectar animales sin potrero
                cursor.execute("""
                    SELECT COUNT(*) FROM animal
                    WHERE estado = 'activo' AND potrero_id IS NULL
                """)
                count = cursor.fetchone()[0]
                if count > 0:
                    results["warnings"].append({
                        "category": "inventario",
                        "severity": "MEDIUM",
                        "message": f"{count} animales activos sin potrero asignado"
                    })
        
        results["stats"]["total_violations"] = len(results["violations"])
        results["stats"]["total_warnings"] = len(results["warnings"])
        
        return results


# ═══════════════════════════════════════════════════════════════════════════
#                            INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════════════════

# Singleton para uso en toda la aplicación
business_rules = BusinessRules()
