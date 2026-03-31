# Code Style Rules

## General
- Follow PEP 8, enforced by Ruff (config in `pyproject.toml`)
- Indentation: 4 spaces (no tabs)
- Max line length: 100 characters (relaxed from 79 for scientific formulas)
- Single quotes for strings (Ruff formatter setting)

## Naming Conventions
- Functions and variables: `snake_case`
- Constants: `UPPER_CASE` (e.g., `IWA_SS_REF`, `TOLERANCE`)
- Classes: `PascalCase`
- ASM1 component names are EXEMPT from naming rules: use standard notation
  (`S_I`, `S_S`, `X_BH`, `X_BA`, `S_NH`, `S_NO`, `S_ALK`, etc.)

## Imports
- Order: stdlib -> numpy/pandas/scipy -> qsdsan/exposan -> local modules
- Use `isort` via Ruff to enforce ordering
- Prefer explicit imports over wildcard (`from module import *`)

## Console Output
- **CRITICAL**: Use ASCII only in all print() output (Windows cp1252 encoding)
- Use `[PASS]`, `[FAIL]`, `[OK]`, `[ERROR]` instead of Unicode symbols
- Use `-->`, `---`, `===` instead of arrows or decorative characters

## Numeric Constants
- Always include units in a comment next to the constant:
  ```python
  KLa = 240       # 1/d - volumetric oxygen transfer coefficient
  V_max = 1333    # m3 - reactor volume
  Q_inf = 18446   # m3/d - influent flow rate
  ```

## Code Quality
- Run `ruff check .` before committing
- Run `ruff format --check .` to verify formatting
- Auto-fix: `ruff check --fix .` and `ruff format .`
