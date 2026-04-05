# Testing Rules

## Framework
- **pytest** configurado en `pyproject.toml` (testpaths = ["tests"]).
- Ejecutar: `python -m pytest tests/ -v`
- Tests rapidos (sin simulacion): `python -m pytest tests/ -m "not slow"`
- Tests de tendencias (simulacion real): `python -m pytest tests/test_trends.py -v`
- Adicionalmente, **validacion IWA** por comparacion contra valores de referencia
  (Dr. Ulf Jeppsson, Lund University, 2008) hardcodeados en `app/config.py`.

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

## Suite de tests

| Fichero | Contenido | Velocidad |
|---------|-----------|-----------|
| `tests/test_api.py` | Tests de endpoints FastAPI (TestClient) | Rapido |
| `tests/test_engine.py` | Tests unitarios del motor (validate_value, do_to_kla, etc.) | Rapido |
| `tests/test_trends.py` | 16 tests de tendencias/sensibilidad (@slow) | ~90 seg |
