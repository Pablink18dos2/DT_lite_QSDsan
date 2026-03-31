# Testing Rules

## Framework
- No pytest or unittest framework. Validation is done by **comparison against
  IWA reference values** (Dr. Ulf Jeppsson, Lund University, 2008).
- Reference values are hardcoded in the simulation scripts.

## Steady-State Validation
- Tolerance: +/- 5% for all checks
- 13 ASM1 components + TSS = **14 total checks** that must PASS
- Key reference values (effluent):
  - S_NH: 1.733 mg N/L
  - S_NO: 10.415 mg N/L
  - TSS: 12.497 mg SS/L
  - SRT traditional: 7.32 days
  - SRT specific: 9.14 days

## Dynamic Validation (when available)
- Flow-weighted means over days 7-14 of dry weather simulation
- IWA effluent limits:
  - COD total < 100 mg COD/L
  - TN total < 18 mg N/L
  - TSS < 30 mg SS/L
  - BOD5 < 10 mg/L
  - S_NH > 4 mg/L is an **EXPECTED violation** in open-loop BSM1

## When to Run Validation
- After ANY change to simulation logic, kinetic parameters, or system configuration
- Run the full simulation (200 days) and verify 14/14 PASS
- Results must be saved to both CSV and TXT report files

## Results Files
- `resultados_bsm1_ss_componentes.csv` - Tabulated component data
- `RESULTADOS_VALIDACION_BSM1.txt` - Full validation report with PASS/FAIL
