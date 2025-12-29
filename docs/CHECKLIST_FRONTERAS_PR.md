# CHECKLIST DE FRONTERAS PARA PR (Fase 7.3)

**Uso:** Copia/pega esta tabla en la descripción del PR y marca cada ítem. Si algún ítem falla, explica la excepción o rechaza el cambio.

| # | Regla | Ejemplo ❌ | Ejemplo ✅ |
|---|-------|------------|-----------|
| 1 | UI NO importa Infra | `from database import get_connection` en una vista | UI llama a un caso de uso de Dominio |
| 2 | Dominio NO importa UI | `from ui.formularios import ...` en lógica de negocio | Dominio solo depende de repositorios/puertos |
| 3 | Utils NO importa Dominio/UI/Infra | `from dominio.animales import ...` dentro de utils | Utils solo usa stdlib o helpers internos |
| 4 | Validaciones técnicas vienen de `modules.utils.validators` | `from modules.utils.validaciones import validar_email` | `from modules.utils.validators import validator` |
| 5 | No se usa legacy nuevo | Nuevo archivo importando `modules.utils.validaciones` | Código nuevo usa APIs modernas documentadas |
| 6 | No hay re-exports con `from modules.utils import *` | Uso de import * para acortar rutas | Imports explícitos y locales |
| 7 | UI no accede a BD directamente | `db.execute(...)` en controlador UI | UI invoca Dominio; Infra encapsula BD |
| 8 | Dominio accede a Infra solo vía puerto/repositorio | Dominio llama `get_connection()` directo | Dominio usa repositorio o servicio de Infra |
| 9 | Utils no actúa como "god module" | Utils expone funciones de Dominio o Infra | Utils limita a utilidades técnicas puras |
|10 | Sin nuevos fallbacks/aliases cruzando capas | try/except para importar de capas diferentes | Imports directos y claros |
|11 | Legacy permanece congelado | Cambios en APIs marcadas en CONTRATO_LEGACY | Legacy intacto; si toca, abrir fase | 
|12 | Reporte de fronteras revisado (opcional) | Ignorar `REPORT_FRONTERAS.md` si hay warnings | Revisar y adjuntar resultado del reporte |

## Cómo usar este checklist en PRs
1. Ejecuta (opcional pero recomendado) el auditor: `python tools/auditar_fronteras.py`.
2. Revisa el `REPORT_FRONTERAS.md`; si hay violaciones, corrige o documenta excepción.
3. Marca cada ítem de la tabla en la descripción del PR.
4. Si alguna regla no se cumple, documenta la justificación y quién aprobó la excepción.
5. Merge solo si todos los ítems están OK o con excepción aprobada explícitamente.
