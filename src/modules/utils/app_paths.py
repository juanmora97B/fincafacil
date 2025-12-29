"""Helpers for resolving writable app paths.

All writable assets (DB, config) live under the user profile to avoid
permission issues when installed under Program Files.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Union

APP_FOLDER_NAME = "FincaFacil"


def _user_base_dir() -> Path:
    """Return base writable directory for app data."""
    base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
    if base:
        return Path(base) / APP_FOLDER_NAME
    return Path.home() / f".{APP_FOLDER_NAME.lower()}"


def get_user_data_dir() -> Path:
    """Ensure and return the main user data directory."""
    path = _user_base_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_database_dir() -> Path:
    """Ensure and return the database directory inside user data."""
    path = get_user_data_dir() / "database"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_dir() -> Path:
    """Ensure and return the config directory inside user data."""
    path = get_user_data_dir() / "config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    """Return the writable database path."""
    return get_database_dir() / "fincafacil.db"


def get_config_file(name: str) -> Path:
    """Return a config file path inside the writable config dir."""
    return get_config_dir() / name


def get_seed_path(relative: Union[str, Path]) -> Path:
    """Return the path to a bundled seed file (works in frozen mode)."""
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
    return bundle_root / Path(relative)
