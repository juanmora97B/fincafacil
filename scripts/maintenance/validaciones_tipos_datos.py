"""
Agregar validaciones de tipo de datos en guardar_mantenimiento
===============================================================

CÓDIGO A INSERTAR después de la línea donde se obtiene 'responsable'
y antes de procesar 'cantidad'
"""

validaciones = '''
            # VALIDACIÓN 1: Responsable debe ser texto, no número
            if responsable:
                # Verificar que no sea solo dígitos o decimales
                test_value = responsable.replace('.', '').replace(',', '').replace(' ', '')
                if test_value.isdigit():
                    messagebox.showerror(
                        "Error de Validación", 
                        f"El campo 'Responsable' debe ser un nombre o texto, no un número.\\n\\n"
                        f"Valor ingresado: '{responsable}'"
                    )
                    return
            
            # VALIDACIÓN 2: Cantidad debe ser numérica y positiva
            try:
                cantidad_txt = (self.entry_costo_mant.get().strip() or "").replace(",", ".")
                if not cantidad_txt:
                    messagebox.showwarning("Datos incompletos", "Debe ingresar una cantidad")
                    return
                    
                cantidad = float(cantidad_txt)
                if cantidad <= 0:
                    messagebox.showerror(
                        "Error de Validación",
                        f"La cantidad debe ser un número mayor a 0\\n\\n"
                        f"Valor ingresado: {cantidad}"
                    )
                    return
            except ValueError:
                messagebox.showerror(
                    "Error de Validación",
                    f"La cantidad debe ser un número válido\\n\\n"
                    f"Valor ingresado: '{self.entry_costo_mant.get()}'"
                )
                return
            
            # VALIDACIÓN 3: Precio debe ser numérico si se ingresa
            costo_unitario = None
            costo_total = None
            if tipo_mov == "Entrada":
                precio_unit_txt = self.entry_precio_unitario_mov.get().strip().replace(",", ".")
                if precio_unit_txt:
                    try:
                        costo_unitario = float(precio_unit_txt)
                        if costo_unitario < 0:
                            messagebox.showerror(
                                "Error de Validación",
                                "El precio unitario no puede ser negativo"
                            )
                            return
                        costo_total = cantidad * costo_unitario
                    except ValueError:
                        messagebox.showerror(
                            "Error de Validación",
                            f"El precio unitario debe ser un número válido\\n\\n"
                            f"Valor ingresado: '{precio_unit_txt}'"
                        )
                        return
'''

print("=" * 80)
print("VALIDACIONES A AGREGAR EN guardar_mantenimiento()")
print("=" * 80)
print("\nUBICACIÓN: Después de obtener 'responsable' (línea ~1365)")
print("REEMPLAZAR el bloque actual de validación de cantidad")
print("\nCÓDIGO A INSERTAR:")
print("-" * 80)
print(validaciones)

print("\n" + "=" * 80)
print("VALIDACIONES QUE SE IMPLEMENTAN:")
print("=" * 80)
print("""
1. VALIDACIÓN DE RESPONSABLE:
   - Verifica que no sea un número puro (ej: "3.0", "123")
   - Permite nombres con números (ej: "Juan 2do")
   - Muestra error claro indicando el valor rechazado

2. VALIDACIÓN DE CANTIDAD:
   - Convierte comas a puntos ("3,5" → "3.5")
   - Verifica que sea numérico válido
   - Verifica que sea mayor a 0
   - Captura ValueError y muestra mensaje específico

3. VALIDACIÓN DE PRECIO:
   - Solo se valida si es movimiento de Entrada
   - Convierte comas a puntos
   - Verifica que sea numérico válido
   - Verifica que no sea negativo
   - Calcula precio_total automáticamente

CASOS DE PRUEBA:
================

✓ VÁLIDOS:
  - Responsable: "bodega", "Juan Pérez", "Trabajador 1"
  - Cantidad: "10", "10.5", "10,5", "1000"
  - Precio: "500", "500.50", "500,50"

✗ INVÁLIDOS:
  - Responsable: "123", "45.6" (números puros)
  - Cantidad: "abc", "diez", "" (no numéricos o vacío)
  - Precio: "-100", "abc" (negativos o no numéricos)
""")
