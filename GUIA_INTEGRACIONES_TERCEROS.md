# GUÍA DE INTEGRACIONES CON TERCEROS
**Versión:** 1.0  
**Fecha:** 2025-12-28  
**Responsable:** Head of Integrations  
**Compatibilidad:** API v1.0.0 (OpenAPI adjunto)

---
## 1. Requisitos Previos
- Solicitar acceso sandbox (llave API o OAuth client). 
- Aportar IPs para allowlist si aplica. 
- Firmar NDA si se consume data agregada premium. 
- Confirmar tenant de pruebas (X-Tenant-ID).

---
## 2. Seguridad y Autenticación
- **API Key:** Header `X-API-Key`. Uso recomendado server-to-server.
- **OAuth2 Client Credentials:** Token endpoint `/auth/token`; scopes por recurso.
- **Headers obligatorios:** `X-Tenant-ID` en todas las llamadas.
- **Rate limiting:** 100 req/min default; solicitar aumento con caso de uso.
- **Webhooks:** Firma HMAC; retries exponenciales; endpoint debe responder 2xx.

---
## 3. Flujos Comunes
- **Alta de animal:** `POST /animals` con identificador y estado.
- **Registro ordeño:** `POST /milking` con litros por franja.
- **Recepción alerta:** Suscribirse a webhook `alertaCritica` y validar firma.
- **Consulta predicciones (enterprise):** `GET /predicciones` con scope adecuado.

---
## 4. Buenas Prácticas
- Usar paginación (`limit`, `offset`).
- Respetar códigos HTTP (429 = throttling → backoff exponencial). 
- No guardar PII innecesaria; evitar enviar datos sensibles en claro.
- Registrar idempotency key en operaciones críticas (si se habilita).
- Monitorizar latencia y errores; activar alertas ante >1% errores.

---
## 5. Casos de Integración Tipo
- **Sensores IoT:** Buffer local → envío batched cada 5–15 min; validar timestamps; manejar pérdida de conectividad.
- **ERP rural:** Sincronizar catálogo y stock 1–4 veces/día; usar webhooks para cambios críticos.
- **App móvil partner:** OAuth; consumir solo endpoints de lectura; caché corto; mostrar disclaimers de origen de datos.
- **Gobierno/Institución:** Endpoints certificados; logs exportables; datos anonimizados; contrato específico.

---
## 6. Soporte y Escalaciones
- Canal integradores: integraciones@fincafacil.com  
- Slack/Discord: #integraciones (beta)  
- Horarios: 24/7 con severidad; P1 <30min, P2 <4h, P3 <24h.

---
## 7. Checklist de Go-Live
- [ ] Llaves rotadas y guardadas en vault.  
- [ ] Webhooks probados con `POST /webhooks/test`.  
- [ ] Monitoreo activo (latencia, errores, 429).  
- [ ] Límites de uso acordados por contrato.  
- [ ] Aviso de privacidad y términos visibles para usuarios finales.
