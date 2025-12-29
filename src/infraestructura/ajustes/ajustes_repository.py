"""
Dominio Ajustes — Repository
Responsabilidad: SQL puro, sin lógica de negocio.
"""
from typing import List, Tuple
from database import db


class AjustesRepository:
    def listar_fincas(self) -> List[Tuple[int, str]]:
        """Retorna (id, nombre) de fincas ordenadas por nombre."""
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nombre FROM finca ORDER BY nombre")
            return [(row[0], row[1]) for row in cur.fetchall()]

    def listar_app_settings(self) -> List[Tuple[str, str]]:
        """Retorna (clave, valor) desde app_settings."""
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT clave, valor FROM app_settings")
            return [(row[0], row[1]) for row in cur.fetchall()]

    def upsert_app_setting(self, clave: str, valor: str) -> None:
        """Inserta o actualiza una preferencia en app_settings."""
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO app_settings (clave, valor) VALUES (?, ?)",
                (clave, valor),
            )
            conn.commit()
