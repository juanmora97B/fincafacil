# 📊 Módulo de Pesaje de Leche - v2.0

## ✨ Mejoras Implementadas

### 1. **Sistema de Análisis y Validación**
✅ Validación automática de cantidad de leche producida  
✅ Identificación de vacas con baja producción (< 5L)  
✅ Estadísticas diarias y mensuales en tiempo real  
✅ Información de última 3 días por animal  

### 2. **Comparativa de Meses**
✅ Compara mes anterior vs mes actual por cada vaca  
✅ Calcula cambio porcentual en producción  
✅ Filtro por animal específico o todas las vacas  
✅ Muestra días registrados, totales y promedios  

### 3. **Gráficas Profesionales** 📈
✅ **Producción Total Diaria**: Línea temporal del mes  
✅ **Producción por Vaca**: Barras con código de colores  
✅ **Comparativa Meses**: Cambio porcentual visual  
✅ **Vacas Bajas**: Ranking de animales problémáticos  

### 4. **Interfaz Profesional**
✅ Organización en 4 pestañas (Registro, Análisis, Comparativa, Gráficas)  
✅ Tema oscuro consistente con la aplicación  
✅ Tooltips informativos en todos los campos  
✅ Botones de acción claros y accesibles  

---

## 📂 Estructura

```
modules/leche/
├── pesaje_leche.py          # Módulo principal (v2.0 mejorado)
├── pesaje_leche_old.py      # Backup de versión anterior
└── __pycache__/
```

---

## 🎯 Características Clave

### **Límite de Producción Baja: 5 Litros**
El sistema marca automáticamente como "baja producción" a cualquier vaca que produzca menos de 5 litros en promedio durante el mes.

### **Análisis Inteligente**
- Calcula automáticamente promedio por vaca
- Identifica tendencias en últimos 3 días
- Compara con mes anterior

### **Gráficas Interactivas**
- Seleccione tipo de gráfica
- Filtros dinámicos por animal
- Exportable a pantalla

---

## 🔧 Configuración

Para cambiar el límite de baja producción, edite en `pesaje_leche.py`:

```python
self.LIMITE_PRODUCCION_BAJA = 5.0  # Cambiar a otro valor si desea
```

---

## 📋 Requisitos

- matplotlib (instalado automáticamente)
- Python 3.7+
- SQLite3

---

## 🚀 Uso Rápido

1. **Seleccione Finca** en el combobox
2. **Ingrese Datos** en la pestaña "Registro Diario"
3. **Analice** en la pestaña "Análisis y Validación"
4. **Compare** meses en la pestaña "Comparativa de Meses"
5. **Visualice** gráficas en la pestaña "Gráficas"

---

## 📊 Tipo de Reportes Disponibles

| Reporte | Ubicación | Datos |
|---------|-----------|-------|
| Registros diarios | Tab Registro | Últimos 30 días |
| Análisis actual | Tab Análisis | Hoy y mes actual |
| Vacas bajas | Tab Análisis | Promedio < 5L |
| Comparativa | Tab Comparativa | Mes anterior vs actual |
| Gráficas | Tab Gráficas | 4 tipos diferentes |

---

## 💡 Consejos de Uso

1. **Revisión Diaria**: Use la pestaña Análisis para ver qué vacas ordeñar
2. **Monitoreo Semanal**: Verifique vacas bajas para intervención temprana
3. **Evaluación Mensual**: Use Comparativa para evaluar cambios
4. **Reportes**: Capture gráficas para presentaciones

---

**Versión**: 2.0  
**Estado**: ✅ Producción  
**Última actualización**: Diciembre 2025

Para documentación completa, ver: `GUIA_PESAJE_LECHE_V2.md`
