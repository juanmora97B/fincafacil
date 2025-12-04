"""
Script para mostrar la configuración completa de cada finca
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from database import db


def mostrar_configuracion_fincas():
    """
    Muestra toda la configuración de fincas, potreros, sectores, lotes, razas, procedencias
    """
    print("\n" + "=" * 100)
    print("CONFIGURACION COMPLETA DEL SISTEMA")
    print("=" * 100)
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # ============ FINCAS ============
            print("\n" + "=" * 100)
            print("🏡 FINCAS")
            print("=" * 100)
            
            cursor.execute("""
                SELECT id, nombre, ubicacion, area_hectareas, estado 
                FROM finca 
                ORDER BY nombre
            """)
            fincas = cursor.fetchall()
            
            if fincas:
                print(f"\nTotal de fincas: {len(fincas)}\n")
                print(f"{'ID':<5} {'Nombre':<30} {'Ubicación':<25} {'Área (ha)':<15} {'Estado':<10}")
                print("-" * 100)
                for finca in fincas:
                    id_f, nombre, ubicacion, area, estado = finca
                    ubicacion = ubicacion or "N/A"
                    area = f"{area} ha" if area else "N/A"
                    print(f"{id_f:<5} {nombre:<30} {ubicacion:<25} {area:<15} {estado:<10}")
            else:
                print("\n⚠ No hay fincas registradas")
            
            # ============ POTREROS POR FINCA ============
            print("\n\n" + "=" * 100)
            print("🌿 POTREROS POR FINCA")
            print("=" * 100)
            
            cursor.execute("""
                SELECT f.id, f.nombre as finca_nombre
                FROM finca f
                WHERE f.estado IN ('Activa', 'Activo')
                ORDER BY f.nombre
            """)
            fincas_activas = cursor.fetchall()
            
            for id_finca, nombre_finca in fincas_activas:
                cursor.execute("""
                    SELECT id, nombre, area_hectareas, capacidad_maxima, estado, tipo_pasto
                    FROM potrero
                    WHERE id_finca = ?
                    ORDER BY nombre
                """, (id_finca,))
                potreros = cursor.fetchall()
                
                print(f"\n🏡 Finca: {nombre_finca} (ID: {id_finca})")
                print("-" * 100)
                
                if potreros:
                    print(f"   Total de potreros: {len(potreros)}\n")
                    print(f"   {'ID':<5} {'Nombre':<25} {'Área (ha)':<12} {'Capacidad':<12} {'Tipo Pasto':<20} {'Estado':<10}")
                    print("   " + "-" * 95)
                    for potrero in potreros:
                        id_p, nombre_p, area_p, capacidad, estado_p, tipo_pasto = potrero
                        area_p = f"{area_p} ha" if area_p else "N/A"
                        capacidad = str(capacidad) if capacidad else "N/A"
                        tipo_pasto = tipo_pasto or "N/A"
                        print(f"   {id_p:<5} {nombre_p:<25} {area_p:<12} {capacidad:<12} {tipo_pasto:<20} {estado_p:<10}")
                else:
                    print("   ⚠ Esta finca no tiene potreros configurados")
            
            # ============ SECTORES POR FINCA ============
            print("\n\n" + "=" * 100)
            print("📍 SECTORES POR FINCA")
            print("=" * 100)
            
            for id_finca, nombre_finca in fincas_activas:
                cursor.execute("""
                    SELECT id, codigo, nombre, descripcion, estado
                    FROM sector
                    WHERE finca_id = ?
                    ORDER BY nombre
                """, (id_finca,))
                sectores = cursor.fetchall()
                
                print(f"\n🏡 Finca: {nombre_finca} (ID: {id_finca})")
                print("-" * 100)
                
                if sectores:
                    print(f"   Total de sectores: {len(sectores)}\n")
                    print(f"   {'ID':<5} {'Código':<15} {'Nombre':<25} {'Descripción':<30} {'Estado':<10}")
                    print("   " + "-" * 95)
                    for sector in sectores:
                        id_s, codigo, nombre_s, descripcion, estado_s = sector
                        codigo = codigo or "N/A"
                        descripcion = descripcion or "N/A"
                        print(f"   {id_s:<5} {codigo:<15} {nombre_s:<25} {descripcion:<30} {estado_s:<10}")
                else:
                    print("   ⚠ Esta finca no tiene sectores configurados")
            
            # ============ LOTES ============
            print("\n\n" + "=" * 100)
            print("📦 LOTES")
            print("=" * 100)
            
            cursor.execute("""
                SELECT id, nombre, descripcion, estado
                FROM lote
                ORDER BY nombre
            """)
            lotes = cursor.fetchall()
            
            if lotes:
                print(f"\nTotal de lotes: {len(lotes)}\n")
                print(f"{'ID':<5} {'Nombre':<30} {'Descripción':<50} {'Estado':<10}")
                print("-" * 100)
                for lote in lotes:
                    id_l, nombre_l, descripcion, estado_l = lote
                    descripcion = descripcion or "N/A"
                    print(f"{id_l:<5} {nombre_l:<30} {descripcion:<50} {estado_l:<10}")
            else:
                print("\n⚠ No hay lotes registrados")
            
            # ============ RAZAS ============
            print("\n\n" + "=" * 100)
            print("🐄 RAZAS")
            print("=" * 100)
            
            cursor.execute("""
                SELECT id, nombre, descripcion, estado
                FROM raza
                ORDER BY nombre
            """)
            razas = cursor.fetchall()
            
            if razas:
                print(f"\nTotal de razas: {len(razas)}\n")
                print(f"{'ID':<5} {'Nombre':<30} {'Descripción':<50} {'Estado':<10}")
                print("-" * 100)
                for raza in razas:
                    id_r, nombre_r, descripcion, estado_r = raza
                    descripcion = descripcion or "N/A"
                    print(f"{id_r:<5} {nombre_r:<30} {descripcion:<50} {estado_r:<10}")
            else:
                print("\n⚠ No hay razas registradas")
            
            # ============ PROCEDENCIAS ============
            print("\n\n" + "=" * 100)
            print("📍 PROCEDENCIAS (Lugares de origen de animales comprados)")
            print("=" * 100)
            
            # Verificar si existe la tabla procedencia
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='procedencia'
            """)
            tabla_existe = cursor.fetchone()
            
            if tabla_existe:
                cursor.execute("""
                    SELECT id, nombre, ubicacion, contacto, estado
                    FROM procedencia
                    ORDER BY nombre
                """)
                procedencias = cursor.fetchall()
                
                if procedencias:
                    print(f"\nTotal de procedencias: {len(procedencias)}\n")
                    print(f"{'ID':<5} {'Nombre':<30} {'Ubicación':<25} {'Contacto':<25} {'Estado':<10}")
                    print("-" * 100)
                    for proc in procedencias:
                        id_p, nombre_p, ubicacion, contacto, estado_p = proc
                        ubicacion = ubicacion or "N/A"
                        contacto = contacto or "N/A"
                        print(f"{id_p:<5} {nombre_p:<30} {ubicacion:<25} {contacto:<25} {estado_p:<10}")
                else:
                    print("\n⚠ No hay procedencias registradas")
            else:
                print("\n⚠ La tabla 'procedencia' no existe en la base de datos")
            
            # ============ VENDEDORES ============
            print("\n\n" + "=" * 100)
            print("👤 VENDEDORES (Proveedores de animales)")
            print("=" * 100)
            
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='vendedor'
            """)
            tabla_existe = cursor.fetchone()
            
            if tabla_existe:
                cursor.execute("""
                    SELECT id, nombre, contacto, direccion, estado
                    FROM vendedor
                    ORDER BY nombre
                """)
                vendedores = cursor.fetchall()
                
                if vendedores:
                    print(f"\nTotal de vendedores: {len(vendedores)}\n")
                    print(f"{'ID':<5} {'Nombre':<30} {'Contacto':<25} {'Dirección':<30} {'Estado':<10}")
                    print("-" * 100)
                    for vend in vendedores:
                        id_v, nombre_v, contacto, direccion, estado_v = vend
                        contacto = contacto or "N/A"
                        direccion = direccion or "N/A"
                        print(f"{id_v:<5} {nombre_v:<30} {contacto:<25} {direccion:<30} {estado_v:<10}")
                else:
                    print("\n⚠ No hay vendedores registrados")
            else:
                print("\n⚠ La tabla 'vendedor' no existe en la base de datos")
            
            # ============ CONDICIÓN CORPORAL ============
            print("\n\n" + "=" * 100)
            print("💪 CONDICIÓN CORPORAL (Valores posibles)")
            print("=" * 100)
            
            print("""
La condición corporal es una escala para evaluar el estado físico del animal:

Escala típica 1-5:
  1 - Muy delgado (emaciado)
  2 - Delgado
  3 - Moderado (ideal)
  4 - Gordo
  5 - Muy gordo (obeso)

O puede ser descriptiva:
  - Emaciado
  - Delgado
  - Normal
  - Sobrepeso
  - Obeso

Nota: Este es un campo de texto libre en la base de datos.
Puedes usar números (1-5) o descripciones según tu preferencia.
""")
            
            # Ver si hay animales con condición corporal registrada
            cursor.execute("""
                SELECT DISTINCT condicion_corporal, COUNT(*) as total
                FROM animal
                WHERE condicion_corporal IS NOT NULL
                GROUP BY condicion_corporal
                ORDER BY total DESC
            """)
            condiciones = cursor.fetchall()
            
            if condiciones:
                print("\nCondiciones corporales actualmente registradas en animales:")
                print(f"{'Condición Corporal':<30} {'Cantidad de Animales':<20}")
                print("-" * 60)
                for cond, total in condiciones:
                    print(f"{cond:<30} {total:<20}")
            else:
                print("\n⚠ No hay animales con condición corporal registrada aún")
            
            # ============ RESUMEN GENERAL ============
            print("\n\n" + "=" * 100)
            print("📊 RESUMEN GENERAL")
            print("=" * 100)
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM finca WHERE estado IN ('Activa', 'Activo')")
            total_fincas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM potrero WHERE estado IN ('Activa', 'Activo')")
            total_potreros = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sector WHERE estado = 'Activo'")
            total_sectores = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lote WHERE estado = 'Activo'")
            total_lotes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM raza WHERE estado IN ('Activa', 'Activo')")
            total_razas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM animal WHERE estado = 'Activo'")
            total_animales = cursor.fetchone()[0]
            
            print(f"""
┌─────────────────────────────────────────┐
│ Configuración Actual del Sistema       │
├─────────────────────────────────────────┤
│ Fincas activas:        {total_fincas:>3}             │
│ Potreros activos:      {total_potreros:>3}             │
│ Sectores activos:      {total_sectores:>3}             │
│ Lotes activos:         {total_lotes:>3}             │
│ Razas activas:         {total_razas:>3}             │
│ Animales activos:      {total_animales:>3}             │
└─────────────────────────────────────────┘
""")
            
            # Verificar configuración completa por finca
            print("\n" + "=" * 100)
            print("✅ VERIFICACIÓN DE CONFIGURACIÓN POR FINCA")
            print("=" * 100)
            
            for id_finca, nombre_finca in fincas_activas:
                print(f"\n🏡 {nombre_finca}:")
                
                # Potreros
                cursor.execute("SELECT COUNT(*) FROM potrero WHERE id_finca = ? AND estado IN ('Activa', 'Activo')", (id_finca,))
                num_potreros = cursor.fetchone()[0]
                simbolo_potreros = "✅" if num_potreros > 0 else "⚠"
                print(f"   {simbolo_potreros} Potreros: {num_potreros}")
                
                # Sectores
                cursor.execute("SELECT COUNT(*) FROM sector WHERE id_finca = ? AND estado = 'Activo'", (id_finca,))
                num_sectores = cursor.fetchone()[0]
                simbolo_sectores = "✅" if num_sectores > 0 else "⚠"
                print(f"   {simbolo_sectores} Sectores: {num_sectores}")
                
                # Animales
                cursor.execute("SELECT COUNT(*) FROM animal WHERE id_finca = ? AND estado = 'Activo'", (id_finca,))
                num_animales = cursor.fetchone()[0]
                simbolo_animales = "✅" if num_animales > 0 else "ℹ"
                print(f"   {simbolo_animales} Animales: {num_animales}")
            
            print("\n" + "=" * 100)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    mostrar_configuracion_fincas()
    print("\n")
