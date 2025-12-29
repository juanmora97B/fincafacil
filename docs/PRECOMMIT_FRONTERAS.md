# PRE-COMMIT DE FRONTERAS (Fase 7.3)

Este archivo documenta cómo ejecutar la verificación de fronteras antes de hacer commit. **No instala hooks automáticamente.**

## Comando sugerido

```bash
python tools/auditar_fronteras.py
```

## Qué hacer si falla
- Revisa `REPORT_FRONTERAS.md` generado en la raíz.
- Corrige los imports que crucen fronteras prohibidas.
- Si la violación es inevitable, documenta la excepción en el PR y en `docs/ENFORCEMENT_FASE7_3.md`.

## Cómo ignorar temporalmente (solo con justificación)
- No se recomienda ignorar. Si es imprescindible:
  1. Documenta la excepción en el PR con motivo y alcance.
  2. Añade una nota en `docs/ENFORCEMENT_FASE7_3.md` indicando archivo y razón.
  3. Planifica la reversión de la excepción.

## Integración opcional con git hooks
- Crea un hook local `.git/hooks/pre-commit` con:

```bash
#!/bin/bash
python tools/auditar_fronteras.py || exit 1
```
- Hazlo ejecutable (`chmod +x .git/hooks/pre-commit`).
- No lo incluyas en commits si no está aprobado por el equipo.
