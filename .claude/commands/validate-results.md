# Validate Results

Read and validate BSM1 simulation results against IWA reference values.

## Instructions

1. Locate the latest results files:
   - `resultados_bsm1_ss_componentes.csv` (tabulated data)
   - `RESULTADOS_VALIDACION_BSM1.txt` (full report)
2. Read both files and extract effluent concentrations
3. Compare each of the 13 ASM1 components + TSS against IWA reference (CLAUDE.md section 7):
   - S_I: 30.0, S_S: 0.889, X_I: 4.392, X_S: 0.188
   - X_BH: 9.782, X_BA: 0.573, X_P: 1.728
   - S_O: 0.491, S_NO: 10.415, S_NH: 1.733
   - S_ND: 0.688, X_ND: 0.013, S_ALK: 4.126 mol/m3
   - TSS: 12.497 mg/L
4. For each component, calculate % error and flag if > 5%
5. Check aggregate parameters:
   - COD total < 100 mg/L
   - TN total < 18 mg/L
   - TSS < 30 mg/L
   - BOD5 < 10 mg/L
6. Report in this format:
   - **Summary**: X/14 PASS
   - **Failures** (if any): component, obtained, reference, % error
   - **Aggregate checks**: all limits met?
   - **SRT**: traditional (ref 7.32 d) and specific (ref 9.14 d)

$ARGUMENTS
