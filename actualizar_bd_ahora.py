"""
Script para actualizar la base de datos inmediatamente
Ejecuta este script para agregar todas las columnas faltantes
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from database.actualizar_db import actualizar_base_datos

if __name__ == "__main__":
    print("=" * 50)
    print("ACTUALIZANDO BASE DE DATOS")
    print("=" * 50)
    print()
    actualizar_base_datos()
    print()
    print("=" * 50)
    print("✅ ACTUALIZACIÓN COMPLETADA")
    print("=" * 50)
    print()
    input("Presiona Enter para continuar...")

