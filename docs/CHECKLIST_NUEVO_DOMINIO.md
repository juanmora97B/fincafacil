# ✅ Checklist Único para Nuevos Dominios (FASE 8.7)

Objetivo: onboarding repetible y seguro. Completar en orden.

---

## 1) Auditoría Pasiva
- Inventariar UI y puntos de acceso a BD
- Documentar violaciones de frontera (UI→BD)
- Sin cambios de código

## 2) Encapsulación de Infraestructura
- Crear Repository con todas las queries necesarias
- Crear Service con validaciones y orquestación
- Exportar API en `__init__.py`
- Pylance: 0 errores

## 3) Migración Gradual de UI
- Reemplazar catálogos (`cargar_*`) por llamadas al Service
- Migrar lecturas (`listar_*` / `obtener_historial_*`)
- Migrar escrituras (`registrar_*`, `actualizar_*`, `marcar_*`)
- Capturar errores (`ValueError`) y mostrar mensajes claros

## 4) Validaciones y Catálogos
- Validaciones en Service (no UI)
- Estados/tipos desde gateway o tablas (no hardcoded)

## 5) Auditor y Calidad
- Auditor de fronteras: Exit 0
- Pylance: 0 errores
- Pruebas manuales: CRUD + catálogos

## 6) Documentación Final
- Estado final y métricas
- Lecciones aprendidas
- Riesgos remanentes y próximos pasos

---

## Reglas rápidas
- Filtros por ID (`*_id: Optional[int]`), nunca por nombre
- UI no llama `ejecutar_consulta`
- Service no contiene SQL
- Repository no contiene reglas de negocio

Referencias:
- Guía: [docs/GUIA_DESARROLLO_DOMINIOS.md](GUIA_DESARROLLO_DOMINIOS.md)
- Contratos: [src/dominio/contratos/service_contracts.py](../src/dominio/contratos/service_contracts.py)
- Adopción: [docs/FASE8_6_3_ADOPCION_Y_DEPRECACION.md](FASE8_6_3_ADOPCION_Y_DEPRECACION.md)
