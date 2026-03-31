# Run Simulation

Execute a BSM1/QSDsan simulation script and summarize results.

## Instructions

1. Identify the script to run:
   - If $ARGUMENTS is provided, use it as the script name
   - Otherwise, look for Python scripts matching `run_*.py` or `*_simulation.py` in the project root
   - If multiple scripts are found, list them and ask which one to run
2. Before running, verify the environment:
   - Check that Python 3.13+ is available
   - Check that QSDsan and EXPOsan are installed
3. Execute the script: `python <script_name>`
4. Monitor the output for:
   - Errors or exceptions (report immediately)
   - Simulation method used (BDF or Radau fallback)
   - Convergence time
5. Summarize results:
   - Number of PASS/FAIL validations
   - Any components outside +/-5% tolerance
   - Key effluent values (S_NH, S_NO, TSS, COD)
   - Compute time
6. If the simulation fails:
   - Check if it's a known issue (see CLAUDE.md section 16)
   - Suggest BDF -> Radau fallback if applicable
   - Check initial conditions (X_BA must be present)

$ARGUMENTS
