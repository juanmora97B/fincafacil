"""Auditoría pasiva de fronteras (Fase 7.3).

Escanea archivos .py (excluye tests, scripts, tools y carpetas comunes de build) para
reportar violaciones de fronteras definidas en:
- docs/CONTRATO_CODIGO_NUEVO.md
- docs/CONTRATO_LEGACY.md
- docs/FRONTERAS_DEL_SISTEMA.md

Salida: REPORT_FRONTERAS.md en la raíz del proyecto.

Este script no modifica código fuente ni corrige violaciones; solo reporta.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

# Raíz del proyecto = carpeta padre de tools/
BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_PATH = BASE_DIR / "REPORT_FRONTERAS.md"

EXCLUDE_DIRS = {
    "tests",
    "scripts",
    "tools",
    ".git",
    ".venv",
    "dist",
    "build",
    "assets",
    "uploads",
    "logs",
    "__pycache__",
}

ZONE_UI_HINTS = {"ui", "views", "pantallas", "formularios", "widgets"}
ZONE_INFRA_HINTS = {"database", "infra", "infraestructura", "repositorios"}
ZONE_UTILS_HINTS = {"utils"}

SEVERIDAD_CRITICA = "CRÍTICA"
SEVERIDAD_WARNING = "WARNING"


@dataclass
class ImportEntry:
    kind: str  # "import" | "from"
    module: str
    name: str
    lineno: int
    is_star: bool

    def describe(self) -> str:
        if self.kind == "import":
            return f"import {self.module}"
        mod = self.module or "."
        if self.is_star:
            return f"from {mod} import *"
        return f"from {mod} import {self.name}"


@dataclass
class Violation:
    file_path: Path
    regla: str
    import_str: str
    severidad: str


def iter_python_files(base: Path) -> Iterable[Path]:
    for path in base.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def parse_imports(path: Path) -> List[ImportEntry]:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    entries: List[ImportEntry] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                entries.append(
                    ImportEntry(
                        kind="import",
                        module=alias.name or "",
                        name=alias.name or "",
                        lineno=node.lineno,
                        is_star=alias.name == "*",
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                entries.append(
                    ImportEntry(
                        kind="from",
                        module=module,
                        name=alias.name or "",
                        lineno=node.lineno,
                        is_star=alias.name == "*",
                    )
                )
    return entries


def classify_zone(path: Path, imports: Sequence[ImportEntry]) -> str:
    parts = {p.lower() for p in path.parts}
    modules = {entry.module.lower() for entry in imports if entry.module}
    names = {entry.name.lower() for entry in imports if entry.name}

    if parts & ZONE_UTILS_HINTS:
        return "utils"
    if parts & ZONE_UI_HINTS:
        return "ui"
    if parts & ZONE_INFRA_HINTS:
        return "infra"
    if any(mod.startswith("customtkinter") for mod in modules | names):
        return "ui"
    return "dominio"


def detect_violations(path: Path, zone: str, imports: Sequence[ImportEntry]) -> List[Violation]:
    violations: List[Violation] = []

    for entry in imports:
        mod_lower = entry.module.lower()
        name_lower = entry.name.lower()

        # Uso de legacy validaciones
        if mod_lower.startswith("modules.utils.validaciones") or (
            mod_lower == "modules.utils" and name_lower == "validaciones"
        ) or name_lower == "modules.utils.validaciones":
            violations.append(
                Violation(
                    file_path=path,
                    regla="Uso de legacy validaciones.py en código nuevo",
                    import_str=entry.describe(),
                    severidad=SEVERIDAD_CRITICA,
                )
            )

        # Re-exports (star) desde utils
        if entry.module.startswith("modules.utils") and entry.is_star:
            violations.append(
                Violation(
                    file_path=path,
                    regla="Uso de re-exports con * desde modules.utils",
                    import_str=entry.describe(),
                    severidad=SEVERIDAD_WARNING,
                )
            )

        # Reglas por zona
        if zone == "ui":
            if mod_lower.startswith("database") or mod_lower.startswith("infra") or mod_lower.startswith("infraestructura"):
                violations.append(
                    Violation(
                        file_path=path,
                        regla="UI no puede importar Infraestructura (BD/IO)",
                        import_str=entry.describe(),
                        severidad=SEVERIDAD_CRITICA,
                    )
                )
        elif zone == "dominio":
            if mod_lower.startswith("ui") or mod_lower.startswith("modules.ui"):
                violations.append(
                    Violation(
                        file_path=path,
                        regla="Dominio no puede importar UI",
                        import_str=entry.describe(),
                        severidad=SEVERIDAD_CRITICA,
                    )
                )
        elif zone == "utils":
            if mod_lower.startswith("dominio") or mod_lower.startswith("ui") or mod_lower.startswith("modules.ui"):
                violations.append(
                    Violation(
                        file_path=path,
                        regla="Utils no puede depender de UI o Dominio",
                        import_str=entry.describe(),
                        severidad=SEVERIDAD_CRITICA,
                    )
                )
            if mod_lower.startswith("infra") or mod_lower.startswith("infraestructura") or mod_lower.startswith("database"):
                violations.append(
                    Violation(
                        file_path=path,
                        regla="Utils no puede depender de Infraestructura",
                        import_str=entry.describe(),
                        severidad=SEVERIDAD_CRITICA,
                    )
                )

    return violations


def write_report(violations: Sequence[Violation], scanned: int) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: List[str] = []
    lines.append("# REPORT_FRONTERAS")
    lines.append("")
    lines.append(f"Fecha de generación: {timestamp}")
    lines.append(f"Archivos escaneados: {scanned}")
    lines.append(f"Violaciones detectadas: {len(violations)}")
    lines.append("")

    if not violations:
        lines.append("Sin violaciones detectadas.")
    else:
        lines.append("| Archivo | Regla violada | Import detectado | Severidad |")
        lines.append("|---------|---------------|------------------|-----------|")
        for v in sorted(violations, key=lambda x: (str(x.file_path), x.severidad)):
            rel = v.file_path.relative_to(BASE_DIR).as_posix()
            lines.append(f"| {rel} | {v.regla} | {v.import_str} | {v.severidad} |")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    violations: List[Violation] = []
    scanned = 0

    for py_file in iter_python_files(BASE_DIR):
        scanned += 1
        imports = parse_imports(py_file)
        zone = classify_zone(py_file, imports)
        violations.extend(detect_violations(py_file, zone, imports))

    write_report(violations, scanned)


if __name__ == "__main__":
    main()
