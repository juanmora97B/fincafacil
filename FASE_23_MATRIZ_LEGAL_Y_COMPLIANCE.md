# FASE 23 — Matriz Legal y Compliance Multipaís
**Versión:** 1.0  
**Fecha:** 2025-12-28  
**Alcance:** Colombia, México, Perú, Chile (base extensible a más países)  
**Responsable:** Legal Lead + CTO  
**Objetivo:** Garantizar operación legal de FincaFácil en LATAM sin romper v2.0.0.

---
## 1. Principios de Datos y Responsabilidad
- **Propiedad de datos del productor:** Registros operativos (animales, ordeños, tratamientos) → propiedad del productor; FincaFácil es encargado de tratamiento.
- **Propiedad de datos del sistema:** Métricas internas, logs, modelos IA entrenados con datos agregados/anonimizados → propiedad de FincaFácil.
- **Datos agregados/anonimizados:** Solo exportables si cumplen: (a) k-anonimato ≥ 20, (b) sin geolocalización exacta, (c) sin identificadores personales.
- **Decisiones automáticas:** Siempre sugerencias; nunca obligan. Requiere override humano explícito. Registrar consentimiento informado.
- **Auditoría:** Bitácora inmutable (timestamp, usuario, acción, input, output IA) retenida 12 meses (mínimo legal, extensible a 24 meses si contrato lo exige).

---
## 2. Matriz Legal Resumida (detalles en LEGAL_MATRIX_LATAM.md)
- **Protección de datos:** CO: Ley 1581; MX: Ley Federal (INAI); PE: Ley 29733; CL: Ley 19.628 (reforma en curso). Base común: consentimiento, finalidad, seguridad, derechos ARCO.
- **Uso de IA:** Transparencia y explicabilidad básica; prohibido perfilar sin consentimiento; sesgos deben auditarse (FASE 17 + FASE 21 alineados).
- **Datos agropecuarios:** Permiten uso y análisis siempre que no revelen datos personales o secretos industriales sin contrato específico.
- **Responsabilidad algorítmica:** IA = recomendación. Usuario mantiene control. SLA cubre servicio, no reemplaza criterio veterinario/agronómico.

---
## 3. Contratos Base
- **Términos de Uso:** Relación SaaS, licencia no exclusiva, prohibición de ingeniería inversa, límites de uso, jurisdicción local.
- **Acuerdo de Procesamiento de Datos (DPA):** Roles (Controlador=cliente; Encargado=FincaFácil), subencargados listados, medidas de seguridad, transferencias internacionales.
- **SLA y Responsabilidades:** Uptime 99.5%, MTTR <15min; exclusión de responsabilidad por decisiones operativas; disclaimers IA; canales de soporte.

---
## 4. Riesgos Legales y Mitigaciones
- **Mal uso de recomendaciones:** Cláusula: IA = apoyo, no sustituto; log de uso; capacitación obligatoria en onboarding.
- **Decisiones automáticas:** Requiere confirmación humana; feature flag para bloquear acciones críticas sin doble confirmación.
- **Dependencia tecnológica:** Ofrecer exportación de datos (parcial) y plan de contingencia offline; contratos con cláusula de continuidad de servicio.
- **Transferencias transfronterizas:** Usar regiones cloud conformes; SCC/Cláusulas modelo donde aplique; cifrado en tránsito/reposo.
- **Incidentes de seguridad:** Notificación ≤72h; plan de respuesta alineado con RUNBOOK_OPERATIVO + RUNBOOK_MULTI_TENANT.

---
## 5. Entregables
- [LEGAL_MATRIX_LATAM.md](LEGAL_MATRIX_LATAM.md)
- [TERMINOS_Y_RESPONSABILIDADES_BASE.md](TERMINOS_Y_RESPONSABILIDADES_BASE.md)
- Actualización de CHANGELOG (próximo release v2.1.0)

---
## 6. Checklist de Cumplimiento por País (Resumen)
- **Colombia:** Habeas Data (Ley 1581); registro de bases de datos si aplica; política publicada; consentimiento informado.
- **México:** Aviso de privacidad (INAI); derechos ARCO; transferencias internacionales informadas; SENASICA si datos veterinarios.
- **Perú:** Ley 29733; registro de banco de datos personales; consentimiento expreso; medidas de seguridad mínimas.
- **Chile:** Ley 19.628; consentimiento; atención a reforma 2024+ (posible GDPR-like). 

---
## 7. Próximos Pasos
1) Validar LEGAL_MATRIX_LATAM con asesor local en cada país.  
2) Incorporar cláusulas específicas en DPA y Términos.  
3) Entrenar soporte en disclaimers IA + manejo de derechos ARCO.  
4) Preparar anexo de transferencia internacional y plan de retención por país.  
5) Publicar políticas actualizadas en web/app (idioma local).
