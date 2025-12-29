"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   SERVICIO DE VALIDACIONES CRUZADAS                      ║
║                         FASE 2 - FincaFácil                              ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Ejecutar validaciones automáticas periódicas para detectar:
        - Inconsistencias en datos
        - Violaciones de reglas de negocio
        - Alertas operativas críticas
        - Problemas de integridad

Responsabilidades:
    - Auditoría automática de datos
    - Generación de alertas con severidad
    - Recomendaciones de corrección
    - Logging de anomalías

Autor: Arquitecto Senior - Fase 2
Fecha: Diciembre 2025
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import logging
from src.database.database import get_db_connection
from src.core.business_rules import business_rules, BusinessRuleViolation


class ValidationAlert:
    """Representa una alerta de validación"""
    
    SEVERITY_CRITICAL = 'CRITICAL'
    SEVERITY_HIGH = 'HIGH'
    SEVERITY_MEDIUM = 'MEDIUM'
    SEVERITY_LOW = 'LOW'
    SEVERITY_INFO = 'INFO'
    
    def __init__(self, category: str, severity: str, message: str, 
                 details: Optional[Dict] = None, recommendation: Optional[str] = None):
        self.category = category
        self.severity = severity
        self.message = message
        self.details = details or {}
        self.recommendation = recommendation
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'category': self.category,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'recommendation': self.recommendation,
            'timestamp': self.timestamp.isoformat()
        }


class ValidationService:
    """
    Servicio centralizado para validaciones cruzadas y auditorías.
    
    Ejecuta chequeos periódicos de:
        - Integridad de datos
        - Coherencia de registros
        - Reglas de negocio
        - Alertas operativas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alerts = []
    
    # ═══════════════════════════════════════════════════════════════════════
    #                    VALIDACIONES DE VENTAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_animal_sales(self) -> List[ValidationAlert]:
        """
        Valida todas las ventas de animales registradas.
        
        Chequeos:
            1. Animales muertos vendidos
            2. Animales vendidos múltiples veces
            3. Fechas de venta incoherentes
            4. Precios sospechosos (muy bajos/altos)
        
        Returns:
            Lista de alertas encontradas
        """
        alerts = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Chequeo 1: Animales muertos vendidos
            cursor.execute("""
                SELECT v.id, v.animal_id, a.identificacion, v.fecha, v.precio
                FROM venta v
                INNER JOIN animal a ON v.animal_id = a.id
                WHERE v.tipo = 'animal' 
                AND a.estado = 'muerto'
            """)
            
            for row in cursor.fetchall():
                venta_id, animal_id, identificacion, fecha, precio = row
                alerts.append(ValidationAlert(
                    category='ventas_animales',
                    severity=ValidationAlert.SEVERITY_CRITICAL,
                    message=f"Venta #{venta_id} registrada para animal MUERTO",
                    details={
                        'venta_id': venta_id,
                        'animal_id': animal_id,
                        'identificacion': identificacion,
                        'fecha': fecha,
                        'precio': precio
                    },
                    recommendation="Anular la venta o corregir estado del animal"
                ))
            
            # Chequeo 2: Animales vendidos múltiples veces
            cursor.execute("""
                SELECT animal_id, a.identificacion, COUNT(*) as ventas
                FROM venta v
                INNER JOIN animal a ON v.animal_id = a.id
                WHERE v.tipo = 'animal'
                GROUP BY animal_id
                HAVING ventas > 1
            """)
            
            for row in cursor.fetchall():
                animal_id, identificacion, ventas = row
                alerts.append(ValidationAlert(
                    category='ventas_animales',
                    severity=ValidationAlert.SEVERITY_CRITICAL,
                    message=f"Animal {identificacion} vendido {ventas} veces",
                    details={
                        'animal_id': animal_id,
                        'identificacion': identificacion,
                        'ventas_registradas': ventas
                    },
                    recommendation="Mantener solo la venta válida, anular las demás"
                ))
            
            # Chequeo 3: Fechas de venta vs nacimiento
            cursor.execute("""
                SELECT v.id, v.animal_id, a.identificacion, v.fecha, a.fecha_nacimiento
                FROM venta v
                INNER JOIN animal a ON v.animal_id = a.id
                WHERE v.tipo = 'animal'
                AND a.fecha_nacimiento IS NOT NULL
                AND DATE(v.fecha) < DATE(a.fecha_nacimiento)
            """)
            
            for row in cursor.fetchall():
                venta_id, animal_id, identificacion, fecha_venta, fecha_nac = row
                alerts.append(ValidationAlert(
                    category='ventas_animales',
                    severity=ValidationAlert.SEVERITY_HIGH,
                    message=f"Venta #{venta_id}: fecha anterior a nacimiento del animal",
                    details={
                        'venta_id': venta_id,
                        'animal': identificacion,
                        'fecha_venta': fecha_venta,
                        'fecha_nacimiento': fecha_nac
                    },
                    recommendation="Corregir fecha de venta"
                ))
            
            # Chequeo 4: Precios sospechosos (< $100k o > $10M)
            cursor.execute("""
                SELECT id, animal_id, precio, fecha
                FROM venta
                WHERE tipo = 'animal'
                AND (precio < 100000 OR precio > 10000000)
            """)
            
            for row in cursor.fetchall():
                venta_id, animal_id, precio, fecha = row
                severity = ValidationAlert.SEVERITY_MEDIUM if precio < 100000 else ValidationAlert.SEVERITY_LOW
                alerts.append(ValidationAlert(
                    category='ventas_animales',
                    severity=severity,
                    message=f"Venta #{venta_id} con precio sospechoso: ${precio:,.0f}",
                    details={
                        'venta_id': venta_id,
                        'animal_id': animal_id,
                        'precio': precio,
                        'fecha': fecha
                    },
                    recommendation="Verificar precio, podría ser error de digitación"
                ))
        
        self.logger.info(f"Validación ventas animales: {len(alerts)} alertas encontradas")
        return alerts
    
    def validate_milk_sales(self) -> List[ValidationAlert]:
        """
        Valida ventas de leche.
        
        Chequeos:
            1. Ventas sin producción registrada
            2. Ventas mayores a producción disponible
            3. Precios por litro sospechosos
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Chequeo 1 y 2: Ventas vs producción por día
            cursor.execute("""
                SELECT 
                    DATE(v.fecha) as fecha,
                    SUM(v.cantidad) as vendido,
                    COALESCE(
                        (SELECT SUM(litros_am + litros_pm) 
                         FROM produccion_leche 
                         WHERE DATE(fecha) = DATE(v.fecha)),
                        0
                    ) as producido
                FROM venta v
                WHERE v.tipo = 'leche'
                GROUP BY DATE(v.fecha)
            """)
            
            for row in cursor.fetchall():
                fecha, vendido, producido = row
                
                if producido == 0:
                    alerts.append(ValidationAlert(
                        category='ventas_leche',
                        severity=ValidationAlert.SEVERITY_HIGH,
                        message=f"Venta de {vendido:.0f}L sin producción registrada ({fecha})",
                        details={
                            'fecha': fecha,
                            'litros_vendidos': vendido,
                            'litros_producidos': 0
                        },
                        recommendation="Registrar producción o anular venta"
                    ))
                elif vendido > producido:
                    deficit = vendido - producido
                    alerts.append(ValidationAlert(
                        category='ventas_leche',
                        severity=ValidationAlert.SEVERITY_CRITICAL,
                        message=f"Sobreventa de leche: {deficit:.0f}L más de lo producido ({fecha})",
                        details={
                            'fecha': fecha,
                            'litros_vendidos': vendido,
                            'litros_producidos': producido,
                            'deficit': deficit
                        },
                        recommendation="Corregir cantidad vendida o registrar producción faltante"
                    ))
            
            # Chequeo 3: Precios por litro sospechosos (< $500 o > $3000)
            cursor.execute("""
                SELECT id, fecha, cantidad, precio, (precio) as precio_litro
                FROM venta
                WHERE tipo = 'leche'
                AND (precio < 500 OR precio > 3000)
            """)
            
            for row in cursor.fetchall():
                venta_id, fecha, cantidad, precio, precio_litro = row
                alerts.append(ValidationAlert(
                    category='ventas_leche',
                    severity=ValidationAlert.SEVERITY_MEDIUM,
                    message=f"Precio sospechoso: ${precio_litro:,.0f}/L ({fecha})",
                    details={
                        'venta_id': venta_id,
                        'fecha': fecha,
                        'cantidad': cantidad,
                        'precio_litro': precio_litro
                    },
                    recommendation="Verificar precio, valor fuera de rango típico ($500-$3000/L)"
                ))
        
        self.logger.info(f"Validación ventas leche: {len(alerts)} alertas encontradas")
        return alerts
    
    # ═══════════════════════════════════════════════════════════════════════
    #                    VALIDACIONES DE NÓMINA
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_payroll(self) -> List[ValidationAlert]:
        """
        Valida registros de nómina.
        
        Chequeos:
            1. Contratos superpuestos
            2. Pagos sin contrato activo
            3. Pagos duplicados en mismo mes
            4. Montos sospechosos
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Chequeo 1: Contratos superpuestos
            cursor.execute("""
                SELECT c1.empleado_id, e.nombre, COUNT(*) as contratos_activos
                FROM contrato c1
                INNER JOIN empleado e ON c1.empleado_id = e.id
                WHERE c1.fecha_fin IS NULL OR c1.fecha_fin >= DATE('now')
                GROUP BY c1.empleado_id
                HAVING contratos_activos > 1
            """)
            
            for row in cursor.fetchall():
                empleado_id, nombre, contratos = row
                alerts.append(ValidationAlert(
                    category='nomina',
                    severity=ValidationAlert.SEVERITY_HIGH,
                    message=f"Empleado '{nombre}' tiene {contratos} contratos activos",
                    details={
                        'empleado_id': empleado_id,
                        'nombre': nombre,
                        'contratos_activos': contratos
                    },
                    recommendation="Finalizar contratos obsoletos, dejar solo el vigente"
                ))
            
            # Chequeo 2: Pagos sin contrato activo
            cursor.execute("""
                SELECT pn.id, pn.empleado_id, e.nombre, pn.fecha_pago, pn.monto
                FROM pago_nomina pn
                INNER JOIN empleado e ON pn.empleado_id = e.id
                WHERE NOT EXISTS (
                    SELECT 1 FROM contrato c
                    WHERE c.empleado_id = pn.empleado_id
                    AND c.fecha_inicio <= DATE(pn.fecha_pago)
                    AND (c.fecha_fin IS NULL OR c.fecha_fin >= DATE(pn.fecha_pago))
                )
            """)
            
            for row in cursor.fetchall():
                pago_id, empleado_id, nombre, fecha, monto = row
                alerts.append(ValidationAlert(
                    category='nomina',
                    severity=ValidationAlert.SEVERITY_CRITICAL,
                    message=f"Pago #{pago_id} sin contrato activo para '{nombre}'",
                    details={
                        'pago_id': pago_id,
                        'empleado': nombre,
                        'fecha_pago': fecha,
                        'monto': monto
                    },
                    recommendation="Crear contrato retroactivo o anular pago"
                ))
            
            # Chequeo 3: Pagos duplicados en mismo mes
            cursor.execute("""
                SELECT 
                    empleado_id, 
                    e.nombre,
                    strftime('%Y-%m', fecha_pago) as mes,
                    COUNT(*) as pagos,
                    SUM(monto) as total
                FROM pago_nomina pn
                INNER JOIN empleado e ON pn.empleado_id = e.id
                GROUP BY empleado_id, strftime('%Y-%m', fecha_pago)
                HAVING pagos > 1
            """)
            
            for row in cursor.fetchall():
                empleado_id, nombre, mes, pagos, total = row
                alerts.append(ValidationAlert(
                    category='nomina',
                    severity=ValidationAlert.SEVERITY_HIGH,
                    message=f"'{nombre}' tiene {pagos} pagos en {mes}",
                    details={
                        'empleado_id': empleado_id,
                        'nombre': nombre,
                        'mes': mes,
                        'pagos': pagos,
                        'total': total
                    },
                    recommendation="Consolidar en un solo pago o justificar pagos adicionales"
                ))
            
            # Chequeo 4: Montos sospechosos (< $500k o > $10M)
            cursor.execute("""
                SELECT id, empleado_id, fecha_pago, monto
                FROM pago_nomina
                WHERE monto < 500000 OR monto > 10000000
            """)
            
            for row in cursor.fetchall():
                pago_id, empleado_id, fecha, monto = row
                alerts.append(ValidationAlert(
                    category='nomina',
                    severity=ValidationAlert.SEVERITY_MEDIUM,
                    message=f"Pago #{pago_id} con monto sospechoso: ${monto:,.0f}",
                    details={
                        'pago_id': pago_id,
                        'empleado_id': empleado_id,
                        'fecha': fecha,
                        'monto': monto
                    },
                    recommendation="Verificar monto, fuera de rango típico ($500k-$10M)"
                ))
        
        self.logger.info(f"Validación nómina: {len(alerts)} alertas encontradas")
        return alerts
    
    # ═══════════════════════════════════════════════════════════════════════
    #                    VALIDACIONES DE PRODUCCIÓN
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_production(self) -> List[ValidationAlert]:
        """
        Valida registros de producción de leche.
        
        Chequeos:
            1. Producción sin animal válido
            2. Producción de animales machos
            3. Producción de animales muertos
            4. Cantidades anormales (>50L/día)
            5. Producción sin registros recientes
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Chequeo 1, 2, 3: Animal inválido, macho o muerto
            cursor.execute("""
                SELECT pl.id, pl.animal_id, a.identificacion, a.sexo, a.estado,
                       pl.fecha, (pl.litros_am + pl.litros_pm) as total
                FROM produccion_leche pl
                LEFT JOIN animal a ON pl.animal_id = a.id
                WHERE a.id IS NULL OR a.sexo != 'Hembra' OR a.estado = 'muerto'
            """)
            
            for row in cursor.fetchall():
                prod_id, animal_id, identificacion, sexo, estado, fecha, litros = row
                
                if identificacion is None:
                    severity = ValidationAlert.SEVERITY_CRITICAL
                    msg = f"Producción #{prod_id} asociada a animal inexistente (ID: {animal_id})"
                elif sexo != 'Hembra':
                    severity = ValidationAlert.SEVERITY_CRITICAL
                    msg = f"Producción #{prod_id} de animal MACHO ({identificacion})"
                else:  # estado == 'muerto'
                    severity = ValidationAlert.SEVERITY_CRITICAL
                    msg = f"Producción #{prod_id} de animal MUERTO ({identificacion})"
                
                alerts.append(ValidationAlert(
                    category='produccion',
                    severity=severity,
                    message=msg,
                    details={
                        'produccion_id': prod_id,
                        'animal_id': animal_id,
                        'identificacion': identificacion,
                        'fecha': fecha,
                        'litros': litros
                    },
                    recommendation="Corregir animal_id o eliminar registro"
                ))
            
            # Chequeo 4: Cantidades anormales
            cursor.execute("""
                SELECT pl.id, pl.animal_id, a.identificacion, pl.fecha,
                       pl.litros_am, pl.litros_pm, (pl.litros_am + pl.litros_pm) as total
                FROM produccion_leche pl
                INNER JOIN animal a ON pl.animal_id = a.id
                WHERE (pl.litros_am + pl.litros_pm) > 50
            """)
            
            for row in cursor.fetchall():
                prod_id, animal_id, identificacion, fecha, am, pm, total = row
                alerts.append(ValidationAlert(
                    category='produccion',
                    severity=ValidationAlert.SEVERITY_MEDIUM,
                    message=f"Producción anormal: {total:.1f}L en {fecha} ({identificacion})",
                    details={
                        'produccion_id': prod_id,
                        'animal': identificacion,
                        'fecha': fecha,
                        'litros_am': am,
                        'litros_pm': pm,
                        'total': total
                    },
                    recommendation="Verificar medición, >50L/día es inusual"
                ))
            
            # Chequeo 5: Vacas sin producción reciente (últimos 7 días)
            cursor.execute("""
                SELECT a.id, a.identificacion, MAX(pl.fecha) as ultima_produccion
                FROM animal a
                LEFT JOIN produccion_leche pl ON a.id = pl.animal_id
                WHERE a.sexo = 'Hembra' 
                AND a.estado = 'activo'
                AND (pl.fecha IS NULL OR DATE(pl.fecha) < DATE('now', '-7 days'))
                GROUP BY a.id
            """)
            
            for row in cursor.fetchall():
                animal_id, identificacion, ultima = row
                dias = "nunca" if not ultima else f"{(date.today() - datetime.strptime(ultima, '%Y-%m-%d').date()).days} días"
                alerts.append(ValidationAlert(
                    category='produccion',
                    severity=ValidationAlert.SEVERITY_LOW,
                    message=f"Vaca {identificacion} sin producción reciente (última: {dias})",
                    details={
                        'animal_id': animal_id,
                        'identificacion': identificacion,
                        'ultima_produccion': ultima
                    },
                    recommendation="Verificar estado de la vaca (seca, enferma, etc.)"
                ))
        
        self.logger.info(f"Validación producción: {len(alerts)} alertas encontradas")
        return alerts
    
    # ═══════════════════════════════════════════════════════════════════════
    #                    VALIDACIONES DE INVENTARIO
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_inventory(self) -> List[ValidationAlert]:
        """
        Valida inventarios y asignaciones.
        
        Chequeos:
            1. Animales sin potrero
            2. Potreros sobrecargados
            3. Stock negativo de insumos
            4. Herramientas sin mantenimiento
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Chequeo 1: Animales sin potrero
            cursor.execute("""
                SELECT id, identificacion
                FROM animal
                WHERE estado = 'activo' AND potrero_id IS NULL
            """)
            
            count = 0
            for row in cursor.fetchall():
                count += 1
                animal_id, identificacion = row
                alerts.append(ValidationAlert(
                    category='inventario',
                    severity=ValidationAlert.SEVERITY_MEDIUM,
                    message=f"Animal {identificacion} activo sin potrero asignado",
                    details={
                        'animal_id': animal_id,
                        'identificacion': identificacion
                    },
                    recommendation="Asignar potrero al animal"
                ))
            
            # Chequeo 2: Potreros sobrecargados
            cursor.execute("""
                SELECT 
                    p.id,
                    p.nombre,
                    p.capacidad,
                    COUNT(a.id) as ocupacion
                FROM potrero p
                LEFT JOIN animal a ON p.id = a.potrero_id AND a.estado != 'muerto'
                GROUP BY p.id
                HAVING ocupacion > p.capacidad
            """)
            
            for row in cursor.fetchall():
                potrero_id, nombre, capacidad, ocupacion = row
                sobrecarga = ocupacion - capacidad
                alerts.append(ValidationAlert(
                    category='inventario',
                    severity=ValidationAlert.SEVERITY_HIGH,
                    message=f"Potrero '{nombre}' sobrecargado: {ocupacion}/{capacidad} (+{sobrecarga})",
                    details={
                        'potrero_id': potrero_id,
                        'nombre': nombre,
                        'capacidad': capacidad,
                        'ocupacion': ocupacion,
                        'sobrecarga': sobrecarga
                    },
                    recommendation="Redistribuir animales a otros potreros"
                ))
            
            # Chequeo 3: Stock negativo
            cursor.execute("""
                SELECT id, nombre, stock_actual, unidad_medida
                FROM insumo
                WHERE stock_actual < 0
            """)
            
            for row in cursor.fetchall():
                insumo_id, nombre, stock, unidad = row
                alerts.append(ValidationAlert(
                    category='inventario',
                    severity=ValidationAlert.SEVERITY_CRITICAL,
                    message=f"Insumo '{nombre}' con stock NEGATIVO: {stock} {unidad}",
                    details={
                        'insumo_id': insumo_id,
                        'nombre': nombre,
                        'stock': stock,
                        'unidad': unidad
                    },
                    recommendation="Corregir movimientos, el stock no puede ser negativo"
                ))
            
            # Chequeo 4: Stock bajo
            cursor.execute("""
                SELECT id, nombre, stock_actual, stock_minimo, unidad_medida
                FROM insumo
                WHERE stock_actual < stock_minimo AND stock_actual >= 0
            """)
            
            for row in cursor.fetchall():
                insumo_id, nombre, stock, minimo, unidad = row
                alerts.append(ValidationAlert(
                    category='inventario',
                    severity=ValidationAlert.SEVERITY_MEDIUM,
                    message=f"Stock bajo: '{nombre}' ({stock}/{minimo} {unidad})",
                    details={
                        'insumo_id': insumo_id,
                        'nombre': nombre,
                        'stock_actual': stock,
                        'stock_minimo': minimo,
                        'unidad': unidad
                    },
                    recommendation="Realizar pedido de reabastecimiento"
                ))
        
        self.logger.info(f"Validación inventario: {len(alerts)} alertas encontradas")
        return alerts
    
    # ═══════════════════════════════════════════════════════════════════════
    #                    ORQUESTACIÓN Y REPORTES
    # ═══════════════════════════════════════════════════════════════════════
    
    def run_all_validations(self, scope: str = 'all') -> Dict[str, Any]:
        """
        Ejecuta todas las validaciones y genera reporte completo.
        
        Args:
            scope: 'all', 'ventas', 'nomina', 'produccion', 'inventario'
        
        Returns:
            {
                'timestamp': ISO timestamp,
                'scope': Alcance ejecutado,
                'alerts': Lista de todas las alertas,
                'summary': Resumen por categoría y severidad,
                'critical_count': Cantidad de alertas críticas
            }
        """
        all_alerts = []
        
        # Ejecutar validaciones según scope
        if scope in ['all', 'ventas']:
            all_alerts.extend(self.validate_animal_sales())
            all_alerts.extend(self.validate_milk_sales())
        
        if scope in ['all', 'nomina']:
            all_alerts.extend(self.validate_payroll())
        
        if scope in ['all', 'produccion']:
            all_alerts.extend(self.validate_production())
        
        if scope in ['all', 'inventario']:
            all_alerts.extend(self.validate_inventory())
        
        # Generar resumen
        summary = {
            'by_category': {},
            'by_severity': {
                'CRITICAL': 0,
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'INFO': 0
            }
        }
        
        for alert in all_alerts:
            # Contar por severidad
            summary['by_severity'][alert.severity] += 1
            
            # Contar por categoría
            if alert.category not in summary['by_category']:
                summary['by_category'][alert.category] = 0
            summary['by_category'][alert.category] += 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'scope': scope,
            'alerts': [alert.to_dict() for alert in all_alerts],
            'summary': summary,
            'total_alerts': len(all_alerts),
            'critical_count': summary['by_severity']['CRITICAL']
        }
        
        self.logger.info(
            f"Validación completa: {len(all_alerts)} alertas "
            f"({summary['by_severity']['CRITICAL']} críticas)"
        )
        
        return report
    
    def get_critical_alerts_only(self) -> List[Dict]:
        """Retorna solo alertas críticas (para dashboard)"""
        report = self.run_all_validations()
        return [
            alert for alert in report['alerts']
            if alert['severity'] == 'CRITICAL'
        ]


# ═══════════════════════════════════════════════════════════════════════════
#                            INSTANCIA GLOBAL
# ═══════════════════════════════════════════════════════════════════════════

# Singleton para uso en toda la aplicación
validation_service = ValidationService()
