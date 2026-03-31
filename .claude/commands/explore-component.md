# Explore ASM1 Component

Trace an ASM1 component through the BSM1 system and explain its behavior.

## Instructions

1. Parse the component name from $ARGUMENTS (e.g., S_NH, X_BH, S_NO, S_ALK)
2. Verify it is a valid ASM1 component:
   - Soluble: S_I, S_S, S_O, S_NO, S_NH, S_ND, S_ALK
   - Particulate: X_I, X_S, X_BH, X_BA, X_P, X_ND
3. Provide this information:
   - **What it is**: Full name, units, type (soluble/particulate)
   - **Influent value**: From CLAUDE.md section 6.4
   - **Effluent reference**: From CLAUDE.md section 7
   - **Biological processes**: Which of the 8 ASM1 processes produce or consume it
     (see CLAUDE.md section 9 for kinetic parameters)
   - **Reactor behavior**: What happens in anoxic (A1, A2) vs aerobic (O1-O3) zones
   - **Clarifier effect**: How sedimentation affects it (soluble passes through,
     particulate is separated by TSS fraction fr_SS_COD=0.75)
   - **Key formulas**: Any relevant calculation formulas from CLAUDE.md section 10
4. If the component is part of an aggregate variable (COD, TN, TSS, BOD5),
   explain which aggregate(s) it contributes to and how

$ARGUMENTS
