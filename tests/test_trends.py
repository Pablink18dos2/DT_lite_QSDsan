"""Trend validation tests for BSM1 simulation engine.

These tests verify that the model responds qualitatively correctly to
parameter changes. Each test runs two simulations with different values
of one parameter and checks that the output variable changes in the
expected direction according to ASM1 process theory.

Validation is ordinal/relational, NOT absolute. The goal is to detect
implementation errors that point-validation against IWA references cannot
catch (e.g. temperature patch not applied, KLa not recalculated, etc.).

All tests are marked @pytest.mark.slow (real simulations, ~6-10 s each).
Run with: python -m pytest tests/test_trends.py -v
"""

import pytest

from app.engine import run_steady_state_simulation
from app.models import PlantParameters

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get(result, component):
    """Return simulated concentration for a named ASM1 component."""
    return next(c.obtained for c in result.components if c.component == component)


def _agg(result, key):
    """Return an aggregate value (COD_total, TN_total, TSS, ...) from result."""
    return result.aggregates[key]


# ---------------------------------------------------------------------------
# Test 1: SRT effect on nitrification
# ---------------------------------------------------------------------------


class TestTrendSRT:
    """SRT is the most critical design parameter for nitrification.

    Autotrophs (X_BA) have mu_A = 0.5 1/d. At low SRT they are washed out
    before they can reproduce; at high SRT they accumulate and nitrify well.
    """

    @pytest.mark.slow
    def test_low_srt_increases_ammonia(self):
        """Low SRT (short sludge age) -> autotrophs washed out -> S_NH rises.

        BSM1 default: Q_WAS = 385 m3/d -> SRT ~9.1 days.
        Low SRT: Q_WAS = 855 m3/d -> SRT ~4.5 days (washout risk for X_BA).
        High SRT: Q_WAS = 192 m3/d -> SRT ~18.3 days (robust nitrification).
        """
        plant_low_srt = PlantParameters(Q_WAS=855)  # ~4.5 d SRT
        plant_high_srt = PlantParameters(Q_WAS=192)  # ~18.3 d SRT

        r_low = run_steady_state_simulation(plant=plant_low_srt, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_srt, t_days=200)

        s_nh_low_srt = _get(r_low, 'S_NH')
        s_nh_high_srt = _get(r_high, 'S_NH')

        assert s_nh_low_srt > s_nh_high_srt, (
            f'S_NH should be higher at low SRT: '
            f'SRT~4.5d -> {s_nh_low_srt:.3f} mg/L, '
            f'SRT~18.3d -> {s_nh_high_srt:.3f} mg/L'
        )

    @pytest.mark.slow
    def test_low_srt_reduces_autotrophs(self):
        """Low SRT causes autotrophic biomass (X_BA) washout.

        X_BA should be lower at low SRT (near washout) than at high SRT.
        """
        plant_low_srt = PlantParameters(Q_WAS=855)  # ~4.5 d SRT
        plant_high_srt = PlantParameters(Q_WAS=192)  # ~18.3 d SRT

        r_low = run_steady_state_simulation(plant=plant_low_srt, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_srt, t_days=200)

        x_ba_low_srt = _get(r_low, 'X_BA')
        x_ba_high_srt = _get(r_high, 'X_BA')

        assert x_ba_low_srt < x_ba_high_srt, (
            f'X_BA should be lower at low SRT (washout): '
            f'SRT~4.5d -> {x_ba_low_srt:.4f} mg/L, '
            f'SRT~18.3d -> {x_ba_high_srt:.4f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 2: Aeration (DO setpoint) effect on nitrification
# ---------------------------------------------------------------------------


class TestTrendAeration:
    """DO setpoint controls O2 availability for autotrophic nitrification.

    Autotrophs have K_OA = 0.4 mg O2/L. When DO < K_OA the growth rate is
    severely limited (Monod kinetics). Higher DO -> faster nitrification
    -> lower S_NH in effluent.
    """

    @pytest.mark.slow
    def test_low_do_increases_ammonia(self):
        """Low DO setpoint limits autotroph growth -> S_NH rises.

        Low DO: O1=0.3, O2=0.3, O3=0.3 mg/L (below K_OA = 0.4 for autotrophs)
        High DO: O1=3.5, O2=3.5, O3=3.5 mg/L (well above K_OA)
        """
        plant_low_do = PlantParameters(DO_O1=0.3, DO_O2=0.3, DO_O3=0.3)
        plant_high_do = PlantParameters(DO_O1=3.5, DO_O2=3.5, DO_O3=3.5)

        r_low = run_steady_state_simulation(plant=plant_low_do, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_do, t_days=200)

        s_nh_low_do = _get(r_low, 'S_NH')
        s_nh_high_do = _get(r_high, 'S_NH')

        assert s_nh_low_do > s_nh_high_do, (
            f'S_NH should be higher at low DO: '
            f'DO=0.3 -> {s_nh_low_do:.3f} mg/L, '
            f'DO=3.5 -> {s_nh_high_do:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 3: Temperature effect on nitrification kinetics
# ---------------------------------------------------------------------------


class TestTrendTemperature:
    """Temperature controls all ASM1 kinetic rates via Arrhenius (theta=1.07).

    Nitrifiers are the most temperature-sensitive group. At 15 C the max
    growth rate mu_A drops to ~0.36 1/d (from 0.5 at 20 C), while the
    minimum SRT for nitrification increases. With Q_WAS fixed, lower
    temperature means worse nitrification.
    """

    @pytest.mark.slow
    def test_low_temperature_increases_ammonia(self):
        """Cold temperature slows autotrophs -> S_NH rises.

        Cold: T = 15 C  (mu_A * theta^(15-20) ~ 0.36 1/d)
        Warm: T = 25 C  (mu_A * theta^(25-20) ~ 0.70 1/d)
        """
        plant_cold = PlantParameters(Temperature=15)
        plant_warm = PlantParameters(Temperature=25)

        r_cold = run_steady_state_simulation(plant=plant_cold, t_days=200)
        r_warm = run_steady_state_simulation(plant=plant_warm, t_days=200)

        s_nh_cold = _get(r_cold, 'S_NH')
        s_nh_warm = _get(r_warm, 'S_NH')

        assert s_nh_cold > s_nh_warm, (
            f'S_NH should be higher at low temperature: '
            f'15C -> {s_nh_cold:.3f} mg/L, '
            f'25C -> {s_nh_warm:.3f} mg/L'
        )

    @pytest.mark.slow
    def test_low_temperature_reduces_nitrate(self):
        """Less nitrification at low temperature -> less S_NO produced.

        S_NO effluent reflects how much ammonia was oxidized. Lower temperature
        means less nitrification, so S_NO should also be lower.
        """
        plant_cold = PlantParameters(Temperature=15)
        plant_warm = PlantParameters(Temperature=25)

        r_cold = run_steady_state_simulation(plant=plant_cold, t_days=200)
        r_warm = run_steady_state_simulation(plant=plant_warm, t_days=200)

        s_no_cold = _get(r_cold, 'S_NO')
        s_no_warm = _get(r_warm, 'S_NO')

        assert s_no_cold < s_no_warm, (
            f'S_NO should be lower at low temperature (less nitrification): '
            f'15C -> {s_no_cold:.3f} mg/L, '
            f'25C -> {s_no_warm:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 4: COD load effect on effluent COD
# ---------------------------------------------------------------------------


class TestTrendCODLoad:
    """Influent COD load scales effluent COD through the inert soluble fraction.

    S_I (inert soluble COD) passes through the plant completely unchanged.
    In the decomposition model: S_I = 30.0 * (COD_total / 381.19).
    So doubling COD_total doubles S_I in the effluent, raising COD_total out.
    """

    @pytest.mark.slow
    def test_higher_cod_increases_effluent_cod(self):
        """Double COD influent -> higher COD effluent (dominated by inert S_I).

        Low COD:  200 mg/L (~52% of default) -> S_I_inf ~ 15.7 mg/L
        High COD: 762 mg/L (2x default)      -> S_I_inf ~ 60.0 mg/L
        """
        plant_low_cod = PlantParameters(COD_total=200)
        plant_high_cod = PlantParameters(COD_total=762)

        r_low = run_steady_state_simulation(plant=plant_low_cod, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_cod, t_days=200)

        cod_low = _agg(r_low, 'COD_total')
        cod_high = _agg(r_high, 'COD_total')

        assert cod_high > cod_low, (
            f'Effluent COD should be higher with higher influent COD: '
            f'COD_inf=200 -> {cod_low:.2f} mg/L, '
            f'COD_inf=762 -> {cod_high:.2f} mg/L'
        )

    @pytest.mark.slow
    def test_higher_cod_increases_inert_si(self):
        """S_I effluent scales linearly with influent COD (inert, not degraded).

        S_I passes through untouched: S_I_eff = S_I_inf = 30 * (COD/381.19).
        """
        plant_low_cod = PlantParameters(COD_total=200)
        plant_high_cod = PlantParameters(COD_total=762)

        r_low = run_steady_state_simulation(plant=plant_low_cod, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_cod, t_days=200)

        s_i_low = _get(r_low, 'S_I')
        s_i_high = _get(r_high, 'S_I')

        assert s_i_high > s_i_low, (
            f'Effluent S_I should scale with influent COD: '
            f'COD_inf=200 -> S_I={s_i_low:.2f} mg/L, '
            f'COD_inf=762 -> S_I={s_i_high:.2f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 5: Internal recirculation effect on denitrification
# ---------------------------------------------------------------------------


class TestTrendInternalRecirculation:
    """Internal recirculation (O3 -> A1) transports nitrate to the anoxic zone.

    In the anoxic reactors (A1, A2) S_NO is used as electron acceptor
    (denitrification). Higher Q_intr -> more S_NO recycled to anoxic zone
    -> more denitrification -> lower S_NO in effluent.

    This effect is clear in the range 1Q-6Q. Above 6Q it saturates.
    """

    @pytest.mark.slow
    def test_higher_recirculation_reduces_nitrate(self):
        """More internal recirculation -> more denitrification -> less S_NO.

        Low Q_intr:  1Q = 18446 m3/d  (minimal anoxic recycle)
        High Q_intr: 6Q = 110676 m3/d (maximum practical recycle)
        """
        plant_low_intr = PlantParameters(Q_intr=18446)  # 1Q
        plant_high_intr = PlantParameters(Q_intr=110676)  # 6Q

        r_low = run_steady_state_simulation(plant=plant_low_intr, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_intr, t_days=200)

        s_no_low = _get(r_low, 'S_NO')
        s_no_high = _get(r_high, 'S_NO')

        assert s_no_low > s_no_high, (
            f'S_NO should be lower with higher internal recirculation: '
            f'Q_intr=1Q -> {s_no_low:.3f} mg/L, '
            f'Q_intr=6Q -> {s_no_high:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 6: Reactor volume effect on treatment efficiency
# ---------------------------------------------------------------------------


class TestTrendReactorVolume:
    """Reactor volume controls HRT and effective SRT (with fixed Q_WAS).

    Larger volume -> longer HRT -> more contact time for substrate removal
    and nitrification. With Q_WAS fixed, larger volume also means higher SRT
    (more sludge mass), which improves nitrification further.
    """

    @pytest.mark.slow
    def test_larger_volume_improves_nitrification(self):
        """Larger reactor volume -> higher HRT and SRT -> lower S_NH.

        Small: V_anoxic=500, V_aerobic=666 m3  (50% of BSM1 default)
        Large: V_anoxic=2000, V_aerobic=2666 m3 (200% of BSM1 default)
        """
        plant_small = PlantParameters(V_anoxic=500, V_aerobic=666)
        plant_large = PlantParameters(V_anoxic=2000, V_aerobic=2666)

        r_small = run_steady_state_simulation(plant=plant_small, t_days=200)
        r_large = run_steady_state_simulation(plant=plant_large, t_days=200)

        s_nh_small = _get(r_small, 'S_NH')
        s_nh_large = _get(r_large, 'S_NH')

        assert s_nh_small > s_nh_large, (
            f'S_NH should be lower with larger reactor volume: '
            f'50%% vol -> {s_nh_small:.3f} mg/L, '
            f'200%% vol -> {s_nh_large:.3f} mg/L'
        )

    @pytest.mark.slow
    def test_larger_volume_reduces_effluent_cod(self):
        """Larger volume -> more biodegradation -> lower effluent COD.

        With more reactor volume, slowly biodegradable X_S has more time to
        hydrolyze and be consumed by heterotrophs.
        """
        plant_small = PlantParameters(V_anoxic=500, V_aerobic=666)
        plant_large = PlantParameters(V_anoxic=2000, V_aerobic=2666)

        r_small = run_steady_state_simulation(plant=plant_small, t_days=200)
        r_large = run_steady_state_simulation(plant=plant_large, t_days=200)

        cod_small = _agg(r_small, 'COD_total')
        cod_large = _agg(r_large, 'COD_total')

        assert cod_small > cod_large, (
            f'Effluent COD should be lower with larger reactor volume: '
            f'50%% vol -> {cod_small:.2f} mg/L, '
            f'200%% vol -> {cod_large:.2f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 7: Influent flow (Q) effect on treatment efficiency
# ---------------------------------------------------------------------------


class TestTrendInfluentFlow:
    """Influent flow Q controls hydraulic retention time (HRT) and clarifier load.

    HRT = (2*V_an + 3*V_ae) / Q. With fixed reactor volumes, doubling Q halves
    HRT. Less contact time -> incomplete nitrification -> S_NH rises. The
    clarifier is also overloaded (surface overflow rate Q/A increases) -> TSS
    rises sharply.

    With fixed Q_WAS, SRT also changes because MLSS mass changes with loading.
    Both effects compound to degrade treatment quality at high Q.
    """

    @pytest.mark.slow
    def test_lower_flow_reduces_ammonia(self):
        """Low Q -> longer HRT -> better nitrification -> lower S_NH.

        Low Q:  9000 m3/d  (0.5x default, HRT ~16 h)
        High Q: 36000 m3/d (2x default,  HRT ~4 h)
        """
        plant_low_q = PlantParameters(Q=9000)
        plant_high_q = PlantParameters(Q=36000)

        r_low = run_steady_state_simulation(plant=plant_low_q, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_q, t_days=200)

        s_nh_low = _get(r_low, 'S_NH')
        s_nh_high = _get(r_high, 'S_NH')

        assert s_nh_low < s_nh_high, (
            f'S_NH should be lower at low influent flow (longer HRT): '
            f'Q=9000 -> {s_nh_low:.3f} mg/L, '
            f'Q=36000 -> {s_nh_high:.3f} mg/L'
        )

    @pytest.mark.slow
    def test_higher_flow_overloads_clarifier(self):
        """High Q -> clarifier surface overflow rate Q/A rises -> higher TSS.

        The clarifier surface area is fixed at 1500 m2. At Q=36000 m3/d plus
        Q_RAS=18446 the surface overflow rate exceeds 2 m/h, washing solids out.
        """
        plant_low_q = PlantParameters(Q=9000)
        plant_high_q = PlantParameters(Q=36000)

        r_low = run_steady_state_simulation(plant=plant_low_q, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_q, t_days=200)

        tss_low = _agg(r_low, 'TSS')
        tss_high = _agg(r_high, 'TSS')

        assert tss_low < tss_high, (
            f'Effluent TSS should be higher at high influent flow (clarifier overload): '
            f'Q=9000 -> {tss_low:.3f} mg/L, '
            f'Q=36000 -> {tss_high:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 8: Influent TKN effect on nitrification
# ---------------------------------------------------------------------------


class TestTrendTKN:
    """Influent TKN directly controls the ammonia load entering the reactors.

    In decompose_influent(), S_NH_inf = 31.56 * (TKN / 51.35). Higher TKN means
    more ammonia must be nitrified. With fixed SRT and fixed aeration (same KLa),
    the nitrification capacity is finite. Beyond a threshold, S_NH_eff rises.

    Effect is large and monotonic across the tested range (TKN 25-100 mg N/L).
    """

    @pytest.mark.slow
    def test_higher_tkn_increases_ammonia(self):
        """High TKN influent -> more ammonia load -> higher S_NH effluent.

        Low TKN:  25 mg N/L  -> S_NH_inf ~15.4 mg/L (easy to nitrify)
        High TKN: 100 mg N/L -> S_NH_inf ~61.5 mg/L (overloads nitrification)
        """
        plant_low_tkn = PlantParameters(TKN=25)
        plant_high_tkn = PlantParameters(TKN=100)

        r_low = run_steady_state_simulation(plant=plant_low_tkn, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_tkn, t_days=200)

        s_nh_low = _get(r_low, 'S_NH')
        s_nh_high = _get(r_high, 'S_NH')

        assert s_nh_low < s_nh_high, (
            f'S_NH should be higher with higher influent TKN: '
            f'TKN=25 -> {s_nh_low:.3f} mg/L, '
            f'TKN=100 -> {s_nh_high:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 9: RAS flow effect on biomass retention and nitrification
# ---------------------------------------------------------------------------


class TestTrendQRAS:
    """External recirculation (RAS) returns clarifier underflow back to A1.

    Higher Q_RAS -> more sludge mass recycled to A1 -> higher MLSS in reactors
    -> better biomass retention -> better nitrification -> lower S_NH.

    The tradeoff is higher hydraulic load on the clarifier: high Q_RAS increases
    Q_feed to C1 (Q + Q_RAS) and raises surface overflow rate, which may increase
    effluent TSS. Both effects are expected and confirmed.

    Range tested: 0.5Q (9000) vs ~3Q (55000 m3/d).
    """

    @pytest.mark.slow
    def test_lower_ras_worsens_nitrification(self):
        """Low Q_RAS -> less sludge return -> lower MLSS -> higher S_NH.

        Low RAS:  Q_RAS=9000  m3/d (~0.5Q) -> poor biomass retention
        High RAS: Q_RAS=55000 m3/d (~3Q)   -> strong biomass retention
        """
        plant_low_ras = PlantParameters(Q_RAS=9000)
        plant_high_ras = PlantParameters(Q_RAS=55000)

        r_low = run_steady_state_simulation(plant=plant_low_ras, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high_ras, t_days=200)

        s_nh_low_ras = _get(r_low, 'S_NH')
        s_nh_high_ras = _get(r_high, 'S_NH')

        assert s_nh_low_ras > s_nh_high_ras, (
            f'S_NH should be higher with low RAS (poor biomass retention): '
            f'Q_RAS=9000 -> {s_nh_low_ras:.3f} mg/L, '
            f'Q_RAS=55000 -> {s_nh_high_ras:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 10: Clarifier area effect on solids separation
# ---------------------------------------------------------------------------


class TestTrendClarifierArea:
    """Clarifier surface area controls the surface overflow rate (SOR = Q/A).

    At higher SOR, upward hydraulic velocity exceeds settling velocity of flocs
    -> solids escape over the weir -> TSS in effluent rises. This is the primary
    design constraint for secondary clarifiers (typical design SOR < 1.5 m/h).

    With fixed Q and Q_RAS = 36892 m3/d to clarifier:
    - SOR at A=500 m2:  36892 / (500*24) = 3.07 m/h  (FAR above limit)
    - SOR at A=4000 m2: 36892 / (4000*24) = 0.38 m/h (well within limit)
    """

    @pytest.mark.slow
    def test_smaller_clarifier_increases_tss(self):
        """Smaller clarifier area -> higher SOR -> worse settling -> higher TSS.

        Small: Clarifier_area=500 m2  (SOR ~3 m/h - overloaded)
        Large: Clarifier_area=4000 m2 (SOR ~0.4 m/h - comfortable)
        """
        plant_small = PlantParameters(Clarifier_area=500)
        plant_large = PlantParameters(Clarifier_area=4000)

        r_small = run_steady_state_simulation(plant=plant_small, t_days=200)
        r_large = run_steady_state_simulation(plant=plant_large, t_days=200)

        tss_small = _agg(r_small, 'TSS')
        tss_large = _agg(r_large, 'TSS')

        assert tss_small > tss_large, (
            f'Effluent TSS should be lower with larger clarifier area: '
            f'A=500 m2 -> {tss_small:.3f} mg/L, '
            f'A=4000 m2 -> {tss_large:.3f} mg/L'
        )


# ---------------------------------------------------------------------------
# Test 11: TSS_inf invariance (intentional design verification)
# ---------------------------------------------------------------------------


class TestTrendTSSInf:
    """TSS_inf is an informational input used ONLY for consistency warnings.

    The influent decomposition (decompose_influent) uses COD_total and TKN to
    scale ASM1 components. TSS_inf does NOT change any component concentration:
    the particulate fraction is already captured by X_I, X_S, X_BH (scaled
    with COD_total). Changing TSS_inf alone leaves the simulation unchanged.

    This test verifies that intentional design invariance is preserved. If this
    test fails, TSS_inf has accidentally been wired into the decomposition logic.
    """

    @pytest.mark.slow
    def test_tss_inf_does_not_affect_simulation(self):
        """TSS_inf is a warning-only parameter and must not alter simulation output.

        Low TSS_inf:  50 mg/L
        High TSS_inf: 1000 mg/L
        All other parameters at default -> results must be identical.
        """
        plant_low = PlantParameters(TSS_inf=50)
        plant_high = PlantParameters(TSS_inf=1000)

        r_low = run_steady_state_simulation(plant=plant_low, t_days=200)
        r_high = run_steady_state_simulation(plant=plant_high, t_days=200)

        s_nh_low = _get(r_low, 'S_NH')
        s_nh_high = _get(r_high, 'S_NH')
        cod_low = _agg(r_low, 'COD_total')
        cod_high = _agg(r_high, 'COD_total')

        assert abs(s_nh_low - s_nh_high) < 0.001, (
            f'S_NH must not change with TSS_inf (warning-only param): '
            f'TSS_inf=50 -> {s_nh_low:.4f}, '
            f'TSS_inf=1000 -> {s_nh_high:.4f}'
        )
        assert abs(cod_low - cod_high) < 0.001, (
            f'COD_total must not change with TSS_inf (warning-only param): '
            f'TSS_inf=50 -> {cod_low:.4f}, '
            f'TSS_inf=1000 -> {cod_high:.4f}'
        )
