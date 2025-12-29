"""
╔══════════════════════════════════════════════════════════════════════════╗
║               HELPERS PARA DASHBOARD - FASE 2                            ║
║                     KPIs Financieros Mejorados                           ║
╚══════════════════════════════════════════════════════════════════════════╝

Propósito:
    Funciones auxiliares para integrar KPIs financieros avanzados
    en el dashboard principal de FincaFácil.

Uso:
    Importar estas funciones en dashboard_main.py para mostrar
    métricas financieras consolidadas.

Autor: Arquitecto Senior - Fase 2
Fecha: Diciembre 2025
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple
import customtkinter as ctk
from tkinter import messagebox

from src.services.financial_service import financial_service
from src.services.validation_service import validation_service


def obtener_kpis_dashboard(periodo: str = 'mes_actual') -> Dict:
    """
    Obtiene todos los KPIs financieros para el dashboard.
    
    Args:
        periodo: 'mes_actual', 'mes_anterior', 'anio_actual', 'ultimos_30_dias'
    
    Returns:
        Diccionario completo con KPIs, incluyendo alertas
    """
    return financial_service.get_dashboard_kpis(periodo)


def crear_tarjeta_kpi(parent, titulo: str, valor: str, subtitulo: str = "",
                     color: str = "#2E7D32", icon: str = "💰") -> ctk.CTkFrame:
    """
    Crea una tarjeta visual para mostrar un KPI.
    
    Args:
        parent: Frame padre donde insertar la tarjeta
        titulo: Título del KPI
        valor: Valor principal a mostrar
        subtitulo: Texto adicional (opcional)
        color: Color del borde izquierdo
        icon: Emoji o ícono
    
    Returns:
        Frame de la tarjeta creada
    """
    # Frame principal con borde colorido
    card = ctk.CTkFrame(parent, corner_radius=10, border_width=2, border_color=color)
    
    # Barra lateral de color
    color_bar = ctk.CTkFrame(card, width=5, fg_color=color, corner_radius=0)
    color_bar.pack(side="left", fill="y", padx=(0, 10))
    
    # Contenido
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    # Ícono + Título
    header = ctk.CTkFrame(content, fg_color="transparent")
    header.pack(fill="x", pady=(0, 5))
    
    ctk.CTkLabel(
        header,
        text=f"{icon} {titulo}",
        font=("Segoe UI", 12, "bold"),
        anchor="w"
    ).pack(side="left")
    
    # Valor principal
    ctk.CTkLabel(
        content,
        text=valor,
        font=("Segoe UI", 20, "bold"),
        anchor="w"
    ).pack(fill="x")
    
    # Subtítulo (si existe)
    if subtitulo:
        ctk.CTkLabel(
            content,
            text=subtitulo,
            font=("Segoe UI", 10),
            text_color="gray",
            anchor="w"
        ).pack(fill="x")
    
    return card


def crear_seccion_kpis_financieros(parent_frame) -> ctk.CTkFrame:
    """
    Crea una sección completa con KPIs financieros.
    
    Args:
        parent_frame: Frame padre donde insertar la sección
    
    Returns:
        Frame de la sección completa
    """
    # Frame contenedor
    section = ctk.CTkFrame(parent_frame, corner_radius=15)
    section.pack(fill="x", padx=15, pady=10)
    
    # Título de la sección
    header = ctk.CTkFrame(section, fg_color="transparent")
    header.pack(fill="x", padx=15, pady=(15, 10))
    
    ctk.CTkLabel(
        header,
        text="💰 KPIs Financieros (Mes Actual)",
        font=("Segoe UI", 18, "bold"),
        anchor="w"
    ).pack(side="left")
    
    # Botón para actualizar
    ctk.CTkButton(
        header,
        text="🔄",
        width=30,
        command=lambda: actualizar_kpis_dashboard(section)
    ).pack(side="right")
    
    # Contenedor de tarjetas
    cards_container = ctk.CTkFrame(section, fg_color="transparent")
    cards_container.pack(fill="x", padx=15, pady=(0, 15))
    
    # Grid de tarjetas (2 columnas)
    cards_container.columnconfigure(0, weight=1)
    cards_container.columnconfigure(1, weight=1)
    
    # Obtener KPIs
    kpis = obtener_kpis_dashboard('mes_actual')
    
    # Tarjeta 1: Ingresos Totales
    card1 = crear_tarjeta_kpi(
        cards_container,
        "Ingresos Totales",
        f"${kpis['ingresos_totales']:,.0f}",
        f"Animales: ${kpis['ingresos_animales']:,.0f} | Leche: ${kpis['ingresos_leche']:,.0f}",
        color="#2E7D32",
        icon="💵"
    )
    card1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    
    # Tarjeta 2: Costos Totales
    card2 = crear_tarjeta_kpi(
        cards_container,
        "Costos Totales",
        f"${kpis['costos_totales']:,.0f}",
        f"Nómina: ${kpis['costos_nomina']:,.0f} | Otros: ${kpis['costos_tratamientos'] + kpis['costos_insumos']:,.0f}",
        color="#D32F2F",
        icon="💸"
    )
    card2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    # Tarjeta 3: Margen Bruto
    margen_color = "#2E7D32" if kpis['margen_bruto'] >= 0 else "#D32F2F"
    margen_icon = "📈" if kpis['margen_bruto'] >= 0 else "📉"
    
    card3 = crear_tarjeta_kpi(
        cards_container,
        "Margen Bruto",
        f"${kpis['margen_bruto']:,.0f}",
        f"Margen: {kpis['margen_porcentaje']:.1f}%",
        color=margen_color,
        icon=margen_icon
    )
    card3.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    
    # Tarjeta 4: Costo por Litro
    if kpis['costo_por_litro']:
        card4 = crear_tarjeta_kpi(
            cards_container,
            "Costo por Litro",
            f"${kpis['costo_por_litro']:,.0f}/L",
            f"Precio prom: ${kpis['precio_promedio_leche']:,.0f}/L" if kpis['precio_promedio_leche'] else "Sin ventas",
            color="#1976D2",
            icon="🥛"
        )
        card4.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    # Mostrar alertas si existen
    if kpis['alertas']:
        alertas_frame = ctk.CTkFrame(section, fg_color="#FFF3CD", corner_radius=10)
        alertas_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            alertas_frame,
            text="⚠️ Alertas Financieras",
            font=("Segoe UI", 12, "bold"),
            text_color="#856404"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        for alert in kpis['alertas'][:3]:  # Mostrar máximo 3
            ctk.CTkLabel(
                alertas_frame,
                text=f"• {alert['message']}",
                font=("Segoe UI", 10),
                text_color="#856404",
                anchor="w"
            ).pack(anchor="w", padx=20, pady=2)
        
        if len(kpis['alertas']) > 3:
            ctk.CTkLabel(
                alertas_frame,
                text=f"... y {len(kpis['alertas']) - 3} alertas más",
                font=("Segoe UI", 9, "italic"),
                text_color="#856404",
                anchor="w"
            ).pack(anchor="w", padx=20, pady=(2, 10))
    
    return section


def actualizar_kpis_dashboard(section_frame):
    """
    Actualiza los KPIs del dashboard (recarga datos).
    
    Args:
        section_frame: Frame de la sección a actualizar
    """
    # Destruir widgets existentes
    for widget in section_frame.winfo_children():
        widget.destroy()
    
    # Recrear sección
    crear_seccion_kpis_financieros(section_frame.master)
    
    messagebox.showinfo("Actualizado", "KPIs financieros actualizados correctamente")


def crear_boton_alertas_criticas(parent_frame) -> ctk.CTkButton:
    """
    Crea un botón para mostrar alertas críticas del sistema.
    
    Args:
        parent_frame: Frame padre
    
    Returns:
        Botón creado
    """
    def mostrar_alertas():
        alertas = validation_service.get_critical_alerts_only()
        
        if not alertas:
            messagebox.showinfo(
                "Validaciones",
                "✅ No hay alertas críticas en el sistema.\n\n"
                "Todas las operaciones cumplen con las reglas de negocio.",
                icon='info'
            )
        else:
            mensaje = f"🚨 Se encontraron {len(alertas)} alertas CRÍTICAS:\n\n"
            
            for i, alert in enumerate(alertas[:5], 1):
                mensaje += f"{i}. [{alert['category']}] {alert['message']}\n"
            
            if len(alertas) > 5:
                mensaje += f"\n... y {len(alertas) - 5} alertas más.\n"
            
            mensaje += "\nEjecute el script de auditoría para detalles completos."
            
            messagebox.showwarning("Alertas Críticas", mensaje)
    
    btn = ctk.CTkButton(
        parent_frame,
        text="🔍 Ver Alertas Críticas",
        command=mostrar_alertas,
        fg_color="#D32F2F",
        hover_color="#B71C1C",
        width=180
    )
    
    return btn


def crear_comparativa_periodos(parent_frame) -> ctk.CTkFrame:
    """
    Crea una sección con comparativa mes actual vs anterior.
    
    Args:
        parent_frame: Frame padre
    
    Returns:
        Frame de la comparativa
    """
    section = ctk.CTkFrame(parent_frame, corner_radius=15)
    section.pack(fill="x", padx=15, pady=10)
    
    # Título
    ctk.CTkLabel(
        section,
        text="📊 Comparativa Mes Actual vs Anterior",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(15, 10))
    
    # Calcular fechas
    hoy = date.today()
    fecha_fin_actual = hoy
    fecha_inicio_actual = date(hoy.year, hoy.month, 1)
    
    primer_dia_mes = date(hoy.year, hoy.month, 1)
    fecha_fin_anterior = primer_dia_mes - timedelta(days=1)
    fecha_inicio_anterior = date(fecha_fin_anterior.year, fecha_fin_anterior.month, 1)
    
    # Obtener comparación
    comparacion = financial_service.compare_periods(
        fecha_inicio_anterior, fecha_fin_anterior,
        fecha_inicio_actual, fecha_fin_actual
    )
    
    # Contenedor de métricas
    metrics = ctk.CTkFrame(section, fg_color="transparent")
    metrics.pack(fill="x", padx=15, pady=(0, 15))
    
    # Grid de 3 columnas
    for i in range(3):
        metrics.columnconfigure(i, weight=1)
    
    # Función auxiliar para crear métrica
    def crear_metrica_comparativa(col, titulo, valor_anterior, valor_actual, variacion_pct):
        card = ctk.CTkFrame(metrics, corner_radius=10)
        card.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 5))
        
        # Valores
        ctk.CTkLabel(
            card,
            text=f"Anterior: ${valor_anterior:,.0f}",
            font=("Segoe UI", 9),
            text_color="gray"
        ).pack()
        
        ctk.CTkLabel(
            card,
            text=f"Actual: ${valor_actual:,.0f}",
            font=("Segoe UI", 11, "bold")
        ).pack()
        
        # Variación
        if variacion_pct >= 0:
            var_color = "#2E7D32"
            var_icon = "↗"
        else:
            var_color = "#D32F2F"
            var_icon = "↘"
        
        ctk.CTkLabel(
            card,
            text=f"{var_icon} {abs(variacion_pct):.1f}%",
            font=("Segoe UI", 12, "bold"),
            text_color=var_color
        ).pack(pady=(5, 10))
    
    # Crear métricas
    crear_metrica_comparativa(
        0, "Ingresos",
        comparacion['periodo1']['ingresos'],
        comparacion['periodo2']['ingresos'],
        comparacion['variaciones']['ingresos_pct']
    )
    
    crear_metrica_comparativa(
        1, "Costos",
        comparacion['periodo1']['costos'],
        comparacion['periodo2']['costos'],
        comparacion['variaciones']['costos_pct']
    )
    
    crear_metrica_comparativa(
        2, "Margen",
        comparacion['periodo1']['margen'],
        comparacion['periodo2']['margen'],
        comparacion['variaciones']['margen_pct']
    )
    
    return section


# ═══════════════════════════════════════════════════════════════════════════
#                      INSTRUCCIONES DE INTEGRACIÓN
# ═══════════════════════════════════════════════════════════════════════════

"""
INTEGRACIÓN EN DASHBOARD (dashboard_main.py)
=============================================

1. IMPORTAR HELPERS:
    from src.modules.dashboard.dashboard_helpers_fase2 import (
        crear_seccion_kpis_financieros,
        crear_boton_alertas_criticas,
        crear_comparativa_periodos
    )

2. AGREGAR SECCIÓN DE KPIs en crear_widgets():
    # Después de las tarjetas de KPIs básicos (animales, producción, etc.)
    
    # KPIs Financieros (Fase 2)
    kpis_financieros = crear_seccion_kpis_financieros(self.scrollable_frame)
    
    # Comparativa de períodos
    comparativa = crear_comparativa_periodos(self.scrollable_frame)
    
    # Botón de alertas críticas (colocar en header o sidebar)
    btn_alertas = crear_boton_alertas_criticas(self.header_frame)
    btn_alertas.pack(side="right", padx=10)

3. OPCIONAL - Actualización automática:
    def actualizar_dashboard_automatico(self):
        '''Actualiza dashboard cada 5 minutos'''
        self.after(300000, self.actualizar_dashboard_automatico)  # 5 min
        # Llamar a actualizar_kpis_dashboard()

4. RESULTADO VISUAL:
    ┌────────────────────────────────────────────────────────┐
    │ 💰 KPIs Financieros (Mes Actual)             🔄        │
    ├────────────────────────────────────────────────────────┤
    │ ┌──────────────────────┐ ┌──────────────────────┐    │
    │ │ 💵 Ingresos Totales  │ │ 💸 Costos Totales    │    │
    │ │ $15,240,000          │ │ $8,650,000           │    │
    │ │ Animales: $12M | ... │ │ Nómina: $5M | ...    │    │
    │ └──────────────────────┘ └──────────────────────┘    │
    │ ┌──────────────────────┐ ┌──────────────────────┐    │
    │ │ 📈 Margen Bruto      │ │ 🥛 Costo por Litro   │    │
    │ │ $6,590,000           │ │ $850/L               │    │
    │ │ Margen: 43.2%        │ │ Precio prom: $1500/L │    │
    │ └──────────────────────┘ └──────────────────────┘    │
    │ ┌──────────────────────────────────────────────────┐  │
    │ │ ⚠️ Alertas Financieras                           │  │
    │ │ • Nómina representa 57.8% de costos totales     │  │
    │ └──────────────────────────────────────────────────┘  │
    └────────────────────────────────────────────────────────┘
"""
