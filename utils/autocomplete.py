"""Helper para añadir autocomplete a CTkComboBox.

Uso:
from utils.autocomplete import enable_autocomplete
enable_autocomplete(mi_combo, lista_valores)

El filtrado se hace por coincidencia parcial (substring) case-insensitive.
Se restaura la lista original con Escape o dejando el texto por debajo de min_chars.
"""
from typing import List, Sequence, Callable

try:
    import customtkinter as ctk  # noqa: F401
except Exception:
    pass


def enable_autocomplete(combo, original_values: Sequence[str], min_chars: int = 1,
                        match_mode: str = "contains", case_insensitive: bool = True,
                        transform: Callable[[str], str] | None = None) -> None:
    """Activa comportamiento de autocomplete sobre un CTkComboBox.

    Parámetros:
        combo: instancia de CTkComboBox.
        original_values: lista completa de valores base.
        min_chars: mínimo de caracteres antes de filtrar (default 1).
        match_mode: 'startswith' | 'contains'.
        case_insensitive: si True normaliza a lower-case para comparar.
        transform: función opcional para transformar el texto antes de comparar.
    """
    # Copia defensiva
    base = list(original_values)
    # Config persistida en el propio combo para poder cambiar modo dinámicamente
    combo.autocomplete_config = {  # type: ignore[attr-defined]
        "min_chars": min_chars,
        "match_mode": match_mode,
        "case_insensitive": case_insensitive,
        "transform": transform,
        "base": base
    }

    def _filter(event=None):  # noqa: ARG001
        try:
            text = combo.get().strip()
        except Exception:
            return
        if transform:
            text = transform(text)
        cfg = getattr(combo, "autocomplete_config", {})
        mmode = cfg.get("match_mode", match_mode)
        minc = cfg.get("min_chars", min_chars)
        cis = cfg.get("case_insensitive", case_insensitive)
        trans = cfg.get("transform", transform)
        bvals = cfg.get("base", base)
        if trans:
            text = trans(text)
        cmp_text = text.lower() if cis else text
        if len(cmp_text) < minc:
            combo.configure(values=bvals)
            return
        if mmode == "startswith":
            filtrados = [v for v in bvals if (v.lower() if cis else v).startswith(cmp_text)]
        else:  # contains
            filtrados = [v for v in bvals if cmp_text in (v.lower() if cis else v)]
        combo.configure(values=filtrados or ["(sin coincidencias)"])

    def _restore(event=None):  # noqa: ARG001
        combo.configure(values=base)

    # Intentar acceder al entry interno (API privada de CTkComboBox)
    internal_entry = getattr(combo, "_entry", None)
    target_widget = internal_entry if internal_entry else combo
    try:
        target_widget.bind("<KeyRelease>", _filter)
        target_widget.bind("<Escape>", _restore)
    except Exception:
        # Fallback: no se puede bindear
        pass

    # Exponer función manual para restaurar
    combo.autocomplete_restore = _restore  # type: ignore[attr-defined]
    combo.autocomplete_filter = _filter    # type: ignore[attr-defined]

def set_autocomplete_mode(combo, mode: str):
    """Actualiza el modo de coincidencia ('contains'|'startswith') y refiltra inmediatamente."""
    if not hasattr(combo, "autocomplete_config"):
        return
    if mode not in ("contains", "startswith"):
        return
    combo.autocomplete_config["match_mode"] = mode  # type: ignore[index]
    try:
        combo.autocomplete_filter()  # type: ignore[attr-defined]
    except Exception:
        pass

__all__ = ["enable_autocomplete", "set_autocomplete_mode"]
