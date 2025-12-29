"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   HELPERS PARA INTEGRACIÓN FASE 2                        ║
║                   Módulo de Ventas - FincaFácil                          ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Funciones auxiliares para integrar las validaciones y cálculos
    de la Fase 2 en el módulo de ventas existente.

Uso:
    Importar y usar estas funciones en lugar de las validaciones básicas.

Autor: Arquitecto Senior - Fase 2
Fecha: Diciembre 2025
"""

from datetime import datetime, date
from typing import Tuple, Optional, Dict
from tkinter import messagebox
import logging

from src.core.business_rules import business_rules, BusinessRuleViolation
from src.services.financial_service import financial_service
from typing import Optional


def validar_venta_animal_fase2(animal_id: int, fecha_venta: str, 
                               precio: float, logger: Optional[logging.Logger] = None) -> Tuple[bool, str]:
    """
    Validación mejorada para venta de animales (Fase 2).
    
    Integra:
        - Reglas de negocio centralizadas
        - Validación de precios
        - Sugerencias de precio
    
    Args:
        animal_id: ID del animal a vender
        fecha_venta: Fecha en formato 'YYYY-MM-DD'
        precio: Precio de venta propuesto
        logger: Logger opcional para auditoría
    
    Returns:
        (True, "OK") si es válido
        (False, "Razón del error") si no pasa validación
    """
    try:
        # Convertir fecha
        fecha = datetime.strptime(fecha_venta, '%Y-%m-%d').date()
    except ValueError:
        return False, "Formato de fecha inválido. Use YYYY-MM-DD"
    
    # Validación principal de reglas de negocio
    es_valido, mensaje = business_rules.validate_animal_sale(animal_id, fecha)
    
    if not es_valido:
        if logger:
            logger.warning(f"Validación fallida para animal #{animal_id}: {mensaje}")
        return False, mensaje
    
    # Validar precio (debe ser > 0)
    if precio <= 0:
        return False, "El precio debe ser mayor a cero"
    
    # Sugerir precio si está muy bajo
    precio_sugerido = business_rules.calculate_animal_sale_price_suggestion(animal_id)
    if precio_sugerido and precio < (precio_sugerido * 0.5):
        # Si el precio es menos del 50% del sugerido, alertar
        if logger:
            logger.warning(
                f"Precio sospechoso para animal #{animal_id}: "
                f"${precio:,.0f} (sugerido: ${precio_sugerido:,.0f})"
            )
        return False, (
            f"Precio muy bajo (${precio:,.0f}). "
            f"Precio sugerido: ${precio_sugerido:,.0f}. "
            f"¿Confirmar venta con este precio?"
        )
    
    if logger:
        logger.info(f"✓ Venta de animal #{animal_id} validada: ${precio:,.0f}")
    
    return True, "OK"


def obtener_precio_sugerido_animal(animal_id: int) -> Optional[float]:
    """
    Calcula y retorna el precio de venta sugerido para un animal.
    
    Args:
        animal_id: ID del animal
    
    Returns:
        Precio sugerido en COP o None si no hay suficiente información
    """
    return business_rules.calculate_animal_sale_price_suggestion(animal_id)


def mostrar_precio_sugerido_dialog(animal_id: int, entry_precio) -> None:
    """
    Muestra un diálogo con el precio sugerido y lo rellena en el entry.
    
    Args:
        animal_id: ID del animal
        entry_precio: Entry widget donde mostrar el precio
    """
    precio_sugerido = obtener_precio_sugerido_animal(animal_id)
    
    if precio_sugerido:
        respuesta = messagebox.askyesno(
            "Precio Sugerido",
            f"Precio sugerido basado en peso, edad y producción:\n\n"
            f"${precio_sugerido:,.0f} COP\n\n"
            f"¿Desea usar este precio?",
            icon='question'
        )
        
        if respuesta:
            entry_precio.delete(0, 'end')
            entry_precio.insert(0, str(int(precio_sugerido)))
    else:
        messagebox.showinfo(
            "Precio Sugerido",
            "No hay suficiente información para calcular un precio sugerido.\n"
            "Ingrese el precio manualmente.",
            icon='info'
        )


def validar_venta_leche_fase2(litros: float, fecha_venta: str, 
                              precio_litro: float, logger: Optional[logging.Logger] = None) -> Tuple[bool, str]:
    """
    Validación mejorada para venta de leche (Fase 2).
    
    Args:
        litros: Cantidad de litros a vender
        fecha_venta: Fecha en formato 'YYYY-MM-DD'
        precio_litro: Precio por litro
        logger: Logger opcional
    
    Returns:
        (True, "OK") si es válido
        (False, "Razón") si no pasa
    """
    try:
        fecha = datetime.strptime(fecha_venta, '%Y-%m-%d').date()
    except ValueError:
        return False, "Formato de fecha inválido"
    
    # Validación principal
    es_valido, mensaje = business_rules.validate_milk_sale(litros, fecha)
    
    if not es_valido:
        if logger:
            logger.warning(f"Validación fallida para venta de leche: {mensaje}")
        return False, mensaje
    
    # Validar precio por litro
    if precio_litro <= 0:
        return False, "El precio por litro debe ser mayor a cero"
    
    # Alertar si el precio está fuera de rango típico ($500 - $3000)
    if precio_litro < 500 or precio_litro > 3000:
        if logger:
            logger.warning(f"Precio sospechoso para leche: ${precio_litro:,.0f}/L")
        return False, (
            f"Precio por litro fuera de rango típico (${precio_litro:,.0f}/L). "
            f"Rango esperado: $500 - $3,000/L. ¿Confirmar?"
        )
    
    if logger:
        logger.info(f"✓ Venta de leche validada: {litros}L a ${precio_litro:,.0f}/L")
    
    return True, "OK"


def obtener_estadisticas_ventas_periodo(fecha_inicio: str, fecha_fin: str) -> Dict:
    """
    Obtiene estadísticas financieras de ventas para un período.
    
    Args:
        fecha_inicio: Fecha inicial 'YYYY-MM-DD'
        fecha_fin: Fecha final 'YYYY-MM-DD'
    
    Returns:
        Diccionario con estadísticas financieras
    """
    fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    ingresos = financial_service.calculate_total_revenue(fecha_ini, fecha_fin_date)
    
    return {
        'total_ingresos': ingresos['total'],
        'ingresos_animales': ingresos['ventas_animales'],
        'ingresos_leche': ingresos['ventas_leche'],
        'precio_promedio_animal': financial_service.calculate_average_animal_price(fecha_ini, fecha_fin_date),
        'precio_promedio_leche': financial_service.calculate_average_milk_price(fecha_ini, fecha_fin_date)
    }


def mostrar_estadisticas_ventas_dialog(periodo: str = 'mes_actual') -> None:
    """
    Muestra un diálogo con estadísticas de ventas.
    
    Args:
        periodo: 'mes_actual', 'mes_anterior', 'anio_actual', 'ultimos_30_dias'
    """
    hoy = date.today()
    
    if periodo == 'mes_actual':
        fecha_inicio = date(hoy.year, hoy.month, 1)
        fecha_fin = hoy
        titulo = f"Estadísticas - {fecha_inicio.strftime('%B %Y')}"
    elif periodo == 'mes_anterior':
        primer_dia_mes = date(hoy.year, hoy.month, 1)
        from datetime import timedelta
        fecha_fin = primer_dia_mes - timedelta(days=1)
        fecha_inicio = date(fecha_fin.year, fecha_fin.month, 1)
        titulo = f"Estadísticas - {fecha_inicio.strftime('%B %Y')}"
    else:  # ultimos_30_dias
        from datetime import timedelta
        fecha_fin = hoy
        fecha_inicio = hoy - timedelta(days=30)
        titulo = "Estadísticas - Últimos 30 Días"
    
    stats = obtener_estadisticas_ventas_periodo(
        fecha_inicio.isoformat(),
        fecha_fin.isoformat()
    )
    
    mensaje = f"""
╔═══════════════════════════════════════════════════╗
║            {titulo}            ║
╚═══════════════════════════════════════════════════╝

📊 INGRESOS TOTALES: ${stats['total_ingresos']:,.0f}

   🐄 Venta de Animales: ${stats['ingresos_animales']:,.0f}
   🥛 Venta de Leche:    ${stats['ingresos_leche']:,.0f}

💰 PRECIOS PROMEDIO:

   Animal: ${stats['precio_promedio_animal']:,.0f} (por unidad)
   Leche:  ${stats['precio_promedio_leche']:,.0f}/L

──────────────────────────────────────────────────────
Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}
"""
    
    messagebox.showinfo("Estadísticas de Ventas", mensaje)


def ejecutar_validaciones_ventas() -> Dict:
    """
    Ejecuta todas las validaciones automáticas del módulo de ventas.
    
    Returns:
        Reporte con alertas encontradas
    """
    from src.services.validation_service import validation_service
    
    alertas_animales = validation_service.validate_animal_sales()
    alertas_leche = validation_service.validate_milk_sales()
    
    return {
        'alertas_animales': [alert.to_dict() for alert in alertas_animales],
        'alertas_leche': [alert.to_dict() for alert in alertas_leche],
        'total_criticas': sum(
            1 for a in (alertas_animales + alertas_leche)
            if a.severity == 'CRITICAL'
        )
    }


def mostrar_alertas_ventas_dialog() -> None:
    """
    Muestra un diálogo con las alertas del módulo de ventas.
    """
    reporte = ejecutar_validaciones_ventas()
    
    total_alertas = len(reporte['alertas_animales']) + len(reporte['alertas_leche'])
    criticas = reporte['total_criticas']
    
    if total_alertas == 0:
        messagebox.showinfo(
            "Validaciones",
            "✅ No se encontraron problemas en el módulo de ventas.\n\n"
            "Todas las ventas cumplen con las reglas de negocio.",
            icon='info'
        )
    else:
        mensaje = f"⚠️ Se encontraron {total_alertas} alertas:\n\n"
        
        if criticas > 0:
            mensaje += f"🔴 {criticas} alertas CRÍTICAS\n\n"
            mensaje += "Alertas críticas encontradas:\n"
            
            for alert in reporte['alertas_animales'][:3]:  # Mostrar primeras 3
                if alert['severity'] == 'CRITICAL':
                    mensaje += f"• {alert['message']}\n"
            
            for alert in reporte['alertas_leche'][:3]:
                if alert['severity'] == 'CRITICAL':
                    mensaje += f"• {alert['message']}\n"
            
            mensaje += "\nRevise el log para más detalles."
        else:
            mensaje += "Alertas de advertencia. Ver log para detalles."
        
        messagebox.showwarning("Alertas de Validación", mensaje)


# ═══════════════════════════════════════════════════════════════════════════
#                      INSTRUCCIONES DE USO
# ═══════════════════════════════════════════════════════════════════════════

"""
INTEGRACIÓN EN MÓDULO VENTAS (ventas_main.py)
==============================================

1. IMPORTAR HELPERS:
    from src.modules.ventas.ventas_helpers_fase2 import (
        validar_venta_animal_fase2,
        obtener_precio_sugerido_animal,
        mostrar_precio_sugerido_dialog,
        mostrar_estadisticas_ventas_dialog,
        mostrar_alertas_ventas_dialog
    )

2. REEMPLAZAR VALIDACIÓN EN guardar_venta():
    # ANTES:
    if estado_animal == 'Vendido':
        messagebox.showerror("Error", "Este animal ya fue vendido")
        return
    
    # DESPUÉS:
    es_valido, mensaje = validar_venta_animal_fase2(
        id_animal, 
        self.entry_fecha.get(), 
        float(self.entry_precio.get()),
        self.logger
    )
    if not es_valido:
        messagebox.showerror("Validación", mensaje)
        return

3. AGREGAR BOTÓN "💡 Precio Sugerido" en formulario:
    ctk.CTkButton(
        row3,
        text="💡 Sugerido",
        command=lambda: mostrar_precio_sugerido_dialog(
            self.combo_animal.get().split("|")[0],
            self.entry_precio
        ),
        width=100
    ).pack(side="left", padx=5)

4. MEJORAR BOTÓN "📊 Estadísticas":
    En mostrar_estadisticas(), reemplazar por:
    mostrar_estadisticas_ventas_dialog('mes_actual')

5. AGREGAR BOTÓN "🔍 Validar Ventas" en historial:
    ctk.CTkButton(
        action_frame,
        text="🔍 Validar",
        command=mostrar_alertas_ventas_dialog,
        width=150
    ).pack(side="left", padx=5)
"""
