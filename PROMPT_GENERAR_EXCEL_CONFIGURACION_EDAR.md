# Prompt para generar Excel de configuracion de EDAR (QSDsan ASM1 - Linea de aguas)

> Copia este prompt completo y pegalo en una IA con capacidad de generar archivos Excel
> (ChatGPT con Code Interpreter, Claude con Artifacts, Google Gemini, etc.)
> Ultima actualizacion: 2026-03-30

---

## INSTRUCCION PRINCIPAL

Genera un archivo Excel (.xlsx) con multiples hojas que sirva como **plantilla de configuracion**
para simular cualquier EDAR (Estacion Depuradora de Aguas Residuales) usando el modelo ASM1
(Activated Sludge Model No. 1) del software QSDsan/EXPOsan en Python.

El Excel debe cubrir **solo la linea de aguas** (sin digestion de lodos ni tratamiento terciario).
Debe ser util para un ingeniero de proceso que necesite introducir los datos de SU planta real
y luego lanzar una simulacion con QSDsan.

---

## ESTRUCTURA DEL EXCEL: 8 HOJAS

### HOJA 1: "1_GENERAL"
**Proposito:** Datos generales de la planta y configuracion del sistema.

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F |
|-----------|-----------|-----------|-----------|-----------|-----------|
| Parametro | Valor | Unidad | Descripcion | Valor BSM1 (referencia) | Notas |

Incluir estos campos (uno por fila):

| Parametro | Unidad | Descripcion | Valor BSM1 |
|-----------|--------|-------------|------------|
| Nombre de la planta | texto | Nombre identificador de la EDAR | BSM1 Benchmark |
| Modelo de proceso | texto | Modelo cinetico: ASM1 | ASM1 |
| Tipo de reactor | texto | CSTR (mezcla completa) o PFR (flujo piston) | CSTR |
| Numero de reactores anoxicos | entero | Cantidad de tanques anoxicos en serie | 2 |
| Numero de reactores aerobicos | entero | Cantidad de tanques aerobicos en serie | 3 |
| Temperatura del agua | C | Temperatura de operacion del agua residual | 20 |
| Tiene recirculacion interna | SI/NO | Recirculacion del ultimo reactor aerobico al primer anoxica | SI |
| Tiene recirculacion externa (RAS) | SI/NO | Retorno de lodos desde decantador | SI |
| Tiene purga de lodos (WAS) | SI/NO | Purga de lodos del sistema | SI |
| Tiempo de simulacion | dias | Duracion total de la simulacion para alcanzar estado estacionario | 200 |
| Metodo numerico | texto | BDF (recomendado), Radau, RK45, LSODA | BDF |
| Tolerancia relativa (rtol) | - | Precision relativa del integrador ODE | 1e-4 |
| Tolerancia absoluta (atol) | - | Precision absoluta del integrador ODE | 1e-6 |

---

### HOJA 2: "2_INFLUENTE"
**Proposito:** Composicion del agua residual de entrada. Los 13 componentes del modelo ASM1.

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F | Columna G |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Componente | Simbolo ASM1 | Valor | Unidad | Tipo | Descripcion | Valor BSM1 |

Incluir estos campos (uno por fila):

| Componente | Simbolo | Unidad | Tipo | Descripcion | Valor BSM1 |
|------------|---------|--------|------|-------------|------------|
| Caudal influente | Q | m3/d | Caudal | Caudal volumetrico medio diario de entrada | 18446 |
| Temperatura | T | C | Fisico | Temperatura del agua residual | 20 |
| Sustrato soluble facilmente biodegradable | S_S | mg COD/L | Soluble | DQO rapidamente biodegradable (acidos grasos, azucares) | 69.5 |
| Materia organica inerte soluble | S_I | mg COD/L | Soluble | DQO soluble no biodegradable (pasa por la planta sin cambio) | 30.0 |
| Sustrato particulado lentamente biodegradable | X_S | mg COD/L | Particulado | DQO particulada que se hidroliza lentamente | 202.32 |
| Materia organica inerte particulada | X_I | mg COD/L | Particulado | DQO particulada no biodegradable (se acumula en el lodo) | 51.2 |
| Biomasa heterotrofica activa | X_BH | mg COD/L | Particulado | Microorganismos heterotrofos ya presentes en el influente | 28.17 |
| Biomasa autotrofica activa | X_BA | mg COD/L | Particulado | Microorganismos nitrificantes en el influente (normalmente 0) | 0.0 |
| Productos de decaimiento celular | X_P | mg COD/L | Particulado | Residuos inertes de lisis celular (normalmente 0 en influente) | 0.0 |
| Oxigeno disuelto | S_O | mg O2/L | Soluble | OD en el influente (normalmente 0) | 0.0 |
| Nitrato y nitrito | S_NO | mg N/L | Soluble | Nitrogeno oxidado en el influente (normalmente 0) | 0.0 |
| Nitrogeno amoniacal | S_NH | mg N/L | Soluble | Amonio/amoniaco libre y salino | 31.56 |
| Nitrogeno organico soluble biodegradable | S_ND | mg N/L | Soluble | Fraccion de N organico soluble que se amonifica | 6.95 |
| Nitrogeno organico particulado biodegradable | X_ND | mg N/L | Particulado | Fraccion de N organico en particulas que se hidroliza | 10.59 |
| Alcalinidad | S_ALK | mol HCO3/m3 | Soluble | Capacidad tampon del agua (bicarbonato) | 7.0 |

**Notas para la hoja:**
- Anadir una celda de calculo automatico: `DQO Total Influente = S_I + S_S + X_I + X_S + X_BH + X_BA + X_P`
- Anadir una celda: `NT Total Influente = S_NH + S_ND + X_ND + 0.08*(X_BH+X_BA) + 0.06*X_P`
- Anadir nota: "ATENCION: S_ALK se introduce en mol HCO3/m3. QSDsan lo almacena internamente como mg/L multiplicado por 12 (factor de conversion). No multiplicar manualmente."
- Anadir nota: "Los valores de S_O, S_NO, X_BA y X_P en el influente suelen ser 0 para agua residual urbana cruda."

---

### HOJA 3: "3_REACTORES"
**Proposito:** Configuracion de cada reactor biologico (uno por fila).

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F | Columna G | Columna H |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Reactor ID | Tipo | Volumen (m3) | KLa (1/d) | DOsat (mg O2/L) | Orden en serie | Descripcion | Valor BSM1 |

Incluir estos reactores como ejemplo BSM1 (el usuario anadira o quitara filas segun su planta):

| Reactor ID | Tipo | Volumen (m3) | KLa (1/d) | DOsat (mg O2/L) | Orden | Descripcion | BSM1 |
|------------|------|-------------|-----------|-----------------|-------|-------------|------|
| A1 | Anoxic | 1000 | 0 | - | 1 | Primer reactor anoxica. Recibe influente + RAS + recirculacion interna | 1000 |
| A2 | Anoxic | 1000 | 0 | - | 2 | Segundo reactor anoxica en serie | 1000 |
| O1 | Aerobic | 1333 | 240 | 8.0 | 3 | Primer reactor aerobico. Aireacion alta | 1333 |
| O2 | Aerobic | 1333 | 240 | 8.0 | 4 | Segundo reactor aerobico. Aireacion alta | 1333 |
| O3 | Aerobic | 1333 | 84 | 8.0 | 5 | Tercer reactor aerobico. Aireacion reducida. Fuente de recirculacion interna | 1333 |

**Notas para la hoja:**
- "Tipo: Anoxic (sin aireacion, KLa=0) o Aerobic (con aireacion, KLa>0)"
- "KLa: Coeficiente volumetrico de transferencia de oxigeno. Tipico: 60-300 1/d para burbuja fina"
- "DOsat: Concentracion de saturacion de oxigeno. Tipico: 8-9 mg/L a 20C y nivel del mar"
- "El usuario puede anadir o eliminar filas segun el numero real de tanques de su planta"
- "Para reactores anoxicos: KLa = 0, DOsat = dejar vacio o poner '-'"
- Anadir celda de calculo: `Volumen total reactores = SUMA(columna Volumen)`
- Anadir celda de calculo: `HRT reactores (h) = Volumen total * 24 / Q`

---

### HOJA 4: "4_DECANTADOR"
**Proposito:** Parametros del decantador secundario (modelo Takacs de 10 capas).

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F |
|-----------|-----------|-----------|-----------|-----------|-----------|
| Parametro | Valor | Unidad | Descripcion | Valor BSM1 | Rango tipico |

Incluir estos campos:

| Parametro | Unidad | Descripcion | Valor BSM1 | Rango tipico |
|-----------|--------|-------------|------------|--------------|
| Area superficial | m2 | Area del fondo del decantador circular | 1500 | 500-5000 |
| Altura total | m | Profundidad/altura del decantador | 4 | 3-5 |
| Numero de capas del modelo | entero | Capas de discretizacion vertical (modelo Takacs) | 10 | 10 (estandar) |
| Capa de alimentacion | entero | Capa donde entra el flujo (indice 0-based desde arriba) | 5 | 4-6 |
| Velocidad maxima de sedimentacion teorica (v_max) | m/d | Velocidad maxima de Vesilind | 474 | 200-600 |
| Velocidad maxima practica (v_max_practical) | m/d | Limite superior realista | 250 | 100-400 |
| Concentracion umbral SS (X_threshold) | g/m3 | Umbral de solidos para zona compresion | 3000 | 2000-5000 |
| Parametro zona embotellada (rh) | m3/g | Factor exponencial para sedimentacion impedida (hindered) | 5.76e-4 | 3e-4 a 8e-4 |
| Parametro zona floculante (rp) | m3/g | Factor exponencial para sedimentacion floculante | 2.86e-3 | 1e-3 a 5e-3 |
| Fraccion no sedimentable (fns) | - | Fraccion de SST que no sedimenta (0-1) | 2.28e-3 | 1e-3 a 5e-3 |

**Notas para la hoja:**
- "El modelo Takacs usa una funcion exponencial doble: v(X) = min(v_max_practical, v_max * (exp(-rh*X*) - exp(-rp*X*)))"
- "X* = max(X - X_threshold, 0)"
- "Los parametros rh, rp, fns se calibran con ensayos de sedimentabilidad (SVI, SSVI) o datos historicos de la planta"
- Anadir celda de calculo: `Volumen decantador (m3) = Area * Altura`
- Anadir celda de calculo: `Carga superficial (m3/m2/d) = Q / Area`
- Anadir celda de calculo: `HRT decantador (h) = Volumen * 24 / Q_alimentacion`

---

### HOJA 5: "5_CAUDALES"
**Proposito:** Caudales de operacion del sistema.

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F |
|-----------|-----------|-----------|-----------|-----------|-----------|
| Corriente | Valor | Unidad | Ratio vs Q | Descripcion | Valor BSM1 |

Incluir estos campos:

| Corriente | Unidad | Ratio vs Q | Descripcion | Valor BSM1 |
|-----------|--------|-----------|-------------|------------|
| Caudal influente (Q) | m3/d | 1.0 | Caudal de entrada del agua residual | 18446 |
| Recirculacion interna (Q_intr) | m3/d | 3.0 | Desde ultimo reactor aerobico al primer anoxica | 55338 |
| Recirculacion externa RAS (Q_ras) | m3/d | 1.0 | Desde underflow del decantador al primer reactor | 18446 |
| Purga de lodos WAS (Q_was) | m3/d | - | Lodo extraido del sistema (controla la edad del lodo) | 385 |

**Notas para la hoja:**
- Anadir celdas de calculo automatico:
  - `Q efluente = Q - Q_was` (= 18061 m3/d en BSM1)
  - `Q alimentacion decantador = Q + Q_ras` (= 36892 m3/d)
  - `Q entrada al primer reactor = Q + Q_ras + Q_intr` (= 92230 m3/d)
  - `Ratio recirculacion interna = Q_intr / Q`
  - `Ratio recirculacion externa = Q_ras / Q`
- "La recirculacion interna (Q_intr) es critica para la desnitrificacion. Tipico: 1-5 veces Q"
- "La purga (Q_was) controla la edad del lodo (SRT). Mayor purga = menor SRT = menor nitrificacion"
- "En BSM1, Q_was = 385 m3/d produce un SRT de ~9 dias"

---

### HOJA 6: "6_CINETICA_ASM1"
**Proposito:** Parametros cineticos del modelo ASM1 (los que controlan la velocidad de las reacciones).

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F | Columna G |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Parametro | Simbolo | Valor | Unidad | Grupo | Descripcion | Rango tipico |

Incluir estos campos organizados por grupo:

**HETEROTROFOS (crecimiento y degradacion de DQO):**

| Parametro | Simbolo | Unidad | Descripcion | Valor BSM1 | Rango tipico |
|-----------|---------|--------|-------------|------------|--------------|
| Tasa maxima de crecimiento heterotrofico | mu_H | 1/d | Velocidad maxima a la que crecen los heterotrofos | 4.0 | 3.0-6.0 |
| Coef. semisaturacion de sustrato | K_S | mg COD/L | Concentracion de S_S a la que la tasa es la mitad del maximo | 10.0 | 5-20 |
| Coef. semisaturacion de oxigeno (heterotrofos) | K_OH | mg O2/L | Concentracion de OD a la que la tasa aerobica es mitad del maximo | 0.2 | 0.1-0.5 |
| Coef. semisaturacion de nitrato | K_NO | mg N/L | Concentracion de S_NO para crecimiento anoxica | 0.5 | 0.1-1.0 |
| Tasa de decaimiento heterotrofico | b_H | 1/d | Velocidad de muerte/lisis de heterotrofos | 0.3 | 0.2-0.4 |
| Factor de correccion anoxica (crecimiento) | eta_g | - | Reduccion de la tasa de crecimiento en condiciones anoxicas | 0.8 | 0.6-0.8 |

**AUTOTROFOS (nitrificacion):**

| Parametro | Simbolo | Unidad | Descripcion | Valor BSM1 | Rango tipico |
|-----------|---------|--------|-------------|------------|--------------|
| Tasa maxima de crecimiento autotrofico | mu_A | 1/d | Velocidad maxima de los nitrificantes (muy sensible a T) | 0.5 | 0.2-0.8 |
| Coef. semisaturacion de amonio | K_NH | mg N/L | Concentracion de S_NH a la que nitrificacion es mitad del maximo | 1.0 | 0.5-2.0 |
| Coef. semisaturacion de oxigeno (autotrofos) | K_OA | mg O2/L | Concentracion de OD para nitrificacion a media tasa | 0.4 | 0.3-1.0 |
| Tasa de decaimiento autotrofico | b_A | 1/d | Velocidad de muerte/lisis de nitrificantes | 0.05 | 0.03-0.1 |

**HIDROLISIS Y AMONIFICACION:**

| Parametro | Simbolo | Unidad | Descripcion | Valor BSM1 | Rango tipico |
|-----------|---------|--------|-------------|------------|--------------|
| Tasa maxima de hidrolisis | k_h | 1/d | Velocidad a la que X_S se convierte en S_S | 3.0 | 1.0-5.0 |
| Coef. semisaturacion de hidrolisis | K_X | g COD_XS / g COD_XBH | Ratio X_S/X_BH a la que hidrolisis es mitad del maximo | 0.1 | 0.01-0.2 |
| Factor de correccion anoxica (hidrolisis) | eta_h | - | Reduccion de la tasa de hidrolisis en condiciones anoxicas | 0.8 | 0.3-0.8 |
| Tasa de amonificacion | k_a | L/(mg COD * d) | Velocidad de conversion de S_ND a S_NH | 0.05 | 0.02-0.1 |

**Notas para la hoja:**
- "Los valores por defecto (BSM1) son los recomendados por IWA/IAWQ y son validos para 20C"
- "IMPORTANTE: mu_H y mu_A son MUY sensibles a la temperatura. Corregir con Arrhenius si T != 20C"
- "Si no se tiene calibracion especifica de la planta, usar los valores BSM1 como punto de partida"
- "La nitrificacion depende criticamente de mu_A, K_NH y K_OA"
- "La desnitrificacion depende de eta_g, K_NO y la tasa de recirculacion interna"

---

### HOJA 7: "7_ESTEQUIOMETRIA_ASM1"
**Proposito:** Parametros estequiometricos (rendimientos, fracciones, composiciones).

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F |
|-----------|-----------|-----------|-----------|-----------|-----------|
| Parametro | Simbolo | Valor | Unidad | Descripcion | Valor BSM1 |

Incluir estos campos:

| Parametro | Simbolo | Unidad | Descripcion | Valor BSM1 | Rango tipico |
|-----------|---------|--------|-------------|------------|--------------|
| Rendimiento heterotrofico | Y_H | g COD biomasa / g COD sustrato | Fraccion de sustrato que se convierte en biomasa nueva | 0.67 | 0.4-0.8 |
| Rendimiento autotrofico | Y_A | g COD biomasa / g N oxidado | Biomasa nitrificante generada por gramo de N-NH4 oxidado | 0.24 | 0.15-0.35 |
| Fraccion de productos en decaimiento | f_P | - | Parte de la biomasa que genera X_P (productos inertes) al morir | 0.08 | 0.05-0.15 |
| Contenido de N en biomasa | i_XB | g N / g COD | Fraccion de nitrogeno en la biomasa activa (X_BH, X_BA) | 0.08 | 0.06-0.10 |
| Contenido de N en productos de decay | i_XP | g N / g COD | Fraccion de nitrogeno en productos de decaimiento (X_P) | 0.06 | 0.04-0.08 |
| Factor de conversion TSS/COD | fr_SS_COD | g SS / g COD | Relacion entre solidos suspendidos y DQO particulada | 0.75 | 0.7-0.9 |

**Notas para la hoja:**
- "Y_H determina cuanto lodo se genera por unidad de DQO eliminada. Mayor Y_H = mas lodo"
- "Y_A es muy bajo (0.24) porque los nitrificantes crecen lentamente"
- "i_XB y i_XP se usan para el balance de nitrogeno (calcular TN en efluente)"
- "fr_SS_COD se usa para convertir las concentraciones de componentes particulados (en mg COD/L) a mg SS/L"

---

### HOJA 8: "8_CONDICIONES_INICIALES"
**Proposito:** Estado inicial de los reactores y del decantador al comenzar la simulacion.

| Columna A | Columna B | Columna C | Columna D | Columna E | Columna F |
|-----------|-----------|-----------|-----------|-----------|-----------|
| Componente | Simbolo | Valor inicial | Unidad | Descripcion | Valor BSM1 |

Incluir estos campos:

| Componente | Simbolo | Unidad | Descripcion | Valor BSM1 |
|------------|---------|--------|-------------|------------|
| Sustrato soluble | S_S | mg COD/L | Concentracion inicial de sustrato en todos los reactores | 5 |
| Materia inerte particulada | X_I | mg COD/L | Material inerte inicial (acumulado de operacion previa) | 1000 |
| Sustrato particulado | X_S | mg COD/L | Sustrato lento inicial | 100 |
| Biomasa heterotrofica | X_BH | mg COD/L | Biomasa activa inicial (CRITICO: debe ser > 0) | 500 |
| Biomasa autotrofica | X_BA | mg COD/L | Nitrificantes iniciales (CRITICO: debe ser > 0 para que haya nitrificacion) | 100 |
| Productos de decay | X_P | mg COD/L | Productos de decaimiento iniciales | 100 |
| Oxigeno disuelto | S_O | mg O2/L | OD inicial (se controla rapidamente por la aireacion) | 2 |
| Nitrato | S_NO | mg N/L | Nitratos iniciales | 20 |
| Amoniaco | S_NH | mg N/L | Amonio inicial | 2 |
| N organico soluble | S_ND | mg N/L | N organico soluble inicial | 1 |
| N organico particulado | X_ND | mg N/L | N organico particulado inicial | 1 |
| Alcalinidad | S_ALK | mol HCO3/m3 | Alcalinidad inicial (introducir en mol/m3; QSDsan multiplica x12 internamente) | 7 |

**Notas para la hoja:**
- "CRITICO: X_BH y X_BA DEBEN ser mayores que 0. Sin biomasa inicial no hay degradacion ni nitrificacion"
- "Sin X_BA suficiente, la nitrificacion NO arrancara incluso con 200 dias de simulacion"
- "Si se usa EXPOsan create_system(), las condiciones iniciales se cargan automaticamente desde un Excel interno con valores calibrados"
- "Si se construye el sistema manualmente, usar estos valores como punto de partida"
- "Para una planta en operacion real, usar los valores medidos en el licor mezcla como condiciones iniciales"
- "TSS inicial (calculado) = 0.75 * (X_I + X_S + X_BH + X_BA + X_P)"

---

## FORMATO Y ESTILO DEL EXCEL

### Formato visual obligatorio:
1. **Cabeceras**: Fondo azul oscuro (#1F4E79), texto blanco, negrita, filtros activados
2. **Filas alternas**: Gris claro (#F2F2F2) / blanco para facilitar lectura
3. **Columna "Valor"**: Celdas con borde grueso y fondo amarillo claro (#FFF2CC) para indicar que son editables por el usuario
4. **Columna "Valor BSM1"**: Fondo gris (#D9D9D9), solo lectura (referencia)
5. **Columna "Rango tipico"** (donde aplique): Fondo verde claro (#E2EFDA)
6. **Notas**: En filas debajo de la tabla con fondo naranja claro (#FCE4D6)
7. **Celdas de calculo**: Fondo azul claro (#D6E4F0) con formulas (no valores manuales)
8. **Ancho de columnas**: Auto-ajustado al contenido, minimo 15 caracteres
9. **Validacion de datos**: Donde sea posible, anadir listas desplegables (ej: Tipo reactor = "Anoxic" / "Aerobic")

### Hoja resumen (opcional pero recomendada):
Crear una hoja "0_RESUMEN" al inicio con:
- Nombre de la planta (enlazado a hoja 1)
- DQO total influente (calculado desde hoja 2)
- NT total influente (calculado desde hoja 2)
- Volumen total reactores (calculado desde hoja 3)
- HRT total sistema (calculado)
- Volumen decantador (calculado desde hoja 4)
- Numero de parametros configurados vs pendientes (conteo de celdas no vacias en columna "Valor")

### Proteccion:
- Las celdas de referencia (BSM1, rangos, descripciones) deben estar protegidas contra edicion accidental
- Las celdas de "Valor" (amarillas) deben ser las unicas editables
- Incluir un boton o nota indicando: "Desproteger hoja para modo avanzado"

---

## VALIDACIONES EN EL EXCEL

Anadir las siguientes validaciones automaticas (con formato condicional rojo si se violan):

### En hoja 2 (Influente):
- `Q > 0` (caudal debe ser positivo)
- `S_ALK >= 0` (alcalinidad no puede ser negativa)
- Todos los componentes `>= 0`
- `S_O = 0` y `S_NO = 0` son lo normal (advertencia si > 0)

### En hoja 3 (Reactores):
- `Volumen > 0` para todos los reactores
- Si Tipo = "Anoxic" entonces `KLa = 0`
- Si Tipo = "Aerobic" entonces `KLa > 0` y `DOsat > 0`
- Al menos 1 reactor aerobico (sin aireacion no hay nitrificacion)

### En hoja 5 (Caudales):
- `Q_was > 0` (sin purga no hay control de lodo)
- `Q_was < Q` (no se puede purgar mas de lo que entra)
- `Q_ras > 0` (sin RAS no hay lodo activo)
- `Q_efluente = Q - Q_was > 0`

### En hoja 6 (Cinetica):
- Todos los parametros `> 0`
- `mu_A < mu_H` (autotrofos siempre crecen mas lento)
- `0 < eta_g <= 1` y `0 < eta_h <= 1`
- `b_A < b_H` (decaimiento autotrofico menor que heterotrofico)

### En hoja 7 (Estequiometria):
- `0 < Y_H < 1` y `0 < Y_A < 1`
- `0 < f_P < 1`
- `0 < fr_SS_COD < 1`

### En hoja 8 (Condiciones iniciales):
- `X_BH > 0` (CRITICO: sin biomasa heterotrofica no hay degradacion)
- `X_BA > 0` (CRITICO: sin nitrificantes no hay nitrificacion)
- Advertencia si `X_BA < 50` ("Posible fallo de arranque de nitrificacion")

---

## INFORMACION ADICIONAL PARA LA IA

### Contexto tecnico:
- **ASM1** (Activated Sludge Model No. 1) es el modelo estandar IWA para simular eliminacion biologica de DQO y nitrogeno en EDAR
- Tiene 13 componentes de estado y 8 procesos bioquimicos
- NO incluye eliminacion biologica de fosforo (para eso se usa ASM2d)
- El software QSDsan (v1.3.0) con EXPOsan (v1.4.3) implementa este modelo en Python
- El BSM1 (Benchmark Simulation Model No. 1) es la configuracion de referencia IWA para validar implementaciones

### Quien usara este Excel:
- Ingenieros de proceso de EDAR que quieren simular su planta real
- Necesitan saber QUE datos recopilar de su planta antes de simular
- Pueden no ser expertos en modelacion pero si en operacion de EDAR
- El Excel debe ser autoexplicativo: cada campo con descripcion clara

### Objetivo final:
- El usuario rellena el Excel con datos de su planta
- Un script Python lee el Excel y configura QSDsan automaticamente
- Se lanza la simulacion y se comparan resultados con datos reales
- El Excel sirve como documentacion de la configuracion de cada planta simulada
