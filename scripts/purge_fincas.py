"""Script para limpiar todas las fincas y desasociar herramientas.
USO (Windows CMD):
    python scripts\\purge_fincas.py

Acciones:
 1. Muestra conteo actual de fincas y herramientas asociadas.
 2. Pide confirmación (escribe SI) antes de proceder.
 3. Actualiza herramienta.id_finca = NULL donde haya valor.
 4. Elimina todas las filas de finca.
 5. Muestra resumen final.

Advertencia: Esta acción es destructiva. Realiza respaldo previo si es necesario.
"""
import sqlite3
import os
from datetime import datetime

# Ajustar ruta base si se mueve script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'fincafacil.db')

def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró base de datos en: {DB_PATH}")
        return

    print("🔐 Purga de fincas iniciada")
    print(f"→ Usando base de datos: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        # Conteos iniciales
        cur.execute("SELECT COUNT(*) FROM finca")
        fincas_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM herramienta WHERE id_finca IS NOT NULL")
        herramientas_con_finca = cur.fetchone()[0]

        print(f"Fincas registradas: {fincas_count}")
        print(f"Herramientas asociadas a una finca: {herramientas_con_finca}")
        if fincas_count == 0:
            print("No hay fincas para eliminar.")
            return

        confirm = input("Escribe SI para confirmar la eliminación de todas las fincas: ").strip().upper()
        if confirm != 'SI':
            print("⚠️ Operación cancelada por el usuario.")
            return

        # Desasociar herramientas
        cur.execute("UPDATE herramienta SET id_finca = NULL WHERE id_finca IS NOT NULL")
        # Eliminar fincas
        cur.execute("DELETE FROM finca")
        conn.commit()

        # Resumen final
        cur.execute("SELECT COUNT(*) FROM finca")
        fincas_final = cur.fetchone()[0]
        print("✅ Purga completada")
        print(f"Fincas restantes: {fincas_final}")
        cur.execute("SELECT COUNT(*) FROM herramienta WHERE id_finca IS NOT NULL")
        herramientas_restantes = cur.fetchone()[0]
        print(f"Herramientas todavía asociadas (debería ser 0): {herramientas_restantes}")
        print("Ahora puede recrear las fincas necesarias desde la interfaz.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante la purga: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
