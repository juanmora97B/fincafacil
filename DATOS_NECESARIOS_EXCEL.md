# 📋 Datos Necesarios para Importar Animales desde Excel

## 📊 Campos Obligatorios (*)

Estos campos **DEBEN** estar completos para cada animal:

1. **Código*** - Código único del animal
   - Ejemplo: `001`, `VACA-001`, `TORO-2023-01`
   - No puede repetirse

2. **Tipo Ingreso*** - Cómo ingresó el animal
   - Valores permitidos: `Nacimiento` o `Compra`
   - Debe escribirse exactamente así

3. **Sexo*** - Sexo del animal
   - Valores permitidos: `Macho` o `Hembra`
   - Debe escribirse exactamente así

4. **Finca*** - Nombre de la finca
   - Debe ser el nombre EXACTO de una finca que ya existe en el sistema
   - Ejemplo: `Finca El Prado`
   - ⚠️ IMPORTANTE: Primero debe crear la finca en Configuración > Fincas

## 📝 Campos Opcionales (pero recomendados)

5. **Nombre** - Nombre del animal
   - Ejemplo: `Toro 1`, `Vaca Lechera`, `Becerro 001`

6. **Fecha Nacimiento** - Fecha de nacimiento
   - Formato: `YYYY-MM-DD` (año-mes-día)
   - Ejemplo: `2023-01-15`, `2022-12-25`

7. **Fecha Compra** - Solo si Tipo Ingreso = "Compra"
   - Formato: `YYYY-MM-DD`
   - Ejemplo: `2023-06-10`

8. **Raza** - Nombre de la raza
   - Debe ser el nombre EXACTO de una raza que ya existe en el sistema
   - Ejemplo: `Holstein`, `Angus`, `Brahman`
   - ⚠️ IMPORTANTE: Primero debe crear la raza en Configuración > Razas

9. **Potrero** - Nombre del potrero
   - Debe ser el nombre EXACTO de un potrero que ya existe en el sistema
   - Ejemplo: `Potrero 1`, `Potrero Norte`
   - ⚠️ IMPORTANTE: Primero debe crear el potrero en Configuración > Potreros

10. **Peso Nacimiento (kg)** - Peso al nacer
    - Solo números (puede tener decimales)
    - Ejemplo: `35.5`, `40`, `28.3`

11. **Peso Compra (kg)** - Peso al comprar
    - Solo números (puede tener decimales)
    - Ejemplo: `250.5`, `300`

12. **Precio Compra** - Precio pagado (solo si es compra)
    - Solo números (puede tener decimales)
    - Ejemplo: `1500000`, `2000000.50`

13. **Salud** - Estado de salud
    - Valores comunes: `Sano`, `Enfermo`, `En Tratamiento`
    - Por defecto: `Sano`

14. **Color** - Color del animal
    - Ejemplo: `Negro y Blanco`, `Marrón`, `Rojo`

15. **Hierro** - Número o código del hierro
    - Ejemplo: `HIERRO-001`, `12345`

16. **Comentarios** - Notas adicionales
    - Cualquier información adicional sobre el animal

## 📋 Ejemplo de Datos para 70 Animales

### Animales por Nacimiento:
```
Código | Nombre    | Tipo Ingreso | Sexo   | Fecha Nacimiento | Finca          | Raza     | Potrero    | Salud
-------|-----------|--------------|--------|------------------|----------------|----------|------------|-------
001    | Becerro 1 | Nacimiento   | Macho  | 2023-01-15       | Finca El Prado | Holstein | Potrero 1  | Sano
002    | Becerro 2 | Nacimiento   | Hembra | 2023-01-20       | Finca El Prado | Holstein | Potrero 1  | Sano
...
```

### Animales por Compra:
```
Código | Nombre  | Tipo Ingreso | Sexo   | Fecha Nacimiento | Fecha Compra  | Finca          | Raza   | Potrero    | Peso Compra | Precio Compra | Salud
-------|---------|--------------|--------|------------------|---------------|----------------|--------|------------|-------------|---------------|-------
V-001  | Toro 1  | Compra        | Macho  | 2022-05-10      | 2023-06-15    | Finca El Prado | Angus  | Potrero 2  | 350         | 2500000       | Sano
...
```

## ⚠️ IMPORTANTE - Antes de Importar

1. **Configure primero en el sistema:**
   - ✅ Fincas (Configuración > Fincas)
   - ✅ Razas (Configuración > Razas)
   - ✅ Potreros (Configuración > Potreros)

2. **Use los nombres EXACTOS** que están en el sistema para:
   - Finca
   - Raza
   - Potrero

3. **Formato de fechas:** Siempre `YYYY-MM-DD`
   - ✅ Correcto: `2023-01-15`
   - ❌ Incorrecto: `15/01/2023`, `01-15-2023`

4. **Valores exactos para:**
   - Tipo Ingreso: `Nacimiento` o `Compra` (exactamente así)
   - Sexo: `Macho` o `Hembra` (exactamente así)

## 🚀 Pasos para Importar

1. **Crear la plantilla:**
   ```bash
   python crear_plantilla_excel.py
   ```

2. **Completar el Excel** con sus 70 animales

3. **Abrir el sistema:**
   - Ir a **Animales > Registro Animal**
   - Clic en **"📥 Importar desde Excel"**
   - Seleccionar el archivo Excel
   - ¡Listo!

## 📝 Notas

- El sistema validará automáticamente los datos
- Si hay errores, se mostrarán al final de la importación
- Los animales con errores NO se importarán
- Puede importar en varias partes si lo prefiere

---

**¿Necesita ayuda?** Revise la plantilla Excel que incluye ejemplos y más instrucciones.

