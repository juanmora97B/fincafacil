import os
import sys
import random
from typing import List, Dict, Any

# Ensure we can import from src/ as top-level package "modules" and "infraestructura"
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(ROOT, "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from infraestructura.configuracion.configuracion_service import ConfiguracionService  # type: ignore

# --- Helpers ---

def log(msg: str) -> None:
    print(msg)


def ensure_fincas(service: ConfiguracionService) -> List[Dict]:
    """Create ≥3 fincas if missing, return fincas for further seeding."""
    fincas_seed = [
        ("FINCA001", "Finca Altamira", "Caldas"),
        ("FINCA002", "Finca La Esperanza", "Antioquia"),
        ("FINCA003", "Finca El Bosque", "Boyacá"),
        ("FINCA004", "Finca Santa Rosa", "Santander"),
    ]
    created = 0
    for codigo, nombre, ubicacion in fincas_seed:
        try:
            # Idempotent: try to get; if not exists, create
            try:
                service.obtener_finca(codigo)
                log(f"↪ Finca existente: {codigo} - {nombre}")
            except Exception:
                service.crear_finca(codigo, nombre, ubicacion)
                created += 1
                log(f"✔ Finca creada: {codigo} - {nombre} ({ubicacion})")
        except Exception as e:
            log(f"✖ Error finca {codigo}: {e}")
    fincas = service.listar_fincas_para_combo_lotes()
    return fincas


def ensure_lotes(service: ConfiguracionService, fincas: List[Dict]) -> None:
    """Create ≥2 lots per finca (idempotent)."""
    for f in fincas:
        fid_val: Any = f.get("id")
        if fid_val is None:
            # Finca sin ID válido, omitir
            continue
        fid = int(fid_val)
        nombre_finca = str(f.get("nombre") or "")
        # build two codes per finca
        base_code = str(f.get("codigo") or "") or nombre_finca.replace(" ", "").upper()[:6]
        lotes = [
            (f"{base_code}_LT1", f"Lote A {nombre_finca}", "Grupo principal", random.choice(["Por Peso", "Por Edad", "Por Producción"])),
            (f"{base_code}_LT2", f"Lote B {nombre_finca}", "Grupo secundario", random.choice(["Por Peso", "Por Origen", "Personalizado"]))
        ]
        for codigo, nombre, descripcion, criterio in lotes:
            try:
                # Idempotent: check by listing + code match in finca
                existentes = service.listar_lotes_activos()
                ya = []
                for l in existentes:
                    l_fid_val: Any = l.get("finca_id") or l.get("id_finca")
                    if l.get("codigo") == codigo and l_fid_val is not None and int(l_fid_val) == fid:
                        ya.append(l)
                if ya:
                    log(f"↪ Lote existente: {codigo} ({nombre_finca})")
                else:
                    service.crear_lote(codigo=codigo, nombre=nombre, finca_id=fid, descripcion=descripcion, criterio=criterio)
                    log(f"✔ Lote creado: {codigo} en {nombre_finca}")
            except Exception as e:
                log(f"✖ Error lote {codigo} ({nombre_finca}): {e}")


def ensure_sectores(service: ConfiguracionService, fincas: List[Dict]) -> None:
    """Create ≥2 sectors per finca (idempotent)."""
    for f in fincas:
        fid_val: Any = f.get("id")
        if fid_val is None:
            continue
        fid = int(fid_val)
        nombre_finca = str(f.get("nombre") or "")
        base_code = (str(f.get("codigo") or "") or nombre_finca.replace(" ", "").upper()[:6])
        sectores = [
            (f"{base_code}_SC1", f"Sector Norte {nombre_finca}", "Zona alta"),
            (f"{base_code}_SC2", f"Sector Sur {nombre_finca}", "Zona baja"),
        ]
        existentes = service.listar_sectores_activos()
        for codigo, nombre, comentario in sectores:
            try:
                ya = []
                for s in existentes:
                    s_fid_val: Any = s.get("finca_id") or s.get("id_finca")
                    if s.get("codigo") == codigo and s_fid_val is not None and int(s_fid_val) == fid:
                        ya.append(s)
                if ya:
                    log(f"↪ Sector existente: {codigo} ({nombre_finca})")
                else:
                    service.crear_sector(codigo=codigo, nombre=nombre, finca_id=fid, comentario=comentario)
                    log(f"✔ Sector creado: {codigo} en {nombre_finca}")
            except Exception as e:
                log(f"✖ Error sector {codigo} ({nombre_finca}): {e}")


def ensure_tipos_explotacion(service: ConfiguracionService) -> None:
    """Seed tipos de explotación core (idempotent)."""
    tipos = [
        ("CARNE", "Producción de Carne", "Carne", "Orientado a cebas y engorde"),
        ("LECHE", "Producción de Leche", "Leche", "Ordeño y derivados"),
        ("DOBLE", "Doble Propósito", "Doble Propósito", "Carne y Leche"),
        ("REPRO", "Reproducción", "Reproducción", "Mejoramiento genético"),
    ]
    for codigo, descripcion, categoria, comentario in tipos:
        try:
            try:
                service.obtener_tipo_explotacion(codigo)
                log(f"↪ Tipo explotación existente: {codigo}")
            except Exception:
                service.crear_tipo_explotacion(codigo, descripcion, categoria, comentario)
                log(f"✔ Tipo explotación creado: {codigo} - {descripcion}")
        except Exception as e:
            log(f"✖ Error tipo explotación {codigo}: {e}")


def ensure_catalogos_auxiliares(service: ConfiguracionService) -> None:
    """Seed minimal auxiliary catalogs: razas, motivos_venta, procedencias (idempotent)."""
    # Razas
    razas = [
        ("HOL", "Holstein", "Lechera"),
        ("GIR", "Gir", "Lechera"),
        ("BRA", "Brahman", "Carne"),
        ("NORM", "Normando", "Doble Propósito"),
    ]
    for codigo, nombre, comentario in razas:
        try:
            try:
                service.obtener_raza(codigo)
                log(f"↪ Raza existente: {codigo}")
            except Exception:
                # 'crear_raza' acepta: tipo_ganado, especie, descripcion, estado
                service.crear_raza(codigo=codigo, nombre=nombre, descripcion=comentario, estado="Activo")
                log(f"✔ Raza creada: {codigo} - {nombre}")
        except Exception as e:
            log(f"✖ Error raza {codigo}: {e}")

    # Motivos de Venta
    motivos = [
        ("DESC", "Descarte", "Bajo rendimiento"),
        ("REPRO", "Reproducción", "Mejora genética"),
        ("NEGO", "Negocio", "Oportunidad comercial"),
    ]
    for codigo, desc, comentario in motivos:
        try:
            if service.existe_motivo_venta(codigo):
                log(f"↪ Motivo venta existente: {codigo}")
            else:
                service.crear_motivo_venta(codigo=codigo, descripcion=desc, comentario=comentario, estado="Activo")
                log(f"✔ Motivo venta creado: {codigo} - {desc}")
        except Exception as e:
            log(f"✖ Error motivo venta {codigo}: {e}")

    # Procedencias
    procedencias = [
        ("COMPRA", "Compra externa"),
        ("NAC", "Nacimiento en finca"),
        ("DON", "Donación"),
    ]
    for codigo, descripcion in procedencias:
        try:
            try:
                service.obtener_procedencia(codigo)
                log(f"↪ Procedencia existente: {codigo}")
            except Exception:
                service.crear_procedencia(codigo=codigo, descripcion=descripcion, comentario="", estado="Activo")
                log(f"✔ Procedencia creada: {codigo} - {descripcion}")
        except Exception as e:
            log(f"✖ Error procedencia {codigo}: {e}")


def main() -> None:
    log("[SEED] Configuración - inicio")
    svc = ConfiguracionService()
    fincas = ensure_fincas(svc)
    ensure_lotes(svc, fincas)
    ensure_sectores(svc, fincas)
    ensure_tipos_explotacion(svc)
    ensure_catalogos_auxiliares(svc)
    log("[SEED] Configuración - completado")


if __name__ == "__main__":
    main()
