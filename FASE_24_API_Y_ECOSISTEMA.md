# FASE 24 — API Pública, Integraciones y Ecosistema
**Versión:** 1.0  
**Fecha:** 2025-12-28  
**Responsable:** CTO + Head of Integrations  
**Objetivo:** Habilitar extensión segura de FincaFácil sin perder control.

---
## 1. Principios
- **Seguridad primero:** API Keys + OAuth2/JWT, rate limiting, auditoría de llamadas.
- **Control de exposición:** Lo que se expone es mínimo necesario; datos sensibles solo vía contratos enterprise.
- **Compatibilidad:** No romper v2.0.0; versionado semántico en API (v1, v1.1…); deprecaciones con 90 días de aviso.
- **Observabilidad:** Logging, métricas por endpoint, alertas de abuso.

---
## 2. Alcance de Exposición
- **Expuesto (core):** Autenticación, animales, ordeños, tratamientos, alertas, métricas básicas, usuarios, roles, catálogos.
- **Expuesto (avanzado bajo contrato):** Predicciones IA, bulk import/export, webhooks, configuraciones de tenant.
- **No expuesto:** Model weights, lógica propietaria, pipelines internos, datos sin anonimizar de terceros.
- **Requiere contrato especial:** Datos agregados premium, custom models, white-label endpoints.

---
## 3. Autenticación y Seguridad
- **API Keys** para integraciones servidor-servidor simples.
- **OAuth2 (Client Credentials)** para integraciones de terceros y ERPs.
- **JWT** con expiración corta; refresh tokens seguros.
- **Rate limiting:** Default 100 req/min; burst control; límites diferenciados por plan.
- **Scope y roles:** scopes por recurso (read:animal, write:animal, admin:tenant).
- **Auditoría:** Log de request/response (metadatos) + firma opcional.

---
## 4. Webhooks
- Eventos soportados: `animal.created`, `animal.updated`, `ordeño.created`, `alerta.critica`, `prediccion.listo`.
- Entrega: retries exponenciales, firma HMAC, endpoint healthcheck.
- Seguridad: secreto por webhook, IP allowlist opcional.

---
## 5. Versionado
- Prefijo `/api/v1/` estable.
- Nuevas funciones en `/api/v1alpha/` con feature flags.
- Deprecaciones: aviso ≥90 días; métricas de uso para decidir retiro.

---
## 6. Integraciones Tipo
- **Sensores IoT:** Ingesta de datos de producción, temperatura; validación de formato; buffering anti-picos.
- **ERPs rurales:** Sync inventario, contabilidad básica, órdenes de compra; mappings de campos.
- **Apps móviles:** Autenticación OAuth; endpoints livianos; paginación estricta.
- **Sistemas gubernamentales:** Endpoints certificados; logs auditables; anonimización si se comparten datos agregados.

---
## 7. Seguridad Operativa
- **Rotación de llaves:** Semestral (mínimo) o inmediato ante incidente.
- **Pruebas de abuso:** Fuzzing trimestral; WAF activado; bloqueos automáticos.
- **Protección datos:** No PII en logs; cifrado extremo a extremo; masking en respuestas donde aplique.

---
## 8. Observabilidad y SLA
- **Métricas:** Latencia p50/p95/p99, tasa de error, QPS, tasa de throttling, eventos webhook entregados.
- **SLA API:** 99.95% uptime para tier enterprise; 99.5% para estándar.
- **Alertas:** Latencia >2s, tasa error >1%, spikes de 429.

---
## 9. Deliverables
- [OPENAPI_FINCAFACIL.yaml](OPENAPI_FINCAFACIL.yaml)
- [GUIA_INTEGRACIONES_TERCEROS.md](GUIA_INTEGRACIONES_TERCEROS.md)
- Actualización CHANGELOG en v2.1.0

---
## 10. Próximos Pasos
1) Publicar OpenAPI 3.x y portal de desarrolladores.  
2) Implementar API Gateway (Kong) con rate limiting y analítica.  
3) Definir planes de uso (free/standard/enterprise) y límites.  
4) Habilitar sandbox + llaves temporales.  
5) Monitorear early adopters (3–5 integradores piloto).
