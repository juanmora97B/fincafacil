"""
FASE 4 - Health Check
Valida integridad lógica de la BD, auditoría y backups, y que no haya SQL en la UI.
Salida en consola y opcionalmente JSON.
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import sqlite3
import sys
import time

from src.database.database import get_db_path_safe, get_db_connection
from src.core.backup_service import backup_now
from src.core.audit_service import ensure_audit_schema

FORBIDDEN_UI_PATTERNS = [
    "sqlite3.connect",
    "SELECT ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "get_db_connection",
]

UI_DIR = Path("src/modules")


def check_db_integrity() -> Dict[str, Any]:
    result = {"ok": True, "details": []}
    try:
        # asegurar esquema de auditoría antes de verificar
        ensure_audit_schema()
        db_path = get_db_path_safe()
        result["db_path"] = str(db_path)
        result["db_size_bytes"] = db_path.stat().st_size if db_path.exists() else 0
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Foreign keys ON?
            cur.execute("PRAGMA foreign_keys")
            fk_on = cur.fetchone()[0] == 1
            result["foreign_keys_on"] = fk_on
            if not fk_on:
                result["ok"] = False
                result["details"].append("PRAGMA foreign_keys OFF")
            # audit_log exists?
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
            result["audit_log_exists"] = cur.fetchone() is not None
            if not result["audit_log_exists"]:
                result["ok"] = False
                result["details"].append("Tabla audit_log no existe")
    except Exception as e:
        result["ok"] = False
        result["details"].append(f"Error BD: {e}")
    return result


def check_ui_sql() -> Dict[str, Any]:
    result = {"ok": True, "files_with_sql": []}
    try:
        if not UI_DIR.exists():
            return result
        for py in UI_DIR.rglob("*.py"):
            try:
                txt = py.read_text(encoding="utf-8")
            except Exception:
                continue
            for pat in FORBIDDEN_UI_PATTERNS:
                if pat in txt:
                    result["files_with_sql"].append(str(py))
                    result["ok"] = False
                    break
    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)
    return result


def check_backup() -> Dict[str, Any]:
    try:
        zip_path = backup_now("health_check")
        return {"ok": True, "backup_created": str(zip_path)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_checks() -> Dict[str, Any]:
    out = {
        "db": check_db_integrity(),
        "ui_sql": check_ui_sql(),
        "backup": check_backup(),
    }
    out["ok"] = out["db"]["ok"] and out["ui_sql"]["ok"] and out["backup"]["ok"]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    args = parser.parse_args()
    res = run_checks()
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("FASE 4 - Health Check")
        print(f"DB OK: {res['db']['ok']}")
        print(f"UI sin SQL: {res['ui_sql']['ok']}")
        print(f"Backup OK: {res['backup']['ok']}")
        if not res["ok"]:
            print("Detalles:")
            print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
