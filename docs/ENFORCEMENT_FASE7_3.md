# ENFORCEMENT FASE 7.3 (Fronteras del Sistema)

## Qué reglas se aplican automáticamente
- Auditoría de imports con `tools/auditar_fronteras.py` genera `REPORT_FRONTERAS.md`.
- Detecta: 
  - UI → Infra (import de `database`, `get_connection`, `db` desde UI).
  - Dominio → UI (import de `ui.*`).
  - Utils → Dominio/UI/Infra (cualquier import hacia esas zonas).
  - Uso de legacy `modules.utils.validaciones` en código nuevo.
  - `from modules.utils import *` (re-export con `*`).

## Qué reglas siguen siendo revisión humana
- Diseño de nuevos puertos/repositorios.
- Evaluar si un módulo pertenece realmente a una zona u otra (semántica de negocio).
- Validar excepciones solicitadas y su plan de reversión.
- Confirmar que no se introducen nuevos fallbacks/aliases ocultos.

## Qué NO hace esta fase
- No corrige código automáticamente.
- No refactoriza ni mueve archivos.
- No instala hooks automáticamente.
- No cambia comportamiento de producción.

## Cómo escalar violaciones
- **WARNING:** Uso de `from modules.utils import *`. Resolver antes de merge; si no es posible, justificar en el PR.
- **CRÍTICA:** Cualquier cruce de fronteras (UI→Infra, Dominio→UI, Utils→otras zonas) o uso de legacy `modules.utils.validaciones`. Debe corregirse o formalizar excepción aprobada por arquitectura.

## Flujo recomendado
1. Ejecutar `python tools/auditar_fronteras.py` localmente.
2. Revisar `REPORT_FRONTERAS.md` y adjuntar en el PR si hay hallazgos.
3. Pasar por el checklist de [docs/CHECKLIST_FRONTERAS_PR.md](docs/CHECKLIST_FRONTERAS_PR.md).
4. Si hay excepciones, documentarlas (archivo, motivo, duración) y actualizar este documento si es permanente.
