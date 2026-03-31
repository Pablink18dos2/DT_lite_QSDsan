# CLAUDE.md - Contexto completo para el simulador BSM1 con QSDsan

> Este archivo contiene TODA la informacion que necesita una IA para modificar,
> ejecutar y validar el simulador BSM1 implementado con QSDsan/EXPOsan.
> Es el unico archivo de contexto necesario (reemplaza README, INICIO_RAPIDO, BSM1_referencia_IWA).
> Ultima actualizacion: 2026-03-25.

---

## 1. Entorno y rutas

| Elemento | Valor |
|----------|-------|
| Python | `C:\Users\pamongo\AppData\Local\Programs\Python\Python313\python.exe` |
| Version Python | 3.13 |
| OS | Windows 11 Pro |
| Codificacion consola | cp1252 (no soporta Unicode: usar ASCII en prints) |
| QSDsan | 1.3.0 |
| EXPOsan | 1.4.3 |
| Site-packages | `C:\Users\pamongo\AppData\Local\Programs\Python\Python313\Lib\site-packages\` |
| EXPOsan BSM1 | `...\site-packages\exposan\bsm1\system.py` |
| Datos dry weather | `...\site-packages\qsdsan\data\sanunit_data\_inf_dry_2006.tsv` |

### Instalacion

```bash
pip install qsdsan==1.3.0 exposan==1.4.3
```

---

## 2. Estructura del directorio

```
QSDsan_test01/
  claude.md                              <-- Este archivo (unico .md necesario)
  run_bsm1_simulation.py                 <-- Script principal de simulacion
  resultados_bsm1_ss_componentes.csv     <-- CSV con resultados estado estacionario
  RESULTADOS_VALIDACION_BSM1.txt         <-- Reporte completo de validacion
```

---

## 3. Documentacion de referencia externa

> **IMPORTANTE**: Consultar esta documentacion cuando se necesite informacion sobre
> funciones, clases o capacidades de QSDsan que no esten cubiertas en este archivo.

| Recurso | URL |
|---------|-----|
| **Tutoriales y API QSDsan** | https://qsdsan.readthedocs.io/en/latest/tutorials/_index.html |
| **Documentacion oficial** | https://qsdsan.readthedocs.io/en/latest/ |
| **GitHub QSDsan** | https://github.com/QSD-Group/QSDsan |
| **GitHub EXPOsan** | https://github.com/QSD-Group/EXPOsan |
| **PyPI QSDsan** | https://pypi.org/project/qsdsan |
| **Paper principal** | https://doi.org/10.1039/d2ew00455k |
| **Canal YouTube QSD** | https://youtube.com/channel/UC8fyVeo9xf10KeuZ_4vC_GA |

### Tutoriales oficiales disponibles

| Tutorial | Contenido |
|----------|----------|
| 00 - Quick Overview | Panorama general de capacidades |
| 01 - Helpful Basics | Python, Jupyter, OOP |
| 02 - Component | Creacion de componentes |
| 03 - WasteStream | Flujos de agua residual |
| 04 - SanUnit (basico) | Operaciones unitarias |
| 05 - SanUnit (avanzado) | Creacion personalizada |
| 06 - System | Ensamblaje de sistemas |
| 07 - TEA | Analisis economico |
| 08 - LCA | Analisis de ciclo de vida |
| 09 - Uncertainty & Sensitivity | Analisis estadisticos |
| 10 - Process | Procesos estequiometricos y cineticos |
| 11 - Dynamic Simulation | Simulacion dinamica completa |
| 12 - ADM1 | Digestion anaerobia |
| 13 - Process Modeling 101 | Tutorial mas completo para EDAR |

---

## 4. Parche obligatorio para Python 3.13

Python 3.13 elimino `pkg_resources`. Hay que parchear **dos archivos**:

### `site-packages/qsdsan/__init__.py`
### `site-packages/exposan/__init__.py`

Cambiar:
```python
# ANTES
import pkg_resources
__version__ = pkg_resources.get_distribution('qsdsan').version

# DESPUES
try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution('qsdsan').version
except ModuleNotFoundError:
    from importlib.metadata import version
    __version__ = version('qsdsan')
```

---

## 5. Arquitectura de QSDsan

QSDsan (Quantitative Sustainable Design for Sanitation) es una plataforma Python
de codigo abierto para simulacion integrada de EDAR. Combina:
- Simulacion de procesos (ASM1, ASM2d, ADM1)
- Analisis tecno-economico (TEA)
- Analisis de ciclo de vida (ACV/LCA)
- Analisis de incertidumbre y sensibilidad

### Clases principales

| Clase | Funcion |
|-------|---------|
| **Component** | Compuestos quimicos o grupos de biomasa |
| **WasteStream / SanStream** | Flujos de agua residual con propiedades (COD, TN, TP, TSS) |
| **Process** | Proceso estequiometrico y cinetico individual |
| **Processes (CompiledProcesses)** | Conjunto compilado: ASM1, ASM2d, ADM1 |
| **SanUnit** | Operacion unitaria: CSTR, decantador, espesador |
| **System** | Agrupacion de SanUnits con recirculaciones |
| **TEA / SimpleTEA** | Analisis tecno-economico |
| **LCA / ImpactIndicator** | Analisis de ciclo de vida |

### Modelos de proceso disponibles

| Modelo | Descripcion |
|--------|-------------|
| **ASM1** | 13 componentes, 8 procesos. Eliminacion COD + N (sin P). **Usado en BSM1** |
| **ASM2d** | 19 componentes, 21 procesos. Eliminacion COD + N + P biologico (PAOs) |
| **ASM3** | Mejora cinetica de ASM1 en captacion de sustrato |
| **ADM1** | 26 variables. Digestion anaerobia completa + biogas |
| **mASM2d** | ASM2d modificado con precipitacion de minerales |

### Operaciones unitarias principales

**Tratamiento biologico:**
- CSTR -- Reactor de mezcla completa
- ActivatedSludgeProcess -- Sistema de lodo activo parametrizable
- AnaerobicCSTR -- Reactor anaerobio

**Decantacion:**
- FlatBottomCircularClarifier -- Decantador secundario de 10 capas (modelo de Takacs)
- PrimaryClarifier -- Decantador primario

**Tratamiento de lodos:**
- BeltThickener, Centrifuge, DryingBed, Incinerator

**Energia:**
- CHP (cogeneracion biogas), BiogasCombustion, CH4E, H2E

---

## 6. Configuracion BSM1

### 6.1 Reactores

| Reactor | ID  | Tipo     | Volumen (m3) | KLa (1/d) | DOsat (mg/L) |
|---------|-----|----------|--------------|------------|--------------|
| R1      | A1  | Anoxic   | 1000         | 0          | --           |
| R2      | A2  | Anoxic   | 1000         | 0          | --           |
| R3      | O1  | Aerobic  | 1333         | 240        | 8.0          |
| R4      | O2  | Aerobic  | 1333         | 240        | 8.0          |
| R5      | O3  | Aerobic  | 1333         | 84         | 8.0          |

### 6.2 Decantador secundario (C1)

| Parametro | Valor |
|-----------|-------|
| Tipo | FlatBottomCircularClarifier |
| Area superficial | 1500 m2 |
| Altura total | 4 m |
| Volumen total | 6000 m3 |
| Numero de capas | 10 |
| Capa de alimentacion | 5 (indice 0-based en QSDsan; = capa 6 en BSM1 1-based) |

### 6.3 Caudales de operacion

| Corriente | Valor (m3/d) | Nota |
|-----------|-------------|------|
| Influente Q | 18 446 | |
| Recirculacion interna (O3->A1) | 55 338 | = 3Q |
| Recirculacion externa RAS (C1->A1) | 18 446 | = 1Q |
| Purga WAS | 385 | |
| Efluente final | 18 061 | = Q - WAS |
| Alimentacion al decantador | 36 892 | = 2Q |
| Entrada total a A1 | 92 230 | = Q + 3Q + 1Q |

### 6.4 Influente estandar (dry weather constante)

| Componente | Valor | Unidad |
|------------|-------|--------|
| S_I | 30.0 | mg COD/L |
| S_S | 69.5 | mg COD/L |
| X_I | 51.2 | mg COD/L |
| X_S | 202.32 | mg COD/L |
| X_BH | 28.17 | mg COD/L |
| X_BA | 0.0 | mg COD/L |
| X_P | 0.0 | mg COD/L |
| S_O | 0.0 | mg O2/L |
| S_NO | 0.0 | mg N/L |
| S_NH | 31.56 | mg N/L |
| S_ND | 6.95 | mg N/L |
| X_ND | 10.59 | mg N/L |
| S_ALK | 7.0 | mol HCO3/m3 |

> **ATENCION S_ALK en EXPOsan**: Se almacena como `7 * 12 = 84` mg/L internamente.
> Para obtener mol HCO3/m3 desde la concentracion del stream: `conc / 12`.

**COD Total Influente:** 381.19 mg/L

---

## 7. Valores de referencia IWA (estado estacionario)

> Fuente: Dr. Ulf Jeppsson, Lund University, 2008. Tolerancia: +/-5%.

| Variable | Referencia | Unidad |
|----------|-----------|--------|
| S_I | 30.0 | mg COD/L |
| S_S | 0.889 | mg COD/L |
| X_I | 4.392 | mg COD/L |
| X_S | 0.188 | mg COD/L |
| X_BH | 9.782 | mg COD/L |
| X_BA | 0.573 | mg COD/L |
| X_P | 1.728 | mg COD/L |
| S_O | 0.491 | mg COD/L |
| S_NO | 10.415 | mg N/L |
| S_NH | 1.733 | mg N/L |
| S_ND | 0.688 | mg N/L |
| X_ND | 0.013 | mg N/L |
| S_ALK | 4.126 | mol HCO3/m3 |
| TSS | 12.497 | mg SS/L |

### Variables agregadas (estado estacionario)

| Variable | Referencia |
|----------|-----------|
| SRT tradicional | 7.32 dias |
| SRT especifico | 9.14 dias |
| HRT total | 15.61 h |
| HRT solo reactores | 7.81 h |
| TSS underflow | 6394 mg SS/L |
| Q efluente | 18 061 m3/d |

### Cargas medias en efluente (estado estacionario)

| Variable | Carga (kg/d) |
|----------|-------------|
| COD total | 872.3 |
| TN total | 281.2 |
| N Kjeldahl | 121.8 |
| TSS | 234.6 |
| BOD5 | 50.1 |
| S_NO | 159.4 |
| S_NH | 85.95 |

---

## 8. Valores de referencia IWA (dinamico, dry weather dias 7-14)

> Medias ponderadas por caudal, dias 7-14 de la simulacion dinamica.
> Simulacion de 150 dias con CONSTANTINPUT para alcanzar estado estacionario,
> luego 14 dias con DRYWEATHER.

| Variable | Referencia | Limite IWA |
|----------|-----------|-----------|
| Q efluente | 18 061.3 m3/d | -- |
| S_I | 30.0 mg COD/L | -- |
| S_S | 0.974 mg COD/L | -- |
| X_BH | 10.221 mg COD/L | -- |
| S_O | 0.746 mg COD/L | -- |
| S_NH | 4.759 mg N/L | <= 4 (VIOLACION ESPERADA) |
| S_NO | 8.824 mg N/L | -- |
| TSS | 12.992 mg SS/L | <= 30 |
| TN total | 15.569 mg N/L | <= 18 |
| COD total | 48.296 mg COD/L | <= 100 |
| BOD5 | 2.775 mg/L | <= 10 |
| N Kjeldahl | 6.745 mg N/L | -- |
| S_ALK | 4.456 mol HCO3/m3 | -- |

> **IMPORTANTE**: S_NH > 4 mg/L es el comportamiento ESPERADO y CORRECTO
> del BSM1 en lazo abierto. Si S_NH < 4, revisar KLa o recirculacion interna.

---

## 9. Parametros cineticos ASM1 (valores por defecto IWA)

### Estequiometricos

| Parametro | Valor | Unidad | Descripcion |
|-----------|-------|--------|-------------|
| Y_H | 0.67 | gCOD/gCOD | Rendimiento heterotrofos |
| Y_A | 0.24 | gCOD/gN | Rendimiento autotrofos |
| f_P | 0.08 | -- | Fraccion productos en lisis |
| i_XB | 0.08 | g N/g COD | Contenido N en biomasa |
| i_XP | 0.06 | g N/g COD | Contenido N en productos |
| fr_SS_COD | 0.75 | -- | Factor conversion TSS/COD |

### Cineticos -- Heterotrofos

| Parametro | Valor | Unidad | Descripcion |
|-----------|-------|--------|-------------|
| mu_H | 4.0 | 1/d | Tasa max crecimiento |
| K_S | 10.0 | mg COD/L | Saturacion sustrato |
| K_OH | 0.2 | mg O2/L | Saturacion O2 |
| K_NO | 0.5 | mg N/L | Saturacion nitrato |
| b_H | 0.3 | 1/d | Tasa decaimiento |
| eta_g | 0.8 | -- | Factor correccion anoxica |
| eta_h | 0.8 | -- | Factor correccion hidrolisis |
| k_h | 3.0 | 1/d | Tasa max hidrolisis |
| K_X | 0.1 | -- | Saturacion hidrolisis |
| k_a | 0.05 | L/(mg COD*d) | Tasa amonificacion |

### Cineticos -- Autotrofos (nitrificadores)

| Parametro | Valor | Unidad | Descripcion |
|-----------|-------|--------|-------------|
| mu_A | 0.5 | 1/d | Tasa max crecimiento |
| K_NH | 1.0 | mg N/L | Saturacion amonio |
| K_OA | 0.4 | mg O2/L | Saturacion O2 |
| b_A | 0.05 | 1/d | Tasa decaimiento |

---

## 10. Formulas clave para calculos

### TSS (solidos suspendidos totales)
```python
def calc_tss(stream, fr_SS_COD=0.75):
    """TSS = fr_SS_COD * sum(X_i) donde X_i en mg COD/L"""
    x_components = ['X_I', 'X_S', 'X_BH', 'X_BA', 'X_P']
    return fr_SS_COD * sum(get_conc(stream, c) for c in x_components)
```

### COD total
```python
def calc_cod_total(stream):
    """COD = sum(S_i) + sum(X_i) en mg COD/L (NO incluir S_O, S_NO, S_NH, S_ND, X_ND, S_ALK)"""
    cod_components = ['S_I', 'S_S', 'X_I', 'X_S', 'X_BH', 'X_BA', 'X_P']
    return sum(get_conc(stream, c) for c in cod_components)
```

### Nitrogeno total
```python
def calc_tn(stream):
    """TN = S_NO + S_NH + S_ND + X_ND + i_XB*(X_BH+X_BA) + i_XP*X_P"""
    # i_XB = 0.08 g N/g COD (fraccion N en biomasa)
    # i_XP = 0.06 g N/g COD (fraccion N en productos)
    return S_NO + S_NH + S_ND + X_ND + 0.08*(X_BH + X_BA) + 0.06*X_P
```

### BOD5
```python
def calc_bod5(stream, f_P=0.08):
    """BOD5 = 0.65 * (S_S + X_S + (1-f_P)*(X_BH + X_BA))"""
    return 0.65 * (S_S + X_S + (1 - f_P) * (X_BH + X_BA))
```

### Alcalinidad
```python
def get_alk(stream):
    """S_ALK almacenado como mg/L, dividir por 12 para mol HCO3/m3"""
    return get_conc(stream, 'S_ALK') / 12
```

### Caudal
```python
# CRITICO: F_vol esta en m3/hr, NO m3/d
q_m3_d = stream.F_vol * 24
```

---

## 11. API clave de QSDsan/EXPOsan para BSM1

### Crear sistema
```python
from exposan.bsm1 import create_system
sys = create_system()  # Usa todos los defaults BSM1
```

### Acceder a unidades y streams
```python
units = {u.ID: u for u in sys.units}
A1 = units['A1']  # Reactor anoxic 1
C1 = units['C1']  # Clarifier

# Streams de salida del clarifier:
effluent = C1.outs[0]      # Efluente (overflow)
underflow = C1.outs[1]     # Lodos (underflow/RAS + WAS)
```

### Simular estado estacionario
```python
sys.simulate(
    t_span=(0, 200),        # 200 dias para convergencia
    method='BDF',            # O 'Radau' como fallback
    state_reset_hook='reset_cache'  # OBLIGATORIO para dinamica
)
```

### Obtener concentracion de un componente
```python
def get_conc(stream, comp_id):
    """Concentracion en mg/L de un componente en un stream"""
    idx = stream.components.index(comp_id)
    return stream.conc[idx]  # mg/L
```

### Acceso a propiedades de streams
```python
# Propiedades predefinidas que FUNCIONAN:
stream.COD    # mg/L
stream.TN     # mg/L
stream.TP     # mg/L
stream.BOD5   # mg/L
stream.F_vol  # m3/hr (NO m3/d!)

# Acceso a componentes individuales:
stream.imass['S_NH']  # kg/hr (acceso directo)

# NO funciona:
stream.TSS              # No existe, calcular manualmente con calc_tss()
stream.imass.get('X')   # ChemicalMassFlowIndexer NO tiene metodo .get()
```

### Diagrama del sistema
```python
sys.diagram(format='png', dpi='150')  # Requiere Graphviz instalado en sistema
```

### Componentes ASM1 (13 en total)
```python
import qsdsan.processes as pc
cmps = pc.create_asm1_cmps()
# Solubles: S_I, S_S, S_NH, S_NO, S_ND, S_O, S_ALK
# Particulados: X_I, X_S, X_BH, X_BA, X_P, X_ND
```

> **CRITICO** - Nomenclatura ASM1 vs ASM2d:
> - ASM1 usa: `S_O`, `S_NH`, `S_NO` <-- Para BSM1
> - ASM2d usa: `S_O2`, `S_NH4`, `S_NO3`
> Confundir nombres causa KeyError silencioso.

---

## 12. Como ejecutar la simulacion

```bash
cd "c:\Users\pamongo\OneDrive - GlobalOmnium Idrica S.L\Nube personal\IDRICA\📒Bibliografía\AGUAS\EDAR\Modelación & Algoritmia\2026\QSDsan simulador open\QSDsan_test01"
python run_bsm1_simulation.py
```

### Que hace el script:
1. Importa QSDsan/EXPOsan
2. Crea el sistema BSM1 con `create_system()`
3. Intenta generar diagrama (requiere Graphviz instalado)
4. Simula 200 dias estado estacionario (BDF, despues Radau si falla)
5. Valida 14 componentes + TSS contra referencia IWA (+/-5%)
6. Genera CSV y TXT con resultados

### Archivos generados:
- `resultados_bsm1_ss_componentes.csv` - Datos tabulados
- `RESULTADOS_VALIDACION_BSM1.txt` - Reporte completo

---

## 13. Resultados obtenidos (estado estacionario)

**14/14 componentes PASS** (dentro de +/-5% de referencia IWA).

Ejemplos clave:
- S_NH: 1.733 vs ref 1.733 (0.0% error)
- S_NO: 10.415 vs ref 10.415 (0.0% error)
- TSS: 12.507 vs ref 12.497 (0.1% error)
- SRT especifico: 9.14 vs ref 9.14 dias

---

## 14. Checklist de validacion

```python
# Estado estacionario -- tolerancia +/-5%
assert 1.645 < S_NH_ss  < 1.820   # ref: 1.733 mg N/L
assert 9.894 < S_NO_ss  < 10.936  # ref: 10.415 mg N/L
assert 11.87 < TSS_ss   < 13.12   # ref: 12.497 mg SS/L
assert 6.95  < SRT_trad < 7.68    # ref: 7.32 dias
assert 8.69  < SRT_spec < 9.60    # ref: 9.14 dias

# Dinamico dry weather (media dias 7-14) -- limites IWA
assert COD_total < 100   # mg COD/L
assert TN_total  < 18    # mg N/L
assert TSS_eff   < 30    # mg SS/L
assert BOD5_eff  < 10    # mg/L
# S_NH > 4 es VIOLACION ESPERADA en lazo abierto (ref = 4.759)
```

---

## 15. Protocolo de simulacion dinamica BSM1

Si se resuelve la incompatibilidad del clarifier en futuras versiones:

1. Simular 150 dias con CONSTANTINPUT para alcanzar estado estacionario
2. Cambiar a DRYWEATHER (datos en `_inf_dry_2006.tsv`, 14 dias, 1345 puntos)
3. Simular 14 dias adicionales
4. Calcular medias ponderadas por caudal de los dias 7 a 14:
   ```python
   media_ponderada = sum(C_i * Q_i * dt_i) / sum(Q_i * dt_i)
   ```
5. Comparar con valores de la seccion 8 de este documento

---

## 16. Limitaciones conocidas y problemas

### 16.1 Simulacion dinamica NO funciona correctamente

Tres enfoques intentados, ninguno exitoso:

1. **DynamicInfluent + simulate**: FloatingPointError en clarifier ODE
   - `_clarifier.py:426` - `invalid value encountered in subtract`
   - QSDsan configura `np.seterr(divide='raise', invalid='raise')`
   - Relajar con `np.seterr(all='warn')` causa propagacion de NaN

2. **DynamicInfluent relajado**: Simula pero produce NaN en el clarifier

3. **Quasi-dinamico (stepping horario)**: Resultados incorrectos
   - S_NO = 20.17 vs ref 8.824 (128% error)
   - S_NH = 1.63 vs ref 4.759 (65% error)
   - Razon: cada step alcanza cuasi-estado-estacionario, no captura transitorios

> **Conclusion**: La combinacion DynamicInfluent + FlatBottomCircularClarifier
> en modo CSTR tiene una incompatibilidad fundamental en QSDsan 1.3.0/EXPOsan 1.4.3.
> La simulacion dinamica requiere investigar versiones mas recientes o alternativas.

### 16.2 Graphviz no instalado

`sys.diagram()` requiere Graphviz en el sistema. Sin el, se usa un diagrama ASCII.
Para instalar: `pip install graphviz` + instalar binario desde graphviz.org.

### 16.3 Codificacion Windows cp1252

La consola Windows no renderiza caracteres Unicode (checkmarks, flechas, etc.).
Usar siempre ASCII en outputs de print: `[PASS]`, `[FAIL]`, `-->`, etc.

### 16.4 batch_init no funciona con DynamicInfluent

`exposan.bsm1.batch_init()` llama `set_init_conc()` en todas las unidades,
pero DynamicInfluent no tiene ese metodo. Hay que iterar manualmente:
```python
for unit in sys.units:
    if hasattr(unit, 'set_init_conc'):
        unit.set_init_conc(...)
```

### 16.5 Condiciones iniciales son CRITICAS

El BSM1 es muy sensible a las condiciones iniciales. Sin `X_BA` (nitrificadores)
presentes desde el inicio, la nitrificacion no ocurre incluso con:
- Simulaciones largas (40-50 dias)
- Aireacion mejorada (KLa duplicado)
- Intentos de seeding manual

**Solucion**: Usar SIEMPRE EXPOsan `create_system()` que carga condiciones
iniciales correctas desde archivo Excel interno con biomasa nitrificante
pre-existente.

### 16.6 steady_state=True no funciona

En QSDsan 1.3.0, `steady_state=True` tiene problemas de compatibilidad con scipy.
Usar simulacion dinamica larga (200 dias) para alcanzar estado estacionario.

---

## 17. Construccion manual del sistema (referencia)

Si se necesita construir el sistema BSM1 desde cero en lugar de usar EXPOsan:

```python
import numpy as np
from qsdsan import sanunits as su, processes as pc, WasteStream, System
import qsdsan as qs

# 1. Componentes ASM1
cmps = pc.create_asm1_cmps()
qs.set_thermo(cmps)

# 2. Modelo ASM1
asm1 = pc.ASM1()

# 3. Aireacion
aer1 = pc.DiffusedAeration('aer1', DO_ID='S_O', KLa=240, DOsat=8.0, V=1333)
aer3 = pc.DiffusedAeration('aer3', DO_ID='S_O', KLa=84,  DOsat=8.0, V=1333)

# 4. Influente
T = 293.15  # 20C
inf = WasteStream('influente', T=T)
inf.set_flow_by_concentration(
    flow_tot=18446,
    concentrations={
        'S_I': 30, 'S_S': 69.5, 'S_NH': 31.56, 'S_ND': 6.95,
        'X_I': 51.2, 'X_S': 202.32, 'X_BH': 28.17,
        'S_ALK': 84, 'S_O': 0, 'S_NO': 0, 'X_BA': 0
    },
    units=('m3/d', 'mg/L')
)

# 5. Flujos internos
rec_int = WasteStream('rec_int', T=T)
rec_ext = WasteStream('rec_ext', T=T)

# 6. Reactores
A1 = su.CSTR('A1', ins=[inf, rec_ext, rec_int], V_max=1000,
    aeration=0, DO_ID='S_O', suspended_growth_model=asm1)
A2 = su.CSTR('A2', ins=A1-0, V_max=1000,
    aeration=0, DO_ID='S_O', suspended_growth_model=asm1)
O1 = su.CSTR('O1', ins=A2-0, V_max=1333,
    aeration=aer1, DO_ID='S_O', suspended_growth_model=asm1)
O2 = su.CSTR('O2', ins=O1-0, V_max=1333,
    aeration=aer1, DO_ID='S_O', suspended_growth_model=asm1)
O3 = su.CSTR('O3', ins=O2-0, V_max=1333,
    aeration=aer3, DO_ID='S_O',
    outs=[rec_int, 'pretratado'],
    split=[0.6, 0.4],
    suspended_growth_model=asm1)

# 7. Decantador
clarifier = su.FlatBottomCircularClarifier(
    'CL', ins=O3-1,
    outs=['efluente', rec_ext, 'lodos_descarga'],
    underflow=18446, wastage=385,
    surface_area=1500, height=4, N_layer=10, feed_layer=4
)

# 8. Sistema
sys = System('BSM1', path=(A1, A2, O1, O2, O3, clarifier),
    recycle=(rec_ext, rec_int))

# AVISO: condiciones iniciales manuales probablemente fallaran.
# Usar EXPOsan create_system() en su lugar.
```

---

## 18. Analisis avanzados (TEA, LCA, incertidumbre)

### Analisis tecno-economico (TEA)
```python
import qsdsan as qs
tea = qs.TEA(system=sys, IRR=0.05, duration=(2024, 2044),
    depreciation='MACRS7', income_tax=0.21, annual_maintenance=0.01)
print(f"CAPEX: {tea.total_installed_equipment_cost:,.0f} $")
print(f"OPEX anual: {tea.annual_operating_cost:,.0f} $/a")
```

### Analisis de ciclo de vida (LCA)
```python
lca = qs.LCA(system=sys, lifetime=20, lifetime_unit='yr')
print(f"GWP: {lca.total_impacts['GWP100']:,.0f} kg CO2-eq")
```

### Analisis de incertidumbre
```python
import qsdsan.stats as s
modelo = qs.Model(system=sys)

@modelo.parameter(name='mu_H', element=asm1,
    distribution=s.shape.Uniform(lower=3.0, upper=6.0))
def set_mu_H(value):
    asm1.parameters['mu_H'] = value

@modelo.metric(name='COD_eff', units='mg/L')
def get_COD():
    return sys.streams[-1].COD

s.morris_analysis(modelo, num_levels=4, N=100)
```

---

## 19. Glosario

| Termino | Definicion |
|---------|-----------|
| ADM1 | Anaerobic Digestion Model No. 1 (26 variables) |
| ASM1/2d/3 | Activated Sludge Models (modelos IWA de lodo activo) |
| ACV / LCA | Analisis de Ciclo de Vida |
| BDF | Backward Differentiation Formula (metodo numerico ODEs stiff) |
| BSM1 / BSM2 | Benchmark Simulation Model (configuraciones referencia IWA) |
| CAPEX | Capital Expenditure (inversion inicial) |
| COD / DQO | Demanda Quimica de Oxigeno |
| CSTR | Continuously Stirred Tank Reactor |
| EDAR | Estacion Depuradora de Aguas Residuales (WWTP en ingles) |
| KLa | Coeficiente volumetrico de transferencia de oxigeno (1/d) |
| OPEX | Operational Expenditure (costes de operacion) |
| PAO | Phosphorus Accumulating Organisms |
| RAS | Return Activated Sludge (recirculacion externa) |
| SRT | Solids Retention Time (edad del lodo) |
| TEA | Techno-Economic Analysis |
| TN / TP | Nitrogeno / Fosforo Total |
| TSS / VSS | Total / Volatile Suspended Solids |
| WAS | Waste Activated Sludge (purga de lodo) |

---

## 20. Notas para futuras sesiones

- El estado estacionario esta **completamente validado** (14/14 PASS)
- La simulacion dinamica es el **principal trabajo pendiente**
- Investigar actualizaciones de QSDsan > 1.3.0 que puedan resolver el problema del clarifier
- Alternativa: implementar clarifier propio compatible con ODE dinamica
- Si se instala Graphviz, activar `sys.diagram()` para generar PNG del esquema
- El script actual es robusto y autocontenido, no requiere archivos externos
- Todos los valores de referencia IWA estan hardcodeados en `run_bsm1_simulation.py`
- Usar SIEMPRE EXPOsan `create_system()`, NUNCA construir sistema manualmente
- Consultar https://qsdsan.readthedocs.io/en/latest/tutorials/_index.html para API completa

---

## 21. Estructura .claude/ del proyecto

- `.claude/commands/` - Comandos de proyecto:
  - `/project:run-simulation` - Ejecutar simulacion
  - `/project:validate-results` - Validar resultados contra referencia IWA
  - `/project:explore-component` - Explorar un componente ASM1
  - `/project:check-environment` - Verificar entorno Python/QSDsan
- `.claude/rules/` - Convenciones de codigo (code-style, testing, simulation-conventions)
- `.claude/agents/` - Agente validador de simulacion EDAR
- Linter/Formatter: Ruff (config en `pyproject.toml`)
- Ejecutar `ruff check .` y `ruff format .` antes de commits
