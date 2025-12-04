"""
Script de debug para verificar carga de datos en módulo Animales
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db_connection

def verificar_carga_combos():
    """Simula exactamente la lógica de cargar_datos_combos()"""
    print("\n" + "="*70)
    print("SIMULANDO CARGA DE COMBOS EN REGISTRO_ANIMAL.PY")
    print("="*70 + "\n")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # === CARGAR FINCAS (EXACTAMENTE COMO EN EL CÓDIGO) ===
            print("1️⃣ Ejecutando: SELECT id, nombre, estado FROM finca")
            cursor.execute("SELECT id, nombre, estado FROM finca")
            raw_fincas = cursor.fetchall()
            print(f"   📥 Registros obtenidos: {len(raw_fincas)}")
            for r in raw_fincas:
                print(f"      - ID: {r[0]}, Nombre: '{r[1]}', Estado: '{r[2]}'")
            
            # Filtrar inactivas/eliminadas
            excluir = {'eliminada','eliminado','inactiva','inactivo'}
            finca_rows = [r for r in raw_fincas if (r[2] or '').lower() not in excluir]
            print(f"\n   🔍 Después de filtrar estados {excluir}:")
            print(f"      Fincas válidas: {len(finca_rows)}")
            
            if not finca_rows:
                finca_rows = raw_fincas  # fallback
                print(f"      ⚠️ Fallback activado, usando todas las fincas")
            
            # Crear lista de nombres para el combo
            fincas = [row[1] for row in finca_rows]
            print(f"\n   ✅ Lista 'fincas' para combo.configure(values=...):")
            print(f"      {fincas}")
            print(f"      Longitud: {len(fincas)}")
            
            # === CARGAR RAZAS (EXACTAMENTE COMO EN EL CÓDIGO) ===
            print(f"\n{'='*70}")
            print("2️⃣ Ejecutando: SELECT id, nombre, estado FROM raza")
            cursor.execute("SELECT id, nombre, estado FROM raza")
            raw_razas = cursor.fetchall()
            print(f"   📥 Registros obtenidos: {len(raw_razas)}")
            print(f"   Primeros 5 registros:")
            for r in raw_razas[:5]:
                print(f"      - ID: {r[0]}, Nombre: '{r[1]}', Estado: '{r[2]}'")
            print(f"      ... y {len(raw_razas)-5} más")
            
            # Filtrar inactivas/eliminadas
            raza_rows = [r for r in raw_razas if (r[2] or '').lower() not in ('inactiva','eliminada')]
            print(f"\n   🔍 Después de filtrar 'inactiva' y 'eliminada':")
            print(f"      Razas válidas: {len(raza_rows)}")
            
            if not raza_rows:
                raza_rows = raw_razas  # fallback
                print(f"      ⚠️ Fallback activado, usando todas las razas")
            
            # Crear lista de nombres para el combo
            razas = [row[1] for row in raza_rows]
            print(f"\n   ✅ Lista 'razas' para combo.configure(values=...):")
            print(f"      Primeras 10: {razas[:10]}")
            print(f"      Longitud total: {len(razas)}")
            
            # === SIMULAR CONFIGURACIÓN DE COMBOS ===
            print(f"\n{'='*70}")
            print("3️⃣ SIMULANDO CONFIGURACIÓN DE COMBOS")
            print("="*70)
            
            print(f"\n📋 NACIMIENTO:")
            print(f"   combo_finca_nac.configure(values={fincas})")
            print(f"   combo_finca_nac.set('{fincas[0] if fincas else 'N/A'}')")
            print(f"   ✓ Combo finca_nac configurado con {len(fincas)} fincas")
            print(f"\n   combo_raza_nac.configure(values=[...{len(razas)} razas...])")
            print(f"   combo_raza_nac.set('{razas[0] if razas else 'N/A'}')")
            print(f"   ✓ Combo raza_nac configurado con {len(razas)} razas")
            
            print(f"\n📋 COMPRA:")
            print(f"   combo_finca_comp.configure(values={fincas})")
            print(f"   combo_finca_comp.set('{fincas[0] if fincas else 'N/A'}')")
            print(f"   ✓ Combo finca_comp configurado con {len(fincas)} fincas")
            print(f"\n   combo_raza_comp.configure(values=[...{len(razas)} razas...])")
            print(f"   combo_raza_comp.set('{razas[0] if razas else 'N/A'}')")
            print(f"   ✓ Combo raza_comp configurado con {len(razas)} razas")
            
            # === VERIFICAR COMPORTAMIENTO DE COMBOBOX ===
            print(f"\n{'='*70}")
            print("4️⃣ COMPORTAMIENTO ESPERADO DE CTkComboBox")
            print("="*70)
            print(f"""
⚠️ IMPORTANTE: CustomTkinter ComboBox behavior
────────────────────────────────────────────────────────────────────

1. combo.configure(values=[...lista...])
   → Establece TODAS las opciones disponibles en el dropdown
   
2. combo.set('valor')
   → Establece SOLO el valor MOSTRADO inicialmente
   → NO limita las opciones disponibles
   
3. Para ver TODAS las opciones:
   → El usuario debe HACER CLIC en la FLECHA del dropdown ▼
   
4. VALOR MOSTRADO vs OPCIONES DISPONIBLES:
   ┌─────────────────────────┐
   │  finca el prado     ▼  │  ← Valor mostrado (set)
   └─────────────────────────┘
         ↓ Click en ▼
   ┌─────────────────────────┐
   │✓ finca el prado        │  ← Opción 1 (de values)
   │  finca el leon         │  ← Opción 2 (de values)
   └─────────────────────────┘

CONCLUSIÓN:
• Si el código ejecuta: combo.configure(values={fincas})
  donde fincas = {fincas}
• Entonces el combo TIENE las {len(fincas)} opciones disponibles
• El usuario DEBE hacer clic en el dropdown para verlas todas
""")
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verificar_carga_combos()
    print("\n" + "="*70)
    print("VERIFICACIÓN COMPLETADA")
    print("="*70 + "\n")
