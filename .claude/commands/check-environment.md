# Check Environment

Verify that the Python/QSDsan environment is correctly configured for BSM1 simulation.

## Instructions

Run these checks and report results:

1. **Python version**: Run `python --version`. Need >= 3.13
2. **QSDsan version**: Run `pip show qsdsan`. Need 1.3.0
3. **EXPOsan version**: Run `pip show exposan`. Need 1.4.3
4. **pkg_resources patch** (required for Python 3.13):
   - Read `qsdsan/__init__.py` and check if it has the `try/except` block
     for `importlib.metadata` fallback (see CLAUDE.md section 4)
   - Same check for `exposan/__init__.py`
5. **Graphviz**: Check if `dot -V` works. Optional but needed for `sys.diagram()`
6. **Ruff**: Run `ruff --version`. Needed for code formatting
7. **Key dependencies**: Check numpy, pandas, scipy are installed

Report format:
- [OK] or [MISSING] or [WRONG VERSION] for each check
- For any issues, provide the fix command or instructions
- Reference CLAUDE.md section 4 for the pkg_resources patch

$ARGUMENTS
