"""BSM1 simulation engine - core logic extracted from run_bsm1_simulation.py."""

import datetime
import threading
import time
import warnings

import numpy as np
from scipy.integrate import solve_ivp

from .config import (
    BSM1_INF_COMPONENTS,
    COD_DEFAULT,
    COMPONENT_UNITS,
    IWA_SS_REF,
    IWA_SS_SRT_SPEC,
    IWA_SS_SRT_TRAD,
    IWA_SS_TSS,
    OUR_REF_O1,
    OUR_REF_O2,
    OUR_REF_O3,
    PI_KLA_MAX,
    PI_KLA_MIN,
    PI_KP,
    PI_PHASE2_DAYS,
    PI_TI,
    SRT_DEFAULT,
    TKN_DEFAULT,
    TOLERANCE,
    WAS_DEFAULT,
)
from .models import ComponentResult, PlantParameters, PreSimulationResponse, SimulationResult

warnings.filterwarnings('ignore')

# QSDsan uses global state (flowsheet, thermo) - serialize simulation calls
_simulation_lock = threading.Lock()


# ============================================================================
# Helper functions (from run_bsm1_simulation.py lines 95-170)
# ============================================================================


def get_conc(stream, comp_id):
    """Get component concentration in mg/L."""
    try:
        if stream.F_vol > 0:
            return stream.imass[comp_id] / stream.F_vol * 1e3
        return 0.0
    except (KeyError, AttributeError, ZeroDivisionError):
        return np.nan


def get_alk(stream):
    """Get alkalinity in mol HCO3/m3 (S_ALK stored as mg/L with factor 12)."""
    try:
        conc = get_conc(stream, 'S_ALK')
        return conc / 12.0
    except Exception:
        return np.nan


def calc_tss(stream, fr_SS_COD=0.75):
    """Calculate TSS as 0.75 * sum(X_i) [mg COD/L -> mg SS/L]."""
    try:
        if stream.F_vol <= 0:
            return 0.0
        x_sum = sum(stream.imass[cmp.ID] for cmp in stream.components if cmp.ID.startswith('X_'))
        return x_sum / stream.F_vol * 1e3 * fr_SS_COD
    except Exception:
        return 0.0


def calc_cod_total(stream):
    """Calculate total COD from stream."""
    try:
        return stream.COD
    except Exception:
        return np.nan


def calc_tn(stream):
    """Calculate total nitrogen from stream."""
    try:
        return stream.TN
    except Exception:
        return np.nan


def calc_bod5(stream):
    """Estimate BOD5 in mg/L.

    Formula: f_sol*(S_S + X_S) + f_bio*(1-f_P)*(X_BH + X_BA)

    - f_sol = 0.65: standard BOD5/COD ratio for readily/slowly biodegradable substrate.
    - f_bio = 0.15: fraction of active biomass COD that exerts BOD in 5 days via
      endogenous decay; significantly lower than substrate because live cells are not
      immediately consumed (Henze et al. 2000; Jeppsson BSM1 evaluation 2008).
    - f_P = 0.08: inert fraction from biomass decay (ASM1 default).

    Validated against IWA BSM1 SS reference: ~2.5 mg/L at default conditions.
    """
    try:
        ss = get_conc(stream, 'S_S')
        xs = get_conc(stream, 'X_S')
        xbh = get_conc(stream, 'X_BH')
        xba = get_conc(stream, 'X_BA')
        f_P = 0.08
        f_sol = 0.65
        f_bio = 0.15
        return f_sol * (ss + xs) + f_bio * (1 - f_P) * (xbh + xba)
    except Exception:
        return np.nan


def validate_value(obtained, reference, tolerance=TOLERANCE):
    """Check if obtained value is within tolerance of reference."""
    if reference == 0:
        return abs(obtained) < 0.01
    error = abs(obtained - reference) / abs(reference)
    return error <= tolerance


def error_pct(obtained, reference):
    """Calculate error percentage."""
    if reference == 0:
        return 0.0
    return ((obtained - reference) / reference) * 100


def validate_components(values, tolerance=TOLERANCE):
    """Validate a dict of component values against IWA reference.

    Args:
        values: dict mapping component IDs to obtained values.
        tolerance: acceptable relative error (default 5%).

    Returns:
        List of ComponentResult for each matched component.
    """
    results = []
    # Merge SS refs + TSS for lookup
    all_refs = {**IWA_SS_REF, 'TSS': IWA_SS_TSS}
    for comp_id, obtained in values.items():
        if comp_id not in all_refs or obtained is None:
            continue
        ref = all_refs[comp_id]
        err = error_pct(obtained, ref)
        passed = validate_value(obtained, ref, tolerance)
        unit = COMPONENT_UNITS.get(comp_id, 'mg/L')
        results.append(
            ComponentResult(
                component=comp_id,
                obtained=round(obtained, 6),
                reference=ref,
                error_pct=round(err, 4),
                passed=passed,
                unit=unit,
            )
        )
    return results


# ============================================================================
# Influent decomposition and plant parameter functions
# ============================================================================


def decompose_influent(COD_total: float, TKN: float, TSS_inf: float) -> dict:
    """Convert aggregate influent values to ASM1 component concentrations.

    Scales each component proportionally from BSM1 defaults.
    TSS_inf is used for cross-validation warning only.

    Returns:
        dict with 'concentrations' and 'units' keys, ready for create_system(inf_kwargs=...).
    """
    cod_ratio = COD_total / COD_DEFAULT
    tkn_ratio = TKN / TKN_DEFAULT

    # COD components scale with COD ratio
    concentrations = {
        'S_I': BSM1_INF_COMPONENTS['S_I'] * cod_ratio,
        'S_S': BSM1_INF_COMPONENTS['S_S'] * cod_ratio,
        'X_I': BSM1_INF_COMPONENTS['X_I'] * cod_ratio,
        'X_S': BSM1_INF_COMPONENTS['X_S'] * cod_ratio,
        'X_BH': BSM1_INF_COMPONENTS['X_BH'] * cod_ratio,
        # TKN components scale with TKN ratio
        'S_NH': BSM1_INF_COMPONENTS['S_NH'] * tkn_ratio,
        'S_ND': BSM1_INF_COMPONENTS['S_ND'] * tkn_ratio,
        'X_ND': BSM1_INF_COMPONENTS['X_ND'] * tkn_ratio,
        # Alkalinity stays constant (buffering capacity)
        'S_ALK': BSM1_INF_COMPONENTS['S_ALK'],
    }
    return {'concentrations': concentrations, 'units': ('m3/d', 'mg/L')}


def srt_to_was(SRT_target: float) -> float:
    """Approximate WAS flow from target SRT using BSM1 reference ratio.

    WAS_new = WAS_default * (SRT_default / SRT_target)
    """
    return WAS_DEFAULT * (SRT_DEFAULT / SRT_target)


def do_to_kla(DO_target: float, DOsat: float, OUR_ref: float) -> float:
    """Convert DO setpoint (mg O2/L) to KLa (1/d) using reference OUR.

    At steady state: KLa * (DOsat - DO) = OUR
    Therefore: KLa = OUR / (DOsat - DO)

    The OUR_ref is back-calculated from BSM1 reference conditions for each reactor.

    Args:
        DO_target: desired dissolved oxygen in mg O2/L.
        DOsat: oxygen saturation concentration in mg O2/L.
        OUR_ref: reference oxygen uptake rate in mg O2/(L*d).

    Returns:
        KLa in 1/d.
    """
    if DO_target >= DOsat:
        return 0.0
    return OUR_ref / (DOsat - DO_target)


def build_system_kwargs(plant: PlantParameters) -> dict:
    """Build create_system() kwargs and module patches from PlantParameters.

    Returns:
        dict with keys: inf_kwargs, settler_kwargs, aeration_processes, module_patches, Q_WAS_effective
    """
    from qsdsan import processes as pc

    # Determine effective WAS
    if plant.sludge_control == 'SRT' and plant.SRT_target is not None:
        q_was = srt_to_was(plant.SRT_target)
    else:
        q_was = plant.Q_WAS or WAS_DEFAULT

    # Influent decomposition
    inf_kwargs = decompose_influent(plant.COD_total, plant.TKN, plant.TSS_inf)

    # KLa per reactor: direct (KLa mode) or back-calculated from DO setpoint (DO mode)
    if plant.aeration_control == 'KLa':
        kla_o1 = float(plant.KLa_O1 if plant.KLa_O1 is not None else 0.0)
        kla_o2 = float(plant.KLa_O2 if plant.KLa_O2 is not None else 0.0)
        kla_o3 = float(plant.KLa_O3 if plant.KLa_O3 is not None else 0.0)
    else:
        kla_o1 = do_to_kla(plant.DO_O1, plant.DOsat, OUR_REF_O1)
        kla_o2 = do_to_kla(plant.DO_O2, plant.DOsat, OUR_REF_O2)
        kla_o3 = do_to_kla(plant.DO_O3, plant.DOsat, OUR_REF_O3)

    # Settler kwargs
    settler_kwargs = {
        'underflow': plant.Q_RAS,
        'wastage': q_was,
        'surface_area': plant.Clarifier_area,
        'height': plant.Clarifier_height,
        'N_layer': 10,  # fixed BSM1
        'feed_layer': 5,  # fixed BSM1
        'X_threshold': 3000,  # fixed BSM1
        'v_max': 474,
        'v_max_practical': 250,
        'rh': 0.000576,
        'rp': 0.00286,
        'fns': 0.00228,
    }

    # Aeration processes with calculated KLa.
    # QSDsan bug workaround: DiffusedAeration(KLa=0) triggers a Python 'or' falsy
    # check that calls _calc_KLa() before _KLa is set, causing AttributeError.
    # Clamping to _MIN_KLA (1e-4 1/d) is effectively anoxic (transfer < 0.001 mg O2/L/d)
    # while avoiding the internal recursion.
    _MIN_KLA = 1e-4
    DO_ID = 'S_O'
    aer1 = pc.DiffusedAeration(
        'aer_o1', DO_ID, KLa=max(kla_o1, _MIN_KLA), DOsat=plant.DOsat, V=plant.V_aerobic
    )
    aer2 = pc.DiffusedAeration(
        'aer_o2', DO_ID, KLa=max(kla_o2, _MIN_KLA), DOsat=plant.DOsat, V=plant.V_aerobic
    )
    aer3 = pc.DiffusedAeration(
        'aer_o3', DO_ID, KLa=max(kla_o3, _MIN_KLA), DOsat=plant.DOsat, V=plant.V_aerobic
    )

    # Module-level patches needed before create_system()
    module_patches = {
        'Q': plant.Q,
        'V_an': plant.V_anoxic,
        'V_ae': plant.V_aerobic,
        'Q_ras': plant.Q_RAS,
        'Q_intr': plant.Q_intr,
    }

    return {
        'inf_kwargs': inf_kwargs,
        'settler_kwargs': settler_kwargs,
        'aeration_processes': (aer1, aer2, aer3),
        'module_patches': module_patches,
        'Q_WAS_effective': q_was,
    }


def pre_check(plant: PlantParameters) -> PreSimulationResponse:
    """Validate plant parameters and return warnings before simulation."""
    warnings_list = []

    # Calculate effective WAS
    q_was_calc = None
    srt_est = None
    if plant.sludge_control == 'SRT' and plant.SRT_target is not None:
        q_was_calc = round(srt_to_was(plant.SRT_target), 1)
        srt_est = plant.SRT_target
    else:
        srt_est = round(SRT_DEFAULT * (WAS_DEFAULT / (plant.Q_WAS or WAS_DEFAULT)), 2)

    # HRT check
    v_total = 2 * plant.V_anoxic + 3 * plant.V_aerobic
    hrt_hours = v_total / plant.Q * 24
    if hrt_hours < 1.2:
        warnings_list.append(f'HRT muy bajo ({hrt_hours:.1f} h). Puede no converger.')

    # RAS ratio
    ras_ratio = plant.Q_RAS / plant.Q if plant.Q > 0 else 0
    if ras_ratio < 0.25 or ras_ratio > 3.0:
        warnings_list.append(f'Ratio RAS/Q inusual ({ras_ratio:.2f}). Rango tipico: 0.25-3.0')

    # Internal recirculation ratio
    intr_ratio = plant.Q_intr / plant.Q if plant.Q > 0 else 0
    if intr_ratio > 5:
        warnings_list.append(
            f'Recirculacion interna alta ({intr_ratio:.1f}x Q). Optimo tipico: 2-4x Q. '
            'Por encima de 5x Q el TRH anoxico se reduce y la desnitrificacion empeora.'
        )

    # COD/TKN ratio
    if plant.TKN > 0:
        cod_tkn = plant.COD_total / plant.TKN
        if cod_tkn < 3 or cod_tkn > 15:
            warnings_list.append(
                f'Ratio COD/TKN fuera del rango tipico ({cod_tkn:.1f}). Rango: 3-15'
            )

    # Clarifier hydraulic loading (m/h)
    q_total_to_clarifier = plant.Q + plant.Q_RAS  # m3/d
    hydraulic_load = q_total_to_clarifier / (plant.Clarifier_area * 24)  # m3/m2/h = m/h
    if hydraulic_load > 2.0:
        warnings_list.append(
            f'Carga hidraulica del decantador elevada ({hydraulic_load:.2f} m/h). Limite: 2.0 m/h'
        )

    # Aeration mode: compute KLa values and apply DO-mode-specific warnings
    if plant.aeration_control == 'KLa':
        kla_o1 = float(plant.KLa_O1 if plant.KLa_O1 is not None else 0.0)
        kla_o2 = float(plant.KLa_O2 if plant.KLa_O2 is not None else 0.0)
        kla_o3 = float(plant.KLa_O3 if plant.KLa_O3 is not None else 0.0)
        # Warn when KLa_O3 substantially exceeds BSM1 reference (84 1/d),
        # as higher KLa raises DO in O3, which then flows to A1/A2 via internal recirculation.
        KLA_O3_REF = 84.0
        if kla_o3 > KLA_O3_REF * 1.5 and intr_ratio > 2.0:
            warnings_list.append(
                f'KLa_O3 alto ({kla_o3:.0f} 1/d, ref={KLA_O3_REF:.0f}) con Q_intr={intr_ratio:.1f}x Q: '
                'mayor DO en O3 se arrastra al reactor anoxic via recirculacion interna.'
            )
    else:
        # DO too close to DOsat (means almost no aeration / KLa near zero)
        if plant.DOsat - 0.5 <= plant.DO_O1 and plant.DOsat - 0.5 <= plant.DO_O2:
            warnings_list.append(
                f'OD consigna cercano a saturacion ({plant.DOsat} mg/L). '
                'KLa resultante sera muy bajo, sin aireacion efectiva.'
            )

        kla_o1 = do_to_kla(plant.DO_O1, plant.DOsat, OUR_REF_O1)
        kla_o2 = do_to_kla(plant.DO_O2, plant.DOsat, OUR_REF_O2)
        kla_o3 = do_to_kla(plant.DO_O3, plant.DOsat, OUR_REF_O3)
        if kla_o1 > 500 or kla_o2 > 500 or kla_o3 > 500:
            warnings_list.append(
                f'KLa calculado muy alto (O1={kla_o1:.0f}, O2={kla_o2:.0f}, O3={kla_o3:.0f} 1/d). '
                'OD consigna puede ser demasiado bajo para el OUR estimado.'
            )

        # DO_O3 contamination of anoxic zone via internal recirculation
        if plant.DO_O3 > 1.0 and intr_ratio > 2.0:
            warnings_list.append(
                f'DO_O3 alto ({plant.DO_O3} mg/L) con Q_intr={intr_ratio:.1f}x Q: '
                'el O2 arrastrado por recirculacion interna puede inhibir la desnitrificacion en A1/A2. '
                'Mantener DO_O3 < 1.0 mg/L para minimizar contaminacion anoxica.'
            )

    # COD overload: risk of DO starvation for nitrifiers
    # Study D: with default KLa, S_O drops below K_OA=0.4 at COD > ~450 mg/L.
    # Threshold based on empirical simulation: COD > 1.2x default (457 mg/L) is risk zone.
    if plant.COD_total > 450:
        cod_ratio_warn = plant.COD_total / COD_DEFAULT
        warnings_list.append(
            f'COD influente alto ({plant.COD_total:.0f} mg/L, {cod_ratio_warn:.1f}x defecto): '
            'la alta demanda de O2 heterotrofa puede reducir el DO real por debajo de '
            'K_OA=0.4 mg/L, inhibiendo nitrificadores aunque el KLa de consigna sea correcto. '
            'Considerar aumentar DO_O1/DO_O2 para compensar.'
        )

    # Temperature + SRT interaction
    # Study E: at T=15C, Q_WAS=385 (SRT~9.5d) fails nitrification (S_NH=7.6 mg/L).
    # At T=15C, need SRT > ~15d (Q_WAS < ~250 m3/d) to maintain S_NH < 4 mg/L.
    if plant.Temperature <= 16:
        srt_for_temp = srt_est or (SRT_DEFAULT * (WAS_DEFAULT / (plant.Q_WAS or WAS_DEFAULT)))
        srt_needed = 15 + (18 - plant.Temperature) * 0.5  # empirical from Study E
        if srt_for_temp < srt_needed:
            warnings_list.append(
                f'Temperatura baja ({plant.Temperature} C) con SRT estimado ({srt_for_temp:.1f} d) '
                f'insuficiente. A {plant.Temperature} C se recomienda SRT >= {srt_needed:.0f} d '
                '(reducir Q_WAS) para mantener nitrificacion estable.'
            )

    # TSS consistency check
    cod_ratio = plant.COD_total / COD_DEFAULT
    x_sum = (51.2 + 202.32 + 28.17) * cod_ratio  # X_I + X_S + X_BH scaled
    tss_from_cod = 0.75 * x_sum
    if plant.TSS_inf > 0 and abs(tss_from_cod - plant.TSS_inf) / plant.TSS_inf > 0.20:
        warnings_list.append(
            f'TSS influente ({plant.TSS_inf:.0f}) inconsistente con COD '
            f'(TSS estimado: {tss_from_cod:.0f}). Diferencia > 20%.'
        )

    return PreSimulationResponse(
        Q_WAS_calculated=q_was_calc,
        SRT_estimated=srt_est,
        KLa_O1=round(kla_o1, 1),
        KLa_O2=round(kla_o2, 1),
        KLa_O3=round(kla_o3, 1),
        warnings=warnings_list,
        valid=True,
    )


# ============================================================================
# PI DO controller helpers
# ============================================================================


def _run_pi_phase(sys_bsm1, plant, method: str) -> dict:
    """Run PI DO controller phase to set S_O setpoints in aerobic reactors.

    Extends the ODE system with 3 integral states (one per aerobic reactor O1,
    O2, O3). The PI law adjusts each reactor's KLa dynamically so that the
    actual dissolved oxygen converges to the user-specified setpoint.

    Two-phase approach:
    - Phase 1 (200 days, already run by caller): standard simulation that
      reaches biological steady state with reference KLa values.
    - Phase 2 (PI_PHASE2_DAYS, run here): PI-ODE from Phase 1 steady state,
      converging to the target DO setpoint with a new KLa equilibrium.

    The integral warm-start (I_0 = KLa_ref * Ti / Kp) ensures the controller
    begins close to the reference operating point, preventing windup.

    Args:
        sys_bsm1: fully simulated BSM1 system (Phase 1 already completed).
        plant: PlantParameters with DO_O1, DO_O2, DO_O3 setpoints.
        method: ODE solver ('BDF' or 'Radau').

    Modifies sys_bsm1 in-place: updates _state and all streams to PI result.
    """
    # --- Build index map for S_O in the global state vector ---
    # ASM1 component order: S_I, S_S, X_I, X_S, X_BH, X_BA, X_P, S_O, ...
    # S_O is always at local index 7 in the 14-element CSTR state (13 cmps + Q).
    S_O_LOCAL = 7
    reactor_ids = ['O1', 'O2', 'O3']
    idx_SO = {r: sys_bsm1._state_idx[r][0] + S_O_LOCAL for r in reactor_ids}

    # Mutable aeration objects — KLa setter propagates to compiled rate function
    aer_map = {}
    for u in sys_bsm1.units:
        if u.ID in reactor_ids:
            aer = getattr(u, 'aeration', None)
            if aer is not None:
                aer_map[u.ID] = aer

    DO_SP = {'O1': plant.DO_O1, 'O2': plant.DO_O2, 'O3': plant.DO_O3}
    kla_max = PI_KLA_MAX.copy()
    n_orig = len(sys_bsm1._state)

    def _pi_ode(t, y_ext):  # noqa: WPS430 - nested closure needed for state capture
        y_orig = y_ext[:n_orig]
        I = y_ext[n_orig:]
        dI = np.zeros(3)
        for k, r_id in enumerate(reactor_ids):
            S_O = y_orig[idx_SO[r_id]]
            e = DO_SP[r_id] - S_O
            u = PI_KP * e + (PI_KP / PI_TI) * I[k]
            KLa_new = float(np.clip(u, PI_KLA_MIN, kla_max[r_id]))
            aer_map[r_id].KLa = KLa_new
            # Anti-windup: freeze integral when saturated and error drives deeper
            saturated_low = u <= PI_KLA_MIN and e < 0
            saturated_high = u >= kla_max[r_id] and e > 0
            if not saturated_low and not saturated_high:
                dI[k] = e
        dy_orig = sys_bsm1.DAE(t, y_orig)
        return np.concatenate([dy_orig, dI])

    # Warm-start integrals at reference KLa so controller begins near setpoint:
    # At SS with reference KLa and e≈0: u = (Kp/Ti)*I => I_0 = KLa_ref * Ti / Kp
    kla_ref = {'O1': 240.0, 'O2': 240.0, 'O3': 84.0}
    I_warm = [kla_ref[r] * PI_TI / PI_KP for r in reactor_ids]

    y0_ext = np.append(sys_bsm1._state.copy(), I_warm)

    sol = solve_ivp(
        _pi_ode,
        (0, PI_PHASE2_DAYS),
        y0_ext,
        method=method,
        rtol=1e-4,
        atol=1e-6,
    )
    if sol.status != 0:
        raise RuntimeError(f'PI phase solver failed: {sol.message}')

    # Propagate final state to unit internals and all streams
    y_final = sol.y[:n_orig, -1]
    sys_bsm1._update_state(y_final)
    sys_bsm1._write_state()

    # Compute and return final KLa values (for reporting in aggregates)
    I_final = sol.y[n_orig:, -1]
    pi_kla_final = {}
    for k, r_id in enumerate(reactor_ids):
        S_O_r = y_final[idx_SO[r_id]]
        e = DO_SP[r_id] - S_O_r
        u = PI_KP * e + (PI_KP / PI_TI) * I_final[k]
        pi_kla_final[r_id] = round(float(np.clip(u, PI_KLA_MIN, kla_max[r_id])), 1)
    return pi_kla_final


def extract_reactor_biomass(sys_bsm1) -> dict:
    """Extract X_BH and X_BA concentrations (mg COD/L) from each reactor outlet.

    Returns dict with keys like 'reactor_O1_X_BH', 'reactor_A1_X_BA', etc.
    """
    units_map = {u.ID: u for u in sys_bsm1.units}
    result = {}
    for r_id in ['A1', 'A2', 'O1', 'O2', 'O3']:
        unit = units_map.get(r_id)
        if unit is None:
            continue
        try:
            outlet = unit.outs[0]
            result[f'reactor_{r_id}_X_BH'] = round(get_conc(outlet, 'X_BH'), 3)
            result[f'reactor_{r_id}_X_BA'] = round(get_conc(outlet, 'X_BA'), 3)
        except Exception:
            result[f'reactor_{r_id}_X_BH'] = float('nan')
            result[f'reactor_{r_id}_X_BA'] = float('nan')
    return result


def _removal_pct(inf_val: float | None, eff_val: float | None) -> float | None:
    """Calculate removal percentage: (inf - eff) / inf * 100."""
    if inf_val and inf_val > 0 and eff_val is not None and not np.isnan(eff_val):
        return round((inf_val - eff_val) / inf_val * 100, 1)
    return None


# ============================================================================
# Main simulation function
# ============================================================================


def run_steady_state_simulation(
    t_days: int = 200,
    method: str = 'BDF',
    tolerance: float = TOLERANCE,
    plant: PlantParameters | None = None,
) -> SimulationResult:
    """Run a full BSM1 steady-state simulation and validate against IWA.

    Args:
        t_days: Simulation duration in days (min 50 for convergence).
        method: ODE solver - 'BDF' (default) or 'Radau' as fallback.
        tolerance: Validation tolerance as fraction (default 0.05 = 5%).
        plant: Custom plant parameters. None uses BSM1 defaults.

    Returns:
        SimulationResult with all 14 component validations and aggregates.

    Raises:
        RuntimeError: If both BDF and Radau solvers fail.
    """
    with _simulation_lock:
        t_start = time.time()

        # Import inside lock to avoid global state conflicts
        import exposan.bsm1.system as bsm1_sys
        from exposan import bsm1
        from exposan.bsm1.system import biomass_IDs
        from qsdsan.utils import get_SRT

        # Prepare create_system kwargs based on plant parameters
        create_kwargs = {
            'flowsheet': None,
            'suspended_growth_model': 'ASM1',
            'reactor_model': 'CSTR',
            'inf_kwargs': {},
            'asm_kwargs': {},
            'settler_kwargs': {},
            'init_conds': None,
            'aeration_processes': (),
        }

        saved_module_vars = None
        saved_asm1_params = None
        _asm1_sgm = None
        sys_kwargs = None
        if plant is not None:
            # DiffusedAeration needs ASM1 thermo at construction time.
            # create_system() normally sets this, but since we must pass
            # DiffusedAeration objects INTO create_system(), thermo must be
            # initialized first. If a prior simulation already ran, it is set.
            import thermosteam as tmo

            import qsdsan as qs
            import qsdsan.processes as pc

            try:
                _ = tmo.settings.thermo
            except RuntimeError:
                qs.set_thermo(pc.create_asm1_cmps())

            sys_kwargs = build_system_kwargs(plant)
            create_kwargs['inf_kwargs'] = sys_kwargs['inf_kwargs']
            create_kwargs['settler_kwargs'] = sys_kwargs['settler_kwargs']
            create_kwargs['aeration_processes'] = sys_kwargs['aeration_processes']

            # Save and monkey-patch module-level variables
            patches = sys_kwargs['module_patches']
            saved_module_vars = {k: getattr(bsm1_sys, k) for k in patches}
            for k, v in patches.items():
                setattr(bsm1_sys, k, v)

        try:
            # Create a fresh BSM1 system
            sys_bsm1 = bsm1.create_system(**create_kwargs)

            # Patch temperature: influent stream + ASM1 kinetics (Arrhenius theta=1.07)
            if plant is not None and plant.Temperature != 20:
                sys_bsm1.flowsheet.stream.wastewater.T = 273.15 + plant.Temperature

                # Apply Arrhenius temperature correction to ASM1 kinetic rates.
                # Rate parameters scale with theta^(T-20), theta=1.07 (BSM1 standard).
                # Half-saturation constants (K_*) assumed temperature-independent.
                for unit in sys_bsm1.units:
                    sgm = getattr(unit, 'suspended_growth_model', None)
                    if sgm is not None:
                        _asm1_sgm = sgm
                        break
                if _asm1_sgm is not None:
                    theta = 1.07
                    f = theta ** (plant.Temperature - 20)
                    _rate_params = ('mu_H', 'mu_A', 'b_H', 'b_A', 'k_h', 'k_a')
                    saved_asm1_params = {
                        p: _asm1_sgm.parameters[p]
                        for p in _rate_params
                        if p in _asm1_sgm.parameters
                    }
                    for p, v in saved_asm1_params.items():
                        _asm1_sgm.parameters[p] = v * f

            t_eval = np.arange(0, t_days + 1, 1.0)
            method_used = method

            # Try primary method, fallback to alternative
            try:
                sys_bsm1.simulate(
                    state_reset_hook='reset_cache',
                    t_span=(0, t_days),
                    t_eval=t_eval,
                    method=method,
                    rtol=1e-4,
                    atol=1e-6,
                )
            except Exception:
                fallback = 'Radau' if method == 'BDF' else 'BDF'
                try:
                    sys_bsm1.simulate(
                        state_reset_hook='reset_cache',
                        t_span=(0, t_days),
                        t_eval=t_eval,
                        method=fallback,
                        rtol=1e-4,
                        atol=1e-6,
                    )
                    method_used = fallback
                except Exception as e:
                    raise RuntimeError(f'Both {method} and {fallback} solvers failed: {e}') from e

            # Phase 2: PI DO controller — only in DO mode.
            # In KLa mode the user-specified KLa is applied directly in Phase 1;
            # no PI phase is needed.
            pi_kla = {}
            if plant is not None and plant.aeration_control == 'DO':
                pi_kla = _run_pi_phase(sys_bsm1, plant, method_used)

            compute_time = time.time() - t_start

            # Extract influent stream for removal efficiency calculation
            influent = sys_bsm1.flowsheet.stream.wastewater
            inf_cod = calc_cod_total(influent)
            inf_tn = calc_tn(influent)
            inf_nh4 = get_conc(influent, 'S_NH')
            inf_tss = calc_tss(influent, fr_SS_COD=0.75)

            # Extract effluent stream
            effluent = sys_bsm1.flowsheet.stream.effluent

            # Extract 13 ASM1 components.
            # Clip to 0: ODE solvers can produce tiny negative values due to numerical
            # overshoot (e.g. X_BA=-1e-9) in extreme scenarios; these are non-physical.
            ss_values = {}
            for comp_id in IWA_SS_REF:
                if comp_id == 'S_ALK':
                    ss_values[comp_id] = get_alk(effluent)
                else:
                    raw = get_conc(effluent, comp_id)
                    ss_values[comp_id] = max(0.0, raw) if not np.isnan(raw) else None

            # TSS (calculated manually)
            ss_values['TSS'] = calc_tss(effluent, fr_SS_COD=0.75)

            # Validate all 14 components
            components = validate_components(ss_values, tolerance)
            pass_count = sum(1 for c in components if c.passed)

            # Aggregate parameters
            ss_cod = calc_cod_total(effluent)
            ss_tn = calc_tn(effluent)
            ss_bod5 = calc_bod5(effluent)
            ss_q_eff = effluent.F_vol * 24  # m3/hr -> m3/d

            try:
                ss_srt = get_SRT(sys_bsm1, biomass_IDs=biomass_IDs['asm1'])
            except Exception:
                ss_srt = float('nan')

            aggregates = {
                'COD_total': round(ss_cod, 3) if not np.isnan(ss_cod) else None,
                'TN_total': round(ss_tn, 3) if not np.isnan(ss_tn) else None,
                'BOD5': round(ss_bod5, 3) if not np.isnan(ss_bod5) else None,
                'TSS': round(ss_values['TSS'], 3),
                'Q_effluent_m3d': round(ss_q_eff, 1),
                'SRT_specific_days': round(ss_srt, 2) if not np.isnan(ss_srt) else None,
                'SRT_trad_ref': IWA_SS_SRT_TRAD,
                'SRT_spec_ref': IWA_SS_SRT_SPEC,
            }

            # --- Removal efficiencies (influent vs effluent) ---
            eff_nh4 = get_conc(effluent, 'S_NH')
            aggregates['COD_inf'] = round(inf_cod, 3) if not np.isnan(inf_cod) else None
            aggregates['TN_inf'] = round(inf_tn, 3) if not np.isnan(inf_tn) else None
            aggregates['NH4_inf'] = round(inf_nh4, 3) if not np.isnan(inf_nh4) else None
            aggregates['TSS_inf_calc'] = round(inf_tss, 3)
            inf_bod5 = calc_bod5(influent)
            aggregates['removal_COD_pct'] = _removal_pct(inf_cod, ss_cod)
            aggregates['removal_TN_pct'] = _removal_pct(inf_tn, ss_tn)
            aggregates['removal_NH4_pct'] = _removal_pct(inf_nh4, eff_nh4)
            aggregates['removal_TSS_pct'] = _removal_pct(inf_tss, ss_values['TSS'])
            aggregates['removal_BOD5_pct'] = _removal_pct(inf_bod5, ss_bod5)

            # --- Biomass concentrations per reactor ---
            aggregates.update(extract_reactor_biomass(sys_bsm1))

            # Echo back all numeric plant parameters applied, plus computed KLa values.
            # Iterating model_dump() is systematic: new fields are echoed automatically.
            if plant is not None and sys_kwargs is not None:
                for _field, _val in plant.model_dump().items():
                    if isinstance(_val, (int, float)):
                        aggregates[f'_param_{_field}'] = float(_val)
                # Override Q_WAS with effective value (may be computed from SRT_target)
                aggregates['_param_Q_WAS'] = round(sys_kwargs['Q_WAS_effective'], 1)
                # KLa applied in Phase 1 (direct in KLa mode; back-calc from DO in DO mode)
                if plant.aeration_control == 'KLa':
                    aggregates['_param_KLa_O1'] = round(plant.KLa_O1 or 0.0, 1)
                    aggregates['_param_KLa_O2'] = round(plant.KLa_O2 or 0.0, 1)
                    aggregates['_param_KLa_O3'] = round(plant.KLa_O3 or 0.0, 1)
                else:
                    aggregates['_param_KLa_O1'] = round(
                        do_to_kla(plant.DO_O1, plant.DOsat, OUR_REF_O1), 1
                    )
                    aggregates['_param_KLa_O2'] = round(
                        do_to_kla(plant.DO_O2, plant.DOsat, OUR_REF_O2), 1
                    )
                    aggregates['_param_KLa_O3'] = round(
                        do_to_kla(plant.DO_O3, plant.DOsat, OUR_REF_O3), 1
                    )
                    # KLa values converged by the PI controller (Phase 2 result, DO mode only)
                    aggregates['PI_KLa_O1'] = pi_kla.get('O1')
                    aggregates['PI_KLa_O2'] = pi_kla.get('O2')
                    aggregates['PI_KLa_O3'] = pi_kla.get('O3')

            return SimulationResult(
                timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
                method_used=method_used,
                compute_time_seconds=round(compute_time, 2),
                components=components,
                pass_count=pass_count,
                total_count=len(components),
                all_passed=(pass_count == len(components)),
                aggregates=aggregates,
            )
        finally:
            # Restore original module-level variables
            if saved_module_vars is not None:
                for k, v in saved_module_vars.items():
                    setattr(bsm1_sys, k, v)
            # Restore ASM1 kinetic parameters modified for temperature correction
            if saved_asm1_params is not None and _asm1_sgm is not None:
                for p, v in saved_asm1_params.items():
                    _asm1_sgm.parameters[p] = v
