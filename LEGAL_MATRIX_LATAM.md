# LEGAL MATRIX LATAM (CO, MX, PE, CL)
**Versión:** 1.0  
**Fecha:** 2025-12-28  
**Alcance:** Protección de datos, IA, datos agropecuarios, responsabilidad algorítmica, retención, transferencias.

---
## 1. Resumen Tabla Comparativa

| Tema | Colombia (Ley 1581) | México (INAI) | Perú (Ley 29733) | Chile (Ley 19.628 / reforma) | Requisito Común |
|------|---------------------|---------------|------------------|------------------------------|-----------------|
| Base legal datos | Consentimiento (expreso), finalidad | Aviso de privacidad, consentimiento | Consentimiento expreso, registro | Consentimiento, reforma GDPR-like | Consentimiento informado |
| Derechos | ARCO (Acceso, Rectificación, Cancelación, Oposición) | ARCO | ARCO | ARCO (con reforma) | ARCO |
| Registro BD | SIC (según tipo) | No obligatorio, pero aviso | Obligatorio (RNPDP) | No (posible en reforma) | Inventario interno |
| Transferencias int. | Permiso si país adecuado o cláusulas | Informar en aviso | Consentimiento + cláusulas | Consentimiento, reglamentación futura | SCC/Cláusulas + cifrado |
| Datos sensibles | Salud, biométricos | Salud, biométricos | Salud | Salud | Minimizar, cifrar, acceso restringido |
| IA/Automated decisions | Transparencia; no decisiones sin humano | Aviso, consentimiento para perfilado | Consentimiento; evitar daño | Transparencia (reforma) | Humano en el loop, explicación |
| Retención | Definir periodo; suprimir cuando cese finalidad | Definir en aviso | Definir en registro | Definir en política | Política clara + borrado a solicitud |
| Seguridad | Medidas técnicas/organizativas | Medidas admin/técnicas | Medidas mínimas (DS 003-2013-JUS) | Medidas razonables | Cifrado, control acceso, logs |
| Sanciones | Multas hasta ~USD 400k | Multas altas (INAI) | Multas moderadas | Multas (en aumento) | Plan de respuesta + notificación |

---
## 2. Responsabilidad Algorítmica (IA)
- **Principio:** FincaFácil nunca impone decisiones; solo recomienda.
- **Explicabilidad:** Mostrar factores clave y puntaje de confianza (al menos nivel básico).
- **Consentimiento:** Para perfilado/IA, solicitar opt-in donde ley lo pida (especialmente MX, PE).
- **Mitigación de sesgos:** Auditorías trimestrales (alineado FASE 17/21).

---
## 3. Clasificación de Datos
- **Datos del productor (propiedad del cliente):** Registros operativos, geodatos, inventario, producción, tratamientos, reproducción, costos.
- **Datos del sistema (propiedad FincaFácil):** Logs, métricas de uso, modelos IA entrenados con datos agregados/anonimizados, metadata técnica.
- **Datos agregados/anonimizados (uso compartible):** Solo si k-anonimato ≥ 20 y sin geolocalización exacta; para benchmarks y analítica de mercado.

---
## 4. Retención y Borrado
- **Retención estándar:** 12 meses logs; 24 meses operativos (opcional por contrato). 
- **Derecho al olvido:** Implementar borrado selectivo por tenant/usuario en 30 días.
- **Backups:** Cifrados; retención diferenciada; borrado coordinado en restauraciones.

---
## 5. Transferencias Internacionales
- **Cifrado:** TLS 1.2+, AES-256 reposo.
- **Ubicación:** Regiones cloud con cumplimiento local; preferir región en país si disponible.
- **Contratos:** SCC/Cláusulas modelo para MX/PE/CL; autorización SIC para CO si aplica.

---
## 6. Contratos y Políticas
- **Términos de uso:** Jurisdicción local; limitación de responsabilidad; prohibición de uso indebido.
- **DPA:** Roles, subencargados, medidas de seguridad, transferencias, retención, auditorías.
- **SLA:** Uptime 99.5%+, MTTR <15min; exclusión por mal uso; soporte 24/7 escalable.
- **Política de privacidad:** Idioma local; avisos de cookies si web; canal de derechos ARCO.

---
## 7. Riesgos Específicos y Plan
- **Mal uso IA:** Disclaimers + capacitación; doble confirmación en acciones críticas.
- **Datos veterinarios sensibles:** Validar permisos (SENASICA MX, autoridades locales PE/CL); anonimizar cuando se exporte.
- **Cambios normativos:** Monitoreo trimestral; reforma Chile 2024+; ajustes contractuales.

---
## 8. Checklist Operable
- [ ] Aviso/Política por país publicada.  
- [ ] Consentimiento explícito (MX/PE) habilitado en app.  
- [ ] Registro de BD (CO/PE) si aplica.  
- [ ] DPA firmado con clientes enterprise.  
- [ ] Logs auditables activos (12–24m).  
- [ ] Plan de borrado selectivo por tenant listo.  
- [ ] Plan de notificación de incidentes ≤72h.
