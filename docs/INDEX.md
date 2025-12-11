# 📚 ÍNDICE DE DOCUMENTACIÓN - FincaFácil

**Última Actualización**: 9 Diciembre 2025  
**Versión**: 2.0

---

## 🎯 ACCESO RÁPIDO

### Para Usuario Final
- [Manual de Usuario](#manual-de-usuario) ← **COMIENZA AQUÍ**
- [Guía Rápida](#guía-rápida) ← Respuestas en 5 minutos
- [FAQ - Preguntas Frecuentes](#faq) ← Problemas comunes

### Para Desarrollador
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Manual Técnico](#manual-técnico)
- [API y Módulos](#api-y-módulos)
- [Guía de Contribución](#guía-de-contribución)

### Para Administrador
- [Setup e Instalación](#setup-e-instalación)
- [Base de Datos](#base-de-datos)
- [Mantenimiento](#mantenimiento)
- [Reportes de Cambios](#reportes-de-cambios)

---

## 📖 DOCUMENTACIÓN PRINCIPAL

### Manual de Usuario
**Ubicación**: `docs/MANUAL_PROFESIONAL.pdf` (PRÓXIMAMENTE)

Contiene:
- ✅ Introducción al sistema
- ✅ Instalación paso a paso
- ✅ Tour interactivo explicado
- ✅ Cada módulo detallado con screenshots
- ✅ Flujos de trabajo comunes
- ✅ Solución de problemas
- ✅ Glosario de términos ganaderos
- ✅ Buenas prácticas

**Tiempo de lectura**: 2-3 horas completo

---

### Guía Rápida
**Ubicación**: `docs/referencias/GUIA_RAPIDA.md`

Para usuarios que necesitan respuestas rápidas:
- Registro de animal en 5 minutos
- Pesaje de leche paso a paso
- Crear venta en 3 clicks
- Generar reporte diario

**Tiempo de lectura**: 15 minutos

---

### FAQ - Preguntas Frecuentes
**Ubicación**: `docs/referencias/FAQ.md`

Problemas comunes:
- "¿Cómo cambio la finca de un animal?"
- "¿Dónde veo el historial de un animal?"
- "¿Cómo exporto un reporte?"
- "¿Qué significa cada estado de animal?"

---

## 🏗️ DOCUMENTACIÓN TÉCNICA

### Arquitectura del Sistema
**Ubicación**: `ARCHITECTURE.md`

Cobertura:
- Estructura modular del proyecto
- Flujo de datos entre módulos
- Patrones de diseño utilizados
- Dependencias principales
- Diagrama de componentes

**Para**: Desarrolladores y arquitectos

---

### Base de Datos
**Ubicación**: `DATABASE_SCHEMA.md`

Contiene:
- Esquema completo de todas las tablas
- Relaciones (FK) entre tablas
- Índices y optimizaciones
- Datos maestros (razas, fincas, etc.)
- Diagramas ER

**Para**: Desarrolladores y DBA

---

### Manual Técnico
**Ubicación**: `docs/tecnico/` (25+ archivos)

Documentación técnica detallada:
- Componentes de la aplicación
- Funciones clave por módulo
- Implementación de características
- Decisiones técnicas

**Para**: Desarrolladores

---

### API y Módulos
**Ubicación**: `docs/api/`

Referencia técnica:
- Cada módulo principal
- Funciones públicas
- Parámetros y valores de retorno
- Ejemplos de uso

**Para**: Integradores

---

## 📋 MÓDULOS DEL SISTEMA

### 1. Animales
- Registro de nuevos animales
- Ficha completa del animal (genealogía, salud, producción)
- Inventario con filtros
- Reubicación entre fincas
- Bitácora de comentarios

**Documento**: `docs/guias/usuarios/MODULO_ANIMALES.md`

---

### 2. Dashboard
- Panel principal con KPIs
- Gráficos de producción y estado
- Alertas del sistema
- Eventos recientes

**Documento**: `docs/guias/usuarios/MODULO_DASHBOARD.md`

---

### 3. Leche
- Pesaje de leche (mañana, tarde, noche)
- Registro automático de producción
- Reportes diarios/semanales
- Historial de producción

**Documento**: `docs/guias/usuarios/MODULO_LECHE.md`

---

### 4. Reproducción
- Nuevos servicios
- Control de gestantes
- Próximos partos
- Palpación (NUEVO)

**Documento**: `docs/guias/usuarios/MODULO_REPRODUCCION.md`

---

### 5. Ventas
- Registro de ventas
- Detalle de precios
- Historial de ventas
- Reportes de ingresos

**Documento**: `docs/guias/usuarios/MODULO_VENTAS.md`

---

### 6. Salud
- Registro de tratamientos
- Diagnósticos
- Control de medicinas
- Alertas de vencimientos

**Documento**: `docs/guias/usuarios/MODULO_SALUD.md`

---

### 7. Configuración
- Maestros de datos (razas, fincas, empleados)
- Potreros y sectores
- Diagnósticos y medicinas
- Parámetros del sistema

**Documento**: `docs/guias/usuarios/MODULO_CONFIGURACION.md`

---

Otros módulos: Reportes, Nómina, Herramientas, Insumos

---

## 🔧 INSTALACIÓN Y SETUP

### Setup Inicial
**Ubicación**: `SETUP.md`

Cubre:
- Requisitos del sistema
- Instalación de Python
- Instalación de dependencias
- Configuración inicial
- Primera ejecución

**Tiempo**: 30-45 minutos

---

### Troubleshooting
**Ubicación**: `docs/referencias/TROUBLESHOOTING.md`

Problemas comunes:
- Error de conexión a BD
- Módulo no carga
- Iconos no aparecen
- Performance lenta

---

## 📊 REPORTES Y CAMBIOS

### Historial de Cambios
**Ubicación**: `docs/cambios/`

Registro completo de:
- Features agregadas
- Bugs corregidos
- Mejoras de performance
- Cambios de UI/UX

**Archivos**:
- `CAMBIOS_2025_12.md` - Diciembre 2025
- `CAMBIOS_2025_11.md` - Noviembre 2025
- ... (histórico completo)

---

### Reportes Técnicos
**Ubicación**: `docs/reportes/`

Reportes de:
- Implementación de features
- Auditorías de código
- Análisis de performance
- Validaciones

---

## 🎓 CAPACITACIÓN

### Tour Interactivo
**Ubicación**: Dentro de la aplicación (menú Help)

Tour guiado paso a paso:
- Introducción al dashboard
- Cómo registrar un animal
- Cómo registrar pesaje
- Cómo crear una venta
- Y más...

**Duración**: 10-15 minutos

---

### Videos (Próximamente)
- Setup e instalación
- Primeros pasos
- Cada módulo paso a paso
- Tips y trucos

---

## 🔐 SEGURIDAD Y PRIVACIDAD

**Ubicación**: `docs/referencias/SEGURIDAD.md`

Cubre:
- Respaldo de datos
- Contraseñas seguras
- Privacidad de información
- Auditoría de cambios

---

## 🤝 CONTRIBUIR

### Guía para Desarrolladores
**Ubicación**: `CONTRIBUTING.md`

Para quienes quieren contribuir:
- Cómo hacer fork del proyecto
- Estándares de código
- Cómo enviar pull requests
- Proceso de review

---

## 📞 SOPORTE

### Contacto
- **Email**: jfburitica97@gmail.com
- **Teléfono**: 3013869653
- **Forum**: (próximo)
- **GitHub Issues**: (próximo)

### Horarios de Soporte
- Lunes a Viernes: 8:00 AM - 5:00 PM
- Sábados: 9:00 AM - 12:00 PM

---

## 📚 RECURSOS ADICIONALES

### Glosario
**Ubicación**: `docs/referencias/GLOSARIO.md`

Términos ganaderos explicados:
- Qué es una "Gestante"
- Qué significa "Condición Corporal"
- Diferencia entre "Novilla" y "Vaca"
- Ciclo reproductivo
- Y más...

---

### Plantillas de Carga
**Ubicación**: `plantillas de carga/`

Plantillas Excel para importar datos:
- Importar animales en masa
- Importar potreros
- Importar empleados
- Importar historiales

---

### Ejemplos de Uso
**Ubicación**: `docs/referencias/EJEMPLOS.md`

Casos de uso reales:
- Ejemplo: Comprar 10 animales nuevos
- Ejemplo: Registrar parto y productos del parto
- Ejemplo: Generar reporte mensual
- Ejemplo: Auditoría de inventario

---

## 🗺️ MAPA DEL PROYECTO

```
FincaFacil/
├── main.py                           ← Ejecutable principal
├── config.py                         ← Configuración global
├── requirements.txt                  ← Dependencias Python
│
├── modules/                          ← Módulos funcionales
│   ├── animales/                     ← Gestión de animales
│   ├── dashboard/                    ← Panel principal
│   ├── leche/                        ← Pesaje de leche
│   ├── reproduccion/                 ← Reproducción animal
│   ├── ventas/                       ← Ventas
│   ├── salud/                        ← Salud animal
│   ├── reportes/                     ← Reportes
│   ├── configuracion/                ← Maestros de datos
│   └── utils/                        ← Funciones compartidas
│
├── database/
│   ├── fincafacil.db                ← Base de datos SQLite
│   └── connection.py                 ← Gestión de conexión
│
├── docs/                             ← Documentación
│   ├── MANUAL_PROFESIONAL.pdf        ← Manual integrado (próximamente)
│   ├── guias/
│   │   ├── usuarios/                 ← Guías de usuario
│   │   └── tecnicas/                 ← Guías técnicas
│   ├── referencias/                  ← Guías rápidas
│   ├── cambios/                      ← Historial de cambios
│   ├── reportes/                     ← Reportes técnicos
│   └── api/                          ← Referencia de API
│
├── scripts/                          ← Scripts auxiliares
│   ├── maintenance/                  ← Mantenimiento
│   ├── dev/                          ← Desarrollo
│   └── archived/                     ← Scripts legacy
│
├── assets/                           ← Recursos gráficos
│   ├── 3d_soft_clay/                 ← Iconos 3D (próximamente)
│   ├── svg_icons/                    ← Iconos SVG
│   └── flaticon_animated/            ← Iconos animados
│
├── tests/                            ← Pruebas unitarias
├── plantillas de carga/              ← Plantillas Excel
├── backups/                          ← Copias de seguridad
└── config/                           ← Archivos de configuración
```

---

## ✅ ANTES DE EMPEZAR

### Checklist para Usuario Nuevo
- [ ] Leer "Guía Rápida" (15 min)
- [ ] Ejecutar Tour Interactivo (10 min)
- [ ] Registrar un animal de prueba
- [ ] Hacer pesaje de leche de prueba
- [ ] Leer módulo que uses más frecuentemente

**Tiempo total**: 1-2 horas

### Checklist para Desarrollador
- [ ] Leer `ARCHITECTURE.md`
- [ ] Leer `DATABASE_SCHEMA.md`
- [ ] Instalar entorno de desarrollo
- [ ] Ejecutar tests
- [ ] Revisar `CONTRIBUTING.md`

**Tiempo total**: 3-4 horas

---

## 📞 PREGUNTAS FRECUENTES RÁPIDAS

**P: ¿Por dónde empiezo?**  
R: Lee "Guía Rápida" en `docs/referencias/`

**P: ¿Cómo instalo el sistema?**  
R: Lee `SETUP.md`

**P: ¿Cómo registro un animal?**  
R: Módulo Animales en documentación de módulos

**P: ¿Cómo genero un reporte?**  
R: Módulo Reportes en documentación de módulos

**P: ¿Qué hago si algo no funciona?**  
R: Lee `TROUBLESHOOTING.md` en `docs/referencias/`

---

## 📈 VERSIÓN DEL DOCUMENTO

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 2.0 | 9 Dic 2025 | Reorganización completa, consolidación de documentación |
| 1.0 | Nov 2025 | Versión inicial |

---

## 📄 NOTA IMPORTANTE

Este índice centraliza acceso a TODA la documentación del proyecto. Si necesitas algo específico:

1. Busca en la tabla de contenidos arriba
2. Si no lo encuentras, revisa "Recursos Adicionales"
3. Si aún no lo encuentras, contacta a soporte

---

**Última actualización**: 9 de Diciembre de 2025  
**Siguiente revisión**: Diciembre 2025 (después de FASE 5)
