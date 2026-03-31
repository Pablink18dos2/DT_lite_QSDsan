# Simulation Conventions

## System Construction
- ALWAYS use `exposan.bsm1.create_system()` to build the BSM1 system
- NEVER construct the system manually (initial conditions will be wrong)
- EXPOsan loads correct initial conditions from internal Excel file,
  including X_BA (nitrifiers) which are CRITICAL for nitrification

## Simulation Parameters
- Minimum simulation time: **200 days** for steady-state convergence
- ODE method priority: **BDF first**, Radau as fallback
- For dynamic simulations, always use `state_reset_hook='reset_cache'`
- `steady_state=True` does NOT work in QSDsan 1.3.0 (scipy incompatibility)

## Units - CRITICAL
- `stream.F_vol` is in **m3/hr**, NOT m3/d. Multiply by 24 for daily flow:
  ```python
  q_m3_d = stream.F_vol * 24
  ```
- `S_ALK` is stored internally as **mg/L** (= mol HCO3/m3 * 12).
  Divide by 12 to get mol HCO3/m3:
  ```python
  alk_mol_m3 = get_conc(stream, 'S_ALK') / 12
  ```
- TSS must be calculated manually (not a stream property):
  ```python
  TSS = 0.75 * (X_I + X_S + X_BH + X_BA + X_P)  # mg SS/L
  ```

## ASM1 Nomenclature
- Use ASM1 names: `S_O`, `S_NH`, `S_NO`, `S_ND`
- NEVER use ASM2d names: `S_O2`, `S_NH4`, `S_NO3` (causes silent KeyError)

## Component Access
- Get concentration: `stream.conc[stream.components.index('S_NH')]`
- Direct mass flow: `stream.imass['S_NH']` (returns kg/hr)
- `stream.TSS` does NOT exist - calculate manually
- `stream.imass` has NO `.get()` method

## BSM1 Configuration (do not change without justification)
- 5 reactors: A1(1000m3), A2(1000m3), O1(1333m3), O2(1333m3), O3(1333m3)
- Clarifier: 1500m2 area, 4m height, 10 layers, feed layer 5 (0-based)
- Internal recirculation: 3Q (55338 m3/d) from O3 to A1
- External recirculation (RAS): 1Q (18446 m3/d) from C1 to A1
- Wastage (WAS): 385 m3/d
