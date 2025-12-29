# 🚦 Taxonomía de Errores de Dominio (Contrato — sin implementación)

FASE 8.6.2 — Documento de referencia. No se crean clases en esta fase.

## Clases previstas
- EntidadNoExisteError: ID no corresponde a entidad existente.
- EstadoInvalidoError: Estado enviado no permitido según catálogo/reglas.
- ViolacionIntegridadError: Violación de FK/UNIQUE u otras restricciones.
- ParametroInvalidoError: Formato/semántica de parámetro incorrecto.
- OperacionNoPermitidaError: Reglas del dominio impiden la transición.

## Lineamientos
- Los Services lanzarán estos errores en FASE 8.6.3+.
- Se mantendrá `ValueError` temporalmente para compatibilidad; se mapeará a las nuevas clases de error.
- Mensajes claros y accionables (indicar entidad/campo/causa).
