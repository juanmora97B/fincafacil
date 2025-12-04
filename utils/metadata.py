"""Utilidad para generar notas con bloque de metadatos JSON estandarizado.

Formato final:
    <texto_humano>\n[META]{"tipo":"...", ...}

Funciones:
    build_meta_note(event_type, human_text, data) -> str
        event_type: cadena corta identificando el tipo (reubicacion, tratamiento, venta, etc.)
        human_text: versión legible.
        data: dict adicional. Se añadirá clave 'tipo'.

    parse_meta(note) -> (human_text, meta_dict | None)
        Separa la parte humana y el JSON si presente.

Uso recomendado:
    from utils.metadata import build_meta_note
    nota = build_meta_note("reubicacion", human_text, {...})

Seguridad: ensure_ascii=False para mantener caracteres especiales.
"""
from __future__ import annotations
from typing import Any, Dict, Tuple
import json

META_MARK = "[META]"


def build_meta_note(event_type: str, human_text: str, data: Dict[str, Any]) -> str:
    meta = dict(data)
    meta.setdefault("tipo", event_type)
    try:
        meta_json = json.dumps(meta, ensure_ascii=False)
    except Exception:
        # Fallback mínimo si algo falla en serialización
        meta_json = json.dumps({"tipo": event_type}, ensure_ascii=False)
    return f"{human_text}\n{META_MARK}{meta_json}"


def parse_meta(note: str) -> Tuple[str, Dict[str, Any] | None]:
    if META_MARK not in note:
        return note, None
    human, _, rest = note.partition(META_MARK)
    rest = rest.strip()
    try:
        meta = json.loads(rest)
    except Exception:
        meta = None
    return human.rstrip(), meta

__all__ = ["build_meta_note", "parse_meta", "META_MARK"]